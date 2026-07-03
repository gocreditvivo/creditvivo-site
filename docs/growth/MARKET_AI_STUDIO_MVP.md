# Credit Vivo Market AI Studio MVP

Date: 2026-07-02

## Purpose

Credit Vivo Market AI Studio is the in-house creative studio for learning videos, ad images, ad animations, ad videos, thumbnails, captions, scripts, storyboards, campaign ideas, and reusable Credit Vivo-owned brand assets.

## Boundaries

- Separate from Scanner AI.
- Does not access raw credit reports, SSNs, IDs, customer files, or dispute packets.
- Uses approved generic learning topics and approved scanner concepts only.
- No outside stock footage dependency.
- No competitor visuals.
- No auto-publishing.
- Founder/compliance approval required before public use.

## MVP Built

- Backend Market AI studio engine: `scanner_backend/market_ai_studio.py`
- FastAPI studio routes:
  - `/market-ai`
  - `/market-ai/assets`
  - `/market-ai/images`
  - `/market-ai/animations`
  - `/market-ai/videos`
  - `/market-ai/learning`
  - `/market-ai/campaigns`
  - `/market-ai/calendar`
  - `/market-ai/review`
  - `/market-ai/approved`
  - `/market-ai/settings/brand`
- FastAPI API routes:
  - `/api/market/assets`
  - `/api/market/generate-script`
  - `/api/market/generate-storyboard`
  - `/api/market/compliance-check`
  - `/api/market/render-job`
  - `/api/market/templates`
- Next-style scaffold under `app/`, `components/market/`, and `lib/market/`.
- Regression tests in `scanner_backend/tests/test_market_ai_studio.py`.

## Verification

- `npm.cmd install` passed.
- `npm.cmd run build` passed with `131 passed`.
- `npm run dev` was attempted but local dev server could not start because the `.venv` points to a missing/inaccessible Python 3.12 install and the available Python 3.14/3.15 installs do not have FastAPI/uvicorn.
