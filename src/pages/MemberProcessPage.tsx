import { Link, Navigate, useLocation } from 'react-router-dom';
import { AlertCircle, CheckCircle2, FileText, Lock, MessageSquare } from 'lucide-react';
import { dummyCreditReports, getDummyReport, type DummyTradeline } from '../lib/dummyCreditReports';
import { buildLetterWorkflowSummary, buildScannerLetterQueue } from '../lib/scannerLetterEngine';
import { syntheticWorkflow } from '../lib/processOnlyTestData';
import { getProcessOnlyBlock } from '../lib/processOnlyMode';

const memberContent: Record<string, { title: string; eyebrow: string; body: string; labels: string[] }> = {
  signup: { title: 'Create your Credit Vivo test account', eyebrow: 'Step 2', body: 'This looks like signup, but no production account is created. Tim can review the customer experience safely.', labels: ['Simulation only', 'No production account', 'No payment'] },
  login: { title: 'Member login simulation', eyebrow: 'Step 3', body: 'This screen simulates access to the portal. Real auth is a future production gate.', labels: ['Simulation only', 'Production auth blocked'] },
  dashboard: { title: 'Your Credit Vivo roadmap', eyebrow: 'Step 4', body: 'The customer sees what happened, what is waiting, and what Credit Vivo reviews next.', labels: ['Simulation only', 'Synthetic data'] },
  upload: { title: 'Upload ID and credit report', eyebrow: 'Step 5', body: 'The customer sees upload choices, but real ID/report storage is blocked in this test version.', labels: ['Real upload blocked', 'Secure vault required', 'No files saved'] },
  findings: { title: 'Scanner output and AI findings', eyebrow: 'Steps 6-7', body: 'Synthetic scanner output is shown as plain-English possible report errors.', labels: ['Synthetic scanner output', 'Draft review data', 'Results vary'] },
  'negative-accounts': { title: 'Negative account review', eyebrow: 'Step 8', body: 'Masked synthetic negative accounts show what a customer would understand first.', labels: ['Masked data only', 'Admin review required'] },
  'bureau-comparison': { title: '3-bureau comparison', eyebrow: 'Step 9', body: 'Customer sees Experian, Equifax, and TransUnion differences without raw backend details.', labels: ['3-bureau preview', 'Synthetic data only'] },
  'score-blockers': { title: 'Score blockers', eyebrow: 'Step 10', body: 'Educational score blockers show what may be holding a score back without guarantees.', labels: ['No score guarantee', 'Education only'] },
  'comeback-plan': { title: 'Credit Comeback path', eyebrow: 'Step 11', body: 'Customer sees a motivating, non-guaranteed improvement path tied to review items.', labels: ['Estimated only', 'Results not guaranteed'] },
  disputes: { title: 'Draft dispute letters and approvals', eyebrow: 'Steps 12-15', body: 'Draft letter text is visible, customer approval is simulated, and compliance blocks all sending.', labels: ['Draft only', 'Not sent', 'Customer approval simulation', 'Compliance blocked'] },
  progress: { title: 'Progress tracker', eyebrow: 'Step 16', body: 'Customer sees draft, approval, admin review, compliance review, and not-sent status.', labels: ['Production blocked', 'Not sent'] },
  messages: { title: 'Messages and questions', eyebrow: 'Step 17', body: 'Customer sees support/message previews, but no SMS or email leaves Credit Vivo.', labels: ['Preview only', 'No SMS', 'No email'] },
};

function StatusPill({ children }: { children: string }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-700 ring-1 ring-slate-200">{children}</span>;
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"><h2 className="mb-3 text-base font-black text-slate-950">{title}</h2>{children}</section>;
}

function ReportSelector({ selectedId }: { selectedId: string }) {
  return (
    <Card title="10 dummy customer reports">
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-5">
        {dummyCreditReports.map((report, index) => (
          <Link
            key={report.id}
            className={`rounded-lg border p-3 text-xs font-black ${report.id === selectedId ? 'border-emerald-500 bg-emerald-50 text-emerald-900' : 'border-slate-200 bg-slate-50 text-slate-700'}`}
            to={`?case=${report.id}`}
          >
            {index + 1}. {report.persona}
          </Link>
        ))}
      </div>
    </Card>
  );
}

