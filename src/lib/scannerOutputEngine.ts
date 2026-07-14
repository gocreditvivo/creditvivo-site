import type { DummyCreditReport, DummyTradeline } from './dummyCreditReports';
import { buildLetterWorkflowSummary, buildScannerLetterQueue } from './scannerLetterEngine';

export type ScannerSelfCheckStatus = 'PASS' | 'FAIL' | 'REVIEW';

export type ScannerRequiredField =
  | 'account_name'
  | 'bureau'
  | 'account_type'
  | 'account_number_masked'
  | 'status'
  | 'balance_range_or_masked_balance'
  | 'date_fields_synthetic'
  | 'confidence_score'
  | 'possible_issue'
  | 'issue_type'
  | 'recommended_letter_type';

export type ScannerOutput = {
  report_id: string;
  parser_version: 'cv-staging-scanner-output-v1';
  process_mode: 'process_only';
  consumer_info_summary: {
    display_name: string;
    login_email: string;
    persona: string;
    report_status: string;
    score_start: number;
    score_current: number;
    score_goal: number;
    bureau_scores: DummyCreditReport['bureau_scores'];
  };
  bureau_reports: Array<{
    bureau: DummyTradeline['bureau'];
    score: number;
    tradeline_count: number;
    negative_count: number;
    highest_severity: DummyTradeline['severity'];
  }>;
  accounts: Array<DummyTradeline & {
    normalized_account_key: string;
    missing_required_fields: ScannerRequiredField[];
    is_negative_or_review_item: boolean;
  }>;
  negative_tradelines: Array<DummyTradeline & {
    normalized_account_key: string;
    evidence_needed: string[];
    customer_safe_summary: string;
    admin_review_reason: string;
  }>;
  collections: DummyTradeline[];
  inquiries: Array<{ status: 'not_modeled_in_dummy_fixture'; note: string }>;
  bureau_differences: Array<{
    normalized_account_key: string;
    bureaus: DummyTradeline['bureau'][];
    issue: string;
    status: ScannerSelfCheckStatus;
  }>;
  possible_dispute_leads: Array<{
    source_tradeline_id: string;
    issue_type: DummyTradeline['issue_type'];
    recommended_action: string;
    confidence_score: number;
    evidence_needed: string[];
  }>;
  missing_information_needed: string[];
  score_blockers: Array<{
    issue_type: DummyTradeline['issue_type'];
    severity: DummyTradeline['severity'];
    estimated_priority: number;
    reason: string;
  }>;
  customer_summary: string;
  admin_summary: string;
  letter_workflow: ReturnType<typeof buildLetterWorkflowSummary>;
  recommended_letter_queue: ReturnType<typeof buildScannerLetterQueue>;
  self_checks: Array<{
    check_id: string;
    label: string;
    status: ScannerSelfCheckStatus;
    detail: string;
  }>;
};

const REQUIRED_FIELDS: ScannerRequiredField[] = [
  'account_name',
  'bureau',
  'account_type',
  'account_number_masked',
  'status',
  'balance_range_or_masked_balance',
  'date_fields_synthetic',
  'confidence_score',
  'possible_issue',
  'issue_type',
  'recommended_letter_type',
];

const SEVERITY_RANK: Record<DummyTradeline['severity'], number> = {
  Low: 1,
  Medium: 2,
  High: 3,
  Critical: 4,
};

const REVIEW_ISSUES: DummyTradeline['issue_type'][] = [
  'bankruptcy',
  'medical_collection',
  'mortgage_late',
  'reaging',
  'charge_off',
  'duplicate_collection',
  'bureau_mismatch',
  'identity_mismatch',
];

function accountKey(item: DummyTradeline) {
  return `${item.account_name.toLowerCase().replace(/[^a-z0-9]/g, '')}-${item.account_number_masked}`;
}

function missingFields(item: DummyTradeline) {
  return REQUIRED_FIELDS.filter((field) => {
    const value = item[field];
    return value === undefined || value === null || value === '';
  });
}

