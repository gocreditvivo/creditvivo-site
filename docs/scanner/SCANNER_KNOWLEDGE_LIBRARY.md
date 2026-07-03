# Scanner Knowledge Library

The scanner backend now has a rules library under `scanner_backend/rules/`.

## Rule Files

- `negative_account_rules.yml` - negative/reviewable account categories and status-code signals.
- `metro2_field_map.yml` - derived Metro 2-style field map used for workbook comparisons.
- `metro2_issue_rules.yml` - field-level issue detection categories.
- `fcra_rules.yml` - FCRA review areas and safe output language.
- `eoscar_workflow_rules.yml` - e-OSCAR awareness notes and draft-only follow-up routes.
- `compliance_guard_rules.yml` - blocked phrases, preferred phrases, and required disclaimers.

The files use JSON-compatible YAML so the scanner can load them with the Python standard library and avoid adding another dependency.
