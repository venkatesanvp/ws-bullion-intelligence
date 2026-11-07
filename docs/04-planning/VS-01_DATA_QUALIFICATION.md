# VS-01 real ETF dataset qualification

Status as of Step 5D.4: **SQ-01 Open; VS01-T-03 partially technically evidenced, not accepted.** Real owner-authorized transient DhanHQ observations now support engineer verification, while deterministic regressions/recovery use clearly labelled SYNTHETIC_TEST fixtures. Persistent retention, full source qualification and owner acceptance remain unresolved. Earlier task-specific statements below are historical.

Trace: scoped REQ-01-008, REQ-02-007/008/011/012/013/014/015; ADR-04/05; DC-01..04; WI-04/05/09/11 and SQ-01. This checklist elaborates required evidence; it does not grant source rights or change a baseline status.

## Minimum qualification package

| Area | Required information/evidence |
| --- | --- |
| Source and permission | Provider/source name, origin of the exact file, acquisition method/date, applicable license/terms or permission evidence and reviewer/date. Explicitly assess retrieval, local storage, analysis and display, plus retention/deletion, permitted personal-use scope and any redistribution restrictions. A public download link or Dhan/Yahoo name alone is insufficient. |
| Listing identity | At least independently identified Gold and Silver ETF samples for full T-03: exchange MIC (XNSE/XBOM), exact symbol, display name, metal, INR currency and verified ISIN if available. Record listing changes; never infer financial identity from a similar name. |
| Coverage | Actual date bounds, daily frequency, row count, coverage omissions and known listing/inception changes. State the timezone and what each source date/timestamp means. Do not choose a required lookback or claim complete coverage without approval/evidence. |
| Price definition | Explicit RAW_CLOSE, PROVIDER_ADJUSTED or UNKNOWN, units and source definition. Adjusted imports need an adjustment-definition reference and corporate-action coverage; do not relabel raw changes as total return. |
| File/schema | Original file checksum, encoding, filename, headers and explicit canonical-to-file mapping. Required trading_date and close; optional coherent OHLC, volume, symbol/currency and publication/event instants. Supply a minimal permitted sample for inspection; remove unrelated account/personal columns. |
| Time/quality limitations | Actual publication/availability metadata if available; otherwise null/unknown and UNVERIFIED_FOR_REPLAY. Calendar/version/coverage/session evidence and any freshness policy must be explicit; otherwise UNASSESSED. Identify known breaks/actions, duplicates, corrections, missing sessions and provider revisions. |
| Acceptance evidence | Review sample against the claimed provider/listings; record mapping and rights dispositions; import in an authorized environment and inspect counts, rejected rows, exact decimals, dates, raw/batch/source provenance and quality disclosures. Keep source rights and technical validity as separate decisions. |

## Existing application workflow

Registering a source starts UNVERIFIED. The source review records rights and retention references, four permitted uses, classification and a quality profile. QUALIFIED_FOR_RESEARCH requires these assertions; imports also require matching evidence/profile version, explicit listing/source/basis and exact header mapping. Restricted or unqualified sources cannot supply history/imports. Classification cannot be changed to relabel existing synthetic history.

The application records the owner's review; it does not independently verify a license, market prices or ETF identity. Referenced evidence is not fetched automatically. Contract-valid synthetic files exercise parsing and controls but cannot satisfy real-data acceptance. Historical ingestion time does not prove historical market availability.

Next data action: obtain the owner's permitted qualification package, inspect it, and record a concrete SQ-01 disposition before real ingestion. Preserve this blocker if the information is unavailable. The Step 4 indicator/chart/comparison approval does not waive it. Technical synthetic verification of those capabilities is complete; SQ-01/T-03 remain blocked.

## Step 5D.2 provider acquisition counterpart

The bounded provider path extends the file-oriented checklist without requiring retention of raw API responses. For provider imports, record the reviewed plan/listing/calendar identity, canonical-payload and profile digests, actual request/retrieval provenance, validated row source timestamps and quality limitations in the existing import audit. Raw responses and invalid payloads are not archived. CSV file checksum/mapping requirements remain unchanged for CSV imports.

The [Step 5D.2 checkpoint](VS-01_STEP5D2_HISTORY_INGESTION_CHECKPOINT.md) implements this path offline and presents a four-request, one-year transient preflight for review. It does not qualify a live dataset or establish persistent-use/retention rights. A provider source additionally records explicit review of provisional session dates; timestamp semantics remain unverified and matching dates alone do not prove adjustment compatibility or total return. SQ-01/T-03 remain blocked pending the real-source evidence and accepted observations. No live provider prices have been persisted.

## Step 5D.3 real-data technical evidence and transient disposition

Four owner-authorized historical requests returned HTTP 200 and 246 real daily observations per primary ETF (TATAGOLD, TATSILV, GOLDBEES, SILVERBEES), dated 2025-11-03 through 2026-10-30. Requested coverage remains 2025-11-02 through 2026-11-02; the latest scheduled session was not returned. Canonical schema/precision/OHLC/volume/order/duplicate checks passed; epoch/IST mapping matched the reviewed calendar but the full provider time contract remains provisional.

The running application now displays/analyzes these real observations through an explicitly owner-authorized **transient backend-memory** reader. No real prices were written to PostgreSQL/files. This is not a persistent source qualification or an automatic rights grant. Private storage/derived-use/backups/retention terms remain inconclusive; independent reconciliation, adjustment details, point-in-time vintages and owner acceptance are unresolved. SQ-01/T-03 are partially technically evidenced, not fully accepted. See the [Step 5D.3 real-data/UAT record](VS-01_STEP5D3_REAL_DATA_UAT_CHECKPOINT.md).


## Step 5D.4 standing transient acquisition disposition

The owner's 2026-11-06 operating grant permits read-only configured market-data acquisition without separate per-batch approval. The implementation uses that grant for missing/stale ranges, controlled RAM reuse and bounded verification, not as evidence of perpetual storage rights. Public Dhan terms still do not resolve account-applicable private database/backup/retention permission; live provider observations remain transient. The existing persistent-ingestion rights gate is unchanged.

Six bounded technical attempts produced five published validated batches (18 new observations); one attempt did not publish during view switching and its response is not retained. November 2-5 is now common to all four ETFs; November 6 is provider-pending under the documented T-1 policy. SILVERBEES also received two older dates outside the packaged calendar's reviewed coverage, explicitly UNASSESSED. Matching dates and valid OHLCV do not prove actual exchange-session convention, adjustment equivalence, independent price accuracy or total return.

The legacy-to-current RAM handoff preserved canonical fields, original observation/batch IDs and exposed batch evidence without a market-data file. Numeric source epochs were not available from the old read API and were not invented; migrated observations retain that limitation. New acquisitions retain actual adapter epoch evidence. Full timestamp contract, precise adjustment method, reconciliation and point-in-time/replay acceptance remain open, as do SQ-01/T-03 and owner UAT. See [current checkpoint](VS-01_STEP5D4_ON_DEMAND_DATA_CHECKPOINT.md) and [standing policy](../05-operations/MARKET_DATA_OPERATING_POLICY.md).