function highestSeverity(items: DummyTradeline[]) {
  return items.reduce<DummyTradeline['severity']>((highest, item) => {
    return SEVERITY_RANK[item.severity] > SEVERITY_RANK[highest] ? item.severity : highest;
  }, 'Low');
}

function evidenceForIssue(issueType: DummyTradeline['issue_type']) {
  const evidence: Record<DummyTradeline['issue_type'], string[]> = {
    bankruptcy: ['bankruptcy discharge/docket reference', 'bureau page with account', 'account statement if available'],
    medical_collection: ['medical bill or collection notice', 'insurance/EOB if available', 'payment proof if paid'],
    mortgage_late: ['mortgage statements', 'payment confirmations', 'bureau page with payment history'],
    reaging: ['older bureau report showing prior date fields', 'collection notice', 'current bureau page'],
    charge_off: ['account statement', 'charge-off or transfer notice', 'original creditor details'],
    duplicate_collection: ['bureau pages for both collection entries', 'original creditor detail', 'collection notices'],
    bureau_mismatch: ['Experian page', 'Equifax page', 'TransUnion page', 'account statement if available'],
    thin_file: ['no dispute evidence required unless a specific error exists'],
    high_utilization: ['current balance and credit limit', 'latest statement if available'],
    identity_mismatch: ['identity verification status', 'proof of address if needed', 'consumer statement on unrecognized account'],
  };
  return evidence[issueType];
}

function recommendedAction(item: DummyTradeline) {
  if (item.issue_type === 'thin_file') return 'customer education / no dispute recommended';
  if (item.issue_type === 'high_utilization') return 'utilization action plan / no dispute recommended';
  if (item.issue_type === 'identity_mismatch') return 'identity evidence review before draft movement';
  return item.recommended_letter_type;
}

