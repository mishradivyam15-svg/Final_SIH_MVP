import { useEffect, useRef } from 'react';

const TEXT_INPUT =
  'input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="submit"]), textarea, [contenteditable="true"]';
const INTERACTIVE =
  'a, button, select, summary, [role="link"], [role="button"], [tabindex]:not([tabindex="-1"])';

/**
 * Pointer-following cursor: a dot that tracks 1:1 (so clicking stays
 * precise) plus a ring that eases behind it and morphs to signal what is
 * under the pointer — clickable, text field, or pressed.
 *
 * Only runs for fine pointers; touch devices keep native behaviour, and
 * reduced-motion users get the ring locked to the dot with no easing.
 */
export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!window.matchMedia('(pointer: fine)').matches) return;

    const dot = dotRef.current;
    const ring = ringRef.current;
    if (!dot || !ring) return;

    const body = document.body;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let pointerX = 0;
    let pointerY = 0;
    let ringX = 0;
    let ringY = 0;
    let active = false;
    let frame = 0;

    const onMove = (event: MouseEvent) => {
      pointerX = event.clientX;
      pointerY = event.clientY;

      if (!active) {
        active = true;
        ringX = pointerX;
        ringY = pointerY;
        body.classList.add('cursor-active');
      }

      // The dot is written straight to the DOM every move — never through
      // React state, which would re-render the tree at pointer rate.
      dot.style.transform = `translate3d(${pointerX}px, ${pointerY}px, 0)`;

      const target = event.target as Element | null;
      const tone = target?.closest?.('[data-cursor-tone]') as HTMLElement | null;

      body.dataset.cursor = target?.closest?.(TEXT_INPUT)
        ? 'text'
        : target?.closest?.(INTERACTIVE)
          ? 'interactive'
          : 'default';
      body.dataset.cursorTone = tone?.dataset.cursorTone ?? 'brand';
    };

    const onDown = () => body.setAttribute('data-cursor-pressed', 'true');
    const onUp = () => body.setAttribute('data-cursor-pressed', 'false');
    const onLeave = () => {
      active = false;
      body.classList.remove('cursor-active');
    };

    const render = () => {
      const ease = reduced ? 1 : 0.19;
      ringX += (pointerX - ringX) * ease;
      ringY += (pointerY - ringY) * ease;
      ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
      frame = requestAnimationFrame(render);
    };
    frame = requestAnimationFrame(render);

    window.addEventListener('mousemove', onMove, { passive: true });
    window.addEventListener('mousedown', onDown);
    window.addEventListener('mouseup', onUp);
    document.addEventListener('mouseleave', onLeave);
    window.addEventListener('blur', onLeave);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mousedown', onDown);
      window.removeEventListener('mouseup', onUp);
      document.removeEventListener('mouseleave', onLeave);
      window.removeEventListener('blur', onLeave);
      body.classList.remove('cursor-active');
      delete body.dataset.cursor;
      delete body.dataset.cursorTone;
      body.removeAttribute('data-cursor-pressed');
    };
  }, []);

  return (
    <>
      <div ref={ringRef} className="cursor-ring" aria-hidden="true">
        <span className="cursor-ring-shape" />
      </div>
      <div ref={dotRef} className="cursor-dot" aria-hidden="true">
        <span className="cursor-dot-shape" />
      </div>
    </>
  );
}
