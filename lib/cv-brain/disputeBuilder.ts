import type { CreditIssue } from '@/types/credit';

export function buildDisputeParagraph(issue: CreditIssue): string {
  return [
    `DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED`,
    `Credit Vivo identified a possible reporting issue for review: ${issue.plainEnglishFinding}`,
    `Please investigate the accuracy, completeness, and verification of the reported information, including the supporting fields listed with this draft.`,
    `If the information cannot be verified as accurate and complete, please correct it or delete the inaccurate reporting if appropriate.`,
    `This draft is not legal advice and is not sent automatically. Customer approval, admin review, and compliance review are required before any next step.`,
  ].join('\n\n');
}
