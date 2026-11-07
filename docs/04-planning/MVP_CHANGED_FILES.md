# MVP exact proposed checkpoint files

Branch: feature/local-mvp-charting-forecasting-deployment. HEAD: afa434cf2fe7e432f63b241f32e95bdcd2b3b621. No files staged, committed, tagged or pushed.

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

Proposed checkpoint after separate approval: `feat(mvp): complete local research charting forecasting and deployment`. New PR plan: this dedicated branch into main from the merged PR #1 baseline. No commit/push/tag performed. Image security findings remain explicit blockers; a source checkpoint is not release approval.
