import {useEffect,useRef,useState} from 'react';
import IndicatorVisibility from './IndicatorVisibility';
import type {Dispatch,SetStateAction} from 'react';
import {useResearchPreference} from './researchPreferences';
import {createChart,createSeriesMarkers,CandlestickSeries,HistogramSeries,LineSeries,ColorType,TickMarkType,type IChartApi,type ISeriesMarkersPluginApi,type ISeriesApi,type Time,type MouseEventParams} from 'lightweight-charts';
import type {TechnicalResult} from './technicalTypes';
import {exchangeTime} from './api';
import {chartTime,coordinate,orderedCandles,lineSegments,type ForecastEndpoint} from './financialChartData';

const NO_ENDPOINTS:ForecastEndpoint[]=[];
const colors={SMA:'#356b97',EMA:'#267b67',upper:'#9d7228',lower:'#9d7228',middle:'#b5a175',RSI:'#9b79c9',MACD:'#4787b7',signal:'#d88a50',ATR:'#7e995f'};
const key=(t:Time):string=>typeof t==='number'?new Date(t*1000).toISOString():typeof t==='string'?t:`${t.year}-${String(t.month).padStart(2,'0')}-${String(t.day).padStart(2,'0')}`;
type PriceSeries=ISeriesApi<'Candlestick'>;type Line=ISeriesApi<'Line'>;
export default function LightweightResearchChart({result,endpoints=NO_ENDPOINTS,onUnavailable,visibility}:{result:TechnicalResult;endpoints?:ForecastEndpoint[];visibility?:{hidden:string[];setHidden:Dispatch<SetStateAction<string[]>>};onUnavailable?:(message:string)=>void}){
 const markerCleanup=useRef<(()=>void)|null>(null);
 const host=useRef<HTMLDivElement>(null),chart=useRef<IChartApi|null>(null),state=useRef<{candles:PriceSeries;close:Line;volume:ISeriesApi<'Histogram'>;histogram:ISeriesApi<'Histogram'>;lines:Line[]}|null>(null),identity=useRef('');
 const [selected,setSelected]=useState<string|null>(null),[problem,setProblem]=useState(''),[range,setRange]=useState(''),[theme,setTheme]=useState<'light'|'dark'>('light');
 const [storedHidden,setStoredHidden]=useResearchPreference<string[]>('chartHiddenIndicators',[]);const hidden=visibility?.hidden||storedHidden,setHidden=visibility?.setHidden||setStoredHidden;const daily=result.timeframe==='1d';const fallback=useRef(onUnavailable);fallback.current=onUnavailable;
 useEffect(()=>{
  const node=host.current;if(!node)return;let c:IChartApi|undefined,frame:number|undefined;let alive=true;
  const crosshair=(event:MouseEventParams<Time>)=>{if(frame!==undefined)cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(alive)setSelected(event.time===undefined?null:key(event.time));});};
  const visible=(value:{from:number;to:number}|null)=>{if(!alive)return;node.setAttribute('data-visible-range',value?value.from+':'+value.to:'');setRange(value?Math.max(0,Math.round(value.to-value.from))+' bars in view':'');};
  try{
   c=createChart(node,{autoSize:true,height:800,layout:{textColor:'#3a5143',background:{type:ColorType.Solid,color:'#ffffff'},attributionLogo:true},grid:{vertLines:{color:'#eef1e8'},horzLines:{color:'#eef1e8'}},timeScale:{timeVisible:!daily,secondsVisible:false,tickMarkFormatter:(t:Time,kind:TickMarkType)=>daily?key(t):new Intl.DateTimeFormat('en-IN',kind<=TickMarkType.DayOfMonth?{timeZone:'Asia/Kolkata',day:'2-digit',month:'short'}:{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(Number(t)*1000))},localization:{timeFormatter:(t:Time)=>daily?key(t):exchangeTime(key(t))},crosshair:{mode:0}});
   chart.current=c;
   const candles=c.addSeries(CandlestickSeries,{upColor:'#267b67',downColor:'#a34b3b',borderVisible:false,wickUpColor:'#267b67',wickDownColor:'#a34b3b',priceFormat:{type:'price',precision:4,minMove:.0001}},0);
   const close=c.addSeries(LineSeries,{color:'#9d7228',lineVisible:false,pointMarkersVisible:false,lastValueVisible:false,priceLineVisible:false},0);
   const volume=c.addSeries(HistogramSeries,{color:'#8caa87',priceFormat:{type:'volume'}},1);
   // Preserve the indicator panes even when all values are warming up or hidden.
   for(let i=2;i<5;i++)c.addPane(true);
   const histogram=c.addSeries(HistogramSeries,{color:'#8caa87',priceLineVisible:false},3);
   [350,85,115,130,120].forEach((h,i)=>c!.panes()[i].setHeight(h));
   c.subscribeCrosshairMove(crosshair);c.timeScale().subscribeVisibleLogicalRangeChange(visible);
   state.current={candles,close,volume,histogram,lines:[]};identity.current='';setSelected(null);setProblem('');
  }catch{setProblem('Financial chart unavailable. Exact values remain available.');fallback.current?.('Financial chart unavailable; Plotly fallback selected.');}
  // Marker detachment schedules a redraw; remove() must cancel it before canvases are disposed.
  return()=>{alive=false;if(frame!==undefined)cancelAnimationFrame(frame);markerCleanup.current?.();if(c){c.unsubscribeCrosshairMove(crosshair);c.timeScale().unsubscribeVisibleLogicalRangeChange(visible);c.remove();}chart.current=null;state.current=null;};
 },[daily]);
 useEffect(()=>{chart.current?.applyOptions({layout:{textColor:theme==='dark'?'#e4ebdf':'#3a5143',background:{type:ColorType.Solid,color:theme==='dark'?'#18241f':'#ffffff'}},grid:{vertLines:{color:theme==='dark'?'#2d3d33':'#eef1e8'},horzLines:{color:theme==='dark'?'#2d3d33':'#eef1e8'}}});},[theme,daily]);
 useEffect(()=>{
  const c=chart.current,s=state.current;if(!c||!s)return;const markers:ISeriesMarkersPluginApi<Time>[]=[];
  let detached=false;const detachMarkers=()=>{if(detached)return;detached=true;for(const marker of markers)marker.detach();if(markerCleanup.current===detachMarkers)markerCleanup.current=null;};
  markerCleanup.current=detachMarkers;
  try{
   const rows=orderedCandles(result),gaps=result.gap_times||[],seen=new Set(rows.map(r=>r.time));
   const timeline=[...rows.map(row=>({date:row.time,row})),...gaps.filter(t=>!seen.has(t)).map(date=>({date,row:null}))].sort((a,b)=>a.date.localeCompare(b.date));
   s.candles.setData(timeline.map(({date,row:r})=>r&&r.open!==null&&r.high!==null&&r.low!==null?{time:chartTime(date,daily),open:coordinate(r.open)!,high:coordinate(r.high)!,low:coordinate(r.low)!,close:coordinate(r.close)!}:{time:chartTime(date,daily)}));
   s.close.setData(rows.map(r=>({time:chartTime(r.time,daily),value:coordinate(r.close)!})));
   s.volume.setData(timeline.map(({date,row:r})=>{const v=r?.volume==null?null:coordinate(r.volume);return v!==null&&Number.isSafeInteger(v)&&v>=0?{time:chartTime(date,daily),value:v,color:r&&coordinate(r.close)!>=coordinate(r.open??r.close)!?'#7ca991':'#c58378'}:{time:chartTime(date,daily)};}));
   for(const line of s.lines)c.removeSeries(line);s.lines=[];
   const closeOnly=rows.filter(r=>r.open===null||r.high===null||r.low===null);
   if(closeOnly.length){const points=c.addSeries(LineSeries,{color:'#9d7228',lineVisible:false,pointMarkersVisible:true,pointMarkersRadius:3,lastValueVisible:false,priceLineVisible:false},0);points.setData(closeOnly.map(r=>({time:chartTime(r.time,daily),value:coordinate(r.close)!})));s.lines.push(points);}
   for(const [name,color]of Object.entries(colors)){
    const bundle=['upper','lower','middle'].includes(name)?'DONCHIAN':name==='signal'?'MACD':name;
    if(hidden.includes(bundle))continue;
    const field=['upper','lower','middle','signal'].includes(name)?name:name==='MACD'?'macd':'value';
    const pane=name==='RSI'?2:name==='MACD'||name==='signal'?3:name==='ATR'?4:0;
    for(const segment of lineSegments(result.indicators[bundle]?.values||[],field as 'value',daily,gaps)){
     const line=c.addSeries(LineSeries,{color,lineWidth:1,priceLineVisible:false,lastValueVisible:false,pointMarkersVisible:segment.length===1,...(name==='RSI'?{autoscaleInfoProvider:()=>({priceRange:{minValue:0,maxValue:100}})}:{})},pane);line.setData(segment);s.lines.push(line);
     if(name==='RSI'){line.createPriceLine({price:0,color:'#8d9290',lineWidth:1,axisLabelVisible:false});line.createPriceLine({price:100,color:'#8d9290',lineWidth:1,axisLabelVisible:false});}
    }
   }
   s.histogram.setData(hidden.includes('MACD')?[]:(result.indicators.MACD?.values||[]).map(v=>typeof v.histogram==='string'?{time:chartTime(v.time,daily),value:coordinate(v.histogram)!,color:coordinate(v.histogram)!>=0?'#7ca991':'#c58378'}:{time:chartTime(v.time,daily)}));
   // Each forecast is a single endpoint. Never connect it into an invented path.
   for(const [index,e]of endpoints.entries()){
    if(e.model==='B03')continue;const line=c.addSeries(LineSeries,{color:e.model==='B01'?'#ae7923':'#588dba',lineVisible:false,pointMarkersVisible:true,pointMarkersRadius:6,lastValueVisible:false,priceLineVisible:false},0);
    line.setData([{time:chartTime(e.target,daily),value:coordinate(e.price)!}]);s.lines.push(line);
    markers.push(createSeriesMarkers(line,[{time:chartTime(e.target,daily),position:'aboveBar',shape:'circle',color:e.model==='B01'?'#ae7923':'#588dba',text:e.model+' endpoint'}]));
    if(index===0&&rows.some(r=>r.time===e.origin))markers.push(createSeriesMarkers(s.close,[{time:chartTime(e.origin,daily),position:'belowBar',shape:'arrowUp',color:'#9b79c9',text:'Forecast origin'}]));
    if(e.actual!=null){const actual=c.addSeries(LineSeries,{color:'#267b67',lineVisible:false,pointMarkersVisible:true,pointMarkersRadius:4,lastValueVisible:false,priceLineVisible:false},0);actual.setData([{time:chartTime(e.target,daily),value:coordinate(e.actual)!}]);s.lines.push(actual);}
   }
   const next=result.instrument_id+'|'+result.timeframe;if(identity.current!==next){c.timeScale().fitContent();identity.current=next;setSelected(null);}setProblem('');
   host.current?.setAttribute('data-ready','true');host.current?.setAttribute('data-bars',String(rows.length));
  }catch{setProblem('Chart data could not be rendered safely. Exact values remain available.');fallback.current?.('Financial chart rejected the data; Plotly fallback selected.');}
  return detachMarkers;
 },[result,endpoints,hidden,daily]);
 const current=result.candles.find(r=>daily?r.time===selected:new Date(r.time).toISOString()===selected);
 function zoom(factor:number){const scale=chart.current?.timeScale(),v=scale?.getVisibleLogicalRange();if(!scale||!v)return;const mid=(v.from+v.to)/2,half=(v.to-v.from)*factor/2;scale.setVisibleLogicalRange({from:mid-half,to:mid+half});}
 return <figure className="research-figure lightweight-research" data-theme={theme}><div className="range-bar"><button onClick={()=>zoom(.7)}>Zoom in chart</button><button onClick={()=>zoom(1.4)}>Zoom out chart</button><button onClick={()=>chart.current?.timeScale().fitContent()}>Reset chart range</button><label>Chart theme<select aria-label="Chart theme" value={theme} onChange={e=>setTheme(e.target.value as 'light'|'dark')}><option value="light">Light</option><option value="dark">Dark</option></select></label><span role="status">{range}</span></div>
  {!visibility&&<IndicatorVisibility result={result} hidden={hidden} setHidden={setHidden}/>}
  <div ref={host} role="img" aria-label={result.symbol+' Lightweight '+result.timeframe+' candlestick chart'} className="lightweight-canvas"/>
  {!result.candles.length&&<p className="empty">No completed price observations to chart.</p>}
  {result.candles.some(r=>r.open===null||r.high===null||r.low===null)&&<p className="notice warning">Some observations have close only. Missing OHLC is not fabricated; exact close points remain visible.</p>}
  <p className="footnote">Shared time scale and crosshair. Pan by dragging; wheel/pinch to zoom. Panes: price, volume, RSI (0?100 reference), MACD and ATR. Intraday times are IST. Gaps and unavailable indicators are not interpolated. Coordinates are approximate; exact server values remain authoritative.</p>
  <div className="notice" aria-live="polite">{current?<>{daily?current.time:exchangeTime(current.time)} | O {current.open??'Unavailable'} H {current.high??'Unavailable'} L {current.low??'Unavailable'} C {current.close} V {current.volume??'Unavailable'} | {current.classification}</>:'Move the crosshair over a candle for exact OHLCV.'}</div>
  {endpoints.filter(e=>e.model!=='B03').map((e,i)=><p key={e.model+i} className="forecast-endpoint">{e.model} | origin {e.origin} | target {e.target} | endpoint {e.price} | cutoff {exchangeTime(e.cutoff)} | {e.status} {e.mode} {e.qualification}{e.actual!=null?' | actual '+e.actual+' | signed error '+(e.error??'Unavailable'):''}</p>)}
  {problem&&<p role="alert">{problem}</p>}
  <figcaption>TradingView Lightweight Charts, copyright 2025 TradingView, Inc. <a href="https://www.tradingview.com/" target="_blank" rel="noopener noreferrer">TradingView</a> | <a href="/licenses/lightweight-charts-NOTICE.txt">Attribution notice</a> | <a href="/licenses/lightweight-charts-LICENSE.txt">Apache 2.0 license</a> | <a href="/licenses/fancy-canvas-LICENSE.txt">fancy-canvas MIT notice</a>. Local application data; no TradingView market-data connection.</figcaption>
 </figure>;
}
