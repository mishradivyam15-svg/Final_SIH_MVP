import type { LucideIcon } from 'lucide-react';
import { FileText, GitMerge, AlertTriangle, ClipboardList } from 'lucide-react';
import type { DashboardOverview } from '@/types';
import { useCountUp } from '@/hooks/useCountUp';
import { useSpotlight } from '@/hooks/useSpotlight';
import { useChangeFlash } from '@/hooks/useChangeFlash';

type Tone = 'neutral' | 'high' | 'brand';

const TONE_ICON: Record<Tone, string> = {
  neutral: 'bg-surface-muted text-ink-500',
  high: 'bg-priority-highBg text-priority-high',
  brand: 'bg-brand-950 text-brand-300',
};
const TONE_ACCENT: Record<Tone, string> = {
  neutral: 'bg-transparent',
  high: 'bg-priority-high',
  brand: 'bg-brand-600',
};

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
      tone: 'neutral' as const,
    },
    {
      label: 'Precursor Patterns',
      value: overview.precursorPatternCount,
      icon: GitMerge,
      hint: 'Recurring cross-report patterns identified',
      tone: 'neutral' as const,
    },
    {
      label: 'High Priority Patterns',
      value: overview.highPriorityCount,
      icon: AlertTriangle,
      hint: 'Patterns flagged as high risk',
      tone: overview.highPriorityCount > 0 ? ('high' as const) : ('neutral' as const),
    },
    {
      label: 'Review Queue',
      value: overview.reviewQueueCount,
      icon: ClipboardList,
      hint: 'Awaiting HSE decision',
      tone: overview.reviewQueueCount > 0 ? ('brand' as const) : ('neutral' as const),
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item, i) => (
        <StatCard key={item.label} {...item} delayMs={i * 60} />
      ))}
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  hint,
  tone,
  delayMs,
}: {
  label: string;
  value: number;
  icon: LucideIcon;
  hint: string;
  tone: Tone;
  delayMs: number;
}) {
  const animated = useCountUp(value);
  const { ref, onMouseMove } = useSpotlight<HTMLDivElement>();
  const isLive = tone !== 'neutral';
  const justChanged = useChangeFlash(value);

  return (
    <div
      ref={ref}
      onMouseMove={onMouseMove}
      className={`spotlight panel-sheen group relative animate-fade-in-up overflow-hidden rounded-xl border border-ink-300/40 bg-surface p-4 shadow-card transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-panel ${
        justChanged ? 'card-flash' : ''
      }`}
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <span
        className={`absolute inset-x-0 top-0 h-0.5 ${TONE_ACCENT[tone]} ${
          isLive ? 'animate-pulse-glow' : ''
        }`}
        aria-hidden="true"
      />
      <div className="relative mb-3 flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-500">{label}</span>
        <span
          className={`flex h-7 w-7 items-center justify-center rounded-md transition-transform duration-300 group-hover:scale-110 ${TONE_ICON[tone]}`}
        >
          <Icon size={14} aria-hidden="true" />
        </span>
      </div>
      <p
        className={`relative font-mono text-[28px] font-semibold leading-none tabular-nums text-ink-900 ${
          justChanged ? 'value-flash' : ''
        }`}
      >
        {animated.toLocaleString('en-IN')}
      </p>
      <p className="relative mt-2 text-xs leading-snug text-ink-400">{hint}</p>
    </div>
  );
}
