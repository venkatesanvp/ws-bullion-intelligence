"""Bounded chronological synthetic replay and transient experiment evidence."""

from datetime import date, datetime
from decimal import Decimal, DecimalException
from typing import Literal
from pydantic import Field, ValidationError, model_validator, SerializeAsAny
from .forecast_contracts import (
    Frozen,
    Name,
    Stamp,
    Settings,
    QualityRequirements,
    ForecastDataset,
    ForecastRequest,
    ForecastResult,
    ForecastError,
    HORIZONS,
    NUMERIC_VERSION,
    fingerprint,
    settings_valid,
    utc,
)
from .forecast_market_contracts import MarketDataset, MarketRequest, MarketQuality
from .forecast_dataset import _build_snapshot_validated, visible_dataset_fingerprint
from .forecast_baselines import get_model, context, simple_returns
from .forecast_metrics import (
    METRICS_VERSION,
    MetricCase,
    MetricSummary,
    BenchmarkComparison,
    score_cases,
    compare_to_b01,
)

from .forecast_replay import ReplayRequest, replay_snapshot, POLICY, MODE, ASSUMPTIONS

from .forecast_performance_contracts import RegimeEvidence
from .forecast_regimes import classify, VERSION as REGIME_VERSION

VERSION = "walk-forward-synthetic-v1"


class ForecastOrigin(Frozen):
    session: date
    cutoff: Stamp


class ModelRun(Frozen):
    model_id: Name
    configuration: Settings = ()

    @model_validator(mode="after")
    def coherent(self):
        object.__setattr__(self, "configuration", settings_valid(self.configuration))
        return self


class EvaluationSpec(Frozen):
    evaluation_mode: Literal["SYNTHETIC"] = "SYNTHETIC"
    horizon: int = Field(strict=True)
    lookback: int = Field(strict=True, ge=1, le=1000)
    origins: tuple[ForecastOrigin, ...] = Field(min_length=1, max_length=200)
    models: tuple[ModelRun, ...] = Field(min_length=1, max_length=3)
    evaluation_cutoff: Stamp
    overlap_policy: Literal["ALLOW_DEPENDENT", "REQUIRE_NONOVERLAPPING"] = "ALLOW_DEPENDENT"
    quality: QualityRequirements = Field(default_factory=QualityRequirements)

    @model_validator(mode="after")
    def coherent(self):
        if self.horizon not in HORIZONS:
            raise ValueError("UNSUPPORTED_HORIZON")
        days, times = [o.session for o in self.origins], [o.cutoff for o in self.origins]
        if days != sorted(set(days)) or times != sorted(set(times)):
            raise ValueError("ORIGINS_NOT_CHRONOLOGICAL")
        if len({m.model_id for m in self.models}) != len(self.models):
            raise ValueError("DUPLICATE_MODEL_RUN")
        return self


class Failure(Frozen):
    model_id: Name
    origin_session: date
    reason: Name


class ForecastEvidence(Frozen):
    regime: RegimeEvidence | None = None
    evidence_id: Name
    request: SerializeAsAny[ForecastRequest]
    forecast: SerializeAsAny[ForecastResult]
    outcome_status: Literal["MATURED", "PENDING", "UNAVAILABLE"]
    outcome_reason: str | None
    outcome_available_at: Stamp | None
    outcome_fingerprint: str | None
    metric_case: MetricCase | None


class ModelEvaluation(Frozen):
    model_id: Name
    forecast_count: int
    failed_count: int
    matured_count: int
    pending_count: int
    unavailable_outcome_count: int
    metrics: MetricSummary
    benchmark: BenchmarkComparison


class ExperimentEvidence(Frozen):
    regime_rule_version: Literal["fixed-21-close-v1"] | None = None
    evaluation_mode: Literal["SYNTHETIC"] = "SYNTHETIC"
    experiment_id: Name
    execution_id: Name
    executed_at: Stamp
    evaluation_cutoff: Stamp
    dataset_fingerprint: Name
    spec: SerializeAsAny[EvaluationSpec]
    engine_version: Literal["walk-forward-synthetic-v1"] = VERSION
    numeric_version: Literal["decimal34-half-even-wire12-v1"] = NUMERIC_VERSION
    metrics_version: Literal["descriptive-metrics-v2-bias"] = METRICS_VERSION
    classification: Literal["SYNTHETIC_HISTORICAL_REPLAY"] = "SYNTHETIC_HISTORICAL_REPLAY"
    forecasts: tuple[ForecastEvidence, ...]
    exclusions: tuple[Failure, ...]
    evaluations: tuple[ModelEvaluation, ...]
    submitted_origin_count: int
    matured_unique_origins: int
    overlapping_matured_window_pairs: int
    max_disjoint_matured_windows: int
    warnings: tuple[str, ...]
    retention: Literal["TRANSIENT_MEMORY_ONLY"] = "TRANSIENT_MEMORY_ONLY"


