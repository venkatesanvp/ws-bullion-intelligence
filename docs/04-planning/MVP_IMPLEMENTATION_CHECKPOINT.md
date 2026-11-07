# MVP05 engineering checkpoint - 2026-11-07

**Engineering verification passed within the recorded scope. Release security clearance remains BLOCKED; owner UAT and MVP acceptance remain pending.** No engineering change has been deployed to the protected UAT environment.

## Source control and isolation

Functional 52-file review: 33 modified /19 new /0 removed, no configured secret/token-shaped material, restricted data or large artifacts. Functional checkpoint `d781e5b6098cf7b5d44ee43233160c58c5278f37` was pushed to `feature/local-mvp-charting-forecasting-deployment` at existing origin `https://github.com/venkatesanvp/ws-bullion-intelligence.git`. PR #1 is verified merged at `afa434cf2fe7e432f63b241f32e95bdcd2b3b621`; it is not the MVP05 PR. No new PR/merge/tag/protection change is part of MVP05.

Engineering worktree: `C:/ws-bullion/bullion-mvp05`, local branch `engineering/mvp05-hardening`. Only its HEAD is normally fast-forward-pushed to the authorized **remote MVP feature branch**. This local branch name is an isolation aid; it is not pushed as another remote branch. Owner worktree remains clean at d781e5b on its original feature branch; it is deliberately not fast-forwarded while UAT is active, because that would replace its Compose/lifecycle source files. The engineering HEAD/remote equality and exact final SHA are recorded after commit in `artifacts/mvp05-git-synchronization.json` and the completion report. Both worktrees can therefore be clean while the owner branch is behind the remote by the reviewed engineering commits.

Commits: functional d781e5b; container security **87a8763**; recovery/audit **02d9028**; final engineering/verification commit follows those two. No force, reset, amend, rebase, branch/tag deletion or main merge. Requirements baseline, decision register, both lockfiles and `requirements-v1.0` tag object `5eeed03536e43ded7077ac086b97cb05f2e5b73e` remain unchanged.

Protected UAT: project bullion-vs01, UI5173/API8000/DB unexposed, volume bullion-vs01_bullion_data, network bullion-vs01_default, no source bind mounts. Engineering: project bullion-mvp05, UI15173/API18000/testDB15433, browser15174/API18001/18002, independent volume/network, no owner .env or credentials, no shared binds or real cache copies. Internal-only networking initially prevented Docker Desktop loopback test connectivity; the separate bridge now permits engineering host tests. This is **not** an egress firewall. Real-provider capability flags are false and credentials blank; fixtures use MockTransport. The runner validates project/image/port/network/volume/database identity, rejects indirect bind options and fails before runtime actions on unsafe configuration.

UAT metadata preservation receipt confirms the same IDs/start times/images/mounts/ports/networks and unchanged .env hash, and a clean owner worktree. No UAT cache, SQL rows, provider request or profile/account data was read/exported/copied; no UAT lifecycle command was run. This is metadata/non-interference evidence, not a claim that owner-driven UAT cache contents never changed.

## Traceability

| Workstream | Change | Evidence |
|---|---|---|
| MVP05-A | Reviewed functional source checkpoint /normal feature push | Source review receipt, exact MVP_CHANGED_FILES manifest, Git history/remote equality |
| MVP05-B | Supported pinned same-major bases; non-root API/DB; gosu removed; patched static UI runtime | Existing security report's complete54 baseline finding matrix plus two intermediate Alpine findings; unfiltered final SARIF |
| MVP05-C / REQ-05-009 / REQ-06-008 /DC-09 | Fully staged RAM restore, complete evidence comparison, interactive failure guard | test_mvp05_integrity_audit, test_mvp_local_management, synthetic binary recovery and container lifecycle receipts |
| MVP05-D | Sanitized provider start/completion/abort events, request correlation, fixed triggers | Mock status/error/timeout/circuit tests and production-UI synthetic counter guard |
| MVP05-E | Independent engineering runner /distinct browser ports /container lifecycle | Complete regression, isolation refusal tests, production CSP smoke, dependency/credential checks |
| MVP05-F/G | Pending owner UAT intake /honest release gates | Updated UAT plan and release-readiness document |

Canonical Decimal analytics, B01/B02 price models, B03 volatility-only behavior, matched origins, strict/conditional evaluation contracts, source permissions and transient retention policies are unchanged. No new forecasting model, broker execution, order/account/holdings operation, scheduler, live request, durable market-data store or forecast ledger was introduced.

## Recovery verification and limitations