function ScoreSummary({ report }: { report: ReturnType<typeof getDummyReport> }) {
  return (
    <Card title="Score and case summary">
      <div className="grid gap-3 md:grid-cols-4">
        <div className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-200"><p className="text-xs font-black text-slate-500">Start</p><p className="text-3xl font-black text-slate-950">{report.score_start}</p></div>
        <div className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-200"><p className="text-xs font-black text-slate-500">Current</p><p className="text-3xl font-black text-emerald-700">{report.score_current}</p></div>
        <div className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-200"><p className="text-xs font-black text-slate-500">Goal</p><p className="text-3xl font-black text-slate-950">{report.score_goal}</p></div>
        <div className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-200"><p className="text-xs font-black text-slate-500">Stage</p><p className="mt-2 text-sm font-black text-slate-900">{report.stage}</p></div>
      </div>
      <div className="mt-4 grid gap-2 md:grid-cols-3">
        {Object.entries(report.bureau_scores).map(([bureau, score]) => (
          <div key={bureau} className="rounded-lg bg-white p-3 text-sm ring-1 ring-slate-200"><strong>{bureau}</strong>: {score}</div>
        ))}
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-700">{report.profile_summary}</p>
      <p className="mt-2 rounded-md bg-amber-50 p-3 text-sm font-bold text-amber-900">{report.top_risk}</p>
    </Card>
  );
}

