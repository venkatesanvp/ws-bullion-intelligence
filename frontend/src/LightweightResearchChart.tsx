import {useEffect,useRef,useState} from 'react';
import {createChart,CandlestickSeries,HistogramSeries,LineSeries,TickMarkType,type IChartApi,type ISeriesApi,type Time,type UTCTimestamp,type MouseEventParams} from 'lightweight-charts';
import {TechnicalResult,TechnicalValue} from './technicalTypes';
import {exchangeTime} from './api';

type Series=ISeriesApi<'Line'>;
const colors={SMA:'#356b97',EMA:'#267b67',upper:'#9d7228',lower:'#9d7228',middle:'#b5a175'};
const time=(value:string,daily:boolean):Time=>daily?value:(Date.parse(value)/1000 as UTCTimestamp);
function key(value:Time):string {if(typeof value==='number')return new Date(value*1000).toISOString();if(typeof value==='string')return value;return `${value.year}-${String(value.month).padStart(2,'0')}-${String(value.day).padStart(2,'0')}`;}

export default function LightweightResearchChart({result}:{result:TechnicalResult}){
 const host=useRef<HTMLDivElement>(null),chart=useRef<IChartApi|null>(null),series=useRef<{candles:ISeriesApi<'Candlestick'>;volume:ISeriesApi<'Histogram'>;lines:Record<string,Series>;histogram:ISeriesApi<'Histogram'>}|null>(null),fitted=useRef(false);
 const [selected,setSelected]=useState<string|null>(null),[problem,setProblem]=useState(''),[range,setRange]=useState('');
 const daily=result.timeframe==='1d';
 useEffect(()=>{
  const node=host.current;if(!node)return;
  let frame:number|undefined;
  try{
   const c=createChart(node,{autoSize:true,height:800,layout:{textColor:'#3a5143',background:{color:'#ffffff'},attributionLogo:true},grid:{vertLines:{color:'#eef1e8'},horzLines:{color:'#eef1e8'}},timeScale:{timeVisible:!daily,secondsVisible:false,tickMarkFormatter:(t:Time,kind:TickMarkType)=>daily?key(t):new Intl.DateTimeFormat('en-IN',kind<=TickMarkType.DayOfMonth?{timeZone:'Asia/Kolkata',day:'2-digit',month:'short'}:{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(Number(t)*1000))},localization:{timeFormatter:(t:Time)=>daily?key(t):exchangeTime(key(t))},crosshair:{mode:0}});
   chart.current=c;
   const candles=c.addSeries(CandlestickSeries,{upColor:'#267b67',downColor:'#a34b3b',borderVisible:false,wickUpColor:'#267b67',wickDownColor:'#a34b3b',priceFormat:{type:'price',precision:4,minMove:.0001}},0);
   const volume=c.addSeries(HistogramSeries,{color:'#afbd9e',priceFormat:{type:'volume'}},1);
   const lines:Record<string,Series>={};
   for(const [name,color]of Object.entries(colors))lines[name]=c.addSeries(LineSeries,{color,lineWidth:1,priceLineVisible:false,lastValueVisible:false},0);
   lines.RSI=c.addSeries(LineSeries,{color:'#7958a8',lineWidth:1},2);
   lines.MACD=c.addSeries(LineSeries,{color:'#356b97',lineWidth:1},3);lines.signal=c.addSeries(LineSeries,{color:'#bd713b',lineWidth:1},3);
   const histogram=c.addSeries(HistogramSeries,{color:'#a8b89e'},3);
   lines.ATR=c.addSeries(LineSeries,{color:'#576846',lineWidth:1},4);
   c.panes()[0].setHeight(350);c.panes()[1].setHeight(85);c.panes()[2].setHeight(115);c.panes()[3].setHeight(130);c.panes()[4].setHeight(120);
   const crosshair=(event:MouseEventParams<Time>)=>{if(frame!==undefined)cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>setSelected(event.time===undefined?null:key(event.time)));};
   c.subscribeCrosshairMove(crosshair);c.timeScale().subscribeVisibleLogicalRangeChange(value=>{node.setAttribute('data-visible-range',value?String(value.from)+':'+String(value.to):'');setRange(value?Math.max(0,Math.round(value.to-value.from))+' bars in view':'');});
   series.current={candles,volume,lines,histogram};fitted.current=false;
   return()=>{if(frame!==undefined)cancelAnimationFrame(frame);c.unsubscribeCrosshairMove(crosshair);c.remove();chart.current=null;series.current=null;};
  }catch{chart.current?.remove();chart.current=null;series.current=null;setProblem('Parity renderer unavailable. Existing charts and exact values remain available.');}
 },[daily]);
 useEffect(()=>{
  const s=series.current,c=chart.current;if(!s||!c)return;
  try{
   const missing=new Set(result.gap_times||[]),rows=[...result.candles.map(r=>({date:r.time,row:r})),...Array.from(missing).filter(t=>!result.candles.some(r=>r.time===t)).map(t=>({date:t,row:null}))].sort((a,b)=>a.date.localeCompare(b.date));
   s.candles.setData(rows.map(({date,row})=>row&&row.open!==null&&row.high!==null&&row.low!==null?{time:time(date,daily),open:Number(row.open),high:Number(row.high),low:Number(row.low),close:Number(row.close)}:{time:time(date,daily)}));
   s.volume.setData(rows.map(({date,row})=>row?.volume!==null&&row?.volume!==undefined&&Number.isSafeInteger(Number(row.volume))?{time:time(date,daily),value:Number(row.volume)}:{time:time(date,daily)}));
   const values=(name:string,field:keyof TechnicalValue='value')=>(result.indicators[name]?.values||[]).map(v=>{const value=v[field];return typeof value==='string'&&!v.break_before?{time:time(v.time,daily),value:Number(value)}:{time:time(v.time,daily)};});
   for(const name of ['SMA','EMA','RSI','ATR'])s.lines[name].setData(values(name));
   for(const field of ['upper','lower','middle'] as const)s.lines[field].setData(values('DONCHIAN',field));
   s.lines.MACD.setData(values('MACD','macd'));s.lines.signal.setData(values('MACD','signal'));s.histogram.setData(values('MACD','histogram'));
   if(!fitted.current){c.timeScale().fitContent();fitted.current=true;}
   setProblem('');
  }catch{setProblem('Parity renderer rejected this dataset. Existing charts and exact values remain available.');}
 },[result,daily]);
 const current=result.candles.find(r=>daily?r.time===selected:new Date(r.time).toISOString()===selected);
 function zoom(factor:number){const scale=chart.current?.timeScale(),visible=scale?.getVisibleLogicalRange();if(!scale||!visible)return;const middle=(visible.from+visible.to)/2,half=(visible.to-visible.from)*factor/2;scale.setVisibleLogicalRange({from:middle-half,to:middle+half});}
 return <figure className="research-figure lightweight-research"><div className="range-bar"><button onClick={()=>zoom(.7)}>Zoom in chart</button><button onClick={()=>zoom(1.4)}>Zoom out chart</button><button onClick={()=>chart.current?.timeScale().fitContent()}>Reset chart range</button><span role="status">{range}</span></div>
  <div ref={host} role="img" aria-label={result.symbol+' Lightweight '+result.timeframe+' candlestick chart'} className="lightweight-canvas"/>
  <p className="footnote">Pane order: price with SMA/EMA and prior Donchian; volume; Wilder RSI; MACD/signal/histogram; ATR. Crosshair is shared across panes. Drag to pan; wheel/pinch to zoom. Time labels are IST for intraday. Rendering coordinates are approximate; exact server values are below.</p>
  <div className="notice" aria-live="polite">{current?<>{daily?current.time:exchangeTime(current.time)} | O {current.open??'Unavailable'} H {current.high??'Unavailable'} L {current.low??'Unavailable'} C {current.close} V {current.volume??'Unavailable'} | {current.classification}</>:'Move the crosshair over a candle for exact OHLCV.'}</div>
  {problem&&<p role="alert">{problem}</p>}
  <figcaption>TradingView Lightweight Charts, copyright 2025 TradingView, Inc. <a href="https://www.tradingview.com/" target="_blank" rel="noopener noreferrer">TradingView</a> | <a href="/licenses/lightweight-charts-NOTICE.txt">Attribution notice</a> | <a href="/licenses/lightweight-charts-LICENSE.txt">Apache 2.0 license</a> | <a href="/licenses/fancy-canvas-LICENSE.txt">fancy-canvas MIT notice</a>. Local application data; no TradingView market-data connection.</figcaption>
 </figure>;
}