Confirmed defect: old restore published daily state before preparing intraday coverage. An exception at that later step could leave a partial publication. Correction: deep-copy catalogue metadata into a private shadow, validate/remap a private payload, prepare all quote/candle/coverage maps, then publish under existing locks. Caller-owned payload is not mutated. Intraday duration exceeding its declared interval is rejected. Existing numeric/identity/time/OHLC checks remain.

Synthetic tests verify all observation values/IDs, first-seen timestamps, batch/observation evidence, quote/candle classifications and budget fields. Missing Origin is403; malformed/truncated/invalid payloads fail without publication; duplicates, wrong ISIN, source epoch mismatch, bad durations/non-finite prices/fractional volume reject atomically. Injected coverage failure after daily validation leaves the target untouched and allows a corrected retry. Disconnected upload never reaches restore. Unavailable provider is never called by restore. Replay remains deliberately one-shot409 with unchanged state: **idempotent state safety**, not an unconditional repeated200 response. After an uncertain response the management helper exports and compares the entire normalized snapshot, removing only ephemeral catalogue IDs; it never overwrites nonempty concurrent state.

Future authorized managed restart: full offline preflight; refuse noninteractive replacement of an existing API; retain the original payload in process RAM after any replacement/restore failure; explicit local retry or explicit `DISCARD TRANSIENT CACHE` only. No automatic provider retry and no disk/SQL snapshot. Ctrl-C/EOF in the recovery prompt retains the copy; killing that process, workstation failure, unmanaged stop/restart or power loss can still lose transient state. This is not durable recovery. The test action no longer stops the owner UI to free5173; browser verification has independent ports.

Binary synthetic backup: separate uniquely named source/restore *_test databases on engineering test-db. Backup SHA256/archive listing, restore to empty isolated DB, table/schema/query/provenance fingerprints and append-only trigger all pass. No active application DB or real cache is used. Container API/UI/DB/full restart and stop/start preserve the synthetic SQL catalogue checksum; repeated no-recreate start leaves process start times unchanged. Populated RAM handoff is verified separately through the authenticated HTTP boundary. Direct unguarded API restart loses its RAM by design; container catalogue tests do not claim otherwise.

Measured graceful exits: API143 after uv forwards SIGTERM, with explicit Uvicorn shutdown-complete/finished-process messages; UI0/DB0, no OOM/forced137. Runtime UIDs API10001/UI1000/DB999. PostgreSQL major18, Debian13 and data path retained; no active-volume migration. See mvp05-container-recovery.json.

REC-02's original 1294 daily/1442 intraday/four quote cache was lost historically; original identities/first-seen evidence were not recovered. The later owner-authorized fresh reload remains a distinct acquisition. This package neither reacquired nor copied that real cache. Its previously reported992daily/300intraday snapshot is historical, not a new acceptance target.

## Provider-attempt investigation

The earlier **23 ->24 remains an unresolved historical observation**: no retained causal correlation receipt establishes which request caused it. Later **one rejected-token attempt plus eight successful requests** is a separate authorized reload sequence and is not its explanation. No live request was made to reproduce either observation.

The shared budget counts adapters' **HTTP attempt results**, including authentication failures, timeouts and other dispatched failures, not only successful requests or logical UI actions. Pre-dispatch/configuration/cache/circuit/budget rejections count0. One logical range may partition into multiple bounded attempts; automatic retry count remains0. WebSocket subscriptions/messages are separate and not represented by this HTTP budget. Normal clock uses UTC dates for the local daily policy; this is not proof of Dhan's billing/quota reset convention. An unexpected programming exception is logged as ATTEMPT_COUNT_UNKNOWN, never falsely treated as a known zero/success.

Fixed service triggers: MANUAL_REFRESH, RANGE_ENSURE, QUOTE_POLL, INTRADAY_RANGE, DIRECT_SERVICE. Each allowed call records start and completion/abort with ISO timestamp, operation, counter before/after, outcome, retry_count0 and a UUID correlation ID propagated from the authenticated local request. Request logs supply route/method/status for the same ID; no user-supplied trigger, header/credential value, raw exception text, price body, account identifier or raw provider response is logged. These are service-trigger receipts, not a fabricated browser click history.

Source review: startup constructs clients without retrieving; no scheduled provider worker was added; optional open quote view may legitimately poll when due/market open; manual quote refresh and missing/range/intraday operations may acquire under existing read-only policy; technical/forecast live context stays unmounted while closed. Cached snapshot forecast/evaluation do not acquire. Existing bounded transport has no automatic retry. Mocks cover200/401/403/429/500, network timeout, cached reads/startup/manual refresh and circuit behavior. Built UI navigation/forecast/evaluation left synthetic quote/intraday counts **1/0 ->1/0**, zero real provider attempts. Historical attribution is still open; future correlation reduces this diagnostic gap without claiming restart-safe durable audit evidence.

