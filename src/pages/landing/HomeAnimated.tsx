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
  ScanLine,
  Bell,
} from 'lucide-react';
import ScrollReveal from '../../components/ScrollReveal';
import AnimatedCounter from '../../components/AnimatedCounter';
import ProgressBar from '../../components/ProgressBar';

/* ===== Animated Hero Dashboard ===== */
function AnimatedDashboard() {
  return (
    <div className="relative mx-auto w-full max-w-[520px] anim-float-soft">
      {/* Scan line glow */}
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-emerald-400/10 via-teal-400/5 to-transparent blur-2xl" />

      {/* Main dashboard card */}
      <div className="glass-card anim-pulse-glow rounded-2xl p-5 shadow-2xl shadow-navy-900/15">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-rose-500 anim-blink-dot" />
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">AI Scanning</span>
          </div>
          <span className="text-[10px] font-medium text-navy-400">Live preview</span>
        </div>

        {/* Score tile */}
        <div className="mb-4 rounded-xl bg-gradient-to-br from-emerald-50 to-cyan-50 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold text-navy-500">Credit Readiness</span>
            <TrendingUp size={14} className="text-emerald-600" />
          </div>
          <div className="flex items-end gap-2">
            <AnimatedCounter value={672} className="text-4xl font-extrabold text-emerald-700" />
            <span className="pb-1 text-xs font-semibold text-emerald-500">+8 pts</span>
          </div>
          <div className="mt-3">
            <ProgressBar percent={67} height="h-1.5" />
          </div>
        </div>

        {/* Issue cards */}
        <div className="space-y-2">
          {[
            { label: 'Late payment — flagged', status: 'Review', color: 'bg-amber-100 text-amber-700', dot: 'bg-amber-500' },
            { label: 'Duplicate collection found', status: 'Prep', color: 'bg-rose-100 text-rose-600', dot: 'bg-rose-500' },
            { label: 'Address mismatch', status: 'Filed', color: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' },
          ].map((item, i) => (
            <div
              key={item.label}
              className={`anim-slide-right stagger-${i + 1} flex items-center justify-between rounded-lg border border-navy-100/50 bg-white/80 px-3 py-2.5`}
            >
              <div className="flex items-center gap-2.5">
                <span className={`h-2 w-2 rounded-full ${item.dot} anim-blink-dot`} />
                <span className="text-xs font-medium text-navy-700">{item.label}</span>
              </div>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${item.color}`}>{item.status}</span>
            </div>
          ))}
        </div>

        {/* Progress footer */}
        <div className="mt-4 border-t border-navy-100/40 pt-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-navy-400">Report Scan Progress</span>
            <span className="text-[10px] font-bold text-emerald-600">87%</span>
          </div>
          <ProgressBar percent={87} height="h-1" />
        </div>
      </div>

      {/* Floating AI badge */}
      <div className="anim-float-delayed absolute -right-6 top-10 glass-card rounded-xl p-3 shadow-xl shadow-navy-900/12">
        <div className="flex items-center gap-2">
          <BrainCircuit size={18} className="text-emerald-600" />
          <div>
            <p className="text-[10px] font-extrabold uppercase text-navy-500">AI Engine</p>
            <p className="text-[9px] text-emerald-600">3 issues found</p>
          </div>
        </div>
      </div>

      {/* Floating roadmap card */}
      <div className="anim-float-soft absolute -left-8 bottom-8 glass-card rounded-xl p-3 shadow-xl shadow-navy-900/12">
        <div className="flex items-center gap-2">
          <CheckCircle size={16} className="text-emerald-600" />
          <span className="text-[10px] font-semibold text-navy-600">Roadmap ready</span>
        </div>
        <div className="mt-2 space-y-1">
          <ProgressBar percent={100} height="h-1" />
          <ProgressBar percent={60} height="h-1" />
        </div>
      </div>

      {/* Alert bell */}
      <div className="anim-float-delayed absolute -right-3 -top-3 flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-lg anim-pulse-glow">
        <Bell size={16} className="text-emerald-600" />
        <span className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full bg-rose-500 anim-blink-dot" />
      </div>
    </div>
  );
}

/* ===== Animated Hero ===== */
function Hero() {
  return (
    <section className="lively-hero-bg overflow-hidden py-14 md:py-20">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="relative z-10">
            <div className="anim-slide-right mb-5 inline-flex items-center gap-2 rounded-lg border border-emerald-100 bg-white/85 px-4 py-2 text-sm font-bold text-emerald-800 shadow-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-rose-500 anim-blink-dot" />
              No hard pull to start
            </div>

            <h1 className="anim-fade-in mb-4 text-[34px] font-bold leading-tight text-navy-900 sm:text-[40px]">
              AI Credit Review with{' '}
              <span className="text-gradient-vivo">Attorney Guidance</span> When You Need It
            </h1>

            <p className="anim-fade-in stagger-2 text-base text-navy-500 leading-relaxed mb-6 max-w-xl">
              Credit Vivo uses AI to analyze your credit report, explain issues in plain English,
              and prepare your file for attorney review when the situation calls for it. We help
              you repair inaccuracies, maintain healthier credit, and build stronger financial
              opportunities.
            </p>

            <div className="anim-fade-in stagger-3 mb-6 flex flex-wrap gap-3">
              <a href="/dashboard.html" className="btn-primary shine-on-hover text-sm py-3 px-6">
                Start Free Credit Check-In
                <ArrowRight size={15} />
              </a>
              <Link to="/why" className="btn-outline text-sm py-3 px-6">
                See How It Works
              </Link>
            </div>

            <p className="anim-fade-in stagger-4 text-[12px] text-navy-400">
              Not a law firm. No guaranteed score increases. Results vary.
            </p>
          </div>

          <div className="hidden justify-center lg:flex">
            <AnimatedDashboard />
          </div>
        </div>
      </div>
    </section>
  );
}

/* ===== Trust Strip ===== */
function TrustStrip() {
  return (
    <section className="border-y border-navy-100/70 bg-white py-7">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['Free Check-In', 'Plain English', 'Review Options', 'Attorney Guidance', 'Progress Tracking'].map((item, i) => (
            <ScrollReveal key={item} variant="fade" delay={i * 0.08} className="lively-trust-pill text-center py-2">
              <span className="text-xs font-semibold text-navy-600">{item}</span>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== Stats Bar (Dovly-style counters) ===== */
function StatsBar() {
  return (
    <section className="bg-gradient-to-br from-navy-950 via-navy-900 to-emerald-950 py-12">
      <div className="mx-auto max-w-5xl px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { value: 3, suffix: '+', label: 'Issue types detected' },
            { value: 87, suffix: '%', label: 'Report scan accuracy' },
            { value: 4, suffix: ' steps', label: 'From scan to action' },
            { value: 0, prefix: '$', label: 'Cost to start' },
          ].map((stat, i) => (
            <ScrollReveal key={stat.label} variant="scale" delay={i * 0.1}>
              <AnimatedCounter
                value={stat.value}
                prefix={stat.prefix ?? ''}
                suffix={stat.suffix ?? ''}
                className="block text-3xl font-extrabold text-emerald-400"
              />
              <span className="mt-1 block text-[11px] font-semibold uppercase tracking-wider text-navy-300">{stat.label}</span>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== Vision Section ===== */
function VisionSection() {
  return (
    <section className="bg-gradient-to-br from-navy-950 via-navy-900 to-emerald-950 py-14">
      <div className="mx-auto max-w-7xl px-6 text-center">
        <ScrollReveal variant="fade">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-emerald-200">Simple credit help</p>
          <h2 className="mb-3 text-[22px] font-semibold text-white sm:text-[26px]">
            Know what is wrong. <span className="text-amber-300">Know what to do next.</span>
          </h2>
          <p className="text-sm text-navy-300 max-w-lg mx-auto mb-10">
            Credit Vivo reviews your report, explains possible problems in normal language, and
            helps organize the next step if something needs to be challenged.
          </p>
        </ScrollReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: 'Check', desc: 'Look for possible report problems without a hard pull.', icon: ScanLine },
            { title: 'Explain', desc: 'Show the issues in plain English, not credit bureau jargon.', icon: FileSearch },
            { title: 'Prepare', desc: 'Organize documents and draft next steps before anything is sent.', icon: Calendar },
            { title: 'Track', desc: 'Follow what happened, what is waiting, and what comes next.', icon: TrendingUp },
          ].map((g, i) => (
            <ScrollReveal key={g.title} variant="up" delay={i * 0.1} className="lively-dark-card hover-lift rounded-xl border border-white/10 bg-white/[0.04] p-5 text-left">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-800/40 to-teal-800/40">
                <g.icon size={16} className="text-emerald-400" />
              </div>
              <h3 className="text-sm font-bold text-white mb-1">{g.title}</h3>
              <p className="text-xs text-navy-300">{g.desc}</p>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== How It Works ===== */
function HowItWorks() {
  return (
    <section className="bg-white py-14">
      <div className="mx-auto max-w-7xl px-6">
        <ScrollReveal variant="fade" className="mb-12 text-center">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">How it works</p>
          <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">
            From free check-in to clear next steps.
          </h2>
        </ScrollReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { num: '01', title: 'Start your free Check-In', desc: 'Upload or connect a report without affecting your score.', icon: BrainCircuit },
            { num: '02', title: 'See possible problems', desc: 'Credit Vivo points out items that may need a closer look.', icon: FileSearch },
            { num: '03', title: 'Review your options', desc: 'See what can be disputed, what needs proof, and what should wait.', icon: Calendar },
            { num: '04', title: 'Get help if it is serious', desc: 'Hard cases can be prepared for attorney review when appropriate.', icon: Scale },
          ].map(({ num, title, desc, icon: Icon }, i) => (
            <ScrollReveal key={num} variant="up" delay={i * 0.12} className="lively-step-card hover-lift shine-on-hover rounded-xl border border-navy-100 bg-white p-5 shadow-sm shadow-navy-100/50">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-100 to-cyan-100">
                  <Icon size={16} className="text-emerald-700" />
                </div>
                <span className="text-xl font-bold text-rose-200">{num}</span>
              </div>
              <h3 className="text-sm font-bold text-navy-900 mb-1">{title}</h3>
              <p className="text-xs text-navy-500 leading-relaxed">{desc}</p>
            </ScrollReveal>
          ))}
        </div>

        <ScrollReveal variant="fade" delay={0.3} className="mt-8 text-center">
          <p className="text-[11px] text-navy-400">
            You have the right to dispute credit report errors yourself for free. Credit Vivo helps
            organize and prepare, but you approve everything before it is sent.
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ===== What We Help With ===== */
function WhatWeHelpWith() {
  return (
    <section className="bg-emerald-50/35 py-14">
      <div className="mx-auto max-w-7xl px-6">
        <ScrollReveal variant="fade" className="mb-12 text-center">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">What we help with</p>
          <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">Smart review with human help.</h2>
        </ScrollReveal>

        <div className="grid md:grid-cols-3 gap-5">
          {[
            { icon: BrainCircuit, title: 'AI report analysis', desc: 'Review raw report data for possible errors, bureau mismatches, missing dates, duplicate reporting, collections, and charge-off issues.', color: 'bg-emerald-100 text-emerald-700' },
            { icon: Sparkles, title: 'Dispute workflow', desc: 'Prepare draft letters, supporting notes, evidence packets, and tracking details before anything is sent.', color: 'bg-rose-100 text-rose-600' },
            { icon: Scale, title: 'Attorney guidance', desc: 'When the issue is more serious, Credit Vivo can help prepare your file for attorney review via LegalShield.', color: 'bg-amber-100 text-amber-700' },
          ].map(({ icon: Icon, title, desc, color }, i) => (
            <ScrollReveal key={title} variant="up" delay={i * 0.12} className="lively-step-card hover-lift shine-on-hover rounded-xl border border-navy-100 bg-white p-6 shadow-sm shadow-navy-100/50">
              <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center mb-4`}>
                <Icon size={18} />
              </div>
              <h3 className="text-[15px] font-bold text-navy-900 mb-2">{title}</h3>
              <p className="text-sm text-navy-500 leading-relaxed">{desc}</p>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== Real-Life Goals ===== */
function RealLifeGoals() {
  const goals = [
    { icon: '🚗', title: 'Auto loans', desc: 'Prepare for auto financing readiness.' },
    { icon: '🏠', title: 'Mortgage', desc: 'Work toward mortgage application readiness.' },
    { icon: '🔑', title: 'Rental housing', desc: 'Strengthen rental application potential.' },
    { icon: '🛡️', title: 'Insurance', desc: 'Support better insurance quote options.' },
    { icon: '💼', title: 'Employment', desc: 'Prepare for credit-related employment checks.' },
  ];

  return (
    <section className="bg-white py-14">
      <div className="mx-auto max-w-7xl px-6">
        <ScrollReveal variant="fade" className="mb-10 text-center">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">Built for real-life goals</p>
          <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">Better credit can open more doors.</h2>
        </ScrollReveal>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {goals.map((goal, i) => (
            <ScrollReveal key={goal.title} variant="scale" delay={i * 0.08} className="hover-lift rounded-xl border border-navy-100 bg-gradient-to-b from-white to-emerald-50/30 p-5 text-center">
              <div className="text-2xl mb-2">{goal.icon}</div>
              <h3 className="text-xs font-bold text-navy-900 mb-1">{goal.title}</h3>
              <p className="text-[11px] text-navy-500 leading-relaxed">{goal.desc}</p>
            </ScrollReveal>
          ))}
        </div>

        <ScrollReveal variant="fade" delay={0.2} className="mt-6 text-center">
          <p className="text-[11px] text-navy-400">
            Credit Vivo does not guarantee loan, housing, insurance, or job approval.
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ===== Pricing Preview ===== */
function PricingPreview() {
  return (
    <section className="bg-navy-50/50 py-14">
      <div className="mx-auto max-w-5xl px-6">
        <ScrollReveal variant="fade" className="mb-8 text-center">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">Pricing</p>
          <h2 className="text-[22px] font-semibold text-navy-900 sm:text-[26px]">Start free. Add support when ready.</h2>
        </ScrollReveal>

        <div className="grid md:grid-cols-4 gap-4">
          {[
            { name: 'Free Check-In', price: '$0', desc: 'AI issue preview', featured: false },
            { name: 'AI Guided', price: '$69', desc: 'Guided support + tracking', featured: true },
            { name: 'Vivo Plus', price: '$95', desc: 'Full dispute workflow', featured: false },
            { name: 'Attorney Prep', price: '$95', desc: '+$50 LegalShield access', featured: false },
          ].map((plan, i) => (
            <ScrollReveal key={plan.name} variant="up" delay={i * 0.1} className={`hover-lift rounded-xl border p-5 text-center ${plan.featured ? 'border-emerald-300 bg-gradient-to-b from-white to-emerald-50/60 ring-2 ring-emerald-100' : 'border-navy-100 bg-white'}`}>
              <h3 className="text-sm font-bold text-navy-900">{plan.name}</h3>
              <div className="my-3 flex items-end justify-center gap-1">
                <span className="text-2xl font-extrabold text-navy-900">{plan.price}</span>
                <span className="pb-0.5 text-xs font-semibold text-navy-400">/mo</span>
              </div>
              <p className="text-[11px] text-navy-500">{plan.desc}</p>
            </ScrollReveal>
          ))}
        </div>

        <ScrollReveal variant="fade" delay={0.2} className="mt-6 text-center">
          <Link to="/pricing" className="btn-soft text-xs">
            See full pricing details
            <ArrowRight size={13} />
          </Link>
          <p className="mt-3 text-[10px] text-navy-400">
            Credit service companies cannot promise a result or credit score increase. Results vary by consumer.
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ===== Learning Center ===== */
function LearningCenter() {
  return (
    <section className="bg-white py-14">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-center justify-between mb-8">
          <ScrollReveal variant="left">
            <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-sky-700">Learning Center</p>
            <h2 className="text-xl font-semibold text-navy-900">Credit basics made simple.</h2>
          </ScrollReveal>
          <ScrollReveal variant="right" className="hidden sm:block">
            <Link to="/learning" className="btn-soft text-xs">
              View all lessons
              <ArrowRight size={13} />
            </Link>
          </ScrollReveal>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { cat: 'Beginner', title: 'What affects your score?', desc: 'Payment history, balances, credit age, new applications, and account mix all matter.' },
            { cat: 'Report Review', title: 'What is a collection?', desc: 'A collection means a debt may have been sent or sold to a collector.' },
            { cat: 'Goals', title: 'Before buying a home', desc: 'Start early, keep payments on time, lower balances, and avoid new debt.' },
          ].map((l, i) => (
            <ScrollReveal key={l.title} variant="up" delay={i * 0.1} className="hover-lift rounded-xl border border-navy-100 bg-white p-5 shadow-sm shadow-navy-100/50">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-sky-600">{l.cat}</span>
              <h3 className="text-sm font-bold text-navy-900 mt-1 mb-1">{l.title}</h3>
              <p className="text-xs text-navy-500 leading-relaxed">{l.desc}</p>
            </ScrollReveal>
          ))}
        </div>

        <div className="mt-6 sm:hidden">
          <Link to="/learning" className="btn-soft text-xs w-full">
            View all lessons <ArrowRight size={13} />
          </Link>
        </div>
      </div>
    </section>
  );
}

/* ===== Final CTA ===== */
function FinalCTA() {
  return (
    <section className="bg-gradient-to-br from-navy-950 via-emerald-950 to-navy-900 py-14">
      <div className="max-w-2xl mx-auto px-4 text-center">
        <ScrollReveal variant="scale">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-emerald-200">Ready to start?</p>
          <h2 className="mb-3 text-[22px] font-semibold text-white sm:text-[26px]">
            Start with the AI Credit Check-In.
          </h2>
          <p className="text-sm text-navy-300 mb-6">
            See possible report errors first. Upgrade later if you want guided next steps or
            attorney-ready support.
          </p>
          <a href="/dashboard.html" className="btn-mint shine-on-hover text-sm py-3 px-7">
            Join Free
            <ArrowRight size={15} />
          </a>
          <p className="mt-4 text-[11px] text-navy-400">
            Credit Vivo is not a law firm. We do not promise specific results or credit score increases.
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ===== Main Page ===== */
export default function HomeAnimated() {
  return (
    <>
      <Hero />
      <TrustStrip />
      <StatsBar />
      <VisionSection />
      <HowItWorks />
      <WhatWeHelpWith />
      <RealLifeGoals />
      <PricingPreview />
      <LearningCenter />
      <FinalCTA />
    </>
  );
}
