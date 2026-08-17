import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle,
  TrendingUp,
  BrainCircuit,
  Scale,
  FileSearch,
  Sparkles,
  Calendar,
} from 'lucide-react';

function HeroCard() {
  return (
    <div className="lively-hero-card w-full max-w-sm rounded-xl border border-white/70 bg-white/92 p-5 shadow-xl shadow-navy-900/14 backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider text-emerald-700">Your Roadmap</p>
          <p className="mt-0.5 text-sm font-bold text-navy-900">AI + Attorney Review</p>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-100 to-cyan-100">
          <TrendingUp size={16} className="text-emerald-700" />
        </div>
      </div>
      <div className="space-y-2.5">
        {[
          { label: 'AI scan completed', done: true },
          { label: 'Errors prioritized', done: true },
          { label: 'Attorney review option checked', done: false },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-2.5 rounded-lg bg-navy-50/70 px-3 py-2">
            <div className={`flex h-5 w-5 items-center justify-center rounded-full ${item.done ? 'bg-emerald-600' : 'bg-rose-200'}`}>
              {item.done && <CheckCircle size={12} className="text-white" />}
            </div>
            <span className={`text-xs font-medium ${item.done ? 'text-navy-700' : 'text-navy-400'}`}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-2 border-t border-navy-100/60 pt-3">
        <div className="h-2 w-2 rounded-full bg-rose-500" />
        <span className="text-[11px] text-navy-500">Draft review only</span>
      </div>
    </div>
  );
}

function HeroVisual() {
  return (
    <div className="lively-hero-visual relative mx-auto w-full max-w-[520px]">
      <div className="lively-spark lively-spark-one" />
      <div className="lively-spark lively-spark-two" />
      <div className="absolute -right-5 -top-8 z-10 w-56 rounded-xl border border-white/80 bg-white/95 p-4 shadow-xl shadow-navy-900/12 backdrop-blur">
        <p className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700">
          AI scanner path
        </p>
        <div className="mt-2 grid gap-1.5 text-[11px] font-semibold text-navy-700">
          <span>Soft report pull</span>
          <span>Raw report parsing</span>
          <span>File ready for review</span>
        </div>
      </div>
      <div className="overflow-hidden rounded-2xl border border-white/70 bg-white shadow-2xl shadow-navy-900/18">
        <img
          src="/brand/credit-vivo-hero.png"
          alt="Credit Vivo dashboard preview"
          className="h-[360px] w-full object-cover object-center"
        />
      </div>
      <div className="lively-score-card rounded-xl border border-white/80 bg-white/95 p-4 shadow-xl shadow-navy-900/16 backdrop-blur">
        <b className="block text-4xl leading-none text-emerald-600">AI</b>
        <span className="text-[11px] font-extrabold uppercase text-navy-500">review engine</span>
      </div>
      <div className="lively-check-card">
        <HeroCard />
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="lively-hero-bg overflow-hidden py-14 md:py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div className="relative z-10">
              <div className="mb-5 inline-flex items-center gap-2 rounded-lg border border-emerald-100 bg-white/85 px-4 py-2 text-sm font-bold text-emerald-800 shadow-sm shadow-emerald-900/5">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
                No hard pull to start
              </div>

              <h1 className="mb-4 text-[34px] font-bold leading-tight text-navy-900 sm:text-[40px]">
                AI Credit Review + Attorney-Ready Prep
              </h1>

              <p className="text-base text-navy-500 leading-relaxed mb-6 max-w-xl">
                Credit Vivo uses advanced AI to analyze your credit report. See your errors in plain English, track your progress, and seamlessly prepare your file for attorney review when the situation demands it.
              </p>

              <div className="mb-8 flex flex-wrap gap-3">
                <a href="/login" className="btn-primary text-sm py-3 px-6">
                  Start Free Credit Check-In
                  <ArrowRight size={15} />
                </a>
                <Link to="/why" className="btn-outline text-sm py-3 px-6">
                  Why Credit Vivo
                </Link>
              </div>

              <div className="flex flex-wrap gap-4">
                {['Plain-English review', 'Attorney support when needed', 'No hard pull to start'].map((t) => (
                  <span key={t} className="flex items-center gap-1.5 text-[12px] text-navy-500">
                    <CheckCircle size={13} className="text-emerald-700" />
                    {t}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-[11px] leading-relaxed text-navy-400 max-w-xl">
                Credit Vivo is educational software, not a credit repair organization or
                law firm. No guaranteed score increases — results are not guaranteed.
              </p>
              <div className="mt-6 rounded-xl border border-emerald-100 bg-white/85 p-4 shadow-sm shadow-emerald-900/5 lg:hidden">
                <p className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700">
                  What happens next
                </p>
                <p className="mt-1 text-xs font-semibold text-navy-700">
                  Check your report, understand issues, choose next steps
                </p>
              </div>
            </div>

            <div className="hidden justify-center lg:flex">
              <HeroVisual />
            </div>
          </div>
        </div>
      </section>

      {/* Trust strip */}
      <section className="border-y border-navy-100/70 bg-white py-7">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {['Free Check-In', 'Plain English', 'Review Options', 'Attorney Access', 'Progress Tracking'].map((item) => (
              <div key={item} className="lively-trust-pill text-center py-2">
                <span className="text-xs font-semibold text-navy-600">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Vision section */}
      <section className="bg-gradient-to-br from-navy-950 via-navy-900 to-emerald-950 py-14">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-emerald-200">Simple credit help</p>
          <h2 className="mb-3 text-[22px] font-semibold text-white sm:text-[26px]">
            Know what is wrong. <span className="text-amber-300">Know what to do next.</span>
          </h2>
          <p className="text-sm text-navy-300 max-w-lg mx-auto mb-10">
            Credit Vivo reviews your report, explains possible problems in normal language, and helps organize the next step if something needs to be challenged.
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: 'Check', desc: 'Look for possible report problems without a hard pull.' },
              { title: 'Explain', desc: 'Show the issues in plain English, not credit bureau jargon.' },
              { title: 'Prepare', desc: 'Organize documents and draft next steps before anything is sent.' },
              { title: 'Track', desc: 'Follow what happened, what is waiting, and what comes next.' },
            ].map((g) => (
              <div key={g.title} className="lively-dark-card rounded-xl border border-white/10 bg-white/[0.04] p-5 text-left">
                <h3 className="text-sm font-bold text-white mb-1">{g.title}</h3>
                <p className="text-xs text-navy-300">{g.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white py-14">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center mb-12">
            <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">How it works</p>
            <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">
              From free check-in to clear next steps.
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { num: '01', title: 'Start your free Check-In', desc: 'Upload or connect a report without affecting your score.', icon: BrainCircuit },
              { num: '02', title: 'See possible problems', desc: 'Credit Vivo points out items that may need a closer look.', icon: FileSearch },
              { num: '03', title: 'Review your options', desc: 'See what can be disputed, what needs proof, and what should wait.', icon: Calendar },
              { num: '04', title: 'Get help if it is serious', desc: 'Hard cases can be prepared for attorney review when appropriate.', icon: Scale },
            ].map(({ num, title, desc, icon: Icon }) => (
              <div key={num} className="lively-step-card rounded-xl border border-navy-100 bg-white p-5 shadow-sm shadow-navy-100/50">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-100 to-cyan-100">
                    <Icon size={16} className="text-emerald-700" />
                  </div>
                  <span className="text-xl font-bold text-rose-200">{num}</span>
                </div>
                <h3 className="text-sm font-bold text-navy-900 mb-1">{title}</h3>
                <p className="text-xs text-navy-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
          <p className="mt-6 text-center text-[11px] leading-relaxed text-navy-400 max-w-2xl mx-auto">
            You always have the right to dispute inaccurate or incomplete credit report
            information yourself, for free, directly with the credit bureaus and
            furnishers. Credit Vivo's tools are here to help you organize that process —
            not to replace a right you already have.
          </p>
        </div>
      </section>

      {/* What we help with */}
      <section className="bg-emerald-50/35 py-14">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center mb-12">
            <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">What we help with</p>
            <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">
              Smart review with human help.
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {[
              {
                icon: BrainCircuit,
                title: 'AI report analysis',
                desc: 'Review raw report data for possible errors, bureau mismatches, missing dates, duplicate reporting, collections, and charge-off issues.',
                color: 'bg-emerald-100 text-emerald-700',
              },
              {
                icon: Sparkles,
                title: 'Dispute workflow',
                desc: 'Prepare draft letters, supporting notes, evidence packets, and tracking details before anything is sent.',
                color: 'bg-rose-100 text-rose-600',
              },
              {
                icon: Scale,
                title: 'Attorney-ready prep',
                desc: 'When the issue is more serious, Credit Vivo can help organize your file for optional attorney review — attorney access itself is a separate, optional relationship, not legal representation by Credit Vivo.',
                color: 'bg-amber-100 text-amber-700',
              },
            ].map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="lively-step-card rounded-xl border border-navy-100 bg-white p-6 shadow-sm shadow-navy-100/50">
                <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center mb-4`}>
                  <Icon size={18} />
                </div>
                <h3 className="text-[15px] font-bold text-navy-900 mb-2">{title}</h3>
                <p className="text-sm text-navy-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Learning preview */}
      <section className="bg-white py-14">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">Learning Center</p>
              <h2 className="text-xl font-semibold text-navy-900">Credit basics made simple.</h2>
            </div>
            <Link to="/learning" className="btn-soft text-xs hidden sm:flex">
              View all lessons
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { cat: 'Beginner', title: 'What affects your score?', desc: 'Payment history, balances, credit age, new applications, and account mix all matter.' },
              { cat: 'Report Review', title: 'What is a collection?', desc: 'A collection means a debt may have been sent or sold to a collector.' },
              { cat: 'Goals', title: 'Before buying a home', desc: 'Start early, keep payments on time, lower balances, and avoid new debt.' },
            ].map((l) => (
              <div key={l.title} className="rounded-xl border border-navy-100 bg-white p-5 shadow-sm shadow-navy-100/50">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-sky-600">{l.cat}</span>
                <h3 className="text-sm font-bold text-navy-900 mt-1 mb-1">{l.title}</h3>
                <p className="text-xs text-navy-500 leading-relaxed">{l.desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 sm:hidden">
            <Link to="/learning" className="btn-soft text-xs w-full">
              View all lessons <ArrowRight size={13} />
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-gradient-to-br from-navy-950 via-emerald-950 to-navy-900 py-14">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-emerald-200">Ready to start?</p>
          <h2 className="mb-3 text-[22px] font-semibold text-white sm:text-[26px]">
            Start with the AI Credit Check-In.
          </h2>
          <p className="text-sm text-navy-300 mb-6">
            See possible report errors first. Upgrade later if you want guided next steps or attorney-ready support.
          </p>
          <a href="/login" className="btn-mint text-sm py-3 px-7">
            Join Free
            <ArrowRight size={15} />
          </a>
          <p className="mt-5 text-[11px] leading-relaxed text-navy-400 max-w-md mx-auto">
            Results are not guaranteed and vary by consumer. Credit Vivo is educational
            software, not a credit repair organization or law firm.
          </p>
        </div>
      </section>
    </>
  );
}
