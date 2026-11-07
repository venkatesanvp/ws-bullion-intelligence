"""As-of dataset eligibility. Synthetic-only, immutable selected views, no I/O."""

from datetime import datetime
from pydantic import ValidationError
from .forecast_market_contracts import MarketDataset, MarketRequest, MarketSnapshot
from .forecast_contracts import (
    ForecastDataset,
    ForecastRequest,
    ForecastSnapshot,
    ForecastError,
    fingerprint,
    utc,
)


def validated(dataset, request):
    try:
        kind = MarketDataset if type(dataset) is MarketDataset else ForecastDataset
        request_kind = MarketRequest if kind is MarketDataset else ForecastRequest
        dataset = kind.model_validate(dataset.model_dump())
        request = request_kind.model_validate(request.model_dump())
    except (ValidationError, AttributeError, ValueError):
        raise ForecastError("INVALID_DATASET_OR_REQUEST") from None
    return dataset, request


def build_snapshot(dataset: ForecastDataset, request: ForecastRequest) -> ForecastSnapshot:
    dataset, request = validated(dataset, request)
    return _build_snapshot_validated(dataset, request)


def _build_snapshot_validated(dataset, request):
    """Internal entry for an already validated immutable dataset/request, never an API bypass."""
    if request.instrument != dataset.instrument or request.timeframe != dataset.timeframe:
        raise ForecastError("IDENTITY_OR_TIMEFRAME_MISMATCH")
    calendar = dataset.calendar
    if calendar.known_at > request.cutoff or dataset.provenance.known_at > request.cutoff:
        raise ForecastError("METADATA_NOT_AVAILABLE")
    days = [s.session_date for s in calendar.sessions]
    if request.origin_session not in days:
        raise ForecastError("ORIGIN_NOT_TRADING_SESSION")
    index = days.index(request.origin_session)
    closed = [s for s in calendar.sessions if s.close_at <= request.cutoff]
    if isinstance(request, MarketRequest):
        lag = len([s for s in closed if s.session_date > request.origin_session])
        if (
            not closed
            or request.origin_session > closed[-1].session_date
            or lag > request.max_origin_lag_sessions
        ):
            raise ForecastError("LATEST_FINAL_ORIGIN_TOO_STALE")
        newer = [
            r
            for r in dataset.observations
            if r.session_date > request.origin_session and r.available_at <= request.cutoff
        ]
        if newer:
            raise ForecastError("NEWER_FINAL_OBSERVATION_AVAILABLE")
    elif not closed or closed[-1].session_date != request.origin_session:
        raise ForecastError("ORIGIN_NOT_LATEST_COMPLETED_SESSION")
    if index + request.horizon >= len(days):
        raise ForecastError("HORIZON_OUTSIDE_CALENDAR")
    target = calendar.sessions[index + request.horizon]
    if target.close_at <= request.cutoff:
        raise ForecastError("TARGET_NOT_FUTURE")
    if index + 1 < request.lookback:
        raise ForecastError("INSUFFICIENT_LOOKBACK")
    if dataset.adjustment_vintage_at and dataset.adjustment_vintage_at > request.cutoff:
        raise ForecastError("ADJUSTMENT_VINTAGE_NOT_AVAILABLE")
    context = calendar.sessions[index - request.lookback + 1 : index + 1]
    dates = {s.session_date for s in context}
    # Filter availability before handing observations to any model. Future prices never enter hashes.
    available = {
        r.session_date: r
        for r in dataset.observations
        if r.available_at <= request.cutoff and r.session_date in dates
    }
    if any(s.session_date not in available for s in context):
        raise ForecastError("MISSING_OR_UNAVAILABLE_SESSION")
    if dataset.basis == "RAW_CLOSE" and any(
        a.available_at <= request.cutoff
        and context[0].session_date < a.effective_session <= request.origin_session
        for a in dataset.corporate_actions
    ):
        raise ForecastError("UNADJUSTED_CORPORATE_ACTION")
    rows = tuple(available[s.session_date] for s in context)
    if any(not r.completed for r in rows):
        raise ForecastError("INCOMPLETE_CANDLE")
    if any(r.quality != request.quality.quality for r in rows):
        raise ForecastError("QUALITY_REQUIREMENT_FAILED")
    lag = request.quality.max_publication_delay_seconds
    if lag is not None and any(
        (r.available_at - r.observed_at).total_seconds() > lag for r in rows
    ):
        raise ForecastError("PUBLICATION_DELAY_EXCEEDED")
    snapshot_type = MarketSnapshot if isinstance(dataset, MarketDataset) else ForecastSnapshot
    return snapshot_type(
        instrument=dataset.instrument,
        origin_session=request.origin_session,
        target_session=target,
        horizon=request.horizon,
        lookback=request.lookback,
        cutoff=request.cutoff,
        calendar_id=calendar.calendar_id,
        calendar_version=calendar.version,
        calendar_fingerprint=fingerprint(calendar),
        context_sessions=context,
        observations=rows,
        provenance=dataset.provenance,
        basis=dataset.basis,
        adjustment_policy_id=dataset.adjustment_policy_id,
        adjustment_vintage_at=dataset.adjustment_vintage_at,
        quality=request.quality,
    )


def visible_dataset_fingerprint(dataset: ForecastDataset, cutoff: datetime):
    """Experiment view: no beyond-assessment observations or event announcements."""
    cutoff = utc(cutoff)
    if dataset.calendar.known_at > cutoff or dataset.provenance.known_at > cutoff:
        raise ForecastError("METADATA_NOT_AVAILABLE")
    return fingerprint(
        {
            "instrument": dataset.instrument,
            "calendar": dataset.calendar,
            "provenance": dataset.provenance,
            "basis": dataset.basis,
            "adjustment_policy": dataset.adjustment_policy_id,
            "adjustment_vintage": dataset.adjustment_vintage_at,
            "observations": tuple(r for r in dataset.observations if r.available_at <= cutoff),
            "corporate_actions": tuple(
                a for a in dataset.corporate_actions if a.available_at <= cutoff
            ),
        }
    )
