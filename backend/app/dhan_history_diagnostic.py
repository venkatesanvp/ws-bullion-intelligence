"""Step 5C.1 / D-14 / REQ-05-003/004 -> ADR-09/DC-09.

Bounded backend-only, read-only historical qualification probe. No startup hook,
SQL, raw-response storage, token exchange, performance calculation or trading.
"""

import argparse
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import time

import httpx

from .dhan_config import ConfigurationReadError, DhanConfiguration, load_dhan_configuration
from .dhan_http import (
    ERROR_CODES,
    TIMEOUT,
    _quiet_transport_logs,
    configuration_problem,
    live_transport,
)

from .dhan_history_contract import (
    HISTORY_URL,
    FROM_DATE,
    TO_DATE,
    EXPECTED_DATES,
    MAX_RESPONSE_BYTES,
    MAX_OBSERVATIONS,
    BODY_BUDGET_SECONDS,
    TIMESTAMP_EVIDENCE_REF,
    MIN_CANDIDATE_SECONDS,
    MAX_CANDIDATE_SECONDS,
    ADJUSTMENT_REF,
    LIMITATIONS,
    INSTRUMENTS,
    IntegralNumericDiagnostics,
    _instrument,
    _object,
    _integral_values,
    _candidate_nse_date,
    _price,
)


@dataclass(frozen=True)
class DatasetResult:
    symbol: str
    status: str
    request_attempts: int = 0
    http_status: int | None = None
    observation_count: int | None = None
    schema_valid: bool | None = None
    numeric_valid: bool | None = None
    ohlc_consistent: bool | None = None
    coverage_valid: bool | None = None
    duplicate_timestamps: int | None = None
    duplicate_session_dates: int | None = None
    volume_numeric_diagnostics: IntegralNumericDiagnostics | None = None
    timestamp_numeric_diagnostics: IntegralNumericDiagnostics | None = None
    open_interest_numeric_diagnostics: IntegralNumericDiagnostics | None = None
    timestamp_conversion_failures: int | None = None
    timestamps_converted: int | None = None
    successfully_mapped_trading_dates: int | None = None
    coverage_assessment_complete: bool = False
    unmapped_expected_dates: tuple[str, ...] = ()
    timestamp_unit_policy: str = "UNIX_SECONDS_CANDIDATE"
    timestamp_evidence_reference: str = TIMESTAMP_EVIDENCE_REF
    exchange_timezone: str = "Asia/Kolkata"
    candidate_session_dates: tuple[str, ...] = ()
    missing_dates: tuple[str, ...] = ()
    unexpected_dates: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()
    provider_code: str | None = None
    currency: str = "INR"
    price_basis: str = "PROVIDER_ADJUSTED"
    adjustment_reference: str = ADJUSTMENT_REF
    timestamp_interpretation: str = "CANDIDATE_UNIX_SECONDS_IST"
    timestamp_semantics_verified: bool = False
    adjustment_method_verified: bool = False
    source_qualified: bool = False
    limitations: tuple[str, ...] = LIMITATIONS


