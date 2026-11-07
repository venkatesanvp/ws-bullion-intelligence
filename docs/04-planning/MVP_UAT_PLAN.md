# Local Research MVP owner UAT

All cases are PENDING OWNER EXECUTION. Automated SIT is supporting evidence, not owner acceptance. Preconditions: local deployment healthy; credentials entered locally; source/retention limits understood; optional provider data available under existing authorization. Do not put tokens/account information or real price exports in UAT evidence.

| ID / requirement | Preconditions and owner steps | Expected | Actual | Evidence | Status | Defect |
|---|---|---|---|---|---|---|
| UAT-01 / MVP-02 daily | Open workspace; select TATAGOLD, TATSILV, GOLDBEES, SILVERBEES | Correct daily candles/context, source evidence; missing OHLC explicit | Not executed | Owner record pending | PENDING | ? |
| UAT-02 / MVP-02 intraday | Select permitted cached intraday interval and period | IST labels, completed/provisional distinction; daily not mixed | Not executed | Owner record pending | PENDING | ? |
| UAT-03 / MVP-02 chart controls | Toggle overlays/panes; zoom/pan/crosshair; theme/resize | Usable scales/navigation, exact values, no stale instrument | Not executed | Owner record pending | PENDING | ? |
| UAT-04 / MVP-02 fallback | Select Plotly; return to native | Existing values/quality retained, renderer selection works | Not executed | Owner record pending | PENDING | ? |
| UAT-05 / MVP-03 workflow | Forecast view; inspect history/technical, select B01/B02/lookback/horizon | Endpoints/origin/cutoff/status clear; no invented path | Not executed | Owner record pending | PENDING | ? |
| UAT-06 / MVP-03 B03 | Select B03 only | Volatility estimates, no directional price target or probability band | Not executed | Owner record pending | PENDING | ? |
| UAT-07 / MVP-03 historical | Strict first, then explicitly acknowledged conditional replay | Zero strict scores explained; conditional mode visibly labeled | Not executed | Owner record pending | PENDING | ? |
| UAT-08 / MVP-03 comparison | Review B01/B02 common origins, B03 metrics and errors | Distinct units and sample/overlap/qualification limitations understandable | Not executed | Owner record pending | PENDING | ? |
| UAT-09 / MVP-04 restart | Close research tabs; use documented restart/status/reconnect | DB retained; orderly RAM handoff verified; forecast registry loss understood | Not executed | Owner record pending | PENDING | ? |
| UAT-10 / MVP-04 unavailable data | Use mocked demonstration or existing sanitized failure; do not invalidate real credentials just for test | Missing/stale/expired data is clear; no false forecast reliability | Not executed | Owner record pending | PENDING | ? |

Owner records date, pass/fail, usability findings and defect references per case. MVP release remains unaccepted until required owner cases and governance gates are resolved or explicitly accepted with scope limitations.
