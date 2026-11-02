# Step 5B - Gold and Silver ETF instrument qualification

Recorded 2 November 2026 (Asia/Calcutta), following committed Step 5A `e31f19289937225d6399fe9b91f0f381720854e6`. Authority: instrument identification, public documentation/terms review and request proposal only. The owner separately approved one unauthenticated instrument-master GET during this task. No historical request, trading/account call, automated collection or application implementation is authorized or performed. No commit/tag.

Trace: D-04/D-14/D-16; REQ-01-008, REQ-02-007/008/011/012/013/014/015, REQ-05-003/004 -> ADR-04/05/09, DC-01..04/09, WI-04/05/09/11 and SQ-01. Requirements classifications and approved calculations remain unchanged. This assessment does not mark a source QUALIFIED_FOR_RESEARCH or accept VS-01-T-03.

**Later Step 5C scope:** all four listings are primary research instruments, with Tata first in the fixed four-request proposal. The earlier two-request/alternative language below is a historical Step 5B proposal, superseded by [Step 5C](VS-01_STEP5C_HISTORICAL_DIAGNOSTIC_CHECKPOINT.md). No personal holdings are recorded here.

## 1. Identification and evidence

The proposed first pair is GOLDBEES/SILVERBEES, following the owner's candidate order and the existing Gold/Silver qualification plan. This is a technical sample selection, not an investment or liquidity recommendation. Tata's pair is verified as an alternative; it does not add requests to this proposal.

### Proposed first pair

