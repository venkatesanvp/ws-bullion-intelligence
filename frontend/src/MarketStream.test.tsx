import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import MarketSnapshot from './MarketSnapshot';
import ReconciliationPanel from './ReconciliationPanel';
import {Call,MarketEvent,QuoteSnapshot} from './api';
const policy={enabled:true,quotes_enabled:true,intraday_enabled:true,quote_refresh_seconds:15,auto_quote_refresh_seconds:15,intraday_refresh_seconds:60,session_state:'OPEN',today:'2026-11-06'};
const snapshot:QuoteSnapshot={quotes:[{instrument_id:'test',name:'Synthetic',listing:{symbol:'SYNTH',isin:'test',currency:'INR'},last_price:'101.23',freshness:'FRESH',classification:'LIVE_STREAM'}],error:null,policy,checked_at:null,source:'SYNTHETIC_TEST'};
afterEach(()=>{vi.useRealTimers();vi.restoreAllMocks();});
it('renders normalized events, throttles quote polling while healthy and releases the stream',async()=>{
 vi.useFakeTimers();let receive:((e:MarketEvent)=>void)|undefined,aborted=false;
 const api=vi.fn(async()=>({data:snapshot})) as unknown as Call;
 api.stream=async(signal,callback)=>{receive=callback;await new Promise<void>(resolve=>signal.addEventListener('abort',()=>{aborted=true;resolve();}));};
 const view=render(<MarketSnapshot api={api}/>);await act(async()=>{});
 const event:MarketEvent={quotes:snapshot,reconciliation_revision:0,stream:{state:'CONNECTED',error:null,connection_attempts:1,frames:4,rejected_frames:0,price_updates:4,last_received_at:new Date().toISOString(),enabled:true}};
 await act(async()=>{receive!(event);});expect(screen.getByText('101.23 INR')).toBeInTheDocument();expect(screen.getByText(/Price events: 4/)).toBeInTheDocument();
 const before=vi.mocked(api).mock.calls.length;await act(async()=>{vi.advanceTimersByTime(15000);});expect(vi.mocked(api).mock.calls.length).toBe(before);
 view.unmount();expect(aborted).toBe(true);
});
it('falls back after a blocked feed and preserves valid quotes',async()=>{
 let receive:((e:MarketEvent)=>void)|undefined;
 const api=vi.fn(async()=>({data:snapshot})) as unknown as Call;api.stream=async(signal,callback)=>{receive=callback;await new Promise<void>(resolve=>signal.addEventListener('abort',()=>resolve()));};
 render(<MarketSnapshot api={api}/>);await screen.findByText('101.23 INR');
 await act(async()=>receive!({quotes:snapshot,reconciliation_revision:0,stream:{state:'BLOCKED',error:'FEED_DISCONNECT_807',connection_attempts:1,frames:0,rejected_frames:0,price_updates:0,last_received_at:null,enabled:true}}));
 expect(screen.getByText(/Controlled quote polling is the fallback/)).toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Refresh quotes'}));await waitFor(()=>expect(api).toHaveBeenCalledTimes(2));
});
it('shows finality, differences and source limits and refreshes affected research',async()=>{
 const changed=vi.fn();const api=vi.fn(async(path:string)=>({data:path.endsWith('session-policy')?policy:{symbol:'SYNTH',session_date:'2026-11-05',classification:'HISTORICAL_FINAL',provisional_disposition:'SUPERSEDED_BY_VALIDATED_PROVIDER_DAILY',provisional_coverage:'COMPLETE_REGULAR_SESSION',provisional_bar_count:75,differing_fields:['close'],comparison_status:'REVIEW_DIFFERENCES',publication_state:'AVAILABLE',requests:0,error:null,source_qualification:'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',warnings:['ADJUSTMENT_COMPATIBILITY_UNQUALIFIED']}})) as unknown as Call;
 render(<ReconciliationPanel api={api} instrument={{id:'test',symbol:'SYNTH',name:'Synthetic',exchange:'XNSE',metal:'GOLD',currency:'INR',active:true,data_revision:1}} onChange={changed}/>);
 await waitFor(()=>expect(screen.getByLabelText('Reconciliation session')).toHaveValue('2026-11-06'));
 fireEvent.change(screen.getByLabelText('Reconciliation session'),{target:{value:'2026-11-05'}});fireEvent.click(screen.getByRole('button',{name:'Reconcile selected session'}));
 await screen.findByText(/HISTORICAL_FINAL/);expect(screen.getByText(/Fields requiring review: close/)).toBeInTheDocument();expect(changed).toHaveBeenCalledTimes(1);
});
