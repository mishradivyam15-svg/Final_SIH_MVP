import { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import type { PrecursorFilters as FiltersType } from '@/types';
import { useAsync } from '@/hooks/useAsync';
import { getDashboard } from '@/services/dataService';
import { AppShell } from '@/components/layout/AppShell';
import { OverviewCards } from '@/components/dashboard/OverviewCards';
import { PriorityPrecursor } from '@/components/dashboard/PriorityPrecursor';
import { PrecursorCard } from '@/components/dashboard/PrecursorCard';
import { PrecursorFilters } from '@/components/dashboard/PrecursorFilters';
import { ReviewQueue } from '@/components/dashboard/ReviewQueue';
import { PriorityDistributionChart } from '@/components/dashboard/PriorityDistributionChart';
import { OverviewCardsSkeleton, ListSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { SearchX } from 'lucide-react';

/** How often the dashboard re-polls the backend in the background. */
const POLL_INTERVAL_MS = 15_000;

export default function Dashboard() {
  const { data, loading, error, refetch, syncing } = useAsync(getDashboard, [], {
    pollMs: POLL_INTERVAL_MS,
  });
  const [filters, setFilters] = useState<FiltersType>({});
  const location = useLocation();

  useEffect(() => {
    const hash = window.location.hash;
    if (!hash) return;

    const scrollToHash = () => {
      document.getElementById(hash.slice(1))?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    };

    const frame = window.requestAnimationFrame(scrollToHash);
    return () => window.cancelAnimationFrame(frame);
  }, [location.hash]);

  const { sites, hazards, activities } = useMemo(() => {
    const precursors = data?.precursors ?? [];
    return {
      sites: Array.from(new Set(precursors.map((p) => p.site))).sort(),
      hazards: Array.from(new Set(precursors.map((p) => p.hazard))).sort(),
      activities: Array.from(new Set(precursors.map((p) => p.activity))).sort(),
    };
  }, [data]);

  const filteredPrecursors = useMemo(() => {
    if (!data) return [];
    const { search, priority, site, hazard, activity, status } = filters;
    return data.precursors.filter((p) => {
      if (search && search.trim()) {
        const q = search.trim().toLowerCase();
        const haystack = `${p.title} ${p.hazard} ${p.activity} ${p.barrierFailure} ${p.site}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (priority && priority !== 'ALL' && p.priority !== priority) return false;
      if (site && site !== 'ALL' && p.site !== site) return false;
      if (hazard && hazard !== 'ALL' && p.hazard !== hazard) return false;
      if (activity && activity !== 'ALL' && p.activity !== activity) return false;
      if (status && status !== 'ALL' && p.status !== status) return false;
      return true;
    });
  }, [data, filters]);

  if (error) {
    return (
      <AppShell>
        <ErrorState message={error} onRetry={refetch} />
      </AppShell>
    );
  }

  return (
    <AppShell
      lastUpdated={data?.overview.lastUpdated}
      onRefresh={refetch}
      refreshing={loading}
      syncing={syncing}
    >
      <div className="space-y-6">
        {loading || !data ? (
          <OverviewCardsSkeleton />
        ) : (
          <OverviewCards overview={data.overview} />
        )}

        {loading || !data ? (
          <ListSkeleton rows={1} />
        ) : data.topPrecursor ? (
          <PriorityPrecursor precursor={data.topPrecursor} />
        ) : (
          <EmptyState
            title="No priority precursor to display"
            description="No precursor patterns are currently loaded in the dataset."
          />
        )}

        <div
          id="precursors"
          className="grid animate-fade-in-up grid-cols-1 gap-6 lg:grid-cols-3"
          style={{ animationDelay: '80ms' }}
        >
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
              Precursor Patterns
            </h2>
            <PrecursorFilters
              filters={filters}
              onChange={setFilters}
              sites={sites}
              hazards={hazards}
              activities={activities}
            />

            {loading || !data ? (
              <ListSkeleton rows={3} />
            ) : filteredPrecursors.length === 0 ? (
              <EmptyState
                icon={SearchX}
                title="No precursor patterns match the current filters."
                description="Try adjusting or clearing your filters."
                action={
                  <button
                    onClick={() => setFilters({})}
                    className="inline-block transform-gpu text-xs font-semibold text-brand-300 transition-all duration-200 ease-out hover:scale-110 hover:underline active:scale-100"
                  >
                    Clear filters
                  </button>
                }
              />
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {filteredPrecursors.map((p, i) => (
                  <PrecursorCard key={p.id} precursor={p} index={i} />
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
              At a Glance
            </h2>
            {loading || !data ? (
              <ListSkeleton rows={1} />
            ) : (
              <PriorityDistributionChart precursors={data.precursors} />
            )}
          </div>
        </div>

        <div
          id="review-queue"
          className="animate-fade-in-up space-y-4"
          style={{ animationDelay: '140ms' }}
        >
          <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
            Review Queue
          </h2>
          {loading || !data ? (
            <ListSkeleton rows={2} />
          ) : (
            <ReviewQueue items={data.reviewQueue} />
          )}
        </div>
      </div>
    </AppShell>
  );
}
