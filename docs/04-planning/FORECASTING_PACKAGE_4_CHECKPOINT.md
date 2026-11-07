# Package 4 - real-market forecasting implementation checkpoint

Implementation: 2026-11-06; final verification: 2026-11-07 IST. Base HEAD/main remains `fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9`. No stage, commit, tag or push. All FRC-001 through FRC-016 remain **Proposed**. REQ-BL-1.0, the decision register and `requirements-v1.0` remain unchanged.

**Readiness: implemented and locally deployed for conditional, transient personal research. Full source qualification, historical accuracy evidence and full Package 4/VS-01 acceptance remain blocked.** Existing data is real Dhan data, not a one-year synthetic substitute. Synthetic records are used only in explicitly labeled automated tests.

## 1. Implemented behavior and mathematical conventions

- Read-only adapter consumes the existing canonical daily cache or bounded SQL read, resolves all four ETFs through the existing verified registry, preserves exact Decimal OHLCV, identity, canonical hash/ID/batch/row, event/publication nulls and first-seen stamps. No second provider ingestion path, SQL write or market-data file is added.
- Explicit real-research contracts retain `REAL_MARKET`, `CONDITIONAL_OWNER_RESEARCH`, `LOCAL_FIRST_SEEN_ONLY`, `TRANSIENT_OWNER_RESEARCH_ONLY` and `PROVIDER_ADJUSTED_UNVERIFIED`. Existing synthetic-only constructors/guards remain strict. The source is not promoted to qualified status.
- Prior-date, completed daily candidates only; no quote or intraday substitution. Reject identity/basis/time errors, duplicates, invalid OHLCV and invalid temporal ordering. Exclude out-of-calendar, current-date, missing-first-seen and future-availability rows; report counts and gaps. Context building rejects missing required sessions and stale origins rather than filling them.
- B01/B02/B03 reuse the Package 3 engines and Decimal precision34, ROUND_HALF_EVEN and numeric bounds. B01 equals the exact last close. B02 compounds the arithmetic mean of one-session simple returns. B03 uses sample centered variance and square-root-of-horizon scaling under the documented IID assumption; it has no directional price forecast. Optional annualization is explicit. No probability, interval, calibration, winner or performance guarantee is invented.
- Each model exposes model/version, forecast ID/fingerprint, creation/cutoff, nullable original observation time, separate calendar-close proxy, actual first-seen availability, exact last close, target, quality and warnings. Context count and effective usage differ: with lookback60, B01 validates60/uses1 close and0 returns; B02/B03 use60 closes/59 returns.
- Shared immutable context for a current multi-model run; public inputs are revalidated. The existing chronological evaluator reuses one validated dataset and one context per origin. Future prices never enter model contexts or their fingerprints.
- Historical evaluation provides price MAE/RMSE, return MAE, three-class directional hit fraction, signed forecast-minus-actual price/return bias and separate B03 future realized-volatility-proxy errors. B01/B02 benchmark comparisons use common supported targets. Exclusions, zero samples, overlap pairs and disjoint windows are explicit; zero samples produce null metrics.
- Schema versions are `forecast-contract-v2` / `forecast-research-v2`; metric version `descriptive-metrics-v2-bias`; conditional historical engine `walk-forward-research-v2`. Versions participate in semantic fingerprints. Baseline equations/version `baseline-simple-v1` are unchanged; evidence IDs can change when contracts change.
- Forecasting Research adds instrument/horizon/model/lookback/annualization/period/frequency controls, loading/cancel/error/insufficient states, freshness and source warnings, endpoint-only native charts, distinct volatility results, shared 15-row tables, exclusions, comparison/evidence and session forecast reopening. Existing Daily/Intraday/Technical navigation remains.
- Manual finalized-data refresh reuses the existing acquisition route only after an owner click, for the existing policy's latest eligible session. Forecast APIs themselves do not acquire data. No scheduler, worker, GPU, account or trading capability is introduced.
- Tracking keeps immutable forecasts in process RAM, checks unchanged input hashes/source profile, and reports PENDING, MATURED, EVALUATED, INSUFFICIENT_DATA or DATA_QUALITY_BLOCKED. Later observations do not rewrite predictions. At most32 runs; retention through target plus7days, capped365days. Restart, expiry or eviction loses tracking. Stored receipts omit chart history and retain input references/hashes; no persistent forecast ledger or derived-history archive.

