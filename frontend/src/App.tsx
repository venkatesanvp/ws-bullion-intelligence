import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { allPages, ApiError, Batch, Call, client, Instrument, Issue, Observation, SeriesMeta, Source, Watchlist } from './api';

type Tab = 'History & quality' | 'CSV imports' | 'Instruments & watchlists' | 'Source qualification';
const tabs: Tab[] = ['History & quality', 'CSV imports', 'Instruments & watchlists', 'Source qualification'];
const json = (value: unknown) => JSON.stringify(value);
const describe = (error: unknown) => error instanceof ApiError ? error.code + ': ' + error.message : error instanceof Error ? error.message : 'An unexpected error occurred.';
const stamp = (value: string | null) => value ? value.replace('T', ' ').replace('Z', ' UTC') : 'Unknown';
const initialMap = JSON.stringify({ trading_date: 'trading_date', close: 'close' }, null, 2);
function Field({ label, children }: { label: string; children: ReactNode }) { return <label className="field"><span>{label}</span>{children}</label>; }
function Badge({ children, tone = '' }: { children: ReactNode; tone?: string }) { return <span className={'badge ' + tone}>{children}</span>; }
function Empty({ children }: { children: ReactNode }) { return <div className="empty">{children}</div>; }

export default function App() {
  const [token, setToken] = useState('');
  const [input, setInput] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');
  async function connect(event: FormEvent) {
    event.preventDefault(); setConnecting(true); setError('');
    try { await client(input.trim())('/health/ready'); setToken(input.trim()); setInput(''); }
    catch (e) { setError(describe(e)); } finally { setConnecting(false); }
  }
  return <div className="shell">
    <aside className="sidebar"><a className="brand" href="#main"><span className="brand-mark">Au<span>Ag</span></span><span>BULLION<br/><small>INTELLIGENCE</small></span></a>
      <div className="sidebar-caption">PERSONAL RESEARCH WORKSPACE</div>
      <div className="sidebar-note"><span className="local-dot"/> Local workspace<br/><small>CSV data inspection · VS-01</small></div>
      <div className="sidebar-bottom">Evidence before interpretation.<p>Daily ETF observations, with their source and limitations kept in view.</p><Badge>Research only</Badge></div>
    </aside>
    <main id="main">
      <header className="topbar"><span>GLOBAL BULLION / DATA WORKBENCH</span><div><Badge>LOCAL ONLY</Badge>{token && <button className="text-button" onClick={() => { setToken(''); setInput(''); }}>Lock workspace</button>}</div></header>
      {!token ? <section className="login"><div className="eyebrow">CONTROLLED DATA FOUNDATION</div><h1>Your research starts<br/>with trusted inputs.</h1><p className="lede">Inspect Indian Gold and Silver ETF history. Keep source qualification, import evidence and data limitations together.</p>
        <form className="card login-card" onSubmit={connect}><h2>Unlock local workspace</h2><p>Use LOCAL_APP_TOKEN from your local .env file. The token stays in memory and is cleared when this page closes.</p>
          <Field label="Local application token"><input autoComplete="off" type="password" required value={input} onChange={e => setInput(e.target.value)}/></Field>
          {error && <div role="alert" className="notice error">{error}</div>}
          <button className="primary" disabled={connecting}>{connecting ? 'Checking connection…' : 'Open workspace →'}</button>
        </form><p className="footnote">No live prices or broker connection. Market data must be qualified before import.</p></section>
      : <Workbench token={token}/>}
    </main>
  </div>;
}

