import { Link } from 'react-router-dom';
import { Check, ArrowRight, Scale, Phone, FileText, ShieldCheck } from 'lucide-react';

const plans = [
  {
    badge: 'Start here',
    name: 'Free Check-In',
    price: '$0',
    cadence: '/mo',
    description: 'A free starting point to see what may be on your report before choosing support.',
    cta: 'Start Free',
    to: '/join',
    featured: false,
    features: [
      'No-hard-pull starting point',
      'One-report AI issue preview',
      'Plain-English summary',
      'See possible next steps',
      'Learning Center access',
    ],
  },
  {
    badge: 'Popular',
    name: 'AI Guided',
    price: '$69',
    cadence: '/mo',
    description: 'For customers who want guided support after the free scan, with clearer findings, tracking, and draft dispute prep.',
    cta: 'Choose AI Guided',
    to: '/join',
    featured: true,
    features: [
      'AI findings dashboard',
      'Draft dispute letter workspace',
      'Monthly roadmap updates',
      'Progress tracking',
      'Customer next-step reminders',
    ],
  },
  {
    badge: 'Full workflow',
    name: 'Vivo Plus',
    price: '$95',
    cadence: '/mo',
    description: 'For customers who want a fuller workflow for bureau, furnisher, tracking, and escalation preparation.',
    cta: 'Choose Vivo Plus',
    to: '/join',
    featured: false,
    features: [
      'Bureau dispute workflow',
      'Furnisher validation workflow',
      'Attorney-ready evidence packet',
      'CFPB and state complaint prep',
      'Priority file organization',
    ],
  },
  {
    badge: 'Escalation prep',
    name: 'Attorney Access Prep',
    price: '$95',
    cadence: '/mo',
    description: 'For serious files that may need attorney-ready organization and LegalShield legal access.',
    cta: 'Choose Attorney Prep',
    to: '/join',
    featured: false,
    features: [
      'Everything in Vivo Plus',
      'Attorney-ready file summary',
      'Evidence timeline organization',
      'Escalation checklist',
      'LegalShield attorney access (+$50/mo)',
    ],
  },
];

const addOns = [
  {
    name: 'LegalShield attorney access',
    provider: 'LegalShield (Credit Vivo partner)',
    price: '+$50/mo',
    detail: 'LegalShield personal plans provide attorney access for guidance and review. Available as an add-on with the Attorney Access Prep plan. LegalShield is a separate service with its own membership terms.',
  },
  {
    name: 'Optional credit monitoring',
    provider: 'IDShield or another monitoring provider',
    price: 'From $14.95/mo',
    detail: 'IDShield individual plans publicly list 1-bureau monitoring from $14.95/mo and 3-bureau monitoring from $19.95/mo.',
  },
  {
    name: 'Mail and third-party costs',
    provider: 'Certified mail, report access, identity verification, or legal costs',
    price: 'As used',
    detail: 'These costs are not included unless a written plan says they are included before purchase.',
  },
];

