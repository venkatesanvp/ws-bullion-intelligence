"""SYNTHETIC_TEST OHLCV with injected HTTP only; real DNS/socket use forbidden."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
import logging
import socket
from unittest.mock import Mock

import httpx
import pytest
from app.dhan_config import load_dhan_configuration
from app.dhan_history_diagnostic import (
    EXPECTED_DATES,
    HISTORY_URL,
    MAX_RESPONSE_BYTES,
    fetch_one,
    main,
    run_batch,
)

TOKEN = "SYNTHETIC-HISTORY-ACCESS-TOKEN-NOT-REAL"
CLIENT = "SYNTHETIC-ACCOUNT-NOT-REAL"
ENV = {
    "DHAN_ACCESS_TOKEN": TOKEN,
    "DHAN_CLIENT_ID": CLIENT,
    "DHAN_DATA_API_ENABLED": "true",
    "DHAN_API_KEY": "SYNTHETIC-KEY",
    "DHAN_API_SECRET": "SYNTHETIC-SECRET",
    "DHAN_APP_NAME": "SYNTHETIC-APP",
}


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network forbidden in offline historical tests")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def synthetic(count=5):
    return {
        "open": [100.25] * count,
        "high": [102] * count,
        "low": [99] * count,
        "close": [101.125] * count,
        "volume": [12345] * count,
        "timestamp": [
            int(datetime(2026, 10, d, tzinfo=timezone.utc).timestamp())
            for d in range(26, 26 + count)
        ],
    }


def batch(handler, **kwargs):
    return run_batch(
        load_dhan_configuration(environ=ENV),
        transport=httpx.MockTransport(handler),
        pause=kwargs.get("pause", lambda seconds: None),
    )


class Chunks(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks, self.closed, self.reads = chunks, False, 0

    def __iter__(self):
        for chunk in self.chunks:
            self.reads += 1
            yield chunk

    def close(self):
        self.closed = True


def test_four_requests_exact_order_shape_timeouts_redaction_and_no_writes(
    tmp_path, monkeypatch, caplog
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HTTPS_PROXY", "https://" + TOKEN + ".invalid")
    monkeypatch.setenv("SSL_CERT_FILE", TOKEN)
    monkeypatch.setattr(
        "sqlalchemy.create_engine", Mock(side_effect=AssertionError("No database allowed"))
    )
    caplog.set_level(logging.DEBUG)
    before = logging.root.manager.disable
    calls, pauses = [], []
    expected = [
        ("TATAGOLD", "21401"),
        ("TATSILV", "21428"),
        ("GOLDBEES", "14428"),
        ("SILVERBEES", "8080"),
    ]

    def handler(request):
        calls.append(request)
        logging.getLogger("httpcore.http11").debug(TOKEN)
        assert (
            request.method == "POST" and str(request.url) == HISTORY_URL and not request.url.query
        )
        assert request.headers["access-token"] == TOKEN
        assert request.headers["Accept-Encoding"] == "identity"
        assert request.headers["Content-Type"] == "application/json"
        assert all(
            k not in request.headers for k in ("app_id", "app_secret", "client-id", "Authorization")
        )
        assert request.extensions["timeout"] == {
            "connect": 5.0,
            "read": 10.0,
            "write": 5.0,
            "pool": 5.0,
        }
        assert json.loads(request.content) == {
            "securityId": expected[len(calls) - 1][1],
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "oi": False,
            "fromDate": "2026-10-26",
            "toDate": "2026-10-31",
        }
        return httpx.Response(200, json=synthetic())

    result = batch(handler, pause=pauses.append)
    assert len(calls) == result["request_attempts"] == 4 and pauses == [1.0, 1.0, 1.0]
    assert [x["symbol"] for x in result["datasets"]] == [x[0] for x in expected]
    assert all(x["status"] == "VALIDATION_PASSED_UNQUALIFIED" for x in result["datasets"])
    assert all(
        x["technical_inputs_compatible"] and not x["qualified_for_comparison"]
        for x in result["comparisons"]
    )
    assert logging.root.manager.disable == before and list(tmp_path.iterdir()) == []
    output = json.dumps(result) + caplog.text
    assert all(v not in output for k, v in ENV.items() if k not in {"DHAN_DATA_API_ENABLED"})
    assert "101.125" not in output and "12345" not in output


def test_instrument_coverage_is_independent_and_empty_does_not_imply_other_empty():
    counts = {"21401": 5, "21428": 4, "14428": 0, "8080": 5}
    seen = []

    def handler(request):
        key = json.loads(request.content)["securityId"]
        seen.append(key)
        return httpx.Response(200, json=synthetic(counts[key]))

    result = batch(handler)
    assert len(seen) == 4 and [x["observation_count"] for x in result["datasets"]] == [5, 4, 0, 5]
    assert result["datasets"][1]["missing_dates"] == ("2026-10-30",)
    assert all(not x["qualified_for_comparison"] for x in result["comparisons"])


@pytest.mark.parametrize(
    "status,payload,expected",
    [
        (401, {"errorCode": "807", "errorMessage": TOKEN}, "TOKEN_EXPIRED"),
        (401, {"errorCode": "809", "errorMessage": TOKEN}, "INVALID_CREDENTIALS"),
        (403, {"errorCode": "806", "errorMessage": TOKEN}, "DATA_ENTITLEMENT_REQUIRED"),
        (400, {"errorCode": "813", "errorMessage": TOKEN}, "INVALID_INSTRUMENT"),
        (429, {"errorMessage": TOKEN}, "RATE_LIMITED"),
        (503, {"errorMessage": TOKEN}, "PROVIDER_SERVICE_ERROR"),
        (302, {}, "REDIRECT_REFUSED"),
        (307, {}, "REDIRECT_REFUSED"),
        (308, {}, "REDIRECT_REFUSED"),
        (200, {"data": TOKEN}, "UNEXPECTED_RESPONSE"),
    ],
)
def test_provider_failures_stop_batch_without_retry_or_follow_up(status, payload, expected):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status,
            json=payload,
            headers={"Location": "https://evil.invalid/" + TOKEN, "Retry-After": TOKEN},
        )

    result = batch(handler)
    assert len(calls) == result["request_attempts"] == 1
    assert result["datasets"][0]["status"] == expected
    assert all(x["status"] == "NOT_ATTEMPTED_AFTER_FAILURE" for x in result["datasets"][1:])
    assert result["status"] == "BATCH_STOPPED_UNQUALIFIED" and TOKEN not in json.dumps(result)


@pytest.mark.parametrize(
    "error,expected",
    [
        (httpx.ConnectTimeout, "NETWORK_TIMEOUT"),
        (httpx.ReadTimeout, "NETWORK_TIMEOUT"),
        (httpx.WriteTimeout, "NETWORK_TIMEOUT"),
        (httpx.PoolTimeout, "NETWORK_TIMEOUT"),
        (httpx.ConnectError, "NETWORK_ERROR"),
        (httpx.ReadError, "NETWORK_ERROR"),
        (httpx.RemoteProtocolError, "UNEXPECTED_RESPONSE"),
        (OSError, "NETWORK_ERROR"),
        (RuntimeError, "DIAGNOSTIC_ERROR"),
    ],
)
def test_network_failures_sanitized_and_no_retry(error, expected, caplog):
    seen = []

    def handler(request):
        seen.append(request)
        raise error(TOKEN + CLIENT)

    result = batch(handler)
    assert len(seen) == result["request_attempts"] == 1
    assert result["datasets"][0]["status"] == expected
    assert TOKEN not in caplog.text + json.dumps(result) and CLIENT not in json.dumps(result)


@pytest.mark.parametrize(
    "headers,body,expected",
    [
        ({"Content-Type": "text/html"}, TOKEN.encode(), "UNEXPECTED_RESPONSE"),
        ({"Content-Type": "application/json"}, b"bad-json", "UNEXPECTED_RESPONSE"),
        (
            {"Content-Type": "application/json", "Content-Encoding": "gzip"},
            b"bad",
            "UNEXPECTED_RESPONSE",
        ),
        (
            {"Content-Type": "application/json", "Content-Length": TOKEN},
            b"{}",
            "UNEXPECTED_RESPONSE",
        ),
        (
            {"Content-Type": "application/json", "Content-Length": "9" * 25},
            b"{}",
            "UNEXPECTED_RESPONSE",
        ),
        (
            {"Content-Type": "application/json", "Content-Length": str(MAX_RESPONSE_BYTES + 1)},
            b"{}",
            "RESPONSE_TOO_LARGE",
        ),
    ],
)
def test_response_bounds_and_formats_close_stream(headers, body, expected):
    stream = Chunks([body])
    result = batch(lambda request: httpx.Response(200, headers=headers, stream=stream))
    assert (
        result["datasets"][0]["status"] == expected
        and stream.closed
        and result["request_attempts"] == 1
    )
    assert TOKEN not in json.dumps(result)


def test_streamed_size_elapsed_budget_and_close(monkeypatch):
    stream = Chunks([b"x" * 32768] * 9)
    result = batch(
        lambda request: httpx.Response(
            200, headers={"Content-Type": "application/json"}, stream=stream
        )
    )
    assert result["datasets"][0]["status"] == "RESPONSE_TOO_LARGE" and stream.closed
    clock = iter([0.0, 21.0])
    monkeypatch.setattr("app.dhan_history_diagnostic.time.monotonic", lambda: next(clock))
    slow = Chunks([b"{}"])
    result = batch(
        lambda request: httpx.Response(
            200, headers={"Content-Type": "application/json"}, stream=slow
        )
    )
    assert result["datasets"][0]["status"] == "NETWORK_TIMEOUT" and slow.closed


def test_low_level_invalid_symbol_never_uses_http_or_reflects_input():
    handler = Mock(side_effect=AssertionError("No request permitted"))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_one(load_dhan_configuration(environ=ENV), TOKEN, client=client)
    assert result.status == "INVALID_INSTRUMENT" and result.request_attempts == 0
    assert TOKEN not in json.dumps(asdict(result))
    handler.assert_not_called()


def test_cli_mocked_end_to_end_with_synthetic_env_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(k + "=" + v for k, v in ENV.items()) + "\n")
    before = env_file.read_bytes()
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=synthetic())

    assert (
        main(
            ["--live-approved", "--permissions-reviewed", "--env-file", str(env_file)],
            environ={},
            transport_factory=lambda: httpx.MockTransport(handler),
            pause=lambda seconds: None,
        )
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["request_attempts"] == len(calls) == 4
    assert all(x["candidate_session_dates"] == list(EXPECTED_DATES) for x in result["datasets"])
    assert not result["source_qualified"] and not result["raw_responses_persisted"]
    assert TOKEN not in output.out + output.err and CLIENT not in output.out + output.err
    assert env_file.read_bytes() == before and set(tmp_path.iterdir()) == {env_file}


def test_transport_factory_failure_has_no_secret_error(capsys):
    factory = Mock(side_effect=RuntimeError(TOKEN))
    assert (
        main(["--live-approved", "--permissions-reviewed"], environ=ENV, transport_factory=factory)
        == 1
    )
    output = capsys.readouterr()
    assert json.loads(output.out)["request_attempts"] == 0 and TOKEN not in output.out + output.err


def test_inter_request_control_failure_reports_stopped_without_another_request():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=synthetic())

    pause = Mock(side_effect=RuntimeError(TOKEN))
    result = batch(handler, pause=pause)
    assert len(calls) == result["request_attempts"] == 1
    assert result["status"] == "BATCH_STOPPED_UNQUALIFIED"
    assert all(x["status"] == "DIAGNOSTIC_ERROR" for x in result["datasets"][1:])
    assert TOKEN not in json.dumps(result)
