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

### Technical RC verifier checkpoint 2 and remediation 3 - 2026-08-15

- Independent verdict at `dd0eae1`: BLOCKED. Independent PASS evidence included grouped/separated masking, opaque native match ids, raw evidence removal, filename opacity, CSV/XLSX formula safety, browser memory-only handling, owner-bound code paths, SELECT-only RLS, current-scan/hash approval binding, immutable approval/revoke/status audit transactions, app-metadata roles, private source evidence, exact golden assertions, security headers, `api/index.py`, Plaid Vault migration logic, typecheck, lint, build, and zero-vulnerability dependency audit.
- Remaining verifier FAIL findings were repaired without feature expansion: a separate founder/admin actor can now perform only the `approved -> sent` transition for a customer-owned case while the approval remains bound to the customer's current scan/hash; case/scan/current-scan creation is one service-role-only database transaction; rollback clears the cyclic reference and is one service-role-only RPC; non-2xx object cleanup is a surfaced failure rather than silently accepted.
- The parser/export phase now runs in an isolated spawned process. The parent enforces the remaining wall-clock budget, terminates and then kills an overrun worker if necessary, verifies the output hash before loading the result, and releases request capacity after cleanup. This replaces the prior cooperative post-work deadline check for the CPU-heavy phase.
- The unused Sky Bell connector proxy is disabled at the route with a constant 404 response. It performs no fetch, imports no absent connector package, and no longer buffers an untrusted upstream response. Reintroduction requires a separate reviewed implementation.
- Synthetic-only hygiene restored: the personal-name filename vector is replaced with `SYNTHETIC-PERSON-...` while retaining the filename/identifier leakage adversarial test.
- Builder verification after remediation 3: Python full suite PASS, 127 passed with one third-party TestClient deprecation warning; TypeScript typecheck PASS; ESLint PASS; Vite production bundle PASS with 1,593 modules transformed and only the existing chunk-size warning; complete NPM audit PASS with 0 vulnerabilities across 412 dependencies; Python compile, Node syntax, and `git diff --check` PASS.
- Status: READY FOR INDEPENDENT RE-VERIFICATION 3 after commit. Live staging migration, two-user RLS/storage denial, monitoring alerts, and backup/restore remain FAIL/UNPROVEN and require a Tim-approved isolated staging project and credentials. Production remains NO-GO.

### Technical RC verifier checkpoint 3 and remediation 4 - 2026-08-15

- Independent verdict at `8037803`: BLOCKED on two P1 failure-cleanup paths. The verifier confirmed every other locally reviewable gate PASS in code/tests and withdrew an initial internal-route authorization concern after confirming the global founder/admin middleware.
- Local cleanup fix: request failure cleanup now attempts remote-object rollback and database rollback independently, unconditionally deletes the local derived-output directory in `finally`, and surfaces the first cleanup error only after all cleanup lanes run. A database rollback failure can no longer skip local PII deletion.
- Remote cleanup fix: successful artifact persistence returns the exact private object paths to the endpoint. Any later deadline or response-path failure deletes those exact objects before/alongside atomic database rollback; non-2xx remote cleanup remains a surfaced failure.
- Executable regression evidence: a forced database rollback failure leaves no local job/output directory; a simulated stuck worker executes terminate and kill fallback; a hard-deadline failure releases scan capacity; and a post-upload deadline passes the returned remote paths into object cleanup and then rolls back database state.
- Builder verification after remediation 4: upload/cleanup suite PASS, 14 passed; full Python suite PASS, 131 passed with one third-party TestClient deprecation warning; Python compile and `git diff --check` PASS. Frontend code was unchanged from the prior typecheck, ESLint, 1,593-module build, and zero-vulnerability audit passes.
- Status: READY FOR INDEPENDENT RE-VERIFICATION 4 after commit. Live staging migration, two-user RLS/storage denial, monitoring alerts, and backup/restore remain FAIL/UNPROVEN pending Tim-approved isolated staging access. Production remains NO-GO.

### Technical RC independent code verdict - 2026-08-15

