import type { CSSProperties, ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, Users, Clock3, ArrowRight } from 'lucide-react';
import type { Precursor, Priority } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/common/Button';
import { PRIORITY_CLASSES } from '@/lib/display';
import { useCountUp } from '@/hooks/useCountUp';

interface PriorityPrecursorProps {
  precursor: Precursor;
}

/** Drives the rotating conic border, matched to the alert's severity. */
const SWEEP_COLOR: Record<Priority, string> = {
  HIGH: 'rgba(248, 113, 113, 0.95)',
  MEDIUM: 'rgba(251, 191, 36, 0.95)',
  LOW: 'rgba(74, 222, 128, 0.9)',
};

export function PriorityPrecursor({ precursor }: PriorityPrecursorProps) {
  const navigate = useNavigate();
  const accent = PRIORITY_CLASSES[precursor.priority];
  const animatedScore = useCountUp(precursor.riskScore);

  // Fill starts at 0 and animates to the real width just after mount, so
  // the bar genuinely grows in rather than appearing pre-filled.
  const [fillWidth, setFillWidth] = useState(0);
  useEffect(() => {
    const frame = requestAnimationFrame(() =>
      setFillWidth(Math.min(100, Math.max(0, precursor.riskScore)))
    );
    return () => cancelAnimationFrame(frame);
  }, [precursor.riskScore]);

  return (
    <section
      aria-labelledby="priority-precursor-heading"
      data-cursor-tone={precursor.priority.toLowerCase()}
      style={{ '--sweep-color': SWEEP_COLOR[precursor.priority] } as CSSProperties}
      className={`sweep-border panel-sheen relative animate-fade-in-up overflow-hidden rounded-xl border-2 bg-surface p-6 shadow-panel ${accent.border}`}
    >
      <span
        className={`absolute inset-x-0 top-0 h-1 animate-pulse-glow ${accent.dot}`}
        aria-hidden="true"
      />
      {/* Ambient halo bleeding from the accent edge — keeps the card feeling live. */}
      <span
        className={`pointer-events-none absolute -top-16 left-1/2 h-32 w-2/3 -translate-x-1/2 animate-pulse-glow rounded-full opacity-20 blur-3xl ${accent.dot}`}
        aria-hidden="true"
      />
      <div className="relative mb-4 flex flex-wrap items-center gap-2">
        <Flame size={16} className={`animate-breathe ${accent.text}`} aria-hidden="true" />
        <span className={`text-xs font-semibold uppercase tracking-wide ${accent.text}`}>
          Top Priority Alert
        </span>
        <PriorityBadge priority={precursor.priority} />
        <StatusBadge status={precursor.status} />
      </div>

      <h2 id="priority-precursor-heading" className="text-xl font-bold tracking-tight text-ink-900">
        {precursor.title}
      </h2>
      <p className="mt-2 max-w-3xl text-sm text-ink-700">{precursor.shortExplanation}</p>

      <div className="mt-5 rounded-xl bg-surface-subtle p-3">
        <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wide text-ink-500">
          <span>Risk score</span>
          <span className="font-mono tabular-nums text-ink-900">{animatedScore} / 100</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-muted" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={precursor.riskScore} aria-label={`Risk score ${precursor.riskScore} out of 100`}>
          <div
            className={`relative h-full overflow-hidden rounded-full transition-[width] duration-[900ms] ease-out ${accent.dot} ${accent.text}`}
            style={{ width: `${fillWidth}%`, boxShadow: `0 0 12px -2px currentColor` }}
          >
            {/* Light sweeping across the fill — reads as a live, monitored value. */}
            <span
              className="absolute inset-0 animate-sweep bg-[length:200%_100%] bg-gradient-to-r from-transparent via-white/40 to-transparent"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Metric label="Risk Score" value={`${animatedScore} / 100`} />
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
  const isUnknown = /^unknown /i.test(value);
  return (
    <div>
      <p className="flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-ink-400">
        {icon}
        {label}
      </p>
      <p
        className={`mt-0.5 truncate text-sm font-semibold ${
          isUnknown ? 'font-normal italic text-ink-400' : 'text-ink-900'
        }`}
        title={value}
      >
        {isUnknown ? 'Not detected' : value}
      </p>
    </div>
  );
}
