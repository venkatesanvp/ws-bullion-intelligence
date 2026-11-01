# Bullion Intelligence — VS-01 data workbench

A local Gold/Silver ETF daily-data inspection application. This increment implements the human-authorized watchlist, qualified CSV ingestion, PostgreSQL history/provenance and quality workflows. The full VS-01 and R1 release are not complete.

[Scoped approval and verification](docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md) · [Requirements baseline](docs/01-requirements/REQUIREMENTS_BASELINE.md) · [Design contracts](docs/03-design/VS-01_DETAILED_DESIGN.md)

## Local startup

Prerequisites: Docker Desktop with its Linux engine running (WSL 2 on this Windows workstation). For local development/tests: Python 3.13, uv, Node 22 and npm. Application secrets stay in ignored `.env`; do not paste them into issues, commits or screenshots.

From the repository root:

```powershell
python scripts/configure_local.py
docker compose up --build -d --wait
```

The configuration script creates random local secrets and refuses to overwrite an existing file. Open `.env` locally, copy only the `LOCAL_APP_TOKEN` value into the access gate, then close the file.

- UI: http://127.0.0.1:5173
- API liveness: http://127.0.0.1:8000/api/v1/health/live
- Readiness and every data API require the local bearer token.
- UI/API host ports bind only to loopback. The application database has no published host port.
- Migration service runs Alembic revision `0001_market_workbench` before API startup.
- `docker compose stop` preserves the named database volume. Do not use volume deletion/reset commands on application data.
- If Docker is not on PATH in PowerShell, replace `docker` with `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'`.

Compose startup, PostgreSQL integration and full browser evidence remain pending while the workstation's WSL/Docker setup is unavailable. See the verification record for actual results; successful code generation/build is not database acceptance.

## First-use workflow

1. Add exchange-specific Gold/Silver ETF listing metadata under **Instruments & watchlists**. No fund universe is preselected or endorsed.
2. Register a CSV source under **Source qualification**. Choose REAL_MARKET or SYNTHETIC_TEST explicitly. Classification cannot be changed to relabel existing history; register another source instead.
3. Record reviewed source-use and retention evidence, the four permitted uses, and qualification. An owner-recorded assertion is not independent licensing/sample verification. Actual real ETF samples/permissions remain Open under SQ-01; none are bundled.
4. Select the exact listing, source and price basis under **CSV imports**. Review the explicit canonical-to-file-header mapping and import one bounded UTF-8 daily CSV.
5. Inspect terminal batch counts and row diagnostics. A hard error/conflicting value rejects all new observations; existing history is preserved.
6. Inspect exact decimal prices, original batch/row, dataset/range dates and unknown quality/timing under **History & quality**. Watchlist membership removal does not remove prices.

The token stays in memory, is cleared by page reload/lock and is not embedded in the frontend build. Mutating API requests require a configured local Origin as well as bearer authentication.

## CSV and quality contract

- Supported source contract: `csv-v1`; quality evaluator: `quality-v1`.
- Required mapped fields: `trading_date` in YYYY-MM-DD and finite positive `close`.
- Optional: coherent complete `open/high/low` trio, nonnegative integer `volume`, exact `symbol/currency`, timezone-aware `provider_published_at/event_time`.
- Prices are exactly representable NUMERIC(24,10), serialized as strings. Excess precision is rejected without rounding.
- One instrument/source/basis per file. All file headers must be mapped to allowed canonical fields; unrelated fields are rejected without retention. Mapped raw strings are retained.
- Technical bounds: 10 MiB file, 100,000 data rows, 1,024 characters per mapped field, first 1,000 diagnostics. Error count retains the full total. General list/history pages default to 100, maximum 1,000; history/import/issue cursors are opaque.
- CSV rows may be out of order; canonical observations are ordered by trading date, with original row numbers retained.
- Same date/key and canonical values are exact duplicates; conflicts reject the batch. No observation-update/delete API exists. Database triggers also protect accepted market audit rows.
- `RAW_CLOSE`, `PROVIDER_ADJUSTED` and `UNKNOWN` remain separate. Adjusted data needs an explicit source adjustment-definition reference; the application does not adjust prices.
- Unknown calendar, freshness, corporate actions and publication times remain unknown/unassessed. No dates/bars/publication instants are invented.
- An explicit calendar profile includes reviewed evidence, version, coverage and enumerated sessions. An explicit freshness profile applies only at its recorded timezone-aware as-of instant. No default financial cutoff or holiday inference exists.
- Browser display never shows an unsafe rounded BIGINT volume as exact; values outside JavaScript's exact integer range are explicitly unavailable in the table. PostgreSQL and the API retain the integer.
- Historical CSV remains unverified for replay; ingestion time is not proof of point-in-time market availability.

