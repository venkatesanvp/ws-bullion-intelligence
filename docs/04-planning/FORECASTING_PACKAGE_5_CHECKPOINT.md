# Package 5 - market-data qualification and historical evaluation checkpoint

Date:2026-11-07 IST. Base HEAD/main remains `fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9`. No stage/commit/tag/push. REQ-BL-1.0, the decision register, FRC-001..016 Proposed statuses and `requirements-v1.0` remain unchanged.

**Implemented and locally deployed:** separated strict, conditional and synthetic evaluation, qualification evidence and usable real-data retrospective baseline metrics. **Still blocked:** strict real historical accuracy evidence, full source/adjustment/vintage/finality qualification, retention rights and production/release acceptance. Conditional replay is not a substitute for those qualifications.

Design: [Package5 scoped modes](../03-design/FORECASTING_PACKAGE_5_DESIGN.md). Actual source evidence/root cause: [four-ETF qualification matrix](FORECASTING_PACKAGE_5_QUALIFICATION.md). Package4 checkpoint is preserved as historical evidence, not silently rewritten.

## 1. Root cause and mode semantics

Zero scores were caused first by `METADATA_NOT_AVAILABLE`: present source/calendar review times were after every sampled historical cutoff. Independently, local first-seen times cannot establish earlier historical provider availability. OHLCV arithmetic was not the failing rule. Both gates remain valid for strict PIT. Requiring today's calendar compilation to be historically available is unnecessarily restrictive only when defining explicitly retrospective structural research; the answer is a separate mode, never fabricated earlier metadata.

| Mode | Input/eligibility | Interpretation |
| --- | --- | --- |
| STRICT_POINT_IN_TIME | Default real-source mode. Existing metadata-known-at, recorded availability, complete contiguous daily context, quality/calendar/vintage controls unchanged | Evidence-based local as-of reconstruction; source qualification still separate. Current real verification scores0; no false accuracy |
| CONDITIONAL_HISTORICAL_REPLAY | Explicit selection plus boolean acknowledgement and `FIXED_RETRIEVED_VINTAGE_V1`. As-retrieved provider-adjusted snapshot at actual assessment; context sessions through origin only; actual stamps retained | Conditional fixed-vintage numerical replay, not verified provider historical availability, original adjustment vintage, economic PIT purity or live predictive performance |
| SYNTHETIC | Only explicitly synthetic sources; existing deterministic evaluator | Arithmetic/testing evidence only; no substitution for real market data |

The separate ReplaySnapshot validator preserves actual source review/first-seen/publication metadata. It allows those actual times after a simulated historical cutoff only if they precede actual assessment. It never invents availability or forecast issuance times. Only input dates through origin reach the model; outcome prices enter later scoring. Changing future target values does not change an earlier forecast ID, prediction or context fingerprint (independently tested). However, provider-adjusted input values themselves may embed later actions/revisions; unknown adjustment methodology prevents an economic no-lookahead guarantee. This limitation is prominent in every conditional result and acknowledgement.

Missing/duplicate/malformed OHLCV, unsupported or mixed basis, unavailable-at-assessment records, current/provisional candles, incomplete contexts/targets, unsupported calendars/special-session timing and declared action/revision-break crossings remain excluded. No filling, rounding inputs, unadjusting, corporate-action inference or global fitted transform. A declared-break-free profile is not evidence that no unknown action occurred.

B01/B02/B03 equations, Decimal34, precision/bounds, sample variance, simple-return compounding and wire12 conventions are unchanged. AST comparisons against the pre-task recovery ZIP prove unchanged arithmetic kernels and the prediction Decimal block; independent Fraction/100-digit tests verify outputs and metrics. B03 remains volatility only, using the existing future realized-volatility proxy. Price MAE/RMSE, return MAE, three-class direction, signed price/return bias and B01 paired comparisons remain separate from B03 proxy MAE/RMSE. No calibration/probability/winner/strategy return is fabricated.

## 2. Real canonical verification

