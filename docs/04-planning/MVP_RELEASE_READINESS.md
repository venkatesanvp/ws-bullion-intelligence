# Local Research MVP release readiness

Status: NOT RELEASED / NOT OWNER ACCEPTED. Candidate preparation only. No commit/push/tag authorized for this package.

| Gate | Current status |
|---|---|
| PR #1 baseline | Verified merged at afa434cf2fe7e432f63b241f32e95bdcd2b3b621 |
| MVP-02/03/04 implementation | Implemented and verified within stated limits |
| Full backend/frontend/browser/build/container checks | PASS: 915 backend / 62 frontend / 11 browser; lint/build/container/synthetic recovery and deployed smoke |
| Credential/dependency/data-governance checks | PASS: dependency and credential checks; image CVE result recorded separately |
| Owner UAT | Pending owner execution |
| Source rights/retention/private backup permission | Unqualified; no durable market-data retention added |
| Provider timestamp/publication/finality/adjustment/revision evidence | Open; matching source values does not establish economic point-in-time purity |
| Forecast validation | Deterministic baselines only; no superiority/significance/calibration claim |
| Provider-attempt anomaly | Historical 23?24 remains unattributed; bounded future operation logging added |
| Repository protection and CI | None configured remotely; no settings changed; local reproducible verification remains required |
| Requirements and tags | Must remain unchanged; no release tag |

Recommend owner SIT evidence review and UAT after verification, then a separately authorized source checkpoint/PR. A source commit does not establish full VS-01 acceptance, licensing clearance or production readiness. Durable forward-evaluation evidence needs a separate retention/architecture authorization.

Recovery incident REC-02 is material: the original transient cache was lost during the first deployment. Origin handling/preflight are corrected and must pass final regression. Owner authorized fresh transient reacquisition, which cannot recover prior identities/first-seen evidence. UAT must use the new acquisition context. No claim of successful original-cache preservation or durable recovery is permitted.

Actual-data readiness: fresh approved Dhan data available for all four ETFs (248 daily + 75 five-minute candles each). All three baseline models and technical routes operate on the cached inputs; strict historical scoring remains correctly blocked at zero origins. No quotes were reloaded because the nine-attempt authorization was exhausted. UAT should start with these newly acquired vintages, not assume the lost original cache/provenance survived.

The owner replaced the rejected token locally; only the token value differed from the prior backend environment. .env remains ignored/untracked, agent did not edit credentials, and all credential-isolation checks pass. Existing API runtime remains root (not privileged); frontend is non-root/read-only/capability-dropped. Image OS CVE results must not be conflated with zero-vulnerability Python/npm audits.

## Final image security gate

Project dependency/credential checks pass, but image security is not clear: API 7 high / 0 critical, UI 8 high / 0 critical, PostgreSQL 35 high / 4 scanner-reported critical findings. One critical is Windows-specific and not applicable to the verified Linux image; three require binary reachability qualification and/or patched compatible image selection. All raw findings are retained. [Security assessment and full rule inventory](MVP_SECURITY_ASSESSMENT.md) records severity, packages, fixes, exposure, remediation and compatibility. **Release security clearance is blocked.**

Runtime hardening removed unused pip/npm/Yarn/Corepack tooling without changing the required API uv command or frozen dependencies. Final guarded deployment preserved the fresh real cache exactly (992 daily/300 intraday, original new IDs/first-seen times, counter 8?8), with no fallback and no provider calls. Full offline preflight also validated the same real snapshot without changing the active cache. This success does not undo REC-02's loss of the original pre-MVP cache.

Reproducibility: generated TypeScript cache/log files are excluded from frontend build context. Consecutive builds had identical rootfs layers and runtime configuration; image/index IDs differed with provenance metadata. Provenance was retained, not disabled to force matching IDs. Base digests/lockfiles remain fixed. Functional UAT is prepared; security/source/retention/statistical gates and owner acceptance remain open.
