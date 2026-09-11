import type { PrecursorStatus } from '@/types';
import { STATUS_CLASSES, STATUS_LABEL } from '@/lib/display';

export function StatusBadge({ status, className = '' }: { status: PrecursorStatus; className?: string }) {
  const cls = STATUS_CLASSES[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold ${cls.bg} ${cls.text} ${className}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {STATUS_LABEL[status]}
    </span>
  );
}
