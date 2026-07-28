import { Link } from 'react-router-dom';
import { ArrowRight, Check, FileCheck2, LockKeyhole, Scale, ShieldCheck } from 'lucide-react';

const steps = [
  ['Get your reports', 'Securely import your Experian, Equifax, and TransUnion reports.'],
  ['Start a secure review', 'Review your reports in one private, guided workspace.'],
  ['Understand possible review points', 'See plain-English findings that may deserve a closer look.'],
  ['Organize supporting records', 'Keep statements, letters, and notes connected to the right item.'],
  ['Approve each next step', 'You stay in control before any dispute support moves forward.'],
  ['Track responses and updates', 'Follow bureau and furnisher replies without juggling spreadsheets.'],
];

const plans = [
  ['Free Scan', 'Start with a secure review of your reports.', ['Import 3-bureau reports', 'Plain-English summary', 'Possible review points', 'Portal access']],
  ['AI Guided', 'Go deeper with evidence and response tools.', ['Everything in Free Scan', 'Unlimited review points', 'Evidence organizer', 'Response tracking']],
  ['Plus Managed', 'Get expert guidance while you stay in control.', ['Everything in AI Guided', 'Expert case review', 'Strategy recommendations', 'Ongoing tracking']],
  ['Legal Review', 'A separate attorney path for eligible matters.', ['Eligibility screening', 'Independent attorney review', 'Separate engagement', 'Clear next steps']],
];

