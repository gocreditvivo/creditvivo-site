# Scanner Skills Engine

The skills engine is the internal rule layer that helps the proprietary parser classify and explain consumer credit report findings.

## What It Does

1. Loads scanner rule files from `scanner_backend/rules/`.
2. Classifies negative/reviewable tradelines using keywords and Metro 2-style status-code signals.
3. Maps parsed fields into a consistent Metro 2-style review table.
4. Adds possible FCRA/Metro 2 review issue labels.
5. Exports the rules and review results into the workbook.

## What It Does Not Do

- It does not parse commercial/business credit reports.
- It does not use paid AI APIs.
- It does not send disputes, validation letters, mail, complaints, or legal escalations.
- It does not claim violations are proven.
