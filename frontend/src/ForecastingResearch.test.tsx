import {fireEvent,render,screen,within,waitFor} from '@testing-library/react';
import {it,expect,vi} from 'vitest';
import ForecastingResearch from './ForecastingResearch';
import {ApiError,Call,Source} from './api';
import {ForecastContext,ForecastRun,ForecastEvaluation,ForecastOutput} from './forecastTypes';
const plotted=vi.fn();
vi.mock('./ResearchChart',()=>({default:(props:{title:string})=>{plotted(props);return <div role="img" aria-label={props.title}/>;}}));
const instrument={id:'synthetic-gold',symbol:'SYNTHGOLD',name:'Synthetic gold fixture',exchange:'XNSE',metal:'GOLD',currency:'INR',active:true,data_revision:1};
const source:Source={id:'synthetic-source',source_kind:'DHANHQ',label:'Synthetic verification only',qualification:'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',rights_evidence_ref:'TEST ONLY',reviewed_at:null,permitted_uses:{retrieval:true,analysis:true,display:true,storage:false},profile:{data_class:'SYNTHETIC_TEST',policy_version:'quality-v1'}};
const ctx:ForecastContext={instrument:{instrument_id:instrument.id,symbol:instrument.symbol,currency:'INR',isin:null},source_id:source.id,source:source.label,source_qualification:source.qualification,data_class:'SYNTHETIC_TEST',quality:'QUALIFIED_SYNTHETIC',canonical_basis:'PROVIDER_ADJUSTED',model_basis:'RAW_CLOSE',available_observations:120,eligible_observations:120,missing_sessions:0,excluded_observations:{},available_first_date:'2026-01-01',available_last_date:'2026-11-05',first_date:'2026-01-01',last_date:'2026-11-05',last_close:'100',last_first_seen_at:'2026-11-05T10:30:00Z',last_source_event_at:null,freshness:'SYNTHETIC_FIXTURE',limitations:['SYNTHETIC_TEST_ONLY'],revision:'synthetic-revision',calendar_version:'SYNTHETIC_NOT_NSE',calendar_coverage_end:'2026-12-31',history:Array.from({length:30},(_,i)=>({time:new Date(Date.UTC(2026,9,1+i)).toISOString().slice(0,10),close:'100'})),horizons:[1,5,20,60,120].map(h=>({horizon:h,target_session:h<60?'2026-11-12':null,status:h<60?'AVAILABLE':'UNAVAILABLE',reason:h<60?null:'HORIZON_OUTSIDE_REVIEWED_CALENDAR'})),instruments:[{instrument_id:instrument.id,symbol:instrument.symbol},{instrument_id:'synthetic-silver',symbol:'SYNTHSILVER'}],refresh_session:'2026-11-05',manual_refresh_enabled:true};
function output(model:string):ForecastOutput{return{forecast_id:'synthetic-'+model,model:{model_id:model,version:'synthetic-v1',lifecycle:'SYNTHETIC'},instrument:{symbol:instrument.symbol,currency:'INR'},horizon:5,origin_session:'2026-11-05',target_session:'2026-11-12',created_at:'2026-11-06T10:00:00Z',cutoff:'2026-11-06T10:00:00Z',dataset_fingerprint:'synthetic-fingerprint',predicted_price:model==='B03'?null:'101.123456789012',predicted_return:model==='B03'?null:'0.011234567890',session_volatility:model==='B03'?'0.01':null,horizon_volatility:model==='B03'?'0.022360679775':null,annualized_volatility:null,data_quality:'QUALIFIED_SYNTHETIC',calibration_status:'NOT_SUPPORTED',warnings:['SYNTHETIC_TEST_ONLY'],provenance:{source_id:source.id,source_version:'synthetic-v1',known_at:'2026-01-01T00:00:00Z',evidence_ref:'TEST ONLY'}};}
const run:ForecastRun={run_id:'synthetic-run',status:'AVAILABLE',computed_at:'2026-11-06T10:00:00Z',cutoff:'2026-11-06T10:00:00Z',horizon:5,lookback:60,target_session:'2026-11-12',context:ctx,results:['B01','B02','B03'].map(m=>({model_id:m,status:'AVAILABLE',reason:null,forecast:output(m)})),retention:'PROCESS_MEMORY_ONLY'};
const evaluation:ForecastEvaluation={status:'AVAILABLE',reason:null,context:ctx,sample_count:20,rows:Array.from({length:20},(_,i)=>({forecast_id:'synthetic-case-'+i,model_id:'B01',origin:'2026-10-01',target:'2026-10-08',cutoff:'2026-10-01T10:00:00Z',created_at:'2026-11-06T10:00:00Z',dataset_fingerprint:'synthetic',status:'MATURED',reason:null,predicted_price:'100',actual_price:'101',price_error:'-1'})),exclusions:[],experiment:{experiment_id:'synthetic-experiment',executed_at:'2026-11-06T10:00:00Z',dataset_fingerprint:'synthetic',classification:'SYNTHETIC_HISTORICAL_REPLAY',requested_period:{start:'2026-10-01',end:'2026-11-01'},frequency_sessions:5,horizon:5,lookback:60,submitted_origins:20,matured_unique_origins:20,overlapping_pairs:0,disjoint_windows:20,warnings:['SYNTHETIC_TEST_ONLY'],evaluations:['B01','B02','B03'].map(m=>({model_id:m,forecast_count:20,failed_count:0,matured_count:20,pending_count:0,unavailable_outcome_count:0,metrics:{price_samples:m==='B03'?0:20,volatility_samples:m==='B03'?20:0,price_mae:m==='B03'?null:'1',price_rmse:m==='B03'?null:'1',return_mae:m==='B03'?null:'0.01',price_bias:m==='B03'?null:'-1',return_bias:m==='B03'?null:'-0.01',directional_hit_rate:m==='B03'?null:'0',volatility_proxy_mae:m==='B03'?'0.01':null,volatility_proxy_rmse:m==='B03'?'0.01':null},benchmark:{paired_samples:m==='B03'?0:20,price_mae_relative_improvement:m==='B03'?null:'0',unavailable_reason:null}}))}};
function apiFor(handler?:(path:string,options?:RequestInit)=>unknown){return vi.fn(async(path:string,options?:RequestInit)=>{const special=handler?.(path,options);if(special!==undefined)return special;return{data:path.includes('/context?')?ctx:path.endsWith('/evaluate')?evaluation:run};});}
async function ready(){await screen.findByText(/120 eligible of 120/);await waitFor(()=>expect(screen.getByRole('button',{name:'Run Forecast'})).toBeEnabled());}

