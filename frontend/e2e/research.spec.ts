import { expect, test, APIRequestContext } from '@playwright/test';
import { randomUUID } from 'node:crypto';
const root='http://127.0.0.1:8001/api/v1';
function access(){
  const token=process.env.TEST_APP_TOKEN;
  if(!token || !process.env.TEST_DATABASE_URL)throw new Error('Explicit disposable PostgreSQL and synthetic test token required.');
  return {token,headers:{Authorization:'Bearer '+token,Origin:'http://127.0.0.1:5173'}};
}
async function fixture(request:APIRequestContext,withPrices=true,flat=false){
  const {headers}=access(),suffix=randomUUID().slice(0,8).toUpperCase();
  const sourceResponse=await request.post(root+'/data-sources',{headers,data:{label:'SYNTHETIC research source '+suffix,profile:{data_class:'SYNTHETIC_TEST',policy_version:'quality-v1'}}});
  expect(sourceResponse.status()).toBe(201);const source=(await sourceResponse.json()).data;
  const qualification=await request.patch(root+'/data-sources/'+source.id+'/qualification',{headers,data:{qualification:'QUALIFIED_FOR_RESEARCH',rights_evidence_ref:'Generated synthetic test only',retention_review_ref:'Disposable automated verification',permitted_uses:{retrieval:true,storage:true,analysis:true,display:true}}});
  expect(qualification.status()).toBe(200);
  const listings=[];
  for(const [metal,prefix]of [['GOLD','SG'],['SILVER','SS']]){
    const response=await request.post(root+'/instruments',{headers,data:{exchange:'XNSE',symbol:prefix+'_'+suffix,name:'SYNTHETIC TEST ONLY '+metal+' '+suffix,metal,currency:'INR'}});
    expect(response.status()).toBe(201);const instrument=(await response.json()).data;listings.push(instrument);
    if(withPrices){
      const csv=flat?'trading_date,close\n2026-01-01,10\n2026-01-02,10\n2026-01-03,10\n2026-01-04,10\n':metal==='GOLD'?'trading_date,close\n2026-01-01,10\n2026-01-02,12\n2026-01-03,14\n2026-01-04,13\n':'trading_date,close\n2026-01-01,20\n2026-01-03,23\n';
      const imported=await request.post(root+'/import-batches',{headers:{...headers,'Idempotency-Key':randomUUID()},multipart:{metadata_json:JSON.stringify({instrument_id:instrument.id,source_id:source.id,interval:'1d',price_basis:'RAW_CLOSE',mapping_version:'synthetic-v1',column_map:{trading_date:'trading_date',close:'close'},quality_policy_version:'quality-v1',qualification_ref:'Generated synthetic test only'}),file:{name:'synthetic-research.csv',mimeType:'text/csv',buffer:Buffer.from(csv)}}});
      expect(imported.status()).toBe(201);
    }
  }
  return {source,gold:listings[0],silver:listings[1]};
}

