import type {Time, UTCTimestamp} from 'lightweight-charts';
import type {TechnicalCandle, TechnicalResult, TechnicalValue} from './technicalTypes';

export interface ForecastEndpoint {model:string; origin:string; target:string; price:string; cutoff:string; status:string; actual?:string|null; error?:string|null; mode?:string; qualification?:string}
export function chartTime(value:string,daily:boolean):Time {
 if(daily){if(!/^\d{4}-\d{2}-\d{2}$/.test(value)||!Number.isFinite(Date.parse(value+'T00:00:00Z'))||new Date(value+'T00:00:00Z').toISOString().slice(0,10)!==value)throw Error('Invalid session date');return value;}
 if(!/(Z|[+-]\d{2}:\d{2})$/.test(value))throw Error('Timezone required');
 const n=Date.parse(value)/1000;if(!Number.isSafeInteger(n))throw Error('Invalid timestamp');return n as UTCTimestamp;
}
export function coordinate(value:string|null|undefined):number|null {if(value==null)return null;const n=Number(value);if(!value.trim()||!Number.isFinite(n))throw Error('Invalid numeric coordinate');return n;}
function chronological(a:string,b:string,daily:boolean){return daily?a.localeCompare(b):Number(chartTime(a,false))-Number(chartTime(b,false));}
export function orderedCandles(result:TechnicalResult):TechnicalCandle[]{
 const daily=result.timeframe==='1d',rows=[...result.candles].sort((a,b)=>chronological(a.time,b.time,daily)),seen=new Set<string>();
 for(const r of rows){const t=String(chartTime(r.time,daily));if(seen.has(t))throw Error('Duplicate chart timestamp');seen.add(t);const c=coordinate(r.close),o=coordinate(r.open),h=coordinate(r.high),l=coordinate(r.low);if(c===null||c<=0||[o,h,l].some(x=>x!==null&&x<=0))throw Error('Invalid price');if(o!==null&&h!==null&&l!==null&&(l>Math.min(o,c)||h<Math.max(o,c)))throw Error('Invalid OHLC');}
 return rows;
}
// These are display segments only. Canonical financial calculations stay in the backend.
export function lineSegments(values:TechnicalValue[],field:keyof TechnicalValue,daily:boolean,gaps:string[]=[]){
 const sorted=[...values].sort((a,b)=>chronological(a.time,b.time,daily));const times=new Set<string>();const segments:{time:Time;value:number}[][]=[];let part:{time:Time;value:number}[]=[];let previous='';
 for(const row of sorted){const time=chartTime(row.time,daily),key=String(time);if(times.has(key))throw Error('Duplicate indicator timestamp');times.add(key);const raw=row[field],value=typeof raw==='string'?coordinate(raw):null;
  if(row.break_before||value===null||gaps.some(g=>previous&&chronological(previous,g,daily)<0&&chronological(g,row.time,daily)<=0)){if(part.length)segments.push(part);part=[];}
  if(value!==null)part.push({time,value});previous=row.time;
 }if(part.length)segments.push(part);return segments;
}
