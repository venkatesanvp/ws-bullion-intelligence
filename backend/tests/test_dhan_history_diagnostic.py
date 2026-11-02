"""SYNTHETIC_TEST OHLCV only; pure checks and CLI gates never use provider sockets."""

from dataclasses import asdict, replace
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import json
import socket
from unittest.mock import Mock

import pytest
from app.dhan_history_diagnostic import (
    ADJUSTMENT_REF,
    EXPECTED_DATES,
    INSTRUMENTS,
    MAX_OBSERVATIONS,
    _integral_values,
    comparison_readiness,
    main,
    validate_response,
)

TOKEN = "SYNTHETIC-HISTORY-TOKEN-NOT-A-CREDENTIAL"


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network forbidden in offline historical tests")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def synthetic():
    return {
        "open": [10.25] * 5,
        "high": [12] * 5,
        "low": [9] * 5,
        "close": [11.125] * 5,
        "volume": [100] * 5,
        "timestamp": [
            int(datetime(2026, 10, d, tzinfo=timezone.utc).timestamp()) for d in range(26, 31)
        ],
    }


def validate(payload, symbol="TATAGOLD", status=200):
    return validate_response(
        symbol, status, json.dumps(payload).encode(), content_type="application/json"
    )


@pytest.mark.parametrize(
    "symbol,security_id,isin,metal",
    [
        ("TATAGOLD", "21401", "INF277KA1976", "GOLD"),
        ("TATSILV", "21428", "INF277KA1984", "SILVER"),
        ("GOLDBEES", "14428", "INF204KB17I5", "GOLD"),
        ("SILVERBEES", "8080", "INF204KC1402", "SILVER"),
    ],
)
def test_four_primary_identities_and_fixed_request_contract(symbol, security_id, isin, metal):
    instrument = next(x for x in INSTRUMENTS if x.symbol == symbol)
    assert (instrument.security_id, instrument.isin, instrument.metal) == (security_id, isin, metal)
    assert instrument.request_body() == {
        "securityId": security_id,
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "oi": False,
        "fromDate": "2026-10-26",
        "toDate": "2026-10-31",
    }
    result = validate(synthetic(), symbol)
    assert result.status == "VALIDATION_PASSED_UNQUALIFIED" and result.observation_count == 5
    assert (
        result.schema_valid
        and result.numeric_valid
        and result.ohlc_consistent
        and result.coverage_valid
    )
    assert result.candidate_session_dates == EXPECTED_DATES
    assert (
        result.price_basis == "PROVIDER_ADJUSTED" and result.adjustment_reference == ADJUSTMENT_REF
    )
    assert (
        not result.source_qualified
        and not result.timestamp_semantics_verified
        and not result.adjustment_method_verified
    )
    assert "11.125" not in json.dumps(asdict(result))  # Never report prices.


def test_empty_response_and_optional_zero_open_interest():
    empty = validate({k: [] for k in synthetic()})
    assert empty.status == "EMPTY_RESPONSE" and empty.observation_count == 0
    assert empty.missing_dates == EXPECTED_DATES and not empty.coverage_valid
    assert (
        validate({**synthetic(), "open_interest": [0] * 5}).status
        == "VALIDATION_PASSED_UNQUALIFIED"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", True),
        ("high", "12"),
        ("low", None),
        ("close", 0),
        ("close", -1),
        ("close", 10**14),
        ("volume", -1),
        ("volume", 1.5),
        ("volume", True),
        ("volume", 2**63),
        ("open_interest", 1),
        ("open_interest", False),
    ],
)
def test_numeric_invalidity_never_echoes_values(field, value):
    payload = synthetic()
    if field == "open_interest":
        payload[field] = [0] * 5
    payload[field][0] = value
    result = validate(payload)
    assert result.status == "INVALID_DATA" and result.numeric_valid is False
    assert "INVALID_NUMERIC_VALUE" in result.issues


@pytest.mark.parametrize("field,value", [("open", 13), ("close", 8), ("high", 8), ("low", 13)])
def test_incoherent_ohlc_is_not_accepted(field, value):
    payload = synthetic()
    payload[field][0] = value
    result = validate(payload)
    assert not result.ohlc_consistent and "INCONSISTENT_OHLC" in result.issues


@pytest.mark.parametrize("stamp", [True, None, "1792972800", 1792972800000, 1.5, -1, 999999999999])
def test_timestamp_types_units_and_range_are_not_guessed(stamp):
    payload = synthetic()
    payload["timestamp"][0] = stamp
    result = validate(payload)
    assert "UNSUPPORTED_TIMESTAMP_UNIT_OR_RANGE" in result.issues and not result.coverage_valid
    assert not result.timestamp_semantics_verified


