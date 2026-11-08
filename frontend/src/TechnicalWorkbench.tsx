import FinancialChart from './FinancialChart';
import {useResearchPreference} from './researchPreferences';
import {INDICATORS} from './indicatorCatalog';
import {useEffect,useRef,useState} from 'react';
import {Call,Instrument,Source,IntradayResult,SeriesMeta,ensureProviderHistory,acquisitionMessage,supportsMarketSession,exchangeTime} from './api';
import DataViewport,{DATA_PAGE_SIZE} from './DataViewport';
import {defaultTechnical,TechnicalParameters,TechnicalResult,TechnicalValue} from './technicalTypes';
import {ResearchField as Field,DataClass,ResearchQuality} from './ResearchShared';
const labels:Record<keyof TechnicalParameters,string>={atr_n:'ATR period',macd_fast:'MACD fast period',macd_slow:'MACD slow period',macd_signal:'MACD signal period',donchian_n:'Donchian prior lookback',sma_n:'Technical SMA lookback',ema_n:'Technical EMA lookback',rsi_n:'Technical RSI lookback'};
type ExtendedIntraday=IntradayResult&{technical:TechnicalResult['indicators']|null;input_fingerprint?:string;computed_at:string;missing_timestamps:string[]};
export default function TechnicalWorkbench({api,instrument,source,basis,mode='technical'}:{api:Call;instrument:Instrument;source:Source;basis:string;mode?:'daily'|'technical'}){
 const [meta,setMeta]=useState<SeriesMeta|null>(null);
 const [frame,setFrame]=useResearchPreference('technicalTimeframe','1d'),[preset,setPreset]=useState('previous'),[start,setStart]=useResearchPreference('researchFrom',''),[end,setEnd]=useResearchPreference('researchThrough',''),[parameters,setParameters]=useResearchPreference('technicalParameters',defaultTechnical),[result,setResult]=useState<TechnicalResult|null>(null),[problem,setProblem]=useState(''),[busy,setBusy]=useState(false),[shown,setShown]=useState(DATA_PAGE_SIZE);
 const abort=useRef<AbortController|null>(null),generation=useRef(0);
 async function load(){const current=++generation.current;abort.current?.abort();const controller=new AbortController();abort.current=controller;
  const selectedFrame=mode==='daily'?'1d':frame;
  if(start&&end&&start>end){setBusy(false);setProblem('From must be on or before Through.');return;}
  if(Object.values(parameters).some(n=>!Number.isSafeInteger(n)||n<1||n>10000)||parameters.rsi_n<2||parameters.macd_fast>=parameters.macd_slow||parameters.macd_slow+parameters.macd_signal-1>10000||Math.max(parameters.atr_n+1,parameters.donchian_n+1,parameters.rsi_n+1)>10000){setBusy(false);setProblem('Use positive integer periods, RSI at least 2, fast less than slow and a MACD warm-up within 10000 bars.');return;}
  setBusy(true);setProblem('');setResult(null);setMeta(null);setShown(DATA_PAGE_SIZE);
  try{let data:TechnicalResult;
   if(selectedFrame==='1d'){
    const acquisition=basis==='PROVIDER_ADJUSTED'?await ensureProviderHistory(api,instrument,source,start,end,controller.signal,Math.max(parameters.atr_n+1,parameters.macd_slow+parameters.macd_signal-1,parameters.donchian_n+1,parameters.sma_n,parameters.ema_n,parameters.rsi_n+1)):null;
    if(current!==generation.current||controller.signal.aborted)return;
    if(acquisition?.error)setProblem(acquisitionMessage(acquisition));
    const response=await api<TechnicalResult>('/research/technical',{method:'POST',signal:controller.signal,body:JSON.stringify({instrument_id:instrument.id,source_id:source.id,basis,start:start||null,end:end||null,parameters})});
    data=response.data;
    const raw=data as TechnicalResult&{series_ref?:Record<string,unknown>};const evidence=response.meta as unknown as SeriesMeta|undefined;
    if(data.instrument_id!==instrument.id||data.timeframe!=='1d'||raw.series_ref?.source_id!==source.id||raw.series_ref?.price_basis!==basis||!evidence||(['instrument_id','source_id','price_basis','interval','revision','profile_digest'] as const).some(k=>raw.series_ref?.[k]!==(evidence.series_ref as unknown as Record<string,unknown>)[k]))throw Error('SNAPSHOT_CHANGED: returned research identity differs. Reload the selected series.');
    if(current===generation.current&&!controller.signal.aborted)setMeta(evidence);
   }else{
    const r=(await api<ExtendedIntraday>('/market-data/intraday',{method:'POST',signal:controller.signal,body:JSON.stringify({instrument_id:instrument.id,interval:Number(selectedFrame),preset,start:start||null,end:end||null,indicators:{SMA:parameters.sma_n,EMA:parameters.ema_n,RSI:parameters.rsi_n},technical:parameters})})).data;
    const indicators:TechnicalResult['indicators']={...(r.technical||{})};
    for(const [name,bundle]of Object.entries(r.indicators))indicators[name]={algorithm_version:'decimal-research-v1',values:bundle.values.map(v=>({...v,time:v.candle_start}))};
    data={instrument_id:r.instrument_id,symbol:r.listing.symbol,timeframe:selectedFrame+'m',parameters,indicators,candles:r.candles.filter(c=>c.classification==='INTRADAY_COMPLETED').map(c=>({...c,time:c.start,break_before:r.technical?.MACD.values.find(v=>v.time===c.start)?.break_before})),gap_times:r.missing_timestamps,status:r.status,input_fingerprint:r.input_fingerprint||String(r.revision),computed_at:r.computed_at,warmup_bars:r.warmup_bars,source:r.source,source_qualification:source.qualification,price_basis:r.price_basis||'INTRADAY_PROVIDER_ADJUSTMENT_UNQUALIFIED',freshness:r.freshness,warnings:r.warnings,last_successful_retrieval:r.last_successful_retrieval};
    if(r.error)setProblem('Intraday retrieval status: '+r.error+'. Available completed data is shown.');
   }
   if(current===generation.current&&!controller.signal.aborted)setResult(data);
  }catch(error){if(current===generation.current&&!controller.signal.aborted)setProblem(error instanceof Error?error.message:'Technical research unavailable.');}
  finally{if(current===generation.current)setBusy(false);}
 }
 useEffect(()=>{void load();return()=>{++generation.current;abort.current?.abort();};},[api,instrument.id,source.id,basis]);
 const lookup=(name:string,time:string)=>(result?.indicators[name]?.values||[]).find(v=>v.time===time);
 const number=(v:TechnicalValue|undefined,field:keyof TechnicalValue='value')=>v&&typeof v[field]==='string'?String(v[field]):'Unavailable: '+(v?.reason||'WARMUP_OR_MISSING');
 return <section className="card technical-workbench" aria-label={mode==='daily'?'Daily research':'Technical analytics'}><DataClass synthetic={source.profile.data_class==='SYNTHETIC_TEST'}/><h2>{instrument.symbol} {mode==='daily'?'research dashboard':'technical analytics'}</h2><p>Deterministic completed-bar research. ATR/MACD/prior-window Donchian add descriptive context; no forecasts or buy/sell signals are generated.</p>
  <form onSubmit={e=>{e.preventDefault();void load();}}><div className="range-bar">{mode!=='daily'&&<Field label="Technical timeframe"><select value={frame} onChange={e=>setFrame(e.target.value)}><option value="1d">Daily</option>{(supportsMarketSession(source)?[1,5,15,25,60]:[]).map(n=><option key={n} value={String(n)}>{n} minutes</option>)}</select></Field>}
  {mode!=='daily'&&frame!=='1d'&&<Field label="Technical intraday period"><select value={preset} onChange={e=>setPreset(e.target.value)}><option value="previous">Previous trading session</option><option value="current">Current session (completed bars)</option><option value="five">Last five sessions</option><option value="thirty">Last 30 calendar days</option><option value="custom">Custom</option></select></Field>}
  <Field label={mode==='daily'?'Research from':'Technical from'}><input type="date" value={start} onChange={e=>setStart(e.target.value)}/></Field><Field label={mode==='daily'?'Research through':'Technical through'}><input type="date" value={end} onChange={e=>setEnd(e.target.value)}/></Field></div>
  <fieldset className="technical-parameters"><legend>Explicit observed-bar parameters</legend>{(Object.keys(labels) as (keyof TechnicalParameters)[]).map(name=><Field key={name} label={mode==='daily'&&['sma_n','ema_n','rsi_n'].includes(name)?name.slice(0,3).toUpperCase()+' lookback':labels[name]}><input type="number" min={name==='rsi_n'?2:1} max={10000} step={1} required value={Number.isFinite(parameters[name])?parameters[name]:''} onChange={e=>setParameters(p=>({...p,[name]:e.target.valueAsNumber}))}/></Field>)}</fieldset><button type="button" onClick={()=>setParameters(defaultTechnical)}>Reset to Defaults</button><button className="primary" disabled={busy}>{mode==='daily'?'Apply research settings':'Apply technical settings'}</button></form>

  {busy&&<p role="status">Checking coverage and calculating completed-bar technical values.</p>}{problem&&<p role="alert" className="notice warning">{problem}</p>}
  {meta&&<details><summary>Source quality and provenance</summary><ResearchQuality meta={meta}/></details>}
  <details><summary>Indicator definitions and prerequisites</summary><ul>{INDICATORS.map(i=><li key={i.id}>{i.label}: {i.description} Minimum {i.minimum(parameters)} consecutive eligible observations. A known gap restarts warm-up.</li>)}</ul><p>These are conventional research defaults. They are not optimized trading parameters.</p></details>
  {result&&<>{JSON.stringify(result.parameters)!==JSON.stringify(parameters)&&<p className="notice">Settings changed. Apply settings to recalculate. The values below use the last applied periods.</p>}<p role="status">Source: {result.source}. {result.source_qualification} | {result.timeframe} | {result.price_basis} | Freshness: {result.freshness} | {result.candles.length} completed observations; {result.warmup_bars} earlier warm-up bars. Computed: {exchangeTime(result.computed_at)}</p><p className="footnote">Current/future daily records excluded: {result.excluded_incomplete_daily_rows||0}. Forming intraday bars are excluded. Price adjustment and point-in-time source qualification remain separate. {result.warnings.join('; ')}</p>
  {!result.candles.length&&<p className="empty">No completed observations for this selection.</p>}<><FinancialChart result={result} title={mode==='daily'?instrument.symbol+' price chart':instrument.symbol+' technical price / '+result.timeframe}/>
  <h3>Exact technical values</h3><p>{Math.min(shown,result.candles.length)} of {result.candles.length} completed rows shown. Donchian excludes the current bar. MACD line may become available before signal/histogram.</p>
  <DataViewport label="Exact technical values" className="table-wrap"><table><caption>Exact OHLCV, existing indicators and Package 2B calculations</caption><thead><tr><th>Time / IST</th><th>Close / INR</th><th>Open / High / Low</th><th>Volume</th><th>SMA ({result.parameters.sma_n})</th><th>EMA ({result.parameters.ema_n})</th><th>RSI ({result.parameters.rsi_n})</th><th>ATR</th><th>MACD / signal / histogram</th><th>Prior Donchian upper / lower / middle</th><th>Classification / provenance</th></tr></thead><tbody>{result.candles.slice(0,shown).map(c=><tr key={c.time}><td>{result.timeframe==='1d'?c.time:exchangeTime(c.time)}</td><td>{c.close}</td><td>{c.open??'Unknown'} / {c.high??'Unknown'} / {c.low??'Unknown'}</td><td>{c.volume??'Unknown'}</td><td>{number(lookup('SMA',c.time))}</td><td>{number(lookup('EMA',c.time))}</td><td>{number(lookup('RSI',c.time))}</td><td>{number(lookup('ATR',c.time))}</td><td>{number(lookup('MACD',c.time),'macd')} / {number(lookup('MACD',c.time),'signal')} / {number(lookup('MACD',c.time),'histogram')}</td><td>{number(lookup('DONCHIAN',c.time),'upper')} / {number(lookup('DONCHIAN',c.time),'lower')} / {number(lookup('DONCHIAN',c.time),'middle')}</td><td>{c.classification}<small>{c.observation_id||'Provider intraday candidate'} {c.batch_id||''}</small></td></tr>)}</tbody></table></DataViewport>{shown<result.candles.length&&<button onClick={()=>setShown(n=>n+DATA_PAGE_SIZE)}>Show more technical rows</button>}</>
  </>}
 </section>;
}
