# Local Research MVP SIT matrix

Evidence is synthetic unless explicitly marked metadata-only active deployment. Automated SIT does not imply owner UAT, source qualification or release acceptance.

| ID / requirement | Preconditions | Steps | Expected result | Actual / evidence | Status / defect |
|---|---|---|---|---|---|
| SIT-01 / MVP-02 default | Synthetic catalog, browser | Select each of four ETFs; daily/technical | Native candles, correct instrument and exact values | Native multi-ETF workflow; 11 browser scenarios passed | PASSED (automated) |
| SIT-02 / MVP-02 panes | Completed synthetic data | Toggle SMA/EMA/Donchian/RSI/MACD/ATR; pan/zoom/crosshair | Correct separate units/scales, shared time range | Native API and browser tests | PASSED (automated) |
| SIT-03 / MVP-02 lifecycle | Mounted chart | Refresh repeatedly, switch timeframe/instrument/theme, resize/unmount | No stale identity/subscriptions/instances; responsive | Lifecycle unit tests, stable canvas counts, measured timings | PASSED (automated) |
| SIT-04 / MVP-02 gaps/fallback | Missing/partial/malformed synthetic input | Exercise gaps, close-only, invalid times, renderer failure and Plotly selection | No invented OHLC/interpolation; explicit fallback | Display helper/native/fallback tests | PASSED (automated) |
| SIT-05 / MVP-03 forecasts | Canonical completed synthetic history | Select model/lookback/horizon; B01/B02/B03; inspect cached technical context | Exact deterministic results; endpoints only; B03 separate | Backend suite, forecasting browser | PASSED (automated) |
| SIT-06 / MVP-03 modes | Real-like synthetic metadata | Strict default; conditional without/with acknowledgement; synthetic | No silent downgrade; exclusions/nulls retained | Existing service/routes/UI tests | PASSED (automated) |
| SIT-07 / MVP-03 comparison | Common eligible origins | Evaluate/review common-origin cards, error charts and history selection | Matched B01/B02; B03 volatility metrics separate; warnings | Forecast/performance/replay regression | PASSED (automated) |
| SIT-08 / MVP-04 lifecycle | Isolated runtime and cache metadata guard | Setup/start/status, UI/API/DB restart, graceful stop/start | Healthy local services, DB volume retained; RAM handoff only | Isolated lifecycle + corrected real guarded handoff pass; original cache loss retained as REC-02 | PASSED (automated) |
| SIT-09 / MVP-04 provider failure | Mock provider only | Timeout, expired token, missing/stale data | Cached values retained, sanitized errors, no retry loop | Existing mocked provider/session tests | PASSED (automated) |
| SIT-10 / MVP-04 recovery | Disposable test-db, synthetic entities | Backup/hash/archive/isolated restore/query comparison | Identical data/schema/provenance; no active DB writes | recovery-verification.json | PASSED (automated) |
| SIT-11 / security | Built assets and containers | Dependency, credential, source/image and network review | No secrets/restricted data; loopback/API-only credentials | Audit/security reports | PARTIAL ? credentials/deps pass; image security blocked |
| SIT-12 / audit | Active API, no owner browsing | Compare counters, row hashes before/after; inspect causal logs | Attribute future events, retain historical uncertainty | Metadata-only guard | VERIFIED LIMITATION / AUD-01 remains open |

Performance evidence reports observed timings and resource counts, not invented service-level targets. Data-flow consistency is checked through the same canonical observations, exact adapters, deterministic models, API serialization and browser values; no additional Dhan request is authorized or needed by these tests.

## Executed evidence
915 backend/PostgreSQL, 62 frontend, 11 browser workflows, lint and build passed. Production built-asset smoke passed with synthetic API responses and zero CSP/runtime errors. Synthetic Compose lifecycle and binary backup/restore passed; populated HTTP handoff/Origin and preflight rejection are covered in regression. The real-source chart/technical/forecast consistency check used cached values only, made zero provider requests and preserved explicit source limitations.

REC-01: verifier normalized only the exact two equivalent provider-kind enum deparses; modified enums still fail. REC-02: first active handoff failed Origin authentication and lost original transient data; corrected and tested, owner-authorized fresh reacquisition completed within nine total attempts. This incident is not a passed original-data-preservation test. The synthetic safety scenarios pass, while original provenance recovery is unavailable. Owner UAT remains unexecuted; source qualification and historical audit attribution remain open.

Evidence files (ignored local artifacts): verification.json, backend-tests.xml, browser-tests.xml, mvp-production-smoke.json, mvp-container-recovery.json, recovery-verification.json, mvp-security.json, mvp-audit-summary.json, mvp-real-data-consistency.json, mvp-fresh-reload.json and mvp-fresh-reload-remaining.json. No raw real prices/responses or real-data screenshots/traces are included.


## MVP05 independently isolated verification

`python scripts/engineering.py setup/build/start/test/recover` in C:/ws-bullion/bullion-mvp05 (one action per command); `python scripts/verify_container_recovery.py`. The runner refuses owner.env/shared mounts/ports/volumes/networks, non-synthetic DB destination and enabled provider settings. It does not run default owner lifecycle commands.

MVP05-C/D/E cases map to test_mvp05_integrity_audit.py, test_mvp_local_management.py and test_engineering_isolation.py: complete provenance/identity/value handoff, missing Origin, malformed/partial/disconnected body, injected late coverage failure, duplicates, mismatched identity/epoch, invalid numeric/duration, unavailable provider, one-shot replay/concurrent target safety, RAM guard/noninteractive refusal, complete budget fingerprint, request correlation/manual refresh/failure/no retry, snapshot-only forecast/evaluation, startup/cached reads, and shared/indirect runtime-state refusal.

Final backend 959 passed, frontend 62 passed, Chromium 11 passed, zero failures/skips. Full result and prior failed setup/harness attempts are explicitly recorded in MVP_IMPLEMENTATION_CHECKPOINT. Production-image smoke uses the temporary synthetic fixture backend; it is not owner UAT or evidence of real-data qualification. Critical/high image disposition is a separate gate in MVP_SECURITY_ASSESSMENT.
