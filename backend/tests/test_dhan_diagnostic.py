"""Synthetic profile/error fixtures only; no provider socket is permitted."""

import json
import socket
from unittest.mock import Mock
import pytest
from app.dhan_config import load_dhan_configuration
from app.dhan_diagnostic import classify_response, configuration_problem, main, live_transport

CLIENT = "synthetic-client-id"
TOKEN = "synthetic-token-not-real-000000"
ENV = {"DHAN_ACCESS_TOKEN": TOKEN, "DHAN_CLIENT_ID": CLIENT, "DHAN_DATA_API_ENABLED": "true"}
PROFILE = {"dhanClientId": CLIENT, "tokenValidity": "synthetic validity", "dataPlan": "Active"}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("External sockets/DNS are forbidden in these tests")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)


@pytest.mark.parametrize("http_status,body,expected", [
    (401, {}, "AUTH_INVALID_OR_EXPIRED"), (403, {}, "ACCESS_DENIED"),
    (429, {"errorCode": "807"}, "RATE_LIMITED"), (500, {}, "PROVIDER_SERVICE_ERROR"),
    (502, {"errorCode": "809"}, "PROVIDER_SERVICE_ERROR"),
    (503, {}, "PROVIDER_SERVICE_ERROR"), (302, {}, "REDIRECT_REFUSED"),
    (307, {}, "REDIRECT_REFUSED"), (404, {}, "PROVIDER_REQUEST_REJECTED"),
    (204, {}, "UNEXPECTED_RESPONSE"), (999, {}, "UNEXPECTED_RESPONSE"),
    (400, {"errorCode": "807"}, "TOKEN_EXPIRED"),
    (200, {"errorCode": 807}, "TOKEN_EXPIRED"),
    (401, {"errorCode": "808"}, "INVALID_CREDENTIALS"),
    (401, {"errorCode": "809"}, "INVALID_CREDENTIALS"),
    (400, {"errorCode": "810"}, "INVALID_CREDENTIALS"),
    (400, {"errorCode": "806"}, "DATA_ENTITLEMENT_REQUIRED"),
    (400, {"errorCode": "805"}, "RATE_LIMITED"),
    (400, {"errorCode": "800"}, "PROVIDER_SERVICE_ERROR"),
    (400, {"errorCode": "DH-901"}, "AUTH_INVALID_OR_EXPIRED"),
    (400, {"errorCode": "DH-902"}, "ACCESS_OR_ENTITLEMENT_REQUIRED"),
    (400, {"errorCode": "DH-903"}, "ACCOUNT_ACCESS_RESTRICTED"),
    (400, {"errorCode": "DH-904"}, "RATE_LIMITED"),
    (400, {"errorCode": "DH-908"}, "PROVIDER_SERVICE_ERROR"),
    (400, {"errorCode": "DH-909"}, "NETWORK_ERROR"),
    (400, {"errorCode": "813"}, "PROVIDER_REQUEST_REJECTED"),
    (200, {"errorCode": TOKEN, "dataPlan": "Active"}, "PROVIDER_ERROR"),
    (200, {"errorMessage": TOKEN}, "PROVIDER_ERROR"),
])
def test_documented_error_classification_is_sanitized(http_status, body, expected):
    result = classify_response(http_status, json.dumps({**body, "ignored": TOKEN}).encode(),
                               content_type="application/json")
    assert result.status == expected and result.request_attempts == 1
    assert TOKEN not in repr(result) + json.dumps(result.report())
    if body.get("errorCode") == "DH-901":
        assert result.status != "TOKEN_EXPIRED"  # The provider does not distinguish these.


@pytest.mark.parametrize("payload", [b"not JSON", b"[]", b"null", b"{}", b'{}{}',
    b'{"dataPlan":"Active","dataPlan":"Deactive"}', b'{"dataPlan":NaN}', b'\xff',
    json.dumps({**PROFILE, "dataPlan": "unknown-" + TOKEN}).encode(),
    json.dumps({**PROFILE, "tokenValidity": None}).encode(),
    json.dumps({**PROFILE, "dhanClientId": None}).encode(),
    json.dumps({"data": PROFILE}).encode(),
])
def test_unexpected_profile_formats_never_echo_body(payload):
    result = classify_response(200, payload, content_type="application/json")
    assert result.status == "UNEXPECTED_RESPONSE"
    assert TOKEN not in repr(result) + json.dumps(result.report())


