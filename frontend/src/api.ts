export const API_ROOT = import.meta.env.VITE_API_ROOT || 'http://127.0.0.1:8000/api/v1';
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/api\/v1$/.test(API_ROOT)) throw new Error('The API must use a configured loopback address.');

export interface Envelope<T> { data: T; meta?: Record<string, unknown> & { page?: { next_cursor: string | null } }; error?: { code: string; message: string; request_id?: string } }
export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public payload?: Envelope<unknown>) { super(message); }
}
export type Call = <T>(path: string, options?: RequestInit) => Promise<Envelope<T>>;
export function client(token: string): Call {
  return async <T,>(path: string, options: RequestInit = {}) => {
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
export interface Source { id: string; label: string; qualification: string; rights_evidence_ref: string | null; permitted_uses: Record<string, unknown>; profile: Record<string, unknown> & { data_class: string; policy_version: string }; reviewed_at: string | null }
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
