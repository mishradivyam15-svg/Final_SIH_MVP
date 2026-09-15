import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  className?: string;
  variant?: 'neutral' | 'outline';
}

/** Generic pill badge. For priority/status use PriorityBadge / StatusBadge instead. */
export function Badge({ children, className = '', variant = 'neutral' }: BadgeProps) {
  const base =
    variant === 'outline'
      ? 'border border-ink-300 text-ink-500 bg-surface'
      : 'bg-surface-muted text-ink-700';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${base} ${className}`}
    >
      {children}
    </span>
  );
}
