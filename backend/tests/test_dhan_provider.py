"""Step 5D.1 / DC-02/04, D-14. ALL OHLCV fixtures are synthetic, not market evidence."""

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
import json
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

from app.dhan_config import load_dhan_configuration
from app.dhan_provider import DhanDailyProvider
from app.ingestion import parse_csv
from app.market_data import DailyMarketDataProvider, DailyRequest, Listing
from app.schemas import CalendarProfile, ImportMetadata

TOKEN = "synthetic-provider-token-not-a-real-secret"
DATES = tuple(date(2026, 10, d) for d in range(26, 31))


def config(**updates):
    env = {"DHAN_ACCESS_TOKEN": TOKEN, "DHAN_DATA_API_ENABLED": "true"}
    env.update(updates)
    return load_dhan_configuration(environ=env)


def request(symbol="TATAGOLD", *, calendar=True):
    listing = next(x for x in DhanDailyProvider(config()).listings() if x.symbol == symbol)
    cal = (
        CalendarProfile(
            evidence_ref="SYNTHETIC calendar fixture; not source qualification",
            version="synthetic-v1",
            coverage_start=DATES[0],
            coverage_end=DATES[-1],
            session_dates=list(DATES),
        )
        if calendar
        else None
    )
    return DailyRequest(listing, DATES[0], DATES[-1], cal)


def synthetic(*, decimal=False):
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    stamps = [
        (datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc) - epoch).days * 86400
        for d in DATES
    ]
    data = {
        "open": [10] * 5,
        "high": [12] * 5,
        "low": [9] * 5,
        "close": [11] * 5,
        "volume": [12500] * 5,
        "timestamp": stamps,
    }
    body = json.dumps(data)
    if decimal:
        body = body.replace("12500", "12500.0")
        for stamp in stamps:
            body = body.replace(str(stamp), str(stamp) + ".0")
    return body.encode()


def retrieve(body=None, *, req=None, status=200, content_type="application/json"):
    calls = []

    def handler(r):
        calls.append(r)
        return httpx.Response(
            status,
            content=body if body is not None else synthetic(),
            headers={"Content-Type": content_type},
        )

    provider: DailyMarketDataProvider = DhanDailyProvider(
        config(), transport_factory=lambda: httpx.MockTransport(handler)
    )
    result = provider.retrieve_daily(req or request(), request_approved=True)
    assert len(calls) == 1
    return result, calls[0]


@pytest.mark.parametrize(
    "symbol,security,isin,metal",
    [
        ("TATAGOLD", "21401", "INF277KA1976", "GOLD"),
        ("TATSILV", "21428", "INF277KA1984", "SILVER"),
        ("GOLDBEES", "14428", "INF204KB17I5", "GOLD"),
        ("SILVERBEES", "8080", "INF204KC1402", "SILVER"),
    ],
)
@pytest.mark.parametrize("decimal", [False, True])
def test_four_primary_mappings_and_normalization(symbol, security, isin, metal, decimal):
    result, sent = retrieve(synthetic(decimal=decimal), req=request(symbol))
    assert sent.method == "POST" and str(sent.url) == "https://api.dhan.co/v2/charts/historical"
    assert sent.headers["access-token"] == TOKEN
    assert json.loads(sent.content) == {
        "securityId": security,
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "oi": False,
        "fromDate": "2026-10-26",
        "toDate": "2026-10-31",
    }
    assert sent.extensions["timeout"] == {"connect": 5.0, "read": 10.0, "write": 5.0, "pool": 5.0}
    assert result.status == "VALIDATED_UNQUALIFIED"
    assert len(result.observations) == 5 and result.validation.missing_sessions == ()
    assert result.provenance.listing == Listing("XNSE", symbol, isin, metal)
    assert result.provenance.provider_instrument_id == security
    assert result.provenance.requested_end == DATES[-1]
    assert result.provenance.provider_end_exclusive == date(2026, 10, 31)
    assert result.provenance.retrieved_at.utcoffset() == timedelta(0)
    assert result.provenance.source_qualification == "UNVERIFIED"
    assert not result.provenance.timestamp_semantics_verified
    assert not result.provenance.adjustment_method_verified
    assert result.provenance.replay_status == "UNVERIFIED_FOR_REPLAY"
    assert result.provenance.calendar_version == "synthetic-v1"
    assert result.validation.candidate_dates == DATES
    for i, obs in enumerate(result.observations):
        assert obs.trading_date == DATES[i] and type(obs.close) is Decimal
        assert obs.close == Decimal("11") and type(obs.volume) is int and obs.volume == 12500
        assert obs.event_time is None and obs.provider_published_at is None
        assert obs.event_precision == "SESSION_DATE" and obs.provenance.source_row == i + 1
        assert obs.provenance.batch is result.provenance
        assert obs.provenance.source_timestamp.endswith(".0") is decimal
    counters = {name: dict(values) for name, values in result.validation.numeric_counters}
    for field in ("volume", "timestamp"):
        assert counters[field]["integral_decimal_values" if decimal else "json_integer_values"] == 5