- Independently verified code checkpoint: `0062127244ec6c2e9a8d20ce737daaed1ac46e47` on `codex/technical-rc-20260815`.
- Verifier verdict: all previously confirmed code blockers PASS; no new P0/P1 code defect found. Code is acceptable to enter isolated staging validation, but it is not approved for production or customer data.
- Independent execution: native privacy, release configuration, and exact golden corpus tests PASS, 15 passed; AST syntax validation PASS; exact worktree cleanliness and `git diff --check` PASS. The verifier also inspected the executable rollback/deadline/capacity regressions and the final cleanup control flow.
- Builder execution: full Python suite PASS, 131 passed with one third-party TestClient deprecation warning; upload/cleanup suite PASS, 14 passed; TypeScript typecheck PASS; ESLint PASS; Vite production build PASS with 1,593 modules and only the existing chunk-size warning; NPM audit PASS with 0 vulnerabilities across 412 dependencies.
- Code PASS gates: scanner hardening; exact golden synthetic corpus; masking/evidence traceability; formula safety; authenticated owner binding; memory-only browser handling; atomic server-only case/scan persistence; code-level owner RLS/private storage; customer/current-scan/hash approval and separate staff send authority; immutable transactional audit; killable parser/export deadline; file/page/character/rate/concurrency limits; unconditional local and exact remote failure cleanup; security headers configuration; disabled Sky Bell proxy; internal route authorization; Plaid Vault migration logic; API rewrite integration.
- Remaining release FAIL/UNPROVEN gates: apply the migration in an isolated staging project; execute adversarial two-user RLS and private-object denial; verify staged auth/lifecycle/routes/headers; exercise monitoring and cleanup alerting; perform and document backup/restore. These require Tim-approved isolated staging credentials/environment.
- Final release-candidate verdict: CODE CHECKPOINT PASS / STAGING RELEASE GATE BLOCKED. Production remains NO-GO. No production deployment, real customer data, external communications, vendor/domain/pricing change, spending, or irreversible action occurred.

### Founder-approved staging and emergency upload suspension - 2026-08-15

- Founder approval recorded: temporarily block the current live scanner from accepting real report uploads and proceed with isolated staging preparation for the independently verified RC. This approval does not authorize the final RC production cutover, real customer data, spending, vendor/domain/pricing changes, or destructive cleanup.
- Owner: Codex. Branch: `codex/technical-rc-20260815`. Scope: fail-closed upload availability control, staging configuration/runbook alignment, local verification, and deployment-access discovery. Feature expansion remains frozen.
- Live evidence before action: `https://www.creditvivo.com/api/health` returned HTTP 200 with `environment=local`, `version=16.0`, and `write_raw_text=true`; `/scanner` and `/scan` returned the public application. The live scanner must remain customer-data NO-GO.
- Deployment-access evidence: this isolated RC checkout points to a local Git remote. The production-connected checkout is dirty with extensive unrelated user changes and cannot be edited safely. No linked Vercel project, Vercel/Supabase/Render CLI session, provider token environment variable, or usable GitHub credential was found in the current session.
- Acceptance criteria: provider deployments fail closed unless upload acceptance is explicitly enabled; local tests remain enabled; health/readiness disclose whether uploads are accepted; the staging runbook requires explicit staging enablement; all relevant regression/build checks pass; no production claim until the live endpoint is rechecked after an authorized deploy.

### Emergency upload control and staging preparation checkpoint - 2026-08-15