## Verification

Complete final backend run: **959 passed**, zero failures/errors/skips; 6 existing deprecation warnings. Complete frontend: **62 passed/10files**. Chromium: **11 passed**, retries0. Ruff, TypeScript/Vite production build and final built-image CSP/native/Plotly/forecast/evaluation smoke pass. All56 deployed engineering backend module hashes match source. Additional isolation cases found a missing database-destination check (957passed/1failed); it was corrected before any unsafe runtime operation, exact synthetic settings validation was added, and the complete backend rerun passed959. Frontend/browser evidence remains valid because no frontend application behavior changed afterward. The reproducible built-UI smoke was rerun after promoting its source helper.

Python audits: Windows 40 / Linux 31 dependencies, zero vulnerabilities/skips; npm full/production zero. Exact configured-secret and credential-shaped checks found none in proposed/staged bytes,10built assets/server or both engineering log streams. Actual owner credentials remained only in owner .env/backend; engineering Dhan fields are blank/disabled. .env/artifacts/builds/caches/backups remain ignored/untracked; public-image binary and synthetic backups are not committed.

OS images: API 0 critical / 2 high; UI 0 critical / 1 high (primary tracker branch-fixed, raw retained); DB 0 critical / 4 high. Six Debian finding instances remain open, not accepted. Full individual evidence/dispositions/digests are in MVP_SECURITY_ASSESSMENT. Dependency success is not OS-image clearance.

Failures are retained rather than hidden: initial focused harness used GET instead of documented quote POST and an unused identity field; corrected fixtures and rerun pass. First full run:880passed/59database-setup errors due engineering internal-network host connectivity; browser not run, lint failed before formatting. Isolated bridge and harness fixes yield final zero errors/skips. Initial backup bootstrap lacked synthetic Settings; corrected to non-network engineering defaults, then seven recovery checks pass. Initial lifecycle expected API exit0; inspected shutdown logs establish graceful143 and retain strict failure checks. Alpine's intermediate critical and unavailable edge musl patch were rejected and documented in the security assessment. No failing result is called release acceptance. Engineering services were stopped after verification, retaining only their synthetic volumes; owner UAT stayed running.

Remaining nonfatal warnings: existing Starlette/httpx/Alembic deprecations, large lazy Plotly chunk (~1.2MB), NO_COLOR/FORCE_COLOR browser-tool warning. No increased assertion retries or financial tolerance relaxation.

## Performance observations (synthetic; not SLAs)

| Scenario | Observed time |
|---|---|
| TATAGOLD daily switch/render | 900ms |
| TATSILV daily switch/render | 812ms |
| GOLDBEES daily switch/render | 871ms |
| SILVERBEES daily switch/render | 1262ms |
| indicator visibility | 282ms |
| Production built UI three-model forecast through rendered result | 492ms |
| Production built UI historical evaluation through rendered metrics | 1137ms |
| Engineering restart api | 5017ms |
| Engineering restart ui | 3432ms |
| Engineering restart db | 3568ms |
| Engineering restart db/api/ui | 5477ms |
| Engineering stop/start  | 52529ms |

Switch/render timings include fetch/control/render and cold chart initialization in the workflow; they are not an isolated renderer microbenchmark. Stable23canvas and zero page errors are bounded lifecycle evidence, not a heap/leak proof. One post-check resource sample: API0.16%CPU/79.94MiB, UI0%/16.07MiB, DB6.02%/30.3MiB on Docker's7.623 GiB VM. Concurrent engineering activity affects timings; no superiority, capacity, significance or production SLA claim.

## Evidence and next decisions

Exact changes: MVP_CHANGED_FILES (41 MVP05 files:32modified/9new;65unique outgoing files including the functional checkpoint). Reproduction: MVP_LOCAL_DEPLOYMENT and scripts/engineering.py. Ignored receipts include final-backend-corrected.log/backend-tests.xml, final-verification.log/browser-tests.xml/verification.json, mvp05-production-smoke.json, mvp05-container-recovery.json, recovery-verification.json, dependency-audits.json, mvp05-security-boundary.json and mvp05-uat-preservation.json. Real data was not used for this package's engineering tests.

Owner UAT remains pending/independent. Required next decisions: supported fixes or formal scoped disposition for six open Debian findings; separate controlled deployment window after risk review; owner defect/retest results; source retention/publication/finality/adjustment/calendar qualification before any durable forward-evaluation design. No autonomous risk acceptance, production/MVP acceptance, main merge, release tag or new feature increment.

