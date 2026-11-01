# VS-01 Step 4 research dashboard completion

Recorded: **2 November 2026 (Asia/Calcutta)**. Starting commit `5f0399b40eaa790117c5ab0e4c9ececf08ed251a`; initial working tree was clean. This proposed checkpoint is uncommitted and unstaged. No tag, push or full VS-01/R1 acceptance.

The authorized software capabilities are implemented and verified with explicitly synthetic data. SQ-01 real-source qualification, T-03 and final owner operational/human acceptance remain open. No unqualified market data was downloaded or ingested.

## 1. Work items and authority

| Work item | Delivered capability / status | Existing trace |
| --- | --- | --- |
| WI-07 | Implemented and verified: pure SMA, SMA-seeded EMA and Wilder RSI; versioned exact results, seeds, warm-up/gap/flat reasons | REQ-03-001/007, REQ-06-002/006 -> ADR-06/10 -> DC-04/05/07 -> T-11..14 |
| WI-08 | Implemented and verified: explicit-period common-date price-only comparison and base-100 paths | REQ-02-007, REQ-03-008/009, REQ-04-013 -> ADR-05/07/10 -> DC-04/06/07 -> T-15/16 |
| WI-10 | Implemented and verified in approved research scope: charts, configurable overlays/separate RSI, comparisons, exact table alternatives and quality/source disclosures | REQ-03-007, REQ-04-001/005/006/013 -> ADR-02/05/06/07/10 -> DC-04..08 -> T-02/18 |
| WI-11 | Partial: cumulative synthetic unit/API/DB/component/browser/security evidence passed; qualified real-source T-03 and cumulative human acceptance remain open | REQ-06-002/006/007/008 -> ADR-08/09 -> DC-09 |
| WI-12 | Partial: pinned rebuild/repeated startup, Linux math and isolated synthetic recovery passed; owner-data cutover/retention and final handover remain open | REQ-05-001/009, REQ-06-008 -> ADR-09 -> DC-09 -> T-21..23 |
| WI-01..06, WI-09 | Existing approved implementation regression verified; WI-05 real-source acceptance remains blocked | Prior Step 3 checkpoint and cumulative suite |

Actual dependency order: existing WI-06 precedes each of WI-07 and WI-08; WI-10 follows WI-07/08/09; applicable WI-11/12 verification follows. The prior proposal's incorrect WI-08 dependency was corrected.

Step 4 scoped approvals are recorded in the ADR register/design/backlog: ADR-06/07 and remaining research ADR-10, DC-05/06 and applicable DC-07/08. SQ-04/05 resolved. Before calculations, the former common n>=1 minimum was reported as conflicting with the new RSI n>1 instruction; the explicit Step 4 refinement was recorded. SMA/EMA retain n>=1; RSI requires n>=2. No new trading policy or default lookback was selected. Earlier Step 3 scoped grants remain in force; SQ-01 and conditional SQ-06 operational gates remain open as documented.

D-01..16 and the original baseline are preserved. `requirements-v1.0` remains annotated object `5eeed03536e43ded7077ac086b97cb05f2e5b73e`, resolving to `e10eef55fb21368e53dbe4599006b620cbb48566`; AGENTS/project-context/requirements content has no diff from that baseline. Baseline parent approval/maturity/priority/allocation are not promoted by this implementation.

## 2. Source changes

The exact source/document file set is in section 10. New pure engines are `backend/app/analytics.py` and `comparison.py`; `research.py` supplies read-only API orchestration. Existing main/schema code registers routes, validates selections and gives comparison POST the same repeatable-read snapshot boundary as GET. No schema/migration, service, Python dependency or image change was needed.

Frontend additions are ResearchDashboard, ComparisonPanel, ResearchChart and shared disclosures/types. App adds research/comparison navigation and metal selection within the existing visual design. Exact runtime Plotly basic 4.2.0 and development types 3.0.15 are lockfile-pinned, with MIT attribution preserved. New independent arithmetic/API/component/browser tests and the extended isolated recovery verifier accompany the behavior.

## 3. API and UI workflows

All routes use existing `/api/v1` authentication, safe error envelope and local origin controls:

