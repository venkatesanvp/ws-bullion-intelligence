# Step 5D.4 - standing on-demand market data checkpoint

Date: 2026-11-06. **Implementation ready for owner UAT; owner acceptance Pending. No full VS-01 acceptance.** Parent HEAD remains `ef0a7c460ec82ce3797da37cded883ec82553871`, branch main. Nothing staged/committed/tagged/pushed.

## 1. Architecture and traceability

The owner's Step 5D.4 grant is implementation-level standing authority for read-only market data until revoked; previous per-batch gates no longer govern normal operation. Baseline requirements and Decision Register remain unchanged. Trace: D-14; REQ-02-007/008/011/012/013/014/015; DC-02/03/04/07; existing VS-01 market-data/research work items and SQ-01/T-03. This evidence does not accept every traced requirement.

The provider-neutral MarketDataService coordinates the existing DailyMarketDataProvider adapter, canonical validation and transient repository. No second ingestion database/model, new deployment infrastructure, analytics formula, broker SDK or account capability. The original PostgreSQL persistent-ingestion path remains rights-gated.

## 2. Backend services

`market_data_service.py` resolves full configured identity, assesses coverage, plans bounded retrieval and calls the existing adapter. `market_data_routes.py` exposes authenticated local GET policy and POST ensure with disconnect cancellation. Existing config/main wire the adapter without startup HTTP; `dhan_provider.py` adds bounded timeout/catalog injection. `transient_research.py` adds empty catalog registration, validated atomic merge, bounded evidence and coherent per-request snapshots. Shared `prepare_collected` permits explicitly unassessed calendar only for transient mode; strict persistent defaults remain.

`transient_handoff.py` is a one-time authenticated canonical RAM-view migration, sealed before normal acquisition; not an ongoing provider importer or data cache file. Original 984 canonical rows, IDs and exposed batch provenance were compared exactly across deployment, without re-download or SQL/file prices. Numeric source epochs were not exposed by the old API, so migrated rows disclose their absence rather than inventing them. New acquisitions retain actual source epoch/row/batch evidence.

## 3. Apply range workflow

Select ETF/source/Provider adjusted and inclusive dates -> ensure coverage -> acquire eligible missing/stale spans -> canonical validation -> atomic RAM merge -> existing history/chart/indicator reads. A provider view can also ensure current coverage on opening. No diagnostic script or per-request owner approval. History shows loading, reused/updated/partial and sanitized errors; pagination uses applied rather than draft dates. Explicit Refresh from provider supports bounded revalidation. Existing valid cached observations remain available after failure.

## 4. Coverage algorithm

Per-date states: AVAILABLE, NOT_REQUESTED, ATTEMPTED_EMPTY, NON_TRADING, PROVIDER_PENDING, FAILED, REJECTED, OUTSIDE_VERIFIED_HISTORY. Available rows are reused until stale; empty and failures have separate retry eligibility. Only independently confirmed calendar closures/inception boundaries are excluded. Empty does not mean holiday/inception. Missing ranges never bridge an available session; confirmed closures can be bridged, then dates are partitioned and call count capped.

Packaged reviewed calendar: 2025-11-02 through 2026-11-06, including previous reviewed NSE exceptions. Outside coverage is UNASSESSED, including weekend status. No future/current-day requests under conservative T-1 publication. Latest completed-session candidate (16:00 IST cutoff) is reported separately from provider-eligible date; neither is a publication SLA. Inclusive-to-exclusive translation remains inside the Dhan adapter.

## 5. Request and concurrency controls

Defaults: 8 calls per operation; <=366 inclusive days per request; 10-second phase timeout plus existing streamed-body/size bounds; global single-flight/one provider request at a time; at least one second between requests; local daily budget 1000. No automatic retry/fallback/token exchange. 401/403/429/5xx/timeouts stop further chunks and produce sanitized failures/cooldown. Concurrent waiters replan after publication. Disconnect stops later work; a bounded in-flight result is discarded if canceled, so a later operation can require those still-uncovered dates again. This exception is disclosed rather than claiming all live attempts were published.

