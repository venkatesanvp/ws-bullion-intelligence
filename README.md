# Bullion Intelligence - VS-01 research workbench

Local Gold/Silver ETF research: configurable listings/watchlists, qualified CSV ingestion, exact PostgreSQL history/provenance, quality inspection, price charts, SMA/EMA/Wilder RSI and common-date price-only comparisons. The approved software scope is implemented and verified with labeled synthetic fixtures. **Full VS-01/R1 acceptance remains incomplete.**

[Current implementation status](docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md) | [Step 4 completion and proposed checkpoint](docs/04-planning/VS-01_STEP4_COMPLETION.md) | [Requirements baseline](docs/01-requirements/REQUIREMENTS_BASELINE.md)

## Local startup

Prerequisites: Docker Desktop with its Linux engine running (WSL 2 on this Windows workstation). Development/tests also use Python 3.13, uv, Node 22 and npm.

```powershell
python scripts/configure_local.py
docker compose up --build -d --wait
```

The configuration script generates local secrets and refuses to overwrite an existing `.env`. Open that ignored file locally, copy `LOCAL_APP_TOKEN` into the access gate, then close the file. UI: http://127.0.0.1:5173. API liveness: http://127.0.0.1:8000/api/v1/health/live. Readiness/data APIs require the bearer token; mutating requests also require the configured local Origin. The token stays in memory and clears on reload/lock; it is absent from the frontend build.

UI/API ports publish only to loopback; the application DB has no host port. Alembic revision `0001_market_workbench` runs before API startup. `docker compose stop` preserves the named application volume. Never delete/reset that volume for tests. If Docker is not on PATH, use `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'`.

## Optional DhanHQ credential preparation

DhanHQ market-data configuration is disabled by default. Enter its developer application name/key/secret and any optional runtime client ID/token only in the ignored root `.env`; see [backend-only loading, offline validation and token rotation](docs/05-operations/DHANHQ_LOCAL_CONFIGURATION.md). No provider connection, download or trading capability is implemented by this configuration step. Missing optional credentials do not block the existing workbench.

## Research workflow

1. Configure exchange-specific Gold/Silver listings and watchlist membership in **Instruments & watchlists**. No universe is preselected or endorsed.
2. Register/review a source in **Source qualification**, with explicit REAL_MARKET or SYNTHETIC_TEST classification, inspected source-use/retention references, four permitted uses and quality profile. Classification cannot be changed to relabel existing history. A recorded assertion is not independent licensing or price verification.
3. Under **CSV imports**, select listing/source/basis and exact header mapping; import a permitted bounded daily CSV. Review batch counts, row diagnostics and provenance in **History & quality**.
4. In **Research dashboard**, select the ETF/metal/source/basis and available history or explicit date range. Enable SMA/EMA/RSI, enter each lookback explicitly and apply settings. SMA/EMA overlay the price chart; RSI has a separate panel. Inspect exact values, warm-up/gap reasons, seed dates, input fingerprint, quality and synthetic labels below the plots.
5. In **ETF comparisons**, select 2-10 distinct eligible listings with explicit sources/bases and dates. Inspect actual common endpoints, price changes, base-100 paths and exact common-date values. Incompatible/insufficient results are explicitly unavailable. These are price-only observations, with no total-return or future-performance claim.

No qualified real ETF dataset is bundled or accepted. SQ-01/T-03 remain blocked; do not download/ingest unqualified data. See the [minimum source qualification package](docs/04-planning/VS-01_DATA_QUALIFICATION.md).

## Data and numerical contracts

- Canonical daily CSV `csv-v1`: required `trading_date` (YYYY-MM-DD) and finite positive `close`; optional coherent complete OHLC, nonnegative integer volume, exact symbol/currency and timezone-aware provider/event instants. Every file header must be explicitly mapped; unrelated fields are rejected without retention.
- One listing/source/basis per file; exact NUMERIC(24,10) prices serialize as strings. Excess precision is rejected. Original mapped strings, batch and row lineage are retained. Duplicate canonical rows skip; conflicts/hard errors reject the batch atomically. Accepted audit rows are append-only.
- Bounds: 10 MiB/file, 100,000 CSV rows, 1,024 characters/mapped field, first 1,000 diagnostics with full error count. Lists default 100/max 1,000. History/import/issue cursors are opaque. Complete chart input and indicator prefix are limited to 10,000 observations; excess input is rejected without truncation.
- SMA/EMA use explicit integer n>=1; RSI n>=2; technical upper bound 10,000. EMA seeds with first-n SMA. Wilder RSI seeds from n price changes; gain-only=100, loss-only=0, both zero unavailable. Local Decimal context 34/HALF_EVEN, derived strings 12 places. No floating-point authoritative financial arithmetic.
- Indicators use the full eligible prefix before trimming a visible range. Known calendar gaps/declared breaks reset seeds; unknown calendars remain unassessed. No invented prices, dates, fills or publication times.
- Comparisons use same-currency compatible-basis actual date intersections in an explicit period. Adjusted series require the same recorded adjustment-definition reference; mixed real/synthetic series are unavailable. No dividends or corporate-action adjustments are inferred.
- Plotly basic is bundled locally and lazy loaded. Coordinates are approximate display values; exact server strings remain in hover/table alternatives. Known breaks/nulls are not connected. Large/unsafe BIGINT volume is unavailable in the browser rather than rounded.
- Historical CSV ingestion time is not proof of point-in-time market availability. Replay remains unverified. Raw/adjusted/unknown bases stay distinct; quality/freshness remain unknown without explicit evidence/profiles.