function PortalPreview() {
  const bureaus = [['Experian', 'Reviewed', 'bg-fuchsia-700'], ['Equifax', 'In review', 'bg-rose-700'], ['TransUnion', 'In review', 'bg-sky-600']];
  const findings = [
    ['Needs review', 'Late payment reported 03/2023', '2 records'],
    ['Needs review', 'Account balance may be incomplete', '1 record'],
    ['Reviewed', 'Collection account â€” payment recorded', '3 records'],
  ];
  return (
    <div className="cv-portal-float overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_28px_70px_rgba(8,38,74,.14)]">
      <div className="flex h-10 items-center gap-1.5 border-b border-slate-200 bg-slate-50 px-3">
        <i className="h-2 w-2 rounded-full bg-rose-300" />
        <i className="h-2 w-2 rounded-full bg-amber-300" />
        <i className="h-2 w-2 rounded-full bg-emerald-300" />
        <b className="ml-2 text-[11px] text-slate-600">CreditVivo portal</b>
        <span className="ml-auto text-[10px] text-slate-400">Secure preview</span>
      </div>
      <div className="grid min-h-[390px] grid-cols-[130px_1fr] max-sm:grid-cols-1">
        <aside className="bg-gradient-to-b from-[#082f5b] to-[#061f40] p-4 text-white max-sm:hidden">
          <b className="mb-7 block text-sm">CreditVivo</b>
          {['Overview', 'Reports', 'Review points', 'Evidence', 'Responses'].map((item, i) => (
            <span key={item} className={`mb-2 block rounded px-2 py-2 text-[10px] ${i === 0 ? 'bg-emerald-600' : 'text-slate-300'}`}>{item}</span>
          ))}
        </aside>
        <div className="min-w-0 bg-slate-50 p-5 max-sm:p-4">
          <div className="mb-4 flex items-start justify-between">
            <div><small className="text-[10px] text-slate-500">Your credit workspace</small><h3 className="text-lg font-bold text-navy-900">Report review</h3></div>
            <span className="text-[10px] text-slate-400">Updated today</span>
          </div>
          <div className="mb-3 grid grid-cols-3 gap-2 max-sm:grid-cols-1">
            {bureaus.map(([name, status, color], i) => (
              <div key={name} className={`flex items-center gap-2 rounded border border-slate-200 bg-white p-2.5 ${i > 0 ? 'max-sm:hidden' : ''}`}>
                <b className={`grid h-6 w-6 place-items-center rounded-full text-[10px] text-white ${color}`}>{name[0]}</b>
                <span><strong className="block text-[10px] text-navy-800">{name}</strong><small className="text-[9px] text-slate-500">{status}</small></span>
              </div>
            ))}
          </div>
          <div className="rounded border border-slate-200 bg-white">
            <div className="flex justify-between border-b border-slate-200 p-3 text-[10px]"><b>Possible review points</b><span className="text-emerald-700">View all</span></div>
            {findings.map(([status, item, records]) => (
              <div key={item} className="grid grid-cols-[80px_1fr_52px] gap-2 border-b border-slate-100 p-3 text-[9px] last:border-0 max-sm:grid-cols-[72px_1fr]">
                <b className={status === 'Reviewed' ? 'text-emerald-700' : 'text-amber-700'}>{status}</b>
                <span className="truncate text-slate-700">{item}</span>
                <small className="text-right text-slate-400 max-sm:hidden">{records}</small>
              </div>
            ))}
          </div>
          <div className="mt-6 grid grid-cols-5">
            {['Reports', 'AI review', 'Review points', 'Approval', 'Responses'].map((item, i) => (
              <div key={item} className="relative text-center before:absolute before:left-0 before:right-0 before:top-2 before:h-px before:bg-slate-300 first:before:left-1/2 last:before:right-1/2">
                <i className={`cv-progress-dot relative z-10 mx-auto grid h-4 w-4 place-items-center rounded-full border text-[8px] not-italic ${i < 3 ? 'border-emerald-700 bg-emerald-700 text-white' : 'border-slate-400 bg-white text-slate-500'}`} style={{ animationDelay: `${i * 180}ms` }}>{i < 3 ? 'âœ“' : i + 1}</i>
                <small className="mt-2 block text-[8px] text-slate-500 max-sm:hidden">{item}</small>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <>
      <section className="bg-white py-20 lg:py-28">
        <div className="mx-auto grid max-w-[1440px] items-center gap-14 px-6 lg:grid-cols-[.86fr_1.2fr] lg:px-10">
          <div className="cv-hero-enter">
            <h1 className="max-w-[630px] text-[46px] font-extrabold leading-[.98] tracking-[-.055em] text-navy-950 sm:text-[64px] lg:text-[76px]">
              Credit improvement you can see, prove, and track.
            </h1>
            <p className="mt-7 max-w-[610px] text-[17px] leading-8 text-slate-600">
              CreditVivo helps you review your credit reports, spot possible inaccuracies, organize evidence,
              prepare dispute support, and track every bureau and furnisher response in one secure portal.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/scan" className="cv-cta-shine btn-primary rounded-md px-6 py-3.5">Start free scan <ArrowRight size={16} /></Link>
              <Link to="/dashboard" className="btn-outline rounded-md px-6 py-3.5">View portal preview</Link>
            </div>
            <p className="mt-4 text-xs text-slate-500">No hard pull. You approve every next step.</p>
          </div>
          <PortalPreview />
        </div>
      </section>

      <section className="border-y border-slate-200 bg-sky-50/60">
        <div className="mx-auto grid max-w-[1440px] grid-cols-1 px-6 sm:grid-cols-2 lg:grid-cols-4 lg:px-10">
          {[
            [ShieldCheck, 'No hard pull', 'Reviewing your reports does not impact your score.'],
            [FileCheck2, 'Evidence-based review', 'Findings connect to report details and records you provide.'],
            [LockKeyhole, 'Secure document vault', 'Keep sensitive records in one private workspace.'],
            [Scale, 'Attorney review if eligible', 'Legal services require separate eligibility and engagement.'],
          ].map(([Icon, title, copy]) => {
            const TrustIcon = Icon as typeof ShieldCheck;
            return <div key={String(title)} className="flex gap-4 border-b border-slate-200 py-7 lg:border-b-0 lg:border-r lg:px-6 lg:last:border-0">
              <TrustIcon className="shrink-0 text-emerald-700" size={28} />
              <p><b className="block text-sm text-navy-900">{String(title)}</b><small className="mt-1 block text-[11px] leading-5 text-slate-500">{String(copy)}</small></p>
            </div>;
          })}
        </div>
      </section>

      <section id="how-it-works" className="cv-section-reveal bg-white py-24">
        <div className="mx-auto grid max-w-7xl gap-14 px-6 lg:grid-cols-[.65fr_1.35fr]">
          <div><h2 className="text-4xl font-bold tracking-tight text-navy-950">A clear path from report to response</h2><p className="mt-4 leading-7 text-slate-600">One guided process keeps the details organized and you in control.</p></div>
          <ol>
            {steps.map(([title, copy], i) => (
              <li key={title} className="grid grid-cols-[40px_210px_1fr] items-center gap-5 border-b border-slate-200 py-5 max-sm:grid-cols-[36px_1fr]">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-emerald-700 text-xs font-bold text-white">{i + 1}</span>
                <strong className="text-sm text-navy-900">{title}</strong>
                <p className="m-0 text-sm leading-6 text-slate-500 max-sm:col-start-2">{copy}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="ai-review" className="cv-section-reveal border-y border-slate-200 bg-sky-50/60 py-24">
        <div className="mx-auto grid max-w-7xl gap-14 px-6 lg:grid-cols-[.8fr_1.4fr]">
          <div><h2 className="text-4xl font-bold tracking-tight text-navy-950">Powerful review behind the scenes. Plain English in front.</h2><p className="mt-5 leading-7 text-slate-600">CreditVivo helps surface possible review points, then shows why each item deserves attention. No raw parser logs, confusing technical output, or automatic dispute sending.</p></div>
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['01', 'Report analysis', 'Cross-checks account details, dates, balances, and public-record data.'],
              ['02', 'Plain-English findings', 'Explains each possible review point and why it was flagged.'],
              ['03', 'Source evidence', 'Keeps report details and your supporting records together.'],
              ['04', 'Human approval', 'You review and approve each step. Nothing is sent automatically.'],
            ].map(([number, title, copy]) => <article key={title} className="border-l border-slate-300 pl-5"><span className="text-xs font-bold tracking-widest text-emerald-700">{number}</span><h3 className="mt-7 text-sm font-bold text-navy-900">{title}</h3><p className="mt-3 text-xs leading-6 text-slate-500">{copy}</p></article>)}
          </div>
        </div>
      </section>

      <section id="portal" className="cv-section-reveal bg-white py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 max-w-2xl"><h2 className="text-4xl font-bold tracking-tight text-navy-950">Everything connected to the right next step.</h2><p className="mt-4 leading-7 text-slate-600">Review a finding, see its source, organize evidence, and follow every response in one calm workspace.</p></div>
          <PortalPreview />
        </div>
      </section>

      <section id="plans" className="cv-section-reveal border-t border-slate-200 bg-slate-50 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto mb-12 max-w-2xl text-center"><h2 className="text-4xl font-bold tracking-tight text-navy-950">Choose the level of support you need.</h2><p className="mt-4 text-slate-600">Start free. See plan details before you commit to paid support.</p></div>
          <div className="grid overflow-hidden rounded-lg border border-slate-200 bg-white md:grid-cols-2 lg:grid-cols-4">
            {plans.map(([name, copy, features], i) => (
              <article key={String(name)} className={`border-b border-slate-200 p-7 lg:min-h-[360px] lg:border-b-0 lg:border-r lg:last:border-0 ${i === 1 ? 'shadow-[inset_0_4px_0_#087e73]' : ''}`}>
                <h3 className="text-lg font-bold text-navy-950">{String(name)}</h3>
                <p className="mt-3 min-h-[48px] text-xs leading-5 text-slate-500">{String(copy)}</p>
                <ul className="my-7 space-y-3">{(features as string[]).map((feature) => <li key={feature} className="flex gap-2 text-xs text-slate-600"><Check size={14} className="text-emerald-700" />{feature}</li>)}</ul>
                <Link to={i === 0 ? '/scan' : '/pricing'} className={i === 1 ? 'btn-primary rounded-md text-xs' : 'btn-outline rounded-md text-xs'}>{i === 0 ? 'Get started' : i === 3 ? 'Learn more' : 'See plan details'}</Link>
              </article>
            ))}
          </div>
          <p className="mt-4 text-center text-[11px] text-slate-500">Attorney services require separate eligibility review and attorney engagement. Not all matters will qualify.</p>
        </div>
      </section>

      <section className="bg-sky-50 py-16">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-8 px-6 lg:flex-row lg:items-center">
          <div><h2 className="text-3xl font-bold text-navy-950">Take control of your credit story.</h2><p className="mt-2 text-slate-600">Start with a secure review and clear, human-approved next steps.</p></div>
          <div className="flex flex-wrap gap-3"><Link to="/scan" className="btn-primary rounded-md">Start free scan</Link><Link to="/dashboard" className="btn-outline rounded-md">View portal preview</Link></div>
        </div>
      </section>
    </>
  );
}
