# DhanHQ four-ETF historical qualification diagnostic

Recorded 2 November 2026 (Asia/Calcutta). Authority: owner Step 5C authorizes implementation and **offline verification only**. Live historical requests and commits are withheld. Trace: D-14 / REQ-02-007/008/011/012/013/014/015, REQ-05-003/004 -> ADR-04/05/09, DC-01..04/09. No requirements, financial formula, portfolio, schema or app-startup change.

All four Step 5B identities are primary research instruments. This document records no personal holdings or account information. The previous two-request/alternative proposal is superseded by this four-request proposal.

## Fixed proposed requests

Exactly four proposed **POST https://api.dhan.co/v2/charts/historical** bodies, in this order:

| Order | Symbol | ISIN | securityId |
| --- | --- | --- | --- |
| 1 | TATAGOLD | INF277KA1976 | 21401 |
| 2 | TATSILV | INF277KA1984 | 21428 |
| 3 | GOLDBEES | INF204KB17I5 | 14428 |
| 4 | SILVERBEES | INF204KC1402 | 8080 |

Each JSON body combines its string securityId with:

```json
{
  "exchangeSegment": "NSE_EQ",
  "instrument": "EQUITY",
  "oi": false,
  "fromDate": "2026-10-26",
  "toDate": "2026-10-31"
}
```

