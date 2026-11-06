# VS-01 Step 5D.1 — DhanHQ daily provider adapter checkpoint

Recorded: 2 November 2026. Parent: `ef0a7c460ec82ce3797da37cded883ec82553871`.
**Offline implementation checkpoint for review. Not committed; no full VS-01 acceptance.**

## Authority, architecture and traceability

The owner's Step 5D.1 instruction explicitly authorizes a production-oriented, backend-only adapter and offline verification. It supplements earlier CSV-first descriptions in ADR-04/DC-02/CMP-03 without changing D-01..16, REQ-BL-1.0, the requirements tag, or source qualification. Trace: D-14; REQ-02-007/008/009/011/012/013/015, REQ-05-003/004; ADR-04/05/08/09/10; DC-02/03/04/09; CMP-03/04. Open parent requirement classifications are not promoted by scoped implementation authority.

The existing modular monolith, SQL schema, immutable observation identity, CSV transaction/idempotency path, deterministic analytics and React dashboard remain intact. No provider boundary existed as a reusable typed runtime interface: CSV produced dictionaries matching DC-02 and the history diagnostic produced sanitized summaries. The new interface is an in-memory acquisition boundary, not a second repository or import service. Existing `DataSource.source_kind=USER_CSV` remains unchanged; an adapter result cannot be sent automatically to the existing import transaction.

### Reused and extracted components

- `daily_values.price` is the unchanged pure validator extracted from CSV ingestion: finite positive Decimal, below 10^14, at most ten decimal places. `ingestion.price` remains import-compatible. No analytics formula or rounding convention changes.
- `dhan_history_contract` extracts the existing four verified mappings, strict duplicate-key JSON decoder, direct Decimal numeric parsing, integral-value validator/counters, numeric bounds, explicit candidate Unix-seconds/IST conversion and evidence/limitation constants. Existing diagnostic policy and fixed five-session window remain unchanged.
- `dhan_http` extracts the existing fixed TLS/no-proxy/no-retry transport, timeouts, configuration gate and allowlisted provider errors. Existing diagnostic imports retain their public names. The adapter adds request-thread log filtering, restored after the operation; other threads' logging remains available. Configure logging handlers before acquisition. Existing standalone CLI suppression retains its prior behavior.
- Existing `CalendarProfile`, `digest` and canonical serialization are reused. No SDK, dependency, lock, migration, Compose, credential or frontend changes.

### New interface and implementation

`market_data.DailyMarketDataProvider` defines provider identity, public canonical listing discovery and one daily retrieval. `DailyRequest` carries full listing identity (exchange/symbol/ISIN/metal/currency), inclusive start/end dates and an optional existing calendar profile. There are no Dhan fields or credentials in this request or the analytics/dashboard. Results contain typed canonical observations, shared batch/row provenance, validation and fixed structured failures. `safe_summary()` deliberately excludes observation values and source timestamps.

`DhanDailyProvider` maps only the four approved primary XNSE/INR listings to provider-specific bodies internally:

| Symbol | ISIN | Security ID | Metal |
| --- | --- | --- | --- |
| TATAGOLD | INF277KA1976 | 21401 | GOLD |
| TATSILV | INF277KA1984 | 21428 | SILVER |
| GOLDBEES | INF204KB17I5 | 14428 | GOLD |
| SILVERBEES | INF204KC1402 | 8080 | SILVER |

Identity evidence remains the [Step 5B qualification record](VS-01_STEP5B_INSTRUMENT_QUALIFICATION.md); no new instrument-master fetch occurred. All four remain primary. The adapter does not refresh or guess identifiers.

One operation is fixed to `POST https://api.dhan.co/v2/charts/historical`, `exchangeSegment=NSE_EQ`, `instrument=EQUITY`, `oi=false`, mapped `securityId`, inclusive `fromDate` and exclusive `toDate=end+1 day`. These semantics and header authentication follow the [official daily endpoint](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data). The protocol matches the application's inclusive date boundary; it does not expose Dhan's wire-date convention to research consumers.

Technical limits: at most 366 calendar days/request and 366 observations; dates 2000-01-01 through 2099-12-31; 256 KiB response; numeric JSON tokens at most 128 characters. These are local resource/sanity controls, not claims about ETF inception, provider history limits or exchange completeness. No automatic chunking, pagination, fallback, retries or scheduling. Each invocation makes at most one request. Provider-wide rate budgeting remains for separately authorized orchestration; this increment performs no collection loop.

## Canonical mapping, validation and provenance

OHLC parse directly as Decimal. Integral integer/decimal volume and timestamps are accepted only when finite, mathematically integral and within the existing bounds. Bool/string/null, fractional integer-only values, non-finite values, millisecond-shaped/out-of-range timestamps, nonpositive/excess-scale prices, malformed/unexpected/alignment-invalid arrays, nonzero optional OI and incoherent OHLC are rejected. No rounding, truncation, price repair, date repair or unit autodetection. Any hard row failure returns no normalized observations; safe counts/candidate dates/issues remain available.

