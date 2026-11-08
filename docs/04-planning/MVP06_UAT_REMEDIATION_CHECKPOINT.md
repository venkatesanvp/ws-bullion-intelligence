# MVP-06 UAT remediation checkpoint

Engineering checkpoint, 8 November 2026 IST. **NOT RELEASED. NOT OWNER ACCEPTED. Owner UAT deployment is unchanged.**

Base: 4d3f943e8a293a1f9aed51ea9431b135bc308acb. Dedicated worktree C:/ws-bullion/bullion-mvp06; branch feature/mvp06-uat-ux-remediation. The protected owner checkout remains d781e5b6098cf7b5d44ee43233160c58c5278f37. Requirements, decision register, model contracts, lockfiles and existing tags are preserved. Exact source inventory is MVP06_CHANGED_FILES.md; Git hashes and remote equality are reported by the completion receipt rather than embedding a self-referential final commit hash here.

## A. UAT defect matrix

These are confirmed source-path defects and deterministic synthetic reproductions. The original intermittent owner browser incident was not reproduced against owner caches, and its exact runtime sequence is not claimed to be proven. Every owner retest is **PENDING**; engineering verification is not owner acceptance.

| Defect | Root cause / evidence | Correction and principal files | Verification | Remaining limitation / owner retest |
|---|---|---|---|---|
| UAT-001 | Early invalid-selection/source returns removed the entire dashboard; uncontained snapshot render failure could affect adjacent sections. Optional quote context was collapsed without a persistent explanatory landmark. | ResearchDashboard.tsx retains landmark/navigation and valid conditional children; ResearchShared.tsx isolates snapshot/reconciliation/view failures. | ResearchViews empty-state unit case; mvp06.spec.ts repeated four-ETF switching, invalid listing, recoverable 503 and deliberately malformed snapshot boundary. | Original owner incident timing unverified; quotes still require permitted valid context; retest PENDING. |
| UAT-002 | Instrument/source/revision keyed dashboard remount and tab unmount discarded component-local periods and visibility. | App.tsx, researchPreferences.tsx, ResearchDashboard.tsx, TechnicalWorkbench.tsx, IntradayDashboard.tsx and both chart renderers retain UI-only preferences in unlocked memory; results are refreshed, obsolete requests aborted. | Unit unmount/ETF change; browser EMA23/visibility through History & quality, ETF switches and return. | Lock/reload deliberately clears preferences; unavailable data remains unavailable; retest PENDING. |
| UAT-003 | Daily used three close-only indicators while Technical used six; availability and visibility paths diverged. | indicatorCatalog.ts, IndicatorVisibility.tsx, shared FinancialChart.tsx and TechnicalWorkbench.tsx reuse the existing six-indicator endpoint. Intraday uses existing technical extension. | All six discoverable in empty/warm-up units; browser repeated switches; existing daily/intraday/native/Plotly formula and chart regressions. | ATR/Donchian require OHLC; gaps/flat RSI/warm-up explained; no fabricated values; retest PENDING. |
| UAT-004 | Empty daily drafts and EMA37 technical default differed across views. | technicalTypes.ts and backend/app/technical_analytics.py default EMA20; shared settings preserve valid edits; reset, integer/MACD/range validation; exact labels use applied parameters. | Defaults, period2 legacy arithmetic, EMA23 navigation/reset, server parameter tests and full regression. | Conventional defaults are not optimized parameters; formulas unchanged; retest PENDING. |
| UAT-005 | Strict adjustment eligibility produced unexplained codes; manual ranges/selections obscured common dates; legacy summary omitted volatility/drawdown. | backend/app/comparison.py, research.py, schemas.py; ComparisonPanel.tsx and api.ts add v2 metrics, explicit same-Dhan provisional opt-in, plain messages, cached actual-date intersection, freshness/missing summaries and expandable codes/evidence. | 20 new backend cases; unit strict/opt-in/cached-range/interleaved dates; browser compatible and unavailable bases, four-primary pair workflows and provisional comparison. | No adjustment/total-return/PIT qualification inferred; no fill; stale evidence remains visible; retest PENDING. |
| UAT-006 | Optional saved-runs lookup delayed primary context; controls retained old results. Browser reproduction additionally found edits cancelling initial context and duplicate StrictMode context requests hitting FORECAST_BUSY; edits could erase the context failure while leaving Generate disabled. | ForecastingResearch.tsx/forecastTypes.ts, backend/app/forecast_research_service.py add six-step Basic/Advanced UI, nonblocking optional lookup, guarded request/response identities, in-flight context deduplication, persistent visible context errors, obsolete-result clearing and Decimal display changes. | 20 forecast unit tests including delayed context/records, edits/cancellation/mismatch/StrictMode deduplication/context-error recovery; browser B01/B02/B03 horizons1/5/20, strict/replay acknowledgement, exact native endpoints, evaluation and paging. | Models/metrics unchanged; B03 has no directional endpoint; predictive accuracy unproven; retest PENDING. |
| UAT-007 | No coherent owner-facing training handoff explained these workflows. | docs/06-user-guide guide, four workflows, slide specification and four browser screenshots; scripts/build_user_guide.py publishes local HTML/Markdown help. | Browser help HTTP200; official Draw.io runtime opens/edits/exports/reopens all four; real synthetic browser captures wait for chart rendering and were visually inspected. | PowerPoint tooling unavailable; complete 12-slide Markdown specification supplied instead, as authorized; retest PENDING. |

