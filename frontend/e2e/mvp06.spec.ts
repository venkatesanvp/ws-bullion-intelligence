import {test,expect,Page,APIRequestContext} from '@playwright/test';
import {mkdirSync} from 'node:fs';
const training=process.env.MVP06_CAPTURE_TRAINING==='1'?'../docs/06-user-guide/images':'../artifacts/mvp06-training';
test.beforeAll(()=>mkdirSync(training,{recursive:true}));
test.afterEach(async({page})=>{await page.unrouteAll({behavior:'wait'});});
async function open(page:Page,request:APIRequestContext){
 const token=process.env.TEST_APP_TOKEN;if(!token)throw Error('Synthetic test token required');
 const session=(await(await request.get('http://127.0.0.1:18012/api/v1/transient-session',{headers:{Authorization:'Bearer '+token}})).json()).data;
 await page.route('http://127.0.0.1:18011/api/v1/**',async route=>{if(route.request().url().endsWith('/stream-events'))return route.abort();const response=await route.fetch({url:route.request().url().replace(':18011/',':18012/')});await route.fulfill({response});});
 await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(session.instruments[0].instrument_id);await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');await page.getByRole('button',{name:'Research dashboard',exact:true}).click();return session;
}
test('MVP06 dashboard survives navigation, invalid selection, recoverable errors and repeated ETF changes',async({page,request})=>{
 test.setTimeout(120000);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));const session=await open(page,request);
 const landmark=page.getByRole('region',{name:'DhanHQ Market Snapshot and reconciliation',exact:true});
 await expect(page.getByRole('checkbox',{name:'MACD',exact:true})).toBeVisible();
 await page.getByLabel('EMA lookback',{exact:true}).fill('23');await page.getByRole('button',{name:'Apply research settings',exact:true}).click();await expect(page.getByRole('checkbox',{name:'EMA',exact:true})).toBeEnabled();await page.getByRole('checkbox',{name:'EMA',exact:true}).uncheck();
 await page.getByRole('button',{name:'History & quality',exact:true}).click();await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(session.instruments[1].instrument_id);await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
 await expect(page.getByLabel('EMA lookback',{exact:true})).toHaveValue('23');await expect(page.getByRole('checkbox',{name:'EMA',exact:true})).not.toBeChecked();
 for(const item of session.instruments){await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(item.instrument_id);await expect(landmark).toBeVisible();for(const name of ['SMA','EMA','RSI','MACD','ATR','DONCHIAN'])await expect(page.getByRole('checkbox',{name,exact:true})).toBeVisible();}
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption('');await expect(landmark).toBeVisible();await expect(page.getByText('Select an ETF and a source permitted for research.',{exact:false})).toBeVisible();await expect(page.getByRole('button',{name:'Forecasting Research',exact:true})).toBeEnabled();
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(session.instruments[0].instrument_id);await page.getByRole('button',{name:'Technical analytics',exact:true}).click();await expect(page.getByLabel('Technical EMA lookback',{exact:true})).toHaveValue('23');
 let fail=true;await page.route('**/research/technical',async route=>{if(fail){fail=false;await route.fulfill({status:503,json:{error:{code:'TEMPORARY_UNAVAILABLE',message:'Synthetic recoverable failure'}}});}else await route.fallback();});
 await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();await expect(page.getByRole('alert').first()).toBeVisible();await expect(landmark).toBeVisible();await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();await expect(page.getByRole('region',{name:'Exact technical values',exact:true}).locator('tbody tr')).toHaveCount(15);
 await page.getByRole('button',{name:'Reset to Defaults',exact:true}).click();await expect(page.getByLabel('Technical EMA lookback',{exact:true})).toHaveValue('20');await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();
 await expect(page.getByRole('img',{name:'TATAGOLD Lightweight 1d candlestick chart',exact:true})).toHaveAttribute('data-ready','true');mkdirSync(training,{recursive:true});await page.screenshot({path:training+'/synthetic-technical.png',fullPage:true});await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);expect(errors).toEqual([]);
});
test('MVP06 basic forecast, horizon invalidation, advanced evaluation and qualified comparison workflow',async({page,request})=>{
 test.setTimeout(120000);const session=await open(page,request);const sent:any[]=[];page.on('request',r=>{if(r.url().endsWith('/research/forecasts/run'))sent.push(r.postDataJSON());});
 await page.getByRole('button',{name:'Forecasting Research',exact:true}).click();const advanced=page.locator('details#advanced-research');await expect(advanced).not.toHaveAttribute('open','');
 await page.getByLabel('Forecast lookback closes',{exact:true}).fill('20');
 for(const horizon of ['1','5','20']){await page.getByRole('combobox',{name:'Forecast horizon',exact:true}).selectOption(horizon);await expect(page.getByRole('region',{name:'Current baseline forecasts',exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Generate Forecast',exact:true}).click();await expect(page.getByRole('region',{name:'Current baseline forecasts',exact:true})).toContainText('B03');}
 expect(sent.map(x=>x.horizon)).toEqual([1,5,20]);await expect(page.getByText(/Absolute change/).first()).toBeVisible();await expect(page.getByRole('region',{name:'TATAGOLD observed prices and forecast endpoints',exact:true}).locator('canvas').first()).toBeVisible();await page.screenshot({path:training+'/synthetic-forecast.png',fullPage:true});
 await page.getByText('6. Evaluate historical performance - Advanced Research',{exact:true}).click();await page.getByRole('button',{name:'Run Historical Evaluation',exact:true}).click();await expect(page.getByRole('region',{name:'Forecast performance scorecards',exact:true})).toBeVisible();await expect(page.getByRole('region',{name:'Historical forecast versus actual endpoints',exact:true}).locator('canvas').first()).toBeVisible();await page.screenshot({path:training+'/synthetic-evaluation.png',fullPage:true});
 await page.getByRole('button',{name:'ETF comparisons',exact:true}).click();for(let i=1;i<=2;i++){await page.getByRole('combobox',{name:'Comparison ETF '+i,exact:true}).selectOption(session.instruments[i-1].instrument_id);await page.getByRole('combobox',{name:'Comparison source '+i,exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Comparison basis '+i,exact:true}).selectOption('PROVIDER_ADJUSTED');}
 const acquired:string[]=[];page.on('request',r=>{if(r.url().includes('/ensure'))acquired.push(r.url());});await page.getByRole('button',{name:'Use available common period',exact:true}).click();await expect(page.getByLabel('Comparison from',{exact:true})).not.toHaveValue('');expect(acquired).toEqual([]);
 await page.getByRole('checkbox',{name:/I acknowledge that adjustment consistency/}).check();await page.getByRole('button',{name:'Compare prices',exact:true}).click();await expect(page.getByText('Comparison ready',{exact:true})).toBeVisible();await expect(page.getByText(/This comparison uses available observations and is provisional/)).toBeVisible();await expect(page.getByRole('columnheader',{name:'Maximum observed drawdown %',exact:true})).toBeVisible();await expect(page.getByRole('region',{name:'Common-date comparison values',exact:true}).locator('tbody tr')).toHaveCount(15);await expect(page.getByRole('img',{name:'Price-only common-date comparison',exact:true}).locator('.scatterlayer .trace')).toHaveCount(2);await page.screenshot({path:training+'/synthetic-comparison.png',fullPage:true});
 await page.getByRole('button',{name:'Research dashboard',exact:true}).click();const href=await page.getByRole('link',{name:'Research user guide',exact:true}).getAttribute('href');expect(href).toBe('/user-guide.html');expect((await request.get('http://127.0.0.1:15184'+href)).status()).toBe(200);
});



test('MVP06 a malformed snapshot stays inside its recoverable section boundary',async({page,request})=>{
 test.setTimeout(30000);
 await page.route('**/market-data/quotes',route=>route.fulfill({json:{data:{policy:null,quotes:[],error:null}}}));
 await open(page,request);
 // Last registered route forwards normal traffic; this route takes priority for the injected section failure.
 await page.route('**/market-data/quotes',route=>route.fulfill({json:{data:{policy:null,quotes:[],error:null}}}));
 await page.getByRole('button',{name:'Technical analytics',exact:true}).click();await page.getByRole('button',{name:'Daily research',exact:true}).click();
 await expect(page.getByText(/Market snapshot is unavailable/)).toBeVisible();await expect(page.getByRole('button',{name:'Try this section again',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Forecasting Research',exact:true})).toBeEnabled();await expect(page.getByRole('checkbox',{name:'MACD',exact:true})).toBeVisible();
});

test('forecast markers dispose before native canvases during rapid navigation and mobile resize',async({page,request})=>{
 test.setTimeout(90000);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await open(page,request);
 await page.getByRole('button',{name:'Forecasting Research',exact:true}).click();await expect(page.getByRole('button',{name:'Generate Forecast',exact:true})).toBeEnabled();await page.getByLabel('Forecast lookback closes',{exact:true}).fill('20');await page.getByRole('button',{name:'Generate Forecast',exact:true}).click();await expect(page.getByRole('region',{name:'Current baseline forecasts',exact:true})).toContainText('B01');
 await page.getByText('6. Evaluate historical performance - Advanced Research',{exact:true}).click();await page.getByRole('button',{name:'Run Historical Evaluation',exact:true}).click();await expect(page.getByRole('region',{name:'Historical forecast versus actual endpoints',exact:true}).locator('canvas').first()).toBeVisible();
 for(const tab of ['History & quality','ETF comparisons','Research dashboard'])await page.getByRole('button',{name:tab,exact:true}).click();await page.setViewportSize({width:390,height:844});await expect(page.getByRole('button',{name:'Generate Forecast',exact:true})).toBeEnabled();await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));expect(errors).toEqual([]);
});