def validate_response(symbol: str, status: int, body: bytes, *, content_type: str) -> DatasetResult:
    """Consumes prices transiently; returns fixed fields, counts and ISO dates only."""

    def result(reason, **fields):
        return DatasetResult(
            symbol if _instrument(symbol) else "UNSUPPORTED",
            reason,
            request_attempts=1,
            http_status=status,
            **fields,
        )

    if _instrument(symbol) is None:
        return DatasetResult("UNSUPPORTED", "INVALID_INSTRUMENT")
    if status == 429:
        return result("RATE_LIMITED")
    if 300 <= status < 400:
        return result("REDIRECT_REFUSED")
    if 500 <= status <= 599:
        return result("PROVIDER_SERVICE_ERROR")
    if not 200 <= status <= 499:
        return DatasetResult(symbol, "UNEXPECTED_RESPONSE", request_attempts=1)
    if len(body) > MAX_RESPONSE_BYTES:
        return result("RESPONSE_TOO_LARGE")
    obj = (
        _object(body)
        if content_type.partition(";")[0].strip().lower() == "application/json"
        else None
    )
    if obj is not None and any(k in obj for k in ("errorCode", "errorType", "errorMessage")):
        code = obj.get("errorCode")
        code = str(code) if type(code) is int else code
        known = code if isinstance(code, str) and code in ERROR_CODES else None
        return result(
            "INVALID_INSTRUMENT" if known == "813" else ERROR_CODES.get(known, "PROVIDER_ERROR"),
            provider_code=known,
        )
    if status == 401:
        return result("AUTH_INVALID_OR_EXPIRED")
    if status == 403:
        return result("ACCESS_DENIED")
    if status >= 400:
        return result("PROVIDER_REQUEST_REJECTED")
    if status != 200 or obj is None:
        return result("UNEXPECTED_RESPONSE", schema_valid=False)
    required = {"open", "high", "low", "close", "volume", "timestamp"}
    if not required <= obj.keys() or obj.keys() - required - {"open_interest"}:
        return result("UNEXPECTED_RESPONSE", schema_valid=False)
    if any(type(values) is not list for values in obj.values()):
        return result("UNEXPECTED_RESPONSE", schema_valid=False)
    count = len(obj["timestamp"])
    if count > MAX_OBSERVATIONS:
        return result("OBSERVATION_LIMIT_EXCEEDED", observation_count=count, schema_valid=False)
    if any(len(values) != count for values in obj.values()):
        return result("UNEXPECTED_RESPONSE", observation_count=count, schema_valid=False)
    volumes, volume_diagnostics = _integral_values(obj["volume"], minimum=0, maximum=2**63 - 1)
    stamps, timestamp_diagnostics = _integral_values(
        obj["timestamp"], minimum=MIN_CANDIDATE_SECONDS, maximum=MAX_CANDIDATE_SECONDS
    )
    oi_diagnostics = None
    oi_valid = True
    if "open_interest" in obj:
        oi, oi_diagnostics = _integral_values(obj["open_interest"], minimum=0, maximum=0)
        oi_valid = all(value is not None for value in oi)
    if not count:
        return result(
            "EMPTY_RESPONSE",
            observation_count=0,
            schema_valid=True,
            coverage_valid=False,
            missing_dates=EXPECTED_DATES,
            issues=("MISSING_OBSERVATIONS",),
            volume_numeric_diagnostics=volume_diagnostics,
            timestamp_numeric_diagnostics=timestamp_diagnostics,
            open_interest_numeric_diagnostics=oi_diagnostics,
            timestamp_conversion_failures=0,
            timestamps_converted=0,
            successfully_mapped_trading_dates=0,
            coverage_assessment_complete=True,
            duplicate_timestamps=0,
            duplicate_session_dates=0,
        )
    issues = set()
    prices_valid = all(_price(v) for k in ("open", "high", "low", "close") for v in obj[k])
    numeric = prices_valid and all(value is not None for value in volumes) and oi_valid
    if not oi_valid:
        issues.add("UNEXPECTED_OPEN_INTEREST")
    if not numeric:
        issues.add("INVALID_NUMERIC_VALUE")
    coherent = None
    if prices_valid:
        coherent = all(
            lo <= op <= hi and lo <= close <= hi
            for op, hi, lo, close in zip(
                obj["open"], obj["high"], obj["low"], obj["close"], strict=True
            )
        )
        if not coherent:
            issues.add("INCONSISTENT_OHLC")
    valid_stamps, dates = [], []
    conversion_failures = 0
    for stamp in stamps:
        if stamp is None:
            issues.add("UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE")
            continue
        valid_stamps.append(stamp)
        try:
            dates.append(_candidate_nse_date(stamp))
        except (OverflowError, ValueError, OSError):
            conversion_failures += 1
            issues.add("TIMESTAMP_CONVERSION_FAILED")
    duplicate_stamps = len(valid_stamps) - len(set(valid_stamps))
    duplicate_dates = len(dates) - len(set(dates))
    if duplicate_stamps:
        issues.add("DUPLICATE_TIMESTAMPS")
    if duplicate_dates:
        issues.add("DUPLICATE_SESSION_DATES")
    if valid_stamps != sorted(valid_stamps):
        issues.add("NON_MONOTONIC_TIMESTAMPS")
    present = set(dates)
    complete = len(dates) == count
    absent = tuple(sorted(set(EXPECTED_DATES) - present))
    unexpected = tuple(sorted(present - set(EXPECTED_DATES)))
    if not complete:
        # Rejected/unconvertible timestamps cannot prove missing provider rows or
        # absence of duplicates. Preserve that uncertainty rather than report zero.
        issues.add("DATE_COVERAGE_UNDETERMINED")
    elif absent:
        issues.add("MISSING_OBSERVATIONS")
    if unexpected:
        issues.add("UNEXPECTED_SESSION_DATES")
    coverage = not absent and not unexpected and not duplicate_dates if complete else None
    return result(
        "INVALID_DATA" if issues else "VALIDATION_PASSED_UNQUALIFIED",
        observation_count=count,
        schema_valid=True,
        numeric_valid=numeric,
        ohlc_consistent=coherent,
        coverage_valid=coverage,
        duplicate_timestamps=duplicate_stamps if complete else None,
        duplicate_session_dates=duplicate_dates if complete else None,
        volume_numeric_diagnostics=volume_diagnostics,
        timestamp_numeric_diagnostics=timestamp_diagnostics,
        open_interest_numeric_diagnostics=oi_diagnostics,
        timestamp_conversion_failures=conversion_failures,
        timestamps_converted=len(dates),
        successfully_mapped_trading_dates=len(present & set(EXPECTED_DATES)),
        coverage_assessment_complete=complete,
        unmapped_expected_dates=absent if not complete else (),
        candidate_session_dates=tuple(sorted(present)),
        missing_dates=absent if complete else (),
        unexpected_dates=unexpected,
        issues=tuple(sorted(issues)),
    )


