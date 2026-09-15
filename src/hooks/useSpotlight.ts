import { useCallback, useRef, type MouseEvent } from 'react';

/**
 * Tracks the cursor inside an element and exposes its position as
 * --spot-x / --spot-y CSS variables, which the `.spotlight` class reads
 * to draw a highlight that follows the pointer.
 */
export function useSpotlight<T extends HTMLElement>() {
  const ref = useRef<T>(null);

  const onMouseMove = useCallback((event: MouseEvent<T>) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--spot-x', `${event.clientX - rect.left}px`);
    el.style.setProperty('--spot-y', `${event.clientY - rect.top}px`);
  }, []);

  return { ref, onMouseMove };
}
