import { Activity, Database, FileText, Globe2, Headphones, ShieldCheck } from 'lucide-react';

const checks = [
  {
    title: 'Website',
    detail: 'Customer pages and login access are monitored.',
    icon: Globe2,
  },
  {
    title: 'Scanner API',
    detail: 'Credit report upload and scanner processing use backend health checks.',
    icon: Activity,
  },
  {
    title: 'Customer Data',
    detail: 'Uploads and output files should be stored outside the public website host.',
    icon: Database,
  },
  {
    title: 'Report Output',
    detail: 'Worksheets, findings, and letters are generated only when the scanner is ready.',
    icon: FileText,
  },
];

export default function Status() {
  return (
    <section className="min-h-[70vh] bg-gradient-to-b from-white via-emerald-50/35 to-white px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-100">
          <ShieldCheck size={14} />
          Credit Vivo System Status
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
          <div>
            <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-navy-950 sm:text-5xl">
              If the scanner is paused, your next step stays simple.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-navy-600">
              Credit Vivo monitors the website, scanner backend, and report workflow. If a service is temporarily unavailable, we switch to safe review mode and avoid new credit report uploads until the system is ready.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <a href="/login" className="btn-primary">
                Member Login
              </a>
              <a href="/faq" className="btn-soft">
                Support FAQ
              </a>
            </div>
          </div>

          <div className="rounded-lg border border-emerald-100 bg-white p-5 shadow-sm shadow-navy-900/5">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-emerald-50 p-2 text-emerald-700">
                <Headphones size={20} />
              </div>
              <div>
                <h2 className="text-base font-bold text-navy-950">Emergency Mode</h2>
                <p className="mt-1 text-sm leading-6 text-navy-600">
                  If the scanner backend is down, customers can still view this page, sign in, and contact support. New report uploads should wait until the scanner is marked ready.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {checks.map(({ title, detail, icon: Icon }) => (
            <div key={title} className="rounded-lg border border-navy-100 bg-white p-5 shadow-sm shadow-navy-900/5">
              <div className="mb-4 inline-flex rounded-lg bg-sky-50 p-2 text-sky-700">
                <Icon size={20} />
              </div>
              <h3 className="text-sm font-bold text-navy-950">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-navy-600">{detail}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
