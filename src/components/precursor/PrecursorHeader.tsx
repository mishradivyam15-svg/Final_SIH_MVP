import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Users, Clock3 } from 'lucide-react';
import type { Precursor } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';

export function PrecursorHeader({ precursor }: { precursor: Precursor }) {
  const navigate = useNavigate();

  return (
    <div className="rounded-lg border border-ink-300/40 bg-white p-6 shadow-card">
      <button
        onClick={() => navigate('/dashboard')}
        className="mb-4 inline-flex items-center gap-1.5 text-xs font-medium text-ink-500 hover:text-ink-900"
      >
        <ArrowLeft size={14} aria-hidden="true" />
        Back to dashboard
      </button>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <PriorityBadge priority={precursor.priority} />
            <StatusBadge status={precursor.status} />
          </div>
          <h1 className="text-xl font-bold text-ink-900">{precursor.title}</h1>
          <p className="mt-1 flex items-center gap-1 text-sm text-ink-500">
            <MapPin size={13} aria-hidden="true" />
            {precursor.site}
          </p>
        </div>

        <div className="flex gap-6 rounded-md bg-surface-subtle px-5 py-3">
          <div className="text-center">
            <p className="text-2xl font-bold text-ink-900">{precursor.riskScore}</p>
            <p className="text-[10px] font-medium uppercase tracking-wide text-ink-500">
              Risk score / 100
            </p>
          </div>
          <div className="w-px bg-ink-300/50" />
          <div className="text-center">
            <p className="flex items-center justify-center gap-1 text-2xl font-bold text-ink-900">
              <Users size={16} className="text-ink-400" aria-hidden="true" />
              {precursor.reportCount}
            </p>
            <p className="text-[10px] font-medium uppercase tracking-wide text-ink-500">
              Related reports
            </p>
          </div>
          <div className="w-px bg-ink-300/50" />
          <div className="text-center">
            <p className="flex items-center justify-center gap-1 text-2xl font-bold text-ink-900">
              <Clock3 size={16} className="text-ink-400" aria-hidden="true" />
              {precursor.recurrenceWindowDays}d
            </p>
            <p className="text-[10px] font-medium uppercase tracking-wide text-ink-500">
              Recurrence window
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
