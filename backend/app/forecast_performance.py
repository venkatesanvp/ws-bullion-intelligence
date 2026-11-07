"""Transient descriptive analysis of evaluated evidence; no fitting, acquisition or I/O."""

from decimal import Decimal
from .forecast_contracts import ForecastError, fingerprint
from .forecast_baselines import context, derived
from .forecast_metrics import score_cases, mean
from .forecast_performance_contracts import (
    EvaluationWindow,
    SampleEvidence,
    PerformanceResult,
    ErrorPoint,
    RollingError,
    ErrorDistribution,
    DistributionBin,
    RegimeSummary,
    CommonComparison,
    PerformanceAnalysis,
)

DENOMINATOR_MIN = Decimal("1e-8")
WARNINGS = (
    "DISJOINT_WINDOWS_DO_NOT_ESTABLISH_STATISTICAL_INDEPENDENCE",
    "EFFECTIVE_INDEPENDENT_EVIDENCE_NOT_ESTIMATED",
    "DESCRIPTIVE_ERRORS_NO_SIGNIFICANCE_OR_MODEL_SUPERIORITY_CLAIM",
    "ROLLING_ERRORS_ARE_POST_OUTCOME_DIAGNOSTICS_NOT_ORIGIN_INPUTS",
)


def windows(cases, calendar):
    indices = {s.session_date: i for i, s in enumerate(calendar.sessions)}
    if any(c.origin_session not in indices or c.target_session not in indices for c in cases):
        raise ForecastError("PERFORMANCE_SESSION_OUTSIDE_CALENDAR")
    spans = sorted(
        {(indices[c.origin_session], indices[c.target_session]) for c in cases}, key=lambda x: x[1]
    )
    pairs = sum(a[0] < b[1] and b[0] < a[1] for i, a in enumerate(spans) for b in spans[i + 1 :])
    end = -1
    disjoint = 0
    for a, b in spans:
        if a >= end:
            disjoint += 1
            end = b
    return pairs, disjoint


def error_values(case):
    """Raw Decimal losses; never divide by a substituted epsilon."""
    limits = []
    with context():
        if case.predicted_price is None:
            return (
                case.predicted_volatility - case.realized_volatility,
                None,
                None,
                (),
                "VOLATILITY_PROXY_FRACTION",
            )
        signed = case.predicted_price - case.actual_price
        percentage = (
            100 * signed / case.actual_price if abs(case.actual_price) > DENOMINATOR_MIN else None
        )
        returns = (
            case.predicted_return - (case.actual_price / case.origin_price - 1)
            if abs(case.origin_price) > DENOMINATOR_MIN
            else None
        )
        if percentage is None:
            limits.append("ZERO_OR_NEAR_ZERO_ACTUAL_PERCENTAGE_UNAVAILABLE")
        if returns is None:
            limits.append("ZERO_OR_NEAR_ZERO_ORIGIN_RETURN_ERROR_UNAVAILABLE")
        return signed, percentage, returns, tuple(limits), "PRICE"