function TradelineCards({ tradelines }: { tradelines: DummyTradeline[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {tradelines.map((item) => (
        <article key={item.id} className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-xs font-black uppercase tracking-wide text-emerald-700">{item.bureau} | {item.severity}</p>
          <h3 className="mt-2 text-sm font-black text-slate-950">{item.account_name}</h3>
          <p className="mt-1 text-xs text-slate-500">{item.account_type} | {item.account_number_masked}</p>
          <p className="mt-3 text-sm text-slate-700">{item.possible_issue}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusPill>{item.status}</StatusPill>
            <StatusPill>{item.recommended_letter_type}</StatusPill>
          </div>
        </article>
      ))}
    </div>
  );
}

export default function MemberProcessPage({ view }: { view: string }) {
  const location = useLocation();
  const currentView = view || location.pathname.split('/').filter(Boolean)[1] || 'dashboard';
  const config = memberContent[currentView];
  if (!config) return <Navigate to="/member/dashboard" replace />;
  const uploadBlock = getProcessOnlyBlock('real_upload');
  const selectedReport = getDummyReport(new URLSearchParams(location.search).get('case'));
  const letterQueue = buildScannerLetterQueue(selectedReport);
  const letterWorkflow = buildLetterWorkflowSummary(selectedReport);

  return (
    <div className="space-y-5">
      <header className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-xs font-black uppercase tracking-wide text-emerald-700">{config.eyebrow}</p>
        <h1 className="mt-2 text-2xl font-black text-slate-950 md:text-3xl">{config.title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">{config.body}</p>
        <div className="mt-4 flex flex-wrap gap-2">{config.labels.map((label) => <StatusPill key={label}>{label}</StatusPill>)}</div>
      </header>

      <ReportSelector selectedId={selectedReport.id} />

      {['signup', 'login', 'dashboard'].includes(currentView) && (
        <Card title="Synthetic member profile">
          <div className="grid gap-3 text-sm md:grid-cols-3">
            <p><strong>Name:</strong> {selectedReport.display_name}</p>
            <p><strong>Email:</strong> {selectedReport.login_email}</p>
            <p><strong>Status:</strong> {selectedReport.report_status}</p>
            <p className="md:col-span-3"><strong>Profile:</strong> {selectedReport.persona}</p>
          </div>
        </Card>
      )}

      <ScoreSummary report={selectedReport} />

      {currentView === 'upload' && (
        <Card title="Upload controls are visual only">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5"><FileText className="mb-3 text-slate-500" /><strong>Upload ID</strong><p className="mt-2 text-sm text-slate-600">Blocked in test mode. Secure vault write is required before production.</p></div>
            <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5"><FileText className="mb-3 text-slate-500" /><strong>Upload 3-bureau report</strong><p className="mt-2 text-sm text-slate-600">Blocked in test mode. Scanner preview uses synthetic fixture data only.</p></div>
          </div>
          <p className="mt-4 rounded-md bg-rose-50 p-3 text-sm font-bold text-rose-800">{uploadBlock.status}: {uploadBlock.reason}</p>
        </Card>
      )}

      {['findings', 'negative-accounts', 'bureau-comparison', 'score-blockers', 'comeback-plan'].includes(currentView) && <TradelineCards tradelines={selectedReport.tradelines} />}

      {currentView === 'disputes' && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card title="Generated scanner letter queue">
            <div className="grid gap-3">
              {letterQueue.map((letter) => (
                <article key={letter.queue_id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-xs font-black uppercase text-emerald-700">{letter.letter_type} | {letter.tracking_status}</p>
                  <h3 className="mt-1 text-sm font-black text-slate-950">{letter.letter_subject}</h3>
                  <p className="mt-2 text-xs text-slate-600">{letter.account_name} {letter.account_number_masked} | {letter.bureau}</p>
                  <p className="mt-2 text-xs font-bold text-rose-700">Send: {String(letter.send_allowed)} | Auto-send: {String(letter.auto_send_allowed)} | Mail: {String(letter.mailing_allowed)}</p>
                </article>
              ))}
            </div>
          </Card>
          <Card title="Approval and compliance state">
            <ul className="space-y-2 text-sm text-slate-700">
              <li><CheckCircle2 className="mr-2 inline h-4 w-4 text-emerald-600" /> Customer approval: {syntheticWorkflow.customer_approval_status}</li>
              <li><Lock className="mr-2 inline h-4 w-4 text-amber-600" /> Admin review: {syntheticWorkflow.admin_review_status}</li>
              <li><AlertCircle className="mr-2 inline h-4 w-4 text-rose-600" /> Compliance: {syntheticWorkflow.compliance_status}</li>
              <li><Lock className="mr-2 inline h-4 w-4 text-rose-600" /> Send status: {syntheticWorkflow.send_status}</li>
              <li><Lock className="mr-2 inline h-4 w-4 text-rose-600" /> Engine auto-send: {String(letterWorkflow.auto_send_allowed)}</li>
            </ul>
          </Card>
          <Card title="Dispute test coverage">
            <ul className="space-y-2 text-sm text-slate-700">{selectedReport.dispute_tests.map((test) => <li key={test}><CheckCircle2 className="mr-2 inline h-4 w-4 text-emerald-600" />{test}</li>)}</ul>
          </Card>
          <Card title="Draft body and evidence">
            <div className="space-y-4">
              {letterQueue.map((letter) => (
                <article key={`${letter.queue_id}-body`} className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs font-black text-slate-600">{letter.letter_subject}</p>
                  <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-700">{letter.draft_letter_body}</p>
                  <p className="mt-3 text-xs font-black text-slate-600">Evidence needed: {letter.evidence_needed.join('; ')}</p>
                </article>
              ))}
            </div>
          </Card>
        </div>
      )}

      {currentView === 'progress' && (
        <Card title="Process-only progress tracker">
          <div className="grid gap-3 md:grid-cols-5">{selectedReport.tracking_stages.map((stage) => <div key={stage} className="rounded-lg bg-slate-50 p-3 text-xs font-black text-slate-700 ring-1 ring-slate-200">{stage}</div>)}</div>
        </Card>
      )}

      {currentView === 'messages' && (
        <Card title="Message preview">
          <p className="flex items-center gap-2 text-sm text-slate-700"><MessageSquare size={16} /> {selectedReport.email_preview}</p>
        </Card>
      )}

      <div className="flex flex-wrap gap-2">
        <Link className="btn-primary" to="/founder/uat-1-35-report">View 1-35 UAT report</Link>
        <Link className="btn-soft" to="/founder/dashboard">Founder view</Link>
      </div>
    </div>
  );
}
