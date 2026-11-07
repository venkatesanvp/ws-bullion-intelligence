"""Step 5D.1: bounded in-memory Dhan daily adapter. Not mounted in the application.

Both process configuration and explicit per-request approval are required. No CLI,
SQL, file output, retries, token exchange, account/trading or scheduling operations.
"""

from collections.abc import Callable
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import time

import httpx

from .daily_values import price
from .dhan_config import DhanConfiguration
from .dhan_history_contract import (
    ADJUSTMENT_REF,
    BODY_BUDGET_SECONDS,
)
from .dhan_history_contract import (
    HISTORY_URL,
    INSTRUMENTS,
    LIMITATIONS,
    MAX_CANDIDATE_SECONDS,
    MIN_CANDIDATE_SECONDS,
    TIMESTAMP_EVIDENCE_REF,
    _candidate_nse_date,
    _integral_values,
    _object,
)
from .dhan_http import (
    ERROR_CODES,
    TIMEOUT,
    quiet_request_logs,
    configuration_problem,
    live_transport,
)
from .market_data import (
    BatchProvenance,
    DailyObservation,
    DailyRequest,
    DailyResult,
    Listing,
    ObservationProvenance,
    ProviderFailure,
    ValidationSummary,
)

MAX_RESPONSE_BYTES = 262_144
MAX_OBSERVATIONS = 366
CONTRACT_VERSION = "dhan-daily-v1-provisional"


def _listing(item) -> Listing:
    return Listing("XNSE", item.symbol, item.isin, item.metal)


