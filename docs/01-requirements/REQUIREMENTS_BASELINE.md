# Requirements Baseline REQ-BL-1.0

## 1. Control record

| Field | Value |
| --- | --- |
| Baseline ID | **REQ-BL-1.0** |
| Baseline date | **2026-11-01 (Asia/Calcutta)** |
| Product | Global Bullion Market Intelligence Platform - R1 personal-use Gold/Silver ETF investment intelligence and trade planning |
| Human disposition | Initial controlled product scope and 117-item inventory approved in the human instruction "Formalize Requirements Baseline v1.0". |
| Scope of this approval | Control the scope, source snapshots, requirement identifiers and existing classifications; not blanket approval of all individual requirements or their unresolved details. |
| Individual states | Preserved exactly: 74 Approved / 26 Proposed / 17 Open; 100 Analyzed / 17 Identified. No requirement is promoted by baseline creation. |
| Document-level versus record-level baseline | This document establishes the controlled inventory snapshot. It does **not** assign the per-requirement maturity Baselined, Verified for readiness or Specified. |
| Architecture/design authority | Architecture and VS-01 design may begin progressively before all six detailed specifications are completed, subject to the gates in section 9. |
| Implementation authority | **None under this approval.** No application implementation, scaffolding, dependency installation, deployment, broker connection or real order action. |
| Git archival state | Proposed initial commit and tag await explicit human confirmation. No commit identifier is asserted or invented. |

The human baseline approval is preserved here so the current scope and progressive-development restrictions do not depend solely on conversation history. This manifest introduces no new product requirement ID, product decision, financial policy or architecture selection.

## 2. Approved baseline scope

R1 is a genuinely usable personal investment application with the workflow:

**Market research -> Validated strategy assessment -> Trade planning -> Paper trading or manual transaction recording -> Portfolio reassessment.**

The approved controlled scope includes:
- Gold and silver market intelligence and initial Indian Gold/Silver ETF investment analysis.
- Independent swing (5-20 trading days), tactical (1-3 months) and strategic (6-24 months) strategies, with consolidated exposure within each portfolio.
- Deterministic evidence-supported ETF entry/exit recommendations, stop-loss, targets, position sizing and risk/reward.
- Up to three justified GTT alternatives, including a valid no-trade outcome; one canonical broker-independent plan and up to two selected, capability-verified broker representations.
- Paper orders, simulated fills, virtual cash/positions, explicit execution assumptions and portfolio accounting.
- Manual recording of actual transactions, opening state and cash flows; user-reported records remain **not broker-verified**.
- Interactive advisory AI research, daily intelligence and daily position/recommendation reassessment.
- Historical strategy validation, separate walk-forward/out-of-sample evidence, and forward paper trading with newly arriving data.
- Separate historical strategy, forward paper, manually recorded actual-trade and benchmark performance; historical backtest and OOS/walk-forward results remain distinguishable.
- Versioned recommendations: Draft -> Validated -> Published -> Superseded / Expired / Withdrawn. Detailed checks, authority, validity conditions and expiry behavior remain open.
- Privacy, attributable histories, backup/recovery, reconciliation and cumulative personal-use acceptance.
- A **₹20 lakh configurable hypothetical reference portfolio**, never an inferred actual balance.
- D-01 through D-16 unchanged; deterministic Phase 1 and future Phase 2 ML implementation, with Phase 2 requirements/extension readiness documented during Phase 1.
- Progressive specification-driven development and separate incremental implementation approvals.

Research recommendations, proposed trade plans, paper orders/simulated fills, manually recorded actual orders/fills, and future broker-connected assessment candidates are distinct logical concepts. R1 has **no broker connection or real order execution**. Automatic paper triggers affect virtual state only. Autonomous real execution remains prohibited by D-03.

Advanced options/history, intraday fidelity, event alerts and broker-specific rendering depend on qualified data/capabilities; conditional depth cannot silently remove required core R1 capabilities. Future broker connectivity, read-only synchronization, human-authorized placement and other automation remain assessment candidates, not approved implementation requirements. US ETF/MCX futures investment capabilities and ML implementation are outside R1; relevant extension requirements remain recorded.

## 3. Controlled documents and source authority

