import { Component, ReactNode } from 'react';
import { ApiError, SeriesMeta } from './api';
export const researchProblem = (error: unknown) => error instanceof ApiError ? error.code + ': ' + error.message : error instanceof Error ? error.message : 'Research is unavailable.';
export function ResearchField({ label, children }: { label: string; children: ReactNode }) { return <label className="field"><span>{label}</span>{children}</label>; }
export function DataClass({ synthetic }: { synthetic: boolean }) { return <p className={'notice ' + (synthetic ? 'warning' : '')}>{synthetic ? 'SYNTHETIC TEST DATA - arithmetic fixtures, not real ETF market evidence.' : 'REAL MARKET SOURCE - owner-recorded qualification; not independently verified.'}</p>; }
export const safeVolume = (volume: number | null) => volume === null ? 'Unavailable' : Number.isSafeInteger(volume) ? String(volume) : 'Unavailable: integer precision';
export function ResearchQuality({ meta }: { meta: SeriesMeta }) {
  return <section className="research-quality"><h3>Quality and source evidence</h3>
    <p>{meta.source.label} | {meta.series_ref.price_basis} | revision {meta.series_ref.revision}</p>
    {meta.limitations.includes('TRANSIENT_ONLY_NO_PERSISTENCE') && <p className="notice warning">Real provider observations are held in backend memory for this authorized research session. Persistent-use permission remains unresolved. Restarting the backend clears this data; it does not download it again.</p>}
    <p>Latest available session: <strong>{meta.coverage.dataset_last_date || 'Unavailable'}</strong> | Coverage: {meta.coverage.dataset_first_date || 'Unavailable'} through {meta.coverage.dataset_last_date || 'Unavailable'} | {meta.coverage.dataset_count} observations | Prices in INR per ETF unit.</p>
    <p>Freshness: <strong>{meta.freshness.status}</strong> | assessed {meta.freshness.assessment_as_of} | {meta.freshness.reason.replaceAll('_', ' ')}</p>
    <p>Continuity: {meta.quality.continuity} | {meta.quality.missing_session_count} assessed missing sessions.</p>
    <div className="quality-flags">{meta.quality.flags.map(flag => <span className="badge warning" key={flag}>{flag.replaceAll('_', ' ')}</span>)}</div>
    {meta.quality.known_break_dates.length > 0 && <p>Declared discontinuities: {meta.quality.known_break_dates.join(', ')}</p>}
    <p className="footnote">Unknown calendars and publication times remain unverified. Imported history is unverified for replay. Serialized precision does not establish market-data accuracy.</p>
  </section>;
}

export class ChartBoundary extends Component<{ children: ReactNode; label?: string }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert" className="notice error">{this.props.label||'The local chart module'} is unavailable. Other sections remain accessible. <button onClick={()=>this.setState({failed:false})}>Try this section again</button></p> : this.props.children; }
}
