# VS-01 Detailed Design - Gold/Silver ETF Research Dashboard

**Version/date:** 0.1 - Proposed; 2026-11-01 (Asia/Calcutta).  
**Authority:** Human Step 2 architecture/design task; documentation only.  
**Baseline:** [REQ-BL-1.0](../01-requirements/REQUIREMENTS_BASELINE.md), annotated tag `requirements-v1.0`, commit `e10eef55fb21368e53dbe4599006b620cbb48566`. Tag and unchanged source content verified before authoring.  
**Status:** Architecture/design recommendations are Proposed. No baseline requirement status, maturity, priority, applicability or increment is changed. No implementation or spike is authorized.

## 1. Scope and contract authority

VS-01 implements ten capabilities in the [traceability/readiness matrix](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#readiness). It is a cross-cutting research slice, not complete R1-A/B/C. Portfolio capital, trading rules, recommendations/GTT, strategy backtests, paper orders, manual transactions, LLM integration, scheduled reports and live/provider network adapters are excluded.

All DC contracts and architecture decisions remain Proposed. They elaborate requirements without changing the frozen 117-item inventory. Formula research is not a trade signal. No app, database, API, UI, test or infrastructure code is created by this document.

| Contract | Purpose | Primary architecture decisions |
| --- | --- | --- |
| [DC-01](#dc-01) | Listing identity and watchlists | ADR-01/02/03 |
| [DC-02](#dc-02) | CSV/source adapter input | ADR-04/05 |
| [DC-03](#dc-03) | Persistence and atomic idempotence | ADR-03/04/05 |
| [DC-04](#dc-04) | Provenance, calendar, quality and freshness | ADR-05/10 |
| [DC-05](#dc-05) | Deterministic indicator mathematics | ADR-06/10 |
| [DC-06](#dc-06) | ETF price-only comparisons | ADR-07/10 |
| [DC-07](#dc-07) | REST and common schemas | ADR-02/04/05 |
| [DC-08](#dc-08) | Dashboard workflows/components | ADR-02/07 |
| [DC-09](#dc-09) | Local security, operations and reproducibility | ADR-08/09 |

<a id="dc-01"></a>

## DC-01 - Instruments and watchlists

**Proposed scope:** one local owner can create/edit a named watchlist and add/remove explicit Indian Gold or Silver ETF listings. Removing membership does not delete market history.

Instrument identity:
- UUID instrument_id; explicit symbol + exchange code + currency; metal GOLD/SILVER; human-readable name.
- Unique (exchange, symbol). Accept only explicitly supported Indian exchange metadata; source mapping must use the same listing. An ISIN is optional until verified, never guessed or substituted for a listing.
- INR is the proposed initial quoted currency. No FX conversion in VS-01.
- Financial identity fields become immutable after observations exist. Display-name/active flags can change; historical relisting/currency change needs a separately designed identity change.
- No initial ticker set is invented. SQ-01 identifies the actual acceptance instruments/data; tests use labeled fictitious instrument fixtures.
- Watchlist IDs and membership persist; gold/silver filter changes only the view, not the stored instrument classification.

Parent requirements include Approved REQ-01-001/003 and REQ-04-001, but REQ-01-008 and precise identity contracts remain unresolved. User selection/configuration is not an investment endorsement.

<a id="dc-02"></a>

## DC-02 - CSV and acquisition contract

**Initial adapter:** bounded UTF-8 CSV, optional BOM, comma delimiter, one listing/source/price basis per file, daily observations only. No archive, URL, executable, automatic provider login or heuristic format detection.

### Request profile

Required metadata: instrument_id, source_id, interval=1d, price_basis, mapping_version, column_map, quality_policy_version, and source-use qualification reference. Transport uses an Idempotency-Key UUID. Hash the original bytes plus a canonical metadata/profile representation separately; their combination defines request identity.

Column mapping is a finite field-to-header map, not code or expressions. Dates are ISO YYYY-MM-DD; decimals use a dot without thousands separators; unexpected/unmapped columns are rejected rather than retained. An owner can prepare a canonical file or approve a concrete mapping after inspecting an actual export.

| Canonical field | Required / meaning | Validation |
| --- | --- | --- |
| trading_date | Required; exchange session date | ISO date; no inferred event time. |
| close | Required; ETF per-unit closing value | Finite positive decimal, exactly representable within NUMERIC(24,10); excess precision/range rejected, not silently rounded. |
| open/high/low | Optional complete trio | If present, positive and coherent with close: high >= max(open,low,close), low <= min(open,high,close). Same declared price basis. |
| volume | Optional | Nonnegative integer in BIGINT range; absent is null, never zero. |
| symbol / currency | Optional redundant columns | Must equal selected listing/currency if supplied. |
| provider_published_at | Optional | Timezone-bearing instant only when supplied by source; otherwise null with unknown reason. |
| event_time | Optional | Explicit supplied instant with precision metadata; otherwise session date only. |

price_basis is RAW_CLOSE / PROVIDER_ADJUSTED / UNKNOWN. UNKNOWN may be stored/displayed with warnings, but derived metrics are unavailable until a basis is established. Provider-adjusted fields require an attributable adjustment definition; do not mix raw OHLC with adjusted close. Raw-only corporate-action uncertainty is disclosed, not repaired by invented adjustments.

A source is UNVERIFIED, QUALIFIED_FOR_RESEARCH or RESTRICTED. Human-recorded qualification identifies evidence and permitted retrieval/storage/analysis/display uses; it is not automatic legal verification. Imports require qualification for those uses and an approved retention profile. No provider is qualified by this document.

The provider-independent adapter interface accepts bytes + identity/profile and emits canonical candidates + safe mapped raw values + validation issues. It performs no financial analysis. A future network adapter must satisfy the same contract after separate approval; it is not implemented in VS-01.

<a id="dc-03"></a>

## DC-03 - Persistence and import integrity

PostgreSQL is an accepted baseline constraint; the schema/access design below is Proposed. Eight persistent tables are sufficient; no indicator cache, order, position, job or AI tables.

| Entity | Required fields and types | Keys / constraints / relationships |
| --- | --- | --- |
| instruments | id UUID; exchange/symbol/name text; metal enum; currency text; isin nullable text; active bool; data_revision BIGINT; created_at/updated_at timestamptz | PK id; unique(exchange,symbol); GOLD/SILVER, initial INR; revision nonnegative. Identity immutable after history. |
| data_sources | id UUID; label text; source_kind USER_CSV; qualification enum; rights_evidence_ref text nullable; permitted_uses JSONB; reviewed_at nullable timestamptz; contract_version text; quality/calendar profile JSONB | PK id; qualifying uses/evidence required before permitted import. Profile is versioned/snapshotted, not executable code. |
| import_batches | id UUID; request_key UUID; instrument_id/source_id UUID; file_sha256/profile_sha256 char(64); profile_snapshot JSONB; status enum; bytes/row/count fields BIGINT; sanitized_name nullable text; submitted_at/finished_at timestamptz; request_id text; error_code nullable text | PK id; unique(request_key); FKs instrument/source; unique(id,instrument_id,source_id) supports matching child FKs. Counts nonnegative; terminal status ACCEPTED/NO_CHANGE/REJECTED/FAILED. |
| import_rows | batch_id UUID; row_number BIGINT; mapped_raw JSONB; canonical_hash nullable char(64) | PK(batch_id,row_number); row_number positive; FK batch. No extra account columns/full local file paths retained. |
| price_observations | id UUID; instrument_id/source_id UUID; trading_date date; interval 1d; price_basis enum; close/open/high/low NUMERIC(24,10); volume nullable BIGINT; event_time nullable timestamptz; event_precision enum; provider_published_at nullable timestamptz; ingested_at timestamptz; batch_id/row_number; canonical_hash char(64) | PK id; unique(instrument_id,source_id,trading_date,interval,price_basis); unique(batch_id,row_number); required identity/key fields NOT NULL. FK(batch_id,row_number) -> import_rows and composite FK to matching batch/source/instrument. Finite-positive-price/OHLC/volume checks, explicitly excluding numeric NaN/infinity. Accepted observations immutable. |
| quality_results | id UUID; batch_id UUID; row_number nullable BIGINT; code/severity text; details JSONB; assessed_at timestamptz | PK id; FK batch; composite FK to mapped row when row-level. Severity ERROR/WARN/INFO/UNASSESSED; sanitized bounded details. |
| watchlists | id UUID; name text; created_at/updated_at timestamptz | PK id; nonempty unique name for single owner. |
| watchlist_members | watchlist_id/instrument_id UUID; added_at timestamptz | Composite PK and FKs; remove membership only, not source/history. |

Use indexes on (instrument_id,source_id,interval,price_basis,trading_date), batch submitted_at/id, and quality(batch_id,row_number). Scope is daily data, not a generalized time-series platform. Audit-retention and source deletion policy is not inferred from FK cascades; no hard-delete observation endpoint.

### Transaction and duplicate semantics

1. Authenticate, bound/parse file, validate profile and qualification. Recognized structural failures retain only safe batch diagnostics when source/identity and storage are available.
2. Begin a bounded transaction; hold a source-policy read lock and per-instrument write lock. Recheck source permission/profile and request identity.
3. Build safe mapped audit rows and validate all candidates/existing observation keys before any price insert.
4. Exact canonical duplicate: skip it. Canonical hash includes values and supplied temporal/provenance fields in the declared profile; equal price with conflicting provenance is not silently enriched.
5. Conflicting same-key candidate, conflicting duplicates inside the file or any hard row error: commit REJECTED batch/rows/issues with **zero new observations**.
6. Otherwise insert all new observations, retain original provenance, increment data_revision only if new rows exist, and commit ACCEPTED or NO_CHANGE audit.
7. Unexpected database failures roll back the transaction. Record FAILED separately only when rollback is confirmed and storage is usable. Commit-outcome uncertainty returns a retriable request key, not an invented failed/success state.
8. Reusing a request key with different bytes/profile is 409. Successful exact replay is 200 with the original result; replay of rejection preserves its original error/status and batch ID. A new request key/reordered equivalent file can create a new audit attempt but not duplicate observations.
9. Resolve unique-key races by reading the committed original and comparing identity. No pending-job state, automatic retry worker or silent correction path.

Read history/analytics under a consistent read-only snapshot. Return instrument revision and source/profile identity; pagination rejects changed snapshots. VS-01 does not promise querying an arbitrary old revision. Provider corrections require a later explicitly approved revision contract; conflicts are actionable errors now.

Calendar/session and adjustment evidence can be supplied in the versioned source profile; there is no guessed holiday table. Profile snapshots retain evidence reference/version and declared dates/policies. Only approved source-use rights permit retaining raw mapped rows. PostgreSQL dump/restore includes these rows and metadata, not an external raw-file dependency.

<a id="dc-04"></a>

## DC-04 - Time, quality and freshness policies

| Condition | Proposed import/read behavior |
| --- | --- |
| Missing required date/close, nonfinite/nonpositive price, excess numeric scale, incoherent OHLC | Hard error; reject whole new-observation set. |
| Unknown instrument, currency mismatch, unsupported interval | Hard error; never guess, convert or resample. |
| Duplicate same canonical values | Skip and report count; revision unchanged if no new rows. |
| Duplicate conflict | Reject; no overwrite or last-writer-wins. |
| Out-of-order valid rows | Normalize to chronological order; retain original row number. |
| Non-trading date | Reject when a qualified calendar proves it; if calendar unknown, record UNASSESSED rather than inventing a holiday/session. |
| Missing expected trading session | Record gap; never fill. Known gap breaks the indicator segment. |
| Unknown calendar | Show contiguity UNVERIFIED; proposed research mode counts observed bars, never claims complete daily-session coverage. |
| Known unadjusted corporate-action discontinuity | Break derived segment; disclose action/basis limitation. No automatic split/dividend adjustment. |
| Unknown corporate-action coverage | Warn UNASSESSED; raw-price research is not total return or validated strategy performance. |
| Missing provider publication/event instant | Null + reason; session date retained. No invented midnight/close/publication timestamp. |
| Staleness | With an approved profile, compare last available session against its expected latest session; otherwise UNASSESSED. No default age threshold/cutoff. |

Temporal schema separates event_date/precision, optional event_time, optional provider_published_at, ingested_at, and computed_at. Server instants are UTC; exchange timezone is explicit IANA metadata. Source files lacking original availability/vintages are UNVERIFIED_FOR_REPLAY even when present-day research is permitted.

Source policy shape: {policy_version, calendar:{evidence_ref,version,coverage_start,coverage_end,session_dates}|null, known_break_dates:[], adjustment_definition_ref|null, freshness:{evidence_ref,assessment_as_of,expected_latest_session}|null}. Validate all dates and references; snapshot this policy in the batch. A supplied freshness assessment applies only to its explicit as-of context; if the API cannot establish a valid expected session for the requested assessment, return UNASSESSED rather than extending an old assessment to now. No executable policy expressions or guessed publication lag.

History metadata separates dataset_last_date from range_last_date; requesting an old chart window must not alone mark the entire dataset stale. Freshness includes assessment_as_of, expected_latest_date when known, actual_latest_date, policy_version and FRESH/STALE/UNASSESSED with reasons. Quality is issue counts/flags, not an invented score or confidence percentage.

Missing sessions are assessed only between observed endpoints within qualified calendar coverage; no pre-inception or out-of-coverage prices are inferred. Provider daily-bar timestamp labels are not treated as actual trade instants without a verified mapping.

Known hard discontinuities reset recursive indicator seeding; unknown continuity is visibly unverified. These research policies require SQ-03 approval and do not settle future strategy/backtesting quality gates.

<a id="dc-05"></a>

## DC-05 - Pure deterministic indicator framework

### Inputs, precision and outputs

Inputs: explicit SeriesRef(instrument_id,source_id,interval=1d,price_basis,revision,profile_digest), ordered eligible closes with observation IDs/hashes, segment breaks, requested date range, and required integer n. No implicit period. Proposed technical bound n <= 10,000; n >= 1.

Use a local Decimal context of precision **34**, ROUND_HALF_EVEN and exact parsed decimal inputs; do not mutate a process-global arithmetic context. Proposed derived wire values are decimal strings quantized to **12 fractional places**, negative zero normalized to zero. Compare independent exact-rational/reference wire values, not LLM answers. These are Proposed computation conventions requiring approval, not trading thresholds. Price storage retains source precision up to its declared DB scale.

Each result: indicator_id, algorithm_version, n/window_unit=OBSERVED_BARS, SeriesRef, source/batch evidence references, seed_date, computed_at, input_fingerprint, values[{trading_date,value|null,reason}], and quality/continuity/adjustment limitations. No NaN/Infinity in JSON.

Application orchestration stamps computed_at; the pure engine receives values/parameters and returns numbers/reasons without DB/network/clock. Fingerprint v1 uses canonical UTF-8 JSON with stable keys/order and exact decimal strings over input identities/hashes, series/profile version, algorithm version and parameters; excludes computed_at.

### Proposed mathematical definitions

Let C_t be the eligible close at ordered index t inside a segment.

| Indicator | Definition / purpose | Minimum data and initialization |
| --- | --- | --- |
| SMA(n) | SMA_t = sum(C_(t-n+1)..C_t)/n; descriptive smoothing | n closes; earlier values null WARMUP. |
| EMA(n) | alpha=2/(n+1); seed E_(n-1)=SMA of first n closes; E_t=alpha*C_t+(1-alpha)*E_(t-1) | n closes to seed; no alternative first-close seed. |
| Wilder RSI(n) | delta_t=C_t-C_(t-1); gain=max(delta,0), loss=max(-delta,0); initial G/L are means of first n deltas; later G_t=((n-1)*G_(t-1)+gain_t)/n and likewise L; RSI=100-100/(1+G/L) | n+1 closes to seed. If L=0 and G>0 ->100; G=0 and L>0 ->0; both zero ->null FLAT_WINDOW, not an invented neutral value. |

Purpose is research visualization; no RSI buy/sell threshold, trend recommendation or default n is selected.

### Range, gaps and unavailable behavior

- Seed EMA/RSI from the beginning of the eligible segment, not the visible chart start. Fetch the required complete prefix; changing only display range must not change overlapping values.
- A known missing session/unadjusted action break restarts the segment and warm-up. Missing closes are not imputed.
- Unknown calendar permits explicitly labeled observation-count research under DC-04; do not claim session completeness.
- Unknown price basis returns BASIS_UNVERIFIED for derived values. Insufficient rows -> WARMUP/INSUFFICIENT_HISTORY; known break -> DISCONTINUITY/WARMUP as applicable.
- If the prefix/resource limit is exceeded, return ANALYTICS_RANGE_LIMIT; do not truncate/change seed silently.
- Late earlier history can change a segment seed; changed data_revision/input fingerprint makes that change attributable.
- Decimal arithmetic failure/out-of-range result -> NUMERIC_UNSUPPORTED with no fabricated value.
- Validate formulas against separately authored Fraction/rational examples plus higher-precision decimal arithmetic; optional third-party comparisons must reconcile initialization and flat-window differences. No TA-Lib runtime dependency is required.

Unit/reference cases are VS01-T-11..14. These calculations are not strategy backtests, predictive probabilities or portfolio performance.

<a id="dc-06"></a>

## DC-06 - Supported ETF comparison metrics

Each selected instrument has an explicit source/price basis/revision. Require same currency and compatible declared basis; no FX conversion or silent vendor blend. Use the intersection of observed eligible dates within the requested inclusive range. No forward fill or interpolation.

Supported research metrics:
- Close on common ending date and reported daily volume on that date when available.
- Price change percent = 100*(C_end/C_start - 1), using the actual common endpoints.
- Rebased chart level = 100*C_t/C_start on the common observed dates. Base 100 is a display normalization, not an investment assumption.
- Coverage count, effective common start/end, dataset freshness/quality and unavailable metric reasons.

At least two common dates are needed for a change-over-period result. One date can show closes but change is unavailable INSUFFICIENT_COMMON_DATES. No overlap -> NO_COMMON_DATES; incompatible basis/currency -> comparison unavailable with explicit reason.

Raw/unverified adjustment history cannot support a total-return, tracking-difference, NAV premium/discount, spread, executable-liquidity or fund-quality ranking claim. Adjusted price change is still labeled by its source definition, not automatically total return. Volume is an observation, not a guaranteed fill/liquidity score. No gold/silver exposure ratio is inferred from ETF unit prices.

Decimal precision/serialization follows DC-05. Return endpoint dates, method/version, each SeriesRef/input fingerprint, flags and computed_at. Browser renders these results; it does not independently recompute returns.

<a id="dc-07"></a>

## DC-07 - Minimum REST API contracts

Prefix **/api/v1**. JSON fields use snake_case; IDs UUID; dates ISO YYYY-MM-DD; instants UTC ISO-8601; prices/derived decimals strings; volume integer|null. Reject undeclared request fields. Successful research responses include request_id, served_at and data/meta; errors use the shared envelope below.

### Common envelopes

| Shape | Required fields |
| --- | --- |
| Research response | data; meta {request_id,served_at,SeriesRef or per-series refs,coverage,quality,freshness,limitations}; page info when paginated |
| Batch response | batch_id,status,new_count,duplicate_count,error_count,source/profile/file hashes,revision when applicable; issues and request_id |
| Calculation response | indicator/metric version,parameters,seed/effective endpoints,values/unavailable reasons,input fingerprint,computed_at and research metadata |
| Error | error {code,message,request_id,details[{field?,row_number?,code}]}; batch_id/request_key when available; no stack/raw input/secrets |

### Endpoint inventory

| Method / path | Request / validation | Response and errors |
| --- | --- | --- |
| GET /health/live | No sensitive payload; public loopback health only | 200 process status; no secret/config dump. |
| GET /health/ready | Local access; schema revision and DB usable | 200 ready or 503 DEPENDENCY_NOT_READY. |
| GET /instruments | metal?,cursor?,limit? | Paginated listing metadata; 422 invalid filter/cursor. |
| POST /instruments | DC-01 identity/name/metal/currency | 201 Instrument; 409 duplicate listing; 422 unsupported metadata. |
| PATCH /instruments/{id} | display name/active only after history | 200 Instrument; 404 unknown; 409 immutable identity change. |
| GET /watchlists; POST /watchlists | POST nonempty name | List or 201 Watchlist; 409 duplicate name. |
| GET/PATCH /watchlists/{id} | PATCH name only | Watchlist/members or 404/409. |
| POST /watchlists/{id}/members | instrument_id | 201 member or 200 existing; 404 invalid IDs. |
| DELETE /watchlists/{id}/members/{instrument_id} | Membership identity | 204; idempotent; market data not deleted. |
| GET /data-sources; POST /data-sources | POST label and declared source contract | Sources or 201 UNVERIFIED source; does not grant data rights. |
| PATCH /data-sources/{id}/qualification | Explicit owner review, evidence ref, uses, versioned policy | 200 recorded qualification; 422 missing evidence/uses. Human record is not third-party legal verification. |
| POST /import-batches | Multipart file + metadata_json; required Idempotency-Key UUID; DC-02 | 201 new ACCEPTED/NO_CHANGE; 200 successful replay; 422 invalid CSV; 409 conflict/key misuse; 403 unqualified source; 413 size; 415 type. Rejected replay preserves original status. |
| GET /import-batches | source_id?/instrument_id?,cursor?,limit? | Paginated terminal audit summaries, including rejected imports; no raw file dump. |
| GET /import-batches/{id} | Batch UUID | Summary/profile/issue counts; 404. |
| GET /import-batches/by-key/{key} | Request UUID; route must precede generic {id} matching | Original terminal result or 404 NOT_RECORDED; permits uncertain-commit resolution. |
| GET /import-batches/{id}/issues | cursor?,limit?,severity? | Paginated safe diagnostics, original row numbers; 404/422. |
| GET /instruments/{id}/history | source_id,basis,interval=1d,start,end,cursor?,limit? | Ordered observations and full research meta; 404 unknown; 422 invalid range; 409 SNAPSHOT_CHANGED. |
| GET /instruments/{id}/quality | Explicit source/basis and optional range | Quality/freshness/coverage with policy evidence; unknown stays unassessed. |
| GET /instruments/{id}/indicators | Same SeriesRef selectors, start/end, indicator=SMA/EMA/RSI,n | Defined outputs/reasons; 422 unsupported indicator/parameter or resource limit; source/basis/gap handling per DC-04/05. |
| POST /comparisons | 2 or more explicit series, start/end; bounded list | DC-06 table/series/meta or unavailable reasons; 422 incompatible currency/basis/invalid selectors. |

All data endpoints require the local token; state-changing endpoints also enforce exact origin/host and input rules. Allow only validated local-origin OPTIONS preflights without a bearer token; actual requests still authenticate. State-changing API tests/clients supply the approved Origin explicitly. No order, broker, portfolio, LLM, background scheduler, delete-history or arbitrary SQL endpoint.

Pagination is opaque keyset cursor, stable date+ID for history and submitted_at+ID for imports. Cursor encodes query identity and revision/profile digest; mismatch returns 409, not interleaved pages. List limits default 100 and max 1,000 (Proposed technical bounds). No full-series truncation under the guise of pagination.

Proposed finite resource safeguards: upload <=10 MiB, <=100,000 rows; analytical prefix <=10,000 points per series; comparison <=10 series. These are configurable technical abuse/memory bounds, not financial quality thresholds. Source-derived stale/cutoff policy has no invented numerical default. Changing any limit must preserve explicit errors rather than silent data loss.

Dates are inclusive at this API boundary; future adapters translate external provider boundary conventions explicitly. A record's absent publication timestamp cannot be inferred from an inclusive query.

<a id="dc-08"></a>

## DC-08 - User journeys and component responsibilities

| Journey | Proposed interaction / states |
| --- | --- |
| Open dashboard | Enter local session token; load watchlists and data readiness. First run is an honest empty state with setup/import actions, not fabricated charts. |
| Select Gold/Silver ETFs | Metal filter plus watchlist/listing selection; show exchange/currency/source/basis. Persist membership; no hardcoded recommended ETFs. |
| Import history | Select explicit source/listing/mapping/basis; show qualification/format requirements; upload once; inspect outcome and row issues. Retrying uses the same request key if identity is unchanged. |
| View history | Select date window; fetch typed history; line chart plus data table; show last dataset/range dates and provenance. No source autofallback. |
| Configure indicators | Select indicator and enter n; request server calculation; display overlays/reasons, seed and data revision; never buy/sell labels. |
| Compare ETFs | Select explicit series; show actual shared endpoints and price-only metrics, with basis/currency/gap limitations. |
| Inspect quality | Open batch and series issues, duplicate/rejection counts, unknown calendar/publication/adjustments, and stale/unassessed policy details. |

Proposed components: AppShell/LocalAccessGate, WatchlistPanel, InstrumentSelector, SourceProfilePanel, ImportForm, ImportResult/IssueTable, HistoryChart, IndicatorControls, ComparisonPanel, ProvenancePanel, QualityBanner, EmptyState and ErrorNotice. Small API client + typed hooks own transport/loading/cancellation; financial math stays backend-only.

Every data panel supports loading, empty, error, stale and unavailable states. Unknown freshness is UNASSESSED, not FRESH. Keep the previous result visibly outdated/disabled during selection changes or clear it; never show a delayed response under a different selected ETF. Cancel/ignore obsolete requests by query identity/revision.

Charts provide keyboard-readable controls and a table alternative. Imported strings render as escaped text, never injected HTML/formulas. No signal cards, order buttons or future-page scaffolds in VS-01.

<a id="dc-09"></a>

## DC-09 - Security, reliability and local reproducibility

**Proposed boundary:** one local owner on a trusted machine, loopback UI/API, PostgreSQL private to the Compose network. No internet/LAN hosting, user management service, external AI call or broker connection.

- LOCAL_APP_TOKEN is generated/set locally after implementation authorization; backend configuration is uncommitted. UI requests it from the owner into memory only, not VITE/public build variables, URLs, browser persistence or logs. Token equality uses an appropriate constant-time check in the eventual implementation.
- Exact allowed origins/hosts; bearer header required for data calls. A malicious web page's simple form request must fail authentication even if CORS would block reading its response.
- CSV type/size/row/field validation before expensive work; no archive extraction, filesystem path use, remote fetch or dynamic transformation code. Database statements use bound parameters.
- Retain only qualified mapped market inputs; evidence references are plain text unless a validated http(s) link is explicitly supported, never remotely fetched; sanitize display filenames; errors/logs exclude tokens, raw uploads, account identifiers and stack traces. Restricted source rights stop affected reads/imports under approved policy.
- Structured logs: request/batch IDs, event code, outcome/counts, versions and durations; no need for a separate observability service. Health separates process alive from migrated DB ready.
- Alembic migration revision must match the API's expected schema; initial migrations reviewed before execution. No automatic destructive reset. Integration tests run against disposable PostgreSQL, not the personal database.
- Proposed canonical runtime is Compose UI/API/PostgreSQL, DB health -> one-shot migration -> API readiness -> usable UI. Bind only UI/API loopback ports; no exposed DB port. Persistent named volume is preserved across normal restarts.
- Dependency/runtime/browser/image versions are locked and recorded when the approved work starts. Do not use floating versions as the reproducibility contract. No dependencies, images or browser binaries are installed now.
- Backup/restore: export PostgreSQL to an owner-controlled, permission-restricted location; restore to a separate empty database; verify schema, row counts, source/batch/quality links and known-query outputs before any switch. No unapproved RPO/RTO, retention duration or cloud backup chosen.
- Local tests use explicit fixture databases/clocks. Synthetic prices are labeled test data; real-source acceptance uses permitted samples separately and excludes secrets/personal data from Git.
- Unknown DB commit outcome is resolved using the same request key; no unsupported job engine, automatic corrections or silent retry changes.

See [acceptance plan](VS-01_ACCEPTANCE_AND_TEST_PLAN.md) for executable evidence expectations and [planning approval package](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#approval-package). The design may be reviewed now; implementation remains blocked pending the explicitly identified approvals.
