# Step 5 - DhanHQ developer-credential configuration checkpoint

Revised **2 November 2026 (Asia/Calcutta)**. Parent: `a244cfed5c4a30af5076f73a8bb2ce19d340ae0b`. The owner's latest scope is environment configuration and non-network validation only, extending the earlier credential proposal. REQ-05-003/004 -> ADR-09/DC-09; no changes to approved architecture/requirements or research mathematics. No authentication, token exchange, provider historical API, SDK, callback, scheduler, order/execution capability or schema is implemented.

## Environment variables and preservation

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

Only missing developer keys were appended to the actual `.env`; the existing four Dhan keys and all preceding bytes were preserved at the time of that edit. There was no replacement, regeneration, duplicate key or actual credential written by the assistant. The grouped blank template is in `.env.example`; the existing actual file was not reordered to match it.

Provider values were populated locally after the append. This legitimately changed the old append-prefix hash; it was observed without displaying values and **not reverted**. The original non-provider application-variable prefix still matches its earlier hash, and actual API runtime values match all seven current local settings. `artifacts/dhan-developer-env-update.json` and the environment-preservation details in `dhan-developer-runtime-verification.json` distinguish these facts. No credential is included in this document or Git set.

`.env` remains ignored/untracked and excluded from image contexts, with restricted owner/SYSTEM ACL preserved. The enabled gate remains false. Missing provider credentials do not prevent existing workbench startup; developer-only setup is allowed while disabled.

## Authentication model and configuration behavior

The six requested questions and owner generation/replacement instructions are covered in the [official-documentation review](../05-operations/DHANHQ_LOCAL_CONFIGURATION.md#authentication-model-verified-from-official-documentation). That record separates the app label/key pair, individual consent prerequisites, resource-token authentication and token-specific renewal/expiry behavior. No assumption that an API key/secret can be sent directly to historical resources is implemented.

- Compose injects all seven optional values only into API, never UI, migration, DB/test DB, build args or VITE variables.
- A lazy backend-only module loads environment or an explicitly requested local dotenv file. Environment wins; interpolation is disabled. General app Settings/app state and database models contain no Dhan values.
- App-name/key/secret values are discarded after shape/presence checks. Reports whitelist booleans, fixed issue codes and prerequisite names. The developer pair's completeness and consent completeness are separate from runtime-token completeness.
- A supplied runtime token can be checked without app credentials/client ID. A complete developer pair and client ID without a token is not historical-ready and returns checker exit 1 if enabled. While disabled, missing prerequisites return exit 0 with explicit missing lists. Invalid supplied values fail closed; invalid CLI arguments never echo input.
- Optional enabled runtime credentials use SecretStr, omitted from model dumps/reprs. Disabled/invalid configuration retains no usable runtime credential object. No token validation, renewal, client construction or provider request occurs, even if the configuration gate is true.
- The requested resource base is restricted to its exact HTTPS host/path; no arbitrary URL or auth-server setting is introduced. App-label Unicode/spaces are allowed; controls and bounded invalid header values are rejected without displaying them.

All checker completeness fields mean offline prerequisites/shape only. They are not proof of identity, token validity/expiry, Data API entitlement, source permissions or accepted market data. No trading permission is requested. Future authentication/acquisition still needs a separately authorized design and action.

## Final executed verification

| Check | Actual outcome | Ignored evidence |
| --- | --- | --- |
| Full backend / disposable PostgreSQL | **161 passed; 0 failed/errors/skipped**, including 47 configuration cases | `artifacts/backend-tests.xml`; `dhan-developer-full-regression.log` |
| Frontend components | **16 passed; 0 failed/skipped** | full-regression log; `artifacts/verification.json` |
| Real UI/API/PostgreSQL Chromium | **3 passed; 0 failed/errors/skipped** | `artifacts/browser-tests.xml`; verification report |
| Lint / TypeScript / production build | Passed | full-regression evidence |
| Optional/partial configurations | Blank, developer-only, missing client-ID/token, consent-only, token-only, malformed URL/flags/header values and metadata labels covered; app startup remains independent | configuration tests and full backend XML |
| Docker build/startup | Passed; UI/live/auth-ready 200, anonymous-ready 401, no provider config HTTP route (404) | `artifacts/dhan-developer-runtime-verification.json` |
| Actual container boundary | Seven keys only in API; values match local configuration without display; absent from other containers and build args | runtime report |
| Network-disabled Linux probes | Six scenarios actually executed with `docker run -i --network none`, socket/DNS guards and mandatory marker; includes developer-only, consent-without-token, token-only, complete and invalid flags | `artifacts/dhan-developer-linux-offline-probe.log` |
| Frontend canary isolation | Five synthetic app/runtime values absent from assets/build logs; all five generated production files identical with canary environment | `artifacts/dhan-developer-frontend-isolation.json` |
| Logs / API / model safety | New fields excluded from diagnostics and captured responses/logs; actual private local values absent from checked runtime logs/responses; secret fields excluded from repr/model JSON | unit/runtime evidence |
| Environment | Append preserved existing bytes at edit time; later local provider entry preserved; original non-provider prefix unchanged; gate false | environment update/runtime reports |
| Git / baseline | Scope unchanged outside the nine files below; original requirements/D-01..16/tag and calculation/schema/dependency/image files unchanged; no stage/commit/tag | final review manifest |

The raw post-append prefix check initially reported a mismatch because local runtime credentials had subsequently been entered. The append-time assertion had passed. Verification was reconciled using the unchanged original non-provider prefix and the current API/environment equality check; no credentials or file contents were restored or overwritten. Original observation evidence remains ignored.

An initial focused run used an instance-level Pydantic model_fields test access and emitted deprecations; changed the test to class-level access before the final full run. Final backend warnings are the two pre-existing Starlette/httpx and Alembic deprecations. Runner color and Plotly bundle-size warnings remain. No new dependency, image update or scan result is asserted. Earlier configuration-iteration harness evidence remains local historical evidence, not the current result.

Normal application services are running after verification; the disposable test DB alone was stopped. Active application data was never reset, seeded or restored. All development/regression market fixtures remain labeled synthetic. No token exchange, provider API request, market-data download or T-03 execution.

## Remaining acceptance gates

DhanHQ is selected as the primary candidate; local values are configured but not provider-validated, and the integration gate is disabled. Data entitlement, applicable usage/retention rights, independently qualified actual Gold/Silver samples and SQ-01/T-03 remain open. WI-11/12 owner-data recovery/cutover/retention and final handover/human acceptance remain partial. No full VS-01/R1 acceptance or later financial increment.

## Exact proposed Git checkpoint
**Nine files: four modified, five new**, revising the same uncommitted configuration proposal. The provider-assessment file predates the initial configuration task and now records the later scoped dispositions. Nothing is staged or committed.

| State | Repository-relative file |
| --- | --- |
| Modified | `.env.example` |
| Modified | `README.md` |
| New | `backend/app/dhan_config.py` |
| New | `backend/tests/test_dhan_config.py` |
| Modified | `compose.yaml` |
| New | `docs/04-planning/VS-01_DHAN_CONFIGURATION_CHECKPOINT.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` |
| New | `docs/04-planning/VS-01_STEP5_PROVIDER_ASSESSMENT.md` |
| New | `docs/05-operations/DHANHQ_LOCAL_CONFIGURATION.md` |

Actual `.env`/credentials, account identifiers, raw data, backups, generated builds, caches and test/verification artifacts are excluded. `.env.example` contains blanks only; explicit synthetic test values are not usable credentials. A commit still requires separate owner approval. Requirements baseline/tag unchanged; no release tag.
