# VS-01 container reproducibility review

Authority: current human Step 3 verification/remediation; REQ-05-001/003/008/009 -> ADR-09 -> DC-09 -> WI-01 and VS01-T-21/23. No new deployment service or external account was introduced.

## Immutable inputs and provenance

| Role | Reviewed registry reference and immutable index digest | Observed Linux runtime |
| --- | --- | --- |
| Python backend/migration | `docker.io/library/python:3.13-slim@sha256:2d44738ebf4ce5f63b9d9ea871e9c7cfdc0426f7b0c97cac915fd88ded1d86bb` | Python 3.13.18 |
| UI Node runtime | `docker.io/library/node:22-bookworm-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da` | Node 22.23.4 |
| Both database services | `docker.io/library/postgres:18@sha256:3a4264520e121176619f54ff867d12774bc81e95e7b84db58d63bccdb6144b81` | PostgreSQL 18.6 |
| Backend package-tool binaries | `ghcr.io/astral-sh/uv:0.11.29@sha256:eb2843a1e56fd9e30c7276ce1a52cba86e64c7b385f5e3279a0e08e02dd058fc` | uv 0.11.29 |

Digests were obtained from the registries with Docker image/imagetools inspection. Python and Node OCI manifests identify the docker-library/python and nodejs/docker-node source repositories; uv's OCI source is astral-sh/uv, revision `901092ee11a89ba287f274e3c6e3a2e18ec2fba2`. PostgreSQL resolves through Docker's official library namespace. This verifies registry identity/content references and inspected provenance metadata, not an independently verified maintainer signature or a full software-supply-chain audit.

Dockerfiles pin the Python/Node index digests; Compose pins the same PostgreSQL digest for application/test services. uv binaries are copied from its immutable image instead of an un-hashed bootstrap pip install. Human-readable tags are annotations beside the digests and do not determine content. Linux/amd64 was tested; multiarchitecture index references do not imply every architecture was verified.

`uv sync --frozen --no-dev` and `npm ci` consume the checked-in dependency locks, including package integrity hashes. The Playwright package lock records 1.64.1 and its matching browser revision. Host Node 22.16.0 and container Node 22.23.4 share the supported Node 22 line; Python is constrained to 3.13 and the container fixes its exact patch. Host/container tools need not have identical patch releases to satisfy these declared constraints; both installation paths were executed.

## Executed startup and configuration checks

Two successive `docker compose --progress plain up --build -d --wait` runs succeeded with these pins. Database health gated the one-shot migration; it exited successfully, then API readiness and the UI succeeded. Repeating the build/start reused locked inputs without deleting the named application volume. `artifacts/compose-repeat-startup.log` and `artifacts/runtime-verification.json` retain the observed results, runtime versions and SHA-256 fingerprints of Dockerfiles/Compose/dependency locks.

HTTP checks: UI 200, public API liveness 200, readiness without a token 401 and authenticated readiness 200. The resolved service structure was checked without printing environment values. Only UI 5173 and API 8000 publish to 127.0.0.1; the normal database has no host port. The explicit disposable test database alone publishes 55433 to loopback while its test profile is used.

Secrets remain in ignored `.env`, are injected at runtime, are excluded from both build contexts and are not build arguments or VITE variables. The built frontend was checked against the actual local password/token values without displaying them; neither was present. API authentication/origin/host tests and browser memory-only token tests passed. `.env.example` contains placeholders only. Never print resolved `docker compose config` with secret interpolation or inspect full container environments in shared logs.

The local UI intentionally uses Vite's development runtime, with development dependencies installed inside its container and internal container binding to all interfaces. Host publication remains loopback-only. This is the existing approved local workbench, not public production hosting.

## Reproduce and maintain

```powershell
docker compose up --build -d --wait
```

Use the same source revision, lockfiles and digest references. Do not delete application volumes. A reviewed dependency/image update must deliberately change the relevant lock/digest, rerun scans and applicable tests, then retain the resulting evidence. Digest pinning fixes content; it does not provide automatic security updates.

The verification establishes reproducible dependency selection and startup on the tested platform. It does not assert byte-for-byte identical built-image manifests (build metadata may differ), registry availability forever, another workstation/architecture's readiness, OS-package vulnerability clearance or disaster recovery of actual owner data.


## Step 4 re-verification - 2026-11-02

Compose, Dockerfiles, Python lock and immutable image references are unchanged from checkpoint `5f0399b`. The frontend lock now includes locally bundled Plotly and its development type declarations. Rebuilt startup and a subsequent `docker compose up -d --wait` passed with the existing application volume preserved. API/database are healthy, migration exited 0, and the UI responds HTTP 200 (UI has no Docker HEALTHCHECK). An initial reporting probe assumed every service had a healthcheck; the corrected probe uses the actual service controls and HTTP readiness, with original result retained in ignored evidence.

`artifacts/step4-runtime-verification.json` records current source-input SHA-256 hashes, UI/live/ready authorization checks, loopback-only ports, unpublished application DB, and absence of the actual local token/password from runtime logs and the production frontend. Synthetic Decimal reference vectors passed inside the rebuilt Linux API; its 28-package dependency audit has zero findings/skips. The disposable test DB was stopped after verification; application DB/API/UI remain running. Extended isolated recovery verifies the new research outputs without restoring over active data. Original provenance/platform/build reproducibility limitations above still apply.
