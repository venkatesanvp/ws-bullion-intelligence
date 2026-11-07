# Package 3 - offline forecasting foundation checkpoint

Date: 2026-11-06. Base HEAD/main: `fd5eee5fe4c36b98154c9750e2ff9e9ce437ded9`. **Bounded offline synthetic implementation; review checkpoint, not production forecasting acceptance.** No stage/commit/tag/push. All16 FRC requirements retain Proposed status; REQ-BL-1.0, requirements-v1.0 and existing decisions remain unchanged. Owner UAT for Package 2 is still pending.

## 1. Implemented scope

- Strict immutable provider-neutral dataset/request/snapshot/model/result/evidence contracts with explicit identity, daily timeframe, observation versus availability versus cutoff, source metadata, quality, versioned calendar and deterministic SHA-256 fingerprints.
- Point-in-time dataset builder accepts only explicitly synthetic datasets; selected contexts contain contiguous qualified completed sessions available by cutoff. Rejects gaps, duplicates/order errors, missing publication availability, incomplete bars, unsupported calendar/basis/vintage, stale origins and insufficient lookback. No silent fill, rounding of inputs, guessed holidays or corporate-action adjustment.
- Three deterministic baseline descriptors/implementations: B01 last value, B02 historical simple-return drift, B03 sample return volatility. Explicit model/config/version/capabilities, computational minima and unsupported fields.
- Chronological walk-forward evaluator with explicit per-origin cutoff, separate outcome assessment cutoff, model configuration, reproducible input manifests, complete-path outcome maturity, pending/unavailable/failed counts and overlap policy.
- Independently checked price MAE/RMSE, return MAE, three-class directional hit rate, realized-volatility-proxy MAE/RMSE and same-target B01-relative improvement. Unsupported price/probabilistic metrics are null with reasons.
- Immutable transient experiment/forecast/outcome evidence, semantic experiment/forecast IDs separate from execution/evidence IDs, actual execution timestamp distinct from historical cutoff. No persistent ledger.
- Explicit synthetic-only CLI demonstration. No user-facing forecasting feature, HTTP endpoint, real-data adapter, model loader, ML package, database migration, provider or trading integration added.

Architecture/contracts/formulas/bounds/operating instructions: [scoped Package 3 design](../03-design/FORECASTING_PACKAGE_3_CONTRACTS.md). It supplements the historical [foundation proposal](../03-design/FORECASTING_FOUNDATION_PROPOSAL.md) without rewriting its Proposed decisions. Dataset validation is stricter than current market ingestion because real source publication/vintage rights remain unqualified; it is a separate offline contract, not a change to canonical OHLCV.

## 2. Mathematical conventions

Let L be requested closes, n=L-1 completed one-session returns r_i=C_i/C_(i-1)-1, and h one of1/5/20/60/120 explicitly listed trading sessions. An origin is the latest completed calendar session at cutoff; every context row must already be available. A future session grid is required for forecast targets; future observed prices are never required to form a forecast. Outcome scoring waits for complete qualified target-path availability at the separate assessment cutoff.

| Model / measure | Exact implementation convention |
| --- | --- |
| B01 | Price=C_origin exactly; return0. Minimum1 close; no probability or calibrated interval |
| B02 | Mean simple one-session return mu=sum(r)/n; predicted return=(1+mu)^h-1; price=C_origin*(1+mu)^h. Minimum2 closes; no log-return substitution or fitted full-dataset mean |
| B03 | Sample centered variance=sum((r-mean(r))^2)/(n-1); sigma=sqrt(variance). Minimum3 closes/two returns; zero variance is valid. h-session sigma=sigma*sqrt(h) under explicit IID/no-serial-correlation scaling assumption. Optional annualization uses explicitly configured sessions/year (demo252); no inferred calendar-day annualization, point path, probability or interval |
| Price MAE/RMSE | Mean absolute price error and sqrt(mean squared price error), same synthetic instrument/currency/target/basis |
| Return MAE / direction | Mean absolute simple-return error; exact sign classes -1/0/+1, zero counts/confusion cells disclosed. B01 zero return is not an up prediction |
| Volatility proxy error | Compare h-session sigma with RV=sqrt(sum(future one-session r^2)); RV includes drift and is not observed latent volatility. Report descriptive proxy MAE/RMSE only |
| Paired B01 comparison | Match exact instrument/origin/target, require identical actual/reference prices; price MAE reduction=baseline-model; relative improvement=1-loss_model/loss_B01. Zero benchmark loss -> unavailable ratio; negative improvement allowed. B03 has no supported B01 price comparison |