export default function Pricing() {
  return (
    <>
      {/* Hero */}
      <section className="py-16 bg-gradient-to-b from-emerald-50/70 to-white">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-100 text-emerald-700 text-[11px] font-semibold px-3 py-1.5 rounded-full mb-5">
            <span className="w-1.5 h-1.5 bg-rose-500 rounded-full" />
            Pricing
          </div>
          <h1 className="text-3xl sm:text-[38px] font-bold text-navy-900 leading-tight mb-4">
            Start free. Add premium support when needed.
          </h1>
          <p className="text-[15px] text-navy-500 max-w-xl mx-auto">
            Credit Vivo gives you a free Credit Check-In first. Paid plans add AI-guided support, tracking, dispute preparation, and attorney-ready escalation prep when the situation calls for it.
          </p>
        </div>
      </section>

      {/* Plans */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex flex-col gap-3 rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Free entry point</p>
              <h2 className="mt-1 text-base font-bold text-navy-900">AI Credit Boost + Attorney Access</h2>
              <p className="mt-1 text-xs text-navy-500">
                Start with the scanner first. Upgrade only if you want guided support, tracking, or attorney-ready escalation preparation.
              </p>
            </div>
            <Link to="/join" className="btn-primary shrink-0 text-xs py-2.5">
              Start Free
              <ArrowRight size={14} />
            </Link>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {plans.map((plan) => (
              <article
                key={plan.name}
                className={`relative flex flex-col rounded-2xl border p-6 shadow-sm ${
                  plan.featured
                    ? 'border-emerald-300 bg-gradient-to-b from-white to-emerald-50/60 shadow-emerald-900/10 ring-2 ring-emerald-100'
                    : 'border-navy-100 bg-white'
                }`}
              >
                <span
                  className={`mb-4 w-fit rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${
                    plan.featured
                      ? 'bg-emerald-600 text-white'
                      : 'bg-emerald-50 text-emerald-700'
                  }`}
                >
                  {plan.badge}
                </span>
                <h2 className="text-lg font-bold text-navy-900">{plan.name}</h2>
                <p className="mt-2 min-h-[54px] text-xs leading-relaxed text-navy-500">
                  {plan.description}
                </p>
                <div className="my-6 flex items-end gap-1">
                  <span className="text-4xl font-extrabold text-navy-900">{plan.price}</span>
                  {plan.cadence && (
                    <span className="pb-1 text-sm font-semibold text-navy-400">{plan.cadence}</span>
                  )}
                </div>
                <Link
                  to={plan.to}
                  className={`${plan.featured ? 'btn-primary' : 'btn-soft'} mb-6 w-full text-xs py-2.5`}
                >
                  {plan.cta}
                  <ArrowRight size={14} />
                </Link>
                <ul className="mt-auto space-y-2.5">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-xs text-navy-600">
                      <Check size={13} className="mt-0.5 flex-shrink-0 text-emerald-600" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>

          <div className="mt-8 rounded-2xl border border-amber-100 bg-amber-50 p-5">
              <p className="text-xs leading-relaxed text-amber-900">
              <strong>Launch note:</strong> Pricing is positioned below traditional high-touch credit repair services while keeping Credit Vivo premium. Credit Vivo does not guarantee score increases, removals, approvals, or specific outcomes. Customers review and approve next steps before anything is sent or escalated. LegalShield attorney access ($50/mo), IDShield credit monitoring, mail, report access, and third-party costs are separate unless a written plan says otherwise. Credit Vivo is not a law firm and does not provide legal advice or representation.
            </p>
          </div>
        </div>
      </section>

      {/* LegalShield Partner Section */}
      <section className="py-14 bg-gradient-to-br from-navy-950 via-navy-900 to-emerald-950">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-emerald-900/40 border border-emerald-700/30 text-emerald-300 text-[11px] font-semibold px-3 py-1.5 rounded-full mb-5">
                <ShieldCheck size={12} />
                Attorney Network Partner
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
                LegalShield: Attorney Access When You Need It
              </h2>
              <p className="text-sm text-navy-300 leading-relaxed mb-6">
                Credit Vivo prepares your file and organizes everything for review. When a situation calls for legal guidance, LegalShield connects you with attorneys for consultation, document review, and next-step direction — without the cost and complexity of hiring a law firm directly.
              </p>
              <div className="flex items-end gap-1 mb-6">
                <span className="text-4xl font-extrabold text-emerald-400">+$50</span>
                <span className="pb-1 text-sm font-semibold text-navy-400">/mo</span>
                <span className="ml-3 pb-1 text-xs text-navy-400">added to Attorney Access Prep plan</span>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link to="/join" className="btn-mint text-sm py-3 px-6">
                  Choose Attorney Access Prep
                  <ArrowRight size={15} />
                </Link>
                <a href="https://www.legalshield.com" target="_blank" rel="noopener noreferrer" className="btn-outline text-sm py-3 px-6 border-navy-600 text-navy-300 hover:text-white hover:border-emerald-500">
                  Learn about LegalShield
                </a>
              </div>
            </div>

            <div className="space-y-3">
              {[
                { icon: Phone, title: 'Attorney consultation', desc: 'Connect with a LegalShield attorney for guidance on your credit and financial legal questions.' },
                { icon: FileText, title: 'Document review', desc: 'Get letters, contracts, and legal documents reviewed by an attorney when needed.' },
                { icon: Scale, title: 'Legal direction', desc: 'Receive clear next-step guidance from a licensed attorney for more serious situations.' },
              ].map((item) => (
                <div key={item.title} className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/[0.04] p-5">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-800/40 to-teal-800/40 border border-emerald-700/20">
                    <item.icon size={18} className="text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white mb-1">{item.title}</h3>
                    <p className="text-xs text-navy-300 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
              <div className="rounded-xl border border-amber-700/20 bg-amber-950/20 p-4 mt-2">
                <p className="text-[11px] leading-relaxed text-amber-300/90">
                  LegalShield is a separate service with its own membership terms and agreements. Credit Vivo is not a law firm and does not provide legal advice or legal representation. Attorney access through LegalShield is for guidance only and does not create an attorney-client relationship with Credit Vivo.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Add-ons section */}
      <section className="py-12 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-7 text-center">
            <p className="text-[11px] font-semibold uppercase tracking-widest text-sky-600 mb-1">Optional add-ons</p>
            <h2 className="text-2xl font-bold text-navy-900">Legal access and monitoring stay separate.</h2>
            <p className="mt-2 text-sm text-navy-500">
              Customers can choose these only if they want them. They are not required to use Credit Vivo.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {addOns.map((item) => (
              <div key={item.name} className="rounded-xl border border-navy-100/60 bg-navy-50/40 p-5">
                <p className="text-[11px] font-bold uppercase tracking-wider text-sky-700">{item.provider}</p>
                <h3 className="mt-2 text-sm font-bold text-navy-900">{item.name}</h3>
                <p className="mt-3 text-2xl font-extrabold text-navy-900">{item.price}</p>
                <p className="mt-3 text-xs leading-relaxed text-navy-500">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Info cards */}
      <section className="py-12 bg-sky-50/40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { title: 'Start with free clarity', desc: 'The free Credit Check-In gives consumers a simple starting point before they decide whether they want paid support.' },
              { title: 'Add support when ready', desc: 'Paid tiers are designed around more guidance, tracking, document organization, and attorney-ready escalation preparation.' },
              { title: 'Review comes first', desc: 'Draft findings are for review only. Nothing should be sent, mailed, or escalated without approval.' },
            ].map((card) => (
              <div key={card.title} className="bg-white rounded-xl p-5 border border-navy-100/60">
                <h3 className="text-sm font-bold text-navy-900 mb-2">{card.title}</h3>
                <p className="text-xs text-navy-500 leading-relaxed">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-14 bg-navy-900">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <h2 className="text-xl font-bold text-white mb-3">Start with the free Credit Check-In</h2>
          <p className="text-sm text-navy-300 mb-5">No hard pull to start. Review first. Add attorney-ready support when needed.</p>
          <Link to="/join" className="btn-mint text-sm py-3 px-7">
            Start Free <ArrowRight size={15} />
          </Link>
        </div>
      </section>
    </>
  );
}
