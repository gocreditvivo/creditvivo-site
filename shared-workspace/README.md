# Credit Vivo Shared Workspace

This folder is the single coordination workspace for Tim, ChatGPT, and Codex.

## Roles

### Tim — Founder and final approver
- Approves pricing, customer promise, vendors, contracts, launch gates, and major product decisions.
- Controls GitHub, Vercel, Supabase, domains, email, payment, and vendor accounts.
- Provides real-world workflow feedback and approves launch readiness.

### ChatGPT — Product, customer flow, requirements, compliance design, and launch review
- Defines onboarding, customer portal, billing/signature sequence, dispute wizard UX, messaging, tasks, approval gates, customer-facing wording, and launch checklist.
- Builds and maintains validated requirements, including Metro 2 specifications and rule definitions.
- Reviews Codex output and translates technical decisions into plain English.

### Codex — Scanner, backend, security, testing, and deployment
- Builds credit-report parsing, three-bureau comparison, rule engine, raw evidence preservation, outputs, APIs, database, security, tests, deployments, and Mini Tim backend review assistant.
- Does not independently guess legal, compliance, business, or Metro 2 rules.

## Workspace structure

Use this folder for:

- `CURRENT_STATUS.md` — current project status and blockers
- `DECISIONS.md` — approved founder decisions
- `CHATGPT_TO_CODEX.md` — current implementation instructions
- `CODEX_TO_CHATGPT.md` — completed work, tests, errors, blockers, and next recommendation
- `LAUNCH_CHECKLIST.md` — launch gates and readiness
- `METRO2_REQUIREMENTS.md` — validated Metro 2 requirements and sources
- `CUSTOMER_FLOW.md` — onboarding, portal, billing, signature, dispute, and support flow
- `OPEN_QUESTIONS.md` — unresolved questions requiring Tim, attorney, vendor, or technical confirmation

## Operating rules

1. No feature is production-ready because the screen looks complete.
2. No Metro 2 rule is marked authoritative without a validated source and version.
3. Consumer PDF/TXT disclosures are not treated as original raw Metro 2 files.
4. Raw files and evidence must remain immutable and traceable.
5. Scanner findings must remain possible issues until supported and reviewed.
6. No dispute, complaint, legal conclusion, or customer communication is sent automatically without the required approval.
7. Codex records files changed, migrations, tests, results, errors, blockers, and next task after every run.
8. Tim receives decisions in plain English: issue, risk, recommendation, cost/time, and approval required.

## Current priority

Finish and validate the Credit Vivo scanner/backend before treating the customer-facing portal as launch-ready.
