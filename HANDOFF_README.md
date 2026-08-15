# Credit Vivo — Active Coordination Handoff

**Last reconciled:** 2026-08-15

## Current authority state

- **No production deployment is authorized by this handoff.**
- **Current implementation target is temporarily unresolved** because two active paths were observed at nearly the same time:
  - `gocreditvivo/main-2` / `codex/scanner-core-hardening` was named in the Relay implementation handoff.
  - `gocreditvivo/creditvivo-site` / `fix/next-production-ready` was the later observed local checkout, with pre-existing working-tree changes.
- Until one path is explicitly selected and checkpointed, **agents must not write scanner implementation code across both repositories.**
- ChatGPT owns coordination/reconciliation only for this checkpoint. Codex remains the implementation/testing/verification lane and is paused from Credit Vivo code changes until the repo/branch boundary is resolved.

## Current technical status

The scanner/hardening work is **not verified production-ready yet**. The active release gate is technical verification first, followed separately by founder-controlled legal/compliance/go-live approvals. Do not collapse those into one blocker.

Required checkpoint before implementation resumes:

1. Select exactly one canonical repository and branch.
2. Record current commit SHA and clean/dirty working-tree state.
3. List owned files for the next implementation task.
4. Define regression/security test commands and acceptance criteria.
5. Have Codex ACK the bounded implementation/verification task on the Relay.
6. Preserve customer/admin approval gates and do not deploy production without Tim approval.

## Coordination rule

Relay = live coordination and ACKs. This handoff = durable state. Repository + tests = implementation reality. If they conflict, stop writing code and reconcile first.

---

# Historical Credit Vivo v14.3 — Bolt / Webflow Handoff

This package includes the current Credit Vivo public site plus two handoff prompts:

1. `BOLT_NEW_BUILD_PROMPT.md`
2. `WEBFLOW_DESIGN_BRIEF.md`

## Best next step

Use Bolt.new first if you want a fast working visual rebuild.

Paste the full contents of:

`BOLT_NEW_BUILD_PROMPT.md`

into Bolt.new and upload this whole folder if Bolt asks for files.

## Webflow path

Use:

`WEBFLOW_DESIGN_BRIEF.md`

as the design brief for Webflow AI or a Webflow designer.

## Key design correction

The content is good. The next builder should focus on:
- Better visual balance
- Original illustrations
- Dashboard preview cards
- Smaller calmer typography
- More whitespace
- No repeated bottom buttons
