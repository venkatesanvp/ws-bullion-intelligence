# Package 1 - Bullion Workspace UX checkpoint

Date 2026-11-06. Authority: owner UX/fundamental/correlation/forecasting request explicitly authorizes Package 1 only. **Implemented, deployed and engineer-verified; owner acceptance Pending.** No commit/tag/push created. Packages 2-6 remain review proposals; no baseline/math/provider/dependency changes.

## Changes and shared policy

UX-01: sidebar Bullion Workspace; heading Bullion Data Workspace; consistent unlock/open/lock text and topbar Data Workspace. Actual previous heading was Data workbench. Login language now accurately describes read-only research rather than claiming no live prices. Internal Workbench identifiers, navigation, routes and authentication behavior are preserved.

UX-02: one DataViewport component measures the first 15 actual row heights, including multiline evidence, rather than applying different per-page pixel caps. Table headers stick while scrolling. Named, focusable regions support keyboard scrolling; ResizeObserver/window resize and cleanup handle layout changes. On mobile, viewport height is capped at75dvh so fewer than 15 multiline rows may fit; wide evidence tables scroll internally, without making the page wider. Text wraps where practical; exact prices/provenance remain accessible.

UX-03: DATA_PAGE_SIZE=15 drives history and recorded-batch request limits and research/comparison/intraday reveal increments. Load more/Show more keeps all subsequent rows reachable. Viewports cover all five tables (history, daily research, intraday, comparison summary/common-date values) and data lists (catalog, watchlists/members, sources, validation issues, recorded batches). Lists retain complete content; no underlying array/API response is arbitrarily truncated. Native selectors, forms, summary chips and four quote cards retain their respective behavior. Catalog allPages preloading remains complete for correct filters/selectors; it is not a displayed15-row pagination control.

Existing sort/order/filter/cursor semantics and backend indicator input ranges are unchanged. Chart renderers, canonical calculations, Dhan credentials/settings, PostgreSQL and dependencies are untouched. UI-only container replacement preserved the running API/RAM; no backend restart/handoff was needed.

## Verification actually executed

| Check | Final result |
| --- | --- |
| Backend/PostgreSQL |647 passed,0 failures/errors/skips; migrations/integrity/math/security included |
| Frontend components |29 passed,0 failed |
| Chromium |7 workflows passed,0 failures/errors/skips; six existing workflows plus new45-row UX case |
| New browser UX | Initial15 ->30 ->45 complete rows; final row accessible; sticky header/internal scrolling;4-row filtered range;390px mobile page containment |
| TypeScript/Vite production build | PASS; existing Plotly chunk-size warning remains |
| Compose/UI deployment | Image build/start and HTTP availability PASS; API kept running; immutable base references unchanged |
| Windows Python dependency scan |40 packages,0 vulnerabilities,0 skips |
| Linux Python dependency scan |31 pinned deployed packages,0 vulnerabilities,0 skips; manifest below verified equal to running image |
| Full npm dependency audit |0 vulnerabilities; dependencies/lockfiles unchanged |
| Credentials/source/assets/API logs | PASS: actual values and encoded forms compared only in memory; no matches; .env ignored/untracked |
| Backend isolation/config | Dhan values remain API-only; UI/DB/migration have none; loopback bindings; configured values unchanged |
| Active PostgreSQL | price_observations/import_rows/import_batches each0; no provider-price persistence |
| Encoding/Git | Changed files strict UTF-8; diff check; no staging/commit; baseline/math/tags unchanged |

Initial automated-browser failure was an overly exact sidebar text locator that included its nested subtitle; corrected the test locator, then all seven workflows passed. One Windows SSE test teardown emitted a connection-reset callback notice while its test passed; final browser run passed. Existing Starlette/httpx/Alembic deprecations and Plotly chunk-size warning are not hidden. Original full verification receipt retains the first browser failure; final browser XML and package-specific combined receipt record the successful rerun. No failed checks are relabelled successful in place. OS-image CVE scanning is not claimed.

## Real existing-data regression

Final deployed Chromium verification passed15 checks. Existing real history starts with 15 exact rows and Load more shows30; sticky headers/internal scrolling work. Daily Plotly chart remains rendered, with 15 exact research rows initially. A cached previous-session intraday request returns75 valid five-minute candles with 0 provider requests. Existing read-only feed subscription receives four valid frames and all four LIVE_STREAM cards remain present, with stale after-hours trade times; disconnect preserves cached fallback. Browser contacts only loopback services; no provider credentials enter its assets or requests.

