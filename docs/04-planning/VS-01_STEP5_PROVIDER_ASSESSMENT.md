# VS-01 Step 5 - Provider assessment and qualification proposal

Date: **2 November 2026 (Asia/Calcutta)**. Reviewed checkpoint: `a244cfed5c4a30af5076f73a8bb2ce19d340ae0b`. Initial working tree clean. Requirements baseline, D-01..16, approved architecture and `requirements-v1.0` unchanged.

**For human review. No provider or real dataset is ingestion-approved. SQ-01/T-03 remain blocked.** The latest clarification confirms that no Gold/Silver files have been selected or downloaded; it supersedes the earlier multiple-choice indication that exports existed. This assessment uses public official documentation, not authenticated market-data requests or sample downloads. No account, subscription, provider connection or application change has been made.

## 1. Recommendation

**Primary technical candidate: DhanHQ Data APIs. Fallback: TrueData's licensed historical/EOD market-data service.** This is a recommendation to qualify them, not approval to acquire data. Dhan fits the daily OHLCV requirement and the earlier D-14 provider direction. Its documented historical interface gives a practical route from a small approved sample to later scheduled retrieval. Account/data-plan eligibility, storage/derived-analysis rights, actual ETF coverage and price basis still need verification. A data subscription alone does not resolve these gates.

TrueData is the fallback because a dedicated exchange-data provider offers a different operational acquisition route and an opportunity to obtain a clear single-user licence. Confirm that the actual product includes historical daily ETF data, export/storage, private analytics and automated requests; a desktop-feed subscription or appearance on a real-time vendor list does not establish those rights.

Use NSE-authorized records as the preferred reconciliation reference when access is permitted. Public NSE pages are not an unrestricted automated fallback. BSE is another venue with separate prices and identifiers. AMC/AMFI NAV is a separate valuation series. Kite Connect is technically suitable but its published permanent-copy restrictions are a significant qualification issue for this application's persisted PostgreSQL history.

No reliability or coverage ranking is based on executed provider tests. The recommendation weighs documented capabilities, provenance, current CSV compatibility and operational effort. The actual account, instruments, coverage, terms and samples remain to be qualified.

## 2. Provider assessment

All candidate market-price samples must establish INR **per ETF unit**, volume in traded units, exchange/session date and exact price definition. Neither physical-metal grams nor NAV is a substitute for an exchange close. Exact available first/last dates are **unverified for every candidate** until permitted files/responses are inspected; scheme inception is not proof of uninterrupted price history.