Local Decimal precision34, ROUND_HALF_EVEN, exponent bounds-96..96 and trapped underflow; no binary-float financial math. B01 preserves the observed last price exactly; derived outputs use12-place fixed-decimal strings. Intermediate calculations remain unquantized. Unrepresentable compounding/quantization or nonpositive rounded point forecasts fail NUMERIC_UNSUPPORTED, never clipping to an invented price. A two-pass centered variance avoids subtracting nearly equal large second moments. Independent references use exact Fractions and separate100-digit square-root calculations.

Computational minima1/2/3 do not adopt the earlier Proposed253-close research/evaluation/calibration floors. Short B02/B03 windows are labeled below proposed support; all output remains synthetic research. No significance, calibrated distribution, predictive capability or profitable strategy is established. Overlapping evaluation windows are dependent; the evaluator reports actual overlap pairs and maximum disjoint windows, or rejects them under REQUIRE_NONOVERLAPPING. There is no learned transform/tuning/target-label fitting; future fitted-model purge/embargo protocols remain a separate scope.

## 3. Verification results

| Check | Actual final result |
| --- | --- |
| New forecasting tests | **126 passed**, independent arithmetic/calendar/PIT/metrics/replay/isolation tests; `artifacts/package3-focused-tests.xml` |
| Full backend + isolated PostgreSQL | **801 passed, 0 failed/errors/skips**; includes the existing675 and new126; migrations/integrity/concurrency tests use disposable test DB only |
| Python lint | `ruff check backend scripts` passed |
| Frontend | **33 passed**, six files; no frontend source changes in Package 3 |
| Chromium workflows | **8 passed, 0 failures/skips** against real FastAPI/disposable PostgreSQL and explicitly mocked synthetic provider/feed; existing daily/intraday/live-feed/browser flows and native chart interactions preserved |
| Production build | Passed; preexisting large Plotly chunk warning remains; no suppression or library replacement |
| Local synthetic CLI | Passed;60 forecasts, zero exclusions,20 matured disjoint artificial origins across B01/B02/B03. Actual execution time recorded, no retrospective creation-time claim |
| Offline container | Updated backend image built; same demo passed with `--network none`, no volumes/ports/credentials; installed packages match freshly audited runtime. Active API process not restarted |
| Existing application startup | UI restarted after browser tests, API kept healthy; local ready endpoints verified. No new online forecasting component registered |
| Dependency scans | Windows Python40/Linux runtime31 packages: **0 known vulnerabilities, 0 skipped**; npm full/production **0 known vulnerabilities**. No dependency/lockfile changes introduced by Package 3 |
| Credential checks | Exact configured-value checks across repository/frontend assets/API logs; `.env` ignored/untracked/byte-unchanged, API-only credentials, no source secrets or tokens |
| Real data preservation | **1294 daily rows** and complete available canonical/provenance fingerprint unchanged; **1442 intraday candles** and fingerprint unchanged;4 cached quotes retained. No real prices supplied to forecasting |
| External market requests | **0** new Dhan REST requests; no live feed opened by Package 3; no token exchange/account/trading action |
| PostgreSQL market persistence | Active application price_observations/import_rows/import_batches counts remain **[0,0,0]**; no restricted payload storage or new table |
| Governance/scope | Starting38 files retain their exact bytes; baseline/context/canonical analytics and all existing tags unchanged; staging empty; HEAD unchanged |

