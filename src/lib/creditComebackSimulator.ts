import type { ScannerParseResult, ScannerReviewItem } from './scannerApi';

export type ScoreImpactLevel = 'Low' | 'Medium' | 'High' | 'Very High';

export type ScoreProfile = {
  startingScore: number;
  currentScore: number;
  goalScore: number;
  source: 'Customer entered' | 'Uploaded report' | 'Demo estimate';
  lastUpdatedLabel: string;
};

export type CreditBlocker = {
  id: string;
  accountName: string;
  bureau: string;
  accountType: string;
  status: string;
  balance: string;
  reason: string;
  impactLevel: ScoreImpactLevel;
  possibleRange: [number, number];
  nextAction: 'Build dispute' | 'Review account' | 'Attorney Support' | 'Reduce utilization' | 'Upload document';
  supportingSignals: string[];
};

export type SimulatorScenario = {
  id: string;
  label: string;
  description: string;
  range: [number, number];
};

const DEFAULT_SCORE_PROFILE: ScoreProfile = {
  startingScore: 552,
  currentScore: 579,
  goalScore: 680,
  source: 'Demo estimate',
  lastUpdatedLabel: 'Demo view',
};

function lower(value?: string) {
  return (value || '').toLowerCase();
}

function combinedText(item: ScannerReviewItem) {
  return [
    item.account_name,
    item.account_type,
    item.status,
    item.pay_status,
    item.remarks,
    item.payment_history_summary,
    item.raw_block,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

function parseMoney(value?: string) {
  if (!value) return 0;
  const parsed = Number(value.replace(/[^0-9.-]/g, ''));
  return Number.isFinite(parsed) ? Math.max(0, parsed) : 0;
}

function hasLateSignal(text: string) {
  return /\b(30|60|90|120|150|180)\s*(day|days)?\s*late\b/.test(text) || text.includes('late payment');
}

function detectSignals(item: ScannerReviewItem) {
  const text = combinedText(item);
  const signals: string[] = [];

  if (text.includes('collection')) signals.push('Collection reporting');
  if (text.includes('charge') || text.includes('charged off') || text.includes('charge-off')) signals.push('Charge-off reporting');
  if (hasLateSignal(text)) signals.push('Late payment history');
  if (text.includes('past due')) signals.push('Past-due balance');
  if (text.includes('sold') || text.includes('transferred')) signals.push('Sold or transferred status');
  if (item.original_creditor) signals.push('Original creditor found');
  if (!item.original_creditor && text.includes('collection')) signals.push('Original creditor needs review');
  if (item.needs_admin_review) signals.push('Admin review flag');
  if ((item.confidence_score || 0) < 0.7) signals.push('Lower-confidence extraction');
  if (parseMoney(item.balance) > 0) signals.push('Reported balance');

  return signals;
}

function getSeverityScore(item: ScannerReviewItem) {
  const text = combinedText(item);
  let score = 0;

  if (text.includes('collection')) score += 32;
  if (text.includes('charge') || text.includes('charged off') || text.includes('charge-off')) score += 36;
  if (hasLateSignal(text)) score += 24;
  if (text.includes('past due')) score += 14;
  if (text.includes('bankruptcy') || text.includes('repossession') || text.includes('foreclosure')) score += 42;
  if (text.includes('sold') || text.includes('transferred')) score += 8;
  if (!item.original_creditor && text.includes('collection')) score += 10;
  if (item.needs_admin_review) score += 6;

  const balance = parseMoney(item.balance);
  if (balance >= 2500) score += 12;
  else if (balance >= 1000) score += 8;
  else if (balance > 0) score += 4;

  const bureau = lower(item.bureau);
  if (bureau.includes('experian') || bureau.includes('equifax') || bureau.includes('transunion')) score += 4;

  return Math.min(100, score);
}

function impactFromScore(score: number): { level: ScoreImpactLevel; range: [number, number] } {
  if (score >= 75) return { level: 'Very High', range: [35, 100] };
  if (score >= 52) return { level: 'High', range: [20, 60] };
  if (score >= 28) return { level: 'Medium', range: [10, 35] };
  return { level: 'Low', range: [0, 15] };
}

function nextActionFor(item: ScannerReviewItem, level: ScoreImpactLevel): CreditBlocker['nextAction'] {
  const text = combinedText(item);
  if (level === 'Very High' && (text.includes('charge') || text.includes('collection'))) return 'Attorney Support';
  if (text.includes('utilization') || text.includes('credit limit')) return 'Reduce utilization';
  if (item.needs_admin_review || (item.confidence_score || 0) < 0.7) return 'Review account';
  if (text.includes('collection') || text.includes('charge') || hasLateSignal(text)) return 'Build dispute';
  return 'Review account';
}

function reasonFor(_item: ScannerReviewItem, signals: string[]) {
  if (signals.includes('Collection reporting')) return 'This collection may be holding your score back.';
  if (signals.includes('Charge-off reporting')) return 'This charge-off may be a major credit blocker.';
  if (signals.includes('Late payment history')) return 'Late payments can strongly affect payment history.';
  if (signals.includes('Past-due balance')) return 'A past-due balance may be weighing down your profile.';
  return 'This item may need review before your next score move.';
}

export function buildCreditBlockers(result: ScannerParseResult | null): CreditBlocker[] {
  const items = result?.review_items_preview || [];

  return items
    .map((item, index) => {
      const severity = getSeverityScore(item);
      const impact = impactFromScore(severity);
      const signals = detectSignals(item);
      const accountName = item.account_name || `Review item ${index + 1}`;

      return {
        id: item.id || `blocker-${index}`,
        accountName,
        bureau: item.bureau || 'Bureau review',
        accountType: item.account_type || item.portfolio_type || 'Account review',
        status: item.status || item.pay_status || 'Needs review',
        balance: item.balance || item.past_due || 'Review',
        reason: reasonFor(item, signals),
        impactLevel: impact.level,
        possibleRange: impact.range,
        nextAction: nextActionFor(item, impact.level),
        supportingSignals: signals.slice(0, 4),
      } satisfies CreditBlocker;
    })
    .sort((a, b) => b.possibleRange[1] - a.possibleRange[1])
    .slice(0, 8);
}

function cappedScenarioRange(blockers: CreditBlocker[], multiplier = 1): [number, number] {
  if (!blockers.length) return [0, 0];

  const low = blockers.reduce((sum, item, index) => sum + item.possibleRange[0] * Math.max(0.35, 1 - index * 0.12), 0);
  const high = blockers.reduce((sum, item, index) => sum + item.possibleRange[1] * Math.max(0.3, 1 - index * 0.14), 0);

  return [Math.round(Math.min(75, low * multiplier)), Math.round(Math.min(120, high * multiplier))];
}

export function buildSimulatorScenarios(blockers: CreditBlocker[]): SimulatorScenario[] {
  const top = blockers[0] ? [blockers[0]] : [];
  const highImpact = blockers.filter((item) => item.impactLevel === 'High' || item.impactLevel === 'Very High');
  const collections = blockers.filter((item) => item.accountType.toLowerCase().includes('collection') || item.reason.toLowerCase().includes('collection'));

  return [
    {
      id: 'top-blocker',
      label: 'If your top blocker is corrected or removed',
      description: top[0]?.accountName || 'Start with the item most likely to matter first.',
      range: cappedScenarioRange(top),
    },
    {
      id: 'high-impact',
      label: 'If high-impact items are corrected',
      description: 'Focuses on the accounts Credit Vivo ranks as strongest score blockers.',
      range: cappedScenarioRange(highImpact.length ? highImpact : blockers.slice(0, 3), 1.05),
    },
    {
      id: 'collections',
      label: 'If selected collections are corrected',
      description: 'Models collection-related items from the scanner output.',
      range: cappedScenarioRange(collections.length ? collections : blockers.slice(0, 2), 0.9),
    },
    {
      id: 'comeback-path',
      label: 'Possible 100-point credit comeback path',
      description: 'Combines dispute progress, cleaner reporting, and score-focused next steps.',
      range: cappedScenarioRange(blockers.slice(0, 5), 1.15),
    },
  ];
}

export function getScoreProfile(result: ScannerParseResult | null): ScoreProfile {
  void result;
  // Phase 1: demo/customer-entered score profile.
  // Phase 2: replace this with score extraction from uploaded reports or a monitoring provider.
  return DEFAULT_SCORE_PROFILE;
}

export function getScoreProgress(profile: ScoreProfile) {
  const gained = Math.max(0, profile.currentScore - profile.startingScore);
  const targetGap = Math.max(1, profile.goalScore - profile.startingScore);
  const currentProgress = Math.min(100, Math.round((gained / targetGap) * 100));
  const remaining = Math.max(0, profile.goalScore - profile.currentScore);

  return { gained, currentProgress, remaining };
}