class DhanDailyProvider:
    identity = "DHANHQ"

    def __init__(
        self,
        config: DhanConfiguration,
        *,
        transport_factory: Callable[[], httpx.BaseTransport] | None = None,
        timeout_seconds: int | None = None,
        verified_instruments=None,
    ):
        self._config = config
        self._transport_factory = transport_factory
        self._timeout = TIMEOUT if timeout_seconds is None else httpx.Timeout(timeout_seconds)
        # Only independently verified catalog records may be supplied by the composition root.
        self._instruments = tuple(
            INSTRUMENTS if verified_instruments is None else verified_instruments
        )
        if (
            not self._instruments
            or len(self._instruments) > 100
            or len({x.isin for x in self._instruments}) != len(self._instruments)
            or len({x.security_id for x in self._instruments}) != len(self._instruments)
            or any(
                not x.security_id.isdecimal()
                or not x.symbol
                or len(x.isin) != 12
                or x.metal not in {"GOLD", "SILVER"}
                for x in self._instruments
            )
        ):
            raise ValueError("INVALID_VERIFIED_CATALOG")

    def listings(self) -> tuple[Listing, ...]:
        return tuple(_listing(item) for item in self._instruments)

    def retrieve_daily(
        self, request: DailyRequest, *, request_approved: bool = False
    ) -> DailyResult:
        def failure(code, attempts=0, status=None):
            return DailyResult("FAILED", attempts, status, failure=ProviderFailure(code, status))

        if request_approved is not True:
            return failure("EXPLICIT_REQUEST_APPROVAL_REQUIRED")
        problem = configuration_problem(self._config)
        if problem:
            return failure(problem)
        if not isinstance(request, DailyRequest):
            return failure("INVALID_REQUEST")
        try:
            request.validate()
        except (ValueError, TypeError, AttributeError):
            return failure("INVALID_REQUEST")
        instrument = next((x for x in self._instruments if _listing(x) == request.listing), None)
        if instrument is None:
            return failure("INVALID_INSTRUMENT")
        # Inclusive canonical boundary -> documented exclusive provider end date.
        end_exclusive = request.end + timedelta(days=1)
        body = {
            "securityId": instrument.security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "oi": False,
            "fromDate": request.start.isoformat(),
            "toDate": end_exclusive.isoformat(),
        }
        attempted, status = 0, None
        try:
            # Suppress request-thread wire logs; preserve logging on other application threads.
            with (
                quiet_request_logs(),
                httpx.Client(
                    transport=(self._transport_factory or live_transport)(),
                    timeout=self._timeout,
                    trust_env=False,
                    follow_redirects=False,
                    headers={"Accept": "application/json", "Accept-Encoding": "identity"},
                ) as client,
            ):
                attempted = 1
                with client.stream(
                    "POST",
                    HISTORY_URL,
                    json=body,
                    timeout=self._timeout,
                    follow_redirects=False,
                    headers={
                        "access-token": self._config.credentials.access_token.get_secret_value()
                    },
                ) as response:
                    status = response.status_code
                    if status == 429 or 300 <= status < 400 or status >= 500:
                        return self._normalize(request, instrument, status, b"", "")
                    if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                        return failure("UNEXPECTED_RESPONSE", attempted, status)
                    length = response.headers.get("Content-Length")
                    if length is not None and (
                        len(length) > 20 or not length.isascii() or not length.isdigit()
                    ):
                        return failure("UNEXPECTED_RESPONSE", attempted, status)
                    if length is not None and int(length) > MAX_RESPONSE_BYTES:
                        return failure("RESPONSE_TOO_LARGE", attempted, status)
                    received, started = bytearray(), time.monotonic()
                    for chunk in response.iter_bytes():
                        if time.monotonic() - started > BODY_BUDGET_SECONDS:
                            return failure("NETWORK_TIMEOUT", attempted, status)
                        if len(received) + len(chunk) > MAX_RESPONSE_BYTES:
                            return failure("RESPONSE_TOO_LARGE", attempted, status)
                        received.extend(chunk)
                    return self._normalize(
                        request,
                        instrument,
                        status,
                        bytes(received),
                        response.headers.get("Content-Type", ""),
                    )
        except httpx.TimeoutException:
            return failure("NETWORK_TIMEOUT", attempted, status)
        except httpx.RemoteProtocolError:
            return failure("UNEXPECTED_RESPONSE", attempted, status)
        except (httpx.RequestError, OSError):
            return failure("NETWORK_ERROR", attempted, status)
        except Exception:
            # Never return exception text, request objects, provider messages or bodies.
            return failure("PROVIDER_ADAPTER_ERROR", attempted, status)

    def _normalize(self, request, instrument, status, body, content_type) -> DailyResult:
        def failure(code, provider_code=None, validation=None):
            return DailyResult(
                "FAILED",
                1,
                status,
                validation=validation or ValidationSummary(),
                failure=ProviderFailure(code, status, provider_code),
            )

        if status == 429:
            return failure("RATE_LIMITED")
        if 300 <= status < 400:
            return failure("REDIRECT_REFUSED")
        if status >= 500:
            return failure("PROVIDER_SERVICE_ERROR")
        obj = (
            _object(body)
            if content_type.partition(";")[0].strip().lower() == "application/json"
            else None
        )
        if obj is not None and any(k in obj for k in ("errorCode", "errorType", "errorMessage")):
            code = obj.get("errorCode")
            code = str(code) if type(code) is int else code
            known = code if isinstance(code, str) and code in ERROR_CODES else None
            return failure(
                "INVALID_INSTRUMENT"
                if known == "813"
                else ERROR_CODES.get(known, "PROVIDER_ERROR"),
                known,
            )
        if status == 401:
            return failure("AUTH_INVALID_OR_EXPIRED")
        if status == 403:
            return failure("ACCESS_DENIED")
        if status >= 400:
            return failure("PROVIDER_REQUEST_REJECTED")
        fields = {"open", "high", "low", "close", "volume", "timestamp"}
        if (
            status != 200
            or obj is None
            or not fields <= obj.keys()
            or obj.keys() - fields - {"open_interest"}
            or any(type(v) is not list for v in obj.values())
        ):
            return failure("UNEXPECTED_RESPONSE")
        count = len(obj["timestamp"])
        if count > MAX_OBSERVATIONS:
            return failure("OBSERVATION_LIMIT_EXCEEDED")
        if any(len(v) != count for v in obj.values()):
            return failure("UNEXPECTED_RESPONSE")
        volumes, volume_counts = _integral_values(obj["volume"], minimum=0, maximum=2**63 - 1)
        stamps, stamp_counts = _integral_values(
            obj["timestamp"], minimum=MIN_CANDIDATE_SECONDS, maximum=MAX_CANDIDATE_SECONDS
        )
        counters = [
            ("volume", tuple(asdict(volume_counts).items())),
            ("timestamp", tuple(asdict(stamp_counts).items())),
        ]
        issues, normalized, dates, conversions_failed = set(), [], [], 0
        if "open_interest" in obj:
            oi, oi_counts = _integral_values(obj["open_interest"], minimum=0, maximum=0)
            counters.append(("open_interest", tuple(asdict(oi_counts).items())))
            if any(v is None for v in oi):
                issues.add("UNEXPECTED_OPEN_INTEREST")
        for i in range(count):
            values = {}
            for key in ("open", "high", "low", "close"):
                value = obj[key][i]
                try:
                    if type(value) not in (int, Decimal):
                        raise ValueError()
                    decimal = Decimal(value)
                    # Bound before fixed-point formatting; no huge-exponent expansion or rounding.
                    if (
                        not decimal.is_finite()
                        or not 0 < decimal < Decimal("1e14")
                        or decimal.as_tuple().exponent < -10
                    ):
                        raise ValueError()
                    values[key] = price(format(decimal, "f"))
                except (ValueError, ArithmeticError):
                    issues.add("INVALID_PRICE")
            if len(values) == 4 and not (
                values["low"] <= values["open"] <= values["high"]
                and values["low"] <= values["close"] <= values["high"]
            ):
                issues.add("INCONSISTENT_OHLC")
            if volumes[i] is None:
                issues.add("INVALID_VOLUME")
            day = None
            if stamps[i] is None:
                issues.add("UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE")
            else:
                try:
                    day = date.fromisoformat(_candidate_nse_date(stamps[i]))
                    dates.append(day)
                except (ValueError, OverflowError, OSError):
                    conversions_failed += 1
                    issues.add("TIMESTAMP_CONVERSION_FAILED")
                if day is not None and not request.start <= day <= request.end:
                    issues.add("DATE_OUTSIDE_REQUEST")
            normalized.append((values, volumes[i], day))
        all_dates_mapped = len(dates) == count
        duplicate_stamps = len([v for v in stamps if v is not None]) - len(set(stamps) - {None})
        duplicate_dates = len(dates) - len(set(dates))
        if duplicate_stamps:
            issues.add("DUPLICATE_TIMESTAMPS")
        if duplicate_dates:
            issues.add("DUPLICATE_SESSION_DATES")
        # Retain row provenance while ordering valid candidates, as DC-04 specifies.
        if all_dates_mapped and dates != sorted(dates):
            issues.add("OUT_OF_ORDER_NORMALIZED")
        missing, calendar_status = None, "UNASSESSED"
        if request.calendar is not None and all_dates_mapped:
            expected = {
                d for d in request.calendar.session_dates if request.start <= d <= request.end
            }
            missing = tuple(sorted(expected - set(dates)))
            calendar_status = "ASSESSED_AGAINST_SUPPLIED_CALENDAR_CANDIDATE_DATES"
            if set(dates) - expected:
                issues.add("NON_TRADING_DATE")
            if missing:
                issues.add("MISSING_OBSERVATIONS")
        if not all_dates_mapped:
            issues.add("DATE_COVERAGE_UNDETERMINED")
        validation = ValidationSummary(
            count,
            tuple(sorted(issues)),
            tuple(sorted(set(dates))),
            missing,
            calendar_status,
            duplicate_stamps if all_dates_mapped else None,
            duplicate_dates if all_dates_mapped else None,
            conversions_failed,
            tuple(counters),
        )
        hard = issues - {"MISSING_OBSERVATIONS", "OUT_OF_ORDER_NORMALIZED"}
        if hard:
            return failure("INVALID_DATA", validation=validation)
        state = (
            "EMPTY_UNQUALIFIED"
            if not count
            else "VALIDATED_WITH_GAPS_UNQUALIFIED"
            if missing
            else "VALIDATED_UNQUALIFIED"
        )
        provenance = BatchProvenance(
            self.identity,
            CONTRACT_VERSION,
            request.listing,
            instrument.security_id,
            "NSE_EQ",
            "EQUITY",
            request.start,
            request.end,
            request.end + timedelta(days=1),
            datetime.now(timezone.utc),
            "PROVIDER_ADJUSTED",
            ADJUSTMENT_REF,
            "UNIX_SECONDS_IST_CANDIDATE_V1",
            TIMESTAMP_EVIDENCE_REF,
            "Asia/Kolkata",
            request.calendar.version if request.calendar else None,
            request.calendar.evidence_ref if request.calendar else None,
            state,
            LIMITATIONS
            + (
                "SESSION_MAPPING_NOT_INDEPENDENTLY_VERIFIED",
                "PUBLICATION_TIME_UNKNOWN",
                "TIMESTAMP_POLICY_LIVE_OBSERVED_ONLY_2026_10_26_TO_30",
            )
            + (("CALENDAR_UNASSESSED",) if request.calendar is None else ()),
        )
        observations = tuple(
            DailyObservation(
                day,
                **values,
                volume=volume,
                provenance=ObservationProvenance(
                    provenance,
                    row + 1,
                    str(obj["timestamp"][row]),
                    "JSON_INTEGER" if type(obj["timestamp"][row]) is int else "INTEGRAL_DECIMAL",
                ),
            )
            for row, (values, volume, day) in sorted(enumerate(normalized), key=lambda x: x[1][2])
        )
        return DailyResult(state, 1, status, observations, provenance, validation)