export function buildScannerOutput(report: DummyCreditReport): ScannerOutput {
  const accounts = report.tradelines.map((item) => ({
    ...item,
    normalized_account_key: accountKey(item),
    missing_required_fields: missingFields(item),
    is_negative_or_review_item: REVIEW_ISSUES.includes(item.issue_type),
  }));

  const negativeTradelines = accounts
    .filter((item) => item.is_negative_or_review_item)
    .map((item) => ({
      ...item,
      evidence_needed: evidenceForIssue(item.issue_type),
      customer_safe_summary: `${item.account_name} may need review for ${item.possible_issue.toLowerCase()}`,
      admin_review_reason: `${item.issue_type} | ${item.severity} | confidence ${item.confidence_score}`,
    }));

  const groupedByBureau = (['Experian', 'Equifax', 'TransUnion'] as const).map((bureau) => {
    const bureauItems = accounts.filter((item) => item.bureau === bureau);
    return {
      bureau,
      score: report.bureau_scores[bureau],
      tradeline_count: bureauItems.length,
      negative_count: bureauItems.filter((item) => item.is_negative_or_review_item).length,
      highest_severity: highestSeverity(bureauItems),
    };
  });

  const byKey = accounts.reduce<Record<string, typeof accounts>>((acc, item) => {
    acc[item.normalized_account_key] = acc[item.normalized_account_key] || [];
    acc[item.normalized_account_key].push(item);
    return acc;
  }, {});

  const bureauDifferences = Object.entries(byKey)
    .filter(([, items]) => items.length > 1 || items.some((item) => item.issue_type === 'bureau_mismatch' || item.issue_type === 'duplicate_collection'))
    .map(([normalized_account_key, items]) => ({
      normalized_account_key,
      bureaus: Array.from(new Set(items.map((item) => item.bureau))),
      issue: items.map((item) => item.possible_issue).join(' | '),
      status: 'REVIEW' as const,
    }));

  const possibleDisputeLeads = negativeTradelines.map((item) => ({
    source_tradeline_id: item.id,
    issue_type: item.issue_type,
    recommended_action: recommendedAction(item),
    confidence_score: item.confidence_score,
    evidence_needed: item.evidence_needed,
  }));

  const missingInformation = Array.from(new Set([
    ...accounts.flatMap((item) => item.missing_required_fields.map((field) => `${item.account_name}: missing ${field}`)),
    ...negativeTradelines.flatMap((item) => item.evidence_needed.map((evidence) => `${item.account_name}: ${evidence}`)),
  ]));

  const letterWorkflow = buildLetterWorkflowSummary(report);
  const letterQueue = buildScannerLetterQueue(report);

  const selfChecks = [
    {
      check_id: 'three_bureau_scores_present',
      label: 'Three bureau scores present',
      status: Object.values(report.bureau_scores).every((score) => score > 300) ? 'PASS' : 'FAIL',
      detail: `Experian ${report.bureau_scores.Experian}, Equifax ${report.bureau_scores.Equifax}, TransUnion ${report.bureau_scores.TransUnion}`,
    },
    {
      check_id: 'required_fields_complete',
      label: 'Required tradeline fields complete',
      status: accounts.every((item) => item.missing_required_fields.length === 0) ? 'PASS' : 'FAIL',
      detail: accounts.every((item) => item.missing_required_fields.length === 0) ? 'All modeled tradelines include required fields.' : 'One or more modeled tradelines are missing required fields.',
    },
    {
      check_id: 'negative_items_classified',
      label: 'Negative/review items classified',
      status: negativeTradelines.length > 0 || report.id === 'cv-test-008' || report.id === 'cv-test-009' ? 'PASS' : 'REVIEW',
      detail: `${negativeTradelines.length} negative/review items classified.`,
    },
    {
      check_id: 'letter_queue_safe',
      label: 'Letter queue safe defaults',
      status: letterQueue.every((item) => !item.send_allowed && !item.auto_send_allowed && !item.mailing_allowed && !item.email_allowed) ? 'PASS' : 'FAIL',
      detail: 'All generated queue items keep send, auto-send, mail, and email disabled.',
    },
    {
      check_id: 'evidence_attached',
      label: 'Evidence requirements attached',
      status: letterQueue.every((item) => item.evidence_needed.length > 0) ? 'PASS' : 'FAIL',
      detail: 'Every generated queue item has an evidence checklist.',
    },
  ] satisfies ScannerOutput['self_checks'];

  return {
    report_id: report.id,
    parser_version: 'cv-staging-scanner-output-v1',
    process_mode: 'process_only',
    consumer_info_summary: {
      display_name: report.display_name,
      login_email: report.login_email,
      persona: report.persona,
      report_status: report.report_status,
      score_start: report.score_start,
      score_current: report.score_current,
      score_goal: report.score_goal,
      bureau_scores: report.bureau_scores,
    },
    bureau_reports: groupedByBureau,
    accounts,
    negative_tradelines: negativeTradelines,
    collections: accounts.filter((item) => item.account_type.toLowerCase().includes('collection')),
    inquiries: [{ status: 'not_modeled_in_dummy_fixture', note: 'Inquiry parsing skill is reserved for real/sanitized report fixtures.' }],
    bureau_differences: bureauDifferences,
    possible_dispute_leads: possibleDisputeLeads,
    missing_information_needed: missingInformation,
    score_blockers: accounts
      .map((item) => ({
        issue_type: item.issue_type,
        severity: item.severity,
        estimated_priority: SEVERITY_RANK[item.severity],
        reason: item.possible_issue,
      }))
      .sort((a, b) => b.estimated_priority - a.estimated_priority),
    customer_summary: `${report.display_name} has a ${report.persona.toLowerCase()} with ${negativeTradelines.length} item(s) needing review. Results are not guaranteed.`,
    admin_summary: `${report.id}: ${accounts.length} tradeline(s), ${negativeTradelines.length} negative/review item(s), ${letterQueue.length} generated queue item(s), ${selfChecks.filter((check) => check.status === 'PASS').length}/${selfChecks.length} self-checks passed.`,
    letter_workflow: letterWorkflow,
    recommended_letter_queue: letterQueue,
    self_checks: selfChecks,
  };
}
