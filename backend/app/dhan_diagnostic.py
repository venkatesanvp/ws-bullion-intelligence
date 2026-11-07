"""One read-only profile preflight. Live requests require explicit operator approval.

Step 5A -> D-14 / REQ-05-003/004 -> ADR-09/DC-09. No market-data
endpoint, token exchange, database, account mutation or app-startup hook.
"""

import argparse
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
import hmac
import json
from pathlib import Path
import time

import httpx

from .dhan_config import ConfigurationReadError, DhanConfiguration, load_dhan_configuration

from .dhan_http import (
    ERROR_CODES, TIMEOUT, _quiet_transport_logs, configuration_problem, live_transport,
)

PROFILE_URL = "https://api.dhan.co/v2/profile"
MAX_RESPONSE_BYTES = 65_536
BODY_BUDGET_SECONDS = 20.0
@dataclass(frozen=True)
class DiagnosticResult:
    status: str
    request_attempts: int = 0
    http_status: int | None = None
    authentication_succeeded: bool | None = None
    data_api_plan_reported_active: bool | None = None
    provider_code: str | None = None
    method: str = "GET"
    endpoint: str = PROFILE_URL
    historical_endpoint_tested: bool = False

    def report(self) -> dict:
        return asdict(self)

    @property
    def exit_code(self) -> int:
        if self.status == "PROFILE_AUTHENTICATED_DATA_PLAN_REPORTED_ACTIVE":
            return 0
        if self.status in {"LIVE_APPROVAL_REQUIRED", "INVALID_ARGUMENTS"}:
            return 2
        return 1


def _json_object(body: bytes) -> dict | None:
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError()
            result[key] = value
        return result

    def invalid_number(value):
        raise ValueError()

    try:
        value = json.loads(body.decode("utf-8"), object_pairs_hook=no_duplicates,
                           parse_constant=invalid_number)
        return value if isinstance(value, dict) else None
    except (ValueError, UnicodeError, RecursionError):
        return None


def classify_response(
    status: int, body: bytes, *, content_type: str, expected_client_id: str | None = None
) -> DiagnosticResult:
    def result(code, **kwargs):
        return DiagnosticResult(code, request_attempts=1, http_status=status, **kwargs)

    if status == 429:
        return result("RATE_LIMITED")
    if 300 <= status < 400:
        return result("REDIRECT_REFUSED")
    if 500 <= status <= 599:
        return result("PROVIDER_SERVICE_ERROR")
    if not 200 <= status <= 499:
        return DiagnosticResult("UNEXPECTED_RESPONSE", request_attempts=1)
    if len(body) > MAX_RESPONSE_BYTES:
        return result("RESPONSE_TOO_LARGE")
    is_json = content_type.partition(";")[0].strip().lower() == "application/json"
    data = _json_object(body) if is_json else None
    if data is not None and any(k in data for k in ["errorCode", "errorType", "errorMessage"]):
        code = data.get("errorCode")
        code = str(code) if type(code) is int else code
        known = code if isinstance(code, str) and code in ERROR_CODES else None
        reason = ERROR_CODES[known] if known else "PROVIDER_ERROR"
        auth = False if reason in {"TOKEN_EXPIRED", "INVALID_CREDENTIALS", "AUTH_INVALID_OR_EXPIRED"} else None
        return result(reason, provider_code=known, authentication_succeeded=auth,
                      data_api_plan_reported_active=False if reason == "DATA_ENTITLEMENT_REQUIRED" else None)
    if status == 401:
        return result("AUTH_INVALID_OR_EXPIRED", authentication_succeeded=False)
    if status == 403:
        return result("ACCESS_DENIED")
    if 400 <= status < 500:
        return result("PROVIDER_REQUEST_REJECTED")
    if status != 200 or data is None:
        return result("UNEXPECTED_RESPONSE")
    identity, validity, plan = data.get("dhanClientId"), data.get("tokenValidity"), data.get("dataPlan")
    if not (
        isinstance(identity, str) and identity.strip() and len(identity) <= 256
        and isinstance(validity, str) and validity.strip() and len(validity) <= 128
        and isinstance(plan, str) and plan in {"Active", "Deactive"}
    ):
        return result("UNEXPECTED_RESPONSE")
    if expected_client_id is not None and not hmac.compare_digest(
        identity.encode("utf-8"), expected_client_id.encode("utf-8")
    ):
        return result("ACCOUNT_ID_MISMATCH", authentication_succeeded=True)
    if plan == "Deactive":
        return result("DATA_ENTITLEMENT_REQUIRED", authentication_succeeded=True,
                      data_api_plan_reported_active=False)
    return result("PROFILE_AUTHENTICATED_DATA_PLAN_REPORTED_ACTIVE", authentication_succeeded=True,
                  data_api_plan_reported_active=True)