The proposed baseline commit comprises exactly the nine files below. Eight existing source files are frozen byte-for-byte for this baseline preparation; only this manifest is newly created.

| Path | Role in reproducing the baseline |
| --- | --- |
| [AGENTS.md](../../AGENTS.md) | Repository governance: read sources, preserve decisions, no unauthorized implementation/execution, deterministic calculations, provenance and traceability. |
| [PROJECT_OVERVIEW.md](../00-project-context/PROJECT_OVERVIEW.md) | Product context v0.4 and initial technology direction; unresolved details are not decisions. |
| [DISCUSSION_SUMMARY.MD](../00-project-context/DISCUSSION_SUMMARY.MD) | Rationale, analytical scope and candidate datasets; not evidence of source availability or licenses. |
| [DECISION_REGISTER.md](../00-project-context/DECISION_REGISTER.md) | Authoritative approved D-01 through D-16 and accepted engineering direction. |
| [REQUIREMENTS_INDEX.md](../00-project-context/REQUIREMENTS_INDEX.md) | Planned six-document structure and traceability expectations. |
| [OPEN_QUESTIONS.md](../00-project-context/OPEN_QUESTIONS.md) | Original unresolved topics; neither answers nor approved policies. |
| [STAGE_1_REQUIREMENTS_OUTLINE.md](STAGE_1_REQUIREMENTS_OUTLINE.md) | v0.2 specification boundaries, ownership, conventions, R1 scope and increments. |
| [STAGE_1_REQUIREMENTS_BACKLOG.md](STAGE_1_REQUIREMENTS_BACKLOG.md) | v0.2 canonical 117-item inventory, per-record states, sources, dependencies, planned verification, questions and change history. |
| [REQUIREMENTS_BASELINE.md](REQUIREMENTS_BASELINE.md) | This manifest: current human baseline approval, source snapshots, preserved classifications, process authorization and proposed Git package. |

### 3.1 Interpretation and recorded qualifications

1. D-01 through D-16 retain their approved meaning. This manifest does not amend or reinterpret them.
2. The current human approval controls this baseline's scope and progressive stage authorization. AGENTS governance continues to apply. Existing per-record approval/maturity controls remain intact.
3. Stage 1 review-draft labels and earlier context dates are preserved as source history. A controlled inventory may contain Proposed/Open requirements and immature records.
4. Earlier context, including the suggested all-six-documents-first sequence in OPEN_QUESTIONS, predates the current progressive authorization. Architecture and VS-01 design need not wait for all six documents; capability implementation still requires the applicable approved/specified inputs and separate human authorization.
5. Prior Stage 1 "wait for further authorization" wording remains historical; the current instruction supplies limited architecture/VS-01 design authority, **not implementation authority**.
6. Source text displaying "?20 lakh" is an existing encoding defect. Repeated human direction establishes ₹20 lakh; source files are preserved rather than silently corrected.
7. Priority or phase/increment allocation is not approval, data availability, validation evidence or permission to code. Recommendation state Validated is distinct from requirement maturity Verified for readiness.
8. No provider license, broker capability, market sample, real holding, financial threshold, execution parameter, expiry duration, profitability/win-rate target or validation period is approved by inference.

These qualifications were identified before manifest completion and are recorded rather than silently resolved by editing the sources. No unresolved count, ID or classification discrepancy was found.

## 4. Controlled inventory and classifications

The starting 85 records (66 Must / 18 Should / 1 Could) were retained in the R1 update. Two Should -> Must changes plus 32 new Must records produce the controlled **117-item** inventory. No ID is removed, renumbered or reused.

| Owning specification | Controlled ID range | Count | Must | Should | Could | Approved | Proposed | Open | Identified | Analyzed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| REQ-01 | REQ-01-001 through REQ-01-012 | 12 | 10 | 1 | 1 | 11 | 0 | 1 | 1 | 11 |
| REQ-02 | REQ-02-001 through REQ-02-018 | 18 | 14 | 4 | 0 | 5 | 11 | 2 | 2 | 16 |
| REQ-03 | REQ-03-001 through REQ-03-039 | 39 | 36 | 3 | 0 | 27 | 6 | 6 | 6 | 33 |
| REQ-04 | REQ-04-001 through REQ-04-015 | 15 | 11 | 4 | 0 | 12 | 2 | 1 | 1 | 14 |
| REQ-05 | REQ-05-001 through REQ-05-014 | 14 | 12 | 2 | 0 | 6 | 3 | 5 | 5 | 9 |
| REQ-06 | REQ-06-001 through REQ-06-019 | 19 | 17 | 2 | 0 | 13 | 4 | 2 | 2 | 17 |
| **Total** | **117 unique stable IDs** | **117** | **100** | **16** | **1** | **74** | **26** | **17** | **17** | **100** |

