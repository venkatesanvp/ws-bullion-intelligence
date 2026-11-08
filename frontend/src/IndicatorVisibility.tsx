import type {Dispatch,SetStateAction} from 'react';
import type {TechnicalResult} from './technicalTypes';
import {INDICATORS} from './indicatorCatalog';
export default function IndicatorVisibility({result,hidden,setHidden}:{result:TechnicalResult;hidden:string[];setHidden:Dispatch<SetStateAction<string[]>>}){
 return <fieldset className="chart-indicators"><legend>Visible chart indicators</legend>{INDICATORS.map(i=>{const b=result.indicators[i.id],ready=!!b?.values.some(v=>v.value!=null||v.macd!=null||v.upper!=null);return <label className="check" key={i.id}><input aria-label={i.id} type="checkbox" disabled={!ready} checked={!!b&&!hidden.includes(i.id)} onChange={e=>setHidden(old=>e.target.checked?old.filter(x=>x!==i.id):[...old,i.id])}/>{i.label}<small>{i.description} Minimum {i.minimum(result.parameters)} consecutive eligible observations. {!ready?'Not currently calculable: check completed history, gaps and required fields.':'Calculated by the backend.'}</small></label>;})}</fieldset>;
}
