# Market-data operating policy - Step 5D.4

Owner authorization: 6 November 2026. Implementation policy, not an amendment of the requirements baseline or Decision Register.

## Standing authority and boundaries

The owner's Step 5D.4 instruction grants standing read-only DhanHQ market-data authority until revoked. It supersedes earlier per-batch approval requirements for normal configured retrieval, missing ranges, revalidation, controlled caching, development/integration tests and necessary instrument-master lookup. The old fixed diagnostic budget is historical; when normal retrieval is enabled its one-shot application loader refuses use and directs callers to Apply range.

This does not authorize orders, trading/GTT, holdings, funds, account changes, token exchange/renewal, public redistribution or contractually forbidden retention. No such functionality is introduced. Provider credentials remain API-only. The local owner grants operation authority, not an exchange/provider licence.

## Configuration

Keep the seven existing DHAN_* credential/settings variables unchanged. Historical access requires the configured access token; developer key/secret are never sent to the historical endpoint. No token renewal occurs. Missing or invalid credentials fail only retrieval; ordinary startup/cache inspection remains available. To rotate an expired token, edit DHAN_ACCESS_TOKEN privately in .env, then recreate only the API to load its new environment (this clears RAM); follow [credential rotation instructions](DHANHQ_LOCAL_CONFIGURATION.md). No credential value belongs in a command, browser field or feedback.

`MARKET_DATA_ENABLED=false` is the committed conservative default. The existing ignored local `.env` has **MARKET_DATA_ENABLED=true**, added under the standing grant without changing authentication variables. This is the normal read-only operating gate. `DHAN_DATA_API_ENABLED=false` remains unchanged for legacy diagnostic commands. Normal enabled retrieval builds a request-local Dhan configuration from existing backend credentials; it does not change the environment or authentication configuration. Set MARKET_DATA_ENABLED=false and recreate API to revoke live access; stopping/recreating API loses its RAM observations.

All settings are scoped to the Compose API service only:

| Setting | Default | Meaning |
| --- | --- | --- |
| MARKET_DATA_AUTO_MISSING | true | Permit missing/stale retrieval; false requires explicit provider refresh |
| MARKET_DATA_MAX_REQUESTS | 8 | Maximum calls per operation; configurable 1-32 |
| MARKET_DATA_PARTITION_DAYS | 366 | Inclusive days per adapter call; 1-366 |
| MARKET_DATA_TIMEOUT_SECONDS | 10 | HTTP phase timeout; 1-30 seconds; existing 20-second streamed-body guard and 256 KiB response bound also apply |
| MARKET_DATA_FRESHNESS_SECONDS | 604800 | Historical observations revalidated after seven days |
| MARKET_DATA_EMPTY_RETRY_SECONDS | 3600 | Retry eligibility for successful but missing/empty sessions |
| MARKET_DATA_FAILURE_BACKOFF_SECONDS | 300 | Failure/rejection cooldown and provider failure circuit pause |
| MARKET_DATA_MIN_INTERVAL_SECONDS | 1 | Provider calls serialized; minimum configurable 0.2 seconds |
| MARKET_DATA_DAILY_BUDGET | 1000 | Local process daily call budget; maximum 100000 |
| MARKET_DATA_MAX_ROWS | 100000 | Global RAM observation cap; overflow rejected atomically |
| MARKET_DATA_MAX_COVERAGE_DAYS | 100000 | Coverage metadata capacity |
| MARKET_DATA_AUTO_REFRESH_SECONDS | 0 | Active-view polling off; if enabled, minimum 60 seconds; hidden/unmounted views do not poll |

One API process/worker provides global serialization/single flight, without deployment infrastructure. No background scheduler. Daily budget and coverage/backoff are RAM-only; account usage by other applications is unknown. These controls do not reserve account-wide quota. Dhan documents Data API limits of 5 calls/second and 100000/day; HTTP 429 stops the operation and activates backoff. Do not add API workers or bypass limits to increase throughput.

## Acquisition, dates and coverage

Authenticated local `POST /api/v1/market-data/ensure` takes configured instrument/source UUIDs, optional inclusive start/end, bounded warmup_bars and explicit refresh. It resolves the full exchange/symbol/ISIN/metal/currency identity against adapter-verified listings. Symbols or arbitrary security IDs are never accepted as sufficient identity. The workflow handles any verified adapter catalog; it is not restricted to a four-item loop. Currently registered primary mappings remain TATAGOLD/21401, TATSILV/21428, GOLDBEES/14428 and SILVERBEES/8080, NSE_EQ/EQUITY/INR. Adding instruments requires authoritative listing/security-ID verification before supplying catalog entries to the adapter. No unverified UI mapping is admitted.

Per date, coverage distinguishes AVAILABLE, NOT_REQUESTED, ATTEMPTED_EMPTY, NON_TRADING, PROVIDER_PENDING, FAILED, REJECTED and OUTSIDE_VERIFIED_HISTORY. Confirmed inception evidence may exclude an earlier range; unknown inception is not inferred from the first response. Empty/missing data never establishes a holiday or inception.