- RC implementation: hosted deployments now fail closed unless `SCANNER_ACCEPT_UPLOADS=true` is explicitly configured. Health/readiness disclose `accepting_uploads`; local development/tests remain enabled; isolated staging must opt in only after its migration is applied. `.env.example`, `render.yaml`, and the staging runbook are aligned.
- Separate emergency production-safety branch: `codex/emergency-upload-suspension-20260815`, commit `d84bbe5e28b78573f8aee8ddc4331a4f8339bc53`, based exactly on the currently deployed full-stack source checkpoint `fa22d7c8b9908516b31e56ac5f5a854cd4c305a5`. It disables hosted uploads by default and changes the legacy raw-text default from true to false without importing the broader RC.
- Emergency verification: Python full suite PASS, 91 passed; targeted upload/config suite PASS, 8 passed; TypeScript typecheck PASS; scoped ESLint PASS; Vite production build PASS, 1,591 modules; production dependency audit PASS, 0 vulnerabilities. The legacy branch's full development audit still reports 21 high findings already remediated in the RC, so the emergency branch is mitigation-only, not the release candidate.
- RC verification after control: Python full suite PASS, 133 passed; targeted upload/config suite PASS, 8 passed; TypeScript typecheck PASS; scoped ESLint PASS; Vite production build PASS, 1,593 modules; complete NPM audit PASS, 0 vulnerabilities across 412 dependencies; `git diff --check` PASS.
- Staging access packet: `shared-workspace/TECHNICAL_RC_STAGING_ACCESS_CHECKLIST.md` records the exact provider access, safe variable names, activation order, and evidence required without recording secret values.
- Activation blocker: the current session has no usable GitHub credential, linked Vercel project/session, Render session/token, or isolated Supabase staging project credentials. The prepared emergency commit has not been pushed or deployed. Live status is therefore unchanged and must not be described as blocked until `/api/health` reports `accepting_uploads=false` and an upload attempt returns the expected 503.
- Next authorized action: Tim signs in to or supplies an approved operator for GitHub/Vercel/Render and provides an isolated Supabase staging environment through provider-side secret configuration. No secret should be pasted into chat or committed.

### Founder-approved live scanner safety deployment - 2026-08-15

