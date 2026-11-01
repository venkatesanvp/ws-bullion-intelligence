# Stage 1 Requirements Outline Package

**Version:** 0.2 - R1 scope and refinement review update  
**Date:** 1 November 2026 (Asia/Calcutta)  
**Artifact status:** Authorized Stage 1 update; R1 scope approved with refinements, detailed policies/readiness still under review.  
**Companion:** [Prioritized requirements backlog](STAGE_1_REQUIREMENTS_BACKLOG.md)

## 1. Purpose and limits

Establish the authoring foundation for six specifications without authoring those specifications or beginning implementation planning. The human approved the package structure, independent maturity tracking, and documentation of a proposed change-impact convention, then authorized R1 scope and refinement updates to these two files only.

Approved product scope, proposed requirements elaborations and proposed release allocations remain distinct. No approved decision is modified. No code, scaffolding, dependencies, real trades, broker connections, provider commitments, financial defaults or implementation architecture selections are authorized. Paper trading and manually recorded actual transactions are approved R1 scope, explicitly separate from real execution and broker verification.

The ₹20 lakh reference is hypothetical and configurable. Swing (5-20 trading days), tactical (1-3 months) and strategic (6-24 months) remain independent. Phase 1 financial analytics are deterministic; Phase 2 ML requirements and extension needs must be documented during Phase 1, with ML implementation reserved for Phase 2.

## 2. Sources and authority

Read on 1 November 2026 (Asia/Calcutta).

| Source key | Source | Authority and use |
| --- | --- | --- |
| AGENTS | [AGENTS.md](../../AGENTS.md) | Repository governance, no unauthorized implementation/execution, reproducibility and traceability constraints. |
| D-01 through D-16 | [Decision register](../00-project-context/DECISION_REGISTER.md) | Authoritative approved product baseline v0.4; pending details remain pending. |
| PROJECT_OVERVIEW | [Project overview](../00-project-context/PROJECT_OVERVIEW.md) | Product context and scope; does not silently override approved decisions. |
| DISCUSSION_SUMMARY | [Discussion summary](../00-project-context/DISCUSSION_SUMMARY.MD) | Rationale, analytical scope and candidate sources; candidates are not verified providers. |
| REQUIREMENTS_INDEX | [Requirements index](../00-project-context/REQUIREMENTS_INDEX.md) | Accepted six-document package; detailed specifications are not finalized. |
| OPEN_QUESTIONS | [Open questions](../00-project-context/OPEN_QUESTIONS.md) | Unresolved topics, not approved requirements; existing numbered items remain unchanged. |
| User-Stage1 | Stage 1 task and approved structure in this conversation | Authorizes these two artifacts and confirms the ₹20 lakh configurable hypothetical reference; does not approve new product details. |
| User-Stage1-Approval | Human approval with refinements A and B in this conversation | Authorizes independent maturity tracking and documentation of a proposed change-impact convention. |
| Human-R1-Approval | R1 direction and subsequent approval with refinements A-D in this conversation, 1 November 2026 | Authorizes updating these two artifacts with cumulative R1-A/B/C scope, separate validation/performance records, recommendation lifecycle and logical execution boundaries. No decision amendment or implementation authorization. |

Source authority rules:
- Preserve D-01 through D-16 verbatim in meaning. An elaboration cannot supersede a decision.
- Use Approved only for a faithful approved obligation; new detail remains Proposed and unresolved behavior remains Open.
- Approval of artifact creation alone does not approve all backlog details. Human-R1-Approval separately approves its explicit R1 obligations/refinements; detailed policies, thresholds and new elaborations still require review.
- A genuine conflict requires a human ruling. Record affected IDs and the uncertainty rather than resolving it silently.
- The user explicitly confirmed ₹20 lakh; existing source files displaying "?20 lakh" remain unedited.
- The actual discussion filename ends in .MD. Source encoding defects and traceability separators are noted, not repaired here.
- No web/provider research or export inspection was performed for Stage 1. Data suitability and licensing remain unverified.

## 3. Classification, maturity and traceability

### 3.1 Stable identifiers and single ownership

- Documents: REQ-01 through REQ-06.
- Atomic backlog records: REQ-01-001, REQ-02-001, etc. Never reuse an identifier; retain a withdrawn record with its reason if later authorized.
- Approved decisions: existing D-01 through D-16.
- Stage 1 questions: S1-Q-001, etc.; link the original numbered question without renaming it.
- Data dependencies: DATA-001 through DATA-007.
- Acceptance increments: R1-A / R1-B / R1-C are distinct from implementation phases and are cumulative within one R1 release.
- Planned verification: VER-01-001 corresponds to REQ-01-001, and similarly for other records. These are planned cases, not executed tests.
- Every requirement has exactly one owning document. Related documents reference its ID rather than redefine its normative behavior.
- Candidate accountable roles are proposals; no named person or approval authority is assigned by this package.

### 3.2 Approval status is independent of maturity

| Approval status | Meaning |
| --- | --- |
| Approved | The obligation is explicitly approved in the cited decision, repository governance, or human instruction. This does not automatically approve proposed test detail, priorities or phase allocations. |
| Proposed | New elaboration, requirement detail or governance mechanism awaiting human review. |
| Open | An identified requirement area whose normative behavior depends on a missing decision or evidence. It is not a completed specification. |

| Maturity | Meaning and evidence needed |
| --- | --- |
| Identified | The need and source are recorded; unresolved choices prevent complete analysis/specification. |
| Analyzed | Scope, rationale, dependencies, data assumptions and reviewable verification expectations are recorded. Open details may remain. |
| Specified | Normative behavior and acceptance criteria are complete enough to assess without material unresolved placeholders. |
| Verified for readiness | A requirements review has checked clarity, consistency, feasibility, traceability and testability; evidence is recorded. This is not a claim of implemented functionality. |
| Baselined | A human-authorized controlled requirements version is recorded after the applicable readiness review. |

No record is promoted merely because these files are created or a count/link check passes. Approved/Analyzed and Open/Identified are valid combinations; approval and maturity transitions are separate events. Stage 1 assigns no record Verified for readiness or Baselined.

### 3.3 Category, priority and phase

Categories distinguish business scope/outcomes, market data/contracts/governance, analytics/strategy/confidence, ETF/trade planning/portfolio risk, AI interaction/evidence, system interfaces/security/nonfunctional qualities, validation/release governance and ML extensibility.

