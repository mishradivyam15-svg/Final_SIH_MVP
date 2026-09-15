import { useState } from 'react';
import { CheckCircle, XCircle, Search } from 'lucide-react';
import type { PrecursorStatus, ReviewAction } from '@/types';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { submitReview, ApiError } from '@/services/dataService';

interface ReviewActionsProps {
  precursorId: string;
  currentStatus: PrecursorStatus;
  onStatusChange: (status: PrecursorStatus, note?: string) => void;
}

type PendingAction = 'DISMISS' | 'INVESTIGATE' | null;

export function ReviewActions({ precursorId, currentStatus, onStatusChange }: ReviewActionsProps) {
  const [pending, setPending] = useState<PendingAction>(null);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  async function runAction(action: ReviewAction, payloadNote?: string) {
    setSubmitting(true);
    setFeedback(null);
    try {
      await submitReview(precursorId, { action, note: payloadNote });
      const statusMap: Record<ReviewAction, PrecursorStatus> = {
        CONFIRM: 'CONFIRMED',
        DISMISS: 'DISMISSED',
        INVESTIGATE: 'UNDER_INVESTIGATION',
      };
      onStatusChange(statusMap[action], payloadNote);
      setFeedback({
        type: 'success',
        text:
          action === 'CONFIRM'
            ? 'Precursor confirmed.'
            : action === 'DISMISS'
              ? 'Precursor dismissed.'
              : 'Precursor moved to Under Investigation.',
      });
    } catch (err) {
      setFeedback({
        type: 'error',
        text: err instanceof ApiError ? err.message : 'Could not submit review action.',
      });
    } finally {
      setSubmitting(false);
      setPending(null);
      setNote('');
    }
  }

  const isTerminal = currentStatus === 'CONFIRMED' || currentStatus === 'DISMISSED';

  return (
    <section className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card">
      <h2 className="mb-1 text-sm font-semibold text-ink-900">HSE Review Action</h2>
      <p className="mb-4 text-xs text-ink-500">
        Record the HSE team's decision on this precursor alert.
      </p>

      <div className="flex flex-wrap gap-2">
        <Button
          variant="primary"
          disabled={submitting || isTerminal}
          onClick={() => runAction('CONFIRM')}
        >
          <CheckCircle size={15} aria-hidden="true" />
          Confirm
        </Button>
        <Button
          variant="danger"
          disabled={submitting || isTerminal}
          onClick={() => setPending('DISMISS')}
        >
          <XCircle size={15} aria-hidden="true" />
          Dismiss
        </Button>
        <Button
          variant="secondary"
          disabled={submitting || isTerminal}
          onClick={() => setPending('INVESTIGATE')}
        >
          <Search size={15} aria-hidden="true" />
          Investigate
        </Button>
      </div>

      {isTerminal && (
        <p className="mt-3 text-xs text-ink-500">
          This precursor has already been {currentStatus === 'CONFIRMED' ? 'confirmed' : 'dismissed'}
          . No further review action is available.
        </p>
      )}

      {feedback && (
        <p
          className={`mt-3 text-sm font-medium ${feedback.type === 'success' ? 'text-priority-low' : 'text-priority-high'}`}
          role="status"
        >
          {feedback.text}
        </p>
      )}

      <Modal
        open={pending === 'DISMISS'}
        onClose={() => setPending(null)}
        title="Dismiss this precursor?"
        footer={
          <>
            <Button variant="secondary" onClick={() => setPending(null)}>
              Cancel
            </Button>
            <Button variant="danger" disabled={submitting} onClick={() => runAction('DISMISS', note)}>
              Dismiss precursor
            </Button>
          </>
        }
      >
        <p className="mb-3 text-sm text-ink-700">
          Dismissing marks this pattern as reviewed and not actionable. You can optionally record
          a reason for the record.
        </p>
        <label htmlFor="dismiss-reason" className="mb-1 block text-xs font-medium text-ink-500">
          Reason (optional)
        </label>
        <textarea
          id="dismiss-reason"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="w-full rounded-md border border-ink-300 px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600"
          placeholder="e.g. Root cause already corrected on site"
        />
      </Modal>

      <Modal
        open={pending === 'INVESTIGATE'}
        onClose={() => setPending(null)}
        title="Assign for investigation"
        footer={
          <>
            <Button variant="secondary" onClick={() => setPending(null)}>
              Cancel
            </Button>
            <Button disabled={submitting} onClick={() => runAction('INVESTIGATE', note)}>
              Start investigation
            </Button>
          </>
        }
      >
        <p className="mb-3 text-sm text-ink-700">
          This will move the precursor to <strong>Under Investigation</strong>. Optionally add a
          note or assignment for the HSE team.
        </p>
        <label htmlFor="investigate-note" className="mb-1 block text-xs font-medium text-ink-500">
          Investigation note (optional)
        </label>
        <textarea
          id="investigate-note"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="w-full rounded-md border border-ink-300 px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600"
          placeholder="e.g. Assigned to Site HSE Officer for permit-to-work audit"
        />
      </Modal>
    </section>
  );
}