Configured limits and default-off active-view polling are in [the operating policy](../05-operations/MARKET_DATA_OPERATING_POLICY.md). Rate budgets are per API process, not an account-wide durable ledger; other clients' quota use is unknown. No new scheduler or workers.

## 6. Validation and merge

Shared strict Decimal OHLC, integral bounded volume, OHLC consistency, timestamp numeric/range/provisional IST mapping, identity, arrays, duplicate/date and calendar validation. No financial float arithmetic, rounding/truncation or missing-price fill. Existing identifiers reused for identical data; validated refresh revisions get new IDs/batches/revision while evidence is retained within bounds. Immutable publication/read snapshots prevent mixed metadata/data revisions. Memory overflow fails atomically, preserving existing rows. Defaults cap rows and coverage at 100000, evidence at 2048 batches/series plus twice the row-cap in observation evidence. This is not a durable replay archive.

## 7. Frontend, warm-up and comparisons

History, ResearchDashboard and ComparisonPanel ensure data before their existing reads. Required warm-up uses a bounded earlier observed-session prefix; known missing expected prefix dates prevent a complete-warmup claim. Existing Decimal SMA/EMA/Wilder RSI and common-date comparison formulas are unchanged. Actual indicator unavailable/break rules remain authoritative. Comparisons remain price-only, not total return or evidence of adjustment compatibility. Optional mounted/visible-view polling is implemented, default 0; a nonzero live polling interval was not exercised in this checkpoint.

## 8. Real DhanHQ verification

Engineer-operated Chromium used the actual running UI/API and existing backend token; no raw responses, price files, real screenshots/traces or PostgreSQL prices. Standing-authorized test cap: **six sequential read-only historical attempts**, no automatic retry/fallback, no trading/account operation.

Actual: **six attempts; five published validated batches, 18 observations added**. One attempt did not publish during view switching; its raw response/status is not retained, so success is not claimed for it. Noncanceled concurrent duplicate requests are independently verified to make one provider call in mocked tests.

| Primary ETF | November 2-6 observations | Entire retained count | Latest date |
| --- | --- | --- | --- |
| TATAGOLD | 4 (November 2, 3, 4, 5) | 250 | 2026-11-05 |
| TATSILV | 4 (same dates) | 250 | 2026-11-05 |
| GOLDBEES | 4 (same dates) | 250 | 2026-11-05 |
| SILVERBEES | 4 (same dates) | 252 | 2026-11-05 |

November 6 is displayed PROVIDER_PENDING for all four, not fabricated or labelled a holiday. SILVERBEES has two extra earlier observations from the explicit Apply range test for **2025-10-30 through 2025-10-31**: the range was empty in RAM before the click; exactly one new provider call added two validated observations. Repeating Apply made zero calls. This earlier range is outside the packaged reviewed calendar and remains calendar-unassessed.

Actual charts, SMA 200, EMA 37, Wilder RSI 14 and both metal comparison views refreshed; both November 2-6 comparisons used four common dates. The browser made zero external-origin requests; Dhan traffic stayed backend-only. No investment-performance conclusion, full timestamp contract, adjustment equivalence or source acceptance is inferred.

## 9. Automated verification

Final full run: **577 backend/PostgreSQL tests, 22 frontend component tests, four Chromium workflows passed; zero failed/skipped**. Ruff, production build and rebuilt Compose startup passed. Deterministic tests use explicitly synthetic mocked responses, not live Dhan. Tests cover full/missing/middle/partial ranges, empty/negative cache, calendar/pending/inception, backoff/status/timeout, cancellation, concurrent duplicates, malformed/invalid/duplicate OHLCV, Decimal/provenance, capacity, stale/explicit refresh, warm-up gaps, exact one-time handoff and concurrent merge/read snapshot consistency. Existing all-four mapping/adapter/ingestion/analytics regressions remain passing.

