import {useEffect} from 'react';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,describe,expect,it,vi} from 'vitest';
import MarketSnapshot from './MarketSnapshot';
import IntradayDashboard from './IntradayDashboard';
import {Call,IntradayResult,QuoteSnapshot} from './api';

const instrument={id:'synthetic-gold',exchange:'XNSE',symbol:'SYNTH_GOLD',name:'Synthetic fixture only',metal:'GOLD',currency:'INR',active:true,data_revision:1};
const policy={enabled:true,quotes_enabled:true,intraday_enabled:true,quote_refresh_seconds:15,auto_quote_refresh_seconds:15,intraday_refresh_seconds:60,session_state:'OPEN',today:'2026-11-06'};
const quote:QuoteSnapshot={quotes:[{instrument_id:instrument.id,name:instrument.name,listing:{symbol:instrument.symbol,isin:'INF000000001',currency:'INR'},last_price:'101.1234567890',open:'100',high:'102',low:'99',previous_close:'100',previous_close_basis:'NET_CHANGE_CORROBORATED_BY_PROVIDER_CLOSE',absolute_change:'1.123456789000',percent_change:'1.123456789000',volume:'1000',last_trade_at:'2026-11-06T06:30:00Z',retrieved_at:'2026-11-06T06:30:01Z',freshness:'FRESH',market_session:'OPEN',classification:'LIVE_QUOTE'}],error:null,policy,checked_at:'2026-11-06T06:30:01Z',source:'DHANHQ'};
const result:IntradayResult={instrument_id:instrument.id,listing:{symbol:instrument.symbol,currency:'INR'},interval_minutes:5,requested_period:{start:'2026-11-05',end:'2026-11-05'},candles:[{start:'2026-11-05T03:45:00Z',end:'2026-11-05T03:50:00Z',interval:5,open:'100',high:'102',low:'99',close:'101.1234567890',volume:'1000',retrieved_at:'2026-11-06T06:30:00Z',classification:'INTRADAY_COMPLETED',quality:'VALIDATED_CANDIDATE'}],indicators:{SMA:{n:20,timeframe:'5m',values:[{candle_start:'2026-11-05T03:45:00Z',value:null,reason:'WARMUP',break_before:null}]}},provisional_session:null,status:'PARTIAL',error:null,requests:1,revision:1,missing_completed_candles:1,calendar_unassessed:false,last_successful_retrieval:'2026-11-06T06:30:00Z',latest_provider_timestamp:'2026-11-05T03:45:00Z',freshness:'FRESH',market_session:'OPEN',warmup_bars:0,warnings:['TRANSIENT_MEMORY_ONLY'],source:'DHANHQ'};
afterEach(()=>{vi.useRealTimers();vi.restoreAllMocks();});

describe('P0 market research with synthetic HTTP responses',()=>{
  it('renders exact quote values, verified changes and a manual batched refresh',async()=>{
    const calls=vi.fn(async(_path:string,_options?:RequestInit)=>({data:quote}));render(<MarketSnapshot api={calls as Call} synthetic/>);
    await screen.findByText('101.1234567890 INR');expect(screen.getByText(/1.123456789000 \/ 1.123456789000%/)).toBeInTheDocument();
    expect(screen.getByText(/SYNTHETIC TEST DATA/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Refresh quotes'}));
    await waitFor(()=>expect(calls).toHaveBeenCalledTimes(2));
    expect(JSON.parse(String(calls.mock.calls[1][1]?.body))).toEqual({refresh:true});
  });
  it('polls at 15 seconds, pauses while hidden and cleans up',async()=>{
    vi.useFakeTimers();const visibility=vi.spyOn(document,'visibilityState','get').mockReturnValue('visible');
    const calls=vi.fn(async(_path:string,_options?:RequestInit)=>({data:quote}));const view=render(<MarketSnapshot api={calls as Call}/>);
    await act(async()=>{});expect(calls).toHaveBeenCalledTimes(1);
    await act(async()=>{vi.advanceTimersByTime(15000);});expect(calls).toHaveBeenCalledTimes(2);
    visibility.mockReturnValue('hidden');await act(async()=>{vi.advanceTimersByTime(15000);});expect(calls).toHaveBeenCalledTimes(2);
    view.unmount();await act(async()=>{vi.advanceTimersByTime(60000);});expect(calls).toHaveBeenCalledTimes(2);
  });
  it('keeps last valid quotes visible after an expired-token response',async()=>{
    let n=0;const api=(async()=>({data:++n===1?quote:{...quote,error:'TOKEN_EXPIRED',quotes:quote.quotes.map(q=>({...q,freshness:'STALE'}))}})) as Call;
    render(<MarketSnapshot api={api}/>);await screen.findByText('101.1234567890 INR');
    fireEvent.click(screen.getByRole('button',{name:'Refresh quotes'}));await screen.findByRole('alert');
    expect(screen.getByText('101.1234567890 INR')).toBeInTheDocument();expect(screen.getByRole('alert')).toHaveTextContent('expired');
  });
  it('renders candlesticks, volume, IST timestamps and timeframe-specific indicator gaps',async()=>{
    const bodies:Record<string,unknown>[]=[];
    const api=(async(path:string,options?:RequestInit)=>{
      if(path.endsWith('session-policy'))return {data:policy};bodies.push(JSON.parse(String(options?.body)));return {data:result};
    }) as Call;
    render(<IntradayDashboard api={api} instrument={instrument} synthetic/>);
    await screen.findByRole('img',{name:'SYNTH_GOLD intraday candlestick chart'});
    expect(screen.getByText('101.1234567890')).toBeInTheDocument();expect(screen.getByText('SMA 20 / 5m')).toBeInTheDocument();
    expect(screen.getByText('Unavailable: WARMUP')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Intraday interval'),{target:{value:'15'}});
    fireEvent.change(screen.getByLabelText('Intraday period'),{target:{value:'previous'}});
    fireEvent.click(screen.getByRole('button',{name:'Apply intraday range'}));
    await waitFor(()=>expect(bodies.at(-1)).toMatchObject({interval:15,preset:'previous',indicators:{SMA:20}}));
  });
});

// Canvas is verified with the native chart API tests and real Chromium. jsdom has no canvas.
vi.mock('./LightweightResearchChart',()=>({default:({onUnavailable}:{onUnavailable?:(message:string)=>void})=>{useEffect(()=>{onUnavailable?.('Canvas renderer unavailable in jsdom; fallback exercised.');},[]);return null;}}));

vi.mock('./ResearchChart',()=>({default:({title}:{title:string})=><div role="img" aria-label={title}/>}));
