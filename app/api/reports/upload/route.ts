import { NextRequest, NextResponse } from 'next/server';
import { runCreditVivoScan } from '@/lib/cv-brain';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get('content-type') || '';
    let rawText = '';
    let filename = '';

    if (contentType.includes('multipart/form-data')) {
      const form = await req.formData();
      const file = form.get('file');
      if (file instanceof File) {
        filename = file.name;
        if (file.type === 'text/plain' || filename.toLowerCase().endsWith('.txt')) {
          rawText = await file.text();
        } else {
          return NextResponse.json({
            ok: false,
            error: 'PDF upload should be processed by the approved FastAPI scanner backend before customer-facing findings are released.',
            backendRequired: true,
            allowedTestInput: 'Upload a .txt file with extracted report text for CV Brain route testing.',
          }, { status: 422 });
        }
      }
      rawText = rawText || String(form.get('rawText') || form.get('text') || '');
    } else {
      const body = await req.json();
      rawText = body.rawText || body.text || '';
    }

    if (!rawText || typeof rawText !== 'string') {
      return NextResponse.json({ error: 'rawText or a .txt file is required for this CV Brain route.' }, { status: 400 });
    }

    const result = await runCreditVivoScan(rawText);
    return NextResponse.json({
      ok: true,
      source: filename || 'raw_text',
      result,
      compliance: {
        draftReviewOnly: true,
        customerApprovalRequired: true,
        adminReviewRequired: true,
        complianceReviewRequired: true,
        automaticSendAllowed: false,
      },
    });
  } catch (error) {
    return NextResponse.json({ ok: false, error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
