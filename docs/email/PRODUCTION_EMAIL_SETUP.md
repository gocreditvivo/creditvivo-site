# Credit Vivo Production Email Setup

Source: `C:\Users\miste\Downloads\credit_vivo_production_email_one_file_codex.md`

## Recommended Provider

Use Google Workspace for `@creditvivo.com` email. Microsoft 365, Zoho Mail, and Hostinger Email are acceptable alternatives if the same inbox and security structure is preserved.

## Real Inboxes

- `tim@creditvivo.com` - founder/admin, GitHub, Vercel, domain registrar, Workspace admin, vendor admin, recovery.
- `support@creditvivo.com` - customer support, website contact, member portal support, billing/refund questions, service communication.
- `social@creditvivo.com` - social media, ads, content tools, Google Business Profile, Canva/CapCut/schedulers.

## Aliases

- `hello@creditvivo.com`, `info@creditvivo.com`, `billing@creditvivo.com`, `disputes@creditvivo.com` -> `support@creditvivo.com`
- `privacy@creditvivo.com`, `legal@creditvivo.com`, `security@creditvivo.com` -> `tim@creditvivo.com`
- `marketing@creditvivo.com`, `media@creditvivo.com`, `ads@creditvivo.com`, `brand@creditvivo.com` -> `social@creditvivo.com`
- `no-reply@creditvivo.com` -> system/app sender only

## DNS

Provider must supply exact MX and DKIM values.

SPF for Google Workspace only:

```text
v=spf1 include:_spf.google.com ~all
```

Start DMARC in monitoring mode:

```text
v=DMARC1; p=none; rua=mailto:security@creditvivo.com; fo=1
```

Move to `p=quarantine` and later `p=reject` only after all sending services pass SPF/DKIM/DMARC.

## App Defaults

Email sending is disabled by default:

```env
EMAIL_PROVIDER=disabled
EMAIL_FROM=no-reply@creditvivo.com
SUPPORT_EMAIL=support@creditvivo.com
PRIVACY_EMAIL=privacy@creditvivo.com
SECURITY_EMAIL=security@creditvivo.com
SOCIAL_EMAIL=social@creditvivo.com
ENABLE_EMAIL_SENDING=false
ENABLE_MARKETING_EMAILS=false
ENABLE_DISPUTE_EMAIL_AUTO_SEND=false
EMAIL_API_KEY=
EMAIL_WEBHOOK_SECRET=
```

## Hard Rule

No dispute letters, complaint packets, attorney referrals, credit report attachments, raw scanner workbooks, or raw evidence packets are sent by email by default.

## Live Checklist

- [ ] Provider active
- [ ] Inboxes created
- [ ] Aliases created
- [ ] MX/SPF/DKIM/DMARC verified
- [ ] 2FA enabled on every inbox
- [ ] GitHub/Vercel use `tim@creditvivo.com`
- [ ] Social accounts use `social@creditvivo.com`
- [ ] Website support routes to `support@creditvivo.com`
- [ ] App email sending remains disabled until approved
- [ ] Consent/unsubscribe logic exists before marketing email
- [ ] No sensitive credit data is sent by ordinary email