| Route | Inputs and behavior |
| --- | --- |
| GET /instruments/{id}/chart | Explicit source_id/basis; optional inclusive start/end and assessment_as_of. Complete selected history up to 10,000 points, exact closes, known-break markers, observation/batch/row lineage, SeriesRef, input fingerprint/evidence and quality metadata. |
| GET /instruments/{id}/indicators | Explicit source_id, basis, SMA/EMA/RSI and integer n; optional range/as-of. Calculate the entire eligible prefix through end before clipping start. Return 12-place values/null reasons, seed dates, algorithm version, profile/revision and input evidence. |
| POST /comparisons | Read-only calculation, 2-10 distinct listing/source/basis selectors and required start/end, optional as-of. One consistent DB snapshot; actual common-date endpoints, exact close/volume, changes, base-100 paths, per-series provenance/quality and price-only limitations. |

Unsupported/incompatible requests return safe 422 unavailable errors; no/one common date remain explicit unavailable/partial outcomes. Unknown price basis can be inspected raw but does not produce a derived indicator. Excess research input is rejected without silent prefix truncation. Numeric ranges unsupported by the fixed Decimal framework return NUMERIC_UNSUPPORTED rather than approximate financial results.

Research dashboard selects Gold/Silver ETF, source, basis and available/explicit dates. Each overlay requires an explicit period and Apply; toggles remove lines immediately. RSI is separate without buy/sell thresholds. Comparison has explicit per-series selectors/dates and common-date details. Both expose synthetic/quality/freshness/unavailable state and exact table alternatives. Source/profile/revision mismatch and late responses are rejected/aborted; no stale ETF line is reused. Known breaks/nulls remain gaps. Chart labels are escaped. Plot coordinates approximate server strings; no authoritative financial calculation occurs in JavaScript.

## 4. Indicator mathematics and independent verification

All authoritative arithmetic uses a fresh local Decimal context, precision 34, HALF_EVEN. Derived serialization is 12 places; observed prices retain their exact canonical values. This is serialization precision, not a claim about market accuracy. Neither engine mutates global arithmetic context or reads a clock/network/DB.

- SMA: mean of latest n eligible observations, unavailable before n.
- EMA: SMA seed from first n, then alpha=2/(n+1) recurrence, unavailable until seed.
- Wilder RSI: first n price changes seed average positive/negative changes; subsequent average=(previous*(n-1)+current)/n. Gain-only=100, loss-only=0, both zero unavailable. At least n+1 observations required.
- Declared discontinuities/known missing sessions reset the segment and seed. No elapsed-day calendar guess, missing price fabrication or fill. Full-prefix overlap is invariant under display-window changes and future appends.

For synthetic closes `[10,12,14,13]`, n=2:

| Indicator | Exact expected sequence |
| --- | --- |
| SMA | null, 11.000000000000, 13.000000000000, 13.500000000000 |
| EMA | null, 11.000000000000, 13.000000000000, 13.000000000000 |
| RSI | null, null, 100.000000000000, 66.666666666667 |

26 pure cases include these hand vectors and seeded synthetic series checked against independent exact Fraction references. EMA/RSI references use closed-form weighted sums rather than production recurrences, and a separate integer quotient/remainder ties-to-even serializer. Tests cover n=1 where allowed, RSI rejection of n=1, invalid bounds/types, empty/short/flat/gain/loss, ordering, context isolation and gap/prefix invariance. PostgreSQL API cases verify the stored series, display prefix and future append behavior. Additional synthetic SMA/EMA/RSI reference vectors passed inside the actual rebuilt Linux API.

## 5. ETF comparison verification

For synthetic common-date paths `[10,11,12]` and `[20,22,23]`, expected changes are exactly `20.000000000000` and `15.000000000000` percent; the second rebased endpoint is `115.000000000000`. An independent Fraction check confirms endpoint percentages, including negative changes. Sparse paths use only their observed intersection; a single common point returns its close with percentage/rebase unavailable; zero overlap is unavailable.

