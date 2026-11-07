from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.forecast_contracts import (
    ForecastDataset,
    ForecastObservation,
    TradingCalendar,
    CorporateAction,
    QualityRequirements,
    ForecastRequest,
    Setting,
    ForecastError,
)
from app.forecast_dataset import build_snapshot
from .forecast_fixtures import dataset, request


def change(data, **values):
    return ForecastDataset.model_validate({**data.model_dump(), **values})


def row_change(data, index, **values):
    rows = list(data.observations)
    rows[index] = ForecastObservation.model_validate({**rows[index].model_dump(), **values})
    return change(data, observations=tuple(rows))


@pytest.mark.parametrize("horizon", [1, 5, 20, 60, 120])
def test_calendar_horizons_holidays_and_strict_window(horizon):
    d = dataset()
    q = request(d, index=2, horizon=horizon)
    s = build_snapshot(d, q)
    assert s.target_session == d.calendar.sessions[2 + horizon]
    assert [r.session_date for r in s.observations] == [
        x.session_date for x in d.calendar.sessions[:3]
    ]
    # Artificial holiday Jan4 and weekend are omitted, not treated as missing price sessions.
    assert d.calendar.sessions[3].session_date.isoformat() == "2024-01-05"
    assert s.fingerprint == build_snapshot(d, q).fingerprint
    with pytest.raises(ValidationError):
        s.lookback = 5


def test_unavailable_future_prices_not_visible_and_not_in_forecast_input_hash():
    d = dataset()
    q = request(d, index=10)
    s = build_snapshot(d, q)
    altered = row_change(
        d, 30, open=Decimal(1000), high=Decimal(1000), low=Decimal(1000), close=Decimal(1000)
    )
    assert s == build_snapshot(altered, q)
    assert s.observations[-1].session_date == q.origin_session and len(s.observations) == 3
    assert all(r.available_at <= q.cutoff for r in s.observations)


def test_timezone_normalization_preserves_semantics_and_hash():
    d = dataset()
    q = request(d, index=10)
    same = ForecastRequest.model_validate(
        {**q.model_dump(), "cutoff": q.cutoff.astimezone(timezone(timedelta(hours=5, minutes=30)))}
    )
    assert q == same and build_snapshot(d, q).fingerprint == build_snapshot(d, same).fingerprint
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate({**q.model_dump(), "cutoff": datetime(2024, 1, 1)})


@pytest.mark.parametrize(
    "defect,code",
    [
        ("missing", "MISSING_OR_UNAVAILABLE_SESSION"),
        ("delayed", "MISSING_OR_UNAVAILABLE_SESSION"),
        ("incomplete", "INCOMPLETE_CANDLE"),
        ("quality", "QUALITY_REQUIREMENT_FAILED"),
        ("short", "INSUFFICIENT_LOOKBACK"),
        ("calendar_future", "METADATA_NOT_AVAILABLE"),
        ("stale_origin", "ORIGIN_NOT_LATEST_COMPLETED_SESSION"),
        ("publication_lag", "PUBLICATION_DELAY_EXCEEDED"),
    ],
)
def test_eligibility_rejections(defect, code):
    d = dataset()
    q = request(d, index=10)
    if defect == "missing":
        d = change(d, observations=d.observations[:9] + d.observations[10:])
    if defect == "delayed":
        d = row_change(d, 10, available_at=q.cutoff + timedelta(days=1))
    if defect == "incomplete":
        d = row_change(d, 10, completed=False)
    if defect == "quality":
        d = row_change(d, 10, quality="DEGRADED")
    if defect == "short":
        q = request(d, index=1, lookback=3)
    if defect == "calendar_future":
        d = change(
            d,
            calendar=TradingCalendar.model_validate(
                {**d.calendar.model_dump(), "known_at": q.cutoff + timedelta(days=1)}
            ),
        )
    if defect == "stale_origin":
        q = ForecastRequest.model_validate(
            {**q.model_dump(), "cutoff": d.calendar.sessions[11].close_at + timedelta(hours=1)}
        )
    if defect == "publication_lag":
        q = request(d, index=10, quality=QualityRequirements(max_publication_delay_seconds=60))
    with pytest.raises(ForecastError, match=code):
        build_snapshot(d, q)


def test_delayed_observation_can_be_used_only_after_publication_before_next_close():
    d = dataset()
    q = request(d, index=10)
    publication = q.cutoff + timedelta(hours=1)
    d = row_change(d, 10, available_at=publication)
    with pytest.raises(ForecastError, match="UNAVAILABLE"):
        build_snapshot(d, q)
    later = ForecastRequest.model_validate({**q.model_dump(), "cutoff": publication})
    assert build_snapshot(d, later).observations[-1].available_at == publication