def test_missing_unexpected_duplicate_and_unordered_dates():
    payload = synthetic()
    for key in payload:
        payload[key].pop()
    result = validate(payload)
    assert result.observation_count == 4 and result.missing_dates == ("2026-10-30",)
    payload = synthetic()
    payload["timestamp"][4] += 86400
    result = validate(payload)
    assert result.missing_dates == ("2026-10-30",) and result.unexpected_dates == ("2026-10-31",)
    payload = synthetic()
    payload["timestamp"][1] = payload["timestamp"][0]
    result = validate(payload)
    assert result.duplicate_timestamps == result.duplicate_session_dates == 1
    assert "DUPLICATE_TIMESTAMPS" in result.issues
    payload["timestamp"][1] += 3600
    result = validate(payload)
    assert result.duplicate_timestamps == 0 and result.duplicate_session_dates == 1
    payload = synthetic()
    payload["timestamp"].reverse()
    assert "NON_MONOTONIC_TIMESTAMPS" in validate(payload).issues


def test_utc_to_ist_is_explicitly_only_a_candidate_contract():
    payload = synthetic()
    payload["timestamp"] = [
        int(datetime(2026, 10, d, 18, 30, tzinfo=timezone.utc).timestamp()) for d in range(25, 30)
    ]
    result = validate(payload)
    assert result.candidate_session_dates == EXPECTED_DATES and result.coverage_valid
    assert result.timestamp_interpretation == "CANDIDATE_UNIX_SECONDS_IST"
    assert not result.timestamp_semantics_verified


@pytest.mark.parametrize(
    "change",
    ["missing_key", "extra_key", "nested", "wrong_array", "unequal", "oi_unequal", "too_many"],
)
def test_malformed_ohlcv_structures(change):
    payload = synthetic()
    if change == "missing_key":
        del payload["close"]
    elif change == "extra_key":
        payload[TOKEN] = TOKEN
    elif change == "nested":
        payload = {"data": payload}
    elif change == "wrong_array":
        payload["volume"] = TOKEN
    elif change == "unequal":
        payload["close"].pop()
    elif change == "oi_unequal":
        payload["open_interest"] = []
    else:
        payload = {k: [v[0]] * (MAX_OBSERVATIONS + 1) for k, v in payload.items()}
    result = validate(payload)
    assert (
        result.status in {"UNEXPECTED_RESPONSE", "OBSERVATION_LIMIT_EXCEEDED"}
        and not result.schema_valid
    )
    assert TOKEN not in json.dumps(asdict(result))


@pytest.mark.parametrize(
    "body",
    [
        b"bad-json",
        b"[]",
        b"null",
        b"{}{}",
        b"\xff",
        b'{"open":[],"open":[]}',
        b'{"open":NaN}',
        b'{"volume":Infinity}',
        b'{"open":' + b"1" * 129 + b"}",
        b'{"open":1e99999999999999999999999}',
    ],
)
def test_invalid_json_numbers_and_duplicate_keys(body):
    result = validate_response("TATAGOLD", 200, body, content_type="application/json")
    assert result.status == "UNEXPECTED_RESPONSE"


def test_decimal_prices_are_parsed_without_binary_rounding():
    body = json.dumps(synthetic()).replace("11.125", "11.12345678901234567890123456789").encode()
    result = validate_response("GOLDBEES", 200, body, content_type="application/json")
    assert result.numeric_valid and result.ohlc_consistent
    assert b"11.123456" not in json.dumps(asdict(result)).encode()


@pytest.mark.parametrize(
    "status,code,expected",
    [
        (401, None, "AUTH_INVALID_OR_EXPIRED"),
        (403, None, "ACCESS_DENIED"),
        (401, "807", "TOKEN_EXPIRED"),
        (401, "808", "INVALID_CREDENTIALS"),
        (401, "809", "INVALID_CREDENTIALS"),
        (403, "806", "DATA_ENTITLEMENT_REQUIRED"),
        (400, "813", "INVALID_INSTRUMENT"),
        (400, 813, "INVALID_INSTRUMENT"),
        (429, "807", "RATE_LIMITED"),
        (400, "805", "RATE_LIMITED"),
        (401, "DH-901", "AUTH_INVALID_OR_EXPIRED"),
        (403, "DH-902", "ACCESS_OR_ENTITLEMENT_REQUIRED"),
        (503, "809", "PROVIDER_SERVICE_ERROR"),
        (302, None, "REDIRECT_REFUSED"),
        (200, TOKEN, "PROVIDER_ERROR"),
        (204, None, "UNEXPECTED_RESPONSE"),
    ],
)
def test_auth_entitlement_identifier_rate_and_service_errors_are_sanitized(status, code, expected):
    payload = {} if code is None else {"errorCode": code, "errorMessage": TOKEN}
    result = validate(payload, status=status)
    assert result.status == expected and TOKEN not in repr(result) + json.dumps(asdict(result))


