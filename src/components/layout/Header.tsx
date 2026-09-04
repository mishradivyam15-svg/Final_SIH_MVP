import { ShieldCheck, RefreshCw } from 'lucide-react';
import { DemoDataBadge } from '@/components/common/DemoDataBadge';
import { formatDateTime } from '@/lib/date';
import { isMockMode } from '@/services/dataService';

interface HeaderProps {
  lastUpdated?: string;
  onRefresh?: () => void;
  refreshing?: boolean;
}

export function Header({ lastUpdated, onRefresh, refreshing }: HeaderProps) {
  return (
    <header className="border-b border-ink-300/40 bg-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-700 text-white">
            <ShieldCheck size={20} aria-hidden="true" />
          </span>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-ink-900">NeuroNexus</h1>
              <span className="text-ink-300">|</span>
              <p className="text-sm font-medium text-ink-700">SIF Precursor Early Warning</p>
            </div>
            <p className="text-xs text-ink-500">
              Cross-report safety intelligence for recurring SIF precursors
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isMockMode && <DemoDataBadge />}
          {lastUpdated && (
            <span className="hidden text-xs text-ink-500 sm:inline">
              Updated {formatDateTime(lastUpdated)}
            </span>
          )}
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 rounded-md border border-ink-300 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 hover:bg-surface-subtle disabled:opacity-50"
              aria-label="Refresh dashboard data"
            >
              <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} aria-hidden="true" />
              Refresh
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
