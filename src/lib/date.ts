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
