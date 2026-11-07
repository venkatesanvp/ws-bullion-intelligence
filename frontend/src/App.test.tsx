import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

const TOKEN = 'synthetic-component-test-token-0000000000';
const instrument = { id: 'gold-id', exchange: 'XNSE', symbol: 'SYNTH_GOLD', name: 'Synthetic only', metal: 'GOLD', currency: 'INR', active: true, data_revision: 1 };
const silver = { ...instrument, id: 'silver-id', symbol: 'SYNTH_SILVER', metal: 'SILVER' };
const source = { id: 'source-id', label: '<script>not executed</script>', qualification: 'QUALIFIED_FOR_RESEARCH', rights_evidence_ref: 'Synthetic fixture only', permitted_uses: {}, profile: { data_class: 'SYNTHETIC_TEST', policy_version: 'quality-v1' }, reviewed_at: null };
const meta = {
  source: { label: source.label, data_class: 'SYNTHETIC_TEST', verification: 'OWNER_RECORDED_NOT_THIRD_PARTY_VERIFIED' },
  series_ref: { revision: 1, price_basis: 'RAW_CLOSE', profile_digest: 'synthetic-hash' },
  coverage: { count: 1, dataset_count: 1, dataset_first_date: '2026-01-01', dataset_last_date: '2026-01-01', range_first_date: '2026-01-01', range_last_date: '2026-01-01' },
  quality: { flags: ['CALENDAR_UNVERIFIED', 'PUBLICATION_TIME_UNKNOWN'], continuity: 'UNVERIFIED', missing_session_count: 0, missing_session_dates: [], publication_unknown_count: 1, known_break_dates: [], import_issue_counts: {} },
  freshness: { status: 'UNASSESSED', assessment_as_of: '2026-01-02T00:00:00Z', actual_latest_date: '2026-01-01', expected_latest_date: null, reason: 'NO_APPLICABLE_APPROVED_AS_OF_POLICY' },
  limitations: ['UNVERIFIED_FOR_REPLAY'], page: { next_cursor: null }
};
const observation = { id: 'row-1', trading_date: '2026-01-01', close: '10.1234567890', open: null, high: null, low: null, volume: null, event_time: null, event_precision: 'SESSION_DATE', provider_published_at: null, ingested_at: '2026-01-02T00:00:00Z', batch_id: 'synthetic-batch', row_number: 1 };
const batch = { id: 'batch-1', request_key: 'synthetic-key', status: 'REJECTED', new_count: 0, row_count: 2, duplicate_count: 0, error_count: 1, data_class: 'SYNTHETIC_TEST', submitted_at: '2026-01-02T00:00:00Z', replayed: false, file_sha256: 'synthetic-file-hash', profile_sha256: 'synthetic-profile-hash', profile_snapshot: {}, error_code: 'CONFLICTING_DUPLICATE' };
type Handler = (url: string, options?: RequestInit) => Promise<Response> | Response | undefined;
let extra: Handler | undefined;
function reply(data: unknown, metadata: unknown = {}, status = 200) { return new Response(JSON.stringify({ data, meta: metadata }), { status, headers: { 'Content-Type': 'application/json' } }); }
const fetchMock = vi.fn(async (input: string | URL | Request, options?: RequestInit): Promise<Response> => {
  const url = String(input);
  const custom = extra?.(url, options); if (custom) return custom;
  if (url.endsWith('/health/ready')) return reply({ status: 'ready' });
  if (url.includes('/instruments?')) return reply([instrument, silver], { page: { next_cursor: null } });
  if (url.includes('/data-sources?')) return reply([source]);
  if (url.includes('/watchlists?')) return reply([]);
  if (url.includes('/history?')) return reply([observation], meta);
  if (url.includes('/issues?')) return reply([{ id: 'issue-1', row_number: 2, code: 'CONFLICTING_DUPLICATE', severity: 'ERROR', details: {} }]);
  if (url.includes('/import-batches?')) return reply([], { page: { next_cursor: null } });
  throw new Error('Unexpected test request: ' + url);
});
beforeEach(() => { extra = undefined; fetchMock.mockClear(); vi.stubGlobal('fetch', fetchMock); localStorage.clear(); sessionStorage.clear(); });
afterEach(() => vi.unstubAllGlobals());