def comparison_readiness(left: DatasetResult, right: DatasetResult) -> dict:
    a, b = _instrument(left.symbol), _instrument(right.symbol)
    identity = a is not None and b is not None and a != b and a.metal == b.metal
    currency = left.currency == right.currency == "INR"
    basis = (
        left.price_basis == right.price_basis == "PROVIDER_ADJUSTED"
        and left.adjustment_reference == right.adjustment_reference == ADJUSTMENT_REF
    )
    dates = left.candidate_session_dates == right.candidate_session_dates == EXPECTED_DATES
    valid = all(
        x.status == "VALIDATION_PASSED_UNQUALIFIED"
        and x.schema_valid
        and x.numeric_valid
        and x.ohlc_consistent
        and x.coverage_valid
        for x in (left, right)
    )
    checks = {
        "same_metal_distinct_approved_listings": identity,
        "compatible_currency": currency,
        "compatible_documented_price_basis": basis,
        "same_expected_candidate_dates": dates,
        "both_validation_checks_passed": valid,
    }
    reasons = [key.upper() + "_FAILED" for key, ok in checks.items() if not ok]
    reasons.extend(LIMITATIONS)
    return {
        "left_symbol": left.symbol if a else "UNSUPPORTED",
        "right_symbol": right.symbol if b else "UNSUPPORTED",
        **checks,
        "technical_inputs_compatible": all(checks.values()),
        "status": "BLOCKED_SOURCE_QUALIFICATION" if all(checks.values()) else "BLOCKED_INPUTS",
        "qualified_for_comparison": False,
        "reasons": reasons,
    }


def fetch_one(config: DhanConfiguration, symbol: str, *, client: httpx.Client) -> DatasetResult:
    instrument = _instrument(symbol)
    if instrument is None:
        return DatasetResult("UNSUPPORTED", "INVALID_INSTRUMENT")
    problem = configuration_problem(config)
    if problem:
        return DatasetResult(symbol, problem)
    attempted, status = 0, None
    try:
        with _quiet_transport_logs():
            attempted = 1
            with client.stream(
                "POST",
                HISTORY_URL,
                json=instrument.request_body(),
                timeout=TIMEOUT,
                follow_redirects=False,
                headers={"access-token": config.credentials.access_token.get_secret_value()},
            ) as response:
                status = response.status_code
                if status == 429 or 300 <= status < 400 or 500 <= status <= 599:
                    return validate_response(symbol, status, b"", content_type="")
                if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                    return DatasetResult(symbol, "UNEXPECTED_RESPONSE", 1, status)
                length = response.headers.get("Content-Length")
                if length is not None and (
                    len(length) > 20 or not length.isascii() or not length.isdigit()
                ):
                    return DatasetResult(symbol, "UNEXPECTED_RESPONSE", 1, status)
                if length is not None and int(length) > MAX_RESPONSE_BYTES:
                    return DatasetResult(symbol, "RESPONSE_TOO_LARGE", 1, status)
                body, started = bytearray(), time.monotonic()
                for chunk in response.iter_bytes():
                    if time.monotonic() - started > BODY_BUDGET_SECONDS:
                        return DatasetResult(symbol, "NETWORK_TIMEOUT", 1, status)
                    if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                        return DatasetResult(symbol, "RESPONSE_TOO_LARGE", 1, status)
                    body.extend(chunk)
                return validate_response(
                    symbol,
                    status,
                    bytes(body),
                    content_type=response.headers.get("Content-Type", ""),
                )
    except httpx.TimeoutException:
        return DatasetResult(symbol, "NETWORK_TIMEOUT", attempted, status)
    except httpx.RemoteProtocolError:
        return DatasetResult(symbol, "UNEXPECTED_RESPONSE", attempted, status)
    except (httpx.RequestError, OSError):
        return DatasetResult(symbol, "NETWORK_ERROR", attempted, status)
    except Exception:
        return DatasetResult(symbol, "DIAGNOSTIC_ERROR", attempted, status)


