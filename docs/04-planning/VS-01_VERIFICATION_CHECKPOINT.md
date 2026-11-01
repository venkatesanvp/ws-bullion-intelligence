# VS-01 verification and proposed Git checkpoint

Prepared 2 November 2026 (Asia/Calcutta), from review/executions spanning 1-2 November. Authority: the current human Step 3 verification, safe remediation, isolated recovery, regression and checkpoint-preparation instruction. **No commit, tag, push or next-increment implementation is authorized by this record.**

## Readiness assessment

The authorized data-workbench subset is suitable for a reviewed implementation checkpoint. **Full VS-01 and R1 are not accepted.** A successful implemented suite does not complete absent analytics, charts, qualified real-data acceptance or cumulative handover. Requirements' approval/maturity/priority/allocation and D-01..16 remain unchanged. Historical Step 2 proposal labels are superseded only within the separately recorded scoped approval in IMPLEMENTATION_STATUS, not globally rewritten.

| Work item | Actual status | Implementation/evidence and remaining boundary |
| --- | --- | --- |
| WI-01 locked local runtime | Implemented and verified for approved scope | Dependency locks, pinned Python/Node/PostgreSQL/uv inputs, clean npm ci, two pinned Compose builds/startups, local configuration checks. Cross-platform/byte-identical image claims excluded. |
| WI-02 persistent schema/migrations | Implemented and verified | All eight domain tables, Alembic revision, actual PostgreSQL constraints/immutability and concurrency tests; empty isolated databases migrate successfully. |
| WI-03 local API access/errors | Implemented and verified for approved controls | Token/origin/host and upload/error tests, no-token readiness 401, authenticated readiness 200, actual frontend secret-value scan. No broad external penetration-test claim. |
| WI-04 catalog/source/watchlists | Implemented and verified for scoped software flows | PostgreSQL/API create/edit/membership cases, UI source qualification and watchlist/reload workflow. Synthetic identities are not qualified real ETF listings. |
| WI-05 atomic CSV ingestion | Implemented but not fully verified for slice acceptance | Canonical synthetic validation, exact decimals/raw provenance, rollback, retries/conflicts and concurrency verified. Actual permitted Gold/Silver ETF sample acceptance is blocked by SQ-01. |
| WI-06 history/quality | Implemented and verified for approved scope | Source/basis-specific history/cursors, calendar and freshness disclosures; new endpoint-bound gap tests, explicit STALE/empty/nonmatching-as-of cases; no charts/derived metrics. |
| WI-07 deterministic indicators | Not implemented; approval-blocked | ADR-06/DC-05/SQ-04 and scoped SQ-07 grant pending. No SMA/EMA/RSI endpoint or calculation code. |
| WI-08 price-only comparisons | Not implemented; approval-blocked | Remaining ADR-10/DC-06/SQ-05 and scoped SQ-07 grant pending. |
| WI-09 import/quality UX | Implemented and verified for approved portion | Qualification gate, imports/outcomes/issues, retained retry identity and escaped/synthetic/unknown states; browser and component evidence. Real-source T-03 remains blocked. |
| WI-10 chart/indicator/comparison dashboard | Partially implemented foundation; remaining capabilities blocked | Listing/source/basis/date controls, history table and quality views exist. Charts, overlays and comparisons are absent; ADR-07 and analytical/display contracts require approval. |
| WI-11 integrated acceptance/security | Partially implemented/verified | Current real-PostgreSQL, component/browser and dependency-security suite passes. Full real-data and chart/analytics acceptance is unexecuted. |
| WI-12 restart/restore/handover | Partially implemented/verified | Repeated startup, app-restart persistence and synthetic separate recovery verified. Final full-slice handover, owner-data recovery/cutover and retention disposition remain pending. |

**Blocked acceptance:** SQ-01 and VS01-T-03 require a qualified real dataset and rights/identity/coverage evidence. No sample was provided or accepted. Searches found no qualified CSV package in repository source; restricted backup/cache directories contain test artifacts and were not treated as candidate market datasets. No external ETF download/ingestion occurred.

## Designed cases versus executed evidence

| Designed cases | Current evidence/disposition |
| --- | --- |
| T-01/02 | Listing/watchlist API persistence and response-selection race tests; real browser creation/membership/reload path. Approved software behavior covered using synthetic identities. |
| T-03 | **Blocked, not passed:** no permitted independently identified Gold and Silver samples; chart criterion also awaits implementation. |
| T-04..08 | Parser/actual PostgreSQL hard validation, atomicity, exact/raw provenance, idempotence, precommit/lost-response faults, concurrency and policy locking exercised. |
| T-09/10/17 | History/cursor/revision/quality/calendar cases exercised; explicit FRESH/STALE/UNASSESSED and observed-endpoint regressions included. Chart/derived extensions remain outside current scope. |
| T-11..16 | **Not implemented/not executed:** indicator/reference/comparison cases await approvals and code. Not hidden as skipped pytest cases. |
| T-18 | **Partial:** import/history/quality states and accessible table covered; chart/indicator/comparison and complete real-data journey absent. |
| T-19/20 | Existing auth/origin/host, upload bounds/type/mapping and safe-error cases, token persistence/build-value checks. This is bounded executed evidence, not exhaustive adversarial certification. |
| T-21 | Fresh migrations, app restart, health-gated startup and new reachable-but-wrong-schema readiness/data rejection case pass. Actual owner-volume loss was not simulated. |
| T-22 | **Scoped synthetic recovery passed:** backup/checksum/list/isolated restore, all table hashes and known history query; absent indicators and owner-data restoration are not verified. |
| T-23 | Locks/image/browser versions, local-only exposure, scope/secret/baseline review; final Git commit remains gated on confirmation. |

