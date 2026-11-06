export const API_ROOT = import.meta.env.VITE_API_ROOT || 'http://127.0.0.1:8000/api/v1';
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/api\/v1$/.test(API_ROOT)) throw new Error('The API must use a configured loopback address.');

export interface Envelope<T> { data: T; meta?: Record<string, unknown> & { page?: { next_cursor: string | null } }; error?: { code: string; message: string; request_id?: string } }
export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public payload?: Envelope<unknown>) { super(message); }
}
export type Call = {
  <T>(path: string, options?: RequestInit): Promise<Envelope<T>>;
  stream?: (signal:AbortSignal, receive:(event:MarketEvent)=>void)=>Promise<void>;
};
export function client(token: string): Call {
  const call:Call = async <T,>(path: string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers);
    headers.set('Authorization', 'Bearer ' + token);
    if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
    let res: Response;
    try { res = await fetch(API_ROOT + path, { ...options, headers, cache: 'no-store' }); }
    catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') throw error;
      throw new ApiError(0, 'CONNECTION_UNAVAILABLE', 'Cannot reach the local API. For an interrupted import, resolve or retry the same request key.');
    }
    if (res.status === 204) return { data: null as T };
    const payload = await res.json() as Envelope<T>;
    if (!res.ok) throw new ApiError(res.status, payload.error?.code || 'REQUEST_FAILED', payload.error?.message || 'Request failed.', payload as Envelope<unknown>);
    return payload;
  };
  call.stream=async(signal,receive)=>{
    const response=await fetch(API_ROOT+'/market-data/stream-events',{headers:{Authorization:'Bearer '+token},signal,cache:'no-store'});
    if(!response.ok||!response.body)throw new Error('Local streaming unavailable. Controlled quote polling remains available.');
    const reader=response.body.getReader(),decoder=new TextDecoder();let pending='';
    try{while(!signal.aborted){const item=await reader.read();if(item.done)break;
      pending+=decoder.decode(item.value,{stream:true});if(pending.length>1048576)throw new Error('Local stream message limit exceeded.');
      let boundary:number;while((boundary=pending.indexOf('\n\n'))>=0){const block=pending.slice(0,boundary);pending=pending.slice(boundary+2);
        if(block.startsWith('data: '))receive(JSON.parse(block.slice(6)) as MarketEvent);
      }
    }}finally{await reader.cancel().catch(()=>{});reader.releaseLock();}
  };
  return call;
}
export async function allPages<T>(api: Call, path: string): Promise<T[]> {
  const result: T[] = [];
  let cursor: string | null = null;
  do {
    const page: Envelope<T[]> = await api<T[]>(path + (path.includes('?') ? '&' : '?') + 'limit=1000' + (cursor ? '&cursor=' + encodeURIComponent(cursor) : ''));
    result.push(...page.data); cursor = page.meta?.page?.next_cursor || null;
  } while (cursor);
  return result;
}
export interface Instrument { id: string; exchange: string; symbol: string; name: string; metal: string; currency: string; active: boolean; data_revision: number }
export interface Source { source_kind?: 'USER_CSV' | 'DHANHQ'; id: string; label: string; qualification: string; rights_evidence_ref: string | null; permitted_uses: Record<string, unknown>; profile: Record<string, unknown> & { data_class: string; policy_version: string }; reviewed_at: string | null }
export interface Watchlist { id: string; name: string; members: Instrument[] }
export interface Batch { id: string; request_key: string; status: string; new_count: number; row_count: number; duplicate_count: number; error_count: number; data_class: string; submitted_at: string; replayed: boolean; file_sha256: string; profile_sha256: string; profile_snapshot: Record<string, unknown>; error_code: string | null }
export interface Issue { id: string; row_number: number | null; code: string; severity: string; details: Record<string, unknown> }
export interface Observation { id: string; trading_date: string; close: string; open: string | null; high: string | null; low: string | null; volume: number | null; event_time: string | null; event_precision: string; provider_published_at: string | null; ingested_at: string; batch_id: string; row_number: number }
export interface SeriesMeta {
  source: { label: string; data_class: string; verification: string };
  series_ref: { revision: number; price_basis: string; profile_digest: string };
  coverage: { count: number; dataset_count: number; dataset_first_date: string | null; dataset_last_date: string | null; range_first_date: string | null; range_last_date: string | null };
  quality: { flags: string[]; continuity: string; missing_session_count: number; missing_session_dates: string[]; publication_unknown_count: number; known_break_dates: string[]; import_issue_counts: Record<string, number> };
  freshness: { status: string; assessment_as_of: string; actual_latest_date: string | null; expected_latest_date: string | null; reason: string };
  limitations: string[];
}


