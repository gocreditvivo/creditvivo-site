# Credit Vivo Best-in-Class Flow + Architecture
## A+ Fintech-Grade Customer GUI, Admin System, Scanner, Compliance, and Scalable Build Plan

Version: `credit-vivo-best-flow-architecture-2026.07.03-v1`

## Goal

Build Credit Vivo as a better, safer, smarter platform than a standard credit repair CRM.

Credit Vivo should combine:

- Dovly-style simplicity and AI-first customer experience
- Sky Blue-style client portal, progress, messaging, and dispute cycles
- Credit Saint-style full-service challenge positioning
- Credit Vivo’s own v9 forensic workbook and v17 safety/compliance layer

Final positioning:

**AI Credit Boost + Attorney Support**

Slogan:

**You take control. We clear the path.**

Trust line:

**Find errors. Build disputes. Track progress.**

---

# 1. Best Credit Vivo Customer Flow

```text
Lead → Sign Up → Goal Selection → Upload Reports → AI Review → Findings Summary → Review Accounts → Approve Drafts → Admin QA → Mail/Submit → Track Progress → Response Review → Next Round → Attorney Support Review if Eligible
```

## Step 1 — Lead Capture

Capture:

- name
- email
- phone
- credit goal
- consent
- lead source
- preferred contact method

Customer goal options:

- car loan readiness
- mortgage readiness
- apartment readiness
- credit card approval
- insurance readiness
- job/background readiness
- business funding readiness
- general credit boost

## Step 2 — Sign Up / Member Account

Required:

- email verification
- consent checkbox
- privacy/terms acknowledgment
- no payment until compliance-approved flow is ready

## Step 3 — Goal Dashboard

Customer sees:

- score goal
- target opportunity
- progress steps
- next action
- report upload status

Customer does not see:

- raw Metro 2
- scanner rule IDs
- admin QA
- raw credit report text

## Step 4 — Report Upload

Customer uploads:

- Equifax
- Experian
- TransUnion

Upload statuses:

- not uploaded
- uploaded
- processing
- needs review
- complete
- blocked

Security:

- file validation
- encrypted storage
- source hash
- upload audit log
- no real reports in GitHub or ordinary cloud sync

## Step 5 — AI Review

Customer sees:

- review items found
- possible errors
- draft letters ready
- positive accounts kept
- next step

Admin sees:

- scanner health check
- raw evidence
- v9 workbook
- ground-truth validation
- QA verification
- production gate

## Step 6 — Review Accounts

Customer account cards show:

- account name
- bureau(s)
- issue type
- why it may matter
- recommended next step
- review draft button

Safe language:

- may need review
- appears inconsistent
- should be verified
- possible reporting issue

Blocked language:

- illegal
- guaranteed deletion
- guaranteed score increase
- lawsuit guaranteed

## Step 7 — Draft Approval

Customer sees:

- letter summary
- account
- bureau/furnisher
- evidence summary
- requested verification/correction
- approval checkbox

Hard rule:

**No letters are sent without customer approval.**

## Step 8 — Admin QA

Admin checks:

- raw evidence exists
- verified issue object exists
- safe letter wording
- customer approval
- no positive-account false dispute
- production gate passed

## Step 9 — Mail / Submit

Options:

- certified mail
- future Lob integration
- manual export
- secure PDF packet

Required:

- delivery tracking
- audit log
- packet hash
- vault copy

## Step 10 — Progress Tracker

Customer timeline:

1. Reports uploaded
2. AI review complete
3. Drafts ready
4. Customer approved
5. Admin reviewed
6. Mailed/submitted
7. Waiting for response
8. Response received
9. Next action

## Step 11 — Response Review

Customer uploads bureau/furnisher response.

System/admin:

- parse response
- classify result
- update account status
- prepare next action:
  - wait
  - update report
  - second dispute
  - method of verification
  - complaint packet
  - attorney support review if eligible

## Step 12 — Attorney Support Eligibility

Only if:

- unresolved credit-reporting issue
- evidence exists
- dispute history exists
- customer approval exists
- admin/compliance approval exists

Safe wording:

**Attorney support may be available for eligible unresolved credit-reporting issues.**

---

# 2. Best Admin Flow

```text
Contact Board → Customer Profile → Report Intake → Scanner Health Check → v9 Workbook → Ground Truth → QA → Letters → Customer Approval → Admin Approval → Mail Tracking → Response Parser → Next Round → Escalation
```

Admin modules:

1. Contact board
2. Customer profile
3. Report intake
4. Scanner jobs
5. v9 workbook viewer
6. Raw evidence index
7. Ground truth validation
8. QA verification
9. Production gate
10. Letter review
11. Approval center
12. Mail tracking
13. Response parser
14. Dispute cycle manager
15. Complaint packet builder
16. Attorney support review
17. Vendor/API logs
18. Security audit logs
19. Admin tasks
20. Compliance flags

