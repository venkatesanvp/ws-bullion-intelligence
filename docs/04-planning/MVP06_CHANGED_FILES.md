# MVP-06 exact checkpoint file manifest

Base:4d3f943e8a293a1f9aed51ea9431b135bc308acb. Dedicated branch feature/mvp06-uat-ux-remediation.

60 files: 39 modified and 21 new. This manifest includes itself. No deletions or renames.

| Status | Exact repository-relative path |
|---|---|
| Modified | `backend/app/comparison.py` |
| Modified | `backend/app/forecast_research_service.py` |
| Modified | `backend/app/research.py` |
| Modified | `backend/app/schemas.py` |
| Modified | `backend/app/technical_analytics.py` |
| Modified | `backend/tests/test_engineering_isolation.py` |
| New | `backend/tests/test_mvp06_comparison.py` |
| Modified | `compose.engineering.yaml` |
| New | `docs/03-design/MVP06_UAT_REMEDIATION_DESIGN.md` |
| New | `docs/04-planning/MVP06_CHANGED_FILES.md` |
| New | `docs/04-planning/MVP06_UAT_REMEDIATION_CHECKPOINT.md` |
| New | `docs/06-user-guide/BULLION_INTELLIGENCE_USER_GUIDE.md` |
| New | `docs/06-user-guide/TRAINING_SLIDE_SPECIFICATION.md` |
| New | `docs/06-user-guide/images/synthetic-comparison.png` |
| New | `docs/06-user-guide/images/synthetic-evaluation.png` |
| New | `docs/06-user-guide/images/synthetic-forecast.png` |
| New | `docs/06-user-guide/images/synthetic-technical.png` |
| New | `docs/06-user-guide/workflows/application-navigation.drawio` |
| New | `docs/06-user-guide/workflows/etf-comparison.drawio` |
| New | `docs/06-user-guide/workflows/forecast-evaluation.drawio` |
| New | `docs/06-user-guide/workflows/forecast-generation.drawio` |
| Modified | `frontend/e2e/forecasting.spec.ts` |
| Modified | `frontend/e2e/market-session.spec.ts` |
| Modified | `frontend/e2e/market-stream.spec.ts` |
| Modified | `frontend/e2e/mvp.spec.ts` |
| New | `frontend/e2e/mvp06.spec.ts` |
| Modified | `frontend/e2e/production-smoke.mjs` |
| Modified | `frontend/e2e/provider.spec.ts` |
| Modified | `frontend/e2e/research.spec.ts` |
| Modified | `frontend/e2e/technical.spec.ts` |
| Modified | `frontend/e2e/workbench.spec.ts` |
| Modified | `frontend/e2e/workspace-ux.spec.ts` |
| Modified | `frontend/playwright.config.ts` |
| New | `frontend/public/user-guide.html` |
| New | `frontend/public/user-guide.md` |
| Modified | `frontend/src/App.tsx` |
| Modified | `frontend/src/ComparisonPanel.tsx` |
| Modified | `frontend/src/FinancialChart.tsx` |
| Modified | `frontend/src/ForecastingResearch.test.tsx` |
| Modified | `frontend/src/ForecastingResearch.tsx` |
| New | `frontend/src/IndicatorVisibility.tsx` |
| Modified | `frontend/src/IntradayDashboard.tsx` |
| Modified | `frontend/src/LightweightResearchChart.tsx` |
| Modified | `frontend/src/ResearchDashboard.tsx` |
| Modified | `frontend/src/ResearchShared.tsx` |
| Modified | `frontend/src/ResearchViews.test.tsx` |
| Modified | `frontend/src/TechnicalWorkbench.test.tsx` |
| Modified | `frontend/src/TechnicalWorkbench.tsx` |
| Modified | `frontend/src/api.ts` |
| Modified | `frontend/src/forecastTypes.ts` |
| New | `frontend/src/indicatorCatalog.ts` |
| New | `frontend/src/researchPreferences.tsx` |
| Modified | `frontend/src/styles.css` |
| Modified | `frontend/src/technicalTypes.ts` |
| New | `scripts/build_user_guide.py` |
| Modified | `scripts/engineering.py` |
| Modified | `scripts/verify_container_recovery.py` |
| Modified | `scripts/verify_local.py` |
| Modified | `scripts/verify_production_ui.py` |
| Modified | `scripts/verify_recovery.py` |

Only the four explicitly requested synthetic training PNGs are committed screenshot artifacts. No .env, actual credentials, owner account/portfolio data, raw market responses, price exports, backups, database dumps, generated dist or diagnostic artifacts are included. Published user-guide HTML/Markdown are intentional source-controlled help artifacts generated from the canonical guide.

## Synthetic screenshot SHA256

- `docs/06-user-guide/images/synthetic-comparison.png`: `4308c5cb87561ee270522fab5a340954daa48e47421ae580af637cb1317361a5`.
- `docs/06-user-guide/images/synthetic-evaluation.png`: `23a4888e1cf995faa4022eb17c795bc9a51cfa7e0cf6158797a48ef66d83a241`.
- `docs/06-user-guide/images/synthetic-forecast.png`: `0348361004498a43ca4725381da1bf5ff0aba840c3b5bf59098ac3e5b020e8b2`.
- `docs/06-user-guide/images/synthetic-technical.png`: `78ff2dc4294233799989160a0dbc66aca8b430059f21457ee758db4af8b25c46`.
