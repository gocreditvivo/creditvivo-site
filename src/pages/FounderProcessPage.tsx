import { Link, Navigate, useLocation } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Lock } from 'lucide-react';
import { syntheticCustomer, syntheticTradelines, syntheticWorkflow, uatSteps } from '../lib/processOnlyTestData';
import { PROCESS_ONLY_FLAGS } from '../lib/processOnlyMode';

const founderContent: Record<string, { title: string; body: string; labels: string[] }> = {
  dashboard: { title: 'Founder dashboard', body: 'A+ test command center for the process-only simulator.', labels: ['Production blocked', 'Founder review'] },
  customers: { title: 'Customers', body: 'Synthetic customer list only. No production customer database is used.', labels: ['Synthetic data only'] },
  'report-intake': { title: 'Uploaded reports simulation', body: 'Synthetic report intake status. Real report storage is blocked.', labels: ['No real upload', 'Secure vault required'] },
  'scanner-review': { title: 'Scanner review', body: 'Founder sees extraction confidence and review needs from synthetic data.', labels: ['Scanner fixture only', 'Admin review required'] },
  'bureau-comparison': { title: '3-bureau comparison admin view', body: 'Technical comparison preview across bureaus.', labels: ['Synthetic 3-bureau data'] },
  'negative-tradelines': { title: 'Negative tradeline review', body: 'Collections, charge-offs, lates, mismatches, and duplicates are reviewed from synthetic data.', labels: ['Masked accounts only'] },
  'letter-review': { title: 'Draft letter review', body: 'Draft letters are visible but not sent, exported, or queued externally.', labels: ['Draft only', 'Not sent'] },
  'approval-logs': { title: 'Approval logs preview', body: 'Simulated customer/admin approval log states.', labels: ['Simulation only'] },
  'compliance-blocker': { title: 'Compliance blocker', body: 'Blocks risky actions until approvals, evidence, audit log, safe wording, and compliance review pass.', labels: ['Compliance blocked'] },
  'evidence-checklist': { title: 'Evidence checklist', body: 'Preview of evidence needed before any future dispute prep.', labels: ['Preview only'] },
  'document-vault-preview': { title: 'Document vault preview', body: 'Shows vault requirements without storing documents.', labels: ['Secure vault required', 'No storage'] },
  'signed-url-status': { title: 'Signed URL status', body: 'Signed URLs are blocked until staging Supabase vault verification.', labels: ['Blocked until verified'] },
  'attorney-packet-preview': { title: 'Attorney packet draft', body: 'Attorney packet is draft-only and not shared.', labels: ['Draft only', 'No attorney sharing'] },
  'crm-preview': { title: 'CRM/customer update preview', body: 'Customer updates are portal previews only. No SMS/email is sent.', labels: ['No SMS', 'No email'] },
  'audit-logs': { title: 'Audit log preview', body: 'Audit events are simulated and view-only.', labels: ['No export'] },
  'ai-learning-events': { title: 'AI learning events preview', body: 'AI corrections are simulated and require human review.', labels: ['Human review required'] },
  'deep-learning-preview': { title: 'Deep-learning foundation preview', body: 'Model training and self-modification are blocked.', labels: ['No model training'] },
  'launch-gates': { title: 'Launch gates', body: 'Commercial launch remains blocked until all production gates pass.', labels: ['Commercial launch blocked'] },
  'uat-1-35-report': { title: '1-35 process-only UAT report', body: 'PASS / FAIL / PARTIAL / BLOCKED scorecard for the full test flow.', labels: ['A+ test grade', 'No production actions'] },
};

function Pill({ children }: { children: string }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-700 ring-1 ring-slate-200">{children}</span>;
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"><h2 className="mb-3 text-base font-black text-slate-950">{title}</h2>{children}</section>;
}

