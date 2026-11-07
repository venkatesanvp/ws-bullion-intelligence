# Proposed forecasting requirements extension

Date: 2026-11-06. Package 2C; specification only. **Every FRC requirement below is Proposed, not approved.** This extension does not amend REQ-BL-1.0, the requirements-v1.0 tag, DECISION_REGISTER or existing requirement status. Package 2 authorizes this design work, not a forecasting engine, model installation or training.

Parent: [research expansion assessment](RESEARCH_EXPANSION_ASSESSMENT.md). Design, contracts, evaluation gates and prioritized backlog: [forecasting foundation proposal](../03-design/FORECASTING_FOUNDATION_PROPOSAL.md). Implementation/evidence: [Package 2 checkpoint](TECHNICAL_PACKAGE_2_CHECKPOINT.md).

Priority is a recommendation: Must = required for a credible future forecasting foundation; Should = later extension, not permission to implement. Acceptance criteria describe future verification obligations; none asserts predictive capability. Existing REQ-06-001/002/003/005/018 already require traceability, independent calculation checks, point-in-time replay, out-of-sample evidence and separate evidence classes. FRC elaborates forecast-specific contracts rather than replacing those obligations. REQ-06-006 thresholds and REQ-03-022 ML scope remain Open; REQ-02-012/REQ-06-012 remain Proposed in the baseline.

## FRC-001 - Provider-neutral forecasting interface

- **Status:** Proposed.
- **Description:** A versioned model interface accepts a qualified immutable input snapshot and returns a typed result with capabilities and unavailable reasons.
- **Rationale:** Replace models independently of providers, UI and canonical analytics.
- **Priority:** Must.
- **Acceptance criteria:** The same input contract supports at least two independent baseline adapters; provider credentials/HTTP clients are absent from model inputs; unsupported outputs are explicit, never invented.
- **Dependencies:** FRC-003/004; reviewed numeric and capability policies.
- **Verification:** Contract/conformance tests with deterministic fake adapters, malformed inputs and unsupported capabilities; architecture inspection.
- **Existing trace:** REQ-02-015; REQ-03-001/002; REQ-06-002. Elaborates model separation, not a new acquisition interface.

## FRC-002 - Multi-horizon forecasts

- **Status:** Proposed.
- **Description:** Select configurable horizons initially 1, 5, 20, 60 and 120 verified exchange trading sessions, each with its own target and maturity.
- **Rationale:** Calendar days and independent horizons cannot be conflated.
- **Priority:** Must.
- **Acceptance criteria:** Holiday/weekend tests produce the correct target session; every horizon reports eligibility, counts and maturity independently; unsupported history returns unavailable. A later 252-session horizon requires explicit scope review.
- **Dependencies:** FRC-003/009/015; versioned NSE calendar and target convention.
- **Verification:** Calendar golden vectors including closures, partial coverage and unmatured outcomes.
- **Existing trace:** REQ-03-010; REQ-06-003. Specifies forecasting horizons without changing existing horizon controls.

## FRC-003 - Standardized time-series input

- **Status:** Proposed.
- **Description:** Input includes instrument/ISIN/exchange/currency, source/basis, canonical OHLCV, timeframe, calendar, cutoff, lookback, quality, provenance and optional feature availability masks/vintages.
- **Rationale:** A model must know what data existed, when, and on which price basis.
- **Priority:** Must.
- **Acceptance criteria:** Missing required OHLCV, mixed basis/timeframes, duplicate dates, future availability or unsupported calendar block eligibility; optional macro/fundamental/event features remain absent when unavailable; no imputed observation is represented as actual.
- **Dependencies:** Existing source qualification; FRC-015/016; per-use licensing.
- **Verification:** Dataset-builder fixtures for gaps, revisions, delayed publication, mixed units and incomplete bars.
- **Existing trace:** REQ-02-008/011/012/013; REQ-06-003. Reuses canonical identity and quality controls.

## FRC-004 - Model registry

- **Status:** Proposed.
- **Description:** Registry records model/version, configuration, training/validation periods, source dependencies, artifacts/digests, numeric policy, capabilities and lifecycle status.
- **Rationale:** A model name alone cannot reproduce an experiment.
- **Priority:** Must.
- **Acceptance criteria:** An immutable version identifies code, configuration, data and optional checkpoint/tokenizer; changing any creates a new version; activation and retirement require recorded review.
- **Dependencies:** FRC-001/010; artifact rights and lifecycle approval.
- **Verification:** Registry/version-digest and lifecycle transition tests; reproducibility review.
- **Existing trace:** REQ-03-002/022; REQ-06-001/012. Extends existing component separation and proposed ML governance.

## FRC-005 - Baseline forecasts

