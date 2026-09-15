import { FlaskConical } from 'lucide-react';

/**
 * MUST be shown anywhere mock/representative numbers appear, per the
 * project's data-integrity rule: never let the UI imply demo values are
 * real OIL operational statistics.
 */
export function DemoDataBadge({ className = '' }: { className?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-400 ${className}`}
      title="This prototype uses representative demo data, not real OIL statistics."
    >
      <FlaskConical size={13} aria-hidden="true" />
      Prototype / Representative Data
    </span>
  );
}
