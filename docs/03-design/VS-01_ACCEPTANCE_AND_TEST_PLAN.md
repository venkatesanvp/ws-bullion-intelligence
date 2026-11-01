# VS-01 Acceptance and Test Plan

**Version/date:** 0.1 - Proposed; 2026-11-01 (Asia/Calcutta).  
**Authority:** Human Step 2 architecture/design task; documentation only.  
**Baseline:** [REQ-BL-1.0](../01-requirements/REQUIREMENTS_BASELINE.md), annotated tag `requirements-v1.0`, commit `e10eef55fb21368e53dbe4599006b620cbb48566`. Tag and unchanged source content verified before authoring.  
**Status:** Architecture/design recommendations are Proposed. No baseline requirement status, maturity, priority, applicability or increment is changed. No implementation or spike is authorized.

## 1. Test authority and evidence status

All cases below are **Designed - not executed**. No application exists and no runtime/dependency/database/browser installation was performed. Test readiness does not approve governing requirements. See [DC-01..09](VS-01_DETAILED_DESIGN.md) and [current readiness](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#readiness).

After scoped approval, unit tests accompany each work item; integration/browser evidence closes the end-to-end path. Do not defer correctness tests until all features exist.

### Test layers

- Backend pure tests: canonical parsing/quality and Decimal indicators/comparisons, independent Fraction/high-precision references, controlled clocks and explicit invalid cases.
- Repository integration: real disposable PostgreSQL and migrations, uniqueness/FKs/rollback/concurrency. SQLite/mocks are not the integrity oracle.
- API tests: typed schemas, authentication, stable safe errors, idempotence, pagination/revision and unavailable results.
- Frontend component tests: Vitest/React Testing Library, observable UI behavior, request races and accessibility-oriented controls; no mirrored implementation snapshots as the main evidence.
- Browser end-to-end: Playwright Chromium against actual local UI/API/PostgreSQL, not an all-mocked backend.
- Local operational acceptance: reproducible startup, ordinary restart and separate database restore.

Synthetic fixtures are clearly labeled test-only and never displayed as real market evidence. Actual permitted ETF samples remain required for VS01-T-03 acceptance, but do not license a network adapter.

## 2. Acceptance and verification cases

For every case retain the versioned inputs/profile/algorithm references, expected-versus-observed assertion and future report; no result exists yet.

Every numeric example below is **synthetic arithmetic fixture data**, not a quote, signal, portfolio or backtest. Expected rounded strings implement Proposed DC-05, not an approved trading threshold.

<a id="vs01-t-01"></a>

### VS01-T-01 - Listing and watchlist persistence

- **Layer:** API/DB + UI.
- **Expected behavior / acceptance:** Create/edit listing display metadata and watchlist; add/remove a member twice, reload; reject duplicate listing/invalid metal/currency and immutable financial identity edits; prices survive membership removal.
- **Design contracts:** [DC-01](VS-01_DETAILED_DESIGN.md#dc-01), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-01, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-04](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-04).

<a id="vs01-t-02"></a>

### VS01-T-02 - Metal selection and response identity

- **Layer:** Frontend component.
- **Expected behavior / acceptance:** Switch Gold/Silver/listing while a previous request is delayed; obsolete response never appears under the new selection; user-configured membership survives restart.
- **Design contracts:** [DC-01](VS-01_DETAILED_DESIGN.md#dc-01), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-01, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-04](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-04), [VS01-WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10).

<a id="vs01-t-03"></a>

### VS01-T-03 - Qualified real-CSV acceptance

- **Layer:** Integration + browser.
- **Expected behavior / acceptance:** With permitted independently identified Gold and Silver ETF samples, record source evidence, map/import daily data and inspect chart/table provenance. An unqualified/restricted source is rejected. No sample exists yet; synthetic data cannot pass the real-source criterion.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-02, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [VS01-WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09), [VS01-WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11).

<a id="vs01-t-04"></a>

### VS01-T-04 - CSV hard-validation matrix

- **Layer:** Unit + API/DB.
- **Expected behavior / acceptance:** Exercise absent fields, bad dates, nonfinite/nonpositive values, excess numeric precision, invalid OHLC, negative/noninteger volume, currency/frequency mismatch and unexpected columns. Each hard case rejects all new observations and reports bounded row/code diagnostics.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04).
- **Capability trace:** VS01-CAP-02, VS01-CAP-03, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05).

<a id="vs01-t-05"></a>

### VS01-T-05 - Idempotent imports and retries

- **Layer:** API/DB.
- **Expected behavior / acceptance:** Repeat identical key/body, reject same-key changed profile/body, then re-import reordered equivalent rows with a new key. Observation count/revision changes only for new values; successful replay returns original batch.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07).
- **Capability trace:** VS01-CAP-02, VS01-CAP-03, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05).

