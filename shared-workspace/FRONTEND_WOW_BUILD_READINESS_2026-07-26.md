# Credit Vivo — Frontend WOW Build Readiness Command

**Issued:** 2026-07-26  
**Founder:** Tim Do  
**Status:** READY FOR TEAM ACKNOWLEDGEMENT — BUILD HAS NOT STARTED UNDER THIS COMMAND  
**Repository:** `gocreditvivo/creditvivo-site`  
**Official deployment project:** Vercel `creditvivo-site` (`prj_Ug2RUAMNwVHOw3UJy8khKFhXoSGX`)  
**Production approval:** Not granted

## 1. Founder direction

Build an original Credit Vivo frontend with a genuine **WOW factor** while using **Dovly as the primary customer-experience and frontend benchmark**.

Dovly is the baseline for:

- simplicity
- onboarding clarity
- easy navigation
- clean dashboard structure
- mobile usability
- low-friction customer progress

Credit Vivo must not copy Dovly source code, text, graphics, branding, or proprietary assets. The goal is to study observable UX patterns, then produce an original Credit Vivo experience that is simpler, more memorable, and more useful.

## 2. Product promise

The WOW must come from real product value and excellent execution—not hype that the product cannot prove.

### Required

- Real scanner states tied to actual application events or clearly labeled synthetic demo states.
- Clear, plain-English explanations of possible report issues.
- Transparent progress, evidence, approvals, and next steps.
- Premium visual polish, motion, responsiveness, and accessibility.
- Honest status language and visible limitations.

### Prohibited

- Fake score increases.
- Fake customer results.
- Fake AI percentages or confidence scores without a defined calculation.
- Fake progress bars that pretend backend work is happening.
- Guarantees that items will be removed or scores will rise.
- Automatic dispute sending at launch.
- Real customer credit data in development or preview.
- Competitor code, screenshots, logos, copy, or protected assets in the final product.

## 3. Primary experience goal

Within the first 10 seconds, a customer should understand:

1. Credit Vivo helps organize and explain credit-report information.
2. The scanner is the signature product.
3. The experience is simple, premium, and trustworthy.
4. The customer remains in control of approvals and next steps.

The customer should leave the first session thinking:

> “For the first time, I understand what may be affecting my credit report and what happens next.”

## 4. Approved technical baseline

The current root application is:

- Vite
- React 18
- TypeScript
- React Router
- Tailwind CSS
- Supabase client present, but production data integration remains approval-gated

Do not migrate frameworks or introduce a second frontend stack without a written architecture decision.

## 5. Team lanes

### Tim Do — Founder and final authority

- Approves the visual direction, major product choices, scope changes, and production release.
- Reviews the first-click experience, mobile experience, and overall WOW standard.
- May stop or redirect the build at any checkpoint.

### ChatGPT — Product, requirements, and coordination lead

- Owns this command, customer-flow requirements, Dovly benchmark interpretation, acceptance criteria, and founder reporting.
- Reviews architecture, copy, UX, screenshots, preview behavior, and evidence of completion.
- Resolves conflicts between frontend ambition and backend/security reality.
- Does not declare completion without code, tests, screenshots, and a working preview.

### Claude — Frontend/UX implementation owner

- Owns visual system, responsive layouts, onboarding, customer dashboard, scanner presentation, findings experience, progress timeline, accessibility, frontend tests, and interaction polish.
- Must use a dedicated branch or clearly versioned offline package.
- Current expected package/branch: `claude/frontend-wow-v1`.
- May use only synthetic/redacted data.
- Must not edit scanner rules, backend security controls, Supabase RLS/auth policy, production secrets, or production deployment settings.
- Because Claude has previously lacked authenticated repo access, Claude may deliver a self-contained package with exact file paths, route map, components, mocks, tests, screenshots, and integration notes for Codex to land.

### Codex — Integration, backend contract, security, and verification owner

- Owns API/type contracts, scanner/backend integration, secure state handling, role boundaries, route integrity, data isolation, secrets review, test reruns, preview verification, and integration of Claude’s package when needed.
- Current expected branch: `codex/frontend-wow-integration-v1`.
- Must not redesign Claude-owned UI files concurrently without a written transfer.
- Must report confirmed defects separately from preferences.

### Grok — Research and red-team lane

- May research public competitor UX, customer objections, trust failures, confusing credit-app patterns, and claims/compliance risks.
- Does not write production code or modify repository files unless expressly reassigned.
- Must cite public evidence and separate facts from opinions.

## 6. No-overlap branch rule

- Claude frontend work: `claude/frontend-wow-v1` or versioned offline package.
- Codex integration and verification: `codex/frontend-wow-integration-v1`.
- Coordination documents: `coordination/frontend-wow-readiness-2026-07-26`.
- `main` remains protected by founder approval and review.

Claude and Codex must list the exact files/modules they own before editing. Shared types, routes, APIs, and status values require an interface-ready handoff before either side changes them.

## 7. Phase 1 build scope

The first build must produce one connected, demonstrable path:

**Homepage → Join/Sign up → Account setup → Report connection/import → Scanner status → Findings → Customer approval → Progress timeline → Dashboard**

### Required screens and states

1. **Homepage**
   - Original Credit Vivo brand presentation.
   - Dovly-level simplicity.
   - Strong first visual moment without misleading claims.
   - One primary call to action.
   - Mobile-first layout.