def test_unknown_instrument_is_not_reflected():
    result = validate(synthetic(), TOKEN)
    assert (
        result.symbol == "UNSUPPORTED"
        and result.status == "INVALID_INSTRUMENT"
        and result.request_attempts == 0
    )


@pytest.mark.parametrize("pair", [("TATAGOLD", "GOLDBEES"), ("TATSILV", "SILVERBEES")])
def test_valid_inputs_remain_blocked_pending_real_qualification(pair):
    left, right = [validate(synthetic(), symbol) for symbol in pair]
    result = comparison_readiness(left, right)
    assert result["technical_inputs_compatible"] and not result["qualified_for_comparison"]
    assert result["status"] == "BLOCKED_SOURCE_QUALIFICATION"
    assert "TIMESTAMP_CONTRACT_UNVERIFIED" in result["reasons"]


@pytest.mark.parametrize(
    "change", ["currency", "basis", "reference", "dates", "metal", "same", "invalid", "unknown"]
)
def test_incompatible_comparison_inputs(change):
    left = validate(synthetic(), "TATAGOLD")
    right = validate(synthetic(), "GOLDBEES")
    if change == "currency":
        right = replace(right, currency="USD")
    elif change == "basis":
        right = replace(right, price_basis="RAW_CLOSE")
    elif change == "reference":
        right = replace(right, adjustment_reference="different policy")
    elif change == "dates":
        right = replace(right, candidate_session_dates=EXPECTED_DATES[:-1])
    elif change == "metal":
        right = replace(right, symbol="SILVERBEES")
    elif change == "same":
        right = left
    elif change == "invalid":
        right = replace(right, numeric_valid=False)
    else:
        right = replace(right, symbol=TOKEN)
    result = comparison_readiness(left, right)
    assert not result["technical_inputs_compatible"] and not result["qualified_for_comparison"]
    assert result["status"] == "BLOCKED_INPUTS" and TOKEN not in json.dumps(result)


@pytest.mark.parametrize(
    "argv,status",
    [
        ([], "LIVE_APPROVAL_REQUIRED"),
        (["--permissions-reviewed"], "LIVE_APPROVAL_REQUIRED"),
        (["--live-approved"], "SOURCE_PERMISSION_REVIEW_REQUIRED"),
    ],
)
def test_cli_gates_precede_configuration_and_transport(argv, status, monkeypatch, capsys):
    forbidden = Mock(side_effect=AssertionError("No configuration/network permitted"))
    monkeypatch.setattr("app.dhan_history_diagnostic.load_dhan_configuration", forbidden)
    assert main(argv, transport_factory=forbidden, environ={}) == 2
    assert json.loads(capsys.readouterr().out) == {"status": status, "request_attempts": 0}
    forbidden.assert_not_called()


@pytest.mark.parametrize(
    "env,status",
    [
        ({}, "INTEGRATION_DISABLED"),
        ({"DHAN_DATA_API_ENABLED": "true"}, "MISSING_ACCESS_TOKEN"),
        ({"DHAN_DATA_API_ENABLED": "bad-" + TOKEN}, "INVALID_CONFIGURATION"),
    ],
)
def test_cli_configuration_gates_no_requests(env, status, capsys):
    factory = Mock(side_effect=AssertionError("No client permitted"))
    assert (
        main(["--live-approved", "--permissions-reviewed"], transport_factory=factory, environ=env)
        == 1
    )
    output = capsys.readouterr().out
    assert json.loads(output)["status"] == status and TOKEN not in output
    factory.assert_not_called()


def test_safe_cli_arguments_and_file_errors(capsys, tmp_path):
    assert main([TOKEN]) == 2
    assert (
        main(
            ["--live-approved", "--permissions-reviewed", "--env-file", str(tmp_path / TOKEN)],
            environ={},
        )
        == 1
    )
    output = capsys.readouterr()
    assert TOKEN not in output.out + output.err


