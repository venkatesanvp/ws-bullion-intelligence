import { StrictMode } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ResearchChart from './ResearchChart';
const mock = vi.hoisted(() => ({ react: vi.fn(async (..._args: unknown[]) => undefined), purge: vi.fn(), resize: vi.fn(async () => undefined) }));
vi.mock('plotly.js-basic-dist-min', () => ({ default: { react: mock.react, purge: mock.purge, Plots: { resize: mock.resize } } }));
beforeEach(() => { mock.react.mockClear(); mock.purge.mockReset(); mock.react.mockResolvedValue(undefined); });

describe('local research chart boundary', () => {
  it('keeps the current chart after Strict Mode effect replay', async () => {
    mock.react.mockImplementation(async (...args: unknown[]) => { const node=args[0] as HTMLElement; node.innerHTML='<svg class="synthetic-chart"></svg>'; });
    mock.purge.mockImplementation((node: HTMLElement) => node.replaceChildren());
    const view=render(<StrictMode><ResearchChart title="Strict synthetic chart" identity="synthetic-strict" traces={[]}/></StrictMode>);
    const graph=screen.getByRole('img',{name:'Strict synthetic chart'});
    await waitFor(()=>expect(graph.querySelector('svg.synthetic-chart')).not.toBeNull());
    view.rerender(<StrictMode><ResearchChart title="Strict synthetic chart" identity="synthetic-updated" traces={[]}/></StrictMode>);
    await waitFor(()=>expect(graph.querySelector('svg.synthetic-chart')).not.toBeNull());
    expect(graph.isConnected).toBe(true);
    view.unmount();
    expect(mock.purge).toHaveBeenCalledWith(graph);
    mock.react.mockImplementation(async (..._args: unknown[]) => undefined);
  });

  it('keeps exact hover strings, null warm-up and known gaps without interpolation', async () => {
    const { unmount } = render(<ResearchChart title="Synthetic chart" identity="synthetic-hash" traces={[{ name: '<img src=x>', dates: ['2026-01-01','2026-01-02','2026-01-04'], values: ['10.123456789012',null,'12.000000000000'], breaks: [false,false,true] }]}/>);
    await waitFor(() => expect(mock.react).toHaveBeenCalled());
    const [node,data] = mock.react.mock.calls[0] as [HTMLElement,{customdata:string[];y:(number|null)[];name:string;connectgaps:boolean}[]];
    expect(data[0].customdata[0]).toBe('10.123456789012');
    expect(data[0].y.filter(v => v === null)).toHaveLength(2);
    expect(data[0].connectgaps).toBe(false);
    expect(data[0].name).toBe('&lt;img src=x&gt;');
    expect(screen.getByRole('img',{name:'Synthetic chart'})).toBeInTheDocument();
    expect(document.querySelector('img')).toBeNull();
    unmount(); expect(mock.purge).toHaveBeenCalledWith(node);
  });
  it('uses a separate 0 to 100 RSI scale and a table fallback when rendering fails', async () => {
    mock.react.mockRejectedValueOnce(new Error('Synthetic rendering failure'));
    render(<ResearchChart title="Synthetic RSI" identity="synthetic-rsi" rsi traces={[]}/>);
    expect(await screen.findByRole('alert')).toHaveTextContent('Exact values remain in the table');
    const layout=mock.react.mock.calls[0][2] as {yaxis:{range:number[]}};
    expect(layout.yaxis.range).toEqual([0,100]);
  });
});