The synthetic calendar intentionally omits artificial weekday dates. Its sessions are not verified NSE dates; forecast values/metrics are deterministic test outputs, not real-market forecasts. Existing real-cache snapshots are inspected in RAM only; ignored receipts contain counts/hashes, not raw prices or responses. No raw Dhan response, market-data export or backup was produced. Synthetic pytest/browser artifacts remain ignored.

Initial lint reported compressed one-line formatting; the new files were formatted, then lint and all tests passed. The sandbox initially blocked launching the linter executable; its authorized escalated rerun passed. Focused runs had no failed tests. Final numeric-hardening changes were followed by a complete rerun and updated container smoke test. No failures/skips are hidden. Nonfatal existing warnings: Starlette TestClient/httpx deprecation, Alembic path_separator deprecation, Plotly chunk size and Node color-environment warnings; none changes the result.

Evidence: `artifacts/verification.json`, `backend-tests.xml`, `browser-tests.xml`, `package3-focused-tests.xml`, `package3-regression-preservation.json`, `package3-container-verification.json`, `package3-audit-summary.json`, `package3-security.json`, and `package3-governance-review.json`. These are ignored local evidence, not proposed commit contents.

## 4. Requirements traceability and status

| Requirement / existing obligation | Implemented bounded portion / evidence | Still outside scope |
| --- | --- | --- |
| FRC-001/002/003; REQ-02-011/012, REQ-03-001/002 | Immutable request/snapshot/model seam, daily calendar horizons and availability filtering; contract/dataset tests | Real provider-to-forecast adapter, real source/calendar qualification and broader timeframes |
| FRC-004/005; REQ-06-002 | Static versioned B01/B02/B03 descriptors, explicit simple-return/sample-variance contracts; independent Fraction/high-precision vectors | Production model registry/lifecycle promotion, fitting or external model |
| FRC-006/008 | Unsupported probability/interval/calibration fields explicitly unavailable; capability and rejection tests | Distribution/scenario/calibration engine, CRPS/coverage/calibration scoring |
| FRC-009/015; REQ-06-003/005/018 | Synthetic chronological cutoff snapshots, delayed publication/maturity, no future input, separate historical replay classification | Licensed PIT archives, fitted-model tuning/purging/embargo, real OOS/forward paper evidence |
| FRC-010; REQ-06-001 | Transient immutable experiment/forecast/outcome/config/fingerprint/time contracts and replay tests | Persistent ledger, real-data/derived-output retention or backups |
| FRC-011 | Descriptive same-target metrics and paired B01 comparisons per synthetic instrument/horizon | Multi-instrument/regime leaderboards, statistically supported skill/confidence conclusions |
| FRC-013 | Provider-neutral Protocol and explicit output capability seams | Kronos/external adapter, weights/tokenizer, loader, inference/training dependencies |
| FRC-007/012/014/016 | Existing proposal only | Scenario generation, forecast visualization, fine-tuning and multi-factor data integration |

All16 FRC statuses remain **Proposed**; this implementation does not assert full satisfaction/approval of those requirements. REQ-06-006 evidence/business thresholds remain Open. Package 3 authorizes only the bounded behavior described here. D-03/D-09/D-12/ADR-01/06 boundaries are preserved; AI advice/trading/account functionality is absent.

## 5. Limitations and open decisions

1. Synthetic-only input guard is enforced; no real-market forecasting accuracy is measured. Actual Dhan histories/availability/vintages, adjustment/finality semantics and rights remain unqualified for this path.
2. Daily1d only, explicit calendar coverage and five horizons; no guessed weekdays as real NSE sessions, no intraday forecast, no adaptive schedule or source fetch. Unknown/late context is unavailable rather than silently choosing an older origin.
3. Single immutable declared adjustment vintage; no corporate-action computation/revision store. Raw windows crossing known actions fail; accepted post-action segments do not prove broader total-return compatibility.
4. Drift/volatility are simple descriptive extrapolation assumptions. IID scaling, estimation-window length, computational minima and annualization are disclosed, not market guarantees. Outputs are finite precision with bounded unsupported cases.
5. Overlap counts are not uncertainty estimates. No nested tuning, trained model, calibration, confidence intervals or empirical skill-release thresholds. Proper long-horizon support requires more independent history than current real ETF samples provide.
6. Evidence is in memory, not a persistent origin-time ledger or real forward evidence. Execution timestamps are actual replay execution, never passed off as historical forecast issuance. Rights for prices, derived-output storage/backups/training still require qualification before real-data persistence.
7. Probability/interval/scenario/model-adapter capabilities require future reviewed extensions. No Kronos, model weights, PyTorch, stochastic inference or training is present.
8. Owner review of Package 2 UAT and Package 3 contracts/numeric/sample policies remains pending. No VS-01/R1 release acceptance, production prediction or tag is declared.