test('synthetic chart, overlays, RSI, common-date comparison and unavailable basis',async({page,request})=>{
  test.setTimeout(90000);
  const sample=await fixture(request),{token}=access();
  const external:string[]=[];
  page.on('request',request=>{const url=new URL(request.url());if(['http:','https:'].includes(url.protocol)&&!['http://127.0.0.1:5173','http://127.0.0.1:8001'].includes(url.origin))external.push(request.url());});
  await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open workspace/}).click();
  await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
  await page.getByLabel('ETF listing').selectOption(sample.gold.id);await page.getByLabel('Data source').selectOption(sample.source.id);
  await expect(page.getByRole('table',{name:'Exact prices and server-calculated indicator values'})).toBeVisible();
  await expect(page.getByLabel('SMA lookback')).toHaveValue('');
  for(const method of ['SMA','EMA','RSI']){
    await page.getByRole('checkbox',{name:method==='RSI'?'Show Wilder RSI':'Show '+method,exact:true}).check();
    await page.getByLabel(method+' lookback',{exact:true}).fill('2');
  }
  await page.getByRole('button',{name:'Apply research settings'}).click();
  await expect(page.getByText('66.666666666667',{exact:true})).toBeVisible();
  const priceChart=page.getByRole('img',{name:sample.gold.symbol+' price chart',exact:true});
  await expect(priceChart.locator('svg.main-svg').first()).toBeVisible();
  await expect(priceChart.locator('.scatterlayer .trace')).toHaveCount(3);
  await expect(page.getByRole('img',{name:sample.gold.symbol+' Wilder RSI',exact:true}).locator('svg.main-svg').first()).toBeVisible();
  await page.getByRole('checkbox',{name:'Show SMA',exact:true}).uncheck();
  await expect(page.getByRole('columnheader',{name:'SMA (2)',exact:true})).toHaveCount(0);
  await page.getByLabel('Research from',{exact:true}).fill('2026-01-03');await page.getByLabel('Research through',{exact:true}).fill('2026-01-04');
  await page.getByRole('button',{name:'Apply research settings'}).click();
  const table=page.getByRole('table',{name:'Exact prices and server-calculated indicator values'});
  await expect(table.getByRole('row').filter({hasText:'2026-01-03'}).locator('td').nth(2)).toHaveText('13.000000000000');
  await expect(priceChart.locator('svg.main-svg').first()).toBeVisible();
  await page.screenshot({path:'../artifacts/step4-research-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);
  expect(await priceChart.evaluate(node => { const caption=node.parentElement!.querySelector('figcaption')!; return caption.getBoundingClientRect().top >= node.getBoundingClientRect().bottom; })).toBe(true);
  await page.screenshot({path:'../artifacts/step4-research-mobile.png',fullPage:true});
  await page.setViewportSize({width:1280,height:900});
  await page.getByLabel('Research metal filter').selectOption('SILVER');await page.getByLabel('ETF listing').selectOption(sample.silver.id);
  await expect(page.getByRole('img',{name:sample.silver.symbol+' price chart',exact:true}).locator('svg.main-svg').first()).toBeVisible();
  await expect(page.getByRole('img',{name:sample.gold.symbol+' price chart',exact:true})).toHaveCount(0);
  await page.getByRole('button',{name:'ETF comparisons',exact:true}).click();
  for(const [index,instrument]of [[1,sample.gold],[2,sample.silver]] as const){
    await page.getByRole('combobox',{name:'Comparison ETF '+index,exact:true}).selectOption(instrument.id);
    await page.getByRole('combobox',{name:'Comparison source '+index,exact:true}).selectOption(sample.source.id);
    await page.getByRole('combobox',{name:'Comparison basis '+index,exact:true}).selectOption('RAW_CLOSE');
  }
  await page.getByLabel('Comparison from',{exact:true}).fill('2026-01-01');await page.getByLabel('Comparison through',{exact:true}).fill('2026-01-03');
  await page.getByRole('button',{name:'Compare prices',exact:true}).click();
  await expect(page.getByText('40.000000000000',{exact:true})).toBeVisible();await expect(page.getByText('15.000000000000',{exact:true})).toBeVisible();
  await expect(page.getByText(/Actual common endpoints: 2026-01-01 through 2026-01-03/)).toBeVisible();
  await expect(page.getByRole('img',{name:'Price-only common-date comparison',exact:true}).locator('.scatterlayer .trace')).toHaveCount(2);
  await expect(page.getByText(/Price-only change is not total return/)).toBeVisible();
  await page.screenshot({path:'../artifacts/step4-comparison-desktop.png',fullPage:true});
  await page.getByRole('combobox',{name:'Comparison basis 1',exact:true}).selectOption('UNKNOWN');await page.getByRole('button',{name:'Compare prices',exact:true}).click();
  await expect(page.getByText('UNAVAILABLE',{exact:true})).toBeVisible();await expect(page.getByText(/BASIS_UNVERIFIED/).first()).toBeVisible();
  await expect(page.getByRole('img',{name:'Price-only common-date comparison',exact:true})).toHaveCount(0);
  expect(external).toEqual([]);
  expect(await page.evaluate(()=>localStorage.length+sessionStorage.length)).toBe(0);
});

test('synthetic missing history and flat RSI remain unavailable',async({page,request})=>{
  const empty=await fixture(request,false),flat=await fixture(request,true,true),{token}=access();
  await page.goto('/');await page.getByLabel('Local application token').fill(token);await page.getByRole('button',{name:/Open workspace/}).click();await page.getByRole('button',{name:'Research dashboard',exact:true}).click();
  await page.getByLabel('ETF listing').selectOption(empty.gold.id);await page.getByLabel('Data source').selectOption(empty.source.id);
  await expect(page.getByText('No observations are available for this research range.',{exact:true})).toBeVisible();
  await page.getByLabel('ETF listing').selectOption(flat.gold.id);await page.getByLabel('Data source').selectOption(flat.source.id);
  await page.getByRole('checkbox',{name:'Show Wilder RSI',exact:true}).check();await page.getByLabel('RSI lookback',{exact:true}).fill('2');await page.getByRole('button',{name:'Apply research settings'}).click();
  await expect(page.getByText('UNAVAILABLE: FLAT_WINDOW | OBSERVED_BARS',{exact:true})).toBeVisible();
  await expect(page.getByText('Unavailable: FLAT_WINDOW',{exact:true})).toHaveCount(2);
  await expect(page.getByRole('img',{name:flat.gold.symbol+' Wilder RSI',exact:true})).toHaveCount(0);
});
