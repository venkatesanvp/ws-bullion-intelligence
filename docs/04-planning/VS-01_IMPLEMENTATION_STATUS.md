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


## Step 5C four-primary-ETF offline historical diagnostic - 2026-11-02

All four Step 5B-verified NSE listings are primary research instruments: TATAGOLD, TATSILV, GOLDBEES and SILVERBEES. The fixed order starts with Tata; earlier two-request/alternative wording is superseded. No personal holdings or account data is recorded. The owner's current grant permits backend implementation and mocked verification only, explicitly withholding live historical retrieval and commits.

**Implemented and verified offline:** fixed four POST request contracts for 26-30 October (exclusive end 31 October), unchanged credential loader, permission/approval/enablement gates, explicit time/size/count bounds, no retries/redirects, safe provider/network errors and fail-stop sequencing. JSON/Decimal OHLCV checks cover schema/lengths/numbers/coherence, candidate dates, duplicates/missing/extra observations, empty results and independent per-ETF coverage. Output contains no prices, volumes, raw timestamps, provider messages, account IDs or credentials. No SQL, raw-response persistence, startup hook, new route, scheduler, token exchange or trading function.

**Implemented but not live verified:** actual historical transport, each ETF's availability/coverage and response contract. **Blocked:** source-use/retention permission, timestamp semantics, precise ETF adjustment method and independent reconciliation. Compatible mocked summary inputs still return BLOCKED_SOURCE_QUALIFICATION for Tata Gold/Gold BeES and Tata Silver/Silver BeES. No investment-performance conclusion or source acceptance. The approval/rights flags acknowledge prior decisions; they do not supply a licence. **Not implemented:** canonical real-data ingestion adapter, persistent/scheduled collection or any later portfolio/execution capability.

Final cumulative regression: **356 backend/PostgreSQL tests passed**, including **114 new historical diagnostic cases**; **16 frontend tests and three Chromium workflows passed**; zero failed/errors/skipped. Lint/build, rebuilt Compose startup, six network-disabled Linux scenarios and missing-provider app construction passed. Host/container default diagnostic commands returned LIVE_APPROVAL_REQUIRED with zero attempts. Initial 113 focused cases passed; formatting lint issues were corrected and a reviewed inter-request-control failure case added before the final complete rerun. Existing backend deprecations, runner color and Plotly chunk warnings remain.

Security scans: Windows Python **40 packages**, rebuilt Linux Python **31 packages**, full/production npm: **zero known findings**, zero Python skips; no dependency/image/Compose update or advisory suppression. `.env` unchanged/ignored/untracked and false; provider fields remain API-only, checked assets/logs/local responses contain no actual credentials, and running diagnostic source matches review. Normal services are running; only disposable test DB stopped. No live historical/master/profile/account request during Step 5C. Requirements/tag, credential configuration, profile diagnostic, approved financial mathematics and schema are unchanged.

See [Step 5C checkpoint and exact proposed scope](VS-01_STEP5C_HISTORICAL_DIAGNOSTIC_CHECKPOINT.md) and [permission/validation/operating contract](../05-operations/DHANHQ_HISTORICAL_DIAGNOSTIC.md). SQ-01/T-03, actual source qualification, owner recovery/retention/cutover and final human acceptance remain open. No commit/tag or full VS-01/R1 acceptance.

## Step 5D.1 provider adapter — 2026-11-02

The owner now authorizes a backend-only DhanHQ daily provider adapter and offline verification, supplementing the earlier CSV-first exclusions. All four Step 5B primary listings are supported through a provider-neutral in-memory acquisition interface. Existing canonical price validation, strict exact JSON/integral numeric handling, verified identities and HTTP/security policy are extracted and reused. CSV persistence, schema, financial calculations, dashboard and requirements baseline remain unchanged.