class MarketEvaluationSpec(EvaluationSpec):
    evaluation_mode: Literal["STRICT_POINT_IN_TIME"] = "STRICT_POINT_IN_TIME"
    blocked_target_sessions: tuple[date, ...] = Field(default=(), max_length=500)
    quality: MarketQuality = Field(default_factory=MarketQuality)


class MarketExperiment(ExperimentEvidence):
    evaluation_mode: Literal["STRICT_POINT_IN_TIME"] = "STRICT_POINT_IN_TIME"
    engine_version: Literal["walk-forward-strict-v3"] = "walk-forward-strict-v3"
    classification: Literal["STRICT_POINT_IN_TIME"] = "STRICT_POINT_IN_TIME"


class ReplayEvaluationSpec(MarketEvaluationSpec):
    evaluation_mode: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    assumption_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"]
    known_break_sessions: tuple[date, ...] = Field(default=(), max_length=500)


class ReplayExperiment(MarketExperiment):
    engine_version: Literal["walk-forward-conditional-v1"] = "walk-forward-conditional-v1"
    classification: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    evaluation_mode: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    assumption_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"] = POLICY
    assumptions: tuple[str, ...] = ASSUMPTIONS


def outcome(dataset, snapshot, result, spec):
    if snapshot.target_session.close_at > spec.evaluation_cutoff:
        return "PENDING", "TARGET_SESSION_NOT_COMPLETE", None, None, None
    sessions = dataset.calendar.sessions
    index = next(i for i, s in enumerate(sessions) if s.session_date == snapshot.origin_session)
    target_path = sessions[index + 1 : index + spec.horizon + 1]
    pool = {r.session_date: r for r in dataset.observations}
    if any(s.session_date not in pool for s in target_path):
        return "UNAVAILABLE", "MISSING_OUTCOME_SESSION", None, None, None
    rows = tuple(pool[s.session_date] for s in target_path)
    # No value calculation/fingerprinting until the full target path is available at assessment cutoff.
    if any(r.available_at > spec.evaluation_cutoff for r in rows):
        return "PENDING", "OUTCOME_PUBLICATION_PENDING", None, None, None
    if any(not r.completed or r.quality != spec.quality.quality for r in rows):
        return "UNAVAILABLE", "OUTCOME_QUALITY_FAILED", None, None, None
    lag = spec.quality.max_publication_delay_seconds
    if lag is not None and any(
        (r.available_at - r.observed_at).total_seconds() > lag for r in rows
    ):
        return "UNAVAILABLE", "OUTCOME_PUBLICATION_DELAY_EXCEEDED", None, None, None
    if dataset.basis == "RAW_CLOSE" and any(
        a.available_at <= spec.evaluation_cutoff
        and snapshot.origin_session < a.effective_session <= snapshot.target_session.session_date
        for a in dataset.corporate_actions
    ):
        return "UNAVAILABLE", "UNADJUSTED_OUTCOME_ACTION", None, None, None
    try:
        with context():
            origin_price = snapshot.observations[-1].close
            returns = simple_returns((origin_price,) + tuple(r.close for r in rows))
            rv = sum((r * r for r in returns), Decimal(0)).sqrt()
            case = MetricCase(
                case_id=result.forecast_id,
                instrument_id=result.instrument.instrument_id,
                origin_session=result.origin_session,
                target_session=result.target_session,
                origin_price=origin_price,
                actual_price=rows[-1].close,
                realized_volatility=rv,
                predicted_price=result.predicted_price,
                predicted_return=result.predicted_return,
                predicted_volatility=result.horizon_volatility,
            )
    except (DecimalException, ForecastError, ValidationError):
        return "UNAVAILABLE", "OUTCOME_NUMERIC_UNSUPPORTED", None, None, None
    return "MATURED", None, max(r.available_at for r in rows), fingerprint(rows), case


