"""Offline/synthetic credential fixtures. Never contact a provider or persist credentials."""

import json
import logging
import socket
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.dhan_config import API_BASE_URL, KEYS, load_dhan_configuration, main
from app.main import create_app
from .conftest import TOKEN, test_settings as settings_for_test

CLIENT = "synthetic-client-id"
ACCESS = "synthetic-access-token-not-real-000000"
ENV = {"DHAN_CLIENT_ID": CLIENT, "DHAN_ACCESS_TOKEN": ACCESS}
APP = {"DHAN_APP_NAME": "Synthetic Developer App", "DHAN_API_KEY": "synthetic-api-key-not-real", "DHAN_API_SECRET": "synthetic-api-secret-not-real"}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected outbound socket connection")

    original_connect = socket.socket.connect
    original_lookup = socket.getaddrinfo

    def local_connect(sock, address):
        # Windows asyncio creates a loopback socket pair even with ASGI transport.
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(sock, address)
        return forbidden()

    def local_lookup(host, *args, **kwargs):
        if host in {"127.0.0.1", "::1", "localhost"}:
            return original_lookup(host, *args, **kwargs)
        return forbidden()

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", local_connect)
    monkeypatch.setattr(socket, "getaddrinfo", local_lookup)
    for name in KEYS:
        monkeypatch.delenv(name, raising=False)


def test_disabled_empty_credentials_are_optional_and_not_retained():
    config = load_dhan_configuration(environ={})
    assert config.report()["status"] == "DISABLED" and not config.enabled
    assert config.exit_code == 0 and config.credentials is None
    assert set(config.issues) == {"MISSING_DHAN_ACCESS_TOKEN"}
    assert set(config.missing_for_consent) == {"DHAN_API_KEY", "DHAN_API_SECRET", "DHAN_CLIENT_ID"}
    assert config.missing_for_historical == ("DHAN_ACCESS_TOKEN",)
    supplied = load_dhan_configuration(environ=ENV)
    assert supplied.report()["configuration_valid"] and supplied.credentials is None


@pytest.mark.parametrize("enabled", ["true", "TRUE", "false", "FALSE"])
def test_enabled_and_disabled_valid_configuration_no_network(enabled):
    config = load_dhan_configuration(environ={**ENV, "DHAN_DATA_API_ENABLED": enabled})
    assert config.enabled == (enabled.lower() == "true") and config.exit_code == 0
    assert config.api_base_url == API_BASE_URL
    if config.enabled:
        assert config.credentials.client_id.get_secret_value() == CLIENT
        assert config.credentials.access_token.get_secret_value() == ACCESS
        assert config.credentials.model_dump() == {}
        assert config.credentials.model_dump_json() == "{}"
    for representation in [repr(config), str(config), config.model_dump_json(), json.dumps(config.report())]:
        assert CLIENT not in representation and ACCESS not in representation
    assert "credentials" not in config.model_dump()


@pytest.mark.parametrize("missing", ["DHAN_CLIENT_ID", "DHAN_ACCESS_TOKEN"])
def test_runtime_requirements_distinguish_client_id_from_access_token(missing):
    config = load_dhan_configuration(
        environ={**{k: v for k, v in ENV.items() if k != missing}, "DHAN_DATA_API_ENABLED": "true"}
    )
    assert config.enabled
    if missing == "DHAN_ACCESS_TOKEN":
        assert config.exit_code == 1 and config.credentials is None
        assert "MISSING_DHAN_ACCESS_TOKEN" in config.issues
    else:
        assert config.exit_code == 0 and config.credentials.client_id is None
        assert config.runtime_configuration_complete
        assert "DHAN_CLIENT_ID" in config.missing_for_consent
    assert CLIENT not in str(config.report()) and ACCESS not in str(config.report())


@pytest.mark.parametrize("value", ["yes", "1", "", "enabled-" + ACCESS])
def test_invalid_enabled_value_fails_closed(value):
    config = load_dhan_configuration(environ={**ENV, "DHAN_DATA_API_ENABLED": value})
    assert not config.enabled and not config.enabled_value_valid and config.exit_code == 1
    assert config.credentials is None and "INVALID_DHAN_DATA_API_ENABLED" in config.issues
    assert value not in str(config.report()) if value else True


