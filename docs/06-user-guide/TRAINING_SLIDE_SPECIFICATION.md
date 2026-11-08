# MVP-06 training slide specification

Delivery format: complete editable Markdown specification. PowerPoint-generation tooling (Spaces / artifact runtime) is unavailable in this session. No PPTX is claimed. Use a 16:9 deck, off-white background, dark navy headings, teal accents, 30pt titles and 20pt body. Place a persistent footer: Engineering candidate - not released - screenshots SYNTHETIC TEST ONLY. These are research workflows, never trading recommendations. Alt text and notes are part of each slide.

## Slide 1 - Research with evidence

Layout: title left, four ETF symbols right, no market chart.

On-slide text: Bullion Intelligence / Private local research / TATAGOLD, TATSILV, GOLDBEES, SILVERBEES / Identify the source, time and limitations before interpreting a result.

Speaker notes: MVP-06 addresses seven owner UAT findings. It has not replaced the running owner workspace. It adds no trading, model family or market-data storage permission. Owner acceptance and security gates remain open.

## Slide 2 - Start and navigate safely

Layout: use workflows/application-navigation.drawio as editable diagram; six steps vertical across two columns.

On-slide text: Unlock locally / Select ETF, source, basis / Research Dashboard / History and Quality / ETF Comparison / Return with settings retained.

Speaker notes: Tokens belong in local configuration/login only, never screenshots. The browser holds preferences in memory. Reload locks it. Coordinate a guarded handoff before restarting the owner services, because transient price caches can be lost. The isolated engineering UI is not an owner deployment.

Alt text: Local navigation from unlock to research, quality review and comparison.

## Slide 3 - The dashboard stays understandable

Layout: screenshot images/synthetic-technical.png on right, three callouts left. Crop only in the assembled deck, preserving synthetic banner and ETF title.

On-slide text: Market Snapshot remains accessible / Optional quotes are collapsed in Technical and Forecasting / Empty and error states explain what to do / New ETF selection refreshes data.

Speaker notes: The screenshot is a real browser capture of the isolated synthetic fixture. Its generated prices are not Dhan observations. Expand the optional quote section only when needed; closed sections do not poll. Error boundaries protect adjacent dashboard sections.

Alt text: Synthetic Technical analytics page with persistent research navigation.

## Slide 4 - Six indicators, one catalogue

Layout: six-row text table: indicator, default, prerequisite.

On-slide text: SMA 20: 20 closes / EMA 20: 20 closes / Wilder RSI 14: 15 closes / MACD 12,26,9: 34 for complete signal / ATR 14: 15 OHLC bars / Donchian 20: 21 OHLC bars; prior window excludes current bar.

Speaker notes: These defaults are conventional, not optimized. Existing formulas are unchanged. Flat RSI and missing OHLC can remain unavailable. Gaps restart warm-up. Disabled catalogue entries explain minimum samples rather than disappearing. Checkboxes affect charts; exact tables retain evidence.

## Slide 5 - Edit, apply and recover

Layout: three numbered action blocks with one warning callout.

On-slide text: Edit valid periods / Apply to recalculate / Reset to Defaults then Apply / Draft changes do not relabel old results / Tables begin with 15 rows.

Speaker notes: Periods are positive integers; RSI at least 2; MACD fast less than slow; required warm-up must fit the contract. Invalid values show validation. Settings and visibility survive normal navigation and ETF changes, but not browser reload or lock. Recoverable API failures show a message and can be retried without losing navigation.

## Slide 6 - Compare fair intervals

Layout: workflows/etf-comparison.drawio and one formula card.

On-slide text: Select Gold / Silver or another compatible pair / Inspect cached common period / Compare shared observed dates / Index = 100 x close / starting close / No forward fill.

Speaker notes: Use available common period reads cached dates; it does not acquire missing history. Compare remains subject to the pre-existing provider policy. Strict adjustment compatibility is default. Provisional Dhan as-delivered comparison requires explicit acknowledgement and cannot override a known break, incompatible basis or source restrictions.

Alt text: Comparison workflow from compatible listings through qualification to common-date metrics.

## Slide 7 - Read comparison metrics

Layout: images/synthetic-comparison.png, synthetic arithmetic example box below.

