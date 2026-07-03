# Credit Vivo Member Portal — Production Ready Defaults / No Demo Mode

## What this package does

This is a production-default customer member portal shell.

It is designed to be safe before the scanner backend is live.

## Demo/mock mode is OFF

`.env.production.example` includes:

```env
NEXT_PUBLIC_CREDIT_VIVO_DEMO_MODE=false
NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_PRODUCTION_GATES=true
NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_AUTH=true
```

## Important

This does not certify the full live platform as production ready.

It makes the front-end member portal production-default and safe:

- no mock customer findings shown by default
- no real customer data in code
- findings blocked until backend gates pass
- letters blocked until backend gates pass
- upload disabled until secure backend is connected
- no auto-send
- draft-only letter UI
- customer approval UI prepared
- security gate page included

## Install

Copy these folders/files into:

`C:\CreditVivo\creditvivo_v1_clean_frontend\creditvivo_v1_clean_frontend`

Files/folders:

- `app/member`
- `components/member-portal`
- `lib/credit-vivo`
- `types`
- `.env.production.example`
- `middleware.ts` optional starter

Then run:

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:3000/member
```

## Backend API contract

Set this only when backend is ready:

```env
NEXT_PUBLIC_CREDIT_VIVO_API_BASE_URL=https://your-approved-api.com
```

Frontend calls:

```text
GET /member/portal
```

Backend must return:

- profile
- stats
- uploads
- reviewAccounts
- positiveAccounts
- draftLetters
- progressSteps
- messages
- documents
- productionGate

## Required backend production gate

Customer findings are shown only if:

```json
{
  "productionGate": {
    "healthCheckPassed": true,
    "groundTruthPassed": true,
    "qaVerificationPassed": true,
    "securityAuditPassed": true,
    "productionGatePassed": true,
    "customerDataAllowed": true
  }
}
```

If any gate is false, the portal hides review accounts and draft letters.

## Routes

- `/member`
- `/member/upload`
- `/member/findings`
- `/member/accounts`
- `/member/disputes`
- `/member/progress`
- `/member/documents`
- `/member/messages`
- `/member/profile`
- `/member/settings`
- `/member/security`

## Compliance defaults

- Results are not guaranteed.
- Attorney support may be available for eligible unresolved credit-reporting issues.
- Credit Vivo does not provide legal advice.
- No letters are sent without approval.
- No auto-send.
- No legal conclusions in customer UI.
