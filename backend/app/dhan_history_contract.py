"""Shared Step 5B/5C.1 verified identities and strict, exact response primitives.

Unix-seconds/IST remains provisional; helpers never qualify a source. No I/O.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json

HISTORY_URL = "https://api.dhan.co/v2/charts/historical"
FROM_DATE = "2026-10-26"
TO_DATE = "2026-10-31"  # Exclusive, as documented by the provider.
EXPECTED_DATES = tuple(f"2026-10-{day}" for day in range(26, 31))
MAX_RESPONSE_BYTES = 262_144
MAX_OBSERVATIONS = 64
BODY_BUDGET_SECONDS = 20.0
# NSE exchange-local IST is UTC+05:30 for this approved October 2026 window.
# A fixed offset avoids introducing a timezone-data dependency into the diagnostic.
IST = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")
# The endpoint describes int/Epoch and gives seconds-compatible examples, but no
# explicit unit/session convention. This policy remains a candidate, never an
# auto-detected unit or a verified provider contract. Milliseconds are not scaled.
TIMESTAMP_EVIDENCE_REF = "https://dhanhq.co/docs/v2/historical-data/#daily-historical-data"
MIN_CANDIDATE_SECONDS = 946684800  # 2000-01-01 UTC, technical sanity bound.
MAX_CANDIDATE_SECONDS = 4102444799  # Last second before 2100-01-01 UTC.
ADJUSTMENT_REF = "https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/"
LIMITATIONS = (
    "SOURCE_USE_PERMISSION_UNVERIFIED",
    "TIMESTAMP_CONTRACT_UNVERIFIED",
    "ADJUSTMENT_METHOD_UNVERIFIED",
    "NO_INDEPENDENT_PRICE_RECONCILIATION",
)


@dataclass(frozen=True)
class Instrument:
    symbol: str
    security_id: str
    isin: str
    metal: str

    def request_body(self) -> dict:
        return {
            "securityId": self.security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "oi": False,
            "fromDate": FROM_DATE,
            "toDate": TO_DATE,
        }


# Public, Step 5B-verified listing metadata. All four are primary instruments.
INSTRUMENTS = (
    Instrument("TATAGOLD", "21401", "INF277KA1976", "GOLD"),
    Instrument("TATSILV", "21428", "INF277KA1984", "SILVER"),
    Instrument("GOLDBEES", "14428", "INF204KB17I5", "GOLD"),
    Instrument("SILVERBEES", "8080", "INF204KC1402", "SILVER"),
)


@dataclass(frozen=True)
class IntegralNumericDiagnostics:
    """Only counts. Representation categories partition values; range overlaps.

    Populated only after strict JSON/schema validation. JSON NaN/Infinity remains
    malformed JSON, with no fabricated field counts. No raw value is retained.
    """

    json_integer_values: int = 0
    integral_decimal_values: int = 0
    fractional_numeric_values: int = 0
    unsupported_value_types: int = 0
    non_finite_numeric_values: int = 0
    invalid_numeric_ranges: int = 0


def _instrument(symbol: str) -> Instrument | None:
    return next((item for item in INSTRUMENTS if item.symbol == symbol), None)


def _object(body: bytes) -> dict | None:
    def number(value, *, integer=False):
        if len(value) > 128:
            raise ValueError()
        return int(value) if integer else Decimal(value)

    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError()
            obj[key] = value
        return obj

    def invalid(value):
        raise ValueError()

    try:
        obj = json.loads(
            body.decode("utf-8"),
            parse_float=number,
            parse_int=lambda value: number(value, integer=True),
            parse_constant=invalid,
            object_pairs_hook=unique,
        )
        return obj if isinstance(obj, dict) else None
    except (ValueError, UnicodeError, RecursionError, InvalidOperation, OverflowError):
        return None


def _integral_values(
    values: list, *, minimum: int, maximum: int
) -> tuple[list, IntegralNumericDiagnostics]:
    """Normalize only proven integral, finite, in-range numeric values.

    JSON decimals are parsed as Decimal directly. Equality with an integral value
    is checked before int conversion: no fractional value is rounded/truncated.
    Bounds precede int conversion, avoiding expansion of hostile large exponents.
    bool/str/null/Python floats are unsupported, never coerced into numbers.
    """
    counters = asdict(IntegralNumericDiagnostics())
    normalized = []
    for value in values:
        if type(value) is int:
            counters["json_integer_values"] += 1
            integral = True
        elif type(value) is Decimal:
            if not value.is_finite():
                counters["non_finite_numeric_values"] += 1
                normalized.append(None)
                continue
            integral = value == value.to_integral_value()
            counters["integral_decimal_values" if integral else "fractional_numeric_values"] += 1
        else:
            counters["unsupported_value_types"] += 1
            normalized.append(None)
            continue
        in_range = minimum <= value <= maximum
        if not in_range:
            counters["invalid_numeric_ranges"] += 1
        normalized.append(int(value) if integral and in_range else None)
    return normalized, IntegralNumericDiagnostics(**counters)


def _candidate_nse_date(seconds: int) -> str:
    # Explicit Unix-seconds candidate policy; no host-local zone or float math.
    instant = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return instant.astimezone(IST).date().isoformat()


def _price(value) -> bool:
    if type(value) not in (int, Decimal):
        return False
    value = Decimal(value)
    return value.is_finite() and 0 < value < Decimal("1e14")