## Regression, security and recovery results

- Backend: **62 passed, 0 failed, 0 skipped**. This includes PostgreSQL integration and four added test cases: two parameterized observed-endpoint boundary cases, one explicit freshness case and one wrong-schema case.
- Frontend: **6 passed, 0 failed, 0 skipped**, Vitest 4.1.12. Browser: **1 passed, 0 failed, 0 skipped**, real UI/API/PostgreSQL Chromium workflow. TypeScript/production build and Python lint pass.
- Two backend deprecation warnings remain (Starlette/httpx test-client path and Alembic path_separator); browser tooling reports NO_COLOR/FORCE_COLOR warnings. They did not fail or skip checks and were not suppressed.
- npm full and production-only scans: **zero findings**, down from three affected packages/two critical aggregate findings. Windows Python scan: **40 packages, zero findings/skips**. Linux API scan: **28 packages, zero findings/skips**. No unresolved critical finding in those scanned dependency sets. Details and exploitability/compatibility analysis: [security review](VS-01_SECURITY_REVIEW.md).
- Recovery: source/restored databases have matching full-row hashes/counts for all eight domain tables and the migration table, matching normalized schema objects, no orphan observation provenance, matching fixed-as-of exact-price history output, and a working restored append-only trigger. Backup is custom-format binary, checksum verified, restricted and ignored. [Instructions and limitations](../05-operations/LOCAL_RECOVERY.md).
- Container pins/provenance, repeated startup, version consistency and no-public-DB configuration are recorded in the [reproducibility review](VS-01_CONTAINER_REPRODUCIBILITY.md). Runtime dependency scans do not establish OS-image CVE clearance or independently signed provenance.

Earlier failures were retained and resolved rather than relabeled as successful runs: Windows launcher/HTTP-method/test-locator failures from the previous checkpoint; npm 10's Arborist update crash (isolated npm 11 used, existing npm ci then succeeded); and recovery's initial equivalent enum-cast schema mismatch. Final reports reflect successful runs. Recovery failure summaries and pre-remediation audit remain in ignored artifacts. No financial result, market signal or probability was generated.

Raw execution evidence remains local/ignored: `artifacts/verification.json`, `backend-tests.xml`, `runtime-verification.json`, `frontend-audit-before/after/production.json`, `backend-audit.json`, `backend-linux-audit.json`, `recovery-verification.json`, restricted `backups/recovery-*/`, and `frontend/playwright-report/`. The normal app remains available locally; the disposable test service is stopped after final evidence collection.

## Working-tree review and proposed commit

The existing application implementation is already in parent commit `6dea57f`. The proposed commit is the coherent checkpoint delta (repairs, remediation, locks, recovery verification and review records); it does not rewrite that earlier commit or the requirements baseline.

- Modified source/config/docs and new review/recovery files are listed exactly below.
- `frontend/package-lock.json` is an intentionally versioned generated dependency lock.
- `.env` (local passwords/token), `.venv/`, node_modules, caches, built frontend/dist, browser reports/traces, runtime test artifacts, SQL preview and backup archives remain excluded. No owner dataset, portfolio, account identifier or real credential is included.
- Known actual local password/token values are checked against candidate/staged content without printing values; ignore rules, baseline preservation and whitespace/diff checks are reviewed before handoff.
- No commit has been created. Staging prepares a reviewable index and does not imply acceptance or authorize commit/push.

Proposed message: `feat(vs01): implement market data ingestion and inspection workbench`

Exact proposed staged set (M=modified, A=new):

```text
M README.md
M backend/Dockerfile
M backend/app/queries.py
M backend/tests/test_integration.py
M compose.yaml
A docs/04-planning/VS-01_CONTAINER_REPRODUCIBILITY.md
A docs/04-planning/VS-01_DATA_QUALIFICATION.md
M docs/04-planning/VS-01_IMPLEMENTATION_STATUS.md
A docs/04-planning/VS-01_NEXT_PACKAGE_PROPOSAL.md
A docs/04-planning/VS-01_SECURITY_REVIEW.md
A docs/04-planning/VS-01_VERIFICATION_CHECKPOINT.md
A docs/05-operations/LOCAL_RECOVERY.md
M frontend/Dockerfile
M frontend/e2e/workbench.spec.ts
M frontend/package-lock.json
M frontend/package.json
M frontend/playwright.config.ts
M frontend/src/App.tsx
A scripts/verify_recovery.py
```

## Next authorization to review

See the [bounded next-package proposal](VS-01_NEXT_PACKAGE_PROPOSAL.md): WI-07/08/10 plus remaining WI-11/12; ADR-06/07 and remaining comparison portions of ADR-10; DC-05/06 and applicable analytical/chart/comparison portions of DC-04/07/08; SQ-04/05/07, with SQ-01 and applicable SQ-06 gates retained. No next-increment source/dependencies have been implemented. Confirming the Git checkpoint alone does not approve that increment.
