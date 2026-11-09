# Bullion Intelligence - VS-01 research workbench

## Open and update locally

Open http://127.0.0.1:5173. From PowerShell in the repository, run `.\scripts\local\update.ps1` to build and safely restart the locally checked-out version. It preserves `.env`, the database volume and eligible RAM-cached market observations; keep the terminal open through the recovery guard. It does not fetch/merge Git changes or automatically refill lost data. Session forecasts remain transient and expire on restart. See the [user guide](docs/06-user-guide/BULLION_INTELLIGENCE_USER_GUIDE.md).

Local Gold/Silver ETF research with source/provenance inspection, exact Decimal technical analytics, charts and comparisons, and transient baseline forecasting/performance intelligence. **Packages 1-6 are implemented; owner UAT, full source qualification, statistical validation, retention rights and VS-01 acceptance remain open.** No autonomous trading or new ML model is included.

[Package 6 implementation, verification and UAT](docs/04-planning/FORECASTING_PACKAGE_6_CHECKPOINT.md) | [Four-ETF qualification](docs/04-planning/FORECASTING_PACKAGE_5_QUALIFICATION.md) | [Forward-evaluation readiness](docs/04-planning/FORECASTING_PACKAGE_6_FORWARD_READINESS.md) | [Requirements baseline](docs/01-requirements/REQUIREMENTS_BASELINE.md)

Research Dashboard includes Daily, Intraday, Technical Analytics and Forecasting Research. B01/B02 provide price endpoints; B03 provides volatility only. Historical modes remain separate: strict point in time, explicit acknowledged conditional replay and labeled synthetic verification. Scorecards compare B01/B02 only on matched eligible origins, disclose overlapping/disjoint windows and do not estimate independent evidence or declare a winning model. Regime analysis is optional and uses fixed cutoff-context rules. Results/registries are bounded process memory, lost on restart/expiry.

## Historical MVP05 engineering checkpoint

The functional 52-file MVP is committed as d781e5b. Subsequent security/integrity changes are isolated in C:/ws-bullion/bullion-mvp05 and pushed only to the existing MVP feature branch; protected owner UAT is not updated. Final verification:959 backend/62 frontend/11 browser tests passed, build/CSP/synthetic recovery/dependency/credential checks passed. Candidate images have zero critical findings; six Debian high instances remain open, plus one branch-fixed Alpine scanner high. **Release security clearance and owner acceptance remain blocked.** See [current engineering checkpoint](docs/04-planning/MVP_IMPLEMENTATION_CHECKPOINT.md), [individual security dispositions](docs/04-planning/MVP_SECURITY_ASSESSMENT.md) and [gates](docs/04-planning/MVP_RELEASE_READINESS.md). Use only the engineering runner described in the local deployment document while UAT is protected.

## Local MVP release candidate (functional checkpoint history)

Lightweight Charts 5.2.1 is the default daily/intraday/technical/forecast price renderer, with native panes, exact-value alternatives and a Plotly fallback. Forecast research includes cached technical inspection and endpoint-only B01/B02 overlays; B03 remains volatility-only. Optional live context is collapsed in technical/forecast views and is not polled while unmounted.

[Implementation and exact source scope](docs/04-planning/MVP_IMPLEMENTATION_CHECKPOINT.md) | [Local management/recovery](docs/05-operations/MVP_LOCAL_DEPLOYMENT.md) | [SIT](docs/04-planning/MVP_SIT_TEST_PLAN.md) | [Owner UAT](docs/04-planning/MVP_UAT_PLAN.md) | [Release readiness](docs/04-planning/MVP_RELEASE_READINESS.md)

The first MVP deployment lost the prior RAM cache when its restore POST lacked Origin. The defect is fixed with populated authentication-boundary tests and a full offline restore preflight. Owner-authorized fresh reacquisition now supplies 248 daily observations and 75 five-minute candles per ETF; original provenance was not recovered. See REC-02 in the checkpoint. No release or acceptance is declared.

```powershell
.\scripts\local\bullion.ps1 setup
.\scripts\local\bullion.ps1 start
.\scripts\local\bullion.ps1 status
.\scripts\local\bullion.ps1 test
```

Final MVP verification: 915 backend/PostgreSQL tests, 62 frontend tests and 11 browser workflows passed; production frontend smoke and synthetic container/backup recovery passed. Project dependency/credential checks pass, but image scans retain high findings and four PostgreSQL/gosu critical reports (one Windows-only; three awaiting reachability/patched-image review). **Security release clearance is blocked.** See [security assessment](docs/04-planning/MVP_SECURITY_ASSESSMENT.md) and release readiness.

