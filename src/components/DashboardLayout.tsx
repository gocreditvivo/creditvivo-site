import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  Compass,
  Search,
  FileText,
  Calendar,
  BookOpen,
  Bell,
  Headphones,
  ArrowLeft,
  Landmark,
  Activity,
  Megaphone,
  BrainCircuit,
  LogOut,
} from 'lucide-react';
import UnderConstructionNotice from './UnderConstructionNotice';
import { useAuth } from '../auth/authContext';

const sideLinks = [
  { to: '/dashboard', label: 'Roadmap', icon: Compass },
  { to: '/scan', label: 'Free Scan', icon: Search },
  { to: '/findings', label: 'Findings', icon: FileText },
  { to: '/owner-ai', label: 'Owner AI', icon: BrainCircuit },
  { to: '/founder-health', label: 'Founder Health', icon: Activity },
  { to: '/growth-ai', label: 'Growth AI', icon: Megaphone },
  { to: '/bank-link', label: 'Bank Link', icon: Landmark },
  { to: '/dashboard', label: 'Monthly Plan', icon: Calendar },
  { to: '/learning', label: 'Learning Center', icon: BookOpen },
  { to: '/dashboard', label: 'Updates', icon: Bell },
  { to: '/faq', label: 'Support', icon: Headphones },
];

export default function DashboardLayout() {
  const location = useLocation();
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen flex bg-navy-50/30">
      <UnderConstructionNotice />
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-56 bg-white border-r border-navy-100/60 p-4">
        <Link to="/" className="flex items-center gap-2 mb-6">
          <img src="/logo.webp" alt="Credit Vivo" className="w-6 h-6" />
          <span className="text-sm font-bold text-navy-900">
            Credit <span className="text-mint-600">Vivo</span>
          </span>
        </Link>

        <nav className="flex-1 space-y-0.5">
          {sideLinks.map(({ to, label, icon: Icon }) => (
            <Link
              key={label}
              to={to}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                location.pathname === to
                  ? 'bg-sky-50 text-sky-700'
                  : 'text-navy-500 hover:bg-navy-50 hover:text-navy-700'
              }`}
            >
              <Icon size={14} />
              {label}
            </Link>
          ))}
        </nav>

        <Link
          to="/"
          className="flex items-center gap-2 px-3 py-2 text-xs text-navy-400 hover:text-navy-600 transition-colors mt-4"
        >
          <ArrowLeft size={13} />
          Back to site
        </Link>
        <button type="button" onClick={() => void signOut()} className="mt-2 flex items-center gap-2 px-3 py-2 text-left text-xs text-navy-400 hover:text-navy-700">
          <LogOut size={13} /> Sign out{user?.email ? ` (${user.email})` : ''}
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto">
        {/* Mobile header */}
        <div className="md:hidden mb-6">
          <Link to="/" className="flex items-center gap-2">
            <img src="/logo.webp" alt="Credit Vivo" className="w-6 h-6" />
            <span className="text-sm font-bold text-navy-900">Credit <span className="text-mint-600">Vivo</span></span>
          </Link>
          <nav className="mt-4 flex gap-2 overflow-x-auto pb-2" aria-label="Member navigation">
            {sideLinks.slice(0, 5).map(({ to, label, icon: Icon }) => (
              <Link
                key={`${label}-mobile`}
                to={to}
                className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-2 text-[11px] font-semibold ${
                  location.pathname === to
                    ? 'bg-sky-50 text-sky-700 ring-1 ring-sky-100'
                    : 'bg-white text-navy-500 ring-1 ring-navy-100'
                }`}
              >
                <Icon size={12} />
                {label}
              </Link>
            ))}
          </nav>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