## 6. Exact new files and preserved working tree

**Package 3 adds13 files**, all new. The earlier38 files are preserved byte-for-byte. Combined working tree: **51 files:18 modified and33 new**; none staged. Existing requirements/context, configuration, Compose, runtime registration, ingestion/indicator sources and lockfiles have no Package 3 changes. No `.env`, credentials, builds, backups or test artifacts are proposed Git content.

| Exact new path | Purpose |
| --- | --- |
| `backend/app/forecast_contracts.py` | Canonical synthetic forecasting schemas, validation, fingerprints, model Protocol |
| `backend/app/forecast_dataset.py` | Qualified as-of context and visible-assessment fingerprint |
| `backend/app/forecast_baselines.py` | B01/B02/B03 descriptors/configuration/Decimal calculations |
| `backend/app/forecast_metrics.py` | Typed descriptive metrics and paired B01 comparison |
| `backend/app/forecast_evaluation.py` | Chronological evaluation, outcome maturity, overlap and transient evidence |
| `backend/app/forecast_demo.py` | Explicit synthetic-only runnable demonstration |
| `backend/tests/forecast_fixtures.py` | Artificial calendar and deterministic test observations |
| `backend/tests/test_forecast_dataset.py` | Dataset/calendar/PIT/quality/adjustment/contract cases |
| `backend/tests/test_forecast_baselines.py` | Independent exact-rational/high-precision baseline/numeric cases |
| `backend/tests/test_forecast_metrics.py` | Independent metrics/zero-denominator/invalid-encoding cases |
| `backend/tests/test_forecast_evaluation.py` | Chronology/maturity/overlap/reproducibility/no-I/O cases |
| `docs/03-design/FORECASTING_PACKAGE_3_CONTRACTS.md` | Scoped mathematical/architecture/contract and operating update |
| `docs/04-planning/FORECASTING_PACKAGE_3_CHECKPOINT.md` | This checkpoint, actual evidence, scope and next review |

The prior38 paths are enumerated in [Package 2 checkpoint](TECHNICAL_PACKAGE_2_CHECKPOINT.md#8-git-review-scope). Byte digests and tag/HEAD/env fingerprints are captured in ignored `package3-starting-scope.json` and checked at completion. No unrelated modification or historical document rewrite was needed. No commit/tag/push is performed without explicit later approval.

## 7. Owner review and recommended next package

Review the scoped design/formulas/minima, synthetic CLI labels, unsupported fields, UTC/availability/cutoff distinction, adjusted-vintage rejections, overlap/maturity/exclusion reports and all Proposed FRC/open decisions. Running the CLI is an offline review action; it does not enable forecasts in the dashboard. Confirm the existing workspace/real data remains accessible; owner UAT is distinct from engineer automated verification.

Recommended **Package 4: synthetic experiment inspection and evaluation review** after this checkpoint is approved. Proposed scope: read-only views of in-memory synthetic experiment inputs/configuration/cutoffs, model outputs/capabilities, pending/excluded outcomes and paired baseline metrics, plus accessible exact tables and reproducibility review. Keep synthetic labels and unchanged real-market views; no real-data adapter, persistent ledger, model installation, calibration claim, external source, account or trading integration. Agree FRC/evaluation/retention policy before any separate real-data forecasting authorization. No next-phase implementation begins here.
