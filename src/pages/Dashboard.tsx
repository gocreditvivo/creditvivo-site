import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import CreditComebackSimulator from '../components/CreditComebackSimulator';
import { getLastScanResult } from '../lib/scanStorage';

export default function Dashboard() {
  const result = getLastScanResult();

  const stepsCount = result ? 4 : 3;
  const reviewCount = result?.review_items_count ?? 2;
  const issueCount = result?.issues_count ?? result?.issues_preview?.length ?? 1;

  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-widest text-sky-600 mb-1">
        Member Dashboard
      </p>
      <h1 className="text-xl font-bold text-navy-900 mb-1">
        Your credit comeback starts here.
      </h1>
      <p className="text-sm text-navy-400 mb-6">
        Find errors. Build disputes. See results.
      </p>

      <div className="mb-8">
        <CreditComebackSimulator result={result} compact />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {[
          { val: String(stepsCount), label: 'steps this month' },
          { val: String(reviewCount), label: 'credit blockers' },
          { val: String(issueCount), label: 'review points' },
          { val: '100', label: 'point path' },
        ].map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-xl p-4 border border-navy-100/60 text-center"
          >
            <p className="text-2xl font-bold text-navy-900">{s.val}</p>
            <p className="text-[11px] text-navy-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl p-5 border border-navy-100/60 mb-5">
        <h2 className="text-sm font-bold text-navy-900 mb-4">This Month's Plan</h2>
        <div className="space-y-3">
          {[
            {
              num: 1,
              title: result ? 'Review your credit blockers' : 'Start your AI Credit Boost scan',
              desc: result
                ? 'Your scanner-powered simulator is ready in your dashboard.'
                : 'Upload or connect your report so Credit Vivo can find what may be holding your score back.',
              to: result ? '/findings' : '/scan',
            },
            {
              num: 2,
              title: 'Build smart disputes',
              desc: 'Focus first on the items with the strongest possible score impact.',
              to: '/findings',
            },
            {
              num: 3,
              title: 'See results and next steps',
              desc: 'Watch findings, dispute progress, and score movement in one place.',
              to: '/findings',
            },
          ].map((step) => (
            <Link
              key={step.num}
              to={step.to}
              className="flex items-start gap-3 py-3 px-4 bg-navy-50/50 rounded-lg hover:bg-sky-50/50 transition-colors"
            >
              <div className="w-7 h-7 bg-navy-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-bold text-white">{step.num}</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-navy-800">{step.title}</p>
                <p className="text-xs text-navy-400 mt-0.5">{step.desc}</p>
              </div>
              <ArrowRight size={13} className="text-navy-300 mt-1" />
            </Link>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl p-5 border border-navy-100/60">
        <h2 className="text-sm font-bold text-navy-900 mb-2">Updates</h2>
        <p className="text-xs text-navy-400">
          {result
            ? 'Your latest Credit Vivo scan is ready. Review your simulator, top credit blockers, and dispute-ready findings.'
            : 'Your next update will show score movement, credit blockers, dispute progress, and what to focus on next.'}
        </p>
      </div>
    </div>
  );
}
