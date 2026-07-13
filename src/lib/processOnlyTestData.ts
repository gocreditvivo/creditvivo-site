export type UatStatus = 'PASS' | 'FAIL' | 'PARTIAL' | 'BLOCKED';
export type UatRisk = 'Low' | 'Medium' | 'High';
export type UatArea = 'customer' | 'founder';

export type UatStep = {
  step: number;
  area: UatArea;
  feature: string;
  route: string;
  expected: string;
  actual: string;
  status: UatStatus;
  risk: UatRisk;
  fixNeeded: string;
};

export const syntheticCustomer = {
  customer_id: 'synthetic-cv-001',
  display_name: 'Jordan Rivera',
  test_email: 'member-test@creditvivo.test',
  goal: 'Prepare for a stronger credit profile before an auto-loan application.',
  member_status: 'simulation_active',
  identity_status: 'simulation_only',
  report_status: 'synthetic_fixture_only',
};

export const syntheticTradelines = [
  {
    report_id: 'synthetic-report-001',
    bureau: 'Experian',
    account_name: 'Midland Credit Management',
    account_number_masked: '****1234',
    account_type: 'Collection',
    status: 'Collection account reported',
    balance_range_or_masked_balance: '$1,200-$1,300',
    date_fields_synthetic: 'Synthetic 2024 review window',
    confidence_score: 0.86,
    possible_issue: 'Original creditor and ownership details need review.',
    risk_label: 'Admin review required',
  },
  {
    report_id: 'synthetic-report-001',
    bureau: 'Equifax',
    account_name: 'Capital One',
    account_number_masked: '****8899',
    account_type: 'Credit Card',
    status: 'Charge-off transferred or sold',
    balance_range_or_masked_balance: '$0 reported after transfer',
    date_fields_synthetic: 'Synthetic 2020 delinquency window',
    confidence_score: 0.82,
    possible_issue: 'Balance, transfer status, and date consistency need review.',
    risk_label: 'Compliance blocked until evidence reviewed',
  },
  {
    report_id: 'synthetic-report-001',
    bureau: 'TransUnion',
    account_name: 'Regional Bank Card',
    account_number_masked: '****4421',
    account_type: 'Revolving',
    status: 'Late payment history reported',
    balance_range_or_masked_balance: '$400-$600',
    date_fields_synthetic: 'Synthetic recent-payment review window',
    confidence_score: 0.79,
    possible_issue: 'Payment-history notation differs from other bureau data.',
    risk_label: 'Customer confirmation required',
  },
];

export const syntheticWorkflow = {
  draft_letter_status: 'draft_only',
  customer_approval_status: 'simulation_only',
  admin_review_status: 'required',
  compliance_status: 'blocked_or_required',
  send_status: 'not_sent',
  payment_status: 'disabled',
  launch_status: 'blocked',
};

