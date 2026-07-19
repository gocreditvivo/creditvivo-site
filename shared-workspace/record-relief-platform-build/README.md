# Record Relief Platform Build

> **THE RECORD RELIEF ENGINE IS THE PRODUCT.**
>
> The website exists to collect information for the engine.
>
> No phase advances until tests pass, failures are fixed and re-tested, security passes, legal review passes where required, and founder approval is recorded.

## Build Order

1. Product architecture
2. Document taxonomy
3. Parser evaluation dataset
4. Document classification
5. OCR and extraction
6. Normalization
7. Identity and duplicate resolution
8. Conflict engine
9. Human verification workstation
10. State rule engine
11. Eligibility engine
12. Confidence engine
13. Relief recommendation engine
14. Attorney routing engine
15. Workflow engine
16. Frontend and dashboards
17. Payments and communications
18. Security and compliance
19. End-to-end testing
20. Beta and launch

## Required Phase Status

Each phase must be marked one of:

- NOT_STARTED
- IN_PROGRESS
- BLOCKED
- FAILED
- FIX_IN_PROGRESS
- REVERIFYING
- PASSED

## Gate Rule

If a phase fails:

1. Stop advancement.
2. Record the failed test and evidence.
3. Assign an owner.
4. Fix the defect.
5. Re-run the complete affected test set.
6. Update the verification file.
7. Move forward only after status is PASSED.

## Ownership

- Claude: UX, content, frontend, wireframes, customer journey
- Codex: parser, backend, database, APIs, security, integrations, automated testing
- Attorney reviewer: state law rules, legal boundaries, eligibility logic, legal copy
- Tim: product direction, brand, pricing, approval gates
- Independent reviewer: security, parser accuracy, and release verification

## Core Principle

The parser extracts facts. The rule engine applies jurisdiction rules. The eligibility engine returns preliminary outcomes. No component should claim a final legal determination unless an approved attorney-review workflow supports it.
