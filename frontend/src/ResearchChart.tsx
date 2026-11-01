import { useEffect, useRef, useState } from 'react';
import Plotly from 'plotly.js-basic-dist-min';
import type { Data, Layout } from 'plotly.js';

export interface ResearchTrace { name: string; dates: string[]; values: (string | null)[]; breaks?: boolean[]; color?: string }
const escaped = (text: string) => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

export default function ResearchChart({ title, traces, identity, rsi = false }: { title: string; traces: ResearchTrace[]; identity: string; rsi?: boolean }) {
  const element = useRef<HTMLDivElement>(null);
  const [problem, setProblem] = useState('');
  const [narrow, setNarrow] = useState(false);
  const pending = useRef<Promise<unknown>>(Promise.resolve());
  useEffect(() => {
    const node = element.current;
    if (!node) return;
    if ((node.clientWidth < 600) !== narrow) { setNarrow(node.clientWidth < 600); return; }
    let active = true;
    setProblem('');
    const data: Data[] = traces.map(trace => {
      const x: string[] = [], y: (number | null)[] = [], exact: string[] = [];
      trace.dates.forEach((day, index) => {
        if (index > 0 && trace.breaks?.[index]) { x.push(day); y.push(null); exact.push('Known discontinuity'); }
        const raw = trace.values[index];
        // Approximate plot coordinates only. Authoritative financial math stays on the API.
        const coordinate = raw === null ? null : Number(raw);
        x.push(day); y.push(coordinate !== null && Number.isFinite(coordinate) ? coordinate : null);
        exact.push(raw ?? 'Unavailable');
      });
      return { type: 'scatter', mode: 'lines+markers', name: escaped(trace.name), x, y, customdata: exact,
        connectgaps: false, marker: { size: 4 }, line: { color: trace.color, width: 2, shape: 'linear' },
        hovertemplate: '%{x|%Y-%m-%d}<br>%{customdata}<extra>' + escaped(trace.name) + '</extra>' };
    });
    const allDates = [...new Set(traces[0]?.dates || [])];
    const labelCount = Math.min(narrow ? 2 : 5, allDates.length);
    const dateTicks = labelCount < 2 ? allDates : Array.from({ length: labelCount }, (_, i) => allDates[Math.round(i * (allDates.length - 1) / (labelCount - 1))]);
    const layout: Partial<Layout> = { title: { text: escaped(title), font: { size: 17 } }, autosize: true,
      height: rsi ? 380 : 450, margin: { l: narrow ? 55 : 65, r: 25, t: 55, b: 120 },
      paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#334d41' },
      xaxis: { type: 'date', title: { text: 'Observed date', standoff: 12 }, tickmode: 'array', tickvals: dateTicks, ticktext: dateTicks, tickangle: 0, tickfont: { size: narrow ? 10 : 12 }, automargin: true, gridcolor: '#e2e7de' },
      yaxis: { title: { text: rsi ? 'Wilder RSI' : 'Research value' }, gridcolor: '#e2e7de', ...(rsi ? { range: [0, 100] } : {}) },
      legend: { orientation: 'h', x: 0, y: -0.3, yanchor: 'top', font: { size: narrow ? 10 : 12 } }, uirevision: identity, hovermode: 'closest' };
    pending.current = pending.current.catch(() => undefined).then(async () => {
      if (!active) return;
      await Plotly.react(node, data, layout, { displaylogo: false, showLink: false,
      responsive: true, scrollZoom: false, modeBarButtonsToRemove: ['select2d', 'lasso2d'] });
      if (!active && !node.isConnected) Plotly.purge(node);
    })
      .catch(() => { if (active) setProblem('Chart rendering is unavailable. Exact values remain in the table.'); });
    const resize = () => { if (active && (node.clientWidth < 600) !== narrow) { setNarrow(node.clientWidth < 600); return; } if (active) void Promise.resolve(Plotly.Plots.resize(node)).catch(() => {}); };
    const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : null;
    observer?.observe(node);
    window.addEventListener('resize', resize);
    return () => { active = false; observer?.disconnect(); window.removeEventListener('resize', resize); if (!node.isConnected) Plotly.purge(node); };
  }, [title, traces, identity, rsi, narrow]);
  return <figure className="research-figure">
    <div ref={element} role="img" aria-label={title} className="research-plot" style={{ height: rsi ? 380 : 450 }}/>
    {problem && <p role="alert" className="notice error">{problem}</p>}
    <figcaption>Plot coordinates are approximate; exact values are available below and on hover. Lines use observed data. Known breaks and unavailable values are not filled.</figcaption>
  </figure>;
}