No new Dhan historical/quote/profile/feed request was made. Existing RAM-only canonical data was used. Verification receipt recorded2026-11-06T19:08:32Z (2026-11-07 00:38:32 IST). All four ETFs had250 eligible daily candidates covering2025-11-03..2026-11-05; actual source status remained TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED. Available totals remain250/542/250/252, respectively;292 older TATSILV rows and2 older SILVERBEES rows remain outside reviewed calendar coverage, not deleted.

Common evaluation-origin period:2026-01-30..2026-10-07, sampled every5 sessions, lookback60, B01/B02/B03. Origins are the same within each mode/horizon/instrument comparison. The earlier period end leaves actual outcomes available even at20sessions; no extra data download was needed.

| ETF | Available / eligible | Strict h5 scored / excluded model cutoffs | Conditional h1 scored | Conditional h5 scored | Conditional h20 scored |
| --- | --- | --- | ---: | ---: | ---: |
| TATAGOLD | 250 / 250 | 0 / 102 | 34 | 34 | 34 |
| TATSILV | 542 / 250 | 0 / 102 | 34 | 34 | 34 |
| GOLDBEES | 250 / 250 | 0 / 102 | 34 | 34 | 34 |
| SILVERBEES | 252 / 250 | 0 / 102 | 34 | 34 | 34 |

Strict exclusions are METADATA_NOT_AVAILABLE,102 model-cutoff exclusions per ETF (34 origins x3 models). No strict metrics or paired samples are invented. Conditional verification has34scored origins per model/ETF/horizon, zero exclusions/pending/failed/unavailable outcomes in this deliberately eligible period, and34common B01/B02 benchmark pairs. Across all12 instrument/horizon combinations,1224 model outcomes were computed transiently; that is not1224 independent samples.

Every ETF/horizon/model exposes MAE/RMSE, return MAE, directional fraction and signed bias where supported; B03 has null point/directional metrics and separate volatility-proxy errors. Aggregate loss summaries are in ignored `artifacts/package5-real-verification.json` and working dashboard responses. The receipt contains no per-date real prices, prediction paths or raw provider responses; it is not a persistent forecast ledger. Below are compact error summaries (backend strings preserved; INR per ETF unit for point loss, return-fraction units for volatility):

| ETF | h | B01 price MAE | B01 price RMSE | B02 price MAE | B02 price RMSE | B03 proxy MAE | B03 proxy RMSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TATAGOLD | 1 | 0.170000000000 | 0.295097192364 | 0.178302882341 | 0.311133163361 | 0.014421769939 | 0.018112874298 |
| TATAGOLD | 5 | 0.314705882353 | 0.430997475085 | 0.359869316411 | 0.505054391127 | 0.022277592583 | 0.028631487525 |
| TATAGOLD | 20 | 0.628823529412 | 0.749866654813 | 0.935246398225 | 1.142112175134 | 0.028806568870 | 0.040026635425 |
| TATSILV | 1 | 0.558823529412 | 0.872491361832 | 0.588818736375 | 0.948432887329 | 0.023767095408 | 0.029665610097 |
| TATSILV | 5 | 0.970882352941 | 1.480235474113 | 1.126490873921 | 1.872150349496 | 0.039896839394 | 0.056424622506 |
| TATSILV | 20 | 1.665588235294 | 2.052329379596 | 2.875750737574 | 4.050339975816 | 0.059935837889 | 0.078791883419 |
| GOLDBEES | 1 | 1.482941176471 | 2.632490433478 | 1.548455169835 | 2.761433646285 | 0.015204327549 | 0.019225902600 |
| GOLDBEES | 5 | 2.620588235294 | 3.593224833751 | 2.985483211735 | 4.133078827871 | 0.022594709989 | 0.029086743039 |
| GOLDBEES | 20 | 5.325294117647 | 6.429709992545 | 7.802452344366 | 9.474445046399 | 0.027776607271 | 0.039478502062 |
| SILVERBEES | 1 | 5.571764705882 | 9.024499008418 | 5.830180934547 | 9.718820754557 | 0.023897496218 | 0.030457300070 |
| SILVERBEES | 5 | 9.228529411765 | 12.993975640318 | 10.603818999777 | 16.343014938798 | 0.037589901079 | 0.052018414549 |
| SILVERBEES | 20 | 16.194411764706 | 19.347167067284 | 27.435877053532 | 36.944463500801 | 0.054907688991 | 0.072733918589 |

