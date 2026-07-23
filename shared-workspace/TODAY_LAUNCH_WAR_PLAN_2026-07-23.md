# Credit Vivo — Same-Day Scanner & Launch Readiness War Plan

**Date:** July 23, 2026  
**Founder directive:** Finish the scanner today and drive the platform to the strongest honest launch-ready state possible today.  
**Decision rule:** No one may label the product production-ready without test evidence. A safe private beta or controlled preview is acceptable if any production gate remains open.

## Team ownership

### Codex — Scanner, backend, security, integration lead
Codex owns the critical path. Work only on a dedicated branch such as `codex/scanner-launch-gate-2026-07-23`.

### Claude — Landing page, customer flow, dashboard, UX lead
Claude owns frontend integration and launch presentation. Work only on a separate branch such as `claude/launch-frontend-2026-07-23`.

### Grok — Independent adversarial QA and product audit
Grok must not make overlapping code edits. It reviews test evidence, attempts to break the scanner and customer flow, and returns defects with severity and reproduction steps.

### ChatGPT — Product owner, acceptance gates, coordination
ChatGPT maintains this plan, resolves requirements, reviews evidence, and reports the truth to Tim.

### Tim Do — Founder and release authority
Tim approves visual direction and decides whether to open a preview/private beta after all mandatory gates are reported.

---

# Definition of done for today

The scanner is considered **done for controlled beta** only when all mandatory gates pass:

1. Accepts supported PDF/TXT credit-report inputs and rejects unsupported/corrupt files safely.
2. Detects bureau/source and separates combined three-bureau reports where supported.
3. Parses consumer identity and negative tradelines with provenance to source page/section.
4. Produces normalized three-bureau comparisons without silently inventing data.
5. Flags missing, conflicting, duplicate, transferred/sold, date, balance, status, and bureau-presence issues as **possible issues**, not legal conclusions.
6. Masks account numbers consistently in every visible and hidden output, exposing no more than approved last-four identifiers.
7. Generates usable customer findings and draft evidence/output artifacts.
8. Preserves raw input, parser version, rules version, timestamps, confidence, and audit events.
9. Keeps customer cases isolated and prevents cross-user access.
10. Passes unit, integration, regression, security, and end-to-end tests using synthetic reports.
11. No automatic dispute sending.
12. No real customer data in development, CI, screenshots, or preview.

**Production launch requires all of the above plus:** verified authentication, RLS/data isolation, secret management, backups, monitoring, rollback, legal/compliance approval, vendor production credentials, payment readiness if payments are enabled, and founder approval.

---

# Execution sequence

## Phase 0 — Freeze and establish truth
**Owner: Codex**

- Read `AGENTS.md` or the current operating directive and all files in `shared-workspace/`.
- Post branch name, current commit, owned modules, test commands, environment assumptions, and blockers.
- Inventory the actual scanner entry points, parser modules, rules engine, exporters, API routes, database tables/migrations, and current tests.
- Run the existing test suite unchanged and record the baseline.
- Do not refactor unrelated code.

**Exit evidence:** baseline test report, architecture map, exact critical path, and blocker list.

## Phase 1 — Fix privacy-critical masking defect
**Owner: Codex; verifier: Grok**

- Reproduce the reported backward masking issue across every workbook sheet, hidden sheet, letter draft, JSON/API response, log, and UI fixture.
- Centralize identifier masking in one tested utility.
- Default output must be fully masked except approved last four characters where operationally required.
- Prevent raw identifiers from appearing in logs, exceptions, telemetry, filenames, snapshots, and generated letters.
- Add regression tests for short, long, formatted, blank, malformed, and already-masked identifiers.

**Hard stop:** No preview or generated output distribution until this gate passes.

## Phase 2 — Scanner accuracy completion
**Owner: Codex**

Build or repair the pipeline in this order:

1. File validation and malware-safe handling boundary.
2. Text extraction with deterministic fallbacks.
3. Bureau/report-format detection.
4. Section segmentation and page provenance.
5. Consumer identity normalization.
6. Tradeline extraction.
7. Negative-account classification: collections and charge-offs first.
8. Three-bureau account matching and normalization.
9. Issue rules with reason codes, confidence, source evidence, and plain-English explanation.
10. Export/API output with versioning and audit metadata.

Required issue families for today:
- Account missing from one or more bureaus.
- Conflicting account status, balance, dates, ownership, payment history, or remarks.
- Duplicate or possible duplicate debt.
- Sold/transferred account inconsistencies.
- Missing or conflicting DOFD-related data where available in the source.
- Collection original-creditor or classification gaps.
- Charge-off/collection balance and status inconsistencies.
- Identity/name/address/phone mismatches.

**Rule:** Missing data must remain null/unknown. Never infer a fact merely to complete a row.

## Phase 3 — Golden synthetic report suite
**Owner: Codex; verifier: Grok**

Create a versioned synthetic fixture pack covering:
- Experian-only, Equifax-only, and TransUnion-only reports.
- Three separate bureau reports.
- Combined three-bureau report.
- Clean report with no negative items.
- Collections and charge-offs.
- Duplicate tradelines.
- Sold/transferred accounts.
- Missing fields and conflicting dates/balances/statuses.
- OCR-like spacing/noise and reordered sections.
- Corrupt, encrypted, blank, oversized, and unsupported files.

