import {fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {expect,it,vi} from 'vitest';
import TechnicalWorkbench from './TechnicalWorkbench';
import {Call} from './api';
import {defaultTechnical,TechnicalResult} from './technicalTypes';
vi.mock('./ResearchChart',()=>({default:({title}:{title:string})=><div role="img" aria-label={title}/>}));
vi.mock('./LightweightResearchChart',()=>({default:({result}:{result:TechnicalResult})=><div role="img" aria-label={'Parity '+result.timeframe}/> }));
const instrument={id:'synthetic-id',symbol:'SYNTH',name:'Synthetic test',exchange:'XNSE',metal:'GOLD',currency:'INR',active:true,data_revision:1};
const source={id:'synthetic-source',label:'Synthetic only',qualification:'QUALIFIED_FOR_RESEARCH',rights_evidence_ref:'TEST ONLY',permitted_uses:{},profile:{data_class:'SYNTHETIC_TEST',policy_version:'quality-v1'},reviewed_at:null};
const candles=Array.from({length:45},(_,i)=>({time:new Date(Date.UTC(2026,0,1+i)).toISOString().slice(0,10),open:'10',high:'12',low:'9',close:'11',volume:'1000',classification:'HISTORICAL_FINAL'}));
const bundle=(fields:Record<string,string|null>)=>({algorithm_version:'synthetic-test',values:candles.map(c=>({time:c.time,reason:null,...fields}))});
const result:TechnicalResult={instrument_id:instrument.id,symbol:instrument.symbol,timeframe:'1d',parameters:defaultTechnical,indicators:{ATR:bundle({value:'2.333333333333'}),MACD:bundle({macd:'0.666666666667',signal:'0.583333333333',histogram:'0.083333333333'}),DONCHIAN:bundle({upper:'13.000000000000',lower:'9.000000000000',middle:'11.000000000000'}),SMA:bundle({value:'10'}),EMA:bundle({value:'10'}),RSI:bundle({value:'50'})},candles,status:'AVAILABLE',input_fingerprint:'synthetic-fingerprint',computed_at:'2026-11-06T12:00:00Z',warmup_bars:30,source:'SYNTHETIC TEST',source_qualification:source.qualification,price_basis:'RAW_CLOSE',freshness:'UNASSESSED',warnings:['NO_FORECAST_OR_TRADING_SIGNAL']};

it('displays exact backend technical values, preserves fifteen-row paging and offers an opt-in renderer',async()=>{
 const api=vi.fn(async()=>({data:result})) as unknown as Call;
 render(<TechnicalWorkbench api={api} instrument={instrument} source={source} basis="RAW_CLOSE"/>);
 const region=await screen.findByRole('region',{name:'Exact technical values'});
 expect(within(region).getAllByRole('row')).toHaveLength(16);
 expect(within(region).getAllByText('2.333333333333')).toHaveLength(15);
 expect(await screen.findByRole('img',{name:'SYNTH technical price / 1d'})).toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Show more technical rows'}));expect(within(region).getAllByRole('row')).toHaveLength(31);
 fireEvent.change(screen.getByLabelText('Technical chart renderer'),{target:{value:'lightweight'}});await screen.findByRole('img',{name:'Parity 1d'});
});

it('sends explicit reviewed parameters and rejects invalid MACD ordering without another call',async()=>{
 const calls=vi.fn(async()=>({data:result}));const api=calls as unknown as Call;
 render(<TechnicalWorkbench api={api} instrument={instrument} source={source} basis="RAW_CLOSE"/>);await screen.findByRole('region',{name:'Exact technical values'});
 fireEvent.change(screen.getByLabelText('ATR period'),{target:{value:'3'}});fireEvent.click(screen.getByRole('button',{name:'Apply technical settings'}));
 await waitFor(()=>expect(calls).toHaveBeenCalledTimes(2));
 const [,options]=calls.mock.calls[1] as unknown as [string,RequestInit];expect(JSON.parse(String(options.body)).parameters.atr_n).toBe(3);
 await screen.findByRole('region',{name:'Exact technical values'});
 fireEvent.change(screen.getByLabelText('MACD fast period'),{target:{value:'26'}});fireEvent.click(screen.getByRole('button',{name:'Apply technical settings'}));
 await screen.findByRole('alert');expect(calls).toHaveBeenCalledTimes(2);
});

it('reports sanitized local errors and never presents a forecast as a calculated result',async()=>{
 const api=vi.fn(async()=>{throw new Error('Technical service unavailable.');}) as unknown as Call;
 render(<TechnicalWorkbench api={api} instrument={instrument} source={source} basis="RAW_CLOSE"/>);
 expect(await screen.findByRole('alert')).toHaveTextContent('Technical service unavailable');expect(screen.queryByRole('region',{name:'Exact technical values'})).not.toBeInTheDocument();
});

it('keeps acquisition basis-specific and reports retrieval failures while preserving exact cached results',async()=>{
 const dhan={...source,source_kind:'DHANHQ' as const,qualification:'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',permitted_uses:{retrieval:true,analysis:true,display:true,storage:false},profile:{...source.profile,data_class:'REAL_MARKET'}};
 const calls=vi.fn(async(path:string)=>({data:path==='/market-data/ensure'?{error:'TOKEN_EXPIRED',status:'PARTIAL'}:result}));
 const first=render(<TechnicalWorkbench api={calls as unknown as Call} instrument={instrument} source={dhan} basis="RAW_CLOSE"/>);
 await screen.findByRole('region',{name:'Exact technical values'});expect(calls.mock.calls.every(([path])=>path==='/research/technical')).toBe(true);first.unmount();calls.mockClear();
 render(<TechnicalWorkbench api={calls as unknown as Call} instrument={instrument} source={dhan} basis="PROVIDER_ADJUSTED"/>);
 await screen.findByRole('region',{name:'Exact technical values'});expect(await screen.findByRole('alert')).toHaveTextContent('expired');expect(calls.mock.calls.map(([path])=>path)).toEqual(['/market-data/ensure','/research/technical']);
});