- Emergency deployment result: PASS. GitHub PR [#12](https://github.com/gocreditvivo/creditvivo-site/pull/12) was squash-merged as `6b4b523ff9fe9322de31436694d51ac7877c59ba`; it makes hosted scanner uploads fail closed unless explicitly enabled and changes the legacy raw-text default to false.
- Pre-merge evidence for PR #12: both Vercel preview deployments Ready; public preview `/api/health` returned `accepting_uploads=false` and `write_raw_text=false`; a synthetic multipart upload returned HTTP 503 with `scanner_uploads_disabled`.
- Middleware hardening: PR #13 was closed without merge because its reused branch produced a misleading merge-base diff. No code from PR #13 entered `main`. Clean two-file PR [#14](https://github.com/gocreditvivo/creditvivo-site/pull/14) was squash-merged as `45abb121b747ae332237e6457c554eccc6f0a952`; it rejects hosted scanner POST requests in middleware before FastAPI route validation or multipart parsing, while keeping the handler guard as defense in depth.
- Pre-merge evidence for PR #14: clean diff of 34 additions/1 deletion across two files; emergency Python suite PASS, 92 passed; targeted middleware/config suite PASS, 9 passed; RC Python suite PASS, 134 passed; current public preview returned 503 for a malformed non-multipart synthetic request. Both production Vercel status checks passed after merge.
- Post-deployment live evidence: `https://www.creditvivo.com/`, `/scanner`, `/scan`, and `/api/health` returned HTTP 200. Health reported `accepting_uploads=false`, `write_raw_text=false`, and `retain_uploads=false`. Both a malformed synthetic request and a synthetic multipart file request to `/api/scanner/parse` returned HTTP 503 with `scanner_uploads_disabled`.
- Security impact: the public site remains available, but the hosted scanner now refuses upload request bodies before application parsing. No real customer data, provider secret, domain/pricing/vendor change, spending, or destructive action was used.
- Rollback: revert `45abb121` to remove middleware-only hardening; revert `6b4b523f` to remove the emergency upload control. Do not perform either rollback while customer-data use remains unapproved.
- Corrected access status: an authorized GitHub connector and automatic Vercel previews/deployments were available and used after the earlier CLI/session check. No isolated Supabase staging project or approved Render/Supabase staging credential set is available yet.
- Current release status: LIVE UPLOAD SAFETY CONTROL PASS / TECHNICAL RC STAGING GATE BLOCKED. The production site is not approved for customer report processing. Next gate is the isolated Supabase/Render/Vercel RC staging environment in `TECHNICAL_RC_STAGING_ACCESS_CHECKLIST.md`.

### Isolated Supabase staging discovery - 2026-08-15

- Read-only discovery found one healthy CreditVivo Supabase project, `gykmlrctdzyzoobsmfqw`, in the `gocreditvivo` organization. It is treated as production and was not queried, migrated, reconfigured, or used for synthetic testing.
- The CreditVivo project currently has zero development branches. Supabase quoted a new isolated branch at `$0.01344` per hour.
- Spending remains outside the existing approval. Branch creation, cost confirmation, migration application, and staging tests are stopped pending Tim's explicit approval of that hourly charge. The smallest founder decision is: approve or decline a temporary Supabase staging branch at `$0.01344/hour`, with deletion only after a separate explicit cleanup approval.

### ChatGPT-design customer-flow preview task start - 2026-08-15

- Status: In progress. Founder identified `https://creditvivo-preview.gotimdo.chatgpt.site/` as the authoritative visual direction and requested a test environment connected to the CreditVivo customer flow.
- Owner: Codex by direct founder assignment for this isolated integration. Branch: `codex/chatgpt-home-customer-flow-preview` from the independently code-approved Technical RC checkpoint. No concurrent Claude file ownership is assumed.
- Scope: preserve the authoritative public-page layout in a no-index Vercel preview; replace the prototype's dead `#top` sign-in and `mailto:` primary conversion paths with the existing `/login` route; retain protected `/dashboard`, `/scan`, and `/findings` routing; do not change scanner/backend, Supabase, RLS, domains, pricing configuration, or production deployment.
- Expected files: `public/customer-flow-preview.html`, `public/chatgpt-preview.css`, `public/customer-flow-preview.js`, `vercel.json`, and this handoff only.
- Acceptance criteria: preview root matches the identified visual direction; primary CTAs reach `/login`; protected routes still fail closed for anonymous users; build, typecheck, lint, and link checks pass; synthetic accounts/data only; `creditvivo.com` remains unchanged pending separate production approval.
- Founder scope addition: add an Evidence Vault section for government-ID verification and proof-of-error documents. Preview uploads remain disabled and synthetic-only; the section must show distinct upload, security-scan, extract, review, and confirm states and must not claim real identity-document readiness before isolated staging storage/security tests pass.
- Founder pricing input: each bureau report costs $5, so a three-bureau report set costs $15. Founder deferred tier selection to the next product task; the test page now says pricing is under review and that no charges occur in the preview.
- Verification found a route collision: `dashboard.html` was configured as a second Vite entry and caused `/dashboard` to serve an unprotected legacy static scanner screen in local preview. The legacy entry is removed from the build so `/dashboard` resolves through the protected React router.

### ChatGPT-design customer-flow preview pre-deployment checkpoint - 2026-08-15

- Environment: local preview only; synthetic data only; no production domain, provider configuration, scanner backend, Supabase policy, or real document changed.
- Visual result: authoritative ChatGPT direction reproduced at the preview root, with responsive navigation, interactive bureau tabs, customer-flow explanation, Evidence Vault, attorney-support positioning, and transparent pricing.
- Evidence Vault: government-ID verification and proof-of-error cards are present; real upload control is disabled; copy explicitly requires synthetic documents until private-storage staging passes; processing states are Upload -> Security scan -> Extract -> Review -> Confirm.
- Pricing status: under review and explicitly deferred to the next product task. The page states that no charges occur in the preview. Service bullets retain customized bureau/furnisher letters and customer approval before sending so the next pricing task can price the actual offer.
- Route safety repair: removed `dashboard.html` from Vite's build inputs. Built output contains no `dist/dashboard.html`; a fresh anonymous local request to `/dashboard` redirects to `/login` and renders the customer test-access screen.
- Tests: TypeScript typecheck PASS; scoped ESLint PASS for `src`, `api`, `vite.config.ts`, and the new preview script; Vite production build PASS with 1,592 modules and only the existing chunk-size warning; legacy dashboard absence assertion PASS; local CTA `/login` handoff PASS; Evidence Vault disabled-upload assertion PASS.
- Known limits: real identity/report uploads remain disabled; isolated Supabase/storage staging remains blocked by the separately recorded cost/access decision; no authenticated multi-user flow or real scanner execution is claimed by this visual preview.
- Rollback: remove the three preview assets and root rewrite, restore the legacy Vite input only if the obsolete unprotected static dashboard is deliberately needed under a non-colliding path. Do not restore it at `/dashboard`.
- Status: Ready for independent preview verification. Vercel preview deployment is held until the verifier checks the committed branch.
