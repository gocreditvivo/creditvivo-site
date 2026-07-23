# Credit Vivo — P0 Scanner and Core Customer Flow Mission

**Issued:** July 23, 2026  
**Founder:** Tim Do  
**Release authority:** Tim Do  
**Status:** In progress — release blocked pending evidence

## Mission

Complete and verify:

> Upload → Scan → Findings → Customer Approval → Track Progress

No unrelated features, redesign detours, scope expansion, weakened security controls, automatic dispute sending, real customer data in development/preview, or production deployment without Tim's explicit approval.

## Task-start checkpoint

- **Current status:** P0 mission accepted; repository triage started; no production-readiness claim.
- **Branch:** `codex/p0-scanner-core-flow-2026-07-23`
- **Base commit:** `edb51f0a957fdf766c8126d882e3e99bded7dcde`
- **Assigned backend/security modules:** scanner/parser, bureau detection, account extraction, three-bureau matching, negative tradelines, possible inconsistency rules, masking, backend APIs, case relationships, Supabase/auth/RLS assumptions, audit events, regression tests, end-to-end verification, blocker report.
- **Assigned frontend modules:** upload and processing states, findings dashboard, three-bureau comparison, customer approval, progress tracker, customer/founder dashboards, mobile/accessibility, frontend tests, protected synthetic-data preview.
- **Baseline condition:** the repository contains plans and handoffs, but current evidence does not prove the complete authenticated customer journey, privacy, masking, isolation, or deployment gates pass.
- **Known P0 blocker:** alleged backward account-number masking in `credit-vivo-desktop-scanner-output__55_.xlsx`, reportedly affecting 299 cells, including 274 hidden Draft Letters. This remains unverified and release-blocking until reproduced, fixed at source, and regression-tested.
- **Other known blockers:** scanner production verification incomplete; Scan + Vault + Progress not yet proven as one authenticated case; auth/case isolation and RLS not proven; preview/deployment health not proven; OCR/parser accuracy not proven across supported formats.

## Immediate controls

1. Do not distribute or use the allegedly affected workbook or draft letters.
2. Do not use real customer data in development, tests, screenshots, or preview.
3. Do not deploy production or change production configuration.
4. Do not enable any automatic dispute submission.
5. Treat all scanner findings as possible reporting issues, not legal conclusions.
6. Stop release activity on any privacy, isolation, bureau-ID, parsing, matching, fabricated-finding, secret-exposure, or unsafe-deployment defect.

## First actions

1. Read `AGENTS.md`, `shared-workspace/TEAM_HANDOFF_PROTOCOL.md`, and active handoffs.
2. Inventory current scanner, API, auth, Supabase, storage, approval, and tracking implementation.
3. Reproduce and classify the masking defect across visible sheets, hidden sheets, letters, exports, logs, and fixtures.
4. Establish baseline tests using synthetic representative Equifax, Experian, TransUnion, combined, unsupported, malformed, and duplicate-account cases.
5. Document API contracts, status values, errors, approval events, audit events, and frontend/backend mismatches.
6. Fix in order: privacy → isolation → bureau detection → parsing → matching → findings → output → approval → tracking.
7. Run regression, security, frontend, integration, and end-to-end tests.
8. Produce a protected synthetic-data preview only after all pre-deployment gates pass.

## Required release classification

Use only: **APPROVED**, **CONDITIONALLY APPROVED**, **BLOCKED**, or **REJECTED**.

Current classification: **BLOCKED** — critical gates have not yet been demonstrated with evidence.
