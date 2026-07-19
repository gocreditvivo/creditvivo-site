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
