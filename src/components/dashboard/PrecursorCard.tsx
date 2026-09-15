import { useNavigate } from 'react-router-dom';
import { Users, Clock3, ShieldAlert } from 'lucide-react';
import type { Precursor } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { PRIORITY_CLASSES } from '@/lib/display';
import { useCountUp } from '@/hooks/useCountUp';
import { useSpotlight } from '@/hooks/useSpotlight';
import { useChangeFlash } from '@/hooks/useChangeFlash';

interface PrecursorCardProps {
  precursor: Precursor;
  index?: number;
}

export function PrecursorCard({ precursor, index = 0 }: PrecursorCardProps) {
  const navigate = useNavigate();
  const accent = PRIORITY_CLASSES[precursor.priority];
  const animatedScore = useCountUp(precursor.riskScore);
  const { ref, onMouseMove } = useSpotlight<HTMLElement>();
  const scoreChanged = useChangeFlash(precursor.riskScore);

  return (
    <article
      ref={ref}
      onMouseMove={onMouseMove}
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
      data-cursor-tone={precursor.priority.toLowerCase()}
      style={{ animationDelay: `${Math.min(index, 8) * 50}ms` }}
      className={`spotlight panel-sheen group relative flex animate-fade-in-up cursor-pointer flex-col overflow-hidden rounded-xl border bg-surface p-4 shadow-card transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-panel focus:outline-none focus:ring-2 focus:ring-brand-600 ${accent.border}`}
    >
      <span
        className={`absolute inset-x-0 top-0 h-0.5 transition-opacity duration-300 group-hover:animate-pulse-glow ${accent.dot}`}
        aria-hidden="true"
      />
      <div className="relative mb-2 flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <PriorityBadge priority={precursor.priority} />
          {precursor.sifPotential && (
            <span className="inline-flex animate-breathe items-center gap-1 rounded-md bg-priority-highBg px-1.5 py-0.5 text-[10px] font-semibold text-priority-high ring-1 ring-priority-high/30">
              <ShieldAlert size={10} aria-hidden="true" />
              SIF
            </span>
          )}
        </div>
        <span
          className={`whitespace-nowrap font-mono text-sm font-bold tabular-nums text-ink-900 ${
            scoreChanged ? 'value-flash' : ''
          }`}
        >
          {animatedScore}
          <span className="text-xs font-normal text-ink-400">/100</span>
        </span>
      </div>

      <h3 className="text-sm font-semibold text-ink-900">{precursor.title}</h3>

      <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
        <Field label="Hazard" value={precursor.hazard} />
        <Field label="Barrier Failure" value={precursor.barrierFailure} />
        <Field label="Site" value={precursor.site} />
        <Field label="Activity" value={precursor.activity} />
        {precursor.iogpRule && <Field label="IOGP Rule" value={precursor.iogpRule} />}
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
  const isUnknown = /^unknown /i.test(value);
  return (
    <div className="min-w-0">
      <dt className="text-[10px] font-medium uppercase tracking-wide text-ink-400">{label}</dt>
      <dd
        className={`truncate ${isUnknown ? 'italic text-ink-400' : 'text-ink-700'}`}
        title={value}
      >
        {isUnknown ? 'Not detected' : value}
      </dd>
    </div>
  );
}