export interface SeriesRef { instrument_id: string; source_id: string; interval: string; price_basis: string; revision: number; profile_digest: string }
export interface ChartPoint { trading_date: string; close: string; observation_id: string; batch_id: string; row_number: number; break_before: string | null }
export interface PriceChartResult { status: string; unavailable_reason: string | null; series_ref: SeriesRef; computed_at: string; input_fingerprint: string; input_evidence: { observation_count: number; first_date: string | null; last_date: string | null; batch_ids: string[] }; points: ChartPoint[] }
export interface IndicatorValue { trading_date: string; value: string | null; reason: string | null; seed_date: string | null; break_before: string | null }
export interface IndicatorResult { status: string; unavailable_reason: string | null; indicator_id: string; algorithm_version: string; n: number; window_unit: string; series_ref: SeriesRef; seed_date: string | null; seed_dates: string[]; computed_at: string; input_fingerprint: string; values: IndicatorValue[] }
export interface ComparisonValue { trading_date: string; close: string; rebased_price: string | null; volume: number | null; observation_id: string; batch_id: string; row_number: number }
export interface ComparisonSeries { key: string; currency: string; price_basis: string; data_class: string; close_end: string | null; volume_end: number | null; price_change_percent: string | null; input_fingerprint: string; values: ComparisonValue[]; meta: SeriesMeta & { instrument: { id: string; symbol: string; name: string; metal: string }; input_fingerprint: string } }
export interface ComparisonResult { status: string; unavailable_reason: string | null; method_version: string; computed_at: string; requested_period: { start: string; end: string }; effective_period: { start: string | null; end: string | null }; common_dates: string[]; common_observation_count: number; input_fingerprint: string; limitations: string[]; series: ComparisonSeries[] }

export function canResearch(source: Source | undefined): boolean {
  return source?.qualification === 'QUALIFIED_FOR_RESEARCH' || Boolean(
    source?.qualification === 'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED' &&
    source.permitted_uses.storage === false &&
    ['retrieval', 'analysis', 'display'].every(use => source.permitted_uses[use] === true)
  );
}

export interface AcquisitionResult {
  status: string; requests: number; added: number; revised: number; error: string | null;
  coverage: Record<string, number>; dataset_count: number; dataset_first_date: string | null;
  dataset_last_date: string | null; warmup_complete: boolean; calendar_unassessed: boolean;
  latest_completed_session_candidate: string; latest_provider_eligible_session_candidate: string;
}
export function hasLiveRetrieval(source?: Source): boolean {
  return source?.source_kind === 'DHANHQ' && source.qualification === 'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED' && source.profile.data_class === 'REAL_MARKET';
}
export async function ensureProviderHistory(api: Call, instrument: Instrument, source: Source, start: string, end: string, signal: AbortSignal, warmup = 0, refresh = false): Promise<AcquisitionResult | null> {
  if (!hasLiveRetrieval(source)) return null;
  return (await api<AcquisitionResult>('/market-data/ensure', { method: 'POST', signal,
    body: JSON.stringify({ instrument_id: instrument.id, source_id: source.id,
      start: start || null, end: end || null, warmup_bars: warmup, refresh }) })).data;
}
export function acquisitionMessage(result: AcquisitionResult | null): string {
  if (!result) return '';
  const errors: Record<string, string> = {
    TOKEN_EXPIRED: 'DhanHQ authentication has expired. Replace the token locally; no renewal was attempted.',
    INVALID_CREDENTIALS: 'DhanHQ authentication was rejected. Check the token locally.',
    MISSING_ACCESS_TOKEN: 'DhanHQ access token is missing. Configure it locally in the backend environment.',
    INVALID_CONFIGURATION: 'DhanHQ backend configuration is invalid. Check local settings without sharing credentials.',
    DATA_ENTITLEMENT_REQUIRED: 'An active DhanHQ Data API entitlement is required.',
    ACCESS_OR_ENTITLEMENT_REQUIRED: 'DhanHQ access or Data API entitlement was rejected.',
    AUTH_EXPIRED: 'DhanHQ authentication has expired. Replace the token locally; no renewal was attempted.',
    AUTH_INVALID_OR_EXPIRED: 'DhanHQ authentication is invalid or expired. Check the token locally.',
    AUTH_INVALID: 'DhanHQ authentication was rejected. Check the token locally.',
    ACCESS_DENIED: 'DhanHQ access was denied. Check Data API entitlement.',
    RATE_LIMITED: 'DhanHQ rate limit reached. Retrieval is paused; no retry was made.',
    NETWORK_TIMEOUT: 'DhanHQ request timed out. Cached observations remain available.',
    MARKET_DATA_DISABLED: 'Live market-data retrieval is disabled in backend configuration.',
    PROVIDER_BACKOFF: 'Provider retrieval is paused after an earlier failure. Cached data remains available.',
    DATA_API_ENTITLEMENT_REQUIRED: 'An active DhanHQ Data API entitlement is required.',
  };
  if (result.error) return (errors[result.error] || 'Historical data is temporarily unavailable (' + result.error + '). Cached observations remain available.');
  return (result.requests ? 'Historical data updated successfully. ' + result.added + ' observations added. ' : 'Historical data loaded from the existing dataset. ')
    + (result.status === 'PARTIAL' ? 'Some requested sessions are not yet available. ' : '')
    + (result.warmup_complete === false ? 'Indicator warm-up history remains incomplete. ' : '')
    + 'Provider-eligible session: ' + result.latest_provider_eligible_session_candidate + '. Data is transient and will be lost after backend restart.';
}


