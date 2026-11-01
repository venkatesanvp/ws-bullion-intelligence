# Discussion Summary

## Origin and evolution
The discussion began with MCX gold/silver futures, expiry-month pricing, cost of carry, contango/backwardation, liquidity, open interest, and selecting contracts. The investment approach evolved into using futures information to guide ETF investments rather than taking leveraged futures positions.

## Global intelligence scope
Include COMEX gold/silver futures and options chains (OI, volume, IV, skew, Greeks, expiries), MCX futures and term structure, DXY, USD/INR, Fed policy and market-implied rates, Treasury nominal and real yields, US CPI/PCE/PPI/jobs, WTI/Brent, CFTC COT, gold/silver ratio, ETF flows/NAV, physical-market data and other contextual indicators. Validate availability, licensing, timestamps and historical coverage.

## Analytical architecture
Separate market-data ingestion/quality, macro regime, futures positioning, options analytics, technical analysis, relative value, ETF execution quality, strategy decisions, trade planning, portfolio risk, and AI explanations. Distinguish descriptive, diagnostic, predictive, and prescriptive outputs. No claim of predictive performance without point-in-time out-of-sample testing.

## Three strategy horizons
Swing (5–20 trading days), tactical (1–3 months), strategic (6–24 months), with independent rules and combined exposure control.

## Confidence
Show signal strength, historical reliability, and data quality separately. Backtests should include realistic execution, fees, slippage, ETF spreads, futures rollover, and no look-ahead bias.

## Trade planning
Provide entry, exit, target, stop-loss, risk/reward and sizing. Up to three alternative GTT plans, e.g. breakout/pullback/deeper correction, only if justified. GTT orders are broker-specific and not guaranteed stop fills. Do not assume protective exits are linked to an entry unless verified.

## AI scope
Interactive research, proactive requests for relevant additional information, what-if analysis, explanations with evidence and timestamps, prior-signal comparison, scheduled reports and event alerts. L1–L4 advisory; exclude L5 autonomous trading.

## Engineering workflow
Specification-driven development using Codex in VS Code. ChatGPT for requirements/architecture/review, Codex for approved engineering tasks, Git Markdown as shared source of truth. PostgreSQL locally via Docker persistent volume; no coding until requirements review.

## Data candidates
User may provide Dhan historical market downloads. Yahoo Finance is a candidate fallback for some US market series, not an assured source of complete COMEX options or licensed institutional data.
