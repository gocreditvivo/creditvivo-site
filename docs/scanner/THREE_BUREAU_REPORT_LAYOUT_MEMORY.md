# Three-Bureau Credit Report Layout Memory

Last updated: 2026-07-02

Use this document as scanner memory for how the local Credit Vivo parser should expect consumer credit reports from Equifax, Experian, and TransUnion to appear after PDF text extraction.

Do not store customer names, full account numbers, full SSNs, full DOBs, IDs, bureau credentials, or real report documents here. This file records layout structure only.

## Shared Parser Rules

- Treat each bureau as its own layout template before normalizing to the Credit Vivo tradeline schema.
- Preserve raw bureau values in workbook output before applying normalization.
- Verify parsed tradeline fields against raw extracted report text before output.
- For identity cleanup, parse only consumer personal-information sections; do not pull creditor, collector, furnisher, or bureau contact addresses into `Identity_Cleanup`.
- Keep account names as shown on the report for raw field display.
- Use one readable group name in `Tradeline / Furnisher (shown once)` while keeping the raw bureau names in source fields and evidence.
- Output remains draft review data only. Customer approval and admin review are required before disputes, letters, mail, complaints, or escalation.

## Equifax Layout Memory

Typical extracted flow:

1. Cover/overview pages.
2. `Prepared for:` block appears on pages.
3. Overview text explains report sections.
4. `Personal Information` section appears before account detail pages.
5. Personal section may include:
   - consumer name directly under the section text
   - current address
   - masked SSN
   - DOB
   - former names
   - employment information
   - former addresses
   - former phone numbers
   - consumer statement
6. Account detail section starts around `Credit Accounts`.
7. Each account block commonly includes:
   - furnisher name, often followed by `- Closed`
   - furnisher address and phone on the same line
   - date reported
   - balance
   - masked account number
   - owner/responsibility
   - credit limit / high credit
   - loan/account type
   - status
   - date opened
   - date of first delinquency
   - date major delinquency first reported
   - scheduled payment / amount past due
   - date closed / last payment / last activity when present
   - payment history grid
   - narrative code and narrative code description

Parser cautions:

- `Prepared for:` repeats on account pages; do not treat every repeated prepared-for name as a separate identity issue unless the value differs.
- Furnisher address/phone lines appear immediately below account names in account blocks; exclude these from identity cleanup.
- Equifax account type labels may use `Loan/Account Type`.
- Equifax may represent payment history using code grids and narrative codes.

## Experian Layout Memory

Typical extracted flow:

1. Page 1 has `Prepared For`, report date, report number, summary counts, and `Personal Information`.
2. Page 1 may show a personal-information dashboard with labels such as `Names`, `Addresses`, `Employers`, and `Other Records`.
3. Personal details often continue on page 2.
4. Personal section may include:
   - `Names`
   - name values followed by `Name ID`
   - `Addresses`
   - address values followed by `Address ID`
   - address type labels such as single family, multifamily, apartment complex
   - employers when present
5. Account section commonly starts around `Account Information`.
6. Account blocks may include:
   - account/furnisher name
   - account number or masked account number
   - account type
   - account status
   - payment status
   - status updated
   - balance
   - balance updated
   - credit limit / original amount / high balance
   - monthly payment
   - past due
   - date opened
   - responsibility
   - remarks
   - payment history
   - on-record-until / estimated removal date when present

Parser cautions:

- Do not parse the page-1 labels `Names Addresses Employers Other Records` as a consumer name or employer.
- Experian may show multiple names and many addresses in a compact list with IDs; preserve raw values and page references.
- Experian account fields can span multiple lines and may use labels like `Status Updated`, `Balance Updated`, and `On Record Until`.

## TransUnion Layout Memory

Typical extracted flow:

1. Opening pages may include hardship/consumer-statement language before personal data.
2. `Personal Information` appears near the beginning and may repeat.
3. Personal section commonly includes:
   - credit report date
   - masked SSN
   - DOB
   - `Name`
   - `Also Known As` / `AKA`
   - `Addresses`
   - `Current Address`
   - `Other Address`
   - date reported for each address
   - phone numbers on a following page
4. Account information begins after personal information.
5. Account blocks may include:
   - account name
   - account number / masked account number
   - account type
   - responsibility
   - date opened
   - status
   - balance
   - date updated/reported
   - payment received
   - high balance / credit limit
   - past due
   - pay status
   - remarks
   - payment history
   - estimated month/year of removal when present
6. Inquiry sections may appear later and should not be mixed into tradeline parsing.

Parser cautions:

- `Name` can appear as a standalone label followed by the consumer name on the next line.
- `Also Known As` and `AKA` may appear together before alias values.
- Address blocks include `Date Reported`; do not confuse date-reported address data with tradeline date-reported fields.
- Phone numbers should be pulled for identity cleanup only from the personal-information phone-number section, not from account/furnisher contact lines.

## Workbook Expectations

- `Dashboard`: high-level scan status and raw verification summary.
- `Account_Summary`: one row per negative/reviewable account.
- `Ours 3 Bureaus Comparison`: raw bureau values across Equifax, Experian, and TransUnion with brief issue/rules/outcome language.
- `Identity_Cleanup`: raw personal-information values only, with one `KEEP` value per category and extra/obsolete/unverified values marked `DELETE` for review.
- `License_Check`: entity compliance intelligence for furnishers, collectors, debt buyers, banks, credit unions, telecom/utility, mortgage, and related entities.
- `CFPB_Packet_Checklist`, `3B_Comparison_Attachment`, `Document_Vault`, and `Lob_Tracking`: packet planning only; no automatic filing, mailing, or sending.

## Future Parser Acceptance Notes

- Add bureau-specific regression fixtures using synthetic report text only.
- Keep raw field values and source page notes visible in workbook exports.
- Avoid over-normalizing account type before raw display; simplified account type belongs in the workbook review column.
- Treat a collection account showing open/current style fields as a compliance review prompt, not an automatic violation finding.
- Maintain full masking of SSNs, full account numbers, and DOB details in workbook output.