All frontend filenames above are under frontend/src unless another path is shown. Complete paths are in the manifest.

## B. ETF Comparison

See ../03-design/MVP06_UAT_REMEDIATION_DESIGN.md for exact formulas, precision, guards and traceability. The v2 comparison uses shared observed dates, identical endpoints and compatible currency/basis/data class. Rebase=100*close/start; endpoint return=100*(end/start-1). Volatility is sample standard deviation of matched reviewed one-session simple returns, percentage units, no annualization; missing/unreviewed intervals are excluded and counted. Maximum drawdown uses common observed closes only. The available-period helper intersects actual cached dates and refuses interleaved histories with no shared observations.

Strict compatibility is the default. Explicit provisional mode is restricted to the same DhanHQ source/provider basis, with source limitations acknowledged; it neither upgrades source rights nor overrides breaks/conflicting references. Data freshness and missing sessions are summarized; full evidence is expandable. Gold/Silver and other compatible pairs among the four primary ETFs are supported, with up to ten distinct listings in the existing contract.

Independent arithmetic fixture: 100/120/90 versus 200/240/180 on three reviewed consecutive sessions -> both indices100/120/90, return -10%, maximum observed drawdown25%, sample session volatility31.819805153395%. This is generated arithmetic, not ETF investment performance.

## C. Forecasting UX

Select ETF, horizon and model, Generate Forecast, review origin/target/endpoint/change, optionally evaluate history. Existing context, run, evaluate, session records and bounded refresh routes are reused. Requests do not run merely because controls change. A valid primary context is usable even if optional records fail. Results must match requested ETF/source/horizon/lookback/model set. Stale and cancelled responses cannot replace current results.

B01/B02 summaries include exact absolute and percentage changes using the existing Decimal serialization context. B03 is separately labeled as volatility with null price-change fields. Lightweight Charts remains primary, Plotly fallback retained, endpoint markers never imply a fabricated intermediate path. Advanced controls are initially collapsed. Strict real-data evaluation, explicit acknowledged conditional replay and synthetic mode remain distinct; B01/B02 common-origin and separate B03 performance evidence are unchanged. Existing 15-row paging remains.

The generated screenshot fixture demonstrates B01 endpoint172, B02 endpoint194.554501265747 and B03 horizon volatility0.000961335644 for a 20-session/20-close synthetic request. These are UI verification values from generated observations, not real prices, accuracy results or investment recommendations.

## D. Training artifacts

- ../06-user-guide/BULLION_INTELLIGENCE_USER_GUIDE.md:13 topics plus exact seven-case retest checklist.
- ../06-user-guide/workflows/application-navigation.drawio.
- ../06-user-guide/workflows/etf-comparison.drawio.
- ../06-user-guide/workflows/forecast-generation.drawio.
- ../06-user-guide/workflows/forecast-evaluation.drawio.
- ../06-user-guide/TRAINING_SLIDE_SPECIFICATION.md:12 slides with content, layout, speaker notes, screenshot references and alt text. No PPTX claimed: required presentation-generation runtime unavailable.
- Four images under ../06-user-guide/images, captured from the actual synthetic browser workflows, explicitly labeled SYNTHETIC TEST DATA. They contain no real market responses or owner account data.
- frontend/public/user-guide.html and user-guide.md: intentional reproducible local help publications of the canonical guide, generated by scripts/build_user_guide.py. They are not compiled application bundles.

