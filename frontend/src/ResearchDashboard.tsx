import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, Call, IndicatorResult, Instrument, PriceChartResult, SeriesMeta, Source } from './api';
import { ChartBoundary, DataClass, ResearchField as Field, ResearchQuality, researchProblem } from './ResearchShared';
import type { ResearchTrace } from './ResearchChart';
const Chart = lazy(() => import('./ResearchChart'));
type Method = 'SMA' | 'EMA' | 'RSI';
type Settings = { start: string; end: string; asOf: string; SMA: boolean; EMA: boolean; RSI: boolean; smaN: string; emaN: string; rsiN: string };
const empty: Settings = { start: '', end: '', asOf: '', SMA: false, EMA: false, RSI: false, smaN: '', emaN: '', rsiN: '' };
const methods: Method[] = ['SMA', 'EMA', 'RSI'];
const period = (settings: Settings, method: Method) => settings[method === 'SMA' ? 'smaN' : method === 'EMA' ? 'emaN' : 'rsiN'];
type Calculation = { method: Method; n: number; result?: IndicatorResult; problem?: string };
type Loaded = { chart: PriceChartResult; meta: SeriesMeta; calculations: Calculation[] };
const sameRef = (a: PriceChartResult['series_ref'], b: IndicatorResult['series_ref']) => Number.isSafeInteger(a.revision) && Number.isSafeInteger(b.revision) && a.instrument_id === b.instrument_id && a.source_id === b.source_id && a.price_basis === b.price_basis && a.interval === b.interval && a.revision === b.revision && a.profile_digest === b.profile_digest;