- **Status:** Proposed.
- **Description:** Specify no-change last-price, historical drift and historical-volatility benchmarks before complex models; add simple alternatives only with justification.
- **Rationale:** Complexity needs an honest same-target comparison.
- **Priority:** Must.
- **Acceptance criteria:** Formula, lookback, seed, target, uncertainty and eligibility are versioned; independent vectors verify outputs; a no-change point forecast does not imply a probability distribution.
- **Dependencies:** FRC-001/003/009; approved numerical conventions.
- **Verification:** Independent exact vectors, prefix invariance, chronological benchmark comparison.
- **Existing trace:** REQ-03-001; REQ-06-002/005/006. Does not approve a profitable strategy or acceptance threshold.

## FRC-006 - Probabilistic output contract

- **Status:** Proposed.
- **Description:** Support expected/median return, quantiles, P(return>0), configurable downside-threshold probabilities and forecast volatility, each with support and calibration status.
- **Rationale:** Point paths, probabilities and data quality express different information.
- **Priority:** Must.
- **Acceptance criteria:** Unsupported fields are null with reasons; probabilities are bounded, quantiles ordered, units/target consistent; calibration evidence is identified independently of raw sample count. Never substitute 50% for unknown.
- **Dependencies:** FRC-001/005/008; sufficient matured outcomes.
- **Verification:** Distribution conformance, monotonicity, probability/quantile and calibration-state tests.
- **Existing trace:** REQ-03-012/013; REQ-06-005/006. Keeps confidence dimensions distinct; sufficiency policy still requires approval.

## FRC-007 - Hypothetical scenario paths

- **Status:** Proposed.
- **Description:** Represent multiple hypothetical future paths in a separate simulation contract, with session grid, assumptions, seed, sampling count and model version.
- **Rationale:** Simulations must not contaminate actual observations or imply calibrated likelihood.
- **Priority:** Should.
- **Acceptance criteria:** All paths are SIMULATED; observed prices cannot be overwritten; inconsistent OHLC or nonpositive prices fail validation; scenario count is not presented as calibration evidence.
- **Dependencies:** FRC-003/004/006; reviewed sampling/numeric policy.
- **Verification:** Namespace/isolation, seed-repeatability and scenario-label tests.
- **Existing trace:** REQ-03-001/002; REQ-06-002/018. Forecast scenarios remain separate from trade simulation and evidence classes.

## FRC-008 - Calibration

- **Status:** Proposed.
- **Description:** Evaluate and, where justified, calibrate probabilities/intervals using training/validation data; reserve untouched out-of-sample assessment.
- **Rationale:** Plausible-looking probabilities need measured reliability.
- **Priority:** Must.
- **Acceptance criteria:** Calibration method/version, fit period, support by horizon/regime, reliability curves, interval coverage/width and proper scores are reported; insufficient outcomes remain UNASSESSED; holdout never fits calibration.
- **Dependencies:** FRC-006/009/010; approved minimum support and scoring policy.
- **Verification:** Known miscalibration fixtures, separated fitting/evaluation manifests and held-out scoring.
- **Existing trace:** REQ-03-013; REQ-06-005/006/012. Refines unresolved validation policy without adopting it.

## FRC-009 - Walk-forward validation

- **Status:** Proposed.
- **Description:** Chronological rolling/expanding evaluation with nested tuning, overlapping-label purge, availability-aware embargo and immutable final holdout.
- **Rationale:** Random splits and future-fitted features produce misleading evidence.
- **Priority:** Must.
- **Acceptance criteria:** Every input was available at origin; all transforms fit on eligible training data only; targets mature before scoring; windows, exclusions, independent counts and benchmarks are disclosed.
- **Dependencies:** FRC-002/003/015; approved split/support policy and adequate history.
- **Verification:** Deliberate leakage traps, replay/prefix checks, partition audits and independent scoring vectors.
- **Existing trace:** REQ-06-003/005/018. Elaborates existing approved validation obligations.

## FRC-010 - Forecast evidence ledger

- **Status:** Proposed.
- **Description:** Attributable forecast ID, identity/horizon/model, input cutoff/fingerprint, creation time, outputs/calibration, later realized outcome and evaluation results.
- **Rationale:** Predictions must be fixed before their outcomes are known.
- **Priority:** Must.
- **Acceptance criteria:** Revisions append versions, never rewrite original evidence; outcomes record availability and maturity; ledger retention respects dataset rights; no persistent market-data payload is stored without a grant.
- **Dependencies:** FRC-004/009/015; separate storage/backup/derived-output permissions and retention design.
- **Verification:** Append-only evidence, unauthorized-storage rejection, replay and retention-policy tests.
- **Existing trace:** REQ-02-008/014; REQ-06-001/005/018. Forecast evidence does not replace forward paper evidence.

## FRC-011 - Model comparison

