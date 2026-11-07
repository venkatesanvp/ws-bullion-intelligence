# Package 6 - forecast performance intelligence checkpoint

Date:2026-11-07 IST. Base HEAD/main remains `fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9`. No stage/commit/tag/push. Requirements baseline, decision register, FRC-001..016 Proposed statuses and requirements-v1.0 remain unchanged.

**Implemented and deployed:** descriptive performance scorecards, matched-origin B01/B02 analysis, separate B03 volatility errors, error/rolling/distribution diagnostics, optional cutoff-snapshot regimes, and bounded transient aggregate registry. **Not established:** effective independent sample size, significance, model superiority, strict real historical accuracy, full source qualification or restart-safe forward evidence. No new ML/forecast model or trading capability.

Design: [Package6 scoped decisions](../03-design/FORECASTING_PACKAGE_6_DESIGN.md). Forward gates/proposal: [forward-evaluation readiness](FORECASTING_PACKAGE_6_FORWARD_READINESS.md). Package5 checkpoint/qualification remain unchanged as historical evidence. Owner UAT remains pending.

## 1. Verified baseline and implemented behavior

Package5 source/tests/receipts support its reported874backend/45frontend/9browser results and34conditional origins per ETF/horizon. Re-execution now passes901/51/9. Strict availability/source/calendar/vintage gates and conditional owner acknowledgement remain intact. All four real histories retain their original null provider event/publication fields and actual local first-seen. Original source is still TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED; a performance contract does not promote it.

New immutable model-independent `forecast-performance-v1` results record model ID/version/configuration, instrument/currency, horizon, evaluation mode, dataset/experiment/origin-set fingerprints, basis/window, metrics, requested/matured-eligible/scored/unmatched/excluded/pending/unavailable counts, overlap/disjoint support, qualification, assumptions, assessment/computation and retention. Capabilities separate point price/return from volatility proxy; fields are not restricted to one model's identity. Type/consistency validators reject mixed dataset/mode/window/horizon/instrument evidence and directional scoring of volatility-only cards. Versions/configurations cannot be silently pooled.

When both B01/B02 are requested, both new scorecards and their error/rolling/regime diagnostics use exactly the intersection of matured compatible origin/target/reference/actual cases. Unmatched cases are counted explicitly. B03 uses its own eligible volatility outcomes; a single-model request cannot manufacture a paired comparison. B02-minus-B01 MAE is a descriptive matched loss difference, not a superiority test. No winner/leaderboard/ranking is produced. Existing individual-model evaluation tables retain their original metric behavior; the new matched scorecards are the comparison surface.

Signed error=forecast-actual; absolute error=absolute signed value. Point percentage error=100*signed/actual, return error=predicted simple return-(actual/origin-1). Zero or abs(denominator)<=1e-8 makes the corresponding normalized diagnostic null with a reason, never an epsilon substitute. Canonical Price already rejects actual zero; direct numeric tests also cover zero defensively. These normalization safeguards do not alter existing primary metric equations. B03 uses horizon-sigma minus the existing future realized-volatility proxy, without price/directional/percentage scoring.

All authoritative arithmetic uses Decimal34 and existing wire12 fixed strings. Rolling MAE/RMSE/bias use trailing scored origins, default10/configurable2..30; partial-window counts and latest outcome availability are explicit. They are post-outcome diagnostics at actual assessment and cannot be used as historical origin inputs. The existing forecast-versus-actual endpoints remain, with separate price-error and volatility-proxy-error plots; approximate browser coordinates never become financial calculations.

Distributions use signed return-error fractions for point models and separate signed volatility-proxy fractions for B03. Seven fixed raw-Decimal bins are x<-.05;[-.05,-.01);[-.01,0);exact0;(0,.01];(.01,.05];x>.05. p10/median/p90 use nearest-rank, no interpolation/normality/probability/calibration assumption. Near-zero normalized exclusions are counted. Display rounding can hide tiny nonzero errors; raw Decimal values determine bins.

