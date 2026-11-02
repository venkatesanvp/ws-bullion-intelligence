"""Offline DhanHQ configuration only; no authentication, client or API routes.

Scoped Step 5 grant -> REQ-05-003/004 -> ADR-09/DC-09.
Developer credentials are validated separately and never substituted for a token.
"""

import argparse
from collections.abc import Mapping
from io import StringIO
import json
import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, SecretStr

API_BASE_URL = "https://api.dhan.co/v2"
KEYS = (
    "DHAN_APP_NAME",
    "DHAN_API_KEY",
    "DHAN_API_SECRET",
    "DHAN_CLIENT_ID",
    "DHAN_ACCESS_TOKEN",
    "DHAN_API_BASE_URL",
    "DHAN_DATA_API_ENABLED",
)
CONSENT_KEYS = ("DHAN_API_KEY", "DHAN_API_SECRET", "DHAN_CLIENT_ID")


class _DhanCredentials(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)
    # The historical endpoint documents access-token, not a separate client-ID header.
    client_id: SecretStr | None = Field(default=None, exclude=True, repr=False)
    access_token: SecretStr = Field(exclude=True, repr=False)


class DhanConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)
    enabled: bool
    enabled_value_valid: bool
    api_base_url_valid: bool
    values_valid: bool
    app_name_present: bool
    api_key_present: bool
    api_secret_present: bool
    client_id_present: bool
    access_token_present: bool
    developer_credentials_complete: bool
    consent_configuration_complete: bool
    runtime_configuration_complete: bool
    missing_for_consent: tuple[str, ...]
    missing_for_historical: tuple[str, ...]
    issues: tuple[str, ...]
    credentials: _DhanCredentials | None = Field(default=None, exclude=True, repr=False)

    @property
    def api_base_url(self) -> str | None:
        return API_BASE_URL if self.api_base_url_valid else None

    @property
    def exit_code(self) -> int:
        # Missing optional setup does not prevent normal disabled operation.
        return int(not self.values_valid or (self.enabled and not self.runtime_configuration_complete))

    def report(self) -> dict:
        return {
            "status": "INVALID_CONFIGURATION"
            if self.exit_code
            else "ENABLED_CONFIGURATION_ONLY"
            if self.enabled
            else "DISABLED",
            "enabled": self.enabled,
            "enabled_value_valid": self.enabled_value_valid,
            "api_base_url_valid": self.api_base_url_valid,
            "app_name_present": self.app_name_present,
            "api_key_present": self.api_key_present,
            "api_secret_present": self.api_secret_present,
            "client_id_present": self.client_id_present,
            "access_token_present": self.access_token_present,
            "developer_credentials_complete": self.developer_credentials_complete,
            "consent_configuration_complete": self.consent_configuration_complete,
            "runtime_configuration_complete": self.runtime_configuration_complete,
            "configuration_valid": self.values_valid and self.runtime_configuration_complete,
            "missing_for_consent": list(self.missing_for_consent),
            "missing_for_historical": list(self.missing_for_historical),
            "issues": list(self.issues),
            "network_client_implemented": False,
            "authentication_implemented": False,
        }


class ConfigurationReadError(Exception):
    """Only a fixed safe message is exposed to the caller."""


def _environment(environ: Mapping[str, str], env_file: Path | None) -> dict:
    selected = {}
    unreadable = False
    if env_file is not None:
        try:
            with env_file.open(encoding="utf-8-sig") as handle:
                parsed = dotenv_values(stream=StringIO(handle.read()), interpolate=False)
            selected = {key: parsed[key] for key in KEYS if key in parsed}
        except (OSError, UnicodeError):
            unreadable = True
        if unreadable:
            raise ConfigurationReadError("DHAN_ENV_FILE_UNREADABLE")
    selected.update({key: environ[key] for key in KEYS if key in environ})
    return selected


def _present(raw) -> bool:
    return isinstance(raw, str) and bool(raw.strip())


def _valid_optional(raw, bound: int, *, label=False) -> bool:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return True
    if not isinstance(raw, str) or len(raw) > bound:
        return False
    # App name is a human label: spaces/Unicode are allowed, controls are not.
    return raw.isprintable() if label else raw.isascii() and all(33 <= ord(c) <= 126 for c in raw)