### A. NSE official historical reports and licensed EOD products

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | NSE's [historical report index](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives) explicitly directs ETF price/volume archives to security-wise reports. Select the actual NSE listing/series, not just a fund name. |
| Coverage / granularity | Daily report archives and [licensed EOD/historical products](https://www.nseindia.com/static/market-data/eod-historical-data-subscription). Exact per-ETF start/end/omissions unverified. Licensed EOD and order/trade products are distinct; order-level history is unnecessary here. |
| OHLCV / price / currency | Suitable candidate for daily exchange-price/volume reconciliation. Inspect the specific report layout, close versus last/average price, INR/unit and corporate-action treatment before assigning RAW_CLOSE. NAV is separate. |
| Manual CSV / API / authentication | Security-wise reports are a manual report/export route to verify. Paid products use contracted delivery; the EOD product description includes binary files, while order/trade delivery includes SFTP/online access. No general public automation entitlement or drop-in historical CSV API was established. Contracted credentials/format apply to paid delivery. |
| Rights / personal use | [Website terms](https://www.nseindia.com/static/nse-terms-of-use) restrict collection/copying/storage/display and prohibit automated collection. Download availability does not establish this application's complete permitted-use scope. The [data policy](https://www.nseindia.com/static/market-data/nse-data-policy) makes usage/redistribution agreement-dependent. Pending exact applicable permission. Personal investing is not automatically the policy's academic/noncommercial research category. |
| Reliability / suitability | Direct exchange provenance is valuable for source-record checks. Formats, archive availability, revisions and corporate actions still require validation. Suitable after permission; direct contracted acquisition may be more complex than two initial CSVs. No scraping, hidden endpoint calls, access-control bypass or paid purchase is proposed for execution now. |

### B. BSE official EOD / historical information products

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | BSE's [official information-products sheet](https://www.bseindia.com/downloads1/Information_Products_Pricing_Sheet.pdf) describes EOD and historical products. Exact Gold/Silver ETF listings, BSE scrip codes and series must be verified; NSE symbols/prices cannot simply be relabeled as BSE. |
| Coverage / granularity | Daily EOD and historical offerings are identified in the official indexed material. Exact ETF date bounds/rows unverified. |
| OHLCV / price / currency | Candidate for BSE exchange EOD prices. Actual OHLCV schema, INR/unit, volume units and adjustment rules not inspected. No basis assumption. |
| Manual CSV / API / authentication | [Bhavcopy page](https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx) is a candidate manual route. Its direct retrieval and the product PDF returned HTTP 403 in this review; the indexed official product description was available. Export details, account/subscription requirements and contracted machine delivery need confirmation. No verified unrestricted public historical API. |
| Rights / personal use | No specific agreement or verified permission covering local storage/analytics/display was obtained. **Pending**, including retention and redistribution. An unrelated site branded as a BSE downloader, or BSE Indices terms, is not BSE exchange-data permission. |
| Reliability / suitability | Direct venue provenance can be strong after qualification. Venue liquidity and closes can differ from NSE. Treat this as a distinct source/listing, not a silent missing-NSE-bar replacement. Current evidence is weaker because the documents could not be fully retrieved; no access workaround attempted. |

### C. ETF issuer / AMC disclosures and AMFI NAV

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | Examples: [SBI MF historical NAV facility](https://www.sbimf.com/mutual-fund-nav) and [AMFI NAV history](https://www.amfiindia.com/net-asset-value/nav-history). Qualify the exact ETF scheme; an ETF fund-of-funds or another share/plan is a different instrument. |
| Coverage / granularity | Historical daily valuation dates can be selected; exact scheme/date coverage and export limits unverified. Do not infer a complete series from a scheme's inception date. |
| OHLCV / price / currency | NAV per unit, normally the scheme's stated currency, subject to confirmation. **Not traded OHLCV, exchange close or traded volume.** Missing market-volume data is not zero. iNAV is another separate definition. |
| Manual CSV / API / authentication | SBI's historical form offers file-format and date selectors. AMFI exposes historical NAV selections. Actual export format and any authentication must be checked. No documented unrestricted automated NAV API was qualified. No download performed. |
| Rights / personal use | Disclosure availability does not establish automation, persistent copying or redistribution rights. Review the applicable AMC/AMFI terms and scheme evidence; pending. |
| Reliability / suitability | Useful for issuer identity, valuation/context and later separate NAV research. **Does not satisfy the current real exchange-price acceptance requirement.** The existing close/basis contract must not be used to disguise NAV as RAW_CLOSE or PROVIDER_ADJUSTED. Adding a NAV domain would need a separately assessed design change. |

### D. DhanHQ Data APIs - primary candidate

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | Broker's [daily historical documentation](https://dhanhq.co/docs/v2/historical-data/) and [instrument-master documentation](https://dhanhq.co/docs/v2/instruments/). Verify exchange, current security ID, symbol/series, ISIN and ETF identity against exchange/issuer evidence. Actual Gold/Silver availability has not been requested. |
| Coverage / granularity / OHLCV | Documented daily OHLCV, with history advertised back to instrument inception; actual ETF bounds/completeness unverified. The documented five-year intraday coverage is a different product limit. |
| Price / currency / units | Exchange-candle fields; raw versus adjusted definition is not established by the historical page. Confirm close semantics, corporate actions, INR/unit, traded-volume units and epoch/session-date interpretation. Do not mark RAW_CLOSE merely because the field is named close. |
| Manual CSV / automated API | Authenticated historical JSON API is documented. A native end-user historical CSV export was **not verified**; the documented instrument-master CSV is metadata, not historical prices. After approval, an exact, reproducible JSON-to-canonical-CSV preparation can support VS-01 without changing the app. Scheduled API retrieval would be later authorized work. |
| Authentication / cost | Requires a Dhan account, eligible data access and access-token authentication. [Official support](https://dhan.co/support/platforms/dhanhq-api/how-can-i-access-live-market-data-through-dhan/) advertises INR 499 plus taxes/month for Data APIs, including historical data. Confirm current account price before subscribing; no purchase made. |
| Rights / personal use | [General Dhan terms](https://dhan.co/terms/) restrict extraction, publication and commercialization. API availability does not itself settle persistent storage/export/backup and our derived-analysis rights. Obtain the applicable Data API terms or written confirmation covering this use. Pending; no redistribution entitlement inferred. |
| Reliability / suitability | Good documented fit and modest daily two-series workload; no independent uptime, sample reconciliation, adjustment or revision verification executed. Token lifecycle, provider changes and history corrections are operational risks. Credentials may cover broader broker functions: any future collector must be restricted by implementation to approved data endpoints, with no trading/account actions. |

### E. Zerodha Kite Connect - alternative broker candidate

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | [Kite historical API](https://www.kite.trade/docs/connect/v3/historical/) addresses exchange instruments by instrument token. Independently map the actual ETFs/listings. |
| Coverage / granularity / OHLCV | Documents several years of history and daily/intraday OHLCV. No exact ETF start/end or completeness established. Futures continuous-history features are irrelevant to this ETF slice. |
| Price / currency / units | Confirm daily-close adjustment rules, INR/unit, date semantics and volume against the specific sample; the endpoint description alone is insufficient. |
| Manual CSV / automated API | Authenticated JSON historical retrieval is documented; native historical CSV export not verified. A later permitted deterministic conversion would be needed for the current CSV importer. |
| Authentication / cost | Requires Zerodha account/app/token and the paid data tier. [Official support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/historical-data-and-live-market-data-payment-plan) lists INR 500/month per API key; free Personal API excludes historical/live market data. Confirm price/tax treatment before any purchase. |
| Rights / personal use | [Kite terms, section 4(b)](https://www.kite.trade/terms/) restrict permanent copies/databases absent express permission; public display and virtual/mock trading are also restricted. Personal-interface permission is not blanket PostgreSQL storage permission. Pending written clarification for our actual retained-data workflow. |
| Reliability / suitability | Documented technical alternative, especially if the owner already uses it, but not the preferred persistent-data route until its storage issue is resolved. No provider reliability benchmark performed. |

### F. TrueData - licensed-vendor fallback

| Attribute | Assessment |
| --- | --- |
| Official origin / instruments | [TrueData market-data API](https://www.truedata.in/products/marketdataapi). NSE's [authorized real-time vendor list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Authorized_Realtime_Data_Vendors.pdf) includes TrueData; this establishes the listed real-time relationship, not our historical export rights. Confirm current ETF/product entitlements. |
| Coverage / granularity / OHLCV | API describes historical chart data and EOD candles. Exact daily ETF dates, row limits, OHLCV schema and product-specific history depth need a written sample specification; no date range promised here. |
| Price / currency / units | [Velocity](https://www.truedata.in/products/velocity) markets adjusted history for splits/bonuses. Confirm the selected API product's raw/adjusted semantics, coherent OHLC, INR/unit and volume; do not assume every product has identical treatment. |
| Manual CSV / automated API | REST chart/EOD retrieval is documented. Native historical CSV export or a one-off licensed file delivery must be confirmed; desktop/plugin access is not automatically custom API/export access. |
| Authentication / cost | Requires the specific vendor account/product/credentials and any applicable exchange approvals. Obtain a historical/EOD-only quote; real-time/plugin headline prices are not a verified quote for our use. No account/contact/subscription made. |
| Rights / personal use | API product terms describe one subscriber's personal charting and restrict onward distribution and simulation. [General terms](https://www.truedata.in/terms-and-conditions) also defer to product licences. Obtain express coverage for automated requests, retained data/backups and private derived research; pending. |
| Reliability / suitability | Dedicated vendor alternative with exchange-linked provenance. Licence/format/coverage confirmation is still necessary; advertised performance is not a measured SLA or our validation evidence. A broker-independent route can be preferable if no broker account is wanted. |

Unknown or unverified attributes above are qualification tasks, not assertions of absence. Public mirrors, GitHub datasets, unofficial scrapers and a free download button are not substitutes for verified upstream rights. No paid or free third-party dataset has been qualified by this review.

## 3. What to obtain or configure after provider-selection approval

For Dhan, the proposed sequence is:

1. Confirm the owner's account/access and exact Data API subscription; do not open/fund/subscribe automatically. Request the applicable data-use permission described below before acquiring market samples.
2. Confirm the two listings and their current provider IDs with the official instrument master. Do not guess IDs or reuse another exchange's identifiers. The master itself would be fetched only after acquisition approval.
3. Select the supported authentication flow. [Dhan authentication docs](https://dhanhq.co/docs/v2/authentication/) describe web-generated tokens valid 24 hours, renewal of active web tokens and API-key/consent flows. Token expiry/reconsent is an explicit scheduling requirement; unattended indefinite login is not assumed. Keep credentials local and restricted; none in chat, Git, browser storage or logs. No credential is requested now.
4. Approve one bounded market-data-only acquisition of the representative samples. Record exact request/range, retrieved-at instant, original response hash, instrument snapshot and rights reference. No orders, holdings, funds, positions or portfolio account endpoints are needed.
5. After actual file/response inspection, approve the concrete date/currency/basis mapping and a deterministic canonical CSV preparation. Parse numeric JSON lexemes into Decimal/string values; never route authoritative prices through binary floats or invent precision. Preserve originals and transformation version/checksums outside Git.
6. Use existing source registration/qualification/import, then execute the real-data plan below. Scheduling is a separate implementation authorization, not part of VS-01's current manual CSV interface.

For TrueData, obtain a written offer for the **two exact ETFs, daily OHLCV, desired historical bounds, one user's local persistent research, automated EOD access, permitted exports and backups**. Confirm whether API credentials or licensed files are supplied, their correction/adjustment policy and retention after cancellation. Qualify the offer/sample before any account, payment or connection. No ongoing real-time service is necessary for this daily slice.

### Permission question to resolve for either provider

Does the applicable agreement permit this single user's scheduled daily historical requests, deterministic conversion, persistent local PostgreSQL/raw-file storage, restricted backups/restores, private charts and derived SMA/EMA/RSI/comparisons, and research supporting their own trade planning/portfolio reassessment? Record retrieval, storage, analysis and display separately, plus retention after cancellation, required deletion, public/third-party/cloud display and redistribution limits. Clarify whether derived/non-display analytics need additional permission. Keep an attributable dated agreement/support decision; a technical support answer about an endpoint is not a licence grant.

Current qualification is only for the approved research use. Future paper/mock trading, wider distribution, multi-user/cloud service or additional uses require a fresh rights review. NSE website, TrueData and Kite material explicitly raises simulation restrictions; no VS-01 data approval should be represented as permission for later paper trading.

## 4. Minimum representative Gold/Silver package

**Required:** one independently identified Gold ETF and one Silver ETF exchange-price series, with compatible currency/basis, a shared observed period, original source records and permission evidence. Example candidates for review are NSE GOLDBEES and SILVERBEES; they are not preselected, registered or recommended investments.

For each file/response record:

| Evidence | Required content |
| --- | --- |
| Identity | Fund/scheme, metal, exchange MIC and trading symbol/series, provider ID, INR/unit and verified ISIN if available; distinguish ETF from FoF. |
| Time and coverage | Explicit inclusive target period, returned first/last session dates, actual row counts, daily granularity, timezone/date meaning, absent sessions, inception/symbol-change limitations and known revisions/actions. Keep unknown publication time null. |
| Price/volume | Provider-confirmed raw/adjusted closing definition; source adjustment reference if adjusted, coherent same-basis OHLC where supplied, integer traded units or null volume. No NAV substitution. |
| Original and prepared files | Origin URL/product, acquisition method and timezone-aware retrieved-at timestamp, original bytes/checksum, encoding/schema, transformation version, prepared CSV checksum and explicit field mapping. One listing/source/basis per CSV; no account or unrelated personal columns. |
| Rights and review | Applicable terms/permission version, four permitted uses, reviewer/date, permitted retention and backup handling; source qualification reference. Provider selection and source qualification are distinct decisions. |

For numerical coverage, SMA/EMA n require n observations to seed; RSI n requires n+1. To test one post-seed step for all methods, a continuous eligible segment needs at least `max(n_sma+1, n_ema+1, n_rsi+2)` observations. Comparisons need at least two actual common dates. These are mathematical lower bounds, not sufficient proof of representative market-data acceptance.

**Proposed practical first sample:** about 60 actual daily observations per ETF over the same recent completed-session window, with no artificial fill. Optional explicit verification parameters SMA(5), EMA(5), RSI(14) would need at least 16 uninterrupted eligible observations for one post-seed step; they are test parameters for review, not product defaults or trading thresholds. Review the actual window and coverage before fixing the acceptance sample. No performance inference or favourable-period selection is intended.

Identity changes matter: [NSE circular CML/52187](https://archives.nseindia.com/content/circulars/CML52187.pdf) records NETFSILVER -> SILVERBEES effective 10 May 2022. If that ETF/history is selected, do not silently stitch old/new symbols or mistake missing old-symbol rows for inception. Verify the actual mapping and applicable period; do not infer complete historical coverage from a present-day master. BSE and NSE prices for the same fund remain separate listings.

## 5. Existing qualification workflow and planned real-data acceptance

No change to the approved contracts is needed merely to evaluate a source. Actual sample formats may reveal an impact, which must be presented before any material schema/API/security/calculation change. CSV preparation cannot silently revise price basis, identity, source values or financial conventions.

Use the existing [qualification checklist](VS-01_DATA_QUALIFICATION.md), DC-02..04/07/08 and the implemented workflow:

1. Review permissions/retention and independently establish identities/price definitions. Reject or leave pending any missing evidence. No market-data download until the owner approves acquisition.
2. Preserve source evidence/originals securely outside Git. After qualification, prepare inspected canonical CSVs. Existing bound: 10 MiB/file, 100,000 rows; analytics prefix <=10,000 points. No silent prefix truncation.
3. Register a new `REAL_MARKET` source with `csv-v1` and explicit `quality-v1` profile. Leave unknown calendar/freshness unassessed. Record `rights_evidence_ref`, all four permitted uses and `retention_review_ref`; only then record QUALIFIED_FOR_RESEARCH. Do not relabel synthetic history. The app records an owner assertion, not an independent legal guarantee.
4. Use permitted isolated acceptance storage and a separate database, preserving the active volume. Import each explicit listing/source/basis through the real API/UI with its UUID idempotency key, inspected mapping and checksums. Record batch counts/rejections and exact raw/canonical lineage.
5. Independently reconcile every imported date/close and supplied OHLCV against original source values and the recorded transformation. Retain observed-versus-expected evidence, counts and hashes; do not validate only by reading the app's own output back. Where permitted, corroborate selected endpoints/dates/actions with exchange records and explain any different close/adjustment definition.
6. Verify real charts, exact tables, source/classification, provenance, quality/freshness and known gaps. Independently calculate SMA/EMA/RSI on the exact qualified prefix with approved Decimal 34/HALF_EVEN and 12-place outputs. Confirm seeds, unavailable warm-ups and display-range overlap invariance.
7. Verify comparison common dates/endpoints and exact price-only percentages with compatible basis/currency; no total-return or NAV equivalence. Test empty/insufficient/unsupported requests without inventing or relabeling real data. Existing synthetic edge tests remain synthetic evidence.
8. Execute T-03 and applicable cumulative unit/API/DB/component/browser/build/security and operational checks on the accepted revision; retain actual results. Do not infer real-source acceptance from the previous synthetic suite. Submit the remaining WI-11/12 evidence for explicit human acceptance.

**Execution status now:** no provider selected, no sample acquired, no real source registered/imported, no T-03 or real-data chart/indicator/comparison tests executed. The normal app's read-only source inventory was empty during this review. No synthetic evidence is promoted to real-market acceptance.

## 6. Later automated daily acquisition - proposal only

A separately authorized data-only adapter could preserve provider responses/metadata/checksums, prepare canonical inputs and use the current import boundary, without redesigning the research UI. It would need reviewed endpoint allowlisting, restricted credentials, token renewal/reconsent, provider quotas, exact exchange calendar/finality evidence, bounded retries, explicit freshness state and audit evidence.

A job must not assume a fixed close/publication time or turn missing data into a price. Preserve retrieval timestamps separately from unknown historical publication. Re-fetching revised history may conflict with append-only observations; detect/quarantine and present a correction/versioning impact instead of overwriting. A fallback provider gets a distinct source/basis identity; it cannot silently extend the primary provider's series.

The existing contracts are CSV-first and have no scheduler/network adapter. No adapter, scheduler, API SDK, token automation, broker integration or future financial capability is implemented or authorized by this assessment. Provider approval is not implementation authorization.

## 7. Operational review and actual execution evidence

| Activity | Current outcome / boundary |
| --- | --- |
| Checkpoint and baseline | Approved Step 4 commit a244cfed verified; starting tree clean. Tagged baseline source files and approved D-01..16 unchanged. |
| Read-only service/config checks | Nine checks passed: current API/DB health, UI running/migration exit 0, UI/live/auth-ready 200, anonymous ready 401, loopback-only configured ports/private normal DB, stopped test DB, ignored sensitive/generated paths, and existing synthetic backup checksum. `artifacts/step5-operational-review.json`. |
| Local file permissions | Found inherited broad local-user allow rules on ignored `.env`. Before the later provider-only clarification, restricted that existing file to current user/SYSTEM, preserving the original ACL in restricted ignored rollback evidence. Secret/config bytes unchanged. Synthetic backup directory was already restricted. Reports: `step5-local-acl-review.json`, `step5-local-acl-remediation.json`. No application code changed. |
| Check after local ACL correction | Five checks passed: UI/live/auth-ready 200, anonymous ready 401 and owner Compose-config parsing. `artifacts/step5-acl-post-verification.json`. No external data calls. |
| Backup / restore | Existing Step 4 synthetic archive checksum still matches; prior full isolated restore/research-query evidence reviewed. No new restore, active-database backup/reset/cutover or owner-data recovery executed. |
| Startup / shutdown | Current state and documented safe start/stop reviewed. No new build, startup or shutdown executed in Step 5; prior Step 4 repeated startup is historical evidence. `docker compose stop` preserves the application volume. |
| Automated application suite / scans | Previous Step 4: 114 backend, 16 frontend, three browser tests passed; build/lint and dependency scans passed. Not rerun or claimed as new Step 5 executions. No application/dependency change justifies repeating them for provider-document assessment. |
| Retention / handover | Owner decisions remain pending. No retention duration, deletion policy, backup destination, RPO/RTO or full operational acceptance invented. Existing [recovery instructions](../05-operations/LOCAL_RECOVERY.md) remain applicable. |

The current one-host `.env` ACL correction is reversible and leaves content untouched. The configuration generator was not changed; any newly generated/copied secret file needs its local permissions reviewed. No security guarantee for other files/hosts or token rotation is implied. This local correction does not qualify a market-data source.

Accepted observations are append-only and the app has no general per-row deletion endpoint or scheduled retention erasure. A source becoming RESTRICTED prevents affected reads/imports; it does not erase retained rows or backups. If the selected licence requires expiry/deletion, establish a compatible, reviewed procedure or present the schema/operations/security impact before ingestion. Do not promise automatic compliance or weaken audit/restore guards.

Owner handover still needs explicit decisions on restricted source/backup location and retention, restoration validation/cutover authority, provider suspension/revocation handling, authentication maintenance and ability to perform normal lock/start/stop and inspect provenance/quality. Automated checks are not owner acceptance.

## 8. Blockers and readiness recommendation

- SQ-01 / T-03: provider choice, verified rights/retention, actual independently identified Gold/Silver samples and source-basis/coverage reconciliation are outstanding.
- WI-11: real-source and cumulative acceptance evidence remains incomplete.
- WI-12 / conditional SQ-06: owner-data recovery/cutover/retention and final handover acceptance remain pending.
- All later data automation, strategy/trade-planning, portfolio, paper trading and broker/execution increments require their own permissions and scoped implementation grants. No full VS-01 acceptance is declared.

**Recommended next authorization for review:** qualify DhanHQ as the primary candidate (TrueData fallback), including review of the specific data agreement and a bounded sample-acquisition plan. Only a subsequent explicit acquisition approval should lead to account/subscription actions, authenticated data requests or downloads. No local files are requested before the provider decision.

## 9. Historical assessment-only proposed Git changes

The assessment-only turn proposed one new documentation file:

- `docs/04-planning/VS-01_STEP5_PROVIDER_ASSESSMENT.md` - provider comparison, recommendations, prerequisites, representative-sample proposal, qualification/acceptance plan, current execution evidence and remaining gates.

No tracked source/configuration, schema/API/calculation, dependency, architecture/baseline, existing verification record or application file is modified. No credentials, raw data, rights documents containing account details, backups or generated evidence are Git contents. The existing ignored `.env` had only its local filesystem ACL corrected; ignored evidence includes the rollback ACL and check summaries. Nothing is staged or committed and no release tag created. This document is an assessment proposal, not accepted provider rights or final VS-01 approval.


## Later Step 5 credential-preparation disposition - 2026-11-02

The owner reports an active Dhan account/access token and selects DhanHQ as the primary candidate. The later scoped grant authorizes secure environment/configuration preparation, offline validation and verification only. This supersedes the earlier unselected-provider state for candidate choice; dataset/source permission and real-data acceptance remain pending. No provider contact or acquisition is authorized. See [local configuration instructions](../05-operations/DHANHQ_LOCAL_CONFIGURATION.md) and the [credential-configuration completion record](VS-01_DHAN_CONFIGURATION_CHECKPOINT.md) for the later implementation evidence. Sections above remain the historical assessment, not a claim that the later credential configuration was absent.


The historical one-file proposal above predates this later grant. The linked configuration checkpoint gives the exact current proposed Git set, including this previously uncommitted assessment and its dated scope disposition. Configuration values are entered locally and remain private, with the backend gate disabled; source/data acceptance is not established.


### Developer-application revision - 2026-11-02

The later owner request adds application name/API key/API secret placeholders and requires the official individual-app authentication model to be established before any authentication implementation. The offline configuration now distinguishes developer/consent completeness from historical token prerequisites; all seven values are backend-only. Local provider entry occurred after the append and was preserved; no values are recorded here. The linked configuration checkpoint/instructions carry the current evidence and optional-versus-mandatory distinctions. Provider rights, actual token validity and real-data acceptance remain unverified; this is not permission to exchange credentials or retrieve data.