function Workbench({ token }: { token: string }) {
  const api = useMemo(() => client(token), [token]);
  const [tab, setTab] = useState<Tab>('History & quality');
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [instrumentId, setInstrumentId] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [basis, setBasis] = useState('RAW_CLOSE');
  const [revision, setRevision] = useState(0);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const refresh = useCallback(async () => {
    const [i, s, w] = await Promise.all([allPages<Instrument>(api, '/instruments'), allPages<Source>(api, '/data-sources'), allPages<Watchlist>(api, '/watchlists')]);
    setInstruments(i); setSources(s); setWatchlists(w);
    setInstrumentId(old => old || i[0]?.id || ''); setSourceId(old => old || s[0]?.id || '');
    setRevision(n => n + 1);
  }, [api]);
  useEffect(() => { let active = true; setBusy(true); refresh().catch(e => { if (active) setError(describe(e)); }).finally(() => { if (active) setBusy(false); }); return () => { active = false; }; }, [refresh]);
  async function mutate(path: string, body?: unknown, method = 'POST') {
    setBusy(true); setError('');
    try { await api(path, { method, ...(body === undefined ? {} : { body: json(body) }) }); await refresh(); }
    catch (e) { setError(describe(e)); throw e; } finally { setBusy(false); }
  }
  const selected = instruments.find(i => i.id === instrumentId);
  const source = sources.find(s => s.id === sourceId);
  return <div className="workspace">
    <div className="page-heading"><div><div className="eyebrow">MARKET DATA · FOUNDATION</div><h1>Data workbench</h1><p>Gold & silver ETF history, with evidence attached.</p></div><div className="workspace-count"><strong>{instruments.length}</strong><span>configured listings</span></div></div>
    <div className="scope-note"><span className="scope-icon">i</span>Historical data inspection. Prices are descriptive, not live quotes or executable recommendations.</div>
    <nav className="tabs" aria-label="Workspace views">{tabs.map(t => <button key={t} aria-current={tab === t ? 'page' : undefined} onClick={() => setTab(t)}>{t}</button>)}</nav>
    {error && <div role="alert" className="notice error">{error}<button className="text-button" onClick={() => { setError(''); refresh().catch(e => setError(describe(e))); }}>Retry connection</button></div>}
    {busy && <div role="status" className="loading">Updating workspace…</div>}
    {(tab === 'History & quality' || tab === 'CSV imports') && <section className="card selectors">
      <Field label="ETF listing"><select value={instrumentId} onChange={e => setInstrumentId(e.target.value)}><option value="">Select listing</option>{instruments.map(i => <option key={i.id} value={i.id}>{i.symbol} · {i.exchange} · {i.metal}{!i.active ? ' · inactive' : ''}</option>)}</select></Field>
      <Field label="Data source"><select value={sourceId} onChange={e => setSourceId(e.target.value)}><option value="">Select source</option>{sources.map(s => <option key={s.id} value={s.id}>{s.label} · {s.profile.data_class} · {s.qualification}</option>)}</select></Field>
      <Field label="Price basis"><select value={basis} onChange={e => setBasis(e.target.value)}><option value="RAW_CLOSE">Raw close</option><option value="PROVIDER_ADJUSTED">Provider adjusted</option><option value="UNKNOWN">Unknown basis</option></select></Field>
    </section>}
    {tab === 'History & quality' && <History key={instrumentId + sourceId + basis + revision} api={api} instrument={selected} source={source} basis={basis}/>}
    {tab === 'CSV imports' && <Imports key={instrumentId + sourceId + basis} api={api} instrument={selected} source={source} basis={basis} refreshed={refresh}/>}
    {tab === 'Instruments & watchlists' && <Catalog instruments={instruments} watchlists={watchlists} mutate={mutate} busy={busy}/>}
    {tab === 'Source qualification' && <Sources sources={sources} mutate={mutate} busy={busy}/>}
    <footer>VS-01 · Authorized data foundation <span>Source evidence is owner recorded. It is not independently verified.</span></footer>
  </div>;
}

