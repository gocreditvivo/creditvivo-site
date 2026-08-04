import { Link, Outlet, useLocation } from 'react-router-dom';

type HeaderLink =
  | { href: string; label: string; primary: true }
  | { to: string; label: string; primary?: false };

const headerLinks: HeaderLink[] = [
  { href: '/login', label: 'Get Started', primary: true },
  { to: '/why', label: 'Why Credit Vivo' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/faq', label: 'FAQ' },
  { to: '/learning', label: 'Learning' },
];

function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-emerald-100/70 bg-white/95 shadow-sm shadow-navy-900/5 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex min-h-[72px] flex-col items-start justify-center gap-3 py-3 lg:h-[72px] lg:flex-row lg:items-center lg:justify-between lg:gap-6 lg:py-0">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.webp" alt="Credit Vivo" className="h-9 w-9 sm:h-12 sm:w-12" />
            <span className="text-xl font-semibold tracking-tight text-navy-900 sm:text-3xl">
              Credit <span className="text-emerald-700">Vivo</span>
            </span>
          </Link>

          <nav className="flex w-full items-center gap-2 overflow-x-auto pb-1 lg:w-auto lg:justify-end lg:overflow-visible lg:pb-0" aria-label="Main navigation">
            {headerLinks.map((link) => (
              'href' in link ? (
                <a
                  key={link.href}
                  href={link.href}
                  className="shrink-0 rounded-lg bg-gradient-to-r from-emerald-600 via-teal-500 to-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-900/15 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-emerald-900/20"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.to}
                  to={link.to}
                  className={
                  link.primary
                    ? 'shrink-0 rounded-lg bg-gradient-to-r from-emerald-600 via-teal-500 to-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-900/15 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-emerald-900/20'
                    : 'shrink-0 rounded-lg px-3 py-2.5 text-sm font-semibold text-navy-700 transition-colors hover:bg-emerald-50 hover:text-emerald-800'
                  }
                >
                  {link.label}
                </Link>
              )
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}

function BottomButtons({ exclude }: { exclude?: string }) {
  const allLinks = [
    { to: '/join', label: 'Join Free', primary: true },
    { to: '/why', label: 'Why Credit Vivo' },
    { to: '/pricing', label: 'Pricing' },
    { to: '/faq', label: 'FAQ' },
    { to: '/learning', label: 'Learning' },
  ];

  const filtered = allLinks.filter((l) => l.to !== exclude);

  return (
    <section className="py-16 bg-navy-50/50">
      <div className="max-w-2xl mx-auto px-4 text-center">
        <h3 className="text-lg font-bold text-navy-900 mb-2">Keep going with Credit Vivo</h3>
        <p className="text-sm text-navy-500 mb-6">Choose the next page that helps you move forward.</p>
        <div className="flex flex-wrap justify-center gap-2">
          {filtered.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={l.primary ? 'btn-primary text-xs' : 'btn-soft text-xs'}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-navy-950 text-navy-300 pt-14 pb-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-3">
              <img src="/logo.webp" alt="Credit Vivo" className="w-6 h-6 brightness-200" />
              <span className="text-sm font-bold text-white">
                Credit <span className="text-emerald-300">Vivo</span>
              </span>
            </Link>
            <p className="text-xs text-navy-400 leading-relaxed">
              You take control. We clear the path.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Product</h4>
            <div className="space-y-2">
              <Link to="/join" className="block text-xs text-navy-400 hover:text-white transition-colors">Join Free</Link>
              <Link to="/pricing" className="block text-xs text-navy-400 hover:text-white transition-colors">Pricing</Link>
              <Link to="/learning" className="block text-xs text-navy-400 hover:text-white transition-colors">Learning</Link>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Company</h4>
            <div className="space-y-2">
              <Link to="/why" className="block text-xs text-navy-400 hover:text-white transition-colors">Why Credit Vivo</Link>
              <Link to="/faq" className="block text-xs text-navy-400 hover:text-white transition-colors">FAQ</Link>
              <Link to="/reviews" className="block text-xs text-navy-400 hover:text-white transition-colors">Reviews</Link>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Members</h4>
            <div className="space-y-2">
              <a href="/login" className="block text-xs text-navy-400 hover:text-white transition-colors">Sign In</a>
              <Link to="/scan" className="block text-xs text-navy-400 hover:text-white transition-colors">Free Scan</Link>
              <Link to="/findings" className="block text-xs text-navy-400 hover:text-white transition-colors">Findings</Link>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Legal</h4>
            <div className="space-y-2">
              <Link to="/compliance" className="block text-xs text-navy-400 hover:text-white transition-colors">Compliance</Link>
              <Link to="/status" className="block text-xs text-navy-400 hover:text-white transition-colors">System Status</Link>
              <Link to="/terms" className="block text-xs text-navy-400 hover:text-white transition-colors">Terms</Link>
              <Link to="/privacy" className="block text-xs text-navy-400 hover:text-white transition-colors">Privacy</Link>
              <Link to="/disclosure" className="block text-xs text-navy-400 hover:text-white transition-colors">Disclosure</Link>
            </div>
          </div>
        </div>

      </div>
    </footer>
  );
}

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      <Nav />
      <main className="flex-1">
        <Outlet />
      </main>
      <BottomButtons exclude={location.pathname} />
      <Footer />
    </div>
  );
}

export { BottomButtons };
