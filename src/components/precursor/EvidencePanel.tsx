import { CheckCircle2, HelpCircle } from 'lucide-react';
import type { Precursor } from '@/types';

interface EvidencePanelProps {
  precursor: Precursor;
}

/**
 * Answers: "Why should an HSE officer care about this alert?"
 * Renders only fields the data actually provides — never invents evidence.
 */
export function EvidencePanel({ precursor }: EvidencePanelProps) {
  const { evidence } = precursor;

  const metrics: { label: string; value: string }[] = [];
  if (typeof evidence.semanticSimilarity === 'number') {
    metrics.push({ label: 'Semantic Similarity', value: `${Math.round(evidence.semanticSimilarity * 100)}%` });
  }
  if (typeof evidence.hazardMatch === 'boolean') {
    metrics.push({ label: 'Hazard Match', value: evidence.hazardMatch ? 'Yes' : 'No' });
  }
  if (typeof evidence.activityMatch === 'boolean') {
    metrics.push({ label: 'Activity Match', value: evidence.activityMatch ? 'Yes' : 'No' });
  }
  if (typeof evidence.barrierMatch === 'boolean') {
    metrics.push({ label: 'Barrier Match', value: evidence.barrierMatch ? 'Yes' : 'No' });
  }
  if (typeof evidence.siteMatch === 'boolean') {
    metrics.push({ label: 'Site/Context Match', value: evidence.siteMatch ? 'Yes' : 'No' });
  }
  if (evidence.temporalRecurrence) {
    metrics.push({ label: 'Temporal Recurrence', value: evidence.temporalRecurrence });
  }
  metrics.push({ label: 'Contributing Reports', value: String(evidence.contributingReportCount) });

  return (
    <section className="rounded-lg border border-ink-300/40 bg-white p-6 shadow-card">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
        Why was this alert generated?
      </h2>

      {evidence.summaryPoints.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {evidence.summaryPoints.map((point, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-ink-700">
              <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-priority-low" aria-hidden="true" />
              {point}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 flex items-center gap-2 text-sm text-ink-500">
          <HelpCircle size={15} aria-hidden="true" />
          No explanation summary was provided for this precursor.
        </p>
      )}

      <div className="mt-5 border-t border-ink-300/30 pt-4">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-400">
          Numerical evidence
        </p>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-3">
          {metrics.map((m) => (
            <div key={m.label} className="flex items-center justify-between border-b border-ink-300/20 pb-1.5 sm:block sm:border-none sm:pb-0">
              <dt className="text-xs text-ink-500">{m.label}</dt>
              <dd className="text-sm font-semibold text-ink-900">{m.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <p className="mt-5 rounded-md bg-surface-subtle px-3 py-2 text-xs text-ink-500">
        This precursor was not flagged from a single report — it reflects a recurring pattern
        across {evidence.contributingReportCount} related reports sharing hazard, activity,
        barrier-failure, and site/context signals. Evidence values are computed by the AI/ML
        pipeline and shown here as provided; the frontend does not calculate them.
      </p>
    </section>
  );
}
