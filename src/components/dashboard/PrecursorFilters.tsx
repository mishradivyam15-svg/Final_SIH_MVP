import { Search, X } from 'lucide-react';
import type { PrecursorFilters as FiltersType, Priority, PrecursorStatus } from '@/types';
import { PRIORITY_LABEL, STATUS_LABEL } from '@/lib/display';

interface PrecursorFiltersProps {
  filters: FiltersType;
  onChange: (filters: FiltersType) => void;
  sites: string[];
  hazards: string[];
  activities: string[];
}

const PRIORITIES: (Priority | 'ALL')[] = ['ALL', 'HIGH', 'MEDIUM', 'LOW'];
const STATUSES: (PrecursorStatus | 'ALL')[] = [
  'ALL',
  'OPEN',
  'UNDER_INVESTIGATION',
  'CONFIRMED',
  'DISMISSED',
];

export function PrecursorFilters({
  filters,
  onChange,
  sites,
  hazards,
  activities,
}: PrecursorFiltersProps) {
  const hasActiveFilters =
    !!filters.search ||
    (filters.priority && filters.priority !== 'ALL') ||
    (filters.site && filters.site !== 'ALL') ||
    (filters.hazard && filters.hazard !== 'ALL') ||
    (filters.activity && filters.activity !== 'ALL') ||
    (filters.status && filters.status !== 'ALL');

  const selectCls =
    'rounded-md border border-ink-300 bg-white px-2.5 py-1.5 text-xs text-ink-700 focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600';

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-ink-300/40 bg-white p-3 shadow-card">
      <div className="relative min-w-[200px] flex-1">
        <Search
          size={14}
          className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-ink-400"
          aria-hidden="true"
        />
        <input
          type="search"
          value={filters.search ?? ''}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          placeholder="Search precursors, hazards, sites…"
          aria-label="Search precursor patterns"
          className="w-full rounded-md border border-ink-300 bg-white py-1.5 pl-8 pr-2.5 text-xs text-ink-700 focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600"
        />
      </div>

      <label className="sr-only" htmlFor="filter-priority">
        Priority
      </label>
      <select
        id="filter-priority"
        className={selectCls}
        value={filters.priority ?? 'ALL'}
        onChange={(e) => onChange({ ...filters, priority: e.target.value as Priority | 'ALL' })}
      >
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p === 'ALL' ? 'All priorities' : PRIORITY_LABEL[p]}
          </option>
        ))}
      </select>

      <label className="sr-only" htmlFor="filter-site">
        Site
      </label>
      <select
        id="filter-site"
        className={selectCls}
        value={filters.site ?? 'ALL'}
        onChange={(e) => onChange({ ...filters, site: e.target.value })}
      >
        <option value="ALL">All sites</option>
        {sites.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      <label className="sr-only" htmlFor="filter-hazard">
        Hazard
      </label>
      <select
        id="filter-hazard"
        className={selectCls}
        value={filters.hazard ?? 'ALL'}
        onChange={(e) => onChange({ ...filters, hazard: e.target.value })}
      >
        <option value="ALL">All hazards</option>
        {hazards.map((h) => (
          <option key={h} value={h}>
            {h}
          </option>
        ))}
      </select>

      <label className="sr-only" htmlFor="filter-activity">
        Activity
      </label>
      <select
        id="filter-activity"
        className={selectCls}
        value={filters.activity ?? 'ALL'}
        onChange={(e) => onChange({ ...filters, activity: e.target.value })}
      >
        <option value="ALL">All activities</option>
        {activities.map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>

      <label className="sr-only" htmlFor="filter-status">
        Status
      </label>
      <select
        id="filter-status"
        className={selectCls}
        value={filters.status ?? 'ALL'}
        onChange={(e) => onChange({ ...filters, status: e.target.value as PrecursorStatus | 'ALL' })}
      >
        {STATUSES.map((s) => (
          <option key={s} value={s}>
            {s === 'ALL' ? 'All statuses' : STATUS_LABEL[s]}
          </option>
        ))}
      </select>

      {hasActiveFilters && (
        <button
          onClick={() => onChange({})}
          className="inline-flex items-center gap-1 rounded-md px-2 py-1.5 text-xs font-medium text-ink-500 hover:bg-surface-muted hover:text-ink-900"
        >
          <X size={13} aria-hidden="true" />
          Clear filters
        </button>
      )}
    </div>
  );
}
