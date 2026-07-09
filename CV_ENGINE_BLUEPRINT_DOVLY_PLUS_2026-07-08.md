# CV Engine Blueprint - Dovly Benchmark Plus

Created 2026-07-08.

Purpose: study Dovly's visible AI/product/process engines and define a stronger CreditVivo engine architecture before CreditVivo goes live.

This is a product and software design document. It does not assert access to Dovly's private code or internal systems. It only benchmarks public-facing product claims, pages, app listings, and observable workflows.

## 1. Dovly Visible Engine Model

Based on Dovly's public website, pricing page, app listings, and support pages, Dovly appears to operate around these visible engine layers:

| Dovly Layer | Public Evidence / Claim | Likely Function |
|---|---|---|
| Sign-up engine | Sign up in under 2 minutes; no hard pull | Fast consumer onboarding and identity/report connection |
| Credit data engine | Monthly TransUnion report on Free; weekly TransUnion report on Premium | Pull score/report and refresh changes |
| AI dispute engine | Manual dispute tool on Free; unlimited AI-powered disputes with TransUnion on Premium | Detect negative/inaccurate items and submit disputes on a cadence |
| Dispute optimization engine | Pricing FAQ says automated engine submits an optimal number of disputes each month based on credit report factors | Prioritize dispute volume/timing to maximize score movement or investigation outcomes |
| Credit builder engine | Premium includes eligible $2,000 builder line; subscription payments reported to TransUnion | Add positive tradeline/utilization/payment behavior |
| Monitoring/protection engine | Alerts, credit lock, data breach alerts, security score, ID theft insurance | Retention and risk/protection layer |
| Mortgage/goal engine | Mortgage content/tool pages and pre-approval positioning | Convert credit improvement into life-goal use cases |
| Mobile engagement engine | App-first experience, alerts, check-ins | Habit and retention loop |
| Proof/claims engine | Average score lift, total points increased, downloads | Conversion and trust/social proof layer |

## 2. Dovly Strengths To Study Closely

### 2.1 Layout And UX

Dovly's public UX is simple:

1. Join free.
2. No hard pull.
3. AI reviews report.
4. App gives plan.
5. Premium unlocks stronger tools.
6. User checks app for progress.

What CreditVivo should learn:

- First screen must show outcome, not internal complexity.
- User should understand the next step in less than 10 seconds.
- Free entry matters.
- App/status updates drive retention.
- Proof matters, but CreditVivo must avoid unsupported claims.

### 2.2 AI Process

Dovly's public AI promise is "we do the heavy lifting." The user does not need to understand dispute mechanics.

What CreditVivo should improve:

- Do not make AI a black box.
- Show why an item is being reviewed.
- Show evidence needed.
- Show confidence and risk.
- Add human/compliance review before action.

### 2.3 Dispute Workflow

Dovly appears TransUnion-centered publicly. It emphasizes automated disputes and optimal monthly dispute count.

CreditVivo should not copy blind automation first. Instead:

- Three-bureau comparison when data is available.
- Evidence-bound issue classification.
- Dispute readiness score.
- Human review checkpoint.
- Client authorization checkpoint.
- Audit trail.
- Escalation packet if repeated verified response conflicts with evidence.

### 2.4 Builder / Protection Layer

Dovly wins by bundling repair, builder, monitoring, protection, and insurance.

CreditVivo should partner first:

- Rent/bill reporting partner.
- Secured card/credit builder partner.
- Monitoring partner.
- Identity protection partner.
- Mortgage/auto/rental referral partners.

## 3. Better CV Engine Architecture

The CV Engine should be more than a dispute bot. It should be a decision system that answers:

> What is the safest, highest-impact next step for this client, given their goal, report facts, evidence, risks, and timeline?

## 4. CV Engine Layers

| Layer | Purpose | Build Status |
|---|---|---|
| CV Intake Engine | Classify lead by goal, score range, timeline, and risk | Started |
| CV Workflow Engine | Track stage, next action, missing docs, owner, due date | Started |
| CV Client Status Engine | Show safe client-facing status and expectations | Started |
| CV Evidence Engine | Store/classify uploaded reports and evidence securely | Not built |
| CV Report Parser | Extract accounts, dates, balances, statuses, bureau differences | Not built |
| CV Issue Classifier | Classify possible inaccurate/incomplete/outdated/duplicate/unverifiable/mixed-file/fraud items | Designed, not built |
| CV Dispute Readiness Engine | Decide if item has enough evidence for dispute drafting | Not built |
| CV Compliance Gate | Block guarantees, fake claims, unsupported disputes, legal advice | Partly in copy/docs |
| CV Goal Readiness Engine | Auto/mortgage/apartment/job/funding plan by timeline | Not built |
| CV Partner Engine | Track referral source and route client back when ready | Not built |
| CV Builder/Protect Engine | Match to builder, monitoring, identity tools | Not built |
| CV AI Summary Engine | Evidence-bound summaries for human review | Not built |
| CV Audit Engine | Immutable history of actions, messages, uploads, decisions | Not built |

## 5. CV Engine Workflow

### Step 1 - Intake

Input:

- Goal
- Timeline
- Score range
- Preferred contact
- Notes
- Referral source

Output:

- Track: repair, build, protect, prepare, attorney-review
- Priority
- Next action
- Documents needed

### Step 2 - Report/Evidence Intake

Input:

- Three-bureau report
- Creditor/collector letters
- Denial/adverse action letter
- Payment proof
- Identity theft documents if applicable

Output:

