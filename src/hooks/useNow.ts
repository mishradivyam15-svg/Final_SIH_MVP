import { useEffect, useState } from 'react';

/**
 * Re-renders on an interval so relative timestamps ("14s ago") keep
 * counting without needing new data to arrive.
 */
export function useNow(intervalMs = 1000): number {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), intervalMs);
    return () => window.clearInterval(id);
  }, [intervalMs]);

  return now;
}