Requested origins, matured eligible origins, common scored origins, overlap pairs and maximum disjoint target windows are distinct. Disjoint target intervals (origin,target] are counted by reviewed session indices and maximum interval scheduling. They do not establish statistical independence: serial dependence and shared lookback inputs remain. Effective independent count is null/NOT_ESTIMATED. No HAC/bootstrap/effective-n/significance methodology or reliable ranking is claimed; small subgroup/disjoint support warnings remain visible.

Optional regime analysis is off by default. It reads only the final21 contiguous completed closes of the exact validated cutoff snapshot and runs before outcome access. TRENDING requires efficiency abs(last-first)/sum(abs(changes))>=.35 and absolute20-session simple return>=.02; otherwise SIDEWAYS. A flat path has efficiency0. HIGH volatility means sample sigma of20simple returns>=.015; otherwise LOW. Context<21 or unsupported numerics ->UNAVAILABLE, not invented labels. Trend and volatility are separate axes. Rules/version fixed-21-close-v1 are deterministic research thresholds, not fitted/validated economic regimes. Conditional labels share unverified adjustment/availability limitations; later adjustments may embed economic future information even though no future target rows enter the classifier. Enabling regimes changes experiment identity by rule version; turning them off preserves prior semantic identity. Forecast equations/IDs are unchanged for the same request/context.

## 2. API, transient registry and dashboard

Existing authenticated compute-only POST `/api/v1/research/forecasts/evaluate` adds strict boolean `regime_analysis` (false default) and integer `rolling_error_window`2..30 (10default). Response adds `performance`: scorecards, matched comparison, per-origin errors, rolling diagnostics, distributions, optional aggregate regime groups and warnings. Existing modes/ACK/period/horizon/model controls and sanitized error handling remain.

New authenticated GET `/api/v1/research/forecasts/performance` returns `transient-performance-registry-v1`: up to32experiment aggregate records in backend RAM, expiring after3600seconds and lost on restart/eviction. Records retain only registry ID/computation time/cards/comparison; no per-origin error vectors, price histories, raw responses or regime paths are retained. It creates no persistent ledger, SQL table/migration, file or browser storage. The actual receipt verified16records after the bounded four-ETF evaluation (strict plus three conditional horizons for each). Registry rows remain separate by mode/dataset/window and are not pooled into a comparison.

Current POST run, context and outcome tracking remain available. Existing limits unchanged:5000input rows,80sampled origins/1100calendar-day period, lookback<=1000,3models, one compute gate,30requests/minute, cooperative30-second server deadline and45-second client cancellation. New analysis checks cancellation/deadline per model/error; no worker, GPU, source fetch or schedule. Registry GET is a bounded metadata read. Existing Bearer/Origin/no-store/loopback controls apply.

Forecasting Research adds scorecards/evidence, matched counts, signed/rolling error charts, normalized distributions, optional regime groups, qualification and sample warnings, plus an explicit session-registry button. Shared DataViewport limits initial rows to15 with Show more15increments for errors/rolling/regime/registry tables. B03 fraction units remain separate from point price/return units. Source/mode changes still clear evaluation evidence and reset conditional acknowledgement. No trading controls were added.

## 3. Real-market verification and performance results

Verification used existing real canonical cache only:1294daily rows (250/542/250/252 available,250eligible each),1442intraday candles and4quotes. No Dhan download, profile/account/holdings/balance operation, quote refresh or streaming connection was issued by the performance verification helpers. The wider elapsed-session counter has an unattributed interphase change documented below. Actual receipt time:

2026-11-07 01:15:38 IST (source UTC 2026-11-06T19:45:38.558206+00:00). For each ETF, origin period2026-01-30..2026-10-07, frequency5sessions, lookback60, all3models, regimes enabled and rolling window10. Each1/5/20session conditional horizon scores34common origins; strict h5 scores0 with METADATA_NOT_AVAILABLE exclusions. All primary performance-card metrics exactly equal the Package5 aggregate metrics for the same data/period/model/horizon.