These are descriptive error magnitudes, not performance/ranking recommendations. Price loss scales differ across ETFs and must not be compared as a model leaderboard. Mode, horizon, origin period, basis, policy and input availability are required comparison dimensions. Return errors/direction/bias and support counts are returned by the API/dashboard and retained as aggregate summaries in the local receipt. No real prices or individual outcomes are placed in this document.

For h1 and h5, each ETF has0overlapping target-window pairs and34disjoint windows. For h20, each has96overlap pairs and only9maximally disjoint windows; errors are dependent. Temporal disjointness does not prove statistical independence. The engine's legacy BELOW_PROPOSED_INDEPENDENT_EVALUATION_SUPPORT warning uses disjoint-window count as a support proxy, not an independence test. All real lookbacks60 remain below the Proposed253-close research support floor. No significance, forecast reliability or winning model is declared. Actual60/120 real evaluations were not run; the engine accepts them only with sufficient contiguous input/calendar/outcome support and reports insufficiency otherwise. Long-horizon mechanics are verified with synthetic fixtures.

## 3. API, UI and resource behavior

Existing authenticated read-only computation endpoints remain unchanged:

- GET `/api/v1/research/forecasts/context`: now includes eight-dimension qualification summary, supported evaluation modes, policy and assumptions.
- POST `/api/v1/research/forecasts/evaluate`: adds `evaluation_mode`, strict boolean `acknowledge_replay_assumptions` and optional `replay_policy`. Default strict; conditional requires true and exact policy; synthetic/real source mismatch is rejected. Unknown/credential-bearing values are sanitized, not echoed.
- POST `/api/v1/research/forecasts/run` and GET `/runs`, `/runs/{run_id}`: current forecast math, values, evidence and transient tracking remain unchanged.

Evaluation evidence includes explicit mode on experiments and outcome rows, assessment/execution versus historical cutoff, policy, assumptions, source qualification and engine identity. Direct synthetic results are SYNTHETIC; strict engine identity is `walk-forward-strict-v3`; conditional engine is `walk-forward-conditional-v1`, result contract `forecast-conditional-replay-v1`. Synthetic/current result contracts and model version `baseline-simple-v1` are unchanged. Mode participates in semantic experiment identity; comparison never pools modes.

Forecasting Research exposes mode selection, qualification matrix, unselected conditional acknowledgement, assumptions, mode-labeled forecasts-versus-actual, metrics and exclusions. Mode/source/instrument changes reset acknowledgement and clear stale evaluation evidence; mode changes cancel an in-flight request. Historical horizon is separate from current forecast horizon, allowing1-session historical scoring even when the current1-session target has already passed. Historical horizon options use numerical history support; per-origin context/target/calendar gates still apply. Existing15-row paging and native endpoint charts remain. Current forecast display and Technical Analytics remain available.

Resource controls unchanged: lookback1..1000, input5000, max80origins/1100calendar days, up to3models, frequency1..120, single compute gate,30calls/minute, cooperative30-second server deadline and45-second client cancellation. Read-only repeatable-read canonical snapshots, no SQL/file writes/provider acquisition inside evaluation. No worker, GPU, new dependency, trained model, automated refresh or trading/account capability.

## 4. Verification and recovery