The adapter is implemented and offline verified: final 506 backend/PostgreSQL, 16 frontend and three Chromium tests pass without failures/errors/skips; lint, production build, Compose startup and Linux network-none four-mapping probe pass. Windows 40-package/Linux 31-package Python and full/production npm scans report zero known findings; no Python skips. Offline credential-pattern and private exposure checks pass. Real adapter connectivity and persistent ingestion are not accepted. Normal integration stays disabled. No live request, price persistence, trading/account operation or automated collection is authorized or performed in this increment. Prior Step 5C.1 transient diagnostics established only five-day numerical/date compatibility, not full timestamp, adjustment, historical coverage or data-use qualification. Every adapter result retains source UNVERIFIED, provisional candidate session mapping and UNVERIFIED_FOR_REPLAY. A missing calendar means completeness UNASSESSED, not no gaps.

See the [Step 5D.1 design, exact proposed changes, executed verification and remaining acceptance limitations](VS-01_STEP5D1_PROVIDER_ADAPTER_CHECKPOINT.md). This is an uncommitted implementation checkpoint, not full VS-01/R1 acceptance. SQ-01/T-03, persistent-use/retention rights, independent reconciliation, timestamp/adjustment/history qualification, owner recovery/cutover and final human acceptance remain open. Step 5D.2 requires separate approval; no release tag.

## Step 5D.2 — one-year acquisition and canonical persistence (offline checkpoint)

The owner now authorizes bounded one-year acquisition/persistence implementation and offline verification, with explicit preflight review before live requests and established applicable rights before live storage. The provider collector and canonical bridge reuse the existing atomic import repository. Source contracts gain a minimal migration; the schema/CSV behavior, duplicate/recovery rules and financial mathematics are preserved. The migration was applied only to disposable test databases, not the active application database. Existing normal services retain their prior deployed source/schema pending review.

The [Step 5D.2 implementation and exact live preflight](VS-01_STEP5D2_HISTORY_INGESTION_CHECKPOINT.md) describes four primary mappings, inclusive 2025-11-02 through 2026-11-02 (provider-exclusive 2026-11-03), 247 explicit scheduled sessions including the Sunday Budget session, and four bounded sequential requests. Normal integration remains false. No live request or live data persistence occurred. Public terms have not established persistent local storage/derived-use/backups/retention rights; source-use and provisional-date review remain required gates. T−1 provider availability may omit the most recently completed requested session.

Checkpoint A is implemented and tested offline; Checkpoint B is ready for human review. C/D (authorized live execution and real-data application acceptance) remain pending. The source remains unqualified for full acceptance; timestamp/adjustment/history/reconciliation gaps and SQ-01/T-03 remain open. The working tree includes the prior uncommitted Step 5D.1 scope; no commit or tag was created, and the requirements baseline is unchanged.

Final Step 5D.2 offline evidence: **547 backend/PostgreSQL, 17 frontend and four Chromium tests passed**, no final failures/errors/skips; lint/production build and Linux network-none four-ETF/247-date synthetic probe passed. Windows 40-package/Linux 31-package Python audits and full/production npm audits report zero known vulnerabilities, no Python skips. One credential-pattern candidate was a reviewed, explicitly synthetic test token; actual local credential exposure checks passed. A provider explicit-end trailing-session quality defect was corrected and regression tested. Cumulative review scope is **33 files (14 modified, 19 new)**, including carried-forward Step 5D.1 work; nothing staged/committed. See the checkpoint for intermediate failures, remaining warnings, source limitations and exact preflight/contents.

## Step 5D.3 — real data deployed for owner UAT

The owner explicitly authorized the bounded live acquisition and local application deployment. Exactly four historical requests succeeded (HTTP 200), returning **246 real observations per primary ETF**, from 2025-11-03 through 2026-10-30. Requested dates remain 2025-11-02 through 2026-11-02 inclusive; only the scheduled 2026-11-02 session is missing, consistent with provider T−1 availability. No duplicate or invalid canonical observation was found.

Applicable persistent-storage/retention permission remains inconclusive, so live observations are retained only in backend process memory. A transient read capability uses the existing canonical validator, research routes and Decimal engines without granting storage qualification or creating a parallel ingestion database. Schema 0002_provider_ingestion is now deployed locally; SQL live-price row counts remain unchanged. Normal provider enablement remains false and no scheduler/trading/account-data operation exists.

