import { ShieldCheck, RefreshCw } from 'lucide-react';
import { DemoDataBadge } from '@/components/common/DemoDataBadge';
import { formatDateTime, formatRelativeTime } from '@/lib/date';
import { isMockMode } from '@/services/dataService';
import { useNow } from '@/hooks/useNow';

interface HeaderProps {
  lastUpdated?: string;
  onRefresh?: () => void;
  refreshing?: boolean;
  /** A background poll is in flight — shown on the live indicator. */
  syncing?: boolean;
}

export function Header({ lastUpdated, onRefresh, refreshing, syncing }: HeaderProps) {
  const now = useNow();

  return (
    <header className="panel-sheen relative bg-surface">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-glow">
            <span
              className="absolute inset-0 animate-pulse-glow rounded-xl bg-brand-500/30 blur-md"
              aria-hidden="true"
            />
            <ShieldCheck size={20} className="relative" aria-hidden="true" />
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
          {isMockMode ? (
            <DemoDataBadge />
          ) : (
            <span
              className={`inline-flex items-center gap-2 rounded-md border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide transition-colors duration-300 ${
                syncing
                  ? 'border-brand-300/50 bg-brand-950 text-brand-300'
                  : 'border-priority-lowBorder/60 bg-priority-lowBg text-priority-low'
              }`}
              title={
                syncing
                  ? 'Fetching the latest analysis results…'
                  : 'Connected to the live analysis backend — refreshes automatically'
              }
            >
              <span className="relative flex h-1.5 w-1.5">
                <span
                  className={`absolute inline-flex h-full w-full animate-pulse-ring rounded-full ${
                    syncing ? 'bg-brand-400' : 'bg-priority-low'
                  }`}
                />
                <span
                  className={`relative inline-flex h-1.5 w-1.5 rounded-full ${
                    syncing ? 'bg-brand-400' : 'bg-priority-low'
                  }`}
                />
              </span>
              {syncing ? 'Syncing' : 'Live'}
            </span>
          )}
          {lastUpdated && (
            <span
              className="hidden font-mono text-xs tabular-nums text-ink-500 sm:inline"
              title={`Last updated ${formatDateTime(lastUpdated)}`}
            >
              Updated {formatRelativeTime(lastUpdated, now)}
            </span>
          )}
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="inline-flex transform-gpu items-center gap-1.5 rounded-md border border-ink-300 bg-surface px-3 py-1.5 text-xs font-medium text-ink-700 transition-all duration-200 ease-out hover:scale-105 hover:border-brand-300 hover:bg-surface-subtle hover:text-brand-300 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
              aria-label="Refresh dashboard data"
            >
              <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} aria-hidden="true" />
              Refresh
            </button>
          )}
        </div>
      </div>
      <div className="h-px bg-gradient-to-r from-transparent via-ink-300/60 to-transparent" />
    </header>
  );
}
