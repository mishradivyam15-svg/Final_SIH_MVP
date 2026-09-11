import { useCallback, useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import type { PrecursorStatus } from '@/types';
import { useAsync } from '@/hooks/useAsync';
import { getPrecursor, getRelationships, getReportsByIds } from '@/services/dataService';
import { AppShell } from '@/components/layout/AppShell';
import { PrecursorHeader } from '@/components/precursor/PrecursorHeader';
import { EvidencePanel } from '@/components/precursor/EvidencePanel';
import { ContributingReports } from '@/components/precursor/ContributingReports';
import { Timeline } from '@/components/precursor/Timeline';
import { ReviewActions } from '@/components/precursor/ReviewActions';
import { RelationshipGraph } from '@/components/graph/RelationshipGraph';
import { DetailHeaderSkeleton, ListSkeleton, GraphSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';

export default function PrecursorDetail() {
  const { id } = useParams<{ id: string }>();
  const [statusOverride, setStatusOverride] = useState<PrecursorStatus | null>(null);

  const fetchPrecursor = useCallback(() => {
    if (!id) return Promise.reject(new Error('Missing precursor id'));
    return getPrecursor(id);
  }, [id]);
  const fetchGraph = useCallback(() => {
    if (!id) return Promise.resolve({ nodes: [], edges: [] });
    return getRelationships(id);
  }, [id]);

  const {
    data: precursor,
    loading: precursorLoading,
    error: precursorError,
    refetch: refetchPrecursor,
  } = useAsync(fetchPrecursor, [id]);

  const { data: graph, loading: graphLoading, error: graphError } = useAsync(fetchGraph, [id]);

  const fetchReports = useCallback(() => {
    if (!precursor) return Promise.resolve([]);
    return getReportsByIds(precursor.reportIds);
  }, [precursor]);

  const { data: reports, loading: reportsLoading, error: reportsError } = useAsync(
    fetchReports,
    [precursor?.id]
  );

  if (!id) return <Navigate to="/dashboard" replace />;

  if (precursorError) {
    return (
      <AppShell>
        <ErrorState message={precursorError} onRetry={refetchPrecursor} />
      </AppShell>
    );
  }

  if (precursorLoading || !precursor) {
    return (
      <AppShell>
        <div className="space-y-6">
          <DetailHeaderSkeleton />
          <ListSkeleton rows={2} />
        </div>
      </AppShell>
    );
  }

  const effectiveStatus = statusOverride ?? precursor.status;

  return (
    <AppShell>
      <div className="space-y-6">
        <PrecursorHeader precursor={{ ...precursor, status: effectiveStatus }} />

        <EvidencePanel precursor={precursor} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {graphLoading ? (
            <GraphSkeleton />
          ) : graphError ? (
            <ErrorState message={graphError} />
          ) : (
            <RelationshipGraph data={graph ?? { nodes: [], edges: [] }} />
          )}

          {reportsLoading ? (
            <ListSkeleton rows={2} />
          ) : reportsError ? (
            <ErrorState message={reportsError} />
          ) : (
            <Timeline reports={reports ?? []} precursorTitle={precursor.title} />
          )}
        </div>

        {reportsLoading ? (
          <ListSkeleton rows={3} />
        ) : reportsError ? (
          <ErrorState message={reportsError} />
        ) : (
          <ContributingReports reports={reports ?? []} />
        )}

        <ReviewActions
          precursorId={precursor.id}
          currentStatus={effectiveStatus}
          onStatusChange={(status) => setStatusOverride(status)}
        />
      </div>
    </AppShell>
  );
}
