"""Explicit fixed-vintage retrospective context; never a strict-PIT availability claim."""

from typing import Literal
from pydantic import model_validator
from .forecast_contracts import Stamp, ForecastError, HORIZONS, fingerprint
from .forecast_market_contracts import MarketRequest, MarketSnapshot, MarketResult

POLICY = "FIXED_RETRIEVED_VINTAGE_V1"
MODE = "CONDITIONAL_HISTORICAL_REPLAY"
ASSUMPTIONS = (
    "RETROSPECTIVE_FIXED_RETRIEVED_VINTAGE_NOT_VERIFIED_LIVE_PERFORMANCE",
    "HISTORICAL_PROVIDER_AVAILABILITY_NOT_VERIFIED",
    "CALENDAR_AND_SOURCE_REVIEWED_AT_ASSESSMENT_NOT_HISTORICAL_CUTOFF",
    "PRIOR_DATE_DAILY_COMPLETED_CANDIDATES_NOT_INDEPENDENTLY_FINAL_CERTIFIED",
    "PROVIDER_ADJUSTMENTS_AND_REVISIONS_MAY_EMBED_LATER_INFORMATION",
    "NO_DIRECT_FUTURE_TARGET_ROWS_IN_MODEL_CONTEXT",
    "KNOWN_BREAKS_EXCLUDED_UNKNOWN_ACTIONS_AND_REVISIONS_REMAIN_UNQUALIFIED",
    "PRICE_ONLY_NOT_TOTAL_RETURN_OR_EXECUTABLE_STRATEGY_PERFORMANCE",
)


class ReplayRequest(MarketRequest):
    evaluation_mode: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    assumption_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"]
    assessment_cutoff: Stamp


class ReplaySnapshot(MarketSnapshot):
    evaluation_mode: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    assumption_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"]
    assessment_cutoff: Stamp

    @model_validator(mode="after")
    def coherent(self):
        # Deliberately separate validator; strict MarketSnapshot remains unchanged.
        if (
            self.horizon not in HORIZONS
            or len(self.observations) != self.lookback
            or len(self.context_sessions) != self.lookback
        ):
            raise ValueError("INVALID_CONTEXT_LENGTH")
        days = [r.session_date for r in self.observations]
        if (
            not days
            or days[-1] != self.origin_session
            or days != sorted(set(days))
            or days != [s.session_date for s in self.context_sessions]
        ):
            raise ValueError("NONCONTIGUOUS_REPLAY_CONTEXT")
        if self.target_session.close_at <= self.cutoff or self.assessment_cutoff < self.cutoff:
            raise ValueError("INVALID_REPLAY_CUTOFF")
        if (
            self.provenance.known_at > self.assessment_cutoff
            or self.adjustment_vintage_at is not None
        ):
            raise ValueError("REPLAY_METADATA_OR_VINTAGE_UNSUPPORTED")
        if self.quality.max_publication_delay_seconds is not None:
            raise ValueError("REPLAY_CANNOT_ASSERT_PUBLICATION_DELAY")
        for r, s in zip(self.observations, self.context_sessions):
            if (
                r.observed_at != s.close_at
                or s.close_at > self.cutoff
                or r.available_at > self.assessment_cutoff
            ):
                raise ValueError("REPLAY_CONTEXT_UNAVAILABLE_AT_ASSESSMENT")
            if not r.completed or r.quality != self.quality.quality:
                raise ValueError("INELIGIBLE_CONTEXT")
        return self


class ReplayResult(MarketResult):
    contract_version: Literal["forecast-conditional-replay-v1"] = "forecast-conditional-replay-v1"
    evaluation_mode: Literal["CONDITIONAL_HISTORICAL_REPLAY"] = MODE
    assumption_policy: Literal["FIXED_RETRIEVED_VINTAGE_V1"]
    assessment_cutoff: Stamp


def replay_snapshot(dataset, request):
    cal = dataset.calendar
    if request.instrument != dataset.instrument or request.timeframe != dataset.timeframe:
        raise ForecastError("IDENTITY_OR_TIMEFRAME_MISMATCH")
    if (
        cal.known_at > request.assessment_cutoff
        or dataset.provenance.known_at > request.assessment_cutoff
    ):
        raise ForecastError("METADATA_NOT_AVAILABLE_AT_ASSESSMENT")
    if dataset.basis != "PROVIDER_ADJUSTED_UNVERIFIED" or dataset.adjustment_vintage_at is not None:
        raise ForecastError("REPLAY_BASIS_OR_VINTAGE_UNSUPPORTED")
    days = [s.session_date for s in cal.sessions]
    if request.origin_session not in days:
        raise ForecastError("ORIGIN_NOT_TRADING_SESSION")
    idx = days.index(request.origin_session)
    closed = [s for s in cal.sessions if s.close_at <= request.cutoff]
    if not closed or closed[-1].session_date != request.origin_session:
        raise ForecastError("ORIGIN_NOT_LATEST_COMPLETED_SESSION")
    if idx + request.horizon >= len(days):
        raise ForecastError("HORIZON_OUTSIDE_CALENDAR")
    if idx + 1 < request.lookback:
        raise ForecastError("INSUFFICIENT_LOOKBACK")
    slots = cal.sessions[idx - request.lookback + 1 : idx + 1]
    pool = {
        r.session_date: r
        for r in dataset.observations
        if r.available_at <= request.assessment_cutoff and r.session_date <= request.origin_session
    }
    if any(s.session_date not in pool for s in slots):
        raise ForecastError("MISSING_OR_UNAVAILABLE_SESSION")
    if any(not pool[s.session_date].completed for s in slots):
        raise ForecastError("INCOMPLETE_CANDLE")
    if any(pool[s.session_date].quality != request.quality.quality for s in slots):
        raise ForecastError("QUALITY_REQUIREMENT_FAILED")
    if request.quality.max_publication_delay_seconds is not None:
        raise ForecastError("REPLAY_CANNOT_ASSERT_PUBLICATION_DELAY")
    return ReplaySnapshot(
        instrument=dataset.instrument,
        origin_session=request.origin_session,
        target_session=cal.sessions[idx + request.horizon],
        horizon=request.horizon,
        lookback=request.lookback,
        cutoff=request.cutoff,
        calendar_id=cal.calendar_id,
        calendar_version=cal.version,
        calendar_fingerprint=fingerprint(cal),
        context_sessions=slots,
        observations=tuple(pool[s.session_date] for s in slots),
        provenance=dataset.provenance,
        basis=dataset.basis,
        adjustment_policy_id=dataset.adjustment_policy_id,
        adjustment_vintage_at=dataset.adjustment_vintage_at,
        quality=request.quality,
        assumption_policy=request.assumption_policy,
        assessment_cutoff=request.assessment_cutoff,
    )
