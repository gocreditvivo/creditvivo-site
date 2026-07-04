import { NextRequest, NextResponse } from 'next/server';
import { buildDisputeParagraph } from '@/lib/cv-brain/disputeBuilder';
import type { CreditIssue } from '@/types/credit';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const issue = (await req.json()) as CreditIssue;
    if (!issue?.plainEnglishFinding) {
      return NextResponse.json({ error: 'Credit issue is required.' }, { status: 400 });
    }
    const letterParagraph = buildDisputeParagraph(issue);
    return NextResponse.json({
      ok: true,
      status: 'draft_only',
      letterParagraph,
      requiresCustomerApproval: true,
      requiresAdminReview: true,
      requiresComplianceReview: true,
      automaticSendAllowed: false,
      mailingAllowed: false,
    });
  } catch (error) {
    return NextResponse.json({ ok: false, error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
