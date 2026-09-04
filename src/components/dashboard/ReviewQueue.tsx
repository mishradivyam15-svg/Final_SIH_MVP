import { useNavigate } from 'react-router-dom';
import type { Precursor } from '@/types';
import { PriorityBadge } from '@/components/common/PriorityBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { EmptyState } from '@/components/common/EmptyState';
import { ClipboardCheck } from 'lucide-react';

interface ReviewQueueProps {
  items: Precursor[];
}

export function ReviewQueue({ items }: ReviewQueueProps) {
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <EmptyState
        icon={ClipboardCheck}
        title="Review queue is empty"
        description="No precursor alerts are currently awaiting HSE review."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-ink-300/40 bg-white shadow-card">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-ink-300/40 bg-surface-subtle text-xs uppercase tracking-wide text-ink-500">
          <tr>
            <th scope="col" className="px-4 py-2.5 font-medium">Precursor</th>
            <th scope="col" className="px-4 py-2.5 font-medium">Priority</th>
            <th scope="col" className="px-4 py-2.5 font-medium">Score</th>
            <th scope="col" className="px-4 py-2.5 font-medium">Recurrence</th>
            <th scope="col" className="px-4 py-2.5 font-medium">Status</th>
            <th scope="col" className="px-4 py-2.5 font-medium text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-300/30">
          {items.map((p) => (
            <tr key={p.id} className="hover:bg-surface-subtle">
              <td className="px-4 py-3 font-medium text-ink-900">{p.title}</td>
              <td className="px-4 py-3">
                <PriorityBadge priority={p.priority} />
              </td>
              <td className="px-4 py-3 text-ink-700">{p.riskScore}/100</td>
              <td className="px-4 py-3 text-ink-700">
                {p.reportCount} reports / {p.recurrenceWindowDays}d
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={p.status} />
              </td>
              <td className="px-4 py-3 text-right">
                <button
                  onClick={() => navigate(`/precursors/${p.id}`)}
                  className="text-xs font-semibold text-brand-700 hover:underline"
                >
                  Review →
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
