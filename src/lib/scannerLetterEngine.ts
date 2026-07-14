import type { DummyCreditReport, DummyTradeline } from './dummyCreditReports';

export type LetterType =
  | 'bankruptcy_reporting_review'
  | 'medical_collection_validation'
  | 'mortgage_payment_history_review'
  | 'reaging_date_review'
  | 'charge_off_balance_status_review'
  | 'duplicate_collection_review'
  | 'bureau_consistency_review'
  | 'no_dispute_recommended'
  | 'utilization_action_plan'
  | 'identity_account_investigation';

export type RecipientType = 'credit_bureau' | 'furnisher_or_collector' | 'customer_action_plan' | 'admin_review';

export type ScannerLetterQueueItem = {
  queue_id: string;
  source_report_id: string;
  source_tradeline_id: string;
  account_name: string;
  account_number_masked: string;
  bureau: DummyTradeline['bureau'];
  issue_type: DummyTradeline['issue_type'];
  letter_type: LetterType;
  recipient_type: RecipientType;
  letter_subject: string;
  draft_letter_body: string;
  evidence_needed: string[];
  approval_status: {
    customer_approval_required: true;
    customer_approval_status: 'required';
    admin_review_required: true;
    admin_review_status: 'required';
    compliance_review_required: true;
    compliance_review_status: 'blocked_until_review';
  };
  tracking_status: 'draft_not_sent' | 'no_letter_recommended';
  queue_stage:
    | '00_SYSTEM_DRAFTS'
    | '01_CUSTOMER_APPROVAL_REQUIRED'
    | '02_ADMIN_REVIEW_REQUIRED'
    | '03_COMPLIANCE_REVIEW_REQUIRED'
    | '05_BLOCKED_REJECTED';
  send_allowed: false;
  auto_send_allowed: false;
  mailing_allowed: false;
  email_allowed: false;
  lob_ready_preview: {
    status: 'blocked_until_approvals';
    blocked_until: string[];
  };
  safe_wording_status: 'pass';
};

const LETTER_RULES: Record<DummyTradeline['issue_type'], {
  letter_type: LetterType;
  recipient_type: RecipientType;
  subject: string;
  evidence: string[];
  action: string;
}> = {
  bankruptcy: {
    letter_type: 'bankruptcy_reporting_review',
    recipient_type: 'furnisher_or_collector',
    subject: 'Draft Bankruptcy Reporting Review',
    evidence: ['bankruptcy discharge or docket reference', 'account statement if available', 'bureau report page showing the tradeline'],
    action: 'review the bankruptcy status, balance, remarks, and post-discharge reporting for accuracy and completeness',
  },
  medical_collection: {
    letter_type: 'medical_collection_validation',
    recipient_type: 'furnisher_or_collector',
    subject: 'Draft Medical Collection Validation Review',
    evidence: ['medical bill or collection notice', 'insurance/EOB record if available', 'payment or settlement proof if applicable'],
    action: 'review the medical collection classification, balance, payment status, and supporting documentation',
  },
  mortgage_late: {
    letter_type: 'mortgage_payment_history_review',
    recipient_type: 'furnisher_or_collector',
    subject: 'Draft Mortgage Payment History Review',
    evidence: ['mortgage statements', 'payment confirmation records', 'bureau report page showing the late-payment notation'],
    action: 'review the reported mortgage payment history against available payment evidence',
  },
  reaging: {
    letter_type: 'reaging_date_review',
    recipient_type: 'credit_bureau',
    subject: 'Draft Date Reporting Review',
    evidence: ['prior report showing older date fields', 'collection notice if available', 'bureau report page showing current date fields'],
    action: 'review whether the reported dates are accurate, complete, and supported by the account history',
  },
  charge_off: {
    letter_type: 'charge_off_balance_status_review',
    recipient_type: 'furnisher_or_collector',
    subject: 'Draft Charge-Off Balance and Status Review',
    evidence: ['account statement', 'charge-off notice if available', 'transfer or sale notice if available'],
    action: 'review the charge-off balance, transferred/sold status, and original creditor information',
  },
  duplicate_collection: {
    letter_type: 'duplicate_collection_review',
    recipient_type: 'credit_bureau',
    subject: 'Draft Duplicate Collection Review',
    evidence: ['bureau pages for both collection entries', 'original creditor information if available', 'collection notices if available'],
    action: 'review whether the listed collection entries may represent the same alleged debt',
  },
  bureau_mismatch: {
    letter_type: 'bureau_consistency_review',
    recipient_type: 'credit_bureau',
    subject: 'Draft Cross-Bureau Consistency Review',
    evidence: ['Experian report page', 'Equifax report page', 'TransUnion report page', 'account statement if available'],
    action: 'compare the reported status, balance, dates, and account details across bureaus',
  },
  thin_file: {
    letter_type: 'no_dispute_recommended',
    recipient_type: 'customer_action_plan',
    subject: 'No Dispute Draft Recommended',
    evidence: ['no evidence required unless a specific report error is identified'],
    action: 'provide education and score-path guidance instead of creating a dispute draft without a clear report error',
  },
  high_utilization: {
    letter_type: 'utilization_action_plan',
    recipient_type: 'customer_action_plan',
    subject: 'Utilization Action Plan Preview',
    evidence: ['current balance and limit shown on report', 'latest statement if available'],
    action: 'show a utilization-focused action plan rather than a dispute draft when reporting appears accurate',
  },
  identity_mismatch: {
    letter_type: 'identity_account_investigation',
    recipient_type: 'admin_review',
    subject: 'Draft Identity-Related Account Investigation',
    evidence: ['identity verification status', 'proof of address if needed', 'consumer statement about unrecognized account', 'bureau report page showing the account'],
    action: 'route to identity evidence review before any dispute, escalation, or referral',
  },
};

