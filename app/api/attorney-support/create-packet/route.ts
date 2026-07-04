import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const packet = {
      customerSummary: body.customerSummary || '',
      creditReportEvidence: body.creditReportEvidence || [],
      disputeHistory: body.disputeHistory || [],
      bureauResponses: body.bureauResponses || [],
      furnisherResponses: body.furnisherResponses || [],
      possibleIssueSummary: body.possibleIssueSummary || '',
      status: 'attorney_review_queue_preview',
      note: 'Attorney support is not automatic and is not guaranteed. This packet preview requires customer approval, admin review, and compliance review before any referral or next step.',
      customerApprovalRequired: true,
      adminReviewRequired: true,
      complianceReviewRequired: true,
      automaticEscalationAllowed: false,
    };
    return NextResponse.json({ ok: true, packet });
  } catch (error) {
    return NextResponse.json({ ok: false, error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
