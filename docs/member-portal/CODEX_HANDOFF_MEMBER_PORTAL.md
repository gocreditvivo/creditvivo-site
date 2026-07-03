# Codex / Developer Notes — Member Portal A+ Production Defaults

## Build goal

Implement the Credit Vivo customer member portal with production-safe defaults.

## Do not enable mock mode by default

`NEXT_PUBLIC_CREDIT_VIVO_DEMO_MODE=false`

## Required behavior

If backend is not connected:
- show empty safe states
- do not show sample credit data
- do not show draft letters
- do not enable approvals
- show production gate banner

If backend is connected but scanner gates fail:
- hide findings
- hide letters
- show blocked production gate message

If backend says gates passed:
- show customer-safe findings
- keep letters draft-only
- require approval

## Required backend gates

- healthCheckPassed
- groundTruthPassed
- qaVerificationPassed
- securityAuditPassed
- productionGatePassed

## Never expose

- full SSN
- full DOB
- full account numbers
- raw credit report text
- admin forensic workbook
- private scanner rules
- backend secrets

## Customer copy style

Simple. Score-goal focused. No legal conclusions.

Use:
- possible issue
- should be verified
- may need review
- draft only
- no letters sent without approval

Do not use:
- guaranteed deletion
- guaranteed score increase
- this violates the law
- lawsuit guaranteed