export default function ResearchDashboard({ api, instrument, source, basis }: { api: Call; instrument?: Instrument; source?: Source; basis: string }) {
  const [draft, setDraft] = useState<Settings>(empty);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [problem, setProblem] = useState('');
  const [busy, setBusy] = useState(false);
  const [shownRows, setShownRows] = useState(100);
  const generation = useRef(0), abort = useRef<AbortController | null>(null);
  const load = useCallback(async (settings: Settings) => {
    const current = ++generation.current;
    abort.current?.abort(); const controller = new AbortController(); abort.current = controller;
    setLoaded(null); setProblem(''); setShownRows(100);
    if (!instrument || source?.qualification !== 'QUALIFIED_FOR_RESEARCH') { setBusy(false); return; }
    for (const method of methods.filter(m => settings[m])) {
      const raw = period(settings, method), n = Number(raw);
      if (!/^\d+$/.test(raw) || !Number.isInteger(n) || n < (method === 'RSI' ? 2 : 1) || n > 10000) { setBusy(false); setProblem(method + ': enter an explicit supported integer lookback.'); return; }
    }
    setBusy(true);
    const params = new URLSearchParams({ source_id: source.id, basis });
    if (settings.start) params.set('start', settings.start); if (settings.end) params.set('end', settings.end);
    if (settings.asOf) params.set('assessment_as_of', settings.asOf);
    const path = '/instruments/' + instrument.id;
    try {
      const price = await api<PriceChartResult>(path + '/chart?' + params, { signal: controller.signal });
      if (!price.meta || !Number.isSafeInteger(price.data.series_ref.revision)) throw new Error('Research snapshot identity is unavailable. Reload the series.');
      const calculations = await Promise.all(methods.filter(m => settings[m]).map(async method => {
        const n = Number(period(settings, method));
        const query = new URLSearchParams(params); query.set('indicator', method); query.set('n', String(n));
        try { return { method, n, result: (await api<IndicatorResult>(path + '/indicators?' + query, { signal: controller.signal })).data }; }
        catch (error) {
          if (controller.signal.aborted) throw error;
          return { method, n, problem: researchProblem(error), ...(error instanceof ApiError && error.payload?.data ? { result: error.payload.data as IndicatorResult } : {}) };
        }
      }));
      if (current !== generation.current || controller.signal.aborted) return;
      if (calculations.some(c => c.result && (c.result.indicator_id !== c.method || c.result.n !== c.n))) throw new Error('RESEARCH_IDENTITY_MISMATCH: indicator parameters differ from the request. Reload research.');
      if (calculations.some(c => c.result && !sameRef(price.data.series_ref, c.result.series_ref))) throw new Error('SNAPSHOT_CHANGED: prices and indicators changed during loading. Reload to use one version.');
      setLoaded({ chart: price.data, meta: price.meta as unknown as SeriesMeta, calculations });
    } catch (error) { if (current === generation.current && !controller.signal.aborted) setProblem(researchProblem(error)); }
    finally { if (current === generation.current) setBusy(false); }
  }, [api, instrument, source, basis]);
  useEffect(() => { setDraft(empty); void load(empty); return () => { ++generation.current; abort.current?.abort(); }; }, [load]);
  function rangeEdit(key: 'start' | 'end' | 'asOf', value: string) { ++generation.current; abort.current?.abort(); setBusy(false); setLoaded(null); setProblem(''); setDraft(old => ({ ...old, [key]: value })); }
  if (!instrument || !source) return <div className="empty">Select a configured ETF listing and source to open the research dashboard.</div>;
  if (source.qualification !== 'QUALIFIED_FOR_RESEARCH') return <div className="empty">This source is {source.qualification.toLowerCase()}. Review its usage evidence before research.</div>;
  const calculations = loaded?.calculations.filter(c => draft[c.method] && Number(period(draft, c.method)) === c.n) || [];
  const price = loaded?.chart;
  const valueMaps = new Map(calculations.map(c => [c.method, new Map(c.result?.values.map(v => [v.trading_date, v]) || [])]));
  const traces: ResearchTrace[] = price ? [{ name: instrument.symbol + ' close', dates: price.points.map(p => p.trading_date), values: price.points.map(p => p.close), breaks: price.points.map(p => !!p.break_before), color: '#9e772d' },
    ...calculations.filter(c => c.method !== 'RSI' && c.result).map(c => ({ name: c.method + ' (' + c.n + ')', dates: c.result!.values.map(v => v.trading_date), values: c.result!.values.map(v => v.value), breaks: c.result!.values.map(v => !!v.break_before), color: c.method === 'SMA' ? '#326f9d' : '#267b67' }))] : [];
  const rsi = calculations.find(c => c.method === 'RSI' && c.result)?.result;
  return <div className="research-dashboard">
    <section className="card"><div className="eyebrow">DESCRIPTIVE RESEARCH</div><h2>{instrument.symbol} research dashboard</h2>
      <DataClass synthetic={source.profile.data_class === 'SYNTHETIC_TEST'}/>
      <p>{instrument.name} | {instrument.metal} | {instrument.currency} | {basis}. No investment recommendations.</p>
      <form onSubmit={e => { e.preventDefault(); void load(draft); }}>
        <div className="range-bar"><Field label="Research from"><input type="date" value={draft.start} onChange={e => rangeEdit('start', e.target.value)}/></Field>
          <Field label="Research through"><input type="date" value={draft.end} onChange={e => rangeEdit('end', e.target.value)}/></Field>
          <Field label="Research assessment as of (optional ISO + timezone)"><input value={draft.asOf} onChange={e => rangeEdit('asOf', e.target.value)}/></Field></div>
        <fieldset className="indicator-controls"><legend>Indicators - explicit observed-bar lookbacks</legend>{methods.map(method => <div key={method}>
          <label className="check"><input type="checkbox" checked={draft[method]} onChange={e => setDraft(old => ({ ...old, [method]: e.target.checked }))}/>{method === 'RSI' ? 'Show Wilder RSI' : 'Show ' + method}</label>
          <Field label={method + ' lookback'}><input type="number" min={method === 'RSI' ? 2 : 1} max={10000} step={1} required={draft[method]} disabled={!draft[method]} value={period(draft, method)} onChange={e => setDraft(old => ({ ...old, [method === 'SMA' ? 'smaN' : method === 'EMA' ? 'emaN' : 'rsiN']: e.target.value }))}/></Field>
        </div>)}</fieldset>
        <p className="footnote">Blank dates select available history. Apply settings to calculate newly enabled periods. EMA/RSI use the complete eligible prefix; known discontinuities restart warm-up. No missing prices are filled.</p>
        <button className="primary" disabled={busy}>Apply research settings</button>
      </form>
    </section>
    {busy && <p role="status" className="loading">Loading research evidence.</p>}
    {problem && <div role="alert" className="notice error">{problem}<button onClick={() => void load(draft)}>Reload research</button></div>}
    {loaded && <>
      <ResearchQuality meta={loaded.meta}/>
      {!price?.points.length ? <div className="empty">No observations are available for this research range.</div> : <>
        <section className="card"><h3>Historical price and overlays</h3><p>{price.points.length} observations | {loaded.meta.coverage.range_first_date} through {loaded.meta.coverage.range_last_date}</p>
          <ChartBoundary><Suspense fallback={<p role="status">Loading local chart module.</p>}><Chart title={instrument.symbol + ' price chart'} traces={traces} identity={price.input_fingerprint}/></Suspense></ChartBoundary>
        </section>
        {calculations.map(c => <section className="card calculation-summary" key={c.method}><h3>{c.method} / n={c.n}</h3>
          {c.problem && <p role="alert" className="notice warning">{c.problem}</p>}
          {c.result && <><p>{c.result.status}{c.result.unavailable_reason ? ': ' + c.result.unavailable_reason : ''} | {c.result.window_unit}</p>
            <details><summary>{c.method} calculation provenance</summary><p>Algorithm: {c.result.algorithm_version}. Seed dates (first 20): {c.result.seed_dates.slice(0,20).join(', ') || 'Not seeded'}</p><p>Input fingerprint: <code>{c.result.input_fingerprint}</code></p><p>Computed at: {c.result.computed_at}. Derived strings have 12 decimal places; this is serialization precision.</p></details></>}
        </section>)}
        {rsi?.values.some(v => v.value !== null) && <section className="card"><h3>Wilder RSI - separate scale</h3><ChartBoundary><Suspense fallback={<p>Loading local chart module.</p>}><Chart title={instrument.symbol + ' Wilder RSI'} rsi identity={rsi.input_fingerprint} traces={[{ name: 'Wilder RSI (' + rsi.n + ')', dates: rsi.values.map(v => v.trading_date), values: rsi.values.map(v => v.value), breaks: rsi.values.map(v => !!v.break_before), color: '#7958a8' }]}/></Suspense></ChartBoundary></section>}
        <section className="card"><h3>Exact research values</h3><p>{Math.min(shownRows,price.points.length)} of {price.points.length} rows shown. Warm-up and unavailable reasons are retained.</p>
          <div className="table-wrap"><table><caption>Exact prices and server-calculated indicator values</caption><thead><tr><th>Date</th><th>Close / {instrument.currency}</th>{calculations.map(c => <th key={c.method}>{c.method} ({c.n})</th>)}<th>Source row / discontinuity</th></tr></thead>
            <tbody>{price.points.slice(0,shownRows).map(point => <tr key={point.observation_id}><td>{point.trading_date}</td><td>{point.close}</td>{calculations.map(c => { const value = valueMaps.get(c.method)?.get(point.trading_date); return <td key={c.method}>{value?.value ?? ('Unavailable: ' + (value?.reason || c.result?.unavailable_reason || c.problem || 'Not calculated'))}</td>; })}<td>{point.batch_id.slice(0,8)} / {point.row_number}{point.break_before ? ' | ' + point.break_before : ''}</td></tr>)}</tbody></table></div>
          {shownRows < price.points.length && <button onClick={() => setShownRows(n => n+100)}>Show more research rows</button>}
        </section>
      </>}
    </>}
  </div>;
}
