# Credit Vivo Parser/Scanner v15.3 — Proprietary / No Paid AI

## Purpose

This update redesigns the parser integration so Credit Vivo does not need Anthropic/Claude or PyMuPDF.

## Removed

- Anthropic Claude API connector
- `ANTHROPIC_API_KEY`
- PyMuPDF dependency
- Paid AI second-pass requirement

## Added

- Credit Vivo Native Parser Engine:
  `scanner_backend/credit_vivo_native_parser.py`

## Still used

- FastAPI for backend API
- pypdf for PDF text extraction

## Layout

The approved public website layout was not changed.

## Frontend env

```env
VITE_SCANNER_API_URL=http://localhost:8080
```

## Backend env

```env
CREDIT_VIVO_ALLOWED_ORIGINS=http://localhost:5173,https://creditvivo.com
```

No AI API key needed.