@pytest.mark.parametrize(
    "url",
    ["http://api.dhan.co/v2", "https://example.com/v2", "https://api.dhan.co/v2/orders",
     "https://" + ACCESS + "@api.dhan.co/v2", API_BASE_URL + "?token=" + ACCESS, ""],
)
def test_base_url_is_fixed_https_host_path_and_never_echoed(url):
    config = load_dhan_configuration(environ={**ENV, "DHAN_API_BASE_URL": url})
    assert config.exit_code == 1 and not config.api_base_url_valid
    assert config.api_base_url is None and config.credentials is None
    assert "INVALID_DHAN_API_BASE_URL" in config.issues and ACCESS not in str(config.report())


@pytest.mark.parametrize("name,value", [("DHAN_CLIENT_ID", CLIENT + "\n"), ("DHAN_ACCESS_TOKEN", ACCESS + "\r\n"), ("DHAN_ACCESS_TOKEN", "x" * 8193)])
def test_invalid_credentials_do_not_escape_or_become_available(name, value):
    config = load_dhan_configuration(environ={**ENV, name: value, "DHAN_DATA_API_ENABLED": "true"})
    assert config.exit_code == 1 and config.credentials is None
    assert "INVALID_" + name in config.issues
    assert value not in str(config.report()) and ACCESS not in repr(config)


def test_explicit_dotenv_loading_precedence_and_no_interpolation(tmp_path):
    file = tmp_path / ".env"
    file.write_text(
        'DHAN_CLIENT_ID="file-client"\nDHAN_ACCESS_TOKEN="${NOT_EXPANDED}"\n'
        'DHAN_DATA_API_ENABLED=true\nUNRELATED_CREDENTIAL=do-not-retain\n', encoding="utf-8"
    )
    config = load_dhan_configuration(environ={"DHAN_CLIENT_ID": CLIENT}, env_file=file)
    assert config.credentials.client_id.get_secret_value() == CLIENT
    assert config.credentials.access_token.get_secret_value() == "${NOT_EXPANDED}"
    assert "UNRELATED_CREDENTIAL" not in str(config.model_dump())
    assert not load_dhan_configuration(environ={}).client_id_present


