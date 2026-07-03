# Credit Vivo Staging / UAT Safe Mode

Source: `C:\Users\miste\Downloads\credit_vivo_staging_uat_mock_test_codex.md`

## Purpose

Use staging to test the full customer journey without real customer data, live payments, live email sending, auto-send, complaints, or attorney escalation.

## Staging Rules

- Demo mode off
- Synthetic reports only
- Real customer data off
- Stripe test mode only
- Email sending off
- Marketing emails off
- Dispute email auto-send off
- Auto-send off
- External calls off
- Customer findings blocked until production gates pass

## UAT Route Flow

```text
/ -> /signup -> /pricing -> /checkout -> /checkout/success -> /member
-> /member/upload -> /member/findings -> /member/accounts -> /member/disputes
-> /member/progress -> /member/documents -> /member/messages -> /member/security
-> /admin/production-certification
```

## Required Manual Checks

- Homepage loads and has safe disclosure.
- Signup does not request SSN, DOB, or credit report data.
- Checkout is test-mode only.
- Member findings remain blocked until gates pass.
- Upload page warns synthetic/test only.
- Admin production certification shows blockers.
- Email sending remains disabled.
- No live customer data is used.

## Production Rule

Do not test the full customer journey in production first. Use staging safe mode plus synthetic reports.