function History({ api, instrument, source, basis }: { api: Call; instrument?: Instrument; source?: Source; basis: string }) {
  const [start, setStart] = useState(''); const [end, setEnd] = useState('');
  const [asOf, setAsOf] = useState('');
  const [rows, setRows] = useState<Observation[]>([]);
  const [meta, setMeta] = useState<SeriesMeta | null>(null);
  const [next, setNext] = useState<string | null>(null);
  const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const query = useRef(0);
  const eligible = instrument && source?.qualification === 'QUALIFIED_FOR_RESEARCH';
  const load = useCallback(async (cursor?: string, rangeStart = '', rangeEnd = '', assessment = '') => {
    if (!instrument || !source || source.qualification !== 'QUALIFIED_FOR_RESEARCH') return;
    controller.current?.abort(); const abort = new AbortController(); controller.current = abort;
    const identity = ++query.current; setLoading(true); setError('');
    if (!cursor) { setRows([]); setMeta(null); setNext(null); }
    const params = new URLSearchParams({ source_id: source.id, basis, limit: '100' });
    if (rangeStart) params.set('start', rangeStart); if (rangeEnd) params.set('end', rangeEnd);
    if (assessment) params.set('assessment_as_of', assessment); if (cursor) params.set('cursor', cursor);
    try {
      const result = await api<Observation[]>('/instruments/' + instrument.id + '/history?' + params, { signal: abort.signal });
      if (identity !== query.current) return;
      setRows(old => cursor ? [...old, ...result.data] : result.data);
      setMeta(result.meta as unknown as SeriesMeta); setNext(result.meta?.page?.next_cursor || null);
    } catch (e) {
      if (identity === query.current && !(e instanceof DOMException && e.name === 'AbortError')) { setError(describe(e)); setNext(null); }
    } finally { if (identity === query.current) setLoading(false); }
  }, [api, basis, instrument, source]);
  useEffect(() => { void load(); return () => { ++query.current; controller.current?.abort(); }; }, [load]);
  if (!instrument || !source) return <Empty>Configure an ETF listing and a data source, then import qualified daily CSV observations to inspect history.</Empty>;
  if (!eligible) return <Empty>This source is {source.qualification.toLowerCase()}. Record its usage and retention evidence in Source qualification before viewing or importing prices.</Empty>;
  return <div>
    <div className="section-title"><div><h2>{instrument.symbol} <span className="muted">/ {instrument.exchange}</span></h2><p>{instrument.name} · INR · daily observations</p></div><Badge tone={source.profile.data_class === 'SYNTHETIC_TEST' ? 'warning' : ''}>{source.profile.data_class === 'SYNTHETIC_TEST' ? 'SYNTHETIC TEST DATA' : 'REAL MARKET SOURCE'}</Badge></div>
    <form className="range-bar" onSubmit={e => { e.preventDefault(); void load(undefined, start, end, asOf); }}>
      <Field label="From"><input type="date" value={start} onChange={e => setStart(e.target.value)}/></Field>
      <Field label="Through"><input type="date" value={end} onChange={e => setEnd(e.target.value)}/></Field>
      <Field label="Assessment as of (optional ISO + timezone)"><input placeholder="Leave blank for current UTC" value={asOf} onChange={e => setAsOf(e.target.value)}/></Field>
      <button disabled={loading}>Apply range</button>
    </form>
    {error && <div role="alert" className="notice error">{error}<button onClick={() => void load(undefined, start, end, asOf)}>Reload series</button></div>}
    {loading && <div role="status" className="loading">Loading persisted observations…</div>}
    {meta && <>
      <div className="metrics"><div className="metric"><span>Selected observations</span><strong>{meta.coverage.count}</strong><small>{meta.coverage.range_first_date || 'No history'} → {meta.coverage.range_last_date || '—'}</small></div>
        <div className="metric"><span>Dataset last session</span><strong className="date-metric">{meta.coverage.dataset_last_date || 'Unknown'}</strong><small>Entire selected source & basis, not just this range</small></div>
        <div className="metric"><span>Freshness assessment</span><strong className="date-metric">{meta.freshness.status}</strong><small>{meta.freshness.reason.replaceAll('_', ' ')}</small></div>
      </div>
      <section className="card quality"><div><div className="eyebrow">QUALITY & PROVENANCE</div><h3>Limitations stay visible</h3></div><div className="quality-flags">{meta.quality.flags.map(flag => <Badge key={flag} tone="warning">{flag.replaceAll('_', ' ')}</Badge>)}<Badge>{meta.quality.continuity.replaceAll('_', ' ')}</Badge></div>
        <p>Publication time unknown for {meta.quality.publication_unknown_count} dataset observations. Missing sessions in assessed range: {meta.quality.missing_session_count}. No sessions are filled.</p>
        {meta.quality.missing_session_dates.length > 0 && <p>Missing dates (first 100): {meta.quality.missing_session_dates.join(', ')}</p>}
        {meta.quality.known_break_dates.length > 0 && <p>Recorded discontinuities: {meta.quality.known_break_dates.join(', ')}</p>}
        <dl><div><dt>Source</dt><dd>{meta.source.label}</dd></div><div><dt>Series revision</dt><dd>{meta.series_ref.revision} · {meta.series_ref.price_basis}</dd></div><div><dt>Assessed at</dt><dd>{stamp(meta.freshness.assessment_as_of)}</dd></div></dl>
        <p className="footnote">Historical CSV is unverified for replay. Missing publication timestamps remain unknown; ingestion time does not establish market availability.</p>
      </section>
      <section className="card history"><div className="card-title"><h3>Daily observations</h3><span className="muted">{rows.length} shown · prices stored as exact decimals</span></div>
        {!rows.length ? <Empty>No observations in this range. Import a qualified CSV or change the dates.</Empty> : <div className="table-wrap"><table><thead><tr><th>Trading date</th><th className="numeric">Close · INR</th><th>Open / High / Low</th><th className="numeric">Volume</th><th>Publication / ingestion evidence</th><th>Provenance</th></tr></thead><tbody>{rows.map(row => <tr key={row.id}><td>{row.trading_date}</td><td className="numeric price">{row.close}</td><td>{row.open ?? '—'} / {row.high ?? '—'} / {row.low ?? '—'}</td><td className="numeric">{row.volume === null ? 'Unknown' : Number.isSafeInteger(row.volume) ? row.volume : 'Unavailable: integer precision'}</td><td><span>Published: {stamp(row.provider_published_at)}</span><small>Ingested: {stamp(row.ingested_at)}</small><small>Event: {stamp(row.event_time)} · {row.event_precision}</small></td><td><code title={row.batch_id}>{row.batch_id.slice(0, 8)}…</code><small>CSV row {row.row_number}</small></td></tr>)}</tbody></table></div>}
        {next && <button disabled={loading} onClick={() => void load(next, start, end, asOf)}>Load more observations</button>}
      </section>
    </>}
  </div>;
}

