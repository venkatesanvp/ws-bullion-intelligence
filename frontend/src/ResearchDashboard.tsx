import TechnicalWorkbench from './TechnicalWorkbench';
import ForecastingResearch from './ForecastingResearch';
import ReconciliationPanel from './ReconciliationPanel';
import MarketSnapshot from './MarketSnapshot';
import IntradayDashboard from './IntradayDashboard';
import {useState} from 'react';
import {useResearchPreference} from './researchPreferences';
import {type Call,type Instrument,type Source,canResearch,supportsMarketSession} from './api';
import {ChartBoundary} from './ResearchShared';
export default function ResearchDashboard(props:{api:Call;instrument?:Instrument;source?:Source;basis:string}) {
 const [view,setView]=useResearchPreference<'daily'|'intraday'|'technical'|'forecast'>('researchView','daily');
 const [revision,setRevision]=useState(0),[marketOpen,setMarketOpen]=useState(false);
 const valid=!!props.instrument&&!!props.source&&canResearch(props.source),session=valid&&supportsMarketSession(props.source!);
 const identity=[props.instrument?.id,props.source?.id,props.basis,revision].join('|');
 const context=valid&&session?<><ChartBoundary key={'snapshot'+props.source!.id} label="Market snapshot"><MarketSnapshot api={props.api} synthetic={props.source!.profile.data_class==='SYNTHETIC_TEST'} onReconciliation={()=>setRevision(r=>r+1)}/></ChartBoundary><ChartBoundary label="Reconciliation"><ReconciliationPanel api={props.api} instrument={props.instrument!} onChange={()=>setRevision(r=>r+1)}/></ChartBoundary></>:<p className="empty">Select a supported ETF and permitted DhanHQ source to view market snapshots. Daily research remains available for permitted CSV sources.</p>;
 return <div className="research-dashboard"><section aria-label="DhanHQ Market Snapshot and reconciliation">{view==='daily'||view==='intraday'?context:<details className="card" open={marketOpen} onToggle={e=>setMarketOpen(e.currentTarget.open)}><summary>DhanHQ Market Snapshot and reconciliation (optional live quotes)</summary><p>Open to inspect live context. Closed sections do not poll or download quotes.</p>{marketOpen&&context}</details>}</section>
 <div className="range-bar" role="group" aria-label="Research timeframe">{(['daily','intraday','technical','forecast'] as const).map(id=><button key={id} aria-pressed={view===id} onClick={()=>setView(id)}>{({daily:'Daily research',intraday:'Intraday research',technical:'Technical analytics',forecast:'Forecasting Research'})[id]}</button>)}</div>
 <a href="/user-guide.html" target="_blank" rel="noopener noreferrer">Research user guide</a>
 {!valid?<div className="empty" role="status">Select an ETF and a source permitted for research. Review source qualification if access is restricted.</div>:<ChartBoundary key={identity+view} label="Selected research view">{view==='forecast'?session?<ForecastingResearch api={props.api} instrument={props.instrument!} source={props.source!} basis={props.basis}/>:<p>Forecasting requires a supported DhanHQ or synthetic source.</p>:view==='technical'?<TechnicalWorkbench api={props.api} instrument={props.instrument!} source={props.source!} basis={props.basis}/>:view==='daily'?<TechnicalWorkbench mode="daily" api={props.api} instrument={props.instrument!} source={props.source!} basis={props.basis}/>:session?<IntradayDashboard api={props.api} instrument={props.instrument!} synthetic={props.source!.profile.data_class==='SYNTHETIC_TEST'}/>:<p>Intraday research requires a supported market source.</p>}</ChartBoundary>}
 </div>;
}