For every fixture, maintain expected normalized JSON and expected findings. Tests must compare deterministic outputs and prohibit unexpected PII leakage.

## Phase 4 — Backend and case integration
**Owner: Codex**

Complete the controlled flow:

`case created → report uploaded/imported → scan queued → scan running → scan completed/failed → findings stored → customer review → customer approval → admin review → dispute draft prepared → tracking status`

Required controls:
- Authenticated case ownership.
- Role separation for customer/admin.
- RLS or equivalent server-enforced isolation.
- Signed/private file access.
- Idempotent scan jobs and retry safety.
- Rate limits and file-size limits.
- Audit events for sensitive actions.
- Safe errors that do not leak report contents or secrets.
- Status transitions validated server-side.

## Phase 5 — Frontend launch path
**Owner: Claude; API contract supplied by Codex**

Claude must implement only against the documented contract and must not alter scanner rules.

Required screens/states:
- Premium public landing page.
- Signup/login and disclosure/agreement status.
- Report connect/upload screen.
- Upload validation, progress, failure, and retry states.
- Scanner progress.
- Findings grouped by bureau/account with source evidence and confidence.
- Customer approval controls.
- Admin review queue.
- Dispute draft status and tracking timeline.
- Empty, blocked, unavailable, and support states.
- Responsive mobile layouts and accessibility basics.

Customer wording must say **possible report issues** and **draft dispute preparation**. Do not promise removal, score increase, approval, or legal outcome.

## Phase 6 — Adversarial QA
**Owner: Grok; fixes: Codex/Claude**

Grok independently attempts:
- Cross-account access.
- Direct URL/ID enumeration.
- Upload bypasses and malformed-file attacks.
- PII leakage through UI, exports, logs, errors, analytics, and hidden workbook sheets.
- Status-transition bypass.
- Duplicate scan/retry corruption.
- Incorrect account matching.
- False-positive and false-negative rule cases.
- Mobile and accessibility failures.
- Broken navigation and dead-end states.

Every finding must include severity, exact reproduction, expected behavior, actual behavior, affected files/routes, and recommended test.

Severity policy:
- **P0:** privacy, security, destructive corruption, cross-user exposure — immediate stop.
- **P1:** incorrect scanner output, broken core flow, missing audit trail — must fix before beta.
- **P2:** degraded UX or non-core defect — may ship only if documented and accepted.
- **P3:** polish/backlog.

## Phase 7 — Deployment and release gate
**Owners: Codex + Claude; verifier: Grok; approver: Tim**

Deploy first to a preview/staging environment using synthetic data.

Mandatory evidence:
- Build passes.
- Unit/integration/E2E/security tests pass.
- No exposed secrets.
- No real customer data.
- Database migration and rollback documented.
- Monitoring/error reporting configured without report-body or identifier leakage.
- Backup/restore path documented.
- Smoke test passes on desktop and mobile.
- Privacy masking test passes across all outputs.
- Known limitations listed.

Release classification must be one of:
- **Production approved** — every production gate passed with evidence and Tim approval.
- **Controlled private beta approved** — core and security gates passed, but one or more business/legal/vendor/production gates remain.
- **Preview only** — useful demonstration, but customer data must not be accepted.
- **Blocked** — any P0/P1 scanner, privacy, security, or data-isolation defect remains.

---

# Parallel work lanes

## Codex lane — no distractions
1. Baseline and inventory.
2. Account masking P0 fix.
3. Parser accuracy and provenance.
4. Golden fixtures and regression suite.
5. Backend case integration.
6. Security/data-isolation tests.
7. Preview deployment support.
8. Final evidence report.

## Claude lane
1. Read current API/status contract.
2. Finish the premium landing page and navigation.
3. Complete upload → scan → findings → approval → tracking UI.
4. Add loading/error/blocked/empty states.
5. Run frontend tests, accessibility checks, and mobile verification.
6. Produce preview screenshots and route checklist.

## Grok lane
1. Review this plan and current architecture without editing code.
2. Build a threat-and-failure checklist.
3. Audit Codex test fixtures and scanner outputs.
4. Attack privacy, data isolation, parsing accuracy, and workflow bypasses.
5. Re-test fixes.
6. Issue an independent pass/conditional pass/fail report.

---

# Handoff protocol for today

Each agent must update `shared-workspace/TEAM_ACTIVE_HANDOFF.md` at these checkpoints:

1. **Start:** branch, commit, owner, files/modules, baseline tests, blockers.
2. **Contract ready:** API schemas, statuses, events, data types, privacy rules.
3. **First integrated run:** input used, outputs, failures, screenshots/log references.
4. **Verification:** test commands, counts, defects, severity, fixes.
5. **Release gate:** classification, evidence, remaining blockers, rollback, founder approval status.

Do not report percentages without evidence. Report test counts and named gates instead.

---

# Codex immediate command

Read this file and `shared-workspace/TEAM_ACTIVE_HANDOFF.md`. Begin Phase 0 immediately. The first priority is to reproduce and permanently fix the account-number masking defect across every scanner output. Then complete the scanner using synthetic golden reports, integrate the authenticated case flow, and provide a release-gate report. Do not wait for Claude. Publish the API/status contract as soon as it is stable so Claude can integrate in parallel. Do not weaken privacy, security, auditability, or customer approval controls to meet the same-day target.
