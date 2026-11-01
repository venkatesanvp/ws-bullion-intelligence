"""VS01-T-04/07/17/20; DC-02/04. All numeric inputs are synthetic."""

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4
import pytest
from app.ingestion import parse_csv, price
from app.schemas import ImportMetadata
from app.serialization import decode_cursor, encode_cursor
from app.errors import APIError


def metadata(columns=None):
    return ImportMetadata(
        instrument_id=uuid4(),
        source_id=uuid4(),
        interval="1d",
        price_basis="RAW_CLOSE",
        mapping_version="test-v1",
        column_map=columns or {"trading_date": "Date", "close": "Close"},
        quality_policy_version="quality-v1",
        qualification_ref="SYNTHETIC TEST",
    )


def parse(value, columns=None, profile=None, max_rows=100):
    return parse_csv(
        value if isinstance(value, bytes) else value.encode(),
        metadata(columns),
        SimpleNamespace(symbol="SYNTH_GOLD", currency="INR"),
        SimpleNamespace(profile=profile or {}),
        max_rows,
    )


@pytest.mark.parametrize(
    "value",
    ["NaN", "Infinity", "-1", "0", "1e2", "1,000", "=2+3", "100000000000000", "1.00000000001", ""],
)
def test_invalid_price(value):
    with pytest.raises(ValueError):
        price(value)


def test_decimal_boundary_no_rounding():
    assert price("99999999999999.1234567890") == Decimal("99999999999999.1234567890")


@pytest.mark.parametrize(
    "value,code",
    [
        ("Date,Close\n2026-02-30,12\n", "INVALID_TRADING_DATE"),
        ("Date,Close\n01/02/2026,12\n", "INVALID_TRADING_DATE"),
        ("Date,Close\n2026-01-01,NaN\n", "INVALID_CLOSE"),
        ("Date,Close,Account\n2026-01-01,12,PRIVATE\n", "HEADER_MISMATCH"),
        ("Date,Date\n2026-01-01,12\n", "HEADER_MISMATCH"),
        ("Date,Close\n2026-01-01,12,extra\n", "COLUMN_COUNT_MISMATCH"),
        ("Date,Close\n2026-01-01\n", "COLUMN_COUNT_MISMATCH"),
        (b"Date,Close\n2026-01-01,\xff\n", "INVALID_UTF8"),
        (b"Date,Close\n2026-01-01,\x00\n", "INVALID_TEXT"),
        ('Date,Close\n"unterminated,12\n', "INVALID_CSV"),
    ],
)
def test_hard_validation(value, code):
    report = parse(value)
    assert report.errors > 0
    assert code in [x["code"] for x in report.issues]


def test_exact_duplicate_and_order():
    result = parse("Date,Close\n2026-01-02,12\n2026-01-01,10.0\n2026-01-01,10.00\n")
    assert not result.errors and result.duplicates == 1
    assert len(result.candidates) == 2
    assert result.rows[1][1]["close"] == "10.0"
    assert {i["code"] for i in result.issues} == {"EXACT_DUPLICATE", "OUT_OF_ORDER_NORMALIZED"}


def test_conflicting_duplicate_and_row_bound():
    result = parse("Date,Close\n2026-01-01,10\n2026-01-01,11\n")
    assert result.conflict and result.errors == 1
    bounded = parse("Date,Close\n2026-01-01,10\n2026-01-02,12\n", max_rows=1)
    assert bounded.errors and len(bounded.rows) == 1


@pytest.mark.parametrize(
    "row,code",
    [
        ("2026-01-01,12,13,11,10,1,INR,SYNTH_GOLD,", "INVALID_OHLC"),
        ("2026-01-01,12,10,14,,1,INR,SYNTH_GOLD,", "INVALID_OHLC"),
        ("2026-01-01,12,10,14,9,-1,INR,SYNTH_GOLD,", "INVALID_VOLUME"),
        ("2026-01-01,12,10,14,9,1.5,INR,SYNTH_GOLD,", "INVALID_VOLUME"),
        ("2026-01-01,12,10,14,9,1,USD,SYNTH_GOLD,", "INVALID_CURRENCY"),
        ("2026-01-01,12,10,14,9,1,INR,OTHER,", "INVALID_SYMBOL"),
        (
            "2026-01-01,12,10,14,9,1,INR,SYNTH_GOLD,2026-01-01T10:00:00",
            "INVALID_PROVIDER_PUBLISHED_AT",
        ),
    ],
)
def test_optional_field_validation(row, code):
    keys = [
        "trading_date",
        "close",
        "open",
        "high",
        "low",
        "volume",
        "currency",
        "symbol",
        "provider_published_at",
    ]
    result = parse(",".join(keys) + "\n" + row + "\n", dict(zip(keys, keys)))
    assert code in {x["code"] for x in result.issues}


def test_unknown_times_stay_null():
    result = parse("Date,Close\n2026-01-01,10.1234567890\n")
    value = next(iter(result.candidates.values()))[1]
    assert value["close"] == Decimal("10.1234567890")
    assert value["provider_published_at"] is None and value["event_time"] is None
    assert value["event_precision"] == "SESSION_DATE"


def test_explicit_calendar_only():
    profile = {
        "calendar": {
            "coverage_start": "2026-01-01",
            "coverage_end": "2026-01-03",
            "session_dates": ["2026-01-01", "2026-01-03"],
        }
    }
    assert parse("Date,Close\n2026-01-02,12\n", profile=profile).errors
    assert not parse("Date,Close\n2026-01-04,12\n", profile=profile).errors


def test_diagnostics_bounded():
    result = parse("Date,Close\n" + "2026-01-01,NaN\n" * 1100, max_rows=2000)
    assert result.errors == 1100 and len(result.issues) == 1000


def test_signed_cursor_tamper_and_scope():
    encoded = encode_cursor({"scope": "original", "last": "id"}, "test-key")
    assert decode_cursor(encoded, "test-key", "original") == "id"
    with pytest.raises(APIError) as changed:
        decode_cursor(encoded, "test-key", "other")
    assert changed.value.code == "SNAPSHOT_CHANGED"
    with pytest.raises(APIError):
        decode_cursor("X" + encoded[1:], "test-key", "original")
