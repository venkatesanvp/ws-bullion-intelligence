"""Bounded compute-only orchestration and expiring RAM tracking. No acquisition/SQL writes."""

from collections import OrderedDict, deque
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
from threading import Lock, RLock
import time
from uuid import UUID, uuid4
from typing import Literal
from pydantic import Field, model_validator
from .schemas import Strict
from .forecast_contracts import ForecastRequest, ForecastError, HORIZONS, fingerprint, Setting
from .forecast_market_contracts import MarketDataset, MarketRequest
from .forecast_dataset import build_snapshot
from .forecast_baselines import get_model, context, derived, simple_returns
from .forecast_evaluation import (
    EvaluationSpec,
    MarketEvaluationSpec,
    ReplayEvaluationSpec,
    ForecastOrigin,
    ModelRun,
    evaluate,
)
from .forecast_market_adapter import adapt, IST, chart_history
from .forecast_qualification import qualification
from .forecast_replay import POLICY, MODE, ASSUMPTIONS
from .forecast_performance import analyze


class ResearchOptions(Strict):
    instrument_id: UUID
    source_id: UUID
    basis: str = Field(default="PROVIDER_ADJUSTED", max_length=40)
    horizon: int = Field(default=5, strict=True)
    lookback: int = Field(default=60, strict=True, ge=1, le=1000)
    models: list[str] = Field(
        default_factory=lambda: ["B01", "B02", "B03"], min_length=1, max_length=3
    )
    annualization_sessions: int | None = Field(default=None, strict=True, ge=1, le=1000)
    start: date | None = None
    end: date | None = None
    frequency: int = Field(default=5, strict=True, ge=1, le=120)
    expected_revision: str | None = Field(default=None, max_length=64)
    evaluation_mode: Literal[
        "STRICT_POINT_IN_TIME", "CONDITIONAL_HISTORICAL_REPLAY", "SYNTHETIC"
    ] = "STRICT_POINT_IN_TIME"
    acknowledge_replay_assumptions: bool = Field(default=False, strict=True)
    replay_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"] | None = None
    regime_analysis: bool = Field(default=False, strict=True)
    rolling_error_window: int = Field(default=10, strict=True, ge=2, le=30)

    @model_validator(mode="after")
    def bounded(self):
        if (
            self.horizon not in HORIZONS
            or len(set(self.models)) != len(self.models)
            or set(self.models) - {"B01", "B02", "B03"}
        ):
            raise ValueError("UNSUPPORTED_FORECAST_OPTIONS")
        if (
            self.start
            and self.end
            and (self.start > self.end or (self.end - self.start).days > 1100)
        ):
            raise ValueError("INVALID_EVALUATION_PERIOD")
        return self


def display_changes(result):
    if result.predicted_price is None:
        return None, None
    with context():
        origin = result.last_observed_close
        if origin <= 0:
            raise ForecastError("INVALID_ORIGIN_PRICE")
        return derived(result.predicted_price - origin), derived(
            100 * (result.predicted_price / origin - 1)
        )


