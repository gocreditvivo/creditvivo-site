import type { ParsedTradeline, Bureau } from '@/types/credit';
import { isNegativeTradeline } from './rules';

const ACCOUNT_SPLIT_PATTERNS = [
  /\n(?=Account Name:)/gi,
  /\n(?=Account Information)/gi,
  /\n(?=Creditor Name:)/gi,
  /\n(?=Company Name:)/gi,
  /\n(?=Collection Agency)/gi,
  /\n(?=Original Creditor)/gi,
  /\n(?=Tradeline)/gi,
  /\n(?=[A-Z0-9& .,'/-]{4,80}\n(?:Account|Balance|Status|Date|Type|Original Creditor|Past Due))/g,
];

const BUREAU_SECTION_PATTERN = /(?=(?:^|\n)(?:Experian|Equifax|TransUnion|Trans Union)\s+Credit Report)/gi;

function pick(pattern: RegExp, text: string): string | undefined {
  const match = text.match(pattern);
  return match?.[1]?.trim();
}

function detectBureauInBlock(text: string, fallback: Bureau): Bureau {
  const lower = text.toLowerCase();
  if (lower.includes('transunion') || lower.includes('trans union')) return 'TransUnion';
  if (lower.includes('experian')) return 'Experian';
  if (lower.includes('equifax')) return 'Equifax';
  return fallback;
}

export function splitTradelineBlocks(rawText: string): string[] {
  let blocks = [rawText];
  for (const pattern of ACCOUNT_SPLIT_PATTERNS) {
    blocks = blocks.flatMap((b) => b.split(pattern));
  }
  return blocks
    .map((b) => b.trim())
    .filter((b) => b.length > 80)
    .filter((b) => /(account|balance|opened|reported|status|collection|charge|late|creditor|past due|derogatory|bankruptcy|repossession|foreclosure)/i.test(b));
}

function splitBureauSections(rawText: string, fallbackBureau: Bureau): Array<{ bureau: Bureau; text: string }> {
  const sections = rawText
    .split(BUREAU_SECTION_PATTERN)
    .map((text) => text.trim())
    .filter(Boolean);

  const usableSections = sections.length ? sections : [rawText];
  return usableSections.map((text) => ({
    bureau: detectBureauInBlock(text, fallbackBureau),
    text,
  }));
}

export function parseTradelines(rawText: string, fallbackBureau: Bureau = 'Unknown'): ParsedTradeline[] {
  return splitBureauSections(rawText, fallbackBureau).flatMap(({ bureau, text }) => splitTradelineBlocks(text).map((block) => {
    const negative = isNegativeTradeline(block);
    const creditorName =
      pick(/(?:Account Name|Creditor Name|Company)\s*:?\s*([^\n]+)/i, block) ||
      pick(/^([^\n]{3,80})/i, block) ||
      'Unknown Creditor';

    return {
      bureau: detectBureauInBlock(block, bureau),
      creditorName,
      accountNumberMasked: pick(/(?:Account\s*(?:#|Number)|Acct\s*(?:#|Number))\s*:?\s*([^\n]+)/i, block),
      accountType: pick(/(?:Account Type|Type)\s*:?\s*([^\n]+)/i, block),
      accountStatus: pick(/(?:Status|Account Status)\s*:?\s*([^\n]+)/i, block),
      balance: pick(/(?:Balance|Current Balance)\s*:?\s*([^\n]+)/i, block),
      pastDue: pick(/(?:Past Due|Amount Past Due)\s*:?\s*([^\n]+)/i, block),
      dateOpened: pick(/(?:Date Opened|Opened)\s*:?\s*([^\n]+)/i, block),
      dateClosed: pick(/(?:Date Closed|Closed)\s*:?\s*([^\n]+)/i, block),
      dateReported: pick(/(?:Date Reported|Reported|Last Reported)\s*:?\s*([^\n]+)/i, block),
      lastPaymentDate: pick(/(?:Last Payment|Date of Last Payment)\s*:?\s*([^\n]+)/i, block),
      chargeOffDate: pick(/(?:Charge Off Date|Charged Off)\s*:?\s*([^\n]+)/i, block),
      collectionDate: pick(/(?:Collection Date|Date Assigned|Assigned)\s*:?\s*([^\n]+)/i, block),
      originalCreditor: pick(/(?:Original Creditor|Original Lender)\s*:?\s*([^\n]+)/i, block),
      collectionAgency: pick(/(?:Collection Agency|Collector)\s*:?\s*([^\n]+)/i, block),
      creditorClassification: pick(/(?:Creditor Classification|Classification)\s*:?\s*([^\n]+)/i, block),
      paymentHistory: pick(/(?:Payment History|History)\s*:?\s*([^\n]+)/i, block),
      remarks: pick(/(?:Remarks|Comments)\s*:?\s*([^\n]+)/i, block),
      isNegative: negative.isNegative,
      negativeReason: negative.reason,
      rawTextSnippet: block.slice(0, 1200),
      confidenceScore: creditorName === 'Unknown Creditor' ? 0.55 : negative.isNegative ? 0.82 : 0.78,
    };
  }));
}
