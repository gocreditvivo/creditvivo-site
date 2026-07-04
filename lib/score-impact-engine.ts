import type { ParsedTradeline, CreditIssue } from '@/types/credit';
import type { ImpactEstimate, NegativeAccountType, ScannerNegativeAccount, ScenarioEstimate, ScoreImpactLevel, ScoreProfile, ScoreSummary } from '@/types/score-simulator';

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

function scoreBandMultiplier(currentScore: number): number {
  if (currentScore < 560) return 1.25;
  if (currentScore < 620) return 1.1;
  if (currentScore < 680) return 1.0;
  if (currentScore < 740) return 0.75;
  return 0.55;
}

function recencyMultiplier(recencyMonths?: number): number {
  if (recencyMonths === undefined || recencyMonths === null) return 1.0;
  if (recencyMonths <= 6) return 1.3;
  if (recencyMonths <= 24) return 1.1;
  if (recencyMonths <= 48) return 0.85;
  return 0.55;
}

function bureauMultiplier(account: ScannerNegativeAccount): number {
  const count = new Set(account.bureaus.filter((b) => b !== 'Unknown')).size;
  if (count >= 3) return 1.25;
  if (count === 2) return 1.1;
  return 1.0;
}

function baseImpactRange(account: ScannerNegativeAccount): [number, number] {
  switch (account.accountType) {
    case 'collection':
      return [10, 40];
    case 'charge_off':
      return [15, 50];
    case 'late_payment':
      if (account.severity === '120_plus_late' || account.severity === '90_late') return [15, 45];
      if (account.severity === '60_late') return [8, 25];
      return [3, 15];
    case 'repossession':
    case 'foreclosure':
    case 'bankruptcy':
      return [20, 65];
    case 'high_utilization': {
      if (!account.creditLimit || !account.balance) return [5, 25];
      const utilization = account.balance / account.creditLimit;
      if (utilization >= 0.9) return [20, 60];
      if (utilization >= 0.7) return [15, 45];
      if (utilization >= 0.5) return [10, 30];
      if (utilization >= 0.3) return [5, 18];
      return [0, 8];
    }
    case 'inquiry':
      return [0, 8];
    default:
      return [5, 20];
  }
}

function levelFromMax(max: number): ScoreImpactLevel {
  if (max >= 70) return 'very_high';
  if (max >= 40) return 'high';
  if (max >= 15) return 'medium';
  return 'low';
}

function nextAction(account: ScannerNegativeAccount): ImpactEstimate['nextAction'] {
  if ((account.disputeStrengthScore ?? 0) >= 80 && (account.possibleIssues?.length ?? 0) > 0) return 'build_dispute';
  if (account.accountType === 'high_utilization') return 'reduce_utilization';
  if ((account.disputeStrengthScore ?? 0) >= 70) return 'build_dispute';
  if (account.accountType === 'collection' && account.duplicateRisk) return 'build_dispute';
  if ((account.disputeStrengthScore ?? 0) < 45) return 'review';
  return 'upload_documents';
}

function labelNextAction(action: ImpactEstimate['nextAction']): string {
  switch (action) {
    case 'build_dispute':
      return 'Build a customer-approved dispute draft';
    case 'attorney_support':
      return 'Prepare for attorney-support review';
    case 'reduce_utilization':
      return 'Reduce utilization';
    case 'upload_documents':
      return 'Upload supporting documents';
    default:
      return 'Review account details';
  }
}

function explanationFor(account: ScannerNegativeAccount, min: number, max: number): string {
  const typeLabel = account.accountType.replaceAll('_', ' ');
  const bureauCount = new Set(account.bureaus.filter((b) => b !== 'Unknown')).size;
  const issues = account.possibleIssues?.length ? ` We also found: ${account.possibleIssues.join(', ')}.` : '';
  const duplicate = account.duplicateRisk ? ' This may be a duplicate reporting risk.' : '';
  return `${account.creditorName} is marked as a ${typeLabel}. It appears on ${bureauCount || 1} bureau(s), which may affect your score path. If the reporting is corrected, updated, or removed when appropriate, the estimated score movement range is +${min} to +${max} points.${duplicate}${issues}`;
}

