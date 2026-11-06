"""Mock transport only. All credentials and OHLCV are synthetic fixtures."""

from dataclasses import replace
import json
import logging
import socket
from pathlib import Path

import httpx
import pytest

from app.dhan_provider import DhanDailyProvider, MAX_RESPONSE_BYTES
from app.market_data import DailyRequest
from app.serialization import canonical
from .test_dhan_provider import TOKEN, config, request, retrieve, synthetic


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*a, **k):
        pytest.fail("unexpected live network operation")

    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)


@pytest.mark.parametrize(
    "overrides,approved,expected",
    [
        ({}, False, "EXPLICIT_REQUEST_APPROVAL_REQUIRED"),
        ({}, 1, "EXPLICIT_REQUEST_APPROVAL_REQUIRED"),
        ({"DHAN_DATA_API_ENABLED": "false"}, True, "INTEGRATION_DISABLED"),
        ({"DHAN_ACCESS_TOKEN": ""}, True, "MISSING_ACCESS_TOKEN"),
        ({"DHAN_API_BASE_URL": "http://api.dhan.co/v2"}, True, "INVALID_CONFIGURATION"),
        ({"DHAN_API_BASE_URL": "https://evil.example/v2"}, True, "INVALID_CONFIGURATION"),
        ({"DHAN_DATA_API_ENABLED": "maybe"}, True, "INVALID_CONFIGURATION"),
    ],
)
def test_gates_before_transport(overrides, approved, expected):
    def never():
        pytest.fail("transport constructed")

    provider = DhanDailyProvider(config(**overrides), transport_factory=never)
    result = provider.retrieve_daily(request(), request_approved=approved)
    assert result.failure.code == expected and result.request_attempts == 0


@pytest.mark.parametrize(
    "status,code,expected",
    [
        (401, None, "AUTH_INVALID_OR_EXPIRED"),
        (403, None, "ACCESS_DENIED"),
        (401, "807", "TOKEN_EXPIRED"),
        (403, "806", "DATA_ENTITLEMENT_REQUIRED"),
        (200, "808", "INVALID_CREDENTIALS"),
        (400, "813", "INVALID_INSTRUMENT"),
        (200, "DH-901", "AUTH_INVALID_OR_EXPIRED"),
        (200, "DH-902", "ACCESS_OR_ENTITLEMENT_REQUIRED"),
        (400, "UNKNOWN-PRIVATE-CODE", "PROVIDER_ERROR"),
        (429, "807", "RATE_LIMITED"),
        (503, None, "PROVIDER_SERVICE_ERROR"),
        (307, None, "REDIRECT_REFUSED"),
        (400, None, "PROVIDER_REQUEST_REJECTED"),
        (204, None, "UNEXPECTED_RESPONSE"),
    ],
)
def test_provider_errors_sanitized_no_retry(status, code, expected, caplog):
    caplog.set_level(logging.DEBUG)
    body = (
        json.dumps({"errorCode": code, "errorMessage": TOKEN, "account": TOKEN}).encode()
        if code
        else b""
    )
    result, _ = retrieve(body, status=status)
    assert result.failure.code == expected and result.request_attempts == 1
    assert TOKEN not in repr(result) + canonical(result.safe_summary()) + caplog.text
    if code == "UNKNOWN-PRIVATE-CODE":
        assert result.failure.provider_code is None


@pytest.mark.parametrize(
    "exception,expected",
    [
        (httpx.ReadTimeout(TOKEN), "NETWORK_TIMEOUT"),
        (httpx.ConnectTimeout(TOKEN), "NETWORK_TIMEOUT"),
        (httpx.ConnectError(TOKEN), "NETWORK_ERROR"),
        (httpx.RemoteProtocolError(TOKEN), "UNEXPECTED_RESPONSE"),
        (OSError(TOKEN), "NETWORK_ERROR"),
        (RuntimeError(TOKEN), "PROVIDER_ADAPTER_ERROR"),
    ],
)
def test_network_errors_and_log_isolation(exception, expected, caplog, tmp_path):
    caplog.set_level(logging.DEBUG)
    calls = []

    def handler(r):
        calls.append(r)
        logging.getLogger("httpcore.http11").debug(TOKEN)
        raise exception

    before = logging.root.manager.disable
    result = DhanDailyProvider(
        config(), transport_factory=lambda: httpx.MockTransport(handler)
    ).retrieve_daily(request(), request_approved=True)
    assert len(calls) == 1 and result.failure.code == expected
    assert TOKEN not in canonical(result.safe_summary()) + repr(result) + caplog.text
    assert logging.root.manager.disable == before and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "headers,body,expected",
    [
        ({"Content-Encoding": "gzip"}, synthetic(), "UNEXPECTED_RESPONSE"),
        ({"Content-Length": "no"}, synthetic(), "UNEXPECTED_RESPONSE"),
        ({"Content-Length": str(MAX_RESPONSE_BYTES + 1)}, synthetic(), "RESPONSE_TOO_LARGE"),
        ({"Content-Type": "text/html"}, synthetic(), "UNEXPECTED_RESPONSE"),
        ({}, b"x" * (MAX_RESPONSE_BYTES + 1), "RESPONSE_TOO_LARGE"),
    ],
)
def test_response_resource_bounds(headers, body, expected):
    calls = []

    def handler(r):
        calls.append(r)
        return httpx.Response(
            200,
            stream=httpx.ByteStream(body),
            headers={"Content-Type": "application/json", **headers},
        )

    result = DhanDailyProvider(
        config(), transport_factory=lambda: httpx.MockTransport(handler)
    ).retrieve_daily(request(), request_approved=True)
    assert len(calls) == 1 and result.failure.code == expected and not result.observations


