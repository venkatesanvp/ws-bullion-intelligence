# Step 5E P1 implementation checkpoint - 2026-11-06

**Engineer P1 software/deployed after-hours gate: PASS. Owner P0/P1 acceptance: Pending.** Source/timestamp/retention qualification remains incomplete; this is not full VS-01 acceptance. P0 was committed and its gate passed before P1 started. No release tag or push.

## 1. Architecture

Extends the existing provider/catalog, RAM session service and canonical daily pathway. One backend feed normalizes into the quote cache; intraday and daily inputs remain separate. Authenticated local SSE conveys normalized snapshots/status/reconciliation revisions. A bounded reconciliation ledger links provider daily observations and intraday candidates without a second persistence architecture. Trace and precise policies: [implementation design](../03-design/VS-01_STEP5E_MARKET_DATA_DESIGN.md).

## 2. Provider interfaces

Existing provider-neutral Listing/MarketQuote/IntradayCandle remain unchanged. The Dhan adapter's verified catalog now carries public tick metadata. The read-only feed connector/decoder/controller adds subscription/packet/lifecycle handling; no broker SDK or account capabilities. Binary32 prices recover a uniquely determined one-paise exchange tick using integer-bit/Decimal arithmetic, rejecting ambiguous/nonfinite/negative/off-tick values. Dhan's master and official tick-unit FAQ support this metadata; no float financial calculations enter canonical analytics.

## 3. Backend implementation

One connection, maximum 100 verified catalog instruments, quote subscription code17, frame cap4096bytes/queue16. Fixed-host DNS/TCP/TLS work is bounded; no insecure TLS/proxy fallback. Three reconnects at1/2/4seconds, restored subscriptions,10second health ping/5second wait, automatic pongs, bounded stop, idle shutdown30seconds. Auth/entitlement/rate/provider-disconnect failures terminate retries. Automatic connections pause outside reviewed market hours; explicit manual snapshots remain read-only. No startup connection. Duplicate/out-of-order events and older REST fallback responses cannot roll back newer quotes; session boundaries do not carry old OHLC/volume/previous-close evidence.

New local endpoints: GET stream-status, GET stream-events, POST stream-control, GET reconciliation and POST reconcile under /api/v1/market-data. Existing local bearer/loopback/Origin/no-store controls apply; SSE additionally requires Origin. Maximum16 viewers; coalesced one-second snapshots; locks run off the ASGI event loop. All provider credentials remain backend-only. No API key/secret exchange.

Reconciliation uses existing T-1 daily eligibility, single flight, budgets/backoff and shared canonical validation. A single selected interval is aggregated, never overlapping timeframes or quotes/ticks. Any nonzero comparable field difference is flagged for review; no invented investment-materiality threshold. Official observation/batch IDs, hashes, differing fields and timestamps form a bounded RAM ledger (1000 records/audit entries). Daily finality remains separate from source qualification. Final daily data supersedes provisional presentation and revision events refresh affected charts/indicators. Qualified historical values are not silently overwritten. Current-session daily publication is deferred, not fabricated.

## 4. Frontend implementation

All four quote cards accept normalized LIVE_STREAM events and show provider trade time, reception time, source, changes and freshness. Connection state, retry/disconnect, rejected-frame count and fallback are visible. Updates coalesce at one/second; hidden tabs detach; local-channel retries are bounded. Controlled visible/open-session quote polling resumes when feed health is unavailable. Last valid quotes remain on disconnect, with correct STALE classification. Reconciliation date/control/status exposes provisional disposition, finality, coverage and differing fields, triggering chart/indicator reload. Daily and intraday calculations stay separate.

## 5. Actual Dhan integration results

All operations were read-only under standing authority. No holdings/funds/orders/profile/trading calls, automatic token exchange or provider-price persistence. P1 had five bounded connection attempts in total: one Windows probe did not complete a handshake within its observation window; four Linux connections succeeded (initial timestamp rejection, timestamp-only investigation, corrected normalization probe, deployed browser check). No reconnect was needed in these real tests. Each successful Linux subscription delivered four quote frames. The initial four rejected frames remain reported; the timestamp-only probe inspected no prices. The corrected probe and final browser each normalized one event per ETF with zero rejections. A separate unauthenticated master GET retained only four public listing metadata rows, not the raw master.

Final deployed browser evidence (timestamps UTC; trade-time policy explicitly provisional):

