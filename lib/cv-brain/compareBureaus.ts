import type { BureauComparison, ParsedTradeline } from '@/types/credit';
import { normalizedAccountKey } from './rules';

function mismatch(a?: string, b?: string, c?: string): boolean {
  const values = [a, b, c].filter(Boolean).map((v) => String(v).toLowerCase().trim());
  return new Set(values).size > 1;
}

export function compareBureaus(tradelines: ParsedTradeline[]): BureauComparison[] {
  const groups = new Map<string, ParsedTradeline[]>();

  for (const t of tradelines) {
    const key = normalizedAccountKey(t) || t.creditorName.toLowerCase();
    groups.set(key, [...(groups.get(key) || []), t]);
  }

  return Array.from(groups.entries()).map(([key, items]) => {
    const transunionData = items.find((i) => i.bureau === 'TransUnion');
    const experianData = items.find((i) => i.bureau === 'Experian');
    const equifaxData = items.find((i) => i.bureau === 'Equifax');

    const mismatches = {
      balance: mismatch(transunionData?.balance, experianData?.balance, equifaxData?.balance),
      status: mismatch(transunionData?.accountStatus, experianData?.accountStatus, equifaxData?.accountStatus),
      dateOpened: mismatch(transunionData?.dateOpened, experianData?.dateOpened, equifaxData?.dateOpened),
      dateReported: mismatch(transunionData?.dateReported, experianData?.dateReported, equifaxData?.dateReported),
      missingBureaus: ['TransUnion', 'Experian', 'Equifax'].filter(
        (b) => !items.some((i) => i.bureau === b)
      ),
    };

    const activeMismatchCount = Object.values(mismatches).filter((v) => Array.isArray(v) ? v.length > 0 : Boolean(v)).length;

    return {
      normalizedAccountKey: key,
      transunionData,
      experianData,
      equifaxData,
      mismatches,
      issueSummary: activeMismatchCount ? `${activeMismatchCount} bureau comparison issue(s) found.` : 'No bureau mismatch found.',
      confidenceScore: items.length >= 2 ? 0.82 : 0.6,
    };
  });
}
