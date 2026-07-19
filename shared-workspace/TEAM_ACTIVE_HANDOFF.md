# CreditVivo Team Active Handoff

Created: 2026-07-18

Purpose: one shared active coordination file for Tim, ChatGPT, Claude, and Codex.

## Standing Rules

- Act in CreditVivo's lawful best interests.
- Protect confidential information.
- Do not overlap edits without calling it out.
- Do not change production without Tim's approval.
- Report blockers, compliance risks, security risks, and data risks immediately.
- Do not copy competitor or vendor source code.
- Do not upload real customer credit data to outside tools.
- Keep scanner findings framed as possible issues requiring review.
- Keep dispute letters draft-only until approved.

## Team Roles

| Agent | Lane | Current Status |
|---|---|---|
| Tim | CEO/operator, business decisions, final approvals | Active |
| ChatGPT | Customer flow, CRC benchmark notes, copy, onboarding, sales, FAQ, compliance-friendly wording | Awaiting acknowledgement |
| Claude | Frontend/UX/customer-flow implementation engineer plus fresh-eye risk review | Read and acknowledged; offline package delivered, pending Codex verification |
| Codex | Scanner/backend, parser, tests, deploy, security, Mini Tim backend | Read and acknowledged |

## Codex Acknowledgement

Read and acknowledged. My current assignment is:

Build and verify the CreditVivo scanner/backend engine, especially credit report parsing, Metro 2-style field checks, three-bureau comparison, negative account definitions, skill/rule logging, draft-only letter timeline workflow, approval gates, and secure backend readiness.

## Codex Current Status

| Item | Status |
|---|---|
| Current local branch | `master` |
| Remote | `https://github.com/gocreditvivo/creditvivo-site.git` |
| Production changes | None approved from this handoff |
| Scanner parser | In progress and locally verified, with B-3 masking blocker now accepted |
| Customer flow | ChatGPT lane |
| Fresh-eye audit | Claude lane when Tim requests or when Codex asks |

## Codex Files Owned Right Now

| File/Folder | Purpose |
|---|---|
| `src/metro2-code-parser.js` | Metro 2-style field parser, field dictionaries, negative account profiles, skill logs |
| `src/report-parser.js` | Credit report parser wrapper and output contract |
| `scripts/parse-scanner-workbook-skill-log.js` | Parses scanner workbook and writes redacted skill/result log |
| `tests/metro2-code-parser-smoke.js` | Metro 2 parser smoke test |
| `tests/report-parser-smoke.js` | Report parser smoke test |
| `docs/METRO2_CODE_PARSER_SPEC.md` | Parser design and production validation notes |
| `handoff/` | Launch coordination docs |
| `shared-workspace/TEAM_ACTIVE_HANDOFF.md` | This active team handoff |
| `shared-workspace/SCANNER_MASKING_BLOCKER_B3.md` | Confirmed scanner masking blocker details |
| `shared-workspace/CLAUDE_FRONTEND_PACKAGE_REVIEW.md` | Claude frontend package intake notes and integration cautions |

## Codex Latest Verified Scanner Result

Source workbook:

`C:\Users\miste\OneDrive\Desktop\Documents\CV Scanner\scanner_backend\output\scan_10c98b18f088\credit_vivo_desktop_scanner_output.xlsx`

Generated local parser log:

`C:\Users\miste\OneDrive\Desktop\Documents\New project\scanner-output\metro2_skill_log_scan_10c98b18f088.json`

Summary:

| Metric | Count |
|---|---:|
| Account summary rows | 16 |
| Three-bureau field checks | 412 |
| Possible parser findings | 34 |
| Field boundary errors | 4 |
| Invalid field type errors | 14 |
| Invalid allowed value errors | 16 |

Skills/rules logged:

- `credit-report-parser`
- `creditvivo-compliance-reviewer`
- `metro2-code-parser`
- `negative-account-profile-engine`
- `three-bureau-comparison-review`

## Codex Verified Tests

```powershell
node --check src\metro2-code-parser.js
node --check src\report-parser.js
node --check scripts\parse-scanner-workbook-skill-log.js
npm.cmd run test:metro2-parser
npm.cmd run test:report-parser
npm.cmd run parse:workbook-skill-log
```

## Codex Blockers / Risks

| Risk | Status | Notes |
|---|---|---|
| Real customer data | Blocked until secure vault/auth/RLS are ready | Use dummy/redacted test data only. |
| Production deploy | Blocked until Tim approval and deploy audit | Do not promote without approval. |
| Metro 2 official certification | Open | Current parser is an original audit layer, not official CDIA CRRG certification. |
| Vendor tools | Later | BureauRelay/SwitchLabs only after company is formed and terms/privacy pass. |
| Legal/compliance | Open | Counsel review needed before paid credit repair, attorney claims, and automated workflows. |
| B-3 inverted account masking | Accepted by Codex | Confirmed in scanner workbooks. Account-like values in the form `digits + ****` appear in hidden sheets, including Draft Letters. Fix before using real reports or mailing/exporting letters. |

## API / Vendor Assumptions

- Supabase is not production-ready for real credit reports yet.
- Vercel static/public site is separate from secured backend work.
- BureauRelay/SwitchLabs can be considered later as lawful validation/QA, not as copied code.
- Credit Repair Cloud can be benchmarked from public materials or Tim/ChatGPT notes, not scraped private CRM content.

## Frontend Stack Answer For Claude

For the current local workspace, build against the CommonJS Node/server.js app in `C:\Users\miste\OneDrive\Desktop\Documents\New project`.

Current served UI files are root static files such as `index.html`, `admin.html`, `workflow-admin.html`, `client-status.html`, `styles.css`, and `script.js`, with backend routes in `server.js` and `src/app.js`.

Do not assume Vite unless Tim/Codex explicitly opens a Vite branch/package. If Claude has no repo access, deliver a self-contained offline package with route map, state model, components, mocks, and tests for Codex to land.

## Claude Frontend Package Intake

Claude reports an offline package named `CreditVivo_Frontend_Package.zip` with a 15-step journey, customer/manager/founder dashboards, role-gated routing, typed mock adapter, UI primitives, and tests.

Important integration caution: Claude's response says "root Vite + React + TypeScript," but the current Codex target is the CommonJS Node/server.js app with root static files. Treat Claude's package as a prototype/offline package until Codex verifies the files and Tim approves whether to integrate it as:

1. a separate Vite app/package,
2. a migration path from static root pages, or
3. design/spec reference only.

Claude could not run `npm install`, build, tests, or screenshots. Codex must verify before merge.

## Next Codex Checkpoint

First fix/contain B-3 scanner masking. After that, verify Claude's frontend package if Tim uploads/provides the zip. Then build the letter timeline queue from scanner findings:

1. `letter_type`
2. `recipient`
3. `possible_issue`
4. `raw_evidence`
5. `documents_needed`
6. `approval_status`
7. `deadline`
8. `next_review_date`
9. `skills_used`
10. `compliance_warning`

All letters remain draft-only.

## ChatGPT Reply Slot

Expected reply:

`Read and acknowledged. My current assignment is: ___`

## Claude Reply Slot

Expected reply:

Read and acknowledged. Claude current assignment is:

Frontend/UX/customer-flow implementation engineer. Claude will deliver an offline package named `offline-package/claude-frontend-journey-v1` because Claude has no repo write access. Claude owns proposed `src/journey/`, customer/founder dashboard flow specs, visual components, state-machine model, synthetic mocks, and frontend tests. Claude raised B-3 scanner masking as out of Claude scope and assigned it to Codex.