| Instrument | Feed / result | Updates | Latest provider trade | Backend reception | Freshness / session |
| --- | --- | --- | --- | --- | --- |
| TATAGOLD | Quote feed / CONNECTED | 1 | 2026-11-06T10:27:30Z | 2026-11-06T12:45:48.197223Z | STALE / CLOSED |
| TATSILV | Quote feed / CONNECTED | 1 | 2026-11-06T10:27:35Z | 2026-11-06T12:45:48.197491Z | STALE / CLOSED |
| GOLDBEES | Quote feed / CONNECTED | 1 | 2026-11-06T10:29:56Z | 2026-11-06T12:45:48.197615Z | STALE / CLOSED |
| SILVERBEES | Quote feed / CONNECTED | 1 | 2026-11-06T10:29:41Z | 2026-11-06T12:45:48.197718Z | STALE / CLOSED |

One shared backend connection delivered all four events through authenticated SSE to the real browser. The browser made zero external-provider requests and no duplicate quote/intraday REST calls. The feed was disconnected after verification, preserving all four last valid quotes. This demonstrates current subscription capability; it does not verify market-open continuous movement or provider availability SLAs.

**Timestamp limitation:** official docs call LTT EPOCH, while the SDK renders UTC clock fields without timezone conversion. Observed raw Unix-UTC candidates15:57:30,15:57:35,15:59:56,15:59:41 were future relative to backend UTC12:32:28 and were rejected by the initial strict interpretation. Those clock fields exactly match REST IST strings for all four ETFs. The explicit feed-only SDK_UTC_CLOCK_FIELDS_AS_IST_CANDIDATE_V1 interpretation preserves wire seconds and matches REST UTC10:27:30,10:27:35,10:29:56,10:29:41. This is sample corroboration, not a universal timestamp contract or a fallback/unit guess. Future/range checks remain; daily/intraday timestamp rules are unchanged. Provider/independent source confirmation, market-open and rollover evidence remain open.

For 2026-11-05, each ETF's 75 cached five-minute bars reconciled with its existing validated official daily candle using zero new historical requests. All four showed close and volume differences, flagged REVIEW_DIFFERENCES; no claim of adjustment/volume-scope equivalence or financial performance follows. Open/high/low matched in this sample. The current Tata Gold 2026-11-06 aggregate correctly remained INTRADAY_PROVISIONAL / WAITING_T_MINUS_ONE, with zero historical calls. Synthetic tests verify next-session retrieval through the existing validator, publication, provenance and supersession. An actual future publication transition was not awaited/claimed.

All 1002 canonical daily observations/IDs, four quotes and 1442 intraday candles survived final deployment by authenticated RAM-only transfer. No price file was created. Legacy unavailable original numeric epochs/full batch metadata remain explicit gaps.

## 6. Automated verification

- Backend/PostgreSQL: **647 passed,0 failed,0 skipped**. Includes migrations, integrity, existing mathematics, credentials, HTTP provider and37 new P1 binary/stream/reconciliation cases.
- Frontend: **29 passed,0 failed,0 skipped**.
- Chromium: **six workflows passed,0 failed,0 skipped**, including synthetic binary feed -> actual backend SSE -> browser cards, disconnect/fallback, reconciliation and unchanged daily charts. Existing P0/manual/automatic/intraday workflows remain passing.
- Python lint, production TypeScript/Vite build, API/UI image builds, Compose startup/readiness: PASS.
- Final SSE off-event-loop lock change:37 focused backend tests and real deployed browser PASS; frontend/SSE browser coverage remains passing.
- Deployed real browser: ten checks PASS (four live cards, stale/closed state, four reconciliations, chart reload, publication delay, preserved fallback/cache and no browser provider calls). Final managed handoff: exact values/IDs/evidence PASS.
- Windows Python40 packages and deployed Linux31 package set: **zero known vulnerabilities,0 skips**; Linux installed set compared exactly to audited pins. Full/production npm audits: **zero vulnerabilities**. Websockets17.4 is now an explicit pinned dependency; its version was already present transitively. No forced upgrades/suppressions.

Earlier failures are not hidden: the initial strict feed timestamp candidate rejected four live frames; a publication mock omitted required Content-Type; one new catalog test initially lacked an import and temporarily caused one failure/browser skip; these were corrected and final relevant suites passed. The original Windows connection observation motivated a total dial bound. Existing Starlette/httpx and Alembic deprecations, terminal color notice and Plotly chunk-size warning remain nonblocking. OS/base-image vulnerability scanning is not claimed.

## 7. Security and retention

Actual local credential strings and encoded forms were compared in memory against tracked/untracked proposed source, production frontend assets and API logs: no matches. No credentials were printed. Runtime Dhan fields match local configuration and are present only in API, absent from UI/database/migration containers. Exposed API/UI ports bind loopback; database has no application public port. .env is ignored/untracked, .env.example has placeholders and false capability defaults. Only the ignored local .env adds MARKET_STREAM_ENABLED=true under standing authority; existing credential values remain unchanged. DHAN_DATA_API_ENABLED remains false; explicit market-data capability gates govern the authorized app adapter.

