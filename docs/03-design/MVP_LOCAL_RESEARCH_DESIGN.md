# Local Research MVP design and gap review

Authorization: owner MVP-02/03/04 request, 7 November 2026. Requirements baseline and FRC proposal status are unchanged.

## Verified baseline
PR #1 is merged; GitHub main is afa434cf2fe7e432f63b241f32e95bdcd2b3b621. Dedicated branch: feature/local-mvp-charting-forecasting-deployment. Main has no protection rules/rulesets; no GitHub Actions workflows exist. No remote settings changed.

## Gaps and implementation
- MVP-02: promote the installed lightweight-charts 5.2.1 renderer into a shared financial chart. Single chart with native panes shares one time scale/crosshair, avoiding cross-chart synchronization loops. Retain Plotly selection and automatic renderer-error fallback. Display-only coordinate conversions; all calculations remain server Decimal contracts. Reject invalid timestamps/duplicate bars, retain gaps, and separate volume/RSI/MACD/ATR scales. Lifecycle owns and disposes chart, subscriptions, animation frames, marker primitives and series. Themes and indicator visibility update without recreating the chart.
- MVP-03: reuse existing forecasting routes/models/evaluation/registry. Add exact OHLCV to existing eligible history metadata (same observations and filters), and a reusable completed-history chart with endpoint-only forecast series. Technical inspection stays in the forecasting view via existing read-only technical route, without implicit acquisition. Strict real mode stays default; conditional acknowledgement and sample warnings stay mandatory. B03 remains volatility-only. Historical results retain origin/target/error/mode/qualification evidence.
- MVP-04: wrap existing Compose/configuration/verification/recovery rather than add infrastructure. Loopback-only endpoints; immutable base-image digests and lockfiles. Production frontend serves built assets. Scripts validate config without displaying it and never overwrite .env, reset DBs or delete volumes. Real caches/forecast records remain transient and are lost on process restart; no restart-safe market-data retention is authorized. Recovery exercises use synthetic data and isolated databases only.

## Evidence and unresolved gates
Source-rights, provider publication/finality/adjustment/revision and strict historical point-in-time qualification remain unresolved. Owner UAT is separate from automated SIT. No release/acceptance claim. The prior provider counter 23 to 24 is an open historical audit finding until attributable evidence exists. Tests use synthetic data and prohibit external provider calls; deployment measurements use metadata only.

## Library evidence
Installed frontend/node_modules/lightweight-charts/dist/typings.d.ts is authoritative for 5.2.1 APIs; reviewed addSeries, native panes, autoSize, subscription disposal and createSeriesMarkers. Official references: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IChartApi and https://tradingview.github.io/lightweight-charts/tutorials/how_to/panes .
