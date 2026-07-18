# Credit Vivo — Metro 2 Requirements Relay to Codex

Date: 2026-07-18
Owner direction: ChatGPT is taking the lead on the Metro 2 requirements track. Codex should treat this document as the current coordination message.

## Current decision

Credit Vivo will study the furnisher side using a **synthetic, test-only mock environment** so the scanner can understand the full lifecycle:

`furnisher source data -> Metro 2 record -> validation -> bureau processing/display -> consumer report -> Credit Vivo scanner interpretation`

Do not represent Credit Vivo as an approved data furnisher. Do not use fake bureau-issued credentials, subscriber IDs, vendor IDs, live SFTP credentials, or real consumer data.

## ChatGPT workstream

ChatGPT is organizing the Metro 2 requirements library, including:

- Base Segment and applicable supplemental segments
- Exact field positions, lengths, formats, and valid characters
- Required, optional, and conditional field logic
- Account status, account type, ECOA, compliance condition, special comment, dispute, and payment history codes
- Date rules and cross-field dependencies
- Balance, past-due, charge-off, credit-limit, sold/transferred, collection, bankruptcy, and dispute scenarios
- Header/trailer requirements and file/record controls
- Bureau-specific implementation differences where authoritative material is available
- Rule versioning, traceability, evidence mapping, and audit requirements
- Character-level integrity tests and malformed-record tests

Completion must not be claimed until the current official CRRG and relevant bureau-specific materials are obtained and reconciled.

## Codex instructions

1. Do not hard-code guessed Metro 2 rules into production code.
2. Keep parsing, validation, interpretation, and plain-English explanation as separate modules.
3. Build the rules engine so rules and code tables are versioned data, not scattered application logic.
4. Preserve raw input immutably and store cryptographic hashes, parser version, rule version, and processing logs.
5. Every finding must be traceable to source file, record/segment, exact field, raw value, parsed value, applied rule, and evidence location.
6. Treat PDF/text consumer reports as bureau-presented disclosures, not original raw Metro 2 files.
7. Use synthetic test fixtures only for the mock furnisher workflow.
8. Add golden tests, field-position tests, field-length tests, mutation tests, invalid-code tests, boundary tests, regression tests, and false-positive/false-negative tracking.
9. Do not allow a scanner finding to automatically become a dispute allegation, legal conclusion, complaint, or outgoing communication. Keep customer/admin approval gates.
10. Leave clear interfaces so the official Metro 2 rule library can be inserted after validation of the current CRRG.

## Required synthetic scenarios

- Current account
- 30/60/90-day delinquency
- Charge-off
- Collection
- Paid collection
- Sold/transferred account
- Consumer-disputed account
- Bankruptcy-related status
- Deleted account
- Intentionally malformed fixed-width record
- One-character insertion, deletion, replacement, field shift, leading-zero removal, blank-to-zero conversion, and conflicting status/history mutation

## Expected Codex response

Update the normal Codex handoff with:

- Existing scanner architecture assessment
- Proposed Metro 2 module boundaries
- Files to create or change
- Data model for rules, code tables, raw records, parsed fields, findings, evidence, and review history
- Test fixture plan
- Security and approval-gate plan
- Blockers requiring official CRRG or bureau materials
- No unsupported claim of Metro 2 completeness