def load_dhan_configuration(
    *, environ: Mapping[str, str] | None = None, env_file: Path | None = None
) -> DhanConfiguration:
    """Read seven settings without requests; environment overrides explicit dotenv.

    Key/secret/name values are discarded after presence/shape validation. There is
    no token exchange. Runtime configuration needs a supplied access token; consent
    prerequisites are separately reported, never treated as historical credentials.
    """
    values = _environment(os.environ if environ is None else environ, env_file)
    flag = values.get("DHAN_DATA_API_ENABLED", "false")
    flag_valid = isinstance(flag, str) and flag.casefold() in {"true", "false"}
    enabled = flag_valid and flag.casefold() == "true"
    base = values.get("DHAN_API_BASE_URL", API_BASE_URL)
    base_valid = isinstance(base, str) and base in {API_BASE_URL, API_BASE_URL + "/"}
    issues = []
    if not flag_valid:
        issues.append("INVALID_DHAN_DATA_API_ENABLED")
    if not base_valid:
        issues.append("INVALID_DHAN_API_BASE_URL")
    bounds = {"DHAN_APP_NAME": 256, "DHAN_CLIENT_ID": 256,
              "DHAN_API_KEY": 8192, "DHAN_API_SECRET": 8192, "DHAN_ACCESS_TOKEN": 8192}
    present, valid = {}, {}
    for key, bound in bounds.items():
        raw = values.get(key)
        present[key] = _present(raw)
        valid[key] = _valid_optional(raw, bound, label=key == "DHAN_APP_NAME")
        if not valid[key]:
            issues.append("INVALID_" + key)
    values_valid = flag_valid and base_valid and all(valid.values())
    missing_consent = tuple(key for key in CONSENT_KEYS if not present[key])
    missing_historical = () if present["DHAN_ACCESS_TOKEN"] else ("DHAN_ACCESS_TOKEN",)
    if missing_historical:
        issues.append("MISSING_DHAN_ACCESS_TOKEN")
    developer_complete = all(present[k] and valid[k] for k in ["DHAN_API_KEY", "DHAN_API_SECRET"])
    consent_complete = developer_complete and present["DHAN_CLIENT_ID"] and valid["DHAN_CLIENT_ID"]
    runtime_complete = values_valid and present["DHAN_ACCESS_TOKEN"] and valid["DHAN_ACCESS_TOKEN"]
    credentials = (
        _DhanCredentials(
            client_id=SecretStr(values["DHAN_CLIENT_ID"]) if present["DHAN_CLIENT_ID"] else None,
            access_token=SecretStr(values["DHAN_ACCESS_TOKEN"]),
        )
        if enabled and values_valid and runtime_complete
        else None
    )
    return DhanConfiguration(
        enabled=enabled, enabled_value_valid=flag_valid, api_base_url_valid=base_valid,
        values_valid=values_valid, app_name_present=present["DHAN_APP_NAME"],
        api_key_present=present["DHAN_API_KEY"], api_secret_present=present["DHAN_API_SECRET"],
        client_id_present=present["DHAN_CLIENT_ID"], access_token_present=present["DHAN_ACCESS_TOKEN"],
        developer_credentials_complete=developer_complete, consent_configuration_complete=consent_complete,
        runtime_configuration_complete=runtime_complete, missing_for_consent=missing_consent,
        missing_for_historical=missing_historical, issues=tuple(issues), credentials=credentials,
    )


class _ArgumentError(Exception):
    pass


class _SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise _ArgumentError() from None


def main(argv=None) -> int:
    parser = _SafeParser(description="Offline DhanHQ configuration check; no requests.")
    parser.add_argument("--env-file", type=Path, help="Optional local dotenv file; values never printed")
    try:
        args = parser.parse_args(argv)
    except _ArgumentError:
        print(json.dumps({"status": "INVALID_CONFIGURATION", "issues": ["INVALID_DHAN_CHECK_ARGUMENTS"]}))
        return 2
    try:
        config = load_dhan_configuration(env_file=args.env_file)
    except ConfigurationReadError:
        print(json.dumps({"status": "INVALID_CONFIGURATION", "issues": ["DHAN_ENV_FILE_UNREADABLE"]}))
        return 1
    print(json.dumps(config.report(), sort_keys=True))
    return config.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
