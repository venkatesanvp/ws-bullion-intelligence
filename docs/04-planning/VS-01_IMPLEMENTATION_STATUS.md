# VS-01 implementation status - Step 4

Recorded: 2 November 2026 (Asia/Calcutta). Parent checkpoint: `5f0399b40eaa790117c5ab0e4c9ececf08ed251a`. This is a scoped implementation and verification record; **full VS-01 and R1 are not accepted**.

## Scoped authority

Step 3 authorized WI-01..06 and WI-09: ADR-01/02/03/04/05/08, conditional ADR-09 and quality ADR-10; DC-01/02/03, conditional DC-04/09 and applicable DC-07/08. SQ-02/03 were adopted, SQ-06 remains conditional on documented local controls. ADR-04 real-data acceptance remains conditional on permissions/samples.

Step 4 approves ADR-06/07, remaining research ADR-10, DC-05/06 and applicable research DC-07/08. SQ-04/05 are resolved by explicit formula/precision/common-date conventions. SMA/EMA n>=1; RSI n>=2 refines the former shared lower bound. The grant covers WI-07, WI-08, WI-10 and applicable research WI-11/12 work; WI-07 and WI-08 each depend on WI-06, then WI-10 follows WI-07/08/09. Routine scoped coding/testing is authorized. Commit creation requires review and explicit approval of this new checkpoint; no release tag.

D-01..16, REQ-BL-1.0 and tag `requirements-v1.0` are unchanged. Scoped approvals do not promote frozen parent requirement classifications. SQ-01 remains Open. No strategy, trading recommendation, GTT, sizing, portfolio accounting, paper/manual transaction, AI or broker implementation.

## Current work-item assessment

| Work items / capability | Status | Evidence / limitation |
| --- | --- | --- |
| WI-01..04 | Implemented and regression verified in existing scope | Locked runtime, initial schema, access/error boundary, listing/watchlist/source forms; cumulative tests and original browser workflow pass. |
| WI-05 | Implemented; real-source acceptance blocked | Canonical qualified-source CSV ingestion passes synthetic/API/DB cases. No qualified real ETF sample inspected. |
| WI-06, WI-09 | Implemented and regression verified | Exact history, provenance, quality, import UI/idempotent outcomes; existing tests pass. Calendar/publication/quality unknowns remain explicit. |
| WI-07 | Implemented and verified against synthetic references | Pure Decimal SMA, SMA-seeded EMA, Wilder RSI; 26 pure tests, 15 research PostgreSQL API cases shared with WI-08/10, Linux reference check. |
| WI-08 | Implemented and verified against synthetic references | Same-currency compatible-basis common-date price-only change/rebasing, 11 pure comparison cases and API/browser tests. |
| WI-10 | Implemented and verified within approved research scope | Local lazy Plotly charts, explicit lookbacks/ranges, RSI panel, comparison workbench, exact table alternative, quality/synthetic/limitations. Component and Chromium workflows pass; desktop/mobile inspected. |
| WI-11 | Partially implemented/verified | Cumulative automated/security evidence complete for implemented synthetic scope; real-source T-03 and cumulative human acceptance blocked/pending. |
| WI-12 | Partially implemented/verified | Pinned/repeated startup and isolated synthetic recovery including derived research outputs pass. Actual owner-data restore/cutover, retention decision and final handover remain pending. |
| Broader R1 capabilities | Not implemented; outside this grant | Later strategy/risk/portfolio/execution/AI increments require separate authorization. |

## Final executed verification

| Check | Actual result | Ignored local evidence |
| --- | --- | --- |
| Python lint | Passed | `artifacts/verification.json` |
| Backend with actual disposable PostgreSQL | **114 passed, 0 failed, 0 skipped** | `artifacts/backend-tests.xml` |
| Frontend components | **16 passed, 0 failed, 0 skipped** | verification command; `artifacts/verification.json` |
| Real UI/API/PostgreSQL Chromium | **3 passed, 0 failed, 0 skipped** | `artifacts/browser-tests.xml`; `frontend/playwright-report/` |
| TypeScript/production build | Passed; lazy chart bundle-size warning retained | `artifacts/verification.json` |
| Full and production-only npm audits | **0 findings** | `artifacts/step4-frontend-audit-full.json`; `step4-frontend-audit-production.json` |
| Windows Python audit | **40 packages, 0 findings, 0 skipped** | `artifacts/step4-backend-audit.json` |
| Actual Linux API audit | **28 packages, 0 findings, 0 skipped** | `artifacts/step4-backend-linux-audit.json` |
| Compose build and repeated startup | Passed; auth/readiness and loopback checks passed | `artifacts/step4-runtime-verification.json`; startup logs |
| Linux arithmetic references | SMA/EMA/Wilder RSI passed | `artifacts/step4-linux-arithmetic.log` |
| Backup/new isolated restore | Passed; table/schema/provenance/research-query hashes equal | `artifacts/recovery-verification.json` |

Two backend dependency deprecation warnings, runner color warnings and the chart bundle warning remain. Initial blank-chart browser failure was diagnosed as an obsolete StrictMode render purging the current plot; fixed with serialized lifecycle handling, regression tested and full suite rerun. The original trace is retained. A reporting probe initially assumed UI had a Docker HEALTHCHECK; corrected to actual running/HTTP checks and repeated startup. These failures are not hidden by the final passing run.

## Remaining gaps and next work