---

# 3. Contact Board Flow

Board columns:

1. New Lead
2. Contacted
3. Report Needed
4. Scan Ready
5. Findings Ready
6. Drafts Ready
7. Active Customer
8. Waiting for Response
9. Follow-Up Needed
10. Closed / Won / Lost

Each card shows:

- name
- phone
- email
- goal
- source
- stage
- last contact
- next action
- reports uploaded
- scan status
- findings status
- drafts status
- approval status
- payment status
- compliance flag
- assigned admin
- notes

Rules:

- no risky auto-send
- approved templates only
- no dispute/complaint/legal action without approval

---

# 4. Customer GUI Structure

Routes:

```text
/
 /signup
 /login
 /member
 /member/upload
 /member/findings
 /member/accounts
 /member/disputes
 /member/progress
 /member/documents
 /member/messages
 /member/profile
 /member/settings
 /member/security
 /member/billing
 /member/support
```

Key components:

- HeroSection
- GoalSelector
- SignupForm
- MemberShell
- PortalGateBanner
- UploadReportCard
- ReportStatusGrid
- FindingSummaryCards
- NegativeAccountCard
- PositiveAccountsKeepCard
- DisputeDraftReviewCard
- ApprovalCheckbox
- ProgressTimeline
- DocumentVaultList
- SecureMessageList
- ProfileSummary
- SecurityStatusCard
- BillingStatusCard
- SupportRequestForm

---

# 5. Admin GUI Structure

Routes:

```text
/admin
/admin/contacts
/admin/customers
/admin/customers/:id
/admin/scans
/admin/scans/:scanId
/admin/workbooks
/admin/evidence
/admin/qa
/admin/letters
/admin/approvals
/admin/mail
/admin/responses
/admin/complaints
/admin/attorney-review
/admin/vendors
/admin/audit-logs
/admin/settings
```

Key components:

- AdminShell
- ContactBoard
- ContactCard
- CustomerProfilePanel
- ReportUploadStatus
- ScannerHealthCheckPanel
- V9WorkbookPreview
- RawEvidenceTable
- GroundTruthValidationPanel
- QAVerificationPanel
- ProductionGatePanel
- LetterReviewPanel
- ApprovalQueue
- MailTrackingTable
- ResponseParserPanel
- DisputeCycleTimeline
- ComplaintPacketBuilder
- AttorneyEligibilityPanel
- ComplianceFlagBadge
- AuditLogTable
- VendorRiskTable

---

# 6. Scanner / Backend Architecture

Recommended services:

```text
apps/
  web/                 # Next.js customer/admin front end
  api/                 # backend API
  worker/              # async scanner jobs

packages/
  scanner-core/
  scanner-v9-exporter/
  compliance-rules/
  letter-engine/
  security-vault/
  shared-types/
```

Backend modules:

```text
scanner/
  intake.py
  file_security.py
  text_extraction.py
  bureau_detection.py
  section_classifier.py
  account_block_extractor.py
  field_extractor.py
  evidence_model.py
  account_matcher.py
  negative_classifier.py
  positive_separator.py
  issue_engine.py
  metro2_review.py
  fcra_review.py
  letter_engine.py
  dispute_workflow.py
  response_parser.py
  license_checker.py
  ground_truth_validator.py
  health_check.py
  workbook_v9_exporter.py
  customer_summary.py
  admin_audit.py
  security_audit.py
  production_gate.py
```

---

# 7. Tech Stack Recommendation

Front end:

- Next.js App Router
- TypeScript
- Tailwind CSS
- accessible component library or custom components
- Zod for validation
- TanStack Query if client API state is needed

Backend:

- FastAPI
- Pydantic
- PostgreSQL
- Redis queue
- Python worker
- SQLAlchemy / Alembic

Recommended architecture:

**Next.js front end + FastAPI scanner backend + Python worker + PostgreSQL + Redis**

Storage:

- PostgreSQL for structured data
- encrypted object storage for reports/workbooks
- local encrypted vault for desktop scanner
- S3-compatible storage only after security review

Auth:

- MFA for admins
- role-based permissions
- customer session protection

Security:

- encryption at rest
- encryption in transit
- audit logs
- file hashes
- source hashes
- signed URLs
- short-lived access
- secret management
- dependency scanning
- SAST/secret scan
- OWASP ASVS baseline

---

# 8. Data Model

Core tables:

```text
users
organizations
customers
contacts
contact_events
lead_sources
files
scan_jobs
raw_pages
raw_blocks
tradelines
field_evidence
account_groups
negative_classifications
issue_findings
positive_accounts
workbooks
letters
approvals
dispute_rounds
mail_packets
mail_tracking
bureau_responses
response_findings
complaint_packets
attorney_reviews
collector_license_checks
vendor_connections
audit_logs
security_events
production_gates
```

---

# 9. Permission Model

Roles:

- customer
- support_admin
- scanner_admin
- compliance_admin
- founder_admin
- attorney_review_partner
- read_only_auditor

Default:

- customer sees only customer-safe summary
- admin sees evidence based on role
- attorney partner sees only approved packet
- raw report access is logged every time

---

# 10. Production Safety Gates

Customer-visible result requires:

```text
health_check_passed = true
ground_truth_passed = true
qa_verification_passed = true
security_audit_passed = true
production_gate_passed = true
```

A letter is visible only if:

```text
verified_issue_object_exists = true
raw_evidence_exists = true
safe_language_passed = true
letter_status = draft_only
```

A letter can be mailed only if:

```text
customer_approved = true
admin_approved = true
delivery_method_selected = true
audit_log_created = true
```

Escalation can occur only if:

```text
dispute_history_exists = true
response_evidence_exists = true
customer_approved = true
admin_compliance_approved = true
```

---

# 11. v9 / v17 Scanner Standard

v9 required sheets:

- Dashboard
- Account_Summary
- Ours 3 Bureaus Comparison
- Identity_Cleanup
- Negative_Definitions
- License_Check
- State_License_Links
- Dispute_Cycle_Status
- Exact_Letters_To_Mail
- Escalation_Addresses
- Complaint_Packet
- FICO_Scenario_Planner
- Codex_Build_Task
- Read_Me_v9

v17 additions:

- Raw_Evidence_Index
- Ground_Truth_Validation
- QA_Verification
- Security_Audit_Summary
- Production_Gate
- Positive_Accounts_Keep

Main sheet structure:

```text
Row 1: title
Row 2: source/counts
Row 3: note
Row 4: headers
Row 5+: field-by-field account rows
```

Minimum per negative account:

- 18 field rows

Target:

- 25 field rows

---

# 12. Customer Messaging Standard

Use:

- possible error
- may need review
- should be verified
- dispute draft
- no letters sent without approval
- results are not guaranteed

Avoid:

- guaranteed deletion
- guaranteed score increase
- illegal
- lawsuit guaranteed
- remove all negatives
- attorney included for everyone

---

# 13. Better Than Competitors: Credit Vivo Differentiators

Credit Vivo should win with:

1. AI-first simple customer dashboard
2. 3-bureau upload/review
3. v9 forensic workbook behind admin
4. v17 safety gates
5. raw evidence per field
6. ground-truth validation
7. strict positive/negative classifier
8. customer approval before letters
9. admin approval before escalation
10. returned-response parser
11. collector/license review
12. attorney support eligibility
13. contact board/CRM built in
14. score-goal guidance
15. secure document vault
16. production gate before customer results

---

# 14. MVP Build Order

## Phase 1 — Customer Portal Shell

- member routes
- upload screen
- findings summary
- accounts review
- drafts approval
- progress tracker
- document vault
- messages
- profile/security

## Phase 2 — Admin CRM

- contact board
- customer profile
- tasks
- notes
- status pipeline
- approval queue

## Phase 3 — Scanner Integration

- upload to backend
- scan job status
- v9 workbook output
- raw evidence index
- findings API

## Phase 4 — Safety Gates

- health check
- ground truth
- QA verification
- security audit
- production gate

## Phase 5 — Workflow

- letters
- approvals
- mail tracking
- response upload/parser
- next-round logic

## Phase 6 — Scale

- vendor APIs
- credit monitoring
- identity verification
- payments
- certified mail
- notifications
- attorney support packet

---

# 15. A+ Acceptance Criteria

A+ release requires:

- customer UI simple and responsive
- admin UI has evidence/QA workflow
- scanner passes v9/v17 standards
- no real data in frontend code
- demo mode off by default
- findings blocked unless gates pass
- letters draft-only
- no auto-send
- audit logs enabled
- security controls documented
- compliance review completed
- rollback plan exists

---

# 16. Final Credit Vivo Operating Flow

```text
Website
  → Sign Up
  → Goal Selection
  → Member Portal
  → Upload 3 Reports
  → Scanner Health Check
  → AI Review
  → v9 Admin Workbook
  → Ground Truth Validation
  → Customer Findings
  → Draft Letter Review
  → Customer Approval
  → Admin Approval
  → Mail/Submit
  → Track Response
  → Parse Response
  → Next Round
  → Attorney Support Review if Eligible
```