async function login() {
  const user = userEvent.setup(); render(<App/>);
  await user.type(screen.getByLabelText('Local application token'), TOKEN);
  await user.click(screen.getByRole('button', { name: /Open Bullion Workspace/ }));
  await screen.findByRole('heading', { name: 'Bullion Data Workspace' });
  return user;
}
describe('authorized data foundation', () => {
  it('keeps synthetic, unknown quality and exact price provenance visible', async () => {
    await login();
    await screen.findByText('10.1234567890');
    expect(screen.getByText('SYNTHETIC TEST DATA')).toBeInTheDocument();
    expect(screen.getByText('UNASSESSED')).toBeInTheDocument();
    expect(screen.getByText('CALENDAR UNVERIFIED')).toBeInTheDocument();
    expect(screen.getByText('Published: Unknown')).toBeInTheDocument();
    expect(screen.getAllByText(source.label).length).toBeGreaterThan(0);
    expect(document.querySelectorAll('script')).toHaveLength(0);
    expect(localStorage.length).toBe(0); expect(sessionStorage.length).toBe(0);
    expect(document.body.textContent).not.toContain(TOKEN);
    expect(fetchMock.mock.calls.every(([url]) => !String(url).includes(TOKEN))).toBe(true);
  });
  it('shows readiness failures and permits deliberate retry', async () => {
    extra = url => url.endsWith('/health/ready') ? new Response(JSON.stringify({ error: { code: 'DEPENDENCY_NOT_READY', message: 'Database requires migration.' } }), { status: 503 }) : undefined;
    const user = userEvent.setup(); render(<App/>);
    await user.type(screen.getByLabelText('Local application token'), TOKEN); await user.click(screen.getByRole('button', { name: /Open Bullion Workspace/ }));
    expect(await screen.findByRole('alert')).toHaveTextContent('DEPENDENCY_NOT_READY');
    expect(screen.queryByRole('heading', { name: 'Bullion Data Workspace' })).not.toBeInTheDocument();
    extra = undefined; await user.click(screen.getByRole('button', { name: /Open Bullion Workspace/ })); await screen.findByRole('heading', { name: 'Bullion Data Workspace' });
  });
  it('never paints a delayed Gold response under a Silver selection', async () => {
    let resolveGold!: (response: Response) => void;
    extra = url => url.includes('/instruments/gold-id/history?') ? new Promise(resolve => { resolveGold = resolve; }) : url.includes('/instruments/silver-id/history?') ? reply([{ ...observation, id: 'silver-row', close: '22.0000000000' }], meta) : undefined;
    const user = await login();
    await waitFor(() => expect(resolveGold).toBeTypeOf('function'));
    await user.selectOptions(screen.getByLabelText('ETF listing'), 'silver-id');
    await screen.findByText('22.0000000000');
    await act(async () => { resolveGold(reply([observation], meta)); });
    expect(screen.queryByText('10.1234567890')).not.toBeInTheDocument();
    expect(screen.getByText('22.0000000000')).toBeInTheDocument();
  });
  it('retains the request key on rejected import and retry, with row diagnostics', async () => {
    const keys: string[] = [];
    extra = (url, options) => {
      if (url.endsWith('/import-batches') && options?.method === 'POST') {
        keys.push(new Headers(options.headers).get('Idempotency-Key') || '');
        return new Response(JSON.stringify({ error: { code: 'CONFLICTING_DUPLICATE', message: 'No new observations were stored.' }, data: batch }), { status: 409 });
      }
      return undefined;
    };
    const user = await login(); await user.click(screen.getByRole('button', { name: 'CSV imports' }));
    await user.upload(screen.getByLabelText(/Daily CSV file/), new File(['trading_date,close\n2026-01-01,10\n'], 'synthetic.csv', { type: 'text/csv' }));
    expect((screen.getByLabelText(/Daily CSV file/) as HTMLInputElement).files?.length).toBe(1);
    // jsdom file-required validity does not observe user-event's FileList shim.
    // Native file selection/submission is separately exercised by Playwright.
    fireEvent.submit((screen.getByLabelText(/Daily CSV file/) as HTMLInputElement).form!);
    await screen.findByText('CONFLICTING_DUPLICATE', { exact: true });
    expect(screen.getByText(/CSV data row 2/)).toBeInTheDocument();
    fireEvent.submit((screen.getByLabelText(/Daily CSV file/) as HTMLInputElement).form!);
    await waitFor(() => expect(keys).toHaveLength(2));
    expect(keys[0]).toBeTruthy(); expect(keys[1]).toBe(keys[0]);
    expect(screen.getAllByText(/No new observations were stored/).length).toBeGreaterThan(0);
  });
  it('blocks unqualified sources and shows useful empty/setup states', async () => {
    extra = url => url.includes('/data-sources?') ? reply([{ ...source, qualification: 'UNVERIFIED' }]) : undefined;
    const user = await login();
    await screen.findByText(/This source is unverified/);
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes('/history?'))).toBe(false);
    await user.click(screen.getByRole('button', { name: 'CSV imports' }));
    expect(screen.getByRole('button', { name: /Validate & import/ })).toBeDisabled();
    expect(screen.getByText(/No sample market prices are preloaded/)).toBeInTheDocument();
  });
  it('clears the token and workspace when locked', async () => {
    const user = await login(); await user.click(screen.getByRole('button', { name: 'Lock Bullion Workspace' }));
    expect(screen.getByLabelText('Local application token')).toHaveValue('');
    expect(screen.queryByRole('heading', { name: 'Bullion Data Workspace' })).not.toBeInTheDocument();
  });
});


