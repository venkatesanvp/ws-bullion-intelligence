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


## Step 4 dependency and exposure re-verification - 2026-11-02

Added exact production dependency `plotly.js-basic-dist-min@4.2.0` and development-only type dependency `@types/plotly.js@3.0.15`; both package licenses are MIT. The Plotly MIT notice is preserved in `frontend/public/licenses/plotly.js-LICENSE.txt`. The lock contains registry integrity hashes. The selected basic distribution provides locally bundled Cartesian charts; no CDN script or external market-data request is used. Rendering uses `Plotly.react`/`purge`; see [official function reference](https://plotly.com/javascript/plotlyjs-function-reference/), [distribution descriptions](https://github.com/plotly/plotly.js/blob/main/dist/README.md) and [MIT license](https://github.com/plotly/plotly.js/blob/main/LICENSE). User-controlled plot labels are escaped and numeric hover values are exact validated server strings.

Final full and production-only npm audits: **zero findings** (`artifacts/step4-frontend-audit-full.json`, `step4-frontend-audit-production.json`). Final pinned pip-audit Windows: **40 packages, zero findings/skips** (`step4-backend-audit.json`); actual rebuilt Linux API: **28 packages, zero findings/skips** (`step4-backend-linux-audit.json`). Original Step 3 findings remain remediated; no advisory was suppressed, ignored or downgraded. No forced upgrades or financial-library dependency was introduced. Isolated npm 11.6.4 generated the lock; ordinary frozen container install and host build/tests succeeded.

Cumulative 114 backend, 16 component and three Chromium tests pass, including the original access/ingestion workflow and new local-only request/memory-token checks. Actual local secrets are absent from the production frontend and runtime logs. Lazy chart chunk is about 1.22 MB/407 kB gzip; the build warning is retained as a measured ADR-07 tradeoff. Application dependency scans do not establish OS-image vulnerability clearance or permanent safety.


## Step 5A diagnostic transport review - 2026-11-02

Owner-authorized mocked diagnostic only; live provider access is withheld. HTTPX **0.28.1** moves from development-only to an exact production dependency, retaining all lock versions and artifact hashes. Production Linux package count rises from 28 to 31 (HTTPX, httpcore and h11 become runtime-reachable); Windows development environment remains 40 packages. No Dhan SDK or authentication/trading dependency is added. Frozen Compose install/startup and the isolated Linux mocked diagnostic pass.

Executed `pip-audit==2.9.0`: Windows **40 packages, zero vulnerabilities/skips** (`artifacts/step5a-audit-windows-python.json`); rebuilt Linux **31 packages, zero vulnerabilities/skips** (`step5a-audit-linux-python.json`). Full npm and `--omit=dev` scans both report **zero findings** (`step5a-audit-frontend-full.json`, `step5a-audit-frontend-production.json`). No unresolved critical finding in these application dependency scans; no suppression, advisory exclusion or forced upgrade. These scans do not assess OS-image vulnerabilities or future advisories.

The standalone diagnostic restricts live transport to one fixed TLS-verified HTTPS GET profile, no redirects/retries/environment proxy overrides; token appears only in its header. Default CLI does not construct a transport. App keys are not exchanged. Raw bodies, errors and account identifiers cannot enter its allowlisted report; temporary suppression of library logging is restored afterward. Response cap, explicit timeouts and format checks are documented in the [operating instructions](../05-operations/DHANHQ_READ_ONLY_DIAGNOSTIC.md). The streamed-body elapsed check is not a hard total deadline. The CLI is not exposed as a web route or startup/background task.

The 81 new tests use synthetic credentials, mocked HTTP and socket/DNS guards, including exception/header/message redaction and failure outcomes. Six Linux scenarios run with `--network none`. Existing PostgreSQL/UI/browser regressions pass (242/16/3 total). `.env` remains ignored/untracked, unchanged and disabled; provider values remain API-only, absent from the inspected generated assets, runtime logs and local API responses. No database credential model, profile persistence, market-data response, portfolio/trading mutation or order endpoint is introduced. Account access, actual entitlement and source-use/retention permission remain unverified.