@pytest.mark.parametrize(
    "defect",
    [
        "duplicate",
        "reverse",
        "off_calendar",
        "timestamp",
        "availability",
        "missing_publication",
        "float",
        "boolean_volume",
        "fraction_volume",
        "negative_volume",
        "nan",
        "infinite",
        "ohlc",
        "timezone",
    ],
)
def test_malformed_dataset_rejected_not_corrected(defect):
    d = dataset()
    values = d.model_dump()
    rows = list(values["observations"])
    if defect == "duplicate":
        rows.insert(1, rows[0])
    if defect == "reverse":
        rows.reverse()
    if defect == "off_calendar":
        rows[0]["session_date"] += timedelta(days=3)
    if defect == "timestamp":
        rows[0]["observed_at"] -= timedelta(minutes=1)
    if defect == "availability":
        rows[0]["available_at"] = rows[0]["observed_at"] - timedelta(seconds=1)
    if defect == "missing_publication":
        rows[0].pop("available_at")
    if defect == "float":
        rows[0]["close"] = 100.0
    if defect == "boolean_volume":
        rows[0]["volume"] = True
    if defect == "fraction_volume":
        rows[0]["volume"] = 100.5
    if defect == "negative_volume":
        rows[0]["volume"] = -1
    if defect == "nan":
        rows[0]["close"] = Decimal("NaN")
    if defect == "infinite":
        rows[0]["close"] = Decimal("Infinity")
    if defect == "ohlc":
        rows[0]["low"] = Decimal(101)
    if defect == "timezone":
        rows[0]["observed_at"] = datetime(2024, 1, 1)
    values["observations"] = tuple(rows)
    with pytest.raises(ValidationError):
        ForecastDataset.model_validate(values)


@pytest.mark.parametrize("defect", ["duplicate", "reverse", "zone", "close_date", "coverage"])
def test_calendar_contract_rejections(defect):
    d = dataset()
    values = d.calendar.model_dump()
    sessions = list(values["sessions"])
    if defect == "duplicate":
        sessions.insert(1, sessions[0])
    if defect == "reverse":
        sessions.reverse()
    if defect == "zone":
        values["timezone"] = "Not/AZone"
    if defect == "close_date":
        sessions[0]["close_at"] += timedelta(days=1)
    if defect == "coverage":
        values["coverage_start"] += timedelta(days=3)
    values["sessions"] = tuple(sessions)
    with pytest.raises(ValidationError):
        TradingCalendar.model_validate(values)


def test_adjustment_vintage_and_corporate_action_boundaries():
    d = dataset()
    q = request(d, index=10)
    action = CorporateAction(
        effective_session=d.calendar.sessions[9].session_date,
        available_at=d.calendar.sessions[8].close_at,
        kind="SPLIT",
        evidence_ref="SYNTHETIC_ACTION",
    )
    raw = change(d, corporate_actions=(action,))
    with pytest.raises(ForecastError, match="UNADJUSTED_CORPORATE_ACTION"):
        build_snapshot(raw, q)
    # A complete post-action context needs no invented pre-action adjustment.
    assert (
        build_snapshot(raw, request(raw, index=13)).origin_session
        == raw.calendar.sessions[13].session_date
    )
    vintage = d.calendar.sessions[7].close_at
    rows = tuple(
        ForecastObservation.model_validate(
            {**r.model_dump(), "available_at": max(r.available_at, vintage)}
        )
        for r in d.observations
    )
    adjusted = change(
        d,
        basis="PIT_ADJUSTED_CLOSE",
        adjustment_policy_id="SYNTHETIC_PIT_ADJUSTMENT_V1",
        adjustment_vintage_at=vintage,
        observations=rows,
        corporate_actions=(action,),
    )
    assert build_snapshot(adjusted, q).basis == "PIT_ADJUSTED_CLOSE"
    with pytest.raises(ForecastError, match="ADJUSTMENT_VINTAGE_NOT_AVAILABLE"):
        build_snapshot(adjusted, request(adjusted, index=5))
    with pytest.raises(ValidationError):
        change(d, basis="PIT_ADJUSTED_CLOSE")
    with pytest.raises(ValidationError):
        change(adjusted, observations=d.observations)


@pytest.mark.parametrize(
    "values",
    [
        {"horizon": True},
        {"horizon": 2},
        {"horizon": 5.0},
        {"lookback": 0},
        {"lookback": 1001},
        {"lookback": True},
        {"timeframe": "5m"},
        {"configuration": (Setting(name="x", value=1), Setting(name="x", value=2))},
    ],
)
def test_request_bounds_and_unsupported_contracts(values):
    q = request(dataset())
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate({**q.model_dump(), **values})


def test_real_data_and_quality_relaxation_rejected():
    d = dataset()
    values = d.model_dump()
    values["provenance"]["data_class"] = "REAL_MARKET"
    with pytest.raises(ValidationError):
        ForecastDataset.model_validate(values)
    with pytest.raises(ValidationError):
        QualityRequirements(require_complete=False)
    with pytest.raises(ValidationError):
        QualityRequirements(require_contiguous=False)
    with pytest.raises(ValidationError):
        Setting(name="invalid", value=0.5)
    # model_copy bypasses Pydantic validation; public builder revalidates it.
    tampered = d.model_copy(
        update={"provenance": d.provenance.model_copy(update={"data_class": "REAL_MARKET"})}
    )
    with pytest.raises(ForecastError, match="INVALID_DATASET"):
        build_snapshot(tampered, request(d))


def test_horizon_outside_calendar_and_non_session_origin():
    d = dataset(future=0)
    with pytest.raises(ForecastError, match="HORIZON_OUTSIDE_CALENDAR"):
        build_snapshot(d, request(d))
    q = request(d, index=2)
    q = ForecastRequest.model_validate(
        {**q.model_dump(), "origin_session": q.origin_session + timedelta(days=1)}
    )
    with pytest.raises(ForecastError, match="ORIGIN_NOT_TRADING_SESSION"):
        build_snapshot(d, q)


def test_model_setting_string_payload_is_bounded():
    with pytest.raises(ValidationError):
        Setting(name="bounded", value="x" * 257)