11 pure cases plus DB/API/browser cases cover explicit periods, sparse/no/one common date, incompatible currency/basis, unknown basis, mixed real/synthetic classes and adjusted-definition compatibility. Adjusted inputs conservatively require identical nonempty recorded adjustment-definition references. No source equivalence is inferred. Null volume remains null. A concurrent append during the API comparison confirms both series still report the same pre-append snapshot while the database revision advances afterward. Browser fixtures additionally verify 40%/15% endpoints with clearly synthetic data.

Displayed limitations: price-only, no inferred distributions/adjustments, no total return or NAV/spread claim, no future-performance inference and unverified for replay. No financial recommendation or trade threshold is added.

## 6. Actual regression results

Final command: `.venv/Scripts/python.exe scripts/verify_local.py --database --browser` after source changes were frozen. Normal UI was stopped to free port 5173, then Compose rebuilt/restarted after browser execution.

| Verification | Actual result | Local evidence (ignored) |
| --- | --- | --- |
| Backend including actual disposable PostgreSQL | **114 passed; 0 failed/errors/skipped** | `artifacts/backend-tests.xml`; `artifacts/verification.json` |
| Frontend component tests | **16 passed; 0 failed/skipped** | verification command output and `artifacts/verification.json` |
| Chromium actual UI/API/PostgreSQL workflows | **3 passed; 0 failed/skipped** | `artifacts/browser-tests.xml`; `frontend/playwright-report/` |
| Python lint | Passed | `artifacts/verification.json` |
| TypeScript and production build | Passed | `artifacts/verification.json` |
| Linux Decimal reference execution | Passed | `artifacts/step4-linux-arithmetic.log` |
| Compose rebuild and repeated startup | Passed | `artifacts/step4-compose-startup.log`; `step4-compose-repeat-startup.log`; `step4-runtime-verification.json` |
| Synthetic isolated recovery | Passed | `artifacts/recovery-verification.json` |

Research additions account for 26 indicator, 11 comparison and 15 PostgreSQL API cases; original 62 backend cases remain passing. Component additions cover chart failure/table fallback, exact hover/null breaks, safe labels, StrictMode lifecycle, explicit parameters/toggles, response races and comparison states. Original ingestion/watchlist/quality browser workflow passes alongside two research workflows. Desktop/mobile screenshots were visually inspected; the 390px mobile workflow also asserts no horizontal overflow and captions below plots. Browser verifies local-only HTTP origins and no local/session storage credentials. No provider call is required.

Initial failures and retained limits:

- First research browser run found blank charts: an obsolete StrictMode render purged the current plot. Fixed by serialized render lifecycle handling; a component regression and full browser/cumulative rerun pass. Trace `artifacts/step4-browser-first-failure.trace.zip` retained. Mobile inspection found caption/date-label overlap; fixed with explicit plot space and observed-date ticks, then rerun.
- A transient TypeScript error during text-encoding cleanup was corrected before the final run. No failed/skipped test is relabeled as passing without execution.
- Initial runtime reporting probe assumed the UI had a Docker HEALTHCHECK. Corrected to running state and HTTP 200; API/DB health and migration exit are checked separately. Original `step4-runtime-first-probe.json` retained; subsequent startup/checks passed. No app configuration was changed for this probe.
- Two backend dependency deprecation warnings, runner color warnings and Vite's large-chunk warning remain. Lazy Plotly chart chunk about **1,218 kB / 407 kB gzip**; initial main chunk about **272 kB / 84 kB gzip**. The warning was not suppressed. Chromium/current workstation and Linux/amd64 are the tested platforms.