| ETF | h | Common B01/B02 origins | B01 price MAE | B02 price MAE | B02 minus B01 MAE | B03 proxy MAE | Overlap pairs / disjoint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TATAGOLD | 1 | 34 | 0.170000000000 | 0.178302882341 | 0.008302882341 | 0.014421769939 | 0 / 34 |
| TATAGOLD | 5 | 34 | 0.314705882353 | 0.359869316411 | 0.045163434058 | 0.022277592583 | 0 / 34 |
| TATAGOLD | 20 | 34 | 0.628823529412 | 0.935246398225 | 0.306422868814 | 0.028806568870 | 96 / 9 |
| TATSILV | 1 | 34 | 0.558823529412 | 0.588818736375 | 0.029995206963 | 0.023767095408 | 0 / 34 |
| TATSILV | 5 | 34 | 0.970882352941 | 1.126490873921 | 0.155608520980 | 0.039896839394 | 0 / 34 |
| TATSILV | 20 | 34 | 1.665588235294 | 2.875750737574 | 1.210162502280 | 0.059935837889 | 96 / 9 |
| GOLDBEES | 1 | 34 | 1.482941176471 | 1.548455169835 | 0.065513993365 | 0.015204327549 | 0 / 34 |
| GOLDBEES | 5 | 34 | 2.620588235294 | 2.985483211735 | 0.364894976441 | 0.022594709989 | 0 / 34 |
| GOLDBEES | 20 | 34 | 5.325294117647 | 7.802452344366 | 2.477158226719 | 0.027776607271 | 96 / 9 |
| SILVERBEES | 1 | 34 | 5.571764705882 | 5.830180934547 | 0.258416228665 | 0.023897496218 | 0 / 34 |
| SILVERBEES | 5 | 34 | 9.228529411765 | 10.603818999777 | 1.375289588012 | 0.037589901079 | 0 / 34 |
| SILVERBEES | 20 | 34 | 16.194411764706 | 27.435877053532 | 11.241465288826 | 0.054907688991 | 96 / 9 |

Point loss is INR per ETF unit; B03 loss is a volatility-proxy return fraction. These are separate quantities and cannot be compared as directional model performance or across ETF price scales. Complete RMSE/bias/return-MAE/directional fractions/counts and distributions are in the API/dashboard and sanitized aggregate receipt; no raw real prices or per-origin outcomes are written here. Lower descriptive loss on this fixed-vintage sample does not establish general superiority, statistical significance or actionable returns.

All12instrument/horizon combinations have34scored cases per model, zero excluded/pending/unavailable outcomes in this deliberately eligible period, and34paired B01/B02 cases. Each has102error/rolling response rows and18regime groups (three labels on each of two axes x3models). At h1/h5 there are0overlap pairs/34disjoint target windows; at h20 there are96pairs/9disjoint windows. Effective independent sample size remains unestimated in every card. Reusing this data to invent an effective-n or confidence score is prohibited.

Representative h5 regime counts on the shared B01/B02 context (labels are conditional research classifications, not independently verified market states):

| ETF | TRENDING / SIDEWAYS | HIGH / LOW volatility | UNAVAILABLE |
| --- | --- | --- | ---: |
| TATAGOLD | 3 / 31 | 17 / 17 | 0 |
| TATSILV | 2 / 32 | 31 / 3 | 0 |
| GOLDBEES | 3 / 31 | 18 / 16 | 0 |
| SILVERBEES | 4 / 30 | 31 / 3 | 0 |

Subgroups of2/3/4origins (and dependent context windows) cannot support reliable model comparisons. Each axis sums to34; summing trend plus volatility axes would double-count the same origins. No future outcomes were used for classification. Existing prices/first-seen/publication nulls/source evidence were not rewritten to make regimes or strict evaluation pass.

Deployed real-browser performance verification: **passed**. Verified real Gold/Silver baselines, pending outcomes, strict0/null metrics and exclusions, conditional acknowledgement/historical1-session scoring, matched scorecards/error/regime/registry views, native price and volatility error charts,15->30error paging,15->18regime paging, qualification/mode clearing, session reopening, mobile containment and Technical Analytics navigation. The complete synthetic browser suite passed scorecards, matched support,15->30error paging,15->18regime paging, native error chart rendering and the aggregate registry, alongside all prior workflows. Real browser checks block provider acquisition routes and save no screenshot, trace or price payload.

