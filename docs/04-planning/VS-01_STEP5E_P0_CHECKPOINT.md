# Step 5E P0 completion checkpoint - 2026-11-06

**Engineer P0 gate: PASS. Ready for owner UAT; owner acceptance Pending.** P1 has not started at this checkpoint. No full VS-01 acceptance.

## Architecture and provider interfaces

Provider-neutral MarketSessionProvider/MarketQuote/IntradayCandle/SessionResult extend the existing Listing/daily architecture. DhanMarketProvider reuses the verified catalog and bounded JSON/Decimal/HTTP controls. MarketSessionService coordinates quote/intraday RAM caches, freshness, missing ranges and unchanged canonical indicators. ProviderBudget globally serializes normal REST data calls at <=1/second with a local daily cap/circuit. [Design and provenance decisions](../03-design/VS-01_STEP5E_MARKET_DATA_DESIGN.md).

## Backend implementation

Authenticated local policy, quotes, intraday and sanitized-diagnostics routes. Quotes are batched once for all configured instruments, retain last valid data, and separate provider trade time from retrieval time. Previous close comes from documented net_change, corroborated by provider_close where equal; ambiguous provider_close is never assumed to be today's final close. Strict prices/volumes/schema/timestamps, bounded bodies/phase timeouts, no HTTP retry/redirect/token exchange. All five intraday intervals and range presets, partition/call/row/coverage limits, single flight/cancellation, negative caching, completed-bar warm-up/indicators and conditional per-bar volume aggregation. No real-price SQL writes or raw-response/data files. Ordinary restarts lose RAM.

Controlled RAM deployment transfer preserved all 1002 daily canonical observations and IDs exactly; legacy numeric epoch/full batch evidence not exposed by the old server remains explicitly unavailable, not fabricated. New intraday source epoch/row/request/retrieval evidence and available daily evidence survive managed transfer.

## Frontend implementation

Research dashboard displays four market cards, changes, OHLC/previous close/volume, IST trade/retrieval times, freshness/source and manual refresh. Default 15-second visible/open-session refresh; hidden tabs pause, closed/unreviewed sessions use cached data. Daily/intraday switch, all five intervals/presets/custom dates, native SVG candlestick/volume/indicator views, exact decimal tables and provisional/gap/error states. No additional chart dependency. Daily Plotly charts/formulas remain intact. Native plot coordinates are approximate only. Current-session aggregate is clearly provisional, never a final daily observation.

## Actual DhanHQ results

Preliminary probes: one batched quote, three Tata Gold 1m/5m boundary requests and two 25m/60m adapter requests; all six authenticated requests HTTP200. An initial host probe loaded no token and made zero requests; corrected by explicitly supplying the existing environment file. The 09:15 lower bound omitted the opening bar; midnight bounds returned 375 one-minute and 75 five-minute observations. All 75 start-aligned OHLCV aggregates matched; no raw values were persisted.

Deployed API test: one batched quote plus nine intraday calls, all HTTP200. Four selected previous-session datasets contain 75 bars each plus 150 earlier warm-up bars (225 observations returned per acquisition). All five intervals for Tata Gold validated. Repeated historical requests reused cache with zero provider calls. Current-session aggregate remained provisional. Real browser verification then passed four quote cards/manual refresh, candlestick/volume/timeframe/indicator display, interval switching and existing daily chart. Browser provider-call delta: one quote plus two intraday operations, within its cap. No external-origin browser requests. Daily count remains1002. Combined deployed API/browser calls at this checkpoint: two quote and eleven intraday calls; preliminary probes are recorded separately.

Provider and retrieval timestamps below are **UTC**. Quote times remain based on the explicit corroborated DD/MM/YYYY-to-IST policy. Closed-market quotes correctly show STALE/CLOSED; this is not a claim of open-session price movement.