Available observations are reused until stale. Missing eligible dates are grouped without bridging an already available session, partitioned and capped. Only confirmed calendar closures can be bridged. The packaged reviewed NSE calendar covers 2025-11-02 through 2026-11-06, preserving the previously reviewed election closure and Budget Sunday exception. Outside that scope, calendar status is UNASSESSED; even weekends are not asserted closed. Unknown calendar does not silently block transient retrieval; persistent ingestion retains its strict reviewed-calendar requirement.

The adapter alone translates inclusive end to Dhan's documented exclusive toDate. No future/current-day request is made under the T-1 daily-publication policy. Latest completed-session candidate uses a conservative 16:00 IST cutoff; latest provider-eligible session is separately bounded by the previous exchange-local date. Both remain candidates outside reviewed calendar coverage. T-1 is not a publication SLA, so an eligible session can still be absent.

No automatic retries, redirects, fallback calls or indefinite backfill. Provider/auth/entitlement/rate/network errors are sanitized. A canceled request stops before the next call and discards an in-flight result after its bounded transport completes. A later user/view operation can therefore need another call for those still-uncovered dates; this is not an automatic retry. Normal concurrent overlapping requests wait and replan against the latest cache. Explicit simultaneous refreshes coalesce when overlapping a just-completed refresh.

## Validation, merge and retention

The existing daily adapter, canonical validator, Decimal model and transient repository are reused. Full identity, strict bounded numeric fields, integral volume, coherent OHLC, provisional epoch-to-IST mapping, array schema, duplicate/date-range and calendar checks run before publication. No rounding/truncation or imputation. Original new-row epoch/row/batch evidence remains in RAM. Reviewed-calendar absence is explicit and permitted only for transient validation; persistent qualification gates are unchanged.

Merges publish sorted immutable dataset snapshots under a lock; each API read uses one dataset/revision snapshot. Identical observations reuse their IDs. Conflicts require an explicit refresh or configured stale revalidation; validated replacements get a new revision/batch. Provenance is bounded by 2048 batch records per series and a global observation-evidence capacity of twice the row cap. Capacity failure preserves existing rows. This is not a durable point-in-time revision archive or replay qualification.

Live observations remain RAM-only: no PostgreSQL, raw-response files, hidden disk cache or data backup. Applicable private storage/backup/retention rights remain unresolved after review of public terms; do not infer them from subscription or public availability. Existing qualified persistent ingestion remains gated pending evidence. Browser API responses use no-store; real verification records only sanitized counts/dates/statuses, no screenshots/traces or price exports.

A one-time authenticated canonical-view handoff preserved the pre-existing 984 rows across this deployment without a market-data file/re-download. It seals before acquisition and cannot append/replace an active cache. All exposed canonical fields, observation IDs, batch IDs and batch evidence were compared exactly. The old API did not expose original numeric provider epochs; migrated rows explicitly disclose ORIGINAL_NUMERIC_EPOCH_NOT_EXPORTED. No epochs were reconstructed. New adapter acquisitions preserve their actual numeric epoch provenance. This handoff is not a persistent recovery solution; ordinary restarts lose RAM data and authorized views can reacquire it.

## UI and analytics

History Apply range, research settings and comparisons ensure coverage before existing read/calculation APIs. Opening a provider view can also refresh missing history. Loading/reuse/updated/partial/error messages appear automatically; errors preserve available cached observations. Refresh from provider explicitly revalidates a selected range. Draft dates are separate from applied pagination dates.

Indicators request a bounded observed-bar warm-up prefix and then use the unchanged canonical Decimal SMA/EMA/Wilder RSI engines. Known missing expected prefix sessions prevent a complete-warmup claim; actual indicator availability and discontinuity rules remain authoritative. The cache's earliest retained row is not asserted to be fund inception. Comparisons use the existing common-date, price-only path and never imply total return or adjustment equivalence.

## Evidence and unresolved qualification

Official sources reviewed 2026-11-06: [historical API](https://dhanhq.co/docs/v2/historical-data/), [rate limits](https://dhanhq.co/docs/v2/#rate-limit), [T-1 publication](https://dhan.co/support/platforms/dhanhq-api/why-am-i-not-receiving-the-latest-day-s-data-from-the-daily-historical-data-api/), [NSE holidays](https://www.nseindia.com/resources/exchange-communication-holidays), [Dhan terms](https://dhan.co/terms/). No external terms acceptance/account setup was performed. Existing adjustment FAQ is recorded in adapter provenance.

Source timestamp/session contract, precise adjustment methodology/compatibility, independent price/volume reconciliation, point-in-time/replay evidence, persistent-use rights and owner acceptance remain open. Matching dates or successful charts do not close SQ-01/T-03 or full VS-01 acceptance. See the Step 5D.4 checkpoint and owner UAT guide.
