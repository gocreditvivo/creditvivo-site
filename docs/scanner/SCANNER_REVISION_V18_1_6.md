# Credit Vivo Scanner Revision v18.1.6

## Purpose

`18.1.6` makes the visible workbook output match the supplied v9 three-bureau
forensic layout while preserving the v18 verification engine.

## What changed

- `Ours 3 Bureaus Comparison` now uses the v9 forensic columns:
  `Field #`, `Account Info`, `Experian`, `Equifax`, `TransUnion`,
  `Forensic issue / dispute lead`, `3-CRA Status`,
  `AI Error / Inaccuracy Found`, `Reason / Why It Matters`,
  `Dispute / Verification Request`, `Priority`, and `Evidence / Notes`.
- The visible sheet keeps title, subtitle, note, and row-4 header structure.
- Pre-output verification now checks the visible v9 forensic template in
  addition to the hidden structured comparison export and raw-data verification.

## Compliance guardrails

- Scanner output remains draft review data only.
- No automatic disputes, letters, mail, complaints, or legal escalation were added.
- Customer approval, admin review, and compliance review remain required.
- Credit Vivo is not a law firm and does not provide legal advice.
