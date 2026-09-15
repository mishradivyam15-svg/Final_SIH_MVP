interface SkeletonProps {
  className?: string;
}

/** Base shimmer block. Compose into larger skeletons below. */
export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`animate-shimmer rounded-md bg-surface-muted bg-[length:200%_100%] bg-gradient-to-r from-surface-muted via-white/10 to-surface-muted ${className}`}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-4 shadow-card">
      <Skeleton className="mb-3 h-4 w-24" />
      <Skeleton className="mb-2 h-5 w-3/4" />
      <Skeleton className="mb-1 h-3 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

export function OverviewCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-4 shadow-card">
          <Skeleton className="mb-3 h-3 w-28" />
          <Skeleton className="h-7 w-16" />
        </div>
      ))}
    </div>
  );
}

export function DetailHeaderSkeleton() {
  return (
    <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-6 shadow-card">
      <Skeleton className="mb-4 h-4 w-20" />
      <Skeleton className="mb-3 h-7 w-1/2" />
      <div className="flex gap-3">
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-6 w-24" />
      </div>
    </div>
  );
}

export function ListSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

export function GraphSkeleton() {
  return (
    <div className="flex h-72 w-full items-center justify-center rounded-xl panel-sheen border border-ink-300/40 bg-surface-subtle">
      <Skeleton className="h-40 w-40 rounded-full" />
    </div>
  );
}