Draw.io verification: official full editor HTTP200 (embed endpoint returned403); each standard XML file opened in the real EditorUi runtime, its first vertex label edited, exported, restored and reopened; six vertices/five edges retained. Private application data/credentials were not sent to Draw.io. Local receipt artifacts/drawio-editor-verification.json is excluded from Git.

## E. Verification

Final complete isolated run: scripts/engineering.py test; artifacts/verification.json records all six checks exit0.

| Check | Actual result |
|---|---|
| Backend including PostgreSQL/migration/integrity/concurrency/security/recovery regressions | 979 passed;0 failed;0 skipped;6 existing deprecation warnings; browser fixture logs can report a socket reset when an obsolete request is cancelled |
| Frontend | 73 passed in10 files;0 failed;0 skipped |
| Chromium workflows | 14 passed;0 failed;0 skipped; native/fallback, mobile, strict/replay, chart interactions, navigation/errors and new UAT regressions |
| Python lint / TypeScript / Vite production build | PASS; existing large lazy Plotly chunk warning retained |
| Frozen Python advisory audit | 40 packages;0 vulnerabilities;0 skipped; full dependency-resolving scan and bounded exact-version scan passed |
| npm advisory audit |0 vulnerabilities, full dependency tree |
| Isolated Compose build/start | PASS, independent bullion-mvp06 images/network/volume; loopback-only ports; no owner env or provider credentials |
| Isolated container recovery | PASS restart, graceful stop/start, idempotent up, catalogue checksum retained, nonroot UIDs API10001/UI1000/DB999; gosu absent; provider disabled |
| Owner protection |33 metadata/hash/Git comparisons pass, including unchanged pre-existing stopped services; no owner cache/SQL query or data copy |

Final built-image UI smoke and current-image identities are recorded in the verification addendum below. Local XML/log/SARIF/browser traces remain ignored; the approved training PNGs are the only intentionally committed screenshot artifacts.

Earlier checks found and corrected three calendar-null comparison500s, the initial-context cancellation race, one incomplete mock model set, obsolete hidden-evidence selectors, empty Plotly traces, test teardown requests and the StrictMode FORECAST_BUSY/context-error visibility race. Initial failing runs are retained locally. No test is dropped or skipped to make the final run pass. Malformed-snapshot browser testing intentionally injects a section error; normal workflow runtime-error assertions remain intact.

## F. Security, source-control review and commit plan

Current unfiltered image scans report API55 rules (0critical/2high/2medium/28low/23unspecified;68 location results), UI1high rule/result, DB65 rules/results (0critical/4high/6medium/55low). API highs:CVE-2026-76844/CVE-2026-85091 zlib. DB adds CVE-2026-86140/CVE-2026-74860 libxml2. UI:CVE-2026-107891 musl1.2.6-r3, already tracked as stable-branch-fixed scanner discrepancy by MVP-05. Raw findings retained, no ignores or disposition changes. Six open Debian image/finding instances plus the separately documented UI discrepancy remain; no security clearance or risk acceptance.

No changes to provider authentication/transports, token flow, trading, storage schema, real caches, requirements, approved decisions, base-image pins or dependency versions. Engineering changes only redirect project/ports to isolated MVP-06 and prevent implicit registry fallback on start. .env, credentials, restricted data, database exports, backups, builds and diagnostic artifacts are excluded. Local security and exact staged-content scans are recorded in the final receipt.

Plan: one coherent implementation/regression/isolation checkpoint, followed by the training/design/evidence checkpoint. Push only feature/mvp06-uat-ux-remediation with a normal fast-forward; no main merge, tag, force or owner deployment. Exact file manifest is reviewed before staging; final local/remote SHA equality is reported after synchronization. No unrelated/destructive changes are authorized.

## G. Owner retest

Follow the full seven-case Owner retest checklist in the user guide. Test UAT-001 visibility under repeated selections/errors, UAT-002 EMA23 plus visibility across History and Gold switch, UAT-003 all six indicators including insufficiency, UAT-004 defaults/validation/reset, UAT-005 common-date comparison/provisional warnings/no overlap, UAT-006 supported forecast horizons/model changes/strict and acknowledged replay/paging, and UAT-007 instructions/help/diagrams/training.

