# Step 5A - DhanHQ read-only diagnostic checkpoint

Recorded **2 November 2026 (Asia/Calcutta)**. Parent `2e598c6fc4268f600698d3a46835ecb537232528`. Owner authorizes implementation and mocked tests, with separate explicit approval required before any live authenticated provider request or commit. Trace: REQ-05-003/004 -> D-14 / ADR-09 / DC-09; baseline classifications are preserved.

## Implementation and readiness

A standalone backend command, `backend/app/dhan_diagnostic.py`, reuses the seven-variable credential loader. It performs no work at normal app startup, provides no frontend/API route, and requires both a true process gate and the separately approved `--live-approved` acknowledgment before constructing a real transport. Default invocation returns LIVE_APPROVAL_REQUIRED/zero attempts before loading credentials. The existing offline checker remains offline.

The only proposed live operation is **GET https://api.dhan.co/v2/profile**, with the supplied access-token in a header, no body/query, no retries or redirects. Dhan's [official profile contract](https://dhanhq.co/docs/v2/authentication/#user-profile) recommends this initial integration test. TLS verification is enabled; proxy/certificate environment overrides are ignored. Explicit phase timeouts, 64 KiB response cap and a streamed-body budget constrain the request. The latter is not a hard wall-clock deadline across all phases. No secrets or provider messages are echoed; raw profile/account fields stay in transient backend memory and are discarded. No SQL/file output or portfolio/order mutation exists. [Operating instructions and error dispositions](../05-operations/DHANHQ_READ_ONLY_DIAGNOSTIC.md) document the controls and limitations.

**Implemented and verified offline:** configuration/approval gates, one-request contract, mock authentication/expiry/entitlement/rate-limit/timeouts/network/provider/error-format cases, safe reports/logging and response closure. **Implemented but not live verified:** real HTTPS transport and actual provider response/credentials. **Not implemented:** historical-data retrieval/adapter/ingestion, token generation/refresh, brokerage execution or trading. **Blocked:** live authentication/entitlement evidence awaits owner approval; SQ-01/T-03 require actual source rights, verified identities, representative Gold/Silver samples and acceptance evidence.

An authenticated profile reporting Active is only a preflight result. The historical endpoint is a separate [documented read-only POST `/v2/charts/historical`](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data), requiring a security ID, exchange segment, instrument and explicit date range. It is not called or implemented here. No ETF prices are downloaded, stored or inferred. Existing labeled synthetic fixtures remain the development evidence. ETF formulas, requirements, approved architecture and schema are unchanged.

## Required configuration

- Supplied valid-shaped DHAN_ACCESS_TOKEN; the owner manually generates/replaces it. No API-key/secret exchange is implemented.
- Exact HTTPS resource base, default https://api.dhan.co/v2; optional DHAN_CLIENT_ID enables private account matching. Application name/key/secret are unnecessary for this resource request; supplied invalid settings still fail validation.
- `.env`/ordinary service gate remains false. Only a separately approved one-off process may use `DHAN_DATA_API_ENABLED=true` and `--live-approved`. Direct HTTPS connectivity and trusted CA certificates are required.
- Data API subscription and applicable usage/retention rights are separate historical-access prerequisites; possession of a token or an Active profile flag does not establish all of them.

## Executed verification

