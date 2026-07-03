# Credit Vivo Scanner v18 Letter Lifecycle Plan

## Purpose

The v18 Letter Lifecycle foundation turns scanner worksheet/output data into
draft-only letter recommendations, approval tracking, Lob-ready packet previews,
and response review recommendations.

This foundation does not send mail, call Lob, file complaints, make legal
threats, or use paid AI APIs.

## Inputs

The lifecycle starts from scanner issue/output data such as:

- Issue ID
- Issue type
- Customer label
- Plain-English explanation
- Related tradeline IDs
- Evidence snippets or evidence IDs
- Existing draft letter queue data

The scanner remains the source of possible report errors and evidence context.
The lifecycle module only organizes draft prep and tracking.

## Draft Letter Types

Supported draft-only recommendations:

- Bureau review/dispute letter draft
- Furnisher direct dispute draft
- Debt validation letter draft
- Reinvestigation letter draft
- Method of verification request draft
- Documented follow-up package draft
- Complaint preparation packet draft

Complaint packets are preparation-only. They are not CFPB, state, regulator, or
attorney filing automation.

## Lifecycle Modes

The lifecycle supports two safe operating modes:

- `approval_required`
- `auto_prepare`

`approval_required` is the default. The system drafts the recommended letter and
waits for customer review, admin review, and compliance approval.

`auto_prepare` lets the backend prepare draft letter text and packet previews
more quickly, but it still cannot send mail, file complaints, submit legal
escalations, or bypass approval gates.

If a caller asks for `auto_send`, the system treats it as a blocked request and
uses `auto_prepare` as the effective mode. Sending remains disabled.

## Lifecycle Statuses

- `scan_completed`
- `draft_ready`
- `customer_review_pending`
- `customer_approved`
- `customer_rejected`
- `admin_review_pending`
- `admin_approved`
- `lob_packet_ready`
- `sent_to_lob`
- `mailed`
- `in_transit`
- `delivered`
- `response_waiting`
- `response_uploaded`
- `response_review_pending`
- `next_step_recommended`
- `resolved_updated`
- `resolved_removed`
- `resolved_verified`
- `no_response_review_needed`
- `complaint_packet_ready`
- `closed`
- `cancelled`

The foundation defaults to draft or review-pending states. It does not move
letters into send states by itself.

## Lob-Ready Packet Preview

The packet preview structure includes:

- `customer_id`
- `report_id`
- `letter_id`
- `letter_type`
- `recipient_type`
- `recipient_name`
- `recipient_address`
- `sender_name`
- `sender_address`
- `account_ids`
- `issue_ids`
- `evidence_ids`
- `letter_html_or_pdf_reference`
- `customer_approval_timestamp`
- `admin_approval_timestamp`
- `compliance_review_status`
- `lob_id`
- `lob_status`
- `delivery_event_log`

The packet remains blocked unless all gates are present:

- Customer approval timestamp
- Admin approval timestamp
- Compliance review status of `approved`
- A lifecycle status that is approval-ready

No Lob API call is made in this foundation.

## Response Classification

Uploaded response text can be classified as:

- `verified`
- `updated`
- `removed`
- `partially_updated`
- `request_for_more_information`
- `frivolous_or_irrelevant_notice`
- `no_response`
- `unknown_needs_admin_review`

Classifications produce next-step recommendations only. They do not trigger
automatic disputes, letters, complaints, or legal escalation.

## Compliance Guardrails

- Scanner and letter output are draft review data only.
- Customer approval and admin review are required before action.
- Credit Vivo is not a law firm and does not provide legal advice.
- Accurate, current, and verifiable information may remain.
- Results vary.
- Do not promise removal, deletion, score increase, approval, or legal outcome.
- Use safe wording such as possible report error, possible inconsistency,
  plain-English review, documented next steps, and customer-approved dispute
  prep.
- Avoid unsafe wording such as delete collections, remove bad credit,
  guaranteed score increase, guaranteed approval, fix credit fast, legal
  violation proven, killshot, wet-ink required, must delete, and legally
  indefensible.

## Non-Goals

- No production Lob sending.
- No paid AI dependency.
- No OpenAI, Claude, Gemini, or similar API requirement.
- No automatic CFPB filing.
- No attorney/legal threat automation.
- No customer-facing send action without approval gates.

## Current Implementation

The foundation is implemented as a pure Python service:

`scanner_backend/letter_lifecycle.py`

Key functions:

- `recommend_letter_type(issue_data)`
- `build_draft_letter(scanner_issue_data)`
- `build_lob_packet_preview(letter_data, packet_data)`
- `can_prepare_lob_packet(letter_status, customer_approval, admin_approval, compliance_review_status)`
- `classify_response_text(response_text)`
- `recommend_next_step(response_classification)`

Tests:

`scanner_backend/tests/test_letter_lifecycle.py`
