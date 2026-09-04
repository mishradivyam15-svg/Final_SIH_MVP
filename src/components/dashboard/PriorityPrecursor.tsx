import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, Users, Clock3, ArrowRight } from 'lucide-react';
import type { Precursor } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { PRIORITY_CLASSES } from '@/lib/display';

interface PriorityPrecursorProps {
  precursor: Precursor;
}

export function PriorityPrecursor({ precursor }: PriorityPrecursorProps) {
  const navigate = useNavigate();

  return (
    <section
      aria-labelledby="priority-precursor-heading"
      className="rounded-lg border-2 border-priority-highBorder bg-white p-6 shadow-panel"
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <Flame size={16} className="text-priority-high" aria-hidden="true" />
        <span className="text-xs font-semibold uppercase tracking-wide text-priority-high">
          Top Priority Alert
        </span>
        <PriorityBadge priority={precursor.priority} />
        <StatusBadge status={precursor.status} />
      </div>

      <h2 id="priority-precursor-heading" className="text-xl font-bold text-ink-900">
        {precursor.title}
      </h2>
      <p className="mt-2 max-w-3xl text-sm text-ink-700">{precursor.shortExplanation}</p>

      <div className="mt-5 rounded-md bg-surface-subtle p-3">
        <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wide text-ink-500">
          <span>Risk score</span>
          <span className="text-ink-900">{precursor.riskScore} / 100</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-ink-200" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={precursor.riskScore} aria-label={`Risk score ${precursor.riskScore} out of 100`}>
          <div className={`h-full rounded-full transition-all ${PRIORITY_CLASSES[precursor.priority].dot}`} style={{ width: `${Math.min(100, Math.max(0, precursor.riskScore))}%` }} />
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Metric label="Risk Score" value={`${precursor.riskScore} / 100`} />
        <Metric label="Hazard" value={precursor.hazard} />
        <Metric label="Activity" value={precursor.activity} />
        <Metric label="Barrier Failure" value={precursor.barrierFailure} />
        <Metric
          label="Related Reports"
          value={String(precursor.reportCount)}
          icon={<Users size={13} className="text-ink-400" aria-hidden="true" />}
        />
        <Metric
          label="Recurrence"
          value={`${precursor.reportCount} reports / ${precursor.recurrenceWindowDays}d`}
          icon={<Clock3 size={13} className="text-ink-400" aria-hidden="true" />}
        />
      </div>

      <div className="mt-6 flex items-center justify-between">
        <span className="text-xs text-ink-400">Site/context: {precursor.site}</span>
        <Button onClick={() => navigate(`/precursors/${precursor.id}`)}>
          View Evidence
          <ArrowRight size={15} aria-hidden="true" />
        </Button>
      </div>
    </section>
  );
}

function Metric({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon?: ReactNode;
}) {
  return (
    <div>
      <p className="flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-ink-400">
        {icon}
        {label}
      </p>
      <p className="mt-0.5 truncate text-sm font-semibold text-ink-900" title={value}>
        {value}
      </p>
    </div>
  );
}
