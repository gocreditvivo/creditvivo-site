# Credit Vivo Site

Current revision: `2026-07-01-r16.1.1-repo-cleanup`

Credit Vivo is a Vite + React frontend with a Python scanner API adapter. GitHub is the source of truth and Vercel builds the public site from `main`.

## Active App Structure

- `index.html` - Vite app shell.
- `dashboard.html` - static secure portal preview.
- `src/` - active React/Vite frontend.
- `api/` - Vercel API entrypoint.
- `scanner_backend/` - scanner API and parser modules.
- `public/` - public assets, robots, sitemap, redirects.
- `supabase/` - database migration files.
- `vercel.json` - Vercel build/output/routing config.
- `render.yaml` - Render scanner backend config.

## Removed From Active Source

The old Next/Bolt/demo surfaces were removed from the active GitHub tree because this project builds as Vite and those folders were not used by Vercel:

- `.agents/`
- `.bolt/`
- `app/`
- `components/`
- `demo/`
- `src/app/`
- `next.config.mjs`
- `next-env.d.ts`

## Run Locally

```bash
npm install
npm run dev
```

## Verify Before Deploy

```bash
npm run typecheck
npm run lint
npm run build
```

## Deployment

Push verified changes to GitHub `main`. Vercel should automatically deploy the frontend from GitHub. Render should deploy the scanner API when backend files change.

## Safety

Do not commit customer credit reports, SSNs, IDs, `.env` files, API keys, bureau credentials, payment keys, Vercel tokens, GitHub tokens, or real customer documents.