it('sends selected model horizon and lookback and renders exact separate endpoint/volatility outputs',async()=>{
 const calls=apiFor();render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();
 fireEvent.change(screen.getByLabelText('Forecast horizon'),{target:{value:'20'}});fireEvent.change(screen.getByLabelText('Forecast lookback closes'),{target:{value:'20'}});
 fireEvent.click(screen.getByRole('button',{name:'Run Forecast'}));const table=await screen.findByRole('region',{name:'Current baseline forecasts'});expect(within(table).getAllByText('101.123456789012')).toHaveLength(2);
 expect(within(table).getByText('0.022360679775')).toBeInTheDocument();expect(within(table).getAllByText('Not supported').length).toBeGreaterThanOrEqual(4);
 const options=calls.mock.calls.find(([path])=>path.endsWith('/run'))?.[1];const body=JSON.parse(String(options?.body));expect(body.horizon).toBe(20);expect(body.lookback).toBe(20);expect(body.models).toEqual(['B01','B02','B03']);
 await screen.findByRole('img',{name:'SYNTHGOLD observed prices and forecast endpoints'});const chart=plotted.mock.calls.at(-1)?.[0] as {traces:{name:string;dates:string[];mode?:string}[]};expect(chart.traces.filter(t=>t.name.includes('forecast endpoint')).every(t=>t.dates.length===1&&t.mode==='markers')).toBe(true);
 expect(screen.queryByRole('button',{name:/place order|buy now|sell now/i})).not.toBeInTheDocument();
});