Earlier runs found cancellation/refresh edge cases, the preserved-view versus mixed-snapshot regression and a superseded no-web-wiring assertion. These were corrected; the latter now checks no storage in the adapter and no retrieval in the composition root. The final run above passed. An initial pip-audit command used an unsupported option combination; corrected installed-environment scans completed successfully.

Nonblocking warnings: existing Starlette/httpx and Alembic deprecations, runner color warning, approximately 1.22 MB lazy Plotly chunk. Optional nonzero polling is implemented but not live exercised; no claim of complete OS-image vulnerability clearance.

## 10. Security and persistence verification

Fresh pip-audit: **40 Windows and 31 actual Linux packages, zero vulnerabilities/skips**. Full and production npm audits: zero vulnerabilities. No dependency changes, forced updates or advisory suppression. Private actual-secret/URL/base64 scans of changed sources, production assets and runtime logs found no matches. All seven Dhan fields remain API-only; UI/DB/migration have none. HTTPS historical endpoint, header-only token, explicit timeouts, no proxy/redirect/token exchange. Loopback-only published API/UI; database has no public port.

Application PostgreSQL counts after live verification: **zero observations, import batches and import rows**. Real provider rows/source/catalog exist only in RAM. `.env` is ignored/untracked; `.env.example` contains placeholders. Local standing flag is enabled, committed default disabled, diagnostic flag unchanged false. No raw market response/export, secrets, generated build or test artifact is proposed for Git.

## 11. Readiness and remaining blockers

Implemented and verified for the core on-demand user flow; ready for hands-on UAT. Actual owner acceptance remains Pending. Remaining: SQ-01/T-03 final qualification, account-applicable private storage/backup/retention rights, source timestamp/session contract, precise adjustment and cross-provider compatibility, independent price/volume reconciliation, point-in-time/replay evidence, calendar review beyond packaged scope, and original numeric epoch evidence absent from migrated rows. Nonzero polling is not live exercised. No full VS-01 acceptance.

Not implemented/not authorized: persistent live ingestion pending rights, scheduled acquisition, token renewal, holdings/funds/orders/trading, next implementation increments. Existing PostgreSQL architecture is retained; no file cache circumvents unresolved rights.

## 12. Source-control checkpoint and exact proposed contents

Before changes, all **44 existing dirty files (19 modified, 25 new)** were inspected/preserved, actual-secret checked and archived in ignored source-only `artifacts/step5d4-source-checkpoint.zip` with a hashed starting-scope manifest. It contains no `.env`, market-data response, backup, build or test artifact. No prior work was discarded or history rewritten.

Current proposed cumulative scope: **54 files (21 modified, 33 new)**, comprising the earlier 44 plus the Step 5D.4 additions. `.env` is a separate ignored local operating-policy edit, never staged. Requirements baseline and existing tags are unchanged; requirements-v1.0 remains `5eeed03536e43ded7077ac086b97cb05f2e5b73e`. HEAD unchanged. No commit/tag/push or staging performed; owner review precedes any Git commit.

