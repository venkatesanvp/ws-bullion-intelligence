import {expect,test} from '@playwright/test';

test('synthetic quotes, automatic refresh, intraday candles and timeframe indicators preserve daily research',async({page,request})=>{
  test.setTimeout(90000);
  const token=process.env.TEST_APP_TOKEN;if(!token)throw Error('Synthetic local test token required');
  const headers={Authorization:'Bearer '+token};
  const session=(await(await request.get('http://127.0.0.1:18002/api/v1/transient-session',{headers})).json()).data;
  const instrument=session.instruments.find((i:{symbol:string})=>i.symbol==='TATAGOLD');
  await page.route('http://127.0.0.1:18001/api/v1/**',async route=>{
    if(route.request().url().endsWith('/stream-events')){await route.abort();return;}
    const response=await route.fetch({url:route.request().url().replace(':18001/',':18002/')});
    await route.fulfill({response});
  });
  await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open Bullion Workspace/}).click();
  await page.getByRole('combobox',{name:'ETF listing',exact:true}).selectOption(instrument.instrument_id);
  await page.getByRole('combobox',{name:'Data source',exact:true}).selectOption(session.source_id);
  await page.getByRole('combobox',{name:'Price basis',exact:true}).selectOption('PROVIDER_ADJUSTED');
  await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
  await expect(page.locator('.quote-card')).toHaveCount(4);await expect(page.getByText('SYNTHETIC TEST DATA').first()).toBeVisible();
  const count=async()=> (await(await request.get('http://127.0.0.1:18002/api/v1/market-data/session-policy',{headers})).json()).data.quote_requests;
  const initial=await count();await expect.poll(count,{timeout:22000}).toBeGreaterThan(initial);
  await page.getByRole('button',{name:'Refresh quotes',exact:true}).click();await expect.poll(count).toBeGreaterThan(initial+1);
  await page.getByRole('button',{name:'Intraday research',exact:true}).click();
  await expect(page.getByRole('img',{name:'TATAGOLD Lightweight 5m candlestick chart',exact:true})).toBeVisible();
  await expect(page.getByRole('columnheader',{name:'SMA 20 / 5m',exact:true})).toBeVisible();
  await expect(page.getByText('PROVISIONAL - INTRADAY AGGREGATED', {exact:true})).toBeVisible();
  await page.getByRole('combobox',{name:'Intraday interval',exact:true}).selectOption('25');
  await page.getByRole('combobox',{name:'Intraday period',exact:true}).selectOption('previous');
  await page.getByRole('button',{name:'Apply intraday range',exact:true}).click();
  await expect(page.getByRole('columnheader',{name:'SMA 20 / 25m',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Daily research',exact:true}).click();
  await page.getByLabel('Chart engine',{exact:true}).selectOption('plotly');
  await expect(page.getByRole('img',{name:'TATAGOLD price chart',exact:true}).locator('svg.main-svg').first()).toBeVisible();
});