export const uatSteps: UatStep[] = [
  { step: 1, area: 'customer', feature: 'Website entry', route: '/', expected: 'Homepage loads with Credit Vivo message.', actual: 'Public site route remains separate from test simulator.', status: 'PASS', risk: 'Low', fixNeeded: 'None for test mode.' },
  { step: 2, area: 'customer', feature: 'Signup', route: '/member/signup', expected: 'Customer sees test signup screen.', actual: 'Synthetic signup screen shows test-only access.', status: 'PASS', risk: 'Medium', fixNeeded: 'Replace with production auth later.' },
  { step: 3, area: 'customer', feature: 'Login', route: '/member/login', expected: 'Customer logs in with simulation access.', actual: 'Login is simulated and creates no production account.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect real auth later.' },
  { step: 4, area: 'customer', feature: 'Member dashboard', route: '/member/dashboard', expected: 'Customer sees roadmap.', actual: 'Member dashboard shows synthetic status and next steps.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect real customer data later.' },
  { step: 5, area: 'customer', feature: 'Upload/report intake warning', route: '/member/upload', expected: 'Real uploads blocked and warning shown.', actual: 'Upload UI is visual only; real report/ID storage is blocked.', status: 'PASS', risk: 'High', fixNeeded: 'Verify secure vault before real upload.' },
  { step: 6, area: 'customer', feature: 'Scanner output', route: '/member/findings', expected: 'Sample scanner output displayed.', actual: 'Synthetic scanner summary is displayed only.', status: 'PASS', risk: 'Medium', fixNeeded: 'Run gold-standard scanner validation later.' },
  { step: 7, area: 'customer', feature: 'AI findings', route: '/member/findings', expected: 'Plain-English finding cards displayed.', actual: 'AI finding previews use synthetic tradelines.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect real scanner output after vault/auth/RLS.' },
  { step: 8, area: 'customer', feature: 'Negative accounts', route: '/member/negative-accounts', expected: 'Masked negative accounts displayed.', actual: 'Synthetic negative accounts show masked account numbers.', status: 'PASS', risk: 'Medium', fixNeeded: 'None for test mode.' },
  { step: 9, area: 'customer', feature: '3-bureau comparison', route: '/member/bureau-comparison', expected: 'Three-bureau comparison visible.', actual: 'Synthetic bureau comparison is visible.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect parsed bureau groups later.' },
  { step: 10, area: 'customer', feature: 'Score blockers', route: '/member/score-blockers', expected: 'Score blockers displayed without guarantees.', actual: 'Score blockers are educational and non-guaranteed.', status: 'PASS', risk: 'Medium', fixNeeded: 'Keep no-guarantee copy.' },
  { step: 11, area: 'customer', feature: 'Credit Comeback view', route: '/member/comeback-plan', expected: 'Comeback view with no guarantees.', actual: 'Comeback plan uses estimated ranges and safe wording.', status: 'PASS', risk: 'Medium', fixNeeded: 'Validate scoring language before launch.' },
  { step: 12, area: 'customer', feature: 'Draft dispute letters', route: '/member/disputes', expected: 'Draft-only letters visible.', actual: 'Draft letter preview is not sent and not exportable.', status: 'PASS', risk: 'High', fixNeeded: 'Add real approval workflow later.' },
  { step: 13, area: 'customer', feature: 'Customer approval simulation', route: '/member/disputes', expected: 'Simulation-only approval visible.', actual: 'Approval shown as simulation only, not legally active.', status: 'PASS', risk: 'High', fixNeeded: 'Connect legally reviewed approvals later.' },
  { step: 14, area: 'customer', feature: 'Admin review required', route: '/member/disputes', expected: 'Admin review required status visible.', actual: 'Customer sees admin review required without admin tools.', status: 'PASS', risk: 'High', fixNeeded: 'None for test mode.' },
  { step: 15, area: 'customer', feature: 'Compliance blocker status', route: '/member/disputes', expected: 'Compliance blocked status visible.', actual: 'Compliance blocked label appears before any action.', status: 'PASS', risk: 'High', fixNeeded: 'Attorney review before launch.' },
  { step: 16, area: 'customer', feature: 'Progress tracker', route: '/member/progress', expected: 'Draft/review/not-sent progress visible.', actual: 'Progress tracker shows blocked production stages.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect real events later.' },
  { step: 17, area: 'customer', feature: 'Messages/questions placeholder', route: '/member/messages', expected: 'Preview only, no live SMS/email.', actual: 'Messages preview is internal only and not sent.', status: 'PASS', risk: 'High', fixNeeded: 'Vendor/consent setup later.' },
  { step: 18, area: 'founder', feature: 'Founder dashboard', route: '/founder/dashboard', expected: 'Founder control center.', actual: 'Founder dashboard summarizes test gates.', status: 'PASS', risk: 'High', fixNeeded: 'Protect with real admin auth later.' },
  { step: 19, area: 'founder', feature: 'Customers', route: '/founder/customers', expected: 'Simulated customer list.', actual: 'Synthetic customers only.', status: 'PASS', risk: 'High', fixNeeded: 'Connect Supabase later.' },
  { step: 20, area: 'founder', feature: 'Uploaded reports simulation', route: '/founder/report-intake', expected: 'Synthetic records only.', actual: 'Report intake preview rejects real storage.', status: 'PASS', risk: 'High', fixNeeded: 'Verify secure vault later.' },
  { step: 21, area: 'founder', feature: 'Scanner review', route: '/founder/scanner-review', expected: 'Confidence and extraction review.', actual: 'Synthetic confidence/extraction review shown.', status: 'PASS', risk: 'High', fixNeeded: 'Gold-standard validation later.' },
  { step: 22, area: 'founder', feature: '3-bureau comparison admin view', route: '/founder/bureau-comparison', expected: 'Technical bureau comparison.', actual: 'Synthetic admin bureau comparison displayed.', status: 'PASS', risk: 'High', fixNeeded: 'Connect scanner comparison later.' },
  { step: 23, area: 'founder', feature: 'Negative tradeline review', route: '/founder/negative-tradelines', expected: 'Tradeline review.', actual: 'Negative tradeline review uses masked fixture data.', status: 'PASS', risk: 'High', fixNeeded: 'Connect reviewer corrections later.' },
  { step: 24, area: 'founder', feature: 'Draft letter review', route: '/founder/letter-review', expected: 'Draft-only, not sent.', actual: 'Letter review is draft-only and blocked from send.', status: 'PASS', risk: 'High', fixNeeded: 'Wire internal queue later.' },
  { step: 25, area: 'founder', feature: 'Approval logs preview', route: '/founder/approval-logs', expected: 'Simulated approval logs.', actual: 'Approval logs are preview-only.', status: 'PASS', risk: 'High', fixNeeded: 'Connect Supabase logs later.' },
  { step: 26, area: 'founder', feature: 'Compliance blocker', route: '/founder/compliance-blocker', expected: 'Blocker reasons visible.', actual: 'Blocker reasons visible and production actions disabled.', status: 'PASS', risk: 'High', fixNeeded: 'Attorney review before launch.' },
  { step: 27, area: 'founder', feature: 'Evidence checklist', route: '/founder/evidence-checklist', expected: 'Preview only, no upload.', actual: 'Evidence checklist is synthetic only.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect vault later.' },
  { step: 28, area: 'founder', feature: 'Document vault preview', route: '/founder/document-vault-preview', expected: 'Secure vault required, no real storage.', actual: 'Vault preview says secure vault required and stores nothing.', status: 'PASS', risk: 'High', fixNeeded: 'Verify signed URLs later.' },
  { step: 29, area: 'founder', feature: 'Signed URL status', route: '/founder/signed-url-status', expected: 'Blocked until verified.', actual: 'Signed URL status is blocked pending Supabase verification.', status: 'PASS', risk: 'High', fixNeeded: 'Verify staging Supabase later.' },
  { step: 30, area: 'founder', feature: 'Attorney packet draft', route: '/founder/attorney-packet-preview', expected: 'Draft only, no sharing.', actual: 'Attorney packet preview is draft-only and not shared.', status: 'PASS', risk: 'High', fixNeeded: 'Counsel workflow later.' },
  { step: 31, area: 'founder', feature: 'CRM/customer update preview', route: '/founder/crm-preview', expected: 'No SMS/email sent.', actual: 'CRM updates are preview-only and not sent.', status: 'PASS', risk: 'High', fixNeeded: 'Consent/vendor setup later.' },
  { step: 32, area: 'founder', feature: 'Audit log preview', route: '/founder/audit-logs', expected: 'Simulated audit events.', actual: 'Audit logs are view-only with no export.', status: 'PASS', risk: 'Medium', fixNeeded: 'Connect immutable logs later.' },
  { step: 33, area: 'founder', feature: 'AI learning events preview', route: '/founder/ai-learning-events', expected: 'Simulated corrections and risks.', actual: 'AI learning events require human review and cannot self-modify.', status: 'PASS', risk: 'Medium', fixNeeded: 'Add reviewed training workflow later.' },
  { step: 34, area: 'founder', feature: 'Deep-learning foundation preview', route: '/founder/deep-learning-preview', expected: 'No model training.', actual: 'Model training is blocked; preview only.', status: 'PASS', risk: 'Medium', fixNeeded: 'Formal model governance later.' },
  { step: 35, area: 'founder', feature: 'Launch gates', route: '/founder/launch-gates', expected: 'Commercial launch blocked.', actual: 'Launch gates show production blocked.', status: 'PASS', risk: 'High', fixNeeded: 'Complete auth/RLS/vault/compliance/legal review.' },
];

export const customerRoutes = uatSteps.filter((step) => step.area === 'customer');
export const founderRoutes = uatSteps.filter((step) => step.area === 'founder');
