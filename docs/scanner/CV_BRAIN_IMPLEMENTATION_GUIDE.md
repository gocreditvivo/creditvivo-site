# Credit Vivo Scanner + CV Brain Implementation Guide

Integrated into this workspace on 2026-07-04.

## Current Integration Status

- `lib/cv-brain/` is integrated as a TypeScript intelligence layer for extracted text.
- `types/credit.ts` is integrated for shared scanner response types.
- `app/api/reports/*` routes are integrated for extracted-text scanner tests.
- `app/api/disputes/generate` returns draft-only letter text.
- `app/api/attorney-support/create-packet` returns an attorney-review queue preview only.
- `supabase/schema.sql` is included, with approval and no-auto-send fields.
- `/member/upload` includes a CV Brain extracted-text test panel.

The existing Python FastAPI proprietary scanner remains the production parser authority for real PDF reports, workbook export, and v18.1.7 backend output.

## Current package contents

- `lib/cv-brain/` — scanner rules, bureau detection, tradeline parsing, bureau comparison, issue detection, dispute paragraph generation.
- `types/credit.ts` — shared TypeScript types.
- `supabase/schema.sql` — database schema.
- `app/api/.../route.ts` — starter Next.js API route examples.

## Install into existing Next.js project

1. Copy `lib/cv-brain` into your project `lib/` folder.
2. Copy `types/credit.ts` into your project `types/` folder.
3. Copy API route folders into your `app/api/` folder.
4. Run `supabase/schema.sql` in Supabase SQL editor.
5. Connect routes to Supabase insert/update logic.
6. Replace starter raw text input with real PDF/OCR extraction.

## Scanner rule

If a human can see a negative tradeline on the credit report, Credit Vivo must catch it.

Operational version of this rule:

1. Run a real or synthetic report through the scanner.
2. Create a gold-standard manual answer sheet listing every visible negative tradeline.
3. Compare scanner output against that manual answer sheet.
4. Fix every missed negative tradeline before moving to the next feature.
5. Do not release customer-facing findings until ground-truth and admin QA pass.

## Build next

- Add real PDF text extraction.
- Add OCR fallback.
- Add Supabase persistence.
- Add dashboard screens for AI Findings, Negative Accounts, 3-Bureau Comparison, Dispute Builder, Progress Tracker, and Admin Review Queue.
- Create gold-standard test reports and expected outputs.

## Compliance guardrails

- Scanner output is draft review data only.
- No disputes, letters, mail, complaints, or legal escalation are sent automatically.
- Customer approval, admin review, and compliance review are required before any action.
- Use safe language such as possible report errors, plain-English review, documented next steps, customer-approved dispute prep, and results vary.
- Do not claim guaranteed removals, guaranteed score increases, guaranteed approvals, legal violation proven, or attorney support guaranteed.

## Production architecture

- Vercel hosts the Next.js frontend and extracted-text CV Brain API tests.
- The Python FastAPI scanner backend should handle real PDF extraction, workbook generation, and production scanner jobs.
- Supabase schema must be run in the Supabase SQL editor or migration system before database persistence is live.
- Real customer reports must use encrypted storage, role-based access, and audit logs before launch.

## Test command idea

Send raw report text to:

`POST /api/reports/parse-tradelines`

Body:

```json
{ "rawText": "paste extracted credit report text here" }
```

Expected output:

- bureauResult
- all tradelines
- negative tradelines
- bureau comparisons
- credit issues
- summary
