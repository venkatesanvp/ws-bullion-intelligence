# Codex Working Instructions — Bullion Intelligence

Read `docs/00-project-context/` before any work. This repository follows specification-driven development: requirements and decisions are reviewed before implementation.

## Governance
- Treat `DECISION_REGISTER.md` as the approved baseline; distinguish decisions from proposals.
- Do not implement application code until explicitly authorized.
- Do not execute trades or connect to brokerage accounts without explicit authorization. L5 autonomous trading is out of scope.
- Never fabricate market data, signals, probabilities, or backtest results. Show source, timestamps, and uncertainty.
- Keep market calculations deterministic, reproducible, and independently testable; AI research is advisory.
- Never commit credentials, tokens, account identifiers, or personal portfolio data.
- Preserve point-in-time data and avoid look-ahead bias, survivorship bias, and futures-rollover distortions.
- Trace changes from requirement ID to design, code, tests, and evidence.
- Ask for clarification when requirements conflict; do not silently revise approved decisions.

## First task
Read the project context and produce a requirements gap review. Do not scaffold or implement without approval.
