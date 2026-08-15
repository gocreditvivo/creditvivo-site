import type { ScannerParseResult } from './scannerApi';
import { supabase } from './supabaseClient';

const LAST_SCAN_KEY = 'creditVivoLastScanResult';
const LAST_SCAN_OWNER_KEY = 'creditVivoLastScanOwner';
let activeUserId: string | null = null;

export function setScanStorageUser(userId: string | null) {
  activeUserId = userId;
  try {
    const storedOwner = localStorage.getItem(LAST_SCAN_OWNER_KEY);
    if (!userId || storedOwner !== userId) {
      localStorage.removeItem(LAST_SCAN_KEY);
    }
    if (userId) localStorage.setItem(LAST_SCAN_OWNER_KEY, userId);
    else localStorage.removeItem(LAST_SCAN_OWNER_KEY);
  } catch {
    // Storage can be unavailable in strict private browsing modes.
  }
}

export function saveLastScanResult(result: ScannerParseResult) {
  try {
    if (!activeUserId) return;
    localStorage.setItem(LAST_SCAN_KEY, JSON.stringify(result));
    localStorage.setItem(LAST_SCAN_OWNER_KEY, activeUserId);
  } catch {
    // Storage can be unavailable in strict private browsing modes.
  }
  void persistSafeScanSummary(result);
}

async function persistSafeScanSummary(result: ScannerParseResult) {
  if (!supabase) return;
  const { data: authData } = await supabase.auth.getUser();
  const user = authData.user;
  if (!user) return;

  const { data: scan, error } = await supabase.from('creditvivo_scans').insert({
    user_id: user.id,
    mode: result.job_id === 'demo_scan' ? 'demo' : 'scanner',
    status: 'ready',
    review_items_count: result.review_items_count ?? 0,
    issues_count: result.issues_count ?? 0,
    customer_summary: result.customer_summary ?? {},
  }).select('id').single();
  if (error || !scan) return;

  const reviewById = new Map((result.review_items_preview ?? []).map((item) => [item.id, item]));
  const findings = (result.issues_preview ?? []).map((issue) => {
    const review = issue.related_tradeline_ids?.length ? reviewById.get(issue.related_tradeline_ids[0]) : undefined;
    return {
      scan_id: scan.id,
      user_id: user.id,
      finding_key: issue.id,
      bureau: review?.bureau ?? null,
      account_name: review?.account_name ?? null,
      account_number_masked: review?.account_number_masked ?? null,
      finding_type: issue.issue_type,
      severity: issue.severity,
      explanation: issue.customer_explanation,
      review_status: 'needs_verification',
    };
  });
  if (findings.length) await supabase.from('creditvivo_findings').insert(findings);
}

