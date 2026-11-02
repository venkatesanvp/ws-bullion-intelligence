# DhanHQ local developer and runtime configuration

Authority: human Step 5 environment/offline-validation grants, revised 2 November 2026 (Asia/Calcutta). Trace: scoped REQ-05-003/004 -> ADR-09/DC-09. This section records the configuration checkpoint; the later standalone Step 5A diagnostic is described below. No token exchange, historical acquisition or trading capability is implemented. Account/app ownership is reported by the owner; entitlements and source permissions are unverified.

## Local values and preservation

The seven settings are:

```dotenv
# DhanHQ Developer Application
DHAN_APP_NAME=
DHAN_API_KEY=
DHAN_API_SECRET=

# Optional runtime credentials
DHAN_CLIENT_ID=
DHAN_ACCESS_TOKEN=

# DhanHQ API settings
DHAN_API_BASE_URL=https://api.dhan.co/v2
DHAN_DATA_API_ENABLED=false
```

The three missing developer fields were appended to the actual existing root `.env`; its previous four Dhan fields and every other byte/value were preserved. Existing keys are not duplicated, reordered or overwritten merely to match this example's grouping. Enter values directly in a local editor. Keep the gate false. `.env.example` contains the complete grouped template with blanks, never real values.

All credentials are optional for ordinary application startup. The token is required for any later historical-data request; the optional-runtime heading does not mean unauthenticated historical access. App keys are not an access token. App name is a label and cannot substitute for the API key or client ID.

## Authentication model verified from official documentation

Reviewed 2 November 2026; public documentation only, with no account login or API request:

| Setting | Role |
| --- | --- |
| DHAN_APP_NAME | Entered when registering the application. The documented authentication requests contain no app-name field; treating this as identification metadata rather than an authentication credential is an inference from that contract. |
| DHAN_API_KEY / DHAN_API_SECRET | Application credentials, used to obtain a token through consent. The API key maps to the documented app_id header; the secret maps to app_secret. They are not historical-request substitutes for access-token. |

