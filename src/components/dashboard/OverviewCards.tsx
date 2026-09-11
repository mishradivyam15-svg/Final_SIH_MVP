import { FileText, GitMerge, AlertTriangle, ClipboardList } from 'lucide-react';
import type { DashboardOverview } from '@/types';

interface OverviewCardsProps {
  overview: DashboardOverview;
}

export function OverviewCards({ overview }: OverviewCardsProps) {
  const items = [
    {
      label: 'Reports Analyzed',
      value: overview.reportsAnalyzed,
      icon: FileText,
      hint: 'Unsafe-act, unsafe-condition & near-miss reports processed',
    },
    {
      label: 'Precursor Patterns',
      value: overview.precursorPatternCount,
      icon: GitMerge,
      hint: 'Recurring cross-report patterns identified',
    },
    {
      label: 'High Priority Patterns',
      value: overview.highPriorityCount,
      icon: AlertTriangle,
      hint: 'Patterns flagged as high risk',
    },
    {
      label: 'Review Queue',
      value: overview.reviewQueueCount,
      icon: ClipboardList,
      hint: 'Awaiting HSE decision',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map(({ label, value, icon: Icon, hint }) => (
        <div
          key={label}
          className="rounded-lg border border-ink-300/40 bg-white p-4 shadow-card"
        >
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wide text-ink-500">
              {label}
            </span>
            <Icon size={16} className="text-brand-600" aria-hidden="true" />
          </div>
          <p className="text-2xl font-bold text-ink-900">{value.toLocaleString('en-IN')}</p>
          <p className="mt-1 text-xs text-ink-400">{hint}</p>
        </div>
      ))}
    </div>
  );
}
