import { useCallback, useEffect, useRef, useState } from 'react';
import type { AsyncState } from '@/types';
import { ApiError } from '@/services/dataService';

interface UseAsyncOptions {
  /**
   * Re-fetch on this interval in the background. Background fetches never
   * flip `loading`, so the page updates in place instead of collapsing
   * back to skeletons.
   */
  pollMs?: number;
}

interface UseAsyncResult<T> extends AsyncState<T> {
  refetch: () => void;
  /** A background poll is currently in flight. */
  syncing: boolean;
  /** Epoch ms of the last successful fetch, for "updated Ns ago". */
  lastSyncedAt: number | null;
}

/**
 * Generic async data-fetching hook used by every page.
 * Re-runs `fetcher` whenever `deps` changes, exposes { data, loading, error },
 * and a `refetch` function for retry buttons. Pass `pollMs` to keep the data
 * live.
 */
export function useAsync<T>(
  fetcher: () => Promise<T>,
  deps: React.DependencyList,
  options: UseAsyncOptions = {}
): UseAsyncResult<T> {
  const { pollMs } = options;

  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  });
  const [syncing, setSyncing] = useState(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<number | null>(null);

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const [tick, setTick] = useState(0);

  const run = useCallback(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));

    fetcherRef
      .current()
      .then((data) => {
        if (cancelled) return;
        setState({ data, loading: false, error: null });
        setLastSyncedAt(Date.now());
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message =
          err instanceof ApiError
            ? err.message
            : 'Something went wrong while loading this data. Please try again.';
        setState({ data: null, loading: false, error: message });
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  useEffect(() => run(), [run]);

  useEffect(() => {
    if (!pollMs) return;
    let cancelled = false;

    const id = window.setInterval(async () => {
      // Don't poll a tab nobody is looking at.
      if (document.hidden) return;

      setSyncing(true);
      try {
        const data = await fetcherRef.current();
        if (cancelled) return;
        setState((prev) => ({ ...prev, data, error: null }));
        setLastSyncedAt(Date.now());
      } catch {
        // A dropped poll keeps the last good data on screen. Blanking a
        // working dashboard over one transient network blip would be worse
        // than showing slightly stale numbers.
      } finally {
        if (!cancelled) setSyncing(false);
      }
    }, pollMs);

    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [pollMs]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  return { ...state, refetch, syncing, lastSyncedAt };
}