On-slide text: Same endpoints / Same return intervals / Sample one-session volatility, no annualization / Maximum observed close drawdown / Expand Diagnostic codes for evidence.

Speaker notes: Synthetic sequences 100,120,90 and 200,240,180 both rebase to 100,120,90: endpoint -10%, drawdown 25%, sample volatility 31.819805153395%. Only consecutive sessions in both reviewed calendars qualify for volatility. Missing observations can hide drawdowns. Price-only changes exclude distributions, fees and taxes; they are not predictions or total return.

Alt text: Synthetic two-ETF comparison with common-date metrics and provisional qualification warning.

## Slide 8 - Generate a baseline in five steps

Layout: workflows/forecast-generation.drawio beside images/synthetic-forecast.png, preserve synthetic banner.

On-slide text: 1 ETF / 2 Horizon / 3 Model / 4 Generate Forecast / 5 Review origin, target and change / Historical evaluation is optional step 6.

Speaker notes: Horizons come from the existing contract. A changed ETF/horizon/lookback/model clears obsolete results. Generate issues a fresh request; it does not silently ignore selections. Missing history or unsupported choices receive an explanation. Optional saved-run lookup does not block valid primary context.

Alt text: Synthetic Basic Forecasting with explicit model, horizon and Generate action.

## Slide 9 - Know the three baselines

Layout: three parallel cards.

On-slide text: B01 Last-close baseline: repeats last eligible close / B02 Historical drift baseline: extends existing drift estimate / B03 Historical volatility estimate: no directional price endpoint.

Speaker notes: Show origin close/date, target session, horizon, endpoint, absolute and percentage changes for B01/B02. B03 uses return-fraction volatility. The chart marks discrete endpoints without invented intermediate paths or confidence bands. A research estimate does not prove predictive reliability or create a buy/sell signal.

## Slide 10 - Evaluate without overstating evidence

Layout: workflows/forecast-evaluation.drawio beside images/synthetic-evaluation.png.

On-slide text: Open Advanced Research / Strict point-in-time is real-data default / Conditional replay needs explicit acknowledgement / Synthetic means test evidence / B01/B02 share eligible origins / B03 evaluated separately.

Speaker notes: Inspect MAE, RMSE, bias, period, horizon, origin count and disjoint-window evidence together. Overlap reduces independent evidence. Zero eligible scores is not zero forecast error. Fixed-vintage replay cannot establish strict historical knowledge. No significance or superiority claim follows from small samples. Result tables use 15-row paging.

Alt text: Synthetic historical evaluation scorecards and sample-size limitations.

## Slide 11 - Diagnose common problems

Layout: issue/action table.

On-slide text: No history -> check dates/source/eligibility / Indicator unavailable -> check minimums, OHLC and gaps / Comparison blocked -> read explanation and basis / Generate disabled -> select model and wait for context / Old result clears -> generate for new selection / Snapshot hidden -> expand optional summary.

Speaker notes: Do not fabricate prices or switch evaluation mode to conceal missing evidence. Avoid posting raw responses, credentials or holdings with a defect. Report build, ETF, dates, tab, steps and sanitized message. Coordinate restarts with recovery controls.

## Slide 12 - Owner retest and remaining gates

Layout: seven-item checklist plus separate limitations box.

On-slide text: Retest UAT-001 through UAT-007 using the user guide / Record build identity and pass/fail / Engineering checks do not replace owner acceptance / No automatic deployment or release.

Speaker notes: Full exact steps are in BULLION_INTELLIGENCE_USER_GUIDE.md. Open security findings, source/retention rights, finality/adjustment/revision evidence, strict point-in-time qualification and statistical validation remain separate gates. The running owner environment is unchanged. Recommended next activity is a controlled handoff and owner retest after applicable gates, not another model package.

## Assembly and verification instructions

Use the four committed screenshots exactly as generated by frontend/e2e/mvp06.spec.ts, never as real-market evidence. Use the four editable XML diagrams, not raster screenshots of diagrams. The slide text, layouts, notes, labels and alt text above constitute the full fallback artifact. Before exporting a future PPTX, render every slide, verify readable labels and synthetic qualification, confirm screenshot hashes in the checkpoint manifest and open/edit the deck in presentation software. No deck render or PPTX verification is claimed here.
