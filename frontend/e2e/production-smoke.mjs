import {chromium} from 'playwright-core';
import {writeFileSync} from 'node:fs';
const token='synthetic-test-token-not-a-real-secret-000000',host='http://127.0.0.1:18002/api/v1';
const session=(await(await fetch(host+'/transient-session',{headers:{Authorization:'Bearer '+token}})).json()).data;
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],csp=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'&&/content security|violates|csp/i.test(m.text()))csp.push(m.text());});
 await page.route('http://127.0.0.1:18000/api/v1/**',async route=>{if(route.request().url().endsWith('/stream-events')){await route.abort();return;}const response=await route.fetch({url:route.request().url().replace(':18000/',':18002/')});await route.fulfill({response});});
 await page.goto('http://127.0.0.1:15173');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(session.instruments[0].instrument_id);await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');await page.getByRole('button',{name:'Research dashboard',exact:true}).click();await page.getByRole('button',{name:'Technical analytics',exact:true}).click();
 await page.getByRole('img',{name:'TATAGOLD Lightweight 1d candlestick chart',exact:true}).locator('canvas').first().waitFor();
 await page.getByLabel('Chart engine',{exact:true}).selectOption('plotly');await page.getByRole('img',{name:'TATAGOLD technical price / 1d',exact:true}).locator('svg.main-svg').first().waitFor();
 const counts=async()=>{const d=(await(await fetch(host+'/market-data/session-policy',{headers:{Authorization:'Bearer '+token}})).json()).data;return {quote:d.quote_requests,intraday:d.intraday_requests};};
 const before=await counts();await page.getByRole('button',{name:'Forecasting Research',exact:true}).click();await page.getByLabel('Forecast lookback closes',{exact:true}).fill('20');
 let t=Date.now();await page.getByRole('button',{name:'Run Forecast',exact:true}).click();await page.getByRole('region',{name:'Current baseline forecasts',exact:true}).getByText('B03',{exact:false}).first().waitFor();const forecastMs=Date.now()-t;
 t=Date.now();await page.getByRole('button',{name:'Run Historical Evaluation',exact:true}).click();await page.getByRole('region',{name:'Historical baseline metrics',exact:true}).waitFor();const historicalMs=Date.now()-t;
 const after=await counts();if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Unexpected synthetic provider acquisition from forecast/evaluation');if(errors.length||csp.length)throw Error('Production browser runtime/CSP error');
 await page.screenshot({path:'artifacts/mvp05-production-synthetic.png',fullPage:true});
 const report={data_class:'SYNTHETIC_TEST',ui_origin:'http://127.0.0.1:15173',fixture_api:'18002',native:true,plotly:true,forecast:true,historical:true,forecast_ms:forecastMs,historical_evaluation_ms:historicalMs,provider_counters_before:before,provider_counters_after:after,page_errors:errors,csp_errors:csp};writeFileSync('artifacts/mvp05-production-smoke.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