export function estimateAccountImpact(account: ScannerNegativeAccount, profile: ScoreProfile): ImpactEstimate {
  const [baseMin, baseMax] = baseImpactRange(account);
  const multiplier = scoreBandMultiplier(profile.currentScore) * recencyMultiplier(account.recencyMonths) * bureauMultiplier(account);
  const disputeBoost = clamp((account.disputeStrengthScore ?? 50) / 100, 0.35, 1.1);
  const duplicateBoost = account.duplicateRisk ? 1.1 : 1;

  const possibleMin = Math.round(clamp(baseMin * multiplier * 0.75, 0, 110));
  const possibleMax = Math.round(clamp(baseMax * multiplier * duplicateBoost * disputeBoost, 3, 125));
  const priorityScore = Math.round(clamp(possibleMax * 1.2 + (account.disputeStrengthScore ?? 50) * 0.4, 1, 100));

  return {
    accountId: account.id,
    impactLevel: levelFromMax(possibleMax),
    possibleMin,
    possibleMax,
    priorityScore,
    explanation: explanationFor(account, possibleMin, possibleMax),
    nextAction: nextAction(account),
  };
}

export function estimateAllImpacts(accounts: ScannerNegativeAccount[], profile: ScoreProfile): ImpactEstimate[] {
  return accounts
    .map((account) => estimateAccountImpact(account, profile))
    .sort((a, b) => b.priorityScore - a.priorityScore);
}

export function estimateScenario(
  scenarioName: string,
  selectedAccountIds: string[],
  accounts: ScannerNegativeAccount[],
  profile: ScoreProfile,
): ScenarioEstimate {
  const impacts = estimateAllImpacts(accounts, profile).filter((impact) => selectedAccountIds.includes(impact.accountId));
  const rawMin = impacts.reduce((sum, impact) => sum + impact.possibleMin, 0);
  const rawMax = impacts.reduce((sum, impact) => sum + impact.possibleMax, 0);

  // Diminishing returns: multiple items can overlap in scoring impact.
  const itemCount = Math.max(impacts.length, 1);
  const reduction = itemCount > 1 ? 0.72 : 1;
  const possibleMin = Math.round(clamp(rawMin * reduction, 0, 125));
  const possibleMax = Math.round(clamp(rawMax * reduction, 5, 150));

  return {
    scenarioName,
    selectedAccountIds,
    possibleMin,
    possibleMax,
    headline: possibleMax >= 90 ? 'Possible 100-point credit comeback path' : 'Possible score impact',
    explanation:
      possibleMax >= 90
        ? `If these selected items are corrected, updated, or removed when appropriate, this profile may have a path toward a possible 100-point credit comeback. This is an estimate, not a guarantee.`
        : `If these selected items are corrected, updated, or removed when appropriate, the score may have room to move by an estimated +${possibleMin} to +${possibleMax} points. This is not a guarantee.`,
  };
}

export function estimateUtilizationScenario(accounts: ScannerNegativeAccount[], profile: ScoreProfile): ScenarioEstimate | undefined {
  const utilizationAccounts = accounts.filter((account) => account.accountType === 'high_utilization');
  if (!utilizationAccounts.length) return undefined;

  const selectedIds = utilizationAccounts.map((account) => account.id);
  const base = estimateScenario('Utilization below 30%', selectedIds, accounts, profile);

  return {
    ...base,
    headline: 'What if utilization drops below 30%?',
    explanation:
      'Lower revolving utilization can be one of the clearer score factors to improve. This estimate assumes balances are reduced and reporting updates after the statement cycle.',
  };
}

