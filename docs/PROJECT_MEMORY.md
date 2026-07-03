# Credit Vivo Project Memory

Last updated: 2026-07-02

Use this file as the working memory for Credit Vivo website, scanner, GitHub, and Vercel work. Do not place secrets, API keys, passwords, customer credit reports, SSNs, IDs, bureau credentials, or real customer documents in this file.

## Current Production Repo

- Local repo path: `C:\Users\miste\OneDrive\Desktop\credit-vivo-review-package-20260629-211207\creditvivo-site`
- Scanner-focused workspace: `C:\Users\miste\OneDrive\Desktop\Documents\CV Scanner`
- GitHub repo: `gocreditvivo/creditvivo-site`
- Live site: `https://www.creditvivo.com/`
- Vercel project page: `https://vercel.com/gotimdo-4261s-projects/credit-vivo-v2/deployments`
- Active framework: Vite + React frontend
- Scanner backend: Python FastAPI scanner API in `scanner_backend/`
- Vercel API adapter: `api/index.py`
- Active frontend folder: `src/`
- Static dashboard preview: `dashboard.html`
- Bureau layout scanner memory: `docs/scanner/THREE_BUREAU_REPORT_LAYOUT_MEMORY.md`

## Latest Known Versions And Commits

- Active local scanner revision: `18.1.3`
- Active scanner revision name: `v18.1.3 - Approval-Gated Lob-Ready Letter Packets + Formatted Workbook Layout + Raw Identity Cleanup`
- Current scanner workspace output convention: `scan_six_bureau_v18_1_0_revision`
- Last confirmed public package version before v17 work: `16.1.0`
- Last confirmed GitHub main commit from chat: `62c4ff2 Organize production repo files`
- Earlier commit: `12eb50e Add static dashboard preview`
- Repo cleanup revision: `2026-07-01-r16.1.1-repo-cleanup`
- Planned next version: `17.0.0`
- Planned v17 revision name: `v17.0 - Specific Credit Report Review Content`
- Scanner workspace initialized from the website repo scanner backend on 2026-07-01.

## Current Pause Point

The v18 scanner foundation has started with a consumer-only Report Ingestion
Layer and a draft-only Letter Lifecycle foundation. Native uploaded PDF parsing
remains the default, and future extracted text, parser JSON, or structured
bureau/API input paths are reserved only.

Important: do not run `npm run build`, deploy, commit, or push until the user approves the next execution step.

Partial v17 scanner edits were started before the pause:

- `package.json` version changed from `16.1.0` to `17.0.0`
- `src/lib/scannerApi.ts` started adding `decision_readiness`
- `scanner_backend/credit_vivo_proprietary_engine.py` started updating engine labels and adding `build_decision_readiness`
- `scanner_backend/main.py` started updating API labels from v16 to v17 and returning `decision_readiness`

These edits need to be reviewed and completed before any build.

## Scanner Build Flow

1. User visits `/scan`.
2. User chooses demo scanner flow or uploads real PDF credit report files.
3. Frontend route `src/pages/FreeScan.tsx` sends files through `src/lib/scannerApi.ts`.
4. Frontend calls `/api/scanner/parse`.
5. Backend `scanner_backend/main.py` receives uploads.
6. Backend validates file count, PDF type, file size, temporary storage, and raw-text settings.
7. Backend uses `pypdf` to extract PDF text page by page.
8. v18 ingestion layer normalizes uploaded PDF text into the existing parser input shape while marking the source as native uploaded PDF text.
9. Scanner detects likely bureau: Experian, Equifax, TransUnion, or Unknown.
10. Parser engine `scanner_backend/credit_vivo_proprietary_engine.py` extracts tradeline fields.
    - Bureau-specific layout memory is stored in `docs/scanner/THREE_BUREAU_REPORT_LAYOUT_MEMORY.md`.
    - Equifax, Experian, and TransUnion should be treated as distinct report layouts before normalization.
    - Identity cleanup must use only consumer personal-information sections, not furnisher or collector contact lines.
11. Scanner detects review issues such as collections, charge-offs, date gaps, sold-account balance review, bureau mismatches, and low-confidence manual review.
12. v17 decision-readiness layer maps findings to real situations:
    - Auto loan or refinance review
    - Mortgage readiness
    - Apartment application review
    - Collection account review
    - Charge-off or late-payment review
    - Bureau mismatch review