Provider WSS authentication requires a query URL, held only in backend connection memory; private nonpropagating logs and sanitized errors prevent URL disclosure. Browser SSE uses its local application bearer header, never provider credentials/URLs. No raw-response/packet files, scheduled acquisition, database price writes or licensed-data backups. PostgreSQL price_observations/import_rows/import_batches each remain0. Controlled RAM handoff is not persistent storage approval. All market snapshots/ledgers disappear on ordinary restart.

## 8. Remaining limitations and acceptance blockers

Owner UAT is Pending for both phases. SQ-01/T-03 source qualification, persistent retention/refresh/backups terms, universal timestamp/session semantics, special-session/calendar extensions, independent reconciliation, adjustment/volume-scope compatibility and point-in-time/replay evidence remain open. Some legacy original epoch/batch evidence cannot be reconstructed. Matching fields/dates and HISTORICAL_FINAL do not confer source or total-return qualification. Provisional current-session daily indicators are not offered. Price-only comparisons retain their existing basis limitations.

Market-open streaming continuity, real induced outage/recovery and a real next-session publication transition remain unverified; mocked recovery/exhaustion/publication tests pass. Feed timestamp policy requires source-qualification review rather than silent ADR/DC closure. No proposed requirement/decision is promoted to baseline. Scheduled acquisition, token renewal and all account/trading functionality remain out of scope.

## 9. Source control

Starting Step5D checkpoint: aab1e9afed794d704862ece0d2ce8fbe4d8edc2b (54 reviewed files). P0 checkpoint: 4c77a466db83da9a2f54ca2a15b10fc68949c627 (31 files). This P1 checkpoint has 27 files, listed exactly below. Its resulting local commit hash is reported at completion; no self-referential amend is needed. Immutable requirements/project context, canonical analytics/comparison and requirements-v1.0 remain unchanged; existing tag object 5eeed03536e43ded7077ac086b97cb05f2e5b73e. No tag/push/history rewrite. Ignored local credentials, artifacts, raw data, backups/builds and test outputs are excluded.

- `.env.example`
- `backend/app/config.py`
- `backend/app/dhan_feed.py`
- `backend/app/dhan_history_contract.py`
- `backend/app/feed_connection.py`
- `backend/app/main.py`
- `backend/app/market_reconciliation.py`
- `backend/app/market_session_service.py`
- `backend/app/market_stream.py`
- `backend/app/market_stream_routes.py`
- `backend/tests/session_browser_app.py`
- `backend/tests/test_market_stream.py`
- `compose.yaml`
- `docs/03-design/VS-01_STEP5E_MARKET_DATA_DESIGN.md`
- `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md`
- `docs/04-planning/VS-01_STEP5E_P1_CHECKPOINT.md`
- `docs/05-operations/STEP5E_UAT_CHECKLIST.md`
- `docs/05-operations/STEP5E_UAT_GUIDE.md`
- `frontend/e2e/market-session.spec.ts`
- `frontend/e2e/market-stream.spec.ts`
- `frontend/src/MarketSnapshot.tsx`
- `frontend/src/MarketStream.test.tsx`
- `frontend/src/ReconciliationPanel.tsx`
- `frontend/src/ResearchDashboard.tsx`
- `frontend/src/api.ts`
- `pyproject.toml`
- `uv.lock`

## 10. Owner acceptance instructions

Open http://127.0.0.1:5173 and privately unlock with LOCAL_APP_TOKEN. Select ETF, real transient Dhan source and Provider adjusted, then Research dashboard. After hours select Connect / retry feed; expect four LIVE_STREAM/STALE cards and separate trade/reception times. Disconnect and confirm retained quotes/fallback. Select reconciliation session 2026-11-05 and verify HISTORICAL_FINAL with close/volume review flags and refreshed daily chart. Current session waits for T-1. Check intraday intervals/indicators and daily comparisons remain separate. During the next reviewed market-open session verify actual changing trades/automatic lifecycle; record owner results without credentials/real-data screenshots.

Use [UAT guide](../05-operations/STEP5E_UAT_GUIDE.md) and [separate owner checklist](../05-operations/STEP5E_UAT_CHECKLIST.md). Automated/engineer results do not sign owner acceptance or full VS-01 acceptance. Recommended next action is owner P0/P1 UAT and source/timestamp/retention qualification, not a trading or scheduled-ingestion increment.
