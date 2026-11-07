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
