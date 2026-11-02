# DhanHQ read-only connectivity diagnostic

Recorded 2 November 2026 (Asia/Calcutta). Authority: owner Step 5A, implementation and mocked verification only. Trace: REQ-05-003/004 -> D-14 / ADR-09 / DC-09. Live authenticated requests and Git commits require separate explicit owner approval. Requirements, approved mathematical conventions, architecture and database schema are unchanged.

## Proposed first request and its limits

The standalone backend command proposes exactly **GET https://api.dhan.co/v2/profile**, with an `access-token` header and no body/query parameters. Dhan's [official User Profile documentation](https://dhanhq.co/docs/v2/authentication/#user-profile) recommends this as an initial integration test and documents a reported Data API plan. Public documentation was reviewed without logging into an account.

Only a fixed summary is returned: status, attempt count, HTTP status, authentication result, reported plan flag, an allowlisted provider error code, fixed method/endpoint and `historical_endpoint_tested=false`. Client/account identifiers, segments, raw token-validity strings and all other profile contents are discarded in memory. The profile response is never saved or logged. If an optional local client ID is configured, it is compared privately; a mismatch returns a fixed code without either value.

An active reported plan is **not verification of historical-data access**, dataset rights, ETF identity or data quality. The [historical-data contract](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data) instead specifies POST `/v2/charts/historical` with a token, security ID, exchange segment, instrument and explicit date range (end date exclusive). That read-only data query is not implemented or called here. Selecting its instrument/date parameters and requesting ETF prices requires a later reviewed, approved action and source-use evidence. SQ-01/T-03 remain blocked; synthetic fixtures remain development evidence only.

## Configuration and command gates

`backend/app/dhan_config.py` remains an offline loader/checker. The new standalone `backend/app/dhan_diagnostic.py` is not imported by application startup and adds no HTTP route, scheduler or frontend entry point. The checker's `network_client_implemented=false` and `authentication_implemented=false` describe the offline configuration component, not this separate command.

Ordinary startup needs no Dhan credentials. The diagnostic needs a supplied valid-shaped `DHAN_ACCESS_TOKEN`, the exact HTTPS resource base (default `https://api.dhan.co/v2`) and `DHAN_DATA_API_ENABLED=true` in its own process. `DHAN_CLIENT_ID` is optional for account matching. Application name/key/secret are not used in the request or exchanged for a token. Any supplied invalid configuration value still fails validation. Manual token generation/replacement remains the owner's responsibility; see [local configuration](DHANHQ_LOCAL_CONFIGURATION.md).

Default invocation is safe and offline, returning `LIVE_APPROVAL_REQUIRED`, zero attempts and exit 2 **before loading configuration or constructing a transport**:

```powershell
.\.venv\Scripts\python.exe -m backend.app.dhan_diagnostic
```

Both a true process-local gate and the `--live-approved` acknowledgment are required for a request. The flag records an operator acknowledgment of separate approval; it cannot grant approval by itself. Do not run the following command until the owner explicitly approves the one request:

```powershell
docker compose exec -T -e DHAN_DATA_API_ENABLED=true api uv run --frozen --no-dev python -m app.dhan_diagnostic --live-approved
```

This uses existing API-container environment credentials, overrides the gate only for the exec process, leaves `.env` and normal service configuration disabled, and performs at most one request. The current implementation/testing grant does not authorize that command. After token replacement, recreate API as described in the local instructions so its environment is current. Never put credentials in command arguments, URLs or pasted output.

## Transport and security controls

- Fixed HTTPS endpoint with TLS verification; no user-controlled URL, redirect following, token exchange, retries or automatic follow-up request. Environment proxy and certificate overrides are ignored (`trust_env=False`). The machine must provide direct HTTPS connectivity and trusted system/package CA certificates.
- Connect/pool/write timeouts are 5 seconds each; read inactivity timeout is 10 seconds. A 20-second streamed-body elapsed budget is checked between chunks, with a 65,536-byte body cap. These are not a hard total wall-clock deadline across DNS, headers and body. Compressed bodies are rejected; content length and JSON structure are bounded/validated. Responses/transports close on success or failure.
- HTTPX 0.28.1 is promoted from development to an exact runtime dependency, reusing the existing lock version. All resolved package versions and artifact hashes remain unchanged. No Dhan SDK or trading API is introduced. See [HTTPX transport](https://www.python-httpx.org/advanced/transports/), [timeouts](https://www.python-httpx.org/advanced/timeouts/) and [environment behavior](https://www.python-httpx.org/environment_variables/).
- Library logging is temporarily disabled during transport construction/request, restored afterward. No raw body, provider message/header, exception text, token, key, ID or app name is printed. CLI errors do not echo arguments. The command prints an allowlisted JSON result only. Credentials stay in backend process memory; no SQL, filesystem output, portfolio mutation or order function exists.
- Existing `.env` exclusion, restricted local permissions, API-only Compose injection and build-context exclusion remain. Host/Docker administrators can inspect runtime environment; this is not a boundary against the host owner.

## Sanitized outcomes

| Condition | Result |
| --- | --- |
| No owner-approval acknowledgment / disabled gate | LIVE_APPROVAL_REQUIRED / INTEGRATION_DISABLED; zero attempts |
| Missing token / malformed settings | MISSING_ACCESS_TOKEN / INVALID_CONFIGURATION; zero attempts |
| Documented 807 / 808, 809, 810 | TOKEN_EXPIRED / INVALID_CREDENTIALS |
| DH-901 or bare HTTP 401 | AUTH_INVALID_OR_EXPIRED; no fabricated distinction |
| 806 or profile Deactive | DATA_ENTITLEMENT_REQUIRED |
| DH-902 / bare HTTP 403 | ACCESS_OR_ENTITLEMENT_REQUIRED / ACCESS_DENIED; no entitlement certainty |
| HTTP 429, 805, DH-904 | RATE_LIMITED; Retry-After not echoed or automatically acted on |
| HTTP 5xx, 800, DH-908 | PROVIDER_SERVICE_ERROR |
| Timeout / transport failure | NETWORK_TIMEOUT / NETWORK_ERROR |
| Redirect / invalid format / oversized body | REDIRECT_REFUSED / UNEXPECTED_RESPONSE / RESPONSE_TOO_LARGE |
| Account mismatch / unknown provider error | ACCOUNT_ID_MISMATCH / PROVIDER_ERROR |
| Valid expected profile and Active plan | PROFILE_AUTHENTICATED_DATA_PLAN_REPORTED_ACTIVE; historical endpoint still untested |

Mappings use the [official annexure](https://dhanhq.co/docs/v2/annexure/). Other documented request/account codes remain distinct; unrecognized values and messages are never reflected. Expiry is not inferred from token contents or the profile's date text. Provider authentication, subscription and usage permissions remain unverified until their respective approved checks.

## Offline verification and approval record

Unit and injected HTTPX MockTransport integration tests use explicit synthetic credentials. Socket/DNS guards prevent real network connections. They exercise request shape, single-attempt behavior, gates, TLS/transport settings, all listed error classes, malformed/oversized responses, exception/header/message redaction, logging restoration and no response-file writes. Linux image probes additionally run with `--network none`. No approved flag is run with real credentials in verification.

See the [Step 5A checkpoint](../04-planning/VS-01_STEP5A_DIAGNOSTIC_CHECKPOINT.md) for executed results, exact proposed Git set and pending approval. Live execution, historical acquisition/ingestion, token exchange, trading and full VS-01 acceptance remain outside completed verification.
