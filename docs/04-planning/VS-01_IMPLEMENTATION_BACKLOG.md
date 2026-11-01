# VS-01 Implementation Backlog and Readiness Review

**Version/date:** 0.2 - Scoped implementation disposition; 2026-11-02 (Asia/Calcutta).

**Authority:** Step 2 design record, followed by the human Step 3 implementation/security grant and Step 4 research-dashboard grant; see the dated scoped dispositions and [implementation status](../04-planning/VS-01_IMPLEMENTATION_STATUS.md).

**Baseline:** [REQ-BL-1.0](../01-requirements/REQUIREMENTS_BASELINE.md), annotated tag `requirements-v1.0`, commit `e10eef55fb21368e53dbe4599006b620cbb48566`. Tag and unchanged source content verified before authoring.  
**Status:** Scoped Step 3/4 grants apply. Sections 1-6 retain the historical Step 2 planning/readiness assessment except for explicit dated SQ dispositions. Current execution status follows below. No baseline requirement status, maturity, priority, applicability or increment is changed.

## Current execution disposition - 2026-11-02

| Work items | Current implementation/verification |
| --- | --- |
| WI-01..06, WI-09 | Existing implementation regression verified with synthetic fixtures. WI-05 real-source acceptance remains blocked by SQ-01. |
| WI-07, WI-08, WI-10 | Implemented and verified for the approved deterministic research scope; see the Step 4 completion report. |
| WI-11 | Partially complete: cumulative automated/security evidence passed; qualified real-source T-03 and cumulative human acceptance remain open. |
| WI-12 | Partially complete: pinned startup, Linux arithmetic and isolated synthetic recovery verified; actual owner-data cutover/retention and final handover remain open. |

[Step 4 completion evidence](VS-01_STEP4_COMPLETION.md) records exact tests, source changes and proposed checkpoint contents. Full VS-01 is not accepted.

## 1. Historical Step 2 planning authority and minimum implementation package

This file proposes work; it does not authorize running it. The attached Step 2 task explicitly permits planning while prohibiting source code, installations, Docker infrastructure, broker connection and implementation.

Smallest executable package: the single local UI/API/PostgreSQL path with configurable watchlist, qualified CSV ingestion, persisted history, SMA/EMA/RSI, price-only comparison, visible quality/provenance and automated verification. WI-01..10 provide the functionality with unit tests in each item; WI-11/12 close integrated real-data/operational acceptance. An empty framework or mocked-data chart is not accepted as VS-01.

No completion of all six detailed specifications is demanded. Only the applicable behavior/interface/acceptance/verification must be sufficiently specified and approved. Future R1 strategy/risk/planning/paper/manual/AI modules are not in the package.

## 2. Frozen requirement coverage

Thirty distinct baseline requirements govern this slice. Classifications below are copied from the inventory and preserved. A Proposed/Open parent is not approved by this design. Approved/Analyzed also does not mean implementation-ready.

| Requirement | Approval | Maturity | Priority | Existing R1 applicability/increment |
| --- | --- | --- | --- | --- |
| [REQ-01-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-001) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-01-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-003) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-01-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-008) | Open | Identified | Must | Required; R1-A. |
| [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-02-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-02-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-009) | Proposed | Analyzed | Must | Conditional on selected coverage, reliable data and validation; R1-A. |
| [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013) | Open | Identified | Must | Required; R1-A. |
| [REQ-02-014](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-014) | Open | Identified | Must | Required; R1-A. |
| [REQ-02-015](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-015) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-03-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-001) | Approved | Analyzed | Must | Required; R1-B. |
| [REQ-03-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007) | Proposed | Analyzed | Must | Required; R1-B. |
| [REQ-03-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008) | Proposed | Analyzed | Should | Conditional on selected coverage, reliable data and validation; R1-A. |
| [REQ-03-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-009) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-04-005](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-005) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-04-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-006) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013) | Proposed | Analyzed | Should | Required; R1-A. |
| [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-05-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003) | Approved | Analyzed | Must | Required; R1-A. |
| [REQ-05-004](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004) | Open | Identified | Must | Required; R1-C. |
| [REQ-05-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-008) | Open | Identified | Must | Required; R1-C. |
| [REQ-05-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-009) | Open | Identified | Must | Required; R1-C. |
| [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002) | Approved | Analyzed | Must | Required; R1-B. |
| [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006) | Open | Identified | Must | Required; R1-B. |
| [REQ-06-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-007) | Proposed | Analyzed | Must | Required; R1-A. |
| [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008) | Proposed | Analyzed | Must | Required; R1-C. |

