export type ScannerFileInfo = {
  filename: string;
  bureau: string;
  pages?: number;
  chars?: number;
  status?: string;
  error?: string;
};

export type ScannerReviewItem = {
  id?: string;
  bureau?: string;
  source_filename?: string;
  account_name?: string;
  account_number_masked?: string;
  account_type?: string;
  portfolio_type?: string;
  responsibility?: string;
  creditor_classification?: string;
  original_creditor?: string;
  collector_or_debt_buyer?: string;
  status?: string;
  pay_status?: string;
  balance?: string;
  past_due?: string;
  high_credit_or_original_amount?: string;
  credit_limit?: string;
  date_opened?: string;
  date_closed?: string;
  date_reported?: string;
  date_last_activity?: string;
  date_last_payment?: string;
  date_of_first_delinquency?: string;
  estimated_removal_date?: string;
  remarks?: string;
  payment_history_summary?: string;
  raw_block?: string;
  page_start?: number;
  confidence?: 'high' | 'medium' | 'low';
  confidence_score?: number;
  needs_admin_review?: boolean;
};

export type ScannerIssue = {
  id: string;
  issue_type: string;
  severity: 'low' | 'medium' | 'high' | string;
  customer_label: string;
  customer_explanation: string;
  admin_explanation: string;
  suggested_round: string;
  related_tradeline_ids: string[];
  confidence: 'high' | 'medium' | 'low' | string;
};

export type ScannerParseResult = {
  job_id: string;
  files: ScannerFileInfo[];
  ai_second_pass: boolean;
  paid_ai_used?: boolean;
  status: {
    mode?: string;
    message?: string;
    [key: string]: unknown;
  };
  review_items_count: number;
  review_items_preview: ScannerReviewItem[];
  issues_count?: number;
  issues_preview?: ScannerIssue[];
  cross_bureau_groups?: unknown[];
  output_folder?: string;
  customer_message?: string;
  customer_summary?: {
    headline?: string;
    message?: string;
    review_items?: number;
    possible_review_points?: number;
    categories?: string[];
    next_step?: string;
  };
  admin_summary?: Record<string, unknown>;
};

const SCANNER_API_URL =
  process.env.NEXT_PUBLIC_SCANNER_API_URL ||
  process.env.NEXT_PUBLIC_CREDIT_VIVO_API_BASE_URL ||
  'http://localhost:8080';

export async function parseCreditReports(
  files: File[],
  useAiSecondPass = false
): Promise<ScannerParseResult> {
  const form = new FormData();

  for (const file of files) {
    form.append('files', file);
  }

  // v16 ignores this but keeps compatibility with older UI.
  form.append('use_ai_second_pass', String(useAiSecondPass));

  const response = await fetch(`${SCANNER_API_URL}/api/scanner/parse`, {
    method: 'POST',
    body: form,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Scanner request failed: ${response.status} ${text}`);
  }

  return response.json();
}

export async function getScannerResult(jobId: string): Promise<ScannerParseResult> {
  const response = await fetch(`${SCANNER_API_URL}/api/scanner/result/${jobId}`);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Scanner result failed: ${response.status} ${text}`);
  }

  return response.json();
}