Priority is a recommendation relative to the proposed delivery context:
- Must: necessary to accept an included capability, enforce an approved boundary, or establish its requirements baseline.
- Should: important but release allocation/deferral requires explicit review.
- Could: optional for the proposed delivery context.

A Should label does not revoke approved scope. A Must label does not authorize implementation or force every long-term capability into the first release.

Phase 1 / Phase 2 / Future is a proposed delivery allocation, separate from approval. The human has approved mandatory R1 workflow and refinements. R1-A/B/C are proposed acceptance increments within that release; detailed coverage/policies/acceptance remain open. The approved D-09 boundary remains binding: deterministic Phase 1, Phase 2 ML implementation, with Phase 2 requirements and extension needs documented during Phase 1. Phase 1 is not automatically synonymous with the first release.

### 3.4 Record schema and acceptance detail

Each record contains ID, title, requirement description, source, category, priority, proposed phase, dependencies, data assumptions, verification approach, acceptance criteria, approval status and maturity. Owning document, open-question links, planned verification ID and scope/phase approval notes are also supplied.

For an Approved record, only the faithfully sourced obligation is approved; proposed operationalization and review cases are not new approved product details. For an Open record, acceptance criteria state the evidence needed to close/specify the question; functionality acceptance remains incomplete until that ruling is made. No invented financial thresholds, strategy weights, confidence probabilities, costs or service targets are introduced.

### 3.5 Traceability chain

Source/business objective -> approved decision where applicable -> requirement -> DATA/question dependencies -> planned verification -> future acceptance evidence.

Later design/code/test links are intentionally unpopulated. Dependency means a semantic/input prerequisite, not an implementation sequence. Verification IDs describe future evidence needs and do not authorize scripts, testing infrastructure or code.

The backlog owns the detailed S1-Q and R1-Q registers, data register, per-decision coverage and complete added/revised ID lists. R1 scope and increment contracts below are shared consistently across both artifacts.

The backlog owns the detailed question/data registers and per-decision coverage matrix. The outline owns document boundaries and this conventions definition; the backlog references them.

### 3.6 Release-blocking classification

A blocker must name the release capability or acceptance claim it prevents. Dataset rights/coverage can block a dependent model without proving that every unrelated capability is blocked. Deferral must be approved through the release-scope question; no automatic reduced release is assumed.

Separate:
- Release-baseline blockers: first-release scope, permitted operation, approval authority and relevant acceptance gates.
- Capability blockers: data quality/coverage, strategy/risk rules, broker semantics, confidence/replay evidence, schedules and assistant policy for included capabilities.
- Nonblocking at Stage 1: frontend selection and future-instrument details, except where required to complete later design/extension acceptance.
- Phase 1 ML-readiness questions: not a reason to implement ML early; unresolved requirements still affect acceptance of D-09 readiness work.

## 4. Proposed specification outlines

The sections below are tables of contents and authoring/review contracts, not completed requirements specifications. Each candidate owner role needs human assignment. Inputs describe requirements dependencies rather than build order.

### 4.1 REQ-01 - Product Vision and Business Requirements

- **Purpose:** Define investor needs, outcomes, product boundaries and the distinction between approved product scope and a proposed first release.
- **Scope and exclusions:** Business requirements for gold/silver intelligence, initial Indian ETF investments, contextual markets, three independent horizons, advisory workflows and the configurable ₹20 lakh hypothetical portfolio. Excludes formulas, provider schemas, UI framework and infrastructure choices.
- **Proposed requirements ownership:** Product owner accountable; investor/stakeholder representatives review; quantitative/risk and data owners consulted. Roles require human assignment.
- **Inputs and dependencies:** D-01 through D-07, D-15 and D-16; project overview; discussion rationale; data feasibility findings; human workflow and risk inputs.
- **Expected outputs:** Business objectives/personas; workflow acceptance scenarios; initial investment-universe rules; approved-scope versus proposed-release matrix; explicit exclusions and unresolved decisions.
- **Acceptance and review criteria:** Every approved product boundary is covered; each workflow has an observable outcome; no actual portfolio or account integration is inferred; release recommendations are labeled proposed; quantitative/technical details are referenced rather than duplicated.
- **Cross-document relationships:** REQ-02 establishes feasibility; REQ-03 supplies strategy/trade semantics; REQ-04 supplies interactions; REQ-05 supplies operating constraints; REQ-06 supplies acceptance evidence.
- **Open decisions:** [S1-Q-001](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-001), [S1-Q-007](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-007), [S1-Q-014](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-014), [S1-Q-017](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-017).

**Approved R1 authoring impact:** R1 scope now includes a functional personal-use workflow, paper trading and manually maintained actual transactions. The default remains hypothetical; no actual opening capital is inferred. Outputs add the approved R1 capability and proposed acceptance-increment matrices.

**Proposed sections and subsections**

- 1. Purpose, authority and business context
  - 1.1 Baseline, stakeholders and source references
  - 1.2 Terminology and approved versus proposed content
- 2. Vision, outcomes and success measures
  - 2.1 Investor decisions supported
  - 2.2 Measurable outcomes and unapproved targets
- 3. Users and operating context
  - 3.1 Personas and expertise assumptions
  - 3.2 Hypothetical versus user-entered portfolio information
- 4. Asset and instrument scope
  - 4.1 Gold/silver as primary assets; other markets as context
  - 4.2 Initial Indian Gold/Silver ETF universe
  - 4.3 Future US ETFs and MCX futures investment boundaries
- 5. Investment horizons
  - 5.1 Swing: 5-20 trading days
  - 5.2 Tactical: 1-3 months
  - 5.3 Strategic: 6-24 months
  - 5.4 Independent strategies and consolidated exposure needs
- 6. Business workflows
  - 6.1 Dashboard and conversational research
  - 6.2 Evidence-supported trade planning and no-trade
  - 6.3 EOD reports, event reassessment and prior-research comparison
- 7. Portfolio and execution boundaries
  - 7.1 Configurable ₹20 lakh hypothetical reference
  - 7.2 Allocation/risk decisions and manual state needs
  - 7.3 Human order placement; excluded autonomous execution
