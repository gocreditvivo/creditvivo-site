# B-3 Scanner Masking Blocker

Created: 2026-07-18

Owner: Codex

Status: Confirmed, accepted, not fixed yet.

## Summary

Claude flagged inverted account-number masking in scanner workbooks. Codex verified the issue locally.

Pattern found:

`digits + ****`

This exposes a leading account-number fragment while hiding the trailing digits. CreditVivo output should show only a safe fragment such as `****1234`, or a non-sensitive label such as `ending in 1234`, depending on context.

## Verified Files

| Workbook | Result |
|---|---|
| `C:\Users\miste\Downloads\credit-vivo-desktop-scanner-output (55).xlsx` | 299 `digits + ****` patterns found |
| `C:\Users\miste\OneDrive\Desktop\Documents\CV Scanner\scanner_backend\output\scan_10c98b18f088\credit_vivo_desktop_scanner_output.xlsx` | 299 `digits + ****` patterns found |

## Sheet Findings

In both inspected workbooks:

| Sheet | State | Finding |
|---|---|---|
| `Draft Letters` | Hidden | 274 `digits + ****` patterns |
| `3 Bureau Comparison` | Hidden | 6 `digits + ****` patterns |
| `Raw Tradelines With Dates` | Hidden | 6 `digits + ****` patterns |
| `Dates Found Audit` | Hidden | 13 `digits + ****` patterns |

Visible sheets were mostly safer, but hidden workbook sheets still matter because workbooks can be opened, exported, emailed, attached, or reviewed by staff.

## Likely Cause

Consumer reports can display account identifiers as a leading digit fragment followed by stars. The scanner must not preserve that display value in output sheets or draft letters. It should re-mask any long visible digit run before writing workbooks, including strings that already contain `****`.

Current code contains correct last-four masking functions in some places, but workbook-level/raw-evidence/draft-letter paths still allow source-style values through.

## Required Fix

Before scanner output is used with real customer data:

1. Normalize all account identifiers at extraction and workbook-write time.
2. Convert any `digits + ****` pattern to a safer masked value.
3. Sanitize raw evidence IDs or identifiers that contain long digit runs.
4. Apply the sanitizer to visible and hidden sheets.
5. Add an automated workbook audit test that fails on:
   - `\d{7,}\*{2,}`
   - long unmasked digit runs in account-related cells
   - SSN/DOB patterns
6. Re-run the latest scanner workbook and verify zero `digits + ****` patterns.

## Immediate Workaround

Do not send, mail, upload, or share current scanner workbooks or draft-letter exports that came from real reports until sanitized.
