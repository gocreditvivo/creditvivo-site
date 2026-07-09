# Credit Vivo Platform Architecture

## Version

Current platform version: `0.2.0`

Current engine version: `cv-readiness-rules-v0.2.0`

## Goal

Create a scalable, testable, security-first Credit Vivo foundation that can grow into:

- AI credit review
- Customer portal
- Admin CRM
- Credit readiness engine
- Dispute workflow engine
- Identity protection workflow
- Attorney-supported escalation

## Module Layout

- `server.js` starts the HTTP server only.
- `src/config.js` owns environment, test mode, paths, and tokens.
- `src/app.js` owns routing and API behavior.
- `src/http.js` owns content types, JSON responses, and security headers.
- `src/security.js` owns admin auth, rate limiting, and IP hashing.
- `src/storage.js` owns local storage and atomic writes.
- `src/lead-engine.js` owns validation, readiness recommendations, model version, and diagnostics.
- `src/growth-engine.js` owns acquisition recommendations, retention segments, campaign simulation, and approval-gated automation rules.
- `tests/smoke-security.js` runs isolated test-mode verification on a separate port.

## Environment Modes

Development:

```bash
npm start
```

Test mode:

```bash
npm run test:smoke
```

Production-style:

```bash
set NODE_ENV=production&& set ADMIN_TOKEN=<long-random-token>&& npm start
```

## Engine Design

The current engine is rules-based with an AI-ready interface.

It does:

- Validate allowed customer goals, score ranges, plan interest, and contact method.
- Generate a readiness tier.
- Generate a recommended path.
- Add safe escalation flags for identity protection, document review, and attorney-supported eligibility.
- Report model version and diagnostics.

It does not:

- Rewrite its own code.
- Make legal conclusions.
- Promise score increases, deletions, approvals, or timelines.
- Send disputes automatically.

## Safe Self-Update Model

Credit Vivo should use **self-diagnostics**, not uncontrolled self-modifying code.

Safe pattern:

1. Engine detects gaps.
2. Engine reports recommendations.
3. Human/admin reviews proposed update.
4. Tests run in test mode.
5. Approved update ships through version control.

Future upgrade:

- Store model rules in a signed rule pack.
- Load rule packs by version.
- Validate rule pack schema.
- Run test suite before enabling.
- Keep rollback version available.

## Growth + Retention Automation

The growth engine is designed to help Credit Vivo learn from leads and recommend how to get more customers without creating unsafe ad spend or compliance risk.

It can:

- Segment leads by goal, plan interest, and score range.
- Recommend acquisition channels.
- Simulate ad budget allocation.
- Recommend compliant campaign angles.
- Recommend retention sequences.
- Report blocked automation risks.

It cannot:

- Spend money.
- Publish ads.
- Target using sensitive credit-report data.
- Make promised score, deletion, approval, or timeline claims.
- Contact customers without future consent and messaging compliance controls.

Future approved automation should require:

- Approved budget cap.
- Approved channels.
- Approved copy.
- Campaign end date.
- Stop-loss limits.
- Compliance review.
- Human approval before launch.

## Bank-Grade Upgrade Path

Replace local JSON storage with:

- Encrypted managed database
- Key management
- Immutable audit log
- Encrypted backups
- Retention/deletion jobs

Replace admin token with:

- OIDC or managed auth
- MFA
- RBAC
- Session expiry
- Device/session history

Add:

- Request IDs
- Structured logs
- Security monitoring
- Alerting
- WAF/rate limiting at edge
- Vendor risk register
- Incident response runbook
- Compliance review gates