13. Frontend saves result in local storage and routes user to `/findings`.
14. `src/pages/Findings.tsx` displays review categories, files reviewed, issue previews, downloads, letter queue, and approval-required notices.
15. Backend output files include workbook, issues CSV, tradelines CSV, draft letters TXT, full scanner JSON, and summary JSON.
16. v18 letter lifecycle service can convert scanner issue/output data into
    draft-only letter recommendations, approval-gated Lob packet previews, and
    response-review next-step recommendations without sending anything.

## Content Strategy

The current site content is too generic. v17 should make Credit Vivo feel specific, trusted, and useful.

Primary message:

> Understand what your credit report is saying before your next big decision.

Support this with real customer moments:

- Auto loan denial
- Mortgage readiness
- Apartment approval
- Collection account not recognized
- Charge-off review
- Late payment review
- Bureau mismatch review
- Business credit readiness later

## Homepage Upgrade Plan

Recommended homepage order:

1. Hero with specific scanner promise.
2. Problem: credit reports are confusing and inconsistent.
3. Scanner preview: what Credit Vivo checks.
4. Use cases: auto, mortgage, apartment, collections.
5. How it works: check, explain, organize, track.
6. Plans: free check-in first.
7. Compliance trust block.
8. Final CTA.

Move attorney access lower on the page as an optional escalation path, not the headline.

## Pages To Improve

- `/`
- `/scan`
- `/findings`
- `/pricing`
- `/why`
- `/faq`
- `/learning`
- `/auto-loan-denial`
- `/mortgage-readiness`
- `/apartment-denial`
- `/collection-not-mine`

Later expansion pages:

- `/credit-card-denial`
- `/charge-off-review`
- `/late-payment-review`
- `/identity-theft-credit-report`
- `/business-credit-readiness`

## Compliance Rules

Use:

- `possible report errors`
- `inaccurate, incomplete, outdated, duplicate, or unverifiable information`
- `plain-English review`
- `documented next steps`
- `customer-approved dispute prep`
- `results vary`
- `accurate and verifiable information may remain`

Avoid:

- `fix your credit fast`
- `remove bad credit`
- `delete collections`
- `guaranteed score increase`
- `guaranteed approvals`
- claims that accurate negative information can be removed
- fake urgency
- automatic dispute-sending claims

Scanner and website must say:

- Nothing is sent automatically.
- Customer approval is required.
- Scanner output is draft review data.
- Credit Vivo is not a law firm and does not provide legal advice.
- Accurate, current, and verifiable information may remain.

## GitHub And Vercel File Rules

Keep active:

- `src/`
- `api/`
- `scanner_backend/`
- `public/`
- `dashboard.html`
- `vercel.json`
- `render.yaml`
- `supabase/`
- core config files
- current docs in `docs/`

Current docs organization:

- `docs/content/` - site copy, FAQ, learning center, emails, and content audits.
- `docs/scanner/` - scanner API, parser roadmap, proprietary engine, and scanner notes.
- `docs/prompts/` - Bolt, Codex, Webflow, and feature-build prompts.
- `docs/compliance/` - compliance requirements and copy-risk rules.
- `docs/strategy/` - moat, AI operating system, and growth strategy docs.
- `docs/reports/` - verification, handoff, and layout reports.
- `docs/deployment/` - deployment workflow and release process notes.

Previously marked as old or unused:

- `.agents/`
- `.bolt/`
- `app/`
- `components/`
- `demo/`
- `src/app/`
- `next.config.mjs`
- `next-env.d.ts`

Local legacy copies, when present, are organized under `archive/legacy-builds/2026-07-01-local-legacy/`.

Do not delete anything just because it is old unless the user approves and the file is verified as unused.

## Verification Before Deploy

Before any push or deploy:

```bash
npm run typecheck
npm run lint
npm run build
```

Preferred route checks:

- `/`
- `/scan`
- `/findings`
- `/dashboard.html`
- `/dashboard`
- `/privacy`
- `/terms`
- `/disclosure`
- `/pricing`
- `/faq`
- `/signup`

## Next Safe Work Order

1. Review current v17 partial edits.
2. Finish `decision_readiness` type, backend response, demo data, and findings UI.
3. Update `/scan` copy to match v17 scanner positioning.
4. Update homepage copy to match v17 scanner promise.
5. Run typecheck only after user approves execution.
6. Then lint.
7. Then build.
8. Then local route checks.
9. Then commit and push only after user approval.
