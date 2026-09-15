import { useState, useCallback } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { submitReport } from '@/services/dataService';
import { ApiError } from '@/services/dataService';
import type { AnalysisResponse, ReportSubmission } from '@/types';
import {
  SendHorizonal,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Zap,
  Wrench,
  Activity,
  Target,
  Construction,
  FileText,
  BookOpen,
} from 'lucide-react';

type SubmitState = 'idle' | 'loading' | 'success' | 'error';

export default function SubmitReport() {
  const [narrative, setNarrative] = useState('');
  const [site, setSite] = useState('');
  const [sourceType, setSourceType] = useState('incident');
  const [submitState, setSubmitState] = useState<SubmitState>('idle');
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!narrative.trim()) return;

      setSubmitState('loading');
      setErrorMsg('');
      setResult(null);

      const payload: ReportSubmission = {
        narrative: narrative.trim(),
        site: site.trim() || undefined,
        source_type: sourceType || undefined,
      };

      try {
        const response = await submitReport(payload);
        setResult(response);
        setSubmitState('success');
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : 'Could not reach the backend. Is it running on http://localhost:8000?';
        setErrorMsg(message);
        setSubmitState('error');
      }
    },
    [narrative, site, sourceType]
  );

  const handleReset = () => {
    setNarrative('');
    setSite('');
    setSourceType('incident');
    setSubmitState('idle');
    setResult(null);
    setErrorMsg('');
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Page title */}
        <div>
          <h1 className="text-lg font-bold text-ink-900">Submit Safety Report</h1>
          <p className="text-sm text-ink-500">
            Submit a safety narrative and the backend AI pipeline will extract structured safety
            signals in real time.
          </p>
        </div>

        {/* Form card */}
        <form
          onSubmit={handleSubmit}
          className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card space-y-5"
        >
          {/* Narrative */}
          <div className="space-y-1.5">
            <label htmlFor="narrative" className="block text-sm font-semibold text-ink-700">
              Safety Narrative <span className="text-priority-high">*</span>
            </label>
            <textarea
              id="narrative"
              rows={5}
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
              placeholder="Describe the safety incident or near-miss in detail…"
              className="w-full rounded-md border border-ink-300 bg-surface-subtle px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 focus:outline-none"
              required
            />
          </div>

          {/* Site + Source Type row */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="site" className="block text-sm font-semibold text-ink-700">
                Site / Location
              </label>
              <input
                id="site"
                type="text"
                value={site}
                onChange={(e) => setSite(e.target.value)}
                placeholder="e.g. Duliajan Field Site A"
                className="w-full rounded-md border border-ink-300 bg-surface-subtle px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 focus:outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="source-type" className="block text-sm font-semibold text-ink-700">
                Source Type
              </label>
              <select
                id="source-type"
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full rounded-md border border-ink-300 bg-surface-subtle px-3 py-2 text-sm text-ink-900 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 focus:outline-none"
              >
                <option value="incident">Incident</option>
                <option value="near_miss">Near Miss</option>
                <option value="unsafe_act">Unsafe Act</option>
                <option value="unsafe_condition">Unsafe Condition</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={!narrative.trim() || submitState === 'loading'}
              className="inline-flex items-center gap-2 rounded-md bg-brand-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all duration-150 ease-out hover:scale-105 hover:bg-brand-800 hover:shadow-glow active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100 disabled:active:scale-100"
            >
              {submitState === 'loading' ? (
                <Loader2 size={15} className="animate-spin" aria-hidden="true" />
              ) : (
                <SendHorizonal size={15} aria-hidden="true" />
              )}
              {submitState === 'loading' ? 'Analyzing…' : 'Analyze Report'}
            </button>
            {(submitState === 'success' || submitState === 'error') && (
              <button
                type="button"
                onClick={handleReset}
                className="inline-block transform-gpu text-sm font-medium text-ink-500 underline transition-all duration-200 ease-out hover:scale-105 hover:text-ink-700"
              >
                Submit another
              </button>
            )}
          </div>
        </form>

        {/* Error state */}
        {submitState === 'error' && (
          <div className="rounded-xl border border-priority-highBorder bg-priority-highBg p-4 flex items-start gap-3">
            <AlertTriangle size={18} className="mt-0.5 shrink-0 text-priority-high" />
            <div>
              <p className="text-sm font-semibold text-priority-high">Analysis Failed</p>
              <p className="text-sm text-ink-700 mt-1">{errorMsg}</p>
            </div>
          </div>
        )}

        {/* Success: show extraction results */}
        {submitState === 'success' && result && (
          <div className="space-y-4">
            {/* Success banner */}
            <div className="rounded-xl border border-priority-lowBorder bg-priority-lowBg p-4 flex items-start gap-3">
              <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-priority-low" />
              <div>
                <p className="text-sm font-semibold text-priority-low">Analysis Complete</p>
                <p className="text-sm text-ink-700 mt-1">
                  Pipeline: <code className="rounded bg-black/20 px-1 font-mono text-xs">{result.pipeline_version}</code>
                  {' · '}
                  Report ID: <code className="rounded bg-black/20 px-1 font-mono text-xs">{result.safety_report.report_id}</code>
                </p>
              </div>
            </div>

            {/* Extracted signals grid */}
            <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface shadow-card overflow-hidden">
              <div className="border-b border-ink-300/40 bg-surface-subtle px-5 py-3">
                <h2 className="text-sm font-bold text-ink-900">Extracted Safety Signals</h2>
              </div>
              <div className="grid grid-cols-1 gap-px bg-ink-300/20 sm:grid-cols-2 lg:grid-cols-3">
                <SignalCard
                  icon={ShieldAlert}
                  label="Hazard"
                  value={result.safety_report.hazard}
                  colorClass="text-priority-high"
                />
                <SignalCard
                  icon={Zap}
                  label="Exposure"
                  value={result.safety_report.exposure}
                  colorClass="text-priority-medium"
                />
                <SignalCard
                  icon={Activity}
                  label="Activity"
                  value={result.safety_report.activity}
                  colorClass="text-brand-300"
                />
                <SignalCard
                  icon={Wrench}
                  label="Equipment"
                  value={result.safety_report.equipment}
                  colorClass="text-ink-700"
                />
                <SignalCard
                  icon={Target}
                  label="Barrier Failure"
                  value={result.safety_report.barrier_failure}
                  colorClass="text-priority-high"
                />
                <SignalCard
                  icon={Construction}
                  label="Severity Potential"
                  value={result.safety_report.severity_potential}
                  colorClass="text-ink-500"
                />
                <SignalCard
                  icon={ShieldAlert}
                  label="SIF Potential"
                  value={
                    result.safety_report.sif_potential === true
                      ? 'Yes'
                      : result.safety_report.sif_potential === false
                        ? 'No'
                        : null
                  }
                  colorClass={
                    result.safety_report.sif_potential
                      ? 'text-priority-high'
                      : 'text-priority-low'
                  }
                />
                <SignalCard
                  icon={BookOpen}
                  label="IOGP Life-Saving Rule"
                  value={result.safety_report.iogp_life_saving_rule}
                  colorClass="text-brand-300"
                />
              </div>
            </div>

            {/* Evidence */}
            {result.safety_report.evidence &&
              Object.keys(result.safety_report.evidence).length > 0 && (
                <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface shadow-card overflow-hidden">
                  <div className="border-b border-ink-300/40 bg-surface-subtle px-5 py-3">
                    <h2 className="text-sm font-bold text-ink-900">Supporting Evidence</h2>
                  </div>
                  <div className="p-5 space-y-3">
                    {Object.entries(result.safety_report.evidence).map(([key, phrases]) => (
                      <div key={key}>
                        <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">
                          {key.replace(/_/g, ' ')}
                        </p>
                        <ul className="mt-1 space-y-1">
                          {phrases.map((phrase, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-ink-700">
                              <FileText size={13} className="mt-0.5 shrink-0 text-ink-400" />
                              <span className="italic">"{phrase}"</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {/* Raw narrative */}
            <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface shadow-card overflow-hidden">
              <div className="border-b border-ink-300/40 bg-surface-subtle px-5 py-3">
                <h2 className="text-sm font-bold text-ink-900">Processed Narrative</h2>
              </div>
              <div className="p-5">
                <p className="text-sm text-ink-700 leading-relaxed">
                  {result.safety_report.narrative}
                </p>
              </div>
            </div>

            {/* AI-2 placeholder info */}
            {result.relationships.length === 0 && result.precursors.length === 0 && (
              <div className="rounded-xl border border-ink-300/30 bg-surface-muted p-4 text-center">
                <p className="text-xs text-ink-500">
                  Cross-report relationships and SIF precursor detection (AI-2 pipeline) will appear
                  here once integrated. Currently returns empty results.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

// ---------------------------------------------------------------------------
// Small helper component for the signal cards
// ---------------------------------------------------------------------------

function SignalCard({
  icon: Icon,
  label,
  value,
  colorClass,
}: {
  icon: React.ElementType;
  label: string;
  value: string | null;
  colorClass: string;
}) {
  return (
    <div className="bg-surface p-4 flex items-start gap-3">
      <Icon size={16} className={`mt-0.5 shrink-0 ${colorClass}`} aria-hidden="true" />
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">{label}</p>
        {value ? (
          <p className="mt-0.5 text-sm font-medium text-ink-900">
            {value.replace(/_/g, ' ').replace(/\|/g, ', ')}
          </p>
        ) : (
          <p className="mt-0.5 text-sm text-ink-400 italic">Not detected</p>
        )}
      </div>
    </div>
  );
}
