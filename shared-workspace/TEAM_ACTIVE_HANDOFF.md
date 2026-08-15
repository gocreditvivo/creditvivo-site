# Credit Vivo — Team Active Handoff

This is the shared operating handoff for Tim Do, ChatGPT, Claude, and Codex through launch.

## Standing rules
Everyone must act in Credit Vivo's lawful long-term best interests; be factual, honest, and supportive; distinguish facts, assumptions, risks, and unknowns; protect company and customer data; disclose blockers, failed tests, mistakes, and security concerns; preserve evidence and change history; and avoid overlapping edits unless ownership is agreed.

## Roles

### Tim Do — Founder and final authority
Owns final product, business, visual, pricing, vendor, legal, tax, ownership, and production decisions.

### ChatGPT — Product, customer-flow, operations, and coordination lead
Owns customer-flow requirements, wording direction, acceptance criteria, approval gates, coordination, founder summaries, and maintenance of this handoff.

### Claude — Frontend, UX, and customer-flow implementation engineer
Owns onboarding, customer dashboard, founder/manager dashboard, content, visual system, responsive design, accessibility, frontend tests, approved integrations, and preview deployment.

Claude must use a dedicated branch and synthetic data only. Claude may not change Metro 2 rules, scanner parsing, production migrations, RLS, auth policy, service-role configuration, production environment variables, or production deployment/domain settings without written reassignment.

### Codex — Backend, scanner, security, and independent verification engineer
Owns scanner/parser, rules engine, backend APIs, data model, security controls, audit logs, Supabase architecture, technical verification, independent test reruns, and production-readiness findings.

## Current objective
Build and verify this customer journey:

Invite → Sign up → Account setup → Disclosures → Agreement status → Credit report connection → Import status → Scanner status → Possible issues → Customer review/approval → Admin review → Dispute preparation → Tracking → Bureau response → Next action

## Current assignments

### Claude
Build the complete frontend customer journey, customer dashboard, founder dashboard, mobile layouts, error/blocked/success states, accessibility, tests, and preview deployment.

### Codex
Verify route/state integrity, role separation, customer data isolation, secrets, API/type contracts, Supabase/RLS assumptions, audit events, bypass risks, test coverage, synthetic-data-only preview, and no unauthorized production changes.

### ChatGPT
Maintain requirements, review Claude architecture/visuals, review Codex findings, resolve conflicts, keep Tim informed, and update this handoff.

### Tim
Approve major product/visual decisions, provide Credit Repair Cloud screenshots/exports, arrange legal review, and withhold production approval until testing and verification are complete.

## Accelerated execution target
This is an AI-assisted build. Move fast without weakening controls.

### Claude target
- Start immediately after reading this handoff.
- Post branch name, owned files/modules, approach, dependencies, risks, and first checkpoint before coding deeply.
- Deliver the first working frontend flow within 2–6 hours where technically feasible.
- Deliver the complete mock-data customer flow, mobile layouts, key failure states, and core tests within 6–12 hours where technically feasible.
- Deliver preview deployment, screenshots, test results, known limitations, and Codex verification package within 12–24 hours where technically feasible.
- Report any blocker immediately. Do not wait for a scheduled update.

### Codex target
- Begin review at Claude's architecture checkpoint rather than waiting until completion.
- Verify route/state integrity, role boundaries, data isolation, secrets, API assumptions, Supabase/RLS implications, test coverage, and preview safety.
- Return confirmed defects with severity, file/line references, missing tests, and pass/conditional pass/fail.
- Complete the first verification pass within 6–12 hours after Claude's review package is available where technically feasible.
- Re-test fixes promptly and document remaining launch blockers.

### ChatGPT target
- Review handoff updates on demand and through the active hourly watcher.
- Resolve requirement conflicts quickly.
- Keep Tim informed of actual progress, blockers, risks, and verified completion evidence.

