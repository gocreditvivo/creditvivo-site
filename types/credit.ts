export type Bureau = 'TransUnion' | 'Experian' | 'Equifax' | 'Unknown';

export type ParsedTradeline = {
  bureau: Bureau;
  creditorName: string;
  accountNumberMasked?: string;
  accountType?: string;
  accountStatus?: string;
  balance?: string;
  pastDue?: string;
  dateOpened?: string;
  dateClosed?: string;
  dateReported?: string;
  lastPaymentDate?: string;
  chargeOffDate?: string;
  collectionDate?: string;
  originalCreditor?: string;
  collectionAgency?: string;
  creditorClassification?: string;
  paymentHistory?: string;
  remarks?: string;
  isNegative: boolean;
  negativeReason?: string;
  rawTextSnippet: string;
  confidenceScore: number;
};

export type CreditIssueType =
  | 'duplicate_account'
  | 'balance_mismatch'
  | 'status_mismatch'
  | 'date_mismatch'
  | 'missing_original_creditor'
  | 'bureau_mismatch'
  | 'collection_issue'
  | 'charge_off_issue'
  | 'incomplete_reporting'
  | 'possible_reaging'
  | 'needs_review';

export type RecommendedAction =
  | 'bureau_dispute'
  | 'furnisher_dispute'
  | 'debt_validation'
  | 'method_of_verification'
  | 'complaint_packet'
  | 'attorney_support'
  | 'admin_review';

export type CreditIssue = {
  issueType: CreditIssueType;
  plainEnglishFinding: string;
  supportingFields: Record<string, string>;
  bureausInvolved: Bureau[];
  disputeStrengthScore: number;
  recommendedAction: RecommendedAction;
};

export type BureauComparison = {
  normalizedAccountKey: string;
  transunionData?: ParsedTradeline;
  experianData?: ParsedTradeline;
  equifaxData?: ParsedTradeline;
  mismatches: Record<string, unknown>;
  issueSummary: string;
  confidenceScore: number;
};

export type ScannerSelfCheck = {
  inputQuality: 'pass' | 'review' | 'fail';
  bureauDetection: 'pass' | 'review' | 'fail';
  negativeTradelineCoverage: 'pass' | 'review' | 'fail';
  evidenceCoverage: 'pass' | 'review' | 'fail';
  overallStatus: 'ready_for_admin_review' | 'needs_parser_cleanup' | 'blocked';
  warnings: string[];
};
