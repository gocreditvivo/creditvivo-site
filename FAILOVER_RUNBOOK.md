# Credit Vivo Failover Runbook

Owner version: if the main site goes down, keep customers informed, protect uploads, and avoid new scanner intake until the backend is ready.

## Current Setup

- Frontend: Vercel static app
- Backend scanner: Render FastAPI service
- Backend health checks:
  - `/health` basic service info
  - `/livez` server is alive
  - `/readyz` server plus storage write test
- Customer status page:
  - `/status`
- Static emergency page:
  - `/failover.html`

## Recommended Production Failover

1. Put `creditvivo.com` DNS behind Cloudflare.
2. Keep the main frontend on Vercel.
3. Create a backup frontend project on Cloudflare Pages or a second Vercel project.
4. Deploy the same static `/failover.html` page to the backup project.
5. Keep the scanner backend on Render, with a second backup backend service when budget allows.
6. Use object storage for uploads, not the app server filesystem.
7. Use managed Postgres backups for customer/account/tracking records.
8. Add uptime monitoring for:
   - `https://www.creditvivo.com/`
   - `https://www.creditvivo.com/status`
   - Render backend `/health`
   - Render backend `/readyz`

## Alert Rules

- Website homepage down for 2 minutes: alert owner.
- Backend `/health` down for 2 minutes: alert owner.
- Backend `/readyz` down for 2 minutes: pause uploads and show safe review message.
- Upload error rate above normal: pause scanner intake.
- Database/storage error: do not accept new report uploads.

## Emergency Steps

1. Check Vercel deployment status.
2. Check Render service status.
3. Check backend `/health` and `/readyz`.
4. If frontend is down but backend is okay, switch Cloudflare DNS or redirect to backup frontend.
5. If backend is down, keep frontend live but pause scanner uploads.
6. If storage/database is down, do not accept credit report uploads.
7. Post customer-safe message on `/status`.

## Customer Message

Credit Vivo is temporarily in safe review mode while we check the scanner connection. Please do not upload a new credit report until the system is marked ready. Existing files should remain protected in secure storage.

## What Still Needs Account Setup

- Cloudflare account and DNS access
- Backup Vercel or Cloudflare Pages project
- Monitoring account such as Better Stack or UptimeRobot
- SMS/email alert destination
- Production storage provider, such as Cloudflare R2, AWS S3, or Supabase Storage
- Managed database backups, such as Supabase, Neon, or Render Postgres

## Owner Rule

If the website, scanner, database, or storage is uncertain, pause new uploads. Customer trust matters more than accepting a report during an outage.
