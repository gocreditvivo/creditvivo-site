import type { BureauComparison, CreditIssue, ParsedTradeline } from '@/types/credit';

export function detectIssues(tradelines: ParsedTradeline[], comparisons: BureauComparison[]): CreditIssue[] {
  const issues: CreditIssue[] = [];

  for (const t of tradelines.filter((x) => x.isNegative)) {
    if (/collection/i.test(`${t.accountType} ${t.remarks} ${t.negativeReason}`) && !t.originalCreditor) {
      issues.push({
        issueType: 'missing_original_creditor',
        plainEnglishFinding: `${t.creditorName} appears to be a collection account, but the original creditor information is missing or unclear.`,
        supportingFields: { creditorName: t.creditorName, bureau: t.bureau, rawTextSnippet: t.rawTextSnippet.slice(0, 250) },
        bureausInvolved: [t.bureau],
        disputeStrengthScore: 72,
        recommendedAction: 'bureau_dispute',
      });
    }

    if (t.confidenceScore < 0.75) {
      issues.push({
        issueType: 'needs_review',
        plainEnglishFinding: `${t.creditorName} needs admin review because the scanner confidence is low.`,
        supportingFields: { confidenceScore: String(t.confidenceScore), bureau: t.bureau },
        bureausInvolved: [t.bureau],
        disputeStrengthScore: 45,
        recommendedAction: 'admin_review',
      });
    }
  }

  for (const c of comparisons) {
    const bureaus = [c.transunionData?.bureau, c.experianData?.bureau, c.equifaxData?.bureau].filter(Boolean) as any;
    const m = c.mismatches as Record<string, any>;

    if (m.balance || m.status || m.dateOpened || m.dateReported) {
      issues.push({
        issueType: 'bureau_mismatch',
        plainEnglishFinding: `This account appears to report differently across the bureaus. Different balances, statuses, or dates may need review.`,
        supportingFields: {
          normalizedAccountKey: c.normalizedAccountKey,
          mismatches: JSON.stringify(c.mismatches),
        },
        bureausInvolved: bureaus,
        disputeStrengthScore: 78,
        recommendedAction: 'bureau_dispute',
      });
    }

    if (Array.isArray(m.missingBureaus) && m.missingBureaus.length > 0 && c.confidenceScore >= 0.75) {
      issues.push({
        issueType: 'incomplete_reporting',
        plainEnglishFinding: `This account may be missing from one or more bureaus, or the scanner may need review to confirm bureau coverage.`,
        supportingFields: { missingBureaus: m.missingBureaus.join(', ') },
        bureausInvolved: bureaus,
        disputeStrengthScore: 52,
        recommendedAction: 'admin_review',
      });
    }
  }

  return issues;
}