## 4. Verification and security

| Check | Actual final result |
| --- | --- |
| Complete backend + disposable PostgreSQL |901passed;0failures/errors/skips (874previous +27new parameterized/API checks) |
| Frontend |51passed;0failures/skips (45previous +6new performance/control checks); rerun after final registry row-identity correction |
| Complete Chromium workflows |9passed;0failures/errors/skips; synthetic providers/feeds only |
| Python lint / production build |Passed; final frontend build rerun after row-identity correction |
| Dependency scans |40Windows Python/31Linux runtime packages:0known vulnerabilities/0skipped; npm full/production0known vulnerabilities |
| Containers |API/UI built/startup healthy using existing pinned base images/frozen dependencies; runtime31package audit parity verified in final checks |
| Current forecast parity |Before/after current B01/B02/B03 numerical outputs, counts, quality/warnings and original availability evidence hash-identical for all4ETFs |
| Data/provenance integrity |1294daily,1442intraday,4quotes preserved through RAM-only deployment; normalized-by-ISIN canonical IDs/hashes/batches/values/ingestion/event/publication and evidence digests match |
| Credentials |Configured-value source/assets/log/API-response checks pass; `.env` ignored/untracked/byte-unchanged; provider fields API-only, defaults unchanged; no credentials in UI/DB/migration |
| Market persistence |Active price_observations/import_rows/import_batches counts `[0,0,0]`; no price-history files, raw-response archive or database writes introduced |
| Provider-request audit |Each guarded regression/deployment/local performance/browser check had0counter delta; one unattributed23->24increase occurred between regression completion and pre-deployment capture; see limitation below |
| Governance |Baseline/decisions/FRC statuses/tags/history/config/locks/original calendars/canonical analytics and forecasting arithmetic preserved; nothing staged |

Final operational audit found that the hardcoded old total23 was stale: regression remained23->23, but the pre-deployment baseline was already24 and deployment/controlled API/browser checks stayed24->24. No new forecast/performance code contains acquisition operations, and the real-browser check blocked provider routes. There are no retained post-restart provider receipts identifying the earlier change, so its cause cannot be established from available evidence. A counter change is not proof of which HTTP operation occurred. Do not claim zero requests over the entire elapsed task; only the bounded checks have verified zero deltas. No extra provider request was made to investigate. Local `package6-request-counter-review.json` records this unresolved operational-audit limitation. Future readiness should distinguish transport-attempt/day/lifetime counters and retain permitted sanitized operation receipts; this does not authorize raw-response storage.

Initial focused lint found ambiguous/multiple import formatting and was corrected. One new test incorrectly searched for INDEPENDENT inside the warning ending INDEPENDENCE; explicit semantic-warning assertions corrected that test. The focused suite then passed32checks. All complete regression checks passed on the first full run. A final registry UI key correction makes the same aggregate card safe to list in different registry records; frontend51/build were rerun. Remaining nonfatal existing warnings: Plotly large chunk, Starlette/httpx, Alembic path separator and Node color settings. No vulnerability suppression, forced dependency change or failed/skipped check is hidden.

Independent tests use Fraction/100digit references, exact error signs/percentage/returns/rolling metrics, fixed distribution boundaries/nearest rank, zero/near-zero denominators, same-origin compatibility and unmatched exclusions, window scheduling/independence-null contracts, regime flat/threshold/two-axis cases, future-target perturbation invariance, strict/conditional/synthetic gates, registry bounds/expiry/restart/no-per-origin privacy, no-I/O/cancellation and authenticated API option bounds. Existing full analytics/forecast/market/browser regressions remain.

## 5. Qualification gaps and forward-evaluation design

