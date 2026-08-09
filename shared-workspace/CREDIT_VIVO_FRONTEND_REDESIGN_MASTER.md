# Credit Vivo Frontend Redesign — Master Build & Verification Plan

## Objective
Create a modern, bank-grade, simple, high-conversion Credit Vivo website and customer experience. The design should feel like a premium fintech product, not a traditional credit repair company.

## Core positioning
Primary headline: **AI Precision. Attorney Authority.**

Primary product idea: Credit Vivo helps customers understand possible credit-report issues, prepare customer-approved disputes, track progress, and access attorney support for eligible unresolved credit-reporting issues.

Preferred support line for lower sections: **Find errors. Build disputes. Track progress.**

## Audience
Primary customer: everyday consumer around a 600 credit score who wants a clear path toward a stronger credit profile, better approval opportunities, simple steps, visible progress, and support without technical jargon.

## Design direction
Use the following as inspiration only; do not copy proprietary layouts, copy, graphics, or claims.

- Dovly: simple onboarding, consumer-friendly credit journey, progress visualization.
- Credit Saint: clean plan presentation, trust structure, simple explanation.
- Lexington Law: attorney-support positioning and legal escalation concept.
- Chime: approachable financial language, large whitespace, friendly bank-grade simplicity.
- Brex: premium fintech visual hierarchy, dashboard-led product presentation, polished components.

### Visual rules
- Bank-grade, minimal, spacious, confident.
- No phone mockup in hero.
- No generic stock photos of call centers or attorneys shaking hands.
- Use score cards, dashboard components, progress visuals, clean product UI, icons, and subtle animation.
- Light background, navy/charcoal text, blue/emerald accents.
- One primary CTA color.
- Generous whitespace and short sections.
- Mobile-first.
- WCAG 2.2 AA target.

## Homepage architecture

### 1. Header
Left: Credit Vivo logo.
Center: How It Works, Why Credit Vivo, Pricing, Learn.
Right: Sign In + primary CTA **Get Started**.

### 2. Hero
Headline: **AI Precision. Attorney Authority.**

Subheadline: **Find possible credit-report issues, prepare smarter disputes, and track your progress in one secure place.**

Primary CTA: **Start My Credit Review**
Secondary CTA: **See How It Works**

Hero visual: premium dashboard preview showing:
- Credit score card
- Possible issues found
- Accounts under review
- Dispute progress
- Bureau response status
- Next recommended action

Do not show unsupported score increases, fake customer data, or guaranteed outcomes.

### 3. Fast value strip
Four concise benefits:
- AI-powered report analysis
- Three-bureau comparison
- Customer-approved dispute prep
- Attorney support for eligible unresolved issues

### 4. Score-goal section
Headline: **Know what may be holding your score back.**

Short copy: Credit Vivo organizes your credit data, highlights possible reporting issues, and gives you a clear action plan.

Cards:
- Payment history
- Credit utilization
- Collections / charge-offs
- Identity and account mismatches

### 5. Three-step flow
1. **Connect your credit** — upload or connect an approved report source.
2. **See possible issues** — review cross-bureau differences and potential inaccuracies.
3. **Approve your next steps** — prepare disputes, track responses, and escalate eligible unresolved issues.

### 6. Product dashboard section
Large dashboard preview with:
- Current score / score source label
- Score-factor cards
- Possible issue count
- Negative account summary
- Dispute rounds / status
- Mail tracking
- Bureau responses
- Attorney-support status where applicable

### 7. AI analysis section
Headline: **More than a credit report. A clearer picture.**

Explain in plain English that Credit Vivo compares bureaus, organizes negative items, identifies possible inconsistencies, and prepares draft next steps for customer review.

Important: scanner output is preliminary and not a legal conclusion.

### 8. Attorney support section
Headline: **When an issue stays unresolved, you may have another level of support.**

Copy: **Attorney support may be available for eligible unresolved credit-reporting issues.**

No implication that every customer receives legal representation.

### 9. Progress / tracking section
Headline: **See what is happening at every step.**

Show timeline:
- Report connected
- Review complete
- Possible issues found
- Customer approved
- Dispute prepared
- Sent / tracked
- Bureau response received
- Next action ready

### 10. Pricing
Keep simple and transparent. Do not invent pricing. Use placeholders until Tim approves final plans.

Each plan should show:
- Monthly price
- What is included
- Credit report / monitoring terms
- Attorney-support eligibility language
- Cancellation terms

### 11. FAQ
Core questions:
- How does Credit Vivo work?
- Does Credit Vivo guarantee a score increase?
- What kinds of credit-report issues can Credit Vivo identify?
- Do I approve disputes before they are prepared or sent?
- How are disputes tracked?
- What happens when a bureau responds?
- Is Credit Vivo a law firm?
- When might attorney support be available?
- How is my information protected?
- Can accurate information remain on my report?

### 12. Final CTA
Headline: **Your credit deserves a closer look.**
CTA: **Start My Credit Review**

### 13. Footer
Links:
- Terms
- Privacy
- Security
- Accessibility
- CROA disclosures
- FCRA information
- State disclosures
- Contact
- Cancellation / refund policy

Keep required compliance disclosures in the footer / FAQ / legal pages unless a disclosure is legally required earlier in the flow.

## Customer application architecture

### Public
- /
- /how-it-works
- /pricing
- /learn
- /security
- /faq
- /login
- /signup

### Customer journey
- /onboarding
- /disclosures
- /agreement
- /credit-connect
- /import-status
- /review
- /issues
- /approval
- /disputes
- /tracking
- /responses
- /next-actions

