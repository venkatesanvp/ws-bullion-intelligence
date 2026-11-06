# Step 5D.3 — owner user acceptance checklist

**Owner acceptance status: PENDING.** Only the application owner may complete these results. Developer automated tests and engineer-operated real-data browser verification are separate evidence, not owner acceptance.

Application: http://127.0.0.1:5173. Guide: [Real-data UAT instructions](REAL_DATA_UAT_USER_GUIDE.md).

Data as of 2026-11-06 engineer verification: real DhanHQ; 250 observations per ETF for 2025-11-03 through 2026-11-05. SILVERBEES also has two earlier calendar-unassessed observations (252 overall). The November 2-6 range has four available sessions and November 6 provider-pending. Source: transient RAM, Provider adjusted; no live-price PostgreSQL persistence. Standing read-only retrieval is enabled locally; restart loses RAM and authorized views can reacquire it.

Tester: __________  Date/time/timezone: __________  Browser/viewport: __________

Use **Pass / Fail / Pending** in Result. Keep observations and enhancement requests distinct. Do not record credentials, account/portfolio details, screenshots of secrets, or raw provider prices in this file or feedback.

| ID | Owner test | Expected behavior | Result | Observation / issue reference | Enhancement request |
| --- | --- | --- | --- | --- | --- |
| UAT-01 | Open and unlock application | Local workspace opens with LOCAL_APP_TOKEN; clear error for incorrect token | Pending | | |
| UAT-02 | Select each of the four primary ETFs | TATAGOLD, TATSILV, GOLDBEES, SILVERBEES available; correct names/metal/INR | Pending | | |
| UAT-03 | Select real DhanHQ source and Provider adjusted basis | Source is visibly real, transient and not fully qualified | Pending | | |
| UAT-04 | Inspect each real historical chart | Nonempty chart and exact table; 250 observations in the one-year window; 2025-11-03 to 2026-11-05 | Pending | | |
| UAT-05 | Change research range and Apply | Chart/table update to requested available dates; no fabricated sessions | Pending | | |
| UAT-06 | Show SMA 20, 50 and 200 successively | Selected overlay/table values display; warm-up stays unavailable | Pending | | |
| UAT-07 | Configure EMA (e.g. 37) | Explicit period applies and EMA appears; insufficient prefix stays unavailable | Pending | | |
| UAT-08 | Show Wilder RSI 14 | Separate RSI panel and exact table values; initial warm-up unavailable | Pending | | |
| UAT-09 | Compare TATAGOLD/GOLDBEES | Common-date chart/table, 250 common observations in the one-year window, price-only disclosure | Pending | | |
| UAT-10 | Compare TATSILV/SILVERBEES | Common-date chart/table, 250 common observations in the one-year window, price-only disclosure | Pending | | |
| UAT-11 | Inspect source/coverage/latest/gap information | Latest date 2026-11-05; requested 2026-11-06 pending; source and calendar limitations visible | Pending | | |
| UAT-12 | Use exact values table / Show more research rows | Retained observations can be paginated without another download | Pending | | |
| UAT-13 | Enter an invalid lookback or reverse date range | Understandable validation error, no invented indicator values | Pending | | |
| UAT-14 | Navigate research/history/comparisons | Navigation/layout/table/chart usable at chosen viewport | Pending | | |
| UAT-15 | Review lifecycle and stop instructions | Understand that restart clears RAM; authorized provider views can reacquire; active-view polling defaults off | Pending | | |

| UAT-16 | Apply an eligible unloaded range | Loading shown; missing prices validated/merged and history refreshed without a script or new approval | Pending | | |
| UAT-17 | Apply the same fresh range again | Existing observations reused, no duplicate rows/download | Pending | | |
| UAT-18 | Show indicators on a short visible range | Required earlier prefix used/retrieved; insufficient history never filled | Pending | | |
| UAT-19 | Review partial/error feedback | Pending dates distinguished from holidays; safe errors; valid cached rows retained | Pending | | |
| UAT-20 | Review explicit provider refresh | Controlled revalidation respects budgets/publication and source warnings | Pending | | |

Owner disposition: **Pending / Accepted with recorded limitations / Changes requested**: __________

Open issue references: __________

Accepted limitations / required changes: __________

Owner confirmation/date: __________

This form does not approve a release, trading, portfolio execution, permanent data retention or full VS-01 acceptance by itself.


### Owner-reported range issue - 6 November 2026

Original: SILVERBEES November 2-6 appeared inactive/no history because the old cache ended October 30 and Apply range only filtered it. Step 5D.4 now performs coverage checking and authorized acquisition automatically. Engineer real-browser verification passed: four newly available November sessions, current day pending, a separate previously unloaded two-session range fetched by Apply, repeat reuse, updated charts/indicators and both comparisons. This does not record an owner pass. **Owner retest/acceptance remain Pending.**