def test_exact_canonical_csv_equivalence_no_quantization():
    body = synthetic().replace(
        b'"close": [11, 11, 11, 11, 11]', b'"close": [11.1234567890, 11, 11, 11, 11]'
    )
    result, _ = retrieve(body)
    obs = result.observations[0]
    metadata = ImportMetadata(
        instrument_id=uuid4(),
        source_id=uuid4(),
        interval="1d",
        price_basis="PROVIDER_ADJUSTED",
        mapping_version="synthetic-v1",
        quality_policy_version="quality-v1",
        qualification_ref="SYNTHETIC",
        column_map={k: k for k in ("trading_date", "open", "high", "low", "close", "volume")},
    )
    csv = b"trading_date,open,high,low,close,volume\n2026-10-26,10,12,9,11.1234567890,12500\n"
    parsed = parse_csv(
        csv,
        metadata,
        SimpleNamespace(symbol="TATAGOLD", currency="INR"),
        SimpleNamespace(profile={}),
        10,
    )
    assert not parsed.errors
    assert obs.canonical_values() == parsed.candidates[DATES[0]][1]
    assert obs.canonical_hash == parsed.candidates[DATES[0]][2]
    with localcontext() as context:
        context.prec = 3
        assert obs.canonical_hash == parsed.candidates[DATES[0]][2]
    assert str(obs.close) == "11.1234567890"


