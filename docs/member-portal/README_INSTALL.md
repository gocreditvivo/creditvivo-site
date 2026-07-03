# Credit Vivo Customer Member Portal — A+ Production-Default Package

## What this is

A production-default customer member portal front-end package for Credit Vivo.

It includes:

- Member overview
- Secure upload placeholder
- AI findings page
- Review accounts page
- Dispute draft approval page
- Progress tracker
- Documents page
- Messages page
- Profile page
- Security/approval status page
- Settings placeholder
- API adapter
- Production gate banner
- Demo/mock mode OFF by default

## Production default

Demo/mock mode is OFF:

```env
NEXT_PUBLIC_CREDIT_VIVO_DEMO_MODE=false
```

When demo mode is off and no backend API is connected, the portal renders safe empty states and does not expose sample credit findings.

## Why

Credit Vivo should not show customer credit findings until the scanner backend confirms:

- health check passed
- ground-truth validation passed
- QA verification passed
- production gate passed

## Install

Copy these folders into:

`C:\CreditVivo\creditvivo_v1_clean_frontend\creditvivo_v1_clean_frontend`

Folders:

- `app/member`
- `components/member-portal`
- `lib/credit-vivo`
- `types`

Also copy `.env.example` and merge with your real `.env.local`.

Run:

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:3000/member
```

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

## Backend API contract

When backend is ready, set:

```env
NEXT_PUBLIC_CREDIT_VIVO_API_BASE_URL=https://your-api-domain.com
```

The portal calls:

```text
GET /member/portal
```

Expected payload type is in:

`types/credit-vivo-member.ts`

## Critical production rule

If backend returns:

```json
{
  "productionGate": {
    "healthCheckPassed": false,
    "groundTruthPassed": false
  }
}
```

The front end hides review accounts and draft letters.

## Compliance/safety

- No auto-send
- Draft-only letters
- Customer approval required
- Admin approval required before escalation
- No guarantees
- Attorney support wording is safe
- No real customer data in mock files
- Demo mode off by default

## Disclosure

Results are not guaranteed. Attorney support may be available for eligible unresolved credit-reporting issues. Credit Vivo does not provide legal advice.
