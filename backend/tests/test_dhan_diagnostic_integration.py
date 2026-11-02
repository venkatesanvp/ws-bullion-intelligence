"""Mocked HTTP integration: requests/streaming/parsing/CLI with sockets forbidden."""

import json
import logging
import socket
import httpx
import pytest
from app.dhan_config import load_dhan_configuration
from app.dhan_diagnostic import MAX_RESPONSE_BYTES, PROFILE_URL, main, run_profile_check
from .test_dhan_diagnostic import CLIENT, TOKEN, ENV, PROFILE


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Live network forbidden: only MockTransport is authorized")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


class Chunks(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False

    def __iter__(self):
        yield from self.chunks

    def close(self):
        self.closed = True


def check(handler, env=ENV):
    return run_profile_check(load_dhan_configuration(environ=env), transport=httpx.MockTransport(handler))


def test_single_profile_get_exact_headers_timeouts_and_sanitized_success(monkeypatch, tmp_path, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HTTPS_PROXY", "https://" + TOKEN + "@untrusted.invalid")
    monkeypatch.setenv("SSL_CERT_FILE", TOKEN)
    caplog.set_level(logging.DEBUG)
    seen = []
    secret_values = [CLIENT, TOKEN, "synthetic-key", "synthetic-secret", "Synthetic App"]
    payload = {**PROFILE, "accessToken": TOKEN, "api_key": secret_values[2],
               "api_secret": secret_values[3], "name": secret_values[4]}

    def handler(request):
        seen.append(request)
        assert request.method == "GET" and str(request.url) == PROFILE_URL and not request.url.query
        assert request.headers["access-token"] == TOKEN
        assert request.headers["accept-encoding"] == "identity"
        assert all(k not in request.headers for k in ["app_id", "app_secret", "client_id", "dhanClientId"])
        assert not request.content and TOKEN not in str(request.url)
        assert request.extensions["timeout"] == {"connect": 5.0, "read": 10.0, "write": 5.0, "pool": 5.0}
        logging.getLogger("httpcore.connection").debug("Synthetic wire fixture %s", TOKEN)
        return httpx.Response(200, json=payload)

    env = {**ENV, "DHAN_APP_NAME": secret_values[4], "DHAN_API_KEY": secret_values[2], "DHAN_API_SECRET": secret_values[3]}
    previous = logging.root.manager.disable
    result = check(handler, env)
    assert result.exit_code == 0 and len(seen) == 1 and result.request_attempts == 1
    assert logging.root.manager.disable == previous and not list(tmp_path.iterdir())
    serialized = json.dumps(result.report()) + repr(result) + caplog.text
    assert all(value not in serialized for value in secret_values)
    assert not result.historical_endpoint_tested


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirects_never_follow_or_echo_locations(status):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"Location": "https://evil.invalid/" + TOKEN})
    result = check(handler)
    assert len(calls) == 1 and result.status == "REDIRECT_REFUSED" and TOKEN not in str(result.report())


@pytest.mark.parametrize("error,expected", [
    (httpx.ConnectTimeout, "NETWORK_TIMEOUT"), (httpx.ReadTimeout, "NETWORK_TIMEOUT"),
    (httpx.WriteTimeout, "NETWORK_TIMEOUT"), (httpx.PoolTimeout, "NETWORK_TIMEOUT"),
    (httpx.ConnectError, "NETWORK_ERROR"), (httpx.ReadError, "NETWORK_ERROR"),
    (httpx.ProxyError, "NETWORK_ERROR"), (httpx.RemoteProtocolError, "UNEXPECTED_RESPONSE"),
    (RuntimeError, "DIAGNOSTIC_ERROR"),
])
def test_transport_failures_are_sanitized_and_not_retried(error, expected, caplog):
    calls = []
    def handler(request):
        calls.append(request)
        raise error(TOKEN + CLIENT)
    result = check(handler)
    assert result.status == expected and len(calls) == 1
    assert TOKEN not in repr(result) + caplog.text and CLIENT not in str(result.report())


@pytest.mark.parametrize("status,payload,expected", [
    (401, {"errorCode": "807", "errorMessage": TOKEN}, "TOKEN_EXPIRED"),
    (401, {"errorCode": "809", "errorMessage": TOKEN}, "INVALID_CREDENTIALS"),
    (403, {"errorCode": "806", "errorMessage": TOKEN}, "DATA_ENTITLEMENT_REQUIRED"),
    (429, {"errorMessage": TOKEN}, "RATE_LIMITED"),
    (503, {"errorMessage": TOKEN}, "PROVIDER_SERVICE_ERROR"),
    (200, {**PROFILE, "dataPlan": "Deactive"}, "DATA_ENTITLEMENT_REQUIRED"),
])
def test_mocked_http_provider_failures(status, payload, expected):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, json=payload, headers={"Retry-After": TOKEN})
    result = check(handler)
    assert result.status == expected and len(calls) == 1 and TOKEN not in str(result.report())


@pytest.mark.parametrize("headers,body,expected", [
    ({"Content-Type": "text/html"}, TOKEN.encode(), "UNEXPECTED_RESPONSE"),
    ({"Content-Type": "application/json"}, TOKEN.encode(), "UNEXPECTED_RESPONSE"),
    ({"Content-Type": "application/json", "Content-Encoding": "gzip"}, b"not compressed", "UNEXPECTED_RESPONSE"),
    ({"Content-Type": "application/json", "Content-Length": "invalid-" + TOKEN}, b"{}", "UNEXPECTED_RESPONSE"),
    ({"Content-Type": "application/json", "Content-Length": "9" * 25}, b"{}", "UNEXPECTED_RESPONSE"),
    ({"Content-Type": "application/json", "Content-Length": str(MAX_RESPONSE_BYTES + 1)}, b"{}", "RESPONSE_TOO_LARGE"),
])
def test_stream_format_and_size_are_bounded(headers, body, expected):
    stream = Chunks([body])
    result = check(lambda request: httpx.Response(200, headers=headers, stream=stream))
    assert result.status == expected and stream.closed and TOKEN not in str(result.report())


def test_stream_body_limit_and_elapsed_budget_close_the_response(monkeypatch):
    stream = Chunks([b"x" * 32768] * 3)
    result = check(lambda request: httpx.Response(200, headers={"Content-Type": "application/json"}, stream=stream))
    assert result.status == "RESPONSE_TOO_LARGE" and stream.closed
    clock = iter([0.0, 21.0])
    monkeypatch.setattr("app.dhan_diagnostic.time.monotonic", lambda: next(clock))
    slow = Chunks([b"{}"])
    result = check(lambda request: httpx.Response(200, headers={"Content-Type": "application/json"}, stream=slow))
    assert result.status == "NETWORK_TIMEOUT" and slow.closed


def test_mocked_cli_end_to_end_redaction_and_no_database_or_file_writes(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("DHAN_ACCESS_TOKEN=" + TOKEN + "\nDHAN_CLIENT_ID=" + CLIENT + "\nDHAN_DATA_API_ENABLED=true\n", encoding="utf-8")
    original = env_file.read_bytes()
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={**PROFILE, "secret": TOKEN})
    assert main(["--live-approved", "--env-file", str(env_file)],
                transport_factory=lambda: httpx.MockTransport(handler), environ={}) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["request_attempts"] == 1 and len(calls) == 1
    assert TOKEN not in output.out + output.err and CLIENT not in output.out + output.err
    assert not result["historical_endpoint_tested"] and env_file.read_bytes() == original
    assert set(tmp_path.iterdir()) == {env_file}
