# Open Questions and Pending Decisions

These are **not approved requirements**. Resolve in requirements/design review.

1. **Portfolio:** How should the ₹20 lakh hypothetical capital be split between gold, silver, cash, and swing/tactical/strategic strategies? What per-trade and aggregate risk limits?
2. **Broker:** Which Indian broker(s) should be the first two GTT adapters? Confirm order types, tick sizes, trigger limits, OCO support, order lifecycle, and whether any brokerage API is needed in advisory-only mode.
3. **Data feasibility:** What exactly is available in the user's Dhan historical exports (coverage, OI, expiry, timestamps, corporate actions)? What licensed alternatives are needed for COMEX options, IV/Greeks and historical chains?
4. **Data policy:** What sources may be used for commercial/noncommercial automated retrieval? How should missing/stale data affect reports?
5. **Frontend:** Streamlit for MVP or React from the start? How should interactive charts and chat share state?
6. **Strategy specifications:** Which technical indicators, thresholds, entry/exit methods and benchmarks are candidates for backtesting? How will model weights be validated?
7. **Event alerts:** What alert thresholds, hours, delivery channels, deduplication and escalation rules?
8. **Historical replay:** Required lookback periods and data vintages; methods for futures continuous series and roll adjustments.
9. **Phase 2 ML:** Which forecast targets, evaluation methods, monitoring and model registry should Phase 1 prepare for?
10. **Security and deployment:** Local-only first? GitHub private repository? Secrets handling, backups, recovery and eventual AWS hosting.
11. **Codex governance:** Exact review gates, agent roles, branch protections and approval authority.
12. **GTT representations:** Interpret “one broker-independent, then two broker-dependent” as one canonical plan plus up to two broker-specific renderings; confirm in design.

## Suggested next step
Review detailed ToCs for REQ-01 through REQ-06, then draft and approve each requirements document before implementation.