def test_cli_missing_and_invalid_safe_offline_reports(monkeypatch, capsys, tmp_path):
    assert main([]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "DISABLED"
    for name, value in {**ENV, **APP, "DHAN_DATA_API_ENABLED": "true"}.items():
        monkeypatch.setenv(name, value)
    assert main([]) == 0
    report = capsys.readouterr()
    assert CLIENT not in report.out and ACCESS not in report.out and not report.err
    assert not json.loads(report.out)["network_client_implemented"]
    assert main(["--env-file", str(tmp_path / (ACCESS + ".env"))]) == 1
    report = capsys.readouterr()
    assert ACCESS not in report.out and ACCESS not in report.err
    assert json.loads(report.out)["issues"] == ["DHAN_ENV_FILE_UNREADABLE"]


def test_cli_invalid_arguments_do_not_echo_accidentally_supplied_secrets(capsys):
    assert main(["--" + ACCESS, CLIENT]) == 2
    report = capsys.readouterr()
    assert ACCESS not in report.out + report.err and CLIENT not in report.out + report.err
    assert json.loads(report.out)["issues"] == ["INVALID_DHAN_CHECK_ARGUMENTS"]


@pytest.mark.parametrize("enabled,credentials", [(None, {}), ("false", ENV), ("true", ENV), ("invalid", ENV), ("true", {})])
def test_general_app_startup_and_errors_ignore_provider_settings(monkeypatch, caplog, enabled, credentials):
    caplog.set_level(logging.INFO, logger="bullion")
    for name, value in ({**credentials, **APP} if credentials else {}).items():
        monkeypatch.setenv(name, value)
    if enabled is not None:
        monkeypatch.setenv("DHAN_DATA_API_ENABLED", enabled)
    settings = settings_for_test()
    assert not any(name.startswith("dhan") for name in Settings.model_fields)
    assert CLIENT not in repr(settings) and ACCESS not in repr(settings)
    monkeypatch.setattr("app.main.schema_ready", lambda engine: False)
    app = create_app(settings)
    with TestClient(app) as client:
        responses = [client.get("/api/v1/health/live"), client.get("/api/v1/health/ready"),
                     client.get("/api/v1/health/ready", headers={"Authorization": "Bearer " + TOKEN}),
                     client.get("/api/v1/dhan/config", headers={"Authorization": "Bearer " + TOKEN})]
    assert [r.status_code for r in responses] == [200, 401, 503, 404]
    text = caplog.text + "".join(r.text for r in responses)
    assert CLIENT not in text and ACCESS not in text
    assert all(value not in text for value in APP.values())


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize("with_client", [False, True])
def test_app_keys_are_consent_prerequisites_and_never_replace_runtime_token(enabled, with_client):
    env = {**APP, "DHAN_DATA_API_ENABLED": enabled}
    if with_client:
        env["DHAN_CLIENT_ID"] = CLIENT
    config = load_dhan_configuration(environ=env)
    assert config.developer_credentials_complete
    assert config.consent_configuration_complete == with_client
    assert not config.runtime_configuration_complete and config.credentials is None
    assert config.exit_code == (1 if enabled == "true" else 0)
    assert config.missing_for_historical == ("DHAN_ACCESS_TOKEN",)
    assert all(value not in repr(config) + config.model_dump_json() + str(config.report()) for value in APP.values())
    assert not config.report()["authentication_implemented"]


def test_historical_token_only_configuration_does_not_require_developer_credentials():
    config = load_dhan_configuration(environ={"DHAN_ACCESS_TOKEN": ACCESS, "DHAN_DATA_API_ENABLED": "true"})
    assert config.runtime_configuration_complete and config.exit_code == 0
    assert not config.developer_credentials_complete and not config.consent_configuration_complete
    assert config.credentials.client_id is None
    assert config.credentials.access_token.get_secret_value() == ACCESS
    assert config.credentials.model_dump_json() == "{}"


@pytest.mark.parametrize("missing", ["DHAN_API_KEY", "DHAN_API_SECRET"])
def test_partial_developer_pair_is_explicit_and_optional_while_disabled(missing):
    config = load_dhan_configuration(environ={k: v for k, v in APP.items() if k != missing})
    assert not config.developer_credentials_complete and missing in config.missing_for_consent
    assert config.exit_code == 0 and config.credentials is None


@pytest.mark.parametrize("name", [None, "", "Synthetic App Name", "Synthetic " + chr(0x20B9)])
def test_app_name_is_optional_label_and_does_not_satisfy_authentication(name):
    env = {k: v for k, v in APP.items() if k != "DHAN_APP_NAME"}
    env.update(DHAN_CLIENT_ID=CLIENT)
    if name is not None:
        env["DHAN_APP_NAME"] = name
    config = load_dhan_configuration(environ=env)
    assert config.consent_configuration_complete and config.developer_credentials_complete
    assert config.app_name_present == bool(name)
    assert not config.runtime_configuration_complete and config.exit_code == 0
    if name:
        assert name not in str(config.report()) + repr(config)


@pytest.mark.parametrize("key,value", [
    ("DHAN_APP_NAME", "Synthetic\nApp"), ("DHAN_APP_NAME", "x" * 257),
    ("DHAN_API_KEY", "synthetic-key\r\n"), ("DHAN_API_SECRET", "synthetic-secret\n"),
    ("DHAN_API_KEY", "x" * 8193), ("DHAN_API_SECRET", "secret" + chr(0x20B9)),
])
def test_invalid_developer_values_are_redacted_and_fail_closed(key, value):
    config = load_dhan_configuration(environ={**APP, **ENV, key: value, "DHAN_DATA_API_ENABLED": "true"})
    assert config.exit_code == 1 and config.credentials is None
    assert "INVALID_" + key in config.issues
    assert value not in str(config.report()) + repr(config) + config.model_dump_json()


@pytest.mark.parametrize("enabled", ["false", "true"])
def test_all_developer_values_remain_out_of_model_and_cli_output(monkeypatch, capsys, enabled):
    env = {**APP, **ENV, "DHAN_DATA_API_ENABLED": enabled}
    config = load_dhan_configuration(environ=env)
    assert config.consent_configuration_complete and config.runtime_configuration_complete
    text = repr(config) + config.model_dump_json() + json.dumps(config.report())
    for key, value in env.items():
        monkeypatch.setenv(key, value)
        if key != "DHAN_DATA_API_ENABLED":
            assert value not in text
    assert "api_key" not in type(config).model_fields and "api_secret" not in type(config).model_fields
    assert "app_name" not in type(config).model_fields
    assert main([]) == 0
    output = capsys.readouterr()
    assert all(value not in output.out + output.err for value in [*APP.values(), *ENV.values()])
