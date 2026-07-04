export type ScoreSource = 'FICO' | 'VantageScore' | 'Experian' | 'Equifax' | 'TransUnion' | 'UserEntered' | 'Unknown';

export type NegativeAccountType =
  | 'collection'
  | 'charge_off'
  | 'late_payment'
  | 'repossession'
  | 'foreclosure'
  | 'bankruptcy'
  | 'high_utilization'
  | 'inquiry'
  | 'unknown_negative';

export type Bureau = 'Experian' | 'Equifax' | 'TransUnion' | 'Unknown';

export type ScoreImpactLevel = 'low' | 'medium' | 'high' | 'very_high';

export type ScannerNegativeAccount = {
  id: string;
  creditorName: string;
  accountType: NegativeAccountType;
  bureaus: Bureau[];
  balance?: number;
  creditLimit?: number;
  status?: string;
  dateReported?: string;
  dateOpened?: string;
  lastPaymentDate?: string;
  severity?: '30_late' | '60_late' | '90_late' | '120_plus_late' | 'collection' | 'charge_off' | 'major_derogatory';
  recencyMonths?: number;
  duplicateRisk?: boolean;
  disputeStrengthScore?: number; // 0-100 from scanner/CV Brain
  possibleIssues?: string[];
};

export type ScoreProfile = {
  startingScore: number;
  currentScore: number;
  goalScore: number;
  scoreSource: ScoreSource;
  goalReason?: 'car' | 'home' | 'apartment' | 'credit_card' | 'insurance' | 'business_funding' | 'other';
};

export type ImpactEstimate = {
  accountId: string;
  impactLevel: ScoreImpactLevel;
  possibleMin: number;
  possibleMax: number;
  priorityScore: number;
  explanation: string;
  nextAction: 'build_dispute' | 'review' | 'attorney_support' | 'reduce_utilization' | 'upload_documents';
};

export type ScenarioEstimate = {
  scenarioName: string;
  selectedAccountIds: string[];
  possibleMin: number;
  possibleMax: number;
  headline: string;
  explanation: string;
};

export type ScoreSummary = {
  scoreGap: number;
  scoreMovement: number;
  topCreditBlockers: ImpactEstimate[];
  possibleComeback: ScenarioEstimate;
  utilizationScenario?: ScenarioEstimate;
};
