import {useEffect,useRef,useState} from 'react';
import {Call,Instrument,Reconciliation,SessionPolicy} from './api';

export default function ReconciliationPanel({api,instrument,onChange}:{api:Call;instrument:Instrument;onChange:()=>void}){
  const [day,setDay]=useState(''),[result,setResult]=useState<Reconciliation|null>(null),[problem,setProblem]=useState(''),[busy,setBusy]=useState(false);
  const callback=useRef(onChange);callback.current=onChange;
  useEffect(()=>{const cancel=new AbortController();void api<SessionPolicy>('/market-data/session-policy',{signal:cancel.signal}).then(x=>setDay(x.data.today)).catch(()=>{});return()=>cancel.abort();},[api]);
  useEffect(()=>{setResult(null);},[instrument.id,day]);
  async function reconcile(){if(!day||busy)return;setBusy(true);setProblem('');try{
    const r=await api<Reconciliation>('/market-data/reconcile',{method:'POST',body:JSON.stringify({instrument_id:instrument.id,session_date:day,interval:5})});
    setResult(r.data);if(r.data.classification==='HISTORICAL_FINAL')callback.current();
  }catch{setProblem('Reconciliation unavailable. Select a reviewed session and check local diagnostics.');}finally{setBusy(false);}}
  // Active-view publication checks retain the selected session across midnight.
  // Existing daily negative-cache/backoff prevents repeated provider requests.
  const check=useRef(reconcile);check.current=reconcile;
  useEffect(()=>{if(!result||result.classification==='HISTORICAL_FINAL')return;const timer=setInterval(()=>{if(document.visibilityState==='visible')void check.current();},60000);return()=>clearInterval(timer);},[result]);
  return <section className="card" aria-label="Daily reconciliation"><h3>Daily / intraday reconciliation</h3><p>Validated provider daily observations supersede the provisional presentation. Source qualification and adjustment compatibility remain open. Quotes and stream ticks never enter daily indicators.</p>
    <label>Reconciliation session<input type="date" value={day} onChange={e=>setDay(e.target.value)}/></label><button disabled={!day||busy} onClick={()=>void reconcile()}>{busy?'Checking publication...':'Reconcile selected session'}</button>
    {problem&&<p role="alert">{problem}</p>}{result&&<div role="status"><p>{result.symbol} / {result.session_date}: {result.classification}. {result.publication_state}</p><p>Provisional: {result.provisional_disposition}; {result.provisional_coverage} ({result.provisional_bar_count} bars). {result.comparison_status}</p><p>Fields requiring review: {result.differing_fields.join(', ')||'None identified / insufficient evidence'}. Provider requests: {result.requests}.</p><p>{result.error||''} {result.source_qualification}</p><details><summary>Reconciliation limitations</summary>{result.warnings.join('; ')}</details></div>}
  </section>;
}
