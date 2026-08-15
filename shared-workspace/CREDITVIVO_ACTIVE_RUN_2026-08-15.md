# Credit Vivo — Active Run Handoff — 2026-08-15

Founder: Tim
Lead for this run: ChatGPT
Implementation/security verification partner: Codex
Production authority: Tim only

## Canonical implementation target

Repository: `gocreditvivo/main-2`
Branch: `codex/scanner-core-hardening`

## Current objective

Finish and verify the core customer journey:

Upload → Scan → Possible Issues → Customer Review/Approval → Admin Review → Packet Preparation → Tracking → Bureau Response → Next Action

## Confirmed repository state

- The active scanner implementation is in `gocreditvivo/main-2`.
- The current `src/pages/ScanTestPage.tsx` is malformed and cannot be treated as production-ready. It contains duplicated/partial functions, undefined state/variables, and a broken parse return path.
- A centralized privacy module exists at `src/scanner/privacy.ts` with last-four masking and leak-detection helpers.
- Production deployment remains blocked.

## ChatGPT-owned customer-flow work completed in this run

On `gocreditvivo/main-2` branch `codex/scanner-core-hardening`:

- `src/workflow/creditVivoCoreFlow.ts`
  - typed stages for report → scan → findings → customer approval → admin review → packet → tracking → response → next action
  - evidence references on every possible issue
  - explicit customer/admin/external-authorization gates
  - timeline event model
  - safe external-submission assertion

- `CREDITVIVO_CORE_FLOW_ACCEPTANCE.md`
  - release gates
  - customer finding-card requirements
  - approval behavior
  - tracking requirements
  - synthetic E2E acceptance test
  - release classifications

- `src/components/credit/FindingsReviewPanel.tsx`
  - evidence-first finding cards
  - Supported / Needs review confidence
  - Approve / Needs changes / Do not use controls
  - qualified customer language; no automatic send implication

- `src/components/credit/CaseProgressTimeline.tsx`
  - case/action timeline independent of credit-score history
  - current stage, owner, latest update, blocker, chronological events
  - explicit reminder that customer approval does not equal external submission

## Codex lane

Codex owns implementation/verification of scanner internals and data/security integration only:

1. Replace/repair malformed scanner monolith.
2. Wire centralized privacy/masking to every scanner output.
3. Confidence-aware bureau detection, including combined/ambiguous reports.
4. Bureau-specific tradeline extraction with missing values preserved as missing.
5. Conservative cross-bureau matching; uncertain matches do not merge silently.
6. Evidence-bound possible-issue findings; remove unsupported legal verdict language.
7. Integrate scanner output with customer-flow contract.
8. Verify RLS/customer isolation, secrets, audit events, bypass risks.
9. Run regression and synthetic E2E tests.
10. Do not deploy production.

## Product-language corrections required before preview approval

Existing UI copy that overstates capability must be replaced or qualified. Examples include claims equivalent to:

- AI selects the legally strongest dispute.
- A tradeline must be deleted immediately.
- Guaranteed or fixed score-point gains.
- Scanner findings are violations rather than possible issues requiring review.

Approved direction: plain-language observations tied to report evidence; customer decides what advances; admin review remains required.

## Release gates

BLOCKED until all of the following independently pass:

- scanner source builds cleanly
- sensitive-data masking/leak tests
- bureau detection tests
- tradeline extraction fixtures
- conservative matching tests
- evidence-required findings tests
- customer approval gating
- admin approval gating
- no automatic external submission
- case timeline persistence
- cross-customer isolation/RLS tests
- synthetic end-to-end flow

Allowed final classifications: APPROVED / CONDITIONALLY APPROVED / BLOCKED / REJECTED.

## Founder instruction

Tim authorized the team to finish Credit Vivo core work now. This is authorization to continue development and verification, not authorization to deploy production, spend money, submit disputes, or perform irreversible external actions.