## 2. API and resource controls

All routes use existing local Bearer authentication, Origin checks, sanitized errors and `Cache-Control: no-store`.

| Method | Exact path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/research/forecasts/context?instrument_id=<catalog UUID>&source_id=<source UUID>&basis=PROVIDER_ADJUSTED` | Eligibility, provenance/freshness, source revision, bounded chart context and horizon availability |
| POST | `/api/v1/research/forecasts/run` | Compute selected B01/B02/B03; no data mutation |
| POST | `/api/v1/research/forecasts/evaluate` | Bounded historical walk-forward research; no data mutation |
| GET | `/api/v1/research/forecasts/runs` | Metadata-only process-session run choices |
| GET | `/api/v1/research/forecasts/runs/{run_id}` | Original forecast plus transient outcome assessment |

POST configuration: catalog `instrument_id`, `source_id`, basis `PROVIDER_ADJUSTED`, horizon1/5/20/60/120, lookback1..1000, one to three unique model IDs B01/B02/B03, optional annualization1..1000 and expected source revision. Evaluation also requires ordered start/end dates and frequency1..120 sessions. Max period1100 calendar days,80 sampled origins,5000 input observations, one compute operation at a time,30 requests/minute, cooperative30-second server deadline and45-second client cancellation. Disconnects request cancellation. Repeatable-read canonical snapshots prevent mixed SQL revisions. Resource/source/cancellation errors are sanitized; no stack or caller secrets are echoed.

## 3. Real-data verification

Bounded checks used existing canonical cache only. No historical download, manual refresh, quote refresh, live-feed connection, account access or external Dhan request was made. Verification completed at2026-11-06T18:36:52Z (2026-11-07 00:06:52 IST). Each run used horizon5, lookback60 and all three models, with its actual execution time as cutoff.

| ETF | Available rows | Calendar-eligible rows | Older rows excluded | Origin | B01/B02/B03 | Scored historical origins |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| TATAGOLD | 250 | 250 | 0 | 2026-11-05 | AVAILABLE / AVAILABLE / AVAILABLE | 0 |
| TATSILV | 542 | 250 | 292 | 2026-11-05 | AVAILABLE / AVAILABLE / AVAILABLE | 0 |
| GOLDBEES | 250 | 250 | 0 | 2026-11-05 | AVAILABLE / AVAILABLE / AVAILABLE | 0 |
| SILVERBEES | 252 | 250 | 2 | 2026-11-05 | AVAILABLE / AVAILABLE / AVAILABLE | 0 |

All eligible histories cover2025-11-03..2026-11-05 with zero missing reviewed sessions. Available TATSILV history starts2024-08-30; SILVERBEES starts2025-10-30. Exclusion does not delete or modify those older canonical rows. All original provider event/publication times remain null; the last observation timestamp is explicitly unavailable. Actual first-seen and calendar-close proxy are separate evidence fields. Per-instrument execution cutoffs are preserved in the metadata-only receipt:

- TATAGOLD: `2026-11-06T18:36:51.257631+00:00`.
- TATSILV: `2026-11-06T18:36:51.496173+00:00`.
- GOLDBEES: `2026-11-06T18:36:51.735126+00:00`.
- SILVERBEES: `2026-11-06T18:36:52.029874+00:00`.

Each current forecast targets2026-11-12; all three outcomes are PENDING. Horizon20 is calendar-available to2026-12-04. Horizon1 targets the already completed2026-11-06 and is unavailable; horizons60/120 extend beyond reviewed2026 coverage and are unavailable. Horizons are anchored to the actual input origin, never silently shifted to today. Successful execution establishes deterministic conditional computation, not predictive accuracy.

Historical verification requested2026-08-11..2026-11-05, every5 reviewed sessions, lookback60, horizon5:12 sampled origins per ETF,36 model-cutoff exclusions per ETF, all `METADATA_NOT_AVAILABLE`, zero scored/pending forecasts, zero paired B01 samples, zero matured overlapping/disjoint windows. Source/calendar compilation evidence was not established at those past cutoffs; actual local first-seen times also do not establish historical publication availability. Each model reports12 failed/excluded cutoffs and null MAE/RMSE/return/direction/bias/volatility/benchmark metrics. No real forecast-versus-actual accuracy or winning model is demonstrated. Synthetic integration tests exercise valid point-in-time cutoffs, matured outcomes and populated metrics independently.

Deployed-browser verification passed real Gold B01/B02/B03, Silver B02, native endpoint chart, pending outcomes, zero-score/null-metric historical display, exclusion paging15->30, reopening immutable session forecasts,390px mobile containment and return to existing Technical Analytics. Provider/acquisition routes were explicitly blocked during this read-only browser check. No trace, screenshot or price-response artifact was saved for real verification. Owner UAT remains pending.

## 4. Verification results and failures resolved

| Check | Final actual result |
| --- | --- |
| Complete backend, including disposable PostgreSQL | **838 passed;0 failures/errors/skips** (801 previous +37 additional parameterized cases) |
| Python lint | Passed `ruff check backend scripts` |
| Frontend components | **41 passed** (33 previous +8 new) |
| Complete Chromium workflows | **9 passed;0 failures/errors/skips**, including existing native technical-chart interactions and the new synthetic forecasting flow |
| Production build | Passed after the final mobile containment correction |
| Container build/startup | Final API/UI images built with existing pinned base images/frozen dependency controls; deployed API/UI and database healthy |
| Windows / Linux Python dependency scans | 40 /31 packages;0 known vulnerabilities,0 skipped |
| npm full / production audits |0 known vulnerabilities |
| Configured-value credential checks | No configured credential matches in source, frontend assets or API logs; `.env` ignored/untracked/byte-unchanged; Dhan fields API-only; runtime credentials unchanged |
| API response checks | No configured secret values echoed in actual forecast responses; mocked auth/Origin/canary validation tests pass |
| Real market cache |1294 daily rows,1442 intraday candles and4 quotes preserved; complete canonical field, hash, identity, ingestion/event/publication and batch-evidence fingerprints match before/after RAM-only deployment |
| Market-data SQL persistence | Active `price_observations`, `import_rows`, `import_batches` counts remain `[0,0,0]`; no migration/new table |
| External Dhan requests |0 new requests in regression, deployment, local API verification and local real-browser verification; provider request counter preserved |
| Governance | Baseline/context, canonical ingestion/analytics/comparison, original NSE ingestion calendar, configuration, dependency locks, HEAD and all existing tags unchanged; staging empty |

Intermediate failures are retained rather than hidden. An unsupported Testing Library `exact` option blocked TypeScript and was removed from unit tests. An independent bias assertion had its expected sign wrong; the production calculation already returned the correct signed mean. API-inspection test and lint issues were corrected. The first full browser run had7passes/2failures: exact label selection stalled the new test, whose connected synthetic stream then interfered with the existing quote polling check. Accessible-role selectors and aborting that test's synthetic stream fixed isolation; the next run had8passes/1failure and exposed genuine forecast-grid mobile overflow. Local grid/field containment and waiting for responsive chart resize fixed it; the final complete browser suite passed9/9. No unrelated existing test was weakened.

Some earlier verification processes were slow under host memory pressure. Only ignored orchestration helpers extended test-process deadlines; application resource caps were not relaxed. Remaining nonfatal warnings: Plotly bundle chunk size, Starlette TestClient/httpx and Alembic path-separator deprecations, Node color-environment warning; a Windows synthetic SSE disconnect emitted a connection-reset warning in an intermediate browser run. No dependency finding was suppressed.

Ignored local evidence: `artifacts/backend-tests.xml`, `browser-tests.xml`, `package4-verification.json` (records the initial full run and browser failure), `package4-browser-verification.json` (final passing rerun), `package4-regression-preservation.json`, `package4-browser-preservation.json`, `package4-audit-summary.json`, `package4-security.json`, `package4-deployment-integrity.json`, `step5e-package4-deployment.json`, `package4-real-verification.json`, `package4-real-browser.json`, `package4-governance-review.json`. These contain synthetic test outputs or sanitized counts/status/dates/hashes, not raw Dhan responses/reconstructable real histories. No evidence artifact is proposed Git content.

## 5. Source qualification, calendar and remaining acceptance blockers

1. Actual source remains `TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED`: retrieval/private analysis/display are owner-authorized; storage=false. Provider timestamp/session conventions, daily finality, historical publication/availability, adjustment/revision vintages and total-return compatibility remain unqualified. Current results are conditional descriptive research, not outputs from a fully qualified source.
2. No defensible historical as-of availability archive exists for the selected cutoffs. Calendar/source evidence and recorded first-seen stamps cannot be backdated. Historical accuracy and real benchmark comparison remain blocked; extending price history alone would not fix this.
3. Forecast-only calendar extension reaches2026-12-31 and includes the officially confirmed Sunday2026-11-08 Muhurat date. Exact special-session timing remains unqualified; targets on that date fail explicitly and its internal completion bound is conservative day-end. No2027 calendar is invented. Original ingestion calendar still ends2026-11-06, so future provider acquisition can remain calendar-blocked until separately reviewed.
4. Full retention/derived-output/backup/redistribution rights remain unresolved; no persistent price/forecast ledger, ML archive or restart-safe forward tracking is authorized. Transient in-process runs can survive only while the process remains active and under capacity/expiry limits.
5. Real future targets have not matured. PENDING is the only observed real outcome state. Maturity, revision blocking and EVALUATED transitions are verified using explicitly synthetic fixtures, not fabricated real forward evidence.
6. Computational minima do not establish statistical support, calibration or skill. Long horizons need reviewed future calendars and much stronger independent evidence. No probabilities, confidence intervals, Kronos/model weights, ML training, scenarios or trading are implemented.
7. Owner UAT, source/retention qualification and applicable decision/sample-policy approvals remain open. No FRC status or requirements decision is silently promoted. Full VS-01 acceptance is not claimed.

Official evidence reviewed: [Dhan historical-data contract](https://dhanhq.co/docs/v2/historical-data/), [NSE2026 holiday circular CMTR71775](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf), [NSE holiday page](https://www.nseindia.com/resources/exchange-communication-holidays), [normal NSE market times](https://www.nseindia.com/static/market-data/market-timings). The official special-session timing PDF could not be retrieved; no third-party time was adopted. Current Dhan documentation did not establish a universal T-1 daily guarantee; refresh uses the existing local eligibility policy, not a newly asserted provider guarantee.

## 6. Traceability and implementation status

All referenced FRC items remain Proposed; bounded Package 4 implementation authority does not approve the entire extension.

| Trace | Implemented and verified | Partial / blocked / future |
| --- | --- | --- |
| FRC-001/002/003/005/015; REQ-02-011/012, REQ-03-001/002 | Explicit canonical real adapter, B01/B02/B03, exact arithmetic, availability filtering, source/calendar/identity gates | Fully qualified source, PIT vintage archive, unavailable horizons and daily finality qualification |
| FRC-004/010; REQ-06-001 | Versioned descriptors, IDs/fingerprints, immutable transient forecasts and process-scoped tracking | Persistent evidence registry/retention, restart-safe forward validation |
| FRC-009/011; REQ-06-003/005/018 | Chronological APIs, exclusion accounting, separate point/volatility metrics, signed bias, common-target B01 comparison; synthetic matured-case tests | Real historical samples/metrics and supported accuracy or skill claims blocked |
| FRC-012 | Working Forecasting Research UI, native endpoint markers, evidence, 15-row controls and mobile containment | Broader probabilistic/scenario visualization |
| FRC-006/007/008/013/014/016 | Unsupported probability/calibration fields remain explicit | Scenarios, calibration, external ML/Kronos, training and multi-factor integration not implemented |

## 7. Exact Package 4 files and preserved working tree

Package 4 touches **27 paths**: extends11 of the initial51 paths, modifies one additional tracked chart module, and adds15 new files. The other40 starting paths retain their exact pre-task bytes. Combined working tree: **67 files:19 modified +48 new**, none staged. Existing Package1/2/3 work is retained; the full combined list is in the local governance receipt. These lists are review scope, not a commit approval.

| Exact path | Change |
| --- | --- |
| `backend/app/main.py` | Register authenticated research service/routes and repeatable-read compute snapshots |
| `backend/app/forecast_contracts.py` | Versioned result evidence/count fields; synthetic guards retained |
| `backend/app/forecast_dataset.py` | Explicit real-contract eligibility branch; immutable context reuse |
| `backend/app/forecast_baselines.py` | Reuse unchanged math; conditional real outputs and truthful descriptors/evidence |
| `backend/app/forecast_evaluation.py` | Typed real replay, cancellation, special-target exclusion and metric-version evidence |
| `backend/app/forecast_metrics.py` | Signed price/return bias and metrics version |
| `backend/app/forecast_market_contracts.py` | New explicit conditional real contracts |
| `backend/app/forecast_market_adapter.py` | New pure canonical read adapter and provenance/calendar/availability gates |
| `backend/app/forecast_research_service.py` | New bounded orchestration, context/evaluation and RAM tracking |
| `backend/app/forecast_research_routes.py` | New authenticated compute-only HTTP seam |
| `backend/app/forecast_calendar_extension.json` | New forecast-only reviewed future-session manifest |
| `backend/tests/forecast_research_fixtures.py` | New explicitly synthetic canonical/PIT fixtures |
| `backend/tests/test_forecast_market_adapter.py` | New adapter/temporal/calendar/quality tests |
| `backend/tests/test_forecast_research_service.py` | New execution/evaluation/tracking/resource tests |
| `backend/tests/test_forecast_research_routes.py` | New auth/Origin/contracts/canary/API tests |
| `backend/tests/test_forecast_evaluation.py` | Update bounded architecture expectations for the authorized HTTP integration |
| `backend/tests/test_forecast_metrics.py` | Independent signed-bias reference assertions |
| `backend/tests/session_browser_app.py` | Synthetic-only forecast availability/calendar fixtures |
| `frontend/src/ForecastingResearch.tsx` | New working dashboard |
| `frontend/src/forecastTypes.ts` | New exact-string API types |
| `frontend/src/ForecastingResearch.test.tsx` | New eight component workflows |
| `frontend/src/ResearchDashboard.tsx` | Forecasting Research navigation |
| `frontend/src/ResearchChart.tsx` | Optional marker-only traces; existing default unchanged |
| `frontend/src/styles.css` | Forecast-view layout/mobile containment |
| `frontend/e2e/forecasting.spec.ts` | New isolated native browser workflow |
| `docs/03-design/FORECASTING_PACKAGE_4_DESIGN.md` | Scoped architecture and conservative qualification policy |
| `docs/04-planning/FORECASTING_PACKAGE_4_CHECKPOINT.md` | This implementation, evidence, blockers, exact scope and UAT checkpoint |

Excluded: `.env`, credentials, account/portfolio identifiers, market exports, raw provider responses, backup files, generated builds, test reports/traces, ignored verification helpers and local metadata artifacts. Existing requirements tag remains `5eeed03536e43ded7077ac086b97cb05f2e5b73e`. No release tag or repository operation was performed.

## 8. Owner UAT and recommended next authorization

1. Open the running local workspace at `http://127.0.0.1:5173`, unlock with the existing local application token, choose an ETF, the transient Dhan source and Provider adjusted basis. Never paste provider credentials into the browser.
2. Choose Research dashboard -> Forecasting Research. Confirm REAL_MARKET/conditional labels, source limitations, actual first-seen/null provider time, available versus eligible counts and horizon reasons.
3. Select horizon5/lookback60/B01+B02+B03 and Run Forecast. Inspect endpoint-only chart and evidence. B01/B02 have point estimates; B03 has volatility only. Change to TATSILV/SILVERBEES and repeat. Values are conditional research outputs, not trade instructions.
4. Run Historical Evaluation over the default history. Current real cache should show zero scored samples, null metrics and explicit excluded cutoffs. Inspect15 rows, Show more and source/calendar limitations. A populated accuracy table is not expected with current availability evidence.
5. Check forecast outcomes: future targets remain PENDING. Use Open session forecast to reopen the original immutable run; backend restart/expiry/eviction loses it. Synthetic automated tests, not owner assumptions, establish matured-state mechanics.
6. Verify existing Technical Analytics and daily/intraday views still work; test narrow-screen navigation. Manual Refresh finalized daily data is an explicit acquisition action governed by existing standing provider authorization/calendar/rate policy. It was not invoked during Package 4 verification; do not expect it to overcome missing calendar/source qualification.

Recommended next package: qualify daily finality/timestamp/adjustment semantics, review and extend the acquisition/forecast calendars including special-session times, establish defensible point-in-time/vintage evidence and resolve price/derived-output retention/backup rights. Then separately authorize restart-safe forward evidence collection and a minimum-support evaluation policy. Complete owner UAT and compare baselines only after enough independently eligible outcomes mature. External ML/Kronos/training should wait for those gates. No next package is started here.
