import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Calendar } from 'lucide-react';
import type { SafetyReport } from '@/types';
import { Badge } from '@/components/common/Badge';
import { formatDate } from '@/lib/date';
import { REPORT_TYPE_LABEL } from '@/lib/display';

export function ReportHeader({ report }: { report: SafetyReport }) {
  const navigate = useNavigate();

  return (
    <div className="rounded-lg border border-ink-300/40 bg-white p-6 shadow-card">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 inline-flex items-center gap-1.5 text-xs font-medium text-ink-500 hover:text-ink-900"
      >
        <ArrowLeft size={14} aria-hidden="true" />
        Back
      </button>

      <div className="flex flex-wrap items-center gap-2">
        <Badge>{REPORT_TYPE_LABEL[report.type]}</Badge>
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
