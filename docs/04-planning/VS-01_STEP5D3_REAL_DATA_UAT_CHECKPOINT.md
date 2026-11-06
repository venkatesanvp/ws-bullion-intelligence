# Step 5D.3 — real-data integration, local deployment and UAT checkpoint

Recorded: 2 November 2026. Source-control parent: `ef0a7c460ec82ce3797da37cded883ec82553871`, branch `main`. The initial 33-file Step 5D.1/5D.2 work was reviewed and preserved before changes; its hashes are in ignored `artifacts/step5d3-starting-scope.json`.

**Outcome: real DhanHQ acquisition and application integration verified; local application available for owner UAT. Actual owner acceptance remains pending.** This is not another mock-only milestone, a release, full source qualification or full VS-01 acceptance. No commit/tag/push was created.

Authority: the owner's Step 5D.3 request explicitly approved at most four sequential historical requests for the fixed four listings/window, transient real-data research, local Compose deployment/migrations, and conditional persistence only when applicable terms permit. No additional retrieval approval was requested. Trace: D-04/12/14, ADR-01/03/04/05/08/09/10, DC-02/03/04/07/09 and REQ-02-007/008/009/011/012/013/014/015, REQ-05-003/004/010. Baseline classifications and mathematical conventions remain unchanged.

## A. Actual real-data acquisition

Exactly **four authenticated POST requests** were made to `https://api.dhan.co/v2/charts/historical`, sequentially with the existing one-second spacing and no retries/fallback/token exchange. Every request used exchangeSegment=NSE_EQ, instrument=EQUITY, oi=false, fromDate=2025-11-02, and exclusive toDate=2026-11-03 (inclusive research end 2026-11-02). The requested window was not changed.

| ETF | Symbol / security ID / ISIN | HTTP | Actual observations | Earliest returned candidate session | Latest returned candidate session | Duplicate sessions | Invalid canonical observations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tata Gold ETF | TATAGOLD / 21401 / INF277KA1976 | 200 | 246 | 2025-11-03 | 2026-10-30 | 0 | 0 |
| Tata Silver ETF | TATSILV / 21428 / INF277KA1984 | 200 | 246 | 2025-11-03 | 2026-10-30 | 0 | 0 |
| Nippon India Gold BeES | GOLDBEES / 14428 / INF204KB17I5 | 200 | 246 | 2025-11-03 | 2026-10-30 | 0 | 0 |
| Nippon India Silver BeES | SILVERBEES / 8080 / INF204KC1402 | 200 | 246 | 2025-11-03 | 2026-10-30 | 0 | 0 |