type Mutate = (path: string, body?: unknown, method?: string) => Promise<void>;
function Catalog({ instruments, watchlists, mutate, busy }: { instruments: Instrument[]; watchlists: Watchlist[]; mutate: Mutate; busy: boolean }) {
  const [notice, setNotice] = useState('');
  const [watchId, setWatchId] = useState(''); const [member, setMember] = useState('');
  const [metal, setMetal] = useState('ALL');
  async function submit(e: FormEvent<HTMLFormElement>, type: string) {
    e.preventDefault(); const form = e.currentTarget; const data = Object.fromEntries(new FormData(form));
    try {
      if (type === 'instrument') await mutate('/instruments', { ...data, ...(data.isin ? {} : { isin: null }), currency: 'INR' });
      else await mutate('/watchlists', { name: data.name });
      form.reset(); setNotice(type === 'instrument' ? 'Listing created.' : 'Watchlist created.');
    } catch { /* Workspace displays the structured API error. */ }
  }
  return <div className="two-column"><section className="card"><div className="eyebrow">LISTING IDENTITY</div><h2>ETF instruments</h2><p>Enter the exchange-specific identity from your source. No default fund universe is assumed.</p>
    <form onSubmit={e => void submit(e, 'instrument')} className="form-grid">
      <Field label="Exchange"><select name="exchange"><option value="XNSE">NSE · XNSE</option><option value="XBOM">BSE · XBOM</option></select></Field>
      <Field label="Metal"><select name="metal"><option>GOLD</option><option>SILVER</option></select></Field>
      <Field label="Symbol"><input name="symbol" required maxLength={64} pattern="[A-Z0-9&._\-]+" placeholder="Exchange symbol"/></Field>
      <Field label="Display name"><input name="name" required maxLength={256}/></Field>
      <Field label="ISIN (optional)"><input name="isin" maxLength={12}/></Field><div className="form-action"><button className="primary" disabled={busy}>Add listing</button></div>
    </form>
    <Field label="Filter configured listings"><select value={metal} onChange={e => setMetal(e.target.value)}><option value="ALL">All metals</option><option>GOLD</option><option>SILVER</option></select></Field>
    <div className="item-list">{instruments.filter(i => metal === 'ALL' || i.metal === metal).map(i => <div className="list-item" key={i.id}><div><strong>{i.symbol}</strong><small>{i.exchange} · {i.metal} · {i.name}</small></div><button disabled={busy} onClick={() => void mutate('/instruments/' + i.id, { active: !i.active }, 'PATCH').catch(() => {})}>{i.active ? 'Mark inactive' : 'Reactivate'}</button></div>)}</div>
    {!instruments.length && <Empty>No listings configured.</Empty>}
    {notice && <p role="status">{notice}</p>}
  </section><section className="card"><div className="eyebrow">PERSONAL ORGANIZATION</div><h2>Watchlists</h2><form onSubmit={e => void submit(e, 'watchlist')} className="inline-form"><Field label="New watchlist name"><input name="name" required maxLength={256}/></Field><button disabled={busy}>Create</button></form>
    <form className="form-grid" onSubmit={e => { e.preventDefault(); void mutate('/watchlists/' + watchId + '/members', { instrument_id: member }).catch(() => {}); }}>
      <Field label="Watchlist"><select required value={watchId} onChange={e => setWatchId(e.target.value)}><option value="">Select watchlist</option>{watchlists.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}</select></Field>
      <Field label="Listing to add"><select required value={member} onChange={e => setMember(e.target.value)}><option value="">Select listing</option>{instruments.map(i => <option key={i.id} value={i.id}>{i.symbol} · {i.exchange}</option>)}</select></Field><button disabled={busy}>Add to watchlist</button>
    </form>
    {watchlists.map(w => <div className="watchlist" key={w.id}><form className="inline-form" onSubmit={e => { e.preventDefault(); const data = new FormData(e.currentTarget); void mutate('/watchlists/' + w.id, { name: data.get('name') }, 'PATCH').catch(() => {}); }}><Field label="Watchlist name"><input name="name" defaultValue={w.name} required maxLength={256}/></Field><button disabled={busy}>Rename</button></form>
      {w.members.map(i => <div className="list-item" key={i.id}><div><strong>{i.symbol}</strong><small>{i.exchange} · {i.metal}</small></div><button className="text-button" disabled={busy} onClick={() => void mutate('/watchlists/' + w.id + '/members/' + i.id, undefined, 'DELETE').catch(() => {})}>Remove</button></div>)}{!w.members.length && <p className="muted">No members yet.</p>}</div>)}
    {!watchlists.length && <Empty>Create a watchlist to group listings.</Empty>}
  </section></div>;
}

