import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import type { Precursor, SafetyReport } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { EmptyState } from '@/components/common/EmptyState';
import { Link2Off } from 'lucide-react';
import { formatDate } from '@/lib/date';

export function RelatedPrecursor({ precursor }: { precursor: Precursor | null }) {
  const navigate = useNavigate();

  if (!precursor) {
    return (
      <EmptyState
        icon={Link2Off}
        title="No related precursor"
        description="This report has not yet been grouped into a recurring precursor pattern."
      />
    );
  }

  return (
    <section className="rounded-lg border border-ink-300/40 bg-white p-5 shadow-card">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-500">
        Related SIF Precursor
      </h2>
      <button
        onClick={() => navigate(`/precursors/${precursor.id}`)}
        className="flex w-full items-center justify-between rounded-md border border-ink-300/40 bg-surface-subtle p-4 text-left hover:bg-surface-muted"
      >
        <div>
          <PriorityBadge priority={precursor.priority} className="mb-2" />
          <p className="text-sm font-semibold text-ink-900">{precursor.title}</p>
          <p className="text-xs text-ink-500">Risk score {precursor.riskScore}/100</p>
        </div>
        <ArrowRight size={18} className="text-brand-600" aria-hidden="true" />
      </button>
    </section>
  );
}

export function RelatedReports({ reports }: { reports: SafetyReport[] }) {
  const navigate = useNavigate();

  if (reports.length === 0) {
    return null;
  }

  return (
    <section className="rounded-lg border border-ink-300/40 bg-white p-5 shadow-card">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-500">
        Other Related Reports
      </h2>
      <ul className="space-y-2">
        {reports.map((r) => (
          <li key={r.id}>
            <button
              onClick={() => navigate(`/reports/${r.id}`)}
              className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-surface-subtle"
            >
              <span className="font-medium text-brand-700">{r.displayId}</span>
              <span className="text-xs text-ink-500">{formatDate(r.date)}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
