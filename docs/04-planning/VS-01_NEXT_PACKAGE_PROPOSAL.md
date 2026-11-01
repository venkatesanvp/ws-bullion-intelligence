# Proposed next VS-01 implementation package

**Historical Step 3 proposal, adopted within the human Step 4 scope on 2026-11-02.** The dated architecture/design records and current implementation status govern approval and evidence; the original proposal below is retained for traceability. RSI requires n>=2 under Step 4. D-01..16 and REQ-BL-1.0 classifications remain unchanged. Full VS-01 is not accepted.

## Bounded capability and approval package

| Work | Existing trace | Pending scoped approvals |
| --- | --- | --- |
| Pure SMA(n), SMA-seeded EMA(n), Wilder RSI(n) | WI-07; REQ-03-001/007, REQ-06-002/006; VS01-T-11..14 | ADR-06; DC-05; analytical portions of DC-04/07/08; SQ-04 and applicable SQ-03 extension; explicit SQ-07 grant. |
| Price-only ETF comparisons | WI-08; REQ-03-008/009, REQ-04-013; VS01-T-15/16 | Remaining ADR-10 comparison semantics; DC-06 and comparison portions of DC-04/07/08; SQ-05; SQ-07 grant. |
| Locally bundled price/indicator/comparison charts and accessible tables | WI-10; REQ-04-001/005/006/013; VS01-T-02/09/10/14/16/18 | ADR-07 (Plotly candidate and package/license/bundle review), ADR-06 and remaining ADR-10; chart portions of DC-07/08, DC-05/06; applicable SQ-04/05/07. |
| Remaining integrated and operational acceptance | Remaining WI-11/12; VS01-T-01..23 as applicable | Scoped ADR-08/09/DC-09 extensions if required; SQ-01 for real data, SQ-06 final local recovery/retention disposition and an explicit SQ-07 grant for remaining work. Current synthetic recovery evidence does not waive real-data/final handover gates. |

Dependencies: WI-07 follows existing WI-06; WI-08 follows WI-06 (the actual backlog dependency); WI-10 follows WI-07/08/09; full WI-11 follows required capabilities and qualified real samples; final WI-12 follows integrated acceptance. A chart-only subpackage would need its own bounded approval rather than silently changing this order.

## Proposed contracts to review

Use the existing DC-05 conventions: required integer n (1..10,000 technical bound), local Decimal precision 34/HALF_EVEN, 12-place derived decimal strings, explicit algorithms/fingerprints and input revisions. SMA uses n closes; EMA starts from the n-close SMA; Wilder RSI uses n deltas, specified zero-gain/loss behavior and null FLAT_WINDOW. Preserve warm-up/unknown-basis/gap/action reasons. Calculate recursive series from the full eligible segment prefix, independent of display range; reject excessive prefixes rather than silently truncate. No default period or trading threshold.

Under DC-06, require explicit sources, same currency and compatible known basis; use common observed dates with no filling. Show actual endpoints, closes/available volume, price change and base-100 normalization. At least two common dates for period change. No total-return, NAV premium, tracking, spread, liquidity ranking or investment recommendation claims.

Bundle charts locally, load them lazily, render API-derived values, disclose precision/display conversion and preserve exact values in accessible tables. Keep source/basis/revision/quality and synthetic labels visible. No CDN or hosted chart account. Authoritative financial calculations stay in Python.

## Verification and acceptance

Implement independent Fraction/high-precision references for SMA/EMA/RSI, deterministic fingerprints, prefix/range invariance, no-future-row effects, discontinuities and invalid bounds. Test common-date/basis/currency/insufficient-history comparison failures. Add real API/PostgreSQL browser flows for charts, overlays, comparisons, source changes and unavailable/error/stale states, plus keyboard/table access. Rerun ingestion/security/recovery regressions and scan any added chart dependencies. Qualified real Gold and Silver ETF files are still required for T-03; a synthetic-only package remains explicitly partial.

## Proposed human authorization text

> Approve ADR-06/07 and the remaining research-comparison portions of ADR-10; approve DC-05/06 and the applicable analytical/chart/comparison portions of DC-04/07/08. Adopt the documented SQ-04/05 conventions and preserve the existing SQ-03 data-quality constraints. Grant SQ-07 for WI-07/08/10 and the remaining applicable WI-11/12 verification/handover work, including routine tested dependencies and locally bundled chart assets. Preserve all baseline IDs/classifications. Keep SQ-01 real-data acceptance blocked until samples/rights/listings are qualified; record any SQ-06 retention/recovery disposition explicitly. Exclude strategies, signals, trade plans/GTT, portfolios, paper/manual trading, AI/ML, broker connections and orders.

This text is offered for review, not treated as an instruction. Acceptance and commit confirmation are separate decisions.
