# Credit Vivo Production Readiness

## Current Build

This is a local production-style MVP, not the final regulated fintech platform.

It includes:

- Public landing page
- Review request form
- Lead capture API
- Admin lead view protected by `ADMIN_TOKEN`
- Local JSON storage excluded from Git
- Basic rate limiting, validation, security headers, and atomic writes
- Versioned readiness engine with admin diagnostics
- Test mode with isolated test storage

## Required Environment

Set these before running outside local development:

```bash
PORT=8910
NODE_ENV=production
ADMIN_TOKEN=<long-random-secret>
```

In local development, the fallback admin token is:

```text
dev-admin-token-change-me
```

Do not use that fallback for production.

## Before Real Customer Data

Upgrade these items first:

- Replace JSON storage with an encrypted managed database.
- Replace token admin access with real authentication, MFA, roles, and session expiry.
- Move AI/deep-learning calls behind an audited provider adapter with human review gates.
- Add HTTPS termination, secure cookies, structured audit logs, and encrypted backups.
- Add privacy policy, terms, cancellation flow, consent records, and state-law review.
- Add vendor reviews for credit data, identity protection, builder tools, payments, and attorney network.
- Add monitoring, alerting, incident response, and data retention/deletion workflows.

## Sensitive Data Rule

The current intake form must not collect:

- Social Security numbers
- Full date of birth
- Bureau login credentials
- Full account numbers
- Credit report uploads
- IDs or signatures

Those require a secure authenticated portal and storage controls.
