import type {TechnicalParameters} from './technicalTypes';
export const INDICATORS=[
 {id:'SMA',label:'SMA',description:'Average close over the selected observations.',ohlc:false,legacy:true,minimum:(p:TechnicalParameters)=>p.sma_n},
 {id:'EMA',label:'EMA',description:'An average that gives recent closes more weight.',ohlc:false,legacy:true,minimum:(p:TechnicalParameters)=>p.ema_n},
 {id:'RSI',label:'Wilder RSI',description:'Recent gains relative to losses, on a 0 to 100 scale.',ohlc:false,legacy:true,minimum:(p:TechnicalParameters)=>p.rsi_n+1},
 {id:'MACD',label:'MACD',description:'Fast and slow EMA difference, its signal average and histogram.',ohlc:false,legacy:false,minimum:(p:TechnicalParameters)=>p.macd_slow+p.macd_signal-1},
 {id:'ATR',label:'ATR',description:'Average true range in price units. Requires open, high and low prices.',ohlc:true,legacy:false,minimum:(p:TechnicalParameters)=>p.atr_n+1},
 {id:'DONCHIAN',label:'Donchian',description:'High and low of the prior window, excluding the current observation.',ohlc:true,legacy:false,minimum:(p:TechnicalParameters)=>p.donchian_n+1},
] as const;
export type IndicatorId=typeof INDICATORS[number]['id'];
export const closeIndicators=INDICATORS.filter(i=>i.legacy).map(i=>i.id) as ('SMA'|'EMA'|'RSI')[];