class ForecastResearchService:
    def __init__(self, market, *, calendar_override=None, monotonic=time.monotonic, timeout=30):
        self.market = market
        self.calendar_override = calendar_override
        self.monotonic = monotonic
        self.timeout = timeout
        self._gate = Lock()
        self._records_lock = RLock()
        self._runs = OrderedDict()
        self._calls = deque()
        self._performance = OrderedDict()

    def _purge(self):
        now = self.monotonic()
        with self._records_lock:
            for k in list(self._runs):
                if now >= self._runs[k]["expires_at"]:
                    self._runs.pop(k)
            for key in list(self._performance):
                if now >= self._performance[key]["expires_at"]:
                    self._performance.pop(key)

    def performance_registry(self):
        self._purge()
        with self._records_lock:
            return {
                "schema_version": "transient-performance-registry-v1",
                "records": [deepcopy(v["record"]) for v in reversed(self._performance.values())],
                "retention": "PROCESS_MEMORY_MAX_32_EXPERIMENTS_3600_SECONDS_RESTART_LOSES_RESULTS",
            }

    def identifiers(self, run_id):
        self._purge()
        with self._records_lock:
            record = self._runs.get(str(run_id))
            if not record:
                raise ForecastError("TRACKING_NOT_FOUND_OR_EXPIRED")
            return record["options"].instrument_id, record["options"].source_id

    def receipts(self):
        self._purge()
        with self._records_lock:
            return [
                {
                    "run_id": k,
                    "instrument_id": str(v["options"].instrument_id),
                    "source_id": str(v["options"].source_id),
                    "created_at": v["payload"]["computed_at"],
                    "horizon": v["options"].horizon,
                }
                for k, v in reversed(self._runs.items())
            ]

    def _view(self, reader, now):
        instrument, source, rows = reader()
        view = adapt(
            instrument,
            source,
            rows,
            listings=self.market.provider.listings(),
            now=now,
            calendar_override=self.calendar_override,
        )
        q, breaks = qualification(view.dataset, view.metadata, source.profile)
        view.metadata["qualification"] = q
        known = {x.isin for x in self.market.provider.listings()}
        choices = [
            i
            for i in self.market.store.listings()
            if i.isin in known and self.market.store.has_series(i.id, source.id)
        ]
        view.metadata["instruments"] = [
            {"instrument_id": str(i.id), "symbol": i.symbol} for i in choices
        ] or [{"instrument_id": str(instrument.id), "symbol": instrument.symbol}]
        policy = self.market.public_policy()
        view.metadata["refresh_session"] = policy.get("latest_provider_eligible_session_candidate")
        view.metadata["manual_refresh_enabled"] = bool(policy.get("enabled"))
        view.metadata["revision"] = fingerprint(
            {
                "references": view.references,
                "source_profile": source.profile,
                "calendar": view.dataset.calendar.version,
            }
        )
        return view

    def _horizons(self, view, now):
        rows = view.dataset.observations
        sessions = view.dataset.calendar.sessions
        days = [s.session_date for s in sessions]
        out = []
        for h in HORIZONS:
            reason = None
            target = None
            if not rows:
                reason = "INSUFFICIENT_FINAL_DAILY_DATA"
            else:
                i = days.index(rows[-1].session_date) + h
                if i >= len(sessions):
                    reason = "HORIZON_OUTSIDE_REVIEWED_CALENDAR"
                else:
                    target = sessions[i]
                    if target.session_date in view.unknown_target_times:
                        reason = "TARGET_SESSION_TIMING_UNQUALIFIED"
                    elif target.close_at <= now:
                        reason = "TARGET_SESSION_ALREADY_COMPLETED"
            out.append(
                {
                    "horizon": h,
                    "target_session": str(target.session_date) if target else None,
                    "status": "UNAVAILABLE" if reason else "AVAILABLE",
                    "reason": reason,
                }
            )
        return out

    def work(self, action, reader, body, cancel, *, run_id=None):
        if not self._gate.acquire(blocking=False):
            raise ForecastError("FORECAST_BUSY")
        started = self.monotonic()

        def check():
            if cancel.is_set():
                raise ForecastError("FORECAST_CANCELLED")
            if self.monotonic() - started > self.timeout:
                raise ForecastError("FORECAST_TIMEOUT")

        try:
            self._purge()
            while self._calls and started - self._calls[0] > 60:
                self._calls.popleft()
            if len(self._calls) >= 30:
                raise ForecastError("FORECAST_RATE_LIMITED")
            self._calls.append(started)
            check()
            if body.basis != "PROVIDER_ADJUSTED":
                raise ForecastError("FORECAST_BASIS_NOT_SUPPORTED")
            now = self.market.clock()
            view = self._view(reader, now)
            check()
            if body.expected_revision and body.expected_revision != view.metadata["revision"]:
                raise ForecastError("FORECAST_SOURCE_SNAPSHOT_CHANGED")
            view.metadata["horizons"] = self._horizons(view, now)
            if action == "context":
                return view.metadata
            if action == "run":
                return self._run(view, body, now, check)
            if action == "evaluate":
                return self._evaluate(view, body, now, check)
            if action == "track":
                return self._track(view, str(run_id), now, check)
            raise ForecastError("UNSUPPORTED_FORECAST_ACTION")
        finally:
            self._gate.release()

    def _request(self, view, body, model, now):
        if not view.dataset.observations:
            raise ForecastError("INSUFFICIENT_FINAL_DAILY_DATA")
        kind = MarketRequest if isinstance(view.dataset, MarketDataset) else ForecastRequest
        config = (
            (Setting(name="annualization_sessions", value=body.annualization_sessions),)
            if model == "B03" and body.annualization_sessions
            else ()
        )
        return kind(
            instrument=view.dataset.instrument,
            origin_session=view.dataset.observations[-1].session_date,
            horizon=body.horizon,
            lookback=body.lookback,
            model_id=model,
            configuration=config,
            cutoff=now,
        )

    def _run(self, view, body, now, check):
        horizon = next(h for h in view.metadata["horizons"] if h["horizon"] == body.horizon)
        results = []
        shared_snapshot = None
        for model in body.models:
            check()
            try:
                if horizon["reason"]:
                    raise ForecastError(horizon["reason"])
                q = self._request(view, body, model, now)
                if shared_snapshot is None:
                    shared_snapshot = build_snapshot(view.dataset, q)
                snapshot = shared_snapshot
                result = get_model(model).predict(snapshot, q, created_at=now)
                absolute_change, percentage_change = display_changes(result)
                results.append(
                    {
                        "model_id": model,
                        "status": "AVAILABLE",
                        "reason": None,
                        "forecast": result.model_dump(mode="json"),
                        "display_change": {
                            "absolute_change": absolute_change,
                            "percentage_change": percentage_change,
                        },
                    }
                )
            except ForecastError as exc:
                results.append(
                    {
                        "model_id": model,
                        "status": "UNAVAILABLE",
                        "reason": exc.code,
                        "forecast": None,
                    }
                )
        check()
        run_id = str(uuid4())
        payload = {
            "run_id": run_id,
            "status": "AVAILABLE"
            if all(r["forecast"] for r in results)
            else "PARTIAL"
            if any(r["forecast"] for r in results)
            else "UNAVAILABLE",
            "computed_at": now.isoformat(),
            "cutoff": now.isoformat(),
            "horizon": body.horizon,
            "lookback": body.lookback,
            "target_session": horizon["target_session"],
            "context": view.metadata,
            "results": results,
            "retention": "PROCESS_SCOPED_32_RUNS_TARGET_PLUS_7_DAYS_MAX_365_DAYS_RESTART_LOSES_TRACKING",
            "calibration_status": "NOT_SUPPORTED",
        }
        stored = deepcopy(payload)
        stored["context"].pop("history", None)
        refs = view.references[-body.lookback :]
        with self._records_lock:
            target_date = (
                date.fromisoformat(payload["target_session"]) if payload["target_session"] else None
            )
            days = max(7, (target_date - now.astimezone(IST).date()).days + 7) if target_date else 1
            expires_at = self.monotonic() + min(365, days) * 86400
            self._runs[run_id] = {
                "expires_at": expires_at,
                "stored_at": self.monotonic(),
                "options": body,
                "payload": stored,
                "input_references": refs,
            }
            while len(self._runs) > 32:
                self._runs.popitem(last=False)
        return payload

    def _evaluate(self, view, body, now, check):
        real = isinstance(view.dataset, MarketDataset)
        replay = body.evaluation_mode == MODE
        if (real and body.evaluation_mode == "SYNTHETIC") or (
            not real and body.evaluation_mode != "SYNTHETIC"
        ):
            raise ForecastError("EVALUATION_MODE_SOURCE_MISMATCH")
        if replay and (
            body.acknowledge_replay_assumptions is not True or body.replay_policy != POLICY
        ):
            raise ForecastError("CONDITIONAL_REPLAY_ACKNOWLEDGEMENT_REQUIRED")
        if not replay and (body.acknowledge_replay_assumptions or body.replay_policy is not None):
            raise ForecastError("REPLAY_ASSUMPTIONS_INVALID_FOR_MODE")
        if not body.start or not body.end or body.end > now.astimezone(IST).date():
            raise ForecastError("EVALUATION_DATES_REQUIRED_OR_FUTURE")
        sessions = [
            s for s in view.dataset.calendar.sessions if body.start <= s.session_date <= body.end
        ][:: body.frequency]
        if len(sessions) > 80:
            raise ForecastError("EVALUATION_ORIGIN_LIMIT_USE_LOWER_FREQUENCY")
        if not sessions:
            return {
                "evaluation_mode": body.evaluation_mode,
                "status": "DATA_QUALITY_BLOCKED",
                "reason": "NO_REVIEWED_CALENDAR_SESSIONS",
                "context": view.metadata,
                "experiment": None,
                "rows": [],
                "sample_count": 0,
            }
        cls = ReplayEvaluationSpec if replay else MarketEvaluationSpec if real else EvaluationSpec
        runs = tuple(
            ModelRun(
                model_id=m,
                configuration=(
                    Setting(name="annualization_sessions", value=body.annualization_sessions),
                )
                if m == "B03" and body.annualization_sessions
                else (),
            )
            for m in body.models
        )
        spec = cls(
            horizon=body.horizon,
            lookback=body.lookback,
            origins=tuple(
                ForecastOrigin(session=s.session_date, cutoff=s.close_at + timedelta(minutes=30))
                for s in sessions
            ),
            models=runs,
            evaluation_cutoff=now,
            **(
                {
                    "assumption_policy": POLICY,
                    "known_break_sessions": tuple(
                        date.fromisoformat(d)
                        for d in view.metadata["qualification"]["adjustments"]["declared_breaks"]
                    ),
                }
                if replay
                else {}
            ),
            **(
                {"blocked_target_sessions": tuple(view.unknown_target_times)}
                if isinstance(view.dataset, MarketDataset)
                else {}
            ),
        )
        result = evaluate(
            view.dataset, spec, executed_at=now, check=check, regime_analysis=body.regime_analysis
        )
        performance = analyze(
            result,
            instrument=view.dataset.instrument,
            basis=view.dataset.basis,
            calendar=view.dataset.calendar,
            descriptors={m.model_id: get_model(m.model_id).descriptor for m in spec.models},
            start=body.start,
            end=body.end,
            qualification=view.metadata["qualification"]["status"],
            limitations=view.metadata["limitations"],
            rolling_window=body.rolling_error_window,
            check=check,
        )
        encoded = performance.model_dump(mode="json")
        key = fingerprint(
            {"experiment": result.experiment_id, "rolling_window": body.rolling_error_window}
        )
        with self._records_lock:
            self._performance[key] = {
                "expires_at": self.monotonic() + 3600,
                "record": {
                    "registry_id": key,
                    "computed_at": now.isoformat(),
                    "cards": encoded["cards"],
                    "comparison": encoded["comparison"],
                },
            }
            self._performance.move_to_end(key)
            while len(self._performance) > 32:
                self._performance.popitem(last=False)
        check()
        rows = []
        for e in result.forecasts:
            c = e.metric_case
            f = e.forecast
            with context():
                error = (
                    derived(c.predicted_price - c.actual_price)
                    if c and c.predicted_price is not None
                    else None
                )
            rows.append(
                {
                    "evaluation_mode": body.evaluation_mode,
                    "forecast_id": f.forecast_id,
                    "model_id": f.model.model_id,
                    "model_version": f.model.version,
                    "origin": str(f.origin_session),
                    "target": str(f.target_session),
                    "cutoff": f.cutoff.isoformat(),
                    "created_at": f.created_at.isoformat(),
                    "dataset_fingerprint": f.dataset_fingerprint,
                    "status": e.outcome_status,
                    "reason": e.outcome_reason,
                    "predicted_price": format(f.predicted_price, "f")
                    if f.predicted_price is not None
                    else None,
                    "actual_price": format(c.actual_price, "f") if c else None,
                    "price_error": format(error, "f") if error is not None else None,
                }
            )
        exclusions = [
            {"model_id": x.model_id, "origin": str(x.origin_session), "reason": x.reason}
            for x in result.exclusions
        ]
        return {
            "performance": encoded,
            "evaluation_mode": body.evaluation_mode,
            "assumption_policy": POLICY if replay else None,
            "assumptions": list(ASSUMPTIONS)
            if replay
            else ["ACTUAL_LOCAL_FIRST_SEEN_AND_METADATA_KNOWN_BY_CUTOFF_REQUIRED"]
            if real
            else ["EXPLICIT_SYNTHETIC_TEST_ONLY"],
            "qualification_status": view.metadata["qualification"]["status"],
            "status": "AVAILABLE" if result.matured_unique_origins else "DATA_QUALITY_BLOCKED",
            "reason": None if result.matured_unique_origins else "NO_MATURED_ELIGIBLE_CUTOFFS",
            "context": view.metadata,
            "experiment": {
                "experiment_id": result.experiment_id,
                "executed_at": result.executed_at.isoformat(),
                "dataset_fingerprint": result.dataset_fingerprint,
                "classification": body.evaluation_mode,
                "legacy_engine_classification": result.classification,
                "engine_version": result.engine_version,
                "evaluation_mode": body.evaluation_mode,
                "assumption_policy": POLICY if replay else None,
                "metrics_version": result.metrics_version,
                "requested_period": {"start": str(body.start), "end": str(body.end)},
                "frequency_sessions": body.frequency,
                "horizon": body.horizon,
                "lookback": body.lookback,
                "submitted_origins": result.submitted_origin_count,
                "matured_unique_origins": result.matured_unique_origins,
                "overlapping_pairs": result.overlapping_matured_window_pairs,
                "disjoint_windows": result.max_disjoint_matured_windows,
                "evaluations": [x.model_dump(mode="json") for x in result.evaluations],
                "warnings": list(result.warnings)
                + (
                    ["EVALUATION_PERIOD_OUTSIDE_REVIEWED_CALENDAR_UNCOUNTED_SESSIONS"]
                    if body.start < view.dataset.calendar.coverage_start
                    or body.end > view.dataset.calendar.coverage_end
                    else []
                ),
            },
            "rows": rows,
            "exclusions": exclusions,
            "sample_count": result.matured_unique_origins,
        }

    def _track(self, view, run_id, now, check):
        with self._records_lock:
            rec = self._runs.get(run_id)
            if rec is None:
                raise ForecastError("TRACKING_NOT_FOUND_OR_EXPIRED")
            original = deepcopy(rec["payload"])
            refs = rec["input_references"]
        current = {d: (i, h) for d, i, h in view.references}
        changed = any(current.get(d) != (i, h) for d, i, h in refs)
        pool = {r.session_date: r for r in view.dataset.observations}
        sessions = view.dataset.calendar.sessions
        known_profile = getattr(view.dataset.provenance, "source_profile_fingerprint", None)
        if any(
            r["forecast"]
            and r["forecast"]["provenance"].get("source_profile_fingerprint") != known_profile
            for r in original["results"]
        ):
            changed = True
        original["context"]["history"] = chart_history(
            [
                p
                for p in view.dataset.observations
                if not changed and p.session_date in {d for d, _, _ in refs[-120:]}
            ]
        )
        tracking = []
        for r in original["results"]:
            check()
            f = r["forecast"]
            state = "INSUFFICIENT_DATA"
            reason = r["reason"]
            actual = error = rv_error = None
            if f:
                target = date.fromisoformat(f["target_session"])
                origin = date.fromisoformat(f["origin_session"])
                target_slot = next((s for s in sessions if s.session_date == target), None)
                if changed:
                    state, reason = (
                        "DATA_QUALITY_BLOCKED",
                        "INPUT_REVISED_OR_UNAVAILABLE_SINCE_FORECAST",
                    )
                elif target_slot is None:
                    state, reason = "DATA_QUALITY_BLOCKED", "TARGET_CALENDAR_UNAVAILABLE"
                elif target_slot.close_at > now:
                    state, reason = "PENDING", "TARGET_SESSION_NOT_COMPLETE"
                elif target not in pool:
                    state, reason = "MATURED", "AWAITING_FINAL_DAILY_OBSERVATION"
                else:
                    path = [s for s in sessions if origin < s.session_date <= target]
                    if origin not in pool or any(s.session_date not in pool for s in path):
                        state, reason = "INSUFFICIENT_DATA", "MISSING_REALIZED_PATH"
                    elif any(pool[s.session_date].available_at > now for s in path):
                        state, reason = "MATURED", "OUTCOME_NOT_AVAILABLE"
                    else:
                        with context():
                            actual = pool[target].close
                            if f["predicted_price"] is not None:
                                error = derived(Decimal(f["predicted_price"]) - actual)
                            else:
                                returns = simple_returns(
                                    (pool[origin].close,)
                                    + tuple(pool[s.session_date].close for s in path)
                                )
                                rv = sum((x * x for x in returns), Decimal(0)).sqrt()
                                rv_error = derived(Decimal(f["horizon_volatility"]) - rv)
                        state, reason = "EVALUATED", None
            tracking.append(
                {
                    "model_id": r["model_id"],
                    "status": state,
                    "reason": reason,
                    "actual_close": format(actual, "f") if actual is not None else None,
                    "price_error": format(error, "f") if error is not None else None,
                    "volatility_proxy_error": format(rv_error, "f")
                    if rv_error is not None
                    else None,
                }
            )
        return {
            "run_id": run_id,
            "original_run": original,
            "computed_at": now.isoformat(),
            "original_created_at": original["computed_at"],
            "tracking": tracking,
            "retention": original["retention"],
            "limitations": view.metadata["limitations"],
        }