---

## Archived functional checkpoint (d781e5b; historical counts/status below)

# Local Research MVP implementation checkpoint

Status: MVP-02/03/04 implemented and locally deployed; automated verification passed. Owner UAT and release acceptance remain pending. No commit or push authorized. Baseline: merged PR #1, afa434cf2fe7e432f63b241f32e95bdcd2b3b621. Branch: feature/local-mvp-charting-forecasting-deployment.

## Traceability and implementation
| Request | Implementation | Verification |
|---|---|---|
| MVP-02 chart lifecycle/default/panes | FinancialChart, LightweightResearchChart, financialChartData, chartAdapters; daily/intraday/technical research integration | Native API lifecycle unit tests, safe timestamp/gap tests, native multi-ETF Chromium workflow; Plotly regression workflows |
| MVP-03 coherent history/technical/forecast/evaluation | ForecastingResearch; additive exact OHLCV metadata in research and forecast adapters | Existing deterministic B01/B02/B03 regression, display-contract tests, forecast controls and endpoint-only tests, forecasting browser workflow |
| MVP-04 setup/start/stop/restart/status/test/recovery | scripts/local/manage.py and bullion.ps1; immutable multi-stage frontend image and built-asset server | Safety tests, isolated synthetic recovery and controlled local deployment checks |
| Provider-attempt audit | Existing receipts plus bounded operation/count-only ProviderBudget log events | Audit log secret-exclusion test and metadata-only counter/hash guards |
| MVP-05 SIT/UAT readiness | MVP_SIT_TEST_PLAN, MVP_UAT_PLAN, MVP_RELEASE_READINESS | Automated evidence recorded separately from pending owner UAT |

## Preserved controls
Canonical Decimal engines/models and the requirements baseline are unchanged. Source observations are not synthesized to fill OHLC, missing sessions or forecast paths. Chart numbers are approximate coordinates only; exact strings remain in tables/hover. B03 remains volatility-only. Real evaluation defaults strict; conditional replay needs explicit acknowledgement. Transient performance registry retains maximum 32 experiments/one hour. No durable price or forecast ledger is added.

All four existing verified primary ETF mappings remain unchanged: TATAGOLD 21401, TATSILV 21428, GOLDBEES 14428, SILVERBEES 8080, NSE_EQ/EQUITY/INR. Price basis remains provider-as-delivered with unqualified adjustment/total-return semantics.

## Verification
Final full suite: 915 backend/PostgreSQL tests, 62 frontend tests and 11 Chromium workflows passed, zero failures/skips. Ruff and TypeScript/Vite build passed. Unit-worker concurrency is bounded to two to avoid workstation CPU contention; assertion timeouts/retry behavior were not relaxed. Browser reconciliation verifies the approved native default after a snapshot remount; explicit Plotly coverage remains in other workflows.

Production built-asset smoke: native panes, Plotly fallback and forecast endpoints passed under the deployed CSP, zero runtime/CSP errors, synthetic API only. Fifty-six deployed production Python module hashes match the working source. Separate synthetic Compose project passed startup/shutdown/full start and API/UI/database restarts, preserving its synthetic catalog; Dhan credentials were blank and no provider was contacted. Synthetic backup/archive integrity/isolated restore/query/schema/provenance and append-only guard passed. Active database price/import/import-row counts remain zero.

Fresh Python audits: Windows 40 packages and deployed Linux 31 packages, zero known vulnerabilities/skips; npm full/production zero known vulnerabilities. Credential/asset/log and API-only credential-isolation checks passed after the owner-authorized token rotation. OS-image scan results are tracked separately in release readiness; dependency scans do not establish OS-image safety.

Earlier failed verification attempts exposed canvas-vs-jsdom harness assumptions, explicit label lookup, workstation concurrency, snapshot-remount test expectations and the existing recovery enum normalization gap. These were corrected with meaningful tests; no financial validation or numeric bounds were weakened. Nonfatal existing Plotly chunk-size/deprecation warnings and browser teardown connection-reset diagnostics remain.

## Source-control plan
Do not commit or push without separate approval. Review the complete final diff and exact file manifest; exclude .env, real data, backups, builds and verification artifacts. Recommend one coherent MVP implementation checkpoint with tests and these documents; prepare a new PR into main after authorization. Preserve PR #1 and all existing tags/history. No release tag.

## Recovery incident REC-02 ? active transient cache loss