Record candidate build identity, actual source class, exact dates and pass/fail with sanitized evidence. Retest is blocked on a separately controlled deployment/handoff; this package never swaps the owner's active services or restores/refreshes their RAM cache. All seven owner statuses remain PENDING.

## H. Release limitations and recommended next action

Open security dispositions; source-use/retention/backup rights; provider adjustment, publication/finality, revisions and timestamp qualifications; strict historical point-in-time evidence; independent statistical/model validation; prior provider-attempt23->24 attribution; owner acceptance and authorized handoff remain unresolved. Original lost cache provenance remains unrecoverable and is not reconstructed by later data.

The engineering candidate is ready for review and a separately authorized controlled handoff/retest plan, subject to those gates. Do not infer release approval. Do not begin a new model or trading package. Preferences/results remain transient; unmanaged exits still lose memory. Training fallback does not claim a generated or verified PowerPoint file.

## Final built-image and security addendum

Built candidate identity: API sha256:6287517e9162cb2119627c6a1a08b4b57fd1b6a6dea0f7e58f68a22f38a189f8; UI sha256:f4c83f6e89166a842c691ce8363f4af47c699181a07e5d6a4238c916107c431f; DB sha256:76f96290bf41cc91ca50f875af692ae28a944f30afbe54e7cdefb8e018c6e89a. All56 production Python modules match the final source. Immutable base pins remain unchanged; these are independent engineering image tags, not an owner deployment or release tag.

Built-image synthetic smoke: native and Plotly charts, forecast generation and historical evaluation PASS;0 page errors and0 CSP errors. Synthetic provider counters quote1->1/intraday0->0 during forecast/evaluation. This records fake-provider activity only; no live DhanHQ operation occurred. Measured420ms forecast and1060ms evaluation are one local smoke observation, not a latency guarantee.

Actual Linux production metadata:31 packages,0 vulnerabilities/0 skipped. All three final exact images were rescanned without filters; final findings are listed above. Windows40/npm full tree also have0 vulnerabilities. Source/tag/credential review checks six locally configured secret values without printing them, plus private-key/JWT/GitHub/AWS signatures, output bundles/logs and file-size/artifact exclusions. No configured-secret or signature match was found. This bounded scan does not prove the absence of every possible secret and does not clear the retained OS findings.

Routine browser tests save screenshots only under ignored artifacts/mvp06-training. Regenerating the four approved training images requires the explicit process flag MVP06_CAPTURE_TRAINING=1 with the existing isolated synthetic Playwright suite. The committed images were generated and visually inspected from the same verified workflows; no fabricated screenshots or real observations were persisted. A faster repeat exposed HTTP429 FORECAST_BUSY from concurrent StrictMode context effects (the initially suspected rate limit was not the confirmed cause). Final context deduplication is tested directly; no production guard was weakened. A temporary test-only isolation approach was removed before this checkpoint. The full suite was rerun after the correction; application source and tests are represented by the final results above.

Implementation and local-help source, unit/browser regressions and isolated lifecycle controls form the first logical commit. The design note, training workflows/images/slide specification, exact manifest and this verification report form the second. Neither commit changes owner services, main, requirements, existing tags or security dispositions. Post-push identity/equality and final working-tree status are reported in the completion response.


Final scan delta: two additional LOW advisories were reported in each of the API and DB inventories: CVE-2026-27171 (zlib, scanner lists patched Debian revision 1:1.3.dfsg+really1.3.1-1+deb13u1) and CVE-2026-115456 (gcc-14, no fixed version reported). Installed package versions/base pins were not changed by MVP-06. These newly observed inventory entries are retained, not suppressed or treated as remediated; they do not alter the six existing open HIGH instances or the UI branch-qualified discrepancy. Security dispositions in the MVP-05 baseline were not edited.

Implementation commit:771a03ed8508673a4d56276207fd94f9d8068547 (48 files). Training/evidence is a separate12-file checkpoint; its final hash is in the completion receipt. Normal regression writes only ignored artifacts, so the reviewed source/training images remain clean after tests. The isolated bullion-mvp06 services were stopped after verification; images and synthetic volumes retained. Protected owner UAT remains running in its original state.