- Document classification
- Missing evidence list
- Sensitive data warning
- Review queue

### Step 3 - Report Parsing

Extract:

- Bureau
- Furnisher
- Account number masked
- Open/closed status
- Payment history
- Balance
- Date opened
- Date reported
- Date of first delinquency when visible
- Collection/charge-off flags
- Public record flags
- Inquiry flags

### Step 4 - Issue Classification

Classify each item:

- Possible inaccurate
- Possible incomplete
- Possible outdated
- Possible duplicate
- Possible mixed-file
- Possible fraud/identity theft
- Possible unverifiable
- Accurate negative; no dispute strategy
- Needs more evidence

### Step 5 - Dispute Readiness

Score each issue:

| Score | Meaning |
|---|---|
| 0 | Do not dispute; appears accurate or unsupported |
| 1 | Needs more evidence |
| 2 | Possible issue; human review |
| 3 | Strong issue; ready for draft |
| 4 | Strong issue with supporting evidence |
| 5 | Escalation candidate / attorney review |

### Step 6 - Human Review

Reviewer must confirm:

- The issue category matches evidence.
- Client's claim is supported.
- No fake identity theft or unsupported claim.
- No legal advice is being given.
- Client has authorized next step.

### Step 7 - Action Plan

The engine outputs:

- What to address
- What to ignore
- What to build
- What to protect
- What needs attorney review
- What partner path makes sense

### Step 8 - Client Status

Client sees:

- Current stage
- Next action
- Missing documents
- Review date
- Safe expectations
- Privacy reminder

Client does not see:

- Internal risk scoring
- Admin notes
- Legal conclusions
- Sensitive file paths
- Unsupported predictions

## 6. CV Engine Advantage Over Dovly

| Area | Dovly Style | Better CV Engine |
|---|---|---|
| AI dispute | Automated/optimized disputes | Evidence-bound dispute readiness with human review |
| Bureau scope | Publicly TransUnion-heavy | Designed for three-bureau comparison |
| Customer goal | Score/app improvement | Approval-readiness by goal |
| Workflow | App progress | Admin + client + partner workflow |
| Legal risk | App self-service | Attorney-review routing and packet prep |
| Human support | App/support team | High-touch guided review |
| Partner model | Consumer app first | Mortgage/auto/rental/tax partners first |
| Compliance | Marketing proof-heavy | Conservative, transparent, auditable |

## 7. CV Engine Product Screens Needed

### Admin

- Lead queue
- Promote to workflow
- Client workflow board
- Report/evidence review
- Issue classifier
- Dispute readiness score
- Compliance gate
- Attorney packet builder
- Partner referral tracker

### Client

- Status page
- Tasks and missing documents
- Secure upload
- Plain-English action plan
- Message/update history
- Goal readiness checklist

### Partner

- Referral form
- Customer opt-in link
- Referral status without private details
- Ready/not-ready milestone

## 8. Build Roadmap

### Phase 1 - Already Started

- Lead intake
- Admin lead dashboard
- Lead promotion
- Workflow API
- Workflow admin
- Client-safe status page
- Command center

### Phase 2 - Next

- Authentication
- Production database
- Secure upload
- Document classifier
- Client task portal
- Partner referral tracking

### Phase 3 - CV Intelligence

- Credit report parser
- Three-bureau comparison
- Issue classifier
- Dispute readiness score
- Evidence-bound AI summary
- Compliance gate

### Phase 4 - Marketplace / Partners

- Builder partner
- Rent/bill reporting partner
- Monitoring partner
- Identity protection partner
- Mortgage/auto/rental partner routing

### Phase 5 - Mobile/PWA

- Installable PWA
- Push/status reminders
- Client task notifications
- Partner referral alerts

## 9. First Real CV Engine Data Model

Core objects:

- Lead
- Client
- Workflow
- Task
- Document
- CreditReport
- Tradeline
- BureauDifference
- Issue
- Evidence
- ActionPlan
- DisputeDraft
- ComplianceReview
- PartnerReferral
- AuditEvent

## 10. Engine Guardrails

The CV Engine must never:

- Promise score increase.
- Promise deletion.
- Promise approval.
- Draft unsupported disputes.
- Create fake fraud/identity theft claims.
- Give legal advice.
- Send sensitive data through unsafe channels.
- Let AI act without human approval on high-risk issues.

## 11. Practical Conclusion

Dovly is the benchmark for:

- Simple consumer app
- Fast onboarding
- Credit data/monitoring loop
- Automated dispute cadence
- Builder/protection bundle
- Social proof

CreditVivo should build the better engine for:

- Messy files
- Evidence review
- Human/compliance oversight
- Approval goals
- Partner referrals
- Attorney escalation readiness

The stronger CV Engine is not "more automation." It is:

> Better decisions, better evidence, better workflow, and safer execution.

## Sources

- Dovly official site: https://www.dovly.com/
- Dovly pricing page: https://www.dovly.com/pricing/
- Dovly App Store listing: https://apps.apple.com/us/app/build-credit-fix-it-dovly/id1584248673
- Dovly Google Play listing: https://play.google.com/store/apps/details?id=com.dovly.app
- Dovly AI Credit Builder: https://www.dovly.com/ai-credit-builder/
- Dovly Credit Builder support: https://dovly.zendesk.com/hc/en-us/articles/32431004133015-Dovly-Credit-Builder-Eligibility-How-It-Works
- Dovly mortgage/pre-approval content: https://www.dovly.com/post/documents-needed-for-mortgage-pre-approval/