| Action | Exact path |
| --- | --- |
| Modified | `.env.example` |
| New | `backend/app/acquisition.py` |
| Modified | `backend/app/config.py` |
| New | `backend/app/daily_values.py` |
| Modified | `backend/app/dhan_diagnostic.py` |
| New | `backend/app/dhan_history_contract.py` |
| Modified | `backend/app/dhan_history_diagnostic.py` |
| New | `backend/app/dhan_http.py` |
| New | `backend/app/dhan_import.py` |
| New | `backend/app/dhan_provider.py` |
| Modified | `backend/app/ingestion.py` |
| Modified | `backend/app/main.py` |
| New | `backend/app/market_data.py` |
| New | `backend/app/market_data_routes.py` |
| New | `backend/app/market_data_service.py` |
| Modified | `backend/app/models.py` |
| New | `backend/app/nse_calendar.json` |
| New | `backend/app/provider_ingestion.py` |
| Modified | `backend/app/queries.py` |
| Modified | `backend/app/research.py` |
| Modified | `backend/app/schemas.py` |
| New | `backend/app/transient_handoff.py` |
| New | `backend/app/transient_research.py` |
| New | `backend/app/transient_uat.py` |
| New | `backend/migrations/versions/0002_provider_ingestion.py` |
| New | `backend/tests/provider_fixtures.py` |
| New | `backend/tests/seed_provider_browser.py` |
| New | `backend/tests/test_acquisition.py` |
| New | `backend/tests/test_dhan_provider.py` |
| New | `backend/tests/test_dhan_provider_integration.py` |
| Modified | `backend/tests/test_integration.py` |
| New | `backend/tests/test_market_data_service.py` |
| New | `backend/tests/test_provider_ingestion.py` |
| New | `backend/tests/test_transient_research.py` |
| Modified | `compose.yaml` |
| Modified | `docs/04-planning/VS-01_DATA_QUALIFICATION.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` |
| New | `docs/04-planning/VS-01_STEP5D1_PROVIDER_ADAPTER_CHECKPOINT.md` |
| New | `docs/04-planning/VS-01_STEP5D2_HISTORY_INGESTION_CHECKPOINT.md` |
| New | `docs/04-planning/VS-01_STEP5D3_REAL_DATA_UAT_CHECKPOINT.md` |
| New | `docs/04-planning/VS-01_STEP5D4_ON_DEMAND_DATA_CHECKPOINT.md` |
| New | `docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json` |
| New | `docs/05-operations/MARKET_DATA_OPERATING_POLICY.md` |
| New | `docs/05-operations/REAL_DATA_UAT_USER_GUIDE.md` |
| New | `docs/05-operations/VS-01_STEP5D3_UAT_CHECKLIST.md` |
| New | `frontend/e2e/provider.spec.ts` |
| Modified | `frontend/src/App.test.tsx` |
| Modified | `frontend/src/App.tsx` |
| Modified | `frontend/src/ComparisonPanel.tsx` |
| Modified | `frontend/src/ResearchDashboard.tsx` |
| Modified | `frontend/src/ResearchShared.tsx` |
| Modified | `frontend/src/ResearchViews.test.tsx` |
| Modified | `frontend/src/api.ts` |
| New | `frontend/src/useMarketRefresh.ts` |

Ignored generated evidence includes backend/browser XML, builds, audit/security/live/deployment receipts, source checkpoint and helper scripts. It is not part of this file set. No unintended large source files. The exact proposed-file offline pattern scan returned four reviewed benign candidates: placeholder URI, public plan fingerprint, synthetic fixture token and dummy local test URI. An initial broad all-files scan also saw expected credentials in the ignored local .env and cache markers; these were not Git candidates. Its output was replaced with a sanitized scoped review without hashes of local credentials. No live credential verification or finding suppression.

## 13. Owner UAT and next authorization

Use [the updated guide](../05-operations/REAL_DATA_UAT_USER_GUIDE.md) and [pending owner checklist](../05-operations/VS-01_STEP5D3_UAT_CHECKLIST.md). In History select SILVERBEES / Dhan transient / Provider adjusted / November 2-6 / Apply range; expect the four currently eligible dates, pending-current-day message and clear actual coverage. Repeat for reuse. In Research apply explicit indicator periods with enough prefix; compare both metal pairs on common dates. Record actual owner Pass/Fail/Pending without credentials or exported prices.

Next is owner hands-on review and separate approval of a coherent Git checkpoint. Persistent provider ingestion still needs applicable rights/retention qualification; no later implementation begins here. No per-request market-data approval is required under the standing policy.