| Check | Final actual result |
| --- | --- |
| Full backend + isolated PostgreSQL |874passed;0failures/errors/skips (838previous +36new parameterized/API cases) |
| Frontend |45passed;0failures/skips (41previous +4new mode/horizon checks) |
| Complete Chromium workflows |9passed;0failures/errors/skips, including synthetic mode, existing technical/native charts and prior market workflows |
| Python lint |Passed |
| Production build |Passed after final historical-horizon change |
| Dependency audits |Python40development/31Linux-runtime packages:0known vulnerabilities,0skipped; npm full/production0known vulnerabilities |
| Containers |API/UI built and started with existing pinned bases/frozen dependencies; existing31-package runtime matches audit |
| Current forecast parity |All four ETFs' current B01/B02/B03 numerical outputs/counts/quality/warnings/original availability evidence hash-identical before and after deployment; request/creation times remain actual |
| Canonical integrity |1294daily rows,1442intraday candles,4quotes retained; all canonical field and batch/provenance/hash/first-seen evidence digests equal across RAM-only transfer |
| Security |Configured-value source/assets/log/API-response checks pass; credentials API-only, `.env` ignored/untracked/byte-unchanged, loopback ports, default Dhan flag unchanged |
| Market SQL |price_observations/import_rows/import_batches remain `[0,0,0]`; no new table or migration |
| External market requests |0new Dhan requests through regression/deployment/local real evaluation/browser verification |
| Governance |No Git mutation; original requirements/context/decisions/tags/configuration/locks/calendar/canonical production analytics unchanged |

Initial independent replay testing found an incomplete candle escaped as a Pydantic validation exception rather than an exclusion. It now becomes an explicit INCOMPLETE_CANDLE failure; no quality relaxation. Initial full regression had873passes/1failure: an existing Package2 synthetic test hardcoded November6 but used the real current day after midnight November7. Only that test now pins its declared fixture clock; application time handling and analytics were not changed. Full backend rerun passed874/874. Frontend subsequently gained the separate historical horizon; final frontend45/build/browser9 were rerun and passed. No failed/skipped test is hidden. Nonfatal existing Plotly large-chunk, Starlette/httpx, Alembic path-separator and Node color warnings remain.

Before implementation all67 existing changes were scanned/read/hashed. Ignored source-only `artifacts/package5-preimplementation-source.zip` contains those exact bytes and hash manifest; its CRC and SHA-256 were verified. `.env`, market data, exports, builds and test artifacts are excluded. Recovery requires comparing the manifest and selectively restoring only the intended files; no destructive blanket reset is authorized. Active market data crossed deployment in RAM only using the existing bridge; no backup/price file was created.

Local ignored evidence: package5-starting-scope/start-data metadata, source-only ZIP, initial/full/frontend verification reports, backend-tests.xml/browser-tests.xml, audit/security receipts, deployment-integrity, real-verification, real-browser, governance-review and final-verification. Synthetic test traces are ignored; real-browser checks save no trace/screenshot/price response. Source-only recovery is not market-data retention permission. Final real-browser verification passed Gold/Silver current baselines, pending tracking, strict0/null metrics/exclusion paging, explicit conditional acknowledgement, historical1-session scoring, all8qualification dimensions, clearing results across modes, session reopening, mobile containment and Technical Analytics navigation. Its initial5-second readiness assertion failed; direct local context returned200 with a valid5-session target, and the rerun passed using a45-second assertion budget aligned with the unchanged client request timeout. No production timeout or quality control was relaxed.

RAM restoration may remap ephemeral catalog instrument/source UUIDs. Integrity comparison resolves by verified ISIN; canonical observation IDs/hashes/batch references, values, first-seen/event/publication fields and available source/batch evidence are retained. Forecast creation/cutoff times remain actual and are not expected to equal pre-deployment timestamps.

## 5. Exact proposed Git scope

Package5 touches15paths:9of the existing67, plus6new paths. Other58starting paths retain exact bytes. Combined tree:73uncommitted files (19modified54new), staging empty. Existing Package1..4 work is preserved; no commit/tag/push is authorized.

