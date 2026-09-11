import { useCallback, useEffect, useRef, useState } from 'react';
import type { AsyncState } from '@/types';
import { ApiError } from '@/services/dataService';

/**
 * Generic async data-fetching hook used by every page.
 * Re-runs `fetcher` whenever `deps` changes, exposes { data, loading, error },
 * and a `refetch` function for retry buttons.
 */
export function useAsync<T>(
  fetcher: () => Promise<T>,
  deps: React.DependencyList
): AsyncState<T> & { refetch: () => void } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  });
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const [tick, setTick] = useState(0);

  const run = useCallback(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));

    fetcherRef
      .current()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
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

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  return { ...state, refetch };
}
