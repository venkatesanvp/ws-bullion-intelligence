# Package 2 technical analytics and forecasting foundation checkpoint

Date: 2026-11-06. Base HEAD: `fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9` on main. **Implementation checkpoint for review; owner UAT pending. No commit, stage, tag or push authorized or performed. No full VS-01 acceptance.** Package 1's 16 uncommitted files were preserved; see scope below.

## 1. Readiness and authorization

The current Package 2 request authorizes a bounded chart spike, ATR/MACD/prior-window Donchian and forecasting requirements/design only. Existing requirements/decisions retain their statuses. ADR-01/02/06 architecture and canonical Decimal pipeline are preserved; ADR-07 Plotly remains in use. The opt-in Lightweight renderer is a scoped spike, not an approved universal replacement. No new provider, account/trading action, scheduled collector, persistence layer, model engine or ML dependency was introduced.

| Capability | Actual disposition |
| --- | --- |
| Daily/intraday technical workbench, completed candles, exact values and explicit parameters | Implemented and automated/real-cache verified; owner UAT pending |
| ATR/MACD/prior-window Donchian arithmetic | Implemented; independent exact-rational synthetic and real-cache verification |
| Existing SMA/EMA/Wilder RSI, Plotly daily/intraday and ETF comparisons | Preserved; regression verified, core analytics/comparison files unchanged |
| Lightweight Charts daily/intraday candles, volume, SMA/EMA/RSI and navigation | Implemented bounded parity spike; Chromium/real-data verification; wider parity/UAT incomplete |
| FRC-001..016 and forecast architecture/contracts/evaluation/backlog | Proposed only; review completed for consistency, not approved or implemented |
| Calibrated predictions, Kronos/model integration, fine-tuning, macro/fundamental/event features | Not implemented; new approvals, rights, history and evidence required |
| Persistent real market-data retention/backups, full PIT replay/source semantics | Existing qualification gaps remain open; no PostgreSQL market-data writes |

## 2. Package 2A - parity assessment and recommendation

Pinned `lightweight-charts` **5.2.1** with transitive `fancy-canvas` 2.1.0; package lock records integrity. All assets are local. Plotly basic 4.2.0 remains installed, lazy-loaded and default. The separate **Technical analytics** view offers the opt-in renderer; existing Daily research/Intraday research/ETF comparison views are retained. Daily close-only CSV rows never acquire invented OHLC; missing OHLC yields whitespace candles and unavailable ATR/channel, while close-based methods remain possible. CSV sources offer daily technical research; intraday options require the existing session-capable Dhan source.

| Feature | Existing Plotly / new opt-in parity | Verification / gap |
| --- | --- | --- |
| Daily price | Existing line retained; native candles for real OHLC | Real TATAGOLD and synthetic workflow; all-four real values checked through API |
| Intraday | Existing OHLC hover/line retained; native completed candles | Five-minute real cached bars and browser timeframe selection; forming bars excluded |
| Volume | New separate native histogram pane | Exact share volume table; unsafe JS integer volume omitted from geometry rather than rounded |
| SMA/EMA / RSI | Same backend values; overlays and separate RSI pane | Exact legacy equality; existing RSI flat-window convention preserved |
| ATR/MACD/Donchian | New technical lines/panes/overlays; MACD native histogram | Exact values below chart, explicit warm-up/unavailable reasons |
| Crosshair | Shared across five native panes; exact OHLCV legend | Native Chromium and real data checks; renderer numbers are geometry only |
| Zoom/pan | Native drag/wheel/pinch plus accessible zoom/reset buttons | Native canvas zoom/drag and real-data checks; viewport retained for same-frame refresh |
| Timeframe / timezone | Daily and 1/5/15/25/60-minute options on supported source | Daily session identity unchanged; intraday UTC identity with IST axis/crosshair labels; five-minute browser demonstration |
| Source/freshness/basis | Visible backend computation time, quality, warm-up, incomplete exclusion | Source remains TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED; no false fully-qualified badge |
| Exact/a11y access | Shared 15-row sticky/focusable viewport with Show more | Canvas is not a screen-reader value table; exact semantic table retained; manual keyboard/screen-reader UAT pending |
| Comparison/export/mobile/performance | Existing comparison charts remain Plotly | No native normalized multi-ETF parity, export/annotation/plugin equivalence, large-series latency benchmark or full cross-browser validation |

