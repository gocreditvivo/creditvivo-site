# Credit Vivo — Launch Recovery Sprint

**Date:** July 29, 2026  
**Owner:** ChatGPT coordination; Codex backend/scanner/security; Claude frontend/UX  
**Release status at sprint start:** **Blocked pending current evidence**

## Why this sprint exists
The prior handoff is stale and does not provide current branches, PRs, test counts, deployment evidence, or proof that the scanner privacy defect was resolved. No agent may claim launch readiness from old plans or undocumented work.

## Non-negotiable rules
- Read `AGENTS.md` and `shared-workspace/TEAM_HANDOFF_PROTOCOL.md` first.
- Use separate branches and PRs. Do not edit the same files concurrently.
- Synthetic data only.
- No automatic dispute sending.
- No production deployment, billing activation, customer-data intake, or public launch without Tim's approval and named gate evidence.
- Report exact tests and results; do not report unsupported percentages.

# Lane A — Codex critical path

**Branch:** `codex/launch-recovery-backend-2026-07-29`

## A0. Establish current truth
1. Inventory scanner, API, auth, database, storage, export, audit, and test modules.
2. Record the current commit and all active backend/scanner PRs.
3. Run the existing test suite unchanged and publish exact pass/fail/skip counts.
4. List missing dependencies, unavailable services, and broken commands.

## A1. Close the account-number masking P0
1. Reproduce the alleged backward masking issue across XLSX visible sheets, hidden sheets, letters, JSON/API responses, logs, errors, filenames, and test snapshots.
2. Centralize masking so raw account identifiers never reach presentation or telemetry layers.
3. Add regression tests for blank, malformed, short, long, formatted, and already-masked identifiers.
4. Produce a synthetic corrected workbook and a PII-leak scan report.
5. State confirmed/false-positive, root cause, affected files, and residual risk.

**Hard stop:** no customer preview until this gate passes.

## A2. Scanner controlled-beta gate
Verify with versioned synthetic fixtures:
- PDF/TXT validation and safe rejection.
- Bureau/source detection and supported combined-report segmentation.
- Identity and negative-tradeline extraction with source provenance.
- Three-bureau normalization without invented values.
- Collections and charge-offs first.
- Missing/conflicting fields, duplicates, sold/transferred inconsistencies, DOFD-related gaps where present, balance/status/date mismatches, and bureau-presence differences.
- Confidence, reason code, plain-English explanation, parser/rules versions, timestamps, and audit events.

## A3. Backend security and workflow
Verify or implement:
- Authenticated case ownership and customer/admin role separation.
- Server-enforced RLS or equivalent case isolation.
- Private/signed file access.
- Idempotent scan jobs, retry safety, rate limits, file-size limits, safe errors, and audit logs.
- Server-side status transitions for upload → scan → findings → customer approval → admin review → dispute draft → tracking.
- No service-role secret or report contents exposed to client, logs, analytics, or errors.

## A4. Codex deliverable
Open a PR with:
- Architecture/current-state map.
- Files and migrations changed.
- Exact commands and test results.
- Synthetic fixture manifest.
- Security/privacy findings.
- Rollback notes.
- Release classification: Blocked, Preview only, Controlled private beta, or Production approved.

# Lane B — Claude frontend and customer experience

**Branch:** `claude/launch-recovery-frontend-2026-07-29`

Claude must not modify scanner rules, backend security policy, RLS, production migrations, secrets, or production deployment configuration.

## B0. Establish current frontend truth
1. Record current commit, active frontend PRs, route map, build command, tests, and preview status.
2. Identify what is real, mocked, disconnected, broken, or missing.
3. Confirm the current API/type contract before wiring live data.

## B1. Finish the customer journey
Build and verify:
- Premium public landing page using Credit Vivo's approved direction: **AI Precision. Attorney Authority.**
- Signup/login and disclosures/agreement status.
- Report connect/upload with validation, progress, retry, error, and blocked states.
- Scanner progress and findings grouped by bureau/account.
- Source evidence, confidence, and plain-English **possible report issue** wording.
- Customer approval controls.
- Admin review queue.
- Dispute-draft status and mail/tracking timeline.
- Empty, unavailable, support, and permission-denied states.
- Mobile-first responsive layouts and accessibility basics.

## B2. Frontend quality gate
- No guarantees of deletion, score increase, approval, or legal outcome.
- No fake live status: clearly label mock/demo data.
- No secrets or sensitive report content in browser logs, analytics, URLs, or fixtures.
- Route/role guard tests.
- Loading/error/empty/blocked-state tests.
- Keyboard and basic WCAG AA verification.
- Desktop and mobile screenshots.

## B3. Claude deliverable
Open a separate PR with:
- Route and component map.
- Files changed.
- Screenshots/preview URL.
- Exact build/test/accessibility results.
- Mock-vs-live inventory.
- Known limitations and rollback notes.

# Shared interface gate
Before frontend integration, Codex must publish a versioned contract covering:
- Case and scan status values.
- API request/response schemas.
- Finding/evidence/confidence model.
- Role and permission errors.
- Retry/idempotency behavior.
- Customer approval and admin-review events.

Claude acknowledges the contract in the handoff before integration. Any contract change requires a new handoff entry.

# ChatGPT review and founder report
ChatGPT will review both PRs and report:
1. What is genuinely complete.
2. What remains mocked or disconnected.
3. P0/P1 defects and launch blockers.
4. Test evidence and gaps.
5. Recommended release classification.
6. Decisions, vendor access, legal review, or founder approvals still required.

# Definition of finish
Credit Vivo is not considered finished merely because the site builds. The sprint finishes only when both PRs include complete evidence and the integrated staging flow passes with synthetic data. Production remains separately gated by security, privacy, legal/compliance, vendor credentials, monitoring, backup/rollback, and Tim's explicit approval.
