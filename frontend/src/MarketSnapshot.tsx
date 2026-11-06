import { useEffect, useRef, useState } from 'react';
import { Call, exchangeTime, marketProblem, QuoteSnapshot } from './api';

export default function MarketSnapshot({api,synthetic=false}:{api:Call;synthetic?:boolean}) {
  const [snapshot,setSnapshot]=useState<QuoteSnapshot|null>(null),[busy,setBusy]=useState(false),[problem,setProblem]=useState('');
  const refresh=useRef<(force:boolean)=>void>(()=>{});
  useEffect(()=>{
    let active=true,timer:ReturnType<typeof setTimeout>|undefined,inFlight=false;
    const controller=new AbortController();
    async function load(force=false) {
      if(!active||inFlight)return;
      if(timer)clearTimeout(timer);
      if(document.visibilityState==='hidden'&&!force){timer=setTimeout(()=>void load(),60000);return;}
      inFlight=true;setBusy(true);setProblem('');
      let next=15000;
      try {
        const result=await api<QuoteSnapshot>('/market-data/quotes',{method:'POST',body:JSON.stringify({refresh:force}),signal:controller.signal});
        if(active){setSnapshot(result.data);setProblem(marketProblem(result.data.error));}
        next=(result.data.policy.auto_quote_refresh_seconds||60)*1000;
        if(!result.data.policy.enabled||!result.data.policy.quotes_enabled)next=0;
      }catch(error){if(active&&!controller.signal.aborted)setProblem(error instanceof Error?error.message:'Quote service unavailable.');next=60000;}
      finally{inFlight=false;if(active){setBusy(false);if(next)timer=setTimeout(()=>void load(),next);}}
    }
    refresh.current=force=>void load(force);
    const visibility=()=>{if(document.visibilityState==='visible')void load();};
    document.addEventListener('visibilitychange',visibility);void load();
    return()=>{active=false;controller.abort();if(timer)clearTimeout(timer);document.removeEventListener('visibilitychange',visibility);};
  },[api]);
  return <section className="card market-snapshot" aria-label="ETF market snapshot">
    <div className="card-title"><div><div className="eyebrow">{synthetic?'SYNTHETIC TEST DATA':'DHANHQ MARKET SNAPSHOT'}</div><h2>Latest available ETF quotes</h2></div><button disabled={busy} onClick={()=>refresh.current(true)}>{busy?'Refreshing quotes...':'Refresh quotes'}</button></div>
    <p>Live quotes are provisional market snapshots. They are separate from finalized daily history. All times below are Asia/Kolkata.</p>
    {problem&&<p role="alert" className="notice warning">{problem}</p>}
    {busy&&<p role="status">Retrieving one batched market snapshot.</p>}
    {snapshot&&<><p role="status">Session: {snapshot.policy.session_state}. Automatic refresh: {snapshot.policy.auto_quote_refresh_seconds ? snapshot.policy.auto_quote_refresh_seconds+' seconds while visible':'paused outside the reviewed regular session'}. Source: {snapshot.source}. Transient memory.</p>
      <div className="quote-grid">{snapshot.quotes.map(q=><article className="quote-card" key={q.instrument_id}>
        <h3>{q.listing.symbol}</h3><p>{q.name}</p><strong className="quote-price">{q.last_price??'Unavailable'} {q.listing.currency}</strong>
        <p>Change: {q.absolute_change??'Unavailable'} / {q.percent_change===null||q.percent_change===undefined?'Unavailable':q.percent_change+'%'}</p>
        <p className="notice">{q.freshness} | {q.market_session||snapshot.policy.session_state}</p>
        <dl className="quote-fields"><div><dt>Session open</dt><dd>{q.open??'Unavailable'}</dd></div><div><dt>High</dt><dd>{q.high??'Unavailable'}</dd></div><div><dt>Low</dt><dd>{q.low??'Unavailable'}</dd></div><div><dt>Previous close</dt><dd>{q.previous_close??'Unavailable'}</dd></div><div><dt>Volume</dt><dd>{q.volume??'Unavailable'}</dd></div><div><dt>Last trade</dt><dd>{exchangeTime(q.last_trade_at)}</dd></div><div><dt>Last successful retrieval</dt><dd>{exchangeTime(q.retrieved_at)}</dd></div></dl>
        <details><summary>Quote interpretation</summary><p>Previous-close basis: {q.previous_close_basis||'UNAVAILABLE'}. Provider close is not assumed to be today's final close. Last-trade time is not quote-generation time.</p><p>{q.warnings?.join('; ')}</p></details>
      </article>)}</div></>}
  </section>;
}