def distribution(model, values, excluded, unit):
    labels = (
        "x < -0.05",
        "-0.05 <= x < -0.01",
        "-0.01 <= x < 0",
        "x = 0",
        "0 < x <= 0.01",
        "0.01 < x <= 0.05",
        "x > 0.05",
    )
    counts = [0] * 7
    for x in values:
        k = (
            0
            if x < Decimal("-.05")
            else 1
            if x < Decimal("-.01")
            else 2
            if x < 0
            else 3
            if x == 0
            else 4
            if x <= Decimal(".01")
            else 5
            if x <= Decimal(".05")
            else 6
        )
        counts[k] += 1
    ordered = sorted(values)

    def rank(n):
        return derived(ordered[(len(ordered) * n + 99) // 100 - 1]) if ordered else None

    return ErrorDistribution(
        model_id=model,
        unit=unit,
        sample_count=len(values),
        excluded_count=excluded,
        bins=tuple(DistributionBin(label=label, count=n) for label, n in zip(labels, counts)),
        p10=rank(10),
        median=rank(50),
        p90=rank(90),
    )


def compatible_cards(cards):
    if not cards:
        return
    a = cards[0]
    keys = (
        "instrument",
        "horizon",
        "evaluation_mode",
        "dataset_fingerprint",
        "basis",
        "evaluation_window",
        "experiment_id",
        "assessment_cutoff",
        "origin_set_fingerprint",
        "metric_kind",
        "sample_basis",
    )
    if any(any(getattr(a, k) != getattr(b, k) for k in keys) for b in cards[1:]):
        raise ForecastError("INCOMPATIBLE_PERFORMANCE_COMPARISON")


def _analyze(
    experiment,
    *,
    instrument,
    basis,
    calendar,
    descriptors,
    start,
    end,
    qualification,
    limitations,
    rolling_window=10,
    check=None,
):
    if type(rolling_window) is not int or not 2 <= rolling_window <= 30:
        raise ForecastError("INVALID_ROLLING_ERROR_WINDOW")
    mode = experiment.evaluation_mode
    entries = {r.model_id: [] for r in experiment.evaluations}
    for e in experiment.forecasts:
        f = e.forecast
        if f.instrument != instrument or f.horizon != experiment.spec.horizon or f.basis != basis:
            raise ForecastError("INCOMPATIBLE_PERFORMANCE_FORECAST")
        if e.outcome_status == "MATURED" and e.metric_case is not None:
            if (
                e.metric_case.instrument_id != instrument.instrument_id
                or e.metric_case.origin_session != f.origin_session
                or e.metric_case.target_session != f.target_session
            ):
                raise ForecastError("INCOMPATIBLE_PERFORMANCE_CASE")
            if (
                e.outcome_available_at is None
                or e.outcome_available_at > experiment.evaluation_cutoff
            ):
                raise ForecastError("PERFORMANCE_OUTCOME_NOT_AVAILABLE")
            entries[f.model.model_id].append(e)
    pair = all(m in entries for m in ("B01", "B02"))
    common = set()
    if pair:
        pools = {m: {e.metric_case.key: e.metric_case for e in entries[m]} for m in ("B01", "B02")}
        common = set(pools["B01"]) & set(pools["B02"])
        if any(
            (pools["B01"][k].origin_price, pools["B01"][k].actual_price)
            != (pools["B02"][k].origin_price, pools["B02"][k].actual_price)
            for k in common
        ):
            raise ForecastError("INCOMPATIBLE_BENCHMARK_TARGETS")
    cards = []
    errors = []
    rolling = []
    distributions = []
    regimes = []
    per_model = {}
    raw_loss = {}
    for summary in experiment.evaluations:
        if check:
            check()
        model = summary.model_id
        descriptor = descriptors[model]
        own = entries[model]
        selected = sorted(
            (
                e
                for e in own
                if not (pair and model in ("B01", "B02")) or e.metric_case.key in common
            ),
            key=lambda e: e.forecast.origin_session,
        )
        if any(
            e.forecast.model.version != descriptor.version
            or e.forecast.configuration
            != next(r.configuration for r in experiment.spec.models if r.model_id == model)
            for e in own
        ):
            raise ForecastError("MIXED_PERFORMANCE_MODEL_VERSION_OR_CONFIGURATION")
        cases = tuple(e.metric_case for e in selected)
        per_model[model] = cases
        overlaps, disjoint = windows(cases, calendar)
        samples = SampleEvidence(
            requested_origins=experiment.submitted_origin_count,
            eligible_origins=len(own),
            scored_origins=len(selected),
            unmatched_origins=len(own) - len(selected),
            excluded_origins=summary.failed_count,
            pending_origins=summary.pending_count,
            unavailable_outcomes=summary.unavailable_outcome_count,
            overlapping_pairs=overlaps,
            disjoint_windows=disjoint,
        )
        kind = (
            "VOLATILITY_PROXY" if "VOLATILITY" in descriptor.capabilities else "POINT_PRICE_RETURN"
        )
        core = dict(
            experiment_id=experiment.experiment_id,
            model_id=model,
            model_version=descriptor.version,
            configuration=next(
                r.configuration for r in experiment.spec.models if r.model_id == model
            ),
            instrument=instrument,
            horizon=experiment.spec.horizon,
            evaluation_mode=mode,
            dataset_fingerprint=experiment.dataset_fingerprint,
            basis=basis,
            evaluation_window=EvaluationWindow(start=start, end=end),
            sample_basis="COMMON_B01_B02"
            if pair and model in ("B01", "B02")
            else "MODEL_ELIGIBLE_ONLY",
            origin_set_fingerprint=fingerprint(tuple(c.key for c in cases)),
            metric_kind=kind,
            metrics=score_cases(cases),
            samples=samples,
            qualification_status=qualification,
            assumptions=tuple(getattr(experiment, "assumptions", ()))
            or (
                "ACTUAL_METADATA_AND_AVAILABILITY_REQUIRED"
                if mode == "STRICT_POINT_IN_TIME"
                else "SYNTHETIC_TEST_ONLY",
            ),
            limitations=tuple(limitations)
            + WARNINGS
            + (("SMALL_DISJOINT_SUPPORT_BELOW_20",) if disjoint < 20 else ()),
            assessment_cutoff=experiment.evaluation_cutoff,
            computed_at=experiment.executed_at,
        )
        cards.append(
            PerformanceResult(
                result_id=fingerprint({"version": "forecast-performance-v1", **core}), **core
            )
        )
        raw = []
        dist = []
        raw_loss[model] = []
        for e in selected:
            if check:
                check()
            signed, pct, ret, limits, unit = error_values(e.metric_case)
            raw_loss[model].append(signed)
            raw.append((e, signed))
            chosen = signed if unit == "VOLATILITY_PROXY_FRACTION" else ret
            if chosen is not None:
                dist.append(chosen)
            errors.append(
                ErrorPoint(
                    forecast_id=e.forecast.forecast_id,
                    model_id=model,
                    origin=e.forecast.origin_session,
                    target=e.forecast.target_session,
                    outcome_available_at=e.outcome_available_at,
                    unit=unit,
                    signed_error=derived(signed),
                    absolute_error=derived(abs(signed)),
                    percentage_error=derived(pct) if pct is not None else None,
                    return_error=derived(ret) if ret is not None else None,
                    normalization_limits=limits,
                )
            )
            part = raw[-rolling_window:]
            losses = tuple(x[1] for x in part)
            with context():
                rolling.append(
                    RollingError(
                        model_id=model,
                        first_origin=part[0][0].forecast.origin_session,
                        last_origin=e.forecast.origin_session,
                        sample_count=len(part),
                        requested_window=rolling_window,
                        partial_window=len(part) < rolling_window,
                        outcome_known_at=max(x[0].outcome_available_at for x in part),
                        mae=derived(mean(tuple(abs(x) for x in losses))),
                        rmse=derived(mean(tuple(x * x for x in losses)).sqrt()),
                        bias=derived(mean(losses)),
                        unit=unit,
                    )
                )
        with context():
            distributions.append(
                distribution(
                    model,
                    dist,
                    len(selected) - len(dist),
                    "VOLATILITY_PROXY_FRACTION"
                    if kind == "VOLATILITY_PROXY"
                    else "RETURN_ERROR_FRACTION",
                )
            )
        if experiment.regime_rule_version:
            for axis, attr, labels in (
                ("TREND", "trend", ("TRENDING", "SIDEWAYS", "UNAVAILABLE")),
                ("VOLATILITY", "volatility", ("HIGH", "LOW", "UNAVAILABLE")),
            ):
                for label in labels:
                    subset = tuple(
                        e.metric_case
                        for e in selected
                        if getattr(e.regime, attr, "UNAVAILABLE") == label
                    )
                    ov, dj = windows(subset, calendar)
                    regimes.append(
                        RegimeSummary(
                            model_id=model,
                            axis=axis,
                            label=label,
                            metrics=score_cases(subset),
                            scored_origins=len(subset),
                            overlapping_pairs=ov,
                            disjoint_windows=dj,
                            limitations=(
                                "FIXED_RESEARCH_THRESHOLDS_NOT_TUNED_OR_VALIDATED",
                                "SUBGROUPS_ARE_DESCRIPTIVE_NOT_SIGNIFICANCE_TESTS",
                                "DISJOINT_DOES_NOT_PROVE_INDEPENDENCE",
                            ),
                        )
                    )
    comparison = CommonComparison(
        model_ids=("B01", "B02") if pair else (),
        common_origins=len(common),
        origin_set_fingerprint=next(c.origin_set_fingerprint for c in cards if c.model_id == "B01")
        if pair
        else None,
        b02_minus_b01_mae=None,
        reason="NO_COMMON_ELIGIBLE_ORIGINS" if pair else "BOTH_POINT_MODELS_NOT_REQUESTED",
    )
    if pair and common:
        compatible_cards([c for c in cards if c.model_id in ("B01", "B02")])
        with context():
            delta = derived(
                mean(tuple(abs(x) for x in raw_loss["B02"]))
                - mean(tuple(abs(x) for x in raw_loss["B01"]))
            )
        comparison = comparison.model_copy(update={"b02_minus_b01_mae": delta, "reason": None})
    if check:
        check()
    return PerformanceAnalysis(
        cards=tuple(cards),
        comparison=comparison,
        errors=tuple(errors),
        rolling=tuple(rolling),
        distributions=tuple(distributions),
        regimes=tuple(regimes),
        regime_rule_version=experiment.regime_rule_version,
        rolling_window=rolling_window,
        warnings=WARNINGS
        + (
            ("REGIME_LABELS_SHARE_THE_EVALUATION_MODE_AVAILABILITY_AND_VINTAGE_LIMITS",)
            if experiment.regime_rule_version
            else ()
        ),
    )


def analyze(experiment, **kwargs):
    # Keep normalization, loss differences and all serialization in Decimal34.
    with context():
        return _analyze(experiment, **kwargs)
