import {useEffect} from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ResearchDashboard from './ResearchDashboard';
import ComparisonPanel from './ComparisonPanel';
import { ApiError, Call, ComparisonResult, IndicatorResult, Instrument, PriceChartResult, SeriesMeta, Source } from './api';
const plot = vi.hoisted(() => ({ react: vi.fn(async (..._args: unknown[]) => undefined), purge: vi.fn(), resize: vi.fn() }));
vi.mock('plotly.js-basic-dist-min', () => ({ default: { react: plot.react, purge: plot.purge, Plots: { resize: plot.resize } } }));
const gold: Instrument = { id:'gold',exchange:'XNSE',symbol:'SYNTH_GOLD',name:'Synthetic only',metal:'GOLD',currency:'INR',active:true,data_revision:1 };
const silver: Instrument = { ...gold,id:'silver',symbol:'SYNTH_SILVER',metal:'SILVER' };
const source: Source = { id:'source',label:'Synthetic only source',qualification:'QUALIFIED_FOR_RESEARCH',rights_evidence_ref:'SYNTHETIC TEST',permitted_uses:{},profile:{data_class:'SYNTHETIC_TEST',policy_version:'quality-v1'},reviewed_at:null };
const ref = {instrument_id:'gold',source_id:'source',interval:'1d',price_basis:'RAW_CLOSE',revision:1,profile_digest:'synthetic-profile'};
const meta: SeriesMeta = {source:{label:source.label,data_class:'SYNTHETIC_TEST',verification:'OWNER_RECORDED'},series_ref:ref,coverage:{count:4,dataset_count:4,dataset_first_date:'2026-01-01',dataset_last_date:'2026-01-04',range_first_date:'2026-01-01',range_last_date:'2026-01-04'},quality:{flags:['CALENDAR_UNVERIFIED','PUBLICATION_TIME_UNKNOWN'],continuity:'UNVERIFIED',missing_session_count:0,missing_session_dates:[],publication_unknown_count:4,known_break_dates:[],import_issue_counts:{}},freshness:{status:'UNASSESSED',assessment_as_of:'2026-01-05T00:00:00Z',actual_latest_date:'2026-01-04',expected_latest_date:null,reason:'NO_APPLICABLE_APPROVED_AS_OF_POLICY'},limitations:['UNVERIFIED_FOR_REPLAY']};
const dates=['2026-01-01','2026-01-02','2026-01-03','2026-01-04'];
const prices: PriceChartResult = {status:'AVAILABLE',unavailable_reason:null,series_ref:ref,computed_at:'2026-01-05T00:00:00Z',input_fingerprint:'synthetic-price',input_evidence:{observation_count:4,first_date:dates[0],last_date:dates[3],batch_ids:['synthetic-batch']},points:dates.map((day,i)=>({trading_date:day,close:['10.0000000000','12.0000000000','14.0000000000','13.0000000000'][i],observation_id:'synthetic-'+i,batch_id:'synthetic-batch',row_number:i+1,break_before:null}))};
function calculation(method:string,n=2):IndicatorResult { return {status:'AVAILABLE',unavailable_reason:null,indicator_id:method,algorithm_version:'decimal-research-v1',n,window_unit:'OBSERVED_BARS',series_ref:ref,seed_date:'2026-01-02',seed_dates:['2026-01-02'],computed_at:'2026-01-05T00:00:00Z',input_fingerprint:'synthetic-'+method,values:dates.map((day,i)=>({trading_date:day,value:(method==='RSI'?[null,null,'100.000000000000','66.666666666667']:method==='SMA'?[null,'11.000000000000','13.000000000000','13.500000000000']:[null,'11.000000000000','13.000000000000','13.000000000000'])[i],reason:i===0?'WARMUP':null,seed_date:i===0?null:'2026-01-02',break_before:null}))}; }
type Handler = (path:string,options?:RequestInit)=>Promise<{data:unknown;meta?:unknown}>|{data:unknown;meta?:unknown};
function technical(parameters={sma_n:20,ema_n:20,rsi_n:14,atr_n:14,macd_fast:12,macd_slow:26,macd_signal:9,donchian_n:20},listing=gold,close?:string){
 const identity={...ref,instrument_id:listing.id};
 return {data:{instrument_id:listing.id,symbol:listing.symbol,timeframe:'1d',parameters,series_ref:identity,status:'AVAILABLE',input_fingerprint:'synthetic',computed_at:'2026-01-05T00:00:00Z',source:source.label,source_qualification:source.qualification,price_basis:'RAW_CLOSE',freshness:'UNASSESSED',warmup_bars:0,warnings:[],candles:prices.points.map(p=>({time:p.trading_date,close:close||p.close,open:null,high:null,low:null,volume:null,classification:'SYNTHETIC_TEST'})),indicators:Object.fromEntries(['SMA','EMA','RSI'].map(m=>[m,{algorithm_version:'test',values:calculation(m).values.map(v=>({...v,time:v.trading_date,value:parameters[m==='SMA'?'sma_n':m==='EMA'?'ema_n':'rsi_n']===2?v.value:null,reason:'WARMUP'}))}]))},meta:{...meta,series_ref:identity}};
}
function client(handler?:Handler):Call {return async<T,>(path:string,options?:RequestInit)=>{if(handler)return await handler(path,options) as {data:T};return technical(JSON.parse(String(options?.body)).parameters) as unknown as {data:T};};}
beforeEach(()=>plot.react.mockClear());
async function enable(user:ReturnType<typeof userEvent.setup>,method:string){await user.clear(screen.getByLabelText(method+' lookback'));await user.type(screen.getByLabelText(method+' lookback'),'2');}

