# Test Deploy Notes — Vercel Preview (no external APIs)

Branch: `test/vercel-preview-no-external-apis`
Purpose: a safe Vercel **Preview** deployment for testing the site and scanner
flow with every paid / unavailable third-party service switched off.

## Removed in this branch

| Item | Why |
| --- | --- |
| `api/sky-bell.js` | Imported `@vercel/connect`, which was removed from `package.json` in commit `8f0e68f`. The function would fail to build/run on Vercel. Not called from anywhere in the UI. |
| `src/lib/skyBellClient.ts` | Client for the above. Unused. |
| `/api/sky-bell` rewrite in `vercel.json` | No longer needed. |

## Services intentionally OFF (do not set these env vars in the preview)

All of these already default to disabled in `scanner_backend/main.py`, so the
correct action is simply to **not** define them on the Preview environment.

| Env var | Service | Preview value |
| --- | --- | --- |
| `LOB_API_KEY` | Lob certified-mail dispute letters | unset |
| `ENABLE_MAIL_API` | Mail sending endpoints | `false` (default) |
| `ENABLE_AUTO_SEND` | Automatic letter dispatch | `false` (default) |
| `SOCRATA_APP_TOKEN` | Socrata open-data lookups | unset |
| `ENABLE_EXTERNAL_LICENSE_LOOKUP` | External license lookup | `false` (default) |
| `ENABLE_ATTORNEY_REFERRAL_API` | Attorney referral partner | `false` (default) |
| `ENABLE_COMPLAINT_SUBMISSION_API` | Live CFPB complaint submission | `false` (default) |
| `ENABLE_AI_SECOND_PASS` | Second-pass AI parse | `false` (default) |
| `ENABLE_REMOTE_SYNC` | Remote data sync | `false` (default) |
| iSoftPull | 3-bureau pull — no code path wired yet | n/a |

## Env vars that ARE safe to set on Preview

| Env var | Value | Notes |
| --- | --- | --- |
| `SCANNER_ENVIRONMENT` | `preview` | Labels the deploy as non-production. |
| `SCANNER_STORAGE_DIR` | leave unset | Auto-resolves to `/tmp/creditvivo-scanner` on Vercel. |
| `SCANNER_RETAIN_UPLOADS` | `false` | Default. No customer PDFs kept. |
| `VITE_SCANNER_API_URL` | leave unset | Frontend then calls the same-origin `/api/*` Python function. |
| `SCANNER_ACCESS_TOKEN` | optional | Set a random string to gate the scanner endpoints during testing. |

## Verify after deploy

1. `GET /` — landing page renders.
2. `GET /api/health` — scanner health check responds; expect
   `external_calls_enabled: false` and `auto_send_enabled: false`.
3. `/dashboard` — dashboard shell loads.
4. Scanner upload — use the built-in demo findings (`demo_scan`) rather than a
   real credit report on a preview URL.

## Do not merge to `main`

This branch is for preview testing only. `api/sky-bell.js` should be restored
properly (with `@vercel/connect` reinstalled) before that connector is used.
