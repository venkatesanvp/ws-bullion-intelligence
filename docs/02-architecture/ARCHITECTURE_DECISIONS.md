# Architecture Decisions - Proposed ADR Register

**Version/date:** 0.1 - Proposed; 2026-11-01 (Asia/Calcutta).  
**Authority:** Human Step 2 architecture/design task; documentation only.  
**Baseline:** [REQ-BL-1.0](../01-requirements/REQUIREMENTS_BASELINE.md), annotated tag `requirements-v1.0`, commit `e10eef55fb21368e53dbe4599006b620cbb48566`. Tag and unchanged source content verified before authoring.  
**Status:** Architecture/design recommendations are Proposed. No baseline requirement status, maturity, priority, applicability or increment is changed. No implementation or spike is authorized.

## 1. Decision authority

All ten ADRs below are **Proposed**. None modifies D-01 through D-16 or promotes a requirement. Architecture approval alone does not approve Proposed/Open governing behavior or authorize code. Existing Python/FastAPI/PostgreSQL direction is an input constraint, not an undecided replacement.

A scoped human approval must identify ADR/DC IDs and applicable requirement behavior; record it before implementation. Exact library/runtime versions remain a compatibility/lockfile task under later implementation authorization.

| ADR | Recommendation | Status |
| --- | --- | --- |
| [ADR-01](#adr-01) | Modular monolith and execution boundaries | Proposed |
| [ADR-02](#adr-02) | React TypeScript UI and Vite | Proposed |
| [ADR-03](#adr-03) | PostgreSQL access and migrations | Proposed |
| [ADR-04](#adr-04) | Bounded CSV-first atomic imports | Proposed |
| [ADR-05](#adr-05) | Provenance and immutable observation identity | Proposed |
| [ADR-06](#adr-06) | Deterministic research indicators and numeric contracts | Proposed |
| [ADR-07](#adr-07) | Local Plotly chart rendering | Proposed |
| [ADR-08](#adr-08) | Layered automated verification | Proposed |
| [ADR-09](#adr-09) | Local Compose security and reproducible operations | Proposed |
| [ADR-10](#adr-10) | Research data-quality and comparison semantics | Proposed |

<a id="adr-01"></a>

## ADR-01 - Modular monolith and execution boundaries

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-05-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002), [REQ-03-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-001), [REQ-04-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-003), [REQ-05-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-013).
- **Context:** One personal application must keep evidence, calculations and future execution modes separate without premature operations overhead.
- **Recommended choice:** Recommend one FastAPI deployment with logical module interfaces and a browser client. Implement only CMP-01..06 in VS-01.
- **Alternatives / trade-offs:** Microservices improve independent deployment but add distributed consistency/operations; an unstructured single module is initially shorter but erodes financial isolation.
- **Operational complexity:** Low operational overhead; enforce dependency direction through tests. Runtime role separation does not imply separate domain services.
- **Extensibility / consequences:** Later strategy/risk/paper/manual/AI modules consume canonical evidence/results. No broker adapter, execution bus or future empty modules now.
- **Approval qualification:** Existing backend/DB constraints are retained; new decomposition and module contracts remain Proposed.

<a id="adr-02"></a>

## ADR-02 - React TypeScript UI and Vite

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013), [REQ-05-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-002).
- **Context:** Need explicit import/quality/chart states and automated frontend verification, with React/TypeScript a preferred candidate.
- **Recommended choice:** Recommend React + TypeScript + Vite, native fetch, small local state/hooks and no mandatory global-state framework.
- **Alternatives / trade-offs:** Streamlit reduces initial UI plumbing but offers a different interaction/test boundary. Next.js adds server rendering/server features not required for local research.
- **Operational complexity:** Moderate frontend toolchain cost; no separate frontend server-side business logic. Verify Node/tool compatibility when locking versions.
- **Extensibility / consequences:** Can add richer research/chat without moving calculations to the client; initial dashboard remains simple.
- **Approval qualification:** Frontend is not previously approved; human approval is required.

<a id="adr-03"></a>

## ADR-03 - PostgreSQL access and migrations

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001), [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008).
- **Context:** PostgreSQL persistence is accepted; mappings, uniqueness and reproducible schema upgrades need a design.
- **Recommended choice:** Recommend synchronous SQLAlchemy + psycopg, explicit transaction scopes and Alembic; bounded sync routes/work keep blocking DB/analytics off the event loop.
- **Alternatives / trade-offs:** Direct SQL is viable but adds mapping/migration maintenance; SQLModel couples typed API/DB models more tightly. SQLite does not verify PostgreSQL constraints and is not the canonical DB.
- **Operational complexity:** One connection pool/application process initially; migrations are a one-shot local operation before API readiness.
- **Extensibility / consequences:** Repositories hide DB details; pure analytics receive values only. Add workers/async DB only after measured need.
- **Approval qualification:** PostgreSQL itself is upstream accepted; ORM/driver/migration choices are Proposed.

<a id="adr-04"></a>

## ADR-04 - Bounded CSV-first atomic imports

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-02-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-007), [REQ-02-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-008), [REQ-02-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-009), [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-02-015](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-015).
- **Context:** No inspected user dataset or provider entitlement exists, but the first slice must ingest real historical data reproducibly.
- **Recommended choice:** Recommend canonical daily CSV, explicit mapping/identity/basis, bounded synchronous processing, all-or-nothing new-observation commit, duplicate skipping and conflict rejection.
- **Alternatives / trade-offs:** A network feed creates credentials/rights/reliability dependencies; a job queue handles larger jobs but adds state and infrastructure. Partial successful-row imports complicate user reconciliation.
- **Operational complexity:** One bounded database transaction persists terminal audit and any new prices; resolve uncertain outcomes by request-key lookup. No pending jobs, worker service or provider account.
- **Extensibility / consequences:** An adapter can later emit the same canonical row contract after independent rights/coverage approval.
- **Approval qualification:** No provider is qualified by this choice. Conflicting corrections require a future approved revision workflow.

<a id="adr-05"></a>

## ADR-05 - Provenance and immutable observation identity

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-02-011](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-011), [REQ-02-012](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-012), [REQ-05-010](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-010), [REQ-06-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-003).
- **Context:** Identical prices can have different sources/bases/vintages, and historical publication time may be unknown.
- **Recommended choice:** Recommend retaining mapped raw rows, source/batch references, date precision, nullable publication time, append-only accepted observations and per-instrument data revision.
- **Alternatives / trade-offs:** Overwriting latest values loses auditability. External time-series/event infrastructure is unnecessary for bounded daily histories.
- **Operational complexity:** Eight tables, canonical content hashes, row constraints and per-instrument serialization. A failed import never partially changes prices.
- **Extensibility / consequences:** Later corrections/replay need explicit versioned policy. Current ingestion time does not certify historical availability or point-in-time backtesting eligibility.
- **Approval qualification:** No silent source selection, cross-basis merge or correction/overwrite.

<a id="adr-06"></a>

## ADR-06 - Deterministic research indicators and numeric contracts

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-03-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-001), [REQ-03-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-007), [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006).
- **Context:** VS-01 requires useful research indicators but not strategy triggers.
- **Recommended choice:** Recommend SMA(n), SMA-seeded EMA(n) and Wilder RSI(n), explicit n, ordered daily closes and contract-defined warm-up/gaps. Store input decimals exactly; compute with Python Decimal precision 34 and ROUND_HALF_EVEN; serialize derived values to 12 fractional places with explicit rounding and version references.
- **Alternatives / trade-offs:** NumPy/pandas float vectorization may be faster but needs explicit rounding/NaN conventions; defer it until justified. TA-Lib adds native/convention dependencies; SciPy is unnecessary. LLM calculations are excluded.
- **Operational complexity:** Small pure O(N) engine; independent rational/Fraction references and higher-precision decimal checks. Compare specified serialized values exactly; no arbitrary financial error tolerance is assumed.
- **Extensibility / consequences:** Future strategy engines consume validated results and select approved rules separately. No default lookback, RSI threshold or buy/sell interpretation.
- **Approval qualification:** Formula/seeding/gap/basis, Decimal precision and output quantization conventions require explicit scoped approval; these are software conventions, not trading thresholds.

<a id="adr-07"></a>

## ADR-07 - Local Plotly chart rendering

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-04-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-001), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013), [REQ-03-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008).
- **Context:** Price/indicator overlays and source-aware comparison require interactive but modest visualizations.
- **Recommended choice:** Recommend locally bundled Plotly.js React integration, line charts first, lazy-loaded chart bundle and accessible tabular alternative.
- **Alternatives / trade-offs:** Recharts is lighter for simple charts; financial-specific libraries have different capabilities/licensing surfaces. A hosted chart service adds an unnecessary data egress dependency.
- **Operational complexity:** Bundle size is a trade-off; no CDN, hosted Plotly service or account is needed for the proposed design.
- **Extensibility / consequences:** Future overlays are possible after data/analytics approval; no order interaction or synthetic candles.
- **Approval qualification:** Chart library and display contracts remain Proposed; verify package licenses when locking dependencies.

<a id="adr-08"></a>

## ADR-08 - Layered automated verification

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-06-002](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-002), [REQ-06-006](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-006), [REQ-06-007](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-007), [REQ-06-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-06-008).
- **Context:** Need financially meaningful backend checks and observable frontend workflows, not implementation-mirroring snapshots.
- **Recommended choice:** Recommend pytest with real PostgreSQL integration, Vitest/React Testing Library for UI behavior, and a small Playwright Chromium end-to-end suite.
- **Alternatives / trade-offs:** Jest/Cypress are viable alternatives; two unit runners are unnecessary. Mock-only/SQLite-only DB tests miss actual constraints/concurrency.
- **Operational complexity:** Tests require isolated databases and a browser download later, only after installation authorization. Unit tests accompany work items; not deferred to the last task.
- **Extensibility / consequences:** Add additional browsers/performance suites only for observed need; no CI/cloud service required now.
- **Approval qualification:** No tests have been executed against a nonexistent application; tooling and acceptance suite are Proposed.

<a id="adr-09"></a>

## ADR-09 - Local Compose security and reproducible operations

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-05-001](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-001), [REQ-05-003](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-003), [REQ-05-004](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-004), [REQ-05-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-008), [REQ-05-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-05-009).
- **Context:** Personal-use startup must be reproducible and protected from accidental LAN/browser access.
- **Recommended choice:** Recommend loopback-bound UI/API, private-network PostgreSQL persistent volume, one-shot migrations, local bearer token, exact origins/hosts, health/readiness, manual backup/restore and lockfiles.
- **Alternatives / trade-offs:** Native-only setup may drift; cloud/Kubernetes/OAuth infrastructure is unjustified for one local owner. CORS alone does not authenticate requests.
- **Operational complexity:** Document token entry in UI memory, dependency/image locking and restore procedure; no public hosting or enterprise SLA assumed.
- **Extensibility / consequences:** Future deployment requires a new access/threat review; this does not approve cloud or account integration.
- **Approval qualification:** No Compose/Dockerfile/env/application artifacts are created during this task. Access/retention/recovery policy needs approval.

