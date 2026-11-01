# Decision Register — Baseline v0.4

**Status:** D-01–D-16 approved in discussion. Details marked pending are not yet approved.

| ID | Approved decision | Notes |
|---|---|---|
| D-01 | Gold and silver are primary assets; other markets contextual | Bot can supply requested contextual data and proactively seek relevant information. |
| D-02 | Support swing, tactical, strategic horizons | 5–20 trading days; 1–3 months; 6–24 months. |
| D-03 | AI autonomy L1–L4, not L5 | Advisory trade plans only; no autonomous execution. |
| D-04 | Indian Gold/Silver ETFs initially | Extend architecture to US ETFs and MCX futures. |
| D-05 | Up to three GTT scenarios | Only evidence-supported; no-trade is valid. |
| D-06 | Configurable default portfolio until account integration | Do not represent hypothetical values as actual holdings. |
| D-07 | Dashboard, conversational AI, scheduled and event-driven research | Both on-demand and proactive. |
| D-08 | Multiple analytical models | Separate model outputs and reconciliation. |
| D-09 | ML phased | Document Phase 2 ML requirements and design extension points in Phase 1; deterministic Phase 1 implementation. |
| D-10 | Three-dimensional confidence | Signal strength, historical reliability, data quality. |
| D-11 | Deterministic, explainable, broker-aware GTT | One broker-independent representation, up to two broker-dependent representations; config/env approach decided during design. |
| D-12 | Historical replay | Point-in-time correctness required. |
| D-13 | Event-driven intelligence | Alerts and reassessment, not automatic trades. |
| D-14 | Provider-independent phased data acquisition | Dhan historical download available from user; Yahoo Finance possible US fallback after validation. |
| D-15 | ₹20 lakh hypothetical configurable portfolio | Detailed allocation/risk settings pending agreement. |
| D-16 | Daily EOD initially | Event-driven updates where reliable data permits. |

## Additional accepted engineering direction
- Specification-driven development with Codex and VS Code.
- Python backend, FastAPI, PostgreSQL local Docker persistent storage, Git; frontend selection during design.
- Six-document requirements package and phased implementation/review process accepted.

## Not yet decided
Specific broker adapter(s), provider licenses, portfolio allocations, risk limits, ML algorithms, UI framework, data SLAs, exact schedule, and detailed GTT lifecycle design.