- 8. Scope and release classification
  - 8.1 Approved long-term capabilities
  - 8.2 Proposed first-release inclusion and deferrals
  - 8.3 Explicit exclusions and data-conditional capabilities
  - 8.4 R1-A Research Platform, R1-B Validated Trade Planning and Paper Trading, R1-C Manual Trading Support and Personal-Use Readiness
  - 8.5 Paper versus manually maintained actual portfolio outcomes and unverified provenance
- 9. Business acceptance and dependencies
  - 9.1 End-to-end scenario outcomes
  - 9.2 Data feasibility and cross-specification references
- 10. Open questions and review record
  - 10.1 Release blockers versus nonblocking questions
  - 10.2 Approval authority, change history and traceability

### 4.2 REQ-02 - Market Data and Indicator Requirements

- **Purpose:** Define what market evidence is needed, what its fields mean, when it was knowable and what rights/quality permit its use.
- **Scope and exclusions:** Provider-independent dataset and metadata requirements; data quality, discovery qualification, historical/vintage coverage and acquisition constraints. Excludes analytical scoring and assistant orchestration behavior.
- **Proposed requirements ownership:** Market-data requirements owner accountable; quantitative and validation reviewers; permissions/legal specialist where needed. Provider approval remains human.
- **Inputs and dependencies:** D-01, D-04, D-12, D-14 and D-16; REQ-01 use cases; REQ-03 input needs; representative exports and documented source terms, not assumed API access.
- **Expected outputs:** Dataset/field catalog; source/permission evidence; semantic and timestamp contracts; coverage/quality matrices; fallback qualification criteria; historical limitations.
- **Acceptance and review criteria:** Each included field has units, identity and temporal meaning; candidates are not presented as verified; licensing and absent history are explicit; data gates have measurable approved criteria or open questions; derived fields reference their analytical owner.
- **Cross-document relationships:** REQ-03 consumes canonical fields; REQ-04 requests qualified evidence; REQ-05 preserves contracts operationally; REQ-06 verifies QA and point-in-time suitability.
- **Open decisions:** [S1-Q-002](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-002), [S1-Q-003](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-003), [S1-Q-004](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-004), [S1-Q-005](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-005).

**Approved R1 authoring impact:** Inputs add simulation observation requirements and DATA-008 manual records. Outputs distinguish market availability from user report time and separate historical vintages from newly arriving forward evidence. Data rights, granularity and quality decisions remain open.

**Proposed sections and subsections**

- 1. Scope and data-use scenarios
  - 1.1 Intelligence versus investment/execution inputs
  - 1.2 Mandatory, optional and release-conditional datasets
- 2. Dataset inventory
  - 2.1 COMEX futures contracts, prices, OI, volume and curves
  - 2.2 MCX futures and expiry/session metadata
  - 2.3 COMEX options strikes, expiries, quotes, IV and Greeks
  - 2.4 USD/INR and DXY
  - 2.5 Fed policy/implied rates, nominal/real yields and CPI/PCE/PPI/jobs
  - 2.6 COT, oil/copper, physical markets and inventories
  - 2.7 Indian ETF prices, NAV, flows, fund and adjustment metadata
- 3. Source qualification and permissions
  - 3.1 Provider catalog and intended usage rights
  - 3.2 Commercial/noncommercial retrieval, storage and display constraints
  - 3.3 Candidate discovery qualification and acquisition budget
- 4. Candidate feasibility evidence
  - 4.1 Dhan export inspection and coverage limitations
  - 4.2 Yahoo series-by-series fallback validation
  - 4.3 Licensed or unavailable data dependencies
- 5. Canonical semantics
  - 5.1 Instrument identifiers, contracts, expiries and historical membership
  - 5.2 Units, currency quotes, multipliers and adjustment metadata
  - 5.3 Calendars, time zones, sessions and cross-market alignment
  - 5.4 Paper trigger/fill/mark evidence and limitations
  - 5.5 Manual event time, recording time, source and incomplete transaction inputs
- 6. Temporal and revision contracts
  - 6.1 Observation, publication, availability and ingestion time
  - 6.2 Macro vintages and source corrections
  - 6.3 As-of eligibility and provenance retention
  - 6.4 Historical versus newly arriving forward observations and correction lineage
- 7. Quality and freshness
  - 7.1 Completeness, validity, consistency and duplicate handling
  - 7.2 Dataset-specific cadence and quality gates
  - 7.3 Stale/missing/conflicting evidence and downstream consequences
- 8. Historical coverage and provider independence
  - 8.1 Horizon-specific history and vintage sufficiency
  - 8.2 Futures-roll metadata and ETF adjustments
  - 8.3 Replacement-source compatibility and fallback limitations
- 9. Data acceptance and verification
  - 9.1 Representative sample evidence
  - 9.2 Permission/coverage/quality acceptance matrix
- 10. Dependencies and unresolved decisions
  - 10.1 Data-blocked analytical capabilities
  - 10.2 Open questions, review authority and traceability

### 4.3 REQ-03 - Quantitative Analytics, Strategies and Trade Planning

- **Purpose:** Define deterministic financial meaning, separate analytical models, independent strategy decisions and evidence-supported portfolio/trade plans.
- **Scope and exclusions:** Analytics, confidence, horizon-specific rules, ETF execution assessment, portfolio risk and canonical/broker-rendered GTT semantics. Excludes provider acquisition, conversational wording and order execution.
- **Proposed requirements ownership:** Quantitative requirements owner accountable; human portfolio/risk approver for financial policy; ETF and broker-domain reviewers consulted.
- **Inputs and dependencies:** D-02, D-05, D-06, D-08 through D-12 and D-15; REQ-01 outcomes; REQ-02 contracts/coverage; human risk/strategy settings; REQ-06 evidence standards.
- **Expected outputs:** Calculation/model contracts; strategy rules; confidence definitions; risk and sizing policy; canonical plan semantics; capability-aware rendering criteria; no-trade and lifecycle cases.
- **Acceptance and review criteria:** Financial results are deterministic and independently verifiable; models/horizons remain distinct; portfolio exposure reconciles; no financial thresholds are invented; zero-to-three scenarios and up-to-two broker representations retain approved semantics; data gaps and unsupported capabilities are explicit.
- **Cross-document relationships:** REQ-02 owns inputs; REQ-04 explains outputs without recalculating them; REQ-05 preserves interface semantics and capability evidence; REQ-06 owns independent verification and backtest protocols.
- **Open decisions:** [S1-Q-004](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-004), [S1-Q-006](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-006), [S1-Q-007](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-007), [S1-Q-008](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-008), [S1-Q-009](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-009), [S1-Q-010](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-010), [S1-Q-015](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-015).

