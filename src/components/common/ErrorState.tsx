import { AlertOctagon } from 'lucide-react';
import { Button } from './Button';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-priority-highBorder bg-priority-highBg px-6 py-10 text-center">
      <AlertOctagon size={28} className="mb-3 text-priority-high" aria-hidden="true" />
      <p className="text-sm font-medium text-priority-high">Unable to load this data.</p>
      <p className="mt-1 max-w-sm text-sm text-ink-700">
        {message || 'Please try again in a moment.'}
      </p>
      {onRetry && (
        <Button variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