def evaluate(
    dataset: ForecastDataset,
    spec: EvaluationSpec,
    *,
    executed_at: datetime,
    check=None,
    regime_analysis=False,
) -> ExperimentEvidence:
    if type(regime_analysis) is not bool:
        raise ForecastError("INVALID_REGIME_ANALYSIS_FLAG")
    try:
        real = type(dataset) is MarketDataset
        dataset = (MarketDataset if real else ForecastDataset).model_validate(dataset.model_dump())
        replay = type(spec) is ReplayEvaluationSpec
        if replay and not real:
            raise ValueError("REPLAY_REQUIRES_REAL_DATA")
        spec = (
            ReplayEvaluationSpec if replay else MarketEvaluationSpec if real else EvaluationSpec
        ).model_validate(spec.model_dump())
        executed_at = utc(executed_at)
    except (ValueError, AttributeError):
        raise ForecastError("INVALID_EVALUATION_INPUT") from None
    if executed_at < spec.evaluation_cutoff:
        raise ForecastError("EXECUTION_BEFORE_ASSESSMENT_CUTOFF")
    visible_hash = visible_dataset_fingerprint(dataset, spec.evaluation_cutoff)
    experiment_id = fingerprint(
        {
            "spec": spec,
            "dataset": visible_hash,
            "engine": "walk-forward-conditional-v1"
            if replay
            else "walk-forward-strict-v3"
            if real
            else VERSION,
            "numeric": NUMERIC_VERSION,
            "metrics": METRICS_VERSION,
            "models": tuple(get_model(m.model_id).descriptor for m in spec.models),
            **({"regime_rule_version": REGIME_VERSION} if regime_analysis else {}),
        }
    )
    execution_id = fingerprint({"experiment": experiment_id, "executed_at": executed_at})
    sessions = dataset.calendar.sessions
    indices = {s.session_date: i for i, s in enumerate(sessions)}
    planned = [
        (indices[o.session], indices[o.session] + spec.horizon)
        for o in spec.origins
        if o.session in indices and indices[o.session] + spec.horizon < len(sessions)
    ]
    if spec.overlap_policy == "REQUIRE_NONOVERLAPPING" and any(
        a[1] > b[0] for a, b in zip(planned, planned[1:])
    ):
        raise ForecastError("OVERLAPPING_EVALUATION_ORIGINS")
    evidence, failures, cases = [], [], {m.model_id: [] for m in spec.models}
    # B01 reference is computed per successful snapshot, even if not requested for display.
    benchmark_cases = {}
    for origin in spec.origins:
        shared_snapshot = None
        shared_error = None
        if check:
            check()
        for model_run in spec.models:
            if origin.cutoff > spec.evaluation_cutoff:
                failures.append(
                    Failure(
                        model_id=model_run.model_id,
                        origin_session=origin.session,
                        reason="ORIGIN_AFTER_EVALUATION_CUTOFF",
                    )
                )
                continue
            if check:
                check()
            request_kind = ReplayRequest if replay else MarketRequest if real else ForecastRequest
            request = request_kind(
                instrument=dataset.instrument,
                origin_session=origin.session,
                horizon=spec.horizon,
                lookback=spec.lookback,
                model_id=model_run.model_id,
                configuration=model_run.configuration,
                cutoff=origin.cutoff,
                quality=spec.quality,
                **(
                    {
                        "assumption_policy": spec.assumption_policy,
                        "assessment_cutoff": spec.evaluation_cutoff,
                    }
                    if replay
                    else {}
                ),
            )
            if real and origin.session in indices:
                target_index = indices[origin.session] + spec.horizon
                if (
                    target_index < len(sessions)
                    and sessions[target_index].session_date in spec.blocked_target_sessions
                ):
                    failures.append(
                        Failure(
                            model_id=model_run.model_id,
                            origin_session=origin.session,
                            reason="TARGET_SESSION_TIMING_UNQUALIFIED",
                        )
                    )
                    continue
            try:
                if shared_error:
                    raise ForecastError(shared_error)
                if shared_snapshot is None:
                    try:
                        if replay:
                            a = indices.get(origin.session, -1)
                            span = sessions[max(0, a - spec.lookback + 1) : a + spec.horizon + 1]
                            blocked = set(spec.known_break_sessions) | {
                                x.effective_session for x in dataset.corporate_actions
                            }
                            if span and any(
                                span[0].session_date < d <= span[-1].session_date for d in blocked
                            ):
                                raise ForecastError("DECLARED_ACTION_OR_REVISION_BREAK")
                            shared_snapshot = replay_snapshot(dataset, request)
                        else:
                            shared_snapshot = _build_snapshot_validated(dataset, request)
                    except ForecastError as failure:
                        shared_error = failure.code
                        raise
                snapshot = shared_snapshot
                result = get_model(request.model_id).predict(
                    snapshot, request, created_at=executed_at
                )
            except ForecastError as exc:
                failures.append(
                    Failure(
                        model_id=model_run.model_id, origin_session=origin.session, reason=exc.code
                    )
                )
                continue
            regime = classify(snapshot) if regime_analysis else None
            status, reason, available_at, outcome_hash, case = outcome(
                dataset, snapshot, result, spec
            )
            record = ForecastEvidence(
                evidence_id=fingerprint(
                    {"forecast": result.forecast_id, "execution": execution_id}
                ),
                request=request,
                forecast=result,
                outcome_status=status,
                outcome_reason=reason,
                outcome_available_at=available_at,
                outcome_fingerprint=outcome_hash,
                metric_case=case,
                regime=regime,
            )
            evidence.append(record)
            if case is not None:
                cases[model_run.model_id].append(case)
                if case.key not in benchmark_cases:
                    ref_request = request_kind.model_validate(
                        {**request.model_dump(), "model_id": "B01", "configuration": ()}
                    )
                    ref = get_model("B01").predict(snapshot, ref_request, created_at=executed_at)
                    _, _, _, _, b = outcome(dataset, snapshot, ref, spec)
                    if b is not None:
                        benchmark_cases[case.key] = b
    evaluations = []
    for m in spec.models:
        rows = tuple(r for r in evidence if r.forecast.model.model_id == m.model_id)
        model_cases = tuple(cases[m.model_id])
        evaluations.append(
            ModelEvaluation(
                model_id=m.model_id,
                forecast_count=len(rows),
                failed_count=sum(f.model_id == m.model_id for f in failures),
                matured_count=sum(r.outcome_status == "MATURED" for r in rows),
                pending_count=sum(r.outcome_status == "PENDING" for r in rows),
                unavailable_outcome_count=sum(r.outcome_status == "UNAVAILABLE" for r in rows),
                metrics=score_cases(model_cases),
                benchmark=compare_to_b01(model_cases, tuple(benchmark_cases.values())),
            )
        )
    windows = sorted(
        {
            (indices[r.forecast.origin_session], indices[r.forecast.target_session])
            for r in evidence
            if r.outcome_status == "MATURED"
        },
        key=lambda w: w[1],
    )
    pairs = sum(
        a[0] < b[1] and b[0] < a[1] for i, a in enumerate(windows) for b in windows[i + 1 :]
    )
    end, disjoint = -1, 0
    for a, b in windows:
        if a >= end:
            disjoint += 1
            end = b
    warnings = [
        "CONDITIONAL_REAL_RESEARCH_NO_RELIABILITY_CLAIM"
        if real
        else "SYNTHETIC_ONLY_NO_REAL_MARKET_ACCURACY",
        "RETROSPECTIVE_REPLAY_NOT_FORWARD_EVIDENCE",
        "NO_CALIBRATION_OR_SIGNIFICANCE_CLAIM",
    ]
    if replay:
        warnings.extend(ASSUMPTIONS)
    if pairs:
        warnings.append("OVERLAPPING_ERRORS_ARE_DEPENDENT")
    if disjoint < 20:
        warnings.append("BELOW_PROPOSED_INDEPENDENT_EVALUATION_SUPPORT")
    if check:
        check()
    result_type = ReplayExperiment if replay else MarketExperiment if real else ExperimentEvidence
    return result_type(
        regime_rule_version=REGIME_VERSION if regime_analysis else None,
        experiment_id=experiment_id,
        execution_id=execution_id,
        executed_at=executed_at,
        evaluation_cutoff=spec.evaluation_cutoff,
        dataset_fingerprint=visible_hash,
        spec=spec,
        forecasts=tuple(evidence),
        exclusions=tuple(failures),
        evaluations=tuple(evaluations),
        submitted_origin_count=len(spec.origins),
        matured_unique_origins=len(windows),
        overlapping_matured_window_pairs=pairs,
        max_disjoint_matured_windows=disjoint,
        warnings=tuple(warnings),
    )
