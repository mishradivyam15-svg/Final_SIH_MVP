/** Small shared date-formatting utility so the whole app stays consistent. */

export function formatDate(iso: string | undefined | null): string {
  if (!iso) return 'Date unavailable';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'Date unavailable';
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatShortDate(iso: string | undefined | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

/** Short relative age, e.g. "just now", "14s ago", "3m ago". */
export function formatRelativeTime(
  iso: string | undefined | null,
  now: number = Date.now()
): string {
  if (!iso) return 'never';
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return 'never';

  const seconds = Math.max(0, Math.round((now - then) / 1000));
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  return `${Math.floor(hours / 24)}d ago`;
}

export function formatDateTime(iso: string | undefined | null): string {
  if (!iso) return 'Time unavailable';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'Time unavailable';
  return d.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