All are INR, NSE-listed ETF market prices, not NAV. The 247-session explicit calendar includes the 1 February 2026 Sunday Budget session. Each response omitted only scheduled **2026-11-02**; no unexpected sessions were returned. This is an availability warning, not a failed import or permission to fabricate a last bar. It is consistent with the [official T−1 availability FAQ](https://dhan.co/support/platforms/dhanhq-api/why-am-i-not-receiving-the-latest-day-s-data-from-the-daily-historical-data-api/). No extra catch-up request was made.

The backend load command's local HTTP response was 201/READY_TRANSIENT_UNQUALIFIED. Its one-shot process latch was claimed before network construction; duplicate/concurrent commands cannot issue another batch in that process. A separate ignored owner-scope ledger was created before submission. Neither a profile/master request nor any unrelated account/holdings/balance/order operation was performed. `artifacts/step5d3-live-acquisition-receipt.json` contains sanitized counts/dates/provenance only, not raw prices, response bodies, source epoch values or secrets.

## B. Validation and remaining source limitations

The existing Dhan adapter and shared canonical report validator checked schema/aligned arrays; exact Decimal prices and precision/ranges; positive OHLC and low/open/close/high coherence; nonnegative bounded integer volume; explicit timestamp conversion; calendar membership/order; duplicate epochs/dates; full listing identity and source provenance. All four passed these checks, with MISSING_OBSERVATIONS as the sole dataset issue.

Per ETF, both volume and timestamp counters recorded **246 integral-decimal numeric encodings**, zero JSON-integer encodings, fractional/unsupported/non-finite/range-invalid values, and zero duplicate sessions. All timestamps mapped under the explicit candidate Unix-seconds-to-Asia/Kolkata policy. Original numeric source timestamp values/encoding/row references are preserved in the process-memory canonical acquisition; event/publication times remain null/unknown. There was no float-based canonical arithmetic, rounding/truncation of integer-only fields, value repair or missing-session filling.

Real-data evidence now spans 2025-11-03 through 2026-10-30, expanding the prior five-session observation. It still does not establish the provider's complete timestamp/session contract, independent price/volume truth, ETF adjustment factors/distribution treatment, revision policy or point-in-time availability. Daily PROVIDER_ADJUSTED follows the existing official split/bonus policy reference; total-return comparability is not inferred. Source qualification remains provisional and UNVERIFIED_FOR_REPLAY; SQ-01/T-03 are only partially evidenced, not fully accepted.

## C. Persistence decision and architecture

**No real market prices were persisted to PostgreSQL or files.** The [reviewed Dhan terms](https://dhan.co/terms/) and [historical API documentation](https://dhanhq.co/docs/v2/historical-data/) establish the technical endpoint but do not conclusively establish this account's private database/derived-use/backup/retention rights or duration. No general personal-use exemption, unlimited redistribution right or retention period was assumed. Successful access is not such evidence. Account-applicable terms, subscription/exchange conditions or another authorized permission reference must resolve that separate storage question.

The owner explicitly allowed transient application testing while that question is unresolved. Validated observations therefore live only in **the existing backend process's memory**. This permits the application to reuse the single download during UAT without pretending permanent storage is authorized. The transient source reports TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED, permitted research/display/retrieval, and storage=false. It is not a persisted QUALIFIED_FOR_RESEARCH source or a bypass of the PostgreSQL ingestion licence gate.

Implementation reuses rather than duplicates the architecture:

- The report-building portion of provider ingestion is extracted into `prepare_collected`; both the persisted path and transient retention sink call the same canonical validator. Persistent source-use checks remain separate and unchanged.
- A bounded process-memory registry retains canonical observations and original per-row provenance, atomically publishing the four datasets only after canonical checks. It has no file/SQL writes or scheduler and is not a second ingestion database.
- Existing SQL listing/source pages merge transient identities through the same cursor mechanism. Existing history/chart/indicator/comparison routes read either the SQL source or the transient canonical reader. Quality/provenance assembly is shared through `describe_series`; pure analytical engines are unchanged.
- Owner-authenticated, Origin-protected POST `/api/v1/transient-session/dhan-history` requires explicit live_approved and the fixed reviewed plan fingerprint. It enables credentials only in that call's configuration dictionary; the OS environment and .env are not changed. Normal startup/browser reads do not contact Dhan. GET `/api/v1/transient-session` is a sanitized local status report.
- The frontend recognizes the explicit transient read authorization without granting storage qualification. CSV imports still require their qualified persistent source contract. The real-data warning, latest date, coverage and units are visible.

PostgreSQL row-count equality before/after live loading and testing is verified separately. Schema migration `0002_provider_ingestion` was authorized and applied during Compose deployment; it changes source constraints, not live price data. The existing volume and accepted CSV records were preserved. Process restart/stop clears the real observations; starting services does not redownload them. No hidden file cache, raw authenticated-response store or automatic refresh was introduced.

## D. Real-data application integration verified

All four real ETF histories were exercised through the deployed application APIs and an engineer-operated browser, with zero external browser requests or browser errors:

- Real price charts and exact tables: 246 observations per ETF, requested range selection, latest date 2026-10-30, INR units, source/transient warnings and full-window missing-session disclosure.
- SMA 20/50/200, configurable EMA (37 tested), and Wilder RSI 14: all 20 configurations available on the real observations. API checks verified warm-up periods and independently recomputed the final SMA values with Decimal; no real price/indicator values were exported to evidence files.
- TATAGOLD/GOLDBEES and TATSILV/SILVERBEES: each comparison has **246 common dates**, 2025-11-03 through 2026-10-30. The existing price-only/not-total-return disclosure remains visible. No investment-performance conclusion is asserted here.
- Existing history pagination and source/quality data are available. The table initially shows 100 rows; Show more research rows reveals the remaining rows without another provider request.

Sanitized evidence: `artifacts/step5d3-real-research-verification.json` and `step5d3-live-browser-verification.json`. The real browser verification deliberately created no trace, screenshot, video, HAR, storage-state file or raw-price artifact. Local/session browser storage remained empty.

## E. Local application status

| Component | Status |
| --- | --- |
| PostgreSQL | Running/healthy, existing local volume preserved |
| Backend | Running/healthy, schema 0002_provider_ingestion; four real transient series loaded |
| Frontend | Running; browser HTTP access verified; transient-source gate corrected and deployed |
| Browser address | **http://127.0.0.1:5173** |
| Provider integration default | false in .env and normal backend environment; explicit load was process/call-local |
| Scheduled acquisition | None |
| Startup errors | None in final deployment/readiness checks |
| Disposable test database | Stopped after regression |

All published ports remain loopback-bound. PostgreSQL has no public host port. No public deployment or new framework/infrastructure was added. Do not restart/recreate the backend merely to begin UAT: it holds the only current real-data copy. Normal UI restart does not clear backend memory.

## F. Automated verification and security

Final complete regression: **551 backend/PostgreSQL tests, 18 frontend tests, four existing Chromium workflows passed**, with zero final failures/errors/skips. Lint and TypeScript/production build passed. The four new transient-path tests include canonical rejection, memory lifetime, atomic one-shot claim, full existing research APIs and exact PostgreSQL before/after equality. The accidentally imported test helper was aliased so it is not counted as an artificial extra test.

Actual real-data API/browser verification is additional to those synthetic regressions, not a substitute or an owner acceptance result. Current security results: Windows **40 packages** and actual Linux **31 packages** audited with pip-audit 2.9.0, **zero vulnerabilities and zero skipped packages**; full and production npm audits **zero findings**. No dependency upgrade or advisory suppression. Offline detect-secrets 1.5.0 retained two benign candidates: the public SHA-256 approved-plan fingerprint and the explicitly synthetic fixture TOKEN. Their hashes were checked against the known literals; no live credential verification, ignore pragma or baseline suppression was used.

Final private verification passed **44 checks** across source/assets/evidence, runtime/local responses and Git. No actual credentials or encoded forms matched the inspected files or logs. All seven provider fields remain API-only and normal gate=false; published ports are loopback only. PostgreSQL counts for observations/import batches/import rows/sources/instruments exactly match their pre-load counts. The backend still holds the original four real transient datasets after UI deployment and regression; no additional provider request was made. Sanitized evidence is in `artifacts/step5d3-final-verification.json`, the audit reports, live acquisition/research/browser receipts and `step5d3-final-regression.log`. Existing Starlette/httpx and Alembic deprecations, color-runner warnings and the approximately 1.22 MB lazy Plotly chunk warning remain; OS-image vulnerability clearance is not claimed.

Intermediate findings are retained: the initial real browser check found the frontend still excluded the explicitly authorized transient source. This was corrected with a shared read-capability helper, preserving unverified/restricted-source and CSV storage gates. Optional-source TypeScript narrowing was corrected before the final build. Only the frontend was rebuilt/restarted after loading, preserving the backend's real data. Final real browser checks passed for all four ETFs and both comparisons. No fallback download or extra authenticated request was used to recover.

## G. Owner acceptance readiness

Use [the hands-on guide](../05-operations/REAL_DATA_UAT_USER_GUIDE.md) and [owner checklist](../05-operations/VS-01_STEP5D3_UAT_CHECKLIST.md). They reference actual UI controls, local startup/stop commands, private LOCAL_APP_TOKEN entry, the four ETF/source/basis selections, dates, SMA/EMA/RSI, comparisons, latest/gap information and memory lifecycle. The owner can record Pass/Fail/Pending, observations and enhancement requests without copying secrets/provider payloads into source control.

| Milestone | Disposition |
| --- | --- |
| Automated tests | Passed |
| Engineer real-data integration verification | Passed with recorded source/availability limitations |
| Application available for hands-on UAT | Yes; real observations are currently held in backend memory |
| Actual owner acceptance | **Pending — not performed or inferred from browser automation** |
| Permanent-data/source/full VS-01 acceptance | Not declared; applicable gates remain open |

## H. Source-control status

**Cumulative scope: 44 uncommitted files ? 19 modified and 25 new**, including the original 33-file work. Nothing is staged. The final manifest records each file and its content hash; exact paths follow. Initial work was not discarded or overwritten. Requirements, mathematical conventions, existing tags and source-control parent remain unchanged; no credentials, account identifiers, raw market prices/responses, generated builds, backups or test evidence are proposed for commit. The JSON plan contains scheduling metadata only. No commit, tag, amend or push was performed.

Proposed checkpoint message: `feat(vs01): enable real-data transient research and local UAT`.

## I. Recommended next step

**The owner should now use the running real-data application and complete the UAT checklist.** Collect usability/errors/enhancements before selecting the next implementation increment. In parallel, resolve account-applicable private storage/derived-use/backups/retention conditions. If permitted, separately authorize retaining the existing canonical observations through the already implemented PostgreSQL repository, avoiding another download while the RAM session is alive. Do not silently convert transient authorization into storage permission.

A new bounded retrieval authorization is needed after a backend restart or to acquire later sessions; this step's maximum four requests are consumed. No trading/GTT, paper transactions, portfolio access, scheduled refresh or unrelated research capability is included. Full timestamp/adjustment/reconciliation/replay qualification and owner acceptance remain distinct future decisions.


## Exact cumulative checkpoint file set

Modified (19):

- `backend/app/config.py`
- `backend/app/dhan_diagnostic.py`
- `backend/app/dhan_history_diagnostic.py`
- `backend/app/ingestion.py`
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/queries.py`
- `backend/app/research.py`
- `backend/app/schemas.py`
- `backend/tests/test_integration.py`
- `docs/04-planning/VS-01_DATA_QUALIFICATION.md`
- `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md`
- `frontend/src/App.test.tsx`
- `frontend/src/App.tsx`
- `frontend/src/ComparisonPanel.tsx`
- `frontend/src/ResearchDashboard.tsx`
- `frontend/src/ResearchShared.tsx`
- `frontend/src/ResearchViews.test.tsx`
- `frontend/src/api.ts`

New (25):

- `backend/app/acquisition.py`
- `backend/app/daily_values.py`
- `backend/app/dhan_history_contract.py`
- `backend/app/dhan_http.py`
- `backend/app/dhan_import.py`
- `backend/app/dhan_provider.py`
- `backend/app/market_data.py`
- `backend/app/provider_ingestion.py`
- `backend/app/transient_research.py`
- `backend/app/transient_uat.py`
- `backend/migrations/versions/0002_provider_ingestion.py`
- `backend/tests/provider_fixtures.py`
- `backend/tests/seed_provider_browser.py`
- `backend/tests/test_acquisition.py`
- `backend/tests/test_dhan_provider.py`
- `backend/tests/test_dhan_provider_integration.py`
- `backend/tests/test_provider_ingestion.py`
- `backend/tests/test_transient_research.py`
- `docs/04-planning/VS-01_STEP5D1_PROVIDER_ADAPTER_CHECKPOINT.md`
- `docs/04-planning/VS-01_STEP5D2_HISTORY_INGESTION_CHECKPOINT.md`
- `docs/04-planning/VS-01_STEP5D3_REAL_DATA_UAT_CHECKPOINT.md`
- `docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json`
- `docs/05-operations/REAL_DATA_UAT_USER_GUIDE.md`
- `docs/05-operations/VS-01_STEP5D3_UAT_CHECKLIST.md`
- `frontend/e2e/provider.spec.ts`
