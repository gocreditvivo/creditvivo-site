# Credit Vivo Scanner — Team Update

**Date:** 2026-08-14  
**Priority:** P0  
**Release status:** BLOCKED pending verified hardening

## Discovery

The actual Credit Vivo scanner prototype has been located in `gocreditvivo/main-2`, primarily in `src/pages/ScanTestPage.tsx`.

It already contains PDF extraction, bureau detection, bureau-specific field extraction, tradeline parsing, negative-account heuristics, three-bureau comparison structures, a findings/rules engine, and a scanner test interface.

## Hardening branch

`gocreditvivo/main-2` → `codex/scanner-core-hardening`

Current hardening commits include:
- `3a3c01e20746d1eb34076187cbfa22179901e6e8`
- `3fdc62416090f5d3af37095d8f9c8a645b4cd92a`
- `c4ac3c3109a951852c0069c3fa3fea866f48f4b9`

## Main risks identified

1. Bureau detection is too dependent on bureau-name occurrence and is unsafe for merged reports.
2. Tradeline splitting relies on layout/capitalization heuristics and can create false splits or merges.
3. Masking is embedded inside the UI rather than centrally enforced across API, dashboard, exports, letters, logs, and tests.
4. Some findings are written as legal conclusions rather than evidence-backed possible issues.
5. Sensitive report parsing currently occurs client-side and should move behind a controlled backend before customer beta.
6. Per-field source evidence is not consistently preserved.

## Fixes started

- Centralized account-number masking
- Identifier leak detection
- Regression coverage for masking failures
- Dedicated scanner hardening branch

## Execution order

1. Privacy / masking enforcement
2. Bureau detection hardening
3. Tradeline boundary and extraction hardening
4. Evidence-preserving normalized model
5. Conservative cross-bureau matching
6. Findings validation and wording
7. Customer approval gate
8. Progress-event tracking
9. Auth / RLS / customer-isolation verification
10. Synthetic end-to-end test and protected preview

## Team lanes

- **Codex:** scanner, backend, masking, security, matching, tests, verification
- **Claude:** upload, findings, approval, progress frontend after scanner contracts stabilize
- **ChatGPT:** requirements, evidence review, release gate, founder updates
- **Tim Do:** final beta and production go/no-go

## Immediate rule

Do not expose the scanner to customers and do not deploy production until privacy, parser, matching, findings, isolation, approval, and tracking gates have demonstrated PASS evidence.
