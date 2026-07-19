# CreditVivo Compliance Questions

Created: 2026-07-18

This is not legal advice. Use this file to collect questions for counsel, compliance review, and launch gating.

## Standing Compliance Rules

- No guaranteed score increases.
- No guaranteed deletions.
- No guaranteed approvals.
- No guaranteed timelines.
- Do not claim accurate/current negative information can be removed.
- Do not make attorney-service claims unless the attorney relationship is real and documented.
- Do not charge or launch paid credit repair services until the agreement, cancellation process, payment flow, and state/CROA issues are reviewed.
- Do not auto-send dispute letters.
- Do not submit fake fraud, identity-theft, or not-mine claims.

## Open Legal / Compliance Questions

| Question | Risk | Owner | Status |
|---|---|---|---|
| What entity will operate CreditVivo? | High | Tim | Open |
| Does the entity need state credit services registration? | High | Tim + counsel | Open |
| What exact paid service can be offered without advance-fee risk? | High | Tim + counsel | Open |
| What contract, cancellation notice, and disclosures are required? | High | Tim + counsel | Open |
| Can LegalShield be marketed as attorney-backed support? | High | Tim + counsel | Open |
| What data retention/deletion policy applies to reports and IDs? | High | Tim + counsel/Codex | Open |
| Can third-party validator tools receive synthetic data only? | Medium | Tim + Codex | Yes for testing |
| Can third-party validator tools receive real customer data? | High | Tim + counsel | Not yet |
| What can be said about credit builder lines? | Medium | Tim + counsel | Must be eligibility/no guarantee |
| What SMS language is allowed after A2P approval? | Medium | Tim + counsel/Codex | Open |

## Safe Language

Use:

- possible issue
- review needed
- may be inaccurate, incomplete, duplicate, outdated, or unverifiable
- draft for review
- results vary
- consumer approval required
- attorney services are separate

Avoid:

- guaranteed deletion
- guaranteed score boost
- approved
- legal violation confirmed
- bureau must delete
- attorney guaranteed
- cannot be verified unless evidence supports it

## Vendor Rule

BureauRelay/SwitchLabs or similar tools may be used later as validation/QA vendors if allowed by their terms.

Do not:

- copy their code
- scrape private dashboards
- upload real customer data before vendor review
- pretend CreditVivo is a furnisher if it is not

Do:

- use public docs
- use dummy/synthetic files
- export validation output if allowed
- compare validator output to CreditVivo's original parser
