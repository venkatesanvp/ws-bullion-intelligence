# MVP05 engineering isolation - current execution boundary

**Do not execute owner lifecycle commands or rebuild the owner project during active UAT.** C:/ws-bullion/bullion-intelligence and bullion-vs01 are protected. The historical owner instructions below are for a future separately authorized deployment window.

Engineering worktree C:/ws-bullion/bullion-mvp05 is based on the reviewed functional checkpoint. Do not copy .env, caches, backups or Dhan credentials from owner. Install locked dependencies separately (`uv sync --frozen`; frontend `npm ci`). From the worktree:

```powershell
.venv/Scripts/python.exe scripts/engineering.py setup
.venv/Scripts/python.exe scripts/engineering.py build
.venv/Scripts/python.exe scripts/engineering.py start
.venv/Scripts/python.exe scripts/engineering.py test
.venv/Scripts/python.exe scripts/engineering.py recover
.venv/Scripts/python.exe scripts/verify_container_recovery.py
.venv/Scripts/python.exe scripts/verify_production_ui.py
.venv/Scripts/python.exe scripts/engineering.py stop
```

Setup creates only ignored artifacts/engineering.env with clearly synthetic fixed database/application settings and refuses to overwrite different settings. It requires a Git worktree .git file and absence of owner.env. Project bullion-mvp05 has independent network/volume, UI15173/API18000/testDB15433 and browser15174/18001/18002. No public bindings; no external/bind/shared volumes or host network. Network bridge allows host testing and is not an egress firewall. Dhan credentials are blank, capability flags false and fixtures use mocked providers. Validation refuses indirect bind driver options, wrong DB destination and live settings before state-changing actions. Never use the default compose project for these commands.

`test` runs complete backend/PostgreSQL/frontend/browser/build checks. `recover` uses only unique synthetic *_test databases on isolated test-db; binary backups are ignored synthetic evidence. `verify_production_ui` temporarily starts only the MockTransport fixture API18002, tests the built UI15173 under CSP/native/Plotly/forecast/evaluation, then terminates its own fixture process. `verify_container_recovery` restarts engineering services only, retains its synthetic SQL catalogue and verifies health/non-root/graceful shutdown/idempotent start. Direct API restart is not RAM cache recovery; populated handoff has separate authenticated failure-injection tests. No volume deletion or database reset is part of lifecycle operations.

UI container build ARG VITE_API_ROOT and runtime LOCAL_API_ORIGIN must identify the same loopback API (default127.0.0.1:8000; engineering18000). CSP permits only the selected loopback origin. Never put credentials in either frontend setting.

## Future authorized owner restart safeguards

Full offline handoff preflight occurs before replacement. An existing API restart/start requires an interactive terminal; noninteractive replacement is refused before changing containers. The original snapshot stays only in that process RAM. Restore compares all observation IDs/values/timestamps/provenance/classification/budget fields after normalizing ephemeral catalogue IDs. If a lifecycle/restore check fails, keep that terminal open; repair the local service separately, then type `retry` for an explicit local restore/verification attempt. No provider call/reacquisition is made. Only exact `DISCARD TRANSIENT CACHE` abandons the retained copy. Ctrl-C/EOF at the recovery prompt retains it. Killing the process, machine failure or an unmanaged stop can still lose RAM. No durable recovery guarantee is possible under the current no-persistence policy.

Before any future deployment: owner authorization/window, quiet research activity, explicit volume UID/permissions/locale review for the non-root PG18 candidate, full preflight, keep the RAM guard alive until exact restored-state verification, then owner retest. This package has not performed that deployment. Original REC-02 cache/provenance remains lost; fresh acquisition must never be relabeled restoration.

---

## Historical owner deployment instructions (functional d781e5b; not permission to run during UAT)

# Local Research MVP deployment and recovery

Windows workstation only. Local address: http://127.0.0.1:5173 ; API http://127.0.0.1:8000 . Docker publishes loopback ports only. No cloud/public deployment is added.

## Prerequisites and setup
Install/start Docker Desktop with Compose, Git, Python 3.13 and uv. From repository root run `uv sync --frozen` and `npm ci --prefix frontend` for development/verification. If .env is absent, explicitly run `python scripts/configure_local.py`; it must never overwrite an existing file. Keep database/application credentials locally. Optional Dhan credentials remain API-only. Missing optional credentials permit normal startup. Provider operations are controlled by existing separate default-disabled environment flags and owner permissions, never enabled by these scripts.

Run PowerShell commands from the repository root:

```powershell
.\scripts\local\bullion.ps1 setup
.\scripts\local\bullion.ps1 start
.\scripts\local\bullion.ps1 status
.\scripts\local\bullion.ps1 restart -Service ui
.\scripts\local\bullion.ps1 restart -Service api
.\scripts\local\bullion.ps1 restart -Service db
.\scripts\local\bullion.ps1 test
.\scripts\local\bullion.ps1 recover
.\scripts\local\bullion.ps1 stop
```

Equivalent: `.venv/Scripts/python.exe scripts/local/manage.py <action> [--service api|ui|db]`. Setup validates Docker/Compose, required configuration, loopback ports and directories without printing configuration. It does not create or replace credentials. Start builds locked sources/images, runs migrations and waits for readiness. Status prints service state/health only. Commands fail with sanitized errors and never run `down -v`, remove volumes or reset the database.

## Reproducibility and health
PostgreSQL, Python/uv and Node base images remain pinned by digest; uv.lock/package-lock.json remain authoritative. Frontend is a multi-stage production build: runtime contains dist and a small Node static server, runs as non-root with read-only root filesystem, dropped capabilities and no-new-privileges. No Vite development server or frontend credential injection is used. Frontend /_health, API authenticated readiness and PostgreSQL pg_isready are checked. Migration is a one-shot dependency, not a long-lived service.

## Transient data and restart
Canonical real market data stays in backend RAM. Normal stop or process crash loses this cache and forecast registries; PostgreSQL catalog/configuration survives in bullion_data. Start does not automatically download missing market data. Reopen with the local application token after browser reload; tokens are never stored in browser persistence.

For an orderly start/update or API restart while the existing API is healthy, the management process holds the existing authenticated canonical cache transfer in RAM, runs a complete offline restore preflight before replacement, then restores it only into the empty replacement process using the required local Origin and verifies row hashes. No raw provider response or cache snapshot is written to disk. Concurrent changed nonempty caches are not overwritten. This is a best-effort handoff and cannot protect against process/host failure during handoff; a preflight failure stops before replacement. An unforeseen failure after replacement can still lose transient data. Forecast tracking/performance registries are not transferred, and no first-seen/publication/finality evidence is reconstructed. Close research browser tabs before controlled deployment to avoid concurrent acquisition. If the API is unavailable, the command stops rather than silently discarding an unreadable active cache.

Test temporarily stops only the managed frontend to release its fixed browser-test port and restores it in finally. Backend/database remain running. Browser tests use synthetic providers and an isolated *_test database, not the active application database.

## Recovery
Reuse LOCAL_RECOVERY.md and scripts/verify_recovery.py. `recover` creates synthetic-only source/target databases in the disposable tmpfs test-db service; creates a restricted ignored backup, verifies SHA-256/archive integrity, restores to a fresh isolated database and compares table/schema/provenance/indicator/comparison hashes. It never restores over the application database. Existing backups and credentials are not removed. Stop the disposable test-db when finished.

Provider timeout/expired credentials: cached valid observations remain available, sanitized status is shown and existing backoff applies. No token exchange or fallback acquisition is added. Missing/stale optional data is explicit, without fabricated prices, signals or error scores. For stale/expired credentials, replace the token manually in .env per DHANHQ_LOCAL_CONFIGURATION.md and perform an orderly API restart; no credential values belong in logs or screenshots.

## Known limits
Retention/source permissions, point-in-time vintages and restart-safe durable forecast evidence remain open. An orderly RAM handoff is not a licensed persistent backup or source qualification. Do not export real prices with the synthetic recovery exercise. Owner cutover/UAT and unexpected workstation failure recovery remain owner acceptance work.

## Known deployment incident
The first MVP rollout lost the prior RAM cache because its restore request lacked Origin (403 ORIGIN_REQUIRED). The defect was corrected and populated round-trip/preflight tests added. Original cache/provenance was not recovered; the owner authorized a separately bounded fresh reload. See REC-02 in MVP_IMPLEMENTATION_CHECKPOINT.md. Do not describe this rollout as preserving the original cache. PostgreSQL data and credentials remained intact.

## Runtime hardening and security limitation
Global pip is removed from the API image; its supported `uv run --frozen --no-dev` workflow remains. The UI runtime has Node and built assets, with package managers retained only in its build stage. Development/npm commands run on the host/build stage. Image scans still report unresolved OS/toolchain findings, including PostgreSQL/gosu critical reports; see MVP_SECURITY_ASSESSMENT.md. Local operation and passing functional tests do not grant production release clearance.

The corrected populated real-cache preflight and final deployment preserved 992 daily/300 intraday rows with exact identities/first-seen timestamps and counter 8?8. These are the separately authorized fresh observations; the earlier cache was lost. Only synthetic data is included in disk backups/recovery evidence.