function Sources({ sources, mutate, busy }: { sources: Source[]; mutate: Mutate; busy: boolean }) {
  const [sourceId, setSourceId] = useState('');
  const selected = sources.find(s => s.id === sourceId);
  const [error, setError] = useState('');
  async function create(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); const form = e.currentTarget; const d = new FormData(form);
    try { await mutate('/data-sources', { label: d.get('label'), contract_version: 'csv-v1', profile: { data_class: d.get('data_class'), policy_version: 'quality-v1' } }); form.reset(); }
    catch { /* Parent renders API error. */ }
  }
  async function qualify(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setError(''); const d = new FormData(e.currentTarget);
    try {
      const profile = JSON.parse(String(d.get('profile')));
      await mutate('/data-sources/' + sourceId + '/qualification', { qualification: d.get('qualification'), rights_evidence_ref: d.get('rights_evidence_ref') || null, retention_review_ref: d.get('retention_review_ref') || null, permitted_uses: Object.fromEntries(['retrieval', 'storage', 'analysis', 'display'].map(k => [k, d.get(k) === 'on'])), profile }, 'PATCH');
    } catch (e) { setError(describe(e)); }
  }
  return <div className="two-column"><section className="card"><div className="eyebrow">EXPLICIT SOURCE CONTRACT</div><h2>Register a CSV source</h2><p>Registration starts unverified. Record evidence before prices can be imported or displayed.</p>
    <form onSubmit={e => void create(e)}><Field label="Source label"><input name="label" required maxLength={256}/></Field><Field label="Data classification"><select name="data_class"><option value="REAL_MARKET">Real market data</option><option value="SYNTHETIC_TEST">Synthetic test data · visibly labeled</option></select></Field><button className="primary" disabled={busy}>Register source</button></form>
    <div className="item-list">{sources.map(s => <button className={'source-item ' + (sourceId === s.id ? 'selected' : '')} key={s.id} onClick={() => setSourceId(s.id)}><strong>{s.label}</strong><small>{s.profile.data_class} · {s.qualification}</small></button>)}</div>
  </section><section className="card"><div className="eyebrow">OWNER-RECORDED EVIDENCE</div><h2>Qualification & quality profile</h2>
    <div className="notice">Qualification records your review. It does not verify a license, ETF sample or market prices independently.</div>
    {!selected ? <Empty>Select a registered source to review its permissions.</Empty> : <form key={selected.id + selected.reviewed_at} onSubmit={e => void qualify(e)}>
      <h3>{selected.label}</h3>
      <Field label="Qualification status"><select name="qualification" defaultValue={selected.qualification}><option>UNVERIFIED</option><option>QUALIFIED_FOR_RESEARCH</option><option>RESTRICTED</option></select></Field>
      <Field label="Rights / usage evidence reference"><input name="rights_evidence_ref" defaultValue={selected.rights_evidence_ref || ''} maxLength={1000}/></Field>
      <Field label="Retention and deletion review reference"><input name="retention_review_ref" defaultValue={String(selected.permitted_uses.retention_review_ref || '')} maxLength={1000}/></Field>
      <fieldset><legend>Permitted uses confirmed by evidence</legend>{['retrieval', 'storage', 'analysis', 'display'].map(use => <label className="check" key={use}><input name={use} type="checkbox" defaultChecked={selected.permitted_uses[use] === true}/>{use}</label>)}</fieldset>
      <Field label="Quality profile JSON"><textarea name="profile" rows={12} spellCheck={false} defaultValue={JSON.stringify(selected.profile, null, 2)}/></Field>
      <details><summary>Profile guidance</summary><p>Keep calendar and freshness null when unknown. Calendar requires evidence_ref, version, coverage_start, coverage_end and explicit session_dates. Freshness requires evidence_ref, a timezone-aware assessment_as_of and expected_latest_session; it applies only at that instant. known_break_dates are descriptive. Provider-adjusted imports require adjustment_definition_ref.</p><p>Use references to reviewed evidence. Do not paste credentials or account data.</p></details>
      {error && <div role="alert" className="notice error">{error}</div>}<button className="primary" disabled={busy}>Save qualification review</button>
    </form>}
  </section></div>;
}

