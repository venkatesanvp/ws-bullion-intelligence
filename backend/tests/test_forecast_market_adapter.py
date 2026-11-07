from datetime import timedelta
from decimal import Decimal
from copy import copy
import pytest
from pydantic import ValidationError
from app.forecast_market_adapter import adapt, calendar_view
from app.forecast_market_contracts import MarketDataset, MarketRequest
from app.forecast_contracts import ForecastDataset, ForecastError
from app.forecast_dataset import build_snapshot
from app.forecast_baselines import get_model
from .forecast_research_fixtures import service_fixture


@pytest.mark.parametrize("index", range(4))
def test_four_primary_mappings_preserve_exact_values_ids_null_times_and_limited_quality(index):
    service, reader, body, _, clock, _, cal = service_fixture(index=index)
    i, s, rows = reader()
    v = adapt(
        i, s, rows, listings=service.market.provider.listings(), now=clock[0], calendar_override=cal
    )
    assert isinstance(v.dataset, MarketDataset) and v.metadata["eligible_observations"] == 180
    p = v.dataset.observations[-1]
    r = rows[-1]
    assert (
        p.close == r.close
        and p.available_at == r.ingested_at
        and p.source_event_at is None
        and p.provider_published_at is None
    )
    assert (
        p.canonical_id == str(r.id)
        and p.canonical_hash == r.canonical_hash
        and p.batch_id == str(r.batch_id)
    )
    assert (
        p.quality == "CONDITIONAL_OWNER_RESEARCH"
        and v.dataset.basis == "PROVIDER_ADJUSTED_UNVERIFIED"
    )
    q = MarketRequest(
        instrument=v.dataset.instrument,
        origin_session=p.session_date,
        horizon=5,
        lookback=60,
        model_id="B02",
        cutoff=clock[0],
    )
    out = get_model("B02").predict(build_snapshot(v.dataset, q), q, created_at=clock[0])
    assert (
        out.data_quality == "CONDITIONAL_OWNER_RESEARCH"
        and out.provenance.data_class == "REAL_MARKET"
        and out.model.lifecycle == "TRANSIENT_CONDITIONAL_REAL_RESEARCH_ONLY"
    )
    assert "SYNTHETIC_ONLY" not in " ".join(out.warnings)
    # Existing synthetic-only constructor still cannot be used to launder real provenance.
    with pytest.raises(ValidationError):
        ForecastDataset.model_validate(v.dataset.model_dump())


@pytest.mark.parametrize(
    "defect,code",
    [
        ("symbol", "MISMATCHED"),
        ("permission", "NOT_AUTHORIZED"),
        ("duplicate", "DUPLICATE"),
        ("missing_stamp", ""),
        ("partial_ohlc", "INVALID_CANONICAL"),
        ("float", "INVALID_CANONICAL"),
        ("inconsistent", "INVALID_CANONICAL"),
    ],
)
def test_adapter_rejects_bad_identity_permissions_structure_and_numbers(defect, code):
    service, reader, body, ref, clock, _, cal = service_fixture()
    i, s, rows = reader()
    if defect == "symbol":
        i = copy(i)
        i.symbol = "WRONG"
    if defect == "permission":
        s = copy(s)
        s.permitted_uses = {}
    if defect == "duplicate":
        rows = rows + (rows[-1],)
    if defect in {"missing_stamp", "partial_ohlc", "float", "inconsistent"}:
        rs = list(rows)
        r = copy(rs[-1])
        rs[-1] = r
        rows = tuple(rs)
        if defect == "missing_stamp":
            r.ingested_at = None
        if defect == "partial_ohlc":
            r.high = None
        if defect == "float":
            r.close = 100.0
        if defect == "inconsistent":
            r.low = Decimal(999)
    if defect == "missing_stamp":
        v = adapt(
            i,
            s,
            rows,
            listings=service.market.provider.listings(),
            now=clock[0],
            calendar_override=cal,
        )
        assert v.metadata["excluded_observations"]["missing_first_seen"] == 1
    else:
        with pytest.raises(ForecastError, match=code):
            adapt(
                i,
                s,
                rows,
                listings=service.market.provider.listings(),
                now=clock[0],
                calendar_override=cal,
            )


