# Credit Vivo Scanner v18 Report Ingestion Plan

## Purpose

The v18 foundation adds a consumer-only Report Ingestion Layer in front of the
existing Credit Vivo Proprietary Parser Engine.

The native Credit Vivo uploaded-PDF path remains the default. No paid AI API,
commercial credit parser, bureau pull provider, or third-party parser integration
is added in this step.

## Current Default Path

1. Customer uploads one or more consumer credit report PDFs.
2. FastAPI validates PDF file type, file count, and file size.
3. `pypdf` extracts page text.
4. The Report Ingestion Layer marks the source as `uploaded_pdf_native_text`.
5. The ingestion output is normalized into the existing parser input shape:
   filename mapped to text, bureau, source metadata, and consumer-only flag.
6. `credit_vivo_proprietary_engine.parse_reports()` remains the default parser.
7. The existing scanner output shape is preserved.

## Supported v18 Input Contract

The layer is intentionally narrow. Every input must be a consumer credit report.

Current active source:

- `uploaded_pdf_native_text`

Reserved future sources:

- `extracted_text`
- `third_party_parser_json`
- `structured_bureau_api`

Reserved sources are adapter contracts only. They do not integrate Affinda,
DigiParser, Docparser, Equifax, iSoftpull, CRS, Soft Pull Solutions, or any other
paid or commercial parser in this step.

## Normalization Target

All sources must eventually normalize into the current Credit Vivo tradeline
schema used by the proprietary engine:

- Bureau
- Source filename
- Account name
- Masked account number
- Account type
- Responsibility
- Status and pay status
- Balance and past due
- Dates
- Remarks
- Original creditor
- Collector or debt buyer
- Raw evidence block
- Confidence and review flags

For this foundation step, uploaded PDFs continue through the existing text
parser. Future structured adapters must map into this schema before issue
detection, cross-bureau matching, summaries, workbook output, or letter queues.

## Behaviors Preserved

- Native parser remains default.
- API response shape remains unchanged.
- Evidence snippets remain available.
- Confidence scoring remains available.
- Issue detection remains available.
- Cross-bureau matching and 3-bureau comparison remain available.
- Customer summary and admin summary remain available.
- Draft-only letter queue remains available.
- Workbook, CSV, JSON, and draft TXT outputs remain available.

## Compliance Rules

- Scanner output is draft review data only.
- Use safe language such as possible report errors, plain-English review,
  documented next steps, customer-approved dispute prep, and results vary.
- Do not promise removals, score increases, approvals, or legal outcomes.
- Do not add automatic disputes, automatic letters, mail sending, complaints, or
  legal escalation.
- Customer approval and admin review are required before dispute prep moves
  forward.
- Credit Vivo is not a law firm and does not provide legal advice.
- Accurate, current, and verifiable information may remain.

## Non-Goals For This Step

- No commercial or business credit report parsing.
- No paid AI API requirement.
- No vendor parser integration.
- No bureau/API pull integration.
- No public API response change.
- No automatic dispute, letter, mail, complaint, or escalation workflow.

## Future Adapter Acceptance Criteria

Before any future adapter is enabled, it must:

- Prove the input is a consumer credit report.
- Preserve raw evidence or source references.
- Map fields into the normalized tradeline schema.
- Preserve confidence scoring and admin review flags.
- Maintain the existing scanner response shape unless a separate approved API
  contract change is created.
- Add regression tests using synthetic, non-customer data.
- Avoid storing secrets, bureau credentials, real credit reports, IDs, SSNs, or
  full account numbers.