### Founder expectation
The target is same-day first build and next-day verification, not a guarantee. Actual completion depends on repo health, API readiness, auth/Supabase issues, and test failures. Speed does not override security, customer-data protection, or production approval gates.

## Required handoff checkpoints

### Task start
Post task, branch, owned files/modules, approach, dependencies, risks, and expected checkpoint.

### Architecture checkpoint
Post route map, component/module structure, state model, role model, API assumptions, sensitive actions, and test plan.

### Interface-ready checkpoint
Post API contracts, types, events, status values, integration assumptions, and unresolved dependencies.

### Pull-request checkpoint
Reviewer returns confirmed defects, severity, file/line references, missing tests, security/data-isolation findings, integration mismatches, and pass/conditional pass/fail.

### Pre-deployment checkpoint
Provide passing tests, no exposed secrets, synthetic data only, no unauthorized production changes, rollback path, known limitations, and Tim approval status.

### Completion checkpoint
Post branch/commit, files changed, screenshots or preview URL, tests/results, accessibility findings, security/compliance impact, limitations, blockers, and next task.

## Timing
- Small task: completion handoff.
- Medium task: start + completion.
- Large task: start + architecture + interface-ready + PR + completion.
- Critical/security task: immediate alert + milestone reviews + pre/post-deployment checks.
- Work over one day: daily progress update.
- Any blocker affecting another person: immediate update.
- Any shared API/type/status change: update before merge.

## Status values
Not started; In progress; Waiting on Tim; Waiting on Claude; Waiting on Codex; Waiting on ChatGPT; Blocked; Needs review; Ready for preview; Ready for verification; Conditionally approved; Approved; Rejected; Completed.

## Non-negotiable safeguards
- No automatic dispute sending at launch.
- No scanner output presented as a final legal conclusion.
- No real customer data in development or preview.
- No production secrets in client code.
- No production deployment without Tim's approval.
- No hiding failures or weakening controls for speed.

## Active status updates

### Claude task-start checkpoint — 2026-07-19
- Status: In progress.
- Delivery mode: `offline-package/claude-frontend-journey-v1` because Claude has no authenticated GitHub or working local file access.
- Target integration branch for Codex/Tim to create: `claude/frontend-customer-journey`.
- Stack decision from ChatGPT after repository inspection: build for the root Vite + React + TypeScript application. Root `package.json` uses Vite, React 18, React Router, TypeScript, Tailwind, and Supabase.
- Owned modules: `src/journey/`, `src/dashboard/customer/`, `src/dashboard/founder/`, `src/components/`, `src/state/journeyMachine.*`, `src/mocks/`, and `tests/frontend/`.
- Architecture approach: one explicit typed journey state machine; mock data through a replaceable typed service layer; loading/success/error/blocked rendering for every state; customer/founder role gates at route boundaries; mobile-first WCAG AA.
- Dependencies: Codex API contracts for import/scanner/dispute status; Tim's Credit Repair Cloud screenshots/exports; Codex or Tim must land the package and create the preview deployment.
- Next checkpoint: Claude architecture checkpoint with route map, component structure, state model, role model, API assumptions, sensitive actions, and test plan.

### Critical Codex verification task — B-3 account-number masking
- Reported by Claude from `credit-vivo-desktop-scanner-output__55_.xlsx`.
- Alleged behavior: account numbers appear masked backwards, exposing leading digits and hiding only the last four; Claude reports 299 affected cells, including 274 in hidden Draft Letters.
- Status: Unverified critical finding. Codex must independently reproduce and confirm counts, source logic, affected outputs, and whether any real or synthetic data is involved.
- Required safe behavior: expose no more than the minimum approved identifier, normally masked except last four where operationally necessary.
- Immediate controls: do not distribute the affected workbook, do not use affected draft letters, and do not treat the finding as resolved until Codex fixes and tests all generated outputs.
- Codex deliverable: confirmed/false-positive determination, severity, root cause, files/lines, regression tests, corrected outputs, and pass/fail result.

