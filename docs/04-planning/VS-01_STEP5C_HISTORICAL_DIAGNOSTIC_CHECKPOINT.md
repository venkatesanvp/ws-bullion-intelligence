# Step 5C - Four-primary-ETF historical diagnostic checkpoint

Recorded **2 November 2026 (Asia/Calcutta)**. Parent `e31f19289937225d6399fe9b91f0f381720854e6`. The owner authorizes implementation and offline verification only; **no live historical request or Git commit** is approved. Trace: D-04/D-14/D-16, REQ-02-007/008/011/012/013/014/015 and REQ-05-003/004 -> ADR-04/05/09, DC-01..04/09, WI-04/05/09/11 and SQ-01. Baseline classifications, requirements tag and approved financial conventions are preserved.

## 1. Primary instruments and four proposed requests

All four verified Step 5B listings are primary. The old two-request/alternative proposal is superseded without recording personal holdings. Each proposed request is **POST https://api.dhan.co/v2/charts/historical**:

| Order | Primary symbol | Dhan securityId | exchangeSegment | instrument | oi | fromDate | toDate (exclusive) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TATAGOLD | 21401 | NSE_EQ | EQUITY | false | 2026-10-26 | 2026-10-31 |
| 2 | TATSILV | 21428 | NSE_EQ | EQUITY | false | 2026-10-26 | 2026-10-31 |
| 3 | GOLDBEES | 14428 | NSE_EQ | EQUITY | false | 2026-10-26 | 2026-10-31 |
| 4 | SILVERBEES | 8080 | NSE_EQ | EQUITY | false | 2026-10-26 | 2026-10-31 |

securityId values are JSON strings; all other body types follow the [daily contract](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data). Use Content-Type application/json and only the configured access-token header. No interval/derivative expiryCode or account/app credentials in body/URL. No requests above were executed. The five expected calendar sessions are 26-30 October, under the [verified NSE capital-market calendar](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf); independent actual coverage remains unknown.

## 2. Data-source permission assessment