**Approved R1 authoring impact:** Scope adds virtual accounting/order semantics, recommendation lifecycle, separate performance classes, manual actual accounting and daily reassessment. Exact fill, risk, cost, accounting and expiry policies remain open. No service/API design or real execution is selected.

**Proposed sections and subsections**

- 1. Analytical authority and output types
  - 1.1 Deterministic Phase 1 versus Phase 2 ML
  - 1.2 Descriptive, diagnostic, predictive and prescriptive claims
- 2. Calculation and model contracts
  - 2.1 Inputs, units, parameters, versions and missing-data behavior
  - 2.2 Independent model outputs
  - 2.3 Agreement/disagreement reconciliation and proposed weights
- 3. Analytical domains
  - 3.1 Macro regimes and currency/rates context
  - 3.2 Futures curves, carry, liquidity and positioning
  - 3.3 Options OI/volume, IV, skew and Greeks
  - 3.4 Technical indicators and warm-up conventions
  - 3.5 Gold/silver and cross-market relative value
- 4. ETF analysis and execution considerations
  - 4.1 Liquidity, spreads and NAV timing/premium-discount
  - 4.2 Tracking characteristics, charges and adjustments
  - 4.3 Observed execution evidence versus unavailable estimates
- 5. Independent investment strategies
  - 5.1 Swing rules and validation
  - 5.2 Tactical rules and validation
  - 5.3 Strategic rules and validation
  - 5.4 Entry/exit/invalidation, benchmarks and no-trade conditions
- 6. Confidence dimensions
  - 6.1 Signal strength
  - 6.2 Historical reliability and unknown/insufficient evidence
  - 6.3 Data quality and non-probability presentation rules
- 7. Portfolio and risk policy
  - 7.1 Hypothetical reference and configurable inputs
  - 7.2 Allocation, sizing, cash and rounding
  - 7.3 Cross-horizon attribution, concentration and correlated exposure
- 8. Trade-plan semantics
  - 8.1 Entry, exit, stop, target and risk/reward
  - 8.2 Evidence-supported zero-to-three GTT alternatives
  - 8.3 Shared capital, exclusivity and multiple-trigger scenarios
- 9. Canonical and broker representations
  - 9.1 One canonical deterministic/explainable plan
  - 9.2 Up to two verified broker-specific renderings
  - 9.3 Unsupported capabilities, linked exits, OCO and fill limitations
- 10. Plan and portfolio lifecycle
  - 10.1 Validity, expiration, cancellation and reassessment
  - 10.2 Manual state, partial fills and plans versus orders
  - 10.3 Versioned recommendation states, evidence timestamps, validity and strategy/risk checks
  - 10.4 Virtual cash, positions and simulated order transitions
  - 10.5 Entry/exit activation, fills, gaps and ambiguous bar sequence
  - 10.6 Costs, slippage, liquidity and partial fills
  - 10.7 Expiration, cancellation, reservation and alternative-scenario interaction
  - 10.8 User-reported actual orders/fills, opening state, cash flows and corrections
  - 10.9 Separate P&L, return, drawdown and benchmark methodology
  - 10.10 Simulation history, reproducibility and daily recommendation/position reassessment
  - 10.11 Broker-neutral human placement instructions; no broker connection
- 11. Phase 2 ML analytical needs
  - 11.1 Target/label/horizon requirements documented in Phase 1
  - 11.2 Phase 2 capability and unresolved selection/evidence needs
- 12. Acceptance and traceability
  - 12.1 Worked examples and independent verification references
  - 12.2 Open risk/strategy/broker decisions

### 4.4 REQ-04 - Interactive AI Research Assistant

- **Purpose:** Specify how users request, inspect, question and retain evidence-based research, while AI interpretation remains advisory.
- **Scope and exclusions:** Dashboard/chat interaction requirements, evidence presentation, proactive input gathering, what-if research, saved context, scheduled reports and event investigations. Excludes calculation ownership, scheduler implementation and autonomous execution.
- **Proposed requirements ownership:** AI product requirements owner accountable; product, quantitative, validation and security reviewers consulted.
- **Inputs and dependencies:** D-01, D-03, D-07, D-10, D-13 and D-16; REQ-01 workflows; qualified REQ-02 evidence; REQ-03 results; approved tool/context policies.
- **Expected outputs:** Interaction/use-case catalog; research/interpretation contracts; chart and citation expectations; tool/context policy questions; scheduled/event content acceptance cases; assistant evaluation scenarios.
- **Acceptance and review criteria:** Every material market claim is attributable; generated interpretation is distinguishable from calculations; unsupported requests and missing inputs have observable behavior; retrieved content cannot grant authority; no broker execution/account access is introduced.
- **Cross-document relationships:** REQ-02 qualifies discovered evidence; REQ-03 owns numbers and confidence meanings; REQ-05 owns operating interfaces, scheduling and security; REQ-06 owns evaluation methods.
- **Open decisions:** [S1-Q-001](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-001), [S1-Q-005](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-005), [S1-Q-011](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-011), [S1-Q-012](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-012), [S1-Q-013](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-013), [S1-Q-014](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-014).

**Approved R1 authoring impact:** Interaction requirements add visible paper/manual modes, recommendation states, unverified actual records, prior-version evidence and separated performance presentation. Generated text cannot grant execution authority or alter deterministic figures.

**Proposed sections and subsections**

- 1. Scope, users and advisory boundary
  - 1.1 Permitted L1-L4 actions and excluded L5 execution
  - 1.2 Unsupported requests and explicit authorization boundaries
- 2. Research entry points
  - 2.1 Dashboard and conversational intents
  - 2.2 Follow-up questions and contextual-market requests
- 3. Evidence discovery and orchestration
  - 3.1 Missing-input identification and targeted questions
  - 3.2 Permitted automatic retrieval and qualification handoff
  - 3.3 Tool permissions and disallowed actions
- 4. Research output semantics
  - 4.1 Sources, timestamps, provenance and uncertainty
  - 4.2 Generated interpretation versus deterministic financial output
  - 4.3 Separate confidence dimensions and unsupported claims
