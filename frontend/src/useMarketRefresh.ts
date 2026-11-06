import { useEffect } from 'react';
import { Call, hasLiveRetrieval, Source } from './api';

// Only mounted active views poll. No background scheduler, token storage or broker calls.
export function useMarketRefresh(api: Call, source: Source | undefined, refresh: () => void) {
  useEffect(() => {
    if (!hasLiveRetrieval(source)) return;
    let interval: ReturnType<typeof setInterval> | undefined;
    const abort = new AbortController();
    void api<{ enabled: boolean; auto_refresh_seconds: number }>('/market-data/policy', { signal: abort.signal }).then(({ data }) => {
      if (!abort.signal.aborted && data.enabled && data.auto_refresh_seconds >= 60)
        interval = setInterval(() => { if (document.visibilityState === 'visible') refresh(); }, data.auto_refresh_seconds * 1000);
    }).catch(() => { /* Range application reports connection/configuration errors. */ });
    return () => { abort.abort(); if (interval) clearInterval(interval); };
  }, [api, source, refresh]);
}
