import { Tags } from 'lucide-react';
import type { SafetyReport } from '@/types';

interface SafetySignalsProps {
  report: SafetyReport;
}

/** Renders both the structured core fields and any extra extracted signals array. */
export function SafetySignals({ report }: SafetySignalsProps) {
  const coreFields: { label: string; value?: string }[] = [
    { label: 'Hazard', value: report.hazard },
    { label: 'Activity', value: report.activity },
    { label: 'Equipment', value: report.equipment },
    { label: 'Barrier Failure', value: report.barrier },
    { label: 'Cause', value: report.cause },
    { label: 'Exposure', value: report.exposure },
  ].filter((f) => f.value);

  return (
    <section className="rounded-lg border border-ink-300/40 bg-white p-6 shadow-card">
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-500">
        <Tags size={15} aria-hidden="true" />
        Extracted Safety Signals
      </h2>

      {coreFields.length === 0 ? (
        <p className="text-sm italic text-ink-400">No structured signals were extracted for this report.</p>
      ) : (
        <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {coreFields.map((f) => (
            <div key={f.label} className="rounded-md bg-surface-subtle px-3 py-2">
              <dt className="text-[10px] font-medium uppercase tracking-wide text-ink-400">
                {f.label}
              </dt>
              <dd className="text-sm font-medium text-ink-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      )}

      {report.signals.length > 0 && (
        <div className="mt-4 border-t border-ink-300/30 pt-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-400">
            Model-extracted tags
          </p>
          <div className="flex flex-wrap gap-2">
            {report.signals.map((s, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-md border border-brand-200 bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700"
              >
                {s.label}: {s.value}
                {typeof s.confidence === 'number' && (
                  <span className="text-brand-400">({Math.round(s.confidence * 100)}%)</span>
                )}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
