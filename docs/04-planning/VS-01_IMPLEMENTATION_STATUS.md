# VS-01 authorized subset - approval and verification record

## Human authorization (2026-11-01)

The human Step 3 approval authorizes VS01-WI-01 through WI-06 and WI-09, in their existing dependency order, including code, routine dependencies, local Compose and tests. This record preserves the approval without rewriting the tagged REQ-BL-1.0 inventory.

- Approved ADR-01/02/03/04/05/08. ADR-04 real-data use remains conditional on qualified samples/permissions.
- Conditionally approved ADR-09 and the data-quality portion of ADR-10 only.
- Approved DC-01/02/03; conditionally approved DC-04/09; approved watchlist/import/history/quality portions of DC-07/08 only.
- SQ-02 adopted; SQ-03 unknown/unassessed behavior adopted; SQ-06 conditionally approved for documented local controls. SQ-07 grant is limited to these seven work items.
- SQ-01 remains Open. SQ-04/05, ADR-06/07, DC-05/06 and comparison portions remain unapproved. No indicator, comparison, charting, trade, GTT, paper, broker or real-order implementation.
- Baseline requirements' approval, maturity, priority and allocation are unchanged. The separate scoped behavior approval above is the implementation authority.

## Implementation refinements / impact assessment

The approved contracts are retained. Source profile.data_class explicitly records REAL_MARKET or SYNTHETIC_TEST to implement the approved synthetic-label boundary; it uses the existing JSON profile, not a new market source or claim of verification. Runtime startup uses generated local secrets; technical resource bounds remain those of DC-07. No financial policy or dataset rights are inferred.

| Impact area | Assessment |
| --- | --- |
| Requirements/decisions | Existing IDs and D-01..16 unchanged; authorized seven-item scope only. |
| Data/analytics | Existing eight entities, exact decimal observations and mapped raw provenance; no derived financial analytics. |
| Architecture/interfaces | Logical monolith, protected local API and UI, PostgreSQL/Alembic and canonical CSV; no additional service. |
| Verification | Applicable reference/API/PostgreSQL/component/browser cases; real-data acceptance stays blocked pending SQ-01. |
| Delivery | WI-01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 09; other work items not complete or implemented. |

## Current verification checkpoint

The current human Step 3 instruction additionally authorizes status review, safe dependency remediation, container locking, isolated synthetic recovery verification, regression checks, documentation and Git checkpoint preparation. **A commit still requires human confirmation.** Chart/indicator/comparison implementation is not authorized. This record supersedes the earlier 58-test checkpoint's open technical verification items without changing baseline classifications.

| Check | Actual result | Local evidence |
| --- | --- | --- |
| Python lint | Passed | `artifacts/verification.json` |
| Backend, including PostgreSQL integration | **62 passed, 0 failed, 0 skipped**; two deprecation warnings | `artifacts/backend-tests.xml` |
| Frontend components, Vitest 4.1.12 | **6 passed, 0 failed, 0 skipped** | verification command and `artifacts/verification.json` |
| Real UI/API/PostgreSQL Chromium workflow | **1 passed, 0 failed, 0 skipped** | `frontend/playwright-report/` |
| TypeScript/production build | Passed | `artifacts/verification.json` |
| Pinned Compose build/start | Passed twice; migration completed and API/database/UI ready | `artifacts/runtime-verification.json`; `artifacts/compose-repeat-startup.log` |
| Full npm audit and production-only npm audit | **0 findings** after remediation | `artifacts/frontend-audit-after.json`; `frontend-audit-production.json` |
| Windows backend audit | 40 packages, 0 findings, 0 skipped | `artifacts/backend-audit.json` |
| Actual Linux API audit | 28 packages, 0 findings, 0 skipped | `artifacts/backend-linux-audit.json` |
| Synthetic backup/isolated restore | Passed: all tables/hashes, provenance, known query and audit trigger | `artifacts/recovery-verification.json`; ignored restricted backup archive |

The prior implementation snapshot is commit `6dea57f`. Current working-tree changes supply these fixes and evidence. A scoped review and designed-case matrix is in the [verification checkpoint](VS-01_VERIFICATION_CHECKPOINT.md); passing the implemented suite does not mean all 23 designed cases or full VS-01/R1 are accepted.

## Repairs and traceability

| Change | Existing requirement/design/work/test trace |
| --- | --- |
| Source-qualification form uses PATCH instead of POST | Scoped REQ-02-008 / REQ-05-003; DC-02/07/08; WI-04/09; real browser workflow |
| Quoted platform-specific browser API launcher and accessible watchlist selector | REQ-05-001 / REQ-06-001; DC-09; WI-01/04/09; browser workflow |
| Calendar gaps bounded to observed endpoints, with two regression cases | REQ-02-013; DC-04; WI-06; VS01-T-10/17; `test_calendar_gaps_only_between_observed_endpoints` |
| Assessed Vitest 3.2.7 -> 4.1.12, mocker patched and tinypool removed | REQ-05-003/004 / REQ-06-008; ADR-08/09; DC-09; WI-01/03 and current security grant |
| Immutable official Python/Node/PostgreSQL/uv inputs | REQ-05-001/008; ADR-09; DC-09; WI-01; VS01-T-21/23 |
| Synthetic-only backup/restore verifier and instructions | REQ-05-009 / REQ-06-008; ADR-09; DC-09; current recovery grant; VS01-T-22 scoped portion |

No trading formula, strategy threshold, approved decision, source entitlement or baseline classification was introduced or changed. The two calendar tests restore the already-approved data-quality boundary; they do not choose a financial calendar.

## Remaining gaps and next work

- **Real data remains blocked:** [SQ-01 qualification package](VS-01_DATA_QUALIFICATION.md). No qualified real ETF sample or permissions inspected; VS01-T-03 is not passed by synthetic tests.
- **Remaining capabilities are unimplemented/unapproved:** SMA/EMA/Wilder RSI, price-only comparisons and charts; see the [next-package proposal](VS-01_NEXT_PACKAGE_PROPOSAL.md), including ADR/DC/SQ dispositions and remaining WI-07/08/10/11/12 work.
- **Final operational handover is partial:** synthetic recovery and repeated startup are verified; owner-data restoration/cutover, retention decisions and cumulative full-slice acceptance are not claimed. See [local recovery instructions](../05-operations/LOCAL_RECOVERY.md).
- **Dependency findings are remediated, not waived:** no unresolved critical finding in executed npm/Python dependency scans; [security assessment](VS-01_SECURITY_REVIEW.md). OS-image scanning is outside the reported scan coverage.
- **Container locking/startup controls verified on Linux/amd64:** [reproducibility review](VS-01_CONTAINER_REPRODUCIBILITY.md); no byte-identical build or cross-platform guarantee.

Historical architecture/backlog proposal labels and the tagged baseline are preserved. This record and the current human instruction carry later scoped authority. Full VS-01 and R1 remain **not accepted**.