## Local startup

Prerequisites: Docker Desktop with its Linux engine running (WSL 2 on this Windows workstation). Development/tests also use Python 3.13, uv, Node 22 and npm.

```powershell
python scripts/configure_local.py
docker compose up --build -d --wait
```

The configuration script generates local secrets and refuses to overwrite an existing `.env`. Open that ignored file locally, copy `LOCAL_APP_TOKEN` into the access gate, then close the file. UI: http://127.0.0.1:5173. API liveness: http://127.0.0.1:8000/api/v1/health/live. Readiness/data APIs require the bearer token; mutating requests also require the configured local Origin. The token stays in memory and clears on reload/lock; it is absent from the frontend build.

UI/API ports publish only to loopback; the application DB has no host port. Alembic upgrades to the reviewed migration head before API startup. `docker compose stop` preserves the named application volume. Never delete/reset that volume for tests. If Docker is not on PATH, use `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'`.

## Backend-only DhanHQ market data

Provider credentials belong only in the ignored root `.env`; see [configuration and rotation](docs/05-operations/DHANHQ_LOCAL_CONFIGURATION.md). Missing optional credentials do not prevent normal startup. Configuration validation is offline; credentials never belong in frontend assets, URLs, logs, source control or PostgreSQL. Existing credential/market-data flags remain disabled by default; any configured owner-authorized live acquisition follows the [operating policy](docs/05-operations/MARKET_DATA_OPERATING_POLICY.md).

Existing read-only provider capabilities include bounded on-demand daily history, quotes, intraday candles and streaming/reconciliation under their approved gates. Forecast/performance APIs read existing canonical observations and do not acquire data. The original [profile](docs/05-operations/DHANHQ_READ_ONLY_DIAGNOSTIC.md) and [historical](docs/05-operations/DHANHQ_HISTORICAL_DIAGNOSTIC.md) diagnostics have separate explicit live-authorization controls. No automatic token exchange, account/holdings/balance access, order placement or automated trading is introduced by Packages 1-6.

The current real research cache is transient and source-qualified only conditionally; historical publication/finality, adjustments/revisions and persistence/redistribution permissions remain unresolved. Do not recreate the active API merely to run tests: it loses the RAM cache and forward-tracking state. Any necessary deployment must preserve permitted data through the reviewed RAM-only handoff, never an unapproved price-history file or database export.

## Research workflow

1. Configure exchange-specific Gold/Silver listings and watchlist membership in **Instruments & watchlists**. No universe is preselected or endorsed.
2. Register/review a source in **Source qualification**, with explicit REAL_MARKET or SYNTHETIC_TEST classification, inspected source-use/retention references, four permitted uses and quality profile. Classification cannot be changed to relabel existing history. A recorded assertion is not independent licensing or price verification.
3. Under **CSV imports**, select listing/source/basis and exact header mapping; import a permitted bounded daily CSV. Review batch counts, row diagnostics and provenance in **History & quality**.
4. In **Research dashboard**, select the ETF/metal/source/basis and available history or explicit date range. Enable SMA/EMA/RSI, enter each lookback explicitly and apply settings. SMA/EMA overlay the price chart; RSI has a separate panel. Inspect exact values, warm-up/gap reasons, seed dates, input fingerprint, quality and synthetic labels below the plots.
5. In **ETF comparisons**, select 2-10 distinct eligible listings with explicit sources/bases and dates. Inspect actual common endpoints, price changes, base-100 paths and exact common-date values. Incompatible/insufficient results are explicitly unavailable. These are price-only observations, with no total-return or future-performance claim.

No qualified real ETF dataset is bundled. SQ-01/T-03 and full acceptance remain blocked. Existing owner-authorized transient Dhan observations can support acknowledged conditional research; that does not establish strict historical availability or persistent-use rights. Follow the operating policy and [qualification package](docs/04-planning/VS-01_DATA_QUALIFICATION.md); do not infer permission to persist or redistribute provider data.

## Data and numerical contracts