Designed T-03 is **blocked/not executed**, not a skipped automated test. [Case-by-case execution disposition](../03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md#7-step-4-execution-disposition---2026-11-02) identifies synthetic coverage and operational limits rather than claiming all 23 designed cases have final acceptance.

## 7. Security results

| Scan | Actual final result | Ignored evidence |
| --- | --- | --- |
| npm full dependency audit | 0 findings, including critical | `artifacts/step4-frontend-audit-full.json` |
| npm production-only audit | 0 findings | `artifacts/step4-frontend-audit-production.json` |
| pip-audit 2.9.0, Windows installed environment | 40 packages; 0 findings, 0 skipped | `artifacts/step4-backend-audit.json` |
| pip-audit 2.9.0, actual rebuilt Linux API | 28 packages; 0 findings, 0 skipped | `artifacts/step4-backend-linux-audit.json` |

Step 3's three affected packages remain remediated; **no unresolved critical dependency finding in these scans**. No suppression, forced audit fix, arbitrary override or incompatible major update was used. Plotly/basic and types are exact-pinned with package integrity and MIT notice; Plotly is local/lazy, with no CDN. [Security review](VS-01_SECURITY_REVIEW.md) records package/license/exposure details. Actual local token/password are absent from changed/new source, production frontend and runtime logs. No personal portfolio or account data is introduced.

These are application-package scans; OS-image scanning, signatures and permanent absence of vulnerabilities are not asserted. The large chart chunk is an explicit measured compatibility/performance tradeoff under approved ADR-07.

## 8. Startup, container and recovery results

From the repository root, with Docker Desktop Linux engine available:

```powershell
python scripts/configure_local.py  # first use only; refuses overwrite
docker compose up --build -d --wait
```

Open http://127.0.0.1:5173 and use the locally stored ignored `.env` token at the access gate. Do not paste secrets into reports/commits. Public live=200, unauthenticated ready=401 and authenticated ready=200 were verified. API/DB health, migration exit 0 and UI HTTP 200 were verified after rebuild and repeated startup. Normal DB has no host port; UI/API publish loopback only. Test DB was stopped after verification, while normal application services remain running and the application volume is preserved.

Compose/Dockerfile Python/Node/PostgreSQL/uv digests are unchanged from Step 3. Locked frontend dependency selection includes Plotly; no new service/infrastructure was introduced. [Container review](VS-01_CONTAINER_REPRODUCIBILITY.md) records registry provenance and reproducibility limits; current input hashes are in `artifacts/step4-runtime-verification.json`.

Extended recovery command:

```powershell
.\.venv\Scripts\python.exe scripts/verify_recovery.py
```

Using only isolated synthetic source/restored test databases, verification created a restricted ignored PostgreSQL archive, checked SHA-256/TOC integrity, restored into a separate newly empty DB, matched all nine table counts/content hashes and schema objects, verified provenance/no orphans and append-only audit trigger, then matched fixed-asof history/chart/SMA(2)/EMA(2)/RSI(2)/price-only-comparison outputs. Fixture includes two listings, two batches, six exact observations and null volumes. Recovery research SHA-256: `87cf00a06a00bc81967c9ecbd9d20cb73f48ad8c3a00345eaeb485526ead83ae` before and after restoration. The active application DB was never a restore/reset target.

[Recovery instructions](../05-operations/LOCAL_RECOVERY.md) document reproduction and the manual review boundary before any real-data switch. Owner-data cutover, retention policy and arbitrary RPO/RTO/SLA were not verified or invented. Backup binaries, reports and screenshots are not proposed Git contents.

## 9. Remaining acceptance blockers and real-data qualification

1. **SQ-01 / T-03 blocked:** no inspected permitted real Indian Gold and Silver ETF historical CSV samples. Synthetic tests cannot establish licensing, market-price correctness, actual coverage or real-source acceptance.
2. **WI-11 partial:** qualified real-source end-to-end/chart/indicator/comparison review and cumulative human acceptance remain pending.
3. **WI-12 partial / conditional SQ-06:** owner-data recovery/cutover, retention decision and final handover remain pending. Tested synthetic recovery/startup evidence is complete in its stated scope.

Minimum real-data package: exact provider/file origin and acquisition method/date; reviewed terms/permission for retrieval, storage, analysis/display and retention/redistribution; verified Indian listing/exchange/symbol/metal/INR identity (ISIN where available); actual daily date/row coverage and representative permitted Gold/Silver samples; raw/adjusted price definition, units and adjustment evidence; original checksums/encoding/headers/canonical mapping; date/time/publication meaning, calendar/freshness/break/action/duplicate/correction limitations; and recorded reviewer/acceptance evidence. Remove unrelated account/personal columns before inspection. See [qualification checklist](VS-01_DATA_QUALIFICATION.md). Do not fetch a provider merely because it is publicly named.

No current indicator/chart/comparison ADR/DC/SQ approval is outstanding after Step 4; these remaining gates concern real data and final operational/human acceptance. Broader baseline Open/Proposed parents retain their original states. No full VS-01/R1 acceptance is declared.

## 10. Exact proposed Git checkpoint
**36 files: 20 modified, 16 new.** All remain unstaged; the index is empty. Proposed message: `feat(vs01): complete research charts indicators and ETF comparisons`. Commit creation awaits human review/approval of this exact scope.

| State | Repository-relative file |
| --- | --- |
| Modified | `README.md` |
| New | `backend/app/analytics.py` |
| New | `backend/app/comparison.py` |
| Modified | `backend/app/main.py` |
| New | `backend/app/research.py` |
| Modified | `backend/app/schemas.py` |
| New | `backend/tests/test_analytics.py` |
| New | `backend/tests/test_comparison.py` |
| New | `backend/tests/test_research_api.py` |
| Modified | `docs/02-architecture/ARCHITECTURE_DECISIONS.md` |
| Modified | `docs/03-design/VS-01_ACCEPTANCE_AND_TEST_PLAN.md` |
| Modified | `docs/03-design/VS-01_DETAILED_DESIGN.md` |
| Modified | `docs/04-planning/VS-01_CONTAINER_REPRODUCIBILITY.md` |
| Modified | `docs/04-planning/VS-01_DATA_QUALIFICATION.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_BACKLOG.md` |
| Modified | `docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md` |
| Modified | `docs/04-planning/VS-01_NEXT_PACKAGE_PROPOSAL.md` |
| Modified | `docs/04-planning/VS-01_SECURITY_REVIEW.md` |
| New | `docs/04-planning/VS-01_STEP4_COMPLETION.md` |
| Modified | `docs/05-operations/LOCAL_RECOVERY.md` |
| New | `frontend/e2e/research.spec.ts` |
| Modified | `frontend/package-lock.json` |
| Modified | `frontend/package.json` |
| Modified | `frontend/playwright.config.ts` |
| New | `frontend/public/licenses/plotly.js-LICENSE.txt` |
| Modified | `frontend/src/App.tsx` |
| New | `frontend/src/ComparisonPanel.tsx` |
| New | `frontend/src/ResearchChart.test.tsx` |
| New | `frontend/src/ResearchChart.tsx` |
| New | `frontend/src/ResearchDashboard.tsx` |
| New | `frontend/src/ResearchShared.tsx` |
| New | `frontend/src/ResearchViews.test.tsx` |
| Modified | `frontend/src/api.ts` |
| New | `frontend/src/plotly.d.ts` |
| Modified | `frontend/src/styles.css` |
| Modified | `scripts/verify_recovery.py` |

Reviewed exclusions: `.env`, tokens/credentials/account data, local configuration, `.venv`, node_modules, dist, caches, generated reports/JUnit/screenshots/traces and backup archives. Those local outputs remain ignored. The new license text is deliberate source attribution, not a generated build artifact. No ignored file is force-added. No root AGENTS, context/requirements baseline, schema/migration, image/Compose or unrelated application file changes are proposed. The existing Step 3 verification checkpoint remains historical and unchanged.

Git checks: current HEAD remains `5f0399b40eaa790117c5ab0e4c9ececf08ed251a`; `requirements-v1.0` tag/object and baseline source content unchanged; no staged files; proposed set checked for sensitive/generated paths, actual local secret values and common credential/private-key formats. Whitespace and local Markdown target checks pass. Ignored local manifest hashes permit this file set to be rechecked before any future staging/commit. No release tag was created.

## 11. Recommendation for the next release increment

Review this proposed software checkpoint first. The next VS-01 acceptance activity should be SQ-01 qualification of permitted real Gold/Silver samples, followed only after rights approval by T-03 and cumulative real-source research/quality/provenance verification, then the remaining WI-11/12 owner operational acceptance. Preserve explicit limitations if samples/rights or operational decisions remain unavailable. No additional chart/indicator/comparison formula approval is required within the recorded Step 4 scope.

After those gates, assess VS-01 acceptance separately. Broader R1 strategy, risk/portfolio, paper/manual and execution/AI work must use its existing roadmap requirements and a separate concrete design/authorization package; this task does not authorize or implement it. No release or next implementation increment was started.