The observation's canonical values exactly match the existing CSV candidate keys and Decimal values: trading_date, daily interval, price basis, OHLC, integer volume, SESSION_DATE precision, null event_time and null provider_published_at. Canonical hash equivalence is tested against the actual CSV parser, including ten-place input precision. Source timestamp numeric value/encoding and original one-based response row are retained only in memory as observation provenance, not assigned to event/publication time. Out-of-order valid rows are explicitly reported and ordered chronologically while retaining original row numbers. Duplicate timestamps/session dates reject the batch rather than choosing a winner.

Every successful/empty batch records provider/contract version, full listing, provider ID/segment/instrument, inclusive requested range and provider-exclusive end, UTC retrieval time, adjusted market-price basis, adjustment evidence, candidate timestamp policy, timezone, supplied calendar evidence/version, validation status and limitations. Each observation references that immutable batch plus its row/timestamp evidence. Failure results contain only allowlisted codes/status and safe validation summaries; no raw body, exception text, request object or credential. Retrieval time is not ingestion time or proof of historical availability.

Timestamp policy `UNIX_SECONDS_IST_CANDIDATE_V1` uses exact integer timedelta arithmetic and explicit Asia/Kolkata UTC+05:30 for the supported modern-date range. The [API documentation](https://dhanhq.co/docs/v2/historical-data/) labels timestamps int/Epoch and supplies seconds-compatible examples; it does not explicitly settle the complete unit/session convention. Step 5C.1 live evidence was limited to 26–30 October 2026 for these four ETFs. Numeric parsing, calendar conversion and evidence of the actual exchange session remain distinct. `timestamp_semantics_verified=false` and a limitation identifying the observed window accompany every result, including other requested dates. No current live test occurred.

Only a supplied, fully covering/revalidated `CalendarProfile` supports missing/non-trading-session assessment, against **candidate** dates. Missing observations remain explicit gaps and are not filled. Without a calendar, missing_sessions is null/UNASSESSED, even if every timestamp converts. Invalid/unmapped timestamps produce DATE_COVERAGE_UNDETERMINED and cannot prove missing sessions or absence of duplicates. Supplied calendar evidence is recorded, not automatically independently qualified.

Prices are exchange-traded ETF market candles, not NAV. The [official adjustment FAQ](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/) supports PROVIDER_ADJUSTED for splits/bonuses. Exact ETF factor history, distribution treatment, volume adjustment, correction policy and total-return comparability remain unverified. All results stay UNVERIFIED and UNVERIFIED_FOR_REPLAY; matching dates do not grant research/source acceptance or adjustment compatibility.

## Security and execution boundary

Both validated `DHAN_DATA_API_ENABLED=true` process configuration and `request_approved=True` are required before transport construction. This flag is an explicit caller authorization acknowledgment, not a licence grant. Normal `.env` remains false and unchanged. Missing credentials/disabled configuration do not affect application startup. The provider is not imported by main, analytics, comparison or frontend; there is no route, startup hook, runner or public activation command added.

Credentials use the existing backend SecretStr configuration. Only access-token is sent, only in the header of the fixed HTTPS endpoint. App key/secret/client ID are neither exchanged nor passed to historical requests. TLS verification stays on, environment proxy/CA overrides and redirects are disabled, transport retries are zero. Connect/write/pool timeout is five seconds; read inactivity timeout ten seconds; streamed-body elapsed budget twenty seconds checked between chunks (not a hard total deadline). The bounded one-request operation closes response/client/transport. Known auth, expiry, entitlement, rate, malformed format, service and network errors return fixed classifications; unknown provider messages/codes are discarded.

No Dhan API call, market-price download, raw response persistence, PostgreSQL write from Dhan, scheduled acquisition, token exchange, holdings/balance/portfolio access, order/GTT/trading or broker execution occurred. Only public documentation/advisory checks and local mocked/test runtime activity were used. All new OHLCV and token fixtures are explicitly synthetic; they are not evidence of real source quality.

## Verification

Final full execution on completed source: **506 backend/PostgreSQL tests, 16 frontend tests and 3 Chromium workflows passed; zero failures, errors or skips.** This includes 107 new provider unit/mocked-integration cases. Existing diagnostic/CSV compatibility suites pass after shared extraction. Python lint and TypeScript/production build pass. PostgreSQL tests use only the disposable local `bullion_test` service; no cleanup targets the application database.

| Check | Actual result | Ignored local evidence |
| --- | --- | --- |
| Complete local regression | 506 / 16 / 3 tests passed; lint and production build passed | `artifacts/step5d1-regression-final.log`, `verification.json`, `backend-tests.xml`, `browser-tests.xml` |
| Final Compose build/start | Passed; API/PostgreSQL healthy; UI running and HTTP 200; disposable test DB stopped | `artifacts/step5d1-compose-final.log` |
| Linux isolated adapter probe | All four mappings pass with synthetic OHLCV/token; default-disabled zero attempts; container network none and socket guard | `artifacts/step5d1-linux-offline-probe.log` |
| Windows Python audit | 40 installed packages; 0 vulnerabilities, 0 skipped | `artifacts/step5d1-audit-windows-python.json` |
| Actual Linux Python audit | 31 installed packages; 0 vulnerabilities, 0 skipped | `artifacts/step5d1-audit-linux-python.json` |
| Full / production npm audit | 0 findings in each | `artifacts/step5d1-audit-frontend-full.json`, `step5d1-audit-frontend-production.json` |
| Offline credential-pattern scan | Pinned detect-secrets 1.5.0; no findings; provider verification disabled | `artifacts/step5d1-secret-pattern-scan.json` |
| Private credential/runtime/Git verification | 30 checks passed; 36 inspected source/build/evidence files plus runtime logs/local responses; no actual credential exposure; all seven Dhan settings API-only and false gate; container source matches review | `artifacts/step5d1-runtime-security-verification.json` |

All dependency scans use current installed/locked packages; pip-audit is isolated at 2.9.0. No package upgrade, advisory suppression or new runtime dependency. OS-image vulnerability scanning is not claimed. `.env` is ignored/untracked; no files are staged; only the 12 listed changes exist. Requirements documents still exactly match `requirements-v1.0`; its annotated object and target and the complete existing tag set are unchanged. HEAD remains the parent commit.

Initial checks found an incorrectly eager compressed-response mock and test formatting lint errors; these were corrected before the final passing suite. Final runtime reporting probes were corrected to reflect existing controls: the UI has no Docker HEALTHCHECK (running state and HTTP 200 verified), and OpenAPI is intentionally disabled (HTTP 404 verified). These were probe assumptions, not application outages. A Windows asyncio connection-reset traceback appeared during the final browser run; all three workflows still passed. Existing Starlette/httpx and Alembic deprecations, NO_COLOR/FORCE_COLOR warnings, and the approximately 1.22 MB lazy Plotly bundle warning remain. Nothing was suppressed to claim a clean run.

Local artifacts/ evidence and generated frontend build/browser/test outputs remain ignored and outside the proposed checkpoint.

## Exact proposed Git checkpoint

Modified (4):

1. `backend/app/ingestion.py` — imports extracted unchanged canonical price validator.
2. `backend/app/dhan_diagnostic.py` — imports extracted HTTP/config/error policy; profile behavior unchanged.
3. `backend/app/dhan_history_diagnostic.py` — imports shared history primitives/HTTP policy; original diagnostic behavior unchanged.
4. `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` — current offline adapter status and limitations.

New (8):

1. `backend/app/daily_values.py`
2. `backend/app/dhan_http.py`
3. `backend/app/dhan_history_contract.py`
4. `backend/app/market_data.py`
5. `backend/app/dhan_provider.py`
6. `backend/tests/test_dhan_provider.py`
7. `backend/tests/test_dhan_provider_integration.py`
8. `docs/04-planning/VS-01_STEP5D1_PROVIDER_ADAPTER_CHECKPOINT.md`

Proposed message: `feat(vs01): add read-only DhanHQ daily market data provider adapter`.
**12 files proposed; nothing staged or committed. No tag created.** Credentials, .env, generated build/test/diagnostic artifacts and backup/database exports are excluded.

## Readiness, remaining gaps and proposed Step 5D.2

- **Implemented and offline verified:** provider-neutral contracts; four-listing adapter; exact canonical mapping; provisional timestamp/calendar handling; provenance; sanitized failure isolation; bounded transport and fail-closed gates.
- **Implemented but not live verified:** adapter transport against real Dhan responses. Prior diagnostic successes do not prove this new adapter's runtime parity.
- **Blocked/pending source acceptance:** SQ-01/T-03; actual timestamp/session convention across broader history; independent price/volume reconciliation; inception/history completeness; ETF adjustments/distributions/corrections; point-in-time vintages; applicable persistent storage/derived-use/backups/retention rights. Active subscription and transient technical approval do not establish those persistent-use permissions.
- **Not implemented in this grant:** adapter-to-repository import orchestration, schema/source-kind changes, persistence, historical backfill, rate-budget orchestration, scheduled refresh or dashboard provider selection. Existing CSV research remains functional. Owner recovery/cutover/retention and cumulative human acceptance also remain open.

Proposed Step 5D.2, for separate review: approve a bounded adapter parity test with explicit endpoint/instrument/date/request budget and transient-only output; inspect sanitized canonical/provenance summaries without storing prices. Separately approve the source-use/retention profile, calendar/timestamp and adjustment qualification criteria. Only then design and approve a manual provider-to-existing atomic repository workflow, source identity/qualification contract and tests for immutable duplicates/conflicts, with any necessary migration explicitly reviewed. No backfill/scheduler/portfolio/trading implication. No implementation or live execution of that next increment is authorized by this checkpoint.