def run_profile_check(config: DhanConfiguration, *, transport: httpx.BaseTransport) -> DiagnosticResult:
    """Explicit transport injection supports fully offline mocked integration tests.

    Returns only an allowlisted summary. Nothing writes a response, logs a provider
    message, follows redirects or retries. The caller owns the approval decision.
    """
    problem = configuration_problem(config)
    if problem:
        return DiagnosticResult(problem)
    credentials = config.credentials
    expected_id = credentials.client_id.get_secret_value() if credentials.client_id else None
    attempted = 0
    status = None
    try:
        with _quiet_transport_logs(), httpx.Client(
            transport=transport, timeout=TIMEOUT, trust_env=False, follow_redirects=False,
            headers={"Accept": "application/json", "Accept-Encoding": "identity"},
        ) as client:
            attempted = 1
            with client.stream("GET", PROFILE_URL,
                               headers={"access-token": credentials.access_token.get_secret_value()}) as response:
                status = response.status_code
                if status == 429 or 300 <= status < 400 or 500 <= status <= 599:
                    return classify_response(status, b"", content_type="")
                if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                    return DiagnosticResult("UNEXPECTED_RESPONSE", 1, status)
                length = response.headers.get("Content-Length")
                if length is not None and (len(length) > 20 or not length.isascii() or not length.isdigit()):
                    return DiagnosticResult("UNEXPECTED_RESPONSE", 1, status)
                if length is not None and int(length) > MAX_RESPONSE_BYTES:
                    return DiagnosticResult("RESPONSE_TOO_LARGE", 1, status)
                body = bytearray()
                started = time.monotonic()
                for chunk in response.iter_bytes():
                    if time.monotonic() - started > BODY_BUDGET_SECONDS:
                        return DiagnosticResult("NETWORK_TIMEOUT", 1, status)
                    if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                        return DiagnosticResult("RESPONSE_TOO_LARGE", 1, status)
                    body.extend(chunk)
                return classify_response(status, bytes(body), content_type=response.headers.get("Content-Type", ""),
                                         expected_client_id=expected_id)
    except httpx.TimeoutException:
        return DiagnosticResult("NETWORK_TIMEOUT", attempted, status)
    except httpx.RemoteProtocolError:
        return DiagnosticResult("UNEXPECTED_RESPONSE", attempted, status)
    except (httpx.RequestError, OSError):
        return DiagnosticResult("NETWORK_ERROR", attempted, status)
    except Exception:
        # Never stringify an exception: it may contain headers, payloads or secrets.
        return DiagnosticResult("DIAGNOSTIC_ERROR", attempted, status)


class _ArgumentError(Exception):
    pass


class _SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise _ArgumentError() from None


def main(argv=None, *, transport_factory: Callable[[], httpx.BaseTransport] | None = None,
         environ: Mapping[str, str] | None = None) -> int:
    parser = _SafeParser(description="Read-only profile preflight; live use requires explicit approval.")
    parser.add_argument("--env-file", type=Path, help="Optional local dotenv file; never displayed")
    parser.add_argument("--live-approved", action="store_true",
                        help="Operator acknowledgement of separate owner approval for ONE GET")
    try:
        args = parser.parse_args(argv)
    except _ArgumentError:
        result = DiagnosticResult("INVALID_ARGUMENTS")
    else:
        if not args.live_approved:
            result = DiagnosticResult("LIVE_APPROVAL_REQUIRED")
        else:
            try:
                config = load_dhan_configuration(environ=environ, env_file=args.env_file)
            except ConfigurationReadError:
                result = DiagnosticResult("INVALID_CONFIGURATION")
            else:
                problem = configuration_problem(config)
                if problem:
                    result = DiagnosticResult(problem)
                else:
                    try:
                        with _quiet_transport_logs():
                            transport = (transport_factory or live_transport)()
                        result = run_profile_check(config, transport=transport)
                    except Exception:
                        result = DiagnosticResult("DIAGNOSTIC_ERROR")
    print(json.dumps(result.report(), sort_keys=True))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