export function supportsMarketSession(source?: Source): boolean {
  return source?.source_kind === 'DHANHQ' && (source.profile.data_class === 'REAL_MARKET' || source.profile.market_session_mock === true);
}
export interface SessionPolicy {
  enabled: boolean; quotes_enabled: boolean; intraday_enabled: boolean; quote_refresh_seconds: number;
  auto_quote_refresh_seconds: number; intraday_refresh_seconds: number; session_state: string; today: string;
}
export interface MarketQuote {
  instrument_id: string; name: string; listing: {symbol:string;isin:string;currency:string};
  last_price: string | null; open?: string | null; high?: string | null; low?: string | null;
  previous_close?: string | null; previous_close_basis?: string; provider_close?: string | null;
  absolute_change?: string | null; percent_change?: string | null; volume?: string | null;
  last_trade_at?: string | null; retrieved_at?: string | null; freshness: string;
  market_session?: string; classification: string; warnings?: string[];
}
export interface QuoteSnapshot { quotes:MarketQuote[];error:string|null;policy:SessionPolicy;checked_at:string|null;source:string }
export interface IntradayCandle {
  start:string;end:string;interval:number;open:string;high:string;low:string;close:string;volume:string;
  retrieved_at:string;classification:string;quality:string;
}
export interface IntradayResult {
  instrument_id:string;listing:{symbol:string;currency:string};interval_minutes:number;
  requested_period:{start:string;end:string};candles:IntradayCandle[];
  indicators:Record<string,{n:number;timeframe:string;values:{candle_start:string;value:string|null;reason:string|null;break_before:string|null}[]}>;
  provisional_session:null|{classification:string;session_date:string;open:string;high:string;low:string;close:string;volume:string;coverage:string};
  status:string;error:string|null;requests:number;revision:number;missing_completed_candles:number;
  calendar_unassessed:boolean;last_successful_retrieval:string|null;latest_provider_timestamp:string|null;
  freshness:string;market_session:string;warmup_bars:number;warnings:string[];source:string;
}
export function marketProblem(code:string|null):string {
  if (!code) return '';
  const messages:Record<string,string>={TOKEN_EXPIRED:'DhanHQ token expired. Replace it locally; no renewal was attempted.',
    AUTH_INVALID_OR_EXPIRED:'DhanHQ authentication is invalid or expired.',INVALID_CREDENTIALS:'DhanHQ credentials were rejected.',
    MISSING_CLIENT_ID:'Dhan client ID is required for quotes. Configure it locally in the backend.',MISSING_ACCESS_TOKEN:'Configure the Dhan access token locally in the backend.',
    ACCESS_DENIED:'DhanHQ access denied. Check Data API entitlement.',DATA_ENTITLEMENT_REQUIRED:'An active Data API entitlement is required.',
    RATE_LIMITED:'DhanHQ rate limit reached; no automatic retry.',PROVIDER_BACKOFF:'Provider calls are paused after a failure. Cached data remains available.',
    NETWORK_TIMEOUT:'DhanHQ timed out. Last valid data remains available.',PARTIAL_QUOTES:'Some ETF quotes are missing or invalid. Last valid quotes are retained.',
    MARKET_QUOTES_DISABLED:'Market quotes are disabled in backend configuration.',MARKET_INTRADAY_DISABLED:'Intraday retrieval is disabled in backend configuration.'};
  return messages[code] || 'Market data unavailable ('+code+'). Last valid data remains available.';
}
export function exchangeTime(value?:string|null):string {
  if (!value) return 'Unavailable';
  const date=new Date(value);
  return Number.isFinite(date.getTime()) ? date.toLocaleString('en-IN',{timeZone:'Asia/Kolkata',hour12:false})+' IST' : 'Unavailable';
}

export interface StreamStatus {state:string;error:string|null;connection_attempts:number;frames:number;rejected_frames:number;price_updates:number;last_received_at:string|null;enabled:boolean}
export interface MarketEvent {stream:StreamStatus;quotes:QuoteSnapshot;reconciliation_revision:number}
export interface Reconciliation {symbol:string;session_date:string;classification:string;provisional_disposition:string;provisional_coverage:string;provisional_bar_count:number;differing_fields:string[];comparison_status:string;publication_state:string;requests:number;error:string|null;source_qualification:string;warnings:string[]}