The [official daily contract](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data) documents POST, JSON, access-token header, OHLCV/epoch arrays and exclusive toDate. No interval or derivative expiryCode is sent. The five expected dates are 26-30 October 2026, verified against [NSE's capital-market calendar](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf). Expected calendar sessions are not proof of identical returned ETF coverage. Detailed identifiers and historical naming caveats remain in [Step 5B](../04-planning/VS-01_STEP5B_INSTRUMENT_QUALIFICATION.md).

## Permissions: a live test remains blocked

The [general Dhan terms](https://dhan.co/terms/) restrict extraction, publication, commercialization and unauthorized copying/derived use. An active plan and an API operation do not establish an unrestricted licence. Public technical guidance about storage is not a complete API retention agreement. Account-applicable terms were not available locally for review; no account login, purchase or communication to the provider occurred.

| Use | Current disposition / clarification required |
| --- | --- |
| Four transient historical inspections | Unclear under the account-applicable API terms. Confirm that this specific private diagnostic may receive OHLCV in backend memory, discard the response and retain only non-price validation metadata. Needed before first live request. |
| Persistent PostgreSQL/CSV storage | Unverified; obtain explicit permitted scope, duration and termination/deletion conditions. Not implemented/authorized by this diagnostic. |
| Personal research / derived analytics / private charts | Technical API purpose supports analysis, but applicable rights and any non-display/derived-data restrictions remain unresolved. Do not infer unrestricted use from personal ownership of the account. |
| Local backups | Unverified; confirm permitted copies, protection, retention and deletion from backups. Existing append-only data/backup controls do not promise automatic expiry erasure. |
| Redistribution / public display / commercial sharing | No permission established or proposed. General restrictions apply; a private data subscription is not redistribution authority. |

Precise owner clarification to obtain from an authorized provider source: under the applicable individual Data API agreement, may this platform make the four specified daily requests, inspect transiently and retain only diagnostics? Separately, may it store source/derived data, display private research charts/indicators/comparisons and back up that data, for how long and subject to what deletion/termination/redistribution terms? Record agreement/permission version, authority and review date. An execution approval or CLI acknowledgment does not grant third-party rights.

[Dhan's adjustment FAQ](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/) documents daily splits/bonus adjustments. The declared basis is PROVIDER_ADJUSTED, not raw or total return. Exact ETF adjustment factors, volume treatment, distributions and revision behavior remain unresolved. There is no independent market-price reconciliation or point-in-time publication evidence.

## Backend implementation and output

Standalone `backend/app/dhan_history_diagnostic.py` reuses the unchanged seven-variable configuration and the reviewed HTTPX transport/error-code controls. It has no web route, frontend entry point, scheduler, SQL, file-output function, token exchange, portfolio function or trading endpoint. The profile diagnostic remains unchanged. All credentials remain backend-only, with no client-ID/app-key/secret in the historical request; only the token is used in its header.

The CLI fixes all four instruments, endpoint, method and dates. It accepts no arbitrary URL, symbol, security ID or date override. Config validation precedes client creation. An explicitly supplied unknown low-level symbol is rejected without HTTP and without echo. No master, profile, quote, holdings, funds or order call is made.

Output contains fixed status/issue codes, public instrument symbols, HTTP status, attempt/observation/duplicate counts, candidate ISO dates, missing/unexpected dates and validation/qualification flags. It never includes prices, volumes, raw epoch values, raw responses, provider messages, exception text, account identifiers or credentials. Provider codes are allowlisted. Library logging is temporarily disabled during transport work and restored afterward. Error paths close responses and do not retry.

## Validation contract and limitations

- UTF-8 JSON object; duplicate keys, NaN/Infinity, oversized numeric tokens, wrappers, unexpected fields and unequal/non-list OHLCV arrays fail. The six expected arrays are open/high/low/close/volume/timestamp. Optional open_interest must align and be zero for these oi=false ETF requests.
- Prices parse directly as Decimal, never via binary floats. They must be finite, positive and below the existing magnitude bound of 10^14; volume is a nonnegative signed-64-bit integer. No rounding, rescaling, performance arithmetic or database import occurs. Exact future NUMERIC precision/scale compatibility still needs ingestion qualification.
- Require low <= open/close <= high. Detect duplicate raw timestamps, duplicate candidate session dates, non-monotonic timestamps, missing dates, extra dates and count differences. Empty responses are explicit, independently evaluated per ETF; no date filling or inferred coverage.
- Integer timestamps in a bounded Unix-seconds candidate range are converted using explicit UTC -> IST (+05:30 for this fixed 2026 window). Milliseconds/unsupported values fail rather than being auto-detected or silently rescaled. **Unit, epoch origin and daily session-label semantics remain unverified** under the reviewed provider description. Candidate date checks cannot verify the contract they assume; every result carries TIMESTAMP_CONTRACT_UNVERIFIED. No publication time is invented.
- VALIDATION_PASSED_UNQUALIFIED and exit 0 mean all four structural/numeric/candidate-date checks passed. They never mean source acceptance, proven actual adjustment compatibility or verified trading-session timestamps. Source qualification remains false.

## Request and execution bounds

TLS verification enabled; environment proxy/CA overrides ignored. No redirects or retries. At most one request per mapping, at most four total, serial with one second between attempts. Authentication, provider-request errors, rate limits, service/network errors and unexpected structures stop the sequence and mark remaining instruments unattempted. HTTP-200 empty or data-quality-invalid arrays may continue so other ETFs receive independent coverage checks. No substitute request is made.

Connect/write/pool timeouts are 5 seconds; read inactivity is 10 seconds. Each body has a 262,144-byte cap, 64-observation cap and 20-second body elapsed budget checked between chunks. Compressed responses are rejected. These are not a hard total wall-clock deadline across DNS, headers and body. Limits/errors return sanitized codes. Transport control failures also report the batch as stopped. The [published Data API quota](https://dhanhq.co/docs/v2/#rate-limit) is 5/second and 100,000/day; account-wide concurrent use remains the owner's responsibility. No dependency version changed.

## Default and future commands

Safe offline default (no credential loading or transport creation):

```powershell
.\.venv\Scripts\python.exe -m backend.app.dhan_history_diagnostic
```

It returns LIVE_APPROVAL_REQUIRED, zero attempts, exit 2. Supplying only --live-approved returns SOURCE_PERMISSION_REVIEW_REQUIRED, also before config/client construction. After both acknowledgments, invalid/missing/disabled configuration still prevents requests. Ordinary application startup never imports or invokes this module and does not require Dhan credentials.

The following is a **future command, not authorized or run at this checkpoint**. It requires separately granted owner approval for the four exact requests and an adequate source-use review:

```powershell
docker compose exec -T -e DHAN_DATA_API_ENABLED=true api uv run --frozen --no-dev python -m app.dhan_history_diagnostic --live-approved --permissions-reviewed
```

The override affects only the exec process; `.env` and normal service remain false. The flags acknowledge reviewed authority; they cannot create it or prove a licence. Use the existing configured token, replace expired credentials manually if needed, and never put secrets in command arguments or URLs. There is no automatic renewal/retry. Permission evidence should stay outside credentials and any sensitive rights agreement outside Git.

## Comparison readiness

The pairs are TATAGOLD/GOLDBEES and TATSILV/SILVERBEES. A summary-only readiness check requires distinct approved listings of the same metal, INR currency, matching documented adjusted-basis reference, identical expected candidate dates and passing individual checks. It rejects incompatible/failed/empty inputs. It computes no price changes, rankings, indicators or investment-performance conclusions.

Even compatible mocked inputs return BLOCKED_SOURCE_QUALIFICATION and qualified_for_comparison=false because source-use permission, timestamp contract, detailed adjustment method and independent reconciliation remain open. Actual data was not retrieved; actual coverage/compatibility cannot be asserted. Five bars cannot satisfy longer-lookback research or full T-03/replay/VS-01 acceptance. See [Step 5C checkpoint](../04-planning/VS-01_STEP5C_HISTORICAL_DIAGNOSTIC_CHECKPOINT.md) for execution evidence and exact proposed files.