export function buildScoreSummary(profile: ScoreProfile, accounts: ScannerNegativeAccount[]): ScoreSummary {
  const impacts = estimateAllImpacts(accounts, profile);
  const top = impacts.slice(0, 5);
  const allScenario = estimateScenario('Resolve all selected high-impact blockers', top.map((i) => i.accountId), accounts, profile);
  const scoreGap = Math.max(profile.goalScore - profile.currentScore, 0);

  return {
    scoreGap,
    scoreMovement: profile.currentScore - profile.startingScore,
    topCreditBlockers: top,
    possibleComeback: allScenario,
    utilizationScenario: estimateUtilizationScenario(accounts, profile),
  };
}

export function describeNextAction(action: ImpactEstimate['nextAction']): string {
  return labelNextAction(action);
}

function parseMoney(value?: string): number | undefined {
  if (!value) return undefined;
  const parsed = Number(value.replace(/[^0-9.-]/g, ''));
  return Number.isFinite(parsed) ? parsed : undefined;
}

function accountTypeFromTradeline(tradeline: ParsedTradeline): NegativeAccountType {
  const text = `${tradeline.accountType || ''} ${tradeline.accountStatus || ''} ${tradeline.negativeReason || ''} ${tradeline.remarks || ''}`.toLowerCase();
  if (text.includes('charge')) return 'charge_off';
  if (text.includes('collection')) return 'collection';
  if (text.includes('repo')) return 'repossession';
  if (text.includes('foreclosure')) return 'foreclosure';
  if (text.includes('bankruptcy')) return 'bankruptcy';
  if (text.includes('late') || text.includes('past due')) return 'late_payment';
  return 'unknown_negative';
}

function severityFromTradeline(tradeline: ParsedTradeline): ScannerNegativeAccount['severity'] {
  const text = `${tradeline.paymentHistory || ''} ${tradeline.accountStatus || ''} ${tradeline.negativeReason || ''}`.toLowerCase();
  if (/120|150|180/.test(text)) return '120_plus_late';
  if (/90/.test(text)) return '90_late';
  if (/60/.test(text)) return '60_late';
  if (/30/.test(text)) return '30_late';
  if (text.includes('charge')) return 'charge_off';
  if (text.includes('collection')) return 'collection';
  if (tradeline.isNegative) return 'major_derogatory';
  return undefined;
}

export function scannerTradelinesToSimulatorAccounts(
  tradelines: ParsedTradeline[],
  issues: CreditIssue[] = [],
): ScannerNegativeAccount[] {
  return tradelines
    .filter((tradeline) => tradeline.isNegative)
    .map((tradeline, index) => {
      const matchingIssues = issues.filter((issue) => {
        const creditor = issue.supportingFields?.creditorName || issue.supportingFields?.account || '';
        return creditor && tradeline.creditorName.toLowerCase().includes(creditor.toLowerCase());
      });

      return {
        id: `${tradeline.bureau}-${tradeline.creditorName}-${index}`.replace(/[^a-z0-9_-]+/gi, '-').toLowerCase(),
        creditorName: tradeline.creditorName,
        accountType: accountTypeFromTradeline(tradeline),
        bureaus: [tradeline.bureau],
        balance: parseMoney(tradeline.balance),
        status: tradeline.accountStatus,
        dateReported: tradeline.dateReported,
        dateOpened: tradeline.dateOpened,
        lastPaymentDate: tradeline.lastPaymentDate,
        severity: severityFromTradeline(tradeline),
        disputeStrengthScore: matchingIssues[0]?.disputeStrengthScore ?? Math.round((tradeline.confidenceScore || 0.55) * 100),
        duplicateRisk: matchingIssues.some((issue) => issue.issueType === 'duplicate_account'),
        possibleIssues: [
          tradeline.negativeReason ? `possible ${tradeline.negativeReason}` : 'possible negative reporting',
          ...matchingIssues.map((issue) => issue.plainEnglishFinding),
        ].filter(Boolean),
      };
    });
}