export function getLastScanResult(): ScannerParseResult | null {
  try {
    if (!activeUserId || localStorage.getItem(LAST_SCAN_OWNER_KEY) !== activeUserId) return null;
    const raw = localStorage.getItem(LAST_SCAN_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as ScannerParseResult;
  } catch {
    return null;
  }
}

export async function restoreLatestScanResult(userId: string): Promise<ScannerParseResult | null> {
  const cached = getLastScanResult();
  if (cached || !supabase || !userId) return cached;

  const { data: scan, error: scanError } = await supabase
    .from('creditvivo_scans')
    .select('id, mode, status, review_items_count, issues_count, customer_summary, created_at')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  if (scanError || !scan) return null;

  const { data: findings, error: findingsError } = await supabase
    .from('creditvivo_findings')
    .select('finding_key, bureau, account_name, account_number_masked, finding_type, severity, explanation')
    .eq('user_id', userId)
    .eq('scan_id', scan.id)
    .order('created_at', { ascending: true });

  if (findingsError) return null;

  const restoredFindings = findings ?? [];
  const reviewItems = restoredFindings.map((finding, index) => ({
    id: `restored_review_${index + 1}`,
    bureau: finding.bureau ?? undefined,
    account_name: finding.account_name ?? undefined,
    account_number_masked: finding.account_number_masked ?? undefined,
    needs_admin_review: true,
  }));
  const issues = restoredFindings.map((finding, index) => ({
    id: finding.finding_key || `restored_issue_${index + 1}`,
    issue_type: finding.finding_type,
    severity: finding.severity,
    customer_label: String(finding.finding_type || 'Review point').replace(/_/g, ' '),
    customer_explanation: finding.explanation,
    admin_explanation: finding.explanation,
    suggested_round: 'Review saved finding',
    related_tradeline_ids: [reviewItems[index].id],
    confidence: 'medium',
  }));

  const result: ScannerParseResult = {
    job_id: `saved_${scan.id}`,
    files: [],
    ai_second_pass: false,
    paid_ai_used: false,
    status: { mode: scan.mode, message: 'Your latest saved Credit Check-In is ready.' },
    review_items_count: scan.review_items_count ?? reviewItems.length,
    issues_count: scan.issues_count ?? issues.length,
    customer_message: 'Your latest saved Credit Check-In is ready.',
    customer_summary: scan.customer_summary ?? {},
    review_items_preview: reviewItems,
    issues_preview: issues,
  };

  try {
    localStorage.setItem(LAST_SCAN_KEY, JSON.stringify(result));
    localStorage.setItem(LAST_SCAN_OWNER_KEY, userId);
  } catch {
    // The database remains the source of truth if local storage is unavailable.
  }

  return result;
}

export function clearLastScanResult() {
  try {
    localStorage.removeItem(LAST_SCAN_KEY);
    localStorage.removeItem(LAST_SCAN_OWNER_KEY);
  } catch {
    // Storage can be unavailable in strict private browsing modes.
  }
}

export function getDemoScanResult(): ScannerParseResult {
  return {
    job_id: 'demo_scan',
    files: [
      { filename: 'experian-demo.pdf', bureau: 'Experian', pages: 40, chars: 100000, status: 'demo' },
      { filename: 'equifax-demo.pdf', bureau: 'Equifax', pages: 20, chars: 60000, status: 'demo' },
      { filename: 'transunion-demo.pdf', bureau: 'TransUnion', pages: 56, chars: 120000, status: 'demo' },
    ],
    ai_second_pass: false,
    paid_ai_used: false,
    status: {
      mode: 'credit_vivo_proprietary_engine_v16_demo',
      message: 'Demo findings loaded. No report was uploaded.',
    },
    review_items_count: 7,
    issues_count: 6,
    customer_message:
      'Your Credit Check-In was reviewed. Items are organized for review before any action is sent.',
    customer_summary: {
      headline: 'Your Credit Check-In was reviewed.',
      message:
        'Credit Vivo organized review items into clear categories. No letters or disputes are sent without your approval.',
      review_items: 7,
      possible_review_points: 6,
      categories: [
        'Collection review',
        'Charge-off review',
        'Balance differs across bureaus',
        'Status differs across bureaus',
      ],
      next_step: 'Review findings in the dashboard.',
    },
    review_items_preview: [
      {
        id: 'demo_1',
        bureau: 'Experian',
        account_name: 'Midland Credit Management',
        account_number_masked: '*1234',
        account_type: 'Collection',
        balance: '$1,234',
        status: 'Collection',
        original_creditor: 'Capital One',
        confidence: 'medium',
        confidence_score: 0.64,
        needs_admin_review: true,
      },
      {
        id: 'demo_2',
        bureau: 'Equifax',
        account_name: 'Capital One',
        account_number_masked: '*8899',
        account_type: 'Credit Card',
        balance: '$0',
        status: 'Charge-off transferred or sold',
        date_of_first_delinquency: '10/01/2020',
        confidence: 'medium',
        confidence_score: 0.67,
        needs_admin_review: true,
      },
    ],
    issues_preview: [
      {
        id: 'issue_1',
        issue_type: 'collection_review',
        severity: 'medium',
        customer_label: 'Collection review',
        customer_explanation:
          'This collection item should be reviewed for original creditor, balance, ownership, and reporting details.',
        admin_explanation:
          'Collection/debt buyer candidate. Verify original creditor, assignment/ownership, balance, authority, and reporting fields.',
        suggested_round: 'Round 2 — Collection Review',
        related_tradeline_ids: ['demo_1'],
        confidence: 'medium',
      },
      {
        id: 'issue_2',
        issue_type: 'chargeoff_review',
        severity: 'medium',
        customer_label: 'Charge-off review',
        customer_explanation:
          'This charge-off should be reviewed for balance, status, dates, and whether it was sold or transferred.',
        admin_explanation:
          'Charge-off candidate. Check DOFD, balance, sold/transferred status, creditor ownership, and duplicate collection reporting.',
        suggested_round: 'Round 4 — Reporting Accuracy Review',
        related_tradeline_ids: ['demo_2'],
        confidence: 'medium',
      },
    ],
    cross_bureau_groups: [
      {
        group_id: 'demo_group_1',
        bureaus: ['Experian', 'Equifax'],
        account_names: ['Capital One'],
        review_note:
          'Same or similar item appears across multiple bureaus. Compare balance, status, dates, original creditor, and remarks.',
      },
    ],
    letter_workflow: {
      fcra_notice_of_dispute:
        'This account appears inaccurate, incomplete, or unverifiable. Please investigate under the FCRA and correct, update, or delete any information that cannot be verified.',
    },
    recommended_letter_queue: [
      {
        letter_id: 'letter_demo_1',
        issue_id: 'issue_1',
        issue_type: 'collection_review',
        letter_type: 'furnisher_direct_dispute',
        round: 'Round 2 - Collection Review',
        recipient_type: 'furnisher_or_collector',
        responsible_party: 'furnisher_or_collector',
        delivery_method: 'certified_mail_recommended',
        fcra_notice_required: true,
        fcra_notice_included: true,
        customer_approval_required: true,
        customer_authorization_verified: false,
        tracking_status: 'draft_not_sent',
        recommended_next_action: 'furnisher_direct_dispute_after_bureau_review',
        escalation_candidate: false,
        letter_subject: 'Direct Dispute of Account Reporting - Collection review',
        draft_letter_body:
          'DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED\n\nTo whom it may concern:\n\nI dispute the accuracy and completeness of the collection account reporting on my credit file. Please investigate the account under the FCRA and provide the basis for reporting, ownership or assignment records, original creditor information, balance support, and any documents used to verify the account.\n\nIf the account cannot be verified as accurate and complete, please correct or delete the reporting.\n\nThis draft is not sent automatically.',
      },
      {
        letter_id: 'letter_demo_2',
        issue_id: 'issue_2',
        issue_type: 'chargeoff_review',
        letter_type: 'bureau_dispute',
        round: 'Round 4 - Reporting Accuracy Review',
        recipient_type: 'credit_bureau',
        responsible_party: 'bureau_and_furnisher',
        delivery_method: 'certified_mail_recommended',
        fcra_notice_required: true,
        fcra_notice_included: true,
        customer_approval_required: true,
        customer_authorization_verified: false,
        tracking_status: 'draft_not_sent',
        recommended_next_action: 'round_2_bureau_dispute_then_reinvestigation_if_unverified',
        escalation_candidate: true,
        letter_subject: 'Credit Bureau Dispute - Charge-off review',
        draft_letter_body:
          'DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED\n\nTo whom it may concern:\n\nI dispute the accuracy and completeness of this charge-off reporting. Please conduct a reasonable investigation under the FCRA and verify the balance, status, dates, payment history, ownership, and whether the account was sold or transferred.\n\nIf any reporting cannot be verified as accurate and complete, please correct or delete it.\n\nThis draft is not sent automatically.',
      },
    ],
    fcra_review: [
      {
        issue_id: 'issue_1',
        possible_fcra_issue: true,
        issue_type: 'collection_review',
        responsible_party: 'furnisher_or_collector',
        dispute_history_complete: false,
        evidence_strength: 'medium',
        damages_evidence: 'none',
        next_action: 'furnisher_direct_dispute_after_bureau_review',
        requires_admin_review: true,
      },
    ],
  };
}