The first MVP local deployment replaced the API, but the management helper's restore POST omitted the required Origin header and was rejected with HTTP 403 ORIGIN_REQUIRED. The management process then exited and lost its RAM payload. The 1294 daily observations, 1442 intraday candles and four quote records present before deployment were not preserved. PostgreSQL and .env were unaffected. This is an implementation defect, not successful recovery, and the original first-seen/provenance evidence cannot be recreated.

Correction: add the configured local Origin to write requests; report sanitized HTTP status; validate the complete populated handoff in a disposable in-process backend before any replacement; test the real HTTP authentication boundary with populated daily/quote/intraday fixtures. Daily budget day/count are now transferred explicitly, separately from cumulative capability counts, rather than reconstructed as a daily total. A dated counter is also exposed; prior-day counts no longer appear as today's. These corrections do not retrospectively attribute the older 23?24 anomaly.

Owner separately authorized a bounded fresh transient reload after this correction is verified. Reacquisition must use new first-seen times/identities, and must be reported as new acquisition, not restoration of the lost cache. No real price backup, raw-response file, PostgreSQL price write or durable forecast registry is authorized.

## Fresh acquisition and actual-data checks

After REC-02 correction and populated handoff tests passed, the first fresh reload request failed AUTH_INVALID_OR_EXPIRED and stopped. The owner replaced only DHAN_ACCESS_TOKEN locally and explicitly authorized continuing within the remaining eight requests. The agent did not modify or display credentials.

Exactly nine provider attempts total: one failed attempt, four successful daily requests and four successful intraday requests. No automatic retry, fallback, token exchange or quote request. Each primary ETF now has 248 observations from 2025-11-07 through 2026-11-06 and 75 five-minute candles for 2026-11-06: 992 daily / 300 intraday / zero cached quotes. This is fresh acquisition, not restoration of the original 1294 daily / 1442 intraday / four-quote cache. Original first-seen/identity evidence is lost and was not reconstructed.

Local cached real-data verification: all four exact OHLCV/observation identities match chart output; forecast display history matches canonical inputs; technical status AVAILABLE; B01/B02/B03 forward status AVAILABLE at horizon 5/lookback 60, with B03 price targets null. Strict historical evaluation scores zero origins and returns DATA_QUALITY_BLOCKED for all four. No real conditional-replay acknowledgement or performance superiority claim was invented. These local checks left the new dated provider counter at 8?8 and made no additional provider requests. Data remains TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED.

## Performance observations

Measured on the Windows workstation with synthetic data in Chromium, without invented pass/fail targets. Resource evidence is bounded chart-instance/subscription disposal and stable canvas counts, not a formal heap/leak proof.

| Scenario | Measured milliseconds |
|---|---|
| TATAGOLD daily switch/render | 557 |
| TATSILV daily switch/render | 456 |
| GOLDBEES daily switch/render | 604 |
| SILVERBEES daily switch/render | 1388 |
| indicator visibility | 216 |
| Three-model forecast through rendered results | 617 |

Stable canvas count during repeated refresh: 23. No browser page errors in the measured workflow. Plotly fallback remains a large lazy chunk (~1.2 MB uncompressed). These timings are workload/environment observations, not production SLAs.

Exact source scope: [MVP_CHANGED_FILES.md](MVP_CHANGED_FILES.md). SIT/UAT/readiness: companion MVP documents.

## Final image security gate

Project dependency/credential checks pass, but image security is not clear: API 7 high / 0 critical, UI 8 high / 0 critical, PostgreSQL 35 high / 4 scanner-reported critical findings. One critical is Windows-specific and not applicable to the verified Linux image; three require binary reachability qualification and/or patched compatible image selection. All raw findings are retained. [Security assessment and full rule inventory](MVP_SECURITY_ASSESSMENT.md) records severity, packages, fixes, exposure, remediation and compatibility. **Release security clearance is blocked.**

Runtime hardening removed unused pip/npm/Yarn/Corepack tooling without changing the required API uv command or frozen dependencies. Final guarded deployment preserved the fresh real cache exactly (992 daily/300 intraday, original new IDs/first-seen times, counter 8?8), with no fallback and no provider calls. Full offline preflight also validated the same real snapshot without changing the active cache. This success does not undo REC-02's loss of the original pre-MVP cache.

Reproducibility: generated TypeScript cache/log files are excluded from frontend build context. Consecutive builds had identical rootfs layers and runtime configuration; image/index IDs differed with provenance metadata. Provenance was retained, not disabled to force matching IDs. Base digests/lockfiles remain fixed. Functional UAT is prepared; security/source/retention/statistical gates and owner acceptance remain open.