const QUEUE_STAGE_BY_TYPE: Record<LetterType, ScannerLetterQueueItem['queue_stage']> = {
  bankruptcy_reporting_review: '02_ADMIN_REVIEW_REQUIRED',
  medical_collection_validation: '01_CUSTOMER_APPROVAL_REQUIRED',
  mortgage_payment_history_review: '02_ADMIN_REVIEW_REQUIRED',
  reaging_date_review: '03_COMPLIANCE_REVIEW_REQUIRED',
  charge_off_balance_status_review: '01_CUSTOMER_APPROVAL_REQUIRED',
  duplicate_collection_review: '02_ADMIN_REVIEW_REQUIRED',
  bureau_consistency_review: '02_ADMIN_REVIEW_REQUIRED',
  no_dispute_recommended: '05_BLOCKED_REJECTED',
  utilization_action_plan: '05_BLOCKED_REJECTED',
  identity_account_investigation: '02_ADMIN_REVIEW_REQUIRED',
};

function buildDraftBody(report: DummyCreditReport, tradeline: DummyTradeline, rule: typeof LETTER_RULES[DummyTradeline['issue_type']]) {
  if (rule.letter_type === 'no_dispute_recommended' || rule.letter_type === 'utilization_action_plan') {
    return [
      'DRAFT ONLY - CUSTOMER REVIEW.',
      'Credit Vivo does not recommend creating a dispute letter for this synthetic item unless a specific inaccurate, incomplete, or unverifiable report detail is identified.',
      `Customer profile: ${report.persona}.`,
      `Account reviewed: ${tradeline.account_name} ${tradeline.account_number_masked}.`,
      `Reason: ${tradeline.possible_issue}`,
      'Next step: use the customer action plan, monitor progress, and keep results language non-guaranteed.',
    ].join('\n\n');
  }

  return [
    'DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED.',
    'This draft is for Credit Vivo internal testing and review only. It is not legal advice and is not sent automatically.',
    `Consumer profile: ${report.display_name} (${report.persona}).`,
    `Account: ${tradeline.account_name} ${tradeline.account_number_masked}.`,
    `Bureau/source shown in test data: ${tradeline.bureau}.`,
    `Reported status: ${tradeline.status}.`,
    `Possible issue for review: ${tradeline.possible_issue}`,
    `Requested review: Please ${rule.action}.`,
    'Please investigate the specific information identified above and provide the written results of any review or investigation. Accurate, current, and verifiable information may remain.',
    'Credit Vivo controls: customer approval, admin review, evidence review, compliance review, and audit logging are required before any packet can move forward.',
  ].join('\n\n');
}

export function buildScannerLetterQueue(report: DummyCreditReport): ScannerLetterQueueItem[] {
  return report.tradelines.map((tradeline, index) => {
    const rule = LETTER_RULES[tradeline.issue_type];
    const noLetter = rule.letter_type === 'no_dispute_recommended' || rule.letter_type === 'utilization_action_plan';

    return {
      queue_id: `${report.id}-letter-${String(index + 1).padStart(2, '0')}`,
      source_report_id: report.id,
      source_tradeline_id: tradeline.id,
      account_name: tradeline.account_name,
      account_number_masked: tradeline.account_number_masked,
      bureau: tradeline.bureau,
      issue_type: tradeline.issue_type,
      letter_type: rule.letter_type,
      recipient_type: rule.recipient_type,
      letter_subject: rule.subject,
      draft_letter_body: buildDraftBody(report, tradeline, rule),
      evidence_needed: rule.evidence,
      approval_status: {
        customer_approval_required: true,
        customer_approval_status: 'required',
        admin_review_required: true,
        admin_review_status: 'required',
        compliance_review_required: true,
        compliance_review_status: 'blocked_until_review',
      },
      tracking_status: noLetter ? 'no_letter_recommended' : 'draft_not_sent',
      queue_stage: QUEUE_STAGE_BY_TYPE[rule.letter_type],
      send_allowed: false,
      auto_send_allowed: false,
      mailing_allowed: false,
      email_allowed: false,
      lob_ready_preview: {
        status: 'blocked_until_approvals',
        blocked_until: ['customer approval', 'admin review', 'evidence review', 'compliance review', 'audit log'],
      },
      safe_wording_status: 'pass',
    };
  });
}

export function buildLetterWorkflowSummary(report: DummyCreditReport) {
  const queue = buildScannerLetterQueue(report);
  return {
    report_id: report.id,
    total_queue_items: queue.length,
    draft_letters: queue.filter((item) => item.tracking_status === 'draft_not_sent').length,
    no_letter_recommended: queue.filter((item) => item.tracking_status === 'no_letter_recommended').length,
    send_letters_automatically: false,
    auto_send_allowed: false,
    mailing_allowed: false,
    email_allowed: false,
    approval_required: true,
    customer_approval_required: true,
    admin_review_required: true,
    compliance_review_required: true,
    workflow: 'possible_issue -> recommended_letter_type -> draft_packet -> customer_approval -> admin_review -> compliance_review -> internal_queue_not_sent',
  };
}