### CreditVivo Technical RC task-start checkpoint - 2026-08-15

- Status: In progress. Feature expansion is frozen.
- Founder directive: turn the current red technical gates green in critical-path order without production deployment, real customer data, spending, vendor/domain/pricing changes, external communications, or destructive/irreversible actions.
- Builder: Codex. Independent verifier: a read-only security verifier that cannot edit implementation files. Claude remains frontend/reference-side unless Tim explicitly transfers ownership.
- Authoritative engineering base: preserved full-stack branch `codex/main-quality-automation-repair` at `fa22d7c8b9908516b31e56ac5f5a854cd4c305a5` from `C:\CreditVivo\_GITHUB\creditvivo-main-repair-20260803`.
- Isolated implementation branch: `codex/technical-rc-20260815` in `work/creditvivo-technical-rc-20260815-v2`. Original CreditVivo checkouts are unchanged.
- Base selection evidence: the August 14 `creditvivo-site` checkout is a Next.js demo shell whose active handoff records no real scanner, auth, persistence, tenant isolation, or secure storage; this full-stack base contains the scanner backend, frontend integration, Supabase migration, and existing scanner tests.
- Owned modules: `scanner_backend/`, backend/API contracts, Supabase schema/policies, security and workflow test suites, operational runbooks, and this technical evidence handoff. Frontend UX changes are out of scope unless required to complete a backend contract or critical end-to-end gate.
- Gate order: scanner hardening -> golden synthetic corpus -> independent scanner verification -> auth/persistence -> tenant isolation/private storage -> masking/evidence traceability -> approval/dispute lifecycle -> E2E/security/regression -> staging/monitoring/backup-restore -> final RC verification.
- Test plan: baseline the unchanged Python and frontend suites; add deterministic synthetic fixtures and expected normalized/finding outputs; add negative/security/ownership/state-transition tests; run build, lint, typecheck, scanner unit/integration/regression, and isolated end-to-end checks; submit each completed gate to the independent verifier.
- Environment: Windows local isolated development; synthetic data only; production services and production credentials are not accessed.
- Initial risk: the preserved full-stack branch may still contain demo/local persistence and incomplete RLS/storage controls. These remain FAIL until fresh evidence passes.
- Next checkpoint: baseline inventory and exact PASS/FAIL results before implementation.

### Technical RC baseline checkpoint - 2026-08-15

- Gate result: FAIL. No RC or customer-data readiness claim is permitted from this baseline.
- Frontend lint: PASS (`pnpm run lint`, exit 0).
- Frontend typecheck: PASS (`pnpm run typecheck`, exit 0).
- Scanner tests in privacy-safe mode: 88 passed, 1 failed. The single failure explicitly expected raw extracted text to be written by default; the running safe configuration correctly returned `write_raw_text=false`. This proves the repository test contract still encoded an unsafe default.
- Scanner privacy default: FAIL. `scanner_backend/main.py` defaulted `SCANNER_WRITE_RAW_TEXT` to `true`, despite the environment example recommending `false`.
- Frontend build in the isolated copy: environment-blocked before compilation because the temporary pnpm/esbuild layout attempted to read outside the managed workspace. This is not counted as a product-code PASS or FAIL; lint and typecheck completed.
- Golden synthetic corpus: FAIL. Existing scanner tests use inline samples but there is no versioned fixture manifest with expected normalized output and expected findings for every mandatory report class and malformed-file case.
- Auth/persistence: FAIL/UNPROVEN. Frontend Supabase auth exists, but scanner endpoints are not yet bound to authenticated user-owned cases; browser storage remains part of the scan-result path.
- Tenant isolation/private storage: FAIL/UNPROVEN. The only migration in this base does not define the scanner case/report/finding/approval lifecycle, private report bucket policies, or cross-user denial tests.
- Masking/evidence traceability: PARTIAL/UNVERIFIED. A central mask helper and source evidence fields exist, but there is no current corpus-wide leakage test across JSON, CSV, workbook hidden sheets, draft letters, logs, errors, and downloads.
- Approval/dispute lifecycle: PARTIAL/FAIL. Draft-only wording and approval-required flags exist, but server-enforced ownership and allowed status transitions are not yet implemented end to end.
- Automated E2E/security/regression: FAIL. Scanner unit/regression coverage exists, but authenticated cross-tenant, upload-abuse, workflow-bypass, and full portal-to-scanner E2E suites are absent.
- Staging/monitoring/backup-restore: FAIL/UNPROVEN. No staging deployment will be performed without Tim approval; local configuration/runbooks are not proof of restore or monitoring behavior.
- Next implementation gate: make raw-text minimization fail-safe, add the golden corpus, add full-output leakage checks, and submit scanner evidence to the independent verifier.