function UatScorecard() {
  const counts = uatSteps.reduce<Record<string, number>>((acc, step) => {
    acc[step.status] = (acc[step.status] || 0) + 1;
    return acc;
  }, {});
  return (
    <div className="space-y-5">
      <div className="grid gap-3 md:grid-cols-4">
        {(['PASS', 'PARTIAL', 'FAIL', 'BLOCKED'] as const).map((status) => (
          <div key={status} className="rounded-lg border border-slate-200 bg-white p-4">
            <p className="text-xs font-black text-slate-500">{status}</p>
            <p className="mt-2 text-3xl font-black text-slate-950">{counts[status] || 0}</p>
          </div>
        ))}
      </div>
      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
          <thead className="bg-slate-50 text-slate-600"><tr>{['#', 'Feature', 'Route', 'Expected', 'Actual', 'Status', 'Risk', 'Fix needed'].map((h) => <th key={h} className="px-3 py-3 font-black">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {uatSteps.map((step) => (
              <tr key={step.step}>
                <td className="px-3 py-3 font-bold">{step.step}</td>
                <td className="px-3 py-3 font-bold text-slate-900">{step.feature}</td>
                <td className="px-3 py-3"><Link className="font-bold text-emerald-700" to={step.route}>{step.route}</Link></td>
                <td className="px-3 py-3 text-slate-600">{step.expected}</td>
                <td className="px-3 py-3 text-slate-600">{step.actual}</td>
                <td className="px-3 py-3"><Pill>{step.status}</Pill></td>
                <td className="px-3 py-3">{step.risk}</td>
                <td className="px-3 py-3 text-slate-600">{step.fixNeeded}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function FounderProcessPage({ view }: { view: string }) {
  const location = useLocation();
  const currentView = view || location.pathname.split('/').filter(Boolean)[1] || 'dashboard';
  const config = founderContent[currentView];
  if (!config) return <Navigate to="/founder/dashboard" replace />;

  return (
    <div className="space-y-5">
      <header className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-xs font-black uppercase tracking-wide text-emerald-700">Founder/admin test</p>
        <h1 className="mt-2 text-2xl font-black text-slate-950 md:text-3xl">{config.title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">{config.body}</p>
        <div className="mt-4 flex flex-wrap gap-2">{config.labels.map((label) => <Pill key={label}>{label}</Pill>)}</div>
      </header>

      {currentView === 'uat-1-35-report' ? <UatScorecard /> : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Panel title="Safety state">
            <ul className="space-y-2 text-sm text-slate-700">
              {Object.entries(PROCESS_ONLY_FLAGS).map(([key, value]) => <li key={key}><CheckCircle2 className="mr-2 inline h-4 w-4 text-emerald-600" />{key}: <strong>{String(value)}</strong></li>)}
            </ul>
          </Panel>
          <Panel title="Synthetic case">
            <p className="text-sm text-slate-700"><strong>{syntheticCustomer.display_name}</strong> - {syntheticCustomer.goal}</p>
            <p className="mt-2 text-sm text-slate-700">Workflow: {Object.values(syntheticWorkflow).join(' | ')}</p>
          </Panel>
          <Panel title="Review items">
            <div className="space-y-3">{syntheticTradelines.map((item) => <div key={item.account_number_masked} className="rounded-md bg-slate-50 p-3 text-sm text-slate-700"><strong>{item.bureau}</strong> - {item.account_name} {item.account_number_masked}<br />{item.possible_issue}</div>)}</div>
          </Panel>
          <Panel title="Blocked production actions">
            <ul className="space-y-2 text-sm text-slate-700">
              {['real uploads', 'exports/downloads', 'dispute sends', 'letter mailing', 'SMS/email', 'attorney sharing', 'payments', 'commercial launch'].map((item) => <li key={item}><Lock className="mr-2 inline h-4 w-4 text-rose-600" />{item}</li>)}
            </ul>
          </Panel>
        </div>
      )}

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm font-semibold text-amber-900">
        <AlertTriangle className="mr-2 inline h-4 w-4" /> Test version only. Attorney/compliance review is required before commercial launch.
      </div>

      <div className="flex flex-wrap gap-2">
        <Link className="btn-primary" to="/founder/uat-1-35-report">Open 1-35 UAT report</Link>
        <Link className="btn-soft" to="/member/dashboard">Member view</Link>
      </div>
    </div>
  );
}