| Field | Gold ETF | Silver ETF |
| --- | --- | --- |
| Verified ETF name | Nippon India ETF Gold BeES | Nippon India Silver ETF |
| Metal | Gold | Silver |
| Exchange / MIC / series | NSE / XNSE / EQ | NSE / XNSE / EQ |
| NSE symbol | GOLDBEES | SILVERBEES |
| ISIN | INF204KB17I5 | INF204KC1402 |
| Dhan security ID | 14428 | 8080 |
| Exchange segment | NSE_EQ | NSE_EQ |
| Instrument enum / subtype | EQUITY / ETF | EQUITY / ETF |
| Trading currency | INR, per exchange listing/rupee quotation convention | INR, per exchange listing/rupee quotation convention |
| Market price versus NAV | Exchange-traded ETF market prices; NAV/iNAV are separate series | Exchange-traded ETF market prices; NAV/iNAV are separate series |
| Proposed historical price basis | PROVIDER_ADJUSTED under Dhan's documented daily policy; exact treatment pending | PROVIDER_ADJUSTED under Dhan's documented daily policy; exact treatment pending |
| Source evidence | [Nippon issuer](https://etf.nipponindiaim.com/Funds/details/13), [NSE ISIN-change circular](https://archives.nseindia.com/content/circulars/CML42888.pdf), authorized Dhan master inspection below | [Nippon issuer](https://etf.nipponindiaim.com/Funds/details/2025), [NSE symbol-change circular](https://archives.nseindia.com/content/circulars/CML52187.pdf), authorized Dhan master inspection below |

### Tata alternatives

| Field | Gold ETF | Silver ETF |
| --- | --- | --- |
| Verified ETF name | Tata Gold Exchange Traded Fund | Tata Silver Exchange Traded Fund |
| Metal | Gold | Silver |
| Exchange / MIC / series | NSE / XNSE / EQ | NSE / XNSE / EQ |
| NSE symbol | TATAGOLD | **TATSILV**, correcting candidate TATASILV |
| ISIN | INF277KA1976 | INF277KA1984 |
| Dhan security ID | 21401 | 21428 |
| Exchange segment | NSE_EQ | NSE_EQ |
| Instrument enum / subtype | EQUITY / ETF | EQUITY / ETF |
| Trading currency | INR | INR |
| Market price versus NAV | Exchange-traded ETF market prices; NAV/iNAV separate | Exchange-traded ETF market prices; NAV/iNAV separate |
| Proposed historical price basis | PROVIDER_ADJUSTED, exact treatment pending | PROVIDER_ADJUSTED, exact treatment pending |
| Source evidence | [NSE listing circular](https://nsearchives.nseindia.com/content/circulars/CML60280.pdf), [Tata scheme summary](https://www.tatamutualfund.com/system/files/2026-04/Tata%20Gold%20Exchange%20Traded%20Fund_0.pdf), authorized Dhan master | [NSE listing circular](https://nsearchives.nseindia.com/content/circulars/CML60280.pdf), [Tata SID](https://www.tatamutualfund.com/system/files/2025-07/Tata%20Silver%20Exchange%20Traded%20Fund_2.pdf), authorized Dhan master |

NSE's Tata listing circular is effective 17 January 2024. Current NSE [Gold](https://www.nseindia.com/get-quote/equity/TATAGOLD/Tata-Mutual-Fund-Tata-Gold-Exchange-Traded-Fund) and [Silver](https://www.nseindia.com/get-quote/equity/TATSILV/Tata-Mutual-Fund-Tata-Silver-Exchange-Traded-Fund) listing evidence corroborates names/ISINs and rupee quotation. No displayed price is used or reproduced here. The master extract did not supply currency; INR is attributed to exchange/issuer evidence, not invented as a master field. No BSE mapping or price is substituted for NSE.

The Silver issuer page has an unrelated NIFTY Auto objective paragraph alongside its correct silver scheme type/philosophy and identifiers. It is not used as an objective authority. [Nippon's silver factsheet](https://mf.nipponindiaim.com/investorservices/factsheetsdocuments/fundamentals-february-2023/Innerpage/Silver-ETF.html) independently corroborates silver classification/ISIN; NSE corroborates the symbol change. This upstream content defect is recorded rather than propagated.

## 2. Approved Dhan master inspection and reconciliation

[Dhan's instrument documentation](https://dhanhq.co/docs/v2/instruments/) specifies the detailed public CSV. Exactly one owner-approved **GET https://images.dhan.co/api-data/api-scrip-master-detailed.csv** was made at **2026-11-02 07:20:05 UTC / 12:50:05 IST**. HTTP 200; one invocation; TLS verification, time/size bounds, no credentials, retries or redirects. The raw response was streamed/discarded, never saved. Only matching identifier metadata is reproduced in this assessment. Ignored local attempt evidence: `artifacts/step5b-instrument-master-attempt.json`.

All four ISINs matched exactly one NSE / E row, each with SERIES=EQ, INSTRUMENT=EQUITY and INSTRUMENT_TYPE=ETF. [Dhan's annexure](https://dhanhq.co/docs/v2/annexure/) maps NSE equity cash to NSE_EQ. The API instrument enum is **EQUITY**, not the subtype **ETF**. These values were inspected, not guessed from the trading symbols.

The initial harness's extra SYMBOL_NAME==short-symbol check returned false. Actual SYMBOL_NAME values are descriptive/legacy: `NIP IND ETF GOLD BEES`, `NIPPONAMC - NETFSILVER`, `TATAAML-TATAGOLD`, `TATAAML-TATSILV`. Dhan no longer documents a separate detailed trading-symbol column. Reconciliation uses exact ISIN + exchange + segment + series + ETF subtype, plus issuer/exchange evidence, rather than rewriting the raw observation or guessing a symbol. In particular, NSE documents NETFSILVER -> SILVERBEES effective 10 May 2022. No second master request was needed or made. The original false check remains in local evidence, with this disposition.

These are time-stamped mappings, not permanent identifiers or proof of historical bar availability. A raw-master checksum/version was not retained under this in-memory inspection scope; a later reproducibility policy must address permitted evidence retention separately.

## 3. Historical-data qualification: facts and gaps

| Area | Documented fact / current disposition |
| --- | --- |
| Eligibility | [Dhan support](https://dhan.co/support/platforms/dhanhq-api/are-data-apis-available-for-all-exchanges-and-segments-on-dhan/) covers historical daily data across exchanges/segments. Together with the four equity-cash ETF rows, this establishes technical candidates; actual per-ETF data remains untested. |
| Coverage | [Coverage FAQ](https://dhan.co/support/platforms/dhanhq-api/what-timeframe-data-is-available-through-dhan-s-historical-data-apis/) describes daily OHLCV from inception. It is not an independently verified completeness guarantee. The five-year intraday horizon and 90-day intraday request cap must not be presented as daily limits. No explicit daily request-span cap was found in the reviewed contract. |
| Price basis | [Corporate-action FAQ](https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/) confirms daily adjustments for splits/bonuses. This resolves the earlier general adjusted-versus-raw documentation gap: do not assign RAW_CLOSE. Exact ETF factors, OHLC/volume coherence, distributions, revision policy and raw-close alternative remain unspecified/unverified. Adjusted is not synonymous with total return. |
| Date/time | The [daily contract](https://dhanhq.co/docs/v2/historical-data/#daily-historical-data) specifies date strings, an exclusive toDate, OHLCV arrays and integer epoch timestamps. Timestamp unit/session-label timezone and whether a daily label denotes session open/close are not expressly established there. Unix seconds is an inference from examples, not a verified canonical mapping. Do not use host-local timezone or invent publication timestamps. |
| Availability/finality | [Latest-day FAQ](https://dhan.co/support/platforms/dhanhq-api/why-am-i-not-receiving-the-latest-day-s-data-from-the-daily-historical-data-api/) states previous-trading-day availability (T-1). No exact daily publication SLA or revision/finality guarantee is established. Historical retrieval time is not point-in-time availability. |
| Rate limits | [Official rate-limit table](https://dhanhq.co/docs/v2/#rate-limit): Data APIs 5 requests/second, 100,000/day; minute/hour caps not specified. Proposed requests are serial, at least one second apart, without retries or follow-ups. Account-wide concurrent usage must also fit quota. |
| NAV separation | Issuer NAV/iNAV is a different valuation series. The proposed exchange-candle request is for ETF market-price history; it does not request NAV, direct AMC subscription/redemption prices or physical-metal spot prices. |

## 4. Exactly two proposed requests - NOT EXECUTED

Use one Gold and one Silver only: **GOLDBEES / 14428** and **SILVERBEES / 8080**. Tata candidates are alternatives requiring a revised owner-reviewed request pair, not additional calls.

Common dates: **26, 27, 28, 29 and 30 October 2026** (Monday-Friday). These are five scheduled NSE capital-market sessions under [NSE/CMTR/71775, calendar 2026](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf); that calendar's October holidays are 2 and 20 October. This establishes calendar eligibility, not proof that each ETF has five returned bars or that no exceptional event/revision occurred. Actual bar dates/counts await approval. The current 2 November session is excluded, consistent with T-1 policy.

For each request: **POST https://api.dhan.co/v2/charts/historical**, JSON body; configured access-token in a header only; Content-Type application/json. No client-ID/key/secret in URL/body. No daily interval field. Optional expiryCode is omitted because these are non-derivative ETFs; oi=false explicitly excludes derivative open-interest requests. The endpoint contract explicitly makes toDate non-inclusive, so 2026-10-31 includes the intended Friday without requesting another trading session.

Gold body:

```json
{
  "securityId": "14428",
  "exchangeSegment": "NSE_EQ",
  "instrument": "EQUITY",
  "oi": false,
  "fromDate": "2026-10-26",
  "toDate": "2026-10-31"
}
```

Silver body:

```json
{
  "securityId": "8080",
  "exchangeSegment": "NSE_EQ",
  "instrument": "EQUITY",
  "oi": false,
  "fromDate": "2026-10-26",
  "toDate": "2026-10-31"
}
```

A later authorized diagnostic would inspect equal array lengths, five distinct expected dates, positive finite coherent OHLC, integer nonnegative volume, timestamp interpretation and clear provider-adjusted provenance. Parse price JSON as Decimal, with no authoritative binary-float calculation. Treat missing/extra dates, inconsistent units/adjustments or unexpected schema as failures/gaps; never fill or silently relabel data. In-memory schema checks are not independent market-price reconciliation. No response/price persistence, application import or database mutation is included in this initial proposal. Only safe status/count/validation summaries would be retained, with no token/account fields or price values.

## 5. Usage and retention disposition

[General Dhan terms](https://dhan.co/terms/) restrict extraction, publication, commercialization and unauthorized copying/derivative use. API capability and an active subscription do not establish this application's licence. The historical documentation's intraday-storage recommendation is technical guidance, not a complete retention/redistribution grant.

**Pending qualification:** obtain the account-applicable Data API agreement or provider-authorized written permission covering private API retrieval, local analysis, charts/derived indicators, local database/export/backups, retention/deletion, termination and redistribution restrictions. The review has not established a permitted retention period or unqualified personal-use exception. Distinguish an authorized licence decision from an informal technical-support statement. No account login, purchase or message to Dhan was made.

The proposed two-request in-memory trial also needs its permitted-use basis recorded; owner execution approval does not itself confer third-party rights. For later persistence, [existing qualification gates](VS-01_DATA_QUALIFICATION.md) still require four permitted-use assertions and retention evidence. Existing append-only observation/audit behavior and backups cannot promise automatic expiry deletion; reconcile any contractual deletion requirement before ingestion. No redistribution is proposed.

## 6. Remaining gaps and exact next approval

Instrument identity/mapping is verified for the four named NSE listings. The source remains unqualified for ingestion. Outstanding: applicable rights, exact adjustment definition/ETF treatment, timestamp/date and volume semantics, actual five-day endpoint/sample checks, independent permitted reconciliation, broader coverage/corporate-action evidence and SQ-01/T-03 acceptance. Five bars cannot validate longer-lookback SMA/EMA/RSI, replay correctness or full VS-01 acceptance. Owner-data recovery/retention/cutover and final human acceptance also remain open.

After recording an adequate permitted-use basis, the exact next authorization is: **allow at most two authenticated POSTs to https://api.dhan.co/v2/charts/historical with precisely the two bodies above, one per ETF, serial/no retries/no redirects/no fallback requests, transient inspection only and sanitized results only; no price/response persistence or ingestion.** A request-error/expired-token response stops the sequence and is reported; no automatic reauthentication or replacement call. Any adapter/code needed for that trial must be reviewed/mocked before live use under the next grant. Existing profile-only diagnostic is not extended in this task. A global enablement change, automated collection, additional master/profile/account call, broker operation or market-data storage is not authorized.

## 7. Workspace checkpoint

Only this assessment document is proposed as a new Git file. No application/configuration/dependency/calculation/schema/baseline file changes, staging, commit or tag. Actual credentials remain in ignored local configuration; the gate is false. The original Step 5A commit and requirements tag are preserved. Raw market/master responses are not Git artifacts. No new application tests or regression run is needed for this documentation-only assessment; the prior verified 242/16/3 test checkpoint is not presented as newly executed here.