<a id="vs01-t-06"></a>

### VS01-T-06 - Conflicting duplicate and uncertain outcome

- **Layer:** Integration/fault injection.
- **Expected behavior / acceptance:** Conflict within file or existing key rejects all new prices. Inject failure before commit and lost response after commit; preserve safe audit when possible and resolve the same request key without inventing failure/success or duplicates.
- **Design contracts:** [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07).
- **Capability trace:** VS01-CAP-02, VS01-CAP-03, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05).

<a id="vs01-t-07"></a>

### VS01-T-07 - Temporal/raw provenance and decimal storage

- **Layer:** DB/API.
- **Expected behavior / acceptance:** Keep mapped raw values and exact input decimals; publication/event instant absent remains null, trading date does not become midnight, original batch/row/source persists, and imported history remains unverified for replay.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04).
- **Capability trace:** VS01-CAP-03, VS01-CAP-07, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [VS01-WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06).

<a id="vs01-t-08"></a>

### VS01-T-08 - Concurrent persistence integrity

- **Layer:** Real PostgreSQL integration.
- **Expected behavior / acceptance:** Race same-instrument/source records and global request keys using separate transactions; unique constraints/locks resolve idempotence or explicit conflict. Source-policy change cannot create unauthorized partial price acceptance.
- **Design contracts:** [DC-03](VS-01_DETAILED_DESIGN.md#dc-03).
- **Capability trace:** VS01-CAP-03, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [VS01-WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06).

<a id="vs01-t-09"></a>

### VS01-T-09 - History snapshot and pagination

- **Layer:** API/DB.
- **Expected behavior / acceptance:** Require explicit source/basis; stable cursor pages are ordered and complete. Changed revision/profile yields SNAPSHOT_CHANGED. Missing source does not choose a fallback. Visible range and dataset coverage remain distinct.
- **Design contracts:** [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07).
- **Capability trace:** VS01-CAP-04, VS01-CAP-07, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06).

<a id="vs01-t-10"></a>

### VS01-T-10 - Freshness and calendar truth