- 5. Visual and scenario interaction
  - 5.1 Chart series, units, transforms and as-of labels
  - 5.2 What-if assumptions and baseline comparisons
- 6. Context and research persistence
  - 6.1 Saved research and original evidence versions
  - 6.2 Conversational retention and prior-signal comparison
  - 6.3 Privacy and external-service data boundaries
- 7. Proactive research
  - 7.1 EOD report contents and incomplete-data disclosures
  - 7.2 Event investigation and reassessment narrative
  - 7.3 No-trade and changed-plan explanations
  - 7.4 Recommendation Draft/Validated/Published/terminal-state disclosures
  - 7.5 Paper workflow versus manually recorded actual transaction workflow
  - 7.6 Separate historical, forward paper, manual actual and benchmark performance labels
- 8. Trust and failure behavior
  - 8.1 Untrusted retrieved instructions and tool results
  - 8.2 Conflicting, stale, absent or unavailable evidence
  - 8.3 Research failures and user-visible limitations
- 9. Acceptance and evaluation scenarios
  - 9.1 Normal, missing-input and unsupported-action cases
  - 9.2 Citation, numerical-fidelity and uncertainty checks
- 10. Dependencies and open decisions
  - 10.1 Interaction constraints informing frontend choice
  - 10.2 Tool, retention, channel and release questions

### 4.5 REQ-05 - System Architecture and Nonfunctional Requirements

- **Purpose:** Capture approved technology constraints, logical interface obligations and measurable operating qualities without making pending architectural selections.
- **Scope and exclusions:** Logical responsibilities, semantic interfaces, security/privacy, scheduling, persistence, recovery, observability and extension requirements. Excludes scaffolding, service decomposition decisions, deployment implementation and financial formulas.
- **Proposed requirements ownership:** Architecture requirements owner accountable; security and operations reviewers consulted; user retains authority over pending technology/deployment choices.
- **Inputs and dependencies:** Accepted Python/FastAPI/PostgreSQL local Docker direction; D-04, D-09, D-11, D-14 and D-16; REQ-01 release needs; REQ-02/03/04 contracts; human deployment/access choices.
- **Expected outputs:** Constraint catalog; logical boundary/interface requirements; measurable NFR scenarios with unresolved targets; security/data-flow requirements; broker evidence needs; Phase 1 future-extension requirements.
- **Acceptance and review criteria:** Approved constraints are distinct from proposals; no Streamlit/React, broker, hosting, configuration or architecture pattern is silently chosen; NFR targets are measurable or explicitly open; persistent storage is not equated with backup; no execution or account connection is introduced.
- **Cross-document relationships:** Consumes business/data/analytics/assistant semantics; supplies operational and interface acceptance obligations to REQ-06; does not redefine their meanings.
- **Open decisions:** [S1-Q-002](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-002), [S1-Q-010](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-010), [S1-Q-011](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-011), [S1-Q-013](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-013), [S1-Q-014](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-014), [S1-Q-015](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-015), [S1-Q-016](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-016), [S1-Q-017](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-017).

**Approved R1 authoring impact:** Logical interface, persistence, privacy and recovery requirements extend to recommendations and portfolio records. No framework/service decomposition is prescribed. Future connectivity remains an assessment candidate, not a live R1 path.

**Proposed sections and subsections**

- 1. Architectural requirements authority
  - 1.1 Accepted technology constraints
  - 1.2 Pending choices and excluded implementation planning
- 2. Logical responsibilities and boundaries
  - 2.1 Data, analytics, strategy, risk, planning and interpretation
  - 2.2 Shared semantic contracts and error conditions
  - 2.3 Logical execution-mode isolation without service decomposition or framework selection
- 3. Evidence and version interfaces
  - 3.1 Input/output provenance and as-of context
  - 3.2 Configuration/rule/model version requirements
  - 3.3 Provider replacement compatibility
- 4. Broker capability boundary
  - 4.1 Evidence-backed rendering capabilities
  - 4.2 Unsupported semantics and no account/execution dependency
  - 4.3 Future connectivity/sync/placement/automation as assessment candidates only; D-03 unchanged
- 5. Security, privacy and access
  - 5.1 Actors, trust boundaries and authorization needs
  - 5.2 Secrets/configuration and prohibited repository content
  - 5.3 External AI data flows, personal information and retention
- 6. Scheduling and delivery
  - 6.1 EOD cutoffs, calendars and completion expectations
  - 6.2 Event channels, hours, deduplication and escalation
  - 6.3 Missing-input and interrupted-delivery behavior
- 7. Performance and resilience
  - 7.1 Workload, latency, capacity and availability measures
  - 7.2 Failure isolation, recovery objectives and degraded service
- 8. Persistence and recovery
  - 8.1 Local Docker persistent storage constraints
  - 8.2 Backup, restoration, retention and permission limits
  - 8.3 Attributable recommendation, paper and manual histories under privacy/recovery policy
- 9. Observability and maintainability
  - 9.1 Failures, versions, reports and alert audit evidence
  - 9.2 Sensitive-information protection in diagnostics
- 10. Extension requirements
  - 10.1 Phase 1 documentation of Phase 2 ML needs
  - 10.2 Future US ETF/MCX investment contract differences
- 11. Acceptance and open decisions
  - 11.1 Measurable NFR scenarios and verification references
  - 11.2 Frontend, deployment, configuration and approval questions

### 4.6 REQ-06 - Validation, Governance and Release Requirements