def run_batch(
    config: DhanConfiguration,
    *,
    transport: httpx.BaseTransport,
    pause: Callable[[float], None] = time.sleep,
) -> dict:
    results = []
    problem = configuration_problem(config)
    stopped = problem
    try:
        with (
            _quiet_transport_logs(),
            httpx.Client(
                transport=transport,
                timeout=TIMEOUT,
                trust_env=False,
                follow_redirects=False,
                headers={"Accept": "application/json", "Accept-Encoding": "identity"},
            ) as client,
        ):
            for instrument in INSTRUMENTS:
                if stopped:
                    results.append(
                        DatasetResult(instrument.symbol, problem or "NOT_ATTEMPTED_AFTER_FAILURE")
                    )
                    continue
                if results:
                    pause(1.0)
                item = fetch_one(config, instrument.symbol, client=client)
                results.append(item)
                if item.status not in {
                    "VALIDATION_PASSED_UNQUALIFIED",
                    "EMPTY_RESPONSE",
                    "INVALID_DATA",
                }:
                    stopped = item.status
    except Exception:
        stopped = "DIAGNOSTIC_ERROR"
        while len(results) < len(INSTRUMENTS):
            results.append(DatasetResult(INSTRUMENTS[len(results)].symbol, "DIAGNOSTIC_ERROR"))
    by_symbol = {item.symbol: item for item in results}
    return {
        "status": "BATCH_STOPPED_UNQUALIFIED" if stopped else "BATCH_COMPLETED_UNQUALIFIED",
        "method": "POST",
        "endpoint": HISTORY_URL,
        "from_date": FROM_DATE,
        "to_date_exclusive": TO_DATE,
        "request_attempts": sum(item.request_attempts for item in results),
        "datasets": [asdict(item) for item in results],
        "comparisons": [
            comparison_readiness(by_symbol[a], by_symbol[b])
            for a, b in (("TATAGOLD", "GOLDBEES"), ("TATSILV", "SILVERBEES"))
        ],
        "source_qualified": False,
        "raw_responses_persisted": False,
    }


class _ArgumentError(Exception):
    pass


class _SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise _ArgumentError() from None


def main(
    argv=None,
    *,
    transport_factory: Callable[[], httpx.BaseTransport] | None = None,
    environ: Mapping[str, str] | None = None,
    pause: Callable[[float], None] = time.sleep,
) -> int:
    parser = _SafeParser(
        description="Four fixed read-only ETF probes; owner approval and rights review required."
    )
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--live-approved", action="store_true")
    parser.add_argument("--permissions-reviewed", action="store_true")
    result, code = {"status": "LIVE_APPROVAL_REQUIRED", "request_attempts": 0}, 2
    try:
        args = parser.parse_args(argv)
        if args.live_approved:
            if not args.permissions_reviewed:
                result["status"] = "SOURCE_PERMISSION_REVIEW_REQUIRED"
            else:
                config = load_dhan_configuration(environ=environ, env_file=args.env_file)
                problem = configuration_problem(config)
                if problem:
                    result, code = {"status": problem, "request_attempts": 0}, 1
                else:
                    with _quiet_transport_logs():
                        transport = (transport_factory or live_transport)()
                    result = run_batch(config, transport=transport, pause=pause)
                    code = (
                        0
                        if all(
                            x["status"] == "VALIDATION_PASSED_UNQUALIFIED"
                            for x in result["datasets"]
                        )
                        else 1
                    )
    except _ArgumentError:
        result = {"status": "INVALID_ARGUMENTS", "request_attempts": 0}
    except ConfigurationReadError:
        result, code = {"status": "INVALID_CONFIGURATION", "request_attempts": 0}, 1
    except Exception:
        result, code = {"status": "DIAGNOSTIC_ERROR", "request_attempts": 0}, 1
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