def numeric_encoding_body(*, volume="12500", timestamp_decimal=False, timestamp_token=None):
    """SYNTHETIC_TEST lexical JSON numbers; never serialize through float."""
    payload = synthetic()
    payload["volume"] = ["SYNTHETIC_VOLUME_TOKEN"] * 5
    payload["timestamp"] = ["SYNTHETIC_TIMESTAMP_" + str(i) for i in range(5)]
    body = json.dumps(payload).replace('"SYNTHETIC_VOLUME_TOKEN"', volume)
    for i, stamp in enumerate(synthetic()["timestamp"]):
        token = (
            timestamp_token
            if timestamp_token is not None
            else str(stamp) + (".0" if timestamp_decimal else "")
        )
        body = body.replace('"SYNTHETIC_TIMESTAMP_' + str(i) + '"', token)
    return body.encode()


@pytest.mark.parametrize(
    "token,valid,kind,out_of_range",
    [
        ("12500", True, "json_integer_values", 0),
        ("12500.0", True, "integral_decimal_values", 0),
        ("1.25e4", True, "integral_decimal_values", 0),
        ("0.0", True, "integral_decimal_values", 0),
        ("9223372036854775807.000", True, "integral_decimal_values", 0),
        ("12500.5", False, "fractional_numeric_values", 0),
        ("12500.000000000000000000000001", False, "fractional_numeric_values", 0),
        ("-1", False, "json_integer_values", 5),
        ("-1.0", False, "integral_decimal_values", 5),
        ("-1.5", False, "fractional_numeric_values", 5),
        ("9223372036854775808", False, "json_integer_values", 5),
        ("1e1000000", False, "integral_decimal_values", 5),
        ("true", False, "unsupported_value_types", 0),
        ("null", False, "unsupported_value_types", 0),
        ('"' + TOKEN + '"', False, "unsupported_value_types", 0),
    ],
)
def test_integral_volume_semantics_and_sanitized_counters(token, valid, kind, out_of_range):
    result = validate_response(
        "TATAGOLD", 200, numeric_encoding_body(volume=token), content_type="application/json"
    )
    counters = asdict(result.volume_numeric_diagnostics)
    assert result.numeric_valid is valid and counters[kind] == 5
    assert counters["invalid_numeric_ranges"] == out_of_range
    assert result.coverage_valid and result.coverage_assessment_complete
    assert result.timestamps_converted == result.successfully_mapped_trading_dates == 5
    assert (result.status == "VALIDATION_PASSED_UNQUALIFIED") is valid
    assert TOKEN not in json.dumps(asdict(result))


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
@pytest.mark.parametrize("field", ["volume", "timestamp"])
def test_non_finite_json_is_rejected_without_fabricated_field_counters(token, field):
    body = (
        numeric_encoding_body(volume=token)
        if field == "volume"
        else numeric_encoding_body(timestamp_token=token)
    )
    result = validate_response("TATAGOLD", 200, body, content_type="application/json")
    assert result.status == "UNEXPECTED_RESPONSE" and result.schema_valid is False
    assert (
        result.volume_numeric_diagnostics is None and result.timestamp_numeric_diagnostics is None
    )


def test_normalization_is_exact_and_does_not_depend_on_decimal_context():
    values = [
        12500,
        Decimal("12500.0"),
        Decimal("12500.5"),
        -1,
        True,
        "12500",
        None,
        12500.0,
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("1e1000000"),
    ]
    with localcontext() as context:
        context.prec = 2
        normalized, counters = _integral_values(values, minimum=0, maximum=2**63 - 1)
        fine, fine_counts = _integral_values(
            [Decimal("12500.000000000000000001")], minimum=0, maximum=2**63 - 1
        )
    assert normalized == [12500, 12500] + [None] * 9
    assert fine == [None] and fine_counts.fractional_numeric_values == 1
    assert asdict(counters) == {
        "json_integer_values": 2,
        "integral_decimal_values": 2,
        "fractional_numeric_values": 1,
        "unsupported_value_types": 4,
        "non_finite_numeric_values": 2,
        "invalid_numeric_ranges": 2,
    }


@pytest.mark.parametrize("symbol", ["TATAGOLD", "TATSILV", "GOLDBEES", "SILVERBEES"])
def test_integral_decimal_timestamps_and_volume_all_four_etfs(symbol):
    result = validate_response(
        symbol,
        200,
        numeric_encoding_body(volume="12500.0", timestamp_decimal=True),
        content_type="application/json",
    )
    assert result.status == "VALIDATION_PASSED_UNQUALIFIED"
    assert result.volume_numeric_diagnostics.integral_decimal_values == 5
    assert result.timestamp_numeric_diagnostics.integral_decimal_values == 5
    assert result.timestamp_conversion_failures == 0
    assert result.timestamps_converted == result.successfully_mapped_trading_dates == 5
    assert result.candidate_session_dates == EXPECTED_DATES and result.coverage_assessment_complete
    assert (
        result.timestamp_unit_policy == "UNIX_SECONDS_CANDIDATE"
        and result.exchange_timezone == "Asia/Kolkata"
    )
    assert not result.timestamp_semantics_verified and not result.source_qualified


