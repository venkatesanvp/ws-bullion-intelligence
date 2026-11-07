# VS-01 Step 5D.2 — bounded historical acquisition and canonical ingestion

Recorded: 2 November 2026 (Asia/Kolkata). Parent HEAD: `ef0a7c460ec82ce3797da37cded883ec82553871`.

**Checkpoint A implemented and verified offline. Checkpoint B is presented for review. Checkpoints C/D (live collection and real-data application verification) have not been executed. No commit/tag, authenticated Dhan request, live-price persistence or active-application-database migration occurred.**

## 1. Authority and architecture

The owner's Step 5D.2 request authorizes code, migration design and offline testing of one-year four-ETF retrieval/persistence. It explicitly requires a reviewed preflight before live retrieval, and established applicable data-use/retention rights before live persistence. This supplements the earlier Step 5D.1/CSV-only exclusions without changing requirements or prior mathematical conventions. Trace: D-04/12/14, REQ-02-007/008/009/011/012/013/014/015, REQ-05-003/004/010, ADR-03/04/05/08/09/10 and DC-02/03/04/07/09. Open requirement/SQ classifications are not promoted.

Step 5D.1 remains uncommitted in the starting working tree. Its twelve-file implementation is preserved within this cumulative review. This checkpoint adds the collection/repository bridge; it does not create a separate price store, worker service, scheduler, ORM observation type, analytical engine or dashboard.

- `HistoryPlan` and provider-neutral collection orchestration produce bounded non-overlapping inclusive date partitions and normalized in-memory series through the existing provider protocol. Explicit calendar profiles and optional ISIN-keyed inception dates with evidence are required to distinguish unavailable prefixes from gaps. No inception date is guessed from the first returned row.
- `DhanDailyProvider` keeps the verified identities, fixed historical endpoint, exact Decimal decoding, provisional timestamp policy and bounded HTTP/security behavior from Step 5D.1. Each call remains a single request; no token exchange, fallback or retry.
- `ingestion._ingest` is the shared existing atomic repository path, now accepting a prepared canonical report. CSV uses its original parser, request identity and upload contract; provider candidates use the same request-key advisory lock, source/instrument row locks, observation comparison, duplicate/conflict policy, terminal audit, transaction and revision update.
- `provider_ingestion` is the scoped Dhan-to-canonical repository bridge: it rechecks source rights/policy, full exchange/symbol/ISIN/metal/currency identity, exact numeric/temporal invariants and matching calendar evidence/version/session sets. A calendar changed between collection and persistence fails closed. Provider details remain outside analytics/dashboard calculations.
- Existing query APIs expose the resulting observations without a new financial calculation. Generic quality/provenance fields retain provisional timestamp/adjustment/reconciliation limitations. The source-registration form now supports CSV or DhanHQ contracts; credential entry/retrieval execution remains backend-only. Synthetic end-to-end verification uses the same UI and research APIs.

## 2. Persistence and recovery design

Migration `0002_provider_ingestion` extends the existing source-kind check to USER_CSV/DHANHQ and enforces the matching contract version. It adds no table or column and does not rewrite observations, profiles or old imports. Both the model and readiness revision move to this migration. Tests prove CSV rows survive downgrade/upgrade and provider-bearing downgrade refuses rather than deleting/disguising data. Only the disposable `bullion_test` database was migrated. The active application remains on its existing deployed source/schema; deploy the new source and migration together after review.

All four acquisitions are collected and validated before the runner begins persistence. A provider/auth/rate/network/structure/data failure stops remaining requests and exposes no partial collection for import. Each successfully collected ETF is then imported atomically; the four ETF imports are **not one cross-instrument transaction**. A later database failure can leave earlier ETF batches committed, with their identifiers/status preserved. Partial valid coverage can be stored only after licence/policy authorization, with gaps recorded; it is not automatically accepted as complete one-year coverage. Empty acquisitions are rejected with audit, without fabricated prices.