Import retries use an explicit UUID `Idempotency-Key`. Keep and reuse the identical file/metadata/key after an uncertain response; changed input under that key conflicts. Use **Resolve an interrupted request** or `GET /api/v1/import-batches/by-key/{key}` before retrying. No automatic background job or correction is inferred.

## Verification and recovery

Install frozen dependencies and Chromium:

```powershell
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend exec playwright install chromium
```

Run lint/backend units/components/build without PostgreSQL:

```powershell
.\.venv\Scripts\python.exe scripts/verify_local.py
```

For cumulative real PostgreSQL/browser verification, stop the normal UI first so browser port 5173 is free; ports 55433 and 8001 must also be available:

```powershell
docker compose stop ui
.\.venv\Scripts\python.exe scripts/verify_local.py --database --browser
docker compose up --build -d --wait
```

Tests use only disposable local `bullion_test` on loopback 55433 with tmpfs; guards refuse nonlocal/non-`_test` targets. Browser tests start a separate API on 8001 and Vite on 5173. They use real PostgreSQL/backend requests and visibly synthetic fixtures. Reports/screenshots/traces stay in ignored `artifacts/` and frontend report directories.

Final Step 4 run: **114 backend, 16 component and three Chromium tests passed, none failed/skipped**; lint and production build passed. Full/production npm audits and Windows/Linux Python audits found zero known vulnerabilities. Compose rebuilt/repeated startup and synthetic backup/new isolated restore passed. Two backend deprecations and the lazy Plotly chunk-size warning remain; see the completion record for actual evidence and resolved initial failures.

```powershell
.\.venv\Scripts\python.exe scripts/verify_recovery.py
```

[Recovery instructions](docs/05-operations/LOCAL_RECOVERY.md) cover restricted backups, checksum/integrity, restoration into a separate empty test database and table/schema/research-query consistency. Never restore over the active application DB. Synthetic recovery does not establish owner-data cutover, retention or final handover acceptance.

## Source and API map

- `backend/app/`: strict input/access/CSV/persistence/quality plus pure Decimal arithmetic and read-only snapshot-consistent research orchestration.
- `backend/tests/`: independent arithmetic references, parsing/access, actual PostgreSQL transactions/concurrency, provenance, snapshots and research API cases.
- `frontend/src/`: existing workflows plus local charts, research controls, exact tables, comparison/quality disclosures and component regressions.
- `frontend/e2e/`: original foundation workflow and two research workflows against actual UI/API/PostgreSQL.
- `scripts/`: secret initialization, regression driver and isolated recovery verifier. No new service or migration is needed for research.

All paths below use `/api/v1`:

| Area | Methods / paths |
| --- | --- |
| Health | GET /health/live; GET /health/ready |
| Instruments | GET/POST /instruments; PATCH /instruments/{id} |
| Watchlists | GET/POST /watchlists; GET/PATCH /watchlists/{id}; POST /watchlists/{id}/members; DELETE /watchlists/{id}/members/{instrument_id} |
| Sources | GET/POST /data-sources; PATCH /data-sources/{id}/qualification |
| Imports | POST/GET /import-batches; GET /import-batches/by-key/{key}; GET /import-batches/{id}; GET /import-batches/{id}/issues |
| History/quality | GET /instruments/{id}/history; GET /instruments/{id}/quality |
| Research | GET /instruments/{id}/chart; GET /instruments/{id}/indicators; POST /comparisons (read-only calculation) |

See [design contracts](docs/03-design/VS-01_DETAILED_DESIGN.md), [acceptance dispositions](docs/03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md), [dependency review](docs/04-planning/VS-01_SECURITY_REVIEW.md) and [container controls](docs/04-planning/VS-01_CONTAINER_REPRODUCIBILITY.md). Runtime images/uv are digest pinned; dependencies/browser are locked. Verification establishes tested-platform dependency selection/startup, not byte-identical image builds or OS-image vulnerability clearance.

The next gate is qualified real Gold/Silver source evidence, followed by T-03/cumulative acceptance and operational handover. Later R1 strategy/risk/portfolio/paper/manual/broker/AI features remain unimplemented and require separate authorization. The requirements baseline and approved D-01..16 are preserved. Step 4 implementation is checkpointed at `a244cfe`; later configuration changes await separate review. No full VS-01 acceptance is declared.
