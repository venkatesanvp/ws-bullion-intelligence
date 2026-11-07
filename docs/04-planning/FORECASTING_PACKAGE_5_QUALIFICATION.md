# Package 5 - four-ETF historical-data qualification matrix

Review date:2026-11-07 IST. This is a structural and evidential assessment of the existing RAM-only canonical Dhan snapshot, not a source promotion or a new download. Source remains TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED. The source-only recovery archive contains code/docs/tests only; no market-data snapshot was written.

| Instrument | Available daily rows | Calendar-eligible daily rows | Eligible period | Older rows outside reviewed calendar |
| --- | ---: | ---: | --- | ---: |
| TATAGOLD |250|250|2025-11-03 through2026-11-05|0|
| TATSILV |542|250|2025-11-03 through2026-11-05|292|
| GOLDBEES |250|250|2025-11-03 through2026-11-05|0|
| SILVERBEES |252|250|2025-11-03 through2026-11-05|2|

The same eight dimensions apply individually to each verified registry instrument:

| Qualification dimension | TATAGOLD | TATSILV | GOLDBEES | SILVERBEES |
| --- | --- | --- | --- | --- |
| Observation timestamps |0 original provider event stamps; date-only canonical observations|0 original provider event stamps; date-only canonical observations|0 original provider event stamps; date-only canonical observations|0 original provider event stamps; date-only canonical observations|
| Availability |Actual local first-seen present; provider publication unavailable|Actual local first-seen present; provider publication unavailable|Actual local first-seen present; provider publication unavailable|Actual local first-seen present; provider publication unavailable|
| Final/provisional status |Prior-date daily completed candidate; not independently final-certified|Prior-date daily completed candidate; not independently final-certified|Prior-date daily completed candidate; not independently final-certified|Prior-date daily completed candidate; not independently final-certified|
| Trading calendar |250 contiguous reviewed daily candidates; no missing reviewed sessions|250 contiguous reviewed daily candidates;292 older rows excluded|250 contiguous reviewed daily candidates; no missing reviewed sessions|250 contiguous reviewed daily candidates;2 older rows excluded|
| Corporate-action adjustments |PROVIDER_ADJUSTED as delivered; method/vintage unknown; no declared breaks, unknown actions not ruled out|Same unresolved adjustment evidence|Same unresolved adjustment evidence|Same unresolved adjustment evidence|
| Historical revisions |Canonical current hash/batch evidence retained; no historical vintage archive|Same current-snapshot-only evidence|Same current-snapshot-only evidence|Same current-snapshot-only evidence|
| Source provenance |Verified registry ISIN/symbol/exchange/security mapping; canonical IDs/hashes/batches/first-seen intact|Same full identity/provenance controls|Same full identity/provenance controls|Same full identity/provenance controls|
| Retention/redistribution |Existing owner transient private analysis/display only; storage=false; broader rights unresolved|Same restrictions|Same restrictions|Same restrictions|

## Exact root cause and disposition

Package4 selected12 origins per ETF during2026-08-11..2026-11-05. All36 model-cutoff attempts per ETF failed METADATA_NOT_AVAILABLE because the current source/calendar compilation evidence was reviewed after those cutoffs. This is the first failing rule, not an OHLCV/schema or numeric failure. Independently, recorded local first-seen times from November cannot prove the candles were available to this system months earlier. Existing tests demonstrate the second MISSING_OR_UNAVAILABLE_SESSION gate when metadata is moved to a genuinely earlier fixture review. No actual evidence is moved or backdated.

STRICT_POINT_IN_TIME retains these restrictions. A structural session calendar reviewed today can be used for retrospective date indexing under an explicit conditional mode, but its present review timestamp does not become historical knowledge. The strict gate is intentionally conservative; it is unnecessarily restrictive only if it is mistakenly applied as the definition of all retrospective numerical research. Package5 separates that distinct use case instead of weakening the strict gate.

CONDITIONAL_HISTORICAL_REPLAY uses policy FIXED_RETRIEVED_VINTAGE_V1 after explicit selection and acknowledgement. It scores the present provider-adjusted snapshot under stated completed-candle/session-mapping assumptions. Original observation/publication nulls, local availability times and review times remain unchanged. Past-session context only enters model computation; outcomes are read separately. Unknown adjustments or revisions may still contain later economic information; this is not proof of historical predictive skill or action-free price series. Declared breaks/actions, invalid bases, missing sessions, current/provisional data and records unavailable at actual assessment are excluded. Mode/assumptions travel with every experiment and returned outcome row; results from different modes are never combined into a leaderboard.

SYNTHETIC remains deterministic arithmetic verification only and cannot be selected against the real source. No false real record is introduced into the application.

## Source evidence and unresolved questions

[Dhan daily API documentation](https://dhanhq.co/docs/v2/historical-data/) specifies daily OHLCV and epoch timestamp fields. It does not supply historical publication times, revision vintages or an adjustment methodology sufficient to establish strict PIT qualification. Our original event fields remain null; a calendar close is only a separate proxy. Prior live validation covered a limited October window and does not establish universal timestamp semantics for every historical date.

[Dhan terms](https://dhan.co/terms/) and [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy) were reviewed without account access. They do not establish this subscription's specific rights to persistent prices, derived histories, backups, training or redistribution. The existing narrower owner authorization remains the operating boundary; no new permission is inferred from public accessibility.

Existing ingestion calendar covers2025-11-02..2026-11-06. The separate Package4 forecast calendar reaches2026-12-31 and includes the officially confirmed2026-11-08 Muhurat date, whose exact session time remains unresolved. Targets on that special date remain excluded. No2027 dates are invented. Calendar and source review times remain visible evidence.

Qualification needed next: provider/official evidence for daily finality/session timestamps and adjustments; action/revision-vintage policy; separately reviewed broader session calendars; defensible historical availability archive or properly authorized prospective evidence; explicit retention/derived-output/backup rights. Additional price downloads alone cannot establish those facts. No trading or holdings/balance/account access is needed.