- **Purpose:** Define credible verification evidence, requirements review, change control and human release acceptance.
- **Scope and exclusions:** Calculation/data/assistant/security validation, point-in-time replay/backtests, evidence sufficiency, requirement maturity, traceability and release approval. Excludes asserting unmeasured performance or authorizing implementation.
- **Proposed requirements ownership:** Validation/governance requirements owner accountable; independent quantitative/security reviewers consulted; human approver and release authority remain to be named.
- **Inputs and dependencies:** AGENTS governance; D-09, D-10 and D-12; requirements and open questions from REQ-01 through REQ-05; source coverage evidence; human acceptance decisions.
- **Expected outputs:** Verification catalog; evaluation protocols; evidence and release-gate requirements; approval/maturity records; proposed change-impact template; Phase 2 ML evaluation-readiness questions.
- **Acceptance and review criteria:** Every requirement has planned verification and acceptance evidence; leakage, survivorship, rollover and execution assumptions are explicit; no test/performance claim is fabricated; governance proposals remain labeled; all phase/release approvals remain human.
- **Cross-document relationships:** References business outcomes, data contracts, calculation semantics, assistant behavior and NFRs from their owners; owns how evidence is assessed, not those requirements' financial meanings.
- **Open decisions:** [S1-Q-004](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-004), [S1-Q-006](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-006), [S1-Q-008](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-008), [S1-Q-009](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-009), [S1-Q-011](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-011), [S1-Q-012](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-012), [S1-Q-015](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-015), [S1-Q-016](STAGE_1_REQUIREMENTS_BACKLOG.md#s1-q-016).

**Approved R1 authoring impact:** Verification scope now distinguishes backtesting, OOS/walk-forward and forward paper evidence; tests accounting, lifecycle, mode isolation and cumulative personal-use readiness. Evidence periods, targets and transition authority remain human decisions.

**Proposed sections and subsections**

- 1. Validation scope and independence
  - 1.1 Claim types and evidence standards
  - 1.2 Reviewer roles and approval authority
- 2. Data and calculation verification
  - 2.1 Data contract/quality acceptance evidence
  - 2.2 Independent worked financial examples
  - 2.3 Units, timing, boundary cases and approved tolerances
- 3. Historical replay
  - 3.1 As-of eligibility, vintages and source revisions
  - 3.2 Historical universe and survivorship
  - 3.3 Futures rolls and configuration reproducibility
- 4. Backtest and predictive evaluation
  - 4.1 Execution timing, costs, spreads, adjustments and gaps
  - 4.2 Out-of-sample/walk-forward separation and benchmarks
  - 4.3 Selection bias, sample sufficiency and limitations
  - 4.4 Forward paper trading with newly arriving data and then-active versions
  - 4.5 Separate evidence/performance records; no invented validation periods or targets
- 5. Confidence evidence
  - 5.1 Signal strength versus reliability versus quality
  - 5.2 Unsupported probabilities and unknown reliability
- 6. Assistant evaluations
  - 6.1 Evidence attribution and numerical fidelity
  - 6.2 Missing data, prohibited actions and adversarial retrieval
  - 6.3 Recommendation lifecycle, mode boundaries and simulated/manual disclosure checks
- 7. Operational acceptance
  - 7.1 Access/secrets/privacy evidence
  - 7.2 Reporting/alert failure behavior and restore acceptance
  - 7.3 NFR measurements and approved targets
- 8. Requirements lifecycle
  - 8.1 Independent approval status and maturity
  - 8.2 Traceability and review evidence
  - 8.3 Proposed change-impact mechanism and decision escalation
- 9. Release governance
  - 9.1 Capability inclusion, blockers and approved deferrals
  - 9.2 Acceptance matrix, risk sign-off and release authority
  - 9.3 Cumulative R1-A/B/C gates: paper in R1-B, manual support/readiness in R1-C
  - 9.4 Independent accounting/reconciliation and separated benchmark/performance verification
- 10. Phase 2 ML readiness
  - 10.1 Targets/labels and leakage-free evaluation needs
  - 10.2 Baselines, version evidence, monitoring and approval
- 11. Review record and open decisions
  - 11.1 Evidence gaps and unresolved thresholds
  - 11.2 Human approvals and controlled baseline history

## 5. Cross-document ownership and duplication controls

| Subject | Single normative owner | Referencing consumers / review owner |
| --- | --- | --- |
| Users, business outcomes, universe and release boundaries | REQ-01 | All other documents; REQ-06 checks acceptance coverage. |
| Dataset meanings, permissions, timestamps, vintages and quality gates | REQ-02 | REQ-03 calculations; REQ-04 retrieval/evidence; REQ-05 preservation; REQ-06 data QA. |
| Models, formulas, strategies and reconciliation | REQ-03 | REQ-04 explanations; REQ-05 contracts; REQ-06 independent verification. |
| Confidence meanings and evidence needs | REQ-03 | REQ-02 supplies quality inputs; REQ-04 presents; REQ-06 assesses support. |
| ETF execution assessment, portfolio risk and canonical plan semantics | REQ-03 | REQ-02 supplies evidence; REQ-05 capability/interfaces; REQ-06 verifies. |
| Assistant behavior, charts, context and research content | REQ-04 | REQ-05 operations/security; REQ-06 assistant evaluations. |
| Data candidate qualification versus discovery interaction | REQ-02 qualification; REQ-04 interaction | Separate obligations linked by REQ-02-016 and REQ-04-004. |
| EOD/event research contents versus delivery mechanics | REQ-04 contents; REQ-05 scheduling/delivery | REQ-02 timestamps/quality; REQ-06 acceptance. |
| Security/privacy/service/recovery requirements | REQ-05 | REQ-04 interaction consequences; REQ-06 verification evidence. |
| Traceability, maturity, verification and release/change governance | REQ-06 | Each document supplies acceptance criteria and review records. |
| Phase 2 ML | REQ-03 targets/capability; REQ-05 Phase 1 extension requirements; REQ-06 evaluation governance | D-09 links the distinct obligations; no Phase 1 ML implementation. |

Complementary records are not duplicates: REQ-01 defines a horizon's business meaning, REQ-03 its independent rules, and REQ-06 the method of verification. A field/formula/threshold is defined once and referenced elsewhere. A change in ownership requires reciprocal reference review and human approval where controlled scope is affected.

## 6. Proposed requirements change-impact convention

**Status: Proposed governance convention.** The human authorized documenting this mechanism, not adopting it as a new approved product decision. REQ-06-011 tracks adoption. It cannot amend D-01 through D-16 or authorize implementation.

### 6.1 Trigger and scope

Use an assessment when a proposed requirement change, source/coverage change, data correction, analytical interpretation change, interface revision or phase/acceptance change may affect another controlled artifact. Editorial-only changes may receive a brief no-semantic-impact rationale; disputed classifications require human review.

### 6.2 Lightweight assessment record

Use this template inside the relevant future review record; no additional artifact is created by Stage 1.

| Field | Required assessment |
| --- | --- |
| Change reference and proposer | Stable reference, date, responsible proposer and reason. |
| Before/after and source | Exact proposed semantic change; source evidence; approval status and maturity before/after assessed independently. |
| Decisions and requirements | Affected D-IDs, owning/dependent requirement IDs and any approved obligation that would change. A decision change requires explicit human authorization before adoption. |
| Data and analytics | Affected DATA IDs, fields, units, timestamps/vintages, permissions, quality gates, models, horizons, portfolio/risk rules and historical comparability. |
| Architecture and interfaces | Affected logical contracts, consumers, configuration, security/data flows, broker capability evidence and unresolved interface behavior. Do not select an architectural option implicitly. |
| Verification and acceptance | Affected VER IDs, reference cases, confidence/performance claims, acceptance criteria and evidence that must be reassessed. Do not claim execution of these checks. |
| Delivery and dependencies | Affected Phase 1/Phase 2/Future proposals, first-release inclusion, blockers, documentation needs and later implementation dependencies. Record impact without creating an implementation plan. |
| Unknowns and alternatives | Explicit evidence gaps, assumptions, alternatives, potential incompatibilities and rollback/reversion implications at the requirements level. |
| Human disposition | Proposed / approved / rejected / deferred disposition, authorized reviewer, rationale and links to explicit approval. No approval may be inferred from silence. |

### 6.3 Review flow

1. Record the requested change and affected IDs.
2. Have the proposed owning reviewers assess all five impact domains; mark unknowns rather than assuming no impact.
3. Distinguish clarification, new elaboration and amendment of an approved decision.
4. Obtain the appropriate human ruling; decision amendments require explicit authorization.
5. Only after authorization, update permitted artifacts and reciprocal references, retaining prior rationale.
6. Reassess approval and maturity separately, and identify readiness evidence that is no longer applicable.

No named approver, branch protection policy or automatic enforcement is selected here. Those remain S1-Q-016. No product decision is changed by this proposed procedure.

## 7. Open questions and source tensions

The [backlog question register](STAGE_1_REQUIREMENTS_BACKLOG.md#question-register) owns detailed S1-Q IDs, affected capabilities, original-source links and candidate reviewers.

- Open question 2 says "first two" brokers; D-11 authorizes up to two representations. Preserve the approved upper bound and leave actual broker selection open.
- Open question 12 repeats an already approved canonical/rendering relationship. Do not reopen D-11; resolve schema, capability and lifecycle details.
- "Deterministic Phase 1" must not be read as a guarantee of identical AI prose. Financial calculations/rules must be deterministic; interpretation fidelity is separately reviewed.
- D-16 EOD and conditional event support need cross-market cutoff/availability policies; do not assume simultaneous US/Indian closes.
- Dhan stated availability is not inspected coverage. Yahoo is a conditional candidate. Licensed options/vintage data are unverified.
- ₹20 lakh is confirmed by the current human instruction; the corrupted source currency text is not edited.
- Existing questions on allocation, risk, weights, confidence, broker semantics, schedules, UI, service targets, governance and ML remain unresolved.
- R1 now has an approved mandatory personal-use workflow. Exact ETF/data coverage, financial policies, simulation rules, lifecycle authority and evidence sufficiency remain open. Capability blockers do not authorize silent removal of mandatory R1 scope.

## 8. Stage 1 acceptance and next authorization boundary

Review this outline package and its backlog together:
1. D-01 through D-16 have faithful traceability in the backlog; no elaboration changes their meaning.
2. All six specifications have purpose, scope, detailed sections/subsections, ownership, inputs, outputs, review criteria, relationships and question references.
3. Each backlog record has all required fields, one owner, unique ID, valid dependencies, approval status and independent maturity.
4. Must/Should/Could and Phase 1/Phase 2/Future remain proposed allocations; data availability and licensing are not invented.
5. Release-baseline, capability-specific and nonblocking questions are distinguishable.
6. No invented financial threshold, broker capability, actual opening balance, broker verification, real execution path or architectural choice is introduced; manual actual records remain unverified.
7. The change-impact convention is visibly Proposed, not an adopted product decision.
8. Counts, source preservation, decision coverage and duplicate/missing-requirement review are reported in the companion validation section.

Passing structural checks does not make the records Verified for readiness or Baselined. Recommendation state Validated is a separate concept from requirement maturity. Stage 1 acceptance requires human review. Do not start detailed REQ-01 through REQ-06 authoring without separate human approval. This package contains no implementation plan.

## 9. Stage 1 review history

| Date | Event | Scope |
| --- | --- | --- |
| 2026-11-01 | Human approved structure with maturity and impact refinements | Creation of these two Stage 1 artifacts only. |
| 2026-11-01 | Review draft prepared | No new product decisions or requirement baselines approved by artifact generation. |
| 2026-11-01 | Human approved R1 proposal with refinements A-D | Update only these two Stage 1 artifacts; preserve all 85 IDs and D-01 through D-16. |
| 2026-11-01 | R1 review update prepared | 32 new records and 33 existing content revisions; no implementation or detailed specification authoring. |

## 10. Approved R1 scope and proposed acceptance increments

Market research -> Validated strategy assessment -> Trade planning -> Paper trading or manual transaction recording -> Portfolio reassessment. R1 must be usable for personal investment research/planning, not merely a research prototype.

| Capability | R1 classification | Increment / condition |
| --- | --- | --- |
| Gold/silver intelligence, ETF analysis, AI research, independent horizon assessments and daily reports | Required | R1-A; qualified evidence and an agreed ETF/data coverage profile. |
| Deterministic strategies and evidence-supported entry/exit/stop/targets/sizing/risk-reward | Required | R1-B; eligible evidence, approved rules/risk policy and validation. |
| Up to three justified alternatives, no-trade, risk controls and capital reservation | Required | R1-B; alternatives never imply automatic real OCO behavior. |
| Paper orders, simulated fills, virtual balances/positions and accounting | Required | R1-B; explicit approved execution assumptions are release blockers, not an optional capability. |
| Historical backtesting, separate OOS/walk-forward testing and forward paper evidence | Required | R1-B; separate records and human-approved evidence sufficiency, without invented periods or profitability targets. |
| Broker-neutral placement instructions and manually recorded actual orders/fills | Required | R1-C; no submission, synchronization or broker verification. |
| Separate paper/manual portfolios, reconciliation and class-specific performance/drawdown | Required | R1-B paper accounting; complete R1-C reporting. |
| Daily position/recommendation reassessment; privacy and recoverability | Required | R1-C cumulatively with R1-A daily intelligence. |
| Minimum COMEX/MCX, currency and macro context needed by accepted strategies | Required coverage profile; details Open | R1-A/B; missing required data blocks the dependent strategy/capability. |
| Complete options chains, historical IV/Greeks, detailed flows/physical-market depth | Conditional on licensed data and validation | Approved product scope retained; selected coverage and any R1 deferral need explicit review. |
| Intraday fill fidelity and event-driven alerts | Conditional on suitable reliable data | EOD bars do not establish intraday ordering; no fabricated precision. |
| Up to two broker-specific renderings | Conditional on selection and verified capabilities | R1-C when selected; generic instructions remain required without broker selection. |
| Phase 2 ML implementation; US ETF/MCX futures investment capability | Deferred | D-09 Phase 1 ML requirements/extension readiness remain required at the requirements level; futures intelligence is distinct from futures investment. |
| Broker connectivity, read-only sync, human-authorized placement and other automation | Future assessment candidates only | No R1 implementation requirements or live execution path. |
| Autonomous real execution | Prohibited under D-03 | Requires an explicit approved governance change before any future scope can change. |

Required capability is not satisfied merely by a placeholder or perpetual no-trade. Withholding an unsupported recommendation is valid behavior, but R1 still needs usable qualified data, independent strategy rules and the agreed validation evidence.

| Increment | Human-directed acceptance scope | Acceptance boundary |
| --- | --- | --- |
| R1-A - Research Platform | Market-data acquisition and qualification; gold/silver intelligence; Indian Gold/Silver ETF analysis; interactive AI research; independent horizon assessments; daily intelligence reports. | Research evidence, quality and timestamps are inspectable. This increment alone is not complete R1. |
| R1-B - Validated Trade Planning and Paper Trading | Deterministic strategy evaluation; evidence-supported recommendations; entry/exit/stop/targets/sizing; up-to-three justified GTT scenarios; risk and capital reservation; paper orders/fills/accounting; historical validation and forward paper evidence. | Publication, strategy/evidence and simulation policies meet approved criteria; backtest, OOS/walk-forward and arriving-data forward records stay distinct. No invented target or period. |
| R1-C - Manual Trading Support and Personal-Use Readiness | Broker-neutral instructions; manually recorded real transactions; separate paper/manual portfolios; reconciliation and performance reporting; daily position/recommendation reassessment; privacy, backup/recovery and cumulative acceptance. | All required R1-A/B/C capabilities accepted together; manual records remain unverified; no broker connection or real order path. |

These are proposed acceptance increments within one R1 release, retained as the human-directed scope structure. They are not implementation milestones or authorization to build/deploy. Their detailed acceptance criteria remain reviewable/open. R1-B includes paper trading; it is not postponed to R1-C. All three approved investment horizons remain in R1.

### Evidence, recommendation and performance separation

**Three validation-evidence classes:** historical backtesting; walk-forward/out-of-sample testing; forward paper trading using newly arriving market data. Preserve separate records, eligible timestamps, data/strategy/simulation-policy versions and limitations. Replaying historical data or reproducing a stored forward event does not create new forward evidence. Original versus corrected observations/results retain lineage.

**Four performance groups:** historical strategy performance (with backtest versus OOS/walk-forward separately identifiable); forward paper performance; manually recorded actual-trade performance; benchmark performance. Comparison is permitted with class, period, cost/cash-flow and methodology disclosures. Combining simulated and actual track records into one misleading aggregate metric is not permitted. No periods, profit targets, win-rate targets, return method or benchmark are selected here.

**Recommendation states:** Draft -> Validated -> Published -> Superseded / Expired / Withdrawn. Each version identifies evidence timestamps/as-of context, validity conditions, strategy version, risk-check outcomes and reassessment lineage. State-transition authority, exact checks, additional transitions and expiry/withdrawal conditions remain R1-Q-013; no expiry duration is invented. Previously published versions remain attributable. Recommendation Validated is not requirement maturity Verified for readiness and does not guarantee profitability. Published does not create an order or alter a holding.

**Logical modes:** research recommendation; proposed trade plan; paper order/simulated fill; user-reported actual order/fill; future broker-connected assessment candidate. Paper and manual ledgers, balances and performance remain separate. Recording a user report is not order execution or broker verification. Simulated automatic triggers are confined to paper state. No service decomposition, implementation framework or real execution path is prescribed.

The ₹20 lakh default remains configurable and hypothetical; no actual opening balance is inferred from it. Costs, slippage, liquidity/partial fills, capital reservation, scenario relationships, marks, corporate actions, cash flows, expiry and data-quality behavior require explicit policy/evidence rather than invented defaults.

## 11. R1 review and traceability rules

- Preserve all 85 starting requirement IDs and their sources. Starting priorities are 66 Must / 18 Should / 1 Could. New IDs append within each document; no existing IDs are reused.
- Human-R1-Approval supplies authority for faithful R1 obligations, not for unselected numerical policies or architecture choices. New requirement acceptance operationalization remains reviewable; unresolved policy stays Open.
- REQ-04-008 and REQ-04-009 move Should -> Must for minimum retained research/recommendation evidence and targeted missing-input behavior. Other starting priority labels remain unchanged.
- R1 increment/applicability metadata is added to all records; it is separate from approval, maturity and Phase 1/Phase 2/Future.
- Historical backtest, OOS/walk-forward, forward paper and manual/benchmark reporting cannot be silently substituted or merged. Evidence source/data/strategy/policy versions and limitations must remain attributable.
- Recommendation Draft/Validated/Published/Superseded/Expired/Withdrawn is distinct from requirement approval and maturity. No fixed expiry, profitability target, win-rate target or evidence period is selected.
- The [backlog change log](STAGE_1_REQUIREMENTS_BACKLOG.md#change-log) lists added and revised IDs, status/priority changes and cumulative acceptance cases; [open questions](STAGE_1_REQUIREMENTS_BACKLOG.md#question-register) retain unresolved details.
- The proposed change-impact convention remains Proposed. Applying its review categories does not adopt governance or amend D-01 through D-16.

## 12. Human authorization boundary

Only these two Stage 1 Markdown files may be updated under this authorization. No detailed REQ-01 through REQ-06 authoring, implementation planning, scaffolding, installation, application code, deployment, broker connection or real execution is authorized. Submit the update and wait for further human authorization.
