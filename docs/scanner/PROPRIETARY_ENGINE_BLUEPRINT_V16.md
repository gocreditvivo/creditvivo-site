# Credit Vivo Proprietary Parser Engine v16 Blueprint

## Purpose

Build Credit Vivo's own parser/scanner engine that can become a true proprietary asset.

## What makes it ours

The value is not a generic PDF reader. The value is the Credit Vivo credit-report workflow:

1. Bureau detection
2. Page evidence capture
3. Account block segmentation
4. Normalized tradeline schema
5. Negative item review categories
6. Credit Vivo confidence scoring
7. Cross-bureau account matching
8. Customer-friendly explanations
9. Admin review output
10. Dispute/mail-out workflow integration

## Engine files

- `scanner_backend/credit_vivo_proprietary_engine.py`
- `scanner_backend/main.py`
- `src/lib/scannerApi.ts`

## Proprietary modules added

### 1. Normalized tradeline schema
Captures:
- Bureau
- Source file
- Account name
- Masked account number
- Account type
- Portfolio type
- Responsibility
- Creditor classification
- Original creditor
- Collector/debt buyer
- Status / pay status
- Balance / past due
- Dates
- Remarks
- Raw evidence block
- Confidence score

### 2. Issue detection engine
Flags review categories:
- Collection review
- Charge-off review
- Missing important date review
- Closed/sold balance review
- Cross-bureau balance mismatch
- Cross-bureau status mismatch
- Cross-bureau date mismatch
- Low-confidence admin review

### 3. Cross-bureau matching
Groups similar accounts across Experian, Equifax, and TransUnion using Credit Vivo's own no-dependency similarity logic.

### 4. Evidence-based output
Each issue includes:
- Related tradeline IDs
- Bureau
- Page number if available
- Raw snippet
- Suggested round
- Customer explanation
- Admin explanation

## No paid AI

This version does not require:
- Anthropic
- Claude
- OpenAI
- paid OCR
- PyMuPDF

## Third-party components

Still uses:
- FastAPI for API service
- pypdf for PDF text extraction

These are not the proprietary part. Credit Vivo's native engine is the proprietary part.