### 4.1 Approval distribution

| Approval | Count | Baseline interpretation |
| --- | ---: | --- |
| Approved | 74 | Preserve the sourced obligation; unresolved operational details are not thereby approved. |
| Proposed | 26 | Controlled proposal, still awaiting approval. |
| Open | 17 | Controlled unresolved requirement area; behavior/criteria still need a ruling or evidence. |

### 4.2 Independent maturity distribution

| Maturity | Count |
| --- | ---: |
| Identified | 17 |
| Analyzed | 100 |
| Specified | 0 |
| Verified for readiness | 0 |
| Baselined | 0 |

Document-level approval of REQ-BL-1.0 does not change any of these values. A separately documented decision is required for any individual state change.

Phase allocations remain Phase 1: 115; Phase 2: 1 (REQ-03-022); Future: 1 (REQ-01-010). R1-A/B/C are acceptance increments, not substitutes for those phase attributes. See the inventory for applicability and conditional coverage.

## 5. Approved decisions D-01 through D-16

The decision register remains the authoritative text; the following is an index, not amended decision wording. Direct requirement coverage is in the [backlog decision matrix](STAGE_1_REQUIREMENTS_BACKLOG.md#6-d-01-through-d-16-coverage-and-impact).

| Decision reference | Approved topic |
| --- | --- |
| [D-01](../00-project-context/DECISION_REGISTER.md) | Gold/silver primary assets; other markets contextual |
| [D-02](../00-project-context/DECISION_REGISTER.md) | Swing, tactical and strategic horizons |
| [D-03](../00-project-context/DECISION_REGISTER.md) | Advisory L1-L4; no autonomous real execution |
| [D-04](../00-project-context/DECISION_REGISTER.md) | Indian Gold/Silver ETFs initially; extensibility |
| [D-05](../00-project-context/DECISION_REGISTER.md) | Up to three evidence-supported GTT scenarios; no-trade valid |
| [D-06](../00-project-context/DECISION_REGISTER.md) | Configurable default portfolio; hypothetical versus actual distinction |
| [D-07](../00-project-context/DECISION_REGISTER.md) | Dashboard, conversational, scheduled and event-driven research |
| [D-08](../00-project-context/DECISION_REGISTER.md) | Multiple separate models and reconciliation |
| [D-09](../00-project-context/DECISION_REGISTER.md) | Deterministic Phase 1; Phase 2 ML requirements/readiness then implementation |
| [D-10](../00-project-context/DECISION_REGISTER.md) | Separate signal strength, historical reliability and data quality |
| [D-11](../00-project-context/DECISION_REGISTER.md) | Deterministic explainable canonical plan; up to two broker renderings |
| [D-12](../00-project-context/DECISION_REGISTER.md) | Point-in-time historical replay |
| [D-13](../00-project-context/DECISION_REGISTER.md) | Event-driven alerts/reassessment, not automatic trades |
| [D-14](../00-project-context/DECISION_REGISTER.md) | Provider-independent phased data acquisition |
| [D-15](../00-project-context/DECISION_REGISTER.md) | ₹20 lakh hypothetical configurable reference; risk/allocation still pending |
| [D-16](../00-project-context/DECISION_REGISTER.md) | Daily EOD initially; event updates where reliable data permits |

## 6. R1 acceptance increment definitions

| Increment | Human-directed acceptance scope | Acceptance boundary |
| --- | --- | --- |
| R1-A - Research Platform | Market-data acquisition and qualification; gold/silver intelligence; Indian Gold/Silver ETF analysis; interactive AI research; independent horizon assessments; daily intelligence reports. | Research evidence, quality and timestamps are inspectable. This increment alone is not complete R1. |
| R1-B - Validated Trade Planning and Paper Trading | Deterministic strategy evaluation; evidence-supported recommendations; entry/exit/stop/targets/sizing; up-to-three justified GTT scenarios; risk and capital reservation; paper orders/fills/accounting; historical validation and forward paper evidence. | Publication, strategy/evidence and simulation policies meet approved criteria; backtest, OOS/walk-forward and arriving-data forward records stay distinct. No invented target or period. |
| R1-C - Manual Trading Support and Personal-Use Readiness | Broker-neutral instructions; manually recorded real transactions; separate paper/manual portfolios; reconciliation and performance reporting; daily position/recommendation reassessment; privacy, backup/recovery and cumulative acceptance. | All required R1-A/B/C capabilities accepted together; manual records remain unverified; no broker connection or real order path. |

These increment capability definitions are controlled scope within REQ-BL-1.0. They are not implementation milestones or authorization to build/deploy. Detailed acceptance planning remains reviewable/open. R1-B includes paper trading; it is not postponed to R1-C. All three approved investment horizons remain in R1.

These increments are included in the approved R1 controlled scope. Their detailed acceptance decisions remain open; they are not authorizations to implement or deploy an increment. Full R1 requires cumulative personal-use readiness, not only R1-A research.

## 7. Proposals, open requirements and release blockers

### 7.1 Preserved Proposed records (26)

[REQ-02-001](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-001), [REQ-02-002](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-002), [REQ-02-003](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-003), [REQ-02-004](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-004), [REQ-02-005](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-005), [REQ-02-006](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-006), [REQ-02-008](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008), [REQ-02-009](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-009), [REQ-02-011](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011), [REQ-02-012](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012), [REQ-02-016](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-016), [REQ-03-004](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-004), [REQ-03-005](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-005), [REQ-03-006](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-006), [REQ-03-007](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007), [REQ-03-008](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008), [REQ-03-009](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-009), [REQ-04-007](STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-007), [REQ-04-013](STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013), [REQ-05-002](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002), [REQ-05-005](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-005), [REQ-05-010](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010), [REQ-06-007](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-007), [REQ-06-008](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008), [REQ-06-011](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-011), [REQ-06-012](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-012).

These records remain Proposed. In particular, REQ-06-011's detailed change-impact mechanism is not automatically adopted by inventory approval. Newly drafted acceptance operationalization also requires applicable review even when a high-level obligation is Approved.

### 7.2 Preserved Open records (17)

[REQ-01-008](STAGE_1_REQUIREMENTS_BACKLOG.md#req-01-008), [REQ-02-013](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-02-014](STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-014), [REQ-03-003](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-003), [REQ-03-011](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-011), [REQ-03-013](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-013), [REQ-03-015](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-015), [REQ-03-020](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-020), [REQ-03-022](STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-022), [REQ-04-012](STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-012), [REQ-05-004](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004), [REQ-05-006](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-006), [REQ-05-007](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-007), [REQ-05-008](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-008), [REQ-05-009](STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-009), [REQ-06-006](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006), [REQ-06-009](STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-009).

Financial policies are explicitly unresolved, including strategy/reconciliation (REQ-03-003/011), confidence sufficiency (REQ-03-013), allocation/limits/sizing/financing (REQ-03-015), plan validity/expiry policy (REQ-03-020), data-quality/history gates (REQ-02-013/014), and acceptance/evidence thresholds (REQ-06-006). Approval of paper simulation or a recommendation lifecycle does not select their numerical rules.

### 7.3 Preserved question inventory

There are **32 questions**: 17 S1-Q-001 through S1-Q-017 and 15 R1-Q-001 through R1-Q-015. They remain in the [canonical question register](STAGE_1_REQUIREMENTS_BACKLOG.md#question-register); no answer, due date or named role assignment is inferred.

| Acceptance area | Unresolved decisions/evidence |
| --- | --- |
| R1-A | ETF/minimum global coverage, permissions, inspected data availability, quality/time alignment, AI tool/data permissions and daily cutoff. |
| R1-B | Independent strategy/risk rules; recommendation validation/publication checks; trigger/fill/gap/partial-fill/cost/liquidity/reservation/expiry policies; historical/OOS sufficiency and forward-paper criteria. |
| R1-C | Manual opening/correction/cash-flow handling, accounting/marking/benchmarks, separated performance, daily reassessment, privacy, recovery and cumulative sign-off. |
| Conditional features | Broker capability evidence for selected renderings; licensed options/intraday/event coverage for the affected claims. Generic placement instructions do not require broker selection. |
| Later scope | Frontend selection and future instrument/ML details remain pending; Phase 1 documentation/extension obligations persist without authorizing future implementation. |

These are capability readiness blockers, **not blockers to preserving an honest controlled inventory with Open/Proposed entries**. No mandatory capability may be silently dropped to bypass its blockers. No unsupported financial policy is presented as approved in this manifest.

## 8. Source snapshots and reproducibility

### 8.1 Content fingerprints

Hashes below were captured before manifest creation, with no changes to the eight source files. Raw SHA-256 identifies exact current bytes. Canonical-LF SHA-256 hashes decoded UTF-8 text re-encoded without BOM, replacing CRLF/lone CR with LF while preserving final-newline presence. Canonical fingerprints permit comparison after line-ending conversion. All eight current sources already have identical raw and canonical hashes.

| Source path | Raw SHA-256 | Canonical-LF SHA-256 |
| --- | --- | --- |
| [AGENTS.md](../../AGENTS.md) | `8b3a3bec1e23148fbb67b05256b86b004a5ad58e72f86c7ed6fd453e4cb430f9` | `8b3a3bec1e23148fbb67b05256b86b004a5ad58e72f86c7ed6fd453e4cb430f9` |
| [docs/00-project-context/PROJECT_OVERVIEW.md](../00-project-context/PROJECT_OVERVIEW.md) | `835927b50546ae86ad4bc934227ea8ff8923217d41aa4d734df1336c26c73f9e` | `835927b50546ae86ad4bc934227ea8ff8923217d41aa4d734df1336c26c73f9e` |
| [docs/00-project-context/DISCUSSION_SUMMARY.MD](../00-project-context/DISCUSSION_SUMMARY.MD) | `f999fcce145750d56f2bde305546f85e8427679d2564c7954f65e6c7d33649b8` | `f999fcce145750d56f2bde305546f85e8427679d2564c7954f65e6c7d33649b8` |
| [docs/00-project-context/DECISION_REGISTER.md](../00-project-context/DECISION_REGISTER.md) | `8af8dc23a6ce15b88690bd4153b6be00f5854ce55b0c00db6392bd52116e6d5e` | `8af8dc23a6ce15b88690bd4153b6be00f5854ce55b0c00db6392bd52116e6d5e` |
| [docs/00-project-context/REQUIREMENTS_INDEX.md](../00-project-context/REQUIREMENTS_INDEX.md) | `5d3942b2f30ddba5abaf4a8271d1680f0bf1666680b70ce32228519a434fe9f0` | `5d3942b2f30ddba5abaf4a8271d1680f0bf1666680b70ce32228519a434fe9f0` |
| [docs/00-project-context/OPEN_QUESTIONS.md](../00-project-context/OPEN_QUESTIONS.md) | `a67a66bfa4c3d827868b51e885c718d172190b8034ab68cc5886e91142c91538` | `a67a66bfa4c3d827868b51e885c718d172190b8034ab68cc5886e91142c91538` |
| [docs/01-requirements/STAGE_1_REQUIREMENTS_OUTLINE.md](STAGE_1_REQUIREMENTS_OUTLINE.md) | `d75206628195efe05a231c1e62f479247f6b5b5afbe4000c2e223e091663ba50` | `d75206628195efe05a231c1e62f479247f6b5b5afbe4000c2e223e091663ba50` |
| [docs/01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md](STAGE_1_REQUIREMENTS_BACKLOG.md) | `ec1030aff46a4f2a5d74aafeca332991236d52d29edc11f1b7021538c85d208d` | `ec1030aff46a4f2a5d74aafeca332991236d52d29edc11f1b7021538c85d208d` |

### 8.2 Git-normalized content

Repository object format: **sha1**. Current core.autocrlf is **true**; no .gitattributes was introduced and no Git configuration was changed. Git may normalize LF in the object database and use CRLF in a future Windows checkout. Raw checkout hashes may then differ without a semantic change; compare canonical-LF and Git blob fingerprints. Fingerprinting used read-only hash-object without -w.

| Source path | Expected Git blob ID under inspected attributes/configuration |
| --- | --- |
| AGENTS.md | `ee02d5cb0ed04496ff0ba56fed8085abf0f1daf2` |
| docs/00-project-context/PROJECT_OVERVIEW.md | `72580fa38c3510e4e0c5afeefb99c9814fcc4453` |
| docs/00-project-context/DISCUSSION_SUMMARY.MD | `e537d17738844a3dfc80741e73ff8a4f928a4ce3` |
| docs/00-project-context/DECISION_REGISTER.md | `46bdb2ac2a1b4b5cae1f67efdee2bb2b40570af0` |
| docs/00-project-context/REQUIREMENTS_INDEX.md | `d52126eb511d8fc4a5ffc08197b37f0fd6083ba8` |
| docs/00-project-context/OPEN_QUESTIONS.md | `468a0ccb4ad106a17d9050b3b4b0ea1047b60bf5` |
| docs/01-requirements/STAGE_1_REQUIREMENTS_OUTLINE.md | `8a7981eea4a08defaf79b64801cedb5a14032628` |
| docs/01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md | `65ab6a3625f2003b88e36d163c6516993234c59e` |

The manifest excludes its own checksum to avoid recursive self-reference. The eventual approved commit will version the manifest together with its eight sources; no commit/tag is created by this document. Re-check source fingerprints and inspect the staged diff before any later commit, including any configuration/filter changes.

### 8.3 Inventory fingerprints

- Sorted requirement ID set SHA-256: `1b55a2ef4c8024d61724e49badff224d571569a99f2ceeaebacb513d14bbf8cb`.
- Sorted requirement metadata SHA-256: `646eb13242773a0225c804082dc4d93eb8f951db8103449829ba20d3f3180297`.
- ID serialization: ascending ID, one ID per LF-terminated line.
- Metadata serialization: ascending ID, one LF-terminated line containing ID|Approval|Maturity|Priority|Phase using exact classification text and no added spaces.

These permit future verification that IDs and classifications have not silently changed. Full source fingerprints remain authoritative for all other content; counts alone are insufficient to establish snapshot identity.

## 9. Progressive SDD and explicit implementation restrictions

Current human authorization permits architecture and VS-01 design **before all six detailed specifications are complete**. It does not permit application implementation.

Architecture/design may reference the controlled inventory and expose alternatives, missing requirements and dependencies. Proposed/Open details must remain visibly unresolved, not be converted into architecture decisions without the applicable approval.

Before implementing a capability, separately establish:
1. The capability boundary and applicable requirement IDs, with sufficiently specified and approved behavior.
2. Applicable interfaces/contracts, acceptance criteria and verification expectations, reviewed and approved at the needed level.
3. Relevant data/financial/security policy blockers resolved or explicitly excluded by an approved scope decision.
4. Traceability: **Requirements -> Architecture -> Design -> Code -> Tests**, with later verification evidence linked to the same requirements and design versions.
5. Explicit human authorization for that implementation increment. Baseline approval, a Published recommendation, a Git commit/tag or completion of unrelated specifications does not supply this authorization.

No capability is deemed implementation-ready by the current baseline: no record maturity has been promoted. Do not scaffold, install dependencies, create application code, deploy, connect accounts or place real orders under this instruction. D-03 remains binding.

### 9.1 Exact next architecture-initiation activities

1. Define the candidate VS-01 capability boundary and map it to existing Approved requirements, Proposed/Open dependencies and acceptance scenarios; do not assume its scope is already selected.
2. Prepare architecture context and logical responsibility/mode boundaries, provenance/evidence/version needs, and interface requirements without silently choosing pending frontend, provider, broker, deployment or service-decomposition options.
3. Prepare a VS-01 design specification and verification/acceptance expectations; refine only the applicable requirements needed for this slice, recording assumptions and human decisions.
4. Review architecture options, slice design and requirement/interface readiness with the human owner. Preserve requirement IDs and independent approval/maturity histories.
5. Request the later explicit implementation authorization only when the concrete slice is reviewable and its applicable gates are satisfied. Completing all six detailed documents is not an upfront global gate.

This manifest records the permitted process and next activities; it does not create architecture/design artifacts or select a vertical slice.

## 10. Baseline change control

### 10.1 Preservation rules for REQ-BL-1.0

- Preserve the approved scope, D-01 through D-16, stable IDs, source snapshots and individual classifications until an explicitly documented human decision authorizes a change.
- For a change, record its reason/source, affected IDs, before/after meaning and independent approval/maturity effects. Do not infer approval from inclusion in a baseline.
- Distinguish requirement elaboration, open-question resolution, phase/increment allocation, implementation authorization and an amendment of an approved decision. A decision amendment needs explicit human authorization.
- Assess affected requirements/decisions, data/analytical contracts, logical architecture/interfaces, acceptance/verification and delivery/dependencies. Unknown impacts remain recorded rather than assumed absent.
- After applicable approval, update the authorized artifacts and reciprocal links, counts, fingerprints and baseline/change history; retain stable IDs and the prior controlled version in Git.
- Present the exact Git changes for confirmation before the initial commit/tag. Never reuse or move requirements-v1.0 silently to represent later content; a future revision needs its own authorized baseline/versioning action.

These are baseline preservation controls under the current instruction. They do not promote or blanket-adopt the more detailed Proposed REQ-06-011 workflow, assign review roles/branch protections, or modify any requirement status. Any elaboration of that mechanism remains subject to separate review.

## 11. Consistency verification and qualifications

The baseline preparation checks:
- All 117 requirements are accounted for: unique IDs, continuous per-document ranges and retention of the original 85 IDs.
- Counts match the canonical backlog: 74 Approved / 26 Proposed / 17 Open; 100 Analyzed / 17 Identified; priority 100/16/1.
- All Proposed/Open records and all maturity values are preserved; fingerprints freeze the classifications.
- D-01 through D-16 have source-linked coverage; the decision register and all eight pre-existing files remain unchanged.
- Requirement/data/question references and Markdown file/anchor links resolve; dependency graph has no cycles.
- No unresolved financial/execution/expiry/validation-period policy is supplied as an approved default; no financial or strategy performance evidence is fabricated.
- The distinction between document-level baseline control and individual maturity is explicit; older sequencing/review metadata is qualified by current authority.
- The Git package includes no unrelated work; no index staging, commit, tag, reset, cleanup or discard is performed.

No unresolved inventory or source-preservation inconsistency blocks this manifest. Open capability questions continue to block their applicable readiness gates. Git archival remains pending human confirmation, not completed by this file.

## 12. Exact proposed Git package - confirmation required

Observed repository state before manifest creation: master is an unborn branch (no commits); index empty; all eight existing authority files untracked; no unrelated tracked, staged or ignored files identified. requirements-v1.0 is absent. Command-scoped safe.directory was used for read-only access; no persistent Git configuration was changed.

The proposed initial commit adds exactly these nine files:

| Git path | Proposed action | Change under this task |
| --- | --- | --- |
| AGENTS.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/00-project-context/PROJECT_OVERVIEW.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/00-project-context/DISCUSSION_SUMMARY.MD | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/00-project-context/DECISION_REGISTER.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/00-project-context/REQUIREMENTS_INDEX.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/00-project-context/OPEN_QUESTIONS.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/01-requirements/STAGE_1_REQUIREMENTS_OUTLINE.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md | Add existing untracked source | No content change; fingerprinted snapshot. |
| docs/01-requirements/REQUIREMENTS_BASELINE.md | Add new manifest | Establish REQ-BL-1.0 control record and current progressive authorization. |

**Proposed commit message:** `docs(requirements): establish R1 requirements baseline v1.0`  
**Proposed tag:** `requirements-v1.0`

No files are staged, committed or tagged by baseline preparation. After human confirmation, re-check the exact file list, source fingerprints, index and staged changes; do not stage unrelated work. Apply the tag only to the resulting confirmed baseline commit. No push or publication is authorized.

## 13. Baseline event record

| Date | Event | Effect |
| --- | --- | --- |
| 2026-11-01 | Human approved REQ-BL-1.0 scope and controlled 117-item inventory | Preserves individual approval and maturity; no blanket approval or implementation permission. |
| 2026-11-01 | Manifest prepared and consistency checked | Eight authority files preserved; new manifest only; exact nine-file Git package awaits confirmation. |
