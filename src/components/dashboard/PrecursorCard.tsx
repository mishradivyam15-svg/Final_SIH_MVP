import { useNavigate } from 'react-router-dom';
import { Users, Clock3 } from 'lucide-react';
import type { Precursor } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { PRIORITY_CLASSES } from '@/lib/display';

interface PrecursorCardProps {
  precursor: Precursor;
}

export function PrecursorCard({ precursor }: PrecursorCardProps) {
  const navigate = useNavigate();
  const accent = PRIORITY_CLASSES[precursor.priority];

  return (
    <article
      onClick={() => navigate(`/precursors/${precursor.id}`)}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          navigate(`/precursors/${precursor.id}`);
        }
      }}
      tabIndex={0}
      role="link"
      aria-label={`Open evidence for ${precursor.title}`}
      className={`group flex cursor-pointer flex-col rounded-lg border bg-white p-4 shadow-card transition-all hover:-translate-y-0.5 hover:shadow-panel focus:outline-none focus:ring-2 focus:ring-brand-600 ${accent.border}`}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <PriorityBadge priority={precursor.priority} />
        <span className="whitespace-nowrap text-sm font-bold text-ink-900">
          {precursor.riskScore}
          <span className="text-xs font-normal text-ink-400">/100</span>
        </span>
      </div>

      <h3 className="text-sm font-semibold text-ink-900">{precursor.title}</h3>

      <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
        <Field label="Hazard" value={precursor.hazard} />
        <Field label="Barrier Failure" value={precursor.barrierFailure} />
        <Field label="Site" value={precursor.site} />
        <Field label="Activity" value={precursor.activity} />
      </dl>

      <div className="mt-3 flex items-center gap-4 text-xs text-ink-500">
        <span className="flex items-center gap-1">
          <Users size={12} aria-hidden="true" /> {precursor.reportCount} reports
        </span>
        <span className="flex items-center gap-1">
          <Clock3 size={12} aria-hidden="true" /> {precursor.recurrenceWindowDays}d window
        </span>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-ink-300/30 pt-3">
        <StatusBadge status={precursor.status} />
        <Button
          size="sm"
          variant="secondary"
          onClick={(event) => {
            event.stopPropagation();
            navigate(`/precursors/${precursor.id}`);
          }}
        >
          View Evidence
        </Button>
      </div>
    </article>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-[10px] font-medium uppercase tracking-wide text-ink-400">{label}</dt>
      <dd className="truncate text-ink-700" title={value}>
        {value}
      </dd>
    </div>
  );
}