def test_profile_success_is_only_reported_auth_and_plan_not_historical_evidence():
    result = classify_response(200, json.dumps(PROFILE).encode(), content_type="application/json; charset=utf-8")
    assert result.status == "PROFILE_AUTHENTICATED_DATA_PLAN_REPORTED_ACTIVE"
    assert result.authentication_succeeded and result.data_api_plan_reported_active
    assert not result.historical_endpoint_tested and result.exit_code == 0
    assert CLIENT not in repr(result) + json.dumps(result.report())
    inactive = classify_response(200, json.dumps({**PROFILE, "dataPlan": "Deactive"}).encode(),
                                 content_type="application/json")
    assert inactive.status == "DATA_ENTITLEMENT_REQUIRED" and inactive.authentication_succeeded
    assert inactive.data_api_plan_reported_active is False
    wrong = classify_response(200, json.dumps(PROFILE).encode(), content_type="application/json",
                              expected_client_id="synthetic-other-account")
    assert wrong.status == "ACCOUNT_ID_MISMATCH" and CLIENT not in str(wrong.report())


@pytest.mark.parametrize("env,expected", [
    ({}, "INTEGRATION_DISABLED"),
    ({"DHAN_DATA_API_ENABLED": "true"}, "MISSING_ACCESS_TOKEN"),
    ({"DHAN_DATA_API_ENABLED": "invalid"}, "INVALID_CONFIGURATION"),
    ({**ENV, "DHAN_API_BASE_URL": "https://example.com/" + TOKEN}, "INVALID_CONFIGURATION"),
])
def test_configuration_preconditions_are_safe(env, expected):
    config = load_dhan_configuration(environ=env)
    assert configuration_problem(config) == expected


def test_default_command_never_loads_credentials_or_constructs_transport(monkeypatch, capsys):
    load = Mock(side_effect=AssertionError("Should not load local credentials before approval"))
    factory = Mock(side_effect=AssertionError("Should not construct a transport before approval"))
    monkeypatch.setattr("app.dhan_diagnostic.load_dhan_configuration", load)
    assert main(["--env-file", TOKEN], transport_factory=factory, environ=ENV) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "LIVE_APPROVAL_REQUIRED" and result["request_attempts"] == 0
    assert TOKEN not in str(result) and not load.called and not factory.called


@pytest.mark.parametrize("env,status", [({}, "INTEGRATION_DISABLED"),
    ({"DHAN_DATA_API_ENABLED": "true"}, "MISSING_ACCESS_TOKEN"),
    ({**ENV, "DHAN_DATA_API_ENABLED": "bad"}, "INVALID_CONFIGURATION")])
def test_acknowledgement_does_not_bypass_configuration_gate(env, status, capsys):
    factory = Mock(side_effect=AssertionError("Transport must not be constructed"))
    assert main(["--live-approved"], transport_factory=factory, environ=env) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == status and result["request_attempts"] == 0 and not factory.called


def test_cli_errors_never_echo_secret_arguments_or_file_paths(tmp_path, capsys):
    assert main(["--" + TOKEN]) == 2
    first = capsys.readouterr()
    assert TOKEN not in first.out + first.err
    assert main(["--live-approved", "--env-file", str(tmp_path / TOKEN)], environ=ENV) == 1
    second = capsys.readouterr()
    assert TOKEN not in second.out + second.err
    assert json.loads(second.out)["status"] == "INVALID_CONFIGURATION"


def test_live_transport_security_options_without_constructing_network(monkeypatch):
    constructor = Mock(return_value=object())
    monkeypatch.setattr("app.dhan_diagnostic.httpx.HTTPTransport", constructor)
    live_transport()
    options = constructor.call_args.kwargs
    assert options["verify"] is True and options["trust_env"] is False and options["retries"] == 0
    assert options["limits"].max_connections == 1 and options["limits"].max_keepalive_connections == 0


def test_factory_error_returns_only_safe_summary(capsys):
    factory = Mock(side_effect=RuntimeError(TOKEN))
    assert main(["--live-approved"], transport_factory=factory, environ=ENV) == 1
    output = capsys.readouterr()
    assert TOKEN not in output.out + output.err
    assert json.loads(output.out)["status"] == "DIAGNOSTIC_ERROR"