The Step 2 research slice may expose indicator/verification primitives early, but REQ-03-007 and REQ-06-002 retain their recorded R1-B allocation; this is not a claim that R1-B or all independent strategies are delivered. REQ-04-013 remains Should in the frozen inventory even though the human-defined VS-01 target explicitly includes charts. Scoped acceptance must be approved without silently rewriting these fields.

## 3. Dependency-ordered work items

Complexity is relative L/M/H, not a delivery-time promise. **All work items are currently Blocked for implementation** by the scoped approval gate and applicable questions. Design exploration is authorized; even a nonproduction code spike needs explicit authorization.

Dependencies below form a proposed order, not permission to start. Standard unit tests accompany implementation; no "test later" phase.

<a id="vs01-wi-01"></a>

### VS01-WI-01 - Locked local development and test runtime

- **Description:** Create the authorized project/runtime manifests, compatible dependency/image locks and future Compose startup path, with isolated test configuration; no future business modules.
- **Requirement references:** [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001), [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003), [REQ-05-004](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004), [REQ-05-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-008).
- **Dependencies / proposed order:** Scope/ADR/DC approval; then first package task. Order rank 1; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-08](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-08), [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09); [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Only loopback UI/API and private PostgreSQL; lock identities recorded; missing required config fails safely.
- **Verification approach:** [VS01-T-21](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-21), [VS01-T-23](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-23); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-02"></a>

### VS01-WI-02 - Persistent schema and migrations

- **Description:** Implement the eight DC-03 entities, constraints, indexes and migration/readiness version checks.
- **Requirement references:** [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011), [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001), [REQ-05-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002).
- **Dependencies / proposed order:** [WI-01](#vs01-wi-01) Order rank 2; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05); [DC-03](../03-design/VS-01_DETAILED_DESIGN.md#dc-03), [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Fresh PostgreSQL migrates; invalid FK/unique/decimal cases fail; no personal database reset.
- **Verification approach:** [VS01-T-07](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-07), [VS01-T-08](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-08), [VS01-T-21](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-21); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-03"></a>

### VS01-WI-03 - Local API access and common errors

- **Description:** Implement token/origin/host checks, typed errors, liveness/readiness and structured redacted logs.
- **Requirement references:** [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003), [REQ-05-004](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004), [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008).
- **Dependencies / proposed order:** [WI-01](#vs01-wi-01), [WI-02](#vs01-wi-02) Order rank 3; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09); [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07), [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Unauthorized simple form/invalid token cannot mutate data; readiness reflects DB/schema; no secret/raw upload in responses/logs.
- **Verification approach:** [VS01-T-19](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-19), [VS01-T-20](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-20), [VS01-T-21](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-21); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-04"></a>

### VS01-WI-04 - Instrument source and watchlist workflow

- **Description:** Implement listing/source qualification/watchlist contracts and a minimal persistent UI selection flow.
- **Requirement references:** [REQ-01-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-003), [REQ-01-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-008), [REQ-02-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008), [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001).
- **Dependencies / proposed order:** [WI-02](#vs01-wi-02), [WI-03](#vs01-wi-03) Order rank 4; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-02](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-02), [ADR-03](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-03), [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04); [DC-01](../03-design/VS-01_DETAILED_DESIGN.md#dc-01), [DC-02](../03-design/VS-01_DETAILED_DESIGN.md#dc-02), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](../03-design/VS-01_DETAILED_DESIGN.md#dc-08).
- **Acceptance criteria:** Owner can configure real listings without invented recommendations; source qualification is explicit, not inferred; membership survives reload.
- **Verification approach:** [VS01-T-01](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-01), [VS01-T-02](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-02), [VS01-T-03](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-03); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-05"></a>

### VS01-WI-05 - Canonical CSV atomic ingestion

- **Description:** Implement strict mapping/validation, audit rows/issues, terminal batch outcomes, uniqueness/idempotence and commit-uncertainty resolution.
- **Requirement references:** [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007), [REQ-02-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008), [REQ-02-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-009), [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011), [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-02-015](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-015).
- **Dependencies / proposed order:** [WI-02](#vs01-wi-02), [WI-03](#vs01-wi-03), [WI-04](#vs01-wi-04) Order rank 5; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04), [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05); [DC-02](../03-design/VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](../03-design/VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07).
- **Acceptance criteria:** Whole accepted observation set or rejected audit only; no duplicate growth/overwrite; retries and conflicts have explicit outcomes.
- **Verification approach:** [VS01-T-03](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-03), [VS01-T-04](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-04), [VS01-T-05](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-05), [VS01-T-06](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-06), [VS01-T-07](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-07), [VS01-T-08](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-08), [VS01-T-17](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-17), [VS01-T-20](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-20); retain versioned evidence after execution.
- **Estimated complexity:** H.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-06"></a>

### VS01-WI-06 - History provenance and quality queries

- **Description:** Implement explicit series selection, read snapshots/keyset paging and freshness/quality metadata.
- **Requirement references:** [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-04-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-006), [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010).
- **Dependencies / proposed order:** [WI-05](#vs01-wi-05) Order rank 6; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-05](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-05), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10); [DC-03](../03-design/VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07).
- **Acceptance criteria:** No vendor/basis fallback; cursor changes detected; missing publication/calendar remains unknown rather than invented.
- **Verification approach:** [VS01-T-07](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-07), [VS01-T-08](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-08), [VS01-T-09](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-09), [VS01-T-10](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-10), [VS01-T-17](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-17); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-07"></a>

### VS01-WI-07 - Pure research indicator engine

- **Description:** Implement Decimal SMA/EMA/Wilder RSI, seed/prefix/gap behavior, typed unavailable results and independent arithmetic reference tests.
- **Requirement references:** [REQ-03-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-001), [REQ-03-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007), [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006).
- **Dependencies / proposed order:** [WI-06](#vs01-wi-06) Order rank 7; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-06](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-06), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10); [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](../03-design/VS-01_DETAILED_DESIGN.md#dc-05), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07).
- **Acceptance criteria:** Exact approved wire outputs and metadata; no default n/trading threshold, frontend/LLM math or date-window reseeding.
- **Verification approach:** [VS01-T-11](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-11), [VS01-T-12](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-12), [VS01-T-13](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-13), [VS01-T-14](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-14); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-08"></a>

### VS01-WI-08 - Price-only ETF comparison

- **Description:** Implement common-date compatible-series metrics and transparent unavailable/unsupported claims.
- **Requirement references:** [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007), [REQ-03-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008), [REQ-03-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-009), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013).
- **Dependencies / proposed order:** [WI-06](#vs01-wi-06) Order rank 8; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-07](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-07), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10); [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-06](../03-design/VS-01_DETAILED_DESIGN.md#dc-06), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07).
- **Acceptance criteria:** Actual common endpoints, precise price change/rebase and coverage; no fill-forward/total-return or liquidity claims.
- **Verification approach:** [VS01-T-15](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-15), [VS01-T-16](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-16); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-09"></a>

### VS01-WI-09 - Import and quality user experience

- **Description:** Implement bounded file/profile form, batch/rejection/issue inspection and retry identity in the browser.
- **Requirement references:** [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013), [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003).
- **Dependencies / proposed order:** [WI-04](#vs01-wi-04), [WI-05](#vs01-wi-05), [WI-06](#vs01-wi-06) Order rank 9; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-02](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-02), [ADR-04](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-04); [DC-02](../03-design/VS-01_DETAILED_DESIGN.md#dc-02), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](../03-design/VS-01_DETAILED_DESIGN.md#dc-08), [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Clear permitted-source gate, safe row errors and duplicate/conflict outcomes; no raw file/log secret leakage.
- **Verification approach:** [VS01-T-03](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-03), [VS01-T-17](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-17), [VS01-T-18](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-18), [VS01-T-20](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-20); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-10"></a>

### VS01-WI-10 - Charts indicators and comparison dashboard

- **Description:** Implement Plotly line/history and table, explicit source/basis/date/n controls and research metadata/empty/error/stale/unavailable states.
- **Requirement references:** [REQ-03-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007), [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001), [REQ-04-005](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-005), [REQ-04-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-006), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013).
- **Dependencies / proposed order:** [WI-07](#vs01-wi-07), [WI-08](#vs01-wi-08), [WI-09](#vs01-wi-09) Order rank 10; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-02](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-02), [ADR-06](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-06), [ADR-07](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-07), [ADR-10](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-10); [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](../03-design/VS-01_DETAILED_DESIGN.md#dc-05), [DC-06](../03-design/VS-01_DETAILED_DESIGN.md#dc-06), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](../03-design/VS-01_DETAILED_DESIGN.md#dc-08).
- **Acceptance criteria:** End-to-end user research path works; delayed responses cannot appear under a different selection; no trading/AI future placeholders.
- **Verification approach:** [VS01-T-02](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-02), [VS01-T-09](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-09), [VS01-T-10](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-10), [VS01-T-14](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-14), [VS01-T-16](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-16), [VS01-T-18](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-18); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-11"></a>

### VS01-WI-11 - Integrated acceptance and security evidence

- **Description:** Run real PostgreSQL/API/component/browser cases on the integrated app, including permitted real Gold/Silver ETF samples, failure/retry and adversarial cases.
- **Requirement references:** [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006), [REQ-06-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-007), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008).
- **Dependencies / proposed order:** [WI-01](#vs01-wi-01), [WI-02](#vs01-wi-02), [WI-03](#vs01-wi-03), [WI-04](#vs01-wi-04), [WI-05](#vs01-wi-05), [WI-06](#vs01-wi-06), [WI-07](#vs01-wi-07), [WI-08](#vs01-wi-08), [WI-09](#vs01-wi-09), [WI-10](#vs01-wi-10) Order rank 11; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-08](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-08), [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09); [DC-01](../03-design/VS-01_DETAILED_DESIGN.md#dc-01), [DC-02](../03-design/VS-01_DETAILED_DESIGN.md#dc-02), [DC-03](../03-design/VS-01_DETAILED_DESIGN.md#dc-03), [DC-04](../03-design/VS-01_DETAILED_DESIGN.md#dc-04), [DC-05](../03-design/VS-01_DETAILED_DESIGN.md#dc-05), [DC-06](../03-design/VS-01_DETAILED_DESIGN.md#dc-06), [DC-07](../03-design/VS-01_DETAILED_DESIGN.md#dc-07), [DC-08](../03-design/VS-01_DETAILED_DESIGN.md#dc-08), [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Mandatory applicable cases have versioned expected/actual evidence; no synthetic fixture substituted for real-source acceptance or fabricated market results.
- **Verification approach:** [VS01-T-01](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-01), [VS01-T-02](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-02), [VS01-T-03](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-03), [VS01-T-04](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-04), [VS01-T-05](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-05), [VS01-T-06](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-06), [VS01-T-07](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-07), [VS01-T-08](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-08), [VS01-T-09](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-09), [VS01-T-10](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-10), [VS01-T-11](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-11), [VS01-T-12](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-12), [VS01-T-13](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-13), [VS01-T-14](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-14), [VS01-T-15](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-15), [VS01-T-16](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-16), [VS01-T-17](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-17), [VS01-T-18](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-18), [VS01-T-19](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-19), [VS01-T-20](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-20), [VS01-T-21](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-21), [VS01-T-22](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-22), [VS01-T-23](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-23); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="vs01-wi-12"></a>

### VS01-WI-12 - Local restart restore and handover

- **Description:** Prove reproducible startup, persistent state and separate restore; record locks/environment/evidence and final no-scope-leak/baseline checks.
- **Requirement references:** [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001), [REQ-05-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-009), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008).
- **Dependencies / proposed order:** [WI-11](#vs01-wi-11) Order rank 12; independent items may be scheduled only after their dependencies and approval.
- **Architecture / contracts:** [ADR-08](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-08), [ADR-09](../02-architecture/ARCHITECTURE_DECISIONS.md#adr-09); [DC-03](../03-design/VS-01_DETAILED_DESIGN.md#dc-03), [DC-09](../03-design/VS-01_DETAILED_DESIGN.md#dc-09).
- **Acceptance criteria:** Owner can reproduce the executable app and safe restore using approved instructions; baseline unchanged; no production/broker deployment implied.
- **Verification approach:** [VS01-T-21](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-21), [VS01-T-22](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-22), [VS01-T-23](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#vs01-t-23); retain versioned evidence after execution.
- **Estimated complexity:** M.
- **Implementation readiness:** Blocked - SQ-07 scoped approvals/authorization and applicable SQ-01..06; actual-source acceptance also requires inspected permitted samples.

<a id="readiness"></a>

## 4. Independent second-pass implementation-readiness assessment

Assessment basis: read frozen requirement states independently of the proposal's preferred choices, verify contract/test mappings, then challenge failure cases. No human architecture approval, integrated-system test or data-source qualification is claimed.

Definitions:
- **Ready for implementation:** governing behavior/interfaces/criteria approved and sufficiently specified; prerequisites satisfied; separate implementation authorization still required.
- **Ready with conditions:** governing approvals/specification already sufficient; named external prerequisites remain. Never use this label to conceal an unapproved Proposed/Open governing requirement.
- **Blocked:** applicable approval/specification or critical semantic decision missing.

Current outcome: **0 Ready, 0 Ready with conditions, 10 Blocked**. Every capability has applicable Proposed/Open or insufficiently specified behavior and all architecture/DC choices are still Proposed. This is not a requirement to finish all six documents first.

| Capability | Current class | Minimum missing decision/evidence | Trace |
| --- | --- | --- | --- |
| <a id="vs01-cap-01"></a>VS01-CAP-01: Configurable Gold/Silver ETF watchlist | Blocked | SQ-01; scoped instrument/watchlist contract approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-02"></a>VS01-CAP-02: Real historical CSV import | Blocked | SQ-01/02; source-use qualification and canonical CSV contract; actual sample for real-data acceptance; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-03"></a>VS01-CAP-03: Validate and persist observations | Blocked | SQ-02/03; schema, transaction and quality-policy approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-04"></a>VS01-CAP-04: Historical price charts | Blocked | SQ-02/03; chart/series/source contract approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-05"></a>VS01-CAP-05: Deterministic technical indicators | Blocked | SQ-04; formula, seed, gap/basis and precision criteria approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-06"></a>VS01-CAP-06: Supported ETF comparisons | Blocked | SQ-05; common-date, basis and price-only comparison approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-07"></a>VS01-CAP-07: Provenance freshness and quality disclosure | Blocked | SQ-03; unknown publication/calendar/freshness behavior approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-08"></a>VS01-CAP-08: Missing stale duplicate and invalid data behavior | Blocked | SQ-02/03; explicit reject/warn/unassessed policy approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-09"></a>VS01-CAP-09: Automated backend and frontend verification | Blocked | SQ-06/07; scoped test/tooling and acceptance criteria approval; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |
| <a id="vs01-cap-10"></a>VS01-CAP-10: Reproducible local development startup | Blocked | SQ-06/07; local security/recovery/runtime approval and later installation authorization; ADR/DC scoped approval and SQ-07. | [Full chain](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#3-requirements---architecture---design---task---test-matrix) |

### 4.1 Approval, source and technical blockers

| Area | Current finding / resolution |
| --- | --- |
| Architecture approvals | ADR-01..10 Proposed. Existing Python/FastAPI/PostgreSQL direction is retained; frontend/access/ORM/chart/test/runtime choices need adoption. |
| Requirements decisions | Parent Proposed/Open states stay unchanged. Explicitly approve the bounded VS-01 behavior/criteria traced to them; do not approve their entire future R1 scope by implication. |
| Data source | No real file sample, ETF universe/coverage, mapping or permission evidence inspected. SQ-01 blocks actual real-source acceptance/access. An approved canonical-parser task may later use labeled synthetic fixtures while awaiting the sample. |
| Financial/semantic policy | SQ-02..05 cover no-overwrite/idempotence, dates/calendars/gaps/basis, indicator seeds/precision and comparison meaning. No strategy thresholds are needed for research-only scope. |
| Technical uncertainties | Compatible lock set, Docker daemon/port availability, chart bundle cost and bounded import performance remain unmeasured; resolve during authorized setup/verification, not by claiming a current spike. |
| Security | SQ-06 needs local access/secret/origin/file/retention/restore approval. No LAN/public exposure or personal portfolio fields. |
| Testing prerequisites | Approved contracts/reference values, isolated PostgreSQL and browser/runtime installation after authorization; actual samples for real-data acceptance. |
| External dependencies | Approved future download of runtime libraries/images/browser binaries; permitted user CSV; no paid account/provider/broker connection. |

### 4.2 Counterexample review and residual limitations

The design explicitly addresses mixed source/basis selection, unknown publication/calendar, duplicate conflict/transaction rollback, uncertain commit replay, recursive indicator window seeding, corporate-action gaps, empty comparison intersection, stale UI response and malicious local-browser requests.

Known limits are deliberate proposals: daily-only bounded CSV; conflicting corrections rejected; no total-return/NAV/spread model without inputs; no retrospective point-in-time qualification; no authoritative calendar inferred; no actual trade/AI/scheduler capability. These are not a claim that complete R1 is delivered.

A single scoped approval can resolve the design/requirements gate without editing the historical tagged baseline. Record the human decision against ADR/DC IDs and the applicable parent requirement scope before implementation; broader parent statuses/maturity remain unchanged unless explicitly authorized through change control. Architecture-only approval leaves coding blocked.

<a id="approval-package"></a>

## 5. Human approval package

### 5.1 Architecture and design choices to adopt or amend

- ADR-01..10: modular monolith; React/TypeScript/Vite; PostgreSQL with sync SQLAlchemy/psycopg/Alembic; bounded CSV atomicity; provenance; Decimal indicators; local Plotly; pytest/Vitest/Testing Library/Playwright; local Compose/access/restore; explicit quality/comparison semantics.
- DC-01..09: identity/watchlists, canonical CSV/source qualification, eight-table persistence/idempotence, temporal/quality/freshness, formula/precision/seed, price-only comparison, REST/error/resource, UI and local security/runtime contracts.
- VS01-T-01..23: observable verification and acceptance, including correctly labeled synthetic references versus permitted real market-data acceptance.

These approvals must also explicitly approve the scoped governing behavior traced to Proposed/Open parents; approval of preferred libraries alone is insufficient. The frozen baseline classifications are not silently promoted.

### 5.2 Questions needing human disposition

<a id="sq-01"></a>

#### SQ-01 - Dataset and instrument qualification

- **Decision / evidence:** Confirm intended Gold/Silver ETF listings and supply or identify permitted real historical CSVs plus source/usage evidence. No sample was inspected; Dhan/Yahoo are not qualified by name alone.
- **Existing question/requirement trace:** S1-Q-001/002/003; R1-Q-001.
- **What it blocks:** Actual data access and real-data end-to-end acceptance; canonical-parser coding may use labeled synthetic fixtures after approval.
- **Status:** Open. Approve the concrete proposed DC policy or state the needed alternative; no value/default is inferred.

<a id="sq-02"></a>

#### SQ-02 - Import and series contract

- **Decision / evidence:** Approve daily-only canonical CSV, explicit listing/source/basis/currency, atomic rejection, exact-duplicate skipping, conflict rejection and no silent correction/overwrite.
- **Existing question/requirement trace:** S1-Q-003/005; REQ-02-011/013.
- **What it blocks:** Ingestion/persistence contract implementation.
- **Status:** Adopted by Step 3 for the scoped import/series contract.

<a id="sq-03"></a>

#### SQ-03 - Quality time and calendar behavior

- **Decision / evidence:** Approve date precision, null publication times, missing/unknown-calendar disclosures, strict known-gap handling and freshness UNASSESSED unless an approved calendar/cutoff profile exists.
- **Existing question/requirement trace:** S1-Q-004/005/014; R1-Q-011.
- **What it blocks:** Quality/freshness and affected analytical behavior.
- **Status:** Adopted by Step 3 for explicit unknown/unassessed behavior; no calendar or cutoff is inferred.

<a id="sq-04"></a>

#### SQ-04 - Research indicator conventions

- **Decision / evidence:** Approve SMA, SMA-seeded EMA and Wilder RSI, explicit n, warm-up/flat/gap/basis behavior, Decimal precision 34 with HALF_EVEN and 12-place derived serialization; these are computation conventions, not trading thresholds.
- **Existing question/requirement trace:** S1-Q-006/009; REQ-03-007; REQ-06-006.
- **What it blocks:** Indicator implementation and numerical acceptance.
- **Status:** Resolved for VS-01 by the human Step 4 conventions on 2026-11-02; see the dated disposition. No baseline requirement state is promoted.

<a id="sq-05"></a>

#### SQ-05 - Comparison meaning

- **Decision / evidence:** Approve common-date same-currency/same-basis price-only comparisons, no fill-forward, raw-price corporate-action limitations and no NAV/spread/total-return claims without inputs.
- **Existing question/requirement trace:** S1-Q-008/009; R1-Q-015.
- **What it blocks:** Comparison implementation and claims.
- **Status:** Resolved for VS-01 by the human Step 4 conventions on 2026-11-02; see the dated disposition. No baseline requirement state is promoted.

<a id="sq-06"></a>

#### SQ-06 - Local security and recovery

- **Decision / evidence:** Approve loopback-only deployment, one local token in memory in the UI, no token in frontend build, source/raw-row retention policy and manual backup/restore acceptance; no arbitrary RPO/RTO/SLA.
- **Existing question/requirement trace:** S1-Q-011/016; R1-Q-012.
- **What it blocks:** State-changing APIs and reproducible personal-use startup.
- **Status:** Conditionally approved by Step 3 for the documented local controls; owner-data retention/cutover acceptance remains pending.

<a id="sq-07"></a>

#### SQ-07 - Scoped approval and implementation grant

- **Decision / evidence:** Explicitly approve only the VS-01 behavior/criteria traced to Proposed/Open parents, ADR-01..10 and DC-01..09, and separately authorize the specified work items and routine project dependency/container setup.
- **Existing question/requirement trace:** S1-Q-016; REQ-BL-1.0 section 9.
- **What it blocks:** All production implementation until a documented human grant; approval of architecture alone is insufficient.
- **Status:** Step 3/4 scoped grants recorded; only the listed work items and applicable research verification/operations are authorized.

### 5.3 Historical Step 2 proposed implementation authorization

A future human grant can say:

> Approve ADR-01 through ADR-10, DC-01 through DC-09 and VS01-T-01 through VS01-T-23 with any listed amendments. Approve their explicitly scoped VS-01 requirement behavior/criteria under the referenced parent IDs without blanket approval or rewriting REQ-BL-1.0. Record the SQ-01 through SQ-07 dispositions. Authorize VS01-WI-01 through VS01-WI-12 for the local Gold/Silver ETF Research Dashboard, including routine project dependency/browser/image installation and local Docker setup. Use only permitted real data, with labeled synthetic fixtures for controlled tests; do not claim real-source acceptance until the samples/rights/coverage checks pass. Exclude paid accounts, broker connections, real orders, trading strategies/recommendations, paper/manual portfolios, ML/LLM integration and deployment beyond the approved local boundary.

This text is a proposal for review, not an instruction to execute. If data remains unavailable, explicitly authorize only canonical-contract development/testing and leave real-source acceptance blocked. No further general six-document cycle is needed once applicable scoped questions and approvals are recorded.

## 6. Step 2 completion and validation record

- Baseline tag verified as annotated and resolving to the expected e10eef55fb21368e53dbe4599006b620cbb48566 commit before authoring; nine authority files captured for unchanged-hash verification.
- Six authorized Markdown artifacts only; no baseline edit, application source, test implementation, dependency installation, Docker artifact, paid service/account or code spike.
- Ten capabilities, ten Proposed ADRs, nine Proposed DCs, 23 designed test cases and 12 blocked implementation work items form the checked chain.
- Thirty parent requirement IDs are valid and their approval/maturity/priority/applicability/increment fields remain copied unchanged.
- Links/anchors, ID uniqueness, work dependency acyclicity, capability/test coverage, numerical fixture expectations and cross-document conventions are checked as documentation QA.
- No product test, market-data qualification, performance result, restoration exercise or runtime readiness is asserted.
- Submit the concise package for human approval; do not begin implementation, stage/commit/tag these documents, or amend requirements under the current task.


## Step 4 disposition - 2026-11-02

The human Step 4 grant authorizes WI-07, WI-08, WI-10 and applicable research verification/operational portions of WI-11/12. WI-07 and WI-08 each depend on existing WI-06; WI-10 follows WI-07/08/09, then applicable WI-11/12. Historical blocked/proposed statements above are retained as the original planning record and do not override this dated scoped grant.

SQ-04 resolved: explicit SMA/EMA n>=1, RSI n>=2; documented Decimal, seeding, warm-up/flat/gap/unknown-basis behavior. SQ-05 resolved: same-currency/compatible-basis common-date price-only comparisons; no filling or total-return claims. SQ-07 granted only for the described research scope. SQ-01 remains Open; no real-source acceptance or external download is approved. No broader baseline status changes or trading/portfolio/broker/AI implementation. Executed evidence is recorded in [Step 4 completion](VS-01_STEP4_COMPLETION.md); WI-11/12 remain partial as stated above.
