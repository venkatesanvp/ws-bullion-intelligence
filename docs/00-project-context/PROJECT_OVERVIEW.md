# Global Bullion Market Intelligence & Interactive ETF Research Platform

**Status:** Requirements discovery baseline v0.4 (1 November 2026). No implementation approved yet.

## Vision
Build an interactive, evidence-based investment research and trade-planning platform focused on **gold and silver**. Analyze US and Indian futures, options, macroeconomics, currency, and ETF data to inform investment decisions, without autonomous execution.

## Supported horizons
- **Swing:** 5–20 trading days.
- **Tactical:** 1–3 months.
- **Strategic:** 6–24 months.

Each strategy must have independent signals, validation, and risk controls while aggregating correlated exposure across strategies.

## Investment instruments
Indian Gold and Silver ETFs initially. Architecture extensible to US ETFs and MCX futures. Other commodities (e.g. crude, copper) serve as contextual indicators, with user-requested research available.

## Experience
Web dashboard, conversational research assistant, scheduled end-of-day reports, and event-driven alerts where data permits. Assistant can proactively identify missing inputs and ask targeted questions, or fetch permitted data automatically.

## Trade planning
Evidence-supported entry/exit/targets/stops, risk/reward and position sizing. Generate **up to three** alternative GTT scenarios where justified, not a mandatory three. Canonical broker-independent trade plan plus up to two broker-specific representations, subject to design and broker capability. Human places orders; no autonomous execution.

## Initial technology direction
VS Code + Codex; Python, FastAPI, pandas/NumPy, PostgreSQL in local Docker with persistent storage, Streamlit or React (final selection at design), pytest, Git/GitHub. Specifications in Markdown, review before implementation.

## Default portfolio
₹20 lakh **hypothetical**, configurable reference portfolio. Allocation and risk limits remain to be agreed; it is not the user's actual portfolio.
