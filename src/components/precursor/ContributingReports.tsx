import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpDown, FileSearch } from 'lucide-react';
import type { SafetyReport } from '@/types';
import { EmptyState } from '@/components/common/EmptyState';
import { formatDate } from '@/lib/date';
import { REPORT_TYPE_LABEL } from '@/lib/display';

type SortKey = 'date' | 'similarity' | 'site';

interface ContributingReportsProps {
  reports: SafetyReport[];
}

export function ContributingReports({ reports }: ContributingReportsProps) {
  const [sortKey, setSortKey] = useState<SortKey>('similarity');
  const navigate = useNavigate();

  const sorted = useMemo(() => {
    const copy = [...reports];
    switch (sortKey) {
      case 'date':
        return copy.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      case 'site':
        return copy.sort((a, b) => a.site.localeCompare(b.site));
      case 'similarity':
      default:
        return copy.sort((a, b) => (b.relationshipScore ?? 0) - (a.relationshipScore ?? 0));
    }
  }, [reports, sortKey]);

  if (reports.length === 0) {
    return (
      <EmptyState
        icon={FileSearch}
        title="No contributing reports available"
        description="This precursor does not yet have linked reports in the current dataset."
      />
    );
  }

  return (
    <section className="rounded-lg border border-ink-300/40 bg-white shadow-card">
      <div className="flex items-center justify-between border-b border-ink-300/30 px-5 py-3">
        <h2 className="text-sm font-semibold text-ink-900">
          Contributing Reports ({reports.length})
        </h2>
        <div className="flex items-center gap-1.5 text-xs text-ink-500">
          <ArrowUpDown size={12} aria-hidden="true" />
          <label htmlFor="sort-reports" className="sr-only">
            Sort contributing reports
          </label>
          <select
            id="sort-reports"
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
            className="rounded-md border border-ink-300 bg-white px-2 py-1 text-xs focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600"
          >
            <option value="similarity">Relationship strength</option>
            <option value="date">Date</option>
            <option value="site">Site</option>
          </select>
        </div>
      </div>

      <ul className="divide-y divide-ink-300/20">
        {sorted.map((report) => (
          <li key={report.id}>
            <button
              onClick={() => navigate(`/reports/${report.id}`)}
              className="flex w-full flex-col gap-1 px-5 py-4 text-left hover:bg-surface-subtle"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-sm font-semibold text-brand-700">{report.displayId}</span>
                <div className="flex items-center gap-2 text-xs text-ink-500">
                  <span className="rounded bg-surface-muted px-1.5 py-0.5">
                    {REPORT_TYPE_LABEL[report.type]}
                  </span>
                  <span>{formatDate(report.date)}</span>
                  {typeof report.relationshipScore === 'number' && (
                    <span className="rounded bg-brand-50 px-1.5 py-0.5 font-medium text-brand-700">
                      {Math.round(report.relationshipScore * 100)}% match
                    </span>
                  )}
                </div>
              </div>
              <p className="text-xs text-ink-500">
                {report.site} · {report.activity} · {report.hazard}
                {report.barrier ? ` · ${report.barrier}` : ''}
              </p>
              <p className="mt-1 line-clamp-2 text-sm text-ink-700">{report.narrative}</p>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
