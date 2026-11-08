# MVP-06 calculation and interaction design

Status: implementation within owner-authorized UAT remediation; requirements and decision baseline unchanged. This note records implementation conventions, not new data rights or acceptance.

## Traceability and boundaries

UAT-001/002: ResearchDashboard retains an accessible market-context landmark and navigation while invalid inputs get an explicit empty state. ChartBoundary isolates snapshot, reconciliation and selected research view failures. Workspace-scoped React context retains UI choices only (view, periods, dates and chart visibility) until lock/reload; it stores no token, price, portfolio or durable data. A changed ETF/source/view still replaces the calculating child to cancel obsolete work.

UAT-003/004: indicatorCatalog.ts is the capability definition. Daily and Technical reuse the existing completed-bar technical endpoint and FinancialChart. Intraday requests the existing technical extension as well as legacy close-indicator bundles. Defaults change EMA 37 to 20 as expressly requested; formulas remain unchanged. All six entries stay discoverable. Existing warm-up, gap, OHLC and numeric safeguards continue. The existing legacy chart/indicator routes remain supported and tested.

UAT-005: comparison method common-date-price-v2 extends the existing deterministic Decimal implementation. API schema defaults to STRICT_COMPATIBILITY; PROVISIONAL_AS_DELIVERED needs acknowledge_source_limitations=true, the same DhanHQ source and provider-adjusted basis. Source permitted uses and qualification remain unchanged. Explicit opt-in does not override known breaks, incompatible currency/basis/data class or conflicting adjustment definitions. It is an as-delivered descriptive comparison, not qualification of adjustment semantics.

UAT-006: existing model and forecast contracts remain unchanged. Generate Forecast invokes /research/forecasts/run; context and saved-run lookup are separate so optional records cannot stall the primary flow. In-flight context reads are shared during StrictMode effect replay; deferred unmount cancellation preserves a live subscriber, explicit Cancel and the45-second network timeout remain effective, and final unmount aborts the physical request. Backend computation/rate guards are unchanged. Context failures remain visible through edits until explicit reload. Editing settings during initial context loading does not cancel that context; editing a completed selection invalidates old results and outstanding execution. Returned ETF/source/horizon/lookback/model set are checked. Historical evaluation remains /research/forecasts/evaluate with existing strict/replay/synthetic governance. No automatic run, new model, provider operation, confidence band or intermediate path is added.

## Comparison arithmetic

Use common observed dates in the requested inclusive interval. No forward filling or inferred price. For each positive finite close series p, rebase(t)=100*p(t)/p(first common date). Endpoint price-only change=100*(p(last)/p(first)-1). Every ETF uses the same endpoints and date intersection.

For volatility, an interval between adjacent common observations is included only when those dates are consecutive in every input's reviewed calendar. This conservative matched subset prevents a multi-session or unreviewed return being labeled daily. With at least two included simple returns r=p(t)/p(t-1)-1, volatility=100*sqrt(sum((r-mean(r))^2)/(N-1)); no annualization. Missing reviewed calendars leave volatility unavailable while normalized observed closes may still be plotted. The response reports matched returns and excluded intervals. Sample standard deviation convention agrees with the [NIST definition](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm); sufficiency does not imply statistical significance.

Maximum observed drawdown=max over common dates of 100*(running peak-close)/running peak. It is nonnegative, based on observed closing prices only and may understate intra-window or intraday drawdown. Requested-date known discontinuities block the comparison even in provisional mode. Point-in-time/finality, source staleness and total-return limitations remain in source evidence; this method does not establish them.

Context: precision 34, HALF_EVEN Decimal; wire serialization 12 places. Existing positive finite bounded price validation remains. Reference tests use independent 60-digit Decimal calculations, sparse calendars, incompatible refs, known breaks, flat/rising/falling prices, near-zero values and changed global context. No binary floating-point analytics is introduced. Frontend chart conversion remains display only.

Synthetic example: 100/120/90 and 200/240/180 on three reviewed consecutive sessions yield identical 100/120/90 normalized values, -10% endpoint change, 25% observed drawdown and 31.819805153395% sample session volatility. This is arithmetic evidence, never a real-market result.

## Forecast display changes

Additive response display_change uses the existing forecast Decimal context and derived serialization: absolute=predicted_price-last_observed_close; percentage=100*(predicted_price/last_observed_close-1). A positive origin is required. B03 has null changes and no directional price endpoint. This presentation calculation does not modify B01/B02/B03 formulas, forecast prices or performance scoring.

## Qualification and retained restrictions

Real-data historical evaluation defaults to STRICT_POINT_IN_TIME. Conditional replay requires explicit acknowledgement and does not establish historical publication/finality knowledge. B01/B02 comparisons retain common eligible origins; B03 evaluation remains volatility-specific. Sample/overlap/disjoint evidence labels remain; no model-superiority or calibrated-probability assertion is made.

No new storage, provider integration, credential flow or trading route is introduced. Existing bounded retrieval remains governed by existing authorization and policy. All MVP-06 tests/screenshots use synthetic fixtures and independent engineering ports/project. Protected owner caches and database were not queried or copied. MVP-05 security dispositions remain unchanged; no clearance is inferred.