- Canonical daily CSV `csv-v1`: required `trading_date` (YYYY-MM-DD) and finite positive `close`; optional coherent complete OHLC, nonnegative integer volume, exact symbol/currency and timezone-aware provider/event instants. Every file header must be explicitly mapped; unrelated fields are rejected without retention.
- One listing/source/basis per file; exact NUMERIC(24,10) prices serialize as strings. Excess precision is rejected. Original mapped strings, batch and row lineage are retained. Duplicate canonical rows skip; conflicts/hard errors reject the batch atomically. Accepted audit rows are append-only.
- Bounds: 10 MiB/file, 100,000 CSV rows, 1,024 characters/mapped field, first 1,000 diagnostics with full error count. Lists default 100/max 1,000. History/import/issue cursors are opaque. Complete chart input and indicator prefix are limited to 10,000 observations; excess input is rejected without truncation.
- SMA/EMA use explicit integer n>=1; RSI n>=2; technical upper bound 10,000. EMA seeds with first-n SMA. Wilder RSI seeds from n price changes; gain-only=100, loss-only=0, both zero unavailable. Local Decimal context 34/HALF_EVEN, derived strings 12 places. No floating-point authoritative financial arithmetic.
- Indicators use the full eligible prefix before trimming a visible range. Known calendar gaps/declared breaks reset seeds; unknown calendars remain unassessed. No invented prices, dates, fills or publication times.
- Comparisons use same-currency compatible-basis actual date intersections in an explicit period. Adjusted series require the same recorded adjustment-definition reference; mixed real/synthetic series are unavailable. No dividends or corporate-action adjustments are inferred.
- Lightweight Charts is the default financial renderer; Plotly basic remains bundled locally and lazy loaded as a fallback. Coordinates are approximate display values; exact server strings remain in hover/table alternatives. Known breaks/nulls are not connected. Large/unsafe BIGINT volume is unavailable in the browser rather than rounded.
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

For isolated PostgreSQL/browser verification without stopping the local app, use the separate engineering worktree and run `.venv/Scripts/python.exe scripts/engineering.py test`. Its synthetic database uses15443, UI15184 and APIs18011/18012; the normal5173/8000 services and prices are untouched. Do not run it against the owner database. Reports and traces remain ignored.

Package 6 verification reported **901 backend, 51 component and nine Chromium workflows passed, none failed/skipped**, plus lint, production build, containers, dependency and credential checks. The source-control checkpoint reruns those checks before committing. Existing deprecation and Plotly chunk-size warnings remain. Historical package checkpoints retain their dated results; they are not fresh acceptance claims.

The provider-attempt counter changed from23to24 between guarded phases during Package6. Its cause remains unattributed; controlled checks had flat counters. This remains an open operational-audit item, not a reason to silently alter market-data behavior or assert all-session zero requests.

```powershell
.\.venv\Scripts\python.exe scripts/verify_recovery.py
```

[Recovery instructions](docs/05-operations/LOCAL_RECOVERY.md) cover restricted backups, checksum/integrity, restoration into a separate empty test database and table/schema/research-query consistency. Never restore over the active application DB. Synthetic recovery does not establish owner-data cutover, retention or final handover acceptance.

## Source and API map

- `backend/app/`: strict input/access/CSV/persistence/quality plus pure Decimal arithmetic and read-only snapshot-consistent research orchestration.
- `backend/tests/`: independent arithmetic references, parsing/access, actual PostgreSQL transactions/concurrency, provenance, snapshots and research API cases.
- `frontend/src/`: existing workflows plus local charts, research controls, exact tables, comparison/quality disclosures and component regressions.
- `frontend/e2e/`: fourteen workflows covering workspace, provider/session/streaming, daily/intraday/technical charts and forecasting/performance against isolated UI/API/PostgreSQL.
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
| Research | GET /instruments/{id}/chart; GET /instruments/{id}/indicators; POST /comparisons; POST /research/technical (read-only calculations) |
| Forecasting | GET /research/forecasts/context; POST /research/forecasts/run; POST /research/forecasts/evaluate; GET /research/forecasts/runs; GET /research/forecasts/runs/{run_id} |
| Performance registry | GET /research/forecasts/performance (transient aggregate cards, no price/error history) |

See [design contracts](docs/03-design/VS-01_DETAILED_DESIGN.md), [acceptance dispositions](docs/03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md), [dependency review](docs/04-planning/VS-01_SECURITY_REVIEW.md) and [container controls](docs/04-planning/VS-01_CONTAINER_REPRODUCIBILITY.md). Runtime images/uv are digest pinned; dependencies/browser are locked. Verification establishes tested-platform dependency selection/startup, not byte-identical image builds or OS-image vulnerability clearance.

For personal local use, follow Code -> Test -> Build -> Run -> Use -> Improve. Source/finality/adjustment/vintage/calendar limitations remain visible in research results; retention permission is still required before durable provider-data storage. Durable forward evaluation is proposed only; Packages1-6 do not authorize persistent market-data or forecast-history storage. Later strategy/risk/portfolio/AI/ML/trading features require separate scope. Requirements baseline and approved decisions remain unchanged; no full VS-01, model-reliability or production-readiness acceptance is declared.
