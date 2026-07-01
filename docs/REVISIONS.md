# Credit Vivo Revisions

## 2026-07-01-r16.1.1-repo-cleanup

- Removed unused Next/Bolt/demo files from the GitHub production tree.
- Kept the Vite frontend, static dashboard preview, Vercel config, scanner backend, and public assets.
- Added explicit `/dashboard` routing to the static dashboard preview.
- Updated documentation so GitHub/Vercel file roles are clear.

## 2026-06-30-r16.1.0-dashboard-preview

- Added `dashboard.html`.
- Wired public calls to action to the dashboard preview.
- Added Vite multi-page build entry for `dashboard.html`.

## 2026-06-29-r16.1.0-scanner-integration

- Connected the Vite frontend to the scanner API helper.
- Added upload, findings, dashboard, and admin review preview flows.