| Instrument | API/feed | Provider HTTP | Selected observations | Latest provider timestamp UTC | Backend retrieval UTC | Freshness |
| --- | --- | --- | --- | --- | --- | --- |
| TATAGOLD | QUOTE | 200 | 1 | 2026-11-06T10:27:30Z | 2026-11-06T10:54:11.259774Z | STALE |
| TATSILV | QUOTE | 200 | 1 | 2026-11-06T10:27:35Z | 2026-11-06T10:54:11.259774Z | STALE |
| GOLDBEES | QUOTE | 200 | 1 | 2026-11-06T10:29:56Z | 2026-11-06T10:54:11.259774Z | STALE |
| SILVERBEES | QUOTE | 200 | 1 | 2026-11-06T10:29:41Z | 2026-11-06T10:54:11.259774Z | STALE |
| TATAGOLD | INTRADAY_5M | 200 | 75 | 2026-11-05T09:55:00Z | 2026-11-06T10:54:12.398054Z | FRESH |
| TATSILV | INTRADAY_5M | 200 | 75 | 2026-11-05T09:55:00Z | 2026-11-06T10:54:13.501394Z | FRESH |
| GOLDBEES | INTRADAY_5M | 200 | 75 | 2026-11-05T09:55:00Z | 2026-11-06T10:54:14.609107Z | FRESH |
| SILVERBEES | INTRADAY_5M | 200 | 75 | 2026-11-05T09:55:00Z | 2026-11-06T10:54:15.715814Z | FRESH |
| TATAGOLD | INTRADAY_1M | 200 | 375 | 2026-11-05T09:59:00Z | 2026-11-06T10:54:16.805045Z | FRESH |
| TATAGOLD | INTRADAY_15M | 200 | 25 | 2026-11-05T09:45:00Z | 2026-11-06T10:54:17.914258Z | FRESH |
| TATAGOLD | INTRADAY_25M | 200 | 15 | 2026-11-05T09:35:00Z | 2026-11-06T10:54:19.114617Z | FRESH |
| TATAGOLD | INTRADAY_60M | 200 | 7 | 2026-11-05T09:45:00Z | 2026-11-06T10:54:20.235397Z | FRESH |
| TATAGOLD | CURRENT_SESSION_5M | 200 | 75 | 2026-11-06T09:55:00Z | 2026-11-06T10:54:22.030433Z | FRESH |

Actual real-browser evidence: artifacts/step5e-p0-live-browser.json; API/HTTP summaries: artifacts/step5e-p0-live-api.json; no real screenshots/traces or raw provider payloads.

## Automated verification

**610 backend/PostgreSQL tests, 26 frontend tests and five Chromium workflows passed**, zero failures/skips in their final applicable runs. Ruff, production build and rebuilt Compose startup passed. Browser auto refresh is verified against a progressing synthetic open-session clock; actual testing after close verifies closed/stale/manual behavior. Existing four daily browser workflows remain passing. Initial new-browser failures were fixture calendar/window and locator issues; corrected, then all five passed. An initial TypeScript test-option error and lint/docstring positioning were corrected. A full-run report with an earlier browser failure is retained; the final browser XML/log records five passes, alongside final backend/frontend/build/lint results.

Tests include batched headers/identity, previous-close derivation, 401/403/429/5xx/timeouts, missing/invalid/stale quotes, cache retention, no-secret output, all intervals, strict Decimal/integral timestamps, malformed/duplicate/OHLCV rejection, missing/empty coverage, warm-up/timeframe/provisional separation, cancellation/concurrent reuse, memory limits, exact RAM transfer and rejection of float transfer prices. No normal test depends on live Dhan.

## Security findings

Fresh Windows40/Linux31 package audits and full/production npm audits report **zero known vulnerabilities/skips**. No P0 dependency changes or suppressions. Private actual-secret/URL/base64 scans of proposed sources/assets/logs found zero matches. All seven Dhan runtime values still match local configuration and are API-only; UI/DB/migration have no Dhan fields. Ports are loopback. .env ignored/untracked; example placeholders only. Application price_observations/import_rows/import_batches counts remain0. Immutable requirements/decisions and canonical math unchanged.

Nonblocking: existing Starlette/httpx/Alembic warnings; runner color warning; lazy Plotly bundle-size warning. OS-image clearance is not claimed. Private storage/backup/retention, full timestamp/adjustment/calendar/replay and independent price reconciliation qualification remain open. Regular-session template only; special/out-of-coverage sessions are not silently treated as qualified. Phase/body timeouts are explicit, not an asserted hard end-to-end DNS deadline.

## Source control and acceptance

Starting reviewed Step 5D implementation was committed locally as **aab1e9afed794d704862ece0d2ce8fbe4d8edc2b**, exact54-file scope, after fresh577/22/4 regression and secret review. No push/tag/history rewrite. P0 is a separate logical checkpoint after the successful software/live gate. Requirements-v1.0 tag unchanged. Actual owner acceptance remains Pending.

[Owner guide](../05-operations/STEP5E_UAT_GUIDE.md); [separate P0/P1 owner checklist](../05-operations/STEP5E_UAT_CHECKLIST.md). Open Research dashboard for real quotes, then Intraday research for candles/indicators; retain Daily research for historical analysis. Do not enter broker secrets in the browser or feedback.

P0's requested usable capabilities and engineer verification are satisfied. The owner's Step5E instruction authorizes proceeding to P1; this does not infer owner acceptance of P0 or full VS-01 acceptance.
