import type { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface AppShellProps {
  children: ReactNode;
  lastUpdated?: string;
  onRefresh?: () => void;
  refreshing?: boolean;
  syncing?: boolean;
}

export function AppShell({
  children,
  lastUpdated,
  onRefresh,
  refreshing,
  syncing,
}: AppShellProps) {
  // Transparent and stacked above the WebGL backdrop — the body owns the
  // background colour so the constellation shows through between panels.
  return (
    <div className="relative z-10 min-h-screen">
      <Header
        lastUpdated={lastUpdated}
        onRefresh={onRefresh}
        refreshing={refreshing}
        syncing={syncing}
      />
      <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:flex-row">
        <Sidebar />
        <div className="min-w-0 flex-1">{children}</div>
      </main>
    </div>
  );
}

export function PageContainer({ children }: { children: ReactNode }) {
  return <div className="mx-auto max-w-7xl">{children}</div>;
}