### Technical RC implementation checkpoint - 2026-08-15

- Overall status: READY FOR INDEPENDENT RE-VERIFICATION; production and customer-data use remain BLOCKED.
- Independent baseline review: FAIL. The verifier confirmed raw PII in serialized/exported evidence, weak masking of short and mixed-mask values, no authenticated owner binding, an unauthenticated connector proxy, spreadsheet formula injection, upload cleanup/resource-limit gaps, public operations endpoints, plaintext Plaid tokens, and missing role enforcement. The verifier's claim that `api/index.py` was a one-byte file was independently checked and is incorrect in this checkout; it contains `from scanner_backend.main import app`.
- Scanner hardening - builder PASS: PDF magic/encryption/page/text limits, TXT validation, fail-closed whole-request behavior, request-level cleanup, workbook handle closure, formula neutralization, no raw-text default, and no partial result retention. Evidence: `tests/test_upload_boundaries.py` plus the full Python suite.
- Golden synthetic corpus - builder PASS: eight versioned manifest cases cover Experian collection, Equifax charge-off, TransUnion positive, combined three-bureau, duplicates/transfer, missing fields, OCR/reordered fields, and corpus determinism/leakage. No real customer report is included.
- Masking/evidence traceability - builder PASS: short values are fully masked; leading-clear/trailing-mask values reveal nothing; API/JSON/CSV/XLSX omit `raw_block` and `raw_value`; SSN/DOB/account values are redacted; evidence retains source hash, opaque block id/hash and sanitized source lines. Full-output leakage and formula-injection regression tests pass.
- Auth/persistence - builder PASS: scanner uploads, results and downloads require Supabase-authenticated bearer sessions; every successful scan creates an owner-scoped case/scan record and immutable artifact hash; the frontend sends its session token for parse/result/download calls.
- Tenant isolation/private storage - builder PASS: local paths use hashed tenant/user partitions; database tables and private storage objects are owner-RLS scoped; sanitized artifacts are uploaded to a private bucket and local uploads/outputs default to deletion; cross-user and same-tenant/different-user denial tests pass.
- Approval/dispute lifecycle - builder PASS: approvals are bound to the stored scan hash; allowed status transitions are enforced; `approved` and `sent` require matching approval scopes; only founder/admin can mark sent; audit events are written; no route sends a letter or dispute.
- Privileged surfaces - builder PASS: Sky Bell is disabled by default and additionally requires an internal bearer token plus exact path/method allowlist; founder/admin frontend routes are role-gated; backend admin/growth/operator routes require founder/admin; public lead/event ingestion defaults disabled.
- Bank-token storage - READY FOR STAGING VERIFICATION: the staging migration moves legacy Plaid access tokens into Supabase Vault, removes authenticated table access to secrets, and drops the plaintext column only after complete migration.
- Automated test evidence: Python `pytest -q` PASS, 115 passed, 1 third-party deprecation warning. Frontend typecheck PASS. Frontend lint PASS. Frontend production bundle PASS with Vite runner config and workspace-local temp directory (1,592 modules transformed). NPM production audit PASS with 0 vulnerabilities; full audit PASS after pinned transitive fixes.
- Staging/monitoring/backup-restore - FAIL pending Tim-authorized staging credentials/environment. The staging runbook is `shared-workspace/TECHNICAL_RC_STAGING_RUNBOOK.md`; it specifies required fail-safe configuration, two-user isolation smoke test, privacy checks, monitoring thresholds, and restore drill. A runbook is not restore evidence.
- Independent scanner/security re-verification - PENDING. Builder results are not final verification.
- Final RC - BLOCKED until the independent verifier passes the implementation checkpoint and the staging migration, two-user smoke test, monitoring checks, and backup/restore drill produce recorded evidence.

