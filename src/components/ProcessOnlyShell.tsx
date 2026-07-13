import { Link, Outlet, useLocation } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, ShieldCheck } from 'lucide-react';
import { PROCESS_ONLY_FLAGS } from '../lib/processOnlyMode';

const memberLinks = [
  ['/member/dashboard', 'Dashboard'],
  ['/member/upload', 'Upload'],
  ['/member/findings', 'Findings'],
  ['/member/negative-accounts', 'Negative accounts'],
  ['/member/bureau-comparison', '3-bureau'],
  ['/member/score-blockers', 'Score blockers'],
  ['/member/comeback-plan', 'Comeback'],
  ['/member/disputes', 'Draft letters'],
  ['/member/progress', 'Progress'],
  ['/member/messages', 'Messages'],
];

const founderLinks = [
  ['/founder/dashboard', 'Dashboard'],
  ['/founder/customers', 'Customers'],
  ['/founder/report-intake', 'Reports'],
  ['/founder/scanner-review', 'Scanner'],
  ['/founder/bureau-comparison', '3-bureau'],
  ['/founder/negative-tradelines', 'Tradelines'],
  ['/founder/letter-review', 'Letters'],
  ['/founder/approval-logs', 'Approvals'],
  ['/founder/compliance-blocker', 'Compliance'],
  ['/founder/evidence-checklist', 'Evidence'],
  ['/founder/document-vault-preview', 'Vault'],
  ['/founder/signed-url-status', 'Signed URLs'],
  ['/founder/attorney-packet-preview', 'Attorney'],
  ['/founder/crm-preview', 'CRM'],
  ['/founder/audit-logs', 'Audit'],
  ['/founder/ai-learning-events', 'AI learning'],
  ['/founder/deep-learning-preview', 'Model'],
  ['/founder/launch-gates', 'Launch gates'],
  ['/founder/uat-1-35-report', 'UAT 1-35'],
];

function ProcessOnlyBanner() {
  return (
    <div className="mb-5 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-950">
      <div className="flex items-start gap-3">
        <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" />
        <div>
          <p className="font-extrabold">Credit Vivo TEST VERSION - process-only</p>
          <p className="mt-1 text-emerald-900">
            Simulation only. Draft only. Not sent. Production blocked. No files are saved, exported, routed, charged, or shared.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(PROCESS_ONLY_FLAGS).map(([key, value]) => (
              <span key={key} className="rounded-full bg-white px-2.5 py-1 text-[11px] font-bold text-emerald-800 ring-1 ring-emerald-200">
                {key}={String(value)}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function TestShell({ type }: { type: 'member' | 'founder' }) {
  const location = useLocation();
  const links = type === 'member' ? memberLinks : founderLinks;
  const title = type === 'member' ? 'Member test flow' : 'Founder command test';

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 overflow-y-auto border-r border-slate-200 bg-white p-4 lg:block">
        <Link to="/" className="mb-6 flex items-center gap-2">
          <img src="/logo.webp" alt="Credit Vivo" className="h-7 w-7" />
          <span className="text-sm font-black text-navy-900">Credit <span className="text-emerald-600">Vivo</span></span>
        </Link>
        <p className="mb-3 text-xs font-black uppercase tracking-wide text-slate-500">{title}</p>
        <nav className="space-y-1">
          {links.map(([to, label]) => (
            <Link
              key={to}
              to={to}
              className={`block rounded-md px-3 py-2 text-xs font-bold ${location.pathname === to ? 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-100' : 'text-slate-600 hover:bg-slate-50'}`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <Link to="/" className="mt-6 flex items-center gap-2 px-3 py-2 text-xs font-bold text-slate-500 hover:text-slate-900">
          <ArrowLeft size={14} /> Back to live-style site
        </Link>
      </aside>
      <main className="lg:pl-64">
        <div className="mx-auto max-w-6xl p-4 md:p-8">
          <ProcessOnlyBanner />
          <div className="mb-5 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs font-semibold text-amber-900">
            <div className="flex gap-2"><AlertTriangle size={16} /> This test version is not commercial launch approval and is not legal advice.</div>
          </div>
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export function MemberShell() {
  return <TestShell type="member" />;
}

export function FounderShell() {
  return <TestShell type="founder" />;
}
