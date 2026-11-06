import { useCallback, useEffect, useRef, useState } from 'react';
import { Call, exchangeTime, Instrument, IntradayResult, marketProblem, SessionPolicy } from './api';
import IntradayChart from './IntradayChart';

type Draft={interval:number;preset:string;start:string;end:string;SMA:boolean;EMA:boolean;RSI:boolean;smaN:string;emaN:string;rsiN:string};
const initial:Draft={interval:5,preset:'current',start:'',end:'',SMA:true,EMA:false,RSI:false,smaN:'20',emaN:'37',rsiN:'14'};
export default function IntradayDashboard({api,instrument,synthetic=false}:{api:Call;instrument:Instrument;synthetic?:boolean}){
  const [draft,setDraft]=useState(initial),[loaded,setLoaded]=useState<IntradayResult|null>(null),[busy,setBusy]=useState(false),[problem,setProblem]=useState(''),[shown,setShown]=useState(100);
  const generation=useRef(0),abort=useRef<AbortController|null>(null),inFlight=useRef(false),applied=useRef<Draft>(initial);
  const load=useCallback(async(settings:Draft,refresh=false)=>{
    const current=++generation.current;abort.current?.abort();const controller=new AbortController();abort.current=controller;
    const indicators:Record<string,number>={};
    for(const method of ['SMA','EMA','RSI'] as const){
      if(!settings[method])continue;const raw=settings[method==='SMA'?'smaN':method==='EMA'?'emaN':'rsiN'];
      const n=Number(raw);if(!/^\d+$/.test(raw)||!Number.isSafeInteger(n)||n<(method==='RSI'?2:1)||n>10000){setProblem('Enter supported explicit observed-bar indicator lookbacks.');return;}indicators[method]=n;
    }
    setBusy(true);inFlight.current=true;setProblem('');
    try{
      const response=await api<IntradayResult>('/market-data/intraday',{method:'POST',signal:controller.signal,body:JSON.stringify({instrument_id:instrument.id,interval:settings.interval,preset:settings.preset,start:settings.start||null,end:settings.end||null,indicators,refresh})});
      if(current!==generation.current||controller.signal.aborted)return;
      setProblem(marketProblem(response.data.error));
      if(response.data.candles.length||!response.data.error){setLoaded(response.data);applied.current={...settings};setShown(100);}
    }catch(error){if(current===generation.current&&!controller.signal.aborted)setProblem(error instanceof Error?error.message:'Intraday data unavailable.');}
    finally{if(current===generation.current){setBusy(false);inFlight.current=false;}}
  },[api,instrument.id]);
  useEffect(()=>{void load(initial);return()=>{++generation.current;abort.current?.abort();};},[load]);
  useEffect(()=>{
    let active=true;const controller=new AbortController();let timer:ReturnType<typeof setInterval>|undefined;
    void api<SessionPolicy>('/market-data/session-policy',{signal:controller.signal}).then(({data})=>{
      if(!active||!data.enabled||!data.intraday_enabled)return;
      timer=setInterval(()=>{
        if(document.visibilityState==='hidden'||inFlight.current||applied.current.preset!=='current')return;
        void api<SessionPolicy>('/market-data/session-policy',{signal:controller.signal}).then(({data:policy})=>{if(active&&policy.session_state==='OPEN'&&!inFlight.current)void load(applied.current);}).catch(()=>{});
      },data.intraday_refresh_seconds*1000);
    }).catch(()=>{});
    return()=>{active=false;controller.abort();if(timer)clearInterval(timer);};
  },[api,load]);
  function edit<K extends keyof Draft>(key:K,value:Draft[K]){setDraft(old=>({...old,[key]:value}));}
  return <section className="card" aria-label="Intraday research">
    <div className="eyebrow">{synthetic?'SYNTHETIC TEST DATA':'DHANHQ INTRADAY RESEARCH'}</div><h2>{instrument.symbol} intraday research</h2>
    <p>Daily and intraday indicators are separate. Completed intraday bars feed indicators; forming bars stay provisional. All timestamps below are IST.</p>
    <form onSubmit={e=>{e.preventDefault();void load(draft);}}>
      <div className="range-bar"><label>Intraday interval<select value={draft.interval} onChange={e=>edit('interval',Number(e.target.value))}>{[1,5,15,25,60].map(n=><option key={n} value={n}>{n} minute{n===1?'':'s'}</option>)}</select></label>
        <label>Intraday period<select value={draft.preset} onChange={e=>edit('preset',e.target.value)}><option value="current">Current session</option><option value="previous">Previous trading session</option><option value="five">Last five trading sessions</option><option value="thirty">Last 30 calendar days</option><option value="custom">Custom date range</option></select></label>
        {draft.preset==='custom'&&<><label>Intraday from<input type="date" required value={draft.start} onChange={e=>edit('start',e.target.value)}/></label><label>Intraday through<input type="date" required value={draft.end} onChange={e=>edit('end',e.target.value)}/></label></>}
      </div>
      <fieldset className="indicator-controls"><legend>Indicators on the selected intraday timeframe</legend>{(['SMA','EMA','RSI'] as const).map(method=><div key={method}><label className="check"><input type="checkbox" checked={draft[method]} onChange={e=>edit(method,e.target.checked)}/>Intraday {method==='RSI'?'Wilder RSI':method}</label><label>Intraday {method} lookback<input type="number" min={method==='RSI'?2:1} max="10000" disabled={!draft[method]} value={draft[method==='SMA'?'smaN':method==='EMA'?'emaN':'rsiN']} onChange={e=>edit(method==='SMA'?'smaN':method==='EMA'?'emaN':'rsiN',e.target.value)}/></label></div>)}</fieldset>
      <button className="primary" disabled={busy}>{busy?'Loading intraday...':'Apply intraday range'}</button><button type="button" disabled={busy} onClick={()=>void load(draft,true)}>Refresh intraday</button>
    </form>
    {busy&&<p role="status">Checking intraday coverage and retrieving missing candles.</p>}{problem&&<p role="alert" className="notice warning">{problem}</p>}
    {loaded&&<><p role="status">{loaded.status} | {loaded.candles.length} observed {loaded.interval_minutes}-minute candles | {loaded.requested_period.start} through {loaded.requested_period.end} | {loaded.freshness} | {loaded.market_session}</p>
      <p>Latest candle: {exchangeTime(loaded.latest_provider_timestamp)}. Last successful retrieval: {exchangeTime(loaded.last_successful_retrieval)}. Missing completed candles: {loaded.missing_completed_candles}. {loaded.calendar_unassessed?'Calendar coverage unassessed.':''} Earlier completed warm-up bars: {loaded.warmup_bars}.</p>
      {!loaded.candles.length?<p className="empty">No intraday observations are currently available. This does not establish a holiday or guarantee provider availability.</p>:<IntradayChart result={loaded}/>}
      {loaded.provisional_session&&<section className="notice warning"><h3>{loaded.provisional_session.classification}</h3><p>{loaded.provisional_session.session_date}: O {loaded.provisional_session.open} | H {loaded.provisional_session.high} | L {loaded.provisional_session.low} | latest observed C {loaded.provisional_session.close} | volume {loaded.provisional_session.volume}</p><p>{loaded.provisional_session.coverage}. This is not the official finalized daily candle.</p></section>}
      <details><summary>Intraday data quality and interpretation</summary><p>{loaded.warnings.join('; ')}</p><p>Provider: {loaded.source}. Revision: {loaded.revision}. Adjustment basis unqualified; no total-return or replay claim. Data lives in bounded backend memory and is lost on restart.</p></details>
      <div className="table-wrap"><table><caption>Exact {loaded.interval_minutes}-minute OHLCV and indicator values</caption><thead><tr><th>Candle start / end (IST)</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>{Object.entries(loaded.indicators).map(([m,v])=><th key={m}>{m} {v.n} / {v.timeframe}</th>)}<th>Classification</th></tr></thead><tbody>{loaded.candles.slice(0,shown).map(row=><tr key={row.start}><td>{exchangeTime(row.start)}<small>{exchangeTime(row.end)}</small></td><td>{row.open}</td><td>{row.high}</td><td>{row.low}</td><td>{row.close}</td><td>{row.volume}</td>{Object.entries(loaded.indicators).map(([m,v])=>{const value=v.values.find(x=>x.candle_start===row.start);return <td key={m}>{value?.value??('Unavailable: '+(value?.reason||'PROVISIONAL_OR_WARMUP'))}</td>;})}<td>{row.classification}</td></tr>)}</tbody></table></div>
      {shown<loaded.candles.length&&<button onClick={()=>setShown(n=>n+100)}>Show more intraday rows</button>}
    </>}
  </section>;
}