- **Layer:** Unit/API/UI.
- **Expected behavior / acceptance:** Unknown calendar/publication gives UNASSESSED/UNKNOWN. A fixed approved test policy with expected-session evidence can produce FRESH/STALE; old-window selection alone does not make current dataset stale. Out-of-coverage assessment is unassessed.
- **Design contracts:** [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-04, VS01-CAP-07, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [VS01-WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10).

<a id="vs01-t-11"></a>

### VS01-T-11 - SMA independent reference

- **Layer:** Pure unit/reference.
- **Expected behavior / acceptance:** Synthetic closes [10,12,14,13], n=2 -> WARMUP then 11.000000000000,13.000000000000,13.500000000000. Check n=1, bounds and exact Decimal/rational agreement.
- **Design contracts:** [DC-05](VS-01_DETAILED_DESIGN.md#dc-05).
- **Capability trace:** VS01-CAP-05, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07).

<a id="vs01-t-12"></a>

### VS01-T-12 - EMA seed and prefix reference

- **Layer:** Pure unit/reference.
- **Expected behavior / acceptance:** Same synthetic closes, n=2 -> WARMUP then 11.000000000000,13.000000000000,13.000000000000. Verify SMA seed and full-prefix calculation, never first-close or chart-window seed.
- **Design contracts:** [DC-05](VS-01_DETAILED_DESIGN.md#dc-05).
- **Capability trace:** VS01-CAP-05, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07).

<a id="vs01-t-13"></a>

### VS01-T-13 - Wilder RSI reference and undefined states

- **Layer:** Pure unit/reference.
- **Expected behavior / acceptance:** Same synthetic closes, n=2 -> first output 100.000000000000 at index 2, then 66.666666666667. Flat series -> FLAT_WINDOW null; loss-only ->0; missing history/gap warms up instead of returning a trading signal.
- **Design contracts:** [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](VS-01_DETAILED_DESIGN.md#dc-05).
- **Capability trace:** VS01-CAP-05, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07).

<a id="vs01-t-14"></a>

### VS01-T-14 - Determinism and discontinuities

- **Layer:** Pure unit + API.
- **Expected behavior / acceptance:** Same input/version/params yields same values/fingerprint apart from external computed_at. Changing only visible range preserves overlapping EMA/RSI; known gaps/actions reset segments; no later row affects earlier values. Reject prefix over-limit and unknown basis; arithmetic context remains local.
- **Design contracts:** [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](VS-01_DETAILED_DESIGN.md#dc-05).
- **Capability trace:** VS01-CAP-05, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07), [VS01-WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10).

<a id="vs01-t-15"></a>

### VS01-T-15 - Common-date price comparisons

- **Layer:** Pure unit/API.
- **Expected behavior / acceptance:** Use explicitly synthetic matching series: [10,11,12] and [20,22,23] at common dates ->20% and15% endpoint price change. Sparse series use actual common dates without fill; insufficient common dates are explicit.
- **Design contracts:** [DC-06](VS-01_DETAILED_DESIGN.md#dc-06).
- **Capability trace:** VS01-CAP-06, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-08](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-08).

<a id="vs01-t-16"></a>

### VS01-T-16 - Incompatible/unsupported comparison claims

- **Layer:** Unit/API/UI.
- **Expected behavior / acceptance:** Reject or disclose incompatible currency/basis/no overlap. Null volume stays unavailable. Raw/adjusted price changes are not total return, NAV premium, tracking or executable liquidity; no client-side authoritative recalculation.
- **Design contracts:** [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-06](VS-01_DETAILED_DESIGN.md#dc-06), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-06, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-08](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-08), [VS01-WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10).

<a id="vs01-t-17"></a>

### VS01-T-17 - Quality issue lineage

- **Layer:** Unit/API/DB.
- **Expected behavior / acceptance:** Retain row/source/batch/profile identity for sorted out-of-order data, known non-session/gap/action cases and unknown metadata; no zero-filled bars or fabricated quality score; unrelated input columns are not persisted.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04).
- **Capability trace:** VS01-CAP-07, VS01-CAP-08, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [VS01-WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [VS01-WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09).

<a id="vs01-t-18"></a>

### VS01-T-18 - User workflow states and chart alternative

- **Layer:** Frontend component + browser.
- **Expected behavior / acceptance:** Cover loading/empty/error/stale/unavailable states, watchlist/import/history/indicator/compare flows, source labels, chart and accessible table, escaped imported strings and deliberate retry behavior.
- **Design contracts:** [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08).
- **Capability trace:** VS01-CAP-04, VS01-CAP-06, VS01-CAP-09.
- **Work-item trace:** [VS01-WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09), [VS01-WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10), [VS01-WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11).

<a id="vs01-t-19"></a>

### VS01-T-19 - Access origin and secret controls

- **Layer:** API/security + browser.
- **Expected behavior / acceptance:** Missing/wrong token and malicious-origin simple form cannot mutate state; correct owner flow works; token is absent from URL, frontend build/browser persistence and structured logs. Health returns no sensitive configuration.
- **Design contracts:** [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09).
- **Capability trace:** VS01-CAP-09, VS01-CAP-10.
- **Work-item trace:** [VS01-WI-03](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-03), [VS01-WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11).

<a id="vs01-t-20"></a>

### VS01-T-20 - Upload and error safety

- **Layer:** Unit/API/security.
- **Expected behavior / acceptance:** Reject binary/archive/remote URL, size/row-limit breaches, dynamic mapping expressions and path abuse; SQL uses parameters; formula-like strings are never executed. Responses/logs omit raw uploads, secrets and stack traces.
- **Design contracts:** [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09).
- **Capability trace:** VS01-CAP-02, VS01-CAP-09, VS01-CAP-10.
- **Work-item trace:** [VS01-WI-03](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-03), [VS01-WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [VS01-WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09), [VS01-WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11).

<a id="vs01-t-21"></a>

### VS01-T-21 - Startup migration and restart

- **Layer:** Local integration.
- **Expected behavior / acceptance:** From empty approved test DB, health-gated migration yields readiness, then import/watchlist survives ordinary restart. Missing config or wrong schema blocks readiness. No destructive reset of personal data.
- **Design contracts:** [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09).
- **Capability trace:** VS01-CAP-09, VS01-CAP-10.
- **Work-item trace:** [VS01-WI-01](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-01), [VS01-WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [VS01-WI-03](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-03), [VS01-WI-12](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-12).

<a id="vs01-t-22"></a>

### VS01-T-22 - Backup and separate restore

- **Layer:** Local acceptance.
- **Expected behavior / acceptance:** Dump approved data and restore into separate empty DB; verify schema, observation/batch/quality/watchlist counts, provenance links and known-query/indicator outputs before any switch; do not overwrite live data.
- **Design contracts:** [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09).
- **Capability trace:** VS01-CAP-09, VS01-CAP-10.
- **Work-item trace:** [VS01-WI-12](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-12).

<a id="vs01-t-23"></a>

### VS01-T-23 - Reproducibility and scope freeze

- **Layer:** Review + local acceptance.
- **Expected behavior / acceptance:** Record dependency/image/browser locks, environment and test reports; isolate DB/clock/fixtures; no live provider calls required for tests. Baseline tag/source hashes unchanged; no trading, AI, broker or future-module endpoints; no financial evidence fabricated.
- **Design contracts:** [DC-09](VS-01_DETAILED_DESIGN.md#dc-09).
- **Capability trace:** VS01-CAP-09, VS01-CAP-10.
- **Work-item trace:** [VS01-WI-01](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-01), [VS01-WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11), [VS01-WI-12](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-12).

## 3. Requirements -> architecture -> design -> task -> test matrix

Parent approval/maturity is read from the frozen inventory, not promoted by this mapping. A chain is verification coverage, not implementation authorization.

| Capability | Baseline requirements | Architecture | Contracts | Implementation work | Verification cases |
| --- | --- | --- | --- | --- | --- |
| VS01-CAP-01: Configurable Gold/Silver ETF watchlist | [REQ-01-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-001) (Approved), [REQ-01-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-003) (Approved), [REQ-01-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-008) (Open), [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001) (Approved) | [ADR-01](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-01), [ADR-02](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-02), [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03) | [DC-01](VS-01_DETAILED_DESIGN.md#dc-01), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08) | [WI-04](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-04), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10) | [T-01](#vs01-t-01), [T-02](#vs01-t-02) |
| VS01-CAP-02: Real historical CSV import | [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007) (Approved), [REQ-02-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008) (Proposed), [REQ-02-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-009) (Proposed), [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011) (Proposed), [REQ-02-015](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-015) (Approved) | [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05) | [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07) | [WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09) | [T-03](#vs01-t-03), [T-04](#vs01-t-04), [T-05](#vs01-t-05), [T-06](#vs01-t-06), [T-20](#vs01-t-20) |
| VS01-CAP-03: Validate and persist observations | [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011) (Proposed), [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012) (Proposed), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013) (Open), [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001) (Approved), [REQ-05-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002) (Proposed), [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010) (Proposed) | [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05) | [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04) | [WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06) | [T-04](#vs01-t-04), [T-05](#vs01-t-05), [T-06](#vs01-t-06), [T-07](#vs01-t-07), [T-08](#vs01-t-08) |
| VS01-CAP-04: Historical price charts | [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001) (Approved), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013) (Proposed), [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011) (Proposed), [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012) (Proposed) | [ADR-02](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-02), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05), [ADR-07](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-07) | [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08) | [WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10) | [T-09](#vs01-t-09), [T-10](#vs01-t-10), [T-18](#vs01-t-18) |
| VS01-CAP-05: Deterministic technical indicators | [REQ-03-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-001) (Approved), [REQ-03-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007) (Proposed), [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002) (Approved), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006) (Open) | [ADR-06](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-06), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10) | [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](VS-01_DETAILED_DESIGN.md#dc-05), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07) | [WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10) | [T-11](#vs01-t-11), [T-12](#vs01-t-12), [T-13](#vs01-t-13), [T-14](#vs01-t-14) |
| VS01-CAP-06: Supported ETF comparisons | [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007) (Approved), [REQ-03-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008) (Proposed), [REQ-03-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-009) (Proposed), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013) (Proposed) | [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05), [ADR-07](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-07), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10) | [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-06](VS-01_DETAILED_DESIGN.md#dc-06), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08) | [WI-08](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-08), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10) | [T-15](#vs01-t-15), [T-16](#vs01-t-16), [T-18](#vs01-t-18) |
| VS01-CAP-07: Provenance freshness and quality disclosure | [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012) (Proposed), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013) (Open), [REQ-04-005](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-005) (Approved), [REQ-04-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-006) (Approved), [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010) (Proposed) | [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10) | [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08) | [WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10) | [T-07](#vs01-t-07), [T-09](#vs01-t-09), [T-10](#vs01-t-10), [T-17](#vs01-t-17) |
| VS01-CAP-08: Missing stale duplicate and invalid data behavior | [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011) (Proposed), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013) (Open), [REQ-02-014](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-014) (Open) | [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10) | [DC-02](VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](VS-01_DETAILED_DESIGN.md#dc-05), [DC-06](VS-01_DETAILED_DESIGN.md#dc-06) | [WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07), [WI-08](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-08) | [T-04](#vs01-t-04), [T-05](#vs01-t-05), [T-06](#vs01-t-06), [T-08](#vs01-t-08), [T-13](#vs01-t-13), [T-17](#vs01-t-17) |
| VS01-CAP-09: Automated backend and frontend verification | [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002) (Approved), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006) (Open), [REQ-06-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-007) (Proposed), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008) (Proposed) | [ADR-08](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-08), [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09) | [DC-05](VS-01_DETAILED_DESIGN.md#dc-05), [DC-07](VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](VS-01_DETAILED_DESIGN.md#dc-08), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09) | [WI-01](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-01), [WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [WI-03](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-03), [WI-04](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-04), [WI-05](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-05), [WI-06](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-06), [WI-07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-07), [WI-08](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-08), [WI-09](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-09), [WI-10](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-10), [WI-11](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-11) | [T-01](#vs01-t-01), [T-02](#vs01-t-02), [T-03](#vs01-t-03), [T-04](#vs01-t-04), [T-05](#vs01-t-05), [T-06](#vs01-t-06), [T-07](#vs01-t-07), [T-08](#vs01-t-08), [T-09](#vs01-t-09), [T-10](#vs01-t-10), [T-11](#vs01-t-11), [T-12](#vs01-t-12), [T-13](#vs01-t-13), [T-14](#vs01-t-14), [T-15](#vs01-t-15), [T-16](#vs01-t-16), [T-17](#vs01-t-17), [T-18](#vs01-t-18), [T-19](#vs01-t-19), [T-20](#vs01-t-20), [T-21](#vs01-t-21), [T-22](#vs01-t-22), [T-23](#vs01-t-23) |
| VS01-CAP-10: Reproducible local development startup | [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001) (Approved), [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003) (Approved), [REQ-05-004](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004) (Open), [REQ-05-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-008) (Open), [REQ-05-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-009) (Open), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008) (Proposed) | [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-08](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-08), [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09) | [DC-03](VS-01_DETAILED_DESIGN.md#dc-03), [DC-09](VS-01_DETAILED_DESIGN.md#dc-09) | [WI-01](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-01), [WI-02](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-02), [WI-03](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-03), [WI-12](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#vs01-wi-12) | [T-19](#vs01-t-19), [T-20](#vs01-t-20), [T-21](#vs01-t-21), [T-22](#vs01-t-22), [T-23](#vs01-t-23) |

## 4. Reproducible evidence package - future execution

Capture application commit, baseline tag, approved ADR/DC disposition, requirement scope, locked runtime/dependencies/images/browser, schema revision, test commands/configuration, fixture hashes, source-use evidence, test reports and failures. Keep synthetic fixtures and real permitted acceptance data visibly separate. No live credentials/account identifiers/personal portfolio records in Git.

Tests use isolated DB names/volumes, controlled clocks and explicit source profiles. Database restore targets a separate empty database. External provider outages must not affect controlled automated suites. A live-source smoke test would need separate source/access permission; it is not required to test a CSV adapter.

Numeric validation uses rational references distinct from the production recurrence implementation and higher-precision checks; compare the specified 12-place wire values exactly. Avoid "expected = implementation output". Check seed, gap, source/basis and chart-range invariance as well as ordinary values.

No coverage percentage, latency SLA, financial return/win-rate target or minimum validation period is invented. All included cases must pass their approved observable criteria; failed/unexecuted mandatory evidence is not described as success.

## 5. Definition of done for VS-01

1. Human-approved scoped requirements and ADR/DC criteria exist; governing Proposed/Open detail is not silently treated as Approved.
2. End-to-end watchlist -> permitted real CSV -> atomic validated PostgreSQL history -> chart/indicator/comparison -> quality/provenance works.
3. All ten capabilities have relevant test evidence; all mandatory VS01-T-01..23 cases pass after implementation, including real-source acceptance and no real execution.
4. Source/series/basis and temporal limitations remain visible; no fabricated prices, automatic adjustment, point-in-time or total-return claim.
5. Backend/frontend/unit/integration/API/browser and startup/restore evidence identifies its versions and environment.
6. Missing/error/stale/unassessed/unavailable states and secret/upload boundary cases are reviewed.
7. Baseline source files and D-01..16 unchanged; any later scoped requirement approval is explicit and traceable, not a rewrite of the tagged snapshot.
8. No future strategy/AI/trading/paper/manual module is claimed delivered by VS-01.

## 6. Second-pass readiness assessment protocol

Re-evaluate the completed proposal against the frozen requirement states, rather than assuming its preferred choices have been adopted:
- Trace every CAP to existing requirement IDs and explicit DC, ADR, task and case.
- Treat unapproved/insufficiently specified governing behavior as Blocked.
- Use Ready with conditions only after governing behavior is approved/specified and remaining conditions are external prerequisites, never as a euphemism for missing approval.
- Keep missing actual CSV evidence distinct from permission to code against approved synthetic fixtures.
- Check invariants with counterexamples: mixed source/basis, same-bar invented timing, unknown calendar/publication, failed commit/retry, contaminated test data and stale UI response.
- The assessment outcome is recorded in the planning file; it is a separate review pass, not a claim that a second human or an implemented system has certified readiness.
