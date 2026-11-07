# Functional MVP checkpoint manifest (d781e5b)

Historical review from afa434cf2fe7e432f63b241f32e95bdcd2b3b621. The exact 52 files below were subsequently authorized, committed as d781e5b6098cf7b5d44ee43233160c58c5278f37 and pushed to the existing MVP feature branch. No release tag or main merge.

52 files: 33 modified, 19 new, zero removed.

| Status | File |
|---|---|
| Modified | `README.md` |
| Modified | `backend/Dockerfile` |
| Modified | `backend/app/forecast_market_adapter.py` |
| Modified | `backend/app/forecast_research_service.py` |
| Modified | `backend/app/market_cache_transfer.py` |
| Modified | `backend/app/market_data_service.py` |
| Modified | `backend/app/market_session_service.py` |
| Modified | `backend/app/provider_budget.py` |
| Modified | `backend/app/research.py` |
| Modified | `compose.yaml` |
| Modified | `frontend/.dockerignore` |
| Modified | `frontend/Dockerfile` |
| Modified | `frontend/e2e/forecasting.spec.ts` |
| Modified | `frontend/e2e/market-session.spec.ts` |
| Modified | `frontend/e2e/market-stream.spec.ts` |
| Modified | `frontend/e2e/provider.spec.ts` |
| Modified | `frontend/e2e/research.spec.ts` |
| Modified | `frontend/e2e/technical.spec.ts` |
| Modified | `frontend/src/ForecastingResearch.test.tsx` |
| Modified | `frontend/src/ForecastingResearch.tsx` |
| Modified | `frontend/src/IntradayDashboard.tsx` |
| Modified | `frontend/src/LightweightResearchChart.tsx` |
| Modified | `frontend/src/MarketSession.test.tsx` |
| Modified | `frontend/src/ResearchDashboard.tsx` |
| Modified | `frontend/src/ResearchViews.test.tsx` |
| Modified | `frontend/src/TechnicalWorkbench.test.tsx` |
| Modified | `frontend/src/TechnicalWorkbench.tsx` |
| Modified | `frontend/src/api.ts` |
| Modified | `frontend/src/forecastTypes.ts` |
| Modified | `frontend/src/styles.css` |
| Modified | `frontend/vite.config.ts` |
| Modified | `scripts/verify_local.py` |
| Modified | `scripts/verify_recovery.py` |
| New | `backend/tests/test_mvp_display_contracts.py` |
| New | `backend/tests/test_mvp_local_management.py` |
| New | `docs/03-design/MVP_LOCAL_RESEARCH_DESIGN.md` |
| New | `docs/04-planning/MVP_CHANGED_FILES.md` |
| New | `docs/04-planning/MVP_IMPLEMENTATION_CHECKPOINT.md` |
| New | `docs/04-planning/MVP_RELEASE_READINESS.md` |
| New | `docs/04-planning/MVP_SECURITY_ASSESSMENT.md` |
| New | `docs/04-planning/MVP_SIT_TEST_PLAN.md` |
| New | `docs/04-planning/MVP_UAT_PLAN.md` |
| New | `docs/05-operations/MVP_LOCAL_DEPLOYMENT.md` |
| New | `frontend/e2e/mvp.spec.ts` |
| New | `frontend/server.mjs` |
| New | `frontend/src/FinancialChart.tsx` |
| New | `frontend/src/LightweightResearchChart.test.tsx` |
| New | `frontend/src/chartAdapters.ts` |
| New | `frontend/src/financialChartData.test.ts` |
| New | `frontend/src/financialChartData.ts` |
| New | `scripts/local/bullion.ps1` |
| New | `scripts/local/manage.py` |

Excluded: .env, actual credentials, raw real market data/responses, price caches, backups, generated builds, logs, screenshots/traces and verification artifacts. Owner-authorized token replacement remains local and untracked. Requirements baseline, existing tags/history and PR #1 are preserved.

Authorized functional checkpoint: `feat(mvp): complete local forecasting and lightweight charting`. Security findings and source/retention/acceptance blockers remain explicit; a source checkpoint is not release approval.

## MVP05 engineering change manifest

41 MVP05 files relative to d781e5b: 32 modified, 9 new, zero removed. This is distinct from the 52-file functional checkpoint above. All are security, integrity, verification/isolation or documentation changes; no market dataset or generated artifact is included.

| Status | Path |
|---|---|
| Modified | `README.md` |
| Modified | `backend/Dockerfile` |
| New | `backend/Dockerfile.postgres` |
| Modified | `backend/app/main.py` |
| Modified | `backend/app/market_cache_transfer.py` |
| Modified | `backend/app/market_data_service.py` |
| Modified | `backend/app/market_session_service.py` |
| Modified | `backend/app/provider_budget.py` |
| New | `backend/tests/test_engineering_isolation.py` |
| New | `backend/tests/test_mvp05_integrity_audit.py` |
| Modified | `backend/tests/test_mvp_display_contracts.py` |
| Modified | `backend/tests/test_mvp_local_management.py` |
| New | `compose.engineering.yaml` |
| Modified | `compose.yaml` |
| Modified | `docs/04-planning/MVP_CHANGED_FILES.md` |
| Modified | `docs/04-planning/MVP_IMPLEMENTATION_CHECKPOINT.md` |
| Modified | `docs/04-planning/MVP_RELEASE_READINESS.md` |
| Modified | `docs/04-planning/MVP_SECURITY_ASSESSMENT.md` |
| Modified | `docs/04-planning/MVP_SIT_TEST_PLAN.md` |
| Modified | `docs/04-planning/MVP_UAT_PLAN.md` |
| Modified | `docs/05-operations/MVP_LOCAL_DEPLOYMENT.md` |
| Modified | `frontend/Dockerfile` |
| Modified | `frontend/e2e/forecasting.spec.ts` |
| Modified | `frontend/e2e/market-session.spec.ts` |
| Modified | `frontend/e2e/market-stream.spec.ts` |
| Modified | `frontend/e2e/mvp.spec.ts` |
| New | `frontend/e2e/production-smoke.mjs` |
| Modified | `frontend/e2e/provider.spec.ts` |
| Modified | `frontend/e2e/research.spec.ts` |
| Modified | `frontend/e2e/technical.spec.ts` |
| Modified | `frontend/e2e/workbench.spec.ts` |
| Modified | `frontend/e2e/workspace-ux.spec.ts` |
| Modified | `frontend/playwright.config.ts` |
| Modified | `frontend/server.mjs` |
| New | `scripts/engineering.py` |
| New | `scripts/inspect_gosu.py` |
| Modified | `scripts/local/manage.py` |
| New | `scripts/verify_container_recovery.py` |
| Modified | `scripts/verify_local.py` |
| New | `scripts/verify_production_ui.py` |
| Modified | `scripts/verify_recovery.py` |

Checkpoints: 87a8763 security;02d9028 recovery/audit; final verification/isolation/documentation commit after staged review. Both working trees are kept clean; only the authorized remote feature ref is advanced. Root owner worktree remains at its functional checkpoint during UAT. Exact final SHA/remote equality are reported after commit. Requirements baseline, decision register and existing tag object are unchanged. No .env, real prices, raw provider response, account data, credential, backup, build or verification artifact is staged.

Combined functional+MVP05 outgoing union: **65 unique files relative to origin/main**. The two manifests above overlap; their counts must not be added.
