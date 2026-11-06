# Step 5E owner UAT checklist

Owner acceptance: **Pending**. Only the owner can complete these results. Engineer software/live verification is separate. Guide: [local instructions](STEP5E_UAT_GUIDE.md). Tester/date/timezone/browser: __________.

## P0

| ID | Owner test | Expected | Owner result / issue |
| --- | --- | --- | --- |
| P0-01 | Open real market snapshot | Four correct primary ETF identities, INR/source/last available prices | Pending |
| P0-02 | Review price changes | Previous-close basis visible; unavailable/ambiguous fields not invented | Pending |
| P0-03 | Review trade/retrieval times and freshness | Separate IST times; correct closed/stale/unknown states | Pending |
| P0-04 | Refresh quotes | One batched update, loading state, safe errors and retained valid data | Pending |
| P0-05 | Observe automatic quote refresh | Configured visible/open-session refresh; hidden/closed polling controlled | Pending |
| P0-06 | Select each ETF in intraday view | Real candles and volume, correct identity/source | Pending |
| P0-07 | Select all five intervals/presets/custom dates | Correct explicit timeframe and exchange-local timestamps | Pending |
| P0-08 | Apply indicators | Separate intraday SMA/EMA/RSI; correct prefix/unavailable reasons | Pending |
| P0-09 | Inspect forming/missing data and session aggregate | Provisional/incomplete labels; no fabricated candles/final close | Pending |
| P0-10 | Return to daily/history/comparisons | Existing daily inputs/formulas and common-date price-only behavior preserved | Pending |
| P0-11 | Retry a retained historical range | Cache reuse, no duplicates/unnecessary download | Pending |

## P1 (engineer verification passed; owner gate remains pending)

| ID | Owner test | Expected | Owner result / issue |
| --- | --- | --- | --- |
| P1-01 | Stream connection/subscription | Backend-only connection; correct four instruments | Pending |
| P1-02 | Normalized browser updates | Price/source/provider and reception times, connection/freshness clear | Pending |
| P1-03 | Disconnect/reconnect/fallback | Bounded recovery, restored subscriptions, cached quote and controlled polling | Pending |
| P1-04 | Reconcile provisional versus official daily | Differences/evidence recorded; official data supersedes provisional display | Pending |
| P1-05 | Verify daily indicator integrity | No provisional/stream contamination; recalculation after official update | Pending |
| P1-06 | Review failure/lifecycle controls | Disabled access honored; restart loss/retention limits understood | Pending |

Engineer verification2026-11-06: P0 API/browser PASS; P1 real after-hours feed/browser/reconciliation PASS;647 backend,29 frontend,six Chromium workflows PASS. Temporary reconnect/fallback/publication transition verified with synthetic responses. Market-open feed continuity and a real next-session publication transition remain unverified. These engineer results do not fill owner result cells.

Owner P0 disposition/date: __________. Owner P1 disposition/date: __________.

No result here approves trades, persistent licensed-data retention, a release or full VS-01 acceptance by itself.
