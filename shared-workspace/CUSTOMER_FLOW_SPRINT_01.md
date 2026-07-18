# Credit Vivo — Customer Flow Sprint 01

Date: 2026-07-18
Founder approval: Start building and testing the customer flow now. Use Credit Repair Cloud as a workflow reference, not as an unquestioned compliance or technical authority.

## Sprint goal

Create and test the first end-to-end Credit Vivo customer-flow foundation without mixing it into the scanner engine.

Target flow:

`Landing / Invite -> Account Creation -> Identity & Contact Details -> Required Disclosures -> Agreement & E-signature -> Billing Readiness -> Credit Report Connection / Import -> Import Status -> Scanner Processing Status -> Possible Issues -> Customer Review & Approval -> Admin Review -> Dispute Preparation -> Tracking -> Bureau Response -> Next Step / Escalation`

## Non-negotiable rules

- No real customer data in development or test environments.
- No automatic dispute sending.
- No automatic legal conclusions.
- No payment collection until the approved legal and billing sequence is implemented.
- No production use of the incomplete Credit Repair Cloud agreement template.
- Every sensitive action must be approval-gated and auditable.
- Customer portal and scanner engine remain separate modules connected by defined APIs/events.
- Founder must be able to see status, blockers, approvals, and failures.

## Codex ownership

Codex owns the backend contracts and integration foundation:

1. Audit the existing repository and identify reusable customer/auth/dashboard components.
2. Propose the customer-flow state machine and database schema.
3. Define secure roles: founder, manager, reviewer, customer, support, attorney-viewer where applicable.
4. Define status models for onboarding, agreement, billing readiness, report import, scan, review, approval, dispute round, mailing, response, and escalation.
5. Implement or scaffold secure APIs/events connecting the portal to the scanner without embedding scanner logic in UI code.
6. Add audit logging for every state change, approval, override, upload, and outbound action.
7. Add synthetic fixtures and automated tests.
8. Document migrations, files changed, tests, blockers, and next steps.

## Claude ownership — separate branch/module

Claude should handle a non-overlapping frontend/customer-experience package:

1. Review the approved customer flow and propose screen-level UX.
2. Build or prototype the customer onboarding shell and progress stepper.
3. Build the customer dashboard shell with status cards, next action, messages, documents, and progress timeline.
4. Build the founder/management dashboard shell with needs-attention, customer activity, scanner status, approvals, billing/cancellation alerts, and technical health placeholders.
5. Add frontend unit/component tests and accessibility checks.
6. Do not modify scanner parsing, rule-engine, Supabase migrations, or backend security files unless specifically reassigned.
7. Return branch, commit, files changed, tests, screenshots, limitations, and integration assumptions.

## ChatGPT ownership

- Finalize screen requirements and acceptance criteria.
- Map the Credit Repair Cloud reference flow into Credit Vivo-specific improvements.
- Define required customer, admin, founder, and compliance gates.
- Review Codex and Claude outputs for conflicts and missing requirements.
- Maintain the founder-facing status and decision log.

## Founder tasks

- Approve the legal company identity and business address to be used in customer documents.
- Select the intended pricing/billing model for attorney review.
- Continue walking through existing customer-flow screens and capture screenshots without credentials or customer data.
- Approve the first visual direction for customer and founder dashboards.

## Initial acceptance criteria

- A synthetic customer can move through the state model from invited to report-ready without touching production data.
- The system clearly distinguishes blocked, pending, completed, failed, and requires-review states.
- No dispute or external communication can be sent without required approvals.
- Every state transition is recorded with actor, timestamp, source, and reason.
- Customers cannot access another customer's records or documents.
- Managers cannot access founder-only secrets or destructive controls.
- Scanner status is visible, but scanner internals stay separate from frontend code.
- Automated tests cover happy path, failed import, missing signature, revoked consent, canceled customer, duplicate upload, low-confidence scan, and unauthorized access.

## Required handoff format

Each builder must provide:

- Scope completed
- Branch and commit
- Files changed
- Database migrations, if any
- Tests run and results
- Screenshots or demo notes
- Security impact
- Compliance/approval impact
- Known limitations
- Blockers
- Recommended next task
