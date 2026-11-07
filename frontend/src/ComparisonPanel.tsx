import DataViewport, {DATA_PAGE_SIZE} from './DataViewport';
import { canResearch, ensureProviderHistory, acquisitionMessage } from './api';
import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { ApiError, Call, ComparisonResult, Instrument, Source } from './api';
import { ChartBoundary, DataClass, ResearchField as Field, ResearchQuality, researchProblem, safeVolume } from './ResearchShared';
const Chart = lazy(() => import('./ResearchChart'));
type Selection = { instrument_id: string; source_id: string; price_basis: string };
const blank = (): Selection => ({ instrument_id: '', source_id: '', price_basis: '' });

export default function ComparisonPanel({ api, instruments, sources }: { api: Call; instruments: Instrument[]; sources: Source[] }) {
  const [selection, setSelection] = useState<Selection[]>([blank(), blank()]);
  const [start, setStart] = useState(''), [end, setEnd] = useState('');
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [acquisition, setAcquisition] = useState('');
  const [problem, setProblem] = useState(''), [busy, setBusy] = useState(false);
  const [shownRows, setShownRows] = useState(DATA_PAGE_SIZE);
  const generation = useRef(0), abort = useRef<AbortController | null>(null);
  useEffect(() => () => { ++generation.current; abort.current?.abort(); }, []);
  function clear() { ++generation.current; abort.current?.abort(); setBusy(false); setResult(null); setProblem(''); setShownRows(DATA_PAGE_SIZE); }
  function edit(index: number, field: keyof Selection, value: string) { clear(); setSelection(old => old.map((item,i) => i === index ? { ...item, [field]: value } : item)); }
  async function compare() {
    ++generation.current; abort.current?.abort(); setProblem(''); setAcquisition('');
    if (!start || !end || selection.some(s => !s.instrument_id || !s.source_id || !s.price_basis)) { setProblem('Select each listing, source, basis and both comparison dates.'); return; }
    const current = generation.current, controller = new AbortController(); abort.current = controller; setBusy(true);
    try {
      const messages: string[] = [];
      for (const item of selection) {
        const instrument = instruments.find(i => i.id === item.instrument_id), source = sources.find(s => s.id === item.source_id);
        if (instrument && source && item.price_basis === 'PROVIDER_ADJUSTED') {
          try {
            const update = await ensureProviderHistory(api, instrument, source, start, end, controller.signal);
            if (update) messages.push(instrument.symbol + ': ' + acquisitionMessage(update));
            if (update?.error) break;
          } catch (error) { if (controller.signal.aborted) throw error; messages.push(researchProblem(error)); break; }
        }
      }
      if (current !== generation.current || controller.signal.aborted) return;
      setAcquisition(messages.join(' '));
      const response = await api<ComparisonResult>('/comparisons', { method: 'POST', signal: controller.signal,
        body: JSON.stringify({ series: selection, start, end }) });
      if (current === generation.current && !controller.signal.aborted) setResult(response.data);
    } catch (error) {
      if (current === generation.current && !controller.signal.aborted) {
        setProblem(researchProblem(error));
        if (error instanceof ApiError && error.payload?.data) setResult(error.payload.data as ComparisonResult);
      }
    } finally { if (current === generation.current) setBusy(false); }
  }
  const synthetic = selection.some(s => sources.find(source => source.id === s.source_id)?.profile.data_class === 'SYNTHETIC_TEST');
  const eligible = selection.every(s => canResearch(sources.find(source => source.id === s.source_id)));
  return <div className="research-dashboard">
    <section className="card"><div className="eyebrow">COMMON-DATE RESEARCH</div><h2>Price-only ETF comparisons</h2>
      <p>Choose two to ten distinct listings with explicit sources and compatible bases. Only common observed dates are used; no prices are forward-filled.</p>
      {synthetic && <DataClass synthetic/>}
      <form onSubmit={event => { event.preventDefault(); void compare(); }}>
        <div className="comparison-selections">{selection.map((item,index) => <fieldset key={index}><legend>Series {index+1}</legend>
          <Field label={'Comparison ETF ' + (index+1)}><select required value={item.instrument_id} onChange={e => edit(index,'instrument_id',e.target.value)}><option value="">Select listing</option>{instruments.map(i => <option key={i.id} value={i.id}>{i.symbol} | {i.exchange} | {i.metal}</option>)}</select></Field>
          <Field label={'Comparison source ' + (index+1)}><select required value={item.source_id} onChange={e => edit(index,'source_id',e.target.value)}><option value="">Select source</option>{sources.map(s => <option key={s.id} value={s.id}>{s.label} | {s.profile.data_class} | {s.qualification}</option>)}</select></Field>
          <Field label={'Comparison basis ' + (index+1)}><select required value={item.price_basis} onChange={e => edit(index,'price_basis',e.target.value)}><option value="">Select price basis</option><option value="RAW_CLOSE">Raw close</option><option value="PROVIDER_ADJUSTED">Provider adjusted</option><option value="UNKNOWN">Unknown basis</option></select></Field>
          {selection.length > 2 && <button type="button" onClick={() => { clear(); setSelection(old => old.filter((_,i) => i !== index)); }}>Remove series {index+1}</button>}
        </fieldset>)}</div>
        <button type="button" disabled={selection.length >= 10} onClick={() => { clear(); setSelection(old => [...old,blank()]); }}>Add comparison series</button>
        <div className="range-bar"><Field label="Comparison from"><input type="date" required value={start} onChange={e => { clear(); setStart(e.target.value); }}/></Field><Field label="Comparison through"><input type="date" required value={end} onChange={e => { clear(); setEnd(e.target.value); }}/></Field><button className="primary" disabled={busy || !eligible}>Compare prices</button></div>
        {!eligible && <p className="notice">Every selected source must be qualified for research.</p>}
      </form>
    </section>
    {busy && <p role="status" className="loading">Comparing common-date observations.</p>}
    {acquisition && <p role="status" className="notice">{acquisition}</p>}
    {problem && <p role="alert" className="notice error">{problem}</p>}
    {result && <>
      <section className="card"><h3>Comparison evidence</h3><p><strong>{result.status}</strong>{result.unavailable_reason ? ': ' + result.unavailable_reason : ''}</p>
        <p>Requested: {result.requested_period.start} through {result.requested_period.end}. Actual common endpoints: {result.effective_period.start || 'Unavailable'} through {result.effective_period.end || 'Unavailable'} | {result.common_observation_count} common observations.</p>
        <p className="notice warning">Price-only change is not total return. Dividends, distributions and corporate-action adjustments are not invented. Historical changes do not imply future performance.</p>
        <DataViewport className="table-wrap" label="Comparison summary"><table><caption>Common-endpoint price-only metrics</caption><thead><tr><th>ETF / source</th><th>Basis / currency</th><th>Common ending close</th><th>Reported volume</th><th>Price-only change %</th></tr></thead><tbody>{result.series.map(s => <tr key={s.key}><td>{s.meta.instrument.symbol}<small>{s.meta.source.label} | {s.data_class}</small></td><td>{s.price_basis} | {s.currency}</td><td>{s.close_end ?? 'Unavailable'}</td><td>{safeVolume(s.volume_end)}</td><td>{s.price_change_percent ?? 'Unavailable'}</td></tr>)}</tbody></table></DataViewport>
        <details><summary>Comparison calculation provenance</summary><p>Method: {result.method_version}. Computed: {result.computed_at}.</p><p>Input fingerprint: <code>{result.input_fingerprint}</code></p><p>Derived values are serialized to 12 decimal places; this does not establish market-data accuracy.</p></details>
      </section>
      {result.status === 'AVAILABLE' && <section className="card"><h3>Common-date price normalization</h3><p>Each series starts at 100 on the actual common starting date. This is price normalization, not a portfolio or total-return model.</p>
        <ChartBoundary><Suspense fallback={<p role="status">Loading local chart module.</p>}><Chart title="Price-only common-date comparison" identity={result.input_fingerprint} traces={result.series.map(s => ({ name: s.meta.instrument.symbol, dates: s.values.map(v => v.trading_date), values: s.values.map(v => v.rebased_price) }))}/></Suspense></ChartBoundary>
      </section>}
      {result.series.map(s => <section className="card" key={s.key}><h3>{s.meta.instrument.symbol} source and quality</h3><DataClass synthetic={s.data_class === 'SYNTHETIC_TEST'}/><ResearchQuality meta={s.meta}/></section>)}
      {result.common_dates.length > 0 && <section className="card"><h3>Exact common-date values</h3><p>{Math.min(shownRows,result.common_dates.length)} of {result.common_dates.length} rows shown. Dates outside the intersection are absent.</p><DataViewport className="table-wrap" label="Common-date comparison values"><table><caption>Exact comparison observations and normalized values</caption><thead><tr><th>Date</th>{result.series.map(s => <th key={s.key}>{s.meta.instrument.symbol} ? close / normalized</th>)}</tr></thead><tbody>{result.common_dates.slice(0,shownRows).map((day,index) => <tr key={day}><td>{day}</td>{result.series.map(s => <td key={s.key}>{s.values[index].close} / {s.values[index].rebased_price ?? 'Unavailable'}</td>)}</tr>)}</tbody></table></DataViewport>{shownRows < result.common_dates.length && <button onClick={() => setShownRows(n => n+DATA_PAGE_SIZE)}>Show more comparison rows</button>}</section>}
    </>}
  </div>;
}