it('shows historical metrics and all outcomes through a fifteen-row viewport',async()=>{
 const calls=apiFor();render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();
 fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));const table=await screen.findByRole('region',{name:'Historical forecast outcomes'});
 expect(table.querySelectorAll('tbody tr')).toHaveLength(15);fireEvent.click(screen.getByRole('button',{name:'Show more forecast outcomes'}));expect(table.querySelectorAll('tbody tr')).toHaveLength(20);
 expect(screen.getByRole('region',{name:'Historical baseline metrics'})).toHaveTextContent('B03');expect(screen.getByText(/20 unique matured eligible origins/)).toBeInTheDocument();
});

it('changes the forecast instrument independently and reports insufficient data',async()=>{
 const calls=apiFor((path)=>path.includes('/context?')&&path.includes('synthetic-silver')?{data:{...ctx,instrument:{...ctx.instrument,instrument_id:'synthetic-silver',symbol:'SYNTHSILVER'}}}:path.endsWith('/run')?{data:{...run,status:'UNAVAILABLE',context:{...ctx,instrument:{...ctx.instrument,symbol:'SYNTHSILVER'}},results:[{model_id:'B01',status:'UNAVAILABLE',reason:'INSUFFICIENT_LOOKBACK',forecast:null}]}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();fireEvent.change(screen.getByLabelText('Forecast ETF'),{target:{value:'synthetic-silver'}});
 await screen.findByText(/SYNTHSILVER \| Synthetic verification/);await waitFor(()=>expect(screen.getByRole('button',{name:'Run Forecast'})).toBeEnabled());fireEvent.click(screen.getByRole('button',{name:'Run Forecast'}));
 expect(await screen.findByRole('region',{name:'Current baseline forecasts'})).toHaveTextContent('requested completed-bar lookback');const body=JSON.parse(String(calls.mock.calls.find(([path])=>path.endsWith('/run'))?.[1]?.body));expect(body.instrument_id).toBe('synthetic-silver');
 expect(screen.getByRole('option',{name:/120 trading sessions/})).toBeDisabled();
});

it('reports sanitized errors and cancellation with no automatic forecast retry',async()=>{
 const calls=apiFor((path,options)=>path.endsWith('/run')?new Promise((_,reject)=>options?.signal?.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')))):undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();fireEvent.click(screen.getByRole('button',{name:'Run Forecast'}));
 fireEvent.click(await screen.findByRole('button',{name:'Cancel research request'}));expect(await screen.findByRole('alert')).toHaveTextContent('cancelled');expect(calls.mock.calls.filter(([path])=>path.endsWith('/run'))).toHaveLength(1);
});

it('shows source-snapshot errors without displaying request credentials',async()=>{
 const calls=apiFor((path)=>{if(path.endsWith('/run'))throw new ApiError(409,'FORECAST_SOURCE_SNAPSHOT_CHANGED','Reload the changed source snapshot.');});
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();fireEvent.click(screen.getByRole('button',{name:'Run Forecast'}));expect(await screen.findByRole('alert')).toHaveTextContent('FORECAST_SOURCE_SNAPSHOT_CHANGED');
});


it('reopens a process-scoped forecast and checks later outcome status',async()=>{
 const calls=apiFor(path=>path.endsWith('/runs')?{data:{runs:[{run_id:run.run_id,instrument_id:instrument.id,source_id:source.id,created_at:run.computed_at,horizon:5}]}}:path.endsWith('/runs/'+run.run_id)?{data:{original_run:run,run_id:run.run_id,computed_at:run.computed_at,original_created_at:run.computed_at,retention:run.retention,limitations:[],tracking:[{model_id:'B01',status:'PENDING',reason:'TARGET_SESSION_NOT_COMPLETE',actual_close:null,price_error:null,volatility_proxy_error:null}]}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();
 fireEvent.click(screen.getByRole('button',{name:'Open session forecast'}));
 expect(await screen.findByRole('region',{name:'Current baseline forecasts'})).toHaveTextContent('B01');expect(await screen.findByRole('region',{name:'Forecast outcome tracking'})).toHaveTextContent('PENDING');
 expect(calls.mock.calls.filter(([path])=>path.endsWith('/run'))).toHaveLength(0);
});


it('runs only selected baseline models and leaves volatility separate',async()=>{
 const calls=apiFor((path,options)=>path.endsWith('/run')?{data:{...run,results:run.results.filter(r=>JSON.parse(String(options?.body)).models.includes(r.model_id))}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();
 fireEvent.click(screen.getByRole('checkbox',{name:/B02 simple-return drift/}));fireEvent.click(screen.getByRole('checkbox',{name:/B03 volatility only/}));fireEvent.click(screen.getByRole('button',{name:'Run Forecast'}));
 const table=await screen.findByRole('region',{name:'Current baseline forecasts'});expect(table.querySelectorAll('tbody tr')).toHaveLength(1);expect(table).toHaveTextContent('B01');
});

it('manually refreshes only the eligible daily session through the existing bounded route',async()=>{
 const realSource={...source,profile:{...source.profile,data_class:'REAL_MARKET'}};
 const calls=apiFor(path=>path==='/market-data/ensure'?{data:{status:'PARTIAL',error:'TOKEN_EXPIRED'}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={realSource} basis="PROVIDER_ADJUSTED"/>);await ready();
 fireEvent.click(screen.getByRole('button',{name:'Refresh finalized daily data'}));await screen.findByText(/authentication has expired/);
 const refresh=calls.mock.calls.filter(([path])=>path==='/market-data/ensure');expect(refresh).toHaveLength(1);const body=JSON.parse(String(refresh[0][1]?.body));expect(body.start).toBe(ctx.refresh_session);expect(body.end).toBe(ctx.refresh_session);expect(body.refresh).toBe(true);expect(body.warmup_bars).toBe(0);expect(calls.mock.calls.some(([path])=>path.endsWith('/run'))).toBe(false);
});


it('defaults real-source evaluation to strict and requires explicit conditional acknowledgement',async()=>{
 const realSource={...source,profile:{...source.profile,data_class:'REAL_MARKET'}};const realContext={...ctx,data_class:'REAL_MARKET',quality:'CONDITIONAL_OWNER_RESEARCH'};
 const calls=apiFor(path=>path.includes('/context?')?{data:realContext}:path.endsWith('/evaluate')?{data:{...evaluation,context:realContext,evaluation_mode:'CONDITIONAL_HISTORICAL_REPLAY',qualification_status:'STRUCTURAL_ONLY',assumption_policy:'FIXED_RETRIEVED_VINTAGE_V1',assumptions:['HISTORICAL_PROVIDER_AVAILABILITY_NOT_VERIFIED']}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={realSource} basis="PROVIDER_ADJUSTED"/>);await ready();
 const select=screen.getByRole('combobox',{name:'Historical evaluation mode'});expect(select).toHaveValue('STRICT_POINT_IN_TIME');
 fireEvent.change(select,{target:{value:'CONDITIONAL_HISTORICAL_REPLAY'}});expect(screen.getByRole('button',{name:'Run Historical Evaluation'})).toBeDisabled();expect(calls.mock.calls.some(([p])=>p.endsWith('/evaluate'))).toBe(false);
 fireEvent.click(screen.getByRole('checkbox',{name:/I acknowledge the fixed-vintage/}));fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));await screen.findByText(/Evaluation mode:/);
 const request=calls.mock.calls.find(([p])=>p.endsWith('/evaluate'));const body=JSON.parse(String(request?.[1]?.body));expect(body.evaluation_mode).toBe('CONDITIONAL_HISTORICAL_REPLAY');expect(body.acknowledge_replay_assumptions).toBe(true);expect(body.replay_policy).toBe('FIXED_RETRIEVED_VINTAGE_V1');expect(screen.getByText(/Conditional retrospective research; not verified/)).toBeInTheDocument();
 fireEvent.change(select,{target:{value:'STRICT_POINT_IN_TIME'}});expect(screen.queryByText('Historical evaluation evidence')).not.toBeInTheDocument();fireEvent.change(select,{target:{value:'CONDITIONAL_HISTORICAL_REPLAY'}});expect(screen.getByRole('checkbox',{name:/I acknowledge the fixed-vintage/})).not.toBeChecked();
});

it('keeps synthetic mode separate and sends strict mode without replay assumptions',async()=>{
 const calls=apiFor();render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();
 expect(screen.getByRole('combobox',{name:'Historical evaluation mode'})).toHaveValue('SYNTHETIC');expect(screen.getByRole('option',{name:'Conditional historical replay'})).toBeDisabled();
 fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));await screen.findByText('Historical evaluation evidence');const body=JSON.parse(String(calls.mock.calls.find(([p])=>p.endsWith('/evaluate'))?.[1]?.body));expect(body.evaluation_mode).toBe('SYNTHETIC');expect(body.replay_policy).toBeNull();expect(body.acknowledge_replay_assumptions).toBe(false);
});

it('displays strict mode with unavailable metrics instead of inventing replay performance',async()=>{
 const realSource={...source,profile:{...source.profile,data_class:'REAL_MARKET'}};const realContext={...ctx,data_class:'REAL_MARKET',quality:'CONDITIONAL_OWNER_RESEARCH'};
 const calls=apiFor(path=>path.includes('/context?')?{data:realContext}:path.endsWith('/evaluate')?{data:{...evaluation,context:realContext,evaluation_mode:'STRICT_POINT_IN_TIME',status:'DATA_QUALITY_BLOCKED',sample_count:0,rows:[],experiment:null,assumptions:['ACTUAL_LOCAL_FIRST_SEEN_AND_METADATA_KNOWN_BY_CUTOFF_REQUIRED']}}:undefined);
 render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={realSource} basis="PROVIDER_ADJUSTED"/>);await ready();fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));expect(await screen.findByText(/DATA_QUALITY_BLOCKED: 0/)).toBeInTheDocument();expect(screen.queryByRole('region',{name:'Historical baseline metrics'})).not.toBeInTheDocument();
 const body=JSON.parse(String(calls.mock.calls.find(([p])=>p.endsWith('/evaluate'))?.[1]?.body));expect(body.evaluation_mode).toBe('STRICT_POINT_IN_TIME');expect(body.acknowledge_replay_assumptions).toBe(false);
});


it('allows historical one-session evaluation independently of a completed current forward target',async()=>{
 const realSource={...source,profile:{...source.profile,data_class:'REAL_MARKET'}};const realContext={...ctx,data_class:'REAL_MARKET',horizons:ctx.horizons.map(h=>h.horizon===1?{...h,status:'UNAVAILABLE',reason:'TARGET_SESSION_ALREADY_COMPLETED'}:h)};
 const calls=apiFor(path=>path.includes('/context?')?{data:realContext}:undefined);render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={realSource} basis="PROVIDER_ADJUSTED"/>);await ready();
 expect(screen.getByRole('option',{name:'1 trading session (unavailable)'})).toBeDisabled();expect(screen.getByRole('option',{name:'1 historical session'})).toBeEnabled();fireEvent.change(screen.getByRole('combobox',{name:'Historical evaluation horizon'}),{target:{value:'1'}});fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));await screen.findByText('Historical evaluation evidence');const body=JSON.parse(String(calls.mock.calls.find(([p])=>p.endsWith('/evaluate'))?.[1]?.body));expect(body.horizon).toBe(1);
});


it('sends optional cutoff-regime and bounded rolling error controls only with evaluation',async()=>{
 const calls=apiFor();render(<ForecastingResearch api={calls as unknown as Call} instrument={instrument} source={source} basis="PROVIDER_ADJUSTED"/>);await ready();fireEvent.click(screen.getByRole('checkbox',{name:'Include cutoff-based market-regime research'}));fireEvent.change(screen.getByRole('spinbutton',{name:'Rolling error window scored origins'}),{target:{value:'3'}});fireEvent.click(screen.getByRole('button',{name:'Run Historical Evaluation'}));await screen.findByText('Historical evaluation evidence');const body=JSON.parse(String(calls.mock.calls.find(([p])=>p.endsWith('/evaluate'))?.[1]?.body));expect(body.regime_analysis).toBe(true);expect(body.rolling_error_window).toBe(3);
});
