# VS-01 dependency security review

Review completed: 2 November 2026 (Asia/Calcutta). Authority: current human Step 3 verification/remediation instruction; no scope expansion or finding suppression. Findings below describe the pre-remediation lock, not the current dependency set.

## Original findings and actual exposure

npm reported **three affected packages**, with four underlying advisory identifiers. Vitest's critical classification includes its dependency chain; it is not a third independent critical exploit.

| Package before -> after | Dependency/exposure | Identifiers and reported severity | Assessment and remediation |
| --- | --- | --- | --- |
| `@vitest/mocker` 3.2.7 -> 4.1.12 | Transitive through the direct development dependency Vitest. Installed in the local development UI image, not part of the React production bundle. | [GHSA-82fw-gwwq-j7x9 / CVE-2026-84373](https://github.com/vitest-dev/vitest/security/advisories/GHSA-82fw-gwwq-j7x9), moderate; [GHSA-qxg6-89mg-rqv8 / CVE-2026-112949](https://github.com/vitest-dev/vitest/security/advisories/GHSA-qxg6-89mg-rqv8), moderate. | Redirect mocks can disclose files; manual mock registration can inject browser code when an exposed interceptor accepts unauthenticated WebSocket registrations. The reviewed Vite config installs React's plugin, not these standalone interceptors. Tests run once in jsdom; Vitest browser/API modes are not enabled. No matching remote entry point was found. This is a configuration-based exposure assessment, not proof against every compromised-development scenario. Both issues are patched by mocker 4.1.12. |
| `tinypool` 1.1.1 -> absent | Transitive through Vitest; test-worker tooling. No application CSV/API path supplies its worker options. Present in the former development image, not executed by normal UI/API startup. | [GHSA-5gmw-xhrv-c9v3](https://github.com/tinylibs/tinypool/security/advisories/GHSA-5gmw-xhrv-c9v3), npm critical (publisher labels the original advisory high); [GHSA-85c8-ppgw-ccpr](https://github.com/tinylibs/tinypool/security/advisories/GHSA-85c8-ppgw-ccpr), npm critical. | Prototype pollution can influence worker-module selection. Exploitation requires an additional pollution/input-control path; none was identified in this application's test-worker configuration. Patches are 2.1.1 for the original issue and 2.1.2 for the follow-up. Vitest 4 removes tinypool entirely, avoiding a potentially incompatible transitive override. |
| `vitest` 3.2.7 -> **4.1.12 exact** | Direct `devDependency`; invoked by `npm test`, not the normal application command. Development packages are installed in the local UI image, so dev classification is not a claim that the image excludes them. | npm critical aggregate via tinypool, plus the redirect-mock advisory above. | Upgrade to the patched 4.x release rather than npm audit's suggested 5.x jump. No `audit fix --force`, arbitrary override, audit exclusion or severity downgrade was used. |

## Compatibility assessment

The [Vitest 4 migration guide](https://v4.vitest.dev/guide/migration.html) was reviewed before the update. This release supports the project's Node 22 and Vite 7 versions. Pool configuration, mock restoration and coverage/browser changes were checked against `frontend/vite.config.ts`, `src/App.test.tsx` and `src/test-setup.ts`: no custom pools, coverage provider, constructor automocks or Vitest browser mode are used. Tests explicitly clear/stub globals and clean up the DOM. Playwright remains a separate runner.

Six existing component tests pass without weakened assertions or test exclusions, TypeScript/production build passes, and the real-backend Playwright workflow passes. `package-lock.json` records the complete resolved tree. Clean `npm ci` succeeds with existing host npm 10.9.2 and the container's npm. Initial npm 10 dependency-update attempts crashed inside Arborist before modifying project files; an isolated `npm@11.6.4` command generated the lock. Global npm was not changed and peer checks were not disabled.

## Executed scans and limits

- `artifacts/frontend-audit-before.json`: three affected packages, including two npm critical classifications.
- `artifacts/frontend-audit-after.json`: full npm audit, **zero findings**.
- `artifacts/frontend-audit-production.json`: `npm audit --omit=dev`, **zero findings**.
- `artifacts/backend-audit.json`: pinned `pip-audit==2.9.0`, installed Windows development/backend environment, **40 packages, zero findings, zero skipped packages**.
- `artifacts/backend-linux-audit.json`: actual Linux API environment, **28 packages, zero findings, zero skipped packages**.

No unresolved critical finding from the reported dependency set remains. Registry advisories are time-dependent; zero findings describes the executed scans, not a permanent security guarantee or an OS-image vulnerability assessment. Raw scan outputs remain ignored local artifacts. Local secrets are never placed in scan arguments or reports.

Trace: scoped REQ-05-003/004, REQ-06-008; ADR-08/09; DC-09; WI-01/03 and current Step 3 security grant. Baseline requirement classifications and D-01..16 are unchanged.