| Exact path | Package5 change |
| --- | --- |
| `backend/app/forecast_baselines.py` | Explicit replay type branch/evidence; unchanged arithmetic/current path |
| `backend/app/forecast_evaluation.py` | Three mode identities, conditional context branch, break exclusion, same evaluator/metrics |
| `backend/app/forecast_research_service.py` | Mode/ACK/source gates and qualification response |
| `backend/app/forecast_replay.py` | New separate fixed-vintage contracts and context eligibility |
| `backend/app/forecast_qualification.py` | New pure eight-dimension qualification summary |
| `backend/tests/test_forecast_replay.py` |34independent parameterized mode/leakage/quality/numeric tests |
| `backend/tests/test_forecast_research_routes.py` |Two API mode/ACK/canary tests; clarified strict result classification |
| `backend/tests/test_technical_research.py` |Deterministic clock for existing fixed-date synthetic assertion only |
| `frontend/src/ForecastingResearch.tsx` |Mode/ACK/qualification/evidence and independent historical-horizon controls |
| `frontend/src/forecastTypes.ts` |Mode and qualification API types |
| `frontend/src/ForecastingResearch.test.tsx` |Four new mode/horizon state tests |
| `frontend/e2e/forecasting.spec.ts` |Explicit synthetic mode assertion in existing native workflow |
| `docs/03-design/FORECASTING_PACKAGE_5_DESIGN.md` |Scoped design and review/gap decisions |
| `docs/04-planning/FORECASTING_PACKAGE_5_QUALIFICATION.md` |Actual four-ETF evidence matrix and root cause |
| `docs/04-planning/FORECASTING_PACKAGE_5_CHECKPOINT.md` |This actual implementation/verification/UAT checkpoint |

Requirements trace: FRC-001/003/005 adapter/model seams and deterministic baselines; FRC-009/011/015 and REQ-06-003/005/018 for separated evaluation/common targets/leakage evidence; FRC-010 for transient identity/evidence; FRC-012 for mode-aware charts/tables. FRC-006/007/008/013/014/016 probabilistic/scenario/calibration/ML/training/multi-factor work is not implemented. All16FRC statuses remain Proposed. Baseline/tag `requirements-v1.0` remains `5eeed03536e43ded7077ac086b97cb05f2e5b73e`.

## 6. Owner UAT and remaining authorization

1. Open `http://127.0.0.1:5173`, unlock with the existing local application token, choose a real ETF/transient Dhan source/Provider adjusted basis, then Research dashboard -> Forecasting Research. Provider credentials remain backend-only.
2. Expand Historical data qualification. Verify null/unverified provider event/publication evidence, actual local first-seen, unqualified adjustments/revisions/rights and calendar limits for each of the four ETFs.
3. Leave Strict point in time selected and run historical evaluation. Expect0eligible scored origins under current actual availability evidence, null metrics and explicit exclusions; this is correct.
4. Select Conditional historical replay. Confirm evaluation is disabled until acknowledgement. Read that current provider-adjusted vintages may contain later information, then acknowledge only for private retrospective research. Set historical horizon1/5/20 independently of current forecast horizon, lookback60, frequency5 and origin period2026-01-30..2026-10-07. Run: expect34common scored origins per model/horizon for the reviewed cache.
5. Inspect actual-vs-forecast endpoints, MAE/RMSE/return/direction/bias, B01 paired counts and separate B03 proxy metrics. Review96overlap pairs/9disjoint windows at20sessions. Use15-row paging. Do not infer a winner or compare price losses across ETFs.
6. Switch back to strict: prior conditional metrics must disappear. Return to conditional: acknowledgement must be unchecked. Synthetic mode must be unavailable for the real source. Cancel/load/error/insufficient-context states remain explicit.
7. Run current baselines and inspect pending outcome tracking and existing Technical Analytics. Do not invoke a provider refresh for this UAT; all verification uses the existing cache. Restart/expiry loses transient tracking and the market cache unless an authorized RAM transfer is used. Owner UAT sign-off remains pending.

Remaining blockers: strict historical publication/local-availability vintage evidence; independently qualified daily timestamps/finality and adjustment/action/revision semantics; broader reviewed acquisition/forecast calendars and special-session timing; adequate disjoint support/calibration/forward evidence; explicit retention/derived-history/backup/redistribution rights. No full source, Package5 strict-performance or VS-01 release acceptance is declared.

Recommended next package: prospective PIT evidence and source-vintage qualification, with rights and retention decisions first. Define an approved publication/finality/action/revision policy, calendar maintenance and minimum support; then separately authorize durable forward forecast/outcome evidence if permitted. Additional historical downloads alone will not fix historical availability. Keep Kronos/new ML/training/trading out of scope until those gates are satisfied. No next increment is started here.