Strict historical availability remains absent; event/publication timestamps are null, finality and adjustment/revision vintages unqualified, and structural/current-vintage replay may embed later information. Source rights permit existing owner transient private research/display; persistent prices/derived histories/backups/redistribution remain unresolved. Acquisition calendar ends2026-11-06; forecast extension ends2026-12-31, with unknown special-session timing and no invented2027calendar. No statistical significance, effective independent sample methodology, calibration or model promotion is approved.

Existing RAM forecast tracking tests pending/maturity/revision blocking but actual forward targets remain pending and backend restart loses records. The new aggregate performance registry is not a durable issuance/outcome ledger. Proposed minimum future design: first approve rights/finality/availability/action/revision/calendar policies; then separately authorize actual-time immutable issuance events with model/config/input hashes and permitted evidence, later append-only outcomes/corrections, qualified retention and recovery. Hash-only metadata cannot independently reproduce restricted prices. No schema, migration, storage permission, scheduler, provider fetch, neural network/Kronos or trading feature was implemented. Full forward readiness/source qualification/VS-01 acceptance is not declared.

## 6. Exact source scope, recovery and commit plan

Package6 touches19paths:9of the existing73 plus10new paths; other64starting paths retain exact bytes. Combined working tree:83files (19modified64new), staging empty. All73starting files were read/scanned/hashed and captured in ignored `artifacts/package6-preimplementation-source.zip` with a SHA/CRC-verified source-only manifest. It excludes `.env`, market history, exports, builds and test artifacts. Recovery is selective after manifest comparison; no blanket reset or destructive restoration. Existing market cache crossed deployment only in RAM; ephemeral catalog UUIDs may remap, so integrity proof uses verified ISIN and preserves canonical observation/batch identities and source evidence.

| Exact Package6 path | Purpose |
| --- | --- |
| `backend/app/forecast_performance_contracts.py` | New model-independent immutable performance/error/sample/regime contracts |
| `backend/app/forecast_performance.py` | New common-origin loss, rolling/distribution and scorecard analysis |
| `backend/app/forecast_regimes.py` | New fixed snapshot-only classification rules |
| `backend/app/forecast_evaluation.py` | Optional pre-outcome regime evidence and version identity |
| `backend/app/forecast_research_service.py` | Bounded analysis and RAM aggregate registry |
| `backend/app/forecast_research_routes.py` | Authenticated GET registry route |
| `backend/tests/test_forecast_performance.py` |26new parameterized independent numeric/PIT/contract/registry tests |
| `backend/tests/test_forecast_research_routes.py` |One new auth/registry/options test |
| `frontend/src/ForecastPerformance.tsx` | New scorecard/errors/charts/distribution/regime/registry view |
| `frontend/src/performanceTypes.ts` | New typed performance contracts |
| `frontend/src/ForecastPerformance.test.tsx` |Five new component tests |
| `frontend/src/ForecastingResearch.tsx` | Optional regime/rolling controls and performance presentation |
| `frontend/src/ForecastingResearch.test.tsx` |One new evaluation-option test |
| `frontend/src/forecastTypes.ts` | Extended evaluation response type |
| `frontend/src/styles.css` | Performance layout containment |
| `frontend/e2e/forecasting.spec.ts` | Extended native workflow with performance paging/chart/registry coverage |
| `docs/03-design/FORECASTING_PACKAGE_6_DESIGN.md` | Scoped design/gap review/formulas/governance |
| `docs/04-planning/FORECASTING_PACKAGE_6_FORWARD_READINESS.md` | Source readiness assessment and minimum proposal |
| `docs/04-planning/FORECASTING_PACKAGE_6_CHECKPOINT.md` | This actual results/UAT/scope checkpoint |

Commit plan (no execution): Package6 depends on earlier uncommitted work and overlaps their files. Recommend reviewing one coherent combined83file implementation checkpoint; do not pretend19paths form a standalone commit against HEAD. After explicit owner approval of the exact combined list, rerun staged secret/artifact/baseline checks and commit using `feat(research): add transient forecast performance intelligence`. No tag/push/release is implied. An alternative sequence of separately reviewed earlier package checkpoints requires deliberate overlap reconstruction from source manifests, not an automatic history rewrite. Current HEAD and all tags remain unchanged; requirements-v1.0 is `5eeed03536e43ded7077ac086b97cb05f2e5b73e`.