## Retry and recovery

Each import uses an explicit UUID `Idempotency-Key`. Reuse it with the identical file and metadata if the response is lost. A retry returns the original terminal batch; changed content/metadata under that key returns conflict.

Use **Resolve an interrupted request**, or `GET /api/v1/import-batches/by-key/{request_key}`, before deciding an interrupted request failed. No durable pending job or automatic background retry is invented. A new import key is generated when the selected file/mapping/series changes. Keep the key if the browser must close during an uncertain operation.

## Verification

Install the locked dependencies:

```powershell
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend exec playwright install chromium
```

Run checks that do not need PostgreSQL:

```powershell
.\.venv\Scripts\python.exe scripts/verify_local.py
```

After Docker is running, with ports 55433, 8001 and 5173 available:

```powershell
.\.venv\Scripts\python.exe scripts/verify_local.py --database --browser
```

The database option starts only the separate `test-db` service, named `bullion_test`, published on loopback 55433 with tmpfs storage. Tests migrate and truncate that explicitly disposable database; guards refuse nonlocal/non-`_test` targets. They do not reset the application database or its volume. Fixtures are visibly SYNTHETIC_TEST. Browser tests start a separate API on 8001 and a loopback Vite process on 5173; no mocked backend substitutes for the real PostgreSQL workflow.

Reports go to ignored `artifacts/` and frontend test-report directories. The dependency locks record application/test package versions; Playwright's package fixes its browser revision. Image digests are recorded in Compose/Dockerfiles once resolved.

## Source and interface map

- `backend/app/`: strict schemas, access boundary, CSV validation/transaction, typed persistence and quality/history queries.
- `backend/migrations/`: frozen initial Alembic schema and append-only audit guards; destructive downgrade is disabled.
- `backend/tests/`: parser/access cases plus real-PostgreSQL transaction, concurrency, provenance, cursor and restart checks.
- `frontend/src/`: local access gate, catalog/watchlists, source review, import outcomes and accessible history table.
- `frontend/e2e/`: real UI/API/PostgreSQL browser workflow.
- `scripts/`: exclusive local secret initialization and explicit verification driver.

API prefix `/api/v1`:

| Area | Methods / paths |
| --- | --- |
| Health | GET /health/live; GET /health/ready |
| Instruments | GET/POST /instruments; PATCH /instruments/{id} |
| Watchlists | GET/POST /watchlists; GET/PATCH /watchlists/{id}; POST /watchlists/{id}/members; DELETE /watchlists/{id}/members/{instrument_id} |
| Sources | GET/POST /data-sources; PATCH /data-sources/{id}/qualification |
| Imports | POST/GET /import-batches; GET /import-batches/by-key/{key}; GET /import-batches/{id}; GET /import-batches/{id}/issues |
| History/quality | GET /instruments/{id}/history; GET /instruments/{id}/quality |

## Limits and next approval

No technical indicators, comparison calculations, charting, strategies/recommendations, GTT, portfolios, paper trading, broker execution or AI integration are implemented. R1's configurable hypothetical ₹20 lakh reference portfolio and independent strategy horizons remain requirements for later authorized increments.

See [next-package approval proposal](docs/04-planning/VS-01_NEXT_PACKAGE_PROPOSAL.md). Backup/restore acceptance, qualified real-market samples and the remaining VS-01 capabilities still require their recorded evidence/authorizations. No approved product decision or baseline requirement classification is changed.