[Dhan's official key-generation guide](https://dhan.co/support/platforms/dhanhq-api/how-to-generate-the-api-key-on-dhan-platform-for-api-s/) describes app registration, redirect URL, optional postback, the key pair's 12-month validity and the need to obtain an access token before API calls.

| Question | Confirmed distinction |
| --- | --- |
| Client ID | Separate account identifier required by generate-consent and web-token renewal. It is not the app key/name. |
| Individual developer flow | Generate consent using client ID and app headers, complete browser login/2FA at the registered redirect, then consume tokenId with app headers. The result includes accessToken and expiryTime. |
| Lifetime / refresh | Current docs give web tokens 24 hours. Renewal replaces only an active web-generated token; expired tokens cannot be renewed. Do not extend this renewal method to app-issued tokens. Use returned expiryTime for app-flow expiry. |

These distinctions follow [DhanHQ individual authentication](https://dhanhq.co/docs/v2/authentication/#api-key-secret). Its app-token expiry response is defined in IST. This is the individual-app flow, not the separate partner_id/partner_secret flow. Older support guidance about longer token lifetimes is not used as the current contract.

The [historical endpoint documentation](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data) supplies access-token authentication; it does not document a separate client-ID header for that request. Thus a supplied access token satisfies the historical credential prerequisite; client ID remains relevant to consent, renewal and account attribution. Data entitlement and source rights are separate prerequisites. Authentication endpoints use auth.dhan.co; the configured api.dhan.co/v2 URL is the resource API base, not a replacement authentication URL.

## Backend-only handling

Compose passes all seven settings **only to api**, not UI, migration, PostgreSQL or the test DB. No provider values are build arguments or VITE variables. The root `.env` is untracked, ignored and excluded from both image build contexts; its existing restricted Windows ACL is preserved. Keep values out of chat, screenshots, command-line arguments, Git and logs. Host administrators/Docker operators can inspect runtime environments; this does not isolate secrets from the host owner.

The dedicated lazy `backend/app/dhan_config.py` loader reads process environment. An explicitly selected dotenv file is optional for the local CLI, with process environment taking precedence and interpolation disabled. General app Settings/app state has no Dhan fields. No frontend or database model receives them.

Application name/key/secret are discarded after offline presence/shape checks; they are not retained in the returned model. Enabled, valid runtime configuration may hold only SecretStr token/optional-client-ID fields, excluded from repr and serialization. Disabled/invalid settings retain no runtime credential object. Reports whitelist booleans, missing-field names and fixed issue codes. No config HTTP endpoint, SDK, transport, authentication callback or SQL write path is added.

## Offline checks

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m backend.app.dhan_config --env-file .env
```

Inside the API container, checking only injected environment:

```powershell
docker compose exec -T api uv run --frozen --no-dev python -m app.dhan_config
```

Reports distinguish:

- developer_credentials_complete: valid API key and secret are present; app name is optional metadata.
- consent_configuration_complete / missing_for_consent: key, secret and client-ID prerequisites for the documented individual flow. This does not perform consent.
- runtime_configuration_complete / missing_for_historical: a valid-shaped supplied access token plus valid configuration; app credentials cannot satisfy it.
- enabled and configuration_valid: local switch/state only. authentication_implemented and network_client_implemented remain false even with every field populated.

Only true/false is accepted for the gate (case insensitive); unset defaults false. The resource URL must be `https://api.dhan.co/v2`, optionally one trailing slash; other hosts/paths, HTTP, credentials, queries and fragments are rejected. Header credentials are bounded printable ASCII without whitespace/controls (client ID <=256 characters, keys/secret/token <=8192). App name permits printable Unicode/spaces, <=256 characters. These are technical shape bounds, not provider validity assertions.

Disabled missing/partial setup returns exit 0 with explicit prerequisite reports. Invalid supplied values, flag or URL return 1; enabled without a runtime token returns 1, even when a developer pair/client ID is complete. Unknown CLI arguments return 2 without echo. File errors return a fixed DHAN_ENV_FILE_UNREADABLE code. No secret value or invalid URL/argument is displayed.

## Manual credential-generation and replacement steps

No token generation is needed merely to save developer credentials while disabled. For a later owner-approved historical-data trial, the simplest manual route is to use Dhan Web's access-token option and enter the resulting token locally. Keep the account's client ID if using consent or renewal. This route does not require the developer pair for each historical request.

If using the existing developer application instead, the owner must follow the official consent sequence above with a matching registered Redirect URL and interactive login/2FA, then store the returned token locally. This application has no callback handler or token-exchange utility; no redirect URL is invented here. Order postbacks are unnecessary for this scope. Do not put PIN/TOTP material into these fields or request trading permissions for historical data.

After replacement, run the offline check and recreate the API container to pick up the changed environment:

```powershell
docker compose up -d --no-deps --force-recreate api
```

A restart alone retains the old container environment. There is no automatic token generation, refresh, expiry validation or credential rotation. Replace expiring app keys through the owner's Dhan console separately from runtime-token replacement. Offline configuration cannot establish identity, token signature/expiry, subscription, permissions or permitted retention.

The enabled flag remains false. Changing it only opens a configuration gate; it does not implement or authorize a connection, authentication exchange, download or order. The [source assessment](../04-planning/VS-01_STEP5_PROVIDER_ASSESSMENT.md) and SQ-01/T-03 remain pending real-data qualification. No changes to ETF mathematics, approved architecture/baseline or final acceptance are implied.


## Step 5A standalone diagnostic - 2026-11-02

The later [read-only diagnostic](DHANHQ_READ_ONLY_DIAGNOSTIC.md) adds a separate, dual-gated backend command for one proposed GET profile preflight. It does not change the seven-variable loader, its offline reports, normal application startup or the disabled `.env` gate. Only mocked requests are authorized and executed at this checkpoint. A true process-local gate and `--live-approved` require prior explicit owner approval; neither app keys nor the flag create that authorization. Historical requests, token exchange, source qualification and trading remain unimplemented/unverified.