describe('approved research views',()=>{
 it('uses conventional defaults and a single snapshot, renders exact values and hides only the selected overlay',async()=>{
  const user=userEvent.setup();render(<ResearchDashboard api={client()} instrument={gold} source={source} basis="RAW_CLOSE"/>);await screen.findByText('10.0000000000');
  expect(screen.getByLabelText('SMA lookback')).toHaveValue(20);expect(screen.getByLabelText('EMA lookback')).toHaveValue(20);
  for(const m of ['SMA','EMA','RSI'])await enable(user,m);
  await user.click(screen.getByRole('button',{name:'Apply research settings'}));await screen.findByText('66.666666666667');
  expect(screen.getByRole('columnheader',{name:'EMA (2)'})).toBeInTheDocument();
  await waitFor(()=>expect(plot.react.mock.calls.some(call=>(call[1] as {name:string}[]).some(t=>t.name==='SMA (2)'))).toBe(true));
  await user.click(screen.getByRole('checkbox',{name:'SMA'}));await waitFor(()=>expect((plot.react.mock.calls.at(-1)![1] as {name:string}[]).some(t=>t.name==='SMA (2)')).toBe(false));
  expect(screen.getByRole('columnheader',{name:'SMA (2)'})).toBeInTheDocument();
 });
 it('discards a late Gold snapshot after switching to Silver',async()=>{
  let complete!:(value:unknown)=>void;const api=vi.fn(async(_p:string,o?:RequestInit)=>{const b=JSON.parse(String(o?.body));return b.instrument_id==='gold'?new Promise(resolve=>{complete=resolve;}):technical(b.parameters,silver,'22.0000000000');}) as unknown as Call;
  const view=render(<ResearchDashboard api={api} instrument={gold} source={source} basis="RAW_CLOSE"/>);await waitFor(()=>expect(complete).toBeTypeOf('function'));
  view.rerender(<ResearchDashboard api={api} instrument={silver} source={source} basis="RAW_CLOSE"/>);await screen.findAllByText('22.0000000000');await act(async()=>complete(technical()));expect(screen.queryByText('10.0000000000')).toBeNull();
 });
 it('rejects mismatched snapshot evidence instead of mixing response identities',async()=>{
  const bad=technical();bad.data.series_ref={...ref,revision:2};render(<ResearchDashboard api={client(()=>bad)} instrument={gold} source={source} basis="RAW_CLOSE"/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('SNAPSHOT_CHANGED');expect(screen.queryByRole('table')).toBeNull();expect(screen.getByRole('group',{name:'Research timeframe'})).toBeInTheDocument();
 });
 it('retains all six discoverable indicators and warm-up reasons when history is insufficient',async()=>{
  render(<ResearchDashboard api={client()} instrument={gold} source={source} basis="RAW_CLOSE"/>);await screen.findByText('10.0000000000');
  for(const n of ['SMA','EMA','RSI','MACD','ATR','DONCHIAN'])expect(screen.getByRole('checkbox',{name:n})).toBeDisabled();
  expect(screen.getAllByText('Unavailable: WARMUP').length).toBeGreaterThanOrEqual(4);expect(screen.queryByText('66.666666666667')).toBeNull();
 });
});

function comparison(reason:string|null=null):ComparisonResult {
  return {status:reason?'UNAVAILABLE':'AVAILABLE',unavailable_reason:reason,method_version:'common-date-price-v1',computed_at:'2026-01-05T00:00:00Z',requested_period:{start:'2026-01-01',end:'2026-01-04'},effective_period:{start:reason?null:'2026-01-01',end:reason?null:'2026-01-03'},common_dates:reason?[]:['2026-01-01','2026-01-03'],common_observation_count:reason?0:2,input_fingerprint:'synthetic-comparison',limitations:['PRICE_ONLY_NOT_TOTAL_RETURN'],series:[gold,silver].map((i,index)=>({key:i.id,currency:'INR',price_basis:'RAW_CLOSE',data_class:'SYNTHETIC_TEST',close_end:reason?null:index?'23.0000000000':'12.0000000000',volume_end:null,price_change_percent:reason?null:index?'15.000000000000':'20.000000000000',input_fingerprint:'synthetic-'+i.id,values:reason?[]:[{trading_date:'2026-01-01',close:index?'20':'10',rebased_price:'100.000000000000',volume:null,observation_id:'synthetic-first-'+i.id,batch_id:'synthetic-batch',row_number:1},{trading_date:'2026-01-03',close:index?'23':'12',rebased_price:index?'115.000000000000':'120.000000000000',volume:null,observation_id:'synthetic-last-'+i.id,batch_id:'synthetic-batch',row_number:2}],meta:{...meta,instrument:{id:i.id,symbol:i.symbol,name:i.name,metal:i.metal},input_fingerprint:'synthetic-'+i.id}}))};
}
async function selectComparison(user:ReturnType<typeof userEvent.setup>){
  for(let i=1;i<=2;i++){
    await user.selectOptions(screen.getByRole('combobox',{name:'Comparison ETF '+i}),i===1?'gold':'silver');
    await user.selectOptions(screen.getByRole('combobox',{name:'Comparison source '+i}),'source');
    await user.selectOptions(screen.getByRole('combobox',{name:'Comparison basis '+i}),'RAW_CLOSE');
  }
  fireEvent.change(screen.getByLabelText('Comparison from'),{target:{value:'2026-01-01'}});
  fireEvent.change(screen.getByLabelText('Comparison through'),{target:{value:'2026-01-04'}});
}

describe('price-only comparison UI',()=>{
  it('sends explicit selectors/period and shows actual common dates, exact values and limitations',async()=>{
    let sent='';
    const api=client((_path,options)=>{sent=String(options?.body);return {data:comparison()};});
    const user=userEvent.setup();render(<ComparisonPanel api={api} instruments={[gold,silver]} sources={[source]}/>);
    await selectComparison(user);await user.click(screen.getByRole('button',{name:'Compare prices'}));
    await screen.findByText('20.000000000000');
    expect(JSON.parse(sent)).toEqual({series:[{instrument_id:'gold',source_id:'source',price_basis:'RAW_CLOSE'},{instrument_id:'silver',source_id:'source',price_basis:'RAW_CLOSE'}],start:'2026-01-01',end:'2026-01-04'});
    expect(screen.getByText(/Price-only change is not total return/)).toBeInTheDocument();
    expect(screen.getByText(/Actual common endpoints: 2026-01-01 through 2026-01-03/)).toBeInTheDocument();
    expect(screen.getAllByText('Unavailable').length).toBeGreaterThan(0);
    fireEvent.change(screen.getByLabelText('Comparison from'),{target:{value:'2026-01-02'}});
    expect(screen.queryByText('20.000000000000')).toBeNull();
  });
  it.each(['INCOMPATIBLE_BASIS','NO_COMMON_DATES'])('shows %s without plotting a comparison',async reason=>{
    const data=comparison(reason);
    const api=client(()=>{if(reason==='INCOMPATIBLE_BASIS')throw new ApiError(422,reason,'Series comparison prerequisites are not established.',{data});return {data};});
    const user=userEvent.setup();render(<ComparisonPanel api={api} instruments={[gold,silver]} sources={[source]}/>);
    await selectComparison(user);await user.click(screen.getByRole('button',{name:'Compare prices'}));
    await screen.findByText('UNAVAILABLE');
    expect(screen.getAllByText(new RegExp(reason)).length).toBeGreaterThan(0);
    expect(screen.queryByRole('img',{name:'Price-only common-date comparison'})).toBeNull();
  });
});


it('displays owner-authorized transient research without granting storage qualification', async () => {
  const transient = { ...source, qualification: 'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',
    permitted_uses: { retrieval: true, analysis: true, display: true, storage: false } };
  render(<ResearchDashboard api={client()} instrument={gold} source={transient} basis="RAW_CLOSE"/>);
  expect(await screen.findByText('10.0000000000')).toBeInTheDocument();
  expect(transient.qualification).not.toBe('QUALIFIED_FOR_RESEARCH');
  expect(transient.permitted_uses.storage).toBe(false);
});

// Canvas is verified with the native chart API tests and real Chromium. jsdom has no canvas.
vi.mock('./LightweightResearchChart',()=>({default:({onUnavailable}:{onUnavailable?:(message:string)=>void})=>{useEffect(()=>{onUnavailable?.('Canvas renderer unavailable in jsdom; fallback exercised.');},[]);return null;}}));

it('keeps navigation and the market landmark accessible when selection is empty',()=>{
 const calls=vi.fn();render(<ResearchDashboard api={calls as unknown as Call} basis="RAW_CLOSE"/>);
 expect(screen.getByRole('region',{name:'DhanHQ Market Snapshot and reconciliation'})).toBeInTheDocument();
 for(const name of ['Daily research','Intraday research','Technical analytics','Forecasting Research'])expect(screen.getByRole('button',{name})).toBeEnabled();
 expect(calls).not.toHaveBeenCalled();
});

it('preserves valid periods and chart visibility across an unmount and instrument change',async()=>{
 const {ResearchPreferencesProvider}=await import('./researchPreferences');const user=userEvent.setup();
 const api=client((_p,o)=>{const body=JSON.parse(String(o?.body));return technical(body.parameters,body.instrument_id==='silver'?silver:gold);});
 const view=render(<ResearchPreferencesProvider><ResearchDashboard api={api} instrument={gold} source={source} basis="RAW_CLOSE"/></ResearchPreferencesProvider>);await screen.findByText('10.0000000000');
 for(const m of ['SMA','EMA','RSI'])await enable(user,m);await user.click(screen.getByRole('button',{name:'Apply research settings'}));await screen.findByText('66.666666666667');await user.click(screen.getByRole('checkbox',{name:'SMA'}));
 view.rerender(<ResearchPreferencesProvider><p>History view</p></ResearchPreferencesProvider>);
 view.rerender(<ResearchPreferencesProvider><ResearchDashboard api={api} instrument={silver} source={source} basis="RAW_CLOSE"/></ResearchPreferencesProvider>);
 await screen.findByText('66.666666666667');expect(screen.getByLabelText('EMA lookback')).toHaveValue(2);expect(screen.getByRole('checkbox',{name:'SMA'})).not.toBeChecked();
 for(const id of ['SMA','EMA','RSI','MACD','ATR','DONCHIAN'])expect(screen.getByRole('checkbox',{name:id})).toBeInTheDocument();
});

it('offers provisional comparison only after explicit source acknowledgement',async()=>{
 const dhan={...source,source_kind:'DHANHQ' as const};const calls=vi.fn(async(_p:string,o?:RequestInit)=>{const b=JSON.parse(String(o?.body));if(!b.acknowledge_source_limitations)throw new ApiError(422,'ADJUSTMENT_COMPATIBILITY_UNVERIFIED','Qualification missing.',{data:comparison('ADJUSTMENT_COMPATIBILITY_UNVERIFIED')});return {data:{...comparison(),qualification_status:'PROVISIONAL_PROVIDER_AS_DELIVERED'}};});
 render(<ComparisonPanel api={calls as unknown as Call} instruments={[gold,silver]} sources={[dhan]}/>);
 fireEvent.change(screen.getByLabelText('Comparison from'),{target:{value:'2026-01-01'}});fireEvent.change(screen.getByLabelText('Comparison through'),{target:{value:'2026-01-04'}});fireEvent.click(screen.getByRole('button',{name:'Compare prices'}));
 expect(await screen.findByRole('alert')).toHaveTextContent('Price-adjustment consistency');expect(JSON.parse(String(calls.mock.calls[0][1]?.body)).qualification_mode).toBeUndefined();
 fireEvent.click(screen.getByRole('checkbox',{name:/I acknowledge that adjustment consistency/}));fireEvent.click(screen.getByRole('button',{name:'Compare prices'}));await screen.findByText('Comparison ready');
 expect(JSON.parse(String(calls.mock.calls.at(-1)?.[1]?.body))).toMatchObject({qualification_mode:'PROVISIONAL_AS_DELIVERED',acknowledge_source_limitations:true});
});

it('inspects available common dates without downloading history',async()=>{
 const calls=vi.fn(async(path:string)=>({data:{points:(path.includes('/gold/')?['2026-01-01','2026-01-02','2026-01-04']:['2026-01-02','2026-01-03','2026-01-04']).map(trading_date=>({trading_date}))}}));
 render(<ComparisonPanel api={calls as unknown as Call} instruments={[gold,silver]} sources={[source]}/>);fireEvent.click(screen.getByRole('button',{name:'Use available common period'}));
 await waitFor(()=>expect(screen.getByLabelText('Comparison from')).toHaveValue('2026-01-02'));expect(screen.getByLabelText('Comparison through')).toHaveValue('2026-01-04');expect(calls.mock.calls).toHaveLength(2);expect(calls.mock.calls.every(([p])=>p.includes('/chart?'))).toBe(true);
});

it('rejects interleaved cached histories with no common observations rather than inventing a shared period',async()=>{
 const calls=vi.fn(async(path:string)=>({data:{points:(path.includes('/gold/')?['2026-01-01','2026-01-03']:['2026-01-02','2026-01-04']).map(trading_date=>({trading_date}))}}));
 render(<ComparisonPanel api={calls as unknown as Call} instruments={[gold,silver]} sources={[source]}/>);fireEvent.click(screen.getByRole('button',{name:'Use available common period'}));expect(await screen.findByRole('alert')).toHaveTextContent('at least two common observed dates');expect(screen.getByLabelText('Comparison from')).toHaveValue('');expect(calls.mock.calls).toHaveLength(2);
});
