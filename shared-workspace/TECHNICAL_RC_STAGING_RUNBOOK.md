# CreditVivo Technical RC Staging Runbook

This runbook is staging-only. It does not authorize a production deployment or the use of real customer reports.

## Required staging configuration

- `SCANNER_ENVIRONMENT=staging`
- `SCANNER_ACCEPT_UPLOADS=true` only for the isolated staging service after the migration is applied; leave it false everywhere else until the gate begins
- `SCANNER_WRITE_RAW_TEXT=false`
- `SCANNER_RETAIN_UPLOADS=false`
- `SCANNER_RETAIN_OUTPUTS=false`
- `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` for the isolated staging project
- `CREDIT_VIVO_ALLOWED_ORIGINS` limited to the staging web origin
- `ENABLE_PUBLIC_EVENT_INGEST=false`
- `ENABLE_PUBLIC_LEAD_CAPTURE=false`
- `ENABLE_SKY_BELL_PROXY=false`
- `ENABLE_AUTO_SEND=false`
- `ENABLE_REMOTE_SYNC=false`

Apply `supabase/migrations/20260815070000_technical_rc_security_and_workflow.sql` to staging before accepting a scanner request. The migration creates owner-scoped cases, scans, artifacts, approvals and audit events, a private object bucket, and moves legacy Plaid tokens into Supabase Vault.

## Release smoke check

1. Confirm `/livez` returns 200 and `/readyz` returns 200.
2. Confirm both responses report `accepting_uploads=true`; if false, stop and correct only the isolated staging configuration.
3. Confirm an unsigned scanner request returns 401.
4. With two synthetic staging users, upload the same golden TXT report as user A.
5. Confirm user A can retrieve the summary and each export.
6. Confirm user B receives 404 for user A's job id and cannot list the object path through Supabase.
7. Confirm the persisted JSON, CSV, workbook and browser storage contain no raw account number, SSN, DOB, `raw_block`, or `raw_value`.
8. Confirm a mismatched artifact hash cannot be approved.
9. Confirm a normal member cannot mark a case sent, and no endpoint sends mail or disputes.

## Monitoring and alert thresholds

- Poll `/livez` every minute and `/readyz` every five minutes.
- Alert immediately on three consecutive readiness failures, any 5xx scanner response, artifact upload failure, authentication-service failure, or cross-owner access response other than 404.
- Retain structured platform request logs without request bodies, authorization headers, filenames, report text, or exported artifacts.
- Review Supabase Auth, Database and Storage error rates daily during the RC window.

## Backup and restore drill

1. Use the staging project's managed database backup to create a restore point.
2. Copy the private `credit-report-artifacts` staging bucket to an encrypted, access-controlled staging backup location.
3. Restore both into a new isolated recovery project; never overwrite the active staging project.
4. Run the two-user isolation smoke check against the recovery project.
5. Compare counts and SHA-256 values for `credit_cases`, `credit_scans`, `scan_artifacts`, `customer_approvals`, and stored artifact objects.
6. Record start/end time, row/object counts, hash mismatches, recovery time and tester identity in the authoritative handoff.
7. Delete the recovery project only after Tim explicitly approves that destructive cleanup.

The backup/restore gate remains FAIL until this drill is performed with staging credentials and recorded evidence.