| Check | Actual outcome | Ignored evidence |
| --- | --- | --- |
| New unit + mocked integration/security tests | **81 passed; zero failed/errors/skipped**; socket/DNS connections blocked | `artifacts/step5a-diagnostic-tests.xml` |
| Full backend and disposable PostgreSQL | **242 passed; zero failed/errors/skipped**, includes 81 new and 47 existing configuration tests | `artifacts/backend-tests.xml`; `step5a-full-regression.log` |
| Frontend components / real UI-API-PostgreSQL Chromium | **16 / 3 passed**, zero failed/skipped | full regression log; `browser-tests.xml`; `verification.json` |
| Python lint / TypeScript / production build | Passed; existing warnings retained | full regression log |
| Frozen Linux runtime rebuild / Compose startup | Passed; existing services restored, ordinary application remains functional | `artifacts/step5a-compose-startup.log`; runtime report |
| Network-disabled Linux probes | Six scenarios passed plus app construction without provider credentials, with synthetic ordinary settings and mandatory completion marker | `artifacts/step5a-linux-offline-probe.log`; probe source |
| Windows / actual Linux pip-audit 2.9.0 | **40 / 31 packages; zero findings or skips** | `artifacts/step5a-audit-windows-python.json`; `step5a-audit-linux-python.json` |
| Full / production-only npm audit | **Zero findings** | `artifacts/step5a-audit-frontend-full.json`; `step5a-audit-frontend-production.json` |
| Credential/default/runtime boundaries | `.env` unchanged, ignored/untracked and false; provider keys scoped to API; checked assets/logs/local responses contain no actual private values; default actual-environment diagnostic makes zero attempts | `artifacts/step5a-runtime-verification.json` |
| Git/governance | Index empty, HEAD/tags/baseline unchanged; only the 11 files below proposed | `artifacts/step5a-review-manifest.json` |

An initial lint check found one unused test import; removed before the final passing suite. The first Linux probe completed diagnostic cases but failed the added app-construction check because the harness omitted ordinary required DATABASE_URL/LOCAL_APP_TOKEN. Added synthetic local settings and repeated successfully, preserving initial evidence. Neither failure involved provider access. Two pre-existing backend deprecations, runner color warnings and the Plotly bundle-size warning remain. No failing or skipped tests in the final run. No new advisory suppression or forced upgrade. Application dependency scans do not assess OS-image vulnerabilities.

Actual application data was never reset/restored or used for cleanup; database tests remain restricted to the disposable local `_test` database. Normal application services remain running; only the disposable test DB is stopped afterward. No live authenticated DhanHQ request or token exchange was executed. `.env` and credentials were not modified, staged or included in proposed files.

## Exact proposed Git changes

**11 files: six modified, five new. Nothing staged or committed.**

| State | Repository-relative file |
| --- | --- |
| Modified | `README.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` |
| Modified | `docs/04-planning/VS-01_SECURITY_REVIEW.md` |
| Modified | `docs/05-operations/DHANHQ_LOCAL_CONFIGURATION.md` |
| Modified | `pyproject.toml` |
| Modified | `uv.lock` |
| New | `backend/app/dhan_diagnostic.py` |
| New | `backend/tests/test_dhan_diagnostic.py` |
| New | `backend/tests/test_dhan_diagnostic_integration.py` |
| New | `docs/04-planning/VS-01_STEP5A_DIAGNOSTIC_CHECKPOINT.md` |
| New | `docs/05-operations/DHANHQ_READ_ONLY_DIAGNOSTIC.md` |

HTTPX 0.28.1 is promoted from dev to exact runtime dependency. Resolved package versions and artifact hashes are unchanged; Linux now installs its HTTPX/httpcore/h11 runtime chain. No other dependency change. Actual credentials/account IDs, `.env`, backups, raw provider data, builds, caches and test artifacts are excluded. No commit or release tag is created.

## Exact next action requiring approval

Owner approval under Step 5A section 3 is required for **one authenticated GET https://api.dhan.co/v2/profile**, using the existing API-container token, no query/body, redirects or retries, discarding the raw profile and retaining only the sanitized result. Proposed command, **not executed**:

```powershell
docker compose exec -T -e DHAN_DATA_API_ENABLED=true api uv run --frozen --no-dev python -m app.dhan_diagnostic --live-approved
```

The gate override applies to that process only; `.env` and normal service stay false. This approval would cover profile preflight only, without historical market-data download, ingestion, token exchange or trading. A separate approval is required for any Git checkpoint commit and any later historical-data trial with reviewed instrument/date/usage boundaries. Do not infer approval from a configured token or a CLI flag.

SQ-01/T-03, actual historical access, source licensing/retention/identity/sample quality, owner recovery/cutover/retention and final human acceptance remain unresolved. No full VS-01/R1 acceptance and no later implementation increment is declared or started.