def test_current_date_and_unknown_availability_are_excluded_not_imputed():
    service, reader, body, _, clock, _, cal = service_fixture()
    i, s, rows = reader()
    r = copy(rows[-1])
    clock[0] = r.ingested_at
    v = adapt(
        i, s, rows, listings=service.market.provider.listings(), now=clock[0], calendar_override=cal
    )
    assert (
        v.metadata["excluded_observations"]["not_final_daily"] == 1
        and len(v.dataset.observations) == 179
    )
    assert all(p.session_date < clock[0].date() for p in v.dataset.observations)


def test_real_historical_cutoff_cannot_use_later_first_seen_or_review():
    service, reader, body, _, clock, _, cal = service_fixture()
    i, s, rows = reader()
    rs = list(rows)
    r = copy(rs[100])
    r.ingested_at = clock[0]
    rs[100] = r
    v = adapt(
        i,
        s,
        tuple(rs),
        listings=service.market.provider.listings(),
        now=clock[0],
        calendar_override=cal,
    )
    q = MarketRequest(
        instrument=v.dataset.instrument,
        origin_session=r.trading_date,
        horizon=5,
        lookback=60,
        model_id="B01",
        cutoff=cal.sessions[100].close_at + timedelta(minutes=30),
    )
    with pytest.raises(ForecastError, match="MISSING_OR_UNAVAILABLE_SESSION"):
        build_snapshot(v.dataset, q)


def test_forecasting_calendar_future_dates_special_session_and_2027_limit():
    profile = {
        "version": "test-reviewed-past",
        "coverage_start": "2026-11-02",
        "coverage_end": "2026-11-06",
        "session_dates": ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"],
    }
    cal, unknown = calendar_view(profile)
    days = {s.session_date.isoformat() for s in cal.sessions}
    assert (
        "2026-11-08" in days
        and "2026-11-10" not in days
        and "2026-11-24" not in days
        and "2026-12-25" not in days
    )
    assert str(cal.coverage_end) == "2026-12-31" and {str(d) for d in unknown} == {"2026-11-08"}
    assert not any(d.startswith("2027") for d in days)


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("naive_first_seen", "INVALID_FIRST_SEEN_TIMESTAMP"),
        ("duplicate_provider_time", "DUPLICATE_PROVIDER_EVENT_TIMESTAMP"),
        ("basis", "MIXED_CANONICAL_PRICE_BASIS"),
    ],
)
def test_original_timestamp_and_basis_integrity_is_not_hidden_by_calendar_proxies(defect, reason):
    service, reader, _, _, clock, _, cal = service_fixture()
    i, s, rows = reader()
    rs = list(rows)
    rs[0] = copy(rs[0])
    rs[1] = copy(rs[1])
    if defect == "naive_first_seen":
        rs[0].ingested_at = rs[0].ingested_at.replace(tzinfo=None)
    if defect == "duplicate_provider_time":
        rs[0].event_time = rs[1].event_time = cal.sessions[0].close_at
    if defect == "basis":
        rs[0].price_basis = "RAW_CLOSE"
    with pytest.raises(ForecastError, match=reason):
        adapt(
            i,
            s,
            tuple(rs),
            listings=service.market.provider.listings(),
            now=clock[0],
            calendar_override=cal,
        )


def test_provider_event_after_local_first_seen_is_rejected_not_reinterpreted():
    service, reader, _, _, clock, _, cal = service_fixture()
    i, s, rows = reader()
    rs = list(rows)
    rs[0] = copy(rs[0])
    rs[0].event_time = rs[0].ingested_at + timedelta(seconds=1)
    with pytest.raises(ForecastError, match="CANONICAL_TIMESTAMP_AFTER_FIRST_SEEN"):
        adapt(
            i,
            s,
            tuple(rs),
            listings=service.market.provider.listings(),
            now=clock[0],
            calendar_override=cal,
        )