function Imports({ api, instrument, source, basis, refreshed }: { api: Call; instrument?: Instrument; source?: Source; basis: string; refreshed: () => Promise<void> }) {
  const [file, setFile] = useState<File | null>(null); const [mapping, setMapping] = useState(initialMap);
  const [key, setKey] = useState(''); const [lookup, setLookup] = useState('');
  const [batch, setBatch] = useState<Batch | null>(null); const [issues, setIssues] = useState<Issue[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]); const [next, setNext] = useState<string | null>(null);
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  useEffect(() => { setKey(crypto.randomUUID()); setBatch(null); setIssues([]); }, [file, mapping, instrument?.id, source?.id, source?.rights_evidence_ref, source?.profile.policy_version, basis]);
  const filters = useMemo(() => new URLSearchParams({ ...(instrument ? { instrument_id: instrument.id } : {}), ...(source ? { source_id: source.id } : {}) }).toString(), [instrument, source]);
  const generation = useRef(0);
  const list = useCallback(async (cursor?: string) => {
    const current = ++generation.current;
    const result = await api<Batch[]>('/import-batches?' + filters + (cursor ? '&cursor=' + encodeURIComponent(cursor) : ''));
    if (current !== generation.current) return;
    setBatches(old => cursor ? [...old, ...result.data] : result.data); setNext(result.meta?.page?.next_cursor || null);
  }, [api, filters]);
  useEffect(() => { setBatches([]); setNext(null); list().catch(e => setError(describe(e))); return () => { ++generation.current; }; }, [list]);
  async function show(value: Batch) { setBatch(value); setIssues(await allPages<Issue>(api, '/import-batches/' + value.id + '/issues')); }
  async function upload(e: FormEvent) {
    e.preventDefault(); if (!file || !source || !instrument) return;
    setBusy(true); setError(''); setBatch(null); setIssues([]);
    try {
      const metadata = { instrument_id: instrument.id, source_id: source.id, interval: '1d', price_basis: basis, mapping_version: 'user-map-v1', column_map: JSON.parse(mapping), quality_policy_version: source.profile.policy_version, qualification_ref: source.rights_evidence_ref };
      const body = new FormData(); body.set('metadata_json', json(metadata)); body.set('file', file);
      let result;
      try { result = await api<Batch>('/import-batches', { method: 'POST', body, headers: { 'Idempotency-Key': key } }); }
      catch (e) { if (e instanceof ApiError && e.payload?.data) { await show(e.payload.data as Batch); } throw e; }
      await show(result.data); await refreshed(); await list();
    } catch (e) { setError(describe(e)); } finally { setBusy(false); }
  }
  async function resolve() {
    setBusy(true); setError('');
    try { const result = await api<Batch>('/import-batches/by-key/' + encodeURIComponent(lookup || key)); await show(result.data); await list(); }
    catch (e) { setError(describe(e)); } finally { setBusy(false); }
  }
  return <div className="two-column import-columns"><section className="card"><div className="eyebrow">BOUNDED · ATOMIC · REPEATABLE</div><h2>Import daily observations</h2><p>One listing, source and price basis per CSV. The entire file is accepted or rejected together.</p>
    {source?.profile.data_class === 'SYNTHETIC_TEST' && <div className="notice warning">SYNTHETIC TEST DATA — not real ETF prices.</div>}
    <form onSubmit={e => void upload(e)}><Field label="Daily CSV file · UTF-8 · maximum 10 MiB / 100,000 rows"><input type="file" accept=".csv,text/csv" required disabled={busy} onChange={e => setFile(e.target.files?.[0] || null)}/></Field>
      <Field label="Explicit column mapping (canonical name → exact CSV header)"><textarea rows={6} spellCheck={false} value={mapping} disabled={busy} onChange={e => setMapping(e.target.value)}/></Field>
      <details><summary>CSV contract</summary><p>Required: trading_date (YYYY-MM-DD), close (positive decimal). Optional: open, high, low (complete coherent trio), volume (nonnegative integer), symbol, currency, provider_published_at and event_time (ISO instant with timezone). Every CSV header must be mapped. No financial values are inferred.</p><p>Keep unsupported fields and personal/account information out of uploads. Raw mapped strings are retained for audit. Duplicate values are skipped; conflicting observations reject the file without overwriting history.</p></details>
      <p className="request-key">Request key <code>{key}</code></p><p className="footnote">If the response is interrupted, resolve or retry this same key. Changing the file, mapping or series creates a new key.</p>
      <button className="primary" disabled={busy || !instrument || source?.qualification !== 'QUALIFIED_FOR_RESEARCH'}>{busy ? 'Processing…' : 'Validate & import CSV'}</button>
    </form>
    {source?.qualification !== 'QUALIFIED_FOR_RESEARCH' && <p className="notice">Select a source qualified for research before importing.</p>}
    <div className="recovery"><h3>Resolve an interrupted request</h3><Field label="Request UUID (blank uses current key)"><input value={lookup} onChange={e => setLookup(e.target.value)} placeholder={key}/></Field><button disabled={busy} onClick={() => void resolve()}>Look up outcome</button></div>
    {error && <div role="alert" className="notice error">{error}</div>}
  </section><div><section className="card"><div className="card-title"><h2>Import outcome</h2>{batch && <Badge tone={batch.status === 'REJECTED' ? 'warning' : ''}>{batch.status}{batch.replayed ? ' · REPLAYED' : ''}</Badge>}</div>
    {!batch ? <Empty>Upload a CSV or select a recorded batch. No sample market prices are preloaded.</Empty> : <>
      <Badge tone={batch.data_class === 'SYNTHETIC_TEST' ? 'warning' : ''}>{batch.data_class}</Badge>
      <div className="batch-counts"><div><strong>{batch.new_count}</strong><span>new observations</span></div><div><strong>{batch.duplicate_count}</strong><span>exact duplicates</span></div><div><strong>{batch.error_count}</strong><span>validation errors</span></div></div>
      <p className="footnote">Input rows: {batch.row_count}. {batch.status === 'REJECTED' ? 'No new observations were stored.' : 'Existing observations were preserved.'}</p>
      <details><summary>Audit identity & source snapshot</summary><pre>{JSON.stringify({ batch_id: batch.id, request_key: batch.request_key, file_sha256: batch.file_sha256, profile_sha256: batch.profile_sha256, profile_snapshot: batch.profile_snapshot }, null, 2)}</pre></details>
      <div className="issues">{issues.map(issue => <div className="issue" key={issue.id}><Badge tone={issue.severity === 'ERROR' ? 'warning' : ''}>{issue.severity}</Badge><span>{issue.code}<small>{issue.row_number ? 'CSV data row ' + issue.row_number : 'File / source'} {json(issue.details)}</small></span></div>)}</div>
      {batch.error_count > 1000 && <p className="notice">Diagnostics are capped at 1,000; total error count is retained.</p>}
    </>}
  </section><section className="card batch-history"><h3>Recorded batches</h3>{batches.map(b => <button key={b.id} className="source-item" onClick={() => void show(b).catch(e => setError(describe(e)))}><strong>{b.status} · {b.new_count} new · {b.error_count} errors</strong><small>{stamp(b.submitted_at)} · {b.data_class}</small><code>{b.request_key}</code></button>)}{!batches.length && <Empty>No recorded batches for this selection.</Empty>}{next && <button disabled={busy} onClick={() => void list(next).catch(e => setError(describe(e)))}>Load more batches</button>}</section></div></div>;
}
