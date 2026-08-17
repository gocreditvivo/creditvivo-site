# Credit Vivo — Team Active Handoff

This is the shared operating handoff for Tim Do, ChatGPT, Claude, and Codex through launch.

## Standing authority
Read and follow, in order:
1. `AGENTS.md`
2. `shared-workspace/TEAM_HANDOFF_PROTOCOL.md`
3. `shared-workspace/LAUNCH_RECOVERY_SPRINT_2026-07-29.md`
4. This file and the latest relevant PR evidence

## Current truth — July 29, 2026

- Overall release status: **Blocked pending current evidence**.
- The previous July 19 handoff was stale and did not prove current implementation, test, integration, or deployment status.
- The latest repository planning commit created a same-day launch plan, but a plan is not completion evidence.
- The account-number masking finding remains a P0 hard stop until Codex independently reproduces, fixes, regression-tests, and scans all synthetic outputs for leakage.
- No production approval is recorded.
- No agent may represent Credit Vivo as production-ready from old status notes, mock screens, or unverified test claims.

## Current objective
Complete and verify the integrated synthetic-data journey:

Invite → Sign up → Account setup → Disclosures → Agreement status → Credit report connection/upload → Import status → Scanner status → Possible issues → Customer review/approval → Admin review → Draft dispute preparation → Mail/tracking → Bureau response → Next action

## Active ownership

### Codex — backend/scanner/security critical path
- Required branch: `codex/launch-recovery-backend-2026-07-29`
- Execute Lane A in `LAUNCH_RECOVERY_SPRINT_2026-07-29.md`.
- First checkpoint: current commit, architecture inventory, baseline commands, exact test counts, blockers, and masking-defect determination.
- Must publish a versioned API/status/role contract before Claude connects live data.

### Claude — frontend/UX/customer journey
- Required branch: `claude/launch-recovery-frontend-2026-07-29`
- Execute Lane B in `LAUNCH_RECOVERY_SPRINT_2026-07-29.md`.
- First checkpoint: current commit, route/component map, build/tests, mock-vs-live inventory, preview status, and dependencies.
- Must not modify scanner rules, backend security, RLS, secrets, production migrations, or production deployment settings.

### ChatGPT — product owner and release-gate reviewer
- Maintains requirements and handoff truth.
- Reviews both PRs, resolves interface conflicts, and reports verified completion, blockers, risk, cost/access needs, and founder decisions.

### Tim Do — founder and final release authority
- Approves material visual/business decisions and any production release.
- Production approval is invalid without staging evidence, rollback, monitoring, privacy/security gates, legal/compliance review, and named remaining limitations.

## Immediate checkpoints required from both builders

1. **Task start:** branch, commit, owned files/modules, approach, dependencies, risks.
2. **Baseline truth:** exact build/test commands and pass/fail/skip results.
3. **Architecture/interface:** routes, states, roles, API/types, sensitive actions, privacy rules.
4. **First integrated synthetic run:** input, output, failures, screenshots/log references.
5. **PR verification:** files, migrations/policies, tests, security/accessibility impact, rollback, limitations.
6. **Release gate:** Blocked, Preview only, Controlled private beta, or Production approved—with evidence.

## Non-negotiable safeguards
- Synthetic data only outside approved production workflows.
- No automatic dispute sending.
- Scanner findings are possible report issues, not legal conclusions.
- No real customer data or secrets in commits, fixtures, screenshots, browser logs, analytics, or preview.
- Customer/admin authorization and case isolation must be server-enforced.
- No production deployment or customer-data intake without Tim's explicit approval.
- No unsupported percentages or claims of completion.

## Current coordination branch
- ChatGPT branch: `chatgpt/launch-command-reset-2026-07-29`
- Coordination artifact: `shared-workspace/LAUNCH_RECOVERY_SPRINT_2026-07-29.md`
- Next action: Codex and Claude create separate branches, post start checkpoints, execute their assigned lanes, and open separate evidence-backed PRs.