- **Blocked:** SQ-01/T-03 real ETF permissions, representative samples and source/identity/coverage/basis/time qualification; no external market data was downloaded or ingested.
- **Partially verified:** owner-data recovery/cutover, retention decision and final operational/human acceptance. Synthetic recovery does not establish those gates.
- **Known limitation:** Plotly basic chart chunk about 1.22 MB (407 kB gzip), lazy loaded; numeric coordinates are approximate display values, while authoritative values remain Decimal strings in server results and tables.
- **Security coverage:** no unresolved critical finding in executed application dependency scans. OS-image vulnerability scanning and other platforms were not assessed.

See [Step 4 completion and exact proposed checkpoint](VS-01_STEP4_COMPLETION.md), [executed case dispositions](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#7-step-4-execution-disposition---2026-11-02), [source qualification](VS-01_DATA_QUALIFICATION.md), [security review](VS-01_SECURITY_REVIEW.md), [container review](VS-01_CONTAINER_REPRODUCIBILITY.md) and [recovery instructions](../05-operations/LOCAL_RECOVERY.md). The prior [Step 3 verification checkpoint](VS-01_VERIFICATION_CHECKPOINT.md) and [adopted next-package proposal](VS-01_NEXT_PACKAGE_PROPOSAL.md) are historical records.


## Later Step 5 developer-credential configuration - 2026-11-02

The owner selects DhanHQ as the primary candidate and authorizes environment preparation/offline validation only, now including application name, API key and API secret. There is no authorization for authentication/token exchange, provider data calls, network adapters, broker execution, trading, formula changes or baseline edits.

Seven optional startup settings are scoped only to the API container. The three developer placeholders were appended without changing the existing file prefix at edit time. Subsequent local entry populated provider fields; those entries were preserved. The original non-provider application-variable prefix still matches its earlier checkpoint, and all seven API runtime values match current local configuration without being displayed. Gate remains false.

The dedicated loader reports developer key-pair completeness, separate client-ID/consent prerequisites and historical access-token prerequisites. App name is label metadata; the key pair cannot satisfy the historical token requirement. Client ID is needed for the documented consent/web-renewal flows, while the historical resource endpoint documents access-token rather than a separate client-ID header. No app keys/name are retained in returned models; optional runtime secret fields are excluded from repr/serialization. General Settings/frontend/database models are unchanged. See [verified authentication distinctions and local instructions](../05-operations/DHANHQ_LOCAL_CONFIGURATION.md) and [current configuration checkpoint](VS-01_DHAN_CONFIGURATION_CHECKPOINT.md).

Executed final regression: **161 backend/PostgreSQL tests passed**, including 47 offline configuration cases; **16 frontend and three Chromium workflows passed**; zero failed/errors/skipped. Lint/build and rebuilt Compose startup passed. Five synthetic credential/label values are absent from production assets/logs and assets remain identical. Actual container inspection confirms seven-field API-only isolation. Six Linux scenario probes executed with networking disabled, including app-only, consent-without-token and token-only configurations. Missing provider credentials do not block normal startup. Existing dependency deprecations and Plotly chunk warning remain; no dependency changes/new audit claimed.

SQ-01/T-03, provider validation/entitlement/rights, real samples, owner recovery/retention/cutover and final human acceptance remain pending. No authentication implemented, credentials exchanged, historical data downloaded, commit, tag or full VS-01/R1 acceptance.


## Step 5A read-only diagnostic - 2026-11-02

Owner authority now covers a standalone backend diagnostic and mocked verification. Live authenticated requests and commit creation remain explicitly withheld. The separate profile command is implemented and verified offline; it proposes one GET `/v2/profile` with a supplied access token, explicit timeouts, bounded body, no retries/redirects and an allowlisted result. It requires both an enabled process gate and explicit prior approval acknowledged by a CLI flag. Normal startup has no diagnostic hook. The existing offline configuration checker and seven settings are unchanged; `.env` stays disabled.

**Implemented and verified:** error/credential/expiry/entitlement/rate/timeout/service/schema handling, no-secret response/log/exception behavior, single-request shape and gating under injected mocked HTTP. **Implemented but not live verified:** the real HTTPS transport and provider profile contract. **Not implemented:** historical acquisition/ingestion adapter, token exchange/refresh, trading/order functions and automated retrieval. **Blocked:** live authentication/plan evidence awaits owner approval; SQ-01/T-03 still require rights, listing identity and permitted real Gold/Silver samples. A reported active profile plan will not prove historical endpoint access.

Final regression: **242 backend/PostgreSQL tests passed**, including **81 new diagnostic unit/mocked integration cases** and the existing 47 configuration cases; **16 frontend and three Chromium workflows passed**, zero failures/errors/skips. Lint, production build, rebuilt Compose startup and six Linux scenarios with networking disabled passed. The Linux no-Dhan configuration app-construction check passed with ordinary synthetic local app settings. The initial Linux harness omitted those ordinary required settings; corrected and rerun, with failure evidence retained. One unused test import was removed after initial lint failure. Pre-existing deprecation/runner/chart warnings remain.

Dependency change: existing HTTPX 0.28.1 promoted to exact runtime dependency; lock package versions/hashes unchanged. Full/production npm and Windows Python (40 packages)/actual Linux Python (31 packages) audits found zero known vulnerabilities/skips. No suppressed advisory or forced upgrade. See [Step 5A checkpoint](VS-01_STEP5A_DIAGNOSTIC_CHECKPOINT.md), [operating boundary](../05-operations/DHANHQ_READ_ONLY_DIAGNOSTIC.md) and updated security review. No live provider request, market download, raw profile retention, token exchange, commit/tag, baseline/formula/schema change or full VS-01 acceptance. Owner recovery/retention/cutover and final human acceptance remain partial.
