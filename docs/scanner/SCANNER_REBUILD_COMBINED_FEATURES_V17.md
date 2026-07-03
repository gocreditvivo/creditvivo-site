# Credit Vivo Scanner Rebuild - Combined Feature Blueprint v17

This blueprint combines the useful scanner features from the older v12.9,
v15.3, v16, v17, and v16-to-v20 roadmap builds before further build work.

## Rebuild Goal

Rebuild the scanner as a Credit Vivo-owned credit report review engine that
does not depend on paid AI APIs, keeps the existing frontend API contract, and
produces customer-friendly plus admin-ready review artifacts.

The scanner must stay draft-only. It may organize findings, evidence, letters,
and next steps, but it must not send disputes, letters, mail, complaints, legal
escalations, or customer communications automatically.

## Combined Old Build Features

### v12.9 integration layer

- FastAPI scanner backend adapter.
- Frontend-compatible `/api/scanner/parse` contract.
- Backward-compatible `use_ai_second_pass` form field.
- Draft review output only.
- Customer approval and admin review required before action.

### v15.3 no-paid-AI parser

- Removed Anthropic/Claude dependency.
- Removed `ANTHROPIC_API_KEY`.
- Removed PyMuPDF dependency.
- Added native Credit Vivo rule-based parser.
- Uses `pypdf` for PDF text extraction.
- Preserves approved website layout expectations.

### v16 proprietary engine

- Normalized tradeline schema.
- Bureau detection.
- Page/evidence snippets.
- Account block segmentation.
- Confidence scoring.
- Cross-bureau account grouping.
- Issue detection engine.
- Customer-friendly summaries.
- Admin-ready review output.
- CSV and JSON outputs.
- Desktop workbook output.

### v17 decision-readiness layer

- Maps findings to real customer situations:
  - Auto loan or refinance review.
  - Mortgage readiness.
  - Apartment application review.
  - Collection account review.
  - Charge-off or late-payment review.
  - Bureau mismatch review.
- Clear customer next steps without promising approvals, removals, score
  increases, or legal outcomes.

### v18-v20 roadmap features to preserve as extension points

- Creditor alias intelligence.
- Debt buyer and collector classification.
- Original creditor normalization.
- Bureau-specific extractors for Experian, Equifax, TransUnion, IdentityIQ,
  SmartCredit, and AnnualCreditReport-style layouts.
- Admin correction capture.
- Pattern improvement queue.
- Regression tests from corrected samples.
- Accuracy dashboard.
- Full 3-bureau side-by-side comparison.
- Customer roadmap automation.
- Response analysis.
- Compliance audit logs.

## Combined Scanner Skills

- PDF upload validation: file count, file type, file size, temporary storage,
  raw text retention controls, and upload deletion controls.
- Text extraction: page-by-page `pypdf` extraction with page markers.
- Bureau detection: Experian, Equifax, TransUnion, or unknown report fallback.
- Tradeline parsing: account name, masked account number, type, responsibility,
  status, pay status, balance, past due, credit limit, high credit/original
  amount, dates, remarks, original creditor, collector/debt buyer, and raw
  evidence block.
- Negative item detection: collection, charge-off, late payment, sold or
  transferred account, missing dates, low confidence, and manual review flags.
- Cross-bureau comparison: matching accounts across bureaus and detecting
  balance, status, and date mismatches.
- Date review: date extraction audit, missing date review, DOFD review, date
  mismatch review, and estimated removal date review.
- Customer output: plain-English summary, issue previews, decision-readiness
  cards, and approval-required notice.
- Admin output: evidence snippets, confidence scores, issue categories,
  suggested review rounds, and full parser JSON.
- Desktop output: workbook, tradelines CSV, review issues CSV, dates audit CSV,
  draft letters TXT, and summary JSON.
- Compliance output: FCRA review, Metro 2 field review, field compliance audit,
  FCRA rights/regulator references, bureau/FDCPA reference, e-OSCAR packaging
  review, dispute methods, and dispute SOP.
- Letter workflow: draft-only bureau dispute, furnisher dispute, and debt
  validation queues with customer approval required.
- Growth and operations helpers: lead capture, event collector, growth brief,
  operator brief, Vivo command brief, admin setup user provisioning, and
  outreach planning with owner approval gates.

## API Surface To Preserve

- `GET /health`
- `GET /api/health`
- `POST /scanner/parse`
- `POST /api/scanner/parse`
- `GET /scanner/result/{job_id}`
- `GET /api/scanner/result/{job_id}`
- `GET /scanner/result/{job_id}/full`
- `GET /api/scanner/result/{job_id}/full`
- `GET /scanner/result/{job_id}/download/{download_name}`
- `GET /api/scanner/result/{job_id}/download/{download_name}`

Downloads to preserve:

- `workbook.xlsx`
- `issues.csv`
- `tradelines.csv`
- `letters.txt`

## Safety And Compliance Controls

- No paid AI API is required.
- No Anthropic, Claude, OpenAI, paid OCR, or PyMuPDF dependency is required.
- No automatic dispute sending.
- No automatic letter mailing.
- No automatic legal escalation.
- No guaranteed removals, score increases, approvals, or outcomes.
- Accurate, current, and verifiable information may remain.
- Customer approval and admin review are required before any dispute or letter.
- Raw customer PDFs, SSNs, IDs, full account numbers, credentials, API keys, and
  real customer documents must not be committed.
- Production hosts should use HTTPS, restrictive CORS, private storage, and
  minimal retention.

## Rebuild Acceptance Criteria

- Health response reports version `17.0`, no paid AI, no Anthropic requirement,
  no PyMuPDF requirement, and `pypdf` as the PDF text engine.
- Parser returns tradelines, issues, cross-bureau groups, customer summary,
  admin summary, decision-readiness cards, draft letter workflow, and download
  metadata.
- Workbook output is generated in deployed environments.
- Tests pass using a stable Python 3.12 runtime.
- API remains compatible with the existing Bolt/Vite scanner client.
- Scanner output remains draft review data only.

