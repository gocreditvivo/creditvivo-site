import { readFileSync } from 'node:fs';

const fixture = readFileSync('src/lib/dummyCreditReports.ts', 'utf8');
const letterEngine = readFileSync('src/lib/scannerLetterEngine.ts', 'utf8');
const scannerOutputEngine = readFileSync('src/lib/scannerOutputEngine.ts', 'utf8');
const memberPage = readFileSync('src/pages/MemberProcessPage.tsx', 'utf8');
const founderPage = readFileSync('src/pages/FounderProcessPage.tsx', 'utf8');
const requiredIssueTypes = [
  'bankruptcy',
  'medical_collection',
  'mortgage_late',
  'reaging',
  'charge_off',
  'duplicate_collection',
  'bureau_mismatch',
  'thin_file',
  'high_utilization',
  'identity_mismatch',
];

let failed = false;
const reportCount = (fixture.match(/id: 'cv-test-\d{3}'/g) || []).length;
if (reportCount !== 10) {
  console.error(`FAIL expected 10 dummy reports, found ${reportCount}`);
  failed = true;
}

for (const issue of requiredIssueTypes) {
  if (!fixture.includes(`'${issue}'`)) {
    console.error(`FAIL missing dummy issue type: ${issue}`);
    failed = true;
  }
}

for (const bureau of ['Experian', 'Equifax', 'TransUnion']) {
  if (!fixture.includes(bureau)) {
    console.error(`FAIL missing bureau: ${bureau}`);
    failed = true;
  }
}

for (const requiredText of ['draft_letter_preview', 'email_preview', 'tracking_stages', 'score_start', 'score_current', 'score_goal']) {
  if (!fixture.includes(requiredText)) {
    console.error(`FAIL missing required report field: ${requiredText}`);
    failed = true;
  }
}

for (const requiredEngineText of [
  'buildScannerLetterQueue',
  'buildLetterWorkflowSummary',
  'send_allowed: false',
  'auto_send_allowed: false',
  'mailing_allowed: false',
  'email_allowed: false',
  'blocked_until_approvals',
  'CUSTOMER REVIEW AND APPROVAL REQUIRED',
]) {
  if (!letterEngine.includes(requiredEngineText)) {
    console.error(`FAIL scanner letter engine missing: ${requiredEngineText}`);
    failed = true;
  }
}

for (const requiredType of [
  'bankruptcy_reporting_review',
  'medical_collection_validation',
  'mortgage_payment_history_review',
  'reaging_date_review',
  'charge_off_balance_status_review',
  'duplicate_collection_review',
  'bureau_consistency_review',
  'no_dispute_recommended',
  'utilization_action_plan',
  'identity_account_investigation',
]) {
  if (!letterEngine.includes(requiredType)) {
    console.error(`FAIL scanner letter engine missing letter type: ${requiredType}`);
    failed = true;
  }
}

for (const requiredScannerOutputText of [
  'buildScannerOutput',
  'consumer_info_summary',
  'bureau_reports',
  'negative_tradelines',
  'possible_dispute_leads',
  'missing_information_needed',
  'self_checks',
  'letter_queue_safe',
]) {
  if (!scannerOutputEngine.includes(requiredScannerOutputText)) {
    console.error(`FAIL scanner output engine missing: ${requiredScannerOutputText}`);
    failed = true;
  }
}

if (!memberPage.includes('buildScannerLetterQueue') || !memberPage.includes('Generated scanner letter queue') || !memberPage.includes('ScannerOutputPanel')) {
  console.error('FAIL member page is not wired to generated scanner letter queue');
  failed = true;
}

if (!founderPage.includes('buildScannerLetterQueue') || !founderPage.includes('Generated draft queue') || !founderPage.includes('buildScannerOutput')) {
  console.error('FAIL founder page is not wired to generated scanner letter queue');
  failed = true;
}

if (/\b\d{3}-\d{2}-\d{4}\b/.test(fixture)) {
  console.error('FAIL dummy reports contain SSN-like value');
  failed = true;
}

if (/\b\d{9,}\b/.test(fixture)) {
  console.error('FAIL dummy reports contain long unmasked number');
  failed = true;
}

if (failed) process.exit(1);
console.log('PASS dummy credit report validation');
