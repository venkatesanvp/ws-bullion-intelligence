# Requirements Document Index (Planned)

The following six specifications are planned, **not yet finalized**. Each requirement should have ID, rationale, priority, dependencies, acceptance criteria, and verification method.

## REQ-01 — Product Vision and Business Requirements
Objectives, investor personas, gold/silver focus, Indian ETF instruments, three horizons, interactive workflows, default hypothetical portfolio, use cases, measurable success criteria, scope boundaries.

## REQ-02 — Market Data and Indicator Requirements
COMEX futures/options; MCX; OI, volume, expiry and curve; DXY, USD/INR, Fed policy and expected rates, yields/real yields, inflation/jobs, crude/copper, CFTC COT, ETF NAV/flows, inventories. Provider catalog, licensing, schemas, freshness, calendars, point-in-time vintages, quality gates and Dhan/Yahoo feasibility.

## REQ-03 — Quantitative Analytics, Strategies and Trade Planning
Macro/futures/options/technical/relative-value/ETF models, regime classification, horizon-specific strategies, scoring, historical reliability, entry/stop/targets, position sizing, up-to-three GTT alternatives, canonical and broker-specific representations, portfolio risk and no-trade criteria.

## REQ-04 — Interactive AI Research Assistant
Natural-language queries, tool orchestration, proactive data requests, charts, citations/provenance, conversational context, scenario analysis, event investigations, saved research, AI guardrails and no execution.

## REQ-05 — Architecture and Nonfunctional Requirements
Python/FastAPI, PostgreSQL local Docker, data pipelines, APIs, frontend options, secrets/config, broker adapters, observability, performance, resilience, deployment, access control, backup, maintainability and Codex development governance.

## REQ-06 — Validation, Governance and Release
Historical replay, point-in-time backtesting, out-of-sample/walk-forward tests, cost/slippage models, data QA, financial calculation verification, LLM evals, security, traceability, risk approval, release gates and Phase 2 ML readiness.

## Cross-cutting traceability
Business objective → requirement ID → source/data dependency → model/design → test → evidence → approved release.
