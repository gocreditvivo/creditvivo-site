# Credit Vivo Scanner

This workspace is the scanner-focused project for Credit Vivo. It contains the Python FastAPI scanner backend, parser engine, scanner docs, compliance notes, and project memory.

## Current Focus

- Scanner version: `18.1.7`
- Engine: Credit Vivo Proprietary Parser Engine
- API: FastAPI
- PDF extraction: `pypdf`
- AI policy: no paid AI API required
- Safety policy: no automatic disputes, letters, mail, or legal escalation
- Rules layer: Negative Account Rules Quick Reference + Metro 2/FCRA skills library
- Workbook contract: includes v9-style `Ours 3 Bureaus Comparison`, `Scanner_Skills_Map`, and `Negative_Account_Rules`

See `docs/scanner/SCANNER_REBUILD_COMBINED_FEATURES_V17.md` for the combined
old-build feature and skill blueprint used for the scanner rebuild.

## Project Memory

Read `docs/PROJECT_MEMORY.md` before scanner work. It records the current Credit Vivo context, scanner revision history, compliance rules, and the paused website build instructions.

## Main Folders

- `scanner_backend/` - active scanner API, parser engine, helper modules, and tests.
- `docs/scanner/` - scanner roadmap, API contract, parser notes, and proprietary engine docs.
- `docs/compliance/` - compliance requirements for scanner and credit repair claims.
- `docs/PROJECT_MEMORY.md` - shared Credit Vivo memory copied from the website repo.

## Local Run

```powershell
cd scanner_backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8080
```

Health check:

```text
http://localhost:8080/health
```

## Scanner Flow

1. Receive PDF credit report uploads.
2. Extract page text with `pypdf`.
3. Detect bureau where possible.
4. Parse tradelines and relevant report fields.
5. Detect review issues such as collections, charge-offs, missing dates, sold-account balance review, bureau mismatches, and low-confidence manual review.
6. Map findings to v18.1.7 decision-readiness situations such as auto loan, mortgage, apartment, collection, charge-off, late-payment, and bureau mismatch review.
7. Add workbook export QA flags so parser fragments are held for admin cleanup before customer-facing review.
8. Verify final output against the workbook template, raw parsed tradeline data, and scanner skills map before writing scanner files.
9. Match the visible `Ours 3 Bureaus Comparison` sheet to the v9 forensic workbook template.
10. Document backend skill areas in `Scanner_Skills_Map` for parser, QA, compliance, dispute prep, product workflow, letter lifecycle, and privacy review.
11. Apply the backend rules library for negative-account classification, Metro 2-style field mapping, FCRA review notes, e-OSCAR workflow awareness, and compliance guard language.
12. Return customer/admin summaries, issue previews, download metadata, workbook output, scanner skills map, and draft-only letter queues.

## Safety

Do not commit customer credit reports, SSNs, IDs, full account numbers, bureau credentials, API keys, `.env` files, or real customer documents.

Scanner output is draft review data only. Customer approval and admin review are required before any dispute, letter, mail, complaint, or escalation.
