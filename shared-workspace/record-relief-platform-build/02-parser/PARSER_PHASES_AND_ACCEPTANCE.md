# Parser Build Phases and Acceptance Gates

## Phase P1 — Document Taxonomy

Build:
- Supported document list
- Jurisdiction and court metadata
- Document subtype definitions
- Required fields by document type

Pass when:
- Every supported type has a schema
- Unknown-document handling exists
- Attorney or legal reviewer approves terminology

## Phase P2 — Evaluation Dataset

Build:
- Representative clean PDFs
- Scanned PDFs
- Rotated and skewed images
- Low-resolution scans
- Handwritten annotations
- Multi-document packets
- Court calendars and rosters with 100 and 1,000+ names
- Ground-truth labels

Pass when:
- Dataset is de-identified or authorized
- Ground truth has two-person review
- Train, validation, and holdout sets are separated

## Phase P3 — Scanner Benchmark

Compare:
- ABBYY Vantage
- Azure AI Document Intelligence
- Amazon Textract
- Google Document AI
- Human-in-the-loop workflow benchmark

Measure:
- Classification accuracy
- Field precision and recall
- Table and row accuracy
- Processing time
- Cost per page
- Human-review percentage
- Failure recovery
- Bulk-volume behavior

Pass when:
- Same holdout set is used for all vendors
- Results are reproducible
- Final choice and fallback strategy are documented

## Phase P4 — Ingestion and Safety

Build:
- File validation
- Malware scan
- Size/page limits
- Duplicate-file detection
- Job queue
- Retry and dead-letter handling

Pass when:
- Invalid and malicious files are rejected safely
- Large jobs do not block the customer session
- Failed jobs can be resumed without duplication

## Phase P5 — Classification and Splitting

Build:
- Document classifier
- Packet splitter
- Unknown-document route
- Confidence thresholds

Pass when:
- Holdout classification target is met
- Low-confidence files enter review
- Packet pages remain traceable to the source file

## Phase P6 — OCR and Field Extraction

Build:
- Native text first
- OCR fallback
- Layout reconstruction
- Key-value extraction
- Table extraction
- Named-entity extraction

Pass when:
- Every field includes source evidence
- No silent field invention
- Missing fields remain null and are flagged

## Phase P7 — Bulk Name and Row Parser

Build:
- Court calendar parser
- Defendant roster parser
- Row segmentation
- Continuation-page handling
- 100, 1,000, and larger-name list processing

Pass when:
- No row loss above the approved tolerance
- Header/footer text is not mistaken for people
- Each row preserves page and row evidence
- Similar names are not automatically merged

## Phase P8 — Normalization and Identity Resolution

Build:
- Name normalization
- Date normalization
- Court and county normalization
- Case-number normalization
- Offense and disposition vocabulary mapping
- Probabilistic identity matching

Pass when:
- False merges remain below the approved threshold
- Ambiguous matches enter human review
- Original extracted values are never overwritten

## Phase P9 — Cross-Document Reconciliation

Build:
- Case matching
- Charge matching
- Date conflict detection
- Disposition conflict detection
- Sentence conflict detection
- Missing-document detection

Pass when:
- Conflicts are surfaced rather than silently resolved
- Resolution decisions are logged
- Reviewer can inspect both source documents side by side

## Phase P10 — Human Verification Workstation

Build:
- Document viewer
- Highlighted source regions
- Editable extracted fields
- Verification states
- Reviewer notes
- Escalation queue
- Audit history

Pass when:
- Every correction is attributable
- Reviewer cannot alter source evidence
- Rejected extraction values remain in history

## Phase P11 — Rule Engine Integration

Build:
- Versioned normalized-case API
- Missing-data contract
- Conflict contract
- Confidence contract
- State-rule lookup interface

Pass when:
- Parser and rule engine remain independently testable
- Low-confidence or conflicting cases cannot bypass review
- API contract tests pass

## Phase P12 — Production Volume and Recovery

Test:
- Concurrent uploads
- 100-document batch
- 1,000-document batch
- 1,000+ names in one file
- Multi-thousand-page asynchronous job
- Worker interruption
- Vendor outage
- Duplicate webhook or callback

Pass when:
- No data loss
- No duplicate case creation
- Retry is idempotent
- Performance and cost are within approved limits

## Advancement Rule

Each phase must have a completed verification report. A FAIL or BLOCKED result stops advancement. The owner must fix the defect, add or update regression tests, rerun all affected tests, update the report, and receive approval before starting the next phase.
