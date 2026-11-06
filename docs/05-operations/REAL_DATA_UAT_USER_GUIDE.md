# Real-data local user guide - Step 5D.4

Open **http://127.0.0.1:5173**. The running application uses real DhanHQ ETF observations. Owner acceptance remains **Pending**. The [standing operating policy](MARKET_DATA_OPERATING_POLICY.md) supersedes old per-batch permission/diagnostic instructions.

## Open and unlock

The local services are running. Do not restart the backend merely to test. For a stopped installation, use `docker compose up -d --wait` from the repository root. Startup registers verified instruments but makes no provider request. Opening a selected provider view or applying a range may retrieve missing data under standing authority.

Enter LOCAL_APP_TOKEN privately from the ignored local `.env` in **Local application token**, then choose **Open workspace**. This is the local application token; never enter Dhan access tokens, API keys or API secrets in the browser or feedback.

Select TATAGOLD, TATSILV, GOLDBEES or SILVERBEES in **ETF listing**, the **DhanHQ - real historical data - transient memory** source, and **Provider adjusted** basis. The source remains TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED. Prices are INR per ETF unit, market prices rather than NAV, and are not total return.

## Apply a range

1. Open **History & quality** and select **SILVERBEES**.
2. Set **From** `2026-11-02` and **Through** `2026-11-06`.
3. Choose **Apply range**. Coverage is checked; eligible missing/stale observations are downloaded, validated and merged automatically. No diagnostic command or additional request approval is needed.
4. Read the retrieval message and actual available dates/count. On the 6 November verification, all four ETFs had the four sessions November 2, 3, 4 and 5. November 6 remained provider-pending under T-1 daily publication, not a fabricated candle or a declared holiday.
5. Apply the same range again. Fresh observations are reused. **Refresh from provider** explicitly revalidates eligible dates; it cannot override publication limits, authentication, entitlement, cooldown or request budgets.

Partial coverage stays visible. Empty provider responses are not labelled holidays. A provider failure leaves cached valid observations available. Expired-token errors require replacing the token locally; the app performs no renewal. Do not post credentials when reporting an error.

As of engineer verification, the retained one-year window contains **250 observations per ETF**, 2025-11-03 through 2026-11-05. SILVERBEES additionally has two earlier observations (2025-10-30 and 2025-10-31) acquired by an explicit Apply range test, giving 252 in its entire cache. Those earlier dates are outside the packaged reviewed-calendar coverage and remain calendar-unassessed. Counts will change when later eligible dates/history are requested.

## Charts and indicators

Open **Research dashboard**, choose visible dates and **Apply research settings**. Missing eligible prices are acquired before the chart and existing indicator APIs run. Set visible dates to November 2-6 to use the retained earlier prefix without requesting an unnecessarily earlier start for this UAT.

Enable SMA and apply explicit lookbacks **20**, **50**, then **200** (one SMA at a time). Enable EMA with **37**, and Wilder RSI with **14**. RSI has a separate scale. Required warm-up history is planned under the same bounded policy; incomplete prefix/known breaks remain unavailable rather than being filled. EMA/RSI formulas and observed-bar semantics are unchanged. Blank dates select available/default history; requesting indicators at its earliest edge can legitimately retrieve an earlier warm-up prefix.

Charts use approximate display coordinates; exact server Decimal strings remain in tables. Source timestamps, adjustment methods and point-in-time availability remain provisionally qualified. Declarations of adequate minimum prefix coverage do not independently qualify source timestamps or fund-inception history.

## Comparisons

Open **ETF comparisons**. Choose TATAGOLD/GOLDBEES, then TATSILV/SILVERBEES; use the same Dhan transient source and Provider adjusted basis for both series. Select November 2-6 and **Compare prices**. Both pairs had **four common dates** in the real verification. The one-year window through November 5 has 250 common observations.

Missing ranges are ensured sequentially before comparing. Only common observed dates are used; no forward fill. These are **price-only comparisons**, not total return, adjustment-equivalence proof, recommendations or predictions.

## Operating limits and lifecycle

The [operating policy](MARKET_DATA_OPERATING_POLICY.md) documents request/time/rate/freshness/empty/error/memory bounds. MARKET_DATA_ENABLED is enabled only in the existing local environment; the committed example defaults false. Optional active-view automatic polling defaults off. No background scheduler, token renewal, portfolio/account access or trading exists.

**All real observations remain in backend RAM, with zero live-price PostgreSQL writes or data files. Backend stop/restart loses the cache.** A later view can reacquire allowed data using the configured standing policy; no per-request permission is required. Private persistent-storage/backup/retention rights remain unresolved. The one-time deployment handoff preserved original canonical rows and exposed evidence, but original numeric epochs were not exposed by the old API; this limitation remains visible. New downloads retain actual adapter timestamp provenance.

To stop only the frontend while keeping the cache, use `docker compose stop ui`, then `docker compose start ui`. `docker compose stop` also stops the backend and clears its RAM. Never use volume-deletion commands for UAT.

## Owner feedback

Complete [the owner checklist](VS-01_STEP5D3_UAT_CHECKLIST.md). Engineer-operated tests do not mark owner tests passed or declare full VS-01 acceptance. Report the screen, symbol/source/basis/range, expected versus actual behavior and sanitized error code. Exclude credentials, personal account/portfolio details, screenshots containing licensed prices and exported raw data.

The original November 6 Apply range/no-history issue is implemented and engineer-verified through automatic retrieval. **Owner retest remains Pending.**