Exact combined review set (not staged):

- `backend/app/forecast_baselines.py`
- `backend/app/forecast_calendar_extension.json`
- `backend/app/forecast_contracts.py`
- `backend/app/forecast_dataset.py`
- `backend/app/forecast_demo.py`
- `backend/app/forecast_evaluation.py`
- `backend/app/forecast_market_adapter.py`
- `backend/app/forecast_market_contracts.py`
- `backend/app/forecast_metrics.py`
- `backend/app/forecast_performance.py`
- `backend/app/forecast_performance_contracts.py`
- `backend/app/forecast_qualification.py`
- `backend/app/forecast_regimes.py`
- `backend/app/forecast_replay.py`
- `backend/app/forecast_research_routes.py`
- `backend/app/forecast_research_service.py`
- `backend/app/main.py`
- `backend/app/market_session_routes.py`
- `backend/app/market_session_service.py`
- `backend/app/technical_analytics.py`
- `backend/app/technical_research.py`
- `backend/tests/forecast_fixtures.py`
- `backend/tests/forecast_research_fixtures.py`
- `backend/tests/session_browser_app.py`
- `backend/tests/test_forecast_baselines.py`
- `backend/tests/test_forecast_dataset.py`
- `backend/tests/test_forecast_evaluation.py`
- `backend/tests/test_forecast_market_adapter.py`
- `backend/tests/test_forecast_metrics.py`
- `backend/tests/test_forecast_performance.py`
- `backend/tests/test_forecast_replay.py`
- `backend/tests/test_forecast_research_routes.py`
- `backend/tests/test_forecast_research_service.py`
- `backend/tests/test_technical_analytics.py`
- `backend/tests/test_technical_research.py`
- `docs/03-design/FORECASTING_FOUNDATION_PROPOSAL.md`
- `docs/03-design/FORECASTING_PACKAGE_3_CONTRACTS.md`
- `docs/03-design/FORECASTING_PACKAGE_4_DESIGN.md`
- `docs/03-design/FORECASTING_PACKAGE_5_DESIGN.md`
- `docs/03-design/FORECASTING_PACKAGE_6_DESIGN.md`
- `docs/03-design/RESEARCH_ANALYTICS_PROPOSAL.md`
- `docs/04-planning/FORECASTING_PACKAGE_3_CHECKPOINT.md`
- `docs/04-planning/FORECASTING_PACKAGE_4_CHECKPOINT.md`
- `docs/04-planning/FORECASTING_PACKAGE_5_CHECKPOINT.md`
- `docs/04-planning/FORECASTING_PACKAGE_5_QUALIFICATION.md`
- `docs/04-planning/FORECASTING_PACKAGE_6_CHECKPOINT.md`
- `docs/04-planning/FORECASTING_PACKAGE_6_FORWARD_READINESS.md`
- `docs/04-planning/FORECASTING_REQUIREMENTS_EXTENSION.md`
- `docs/04-planning/RESEARCH_EXPANSION_ASSESSMENT.md`
- `docs/04-planning/TECHNICAL_PACKAGE_2_CHECKPOINT.md`
- `docs/04-planning/UX_PACKAGE_1_CHECKPOINT.md`
- `frontend/e2e/forecasting.spec.ts`
- `frontend/e2e/market-session.spec.ts`
- `frontend/e2e/market-stream.spec.ts`
- `frontend/e2e/provider.spec.ts`
- `frontend/e2e/research.spec.ts`
- `frontend/e2e/technical.spec.ts`
- `frontend/e2e/workbench.spec.ts`
- `frontend/e2e/workspace-ux.spec.ts`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/public/licenses/fancy-canvas-LICENSE.txt`
- `frontend/public/licenses/lightweight-charts-LICENSE.txt`
- `frontend/public/licenses/lightweight-charts-NOTICE.txt`
- `frontend/src/App.test.tsx`
- `frontend/src/App.tsx`
- `frontend/src/ComparisonPanel.tsx`
- `frontend/src/DataViewport.tsx`
- `frontend/src/ForecastPerformance.test.tsx`
- `frontend/src/ForecastPerformance.tsx`
- `frontend/src/ForecastingResearch.test.tsx`
- `frontend/src/ForecastingResearch.tsx`
- `frontend/src/IntradayDashboard.tsx`
- `frontend/src/LightweightResearchChart.tsx`
- `frontend/src/ResearchChart.tsx`
- `frontend/src/ResearchDashboard.tsx`
- `frontend/src/TechnicalWorkbench.test.tsx`
- `frontend/src/TechnicalWorkbench.tsx`
- `frontend/src/api.ts`
- `frontend/src/forecastTypes.ts`
- `frontend/src/performanceTypes.ts`
- `frontend/src/styles.css`
- `frontend/src/technicalTypes.ts`

Ignored local evidence is excluded from this list: package6-starting-scope/source ZIP, verification/regression-preservation, backend-tests.xml/browser-tests.xml, audit/security/deployment-integrity, real-verification, real-browser, governance-review/final-verification. Real receipts contain aggregate errors/counts/quantiles/groups/hashes only, not price paths or per-origin diagnostics. Source-only checkpoints are not market-data backup authorization.

Traceability: FRC-005/009/011/015 and REQ-06-003/005/018 for deterministic matched evaluation/as-of regimes; FRC-010 for versioned transient result identity and proposed forward ledger; FRC-012 for scorecards/visualizations; D-03/D-09/D-12 boundaries preserved. All16FRC requirements remain Proposed. No new requirements/sample threshold, model lifecycle or source qualification is silently approved.

## 7. Owner UAT and recommended next package

1. Open `http://127.0.0.1:5173`, unlock locally, select an ETF/transient Dhan source/Provider adjusted basis, Research dashboard -> Forecasting Research. Never enter provider credentials into the frontend.
2. Run strict historical evaluation: expect0scored origins/null metrics with current evidence. Performance cards must also show0, not conditional scores. Confirm source qualification and independence NOT_ESTIMATED.
3. Explicitly select Conditional historical replay, read/acknowledge assumptions. Choose lookback60, origin period2026-01-30..2026-10-07, frequency5, historical horizon1/5/20. Enable optional cutoff-regime research and rolling window10. Run for each ETF: expect34matched B01/B02 origins and separate B03 volatility scoring.
4. Inspect model/version/mode/window/basis/qualification, eligible/scored/unmatched counts, overlap/disjoint counts, bias/return/directional metrics and descriptive paired loss difference. Do not rank models or compare ETF unit-price errors as a leaderboard. At20sessions verify96overlap pairs and9disjoint windows, with independent evidence unavailable.
5. Inspect actual-versus-forecast and separate price/volatility error charts, signed/absolute/%/return errors, trailing partial windows/outcome-known times, fixed-bin distributions and nearest-rank summaries. Use15->30paging. Review21-close rule definitions and small subgroup counts; Show more regime groups expands15->18. Disable regimes and rerun: no subgroup claims should be invented.
6. Click View session performance registry. Only aggregate results should appear, with explicit mode/dataset/window; records expire after one hour/32limit/restart. Switch mode/source and confirm displayed evaluation evidence clears and conditional acknowledgement resets.
7. Confirm current baselines, outcome tracking and existing Technical Analytics/native charts remain. Do not refresh/acquire provider data for this UAT; the verified cache suffices. Owner sign-off is pending; no trading or source-retention permission is granted by this checklist.

Recommended next package: source rights and prospective PIT evidence readiness. Qualify timestamp/finality/action/revision/calendar policies and allowed retention/backup scope; predeclare support and statistical methodology; then separately authorize a minimal durable prospective issuance/outcome ledger and forward verification. Do not add Kronos/ML, automated collection or trading before those gates. No next increment is started here.
