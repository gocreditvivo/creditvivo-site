import { detectBureaus } from './bureauDetection';
import { parseTradelines } from './tradelineParser';
import { compareBureaus } from './compareBureaus';
import { detectIssues } from './issueDetection';
import type { ScannerSelfCheck } from '@/types/credit';

function buildSelfCheck(rawText: string, result: {
  bureauResult: ReturnType<typeof detectBureaus>;
  tradelines: ReturnType<typeof parseTradelines>;
  negativeTradelines: ReturnType<typeof parseTradelines>;
}): ScannerSelfCheck {
  const warnings: string[] = [];
  const inputQuality = rawText.length >= 500 ? 'pass' : rawText.length >= 120 ? 'review' : 'fail';
  if (inputQuality !== 'pass') warnings.push('Raw text is short. PDF extraction or OCR may be incomplete.');

  const bureauDetection = result.bureauResult.detectedBureaus.includes('Unknown') ? 'review' : 'pass';
  if (bureauDetection !== 'pass') warnings.push('Bureau detection is uncertain. Admin review required.');

  const negativeTradelineCoverage = result.negativeTradelines.length > 0 ? 'pass' : 'review';
  if (negativeTradelineCoverage !== 'pass') warnings.push('No negative tradelines detected. Compare manually against the source report before trusting output.');

  const missingEvidence = result.negativeTradelines.some((t) => !t.rawTextSnippet || t.rawTextSnippet.length < 40);
  const evidenceCoverage = missingEvidence ? 'fail' : result.negativeTradelines.length ? 'pass' : 'review';
  if (evidenceCoverage !== 'pass') warnings.push('One or more negative findings lacks enough raw evidence snippet support.');

  const overallStatus =
    inputQuality === 'fail' || evidenceCoverage === 'fail'
      ? 'blocked'
      : warnings.length
        ? 'needs_parser_cleanup'
        : 'ready_for_admin_review';

  return {
    inputQuality,
    bureauDetection,
    negativeTradelineCoverage,
    evidenceCoverage,
    overallStatus,
    warnings,
  };
}

export async function runCreditVivoScan(rawText: string) {
  const bureauResult = detectBureaus(rawText);
  const fallbackBureau = bureauResult.detectedBureaus.length === 1 ? bureauResult.detectedBureaus[0] : 'Unknown';
  const tradelines = parseTradelines(rawText, fallbackBureau);
  const negativeTradelines = tradelines.filter((t) => t.isNegative);
  const comparisons = compareBureaus(tradelines);
  const issues = detectIssues(negativeTradelines, comparisons);

  const baseResult = {
    bureauResult,
    tradelines,
    negativeTradelines,
    comparisons,
    issues,
    summary: {
      totalTradelines: tradelines.length,
      negativeTradelines: negativeTradelines.length,
      issuesFound: issues.length,
      needsAdminReview: issues.filter((i) => i.recommendedAction === 'admin_review').length,
    },
  };

  return {
    ...baseResult,
    selfCheck: buildSelfCheck(rawText, baseResult),
    compliance: {
      draftReviewOnly: true,
      customerApprovalRequired: true,
      adminReviewRequired: true,
      complianceReviewRequired: true,
      automaticSendAllowed: false,
      legalAdviceProvided: false,
    },
  };
}
