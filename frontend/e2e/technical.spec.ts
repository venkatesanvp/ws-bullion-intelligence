import {expect,test} from '@playwright/test';

test('technical daily and intraday values, native chart panes/crosshair/zoom/pan and existing chart fallback',async({page,request})=>{
 test.setTimeout(90000);await page.setViewportSize({width:1280,height:1200});
 const token=process.env.TEST_APP_TOKEN;if(!token)throw Error('Synthetic local token required');const headers={Authorization:'Bearer '+token};
 const session=(await(await request.get('http://127.0.0.1:8002/api/v1/transient-session',{headers})).json()).data;
 const item=session.instruments.find((i:{symbol:string})=>i.symbol==='TATAGOLD');
 await page.addInitScript(()=>{const original=window.fetch.bind(window);window.fetch=(input,init)=>original(typeof input==='string'?input.replace('127.0.0.1:8001/','127.0.0.1:8002/'):input,init);});
 await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(item.instrument_id);await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');
 await page.getByRole('button',{name:'Research dashboard',exact:true}).click();await page.getByRole('button',{name:'Technical analytics',exact:true}).click();
 await expect(page.getByRole('region',{name:'Exact technical values',exact:true}).locator('tbody tr')).toHaveCount(15);
 await expect(page.getByRole('img',{name:'TATAGOLD Lightweight 1d candlestick chart',exact:true})).toBeVisible();
 const daily=page.getByRole('img',{name:'TATAGOLD Lightweight 1d candlestick chart',exact:true});await expect(daily.locator('canvas').first()).toBeVisible();
 expect(await daily.locator('canvas').count()).toBeGreaterThanOrEqual(5);await expect(page.getByRole('link',{name:'TradingView',exact:true})).toBeVisible();
 await daily.scrollIntoViewIfNeeded();const box=await daily.boundingBox();if(!box)throw Error('Chart bounds unavailable');
 await page.mouse.move(box.x+box.width*.5,box.y+150);await expect(page.locator('.lightweight-research .notice')).toContainText('HISTORICAL_FINAL');
 const before=await daily.getAttribute('data-visible-range');await page.getByRole('button',{name:'Zoom in chart',exact:true}).click();await expect(daily).not.toHaveAttribute('data-visible-range',before||'');
 const zoomed=await daily.getAttribute('data-visible-range');await daily.scrollIntoViewIfNeeded();const moved=await daily.boundingBox();if(!moved)throw Error('Chart bounds unavailable');
 await page.mouse.move(moved.x+moved.width*.5,moved.y+150);await page.mouse.down();await page.mouse.move(moved.x+moved.width*.7,moved.y+150,{steps:8});await page.mouse.up();await expect(daily).not.toHaveAttribute('data-visible-range',zoomed||'');
 await page.getByRole('button',{name:'Reset chart range',exact:true}).click();
 await page.getByLabel('ATR period',{exact:true}).fill('3');await page.getByLabel('MACD fast period',{exact:true}).fill('2');await page.getByLabel('MACD slow period',{exact:true}).fill('3');await page.getByLabel('MACD signal period',{exact:true}).fill('2');await page.getByLabel('Donchian prior lookback',{exact:true}).fill('3');
 const response=page.waitForResponse(r=>r.url().endsWith('/research/technical')&&r.request().method()==='POST');await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();const result=(await(await response).json()).data;
 expect(result.parameters.atr_n).toBe(3);expect(result.indicators.MACD.values.some((v:{histogram:string|null})=>v.histogram!==null)).toBe(true);
 expect(result.indicators.ATR.values[3].value).not.toBeNull();expect(result.indicators.DONCHIAN.values[3].upper).not.toBeNull();
 await page.getByRole('combobox',{name:'Technical timeframe',exact:true}).selectOption('5');await page.getByRole('button',{name:'Apply technical settings',exact:true}).click();
 const intraday=page.getByRole('img',{name:'TATAGOLD Lightweight 5m candlestick chart',exact:true});await expect(intraday.locator('canvas').first()).toBeVisible();await expect(page.getByRole('region',{name:'Technical analytics',exact:true})).toContainText('5m');
 await page.getByRole('button',{name:'Daily research',exact:true}).click();await page.getByLabel('Chart engine',{exact:true}).selectOption('plotly');await expect(page.getByRole('img',{name:'TATAGOLD price chart',exact:true}).locator('svg.main-svg').first()).toBeVisible();
});