Recommendation: retain Plotly as default and for comparison/general research. Lightweight Charts is a useful opt-in OHLC/volume/multi-pane candidate. Before migration, verify comparison, gaps, accessibility, mobile gestures, export and measured update/large-series performance. Migration cost is moderate: normalize typed time/series data, manage imperative chart lifecycle, viewport/resize, explicit timezone formatting, source labels, accessible values and test native canvas behavior. Indicators continue to be calculated once in the backend, independently of renderer. No unsupported performance advantage is claimed.

Final production bundle measurement: native chart lazy chunk about **177.75 kB / 57.84 kB gzip**, versus existing Plotly chunk **1,218.42 kB / 406.91 kB gzip** (bundle sizes, not runtime benchmark). Both are shipped because parity is incomplete. Existing >500 kB Plotly build warning remains; no dependency forced-upgrade or warning suppression.

Licensing review: [official Lightweight Charts docs](https://tradingview.github.io/lightweight-charts/docs) and installed LICENSE/NOTICE specify Apache-2.0 and TradingView attribution/link. The renderer retains the logo, creator notice and visible TradingView link plus local LICENSE/NOTICE. Transitive fancy-canvas is MIT; its upstream copyright/permission notice is retained locally because the published npm package omitted its license file. [Official fancy-canvas license](https://github.com/tradingview/fancy-canvas/blob/master/LICENSE). No TradingView data connection/CDN is used. [TradingView library eligibility](https://www.tradingview.com/free-charting-libraries/) does not make Advanced Charts available for personal use; no Advanced Charts integration was introduced.

## 3. Package 2B - indicator implementation and numerical evidence

`backend/app/technical_analytics.py` is pure, no-I/O arithmetic, version `decimal-technical-v1`. Inputs are finite positive Decimal prices, coherent complete OHLC where required, sorted unique times and nonnegative exact-integer volume. Existing `analytics.py`/`comparison.py` are unchanged. Decimal context is locally **34 digits, ROUND_HALF_EVEN**, recursive state retains full context precision, derived values serialize to exactly **12 decimal places** through existing wire rules. No binary floating-point financial calculation; frontend Number conversion is chart geometry only.

| Method | Implemented formula/default and first eligible value |
| --- | --- |
| ATR 14 | TR=max(H-L,abs(H-Cprev),abs(L-Cprev)); first TR at bar 2; seed mean of first n TR at bar n+1; thereafter ((n-1)*ATRprev+TR)/n. Default first value at 15 OHLC bars |
| MACD 12/26/9 | Fast/slow EMA each seeds with first n-close SMA and alpha=2/(n+1); M=fast-slow; signal EMA seeds on first signal_n valid M values; histogram=M-signal. Line at 26 closes, signal/histogram at 34 |
| Donchian 20 | Upper=max prior n highs, lower=min prior n lows, middle=(upper+lower)/2; **current bar excluded**. First channel at n+1=21 OHLC bars |

Parameters explicit and configurable, strict integers; fast<slow. ATR/channel periods 1..9999, slow 2..10000, fast/signal 1..9999, MACD total warm-up <=10000; existing SMA/EMA 1..10000, RSI 2..9999. Complete calculation prefix is capped at 10000 without silent truncation. Existing workbench defaults use SMA20/EMA37/RSI14; these are explicit workbench choices, not a change to legacy indicator semantics.

Daily endpoint `POST /api/v1/research/technical` uses the existing authenticated source/basis gate, consistent REPEATABLE READ database/transient snapshot, complete eligible prefix then selected-range filtering. Current/future IST daily records are conservatively excluded; this is not a substitute for source-finality/PIT qualification. Daily metadata returns exact OHLCV, provenance, input fingerprint, params/versions, warm-up and source limitations. Existing intraday endpoint accepts optional `technical` parameters, reuses bounded acquisition/cache and completed-bar continuity rules, returns the three additional bundles/fingerprint without changing legacy calculations. No model/data-storage endpoint is added.

Known missing sessions/candles and incomplete session boundaries restart seeds under existing continuity policy; ordinary complete consecutive sessions retain the overnight previous close for ATR. Missing OHLC resets ATR/channel; valid close-based MACD remains independent. Incomplete observations never contribute and reset continuity; no rounding/truncation/fill of bad inputs. Calendar uncertainty remains explicit. Daily and each intraday interval are separate series; there is no implicit resampling or mixing of forming/final data. Technical workbench reports sanitized acquisition failures while retaining available cached values; automatic daily retrieval is restricted to the supported provider-adjusted basis, as in existing daily research.

Independent synthetic references use exact Fraction closed-form EMA/RMA and prior-window scans, not the production recurrence copied into tests. Hand vector: closes [10,11,12,14,13], highs C+1/lows C-1, ATR3 -> first 7/3 then 20/9; MACD2/3/2 -> line at bar3=1/2, bar4 line=2/3, signal=7/12, histogram=1/12; bar5 signal=43/108, histogram=-5/54. Prior Donchian3 at bar4 upper13/lower9, unchanged by raising the current high. Tests cover exact seeds, flat inputs, parameter bounds, malformed OHLC/NaN/float/volume/order/duplicates, gaps, missing OHLC, incomplete bars, future-prefix invariance, output limits and isolation from global Decimal context. Warm-up is numerical eligibility, not convergence or predictive evidence.

Real-cache validation separately compared every available daily value to an exact-rational oracle: **1294 rows**, TATAGOLD250, TATSILV542, GOLDBEES250, SILVERBEES252. All new values matched to 12 places. Existing SMA/EMA/RSI matched their original endpoints exactly; repeat fingerprints matched. Each ETF's previous-session five-minute cache returned **75 completed bars**, with 75 available ATR/MACD/channel values after pre-range warm-up; legacy intraday values were unchanged. No real-price fixture, response file or fabricated expected market result was committed or created.

## 4. Package 2C - deliverable and trace review

- [FRC-001..016](FORECASTING_REQUIREMENTS_EXTENSION.md): each Proposed with description/rationale/priority/acceptance/dependencies/verification/existing requirement trace; overlaps explicitly reuse canonical identity/PIT and REQ-06 obligations.
- [Foundation design](../03-design/FORECASTING_FOUNDATION_PROPOSAL.md): twelve logical modules within the modular monolith; request/dataset/feature/model/result/scenario/evaluation contracts; baseline definitions; proposed coverage/quality/maturity/numeric gates; chronological evaluation/metrics; Kronos source review; feature-source governance; prioritized F0-F5 backlog and ten open decisions.
- Existing [research analytics proposal](../03-design/RESEARCH_ANALYTICS_PROPOSAL.md) retains its historical proposal and adds a dated scoped disposition. Initial forecast horizons 1/5/20/60/120 sessions; earlier exploratory 252 remains deferred. No other indicator, macro/fundamental/event integration or immutable requirement was silently promoted.

REQ-03-007 -> scoped Package 2B authorization -> `technical_analytics.py`, daily/intraday integration -> 28 new backend cases/component/native browser/real-cache evidence. REQ-06-002 independent numerical checks and REQ-06-001 traceability apply. FRC specifications map existing REQ-02-008/011/012/013/014/015, REQ-03-001/002/004/010/012/013/022 and REQ-06-001/002/003/005/006/012/018 without changing their statuses. Forecast-model interfaces, probabilities, evidence ledger and evaluation code remain unimplemented.

## 5. Verification evidence

Final full regression and security disposition is recorded below after the final run. Ignored artifacts contain synthetic-test outputs or sanitized metadata, not raw Dhan responses, credentials or price backups. Automated engineer verification is separate from owner UAT.

| Check | Actual final result / evidence |
| --- | --- |
| Python lint | Passed (`ruff check backend scripts`) |
| Backend with isolated PostgreSQL | **675 passed, 0 failures/errors/skips**; 28 new technical cases; `artifacts/backend-tests.xml` |
| Frontend | **33 passed**, six files; final type-check/build rerun after a test-only literal-type correction |
| Chromium workflows | **8 passed, 0 failures/skips** against real FastAPI + disposable test DB and explicitly synthetic provider; native canvas/navigation covered (`browser-tests.xml`) |
| Production build | Passed after final fixture type correction; native lazy chart/Plotly retained; existing large Plotly chunk warning remains |
| Compose | API/UI images built, ready endpoints/startup verified; PostgreSQL private; API/UI loopback; test DB disposable loopback |
| Real technical references | All 1294 daily rows exact-match independent rational references; four five-minute cached datasets, 75 bars each; existing indicators unchanged (`package2-real-data-verification.json`) |
| Real browser | **24 checks passed** including current native renderer, existing fallback, mobile and feed controls (`package2-live-browser.json`); final acquisition-disclosure update additionally covered by synthetic browser/component tests |
| Bounded existing feed | Final check CONNECTED, four additional frames, zero new price updates and zero rejected frames; disconnected afterward. After-hours duplicate/no-new-trade behavior is not new-tick/live-hours freshness verification |
| Dhan REST calls in engineer verification | **0 new daily/intraday/quote REST downloads**; responses used from existing cache; feed connections reported separately |
| Dependency scans | Windows Python40 and actual Linux runtime31 packages: 0 known vulnerabilities, 0 skipped; npm full and production: 0 known vulnerabilities (`package2-audit-summary.json`) |
| Credentials and writes | Repository/assets/log exact local secret comparisons clean; `.env` ignored/untracked and byte-unchanged; credentials API only; application price_observations/import_rows/import_batches counts remain [0,0,0] |
| Canonical preservation | RAM bridge preserved 1294 daily rows, 4 quotes, 1442 intraday candles exactly incl IDs/available provenance; subsequent daily fingerprints unchanged; no raw-response/price-file persistence |
| Governance | Baseline/context, existing analytics/comparison, requirements-v1.0 and all tags unchanged; HEAD unchanged; staging empty |

Evidence limitation/history: initial independent test helper incorrectly used serialized reference output and was corrected to a raw-rational reference; an initial lazy-render component assertion was changed to wait for the renderer. Final expanded tests then passed. One real verifier initially used the wrong legacy query key (`method` instead of `indicator`), received local HTTP422 and was corrected; no Dhan request occurred. First after-hours feed window did not meet its frame-delta assertion; the final bounded check records an immediate baseline and four additional frames, with zero new price updates. A late test fixture widened `source_kind` to string: tests/browser passed but TypeScript production build failed. The literal type was corrected; final frontend tests/build/startup were rerun. Original intermediate receipts are retained, not rewritten as successes; final frontend results supplement `verification.json`, whose intermediate build failure remains truthful.

Remaining nonfatal warnings: upstream Starlette TestClient/httpx deprecation; existing Alembic path_separator deprecation; existing Plotly chunk size and npm transitive whatwg-encoding deprecation. No forced dependency replacement or warning suppression. Package 2 introduces no backend dependencies; Kronos/PyTorch/tokenizer/training dependencies and weight files remain absent. Dependency audit is a known-vulnerability snapshot, not a guarantee of all security properties.

## 6. Owner UAT checklist - all pending owner execution

1. Open the running local workspace at http://127.0.0.1:5173 using the locally configured application token; never paste credentials into screenshots/issues.
2. Select each of TATAGOLD, TATSILV, GOLDBEES and SILVERBEES with the existing Dhan source/provider-adjusted basis. Confirm source/basis/time/freshness and unqualified/transient limitations remain visible.
3. In Research dashboard -> Technical analytics, confirm default existing Plotly lines, exact OHLCV and first 15 table rows; Show more retains prior rows and sticky/internal scroll works with keyboard.
4. Select Lightweight Charts parity spike: inspect genuine daily candles, volume, SMA/EMA/prior channel and RSI/MACD/ATR panes; crosshair displays exact values; zoom/pan/reset and source labels work. Close-only data must not show invented candles.
5. Confirm default ATR14/MACD12-26-9/Donchian20 and explicit SMA20/EMA37/RSI14. Change periods, Apply, verify parameter labels/results; reject invalid order/periods. Confirm warm-up/unavailable rows are labeled and Donchian excludes current bar.
6. Select supported intraday intervals (1/5/15/25/60), initially previous session. Confirm completed-bar-only technical calculations, distinct intraday basis, IST time labels and no forming candle in the technical values. Broader intervals/real-session coverage remain owner UAT; initial automated native demonstration uses five minutes.
7. Return to Daily research, Intraday research and both metal ETF comparisons; verify existing charts/ranges/results remain available and price-only comparison limitations visible. Canvas geometry is approximate; compare exact values below.
8. Verify mobile width/scroll, pane controls/gestures, keyboard table navigation and actual screen-reader behavior. Full accessibility/cross-browser acceptance remains pending.
9. During an open NSE session, separately verify genuine new quote/tick freshness and controlled fallback. Engineer after-hours checks did not establish new-trade delivery or all outage scenarios.
10. Review FRC-001..016, target/cutoff/support/retention/numeric decisions and F0/F1 proposed scope; do not infer forecasting approval from this UAT. Record pass/fail and discrepancies before checkpoint approval.

## 7. Remaining acceptance and qualification limitations

Owner UAT is pending. Real market source remains transient owner-authorized and unqualified for unrestricted storage/backup/replay; data-use permissions, daily timestamp/session convention, adjustment/revision/finality and total-return compatibility remain unresolved. Date/shape compatibility is not adjustment qualification. No persistent ingestion, historical backup or data-source approval was added. Live-hours fresh-tick verification, full browser/accessibility/performance/export/comparison renderer parity and operational acceptance remain incomplete. Package 2A is a bounded spike; existing Plotly remains default.

No forecast outputs or skill results exist. FRC requirements, model lifecycle, numerical solver policy, support/holdout/calibration thresholds and training/derived-output retention are Proposed/open. Current ~250/542-row ETF histories cannot support the proposed long-horizon independent evaluation/calibration floors; no resampling or simulated paths remove that limitation. Macro/fundamental/event sources/vintages are not integrated. Kronos is only source-assessed; no selection, checkpoint rights, Indian-ETF performance or calibrated distribution is established.

## 8. Git review scope

No files staged or committed. `.env`, artifacts/, node_modules/, frontend/dist/, test reports, generated screenshots/traces and caches remain ignored. Requirements baseline, tags and canonical analytics/comparison are unchanged. The following exact combined working-tree set includes carried Package 1 and Package 2; commit scope requires a later explicit review/approval. Package 1 starting-scope byte digests are in ignored metadata, so extensions to carried files are distinguished below.

**38 files: 18 modified, 20 new.** Starting Package 1 scope16; Package 2 adds22 paths and extends three carried paths (ResearchDashboard, styles, analytical proposal). The other13 carried files retain their Package 1 bytes.

| Path | Git state | Scope |
| --- | --- | --- |
| `backend/app/main.py` | Modified | Package 2 added scope |
| `backend/app/market_session_routes.py` | Modified | Package 2 added scope |
| `backend/app/market_session_service.py` | Modified | Package 2 added scope |
| `backend/app/technical_analytics.py` | New | Package 2 added scope |
| `backend/app/technical_research.py` | New | Package 2 added scope |
| `backend/tests/session_browser_app.py` | Modified | Package 2 added scope |
| `backend/tests/test_technical_analytics.py` | New | Package 2 added scope |
| `backend/tests/test_technical_research.py` | New | Package 2 added scope |
| `docs/03-design/FORECASTING_FOUNDATION_PROPOSAL.md` | New | Package 2 added scope |
| `docs/03-design/RESEARCH_ANALYTICS_PROPOSAL.md` | New | Package 1 + scoped Package 2 extension |
| `docs/04-planning/FORECASTING_REQUIREMENTS_EXTENSION.md` | New | Package 2 added scope |
| `docs/04-planning/RESEARCH_EXPANSION_ASSESSMENT.md` | New | Package 1 carried |
| `docs/04-planning/TECHNICAL_PACKAGE_2_CHECKPOINT.md` | New | Package 2 added scope |
| `docs/04-planning/UX_PACKAGE_1_CHECKPOINT.md` | New | Package 1 carried |
| `frontend/e2e/market-session.spec.ts` | Modified | Package 1 carried |
| `frontend/e2e/market-stream.spec.ts` | Modified | Package 1 carried |
| `frontend/e2e/provider.spec.ts` | Modified | Package 1 carried |
| `frontend/e2e/research.spec.ts` | Modified | Package 1 carried |
| `frontend/e2e/technical.spec.ts` | New | Package 2 added scope |
| `frontend/e2e/workbench.spec.ts` | Modified | Package 1 carried |
| `frontend/e2e/workspace-ux.spec.ts` | New | Package 1 carried |
| `frontend/package-lock.json` | Modified | Package 2 added scope |
| `frontend/package.json` | Modified | Package 2 added scope |
| `frontend/public/licenses/fancy-canvas-LICENSE.txt` | New | Package 2 added scope |
| `frontend/public/licenses/lightweight-charts-LICENSE.txt` | New | Package 2 added scope |
| `frontend/public/licenses/lightweight-charts-NOTICE.txt` | New | Package 2 added scope |
| `frontend/src/App.test.tsx` | Modified | Package 1 carried |
| `frontend/src/App.tsx` | Modified | Package 1 carried |
| `frontend/src/ComparisonPanel.tsx` | Modified | Package 1 carried |
| `frontend/src/DataViewport.tsx` | New | Package 1 carried |
| `frontend/src/IntradayDashboard.tsx` | Modified | Package 1 carried |
| `frontend/src/LightweightResearchChart.tsx` | New | Package 2 added scope |
| `frontend/src/ResearchDashboard.tsx` | Modified | Package 1 + scoped Package 2 extension |
| `frontend/src/TechnicalWorkbench.test.tsx` | New | Package 2 added scope |
| `frontend/src/TechnicalWorkbench.tsx` | New | Package 2 added scope |
| `frontend/src/api.ts` | Modified | Package 2 added scope |
| `frontend/src/styles.css` | Modified | Package 1 + scoped Package 2 extension |
| `frontend/src/technicalTypes.ts` | New | Package 2 added scope |

## 9. Exact next proposed implementation authorization

First review the Proposed FRC and F-OD decisions (F0). Then authorize only **F1: offline provider-neutral baseline contract harness**: typed requests/results/capabilities, synthetic point-in-time fixtures, and independently verified no-change/drift/volatility references. No model download, calibrated-probability claim, provider call, storage/ledger migration, macro/event integration, training or trading. Production chart migration requires a separate parity/UAT decision. No next implementation begins under this checkpoint.