@pytest.mark.parametrize(
    "token,kind,out_of_range",
    [
        ("1792972800.5", "fractional_numeric_values", 0),
        ("1792972800.000000000000001", "fractional_numeric_values", 0),
        ("946684799", "json_integer_values", 5),
        ("4102444800", "json_integer_values", 5),
        ("1792972800000.0", "integral_decimal_values", 5),
        ("-1.0", "integral_decimal_values", 5),
        ("1e1000000", "integral_decimal_values", 5),
        ("true", "unsupported_value_types", 0),
        ("null", "unsupported_value_types", 0),
        ('"' + TOKEN + '"', "unsupported_value_types", 0),
    ],
)
def test_bad_timestamps_do_not_create_missing_or_zero_duplicate_claims(token, kind, out_of_range):
    result = validate_response(
        "GOLDBEES",
        200,
        numeric_encoding_body(timestamp_token=token),
        content_type="application/json",
    )
    counters = asdict(result.timestamp_numeric_diagnostics)
    assert counters[kind] == 5 and counters["invalid_numeric_ranges"] == out_of_range
    assert result.coverage_valid is None and not result.coverage_assessment_complete
    assert result.missing_dates == () and result.unmapped_expected_dates == EXPECTED_DATES
    assert (
        "MISSING_OBSERVATIONS" not in result.issues
        and "DATE_COVERAGE_UNDETERMINED" in result.issues
    )
    assert result.duplicate_timestamps is None and result.duplicate_session_dates is None
    assert result.timestamp_conversion_failures == 0 and result.timestamps_converted == 0
    assert result.successfully_mapped_trading_dates == 0
    assert TOKEN not in json.dumps(asdict(result))


def test_timestamp_conversion_failure_is_counted_without_exception_echo(monkeypatch):
    def fail(stamp):
        raise OverflowError(TOKEN)

    monkeypatch.setattr("app.dhan_history_diagnostic._candidate_nse_date", fail)
    result = validate(synthetic())
    assert result.timestamp_conversion_failures == 5 and result.timestamps_converted == 0
    assert result.coverage_valid is None and result.unmapped_expected_dates == EXPECTED_DATES
    assert "TIMESTAMP_CONVERSION_FAILED" in result.issues and TOKEN not in json.dumps(
        asdict(result)
    )


def test_partial_mapping_keeps_absence_and_duplicates_indeterminate():
    payload = synthetic()
    payload["timestamp"][0] = None
    result = validate(payload)
    assert result.timestamps_converted == result.successfully_mapped_trading_dates == 4
    assert result.candidate_session_dates == EXPECTED_DATES[1:]
    assert result.unmapped_expected_dates == ("2026-10-26",) and result.missing_dates == ()
    assert result.coverage_valid is None and result.duplicate_session_dates is None


def test_candidate_date_outside_expected_exchange_sessions_is_rejected():
    payload = synthetic()
    payload["timestamp"][0] = int(
        datetime(2026, 10, 25, 18, 29, 59, tzinfo=timezone.utc).timestamp()
    )
    result = validate(payload)
    assert result.unexpected_dates == ("2026-10-25",) and result.missing_dates == ("2026-10-26",)
    assert result.coverage_assessment_complete and result.coverage_valid is False
    assert result.timestamps_converted == 5 and result.successfully_mapped_trading_dates == 4


def test_duplicate_session_after_exact_decimal_normalization():
    body = numeric_encoding_body(volume="12500.0", timestamp_decimal=True)
    stamps = synthetic()["timestamp"]
    body = body.replace((str(stamps[1]) + ".0").encode(), (str(stamps[0]) + ".000").encode())
    result = validate_response("TATAGOLD", 200, body, content_type="application/json")
    assert result.duplicate_timestamps == result.duplicate_session_dates == 1
    assert result.missing_dates == ("2026-10-27",) and not result.coverage_valid
    assert (
        result.successfully_mapped_trading_dates == 4 and result.timestamp_conversion_failures == 0
    )


def test_optional_oi_accepts_only_exact_numeric_zero():
    good = validate({**synthetic(), "open_interest": [0.0] * 5})
    assert (
        good.numeric_valid and good.open_interest_numeric_diagnostics.integral_decimal_values == 5
    )
    for bad in [0.5, -1.0, 1.0, True, "0"]:
        result = validate({**synthetic(), "open_interest": [bad] * 5})
        assert not result.numeric_valid and "UNEXPECTED_OPEN_INTEREST" in result.issues