def test_streamed_body_budget(monkeypatch):
    calls = iter([0.0, 21.0])
    monkeypatch.setattr("app.dhan_provider.time.monotonic", lambda: next(calls))
    result, _ = retrieve()
    assert result.failure.code == "NETWORK_TIMEOUT"


def test_safe_summary_contains_no_observation_payload_or_credentials(caplog):
    caplog.set_level(logging.DEBUG)
    result, sent = retrieve(synthetic(decimal=True))
    summary = canonical(result.safe_summary())
    for forbidden in (TOKEN, "12500", "source_timestamp", '"close"', '"open"'):
        assert forbidden not in summary + repr(result) + caplog.text
    assert TOKEN not in str(sent.url) + sent.content.decode()
    assert "client-id" not in sent.headers and "api-key" not in sent.headers
    assert "observations" not in result.safe_summary()


def test_failure_isolation_no_state_carryover():
    calls = []

    def handler(r):
        calls.append(r)
        return httpx.Response(
            200,
            content=b"malformed" if len(calls) == 1 else synthetic(),
            headers={"Content-Type": "application/json"},
        )

    provider = DhanDailyProvider(config(), transport_factory=lambda: httpx.MockTransport(handler))
    first = provider.retrieve_daily(request(), request_approved=True)
    second = provider.retrieve_daily(request("TATSILV"), request_approved=True)
    assert first.failure and not first.observations
    assert second.status == "VALIDATED_UNQUALIFIED" and len(second.observations) == 5
    assert all(x.provenance.batch.listing.symbol == "TATSILV" for x in second.observations)
    assert len(calls) == 2


def test_provider_boundary_has_no_storage_or_startup_retrieval():
    root = Path(__file__).resolve().parents[1] / "app"
    for name in (
        "market_data.py",
        "dhan_provider.py",
        "dhan_history_contract.py",
        "daily_values.py",
        "dhan_http.py",
    ):
        source = (root / name).read_text(encoding="utf-8-sig")
        assert "sqlalchemy" not in source and "psycopg" not in source
        assert "write_text(" not in source and "write_bytes(" not in source
    # Step 5D.4 explicitly authorizes composition-root wiring, never startup retrieval.
    assert "retrieve_daily(" not in (root / "main.py").read_text()
    assert "dhan_provider" not in (root / "analytics.py").read_text()
    assert "dhan_provider" not in (root / "comparison.py").read_text()


def test_normal_enabled_constructor_still_no_network():
    provider = DhanDailyProvider(config())
    assert len(provider.listings()) == 4
    result = provider.retrieve_daily(request())
    assert result.request_attempts == 0


def test_request_contract_is_provider_neutral():
    assert set(DailyRequest.__dataclass_fields__) == {"listing", "start", "end", "calendar"}
    req = request()
    assert not hasattr(req, "security_id") and not hasattr(req, "access_token")
    result, _ = retrieve(
        req=replace(req, end=req.start, calendar=None),
        body=json.dumps({k: v[:1] for k, v in json.loads(synthetic()).items()}).encode(),
    )
    assert (
        len(result.observations) == 1
        and result.provenance.provider_end_exclusive.isoformat() == "2026-10-27"
    )


def test_request_logging_guard_preserves_other_threads(caplog):
    from concurrent.futures import ThreadPoolExecutor

    caplog.set_level(logging.DEBUG)
    before = logging.root.manager.disable

    def handler(r):
        logging.getLogger("httpcore.http11").debug(TOKEN)
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(
                logging.getLogger("bullion.other").warning, "Unrelated operation retained"
            ).result()
        return httpx.Response(
            200, content=synthetic(), headers={"Content-Type": "application/json"}
        )

    result = DhanDailyProvider(
        config(), transport_factory=lambda: httpx.MockTransport(handler)
    ).retrieve_daily(request(), request_approved=True)
    assert result.status == "VALIDATED_UNQUALIFIED"
    assert TOKEN not in caplog.text
    assert "Unrelated operation retained" in caplog.text
    assert logging.root.manager.disable == before
    logging.getLogger("bullion").warning("After operation retained")
    assert "After operation retained" in caplog.text
