# CreditVivo Launch Handoff

Created: 2026-07-18

Purpose: shared launch coordination file for Tim, ChatGPT, and Codex.

## Operating Model

ChatGPT owns product flow, customer journey, copy, onboarding language, CRC-style workflow notes, sales scripts, FAQ drafts, and customer-facing clarity.

Codex owns scanner/backend engineering, parser logic, Metro 2-style field checks, tests, deployment health, security review, Supabase/Vercel implementation, workflow logic, and Mini Tim backend behavior.

Tim owns business decisions, legal/entity decisions, pricing approval, partner approval, production launch approval, and final compliance sign-off with qualified professionals where needed.

## Do First

1. Read this file.
2. Read `CREDITVIVO_PRODUCT_DECISIONS.md`.
3. Read `CREDITVIVO_SCANNER_BUILD_LOG.md`.
4. Read `CREDITVIVO_COMPLIANCE_QUESTIONS.md`.
5. Check `CREDITVIVO_CUSTOMER_FEEDBACK.md` for new notes from Tim or ChatGPT.

## Current Launch Posture

CreditVivo is in controlled demo / build mode.

Public positioning can show a waitlist, free review, credit path, scanner concept, and compliance-safe education.

Do not launch paid credit repair services, automated dispute mailing, real customer report uploads, attorney-service promises, SMS campaigns, or bureau/vendor integrations until the gates below are cleared.

## Launch Gates

| Gate | Status | Owner | Notes |
|---|---|---|---|
| Legal entity / EIN | Open | Tim | Required before vendor accounts and production customer flows. |
| Customer agreement / CROA review | Open | Tim + counsel | Required before paid credit repair service. |
| Privacy policy / data retention | Open | Tim + counsel/Codex | Must cover credit reports, IDs, authorizations, and deletion. |
| Secure auth / RBAC / audit logs | Open | Codex | Required before real customer data. |
| Supabase schema + RLS | Open | Codex | Test only until reviewed. |
| Report upload vault | Open | Codex | No real credit reports until secure storage is ready. |
| Scanner parser validation | In progress | Codex | Metro 2-style parser and skill logs started. |
| Letter workflow approval gates | Open | Codex + ChatGPT | Draft-only, no auto-send. |
| Attorney referral model | Open | Tim | LegalShield or partner model must be real before marketing. |
| SMS/A2P approval | Open | Tim + Codex | No customer SMS campaign until approved. |
| Vendor validation tools | Later | Tim + Codex | BureauRelay/SwitchLabs after company is formed. |

## Hard Rules

- Do not copy competitor or vendor source code.
- Do not upload real customer credit data to outside tools.
- Do not promise score increases, deletions, approvals, or timelines.
- Do not create fake identity-theft, fraud, or legal claims.
- Every scanner finding is a possible issue requiring review.
- Every dispute letter is draft-only until approved.
- Mini Tim is backend/founder assistant only unless Tim later changes that.

## Next Best Work

1. Codex: continue scanner/parser, field checks, evidence logs, timeline engine, and safe backend workflow.
2. ChatGPT: study CRC customer flow from screenshots/notes and turn it into CreditVivo customer journey requirements.
3. Tim: form company, decide partner/legal setup, and approve production posture.
