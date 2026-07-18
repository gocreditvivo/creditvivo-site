# Credit Vivo Team Handoff Protocol

This protocol governs handoffs among Tim, ChatGPT, Codex, and Claude before launch and after launch.

## Core rule
Handoffs happen when they are useful to protect quality, timing, security, and coordination—not only at the end of a task.

## Required handoff timing

### 1. Task start handoff
Update before coding begins when:
- a new task is accepted
- scope changes
- ownership changes
- another agent has a dependency

Include: objective, owner, branch, files/modules expected, dependencies, acceptance criteria, and estimated completion window.

### 2. Architecture/design checkpoint
Required before implementation when the task affects:
- database schema
- Supabase policies or authentication
- scanner/parser architecture
- shared APIs
- customer-flow state machine
- security model
- production deployment behavior

The other builder and ChatGPT must have a chance to identify conflicts before code is locked in.

### 3. Mid-task checkpoint
Required when:
- task exceeds one working day
- more than 10 meaningful files are changed
- a blocker appears
- assumptions change
- new migration/API/interface is introduced
- another builder may be affected

Give a concise status: completed, in progress, blocker, decisions needed, changed interfaces, and remaining estimate.

### 4. Immediate blocker or risk handoff
Do not wait for a scheduled update. Report immediately when:
- security vulnerability or possible data exposure is found
- production/staging is unavailable
- tests fail in a way that changes scope
- scanner output may be inaccurate or misleading
- secrets or customer data may be exposed
- a migration could be destructive
- Codex and Claude have file or interface conflicts
- legal/compliance wording or approval gates are uncertain

Stop risky work until the issue is resolved or explicitly approved.

### 5. Interface-ready handoff
Required as soon as one team member completes an interface needed by another, including:
- API contract
- TypeScript types
- database view/schema
- mock data format
- frontend component contract
- scanner output JSON/CSV structure
- authentication/role contract

Provide examples and version information so parallel work can continue safely.

### 6. Pull request / review handoff
Before merge, include:
- task objective
- branch and PR
- files changed
- screenshots for visual work
- migrations/policies
- tests and exact results
- security/compliance impact
- assumptions and known limitations
- rollback notes
- reviewer requested: Codex, Claude, ChatGPT, or human specialist

### 7. Pre-deployment handoff
Required before any staging or production deployment.

For staging:
- tests passed
- preview/staging URL
- test data only
- known issues listed

For production:
- staging accepted
- material risks resolved
- founder approval recorded
- backup/rollback plan ready
- monitoring plan ready
- no unresolved high-severity security or data-isolation issue

### 8. Post-deployment handoff
Update after deployment with:
- release time and commit
- environment deployed
- smoke-test results
- monitoring/log status
- incidents or regressions
- rollback performed or not needed
- next observation checkpoint

### 9. Task completion handoff
Required before ending the task. Include:
- completed deliverables
- branch/commit/PR
- files changed
- migrations and policies
- tests/results
- screenshots/demo notes
- security/compliance impact
- assumptions
- known limitations
- remaining blockers
- next recommended task

### 10. Daily and weekly handoffs
During active build:
- Daily: only when meaningful work, blockers, decisions, or interface changes occurred.
- Weekly: one consolidated founder-facing status covering progress, risks, tests, launch blockers, decisions, and next priorities.

## Task-size timing guide

### Small task — under 2 hours
- Start note when shared interfaces or risk are involved
- Completion handoff

### Medium task — 2 hours to 1 day
- Start handoff
- Completion handoff
- Immediate blocker updates as needed

### Large task — more than 1 day
- Start handoff
- Architecture checkpoint
- At least one mid-task update each working day
- Interface-ready handoffs
- PR review handoff
- Completion handoff

### Critical task — security, data, billing, compliance, production
- Start handoff
- Architecture/risk checkpoint
- Frequent updates at material milestones
- Human/founder approval where required
- Pre-deployment and post-deployment handoffs

## Claude ↔ Codex protocol
- Use separate branches.
- Do not edit the same files concurrently without a written transfer.
- When transferring ownership, list exact files/modules and the latest commit.
- Codex owns scanner/backend/security unless reassigned.
- Claude owns frontend/UX/integration unless reassigned.
- Shared API/type changes require an interface-ready handoff before either side proceeds.
- Each may review the other's PR, but should separate confirmed defects from preferences.

## Founder communication standard
Every material update to Tim should use:

`What happened → why it matters → recommendation → risk → time/cost → approval needed`

## Source of truth
- Persistent rules: `AGENTS.md`
- Team timing and handoffs: this file
- Current tasks: sprint/task files in `shared-workspace/`
- Technical evidence: GitHub branches, PRs, tests, commits, logs
- Business records: Credit Vivo Google Workspace
