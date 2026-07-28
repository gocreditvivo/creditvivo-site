import type { ScannerParseResult } from './scannerApi';

const LAST_SCAN_KEY = 'creditVivoLastScanResult';

function getBrowserStorage(): Storage | undefined {
  return typeof window !== 'undefined' ? window.localStorage : undefined;
}

export function saveLastScanResult(result: ScannerParseResult) {
  getBrowserStorage()?.setItem(LAST_SCAN_KEY, JSON.stringify(result));
}

export function getLastScanResult(): ScannerParseResult | null {
  const raw = getBrowserStorage()?.getItem(LAST_SCAN_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as ScannerParseResult;
  } catch {
    return null;
  }
}

export function clearLastScanResult() {
  getBrowserStorage()?.removeItem(LAST_SCAN_KEY);
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
        raw_block:
          'MIDLAND CREDIT MANAGEMENT Account Type: Collection Balance: $1,234 Original Creditor: Capital One Remarks: Account placed for collection',
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
        raw_block:
          'CAPITAL ONE Account Type: Credit Card Balance: $0 Status: Charge-off transferred or sold Date of First Delinquency: 10/01/2020',
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
  };
}
