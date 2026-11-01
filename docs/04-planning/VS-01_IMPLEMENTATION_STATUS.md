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

## Work and evidence

Implementation authorized; verification results will be entered only after tests execute. No work item is complete merely because its code exists.