2. **Join and onboarding**
   - Minimal steps.
   - Clear progress and save/resume behavior.
   - Disclosures and agreement status shown without overwhelming the customer.
   - Loading, empty, blocked, error, and success states.

3. **Report connection/import**
   - Clearly distinguish real integration, mock integration, upload, and unavailable states.
   - No fake connection to a bureau or vendor.
   - Explain what is happening in plain English.

4. **Scanner experience**
   - Show only actual backend events when integrated.
   - Synthetic demo events must be labeled as demo/mock data.
   - Avoid meaningless animation.
   - Visualize report organization, bureau comparison, and issue grouping without declaring legal violations.

5. **Findings**
   - Possible issues grouped by account and bureau.
   - Plain-English reason, source data, difference detected, documents needed, and next step.
   - Customer can review and approve or hold items.
   - No unsupported confidence or score-impact number.

6. **Progress timeline**
   - Clear sequence: imported, analyzed, findings ready, customer decision, admin review, preparation, submitted only when actually submitted, response, next action.
   - Dates and statuses must come from real data or be labeled demo values.

7. **Customer dashboard**
   - One clear primary action.
   - Current status, what changed, what is waiting, documents, and next step.
   - Avoid decorative widgets that do not answer a customer question.

8. **Founder/admin view**
   - Preview-only operational view for synthetic data.
   - Shows blockers, pending approvals, failed states, integration health, and customer-flow drop-off points.

## 8. Visual WOW standard

The first frontend is acceptable only when it demonstrates:

- a distinctive Credit Vivo visual identity
- premium typography and spacing
- polished but restrained motion
- meaningful transitions between scanner stages
- responsive behavior at 360, 390, 430, 768, 1024, and 1440 pixel widths
- clear hierarchy and readable contrast
- keyboard navigation and visible focus states
- reduced-motion support
- no horizontal overflow
- no placeholder-looking dashboard cards
- no broken links or dead buttons in the demonstrated flow

The standard is not “more effects.” The standard is clarity, confidence, speed, and memorability.

## 9. Acceptance gates

### Gate A — Team readiness

Before coding deeply, each active agent must post:

`READY: [agent] | branch/package | owned files | dependencies | blockers | first checkpoint`

No agent may claim another agent is ready without that acknowledgement or verifiable work product.

### Gate B — Architecture checkpoint

Claude provides:

- route map
- component/module map
- design tokens
- state model
- role model
- mock/service boundary
- motion plan
- accessibility plan
- test plan
- exact files owned

Codex reviews:

- route and state integrity
- API/type compatibility
- auth/role assumptions
- data isolation
- secret exposure
- backend event availability
- unsafe or fake status presentation

### Gate C — First visual proof

Required evidence:

- working homepage
- onboarding start
- scanner-status screen
- findings screen
- dashboard shell
- mobile screenshots
- desktop screenshots
- build/typecheck/lint results
- list of mock versus live elements

### Gate D — Preview verification

The Vercel preview must:

- build successfully
- use synthetic data only
- expose no secrets
- avoid production writes
- identify the source branch and commit
- include known limitations
- have no critical console errors
- pass route smoke tests

### Gate E — Founder review

Tim reviews the preview for:

- first 10-second reaction
- visual WOW
- simplicity compared with Dovly
- trust and clarity
- mobile usability
- whether the scanner feels like the signature product

Founder approval at this gate permits the next implementation slice—not production release.

## 10. Required quality evidence

Every completion report must include:

- objective
- branch/package
- commit or PR
- files changed
- route map
- screenshots or preview URL
- exact tests and results
- typecheck/lint/build results
- accessibility findings
- performance findings
- mock/live inventory
- security/privacy impact
- known limitations
- rollback notes
- blockers
- next recommended task

## 11. Current verified connections

- GitHub repository is accessible and writable: `gocreditvivo/creditvivo-site`.
- GitHub is connected to the official Vercel project `creditvivo-site`.
- Vercel is producing branch previews and production deployments from the repository.
- The latest observed Vercel previews were READY.
- This command does not authorize a production deployment.
- Claude’s direct authenticated GitHub access is not verified; use the offline package/handoff route until verified.

## 12. Immediate readiness request

### Claude

Read this file, then return the exact Gate A acknowledgement. Do not begin deep implementation until owned files and architecture are posted.

### Codex

Read `AGENTS.md`, `shared-workspace/TEAM_HANDOFF_PROTOCOL.md`, `shared-workspace/TEAM_ACTIVE_HANDOFF.md`, and this file. Return the exact Gate A acknowledgement and identify the current API/type/status contracts Claude can safely build against.

### Grok

Return a concise red-team brief covering Dovly-observable strengths, common customer trust failures, and claims/UX risks. Do not provide copied assets or code.

### ChatGPT

Maintain the source of truth, review all acknowledgements, resolve overlap, and report verified readiness to Tim.

## 13. Readiness definition

The team is **linked and ready** only when:

- GitHub/Vercel connection is verified.
- The active command is in the repository.
- Claude and Codex have separate lanes.
- Each active agent acknowledges its lane.
- Shared contracts and blockers are documented.
- No production action is implied or authorized.

Until those conditions are met, status must be reported as **PARTIALLY LINKED — ACKNOWLEDGEMENTS PENDING**.
