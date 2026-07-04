import { NextRequest, NextResponse } from 'next/server';
import { runCreditVivoScan } from '@/lib/cv-brain';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const rawText = body.rawText || body.text || '';

    if (!rawText || typeof rawText !== 'string') {
      return NextResponse.json({ error: 'rawText is required for this starter route.' }, { status: 400 });
    }

    const result = await runCreditVivoScan(rawText);
    return NextResponse.json({
      ok: true,
      result,
      note: 'This route accepts already-extracted text. Production PDF extraction remains in the FastAPI scanner backend.',
    });
  } catch (error) {
    return NextResponse.json({ ok: false, error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
