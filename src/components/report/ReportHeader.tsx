import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Calendar, ShieldAlert } from 'lucide-react';
import type { SafetyReport } from '@/types';
import { Badge } from '@/components/common/Badge';
import { formatDate } from '@/lib/date';
import { REPORT_TYPE_LABEL } from '@/lib/display';

export function ReportHeader({ report }: { report: SafetyReport }) {
  const navigate = useNavigate();

  return (
    <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 inline-flex origin-left transform-gpu items-center gap-1.5 text-xs font-medium text-ink-500 transition-all duration-200 ease-out hover:scale-110 hover:text-ink-900 active:scale-100"
      >
        <ArrowLeft size={14} aria-hidden="true" />
        Back
      </button>

      <div className="flex flex-wrap items-center gap-2">
        <Badge>{REPORT_TYPE_LABEL[report.type]}</Badge>
        {report.sifPotential && (
          <span className="inline-flex items-center gap-1 rounded-md bg-priority-highBg px-2 py-0.5 text-xs font-semibold text-priority-high">
            <ShieldAlert size={12} aria-hidden="true" />
            SIF-Potential
          </span>
        )}
        {report.iogpRule && <Badge variant="outline">{report.iogpRule}</Badge>}
      </div>
      <h1 className="mt-2 text-xl font-bold text-ink-900">{report.displayId}</h1>

      <div className="mt-3 flex flex-wrap gap-4 text-sm text-ink-500">
        <span className="flex items-center gap-1.5">
          <Calendar size={14} aria-hidden="true" />
          {formatDate(report.date)}
        </span>
        <span className="flex items-center gap-1.5">
          <MapPin size={14} aria-hidden="true" />
          {report.site}
        </span>
      </div>
    </div>
  );
}