<a id="adr-10"></a>

## ADR-10 - Research data-quality and comparison semantics

- **Approval status:** Proposed; no human adoption recorded.
- **Requirement drivers:** [REQ-02-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-02-013), [REQ-03-008](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-008), [REQ-03-009](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-03-009), [REQ-04-013](../01-requirements/STAGE_1_REQUIREMENTS_BACKLOG.md#req-04-013).
- **Context:** Missing sessions, corporate actions and asynchronous endpoints can make apparently precise charts misleading.
- **Recommended choice:** Recommend no filling; flag unknown calendars/publication, break known discontinuities for indicators, require explicit known basis for derived metrics, and compare same-currency/basis series on common dates only.
- **Alternatives / trade-offs:** Calendar inference, automatic adjustment, mixed-vendor joining or total-return claims without evidence hide assumptions.
- **Operational complexity:** Source quality/calendar policy is versioned input; freshness remains UNASSESSED without an approved expected-session policy, not a made-up number of days.
- **Extensibility / consequences:** A later approved calendar/adjustment feed can strengthen quality without redefining original observations.
- **Approval qualification:** Approve DC-04/05/06 policies; no default financial freshness/expiry/risk/return threshold.

## 2. Primary-source technology evidence

Consulted 2026-11-01. These support feasibility, not integrated-system validation or version approval. Recommendations above are architectural judgments.

| Evidence | Supporting primary documentation |
| --- | --- |
| FastAPI multipart file/form handling and HTTP test support | [Forms/files](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/), [testing](https://fastapi.tiangolo.com/tutorial/testing/). |
| React supports typed components; Vite provides a React/TypeScript project option | [React TypeScript](https://react.dev/learn/typescript), [Vite guide](https://vite.dev/guide/). |
| PostgreSQL exact numeric storage, uniqueness and row-locking support the proposed integrity model | [Numeric types](https://www.postgresql.org/docs/current/datatype-numeric.html), [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [locking](https://www.postgresql.org/docs/current/explicit-locking.html). |
| SQLAlchemy transaction scoping and Alembic migrations | [Transactions](https://docs.sqlalchemy.org/en/21/orm/session_transaction.html), [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html). |
| Plotly offers React integration; plotly.js has an MIT license | [React integration](https://plotly.com/javascript/react/), [project license](https://github.com/plotly/plotly.js/blob/main/LICENSE). |
| Frontend behavior and browser testing candidates | [Vitest](https://vitest.dev/guide/), [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/), [Playwright guidance](https://playwright.dev/docs/best-practices). |
| Compose can gate startup on dependency health; published ports need intentional binding | [Startup order](https://docs.docker.com/compose/how-tos/startup-order/), [port publishing](https://docs.docker.com/engine/network/port-publishing/). |
| Origin policy is separate from local access authentication | [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/). |

No current release number is treated as a pinned application dependency. Compatibility, licenses, security updates and platform support must be checked for the actual lock set before installation.

## 3. Provider feasibility - verified documentation versus assumptions

| Candidate | Verified documentary fact | Still unverified / VS-01 treatment |
| --- | --- | --- |
| User's Dhan historical exports | D-14 records availability; [official historical API documentation](https://dhanhq.co/docs/v2/historical-data/) describes authenticated daily candle retrieval. | No export sample, ETF coverage, timestamp mapping, adjustment basis or usage rights inspected. No Dhan account/API connection in VS-01. A permitted externally obtained CSV is an input only after qualification. |
| NSE historical ETF reports | [Official historical-report index](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives) lists ETF price/volume archives. | This does not establish automation, retention/display rights, requested ETF/date coverage or reliable availability. Manual permitted download/CSV is a candidate, not an implemented scraper. |
| Yahoo fallback | D-14 names a possible US fallback; [Yahoo terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) restrict automated collection without prior permission. | Do not infer an approved/free API or Indian ETF coverage. No Yahoo adapter in VS-01; applicable permissions and series suitability would need evidence. |
| Explicitly permitted vendor/user canonical CSV | The proposed contract can accept qualified daily observations regardless of originating vendor. | No vendor selected. Owner must identify source/evidence and approve storage/analysis/display use. A valid schema is not proof of data truth or a license. |

No paid service, account, broker connection or dataset retrieval was attempted. No market sample was downloaded or verified. Reproducible first path: owner obtains permitted real ETF data -> records source/rights and mapping -> imports canonical CSV -> application validates and displays evidence. Synthetic test fixtures are clearly synthetic and never acceptance proof of real market coverage.

## 4. Human approval package

Approve/reject ADR-01..10 as a bundle or identify exceptions; approve the scoped DC-01..09 behaviors and affected requirement dispositions separately from global parent statuses. Resolve [SQ-01..07](../04-planning/VS-01_IMPLEMENTATION_BACKLOG.md#approval-package). Then provide explicit implementation authorization for the bounded work items. Do not interpret this document or a compatible preferred stack as approval.
