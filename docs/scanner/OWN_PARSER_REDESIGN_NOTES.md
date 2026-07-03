# Credit Vivo Own Parser Redesign Notes

## Goal

Make the parser more Credit Vivo-owned and reduce outside paid/proprietary dependency.

## What changed

1. Removed Anthropic/Claude dependency.
2. Removed PyMuPDF dependency.
3. Added `credit_vivo_native_parser.py`.
4. Parser now uses Credit Vivo's own rule-based:
   - bureau detection
   - block segmentation
   - negative-term detection
   - field extraction
   - category assignment
   - confidence scoring
   - bureau match notes
5. Kept API contract compatible with the Bolt frontend.

## What remains third-party

The API and PDF text layer still use permissive open-source tools:
- FastAPI
- pypdf

These do not require paid API keys, but license notices should remain.

## Tradeoff

Removing AI API support lowers cost and avoids relying on Anthropic, but messy scanned/image PDFs may parse less accurately. Future Credit Vivo proprietary improvement should focus on:
- stronger bureau-specific templates
- page-coordinate extraction if using a permissive library
- more report samples
- regression tests
- admin correction feedback loop
