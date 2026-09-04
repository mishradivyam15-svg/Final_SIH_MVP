import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { Priority } from '@/types';
import { PRIORITY_CLASSES, PRIORITY_LABEL } from '@/lib/display';

const ICON: Record<Priority, typeof AlertTriangle> = {
  HIGH: AlertTriangle,
  MEDIUM: AlertCircle,
  LOW: Info,
};

export function PriorityBadge({ priority, className = '' }: { priority: Priority; className?: string }) {
  const cls = PRIORITY_CLASSES[priority];
  const Icon = ICON[priority];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${cls.bg} ${cls.text} ${cls.border} ${className}`}
    >
      <Icon size={13} strokeWidth={2.5} aria-hidden="true" />
      {PRIORITY_LABEL[priority]} priority
    </span>
  );
}