it('registers a provider source without exposing credential or retrieval controls', async () => {
  const user = await login();
  await user.click(screen.getByRole('button', { name: 'Source qualification' }));
  await user.type(screen.getByLabelText('Source label'), 'Synthetic Dhan contract fixture');
  await user.selectOptions(screen.getByLabelText('Source type'), 'DHANHQ');
  let registration: Record<string, unknown> | undefined;
  extra = (url, options) => {
    if (url.endsWith('/data-sources') && options?.method === 'POST') {
      registration = JSON.parse(String(options.body));
      return reply({ ...source, id: 'synthetic-provider-id' }, {}, 201);
    }
    return undefined;
  };
  await user.click(screen.getByRole('button', { name: 'Register source' }));
  await waitFor(() => expect(registration).toMatchObject({ source_kind: 'DHANHQ', contract_version: 'dhan-daily-v1-provisional' }));
  expect(JSON.stringify(registration)).not.toMatch(/access.token|api.secret|client.id/i);
  expect(screen.queryByLabelText(/access token|api key|api secret/i)).toBeNull();
});


it('selects the supported Dhan price basis and explains a requested range after the loaded history', async () => {
  const provider = { ...source, source_kind: 'DHANHQ', label: 'SYNTHETIC Dhan source fixture',
    qualification: 'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED', permitted_uses: { retrieval: true, analysis: true, display: true, storage: false } };
  const loaded = { ...meta, source: { ...meta.source, label: provider.label },
    coverage: { ...meta.coverage, dataset_first_date: '2025-11-03', dataset_last_date: '2026-10-30',
      range_first_date: '2026-10-30', range_last_date: '2026-10-30', count: 1, dataset_count: 246 } };
  extra = url => {
    if (url.includes('/data-sources?')) return reply([provider]);
    if (url.includes('/history?')) {
      const query = new URL(url).searchParams;
      if (query.get('start') === '2026-11-02') return reply([], { ...loaded,
        coverage: { ...loaded.coverage, count: 0, range_first_date: null, range_last_date: null } });
      return reply([{ ...observation, trading_date: '2026-10-30' }], loaded);
    }
    return undefined;
  };
  const user = await login();
  await waitFor(() => expect(screen.getByRole('combobox', { name: 'Price basis' })).toHaveValue('PROVIDER_ADJUSTED'));
  await screen.findByText('10.1234567890');
  fireEvent.change(screen.getByLabelText('From', { exact: true }), { target: { value: '2026-11-02' } });
  fireEvent.change(screen.getByLabelText('Through', { exact: true }), { target: { value: '2026-11-06' } });
  await user.click(screen.getByRole('button', { name: 'Apply range' }));
  expect(await screen.findByText(/Range applied: 2026-11-02 through 2026-11-06. 0 matching observations/)).toBeInTheDocument();
  expect(screen.getByText(/Loaded history is 2025-11-03 through 2026-10-30/)).toHaveTextContent('does not download newer data');
  expect(screen.queryByText('10.1234567890')).toBeNull();
  expect(fetchMock.mock.calls.some(([url]) => String(url).includes('start=2026-11-02') && String(url).includes('end=2026-11-06'))).toBe(true);
});

it('paginates the applied range even when draft dates have changed', async () => {
  const urls: string[] = [];
  extra = url => {
    if (!url.includes('/history?')) return undefined;
    urls.push(url);
    const q = new URL(url).searchParams;
    return reply([{ ...observation, id: q.has('cursor') ? 'next-row' : observation.id }],
      { ...meta, page: { next_cursor: q.has('cursor') ? null : 'synthetic-next-page' } });
  };
  const user = await login(); await screen.findByText('10.1234567890');
  fireEvent.change(screen.getByLabelText('From', { exact: true }), { target: { value: '2026-01-01' } });
  fireEvent.change(screen.getByLabelText('Through', { exact: true }), { target: { value: '2026-01-31' } });
  await user.click(screen.getByRole('button', { name: 'Apply range' }));
  await screen.findByText(/Range applied: 2026-01-01 through 2026-01-31/);
  fireEvent.change(screen.getByLabelText('From', { exact: true }), { target: { value: '2026-02-01' } });
  await user.click(screen.getByRole('button', { name: 'Load more observations' }));
  await waitFor(() => expect(urls.some(url => new URL(url).searchParams.has('cursor'))).toBe(true));
  const next = new URL(urls.find(url => new URL(url).searchParams.has('cursor'))!).searchParams;
  expect(next.get('start')).toBe('2026-01-01'); expect(next.get('end')).toBe('2026-01-31');
});


