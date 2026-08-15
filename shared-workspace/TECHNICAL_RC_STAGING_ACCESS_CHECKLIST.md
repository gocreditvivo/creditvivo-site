# CreditVivo Technical RC Staging Access Checklist

Use this checklist to unblock the isolated staging gate. Do not paste secrets into chat, source files, commits, screenshots, or the team handoff.

## Required access

- GitHub write access to `gocreditvivo/creditvivo-site`, or a Tim-controlled operator who can push the prepared commit.
- A new or existing isolated Vercel preview/staging project linked to the RC branch.
- A new or existing isolated Render staging service for the scanner API.
- An isolated Supabase staging project with Auth, Database, Storage, Vault, and backup/restore capability.

If any new project or service would create a charge, stop and obtain Tim's spending approval first.

## Required staging values

Configure these only in the provider environment settings:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (server environment only)
- `CREDIT_VIVO_ALLOWED_ORIGINS` (exact staging web origin only)
- `SCANNER_ENVIRONMENT=staging`
- `SCANNER_ACCEPT_UPLOADS=false` during setup
- `SCANNER_WRITE_RAW_TEXT=false`
- `SCANNER_RETAIN_UPLOADS=false`
- `SCANNER_RETAIN_OUTPUTS=false`
- `ENABLE_PUBLIC_EVENT_INGEST=false`
- `ENABLE_PUBLIC_LEAD_CAPTURE=false`
- `ENABLE_SKY_BELL_PROXY=false`
- `ENABLE_AUTO_SEND=false`
- `ENABLE_REMOTE_SYNC=false`

## Activation order

1. Push the RC branch and deploy the web/API staging services with uploads disabled.
2. Apply `supabase/migrations/20260815070000_technical_rc_security_and_workflow.sql` to the isolated staging project.
3. Confirm the migration, private bucket, RLS policies, Auth configuration, and server-only service key.
4. Set `SCANNER_ACCEPT_UPLOADS=true` only on the isolated scanner staging service.
5. Execute `TECHNICAL_RC_STAGING_RUNBOOK.md` with synthetic data.
6. Return `SCANNER_ACCEPT_UPLOADS=false` after the validation window unless the next approved beta gate begins.

## Evidence required

- Staging web and API URLs.
- Deployed commit SHA for each service.
- Redacted environment-variable name list, never values.
- Migration result and timestamp.
- Two synthetic user IDs represented by opaque test labels.
- Cross-user database/object denial results.
- Masking and output-leakage results.
- Monitoring/alert exercise results.
- Backup/restore drill counts, hashes, recovery time, and tester.
- Final PASS/FAIL entry in `TEAM_ACTIVE_HANDOFF.md`.
