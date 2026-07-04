import type { ParsedTradeline } from '@/types/credit';

export const NEGATIVE_KEYWORDS = [
  'collection',
  'collections',
  'collection account',
  'debt buyer',
  'assigned to collection',
  'charged off',
  'charge-off',
  'charge off',
  'chargeoff',
  'charged to profit and loss',
  'profit and loss',
  'write off',
  'written off',
  'past due',
  'amount past due',
  'derogatory',
  'major derogatory',
  'potentially negative',
  'adverse',
  'late',
  'delinquent',
  'delinquency',
  'repossession',
  'reposessed',
  'repo',
  'foreclosure',
  'bankruptcy',
  'included in bankruptcy',
  'chapter 7',
  'chapter 13',
  'settled',
  'settled for less',
  'placed for collection',
  'transferred to collection',
  'transferred/sold',
  'sold to',
  'purchased by another lender',
  'account closed by credit grantor',
  '30 days late',
  '60 days late',
  '90 days late',
  '120 days late',
  '150 days late',
  '180 days late',
  '30 days past due',
  '60 days past due',
  '90 days past due',
  '120 days past due',
  '150 days past due',
  '180 days past due',
];

export const BUREAU_MARKERS = {
  TransUnion: ['transunion', 'trans union', 'tuc'],
  Experian: ['experian', 'xp/efx', 'experian credit report'],
  Equifax: ['equifax', 'efx', 'equifax information services'],
} as const;

export function isNegativeTradeline(blockText: string): { isNegative: boolean; reason?: string } {
  const lower = blockText.toLowerCase();
  const match = NEGATIVE_KEYWORDS.find((keyword) => lower.includes(keyword));
  if (!match && /\b(?:30|60|90|120|150|180)\s*(?:day|days)\s*(?:late|past due)\b/i.test(blockText)) {
    return { isNegative: true, reason: 'late payment signal' };
  }
  return match ? { isNegative: true, reason: match } : { isNegative: false };
}

export function requiresAdminReview(tradeline: ParsedTradeline): boolean {
  if (tradeline.confidenceScore < 0.75) return true;
  if (tradeline.bureau === 'Unknown') return true;
  if (tradeline.isNegative && !tradeline.rawTextSnippet) return true;
  if (tradeline.isNegative && /collection/i.test(`${tradeline.accountType} ${tradeline.remarks} ${tradeline.negativeReason}`) && !tradeline.originalCreditor) return true;
  return false;
}

export function normalizeCreditorName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\b(inc|llc|corp|corporation|company|co|bank|na)\b/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function normalizedAccountKey(t: ParsedTradeline): string {
  const creditor = normalizeCreditorName(t.creditorName || 'unknown');
  const acct = (t.accountNumberMasked || '').replace(/[^0-9xX*]/g, '').slice(-4);
  const opened = t.dateOpened || '';
  return [creditor, acct, opened].filter(Boolean).join('|');
}
