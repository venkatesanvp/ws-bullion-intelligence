import {test,expect} from '@playwright/test';
import {writeFileSync} from 'node:fs';

test('MVP native charts across four ETFs, indicators, themes, refresh, timeframe and responsive lifecycle',async({page,request})=>{
 test.setTimeout(180000);const token=process.env.TEST_APP_TOKEN;if(!token)throw Error('Synthetic token required');
 const session=(await(await request.get('http://127.0.0.1:18002/api/v1/transient-session',{headers:{Authorization:'Bearer '+token}})).json()).data;
 await page.route('http://127.0.0.1:18001/api/v1/**',async route=>{if(route.request().url().endsWith('/stream-events')){await route.abort();return;}const response=await route.fetch({url:route.request().url().replace(':18001/',':18002/')});await route.fulfill({response});});
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const measurements:{scenario:string;milliseconds:number}[]=[];
 await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
 await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
 for(const item of session.instruments){
  const t=Date.now();await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(item.instrument_id);await page.getByRole('button',{name:'Technical analytics',exact:true}).click();
  const chart=page.getByRole('img',{name:item.symbol+' Lightweight 1d candlestick chart',exact:true});await expect(chart).toHaveAttribute('data-ready','true');measurements.push({scenario:item.symbol+' daily switch/render',milliseconds:Date.now()-t});
  await expect(page.getByLabel('Chart engine',{exact:true})).toHaveValue('lightweight');await expect(page.getByRole('region',{name:'Exact technical values',exact:true}).locator('tbody tr')).toHaveCount(15);
 }
 const last=session.instruments.at(-1);const chart=page.getByRole('img',{name:last.symbol+' Lightweight 1d candlestick chart',exact:true});
 const canvasCount=await chart.locator('canvas').count();
 const toggle=Date.now();await page.getByRole('checkbox',{name:'RSI',exact:true}).uncheck();await expect(page.getByRole('checkbox',{name:'RSI',exact:true})).not.toBeChecked();measurements.push({scenario:'indicator visibility',milliseconds:Date.now()-toggle});
 await page.getByLabel('Chart theme',{exact:true}).selectOption('dark');await expect(page.locator('.lightweight-research')).toHaveAttribute('data-theme','dark');
 for(let i=0;i<3;i++){await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();await expect(chart).toHaveAttribute('data-ready','true');await expect(chart.locator('canvas')).toHaveCount(canvasCount);}
 await page.getByRole('combobox',{name:'Technical timeframe',exact:true}).selectOption('5');await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();const intraday=page.getByRole('img',{name:last.symbol+' Lightweight 5m candlestick chart',exact:true});await expect(intraday).toHaveAttribute('data-ready','true');
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await expect(intraday.locator('canvas').first()).toBeVisible();await page.screenshot({path:'../artifacts/mvp-native-mobile.png',fullPage:true});
 await page.setViewportSize({width:1440,height:1000});await page.getByLabel('Chart engine',{exact:true}).selectOption('plotly');await expect(page.getByRole('img',{name:last.symbol+' technical price / 5m',exact:true}).locator('svg.main-svg').first()).toBeVisible();
 await page.reload();// Token stays memory-only; reconnect explicitly.
 await expect(page.getByLabel('Local application token')).toBeVisible();
 expect(errors).toEqual([]);writeFileSync('../artifacts/mvp-browser-performance.json',JSON.stringify({data_class:'SYNTHETIC_TEST',measurements,stable_canvas_count:canvasCount,page_errors:errors},null,2));
});

test('MVP strict mode warnings and explicit conditional acknowledgement with real-like synthetic metadata',async({page,request})=>{
 test.setTimeout(60000);const token=process.env.TEST_APP_TOKEN!;const session=(await(await request.get('http://127.0.0.1:18002/api/v1/transient-session',{headers:{Authorization:'Bearer '+token}})).json()).data;
 let context:any=null;const modes:string[]=[];
 await page.route('http://127.0.0.1:18001/api/v1/**',async route=>{
  const url=route.request().url();if(url.endsWith('/stream-events')){await route.abort();return;}
  if(url.endsWith('/research/forecasts/evaluate')){const body=route.request().postDataJSON();modes.push(body.evaluation_mode);expect(body.acknowledge_replay_assumptions).toBe(body.evaluation_mode==='CONDITIONAL_HISTORICAL_REPLAY');await route.fulfill({json:{data:{status:'DATA_QUALITY_BLOCKED',reason:'METADATA_NOT_AVAILABLE',evaluation_mode:body.evaluation_mode,qualification_status:'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',context,sample_count:0,rows:[],exclusions:[],experiment:null,assumptions:[]}}});return;}
  const response=await route.fetch({url:url.replace(':18001/',':18002/')});const payload=await response.json();
  if(url.includes('/data-sources')){for(const source of payload.data||[])if(source.id===session.source_id)source.profile={...source.profile,data_class:'REAL_MARKET'};}
  if(url.includes('/research/forecasts/context?')){payload.data={...payload.data,data_class:'REAL_MARKET',quality:'CONDITIONAL_OWNER_RESEARCH',manual_refresh_enabled:false};context=payload.data;}
  await route.fulfill({response,json:payload});
 });
 await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(session.instruments[0].instrument_id);await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');await page.getByRole('button',{name:'Research dashboard',exact:true}).click();await page.getByRole('button',{name:'Forecasting Research',exact:true}).click();
 const mode=page.getByRole('combobox',{name:'Historical evaluation mode',exact:true});await expect(mode).toHaveValue('STRICT_POINT_IN_TIME');await page.getByRole('button',{name:'Run Historical Evaluation',exact:true}).click();await expect(page.getByText('Zero scores are not zero error.',{exact:false})).toBeVisible();await expect(mode).toHaveValue('STRICT_POINT_IN_TIME');
 await mode.selectOption('CONDITIONAL_HISTORICAL_REPLAY');await expect(page.getByRole('button',{name:'Run Historical Evaluation',exact:true})).toBeDisabled();await page.getByRole('checkbox',{name:'I acknowledge the fixed-vintage replay assumptions and limitations.',exact:true}).check();await page.getByRole('button',{name:'Run Historical Evaluation',exact:true}).click();await expect(page.getByText('Conditional retrospective research; not verified live predictive performance.',{exact:false})).toBeVisible();expect(modes).toEqual(['STRICT_POINT_IN_TIME','CONDITIONAL_HISTORICAL_REPLAY']);
});
