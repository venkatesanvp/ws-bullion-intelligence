import { useMemo } from 'react';
import { exchangeTime, IntradayResult } from './api';

export default function IntradayChart({result}:{result:IntradayResult}) {
  const rows=result.candles.slice(-500);
  const width=1100,left=85,right=25,top=30,bottom=355,volumeTop=400,volumeBottom=505;
  const series=Object.entries(result.indicators).filter(([key])=>key!=='RSI');
  const prepared=useMemo(()=>{
    const numbers=rows.flatMap(r=>[Number(r.low),Number(r.high)]);
    for(const [,s]of series)for(const v of s.values)if(v.value!==null&&rows.some(r=>r.start===v.candle_start))numbers.push(Number(v.value));
    const min=Math.min(...numbers),max=Math.max(...numbers);return {min,max,span:max-min||Math.max(Math.abs(max)*0.001,0.01)};
  },[rows,series]);
  if(!rows.length)return null;
  const y=(value:string)=>bottom-(Number(value)-prepared.min)/prepared.span*(bottom-top);
  const step=(width-left-right)/rows.length,x=(i:number)=>left+(i+0.5)*step;
  const maxVolume=Math.max(1,...rows.map(r=>Number(r.volume)));
  const ticks=[0,Math.floor((rows.length-1)/2),rows.length-1];
  function overlay(values:{candle_start:string;value:string|null;break_before:string|null}[],rsi=false){
    const lookup=new Map(values.map(v=>[v.candle_start,v]));const parts:string[]=[];let part='';
    rows.forEach((row,i)=>{const v=lookup.get(row.start);if(!v||v.value===null||v.break_before){if(part)parts.push(part);part='';}if(v?.value!==null&&v?.value!==undefined)part+=x(i)+','+(rsi?120-Number(v.value):y(v.value))+' ';});if(part)parts.push(part);return parts;
  }
  return <div className="intraday-chart">
    <p>Showing {rows.length} of {result.candles.length} observed candles. Plot coordinates are approximate; exact values are in the table. Session gaps are not filled.</p>
    <svg viewBox={'0 0 '+width+' 565'} role="img" aria-label={result.listing.symbol+' intraday candlestick chart'}>
      <title>{result.listing.symbol} {result.interval_minutes}-minute OHLCV in INR; Asia/Kolkata</title>
      {[0,1,2,3,4].map(t=>{const price=prepared.min+prepared.span*t/4,cy=bottom-(bottom-top)*t/4;return <g key={t}><line x1={left} x2={width-right} y1={cy} y2={cy} stroke="#e2e7de"/><text x={left-8} y={cy+4} textAnchor="end" fontSize="12">{price.toFixed(2)}</text></g>;})}
      {rows.map((r,i)=>{const up=Number(r.close)>=Number(r.open),color=up?'#267b67':'#ae4d42';return <g key={r.start}><title>{exchangeTime(r.start)} | O {r.open} H {r.high} L {r.low} C {r.close} | Volume {r.volume} | {r.classification}</title>
        <line x1={x(i)} x2={x(i)} y1={y(r.high)} y2={y(r.low)} stroke={color}/><rect x={x(i)-Math.max(1,step*0.32)} y={Math.min(y(r.open),y(r.close))} width={Math.max(2,step*0.64)} height={Math.max(1,Math.abs(y(r.open)-y(r.close)))} fill={color}/>
        <rect x={x(i)-Math.max(1,step*0.32)} y={volumeBottom-Number(r.volume)/maxVolume*(volumeBottom-volumeTop)} width={Math.max(2,step*0.64)} height={Number(r.volume)/maxVolume*(volumeBottom-volumeTop)} fill={color} opacity="0.6"/>
      </g>;})}
      {series.flatMap(([key,s],index)=>overlay(s.values).map((points,i)=><polyline key={key+i} points={points} fill="none" stroke={index?'#326f9d':'#9e772d'} strokeWidth="2"/>))}
      <text x="15" y="23" fontSize="13">INR / ETF unit</text><text x="15" y="395" fontSize="13">Volume</text>
      {ticks.map((i,n)=><text key={n} x={x(i)} y="535" textAnchor={n===0?'start':n===2?'end':'middle'} fontSize="12">{exchangeTime(rows[i].start)}</text>)}
      <text x={width/2} y="560" textAnchor="middle" fontSize="12">Exchange-local candle start (IST); ordered observed bars</text>
    </svg>
    <p>{series.map(([key,s])=>key+' '+s.n+' on '+s.timeframe).join(' | ')}</p>
    {result.indicators.RSI&&<svg viewBox={'0 0 '+width+' 155'} role="img" aria-label={result.listing.symbol+' intraday Wilder RSI'}>
      <title>Wilder RSI {result.indicators.RSI.n} on {result.interval_minutes}-minute completed candles</title>
      {[0,50,100].map(v=><g key={v}><line x1={left} x2={width-right} y1={120-v} y2={120-v} stroke="#dce4db"/><text x={left-8} y={124-v} textAnchor="end">{v}</text></g>)}
      {overlay(result.indicators.RSI.values,true).map((points,i)=><polyline key={i} points={points} fill="none" stroke="#7958a8" strokeWidth="2"/>)}
      <text x={width/2} y="150" textAnchor="middle">Intraday Wilder RSI, separate 0-100 scale</text>
    </svg>}
  </div>;
}
