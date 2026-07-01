# Credit Vivo Default Deployment Workflow

Use this process every time Credit Vivo website or portal files change.

## Default Rule

1. Edit files locally.
2. Run the deploy script so checks happen before anything is pushed.
3. Commit changes to GitHub.
4. Let Vercel deploy the website from GitHub.
5. Let Render deploy the scanner API from GitHub when backend files change.
6. Verify the live site and key scanner/API health checks.

Plain English: GitHub is the source of truth. Vercel and Render should update from GitHub automatically after a verified push to `main`.

## Local App

Current working app:

`C:\Users\miste\OneDrive\Desktop\credit-vivo-review-package-20260629-211207\creditvivo-site`

Local preview:

`http://127.0.0.1:4180`

## GitHub

Target repository:

`https://github.com/gocreditvivo/creditvivo-site`

## Vercel

Vercel should stay connected to the GitHub repository. After each approved push to the production branch, Vercel should rebuild and publish the site automatically.

Default behavior is now: after changes pass checks, `tools\deploy-creditvivo.ps1` commits and pushes to GitHub.

Use `tools\deploy-creditvivo.ps1 -NoPush` only when you want a local commit without updating GitHub/Vercel/Render.

## Render

Render should stay connected to the GitHub repository and use `render.yaml`.

Backend service:

`creditvivo-scanner-api`

Health check:

`/health`

If Render auto-deploy is enabled, pushing to GitHub updates the scanner API. If auto-deploy is disabled in Render, manually deploy the latest GitHub commit from the Render dashboard.

## Do Not Commit

- `.env` files
- customer credit reports
- customer IDs
- payment keys
- GitHub tokens
- Vercel tokens
- bureau credentials
- real customer documents

## Verification Checklist

- `npm run build` passes.
- `npm run typecheck` passes.
- `npm run lint` passes.
- `python -m pytest tests` passes inside `scanner_backend` when backend files change.
- `/`, `/scan`, `/privacy`, `/terms`, `/disclosure`, `/pricing`, `/faq`, and `/signup` load.
- `/dashboard.html` or `/dashboard` loads the static dashboard preview.
- Security headers are present.
- Demo scan still creates a case.
- Live domain opens after Vercel deploys.
- Render `/health` returns healthy after scanner backend deployment.

## Safer Deploy Script

`tools\deploy-creditvivo.ps1` now verifies, commits, and pushes by default.

Examples:

```powershell
.\tools\deploy-creditvivo.ps1 -Message "Update homepage"
```

Runs checks, commits, pushes to GitHub, and triggers Vercel/Render if connected.

```powershell
.\tools\deploy-creditvivo.ps1 -Message "Update homepage" -NoPush
```

Runs checks and commits locally only.
