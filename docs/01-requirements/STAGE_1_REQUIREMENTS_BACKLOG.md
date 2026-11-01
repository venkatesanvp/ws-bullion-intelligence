# Stage 1 Prioritized Requirements Backlog

**Version:** 0.2 - R1 scope and refinement review update  
**Date:** 1 November 2026 (Asia/Calcutta)  
**Artifact status:** Authorized documentation update; explicit R1 scope approved, detailed policies/readiness under review.  
**Companion:** [Detailed requirements outline](STAGE_1_REQUIREMENTS_OUTLINE.md)

## 1. Authority and review limits

D-01 through D-16 remain the authoritative product baseline. Human-R1-Approval adds the approved personal-use workflow and refinements without amending those decisions. See the [source authority catalog](STAGE_1_REQUIREMENTS_OUTLINE.md#2-sources-and-authority).

R1: market research -> validated strategy assessment -> trade planning -> paper trading or manual transaction recording -> portfolio reassessment. A research prototype alone is not complete R1.

This is a requirements backlog and outline update, not detailed REQ-01 through REQ-06 authoring or implementation planning. Only these two artifacts are authorized for change.

### 1.1 Classifications

- **Approval:** Approved is a faithful obligation from a cited decision, governance instruction or Human-R1-Approval. Proposed elaborates unapproved detail. Open identifies behavior needing a ruling/evidence.
- **Maturity:** Identified / Analyzed / Specified / Verified for readiness / Baselined is independent of approval. No record is readiness-verified or baselined here.
- **New acceptance detail:** Verification cases and operationalization remain reviewable; approval of an obligation does not invent missing financial/execution/expiry/evidence parameters.
- **Priority and phase:** R1 required scope is binding. Priority labels and acceptance allocations must preserve it. Phase 1 / Phase 2 / Future remains separate from R1-A/B/C; ML implementation remains Phase 2 while its requirements/readiness are documented during Phase 1.
- **Increment:** R1-A/B/C are proposed acceptance increments within one R1 release, not build/deployment authorization. Some records span cumulative increments; labels do not imply implementation sequence.
- **Applicability:** Conditional broker/advanced-data features do not waive required core capabilities. Future connectivity is assessment-only. The change-impact convention remains Proposed.
- **Verification:** VER IDs are planned cases, not executed product tests/backtests or generated performance evidence.
- **Source dates:** Human Stage 1 and R1 approvals are recorded in this conversation on 1 November 2026. No named review authority, provider rights or financial default is inferred.
- **Modes:** Research, plans, paper orders/fills, manual actual records and future execution candidates remain distinct. No R1 broker connection or real order placement.
- **Reference:** ₹20 lakh remains configurable and hypothetical; manually recorded actual balances come from user reports and remain not broker-verified.

## 2. Reconciled inventory

Starting inventory: **85 requirements = 66 Must + 18 Should + 1 Could**. All 85 stable IDs are retained. REQ-04-008 and REQ-04-009 move Should -> Must. Additions: **32 Must**. Final inventory: **117 = 100 Must + 16 Should + 1 Could**.

| Document | Total | Must | Should | Could | Approved | Proposed | Open | Identified | Analyzed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| REQ-01 | 12 | 10 | 1 | 1 | 11 | 0 | 1 | 1 | 11 |
| REQ-02 | 18 | 14 | 4 | 0 | 5 | 11 | 2 | 2 | 16 |
| REQ-03 | 39 | 36 | 3 | 0 | 27 | 6 | 6 | 6 | 33 |
| REQ-04 | 15 | 11 | 4 | 0 | 12 | 2 | 1 | 1 | 14 |
| REQ-05 | 14 | 12 | 2 | 0 | 6 | 3 | 5 | 5 | 9 |
| REQ-06 | 19 | 17 | 2 | 0 | 13 | 4 | 2 | 2 | 17 |
| **Total** | **117** | **100** | **16** | **1** | **74** | **26** | **17** | **17** | **100** |

Specified **0**; Verified for readiness **0**; Baselined **0**. Proposed phase allocations: Phase 1 **115**, Phase 2 **1** (REQ-03-022), Future **1** (REQ-01-010). Phase 1 is not automatically synonymous with a completed R1 or vice versa. Future instrument/ML readiness requirements remain visible.

## 3. R1 capability and increment matrix

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

Full lifecycle/evidence/performance definitions are in the [outline R1 contract](STAGE_1_REQUIREMENTS_OUTLINE.md#10-approved-r1-scope-and-proposed-acceptance-increments). R1-B includes paper trading and forward paper evidence; R1-C includes manual support and cumulative readiness.

## 4. Prioritized requirement index

Sorted by Must / Should / Could, then stable ID. Release applicability and increment details are in each record.

| ID | Title | Priority | Phase | Approval | Maturity |
| --- | --- | --- | --- | --- | --- |
| [REQ-01-001](#req-01-001) | Gold and silver investment focus | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-003](#req-01-003) | Initial Indian ETF investment universe | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-004](#req-01-004) | Swing investment horizon | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-005](#req-01-005) | Tactical investment horizon | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-006](#req-01-006) | Strategic investment horizon | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-007](#req-01-007) | Configurable hypothetical reference portfolio | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-008](#req-01-008) | Users and measurable business outcomes | Must | Phase 1 | Open | Identified |
| [REQ-01-009](#req-01-009) | First-release capability boundary | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-011](#req-01-011) | Paper-trading personal-use scope | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-012](#req-01-012) | Manually maintained actual-transaction scope | Must | Phase 1 | Approved | Analyzed |
| [REQ-02-001](#req-02-001) | COMEX futures dataset | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-002](#req-02-002) | MCX futures dataset | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-004](#req-02-004) | Currency and dollar-index dataset | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-005](#req-02-005) | Macro policy and economic-release dataset | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-007](#req-02-007) | Indian ETF market and fund datasets | Must | Phase 1 | Approved | Analyzed |
| [REQ-02-008](#req-02-008) | Provider permission and coverage evidence | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-009](#req-02-009) | Dhan export feasibility evidence | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-011](#req-02-011) | Canonical market-data semantics | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-012](#req-02-012) | Point-in-time timestamp and vintage contract | Must | Phase 1 | Proposed | Analyzed |
| [REQ-02-013](#req-02-013) | Data quality and degraded-output policy | Must | Phase 1 | Open | Identified |
| [REQ-02-014](#req-02-014) | Historical coverage and retention policy | Must | Phase 1 | Open | Identified |
| [REQ-02-015](#req-02-015) | Provider-independent acquisition | Must | Phase 1 | Approved | Analyzed |
| [REQ-02-017](#req-02-017) | Paper trigger fill and valuation evidence contract | Must | Phase 1 | Approved | Analyzed |
| [REQ-02-018](#req-02-018) | Manual transaction input provenance | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-001](#req-03-001) | Deterministic Phase 1 financial analytics | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-002](#req-03-002) | Separate analytical model outputs | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-003](#req-03-003) | Model reconciliation rules | Must | Phase 1 | Open | Identified |
| [REQ-03-004](#req-03-004) | Macro regime analysis | Must | Phase 1 | Proposed | Analyzed |
| [REQ-03-005](#req-03-005) | Futures positioning and curve analysis | Must | Phase 1 | Proposed | Analyzed |
| [REQ-03-007](#req-03-007) | Technical indicator definitions | Must | Phase 1 | Proposed | Analyzed |
| [REQ-03-009](#req-03-009) | ETF execution-quality assessment | Must | Phase 1 | Proposed | Analyzed |
| [REQ-03-010](#req-03-010) | Independent horizon-specific strategy controls | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-011](#req-03-011) | Strategy decision rules | Must | Phase 1 | Open | Identified |
| [REQ-03-012](#req-03-012) | Three-dimensional confidence | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-013](#req-03-013) | Confidence definitions and evidence sufficiency | Must | Phase 1 | Open | Identified |
| [REQ-03-014](#req-03-014) | Evidence-supported trade-plan contents | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-015](#req-03-015) | Portfolio allocation and sizing policy | Must | Phase 1 | Open | Identified |
| [REQ-03-016](#req-03-016) | Consolidated cross-strategy exposure | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-017](#req-03-017) | Evidence-supported alternative GTT scenarios | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-018](#req-03-018) | Canonical deterministic trade-plan representation | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-019](#req-03-019) | Capability-aware broker representations | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-020](#req-03-020) | Trade-plan validity and reassessment policy | Must | Phase 1 | Open | Identified |
| [REQ-03-021](#req-03-021) | Alternative-scenario capital interaction | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-023](#req-03-023) | Virtual cash and positions | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-024](#req-03-024) | Simulated order lifecycle | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-025](#req-03-025) | Entry and exit trigger evaluation | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-026](#req-03-026) | Fill pricing and within-bar ambiguity | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-027](#req-03-027) | Paper costs and slippage | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-028](#req-03-028) | Liquidity and partial fills | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-029](#req-03-029) | Paper expiration and cancellation | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-030](#req-03-030) | Capital reservation and release | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-031](#req-03-031) | Realized and unrealized P&L | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-032](#req-03-032) | Performance and drawdown reporting | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-033](#req-03-033) | Reproducible paper event history | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-034](#req-03-034) | Manual actual-order and fill recording | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-035](#req-03-035) | Actual opening state and cash flows | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-036](#req-03-036) | Daily position and recommendation reassessment | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-037](#req-03-037) | Broker-neutral placement instructions | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-038](#req-03-038) | Versioned recommendation lifecycle | Must | Phase 1 | Approved | Analyzed |
| [REQ-03-039](#req-03-039) | Separated performance classes | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-001](#req-04-001) | Research dashboard experience | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-002](#req-04-002) | Conversational research experience | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-003](#req-04-003) | Advisory-only action boundary | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-005](#req-04-005) | Generated interpretation versus financial results | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-006](#req-04-006) | Evidence timestamps and uncertainty | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-008](#req-04-008) | Retained research and recommendation evidence | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-009](#req-04-009) | Targeted missing-input questions | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-010](#req-04-010) | Scheduled EOD research report | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-012](#req-04-012) | Assistant tool and context policy | Must | Phase 1 | Open | Identified |
| [REQ-04-014](#req-04-014) | Paper workflow and simulation disclosure | Must | Phase 1 | Approved | Analyzed |
| [REQ-04-015](#req-04-015) | Manual recording and unverified disclosure | Must | Phase 1 | Approved | Analyzed |
| [REQ-05-001](#req-05-001) | Accepted backend and persistence constraints | Must | Phase 1 | Approved | Analyzed |
| [REQ-05-002](#req-05-002) | Cross-component semantic contracts | Must | Phase 1 | Proposed | Analyzed |
| [REQ-05-003](#req-05-003) | Sensitive-information protection | Must | Phase 1 | Approved | Analyzed |
| [REQ-05-004](#req-05-004) | Access privacy and secrets policy | Must | Phase 1 | Open | Identified |
| [REQ-05-005](#req-05-005) | Broker capability evidence contract | Must | Phase 1 | Proposed | Analyzed |
| [REQ-05-006](#req-05-006) | EOD scheduling and cutoff policy | Must | Phase 1 | Open | Identified |
| [REQ-05-008](#req-05-008) | Measurable service qualities | Must | Phase 1 | Open | Identified |
| [REQ-05-009](#req-05-009) | Backup restoration and retention | Must | Phase 1 | Open | Identified |
| [REQ-05-010](#req-05-010) | Operational provenance and observability | Must | Phase 1 | Proposed | Analyzed |
| [REQ-05-011](#req-05-011) | Phase 1 ML requirements and extension readiness | Must | Phase 1 | Approved | Analyzed |
| [REQ-05-013](#req-05-013) | Logical execution-mode boundaries | Must | Phase 1 | Approved | Analyzed |
| [REQ-05-014](#req-05-014) | Persistent attributable activity history | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-001](#req-06-001) | Requirement-to-evidence traceability | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-002](#req-06-002) | Independent financial calculation verification | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-003](#req-06-003) | Point-in-time historical replay | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-004](#req-06-004) | Realistic backtest protocol | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-005](#req-06-005) | Out-of-sample predictive evidence | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-006](#req-06-006) | Validation and release acceptance thresholds | Must | Phase 1 | Open | Identified |
| [REQ-06-007](#req-06-007) | Assistant evaluation protocol | Must | Phase 1 | Proposed | Analyzed |
| [REQ-06-008](#req-06-008) | Security and recovery acceptance evidence | Must | Phase 1 | Proposed | Analyzed |
| [REQ-06-009](#req-06-009) | Review authority and change approval | Must | Phase 1 | Open | Identified |
| [REQ-06-010](#req-06-010) | Independent approval and maturity tracking | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-013](#req-06-013) | Simulation lifecycle and execution-policy verification | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-014](#req-06-014) | Accounting and performance verification | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-015](#req-06-015) | Real-execution prevention and mode isolation | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-016](#req-06-016) | Manual provenance and correction verification | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-017](#req-06-017) | Cumulative R1 personal-use acceptance | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-018](#req-06-018) | Distinct validation evidence records | Must | Phase 1 | Approved | Analyzed |
| [REQ-06-019](#req-06-019) | Forward paper evidence using arriving data | Must | Phase 1 | Approved | Analyzed |
| [REQ-01-002](#req-01-002) | Contextual-market research | Should | Phase 1 | Approved | Analyzed |
| [REQ-02-003](#req-02-003) | Options-chain dataset | Should | Phase 1 | Proposed | Analyzed |
| [REQ-02-006](#req-02-006) | Contextual positioning and physical-market datasets | Should | Phase 1 | Proposed | Analyzed |
| [REQ-02-010](#req-02-010) | Conditional Yahoo fallback validation | Should | Phase 1 | Approved | Analyzed |
| [REQ-02-016](#req-02-016) | Discovery candidate qualification | Should | Phase 1 | Proposed | Analyzed |
| [REQ-03-006](#req-03-006) | Options positioning and volatility analysis | Should | Phase 1 | Proposed | Analyzed |
| [REQ-03-008](#req-03-008) | Relative-value and gold/silver analysis | Should | Phase 1 | Proposed | Analyzed |
| [REQ-03-022](#req-03-022) | Phase 2 ML analytical capability | Should | Phase 2 | Open | Identified |
| [REQ-04-004](#req-04-004) | Dynamic market-data discovery interaction | Should | Phase 1 | Approved | Analyzed |
| [REQ-04-007](#req-04-007) | What-if scenario analysis | Should | Phase 1 | Proposed | Analyzed |
| [REQ-04-011](#req-04-011) | Event investigation and reassessment | Should | Phase 1 | Approved | Analyzed |
| [REQ-04-013](#req-04-013) | Research chart evidence and semantics | Should | Phase 1 | Proposed | Analyzed |
| [REQ-05-007](#req-05-007) | Event and alert delivery policy | Should | Phase 1 | Open | Identified |
| [REQ-05-012](#req-05-012) | Future instrument extension constraints | Should | Phase 1 | Approved | Analyzed |
| [REQ-06-011](#req-06-011) | Proposed requirements change-impact assessment | Should | Phase 1 | Proposed | Analyzed |
| [REQ-06-012](#req-06-012) | Phase 2 ML evaluation and governance readiness | Should | Phase 1 | Proposed | Analyzed |
| [REQ-01-010](#req-01-010) | Future investment-instrument scope | Could | Future | Approved | Analyzed |

## 5. Individual requirement records

Each record has one owner identified by its REQ document prefix. New/changed obligations cite Human-R1-Approval; unresolved policy links are not answers. Unchanged means core wording/status/priority retained; all original records receive release applicability/increment metadata.

## REQ-01 - Product Vision and Business Requirements

<a id="req-01-001"></a>

### REQ-01-001 - Gold and silver investment focus

- **Requirement description:** The platform shall treat gold and silver as its primary investment assets.
- **Source / originating decision:** D-01; PROJECT_OVERVIEW: Vision.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: scope requirement.
- **Planned verification:** VER-01-001 - Review product workflows and instrument classifications.
- **Acceptance criteria:** Gold and silver are classified as primary assets; contextual markets do not become investment assets implicitly.
- **Unresolved questions:** None identified for this obligation; later review may identify more.
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-002"></a>

### REQ-01-002 - Contextual-market research

- **Requirement description:** The platform shall support requested contextual-market research and proactive identification of relevant information.
- **Source / originating decision:** D-01; DISCUSSION_SUMMARY: Global intelligence scope.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-001](#req-01-001)
- **Data availability assumptions:** DATA-004.
- **Planned verification:** VER-01-002 - Review research scenarios with contextual assets.
- **Acceptance criteria:** A contextual research request and a proactive information-gap scenario are represented without changing primary-asset scope.
- **Unresolved questions:** [S1-Q-012](#s1-q-012)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-003"></a>

### REQ-01-003 - Initial Indian ETF investment universe

- **Requirement description:** The initial investment universe shall comprise Indian Gold and Silver ETFs.
- **Source / originating decision:** D-04; PROJECT_OVERVIEW: Investment instruments.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-001](#req-01-001)
- **Data availability assumptions:** DATA-005.
- **Planned verification:** VER-01-003 - Review universe rules against representative instruments.
- **Acceptance criteria:** Indian Gold/Silver ETFs are in initial investment scope; US ETFs and MCX futures are not silently included as initial investments.
- **Unresolved questions:** [S1-Q-001](#s1-q-001)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-004"></a>

### REQ-01-004 - Swing investment horizon

- **Requirement description:** The platform shall support a swing investment horizon of 5-20 trading days.
- **Source / originating decision:** D-02.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-003](#req-01-003)
- **Data availability assumptions:** DATA-001; DATA-003; DATA-005.
- **Planned verification:** VER-01-004 - Review horizon boundaries and strategy scenarios.
- **Acceptance criteria:** Swing is represented separately with the approved 5-20 trading-day range; calendar conventions remain explicitly pending.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-005"></a>

### REQ-01-005 - Tactical investment horizon

- **Requirement description:** The platform shall support a tactical investment horizon of 1-3 months.
- **Source / originating decision:** D-02.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-003](#req-01-003)
- **Data availability assumptions:** DATA-001; DATA-003; DATA-005.
- **Planned verification:** VER-01-005 - Review horizon boundaries and strategy scenarios.
- **Acceptance criteria:** Tactical is represented separately with the approved 1-3-month range.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-006"></a>

### REQ-01-006 - Strategic investment horizon

- **Requirement description:** The platform shall support a strategic investment horizon of 6-24 months.
- **Source / originating decision:** D-02.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-003](#req-01-003)
- **Data availability assumptions:** DATA-001; DATA-003; DATA-005.
- **Planned verification:** VER-01-006 - Review horizon boundaries and strategy scenarios.
- **Acceptance criteria:** Strategic is represented separately with the approved 6-24-month range.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-007"></a>

### REQ-01-007 - Configurable hypothetical reference portfolio

- **Requirement description:** The platform shall provide a configurable ₹20 lakh hypothetical reference portfolio and shall not present it as actual user holdings.
- **Source / originating decision:** D-06; D-15; User-Stage1: currency confirmation.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: configuration and labels.
- **Planned verification:** VER-01-007 - Inspect initial values, configuration changes, and portfolio labels.
- **Acceptance criteria:** The reference amount is ₹20 lakh, is configurable, and is visibly hypothetical; no allocation or risk default is inferred.
- **Unresolved questions:** [S1-Q-007](#s1-q-007)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-008"></a>

### REQ-01-008 - Users and measurable business outcomes

- **Requirement description:** The primary use is personal investment research and trade planning; detailed ETF selection, workflow outcomes and measurable success criteria remain to be agreed.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-01; OPEN_QUESTIONS: 11; Human-R1-Approval.
- **Category / owner:** Business outcome; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: human requirements decision.
- **Planned verification:** VER-01-008 - Stakeholder walkthrough of personas, workflows, and success measures.
- **Acceptance criteria:** Named personas, workflow outcomes, measure definitions, and approving roles are accepted by the human owner; no targets are invented.
- **Unresolved questions:** [S1-Q-001](#s1-q-001), [R1-Q-001](#r1-q-001)
- **R1 change:** Revised; Record personal-use direction; detailed product acceptance remains open.

<a id="req-01-009"></a>

### REQ-01-009 - First-release capability boundary

- **Requirement description:** R1 shall provide market research, validated strategy assessment, trade planning, paper trading or manual transaction recording, and portfolio reassessment as one usable personal investment application.
- **Source / originating decision:** PROJECT_OVERVIEW: Status; REQUIREMENTS_INDEX: REQ-01; User-Stage1; Human-R1-Approval.
- **Category / owner:** Release scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-008](#req-01-008)
- **Data availability assumptions:** DATA-001; DATA-002; DATA-003; DATA-004; DATA-005; DATA-006; DATA-007.
- **Planned verification:** VER-01-009 - Review a capability-by-release matrix against D-01 through D-16.
- **Acceptance criteria:** Cumulative R1-A, R1-B and R1-C cover every mandatory R1 capability; an intermediate research increment is not complete R1. Instrument selection and detailed readiness criteria remain open.
- **Unresolved questions:** [S1-Q-001](#s1-q-001), [R1-Q-001](#r1-q-001), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Replace open broad release intent with approved R1 scope; retain detailed acceptance questions.

<a id="req-01-010"></a>

### REQ-01-010 - Future investment-instrument scope

- **Requirement description:** The product shall preserve extensibility to US ETFs and MCX futures as investment instruments.
- **Source / originating decision:** D-04.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Could; Future.
- **R1 applicability / increment:** Deferred capability; relevant extension requirements remain Phase 1; Outside R1 capability.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-003](#req-01-003)
- **Data availability assumptions:** Future instrument and permission evidence not established.
- **Planned verification:** VER-01-010 - Review future-use cases and reference REQ-05-012 extension requirements.
- **Acceptance criteria:** Future US ETF and MCX futures investment use cases are documented distinctly from current MCX intelligence; implementation is not implied.
- **Unresolved questions:** [S1-Q-017](#s1-q-017)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-01-011"></a>

### REQ-01-011 - Paper-trading personal-use scope

- **Requirement description:** R1 shall support paper orders, simulated fills, virtual positions and performance without affecting real accounts.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-009](#req-01-009)
- **Data availability assumptions:** Qualified market data and approved simulation policies; not yet established.
- **Planned verification:** VER-01-011 - Walk the complete paper workflow.
- **Acceptance criteria:** Paper activity is clearly simulated and contributes to R1 usability; no real order or broker account is involved.
- **Unresolved questions:** [R1-Q-003](#r1-q-003), [R1-Q-004](#r1-q-004), [R1-Q-006](#r1-q-006)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-01-012"></a>

### REQ-01-012 - Manually maintained actual-transaction scope

- **Requirement description:** R1 shall support manual recording of actual transactions in a portfolio separate from paper trading and labeled not broker-verified.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Business scope; REQ-01.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-009](#req-01-009)
- **Data availability assumptions:** DATA-008: user-provided records, not verified broker state.
- **Planned verification:** VER-01-012 - Walk a reported external transaction and mode comparison.
- **Acceptance criteria:** User-reported actual activity never inherits hypothetical balances, simulated fills or broker-verified status.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## REQ-02 - Market Data and Indicator Requirements

<a id="req-02-001"></a>

### REQ-02-001 - COMEX futures dataset

- **Requirement description:** The data specification should define a COMEX gold/silver futures dataset with contract identity, expiry, price, volume, OI, and term-structure coverage.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-01-001](#req-01-001)
- **Data availability assumptions:** DATA-001: access, rights, fields and history unverified.
- **Planned verification:** VER-02-001 - Review field inventory and inspect representative dated contracts.
- **Acceptance criteria:** Every requested field has units, timestamp semantics, source, coverage evidence, and missing-field treatment; unavailable fields are explicit.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-002"></a>

### REQ-02-002 - MCX futures dataset

- **Requirement description:** The data specification should define MCX gold/silver futures coverage by contract, expiry, price, volume, OI, and curve.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-01-001](#req-01-001)
- **Data availability assumptions:** DATA-001; DATA-006.
- **Planned verification:** VER-02-002 - Inspect representative MCX contracts and compare declared coverage with samples.
- **Acceptance criteria:** Contract-level coverage and session conventions are documented; intelligence use is distinguished from futures investment execution.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-003"></a>

### REQ-02-003 - Options-chain dataset

- **Requirement description:** The data specification should define COMEX options-chain coverage for strikes, expiries, quotes, OI, volume, IV and Greeks, identifying supplied versus derived fields.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-001](#req-02-001)
- **Data availability assumptions:** DATA-002: licensed chains and historical snapshots unverified.
- **Planned verification:** VER-02-003 - Inspect dated chains and review field provenance.
- **Acceptance criteria:** Coverage lists strike/expiry availability, observation times, source rights, supplied/derived status, and missing fields; completeness is not assumed.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-004"></a>

### REQ-02-004 - Currency and dollar-index dataset

- **Requirement description:** The data specification should define USD/INR and DXY coverage and quote conventions for cross-market research.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011)
- **Data availability assumptions:** DATA-003.
- **Planned verification:** VER-02-004 - Review sample observations, currency pairs, and calendars.
- **Acceptance criteria:** USD/INR and DXY each have a source, units, quote direction, timestamps, frequency, and documented alignment rules.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-005"></a>

### REQ-02-005 - Macro policy and economic-release dataset

- **Requirement description:** The data specification should catalog Fed policy, market-implied rates, nominal/real Treasury yields, CPI, PCE, PPI, and jobs releases with vintages.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012)
- **Data availability assumptions:** DATA-003: release vintages and implied-rate history unverified.
- **Planned verification:** VER-02-005 - Review a catalog entry and timestamp/vintage evidence for each named series.
- **Acceptance criteria:** Each series records source, units, publication timing, revision handling, frequency and available history; absent vintages are flagged.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003), [S1-Q-004](#s1-q-004)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-006"></a>

### REQ-02-006 - Contextual positioning and physical-market datasets

- **Requirement description:** The data specification should catalog CFTC COT, crude/copper, physical-market and inventory series used as context.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-02.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-01-002](#req-01-002)
- **Data availability assumptions:** DATA-004.
- **Planned verification:** VER-02-006 - Review contextual-series catalog and delayed-release examples.
- **Acceptance criteria:** Named contextual series have coverage, release lag, rights, timestamps and purpose recorded; unavailable data is disclosed.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-007"></a>

### REQ-02-007 - Indian ETF market and fund datasets

- **Requirement description:** The ETF data contract shall identify price, volume, available quotes/spreads, NAV, flows, fund characteristics and corporate-action coverage needed by R1 analysis, valuation and performance.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-02; DISCUSSION_SUMMARY: ETF NAV/flows; Human-R1-Approval.
- **Category / owner:** Market data; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-003](#req-01-003), [REQ-02-011](#req-02-011)
- **Data availability assumptions:** DATA-005: NAV, quotes and flows may have different frequencies and rights.
- **Planned verification:** VER-02-007 - Review instrument samples and publication schedules.
- **Acceptance criteria:** ETF coverage distinguishes observations from estimates, price/NAV times, flows from proxies and corporate-action effects; unavailable fields and dependent outputs are explicit.
- **Unresolved questions:** [S1-Q-001](#s1-q-001), [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003), [R1-Q-001](#r1-q-001), [R1-Q-008](#r1-q-008)
- **R1 change:** Revised; Extend ETF scope to paper/manual valuation; availability remains unverified.

<a id="req-02-008"></a>

### REQ-02-008 - Provider permission and coverage evidence

- **Requirement description:** A provider catalog should record documented retrieval, storage, analysis, display and redistribution permissions for each dataset and intended use.
- **Source / originating decision:** D-14; REQUIREMENTS_INDEX: REQ-02; OPEN_QUESTIONS: 4.
- **Category / owner:** Data governance; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** DATA-001; DATA-002; DATA-003; DATA-004; DATA-005; DATA-006; DATA-007.
- **Planned verification:** VER-02-008 - Inspect provider evidence and a prohibited-use review case.
- **Acceptance criteria:** Each included dataset has attributable permission/coverage evidence or an explicit unresolved gate; a candidate is not treated as licensed by default.
- **Unresolved questions:** [S1-Q-002](#s1-q-002)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-009"></a>

### REQ-02-009 - Dhan export feasibility evidence

- **Requirement description:** Representative user-provided Dhan exports should be assessed for instruments, fields, history, expiry, OI, timestamps and adjustment metadata.
- **Source / originating decision:** D-14; OPEN_QUESTIONS: 3.
- **Category / owner:** Data feasibility; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-008](#req-02-008)
- **Data availability assumptions:** DATA-006: stated availability; actual samples not inspected.
- **Planned verification:** VER-02-009 - Compare sample columns and records with the declared coverage inventory.
- **Acceptance criteria:** The assessment identifies usable fields, gaps and unsuitable uses without assuming a continuous or point-in-time history.
- **Unresolved questions:** [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-010"></a>

### REQ-02-010 - Conditional Yahoo fallback validation

- **Requirement description:** Yahoo Finance shall remain only a possible US-series fallback pending validation of suitability.
- **Source / originating decision:** D-14; DISCUSSION_SUMMARY: Data candidates.
- **Category / owner:** Data constraint; REQ-02.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-008](#req-02-008)
- **Data availability assumptions:** DATA-007: suitability and rights unverified.
- **Planned verification:** VER-02-010 - Review candidate-series validation evidence and unsupported-use cases.
- **Acceptance criteria:** No fallback series is represented as validated without evidence; complete COMEX options coverage is not presumed.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-011"></a>

### REQ-02-011 - Canonical market-data semantics

- **Requirement description:** Canonical data contracts should define instrument identity, units, currencies, multipliers, calendars, sessions, time zones and adjustments, with distinct market and manual-transaction input semantics.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-02; architecture review elaboration; Human-R1-Approval.
- **Category / owner:** Data contract; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** Representative metadata from DATA-001 through DATA-007; coverage unverified.
- **Planned verification:** VER-02-011 - Review contracts using cross-market and expiry-boundary examples.
- **Acceptance criteria:** Each included field has an unambiguous meaning and conversion/calendar rule; unspecified conventions are linked to open questions.
- **Unresolved questions:** [S1-Q-003](#s1-q-003), [S1-Q-004](#s1-q-004), [R1-Q-004](#r1-q-004), [R1-Q-009](#r1-q-009)
- **R1 change:** Revised; Extend semantic contracts; field-level choices remain Proposed.

<a id="req-02-012"></a>

### REQ-02-012 - Point-in-time timestamp and vintage contract

- **Requirement description:** Data contracts should distinguish observation, publication, availability and ingestion times, revisions, and transaction event versus user recording times.
- **Source / originating decision:** D-12; AGENTS: point-in-time correctness; REQUIREMENTS_INDEX: REQ-02; Human-R1-Approval.
- **Category / owner:** Data contract; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011)
- **Data availability assumptions:** DATA-001; DATA-002; DATA-003; DATA-005: vintage/availability evidence unverified.
- **Planned verification:** VER-02-012 - Trace an original observation and a later revision through an as-of query example.
- **Acceptance criteria:** As-of eligibility preserves what was available then; transaction event time is distinguishable from recording time; revisions cannot silently become original evidence.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [R1-Q-009](#r1-q-009), [R1-Q-013](#r1-q-013), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Extend temporal provenance to manual and forward evidence.

<a id="req-02-013"></a>

### REQ-02-013 - Data quality and degraded-output policy

- **Requirement description:** Quality/freshness gates and missing/stale/conflicting-input consequences for research, recommendation publication, paper fills and portfolio marks remain to be agreed.
- **Source / originating decision:** OPEN_QUESTIONS: 4; REQUIREMENTS_INDEX: REQ-02; Human-R1-Approval.
- **Category / owner:** Data quality; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-02-011](#req-02-011), [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Dataset-specific cadence and quality evidence not established.
- **Planned verification:** VER-02-013 - Review normal, stale, absent and conflicting-input cases.
- **Acceptance criteria:** Human-approved quality rules identify whether each dependent output continues, degrades or is withheld; no numerical thresholds are invented.
- **Unresolved questions:** [S1-Q-005](#s1-q-005), [R1-Q-004](#r1-q-004), [R1-Q-011](#r1-q-011), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Extend quality questions without selecting thresholds or fallback marks.

<a id="req-02-014"></a>

### REQ-02-014 - Historical coverage and retention policy

- **Requirement description:** Historical coverage, point-in-time vintages, roll treatment and evidence retention remain to be agreed separately for backtesting, OOS/walk-forward and forward paper records.
- **Source / originating decision:** OPEN_QUESTIONS: 8; D-12; Human-R1-Approval.
- **Category / owner:** Data history; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-02-012](#req-02-012)
- **Data availability assumptions:** DATA-001; DATA-002; DATA-003; DATA-005; DATA-006.
- **Planned verification:** VER-02-014 - Review horizon-specific history needs against inspected source coverage.
- **Acceptance criteria:** Required versus available history and retention are documented by use case; gaps affecting replay or reliability are explicit.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [R1-Q-002](#r1-q-002), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Separate historical coverage from forward observation evidence.

<a id="req-02-015"></a>

### REQ-02-015 - Provider-independent acquisition

- **Requirement description:** Market-data acquisition shall be provider-independent and phased.
- **Source / originating decision:** D-14.
- **Category / owner:** Data constraint; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-008](#req-02-008)
- **Data availability assumptions:** No provider substitution is assumed equivalent.
- **Planned verification:** VER-02-015 - Review a provider replacement scenario against canonical semantics.
- **Acceptance criteria:** A replacement is assessed through declared data contracts and coverage differences; provider choice does not redefine financial meanings silently.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-016"></a>

### REQ-02-016 - Discovery candidate qualification

- **Requirement description:** Newly discovered data candidates should be assessed for relevance, permissions, semantics, coverage and quality before analytical adoption.
- **Source / originating decision:** D-01; D-14; REQ-04 planned proactive retrieval; proposed elaboration.
- **Category / owner:** Data governance; REQ-02.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-008](#req-02-008), [REQ-02-011](#req-02-011), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** Discovery does not establish DATA-001 through DATA-007 availability.
- **Planned verification:** VER-02-016 - Review a new candidate, an unauthorized source, and an incompatible field.
- **Acceptance criteria:** A candidate's qualification state and permitted use are visible; discovery alone does not make it a trusted production input.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-012](#s1-q-012)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-02-017"></a>

### REQ-02-017 - Paper trigger fill and valuation evidence contract

- **Requirement description:** R1 shall identify the observation granularity, timestamps, price/volume fields and limitations used for paper triggers, fills and marks.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Data contract; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-007](#req-02-007), [REQ-02-011](#req-02-011), [REQ-02-012](#req-02-012), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** DATA-005: bars, quotes, volume and marks unverified.
- **Planned verification:** VER-02-017 - Review EOD, intraday and missing-quote examples.
- **Acceptance criteria:** The evidence contract states what can and cannot establish trigger/fill sequence or valuation; EOD bars do not imply intraday ordering.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-005](#r1-q-005), [S1-Q-005](#s1-q-005)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-02-018"></a>

### REQ-02-018 - Manual transaction input provenance

- **Requirement description:** Manual inputs shall distinguish reported transaction time, recording time, source and incomplete information without implying broker verification.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Data contract; REQ-02.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011), [REQ-02-012](#req-02-012), [REQ-01-012](#req-01-012)
- **Data availability assumptions:** DATA-008: manually supplied orders/fills/cash flows; truth and completeness unverified.
- **Planned verification:** VER-02-018 - Review late, incomplete and corrected entries.
- **Acceptance criteria:** The contract distinguishes reported events from recording actions and flags missing data; attachments or user entry do not become broker verification.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## REQ-03 - Quantitative Analytics, Strategies and Trade Planning

<a id="req-03-001"></a>

### REQ-03-001 - Deterministic Phase 1 financial analytics

- **Requirement description:** Phase 1 financial calculations and strategy rules shall be deterministic; ML implementation shall remain Phase 2.
- **Source / originating decision:** D-09; AGENTS: deterministic reproducible calculations; User-Stage1.
- **Category / owner:** Analytical constraint; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011)
- **Data availability assumptions:** Versioned inputs and parameters; provider availability not assumed.
- **Planned verification:** VER-03-001 - Repeat a calculation with identical inputs and inspect separation from generated narrative.
- **Acceptance criteria:** Identical financial inputs and rule versions yield identical financial results; AI wording does not replace calculations and Phase 1 contains no ML implementation.
- **Unresolved questions:** None identified for this obligation; later review may identify more.
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-002"></a>

### REQ-03-002 - Separate analytical model outputs

- **Requirement description:** The platform shall preserve separate outputs from multiple analytical models.
- **Source / originating decision:** D-08.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-001](#req-03-001)
- **Data availability assumptions:** Inputs depend on each selected model.
- **Planned verification:** VER-03-002 - Review a research result containing disagreeing model outputs.
- **Acceptance criteria:** Each model result remains attributable and independently inspectable rather than being hidden inside one unexplained score.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-003"></a>

### REQ-03-003 - Model reconciliation rules

- **Requirement description:** The rules for reconciling model agreement, disagreement, missing outputs and any weights remain to be agreed.
- **Source / originating decision:** D-08; OPEN_QUESTIONS: 6.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-03-002](#req-03-002)
- **Data availability assumptions:** Model coverage and validation evidence not established.
- **Planned verification:** VER-03-003 - Review agreement, contradiction and unavailable-model cases.
- **Acceptance criteria:** Approved reconciliation rules explain the combined interpretation and preserve component outputs; weights and thresholds have human-approved evidence.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-004"></a>

### REQ-03-004 - Macro regime analysis

- **Requirement description:** A deterministic macro model should describe gold/silver conditions using explicitly defined policy, rates, inflation, currency and economic-release inputs.
- **Source / originating decision:** DISCUSSION_SUMMARY: Analytical architecture; REQUIREMENTS_INDEX: REQ-03.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-004](#req-02-004), [REQ-02-005](#req-02-005), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-003.
- **Planned verification:** VER-03-004 - Review formulas and fixed, time-aligned economic scenarios.
- **Acceptance criteria:** Each output states its inputs, as-of time, rule version and interpretation limits; regime definitions await approval rather than invented thresholds.
- **Unresolved questions:** [S1-Q-003](#s1-q-003), [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-005"></a>

### REQ-03-005 - Futures positioning and curve analysis

- **Requirement description:** Futures analytics should define contract liquidity, OI/volume changes, spreads, cost-of-carry inputs and contango/backwardation using explicit expiry and roll conventions.
- **Source / originating decision:** DISCUSSION_SUMMARY: Origin and evolution; REQUIREMENTS_INDEX: REQ-03.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-001](#req-02-001), [REQ-02-002](#req-02-002), [REQ-02-011](#req-02-011), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-001; DATA-006.
- **Planned verification:** VER-03-005 - Review worked contract/curve examples and expiry-boundary cases.
- **Acceptance criteria:** Results identify underlying contracts and conventions and do not confuse contract changes or rollover effects with market signals.
- **Unresolved questions:** [S1-Q-003](#s1-q-003), [S1-Q-004](#s1-q-004), [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-006"></a>

### REQ-03-006 - Options positioning and volatility analysis

- **Requirement description:** Options analytics should define OI/volume, IV, skew and Greeks interpretation with explicit supplied/derived assumptions.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-03.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-003](#req-02-003), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-002; complete chains and historical Greeks unverified.
- **Planned verification:** VER-03-006 - Review a dated chain and missing-strike/expiry scenarios.
- **Acceptance criteria:** Outputs identify chain coverage and derivation assumptions and do not imply full-market coverage or validated prediction from partial chains.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-003](#s1-q-003), [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-007"></a>

### REQ-03-007 - Technical indicator definitions

- **Requirement description:** Technical analysis should use individually defined, reproducible indicators with explicit price series, adjustment and warm-up conventions.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-03; OPEN_QUESTIONS: 6.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-001; DATA-005.
- **Planned verification:** VER-03-007 - Review indicator definitions and independently calculated reference examples.
- **Acceptance criteria:** Every selected indicator has formula, parameters, input series and insufficient-history behavior; indicator selection remains subject to approval.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-008"></a>

### REQ-03-008 - Relative-value and gold/silver analysis

- **Requirement description:** Relative-value analytics should define gold/silver ratio and cross-market comparisons using declared units, currencies and aligned timestamps.
- **Source / originating decision:** DISCUSSION_SUMMARY: Global intelligence scope; REQUIREMENTS_INDEX: REQ-03.
- **Category / owner:** Analytics; REQ-03.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-004](#req-02-004), [REQ-02-011](#req-02-011), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-001; DATA-003; DATA-005.
- **Planned verification:** VER-03-008 - Review currency/unit conversion and asynchronous-market examples.
- **Acceptance criteria:** Comparisons state aligned observation times, denominators and conversion conventions; stale or incompatible inputs follow the agreed quality policy.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [S1-Q-005](#s1-q-005)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-009"></a>

### REQ-03-009 - ETF execution-quality assessment

- **Requirement description:** ETF analysis should assess available liquidity, spreads, NAV premium/discount, tracking characteristics and relevant charges/adjustments.
- **Source / originating decision:** DISCUSSION_SUMMARY: ETF execution quality; REQUIREMENTS_INDEX: REQ-03; proposed elaboration.
- **Category / owner:** ETF analytics; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-007](#req-02-007), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** DATA-005: spread, tracking and cost evidence unverified.
- **Planned verification:** VER-03-009 - Review ETF cases with asynchronous NAV and missing quote information.
- **Acceptance criteria:** The assessment separates observed values from unavailable estimates and records time alignment and cost assumptions without inventing quotes.
- **Unresolved questions:** [S1-Q-003](#s1-q-003), [S1-Q-004](#s1-q-004), [S1-Q-008](#s1-q-008)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-010"></a>

### REQ-03-010 - Independent horizon-specific strategy controls

- **Requirement description:** Swing, tactical and strategic strategies shall retain independent signals, validation and risk controls.
- **Source / originating decision:** D-02; PROJECT_OVERVIEW: Supported horizons; User-Stage1.
- **Category / owner:** Strategy; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-004](#req-01-004), [REQ-01-005](#req-01-005), [REQ-01-006](#req-01-006), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** Inputs and history depend on each strategy.
- **Planned verification:** VER-03-010 - Review one scenario per horizon and a change isolated to one strategy.
- **Acceptance criteria:** Each horizon has separately identifiable rules and evidence; changing one does not silently redefine the others.
- **Unresolved questions:** [S1-Q-006](#s1-q-006), [S1-Q-007](#s1-q-007)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-011"></a>

### REQ-03-011 - Strategy decision rules

- **Requirement description:** Entry, exit, invalidation, holding-period conventions, benchmarks and parameter selection for each strategy remain to be agreed.
- **Source / originating decision:** OPEN_QUESTIONS: 6; REQUIREMENTS_INDEX: REQ-03.
- **Category / owner:** Strategy; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-03-003](#req-03-003), [REQ-03-007](#req-03-007), [REQ-03-010](#req-03-010)
- **Data availability assumptions:** Required signal history and benchmark coverage unverified.
- **Planned verification:** VER-03-011 - Review complete decision scenarios and boundary cases per horizon.
- **Acceptance criteria:** Each strategy has human-approved, reproducible decision rules and no-trade behavior; no financial thresholds are silently supplied.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-012"></a>

### REQ-03-012 - Three-dimensional confidence

- **Requirement description:** Research shall show signal strength, historical reliability and data quality as separate confidence dimensions.
- **Source / originating decision:** D-10.
- **Category / owner:** Confidence; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-002](#req-03-002), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** Historical reliability may be unavailable before validation.
- **Planned verification:** VER-03-012 - Review strong-signal/weak-data and insufficient-history examples.
- **Acceptance criteria:** All three dimensions are separately visible; unknown historical reliability is not replaced with a fabricated probability.
- **Unresolved questions:** [S1-Q-009](#s1-q-009)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-013"></a>

### REQ-03-013 - Confidence definitions and evidence sufficiency

- **Requirement description:** Scales, evidence requirements and minimum sufficiency rules for each confidence dimension remain to be agreed.
- **Source / originating decision:** D-10; REQUIREMENTS_INDEX: REQ-03; architecture review elaboration.
- **Category / owner:** Confidence; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-03-012](#req-03-012), [REQ-06-005](#req-06-005)
- **Data availability assumptions:** Out-of-sample evidence and quality statistics not yet available.
- **Planned verification:** VER-03-013 - Review scale meanings and unsupported/insufficient-evidence cases.
- **Acceptance criteria:** Definitions distinguish signal strength from empirical reliability and data quality; probability language requires an approved evidential basis.
- **Unresolved questions:** [S1-Q-009](#s1-q-009)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-014"></a>

### REQ-03-014 - Evidence-supported trade-plan contents

- **Requirement description:** R1 trade plans shall state evidence-supported entry, exit, stop-loss, targets, sizing and risk/reward using deterministic calculations.
- **Source / originating decision:** PROJECT_OVERVIEW: Trade planning; REQUIREMENTS_INDEX: REQ-03; Human-R1-Approval.
- **Category / owner:** Trade planning; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-001](#req-03-001), [REQ-03-011](#req-03-011), [REQ-03-015](#req-03-015), [REQ-03-038](#req-03-038)
- **Data availability assumptions:** DATA-005; approved risk inputs and costs unavailable.
- **Planned verification:** VER-03-014 - Review a fully supported plan and a plan with missing required inputs.
- **Acceptance criteria:** Plan fields trace to eligible evidence, strategy/risk inputs and a recommendation version; missing mandatory inputs withhold unsupported plans without fabricating values.
- **Unresolved questions:** [S1-Q-006](#s1-q-006), [S1-Q-007](#s1-q-007), [S1-Q-008](#s1-q-008), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Apply approved R1 scope and versioned recommendation linkage.

<a id="req-03-015"></a>

### REQ-03-015 - Portfolio allocation and sizing policy

- **Requirement description:** Allocations, risk limits, sizing, rounding and permitted position/financing rules remain to be agreed for paper and manually maintained portfolios.
- **Source / originating decision:** D-06; D-15; OPEN_QUESTIONS: 1; Human-R1-Approval.
- **Category / owner:** Portfolio risk; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-01-007](#req-01-007), [REQ-03-009](#req-03-009)
- **Data availability assumptions:** Configurable hypothetical capital known; allocations, limits and cost inputs unresolved.
- **Planned verification:** VER-03-015 - Review sizing, insufficient-cash and limit-boundary scenarios after policy approval.
- **Acceptance criteria:** Policies preserve the configurable ₹20 lakh hypothetical reference and require user-provided actual opening state; no actual balance, leverage, allocation or risk limit is inferred.
- **Unresolved questions:** [S1-Q-007](#s1-q-007), [S1-Q-008](#s1-q-008), [R1-Q-003](#r1-q-003), [R1-Q-009](#r1-q-009)
- **R1 change:** Revised; Keep financial policy Open and separate reference from actual state.

<a id="req-03-016"></a>

### REQ-03-016 - Consolidated cross-strategy exposure

- **Requirement description:** Portfolio risk shall aggregate exposure, cash commitments and horizon attribution within each portfolio while keeping paper and manually recorded actual portfolios separate.
- **Source / originating decision:** PROJECT_OVERVIEW: Supported horizons; REQUIREMENTS_INDEX: REQ-03; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Portfolio risk; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-010](#req-03-010), [REQ-03-015](#req-03-015)
- **Data availability assumptions:** Portfolio state and correlation methodology not established.
- **Planned verification:** VER-03-016 - Review overlapping ETF holdings and contradictory horizon plans.
- **Acceptance criteria:** Horizon exposure and commitments reconcile without duplicate holdings; simulated and user-reported actual exposures are not merged. Correlation and limit methodology remains open.
- **Unresolved questions:** [S1-Q-007](#s1-q-007), [R1-Q-003](#r1-q-003), [R1-Q-007](#r1-q-007)
- **R1 change:** Revised; Apply approved portfolio-level risk and mode separation.

<a id="req-03-017"></a>

### REQ-03-017 - Evidence-supported alternative GTT scenarios

- **Requirement description:** The platform shall generate up to three GTT scenarios only where evidence supports them, allowing no-trade.
- **Source / originating decision:** D-05.
- **Category / owner:** Trade planning; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-011](#req-03-011), [REQ-03-014](#req-03-014)
- **Data availability assumptions:** Evidence must meet the eventual approved strategy/data rules.
- **Planned verification:** VER-03-017 - Review cases supporting zero, one, two or three scenarios.
- **Acceptance criteria:** Scenario count never exceeds three and is not forced to three; unsupported conditions can yield no-trade.
- **Unresolved questions:** [S1-Q-006](#s1-q-006)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-018"></a>

### REQ-03-018 - Canonical deterministic trade-plan representation

- **Requirement description:** Trade planning shall retain one broker-independent deterministic, explainable canonical representation distinct from recommendations, paper orders, manual records and future execution.
- **Source / originating decision:** D-11; Human-R1-Approval.
- **Category / owner:** Trade-plan contract; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-014](#req-03-014), [REQ-03-017](#req-03-017)
- **Data availability assumptions:** No broker connection is needed to define the representation.
- **Planned verification:** VER-03-018 - Review canonical plan semantics and repeat the same plan calculation.
- **Acceptance criteria:** A versioned canonical plan is inspectable without broker access; selecting or publishing it does not imply order submission or a fill.
- **Unresolved questions:** [S1-Q-010](#s1-q-010), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Preserve D-11 while distinguishing execution artifacts.

<a id="req-03-019"></a>

### REQ-03-019 - Capability-aware broker representations

- **Requirement description:** The canonical plan shall support up to two broker-specific representations subject to verified broker capability.
- **Source / originating decision:** D-11; PROJECT_OVERVIEW: Trade planning; User-Stage1; Human-R1-Approval.
- **Category / owner:** Trade-plan contract; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Conditional on selected and verified broker rendering; R1-C if rendering selected.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-018](#req-03-018), [REQ-05-005](#req-05-005)
- **Data availability assumptions:** Broker capability evidence unavailable; no linked entry/protective exit or OCO assumption.
- **Planned verification:** VER-03-019 - Compare mappings with dated broker evidence and an unsupported-capability case.
- **Acceptance criteria:** At most two broker renderings are supported when selected and verified; broker-neutral instructions remain required. Renderings neither connect an account nor place or guarantee orders.
- **Unresolved questions:** [S1-Q-010](#s1-q-010), [R1-Q-010](#r1-q-010)
- **R1 change:** Revised; Keep rendering scope conditional, without broker connectivity.

<a id="req-03-020"></a>

### REQ-03-020 - Trade-plan validity and reassessment policy

- **Requirement description:** Trade-plan validity, expiration, cancellation and reassessment details remain to be agreed; recommendation states, paper orders and manual accounting have separate owners.
- **Source / originating decision:** OPEN_QUESTIONS: 2 and 12; REQUIREMENTS_INDEX: REQ-03; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Trade-plan lifecycle; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-03-015](#req-03-015), [REQ-03-018](#req-03-018)
- **Data availability assumptions:** Actual broker/account state is unavailable without separate authorization.
- **Planned verification:** VER-03-020 - Walk through changed-market, partial-fill, expired-plan and manual-update cases.
- **Acceptance criteria:** The plan policy references REQ-03-038 recommendation states, REQ-03-024/029 paper states and REQ-03-034 manual records without conflation or invented expiry durations.
- **Unresolved questions:** [S1-Q-010](#s1-q-010), [R1-Q-005](#r1-q-005), [R1-Q-007](#r1-q-007), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Separate existing plan-policy questions from new state/accounting records.

<a id="req-03-021"></a>

### REQ-03-021 - Alternative-scenario capital interaction

- **Requirement description:** Alternative GTT scenarios shall expose exclusivity or combined exposure, capital reservation and trigger/cancellation relationships under approved rules.
- **Source / originating decision:** D-05; REQUIREMENTS_INDEX: REQ-03; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Portfolio risk; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-016](#req-03-016), [REQ-03-017](#req-03-017), [REQ-03-020](#req-03-020)
- **Data availability assumptions:** Scenario relationships and capital-reservation rules unresolved.
- **Planned verification:** VER-03-021 - Review two alternative triggers and multiple-horizon plans using the same cash.
- **Acceptance criteria:** Concurrent alternatives/horizons respect shared commitments; no single-fill, automatic OCO or broker cancellation behavior is assumed. REQ-03-030 specializes reservations.
- **Unresolved questions:** [S1-Q-007](#s1-q-007), [S1-Q-010](#s1-q-010), [R1-Q-007](#r1-q-007)
- **R1 change:** Revised; Apply approved scenario interactions; exact rules remain open.

<a id="req-03-022"></a>

### REQ-03-022 - Phase 2 ML analytical capability

- **Requirement description:** Phase 2 ML analytics remain subject to human-approved forecast targets, features, horizons and advisory-use definitions.
- **Source / originating decision:** D-09; OPEN_QUESTIONS: 9.
- **Category / owner:** ML extension; REQ-03.
- **Priority / proposed phase:** Should; Phase 2.
- **R1 applicability / increment:** Deferred capability; relevant extension requirements remain Phase 1; Outside R1 capability.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-05-011](#req-05-011), [REQ-06-012](#req-06-012)
- **Data availability assumptions:** Point-in-time training labels and sufficient history unverified.
- **Planned verification:** VER-03-022 - Review target/label definitions and permitted use against deterministic baselines.
- **Acceptance criteria:** The Phase 2 capability is assessable against target definitions and deterministic baselines documented during Phase 1; no training or implementation is authorized by this record.
- **Unresolved questions:** [S1-Q-015](#s1-q-015)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-03-023"></a>

### REQ-03-023 - Virtual cash and positions

- **Requirement description:** Paper trading shall maintain virtual cash and positions with configurable hypothetical opening state.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper accounting; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-007](#req-01-007), [REQ-01-011](#req-01-011), [REQ-03-015](#req-03-015)
- **Data availability assumptions:** Reference is ₹20 lakh and configurable; actual opening balances not inferred.
- **Planned verification:** VER-03-023 - Review initialization, fills and insufficient-cash cases.
- **Acceptance criteria:** Paper balances reconcile to opening state and eligible paper events, independently of manually recorded actual holdings.
- **Unresolved questions:** [R1-Q-003](#r1-q-003), [R1-Q-007](#r1-q-007), [R1-Q-008](#r1-q-008)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-024"></a>

### REQ-03-024 - Simulated order lifecycle

- **Requirement description:** Paper orders shall have an attributable lifecycle distinct from recommendations, plans and real orders.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper lifecycle; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-023](#req-03-023), [REQ-03-018](#req-03-018)
- **Data availability assumptions:** Approved order types/state-transition rules remain open.
- **Planned verification:** VER-03-024 - Review submission, trigger eligibility, fill, partial fill and terminal events.
- **Acceptance criteria:** Only approved transitions change paper state; every state-changing event is traceable and cannot affect a real account.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-005](#r1-q-005), [R1-Q-007](#r1-q-007)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-025"></a>

### REQ-03-025 - Entry and exit trigger evaluation

- **Requirement description:** Paper entry and exit triggers shall be evaluated against eligible observations and approved activation rules.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper simulation; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-024](#req-03-024), [REQ-02-017](#req-02-017), [REQ-03-038](#req-03-038)
- **Data availability assumptions:** Qualified observations at approved timing; no assumed same-bar sequence.
- **Planned verification:** VER-03-025 - Review entry before/after exit activation and late observations.
- **Acceptance criteria:** The result identifies trigger evidence and timing policy; exits do not silently become active before their approved eligibility condition.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-005](#r1-q-005)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-026"></a>

### REQ-03-026 - Fill pricing and within-bar ambiguity

- **Requirement description:** Simulated fill prices, gaps and ambiguous within-bar event order shall follow an explicit approved policy.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper simulation; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-025](#req-03-025), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** DATA-005 may not establish intraday sequencing or executable quotes.
- **Planned verification:** VER-03-026 - Review gaps and entry/stop/target touches in one bar.
- **Acceptance criteria:** No favorable ordering or guaranteed stop price is invented; unresolved policy prevents asserting a definitive fill.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-005](#r1-q-005)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-027"></a>

### REQ-03-027 - Paper costs and slippage

- **Requirement description:** Paper accounting shall expose transaction-cost and slippage assumptions and their effect on results.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper accounting; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-009](#req-03-009), [REQ-03-026](#req-03-026)
- **Data availability assumptions:** Historical/current fees and slippage inputs not verified; no zero-cost default.
- **Planned verification:** VER-03-027 - Review a fill with costs and an incomplete cost profile.
- **Acceptance criteria:** Assumptions are approved and versioned; gross and net impacts are distinguishable and missing costs are disclosed.
- **Unresolved questions:** [R1-Q-006](#r1-q-006), [R1-Q-008](#r1-q-008)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-028"></a>

### REQ-03-028 - Liquidity and partial fills

- **Requirement description:** Simulated fills shall reflect an approved liquidity and partial-fill policy appropriate to available observations.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper simulation; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-026](#req-03-026), [REQ-02-017](#req-02-017)
- **Data availability assumptions:** Volume alone need not establish executable liquidity; no participation rate assumed.
- **Planned verification:** VER-03-028 - Review insufficient liquidity, partial and remaining quantities.
- **Acceptance criteria:** Filled/remaining quantities and limitations are attributable; no full-fill or arbitrary participation assumption is hidden.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-006](#r1-q-006)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-029"></a>

### REQ-03-029 - Paper expiration and cancellation

- **Requirement description:** Paper order expiration and cancellation shall follow approved rules without changing real orders.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Paper lifecycle; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-024](#req-03-024), [REQ-03-020](#req-03-020)
- **Data availability assumptions:** Expiry durations and cancellation/trigger ordering unresolved.
- **Planned verification:** VER-03-029 - Review cancel/expire versus trigger races.
- **Acceptance criteria:** Only approved timing rules determine terminal state and remaining quantity; no expiry duration is invented.
- **Unresolved questions:** [R1-Q-005](#r1-q-005), [R1-Q-007](#r1-q-007)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-030"></a>

### REQ-03-030 - Capital reservation and release

- **Requirement description:** Paper orders shall reserve and release capital according to approved portfolio and alternative-scenario rules.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Portfolio risk; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-023](#req-03-023), [REQ-03-024](#req-03-024), [REQ-03-021](#req-03-021)
- **Data availability assumptions:** Reservation, cost allowance and scenario exclusivity rules unresolved.
- **Planned verification:** VER-03-030 - Review simultaneous alternatives, partial fills, cancellation and expiry.
- **Acceptance criteria:** Available and committed capital reconcile; alternatives cannot silently reuse funds and reservation release follows approved state rules.
- **Unresolved questions:** [R1-Q-003](#r1-q-003), [R1-Q-006](#r1-q-006), [R1-Q-007](#r1-q-007)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-031"></a>

### REQ-03-031 - Realized and unrealized P&L

- **Requirement description:** Portfolio accounting shall distinguish realized and unrealized P&L with explicit cost basis, marks, charges and adjustments.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Portfolio accounting; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C for manual records.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-023](#req-03-023), [REQ-03-027](#req-03-027), [REQ-02-007](#req-02-007), [REQ-03-039](#req-03-039)
- **Data availability assumptions:** Cost-basis, mark, corporate-action and manual-history completeness unresolved.
- **Planned verification:** VER-03-031 - Compare independent worked purchase/sale/mark cases.
- **Acceptance criteria:** P&L reconciles within each performance class and discloses incomplete prices/costs; no simulated amount becomes an actual result.
- **Unresolved questions:** [R1-Q-008](#r1-q-008), [R1-Q-009](#r1-q-009)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-032"></a>

### REQ-03-032 - Performance and drawdown reporting

- **Requirement description:** R1 shall report portfolio performance and drawdown with explicit cash-flow, valuation and period conventions.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Performance; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-031](#req-03-031), [REQ-03-034](#req-03-034), [REQ-03-035](#req-03-035), [REQ-03-039](#req-03-039)
- **Data availability assumptions:** Return/drawdown methodology, marks, cash flows and benchmarks unresolved.
- **Planned verification:** VER-03-032 - Review deposits/withdrawals, partial history and a drawdown path.
- **Acceptance criteria:** Performance identifies its class, period, costs and method; cash flows and incomplete history do not silently become investment return.
- **Unresolved questions:** [R1-Q-008](#r1-q-008), [R1-Q-009](#r1-q-009), [R1-Q-015](#r1-q-015)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-033"></a>

### REQ-03-033 - Reproducible paper event history

- **Requirement description:** Paper outcomes shall be auditable and reproducible from eligible evidence and versioned simulation/strategy policies.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Simulation provenance; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-024](#req-03-024), [REQ-03-025](#req-03-025), [REQ-03-026](#req-03-026), [REQ-03-027](#req-03-027), [REQ-03-028](#req-03-028), [REQ-03-029](#req-03-029), [REQ-03-030](#req-03-030), [REQ-03-031](#req-03-031), [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Original observations and policy/version history must be retained under approved permissions.
- **Planned verification:** VER-03-033 - Reproduce a paper event sequence with the same evidence and versions.
- **Acceptance criteria:** Reproduction explains the original result and revisions; replay is not mislabeled as newly collected forward evidence.
- **Unresolved questions:** [R1-Q-012](#r1-q-012), [R1-Q-014](#r1-q-014)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-034"></a>

### REQ-03-034 - Manual actual-order and fill recording

- **Requirement description:** Actual orders/fills shall be recorded as user reports, with corrections and attributable history separate from paper events.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Manual accounting; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-012](#req-01-012), [REQ-02-018](#req-02-018)
- **Data availability assumptions:** DATA-008; neither complete nor broker-verified by default.
- **Planned verification:** VER-03-034 - Review a partial reported fill, correction and duplicate entry.
- **Acceptance criteria:** Original reports and corrections remain attributable; recording changes no external order and claims no broker verification.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-035"></a>

### REQ-03-035 - Actual opening state and cash flows

- **Requirement description:** Manually maintained portfolios shall use user-provided opening state and external cash-flow records.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Manual accounting; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-034](#req-03-034), [REQ-03-015](#req-03-015)
- **Data availability assumptions:** DATA-008: opening balances, holdings and cash flows may be incomplete.
- **Planned verification:** VER-03-035 - Review an existing holding, deposit, withdrawal and missing cost basis.
- **Acceptance criteria:** The manual portfolio never assumes the hypothetical ₹20 lakh as actual capital; incompleteness is disclosed in risk and performance.
- **Unresolved questions:** [R1-Q-008](#r1-q-008), [R1-Q-009](#r1-q-009)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-036"></a>

### REQ-03-036 - Daily position and recommendation reassessment

- **Requirement description:** R1 shall reassess paper/manual positions and recommendations daily using eligible evidence, strategy versions and risk policy.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Reassessment; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-038](#req-03-038), [REQ-03-010](#req-03-010), [REQ-03-016](#req-03-016), [REQ-03-034](#req-03-034), [REQ-03-023](#req-03-023), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** Current eligible market data and attributable position state required.
- **Planned verification:** VER-03-036 - Review changed evidence, risk breach and stale data.
- **Acceptance criteria:** Reassessment records its evidence and resulting recommendation version/status; no actual order or old published record is silently changed.
- **Unresolved questions:** [R1-Q-003](#r1-q-003), [R1-Q-011](#r1-q-011), [R1-Q-013](#r1-q-013)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-037"></a>

### REQ-03-037 - Broker-neutral placement instructions

- **Requirement description:** R1 shall provide human-readable broker-neutral placement and monitoring instructions for supported plans.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Manual execution support; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-018](#req-03-018), [REQ-03-020](#req-03-020)
- **Data availability assumptions:** Broker-specific semantics remain unverified unless a rendering is selected.
- **Planned verification:** VER-03-037 - Walk a plan with no broker selection and an unsupported broker feature.
- **Acceptance criteria:** Instructions distinguish triggers/orders, protective-action responsibilities and unverified capabilities without submitting or guaranteeing a real order.
- **Unresolved questions:** [R1-Q-010](#r1-q-010), [R1-Q-013](#r1-q-013)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-038"></a>

### REQ-03-038 - Versioned recommendation lifecycle

- **Requirement description:** Recommendations shall follow Draft -> Validated -> Published -> Superseded / Expired / Withdrawn with versioned evidence, validity conditions, strategy references, risk checks and reassessment history.
- **Source / originating decision:** Human-R1-Approval: Refinement C; D-12.
- **Category / owner:** Recommendation lifecycle; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C daily reassessment.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-011](#req-03-011), [REQ-03-015](#req-03-015), [REQ-02-012](#req-02-012), [REQ-06-018](#req-06-018)
- **Data availability assumptions:** Evidence timestamps and required check definitions unresolved; no expiry duration assumed.
- **Planned verification:** VER-03-038 - Walk publication, supersession, expiry and withdrawal with traceable prior versions.
- **Acceptance criteria:** Every state/version identifies evidence as-of/publication context, validity conditions, strategy version and risk-check outcome; Published is not execution, and lifecycle Validated is not a claim of profitability or requirement readiness. Extra transitions/authority remain open.
- **Unresolved questions:** [R1-Q-011](#r1-q-011), [R1-Q-013](#r1-q-013), [R1-Q-014](#r1-q-014)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-03-039"></a>

### REQ-03-039 - Separated performance classes

- **Requirement description:** Historical strategy, forward paper, manually recorded actual-trade and benchmark performance shall remain distinct, with backtest and OOS/walk-forward results separately identifiable within historical evidence.
- **Source / originating decision:** Human-R1-Approval: Refinement D.
- **Category / owner:** Performance governance; REQ-03.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C complete reporting.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-06-018](#req-06-018)
- **Data availability assumptions:** No performance results exist or are asserted by this package.
- **Planned verification:** VER-03-039 - Inspect a comparison containing all performance classes.
- **Acceptance criteria:** Comparisons label class, strategy/version, period, costs and method; no simulated/actual composite or synthetic aggregate return is presented as one track record.
- **Unresolved questions:** [R1-Q-008](#r1-q-008), [R1-Q-014](#r1-q-014), [R1-Q-015](#r1-q-015)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## REQ-04 - Interactive AI Research Assistant

<a id="req-04-001"></a>

### REQ-04-001 - Research dashboard experience

- **Requirement description:** The dashboard shall support R1 research, trade plans and clearly identified paper/manual portfolio context.
- **Source / originating decision:** D-07; PROJECT_OVERVIEW: Experience; Human-R1-Approval.
- **Category / owner:** User experience; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-008](#req-01-008)
- **Data availability assumptions:** Displayed evidence depends on included analytical capabilities.
- **Planned verification:** VER-04-001 - Walk through dashboard research and evidence inspection.
- **Acceptance criteria:** Users can inspect evidence and identify the active portfolio/mode; simulated and user-reported actual outcomes remain distinguishable.
- **Unresolved questions:** [S1-Q-001](#s1-q-001), [S1-Q-013](#s1-q-013)
- **R1 change:** Revised; Extend dashboard to usable R1 workflows.

<a id="req-04-002"></a>

### REQ-04-002 - Conversational research experience

- **Requirement description:** Conversational AI shall support R1 research and explanations of strategies, recommendation versions and selected-portfolio context within advisory scope.
- **Source / originating decision:** D-07; PROJECT_OVERVIEW: Experience; Human-R1-Approval.
- **Category / owner:** AI interaction; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-001](#req-01-001), [REQ-01-008](#req-01-008)
- **Data availability assumptions:** Authorized analytical/data tools not yet selected.
- **Planned verification:** VER-04-002 - Review representative gold/silver and contextual questions.
- **Acceptance criteria:** Answers identify evidence, relevant recommendation versions and limitations without fabricating numbers or real execution status.
- **Unresolved questions:** [S1-Q-012](#s1-q-012)
- **R1 change:** Revised; Extend conversation to approved R1 context.

<a id="req-04-003"></a>

### REQ-04-003 - Advisory-only action boundary

- **Requirement description:** R1 shall not connect to brokers or place, modify or cancel real orders; paper operations and manual recording of externally reported transactions remain distinct and permitted.
- **Source / originating decision:** D-03; AGENTS: Governance; User-Stage1; Human-R1-Approval.
- **Category / owner:** AI constraint; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** No brokerage credentials or account access assumed.
- **Planned verification:** VER-04-003 - Review action permissions and requests to place orders or connect accounts.
- **Acceptance criteria:** Paper actions affect only virtual state; recording a reported transaction neither submits an order nor makes it broker-verified. D-03 remains binding.
- **Unresolved questions:** [S1-Q-012](#s1-q-012), [R1-Q-012](#r1-q-012)
- **R1 change:** Revised; Clarify real versus simulated operations without relaxing D-03.

<a id="req-04-004"></a>

### REQ-04-004 - Dynamic market-data discovery interaction

- **Requirement description:** The assistant shall proactively seek relevant missing market evidence and may fetch permitted data automatically.
- **Source / originating decision:** D-01; PROJECT_OVERVIEW: Experience.
- **Category / owner:** AI interaction; REQ-04.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-016](#req-02-016), [REQ-04-003](#req-04-003)
- **Data availability assumptions:** Candidate data is unverified until qualified; retrieval permissions unresolved.
- **Planned verification:** VER-04-004 - Review a missing-input research case and a disallowed retrieval case.
- **Acceptance criteria:** The interaction identifies the evidence gap, seeks permitted source candidates or reports unavailability, and follows data qualification rather than inventing observations.
- **Unresolved questions:** [S1-Q-002](#s1-q-002), [S1-Q-012](#s1-q-012)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-005"></a>

### REQ-04-005 - Generated interpretation versus financial results

- **Requirement description:** Assistant outputs shall distinguish generated interpretation, deterministic calculations, hypothetical scenarios, simulated results and user-reported actual transactions.
- **Source / originating decision:** AGENTS: AI advisory and deterministic calculations; proposed elaboration; Human-R1-Approval.
- **Category / owner:** AI explanation; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-001](#req-03-001), [REQ-03-018](#req-03-018)
- **Data availability assumptions:** Attributable calculation outputs required.
- **Planned verification:** VER-04-005 - Review a narrative with financial values and a hypothetical what-if.
- **Acceptance criteria:** Numbers and performance identify their calculation/evidence class; narrative cannot alter them or imply broker verification.
- **Unresolved questions:** [S1-Q-012](#s1-q-012)
- **R1 change:** Revised; Apply interpretation and performance separation.

<a id="req-04-006"></a>

### REQ-04-006 - Evidence timestamps and uncertainty

- **Requirement description:** Research shall show sources, timestamps and uncertainty without fabricated data, signals, probabilities or backtest results.
- **Source / originating decision:** AGENTS: Governance.
- **Category / owner:** AI evidence; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Evidence may be incomplete or unavailable.
- **Planned verification:** VER-04-006 - Review supported claims, unavailable results and stale evidence.
- **Acceptance criteria:** Material market claims identify supporting evidence and time context; absent evidence is disclosed and no performance result is invented.
- **Unresolved questions:** [S1-Q-005](#s1-q-005)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-007"></a>

### REQ-04-007 - What-if scenario analysis

- **Requirement description:** The assistant should support what-if research with explicit assumptions and reproducible calculation inputs.
- **Source / originating decision:** DISCUSSION_SUMMARY: AI scope; REQUIREMENTS_INDEX: REQ-04.
- **Category / owner:** AI interaction; REQ-04.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-04-005](#req-04-005), [REQ-03-001](#req-03-001)
- **Data availability assumptions:** Scenario inputs may be hypothetical and must be labeled.
- **Planned verification:** VER-04-007 - Review a changed-input scenario against its baseline.
- **Acceptance criteria:** Changed assumptions are explicit, deterministic results can be traced, and hypothetical outputs are not presented as observations or forecasts with proven reliability.
- **Unresolved questions:** [S1-Q-012](#s1-q-012)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-008"></a>

### REQ-04-008 - Retained research and recommendation evidence

- **Requirement description:** Research/recommendation versions shall retain original evidence and as-of context for personal-use review; conversational retention details remain policy-dependent.
- **Source / originating decision:** DISCUSSION_SUMMARY: AI scope; REQUIREMENTS_INDEX: REQ-04; Human-R1-Approval.
- **Category / owner:** AI context; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-04-006](#req-04-006), [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Retention/storage and user access policy unresolved.
- **Planned verification:** VER-04-008 - Review saved research after a source revision and a later signal.
- **Acceptance criteria:** Original and reassessed versions remain distinct; audit retention does not imply indefinite chat retention or external sharing permission.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-012](#s1-q-012), [R1-Q-012](#r1-q-012), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Promote essential retained evidence, not unlimited conversation storage.

<a id="req-04-009"></a>

### REQ-04-009 - Targeted missing-input questions

- **Requirement description:** The assistant shall ask targeted questions when missing user-provided inputs prevent supported research or planning.
- **Source / originating decision:** PROJECT_OVERVIEW: Experience; D-01; Human-R1-Approval.
- **Category / owner:** AI interaction; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-04-002](#req-04-002)
- **Data availability assumptions:** Missing portfolio/risk inputs must not be inferred.
- **Planned verification:** VER-04-009 - Review a request lacking risk settings or required evidence.
- **Acceptance criteria:** The assistant identifies necessary missing inputs and asks targeted questions rather than silently supplying financial assumptions.
- **Unresolved questions:** [S1-Q-007](#s1-q-007), [S1-Q-012](#s1-q-012), [R1-Q-003](#r1-q-003)
- **R1 change:** Revised; Promote missing-user-input behavior required for valid plans.

<a id="req-04-010"></a>

### REQ-04-010 - Scheduled EOD research report

- **Requirement description:** R1 shall provide daily EOD intelligence reports with identifiable recommendation and selected-portfolio reassessment content.
- **Source / originating decision:** D-07; D-16; Human-R1-Approval.
- **Category / owner:** Reporting; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A intelligence; R1-C position reassessment.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-05-006](#req-05-006), [REQ-04-006](#req-04-006)
- **Data availability assumptions:** Reliable inputs at an approved cutoff; delivery channel unresolved.
- **Planned verification:** VER-04-010 - Review a report with complete evidence and one with unavailable inputs.
- **Acceptance criteria:** Reports identify cutoff, quality, recommendation versions and portfolio mode. Daily reassessment does not alter real orders or rewrite prior recommendations.
- **Unresolved questions:** [S1-Q-001](#s1-q-001), [S1-Q-005](#s1-q-005), [S1-Q-014](#s1-q-014), [R1-Q-011](#r1-q-011), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Daily intelligence in R1-A; cumulative position reassessment in R1-C.

<a id="req-04-011"></a>

### REQ-04-011 - Event investigation and reassessment

- **Requirement description:** Event-driven intelligence shall provide alerts and research reassessment, without automatic trades, where reliable data permits.
- **Source / originating decision:** D-07; D-13; D-16.
- **Category / owner:** Event research; REQ-04.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-05-007](#req-05-007), [REQ-04-003](#req-04-003), [REQ-04-006](#req-04-006)
- **Data availability assumptions:** Reliable event sources and coverage not established.
- **Planned verification:** VER-04-011 - Review an eligible event and an event with unreliable inputs.
- **Acceptance criteria:** An eligible event leads to attributable advisory research/alert behavior; unavailable event evidence does not trigger fabricated reassessment or a trade.
- **Unresolved questions:** [S1-Q-005](#s1-q-005), [S1-Q-014](#s1-q-014)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-012"></a>

### REQ-04-012 - Assistant tool and context policy

- **Requirement description:** Permitted tools, automatic retrieval limits, context retention, untrusted-source handling and unsupported-request behavior remain to be agreed.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-04; OPEN_QUESTIONS: 4 and 10; proposed elaboration.
- **Category / owner:** AI governance; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-04-003](#req-04-003), [REQ-02-008](#req-02-008)
- **Data availability assumptions:** External retrieval and model-service permissions not established.
- **Planned verification:** VER-04-012 - Review allowed/disallowed tools, malicious retrieved instructions and unsupported requests.
- **Acceptance criteria:** Human-approved policies bound tool actions and protect context; retrieved content cannot itself grant permission or override system rules.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-012](#s1-q-012)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-013"></a>

### REQ-04-013 - Research chart evidence and semantics

- **Requirement description:** Research charts should identify series, units, transformations, as-of context and source coverage.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-04; proposed elaboration.
- **Category / owner:** User experience; REQ-04.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-04-001](#req-04-001), [REQ-04-006](#req-04-006), [REQ-02-011](#req-02-011)
- **Data availability assumptions:** Chart series depend on included, permitted datasets.
- **Planned verification:** VER-04-013 - Review cross-currency, stale-series and revised-history charts.
- **Acceptance criteria:** Chart labels and evidence links expose units, transformations and time context; missing observations are not silently presented as measured data.
- **Unresolved questions:** [S1-Q-005](#s1-q-005), [S1-Q-013](#s1-q-013)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-04-014"></a>

### REQ-04-014 - Paper workflow and simulation disclosure

- **Requirement description:** The user experience shall clearly identify paper orders, simulated fills and virtual portfolio effects.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** User experience; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-024](#req-03-024), [REQ-04-003](#req-04-003), [REQ-05-013](#req-05-013)
- **Data availability assumptions:** Paper state and approved simulation policies.
- **Planned verification:** VER-04-014 - Walk paper submission, fill review and cancellation.
- **Acceptance criteria:** The active mode and simulation limitations remain visible; paper actions cannot appear to submit real orders.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-04-015"></a>

### REQ-04-015 - Manual recording and unverified disclosure

- **Requirement description:** The user experience shall distinguish manual reporting/correction of actual transactions from paper trading and broker submission.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** User experience; REQ-04.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-034](#req-03-034), [REQ-04-003](#req-04-003), [REQ-05-013](#req-05-013)
- **Data availability assumptions:** DATA-008: user-reported information.
- **Planned verification:** VER-04-015 - Walk initial entry, correction and performance inspection.
- **Acceptance criteria:** Records show user-reported/unverified provenance and portfolio identity; neither a user action nor an attachment is labeled broker verification.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## REQ-05 - System Architecture and Nonfunctional Requirements

<a id="req-05-001"></a>

### REQ-05-001 - Accepted backend and persistence constraints

- **Requirement description:** The requirements shall preserve Python/FastAPI and PostgreSQL in local Docker with persistent storage as accepted engineering direction.
- **Source / originating decision:** DECISION_REGISTER: Additional accepted engineering direction.
- **Category / owner:** Technology constraint; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: accepted technology constraints.
- **Planned verification:** VER-05-001 - Inspect the architecture constraints section against accepted direction.
- **Acceptance criteria:** The named constraints are retained; frontend, broker configuration and hosting choices remain explicitly undecided.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-013](#s1-q-013)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-002"></a>

### REQ-05-002 - Cross-component semantic contracts

- **Requirement description:** Logical interfaces should preserve data, model, strategy, portfolio, recommendation-version, plan and evidence/performance-class semantics.
- **Source / originating decision:** DISCUSSION_SUMMARY: Analytical architecture; REQUIREMENTS_INDEX: REQ-05; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Interface requirement; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-011](#req-02-011), [REQ-03-002](#req-03-002), [REQ-03-018](#req-03-018), [REQ-04-005](#req-04-005)
- **Data availability assumptions:** Canonical definitions are inputs; no transport/deployment style selected.
- **Planned verification:** VER-05-002 - Walk a dated research request across logical responsibilities.
- **Acceptance criteria:** Contracts distinguish research, plans, paper events, manual events and future candidates without prescribing service decomposition, transport or framework.
- **Unresolved questions:** [S1-Q-013](#s1-q-013)
- **R1 change:** Revised; Extend interface semantics without implementation choices.

<a id="req-05-003"></a>

### REQ-05-003 - Sensitive-information protection

- **Requirement description:** Credentials, tokens, account identifiers and personal portfolio data shall not be committed to the repository.
- **Source / originating decision:** AGENTS: Governance.
- **Category / owner:** Security constraint; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** No real credentials or portfolio data required for review.
- **Planned verification:** VER-05-003 - Review secret/configuration rules using synthetic examples.
- **Acceptance criteria:** Repository content and review fixtures exclude real secrets, account identifiers and personal portfolio data.
- **Unresolved questions:** None identified for this obligation; later review may identify more.
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-004"></a>

### REQ-05-004 - Access privacy and secrets policy

- **Requirement description:** Personal-use access, deployment, external AI sharing, secrets and transaction/context retention policies remain to be agreed.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-05; OPEN_QUESTIONS: 10; Human-R1-Approval.
- **Category / owner:** Security; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-05-003](#req-05-003)
- **Data availability assumptions:** User model, deployment boundary and external-service permissions unresolved.
- **Planned verification:** VER-05-004 - Review access and data-flow scenarios for the selected deployment boundary.
- **Acceptance criteria:** A human-approved policy identifies actors, permitted data flows, retention and secret handling; local-only operation or cloud use is not assumed.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [R1-Q-012](#r1-q-012)
- **R1 change:** Revised; Add personal-transaction privacy scope without choosing deployment.

<a id="req-05-005"></a>

### REQ-05-005 - Broker capability evidence contract

- **Requirement description:** Broker capability records should provide dated evidence for supported trigger/order semantics, tick rules and lifecycle limitations used by renderings.
- **Source / originating decision:** D-11; OPEN_QUESTIONS: 2; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Interface requirement; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Conditional on selected and verified broker rendering; R1-C if rendering selected.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-03-018](#req-03-018), [REQ-04-003](#req-04-003)
- **Data availability assumptions:** Broker documentation/capabilities unverified; no API or account access assumed.
- **Planned verification:** VER-05-005 - Review a rendering against broker evidence and an unsupported linked-exit case.
- **Acceptance criteria:** Dated evidence supports broker-specific instructions; unverified capabilities remain visible, and broker-neutral instructions require no account or API connection.
- **Unresolved questions:** [S1-Q-010](#s1-q-010), [R1-Q-010](#r1-q-010)
- **R1 change:** Revised; Separate broker documentation from live connectivity.

<a id="req-05-006"></a>

### REQ-05-006 - EOD scheduling and cutoff policy

- **Requirement description:** EOD report cutoffs, time zones, market calendars, delivery time and incomplete-input handling remain to be agreed.
- **Source / originating decision:** D-16; OPEN_QUESTIONS: 7; REQUIREMENTS_INDEX: REQ-05.
- **Category / owner:** Scheduling; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-02-012](#req-02-012), [REQ-02-013](#req-02-013)
- **Data availability assumptions:** US/India calendars and publication times required; completion SLA undecided.
- **Planned verification:** VER-05-006 - Walk US/India holiday, late-publication and delayed-ingestion examples.
- **Acceptance criteria:** Approved scheduling rules identify eligible information and report deadlines without including post-cutoff knowledge.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [S1-Q-014](#s1-q-014)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-007"></a>

### REQ-05-007 - Event and alert delivery policy

- **Requirement description:** Event eligibility, thresholds, hours, delivery channels, deduplication, escalation and expiration remain to be agreed.
- **Source / originating decision:** D-13; D-16; OPEN_QUESTIONS: 7.
- **Category / owner:** Event delivery; REQ-05.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Conditional on selected coverage, reliable data and validation; R1-A.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-02-013](#req-02-013), [REQ-04-003](#req-04-003)
- **Data availability assumptions:** Reliable event feeds and delivery permissions unverified.
- **Planned verification:** VER-05-007 - Walk duplicate, delayed, corrected and out-of-hours event cases.
- **Acceptance criteria:** Approved rules determine whether an event is delivered, suppressed or reassessed; no event causes order execution.
- **Unresolved questions:** [S1-Q-014](#s1-q-014)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-008"></a>

### REQ-05-008 - Measurable service qualities

- **Requirement description:** Performance, capacity, availability, failure handling and recovery targets remain to be agreed for the selected deployment scope.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-05; OPEN_QUESTIONS: 10.
- **Category / owner:** Nonfunctional; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-01-009](#req-01-009), [REQ-05-004](#req-05-004)
- **Data availability assumptions:** Expected workload and operating environment not established.
- **Planned verification:** VER-05-008 - Review measurable scenarios and corresponding acceptance methods.
- **Acceptance criteria:** Each required service quality has an owner, workload/measurement context and human-approved target; no arbitrary SLA is inserted.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-016](#s1-q-016)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-009"></a>

### REQ-05-009 - Backup restoration and retention

- **Requirement description:** Backup, restoration, retention and recovery objectives remain to be agreed for research, paper portfolios and manually maintained records.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-05; OPEN_QUESTIONS: 10; Human-R1-Approval.
- **Category / owner:** Resilience; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-05-001](#req-05-001), [REQ-05-004](#req-05-004)
- **Data availability assumptions:** Retention and permission constraints depend on included data.
- **Planned verification:** VER-05-009 - Review a loss-and-restore scenario and data-retention constraints.
- **Acceptance criteria:** Approved requirements distinguish persistent storage from recoverable backups and define evidence for restoration acceptance.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-016](#s1-q-016), [R1-Q-012](#r1-q-012)
- **R1 change:** Revised; Extend recovery scope to personal portfolio state.

<a id="req-05-010"></a>

### REQ-05-010 - Operational provenance and observability

- **Requirement description:** Operational records should attribute data, strategy, recommendation and simulation-policy versions and report/reassessment outcomes without exposing sensitive information.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-05; AGENTS: traceability; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Observability; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012), [REQ-05-003](#req-05-003)
- **Data availability assumptions:** Access to operational metadata must follow retention/permission policy.
- **Planned verification:** VER-05-010 - Trace a failed input to a withheld output and inspect diagnostic records.
- **Acceptance criteria:** An output/failure can be traced to inputs, versions and processing outcomes while sensitive fields follow the approved protection policy.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-016](#s1-q-016), [R1-Q-012](#r1-q-012), [R1-Q-013](#r1-q-013)
- **R1 change:** Revised; Extend provenance rather than duplicate audit contracts.

<a id="req-05-011"></a>

### REQ-05-011 - Phase 1 ML requirements and extension readiness

- **Requirement description:** Phase 1 shall document Phase 2 ML requirements and design extension points while retaining deterministic Phase 1 analytics.
- **Source / originating decision:** D-09.
- **Category / owner:** ML extension; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-001](#req-03-001), [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Future point-in-time features/labels and history unverified.
- **Planned verification:** VER-05-011 - Review Phase 2 requirements topics and extension needs as requirements artifacts.
- **Acceptance criteria:** Targets, data/evaluation needs, versioning and unresolved ML choices are documented during Phase 1; no ML implementation is introduced.
- **Unresolved questions:** [S1-Q-015](#s1-q-015)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-012"></a>

### REQ-05-012 - Future instrument extension constraints

- **Requirement description:** Architecture requirements shall accommodate later US ETF and MCX futures investment support without treating them as initial investment scope.
- **Source / originating decision:** D-04.
- **Category / owner:** Extensibility; REQ-05.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-01-010](#req-01-010), [REQ-02-011](#req-02-011), [REQ-05-002](#req-05-002)
- **Data availability assumptions:** Future instrument, risk and broker data not validated.
- **Planned verification:** VER-05-012 - Review future-instrument scenarios against logical contract requirements.
- **Acceptance criteria:** Future-use needs identify contract differences and unresolved decisions; no adapter, execution service or future investment capability is scaffolded.
- **Unresolved questions:** [S1-Q-017](#s1-q-017)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-05-013"></a>

### REQ-05-013 - Logical execution-mode boundaries

- **Requirement description:** Logical execution interfaces shall separate recommendations, plans, paper events, manual real-transaction records and future broker candidates without prescribing service decomposition or a framework.
- **Source / originating decision:** Human-R1-Approval: Execution architecture; D-03; D-11.
- **Category / owner:** Interface constraint; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C manual boundary.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-018](#req-03-018), [REQ-04-003](#req-04-003)
- **Data availability assumptions:** No broker connectivity, credentials or API assumed.
- **Planned verification:** VER-05-013 - Review cross-mode operations and future-candidate descriptions.
- **Acceptance criteria:** R1 has no broker connection or real order path; paper/manual effects remain isolated. Future synchronization/placement/automation stays assessment-only and D-03 prohibits autonomous real execution.
- **Unresolved questions:** [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-05-014"></a>

### REQ-05-014 - Persistent attributable activity history

- **Requirement description:** R1 shall retain attributable recommendation, paper and manual-activity history sufficient for approved audit/recovery needs.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Persistence requirement; REQ-05.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C recovery readiness.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012), [REQ-05-003](#req-05-003), [REQ-04-008](#req-04-008)
- **Data availability assumptions:** Retention rights, privacy and restoration policy unresolved.
- **Planned verification:** VER-05-014 - Review restart, correction and restored history scenarios.
- **Acceptance criteria:** State and source/version links remain recoverable under the approved policy; no storage schema, service or immutable-event framework is selected.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012), [R1-Q-013](#r1-q-013)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## REQ-06 - Validation, Governance and Release Requirements

<a id="req-06-001"></a>

### REQ-06-001 - Requirement-to-evidence traceability

- **Requirement description:** Changes shall be traceable from requirement ID to design, code, tests and evidence as those artifacts become authorized and available.
- **Source / originating decision:** AGENTS: Governance; REQUIREMENTS_INDEX: Cross-cutting traceability.
- **Category / owner:** Governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: requirements metadata.
- **Planned verification:** VER-06-001 - Audit representative source-to-requirement-to-verification chains.
- **Acceptance criteria:** Each record has a stable source and planned verification; future design/code/test links are not fabricated or populated before those activities are authorized.
- **Unresolved questions:** None identified for this obligation; later review may identify more.
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-06-002"></a>

### REQ-06-002 - Independent financial calculation verification

- **Requirement description:** Financial calculations shall be reproducible and independently testable.
- **Source / originating decision:** AGENTS: Governance.
- **Category / owner:** Validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-001](#req-03-001)
- **Data availability assumptions:** Reference calculations and controlled input fixtures required.
- **Planned verification:** VER-06-002 - Compare calculations with independently derived reference cases.
- **Acceptance criteria:** Each selected calculation has a stated convention and independent expected result; tolerances requiring judgment remain subject to approval.
- **Unresolved questions:** [S1-Q-006](#s1-q-006), [S1-Q-009](#s1-q-009)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-06-003"></a>

### REQ-06-003 - Point-in-time historical replay

- **Requirement description:** The platform shall support historical replay with point-in-time correctness.
- **Source / originating decision:** D-12; AGENTS: avoid look-ahead, survivorship and rollover bias; Human-R1-Approval.
- **Category / owner:** Validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012), [REQ-02-014](#req-02-014)
- **Data availability assumptions:** Historical instrument membership, vintages and availability evidence unverified.
- **Planned verification:** VER-06-003 - Replay before/after a release revision, instrument change and futures roll.
- **Acceptance criteria:** Replay uses then-available evidence and versions; replaying a simulation does not create new forward evidence or a broker-verified transaction.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Separate historical replay from forward evidence.

<a id="req-06-004"></a>

### REQ-06-004 - Realistic backtest protocol

- **Requirement description:** Historical backtesting shall use documented execution timing, costs, slippage, ETF spreads/adjustments, futures-roll context and historical instrument selection.
- **Source / originating decision:** DISCUSSION_SUMMARY: Confidence; REQUIREMENTS_INDEX: REQ-06; Human-R1-Approval.
- **Category / owner:** Validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-014](#req-02-014), [REQ-03-009](#req-03-009), [REQ-03-011](#req-03-011)
- **Data availability assumptions:** DATA-001; DATA-005; historical cost/quote evidence unverified.
- **Planned verification:** VER-06-004 - Review a protocol and adverse execution/rollover examples.
- **Acceptance criteria:** Backtests identify data, strategy and execution-policy versions and limitations; results remain separate from OOS, forward paper and actual records.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [S1-Q-008](#s1-q-008), [R1-Q-002](#r1-q-002), [R1-Q-006](#r1-q-006), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Explicit historical-validation scope; no cost parameters invented.

<a id="req-06-005"></a>

### REQ-06-005 - Out-of-sample predictive evidence

- **Requirement description:** Walk-forward/out-of-sample evaluation shall retain evidence separate from strategy-development backtesting and forward paper trading.
- **Source / originating decision:** DISCUSSION_SUMMARY: Analytical architecture and Confidence; REQUIREMENTS_INDEX: REQ-06; Human-R1-Approval.
- **Category / owner:** Validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-06-004](#req-06-004), [REQ-03-011](#req-03-011), [REQ-06-018](#req-06-018)
- **Data availability assumptions:** Sufficient uncontaminated history and benchmark data unverified.
- **Planned verification:** VER-06-005 - Review evaluation partitions, parameter-selection history and a proposed performance claim.
- **Acceptance criteria:** Evaluation identifies partitions, selection history, benchmarks and limitations; no future information or unsupported predictive claim is admitted.
- **Unresolved questions:** [S1-Q-004](#s1-q-004), [S1-Q-009](#s1-q-009), [R1-Q-002](#r1-q-002), [R1-Q-014](#r1-q-014)
- **R1 change:** Revised; Implement approved evidence distinction.

<a id="req-06-006"></a>

### REQ-06-006 - Validation and release acceptance thresholds

- **Requirement description:** Evidence sufficiency, tolerances, benchmarks and cumulative R1 gates remain to be agreed without assumed profitability, win-rate targets or validation periods.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-06; OPEN_QUESTIONS: 6 and 11; Human-R1-Approval.
- **Category / owner:** Release governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** [REQ-06-002](#req-06-002), [REQ-06-005](#req-06-005)
- **Data availability assumptions:** Validation evidence does not yet exist.
- **Planned verification:** VER-06-006 - Review a draft pass/fail matrix with approving stakeholders.
- **Acceptance criteria:** Each release gate has a verification method, owner and approved criterion; unsupported financial/performance thresholds are not inserted.
- **Unresolved questions:** [S1-Q-009](#s1-q-009), [S1-Q-016](#s1-q-016), [R1-Q-014](#r1-q-014), [R1-Q-015](#r1-q-015)
- **R1 change:** Revised; Keep thresholds and periods Open.

<a id="req-06-007"></a>

### REQ-06-007 - Assistant evaluation protocol

- **Requirement description:** Assistant evaluations should assess evidence attribution, calculation fidelity, uncertainty, prohibited actions and unsupported requests.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-06; AGENTS: AI advisory; proposed elaboration; Human-R1-Approval.
- **Category / owner:** AI validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-04-005](#req-04-005), [REQ-04-006](#req-04-006), [REQ-04-012](#req-04-012)
- **Data availability assumptions:** Controlled scenarios and approved assistant policies required.
- **Planned verification:** VER-06-007 - Review supported, stale, adversarial and insufficient-evidence conversations.
- **Acceptance criteria:** Cases check attribution, calculation fidelity, recommendation states, mode/performance labels and no real execution; numerical acceptance targets remain open.
- **Unresolved questions:** [S1-Q-012](#s1-q-012), [S1-Q-016](#s1-q-016)
- **R1 change:** Revised; Extend assistant evaluation to R1 lifecycle and separation.

<a id="req-06-008"></a>

### REQ-06-008 - Security and recovery acceptance evidence

- **Requirement description:** Security, permission, sensitive-data handling and restoration requirements should have corresponding acceptance evidence.
- **Source / originating decision:** REQUIREMENTS_INDEX: REQ-06; proposed elaboration; Human-R1-Approval.
- **Category / owner:** Security validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-05-003](#req-05-003), [REQ-05-004](#req-05-004), [REQ-05-009](#req-05-009)
- **Data availability assumptions:** Synthetic fixtures only; deployment and recovery objectives unresolved.
- **Planned verification:** VER-06-008 - Review access denial, secret leakage and restore acceptance scenarios.
- **Acceptance criteria:** Security/restoration evidence covers research and separate paper/manual state under approved policy, using synthetic fixtures and no real secrets.
- **Unresolved questions:** [S1-Q-011](#s1-q-011), [S1-Q-016](#s1-q-016)
- **R1 change:** Revised; Extend security and recovery verification.

<a id="req-06-009"></a>

### REQ-06-009 - Review authority and change approval

- **Requirement description:** Named approval authority, requirements review gates, repository protections and risk sign-off remain to be agreed.
- **Source / originating decision:** OPEN_QUESTIONS: 11; REQUIREMENTS_INDEX: REQ-06; Human-R1-Approval.
- **Category / owner:** Governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Open; Identified.
- **Dependencies:** None identified at Stage 1; this does not assert implementation independence.
- **Data availability assumptions:** None: human governance decision.
- **Planned verification:** VER-06-009 - Review a requirement approval, proposed decision change and release sign-off scenario.
- **Acceptance criteria:** Authority distinguishes R1 increment acceptance, requirement readiness, decision amendments and later implementation authorization; this update authorizes none of those later activities.
- **Unresolved questions:** [S1-Q-016](#s1-q-016)
- **R1 change:** Revised; Preserve governance boundaries.

<a id="req-06-010"></a>

### REQ-06-010 - Independent approval and maturity tracking

- **Requirement description:** Requirements shall track approval status independently from maturity using the authorized Stage 1 classifications.
- **Source / originating decision:** User-Stage1-Approval: Refinement A.
- **Category / owner:** Governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-A.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-06-001](#req-06-001)
- **Data availability assumptions:** None: requirements metadata.
- **Planned verification:** VER-06-010 - Inspect records with approved/Analyzed and open/Identified combinations.
- **Acceptance criteria:** Approval is Approved/Proposed/Open; maturity is Identified/Analyzed/Specified/Verified for readiness/Baselined; no maturity or approval transition is inferred from artifact creation.
- **Unresolved questions:** None identified for this obligation; later review may identify more.
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-06-011"></a>

### REQ-06-011 - Proposed requirements change-impact assessment

- **Requirement description:** A lightweight change-impact convention is proposed for decisions/requirements, data/analytics, interfaces, verification and phase/dependency effects.
- **Source / originating decision:** User-Stage1-Approval: Refinement B; proposed governance convention.
- **Category / owner:** Governance; REQ-06.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Proposed governance convention; adoption not implied; Governance review, not product implementation.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-06-001](#req-06-001), [REQ-06-009](#req-06-009)
- **Data availability assumptions:** None: impact assessment metadata.
- **Planned verification:** VER-06-011 - Review a hypothetical data-contract change using the proposed impact template.
- **Acceptance criteria:** The assessment identifies all five impact areas, unknowns, affected IDs and required approvals; it is labeled proposed and grants no authority to alter D-01 through D-16.
- **Unresolved questions:** [S1-Q-016](#s1-q-016)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-06-012"></a>

### REQ-06-012 - Phase 2 ML evaluation and governance readiness

- **Requirement description:** Phase 1 requirements should describe Phase 2 ML evaluation, leakage controls, model/version evidence, monitoring and approval needs without implementing ML.
- **Source / originating decision:** D-09; OPEN_QUESTIONS: 9; REQUIREMENTS_INDEX: REQ-06.
- **Category / owner:** ML governance; REQ-06.
- **Priority / proposed phase:** Should; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Proposed; Analyzed.
- **Dependencies:** [REQ-05-011](#req-05-011), [REQ-06-005](#req-06-005)
- **Data availability assumptions:** Future training/validation data and monitoring needs unverified.
- **Planned verification:** VER-06-012 - Review a Phase 2 evaluation-requirements checklist against deterministic baselines.
- **Acceptance criteria:** Targets and evidence needs are documented or linked to explicit open questions; no algorithm, acceptance threshold or ML implementation is silently selected.
- **Unresolved questions:** [S1-Q-015](#s1-q-015)
- **R1 change:** Unchanged; core obligation retained, applicability metadata added.

<a id="req-06-013"></a>

### REQ-06-013 - Simulation lifecycle and execution-policy verification

- **Requirement description:** Paper lifecycle, triggers, fills, costs, liquidity, reservation and scenario interactions shall have attributable verification evidence.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Simulation validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-033](#req-03-033), [REQ-03-021](#req-03-021)
- **Data availability assumptions:** Controlled observations and human-approved execution-policy cases required.
- **Planned verification:** VER-06-013 - Review normal, partial-fill, ambiguity, expiry and shared-capital cases.
- **Acceptance criteria:** Expected outcomes trace to approved policies and observations; unsupported execution assumptions are explicit and failing cases block affected paper readiness.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-005](#r1-q-005), [R1-Q-006](#r1-q-006), [R1-Q-007](#r1-q-007)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-014"></a>

### REQ-06-014 - Accounting and performance verification

- **Requirement description:** Cash, positions, P&L, returns and drawdown shall be independently verified within each applicable performance class.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Financial validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B paper accounting; R1-C full reporting.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-031](#req-03-031), [REQ-03-032](#req-03-032)
- **Data availability assumptions:** Controlled cost-basis, mark, cash-flow and adjustment cases; policies unresolved.
- **Planned verification:** VER-06-014 - Review independent reference calculations and reconciliation cases.
- **Acceptance criteria:** Accounting reconciles under approved conventions and performance classes remain distinct; no profitability or win-rate target is inferred.
- **Unresolved questions:** [R1-Q-008](#r1-q-008), [R1-Q-009](#r1-q-009), [R1-Q-015](#r1-q-015)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-015"></a>

### REQ-06-015 - Real-execution prevention and mode isolation

- **Requirement description:** R1 acceptance shall verify isolation of paper/manual state and absence of broker connectivity or real order execution.
- **Source / originating decision:** Human-R1-Approval; D-03.
- **Category / owner:** Boundary validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B; R1-C cumulative.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-05-013](#req-05-013), [REQ-04-003](#req-04-003)
- **Data availability assumptions:** Synthetic scenarios only; no real broker credentials required.
- **Planned verification:** VER-06-015 - Review prohibited operations and cross-mode references.
- **Acceptance criteria:** No UI/tool/automation path can connect a broker or place a real order; recording and simulation cannot masquerade as execution.
- **Unresolved questions:** [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-016"></a>

### REQ-06-016 - Manual provenance and correction verification

- **Requirement description:** Manual transaction records shall have verification cases for provenance disclosure, corrections, duplication and incomplete state.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Manual-record validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-034](#req-03-034), [REQ-03-035](#req-03-035), [REQ-05-014](#req-05-014)
- **Data availability assumptions:** DATA-008 fixtures are synthetic; actual truth is not verified by the application.
- **Planned verification:** VER-06-016 - Review duplicate, corrected, incomplete and late-reported events.
- **Acceptance criteria:** Tests verify application accounting/disclosures, not broker truth; incompleteness and corrections remain attributable and cannot silently improve reported performance.
- **Unresolved questions:** [R1-Q-009](#r1-q-009), [R1-Q-012](#r1-q-012)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-017"></a>

### REQ-06-017 - Cumulative R1 personal-use acceptance

- **Requirement description:** R1 acceptance shall cover Research Platform, Validated Trade Planning and Paper Trading, and Manual Trading Support and Personal-Use Readiness cumulatively.
- **Source / originating decision:** Human-R1-Approval.
- **Category / owner:** Release governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-C.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-06-004](#req-06-004), [REQ-06-005](#req-06-005), [REQ-06-013](#req-06-013), [REQ-06-014](#req-06-014), [REQ-06-015](#req-06-015), [REQ-06-016](#req-06-016), [REQ-06-019](#req-06-019)
- **Data availability assumptions:** Evidence must exist for all required capabilities; periods and thresholds remain open.
- **Planned verification:** VER-06-017 - Review the R1-A/B/C acceptance matrix and unresolved blockers.
- **Acceptance criteria:** Intermediate increments are not complete R1; recommendation lifecycle, separate evidence/performance, daily reassessment, privacy and restoration are covered without authorizing implementation/deployment.
- **Unresolved questions:** [S1-Q-016](#s1-q-016), [R1-Q-012](#r1-q-012), [R1-Q-014](#r1-q-014)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-018"></a>

### REQ-06-018 - Distinct validation evidence records

- **Requirement description:** Historical backtesting, walk-forward/out-of-sample testing and forward paper trading shall retain distinct evidence and performance records.
- **Source / originating decision:** Human-R1-Approval: Refinement B.
- **Category / owner:** Evidence governance; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-02-012](#req-02-012)
- **Data availability assumptions:** Historical versus newly arriving observations must be attributable.
- **Planned verification:** VER-06-018 - Inspect one record of each class and a historical replay mislabeled as forward.
- **Acceptance criteria:** Each record identifies method, as-of/observation context, data/strategy/policy versions, limitations and its period. No class substitutes silently for another; no performance result or period is invented.
- **Unresolved questions:** [R1-Q-002](#r1-q-002), [R1-Q-014](#r1-q-014)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

<a id="req-06-019"></a>

### REQ-06-019 - Forward paper evidence using arriving data

- **Requirement description:** R1-B shall collect separately attributable forward paper-trading evidence using newly arriving market data under the then-active recommendation, strategy and simulation-policy versions.
- **Source / originating decision:** Human-R1-Approval: Refinement A R1-B; Refinement B.
- **Category / owner:** Forward validation; REQ-06.
- **Priority / proposed phase:** Must; Phase 1.
- **R1 applicability / increment:** Required; R1-B.
- **Approval status / maturity:** Approved; Analyzed.
- **Dependencies:** [REQ-03-033](#req-03-033), [REQ-06-018](#req-06-018)
- **Data availability assumptions:** New arrivals and versions must be retained; minimum period/sample policy unresolved.
- **Planned verification:** VER-06-019 - Review arrival-time decisions, subsequent corrections and historical replays.
- **Acceptance criteria:** Forward outcomes preserve what was available when decided; corrections/replays retain lineage and do not manufacture additional forward observations. Human approval sets evidence sufficiency without assumed durations or targets.
- **Unresolved questions:** [R1-Q-004](#r1-q-004), [R1-Q-013](#r1-q-013), [R1-Q-014](#r1-q-014)
- **R1 change:** Added; Faithful approved R1 obligation; detailed policies remain open.

## 6. D-01 through D-16 coverage and impact

No approved decision is amended. Direct source-linked records follow; additional transitive traceability is retained through dependencies.

| Decision | Direct source-linked records |
| --- | --- |
| D-01 | [REQ-01-001](#req-01-001), [REQ-01-002](#req-01-002), [REQ-02-016](#req-02-016), [REQ-04-004](#req-04-004), [REQ-04-009](#req-04-009) |
| D-02 | [REQ-01-004](#req-01-004), [REQ-01-005](#req-01-005), [REQ-01-006](#req-01-006), [REQ-03-010](#req-03-010) |
| D-03 | [REQ-04-003](#req-04-003), [REQ-05-013](#req-05-013), [REQ-06-015](#req-06-015) |
| D-04 | [REQ-01-003](#req-01-003), [REQ-01-010](#req-01-010), [REQ-05-012](#req-05-012) |
| D-05 | [REQ-03-017](#req-03-017), [REQ-03-021](#req-03-021) |
| D-06 | [REQ-01-007](#req-01-007), [REQ-03-015](#req-03-015) |
| D-07 | [REQ-04-001](#req-04-001), [REQ-04-002](#req-04-002), [REQ-04-010](#req-04-010), [REQ-04-011](#req-04-011) |
| D-08 | [REQ-03-002](#req-03-002), [REQ-03-003](#req-03-003) |
| D-09 | [REQ-03-001](#req-03-001), [REQ-03-022](#req-03-022), [REQ-05-011](#req-05-011), [REQ-06-012](#req-06-012) |
| D-10 | [REQ-03-012](#req-03-012), [REQ-03-013](#req-03-013) |
| D-11 | [REQ-03-018](#req-03-018), [REQ-03-019](#req-03-019), [REQ-05-005](#req-05-005), [REQ-05-013](#req-05-013) |
| D-12 | [REQ-02-012](#req-02-012), [REQ-02-014](#req-02-014), [REQ-03-038](#req-03-038), [REQ-06-003](#req-06-003) |
| D-13 | [REQ-04-011](#req-04-011), [REQ-05-007](#req-05-007) |
| D-14 | [REQ-02-008](#req-02-008), [REQ-02-009](#req-02-009), [REQ-02-010](#req-02-010), [REQ-02-015](#req-02-015), [REQ-02-016](#req-02-016) |
| D-15 | [REQ-01-007](#req-01-007), [REQ-03-015](#req-03-015) |
| D-16 | [REQ-04-010](#req-04-010), [REQ-04-011](#req-04-011), [REQ-05-006](#req-05-006), [REQ-05-007](#req-05-007) |

| Decision | R1 impact without amendment |
| --- | --- |
| D-01 | Gold/silver focus and contextual research retained. |
| D-02 | All three independent horizons retained in R1. |
| D-03 | No broker connection or real order execution; paper simulation and reported actual records are distinct. |
| D-04 | Initial Indian ETF investment scope; futures intelligence does not imply futures investment. |
| D-05 | Up-to-three justified scenarios/no-trade retained; paper interactions require policy. |
| D-06 | Hypothetical reference and user-reported actual state explicitly separated. |
| D-07 | Dashboard/chat/daily reporting extended to R1 portfolio context. |
| D-08 | Separate model outputs and reconciliation retained. |
| D-09 | Deterministic Phase 1; Phase 2 ML implementation; Phase 1 future-ML documentation retained. |
| D-10 | Confidence dimensions remain separate from performance classes. |
| D-11 | Canonical plan/up-to-two verified renderings retained; rendering is not execution. |
| D-12 | Point-in-time replay retained; reproduction is not new forward evidence. |
| D-13 | Actual-position reassessment remains advisory; paper triggers cannot affect actual orders. |
| D-14 | Provider independence retained; new execution evidence needs no assumed licensing. |
| D-15 | ₹20 lakh hypothetical configurable reference retained; actual balances never inferred. |
| D-16 | EOD initially retained; no intraday simulation fidelity assumed. |

<a id="data-register"></a>

## 7. Data availability and input provenance

No provider licenses, exports, market samples, model results or actual transactions were inspected or fabricated for this update. Dataset availability is not established by requirement approval.

| ID | Dataset family | Availability/limitation | Consumers |
| --- | --- | --- | --- |
| <a id="data-001"></a>DATA-001 | COMEX/MCX futures, contracts, OI/volume and curves | Coverage, historical depth, permission, metadata and timestamps unverified; exchanges/providers not selected. | REQ-02-001, REQ-02-002; REQ-03-005 |
| <a id="data-002"></a>DATA-002 | COMEX options chains, snapshots, IV and Greeks | May require licensed access; no complete historical chain, field derivation or usage rights verified. | REQ-02-003; REQ-03-006 |
| <a id="data-003"></a>DATA-003 | USD/INR, DXY, policy/implied rates, yields and macro releases | Source suitability, implied-rate history, publication times and vintage coverage unverified. | REQ-02-004, REQ-02-005; REQ-03-004 |
| <a id="data-004"></a>DATA-004 | COT, oil/copper, physical-market and inventory context | Series selection, release lag, availability, rights and historical coverage unverified. | REQ-02-006; contextual research |
| <a id="data-005"></a>DATA-005 | Indian ETF market/fund data, bars/quotes, NAV, flows, costs, adjustments and marks | Instrument set, granularity, executable liquidity, quotes/marks, flows, costs, corporate actions and rights unverified; no intraday ordering inferred from EOD bars. | REQ-02-007; REQ-03-009; sizing/backtests |
| <a id="data-006"></a>DATA-006 | User Dhan historical exports | D-14 records user availability; no sample inspected. Fields, dates, OI/expiry/timestamps and permissions unresolved. | REQ-02-009; MCX/ETF history only if supported by samples |
| <a id="data-007"></a>DATA-007 | Candidate Yahoo US fallback series | Candidate only under D-14; retrieval rights, adjustments, reproducibility and suitability unverified; complete COMEX options not presumed. | REQ-02-010; only individually validated fallback uses |
| <a id="data-008"></a>DATA-008 | User-reported actual orders/fills, opening holdings/cash and external cash flows | Manual source only; truth/completeness/cost basis unverified; no broker connection or automatic verification. | REQ-02-018; REQ-03-034/035; manual performance/risk. |

Simulation/strategy policies are versioned user-approved configuration, not licensed market data. Historical source observations, arriving forward observations, user reports and generated interpretations remain distinguishable. Required data absence blocks its dependent capability unless a human approves an appropriate alternative; it does not authorize invented fills or marks.

<a id="question-register"></a>

## 8. Open questions and release blockers

The approved R1 scope answers the broad personal-use workflow question. Exact coverage, policy and acceptance criteria remain open. Existing S1-Q identifiers are preserved; R1-Q identifiers refine or extend them. Question records are not included in requirement counts.

### 8.1 Blocking summary by acceptance increment

| Gate | Blocking decisions/evidence |
| --- | --- |
| R1-A | ETF/minimum evidence coverage; permissions/inspected source coverage; data quality/as-of rules; permitted AI tools/data flows; daily report cutoff. S1-Q-001 through 005, S1-Q-012/014; R1-Q-001/011 and applicable privacy decisions. |
| R1-B | Independent strategy/reconciliation/risk rules; recommendation validation/publication policy; fill/cost/liquidity/capital/expiry policies; historical/OOS sufficiency and forward-paper evidence criteria. S1-Q-006 through 009; R1-Q-002 through 008, 013/014. |
| R1-C | Manual opening state, corrections and accounting; separate performance/benchmarks; daily position/recommendation reassessment; access/privacy/recovery and cumulative sign-off. R1-Q-008/009/011/012/015; S1-Q-011/016. |
| Conditional features | Broker capability evidence blocks a selected rendering, not broker-neutral instructions. Advanced chains or intraday/event coverage block those selected features or claims. R1-Q-010 and relevant data/alert questions. |
| Outside current core acceptance | Frontend selection remains a later design decision, not permission to author/build. Future instrument/ML details do not authorize implementation; Phase 1 extension/documentation requirements still apply. S1-Q-013/015/017. |

No evidence sufficiency, forward observation duration, profitability, win-rate, expiry duration, fill parameter or risk threshold is supplied by this package. Required R1-B forward evidence cannot be claimed collected before newly arriving observations actually exist.

### 8.2 Preserved Stage 1 questions

<a id="s1-q-001"></a>

### S1-Q-001 - Users, success measures, ETF universe and first-release scope

- **Classification / affected acceptance:** Release baseline.
- **Affected requirements / capabilities:** REQ-01-003, REQ-01-008, REQ-01-009; all phase proposals.
- **Decision or evidence needed:** Which specific ETFs, measurable outcomes, minimum datasets and detailed acceptance criteria implement the now-approved R1 workflow?
- **Original source:** REQUIREMENTS_INDEX REQ-01; OPEN_QUESTIONS 11.
- **Candidate reviewers:** Product owner (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Partially answered: personal-use workflow and mandatory R1 capabilities are approved. Remaining ETF universe, measurable outcomes and detailed acceptance are R1-Q-001/014; this is not reopened broad scope.

<a id="s1-q-002"></a>

### S1-Q-002 - Permissions, source budget and permitted retrieval

- **Classification / affected acceptance:** Dataset-dependent release capability.
- **Affected requirements / capabilities:** REQ-02-008, REQ-02-016, REQ-04-004.
- **Decision or evidence needed:** Which documented rights, usage contexts and acquisition budget permit each source and automated use?
- **Original source:** OPEN_QUESTIONS 4; D-14.
- **Candidate reviewers:** Data owner + human approver (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-003"></a>

### S1-Q-003 - Inspected data coverage and Dhan export suitability

- **Classification / affected acceptance:** Dataset-dependent release capability.
- **Affected requirements / capabilities:** REQ-02-001 through REQ-02-011; dependent models.
- **Decision or evidence needed:** What fields, history, metadata, quotes and timestamps actually exist in representative exports/provider evidence?
- **Original source:** OPEN_QUESTIONS 3; D-14.
- **Candidate reviewers:** Data owner (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-004"></a>

### S1-Q-004 - Point-in-time history, market calendars and roll conventions

- **Classification / affected acceptance:** Replay and time-aligned release analytics.
- **Affected requirements / capabilities:** REQ-02-012, REQ-02-014, REQ-06-003, REQ-06-004.
- **Decision or evidence needed:** What history, vintage evidence, availability times, session conventions, retention and roll treatment are required and obtainable?
- **Original source:** OPEN_QUESTIONS 8; D-12.
- **Candidate reviewers:** Data + quantitative owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-005"></a>

### S1-Q-005 - Quality gates and incomplete-evidence behavior

- **Classification / affected acceptance:** Evidence-dependent release outputs.
- **Affected requirements / capabilities:** REQ-02-013, REQ-03-012, REQ-04-010, REQ-04-011.
- **Decision or evidence needed:** When do absent, stale or inconsistent inputs degrade a result, withhold a plan, or prevent a report/alert?
- **Original source:** OPEN_QUESTIONS 4.
- **Candidate reviewers:** Data + product owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-006"></a>

### S1-Q-006 - Strategy rules and model reconciliation

- **Classification / affected acceptance:** Actionable strategy release capability.
- **Affected requirements / capabilities:** REQ-03-003 through REQ-03-011; REQ-06-004.
- **Decision or evidence needed:** Which indicators, model rules, weights, entry/exit logic, benchmarks and horizon conventions are approved for evaluation?
- **Original source:** OPEN_QUESTIONS 6; D-02; D-08.
- **Candidate reviewers:** Quantitative owner + human risk approver (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-007"></a>

### S1-Q-007 - Allocation, risk, shared capital and portfolio state

- **Classification / affected acceptance:** Sizing and portfolio release capability.
- **Affected requirements / capabilities:** REQ-03-015, REQ-03-016, REQ-03-020, REQ-03-021.
- **Decision or evidence needed:** How are gold/silver/cash and horizons allocated; what limits, sizing, ownership, manual-state and scenario-capital rules apply?
- **Original source:** OPEN_QUESTIONS 1; D-06; D-15.
- **Candidate reviewers:** Human portfolio/risk approver (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Reference capital is ₹20 lakh hypothetical/configurable, not actual. Allocations/risk/manual-state choices remain R1-Q-003/007/009.

<a id="s1-q-008"></a>

### S1-Q-008 - Execution-cost and ETF adjustment assumptions

- **Classification / affected acceptance:** Trade sizing and backtest release claims.
- **Affected requirements / capabilities:** REQ-03-009, REQ-03-014, REQ-06-004.
- **Decision or evidence needed:** Which fees, spread/slippage conventions, rounding, adjustments and execution timings are evidenced or sensitivity assumptions?
- **Original source:** REQUIREMENTS_INDEX REQ-03/REQ-06; DISCUSSION_SUMMARY Confidence.
- **Candidate reviewers:** Quantitative/risk owner (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Costs and execution conventions also govern paper accounting; see R1-Q-006/008.

<a id="s1-q-009"></a>

### S1-Q-009 - Confidence meanings and validation sufficiency

- **Classification / affected acceptance:** Confidence and predictive-performance release claims.
- **Affected requirements / capabilities:** REQ-03-013, REQ-06-005, REQ-06-006.
- **Decision or evidence needed:** What scales, minimum evidence, tolerances, benchmarks and acceptance criteria make claims supportable?
- **Original source:** D-10; REQUIREMENTS_INDEX REQ-06.
- **Candidate reviewers:** Validation + quantitative owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Keep historical, OOS and forward evidence distinct; no performance targets or periods assumed. See R1-Q-014/015.

<a id="s1-q-010"></a>

### S1-Q-010 - Broker evidence and trade-plan lifecycle

- **Classification / affected acceptance:** Broker-specific rendering release capability; canonical lifecycle where affected.
- **Affected requirements / capabilities:** REQ-03-018 through REQ-03-021; REQ-05-005.
- **Decision or evidence needed:** Which zero-to-two broker renderings are needed, what semantics are verified, and how do plans expire/change without account connectivity?
- **Original source:** OPEN_QUESTIONS 2 and 12; D-11.
- **Candidate reviewers:** Product + broker-domain reviewer (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Canonical structure is already approved; zero-to-two selected verified renderings are conditional, while broker-neutral instructions are required. No broker connectivity.

<a id="s1-q-011"></a>

### S1-Q-011 - Deployment, access, secrets, privacy and retention

- **Classification / affected acceptance:** Operational release baseline.
- **Affected requirements / capabilities:** REQ-04-008, REQ-05-004, REQ-05-009, REQ-06-008.
- **Decision or evidence needed:** Who can access the system, where does it run, what may reach external AI services, and what security/retention/recovery policy applies?
- **Original source:** OPEN_QUESTIONS 10.
- **Candidate reviewers:** Human owner + security reviewer (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Manual actual records add privacy/recovery needs; see R1-Q-012.

<a id="s1-q-012"></a>

### S1-Q-012 - Assistant tool permissions and research behavior

- **Classification / affected acceptance:** Conversational/proactive release capability.
- **Affected requirements / capabilities:** REQ-04-002 through REQ-04-009; REQ-04-012; REQ-06-007.
- **Decision or evidence needed:** Which tools/actions/context policies are permitted, and how should unsupported requests or untrusted retrieved instructions be handled?
- **Original source:** OPEN_QUESTIONS 4 and 10; REQUIREMENTS_INDEX REQ-04.
- **Candidate reviewers:** AI product + security owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-013"></a>

### S1-Q-013 - Frontend and shared interaction requirements

- **Classification / affected acceptance:** Nonblocking for Stage 1 and product/data requirements; conditional later design dependency.
- **Affected requirements / capabilities:** REQ-04-001, REQ-04-013, REQ-05-002.
- **Decision or evidence needed:** Which dashboard/chat interaction needs and constraints should guide the later Streamlit-versus-React decision?
- **Original source:** OPEN_QUESTIONS 5; DECISION_REGISTER pending frontend.
- **Candidate reviewers:** Product + architecture reviewer (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-014"></a>

### S1-Q-014 - EOD cutoff and event/alert policy

- **Classification / affected acceptance:** EOD release reports; events only if included in the release.
- **Affected requirements / capabilities:** REQ-04-010, REQ-04-011, REQ-05-006, REQ-05-007.
- **Decision or evidence needed:** What cutoff, delivery schedule, channels, thresholds, quiet hours, deduplication and escalation rules apply?
- **Original source:** OPEN_QUESTIONS 7; D-13; D-16.
- **Candidate reviewers:** Product + operations owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Daily intelligence in R1-A and position/recommendation reassessment in R1-C; events remain reliable-data conditional. See R1-Q-011.

<a id="s1-q-015"></a>

### S1-Q-015 - Phase 2 ML targets and governance detail

- **Classification / affected acceptance:** Nonblocking for Stage 1; blocks complete Phase 1 ML-readiness acceptance and later ML capability where unresolved.
- **Affected requirements / capabilities:** REQ-03-022, REQ-05-011, REQ-06-012.
- **Decision or evidence needed:** Which targets, labels, data/evaluation needs and monitoring controls must Phase 1 document, and which details may be explicitly deferred by approval?
- **Original source:** OPEN_QUESTIONS 9; D-09.
- **Candidate reviewers:** Quantitative/ML + validation owners (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

<a id="s1-q-016"></a>

### S1-Q-016 - Approval authority, release gates and measurable NFRs

- **Classification / affected acceptance:** Requirements/release approval baseline.
- **Affected requirements / capabilities:** REQ-05-008 through REQ-05-010; REQ-06-006 through REQ-06-011.
- **Decision or evidence needed:** Who approves requirements and release evidence, what service/recovery targets apply, and will the proposed change-impact convention be adopted?
- **Original source:** OPEN_QUESTIONS 10 and 11; User-Stage1 Refinement B.
- **Candidate reviewers:** Human owner + governance reviewer (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** This documentation approval does not approve deployment, name all review roles or adopt the Proposed change-impact convention.

<a id="s1-q-017"></a>

### S1-Q-017 - Future instrument-specific scope

- **Classification / affected acceptance:** Nonblocking for initial Indian ETF scope; extension-acceptance dependency where applicable.
- **Affected requirements / capabilities:** REQ-01-010, REQ-05-012.
- **Decision or evidence needed:** What future instrument differences must be anticipated without selecting providers, broker access or execution capabilities now?
- **Original source:** D-04; DECISION_REGISTER pending details.
- **Candidate reviewers:** Product + architecture reviewers (proposed).
- **Status:** Open; no due date or answer assumed.

**R1 update:** Scope/refinements do not settle this policy/evidence question. Use the linked R1 questions where applicable; no answer or due date is assumed.

### 8.3 R1 refinement questions

R1-Q-001 through R1-Q-012 preserve the reviewed proposal's open topics. R1-Q-013 through R1-Q-015 identify decisions required by the four human refinements; they do not introduce product scope beyond those refinements. All remain Open.

<a id="r1-q-001"></a>

### R1-Q-001 - ETF universe and minimum evidence coverage

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-A coverage.
- **Decision/evidence needed:** Which Indian ETFs and minimum COMEX/MCX, macro and ETF datasets qualify the required R1 intelligence and accepted strategies?
- **Related Stage 1 questions:** S1-Q-001, S1-Q-002, S1-Q-003.
- **Principal records:** REQ-01-008, REQ-02-007.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-002"></a>

### R1-Q-002 - Strategy and historical evaluation criteria

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B actionable recommendations.
- **Decision/evidence needed:** Which independent rules, benchmarks, historical partitions and acceptance criteria apply to swing, tactical and strategic strategies?
- **Related Stage 1 questions:** S1-Q-006, S1-Q-009.
- **Principal records:** REQ-03-011, REQ-06-004, REQ-06-005.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-003"></a>

### R1-Q-003 - Portfolio and financing policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B risk/sizing/paper capital; R1-C manual risk.
- **Decision/evidence needed:** What allocations, limits, rounding, permitted positions/financing and horizon-attribution rules apply?
- **Related Stage 1 questions:** S1-Q-007.
- **Principal records:** REQ-03-015, REQ-03-016, REQ-03-023, REQ-03-030.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-004"></a>

### R1-Q-004 - Paper observation basis

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B simulation and forward evidence.
- **Decision/evidence needed:** Are paper triggers/fills based on EOD bars, intraday observations, quotes or another evidenced basis, and when is evidence eligible?
- **Related Stage 1 questions:** S1-Q-003, S1-Q-004, S1-Q-005.
- **Principal records:** REQ-02-017, REQ-03-025, REQ-06-019.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-005"></a>

### R1-Q-005 - Gaps activation and ambiguous event order

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B fill validity.
- **Decision/evidence needed:** How are gaps, same-bar touches, entry/exit activation and trigger/cancellation ordering handled when observations cannot establish the sequence?
- **Related Stage 1 questions:** S1-Q-010.
- **Principal records:** REQ-03-025, REQ-03-026, REQ-03-029.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-006"></a>

### R1-Q-006 - Execution cost liquidity and partial-fill policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B paper/backtest accounting.
- **Decision/evidence needed:** What fees, slippage, liquidity and partial-fill assumptions are approved and supported by available observations?
- **Related Stage 1 questions:** S1-Q-008.
- **Principal records:** REQ-03-027, REQ-03-028, REQ-06-004.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-007"></a>

### R1-Q-007 - Scenario reservation cancellation and expiry

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B concurrent orders and risk.
- **Decision/evidence needed:** How do alternatives reserve/release capital, interact, cancel and expire, including partial fills and simultaneous triggers?
- **Related Stage 1 questions:** S1-Q-007, S1-Q-010.
- **Principal records:** REQ-03-021, REQ-03-029, REQ-03-030.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-008"></a>

### R1-Q-008 - Accounting valuation and cash-flow conventions

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B paper accounting; R1-C performance.
- **Decision/evidence needed:** What cost-basis, marking, charges, corporate-action, return and drawdown conventions apply to each portfolio/evidence class?
- **Related Stage 1 questions:** S1-Q-008, S1-Q-009.
- **Principal records:** REQ-03-031, REQ-03-032, REQ-03-035.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-009"></a>

### R1-Q-009 - Actual opening state and reported-record policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-C manual portfolio readiness.
- **Decision/evidence needed:** How are opening holdings/cash, partial or late reports, corrections, duplicates, cash flows and missing cost basis handled without claiming verification?
- **Related Stage 1 questions:** S1-Q-007, S1-Q-011.
- **Principal records:** REQ-02-018, REQ-03-034, REQ-03-035, REQ-06-016.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-010"></a>

### R1-Q-010 - Selected broker renderings and evidence

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** Conditional R1-C broker rendering; not generic instructions.
- **Decision/evidence needed:** Which, if any, broker-specific renderings are selected and what dated evidence establishes their trigger/order/protective-exit semantics?
- **Related Stage 1 questions:** S1-Q-010.
- **Principal records:** REQ-03-019, REQ-03-037, REQ-05-005.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-011"></a>

### R1-Q-011 - Daily cutoff and reassessment policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-A reports; R1-C position/recommendation reassessment.
- **Decision/evidence needed:** What information cutoff, schedule, channels and stale-data/reassessment rules apply across US and Indian sessions?
- **Related Stage 1 questions:** S1-Q-004, S1-Q-005, S1-Q-014.
- **Principal records:** REQ-04-010, REQ-05-006, REQ-03-036.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-012"></a>

### R1-Q-012 - Personal information and recovery policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-C personal-use readiness; relevant earlier security gates.
- **Decision/evidence needed:** What access/deployment, external-AI sharing, retention, backup and restoration policies protect research and manual transaction data?
- **Related Stage 1 questions:** S1-Q-011, S1-Q-016.
- **Principal records:** REQ-05-004, REQ-05-009, REQ-05-014, REQ-06-008.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-013"></a>

### R1-Q-013 - Recommendation state transition policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B publication; R1-C reassessment.
- **Decision/evidence needed:** Which checks and authority establish Validated and Published, what validity/expiry/withdrawal conditions apply, and how are further transitions or renewed recommendations handled?
- **Related Stage 1 questions:** S1-Q-006, S1-Q-010, S1-Q-012.
- **Principal records:** REQ-03-038, REQ-03-036, REQ-04-008.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-014"></a>

### R1-Q-014 - Evidence sufficiency and forward collection policy

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-B validation/forward evidence; cumulative R1 acceptance.
- **Decision/evidence needed:** What history, sample adequacy, forward observation period, corrections and pass/fail evidence are sufficient for each horizon and increment? No durations or performance targets are assumed.
- **Related Stage 1 questions:** S1-Q-004, S1-Q-009, S1-Q-016.
- **Principal records:** REQ-06-006, REQ-06-017, REQ-06-018, REQ-06-019.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

<a id="r1-q-015"></a>

### R1-Q-015 - Separated performance and benchmark methodology

- **Status:** Open; no value, answer, owner assignment or due date inferred.
- **Affected acceptance:** R1-C performance comparisons; earlier claims where used.
- **Decision/evidence needed:** Which benchmarks, periods, cash-flow/cost conventions and comparison methods apply while keeping historical, forward paper, manual actual and benchmark records separate?
- **Related Stage 1 questions:** S1-Q-009.
- **Principal records:** REQ-03-032, REQ-03-039, REQ-06-014.
- **Source:** Human-R1-Approval and retained Stage 1 open questions.

## 9. R1 acceptance scenarios

These are reviewable future acceptance cases, not executed tests, populated evidence or authorization to build. Their policy-dependent details remain blocked by section 8. R1-AC identifiers are scenario identifiers, not additional requirement records.

| Scenario | Increment | Purpose | Expected observable outcome | Requirement trace |
| --- | --- | --- | --- | --- |
| <a id="r1-ac-01"></a>R1-AC-01 | R1-A | Research provenance | Gold/silver and ETF research identifies sources, timestamps, separate model outputs and all confidence dimensions. | [REQ-01-001](#req-01-001), [REQ-02-007](#req-02-007), [REQ-03-002](#req-03-002), [REQ-03-012](#req-03-012), [REQ-04-006](#req-04-006) |
| <a id="r1-ac-02"></a>R1-AC-02 | R1-A/B | Independent horizons | All three approved horizons have distinct assessments and separately defined rules; risk aggregates within the selected portfolio. | [REQ-01-004](#req-01-004), [REQ-01-005](#req-01-005), [REQ-01-006](#req-01-006), [REQ-03-010](#req-03-010), [REQ-03-016](#req-03-016) |
| <a id="r1-ac-03"></a>R1-AC-03 | R1-B | Validated trade plan | Eligible evidence and approved strategy/risk rules support reproducible plan fields and zero-to-three justified alternatives. | [REQ-03-014](#req-03-014), [REQ-03-017](#req-03-017), [REQ-03-018](#req-03-018), [REQ-03-038](#req-03-038) |
| <a id="r1-ac-04"></a>R1-AC-04 | R1-A/B | Insufficient evidence | Missing/stale inputs produce approved degraded/withheld behavior without invented recommendations, fills or probability. | [REQ-02-013](#req-02-013), [REQ-04-006](#req-04-006), [REQ-03-026](#req-03-026) |
| <a id="r1-ac-05"></a>R1-AC-05 | R1-B | Paper lifecycle | Eligible simulated transitions/fills update virtual quantities and balances under approved policies only. | [REQ-03-023](#req-03-023), [REQ-03-024](#req-03-024), [REQ-03-025](#req-03-025), [REQ-03-028](#req-03-028), [REQ-03-029](#req-03-029) |
| <a id="r1-ac-06"></a>R1-AC-06 | R1-B | Ambiguous observation | Entry/stop/target within one bar is handled by the approved ambiguity policy or remains unresolved; no favorable sequence is presumed. | [REQ-02-017](#req-02-017), [REQ-03-026](#req-03-026) |
| <a id="r1-ac-07"></a>R1-AC-07 | R1-B | Shared capital | Alternative scenarios and concurrent horizons obey approved reservation/cancellation rules, including partial fills. | [REQ-03-021](#req-03-021), [REQ-03-030](#req-03-030) |
| <a id="r1-ac-08"></a>R1-AC-08 | R1-B/C | Independent accounting | Cash/positions/charges/marks/P&L reconcile to independent references within each applicable class. | [REQ-03-027](#req-03-027), [REQ-03-031](#req-03-031), [REQ-06-014](#req-06-014) |
| <a id="r1-ac-09"></a>R1-AC-09 | R1-B | Historical evidence distinction | Backtest and OOS/walk-forward records disclose partitions, versions, costs and limitations separately. | [REQ-06-004](#req-06-004), [REQ-06-005](#req-06-005), [REQ-06-018](#req-06-018) |
| <a id="r1-ac-10"></a>R1-AC-10 | R1-B | Forward paper evidence | New arrivals produce attributable forward decisions/outcomes; historical replay/corrections do not manufacture forward samples. | [REQ-03-033](#req-03-033), [REQ-06-018](#req-06-018), [REQ-06-019](#req-06-019) |
| <a id="r1-ac-11"></a>R1-AC-11 | R1-C | Broker-neutral instructions | A plan yields human-readable placement/monitoring instructions without broker selection or real submission. | [REQ-03-037](#req-03-037), [REQ-03-018](#req-03-018) |
| <a id="r1-ac-12"></a>R1-AC-12 | R1-C | Manual actual records | User reports, corrections and opening state affect only the manual portfolio and remain explicitly not broker-verified. | [REQ-02-018](#req-02-018), [REQ-03-034](#req-03-034), [REQ-03-035](#req-03-035), [REQ-04-015](#req-04-015), [REQ-06-016](#req-06-016) |
| <a id="r1-ac-13"></a>R1-AC-13 | R1-C | Separated performance | Historical, forward paper, manual actual and benchmark comparisons retain class/method/period labels without misleading combined results. | [REQ-03-032](#req-03-032), [REQ-03-039](#req-03-039), [REQ-06-014](#req-06-014) |
| <a id="r1-ac-14"></a>R1-AC-14 | R1-C | Daily reassessment | Eligible daily evidence reassesses positions and recommendation validity/version without changing actual orders or rewriting old publications. | [REQ-03-036](#req-03-036), [REQ-03-038](#req-03-038), [REQ-04-010](#req-04-010) |
| <a id="r1-ac-15"></a>R1-AC-15 | R1-C | Privacy and restore | Approved restoration/privacy cases preserve attributable separate portfolio histories and protect personal information. | [REQ-05-004](#req-05-004), [REQ-05-009](#req-05-009), [REQ-05-014](#req-05-014), [REQ-06-008](#req-06-008) |
| <a id="r1-ac-16"></a>R1-AC-16 | All increments | No real execution | UI/tool/paper/manual operations cannot connect brokers or place real orders. | [REQ-04-003](#req-04-003), [REQ-05-013](#req-05-013), [REQ-06-015](#req-06-015) |
| <a id="r1-ac-17"></a>R1-AC-17 | R1-B/C | Recommendation lifecycle | Draft -> Validated -> Published -> Superseded / Expired / Withdrawn retains evidence times, conditions, strategy/risk checks and reassessment lineage; no expiry duration is invented. | [REQ-03-038](#req-03-038), [REQ-04-008](#req-04-008) |
| <a id="r1-ac-18"></a>R1-AC-18 | R1-C cumulative | Personal-use acceptance | All required increments and horizon-specific validation/evidence gates meet human-approved criteria; no invented period, profit or win-rate target. | [REQ-01-009](#req-01-009), [REQ-06-006](#req-06-006), [REQ-06-017](#req-06-017) |

<a id="change-log"></a>

## 10. R1 change-impact and stable-ID log

### 10.1 Added records

32 additions; all faithfully record Human-R1-Approval scope/refinements as Approved/Analyzed, not completed specifications or implementation authorization. Acceptance operationalization and unanswered policy still need review.

| Document | Added IDs |
| --- | --- |
| REQ-01 | [REQ-01-011](#req-01-011), [REQ-01-012](#req-01-012) |
| REQ-02 | [REQ-02-017](#req-02-017), [REQ-02-018](#req-02-018) |
| REQ-03 | [REQ-03-023](#req-03-023), [REQ-03-024](#req-03-024), [REQ-03-025](#req-03-025), [REQ-03-026](#req-03-026), [REQ-03-027](#req-03-027), [REQ-03-028](#req-03-028), [REQ-03-029](#req-03-029), [REQ-03-030](#req-03-030), [REQ-03-031](#req-03-031), [REQ-03-032](#req-03-032), [REQ-03-033](#req-03-033), [REQ-03-034](#req-03-034), [REQ-03-035](#req-03-035), [REQ-03-036](#req-03-036), [REQ-03-037](#req-03-037), [REQ-03-038](#req-03-038), [REQ-03-039](#req-03-039) |
| REQ-04 | [REQ-04-014](#req-04-014), [REQ-04-015](#req-04-015) |
| REQ-05 | [REQ-05-013](#req-05-013), [REQ-05-014](#req-05-014) |
| REQ-06 | [REQ-06-013](#req-06-013), [REQ-06-014](#req-06-014), [REQ-06-015](#req-06-015), [REQ-06-016](#req-06-016), [REQ-06-017](#req-06-017), [REQ-06-018](#req-06-018), [REQ-06-019](#req-06-019) |

### 10.2 Existing content revisions

33 existing records have scope, source, status, wording, acceptance, dependency or question changes below. All 85 original records receive R1 applicability/increment metadata; that metadata does not rename, delete or reuse an ID. Records outside this table retain their core obligation/status/priority.

| ID | Rationale |
| --- | --- |
| [REQ-01-008](#req-01-008) | Record personal-use direction; detailed product acceptance remains open. |
| [REQ-01-009](#req-01-009) | Replace open broad release intent with approved R1 scope; retain detailed acceptance questions. |
| [REQ-02-007](#req-02-007) | Extend ETF scope to paper/manual valuation; availability remains unverified. |
| [REQ-02-011](#req-02-011) | Extend semantic contracts; field-level choices remain Proposed. |
| [REQ-02-012](#req-02-012) | Extend temporal provenance to manual and forward evidence. |
| [REQ-02-013](#req-02-013) | Extend quality questions without selecting thresholds or fallback marks. |
| [REQ-02-014](#req-02-014) | Separate historical coverage from forward observation evidence. |
| [REQ-03-014](#req-03-014) | Apply approved R1 scope and versioned recommendation linkage. |
| [REQ-03-015](#req-03-015) | Keep financial policy Open and separate reference from actual state. |
| [REQ-03-016](#req-03-016) | Apply approved portfolio-level risk and mode separation. |
| [REQ-03-018](#req-03-018) | Preserve D-11 while distinguishing execution artifacts. |
| [REQ-03-019](#req-03-019) | Keep rendering scope conditional, without broker connectivity. |
| [REQ-03-020](#req-03-020) | Separate existing plan-policy questions from new state/accounting records. |
| [REQ-03-021](#req-03-021) | Apply approved scenario interactions; exact rules remain open. |
| [REQ-04-001](#req-04-001) | Extend dashboard to usable R1 workflows. |
| [REQ-04-002](#req-04-002) | Extend conversation to approved R1 context. |
| [REQ-04-003](#req-04-003) | Clarify real versus simulated operations without relaxing D-03. |
| [REQ-04-005](#req-04-005) | Apply interpretation and performance separation. |
| [REQ-04-008](#req-04-008) | Promote essential retained evidence, not unlimited conversation storage. |
| [REQ-04-009](#req-04-009) | Promote missing-user-input behavior required for valid plans. |
| [REQ-04-010](#req-04-010) | Daily intelligence in R1-A; cumulative position reassessment in R1-C. |
| [REQ-05-002](#req-05-002) | Extend interface semantics without implementation choices. |
| [REQ-05-004](#req-05-004) | Add personal-transaction privacy scope without choosing deployment. |
| [REQ-05-005](#req-05-005) | Separate broker documentation from live connectivity. |
| [REQ-05-009](#req-05-009) | Extend recovery scope to personal portfolio state. |
| [REQ-05-010](#req-05-010) | Extend provenance rather than duplicate audit contracts. |
| [REQ-06-003](#req-06-003) | Separate historical replay from forward evidence. |
| [REQ-06-004](#req-06-004) | Explicit historical-validation scope; no cost parameters invented. |
| [REQ-06-005](#req-06-005) | Implement approved evidence distinction. |
| [REQ-06-006](#req-06-006) | Keep thresholds and periods Open. |
| [REQ-06-007](#req-06-007) | Extend assistant evaluation to R1 lifecycle and separation. |
| [REQ-06-008](#req-06-008) | Extend security and recovery verification. |
| [REQ-06-009](#req-06-009) | Preserve governance boundaries. |

### 10.3 Approval and priority reconciliation

| ID | Approval before | Approval after | Source |
| --- | --- | --- | --- |
| [REQ-01-009](#req-01-009) | Open | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-02-007](#req-02-007) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-03-014](#req-03-014) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-03-016](#req-03-016) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-03-021](#req-03-021) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-04-005](#req-04-005) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-04-008](#req-04-008) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-06-004](#req-06-004) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |
| [REQ-06-005](#req-06-005) | Proposed | Approved | Explicit Human-R1-Approval obligation; unselected detailed policy is not thereby approved. |

- REQ-04-008: Should -> Must, limited to retained research/recommendation evidence needed for R1 audit.
- REQ-04-009: Should -> Must for targeted missing-user-input behavior.
- All other original priority labels stay unchanged. Starting 66/18/1 -> 68/16/1 after promotions -> 100/16/1 after 32 additions.
- Original record count remains 85; no ID removed. Final 117. Requirement maturity stays independent; 100 Analyzed, 17 Identified, no higher maturity assigned.
- Phase 1 deterministic analytics, Phase 2 ML implementation, and future instrument boundaries remain unchanged. R1-A/B/C is an additional acceptance attribute.

### 10.4 Impact domains

| Domain | Assessed impact |
| --- | --- |
| Decisions and requirements | D-01 through D-16 unchanged; Human-R1-Approval supplies R1 obligations. Additions/revisions/source authority above preserve stable IDs. |
| Data and analytical dependencies | Extend DATA-005 to paper trigger/fill/mark suitability; add DATA-008 user reports. Historical/OOS/forward evidence, accounting and strategy inputs retain provenance/versions and unresolved policy. |
| Architecture and interfaces | Logical mode boundaries and persistent histories only; no service decomposition/framework, broker adapter, live credentials or real execution path selected. |
| Verification and acceptance | 18 scenarios plus VER references; add lifecycle, accounting, forward evidence, performance separation and cumulative privacy/recovery checks. No test result is asserted. |
| Delivery phases and later dependencies | Paper trading/forward evidence in R1-B; manual support/performance readiness in R1-C. No implementation sequence or deployment plan; future connectivity remains assessment-only. |

This impact assessment uses the proposed convention as a review structure. It does not adopt REQ-06-011 or amend approved decisions.

## 11. Approval still needed

- The 32 added obligations are sourced to approved R1 intent/refinements; no newly invented product scope or unapproved autonomous execution requirement is added.
- Detailed financial/risk/fill/expiry/accounting/benchmark/retention/evidence policies remain Open. No approval, threshold, period or strategy selection is inferred from documentation authorization.
- The 26 remaining Proposed records retain that status; their elaborations/contract choices require review. They are listed below so no proposal is mistaken for a sourced obligation.

[REQ-02-001](#req-02-001), [REQ-02-002](#req-02-002), [REQ-02-003](#req-02-003), [REQ-02-004](#req-02-004), [REQ-02-005](#req-02-005), [REQ-02-006](#req-02-006), [REQ-02-008](#req-02-008), [REQ-02-009](#req-02-009), [REQ-02-011](#req-02-011), [REQ-02-012](#req-02-012), [REQ-02-016](#req-02-016), [REQ-03-004](#req-03-004), [REQ-03-005](#req-03-005), [REQ-03-006](#req-03-006), [REQ-03-007](#req-03-007), [REQ-03-008](#req-03-008), [REQ-03-009](#req-03-009), [REQ-04-007](#req-04-007), [REQ-04-013](#req-04-013), [REQ-05-002](#req-05-002), [REQ-05-005](#req-05-005), [REQ-05-010](#req-05-010), [REQ-06-007](#req-06-007), [REQ-06-008](#req-06-008), [REQ-06-011](#req-06-011), [REQ-06-012](#req-06-012).

- The proposed change-impact governance mechanism (REQ-06-011) is not adopted by this update.
- Candidate review roles need assignment; R1 increment criteria and exact permitted ETF/data coverage need human resolution. Frontend, broker rendering selection, provider licenses and deployment remain undecided.
- Future broker synchronization, human-authorized placement and automated execution are assessment candidates, not Approved/Future implementation records. D-03 prohibits autonomous real execution until explicitly changed through governance.

## 12. Validation and remaining gaps

### 12.1 Documentation checks

- Starting inventory verified as 85 = 66 Must / 18 Should / 1 Could before editing. Every starting ID retained.
- Final inventory: 117 records, 32 added, 33 existing content revisions; totals and field metadata reconcile with the index.
- D-01 through D-16 all retain direct source-linked coverage; no decision changes.
- Each record has unique ID, owner, source, category, priority, phase, increment/applicability, independent approval/maturity, data assumptions, dependencies, verification and acceptance.
- Requirement dependencies, question/data references, acceptance-case references, Markdown links and explicit anchors are checked for defined targets; dependency graph has no cycles.
- Normalized requirement descriptions are checked for duplicates. Complementary scope/contract/verification obligations reference their canonical owner rather than redefine it.
- The six project-context/governance source files are checked against pre-edit SHA-256 values. Only the two authorized Stage 1 Markdown artifacts are updated.
- Structural checks are not readiness verification, market-data qualification, execution simulation, backtesting or forward paper evidence.

### 12.2 Missing and overlapping requirements review

No requested R1 capability family or D-01 through D-16 is absent from the inventory. Historical, OOS/walk-forward and forward paper evidence are individually represented. Recommendation lifecycle and the four performance groups are explicit. Simulation, manual input, accounting, benchmark comparison, privacy/recovery and no-real-execution boundaries have owning records.

Detailed gaps remain in the 17 Open requirement records and 32 question records (17 preserved S1-Q plus 15 R1-Q). These are evidence/policy gaps, not completed specifications. Conditional licensing or data availability cannot silently waive a mandatory R1 capability.

Related obligations are intentionally distinct: REQ-01 business scope; REQ-02 external/input contracts; REQ-03 calculations/accounting/states; REQ-04 interactions/disclosures; REQ-05 logical/persistence/security constraints; REQ-06 verification/governance. In particular, REQ-03-033 covers simulation reproducibility, REQ-05-014 recoverable attributable histories, and REQ-06-013 verification. Their detailed rules must be referenced rather than duplicated during later authoring.

### 12.3 No fabricated outcomes

No market dataset, broker capability, trade, fill, backtest result, forward observation, win rate, profit target, validation period, fixed expiry or acceptance threshold has been generated or assumed. The ₹20 lakh reference is hypothetical/configurable. Manual actual records remain user-reported/unverified. Paper and actual performance are never combined into a misleading track record.

## 13. Next authorization boundary

Submit these two updated Stage 1 artifacts and wait. Do not begin detailed REQ-01 through REQ-06 authoring, implementation planning, scaffolding, dependency installation, application code, deployment, broker connectivity or real execution without further explicit human authorization. D-03 remains binding.