Canonical observation fields and NUMERIC(24,10)/BIGINT constraints are unchanged. Values remain Decimal/integer; no rounding, truncation, filling, resampling or price repair. Batch provenance records provider/listing/security ID, request bounds, contract, actual retrieval UTC time, candidate timestamp policy, adjustment reference, validation summaries, limitations and inception evidence. Validated row provenance retains numeric source timestamp, original provider row, retrieval time and exact canonical values. Event/publication instants stay null/unknown. No unvalidated response is archived.

The legacy `file_sha256` column stores a deterministic normalized-payload identity for provider imports; `bytes=0` means no retained input file/raw-response byte count, not an empty acquisition. Profile/provenance snapshots identify the actual contract. Retrieval timestamps are excluded from replay identity, preserving the original audit/provenance when the same key/content replays. Changed content with the same key returns conflict; a new key with matching observations records NO_CHANGE, and conflicting observations reject the entire ETF batch. Accepted original rows and provenance are never overwritten.

A user-chosen run UUID derives one request key per ISIN using UUID5(run_uuid, isin). On interruption or lost acknowledgement, **query existing** `GET /api/v1/import-batches/by-key/{request_key}` before deciding on any new retrieval. A missing batch means no committed transaction was found; do not infer that from a timeout alone. Retrying the same validated input/key replays a committed import or commits once after rollback. A new manual network run needs a new explicit request budget/approval; the runner never automatically repeats collection. Do not delete accepted prices or reset revisions to recover. Tests cover rollback of batch/rows/revision, lost acknowledgement, conflicting data and concurrent same-key attempts.

## 3. Data-use and retention assessment

