# VS-01 real ETF dataset qualification

Status: **SQ-01 Open; VS01-T-03 blocked.** No qualified real Gold/Silver ETF dataset has been supplied or accepted. Development/regression/recovery evidence uses SYNTHETIC_TEST only. No external ETF dataset was automatically downloaded, scraped or ingested in this task.

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
