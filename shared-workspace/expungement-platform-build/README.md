# Expungement Platform Build Control

This folder is the source of truth for the complete expungement-platform build.

## Operating rule

Build one phase at a time. Every phase must be independently verified.

- If a phase **passes**, record the evidence and move to the next phase.
- If a phase **fails**, stop, document the failure, fix it, rerun every failed and affected test, update the evidence, and verify again.
- No phase may be marked complete without evidence.
- No later phase may be used to hide or postpone a failed gate.
- Tim gives the final founder approval at each phase gate.

## Files

- `MASTER_BUILD_PLAN.md` — complete phased build scope.
- `CURRENT_STATUS.md` — live status and ownership.
- `PHASE_GATE_TEMPLATE.md` — required report after every phase.
- `VERIFICATION_MATRIX.md` — mandatory quality gates.
- `FAIL_FIX_WORKFLOW.md` — failure, remediation, retest, and escalation rules.
- `CLAUDE_DIRECTIVE.md` — frontend/content/UX instructions.
- `CODEX_DIRECTIVE.md` — backend/security/testing instructions.

## Status values

`NOT_STARTED` → `IN_PROGRESS` → `VERIFYING` → `PASSED`

Failure path:

`VERIFYING` → `FAILED` → `FIX_IN_PROGRESS` → `RETESTING` → `PASSED`

A phase is not complete when work is merely implemented. It is complete only when its required verification has passed and evidence has been recorded.