- **Status:** Proposed.
- **Description:** Compare models by instrument, horizon, contemporaneously defined regime, accuracy, calibration, sample support and runtime cost on identical eligible targets.
- **Rationale:** Selective samples and aggregate leaderboards conceal weaknesses.
- **Priority:** Must.
- **Acceptance criteria:** Same origins/basis/targets and benchmark; paired uncertainty respects serial overlap; omitted cases and multiple search disclosed; insufficient strata unavailable.
- **Dependencies:** FRC-005/008/009/010; approved metrics and regime definitions.
- **Verification:** Fixed same-origin scoring cases, missing-model outputs and paired comparison review.
- **Existing trace:** REQ-03-004; REQ-06-005/006/018. No new profitability threshold is approved.

## FRC-012 - Forecast visualization

- **Status:** Proposed.
- **Description:** Distinguish historical actuals, forecast median, intervals, hypothetical paths, forecast-versus-actual and model evaluation views.
- **Rationale:** Chart geometry must not erase uncertainty or time boundaries.
- **Priority:** Should.
- **Acceptance criteria:** Origin/target/maturity and model/calibration are visible; unsupported bands omitted with reason; actuals and scenarios have separate legend/visual encodings and exact accessible values.
- **Dependencies:** FRC-006/007/010/011; renderer accessibility and rights review.
- **Verification:** Future browser/accessibility tests with typed fixtures, absent outputs and stale forecasts.
- **Existing trace:** REQ-03-012/013; REQ-06-001/005. Builds on evidence disclosure, not current technical chart parity.

## FRC-013 - External model adapters

- **Status:** Proposed.
- **Description:** Isolate optional external models behind capability-aware adapters; declare context, horizons, input requirements, runtime/numeric policy and output limitations.
- **Rationale:** External wrappers may return only point paths and cannot satisfy every distribution field.
- **Priority:** Should.
- **Acceptance criteria:** No backend/provider secrets reach the model; unsupported distribution/scenario fields remain unavailable; checkpoint/tokenizer/data rights, isolation and deterministic limitations pass review before installation.
- **Dependencies:** FRC-001/003/004/006/009; explicit model integration authorization.
- **Verification:** Adapter conformance tests with fake capability gaps, timeouts and invalid outputs; later independent model evaluation.
- **Existing trace:** REQ-03-002/022; REQ-06-012. Kronos is assessed only, not selected or installed.

## FRC-014 - Future domain fine-tuning

- **Status:** Proposed.
- **Description:** Support later domain training only after data/training rights, adequate history, versioned splits, resource budgets and out-of-sample review.
- **Rationale:** Source-code licensing does not authorize training on broker data or establish sample sufficiency.
- **Priority:** Should.
- **Acceptance criteria:** Approved dataset/card/experiment, untouched holdout and baseline comparison exist before training; material degradation blocks promotion; all artifacts and costs attributable.
- **Dependencies:** FRC-004/008/009/013/015; separate scope, rights and compute approval.
- **Verification:** Gate/document audit first; later reproducibility and independent held-out evaluation.
- **Existing trace:** REQ-03-022; REQ-06-006/012. Phase 2 capability remains unapproved.

## FRC-015 - Point-in-time integrity

- **Status:** Proposed.
- **Description:** Enforce availability at cutoff using publication/retrieval uncertainty, vintages/revisions, timezone/DST, holidays and source delays.
- **Rationale:** Reference dates alone cannot establish historical availability.
- **Priority:** Must.
- **Acceptance criteria:** Unknown publication times block validated replay; US-after-NSE-close releases cannot enter earlier NSE forecasts; later revisions never replace origin-vintage inputs; future outcomes remain unscored until eligible.
- **Dependencies:** Existing PIT provenance; qualified calendars, vintage archives and source timing evidence.
- **Verification:** Delayed-release, revision, DST/holiday and T-1 availability fixtures plus manifest audits.
- **Existing trace:** REQ-02-012; REQ-06-003/005. Elaborates rather than weakens approved replay requirements.

## FRC-016 - Multi-factor extensibility

- **Status:** Proposed.
- **Description:** Permit technical, macroeconomic, fundamental, correlation and event features through typed units, availability masks, evidence and versioned transformations, independent of model architecture.
- **Rationale:** One OHLCV model must not constrain future research or imply causal reconciliation.
- **Priority:** Should.
- **Acceptance criteria:** Optional unsupported feature families remain absent; source rights/units/cutoff/vintage checks precede use; reconciliation preserves conflicting evidence and does not double count correlated technical features.
- **Dependencies:** FRC-001/003/015; separately qualified sources and later integration authorization.
- **Verification:** Contract-only fixtures for missing/stale features, mixed units, as-of joins and correlated-evidence disclosures.
- **Existing trace:** REQ-03-002/004/007; REQ-02-008/012; REQ-06-003. Does not authorize macro, fundamental or event ingestion.

## Review disposition

All sixteen statuses remain Proposed. Owner review must settle target/basis/cutoff, support thresholds, numerical policy, evidence retention and model lifecycle before an implementation package. Existing approved requirement obligations retain precedence. No forecast, accuracy score, probability, backtest result or profitable-trading claim has been produced by Package 2.