**Transient inspection remains permission-blocked.** Public technical documentation describes data retrieval; [general terms](https://dhan.co/terms/) restrict extraction, copying/derived use, publication and commercialization. No reviewed account-applicable API agreement or authorized licence decision settles this platform's full use. Active plan/profile success is not a rights grant.

Obtain specific clarification allowing these four private in-memory requests and retention of non-price diagnostics. Separately establish persistent PostgreSQL/CSV storage, personal derived analytics/private charts, backups, retention/deletion after termination and redistribution restrictions. No permitted duration or personal-use exemption is invented. General recommendations to store intraday data do not answer those contractual questions. The [operations document](../05-operations/DHANHQ_HISTORICAL_DIAGNOSTIC.md#permissions-a-live-test-remains-blocked) contains the five-use assessment and exact clarification to obtain; no message/account operation was sent or performed.

The [official daily adjustment policy](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/) supports declaring PROVIDER_ADJUSTED for splits/bonuses. Exact ETF factors, OHLC/volume treatment, distributions and revision behavior remain unqualified. Adjusted data is neither raw-close nor proof of total return. Timestamp unit/session labeling, real sample consistency and point-in-time availability remain unresolved.

## 3. Implementation summary

`backend/app/dhan_history_diagnostic.py` is a standalone backend command, not an ingestion service or web route. It reuses unchanged credentials/HTTPX transport settings, fixes all four mappings/window and produces only allowlisted status/count/date/validation fields. Prices parse directly as Decimal; no price arithmetic, ranking, database/file output, token exchange/refresh, schedule, holdings/balance/order or broker function. Normal startup does not invoke it.

Approval, source-permission-review acknowledgment and enabled process configuration are separate gates; default invocation returns zero attempts before configuration loading/client construction. Flags acknowledge previous owner/licence decisions, not create permission. Missing token, invalid settings or disabled integration fail closed. TLS verification, no environment proxy/CA overrides, explicit 5-second connect/write/pool and 10-second read-inactivity timeouts, 256 KiB body/64-observation/128-character numeric-token limits and 20-second streamed-body budget apply. The body check is not a hard total wall-clock deadline. No redirects/retries; requests are serial one second apart, at most four and at most one per mapping.

Validation covers HTTP/error classification; JSON keys/schema/aligned arrays; empty/count/independent coverage; finite positive bounded OHLC, integer bounded volume and coherent low/open/close/high; candidate UTC-to-IST dates; timestamp/session duplicates, order, omissions and extras. Nonzero/malformed optional OI is rejected. Unsupported timestamp units/ranges are not auto-rescaled. Raw timestamps, prices, volumes, error texts and credentials never enter output. Detailed unit/session semantics stay false/unverified even when candidate dates match.

Provider/auth/entitlement/rate/network/service/structure errors stop the remaining sequence; empty/data-quality-invalid HTTP-200 arrays may continue to independently assess other ETFs. A reviewed inter-request-control exception also reports stopped rather than completed. Remaining entries are explicitly not attempted or diagnostic-error; no replacement call.

## 4. Executed mocked and regression verification

| Check | Actual final result | Ignored evidence |
| --- | --- | --- |
| New historical unit/mocked integration/exposure tests | **114 passed; zero failed/errors/skipped**, with external socket/DNS guards | new cases in `artifacts/backend-tests.xml`; initial 113-case `step5c-focused-tests.xml` |
| Full backend + actual disposable PostgreSQL | **356 passed; zero failed/errors/skipped** | `artifacts/backend-tests.xml`; `step5c-full-regression.log` |
| Frontend / actual UI-API-PostgreSQL Chromium | **16 / 3 passed**, zero failed/errors/skipped | final regression log; `browser-tests.xml`; `verification.json` |
| Python lint / TypeScript / production build | Passed | final regression log |
| Frozen Compose rebuild/startup | Passed; normal services restored and API healthy | `artifacts/step5c-compose-startup.log`; runtime verification |
| Rebuilt Linux mock probe with networking disabled | Six scenarios plus app construction without provider credentials passed; mandatory marker, synthetic settings and blocked sockets | `artifacts/step5c-linux-offline-probe.log`; probe source |
| Safe default CLI, host + actual API container | LIVE_APPROVAL_REQUIRED, zero attempts, exit 2 | `artifacts/step5c-runtime-verification.json` |
| Python audits, pinned pip-audit 2.9.0 | Windows **40**, actual Linux **31 packages**; zero findings/skips | `step5c-audit-windows-python.json`; `step5c-audit-linux-python.json` |
| Full / production-only npm audits | **Zero findings** | `step5c-audit-frontend-full.json`; `step5c-audit-frontend-production.json` |
| Credentials / runtime boundary | `.env` unchanged/ignored/untracked and false; seven settings only in API, current values match without display; checked assets/logs/local responses contain no actual credentials; running source matches | `artifacts/step5c-runtime-verification.json` |
| Local HTTP behavior | UI/live/auth-ready 200, anonymous-ready 401, no historical diagnostic route 404 | runtime verification |
| Git/baseline | Exact proposed scope below, index empty, parent/tag/baseline unchanged | `artifacts/step5c-review-manifest.json` |

Initial 113 focused tests passed. Lint found compact multiple-statement formatting in the new tests; formatted only the three new Python files, then lint passed. A subsequent review added the inter-request-control stop-status fix/test, followed by the final full suite above (114 new cases). Initial logs/reports are retained; no failure was suppressed. Final warnings are existing Starlette/httpx and Alembic deprecations, runner color warnings and Plotly chunk-size warning. No new dependency/lock/image-reference/Compose or credential-loader/profile-diagnostic change. No unresolved critical finding in the executed application dependency scans; OS-image scanning is not claimed.

No real historical prices/raw response were obtained or persisted. Tests and Linux probe use clearly synthetic OHLCV only; fabricated fixtures are not claimed as real ETF evidence. All integration cleanup targets the disposable local `_test` database; active application/portfolio data was not reset or modified. Normal app services run after verification; only the disposable test DB is stopped. No new profile/master/account call or provider token exchange during Step 5C.

## 5. Comparison readiness and acceptance blockers

The intended pairs are TATAGOLD/GOLDBEES and TATSILV/SILVERBEES. Known listing currency is INR and the requested dates/general adjusted policy match; actual returned dates and exact adjustment compatibility remain unknown. A pure summary-only readiness check tests approved distinct same-metal identities, currency, policy reference, expected candidate dates and passing individual validation. Compatible mock inputs return **BLOCKED_SOURCE_QUALIFICATION**, not qualified_for_comparison. Invalid/missing/incompatible inputs return BLOCKED_INPUTS. No performance return, indicator or investment conclusion is calculated.

Live permission, actual endpoint/coverage/schema, timestamp contract, detailed adjustment method, independently reconciled permitted samples and broader history remain outstanding. Five bars do not validate longer-lookback indicators, revisions/replay or full T-03. SQ-01/T-03 source qualification, owner recovery/retention/cutover and final human acceptance remain open. No full VS-01/R1 acceptance or later implementation increment.

## 6. Exact proposed Git changes

**10 files: four modified and six new. Nothing staged or committed.** The uncommitted Step 5B report is carried forward, with a scope-supersession note; it does not record personal holdings.

| State | Repository-relative file |
| --- | --- |
| Modified | `README.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` |
| Modified | `docs/04-planning/VS-01_SECURITY_REVIEW.md` |
| Modified | `docs/05-operations/DHANHQ_LOCAL_CONFIGURATION.md` |
| New | `backend/app/dhan_history_diagnostic.py` |
| New | `backend/tests/test_dhan_history_diagnostic.py` |
| New | `backend/tests/test_dhan_history_diagnostic_integration.py` |
| New, carried forward | `docs/04-planning/VS-01_STEP5B_INSTRUMENT_QUALIFICATION.md` |
| New | `docs/04-planning/VS-01_STEP5C_HISTORICAL_DIAGNOSTIC_CHECKPOINT.md` |
| New | `docs/05-operations/DHANHQ_HISTORICAL_DIAGNOSTIC.md` |

Actual `.env`, tokens/keys/client IDs, personal portfolio information, raw provider data, backups, builds, caches and verification artifacts are excluded. Exact reviewed file hashes are saved only in an ignored manifest. Git commit requires separate approval; no release tag.

## 7. Exact authorization required before first live test

First record adequate applicable permission for the proposed transient use. Then obtain **separate explicit owner approval for the four POST bodies in section 1**, in the exact Tata-first order, with no automatic retries/redirects/follow-up, process-only enablement and sanitized output only. The total is at most four; a stopping error leaves remaining requests unattempted. Neither active credentials nor the implementation grant authorizes live acquisition.

Proposed command, **NOT EXECUTED**:

```powershell
docker compose exec -T -e DHAN_DATA_API_ENABLED=true api uv run --frozen --no-dev python -m app.dhan_history_diagnostic --live-approved --permissions-reviewed
```

The gate override affects only that process; `.env` and ordinary service stay false. No automatic token exchange or expiry recovery. No raw response/price storage, PostgreSQL write, ingestion, account operation or scheduled acquisition is included. Those capabilities, and a checkpoint commit, need their own approval. Do not execute this command while permission remains unclear or live authority is absent.
