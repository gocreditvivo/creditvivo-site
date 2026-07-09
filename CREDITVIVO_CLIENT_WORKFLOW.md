# CreditVivo Client Workflow

Created 2026-07-08.

Purpose: give CreditVivo a practical, compliant client workflow from lead to review to monthly follow-up. This is an operations document first. Later it can become the admin queue, client portal, and automation engine.

Compliance posture: no score guarantees, no deletion guarantees, no fake disputes, no promises to remove accurate negative information, no sensitive documents in the public intake form, and no attorney-client relationship unless counsel confirms representation.

## 1. Workflow Summary

CreditVivo should run every client through seven stages:

| Stage | Status | Main Goal | Owner |
|---|---|---|---|
| 1 | `new-lead` | Capture safe contact info and credit goal | Website / founder |
| 2 | `intake-review` | Understand goals, urgency, and risk | Founder / intake reviewer |
| 3 | `document-request` | Ask for reports and evidence through secure channel | Support |
| 4 | `file-analysis` | Identify possible inaccurate, incomplete, outdated, unverifiable, duplicate, mixed-file, or fraud-related items | Reviewer |
| 5 | `action-plan` | Give client a clear path: repair, build, protect, prepare | Reviewer / founder |
| 6 | `active-workflow` | Track disputes, client tasks, bureau/furnisher responses, and education tasks | Support / reviewer |
| 7 | `monthly-follow-up` | Review progress, update plan, and keep client informed | Support |

## 2. Stage 1 - New Lead

Public intake should collect only low-risk data:

- Name
- Email
- Phone
- Main goal
- Estimated score range
- Short notes
- Consent to be contacted
- Partner/referral source if applicable

Do not collect in the public form:

- SSN
- Full date of birth
- Credit report PDFs
- Account numbers
- Driver license / ID
- Bank statements
- Bureau login credentials
- Signature

Safe confirmation message:

> We received your request. CreditVivo will review your goal and follow up with the next safe step. Please do not send Social Security numbers, bureau passwords, IDs, or full account numbers by ordinary email or text.

## 3. Stage 2 - Intake Review

Reviewer classifies the lead:

| Track | Use When | Next Step |
|---|---|---|
| `repair-review` | Client says report has possible errors, collections, late payments, charge-offs, mixed files, fraud, or old items | Ask for credit reports and evidence through secure upload |
| `build-track` | Client has thin file, high utilization, few accounts, or needs positive habits | Give builder checklist and payment/utilization plan |
| `protect-track` | Client mentions identity theft, fraud alerts, unknown accounts, data breach, or family misuse | Give identity/fraud checklist and evidence list |
| `prepare-track` | Client needs mortgage, auto, apartment, employment, or funding readiness | Build approval-readiness checklist |
| `attorney-review-lead` | Client has lawsuit, garnishment, active legal threat, identity theft affidavit issue, or high-risk dispute | Prepare attorney eligibility packet, no legal promises |

Intake call questions:

1. What are you trying to get approved for?
2. When do you need it?
3. What credit reports have you reviewed?
4. What items do you believe are wrong or suspicious?
5. Do you have documents that support your position?
6. Have you already disputed before?
7. Any lawsuits, garnishments, bankruptcy, identity theft, or active collections?

## 4. Stage 3 - Document Request

Documents should be requested only through a secure portal or controlled upload process.

Request only what is needed:

- Credit reports from Equifax, Experian, and TransUnion
- Denial letter or adverse action notice, if goal-driven
- Collection letters
- Payment proof
- Settlement letters
- Identity theft report / FTC IdentityTheft.gov report if fraud-related
- Police report only if the client already has one; do not tell a client to make a false report
- Proof of address / identity only when needed and securely handled

Document handling rules:

- Classify every upload by type.
- Store securely.
- Do not put sensitive files in GitHub, public folders, ordinary screenshots, or unsecured email.
- Redact account numbers when possible.
- Keep a status history showing who reviewed what and when.

## 5. Stage 4 - File Analysis

Review each account or public-record item using an evidence-first checklist:

| Review Field | Questions |
|---|---|
| Identity | Does the account belong to the client? Any mixed-file signs? |
| Accuracy | Is balance, date, status, payment history, creditor, or account type wrong? |
| Completeness | Is key context missing, like paid/settled/discharged/transferred? |
| Timeliness | Is the item too old to report? |
| Duplication | Is the same debt reporting multiple ways incorrectly? |
| Verification | Can the client identify why the item may be unverifiable or unsupported? |
| Fraud | Is there evidence of identity theft, unauthorized account, or family misuse? |
| Goal Impact | Does this item matter for mortgage/auto/apartment/job/funding readiness? |

Allowed issue categories:

- Possible inaccurate reporting
- Possible incomplete reporting
- Possible outdated reporting
- Possible duplicate reporting
- Possible mixed-file reporting
- Possible identity theft / fraud reporting
- Possible unverifiable reporting
- Needs more evidence
- Accurate negative item; education/build strategy only

Do not create disputes for accurate negative information just because it hurts the score.

## 6. Stage 5 - Action Plan

Every client gets a plain-English plan:

- What we found
- What needs more evidence
- What can be addressed through dispute workflow
- What should be handled through habits/building
- What may need attorney review
- What the client should do this week
- What CreditVivo will do next

Safe wording:

> Based on the information reviewed, these items may need dispute review because they appear potentially inaccurate, incomplete, outdated, duplicate, unverifiable, mixed-file, or fraud-related. Results are not guaranteed, and credit bureaus/furnishers may verify or update information.

Avoid:

- "We will delete this."
- "Guaranteed removal."
- "Your score will increase."
- "This will get you approved."
- "We remove accurate negative items."

## 7. Stage 6 - Active Workflow

Active client records should have:

- Current stage
- Next action
- Due date
- Owner
- Client task list
- Evidence list
- Dispute issue list
- Bureau/furnisher routing
- Response tracking
- Monthly summary
- Compliance notes

Suggested workflow statuses:

```text
new-lead
intake-review
waiting-client-docs
documents-received
analysis-in-progress
needs-more-evidence
action-plan-ready
client-approved-plan
dispute-drafting
compliance-review
sent-to-client
sent-to-bureau-or-furnisher
waiting-response
response-received
updated-plan
monthly-follow-up
closed-complete
closed-inactive
attorney-review-lead
```

Dispute preparation checklist:

1. Confirm the disputed fact.
2. Attach or cite supporting evidence.
3. Identify the correct bureau/furnisher route.
4. Use client-specific facts.
5. Avoid template-only disputes that do not match the file.
6. Send only after client review/authorization.
7. Log date sent and expected follow-up window.

## 8. Stage 7 - Monthly Follow-Up

Monthly update should include:

- What was completed
- What is pending
- What responses came back
- What changed on the credit file, if known
- What the client needs to do next
- What CreditVivo will do next
- Reminder that results depend on facts, evidence, and bureau/furnisher investigation

Client update template:

> Quick CreditVivo update: we reviewed your file status and the next step is [next action]. We are still waiting on [response/document/task]. Please upload [specific item] when ready. We will update the plan after the next response or file review.

## 9. Attorney Review Triggers

Route to attorney eligibility review when:

- Active lawsuit
- Garnishment
- Judgment
- Threatened suit
- Bankruptcy questions
- Identity theft with creditor refusal
- Repeated verified reporting despite strong evidence
- FDCPA/FCRA damages question
- Client asks for legal advice
- Settlement negotiation is needed

Safe client message:

> This may need legal review. CreditVivo can help organize a case packet, but we are not your attorney and cannot promise legal outcomes. An attorney-client relationship exists only if a licensed attorney agrees to represent you.

## 10. Admin Queue Fields

Minimum fields for software build:

| Field | Example |
|---|---|
| Client name | Maria L. |
| Goal | Auto loan in 60 days |
| Track | repair-review |
| Stage | analysis-in-progress |
| Risk level | normal / high / attorney-review |
| Next action | Request Experian report |
| Due date | 2026-07-15 |
| Owner | Tim / support |
| Documents received | TU, EQ, collection letter |
| Missing documents | Experian, denial letter |
| Dispute issue count | 4 possible issues |
| Client task count | 2 |
| Last contact | 2026-07-08 |
| Next contact | 2026-07-12 |

## 11. Automation Roadmap

Phase 1: manual workflow

- Use this file as the checklist.
- Track clients in a spreadsheet or simple admin list.
- Use safe email/SMS templates.

Phase 2: admin queue

- Add client statuses in dashboard.
- Add task owner and due dates.
- Add document-needed checklist.
- Add monthly update generator.

Phase 3: secure portal

- Secure upload.
- Document classification.
- Client task list.
- Client-facing status page.

Phase 4: evidence-bound AI

- AI summarizes only uploaded evidence and report facts.
- AI suggests issue categories.
- Human/compliance review before client-facing dispute language.

## Sources Checked

- FTC Credit Repair Organizations Act: https://www.ftc.gov/legal-library/browse/statutes/credit-repair-organizations-act
- FTC Fair Credit Reporting Act: https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act
- CFPB credit report dispute guidance: https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/
- FTC consumer guidance on disputing credit report errors: https://consumer.ftc.gov/articles/disputing-errors-your-credit-reports-0
- CFPB credit repair enforcement / advance fee risk example: https://www.consumerfinance.gov/enforcement/payments-harmed-consumers/payments-by-case/lexlaw/
