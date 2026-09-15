import { useCallback } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useAsync } from '@/hooks/useAsync';
import { getReport, getPrecursor, getReportsByIds } from '@/services/dataService';
import { AppShell } from '@/components/layout/AppShell';
import { ReportHeader } from '@/components/report/ReportHeader';
import { RawReport } from '@/components/report/RawReport';
import { SafetySignals } from '@/components/report/SafetySignals';
import { RelatedPrecursor, RelatedReports } from '@/components/report/RelatedPrecursor';
import { DetailHeaderSkeleton, ListSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { ArrowRight, FileText, GitBranch, Network, ShieldAlert } from 'lucide-react';
import type { Precursor, SafetyReport } from '@/types';

export default function ReportDetail() {
  const { id } = useParams<{ id: string }>();

  const fetchReport = useCallback(() => {
    if (!id) return Promise.reject(new Error('Missing report id'));
    return getReport(id);
  }, [id]);

  const { data: report, loading, error, refetch } = useAsync(fetchReport, [id]);

  const fetchPrecursor = useCallback((): Promise<Precursor | null> => {
    const precursorId = report?.precursorIds[0];
    if (!precursorId) return Promise.resolve(null);
    return getPrecursor(precursorId);
  }, [report]);

  const { data: precursor } = useAsync(fetchPrecursor, [report?.id]);

  const fetchRelatedReports = useCallback((): Promise<SafetyReport[]> => {
    if (!precursor || !report) return Promise.resolve([]);
    return getReportsByIds(precursor.reportIds.filter((rid) => rid !== report.id));
  }, [precursor, report]);

  const { data: relatedReports } = useAsync(fetchRelatedReports, [precursor?.id, report?.id]);

  if (!id) return <Navigate to="/dashboard" replace />;

  if (error) {
    return (
      <AppShell>
        <ErrorState message={error} onRetry={refetch} />
      </AppShell>
    );
  }

  if (loading || !report) {
    return (
      <AppShell>
        <div className="space-y-6">
          <DetailHeaderSkeleton />
          <ListSkeleton rows={2} />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <ReportHeader report={report} />

        {/* Transformation strip — makes the pipeline visually obvious */}
        <div className="flex flex-wrap items-center gap-2 rounded-xl panel-sheen border border-ink-300/40 bg-surface px-4 py-3 shadow-card text-xs font-medium text-ink-500">
          <span className="flex items-center gap-1.5 rounded bg-surface-muted px-2 py-1">
            <FileText size={13} aria-hidden="true" /> Raw Report
          </span>
          <ArrowRight size={13} aria-hidden="true" />
          <span className="flex items-center gap-1.5 rounded bg-surface-muted px-2 py-1">
            <GitBranch size={13} aria-hidden="true" /> Extracted Safety Signals
          </span>
          <ArrowRight size={13} aria-hidden="true" />
          <span className="flex items-center gap-1.5 rounded bg-surface-muted px-2 py-1">
            <Network size={13} aria-hidden="true" /> Related Reports
          </span>
          <ArrowRight size={13} aria-hidden="true" />
          <span className="flex items-center gap-1.5 rounded bg-priority-highBg px-2 py-1 text-priority-high">
            <ShieldAlert size={13} aria-hidden="true" /> SIF Precursor
          </span>
        </div>

        <RawReport narrative={report.narrative} />
        <SafetySignals report={report} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <RelatedPrecursor precursor={precursor ?? null} />
          <RelatedReports reports={relatedReports ?? []} />
        </div>
      </div>
    </AppShell>
  );
}