### Technical RC verifier checkpoint 1 and remediation 2 - 2026-08-15

- Independent verdict at `02fdde5`: BLOCKED. Confirmed PASS included hardened maskers, formula injection defenses, fail-closed bearer auth, local owner partitioning, no auto-send sink, Sky Bell authentication/allowlist, privileged backend route enforcement, synthetic-only fixtures, `api/index.py`, and build/type/lint/production dependency checks.
- Independent FAIL findings: grouped identifier leakage, unsanitized native match notes and filenames, complete scan response in localStorage, broad authenticated RLS writes, stale approval reuse, non-atomic audit, unreproducible source evidence, remote upload orphans, missing concurrency/rate/deadline limits, weak minimum/subset golden assertions, editable frontend role fallback, missing security headers, Sky Bell size/timeout gaps, and legacy returning-user schema references.
- Remediation 2 builder evidence: all grouped/separated identifiers now pass through the central sanitizer; the native parser sanitizes its entire output; upload filenames are replaced with generated report names at every API/persistence boundary; new adversarial tests cover grouped identifiers and native match notes.
- Browser persistence: full scanner results are memory-only; reload restoration reads owner-RLS `credit_scans` and retrieves the result through the authenticated scanner API. No scanner data is written to localStorage and legacy `creditvivo_scans`/`creditvivo_findings` references are removed.
- Database authority: authenticated users have SELECT-only RLS on cases, scans, artifacts, approvals, and audit events. Server-only writes use the service role. Approval, revocation, and status changes run in security-definer database functions that validate `auth.uid()`, bind to `current_scan_id` and its exact artifact hash, enforce trusted `app_metadata` for sent status, and write audit events in the same transaction.
- Evidence durability: each original synthetic upload is stored in the private owner path before local deletion, with SHA-256 calculated from the original file bytes and recorded in immutable `scan_artifacts`; derived artifacts remain separate. Partial object uploads and orphan case/scan rows have compensating rollback paths and regression coverage.
- Abuse controls: authenticated per-user rate limit, process concurrency cap, queue wait bound, request deadline checkpoints, PDF page/character/byte/file caps, heavy parser/export work moved off the async event loop, and Sky Bell request/response size plus upstream timeout limits.
- Golden corpus v2: every fixture now asserts the exact ordered normalized tradelines and exact issue multiset, including zero-issue positive-report assertions, exact duplicate handling, and late-payment/missing-DOFD detection. A generated text-bearing synthetic PDF exercises actual PDF extraction; blank, encrypted, fake, over-page, over-character, binary, and over-byte files fail closed.
- Frontend controls: founder/admin routing trusts only server-controlled `app_metadata`; owner API requests carry the authenticated session; Vercel and Express responses now define CSP, HSTS, frame, MIME, referrer, and permissions policies.
- Builder verification after remediation 2: Python full suite PASS, 125 passed with one third-party TestClient deprecation warning; TypeScript typecheck PASS; ESLint PASS; Vite production bundle PASS with 1,593 modules transformed and only the existing chunk-size warning; complete NPM audit PASS with 0 vulnerabilities.
- Status: READY FOR INDEPENDENT RE-VERIFICATION 2 after commit. Staging migration/RLS/storage denial, monitoring exercise, and backup/restore remain FAIL/UNPROVEN until Tim provides or approves isolated staging credentials. Production remains NO-GO.
