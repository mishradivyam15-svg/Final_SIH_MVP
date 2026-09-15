import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileSearch, ShieldAlert } from 'lucide-react';
import type { SafetyReport } from '@/types';
import { useAsync } from '@/hooks/useAsync';
import { getAllReports } from '@/services/dataService';
import { AppShell } from '@/components/layout/AppShell';
import { Badge } from '@/components/common/Badge';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import { ListSkeleton } from '@/components/common/LoadingSkeleton';
import { formatDate } from '@/lib/date';
import { REPORT_TYPE_LABEL } from '@/lib/display';

export default function ReportsList() {
  const {
    data: reports,
    loading,
    error,
    refetch,
    syncing,
  } = useAsync(getAllReports, [], { pollMs: 15_000 });
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!reports) return [];
    const q = search.trim().toLowerCase();
    if (!q) return reports;
    return reports.filter((r) =>
      `${r.hazard} ${r.site} ${r.activity} ${r.narrative} ${r.displayId}`
        .toLowerCase()
        .includes(q)
    );
  }, [reports, search]);

  if (error) {
    return (
      <AppShell>
        <ErrorState message={error} onRetry={refetch} />
      </AppShell>
    );
  }

  return (
    <AppShell onRefresh={refetch} refreshing={loading} syncing={syncing}>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-ink-900">All Reports</h1>
            <p className="text-sm text-ink-500">
              Every safety narrative analyzed so far, most recent first.
            </p>
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search hazard, site, narrative..."
            className="w-full rounded-md border border-ink-300/60 px-3 py-2 text-sm shadow-sm focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600 sm:w-72"
          />
        </div>

        {loading || !reports ? (
          <ListSkeleton rows={4} />
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={FileSearch}
            title={reports.length === 0 ? 'No reports yet' : 'No reports match your search'}
            description={
              reports.length === 0
                ? 'Submit a safety report to see it appear here.'
                : 'Try a different search term.'
            }
            action={
              reports.length > 0 ? (
                <button
                  onClick={() => setSearch('')}
                  className="inline-block transform-gpu text-xs font-semibold text-brand-300 transition-all duration-200 ease-out hover:scale-110 hover:underline active:scale-100"
                >
                  Clear search
                </button>
              ) : undefined
            }
          />
        ) : (
          <div className="overflow-hidden rounded-xl panel-sheen border border-ink-300/40 bg-surface shadow-card">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-ink-300/40 bg-surface-subtle text-[10px] font-semibold uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="px-4 py-3">Report</th>
                  <th className="px-4 py-3">Hazard</th>
                  <th className="px-4 py-3">Site</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">SIF</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-300/30">
                {filtered.map((r) => (
                  <ReportRow key={r.id} report={r} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function ReportRow({ report }: { report: SafetyReport }) {
  const navigate = useNavigate();
  return (
    <tr
      onClick={() => navigate(`/reports/${report.id}`)}
      className="cursor-pointer transition hover:bg-surface-subtle"
    >
      <td className="px-4 py-3 font-medium text-ink-900">{report.displayId}</td>
      <td className="px-4 py-3 text-ink-700">{report.hazard}</td>
      <td className="px-4 py-3 text-ink-700">{report.site}</td>
      <td className="px-4 py-3">
        <Badge>{REPORT_TYPE_LABEL[report.type]}</Badge>
      </td>
      <td className="px-4 py-3 text-ink-500">{formatDate(report.date)}</td>
      <td className="px-4 py-3">
        {report.sifPotential ? (
          <span className="inline-flex items-center gap-1 rounded-md bg-priority-highBg px-2 py-0.5 text-xs font-semibold text-priority-high">
            <ShieldAlert size={12} aria-hidden="true" />
            Yes
          </span>
        ) : (
          <span className="text-xs text-ink-400">—</span>
        )}
      </td>
    </tr>
  );
}