it('Apply range acquires missing provider data, shows loading, then displays updated history', async () => {
  // Synthetic responses exercise REAL_MARKET routing only; no provider connection.
  const provider = { ...source, source_kind: 'DHANHQ', qualification: 'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',
    permitted_uses: { retrieval: true, analysis: true, display: true, storage: false }, profile: { ...source.profile, data_class: 'REAL_MARKET' } };
  const bodies: Record<string,unknown>[] = [];
  let complete: ((response: Response) => void) | undefined;
  extra = (url, options) => {
    if (url.includes('/data-sources?')) return reply([provider]);
    if (url.endsWith('/market-data/policy')) return reply({ enabled: true, auto_refresh_seconds: 0 });
    if (url.endsWith('/market-data/ensure')) {
      const body=JSON.parse(String(options?.body)); bodies.push(body);
      if (body.start === '2026-11-02') return new Promise(resolve => { complete = resolve; });
      return reply({status:'REUSED',requests:0,added:0,error:null,latest_provider_eligible_session_candidate:'2026-11-05'});
    }
    if (url.includes('/history?') && new URL(url).searchParams.get('start') === '2026-11-02') return reply([{...observation,trading_date:'2026-11-02'}],{...meta,coverage:{...meta.coverage,range_first_date:'2026-11-02',range_last_date:'2026-11-02'}});
    return undefined;
  };
  const user=await login(); await screen.findByText('10.1234567890');
  fireEvent.change(screen.getByLabelText('From',{exact:true}),{target:{value:'2026-11-02'}});
  fireEvent.change(screen.getByLabelText('Through',{exact:true}),{target:{value:'2026-11-06'}});
  await user.click(screen.getByRole('button',{name:'Apply range'}));
  await screen.findByText(/Checking coverage and downloading missing/);
  expect(screen.getByRole('button',{name:'Applying range...'})).toBeDisabled();
  await waitFor(()=>expect(complete).toBeTypeOf('function'));
  await act(async()=>complete!(reply({status:'PARTIAL',requests:1,added:1,error:null,latest_provider_eligible_session_candidate:'2026-11-05'})));
  expect(await screen.findByText(/Historical data updated successfully. 1 observations added/)).toHaveTextContent('Some requested sessions are not yet available');
  expect(bodies.at(-1)).toMatchObject({instrument_id:instrument.id,source_id:source.id,start:'2026-11-02',end:'2026-11-06',refresh:false});
  expect(await screen.findByText(/Range applied: 2026-11-02 through 2026-11-06/)).toBeInTheDocument();
});

it('keeps previously displayed valid rows when provider authentication fails for an empty requested range',async()=>{
  const provider={...source,source_kind:'DHANHQ',qualification:'TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED',
    permitted_uses:{retrieval:true,analysis:true,display:true,storage:false},profile:{...source.profile,data_class:'REAL_MARKET'}};
  extra=(url,options)=>{
    if(url.includes('/data-sources?'))return reply([provider]);
    if(url.endsWith('/market-data/policy'))return reply({enabled:true,auto_refresh_seconds:0});
    if(url.endsWith('/market-data/ensure'))return reply({status:'PARTIAL',requests:0,added:0,error:JSON.parse(String(options?.body)).start?'AUTH_EXPIRED':null,latest_provider_eligible_session_candidate:'2026-11-05'});
    if(url.includes('/history?')&&new URL(url).searchParams.has('start'))return reply([],{...meta,coverage:{...meta.coverage,count:0}});
    return undefined;
  };
  const user=await login(); await screen.findByText('10.1234567890');
  fireEvent.change(screen.getByLabelText('From',{exact:true}),{target:{value:'2026-11-02'}});
  await user.click(screen.getByRole('button',{name:'Apply range'}));
  await screen.findByText(/DhanHQ authentication has expired/);
  expect(screen.getByText('10.1234567890')).toBeInTheDocument();
});
