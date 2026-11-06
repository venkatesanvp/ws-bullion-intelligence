# Step 5E local market-research UAT

Open http://127.0.0.1:5173 and unlock privately with LOCAL_APP_TOKEN from the ignored local .env. Never enter Dhan access tokens/API secrets in the browser or feedback. Select a primary ETF, the real Dhan transient source, and Provider adjusted for daily history.

## P0 quotes and intraday

In Research dashboard, Latest available ETF quotes shows all four instruments, price/change, session OHLC, previous close, volume, provider last-trade time, successful retrieval time, source and freshness. Refresh quotes performs one batched backend operation. Default active/visible regular-session refresh is 15 seconds; hidden tabs pause, and closed/unreviewed sessions do not continuously poll Dhan. STALE plus CLOSED can be the correct latest available after-hours quote, not an authentication failure. Last-trade time is not snapshot-generation time, and quotes are not final daily closes.

Choose Intraday research. Select 1, 5, 15, 25 or 60 minutes; choose Current session, Previous trading session, Last five sessions, Last 30 calendar days or Custom dates; then Apply intraday range. Candlesticks, volume, exact values and IST timestamps appear. A chart displays at most the latest 500 candles with an explicit count; the exact table pages all returned rows. Longer ranges can hit explicit request/analytics/memory limits; choose a narrower range or larger interval.

SMA/EMA/Wilder RSI lookbacks explicitly apply to the selected minute timeframe. Earlier completed bars are retrieved/reused for warm-up; insufficient/gapped history stays unavailable. Forming bars are visible as provisional and excluded from completed-bar indicators. Current-session aggregation remains PROVISIONAL - INTRADAY AGGREGATED, separate from official daily history. Refresh intraday is controlled revalidation. Return to Daily research for unchanged daily charts/indicators. ETF comparisons remain price-only.

Engineer real checks on 2026-11-06: all four quotes, 75 selected previous-session five-minute candles per ETF plus 150 warm-up bars, all five intervals for Tata Gold, current-session provisional aggregation, native chart rendering and daily compatibility passed. Tests after market close correctly show CLOSED/STALE quotes; open-session auto refresh is verified with a controlled synthetic browser clock. This is not owner acceptance.

## Configuration and lifecycle

Master MARKET_DATA_ENABLED and independent MARKET_QUOTES_ENABLED/MARKET_INTRADAY_ENABLED default false in .env.example/Compose and are true only in the local ignored .env. Quote refresh default15 seconds; staleness45; current intraday refresh60; partition7 calendar days (maximum90); calls8/operation; rows100000; shared local provider daily budget10000. Normal HTTP operations are globally serialized at <=1/second with failure cooldown; no HTTP retry. Existing credential fields are unchanged. To disable, edit nonsecret gates and recreate only API; this loses RAM data. Rotate credentials privately using the existing Dhan configuration guide; no automatic renewal.

All real data remains transient backend memory. No permanent provider-price storage/backups are approved. Restart loses cache; controlled deployment handoff preserves canonical values and available evidence in RAM only. Legacy epoch/batch metadata gaps, source/session/adjustment/replay qualification and persistent rights remain visible limitations.

## P1 UAT

P1 is now deployed for owner testing. See the separate [P1 checkpoint](../04-planning/VS-01_STEP5E_P1_CHECKPOINT.md). With the Research dashboard visible during reviewed market hours, one shared read-only feed connects automatically. Outside those hours, select Connect / retry feed for a snapshot. Verify LIVE_STREAM on the four cards, source/trade/reception times, connection state and freshness. A connected feed after hours can correctly show STALE prices. Timestamp interpretation remains explicitly provisional; see Quote interpretation. Disconnect feed preserves the last quotes and restores controlled polling. Retry is explicit after exhaustion/auth/rate errors; replace expired credentials privately, never in the browser. No token exchange occurs.

MARKET_STREAM_ENABLED is an independent backend-only switch, false in committed examples/Compose and enabled only in the ignored local .env under standing read-only authority. Master MARKET_DATA_ENABLED must also be true. Feed limits: one connection, at most100 verified catalog instruments, three reconnects,16 local viewers,4096-byte frames and bounded receive queues; idle feeds stop after30seconds. Reconnects restore subscriptions. Hidden tabs stop local delivery. Network/provider outages retain last valid quotes; STALE/UNAVAILABLE remain visible. Mock tests cover temporary disconnect/recovery/exhaustion and token errors; an actual market-open interruption was not induced against Dhan.

Daily / intraday reconciliation lets you select a reviewed session and Reconcile selected session. For2026-11-05 all four cached official candles supersede75 intraday bars, with close/volume differences flagged for review. These differences are not silently accepted as adjustment-compatible. For2026-11-06, official publication is WAITING_T_MINUS_ONE. While a waiting record is visible, publication checks run at most once/minute and use existing daily negative-cache/backoff; no scheduler or same-day daily fabrication. A final observation refreshes affected charts/indicators, which continue using daily-only inputs. The ledger and all prices are RAM-only and are lost on ordinary restart. Finality is not source acceptance.

No trading, GTT, account/holdings/funds or portfolio transaction capability is part of either phase.

Record owner results in [the separate checklist](STEP5E_UAT_CHECKLIST.md). Include selected ETF/range/timeframe and sanitized error codes; exclude credentials, account details, exported price data and real-data screenshots. Engineer checks and automated tests do not sign owner acceptance.
