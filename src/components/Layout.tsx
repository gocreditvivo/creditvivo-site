import { Link, Outlet } from 'react-router-dom';
import UnderConstructionNotice from './UnderConstructionNotice';

const nav = [
  ['/#how-it-works', 'How it works'],
  ['/#ai-review', 'AI review'],
  ['/dashboard', 'Portal'],
  ['/pricing', 'Plans'],
  ['/login', 'Client login'],
];

function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-lg">
      <div className="mx-auto flex min-h-[72px] max-w-[1440px] items-center justify-between gap-6 px-6 lg:px-10">
        <Link to="/" className="flex shrink-0 items-center gap-2.5">
          <img src="/logo.webp" alt="" className="h-10 w-10" />
          <span className="text-xl font-bold tracking-tight text-navy-950">Credit<span className="text-emerald-700">Vivo</span></span>
        </Link>
        <nav className="hidden items-center gap-7 lg:flex" aria-label="Main navigation">
          {nav.map(([to, label]) => <Link key={to} to={to} className="text-sm font-semibold text-slate-600 transition-colors hover:text-emerald-700">{label}</Link>)}
        </nav>
        <Link to="/scan" className="shrink-0 rounded-md bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-900/10 transition hover:-translate-y-0.5 hover:bg-emerald-800">Start free scan</Link>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="bg-[#06264c] py-12 text-slate-300">
      <div className="mx-auto grid max-w-7xl gap-9 px-6 md:grid-cols-[.55fr_1.4fr_auto]">
        <div>
          <Link to="/" className="text-lg font-bold text-white">Credit<span className="text-emerald-300">Vivo</span></Link>
          <p className="mt-2 text-xs text-slate-400">Secure. Transparent. Human-first.</p>
        </div>
        <p className="text-[11px] leading-5 text-slate-400">
          CreditVivo does not guarantee score increases, approvals, or deletion of accurate, current,
          and verifiable information. Consumers may dispute information directly with credit bureaus
          and furnishers for free. Attorney services, if available, require separate eligibility review
          and attorney engagement.
        </p>
        <nav className="flex flex-wrap gap-4 text-xs">
          <Link to="/privacy" className="hover:text-white">Privacy</Link>
          <Link to="/terms" className="hover:text-white">Terms</Link>
          <Link to="/disclosure" className="hover:text-white">Disclosure</Link>
          <Link to="/faq" className="hover:text-white">FAQ</Link>
        </nav>
      </div>
    </footer>
  );
}

export default function Layout() {
  return (
    <div className="min-h-screen bg-white">
      <UnderConstructionNotice />
      <Header />
      <main><Outlet /></main>
      <Footer />
    </div>
  );
}