### Customer dashboard
- /dashboard
- /dashboard/score
- /dashboard/accounts
- /dashboard/issues
- /dashboard/disputes
- /dashboard/tracking
- /dashboard/responses
- /dashboard/documents
- /dashboard/support
- /dashboard/profile
- /dashboard/security

### Founder/admin
- /admin/overview
- /admin/customers
- /admin/reviews
- /admin/disputes
- /admin/responses
- /admin/attorney-escalations
- /admin/audit

## Product states
Every major screen must support:
- Loading
- Empty
- Success
- Warning
- Error
- Blocked
- Needs customer action
- Needs admin review
- Needs attorney review

No dead buttons. Any unavailable action must be visibly disabled with an explanation.

## Verification model
No phase advances on visual appearance alone.

### Phase 1 — Architecture + wireframes
Deliver:
- Route map
- Homepage wireframe
- Customer dashboard wireframe
- Mobile wireframe
- Design tokens
- Component map
- Content map

Verify:
- Founder product fit
- No missing customer stage
- No unsupported marketing claims
- Mobile flow is understandable
- Competitor inspiration is transformed, not copied

Result: PASS / FAIL

If FAIL: fix all failed items, update evidence, re-test. Do not start Phase 2.

### Phase 2 — Design system + homepage
Deliver:
- Header
- Hero
- Dashboard visual
- Core sections
- Pricing framework
- FAQ
- Footer
- Responsive variants

Verify:
- Desktop + mobile screenshots
- Contrast and accessibility
- CTA consistency
- No fake statistics / testimonials
- No unsupported score claims
- No broken navigation

Result: PASS / FAIL

### Phase 3 — Frontend customer journey
Deliver full mock-data flow from signup through next action.

Verify:
- Every route loads
- State transitions are deterministic
- Back/forward works
- Save/resume behavior is represented
- Error/blocked states exist
- All customer approvals are explicit
- No automatic dispute sending

Result: PASS / FAIL

### Phase 4 — Customer dashboard
Deliver all dashboard modules and responsive navigation.

Verify:
- Score source/date is visible
- Possible issues are labeled as preliminary
- Customer cannot confuse a draft with a sent dispute
- Status labels match backend contract
- No dead controls

Result: PASS / FAIL

### Phase 5 — Backend/API integration
Codex-owned verification.

Verify:
- Typed API contracts
- Import/scanner/dispute statuses match frontend
- Auth enforced server-side
- RLS/data isolation tests pass
- No production secrets in client code
- Error responses handled safely

Result: PASS / FAIL

### Phase 6 — Scanner integration
Verify:
- Scanner output is draft/preliminary
- Account identifiers are correctly masked
- No cross-customer data exposure
- Three-bureau matching is correct on test fixtures
- Missing/conflicting fields surface to customer/admin correctly

Result: PASS / FAIL

### Phase 7 — Dispute + tracking integration
Verify:
- Customer approval gate exists
- Admin review gate exists where required
- Mail tracking states are accurate
- Bureau response parsing maps correctly
- No automatic sending at launch

Result: PASS / FAIL

### Phase 8 — Security + privacy
Verify:
- Auth
- MFA where enabled
- Session expiration
- RLS
- Storage access
- Secrets
- Logging / redaction
- Audit events
- File permissions
- Data retention
- Dependency scan

No open critical/high launch blockers.

Result: PASS / FAIL

### Phase 9 — End-to-end testing
Run Playwright / browser tests for:
- New signup
- Returning login
- Disclosure / agreement flow
- Credit connection/import
- Scanner success
- Scanner failure
- Possible issues review
- Customer approval
- Admin review
- Dispute prep
- Tracking
- Bureau response
- Next action
- Mobile journey
- Accessibility keyboard journey

Result: PASS / FAIL

### Phase 10 — Preview / founder approval
Deliver:
- Vercel preview URL
- Desktop screenshots
- Mobile screenshots
- Test results
- Known limitations
- Security findings
- Data used = synthetic only
- Rollback path

Tim approval required before production deployment.

## Failure rule
For every phase:
1. Build.
2. Run verification.
3. If PASS: document evidence and move forward.
4. If FAIL: stop.
5. Identify root cause.
6. Fix.
7. Add or update regression test.
8. Re-run full phase verification.
9. Update handoff.
10. Move forward only after PASS.

## Required phase report
```
PHASE:
STATUS: NOT STARTED / IN PROGRESS / BLOCKED / PASS / FAIL
OWNER:
FILES CHANGED:
WORK COMPLETED:
TESTS RUN:
TEST RESULTS:
ACCESSIBILITY:
SECURITY IMPACT:
COMPLIANCE IMPACT:
SCREENSHOTS / EVIDENCE:
FAILURES:
FIXES:
RETEST RESULTS:
BLOCKERS:
NEXT CHECKPOINT:
TIM APPROVAL: PENDING / APPROVED
```

## Ownership
- Tim: founder approval, business/visual/pricing/legal/vendor decisions.
- ChatGPT: product direction, copy, customer flow, acceptance criteria, phase gates, coordination.
- Claude: frontend, UI/UX, accessibility, responsive implementation, preview.
- Codex: backend/API/scanner/security/RLS/data isolation and independent verification.
- Attorney/compliance reviewer: legal claims, CROA/FCRA/state-specific required disclosures and attorney-service boundaries.

## Immediate next checkpoint
Claude should produce Phase 1 only:
1. Homepage desktop wireframe.
2. Homepage mobile wireframe.
3. Customer dashboard wireframe.
4. Route map.
5. Design tokens.
6. Component map.
7. Final proposed homepage copy.
8. Assumptions / blockers.

Stop for review before full visual implementation.
