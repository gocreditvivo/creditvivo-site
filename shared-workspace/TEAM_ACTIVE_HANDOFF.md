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

### Frontend WOW readiness command — 2026-07-26
- Founder direction: use Dovly as the primary observable frontend and customer-experience benchmark, then create an original Credit Vivo experience with a stronger genuine WOW factor.
- Official command: `shared-workspace/FRONTEND_WOW_BUILD_READINESS_2026-07-26.md`.
- Coordination branch: `coordination/frontend-wow-readiness-2026-07-26`.
- Current status: **PARTIALLY LINKED — ACKNOWLEDGEMENTS PENDING**.
- Verified: repository access, GitHub-to-Vercel connection, Vercel branch previews, root Vite + React + TypeScript stack, and separate Claude/Codex lanes.
- Not yet verified: Claude acknowledgement for the new command, Codex acknowledgement for the new command, current shared API/type/status contract, and Claude direct GitHub access.
- Expected Claude lane: `claude/frontend-wow-v1` or a clearly versioned offline package using synthetic data only.
- Expected Codex lane: `codex/frontend-wow-integration-v1` for interface contracts, integration, security, tests, and preview verification.
- Required acknowledgement format: `READY: [agent] | branch/package | owned files | dependencies | blockers | first checkpoint`.
- No production deployment is authorized by this readiness command.