Actual precheck cache: TATAGOLD250, TATSILV542, GOLDBEES250, SILVERBEES252 = **1294 observations**. TATSILV history was already extended from the earlier1002-row checkpoint. Final check compares the actual baseline, not a stale hardcoded count: canonical daily rows/IDs/available provenance hash is unchanged, and intraday cache count is unchanged. No values are written to a verification price file. Two bounded existing-provider feed connections were used during real verification: initial UI check received four normalized updates but its stale1002-count assertion failed; corrected baseline check received four repeated frames, correctly suppressing duplicate price events (0 new updates). Both made0 additional Dhan REST calls; no token exchange, historical download, scheduler, account access or trading.

Raw payloads/price screenshots are not persisted. Sanitized counters/timestamps/hashes are ignored artifacts only. The original stale-count assertion remains in its initial receipt. This was a verification-assumption correction, not a data deletion/reset. Source timestamp/adjustment/retention/replay limitations and owner acceptance remain open.

## Assessment delivered for Packages 2-6

[Twelve-part assessment](RESEARCH_EXPANSION_ASSESSMENT.md) covers current state, five observation groups, indicators/fundamentals/macroeconomic drivers, chart comparison, logical architecture, primary-provider/rights research, forecast methodology, prioritized backlog, decisions and next authorization. [Analytical contracts](../03-design/RESEARCH_ANALYTICS_PROPOSAL.md) define every requested indicator's formula/parameters/history/warm-up/timeframe/limitations/tests, typed fundamental/macro/event evidence, point-in-time correlation/beta/lags, exact currency interactions, event studies and purged walk-forward/proper-score evaluation.

Recommendation: keep current charts until an approved Lightweight Charts parity/attribution spike; no Advanced Charts personal-use assumption. Add ATR/MACD first, Donchian next, ADX/Bollinger as separate reviewed follow-ups. Use issuer NAV/facts rather than equity valuation; qualify direct primary macro sources, licensed DXY/bullion and event evidence separately. FRED current terms restrict storage/caching and software/AI/ML use: do not treat it as blanket training/storage permission. No substantial dependency, source adapter, analytical method, fundamental tab, macro/event/forecast implementation or new account is introduced now.

## Owner UAT instructions

Open http://127.0.0.1:5173 and unlock privately with LOCAL_APP_TOKEN. Refresh the page to load the new UI. Owner results below are Pending and must not be filled from engineer automation.

| Owner check | Expected | Result |
| --- | --- | --- |
| Terminology/unlock/navigation/lock | Bullion Workspace/Bullion Data Workspace and unchanged tabs | Pending |
| History |15 initial rows; Load more preserves rows; internal scroll and sticky headings; filters still work | Pending |
| Daily/comparison/intraday exact tables |15 initial values, Show more increments15, complete dataset accessible; charts/indicators unaffected | Pending |
| Catalog/source/watchlist/import lists | Long lists scroll internally; filters, source selection and membership/import controls still function | Pending |
| Keyboard/mobile | Named regions focus and scroll; narrow layouts contain wide tables; no lost columns or provenance | Pending |
| Existing real history/live feed | Real data/source/freshness preserved; after-hours quotes may be stale; no trading capability | Pending |

Record selected ETF/source/date/timeframe and sanitized symptoms only; no Dhan secrets/account details/real-data screenshots. Existing source/replay/full VS-01 acceptance blockers remain. Next recommended approval is Package 2.1 chart parity plus Package 2.2 ATR/MACD conventions, not all future packages at once.

## Exact proposed Git contents

**16 files:11 modified,5 new; nothing staged.** HEAD remains fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9 on main. No commit/tag/push. requirements-v1.0 remains 5eeed03536e43ded7077ac086b97cb05f2e5b73e; requirements/project-context baseline and all backend/financial code unchanged. Local .env, credentials, artifacts, backups, build and test outputs are excluded.

- `docs/03-design/RESEARCH_ANALYTICS_PROPOSAL.md`
- `docs/04-planning/RESEARCH_EXPANSION_ASSESSMENT.md`
- `docs/04-planning/UX_PACKAGE_1_CHECKPOINT.md`
- `frontend/e2e/market-session.spec.ts`
- `frontend/e2e/market-stream.spec.ts`
- `frontend/e2e/provider.spec.ts`
- `frontend/e2e/research.spec.ts`
- `frontend/e2e/workbench.spec.ts`
- `frontend/e2e/workspace-ux.spec.ts`
- `frontend/src/App.test.tsx`
- `frontend/src/App.tsx`
- `frontend/src/ComparisonPanel.tsx`
- `frontend/src/DataViewport.tsx`
- `frontend/src/IntradayDashboard.tsx`
- `frontend/src/ResearchDashboard.tsx`
- `frontend/src/styles.css`
