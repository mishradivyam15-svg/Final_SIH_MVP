import { NavLink } from 'react-router-dom';
import { LayoutDashboard, GitMerge, ClipboardList } from 'lucide-react';

const items = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/dashboard#precursors', label: 'Precursor Alerts', icon: GitMerge },
  { to: '/dashboard#review-queue', label: 'Review Queue', icon: ClipboardList },
];

export function Sidebar() {
  return (
    <aside className="w-full shrink-0 lg:w-52">
      <nav aria-label="Primary navigation" className="rounded-lg border border-ink-300/40 bg-white p-2 shadow-card lg:sticky lg:top-6">
        <p className="px-3 pb-2 pt-2 text-[10px] font-semibold uppercase tracking-widest text-ink-400">
          HSE Workspace
        </p>
        <div className="space-y-1">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={label}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive && to === '/dashboard'
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-ink-600 hover:bg-surface-subtle hover:text-ink-900'
                }`
              }
            >
              <Icon size={16} aria-hidden="true" />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>
    </aside>
  );
}
