import { Link } from 'react-router-dom';
import { ArrowRight, FileSearch, LayoutDashboard, ShieldCheck } from 'lucide-react';

const memberActions = [
  {
    title: 'Open your dashboard',
    body: 'Review your Credit Vivo roadmap, recent activity, and the next step in one place.',
    to: '/dashboard',
    label: 'Go to dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Start a Credit Check-In',
    body: 'Upload an eligible report for scanner-assisted review and organized findings.',
    to: '/scan',
    label: 'Start check-in',
    icon: FileSearch,
  },
  {
    title: 'Review your findings',
    body: 'Return to the findings organized from your most recent completed scanner run.',
    to: '/findings',
    label: 'View findings',
    icon: ShieldCheck,
  },
];

export default function Member() {
  return (
    <>
      <section className="bg-gradient-to-b from-sky-50/50 to-white py-16">
        <div className="mx-auto max-w-3xl px-4 text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full bg-sky-100 px-3 py-1.5 text-[11px] font-semibold text-sky-700">
            <span className="h-1.5 w-1.5 rounded-full bg-sky-500" />
            Member Access
          </div>
          <h1 className="mb-4 text-3xl font-bold leading-tight text-navy-900 sm:text-[38px]">
            Your Credit Vivo member portal
          </h1>
          <p className="mx-auto max-w-xl text-[15px] leading-relaxed text-navy-500">
            Continue your check-in, review organized findings, and choose the next step
            that fits your file.
          </p>
        </div>
      </section>

      <section className="bg-white py-12">
        <div className="mx-auto max-w-4xl px-4">
          <div className="grid gap-5 md:grid-cols-3">
            {memberActions.map(({ title, body, to, label, icon: Icon }) => (
              <article
                key={title}
                className="flex min-h-[250px] flex-col rounded-xl border border-navy-100/60 bg-navy-50/40 p-6"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-sky-100 text-sky-700">
                  <Icon size={18} aria-hidden="true" />
                </div>
                <h2 className="mb-2 text-sm font-bold text-navy-900">{title}</h2>
                <p className="mb-6 text-sm leading-relaxed text-navy-500">{body}</p>
                <Link
                  to={to}
                  className="mt-auto inline-flex items-center gap-2 text-xs font-semibold text-sky-700 hover:text-sky-800"
                >
                  {label}
                  <ArrowRight size={13} aria-hidden="true" />
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
