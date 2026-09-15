import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

const TRUNCATE_LENGTH = 320;

export function RawReport({ narrative }: { narrative: string }) {
  const [expanded, setExpanded] = useState(false);
  const isLong = narrative.length > TRUNCATE_LENGTH;
  const display = expanded || !isLong ? narrative : `${narrative.slice(0, TRUNCATE_LENGTH)}…`;

  return (
    <section className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card">
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-500">
        <FileText size={15} aria-hidden="true" />
        Raw Report Narrative
      </h2>
      {narrative ? (
        <p className="whitespace-pre-line rounded-md bg-surface-subtle p-4 text-sm leading-relaxed text-ink-700">
          {display}
        </p>
      ) : (
        <p className="text-sm italic text-ink-400">No narrative text was provided for this report.</p>
      )}
      {isLong && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-2 inline-flex origin-left transform-gpu items-center gap-1 text-xs font-semibold text-brand-300 transition-all duration-200 ease-out hover:scale-110 hover:underline active:scale-100"
        >
          {expanded ? (
            <>
              Show less <ChevronUp size={13} aria-hidden="true" />
            </>
          ) : (
            <>
              Read full narrative <ChevronDown size={13} aria-hidden="true" />
            </>
          )}
        </button>
      )}
    </section>
  );
}
