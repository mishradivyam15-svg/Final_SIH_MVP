import { NavLink } from 'react-router-dom';
import { LayoutDashboard, GitMerge, ClipboardList, SendHorizonal, FileText } from 'lucide-react';

const items = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/submit', label: 'Submit Report', icon: SendHorizonal },
  { to: '/reports', label: 'All Reports', icon: FileText },
  { to: '/dashboard#precursors', label: 'Precursor Alerts', icon: GitMerge },
  { to: '/dashboard#review-queue', label: 'Review Queue', icon: ClipboardList },
];

export function Sidebar() {
  return (
    <aside className="w-full shrink-0 lg:w-52">
      <nav
        aria-label="Primary navigation"
        className="panel-sheen rounded-xl border border-ink-300/40 bg-surface p-2 shadow-card lg:sticky lg:top-6"
      >
        <p className="px-3 pb-2 pt-2 text-[10px] font-semibold uppercase tracking-widest text-ink-400">
          HSE Workspace
        </p>
        <div className="space-y-0.5">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={label}
              to={to}
              className={({ isActive }) =>
                `group relative flex origin-left transform-gpu items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200 ease-out hover:scale-[1.04] active:scale-100 ${
                  isActive && !to.includes('#')
                    ? 'bg-brand-950 text-brand-300'
                    : 'text-ink-500 hover:bg-surface-subtle hover:text-ink-900'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && !to.includes('#') && (
                    <span
                      className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-brand-400 shadow-[0_0_8px_0_rgba(84,134,196,0.8)]"
                      aria-hidden="true"
                    />
                  )}
                  <Icon
                    size={16}
                    className="transition-transform duration-200 group-hover:scale-110"
                    aria-hidden="true"
                  />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </aside>
  );
}