Engineer-operated API/browser checks verified all four real charts, SMA 20/50/200, EMA 37, Wilder RSI 14 and both metal comparisons on 246 common dates. Final synthetic regression is **551 backend/PostgreSQL, 18 frontend and four browser workflows passed**, plus lint/production build. See the [real-data/deployment checkpoint](VS-01_STEP5D3_REAL_DATA_UAT_CHECKPOINT.md) for actual results, security evidence and remaining source limitations.

The application is available at http://127.0.0.1:5173 for hands-on UAT. [User guide](../05-operations/REAL_DATA_UAT_USER_GUIDE.md); [owner checklist](../05-operations/VS-01_STEP5D3_UAT_CHECKLIST.md). Actual owner acceptance remains Pending. Backend restart clears the real observations and does not automatically fetch them again. SQ-01/T-03 now have real technical evidence but persistent rights, complete timestamp/adjustment/reconciliation/replay qualification and cumulative acceptance remain open. No full VS-01 acceptance, commit, tag or push is declared.

Final Step 5D.3 private verification passed 44 checks: real data remains in backend RAM, exactly four historical requests, zero PostgreSQL live-data writes, default provider gate false, backend-only credentials, no actual credential exposure, and unchanged requirements/tags/math. Audits report zero known vulnerabilities; two pattern candidates were reviewed public/synthetic values, not suppressed credentials. Cumulative working tree: **44 files (19 modified, 25 new)**; nothing staged, committed, tagged or pushed. Application is ready for owner UAT; actual owner acceptance remains pending.


## Step 5D.4 - standing on-demand retrieval, 2026-11-06

This is the latest operating disposition. Earlier per-request grants, disabled normal retrieval, fixed four-call diagnostic-only limits and filter-only Apply range statements above are historical and superseded within the owner's standing read-only grant. Immutable requirements/decisions are unchanged.

**Implemented and verified:** provider-neutral coverage/acquisition coordination, verified identity resolution, missing/stale planning, bounded sequential transport/rate/call budgets, single flight, cancellation/error/backoff, shared canonical Decimal validation, atomic bounded RAM merges and read snapshots, frontend history/research/comparison acquisition, warm-up prefix handling, explicit refresh and cached-data reuse. Existing formulas/persistent repository are reused. Final full regression: **577 backend/PostgreSQL, 22 frontend, four browser workflows passed**, zero failed/skipped; lint/build passed. Earlier discovered cancellation/refresh, mixed-snapshot and obsolete no-wiring test issues were corrected before final verification.

**Real engineer verification:** six bounded read-only attempts; five published validated acquisitions adding 18 observations. One attempt did not publish during view switching; its provider response is not retained/claimed successful. All four ETFs have four sessions November 2-5, with November 6 provider-pending. Apply range retrieved two previously unloaded SILVERBEES dates; repeat reused cache without a request. Charts, SMA 200/EMA 37/RSI 14 and both four-date comparisons refreshed. Current counts: 250 each, SILVERBEES 252 including two earlier calendar-unassessed dates. No raw-response persistence or live-price SQL rows. Deployment preserved the initial 984 canonical rows/IDs through RAM; old original numeric epochs were not exposed by the legacy API and remain explicitly unavailable.

**Implemented but not fully verified/qualified:** nonzero optional polling has not been exercised in the live browser (default off); future dates outside the packaged reviewed calendar remain UNASSESSED; provider timestamp/session semantics, adjustment treatment and independent reconciliation remain open. **Blocked:** permitted persistent retention/backups, point-in-time/replay qualification, SQ-01/T-03 final disposition and actual owner acceptance. **Not implemented/not authorized:** scheduler, token renewal, account/holdings/orders/trading or later increments.

The normal MARKET_DATA_ENABLED gate is enabled locally under standing authority; its committed default is false. The legacy DHAN_DATA_API_ENABLED value remains false. Credentials are API-only; Windows 40/Linux 31 Python package scans and full/production npm scans report zero known vulnerabilities/skips. No full VS-01 acceptance, commit, tag or push. See [complete Step 5D.4 checkpoint](VS-01_STEP5D4_ON_DEMAND_DATA_CHECKPOINT.md), [operating policy](../05-operations/MARKET_DATA_OPERATING_POLICY.md) and [owner guide](../05-operations/REAL_DATA_UAT_USER_GUIDE.md).
