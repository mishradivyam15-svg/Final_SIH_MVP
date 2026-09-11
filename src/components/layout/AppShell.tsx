import type { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface AppShellProps {
  children: ReactNode;
  lastUpdated?: string;
  onRefresh?: () => void;
  refreshing?: boolean;
}

export function AppShell({ children, lastUpdated, onRefresh, refreshing }: AppShellProps) {
  return (
    <div className="min-h-screen bg-surface-subtle">
      <Header lastUpdated={lastUpdated} onRefresh={onRefresh} refreshing={refreshing} />
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
