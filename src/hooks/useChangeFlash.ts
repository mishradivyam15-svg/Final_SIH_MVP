import { useEffect, useRef, useState } from 'react';

/**
 * True for `durationMs` after `value` changes — used to briefly highlight
 * figures that moved during a background refresh, so an operator can see
 * *what* changed rather than just that something did.
 *
 * Never fires on first render; only on an actual change.
 */
export function useChangeFlash(value: unknown, durationMs = 1400): boolean {
  const [flashing, setFlashing] = useState(false);
  const previous = useRef(value);

  useEffect(() => {
    if (Object.is(previous.current, value)) return;
    previous.current = value;

    setFlashing(true);
    const timer = window.setTimeout(() => setFlashing(false), durationMs);
    return () => window.clearTimeout(timer);
  }, [value, durationMs]);

  return flashing;
}
