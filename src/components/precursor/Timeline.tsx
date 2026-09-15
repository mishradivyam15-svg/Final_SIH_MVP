import { useMemo } from 'react';
import { ArrowDown, AlertTriangle, History } from 'lucide-react';
import type { SafetyReport } from '@/types';
import { EmptyState } from '@/components/common/EmptyState';
import { formatDate } from '@/lib/date';

interface TimelineProps {
  reports: SafetyReport[];
  precursorTitle: string;
}

/** Generated entirely from report data — dates/labels are never hard-coded. */
export function Timeline({ reports, precursorTitle }: TimelineProps) {
  const sorted = useMemo(
    () => [...reports].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()),
    [reports]
  );

  if (sorted.length === 0) {
    return (
      <EmptyState
        icon={History}
        title="No timeline data available"
        description="Contributing reports for this precursor do not have date information."
      />
    );
  }

  return (
    <section className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card">
      <h2 className="mb-4 text-sm font-semibold text-ink-900">Recurrence Timeline</h2>
      <ol className="relative border-l border-ink-300 pl-6">
        {sorted.map((report, idx) => (
          <li key={report.id} className="mb-6 last:mb-0">
            <span className="absolute -left-[7px] mt-1 h-3 w-3 rounded-full border-2 border-surface bg-brand-500" />
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">
              {formatDate(report.date)}
            </p>
            <p className="mt-0.5 text-sm font-semibold text-ink-900">{report.displayId}</p>
            <p className="text-xs text-ink-500">
              {report.hazard}
              {idx > 0 && report.barrier === sorted[idx - 1].barrier && ' · same barrier as previous'}
              {idx > 0 &&
                report.barrier !== sorted[idx - 1].barrier &&
                report.activity === sorted[idx - 1].activity &&
                ' · same activity as previous'}
            </p>
            {idx < sorted.length - 1 && (
              <ArrowDown size={14} className="mt-2 text-ink-300" aria-hidden="true" />
            )}
          </li>
        ))}
        <li className="flex items-center gap-2 rounded-md bg-priority-highBg px-3 py-2 text-sm font-semibold text-priority-high">
          <AlertTriangle size={15} aria-hidden="true" />
          Recurring precursor detected: {precursorTitle}
        </li>
      </ol>
    </section>
  );
}