Reviewed the [official daily API](https://dhanhq.co/docs/v2/historical-data/), [rate-limit contract](https://dhanhq.co/docs/v2/#rate-limit), [Dhan terms](https://dhan.co/terms/) and [daily availability FAQ](https://dhan.co/support/platforms/dhanhq-api/why-am-i-not-receiving-the-latest-day-s-data-from-the-daily-historical-data-api/).

The API documentation supports token-authenticated historical retrieval. General platform terms restrict unauthorized extraction/copying, publication, commercialization and derived use, reserving rights not expressly granted. The reviewed public material does not establish this account's applicable permission or duration for persistent local research storage, private charts/derived analytics, local backups, refresh or post-subscription retention. No retention period or personal-use exemption is invented. This is an unresolved evidence gap, not a claim that an API subscription prohibits those uses.

**Live persistence is blocked.** Before enabling it, record the applicable subscription/API/exchange terms or other authorized permission reference; permitted retrieval/storage/analysis/display; private backup and retention/deletion conditions (including expiry/termination); reviewer/date; and the acknowledged provisional session-mapping policy. A support contact is one possible evidence route, not a mandatory prerequisite for the limited transient technical test authorized for review here. An active plan/past successful retrieval is not automatically a persistent-use grant.

The runner's separate `--persist-approved` flag is insufficient by itself: it also requires an existing QUALIFIED_FOR_RESEARCH DHANHQ source, matching contract/rights reference, permitted-use/retention evidence, adjustment definition and an acquisition review explicitly acknowledging the candidate timestamp policy. No such live-source disposition was fabricated or entered. Synthetic test source permissions are labeled TEST ONLY and confined to disposable databases.

## 4. Configurable range and calendar

The explicit initial plan is [DHANHQ_ONE_YEAR_PLAN.json](../05-operations/DHANHQ_ONE_YEAR_PLAN.json): inclusive **2025-11-02 through 2026-11-02**, a full calendar-year span ending at the most recent completed scheduled NSE session as of this report. It contains **247 scheduled sessions**, not an assertion of 247 available rows for each ETF.

Calendar evidence: [NSE CMTR65587](https://nsearchives.nseindia.com/content/circulars/CMTR65587.pdf) for the 2025 remainder, [CMTR71775](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf) for 2026, the [current NSE equities holiday page](https://www.nseindia.com/resources/exchange-communication-holidays) including 15 January 2026 election closure, and [CMTR72349](https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf) for the **Sunday 1 February 2026 Budget live session**. Muhurat sessions on 21 October 2025 and 8 November 2026 are outside this window. Mock trading does not create historical-price observations. Sessions are explicit in the reviewed JSON; runtime does not infer every weekday is an actual session. Unannounced/exceptional changes and actual ETF observations still require reconciliation. The calendar is reviewed scheduling evidence, not proof of actual daily trading or complete market data.

Partitions are non-overlapping, at most 366 calendar days and 366 returned rows per provider request; dates remain within the adapter's existing 2000–2099 sanity bounds. `max_requests` is explicit and validated before any client call. Three-/five-year requests use the same planner with a larger reviewed budget; since-inception history can use evidenced availability metadata. No new acquisition architecture or automatic backfill is introduced. Initial scope remains these four listings. No silent automatic extension, shrinking, catch-up or date adjustment is allowed under an old reviewed plan.

## 5. Checkpoint B — exact proposed live preflight

| Primary ETF | Symbol | ISIN | Dhan security ID |
| --- | --- | --- | --- |
| Tata Gold ETF | TATAGOLD | INF277KA1976 | 21401 |
| Tata Silver ETF | TATSILV | INF277KA1984 | 21428 |
| Nippon India Gold BeES | GOLDBEES | INF204KB17I5 | 14428 |
| Nippon India Silver BeES | SILVERBEES | INF204KC1402 | 8080 |

All are verified XNSE-listed INR exchange-traded ETF market-price series, not NAV; identities remain those recorded in Step 5B. Provider mappings are NSE_EQ / EQUITY. No fresh master/profile/account request was made.

Exactly **four sequential POST requests**, one per row in the table, to `https://api.dhan.co/v2/charts/historical`. Each body substitutes its listed securityId into:

```json
{"securityId":"21401","exchangeSegment":"NSE_EQ","instrument":"EQUITY","oi":false,"fromDate":"2025-11-02","toDate":"2026-11-03"}
```

`toDate` is exclusive. Maximum four attempts, no retry/fallback/token exchange; stop on failure. At least one second between requests, verified TLS, no redirects/proxy overrides; 5-second connect/write/pool and 10-second read inactivity timeouts, 256 KiB/366-row response bounds and existing 20-second between-chunk body budget. The body budget is not a hard total deadline. Official Data API limits are 5 requests/second and 100,000/day; account-wide remaining quota is not known or rechecked. No shared-client/global rate scheduler is added.

Offline preflight fingerprint: `a051f5383ab4f6bb8959ffb845962a58597cf58c7483dfeebe1efb632aa9dbe9`.
Current safe configuration report: valid, access token present, enablement **false**. No token value/expiry or fresh entitlement assertion is reported. No additional profile/refresh call is authorized. The fingerprint binds the plan/calendar/full listing identities, not credentials; changing a date/calendar/availability/budget requires a new preflight review.

Timestamp policy remains UNIX_SECONDS_IST_CANDIDATE_V1. Prior live evidence covered only 26–30 October 2026. New observations will be checked for schema/aligned arrays, exact numeric validity, volume/integer representation, OHLC coherence, bounds, candidate IST date conversion, duplicates, actual returned range, calendar omissions/extras and cross-partition duplicates. Independent permitted-source price/volume reconciliation, full timestamp/session convention and adjustment factors remain separate qualification tasks. No investment-performance conclusion or total-return comparability follows from passing these checks.

**Availability risk:** the official daily FAQ documents T−1 availability. As of 2 November 2026, the completed 2 November bar may still be unavailable. Do not silently change end date to 30 October or make extra catch-up calls. Prefer the approved transient test after the provider has published the intended last bar, with a fresh check that this remains the intended completed-session target. If execution is delayed past another completed session, update/review the plan/calendar rather than silently extending approval.

### Operator controls (not executed)

Default host preflight (set PYTHONPATH=backend in that process):

```text
python -m app.dhan_import --plan docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json
```

For the first approved transient run, the existing API image can run a one-off command with the reviewed backend/plan mounted read-only, so no active migration/deployment is needed. From the repository root, **only after review**:

```powershell
docker compose run --rm --no-deps -T -e DHAN_DATA_API_ENABLED=true -e PYTHONPATH=/review/backend -v C:/ws-bullion/bullion-intelligence/backend:/review/backend:ro -v C:/ws-bullion/bullion-intelligence/docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json:/review/plan.json:ro api uv run --offline --frozen --no-dev python -m app.dhan_import --plan /review/plan.json --env-file /review/no-env-file --execute-approved-plan a051f5383ab4f6bb8959ffb845962a58597cf58c7483dfeebe1efb632aa9dbe9
```

This uses existing backend environment credentials, a process-only override and no `--persist-approved`, source ID or run ID. No DB engine/session is created in transient mode. Only sanitized counts/date/validation/provenance summaries reach stdout; prices/source epochs/raw responses are not exported or retained. Do not save raw output from another tool or add response caches.

After applicable rights/policy review and deployment of the reviewed migration/source, persistent manual ingestion additionally requires `--persist-approved --source-id <reviewed-source-UUID> --run-id <chosen-run-UUID>`. Register the exact four listings and the DhanHQ source using existing application forms/APIs; populate its reviewed calendar/adjustment profile and acquisition_review (`timestamp_policy`, `allow_provisional_session_dates`, `review_ref`) through the existing quality-profile review. These flags record operator authorization; they do not create a licence or prove source accuracy. No live persistent command is proposed for approval yet.

## 6. Executed verification and known failures

Final executed checks: **547 backend/PostgreSQL tests, 17 frontend tests and 4 Chromium workflows passed; zero failures/errors/skips in the final relevant runs.** Python lint and the TypeScript/production build passed. The last backend run includes the demonstrated final-session reporting correction: a provider-reviewed series with an explicit requested end now reports a missing final session rather than clipping assessment at its last observation. CSV assessment behavior and all numerical conventions remain unchanged. Frontend/browser code was unchanged by this backend-only correction.

| Verification | Actual result | Ignored evidence |
| --- | --- | --- |
| Complete backend + actual PostgreSQL | 547 passed, no failures/errors/skips | `artifacts/step5d2-backend-final.log`, `backend-tests.xml` |
| Frontend components | 17 passed | `artifacts/step5d2-frontend-final.log` |
| Chromium with real test API/PostgreSQL | 4 passed, including provider-to-research workflow | `artifacts/browser-tests.xml`, `step5d2-final-all-checks.log` |
| Lint and production build | Passed; chart bundle warning retained | backend lint execution; `artifacts/step5d2-frontend-final.log` |
| Linux final-source isolated probe | Four mappings ? 247 synthetic observations; network none, no persistence calls | `artifacts/step5d2-linux-network-none-final.log` |
| Python security scans | Windows 40 packages / installed Linux 31 packages; 0 vulnerabilities, 0 skipped | `artifacts/step5d2-audit-windows-python.json`, `step5d2-audit-linux-python.json` |
| Full and production npm scans | 0 findings in both | `artifacts/step5d2-audit-frontend-full.json`, `step5d2-audit-frontend-production.json` |
| Credential-pattern scan | One reviewed synthetic-token candidate, 0 actual/unresolved credentials | `artifacts/step5d2-secret-pattern-scan.json` |
| Private runtime/Git/exposure checks | Passed; API-only credentials, false gate, no actual secret matches in inspected source/assets/evidence/logs/local responses; original active schema preserved | `artifacts/step5d2-final-verification.json` |

The general one-year synthetic fixtures intentionally use 261 weekdays, not a claimed NSE calendar. The separate reviewed-calendar probe uses 247 scheduled dates with generated synthetic prices. Neither quantity is actual provider coverage. Actual four-ETF one-year counts remain unknown until approved retrieval.

Scans use isolated pip-audit 2.9.0 / detect-secrets 1.5.0; no dependencies changed and no advisory suppressed. The pattern detector's IBM Cloud IAM signature matched the explicitly labeled synthetic test TOKEN in `provider_fixtures.py`. The hashed finding was verified against that fixture literal and retained, not hidden by ignore pragmas/baselines or live credential verification. Independently, actual local credentials and encoded forms were compared privately against the proposed files, production assets and diagnostic/test evidence, with no matches. OS-image vulnerability clearance is not claimed.

Existing Starlette/httpx and Alembic deprecations, runner color warnings and the approximately 1.22 MB lazy Plotly chunk warning remain. Existing UI/API/PostgreSQL services were restored and remain functional on the prior deployed source/schema; the disposable test database is stopped. Source, schema and full real-data runtime acceptance remain pending the next reviewed execution/deployment. Earlier logs are retained: an incorrect new limitation-label expectation was fixed to the existing PRICE_ONLY_NOT_TOTAL_RETURN contract; a fixture encoder that overwrote intentionally invalid volume was corrected; the browser test now uses actual accessible combobox names and space-formatted quality flags. A Windows default-encoding error interrupted a UI edit; the previously unchanged file was restored from HEAD and scoped edits reapplied with explicit UTF-8. The intervening frontend failures are retained; restored UI browser workflows pass. TypeScript caught two unsupported test-library `exact` options; only those new test options were corrected and frontend/build rerun. No existing test assertion was weakened or production numeric convention altered.

## 7. Remaining blockers and next step

Checkpoint C needs explicit review/approval of the exact four-request transient plan. Persistent use remains blocked on account-applicable rights/retention evidence and source/policy review. Technical blockers remain: actual one-year coverage by listing, latest completed bar availability, broad-history timestamp/session interpretation, independent reconciliation, adjustment/distribution/correction treatment, and point-in-time vintages. Prior diagnostic success and synthetic test quantities cannot resolve these. Source qualification SQ-01/T-03, owner recovery/cutover/retention and final human acceptance remain open.

Recommended next action: review this implementation and bounded transient preflight; approve/revise dates and request budget, preferably after the last requested bar is available. After that limited execution, inspect sanitized quality findings before deciding on any persistent-source approval. Checkpoint D must then verify the real-data dashboard/indicators through the same qualified canonical series; it is not claimed from synthetic tests. No strategy, GTT, paper trading, holdings/balance synchronization, trading or scheduled refresh is implemented or authorized.


## 8. Exact proposed cumulative Git checkpoint

**33 files: 14 modified and 19 new. Nothing staged or committed.** This includes the twelve carried-forward Step 5D.1 files, plus this authorized increment. The count is relative to HEAD, not a claim that all files originated in Step 5D.2. No .env, credentials/account identifiers, backups/database exports, price data files, generated builds, test traces or diagnostic artifacts are included. The JSON plan contains only reviewed scheduling/configuration metadata, not market prices.

Modified:

- `backend/app/config.py`
- `backend/app/dhan_diagnostic.py`
- `backend/app/dhan_history_diagnostic.py`
- `backend/app/ingestion.py`
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/queries.py`
- `backend/app/schemas.py`
- `backend/tests/test_integration.py`
- `docs/04-planning/VS-01_DATA_QUALIFICATION.md`
- `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md`
- `frontend/src/App.test.tsx`
- `frontend/src/App.tsx`
- `frontend/src/ResearchShared.tsx`

New:

- `backend/app/acquisition.py`
- `backend/app/daily_values.py`
- `backend/app/dhan_history_contract.py`
- `backend/app/dhan_http.py`
- `backend/app/dhan_import.py`
- `backend/app/dhan_provider.py`
- `backend/app/market_data.py`
- `backend/app/provider_ingestion.py`
- `backend/migrations/versions/0002_provider_ingestion.py`
- `backend/tests/provider_fixtures.py`
- `backend/tests/seed_provider_browser.py`
- `backend/tests/test_acquisition.py`
- `backend/tests/test_dhan_provider.py`
- `backend/tests/test_dhan_provider_integration.py`
- `backend/tests/test_provider_ingestion.py`
- `docs/04-planning/VS-01_STEP5D1_PROVIDER_ADAPTER_CHECKPOINT.md`
- `docs/04-planning/VS-01_STEP5D2_HISTORY_INGESTION_CHECKPOINT.md`
- `docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json`
- `frontend/e2e/provider.spec.ts`

Proposed commit message: `feat(vs01): add bounded DhanHQ history acquisition and ingestion`.

Current branch `main`; HEAD remains `ef0a7c460ec82ce3797da37cded883ec82553871`. Requirements/project-context content still matches `requirements-v1.0`; its annotated object/target and all existing tags remain unchanged. Mathematical engines, dependency locks and Compose/image references are unchanged. Review the cumulative implementation before authorizing a commit; no commit/tag or full VS-01 acceptance is created by this checkpoint.
