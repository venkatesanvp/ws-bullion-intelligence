import {expect,test} from '@playwright/test';

test('synthetic binary feed reaches authenticated browser SSE and reconciliation refreshes daily research',async({page,request})=>{
 const token=process.env.TEST_APP_TOKEN;if(!token)throw Error('Synthetic local token required');
 const headers={Authorization:'Bearer '+token};
 const session=(await(await request.get('http://127.0.0.1:18012/api/v1/transient-session',{headers})).json()).data;
 const item=session.instruments.find((i:{symbol:string})=>i.symbol==='TATAGOLD');
 // Select the synthetic backend for every local browser API call, including SSE.
 await page.addInitScript(()=>{const original=window.fetch.bind(window);window.fetch=(input,init)=>original(typeof input==='string'?input.replace('127.0.0.1:18011/','127.0.0.1:18012/'):input,init);});
 await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
 await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(item.instrument_id);
 await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);
 await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');
 await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
 await expect(page.getByText(/Read-only stream: CONNECTED/)).toBeVisible();
 await expect(page.locator('.quote-card').first()).toContainText('LIVE_STREAM');
 await expect(page.locator('.quote-card').first()).toContainText('101.23 INR');
 await page.getByLabel('Reconciliation session').fill('2026-11-05');
 await page.getByRole('button',{name:'Reconcile selected session',exact:true}).click();
 await expect(page.getByRole('region',{name:'Daily reconciliation'})).toContainText('HISTORICAL_FINAL');
 // Reconciliation remounts the research snapshot, whose approved default is native.
 await expect(page.getByRole('img',{name:'TATAGOLD Lightweight 1d candlestick chart',exact:true}).locator('canvas').first()).toBeVisible();
 await page.getByRole('button',{name:'Disconnect feed',exact:true}).click();
 await expect(page.getByText(/Read-only stream: DISCONNECTED/)).toBeVisible();
 await expect(page.getByText(/Controlled quote polling is the fallback/)).toBeVisible();
 await expect(page.locator('.quote-card')).toHaveCount(4);
});