@pytest.mark.parametrize(
    "field,value,issue",
    [
        ("volume", 12500.5, "INVALID_VOLUME"),
        ("volume", -1, "INVALID_VOLUME"),
        ("volume", 2**63, "INVALID_VOLUME"),
        ("volume", True, "INVALID_VOLUME"),
        ("volume", "12500", "INVALID_VOLUME"),
        ("volume", None, "INVALID_VOLUME"),
        ("timestamp", 1792960000.5, "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("timestamp", 0, "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("timestamp", 4102444800, "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("timestamp", 1792960000000, "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("timestamp", "1792960000", "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("timestamp", True, "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE"),
        ("close", 0, "INVALID_PRICE"),
        ("close", -1, "INVALID_PRICE"),
        ("close", 1e14, "INVALID_PRICE"),
        ("close", 1.12345678901, "INVALID_PRICE"),
        ("close", "11", "INVALID_PRICE"),
        ("close", True, "INVALID_PRICE"),
        ("close", 13, "INCONSISTENT_OHLC"),
    ],
)
def test_invalid_values_reject_all_without_repair(field, value, issue):
    data = json.loads(synthetic())
    data[field][0] = value
    result, _ = retrieve(json.dumps(data).encode())
    assert result.failure.code == "INVALID_DATA" and not result.observations
    assert issue in result.validation.issues
    if field == "timestamp":
        assert result.validation.missing_sessions is None
        assert result.validation.duplicate_session_dates is None
        assert "DATE_COVERAGE_UNDETERMINED" in result.validation.issues


@pytest.mark.parametrize(
    "body",
    [
        b"{}",
        b"[]",
        b"null",
        b"broken",
        b"\xff",
        b'{"volume":[],"volume":[]}',
        b'{"close":[NaN]}',
        b'{"close":[Infinity]}',
        b'{"close":[-Infinity]}',
    ],
)
def test_strict_malformed_json_and_structure(body):
    result, _ = retrieve(body)
    assert result.failure.code == "UNEXPECTED_RESPONSE" and not result.observations


@pytest.mark.parametrize("change", ["missing", "extra", "scalar", "mismatch", "overflow"])
def test_array_contract(change):
    data = json.loads(synthetic())
    if change == "missing":
        del data["low"]
    if change == "extra":
        data["account"] = ["do not expose"] * 5
    if change == "scalar":
        data["close"] = 11
    if change == "mismatch":
        data["volume"].pop()
    if change == "overflow":
        data = {k: v * 74 for k, v in data.items()}
    result, _ = retrieve(json.dumps(data).encode())
    assert result.failure.code == (
        "OBSERVATION_LIMIT_EXCEEDED" if change == "overflow" else "UNEXPECTED_RESPONSE"
    )
    assert not result.observations


@pytest.mark.parametrize("value,valid", [(0, True), (0.0, True), (1, False), (0.5, False)])
def test_optional_oi_is_zero_only(value, valid):
    data = json.loads(synthetic())
    data["open_interest"] = [value] * 5
    result, _ = retrieve(json.dumps(data).encode())
    assert bool(result.observations) is valid
    if not valid:
        assert "UNEXPECTED_OPEN_INTEREST" in result.validation.issues


def test_missing_sessions_retained_as_gap_never_filled():
    data = json.loads(synthetic())
    data = {k: v[:2] + v[3:] for k, v in data.items()}
    result, _ = retrieve(json.dumps(data).encode())
    assert result.status == "VALIDATED_WITH_GAPS_UNQUALIFIED" and len(result.observations) == 4
    assert result.validation.missing_sessions == (DATES[2],)
    assert result.validation.issues == ("MISSING_OBSERVATIONS",)


def test_no_calendar_never_invents_completeness():
    result, _ = retrieve(req=request(calendar=False))
    assert len(result.observations) == 5
    assert result.validation.missing_sessions is None
    assert result.validation.calendar_assessment == "UNASSESSED"
    assert "CALENDAR_UNASSESSED" in result.provenance.limitations


@pytest.mark.parametrize("calendar", [True, False])
def test_empty_response(calendar):
    result, _ = retrieve(
        json.dumps({k: [] for k in json.loads(synthetic())}).encode(),
        req=request(calendar=calendar),
    )
    assert result.status == "EMPTY_UNQUALIFIED" and not result.observations
    assert result.validation.missing_sessions == (DATES if calendar else None)


@pytest.mark.parametrize("same_epoch", [True, False])
def test_duplicate_candidate_sessions(same_epoch):
    data = json.loads(synthetic())
    data["timestamp"][1] = data["timestamp"][0] + (0 if same_epoch else 3600)
    result, _ = retrieve(json.dumps(data).encode())
    assert result.failure.code == "INVALID_DATA" and not result.observations
    assert result.validation.duplicate_session_dates == 1
    assert result.validation.duplicate_timestamps == int(same_epoch)


def test_out_of_order_normalizes_retaining_source_rows():
    data = json.loads(synthetic())
    data = {k: list(reversed(v)) for k, v in data.items()}
    result, _ = retrieve(json.dumps(data).encode())
    assert result.validation.candidate_dates == DATES
    assert result.observations[0].provenance.source_row == 5
    assert result.validation.issues == ("OUT_OF_ORDER_NORMALIZED",)


def test_outside_requested_date_rejected_and_no_unit_guessing():
    data = json.loads(synthetic())
    data["timestamp"][0] -= 86400
    result, _ = retrieve(json.dumps(data).encode())
    assert "DATE_OUTSIDE_REQUEST" in result.validation.issues
    assert "NON_TRADING_DATE" in result.validation.issues
    assert not result.observations


def test_nse_ist_day_boundary_and_provisional_policy():
    data = json.loads(synthetic())
    data["timestamp"] = [v - 5 * 3600 for v in data["timestamp"]]  # Prior UTC date, same IST date.
    result, _ = retrieve(json.dumps(data).encode())
    assert result.validation.candidate_dates == DATES
    assert not result.provenance.timestamp_semantics_verified
    assert result.provenance.timestamp_policy == "UNIX_SECONDS_IST_CANDIDATE_V1"
    assert result.provenance.exchange_timezone == "Asia/Kolkata"


def test_mapping_failure_not_reported_as_missing(monkeypatch):
    def broken(_):
        raise OverflowError("synthetic confidential exception")

    monkeypatch.setattr("app.dhan_provider._candidate_nse_date", broken)
    result, _ = retrieve()
    assert result.validation.timestamp_conversion_failures == 5
    assert result.validation.missing_sessions is None
    assert not result.observations


@pytest.mark.parametrize(
    "start,end",
    [
        (date(2026, 10, 30), date(2026, 10, 26)),
        (date(1999, 1, 1), date(1999, 1, 2)),
        (date(2099, 12, 31), date(2100, 1, 1)),
        (date(2025, 1, 1), date(2026, 1, 2)),
        ("2026-10-26", DATES[-1]),
    ],
)
def test_invalid_request_dates_no_client(start, end):
    def never():
        pytest.fail("transport constructed")

    result = DhanDailyProvider(config(), transport_factory=never).retrieve_daily(
        replace(request(calendar=False), start=start, end=end), request_approved=True
    )
    assert result.failure.code == "INVALID_REQUEST" and result.request_attempts == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("symbol", "TATASILV"),
        ("isin", "WRONG"),
        ("exchange", "XBOM"),
        ("currency", "USD"),
        ("metal", "SILVER"),
    ],
)
def test_full_listing_identity_required(field, value):
    def never():
        pytest.fail("transport constructed")

    req = request()
    req = replace(req, listing=replace(req.listing, **{field: value}))
    result = DhanDailyProvider(config(), transport_factory=never).retrieve_daily(
        req, request_approved=True
    )
    assert result.failure.code == "INVALID_INSTRUMENT" and result.request_attempts == 0


def test_calendar_must_cover_entire_request_before_client():
    req = request()
    req.calendar.coverage_start = DATES[1]
    result = DhanDailyProvider(
        config(), transport_factory=lambda: pytest.fail("client")
    ).retrieve_daily(req, request_approved=True)
    assert result.failure.code == "INVALID_REQUEST"


def test_mutated_invalid_calendar_rejected_before_transport():
    req = request()
    req.calendar.session_dates.append(DATES[0])
    provider = DhanDailyProvider(config(), transport_factory=lambda: pytest.fail("client"))
    result = provider.retrieve_daily(req, request_approved=True)
    assert result.failure.code == "INVALID_REQUEST" and result.request_attempts == 0
