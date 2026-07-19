# Claude Frontend Package Review

Created: 2026-07-18

Owner: Codex verification after Tim provides the zip/package.

Status: Package described by Claude, not verified by Codex yet.

## What Claude Says Was Delivered

Claude reports an offline package:

`CreditVivo_Frontend_Package.zip`

Reported contents:

- 15-step customer journey
- customer dashboard
- manager dashboard
- founder dashboard
- journey state machine
- typed synthetic fixtures
- mock adapter
- design tokens
- UI primitives
- role-gated routing
- four test suites

## Useful Product Ideas

- Journey Spine: always shows where the customer is and whose turn it is.
- Clear holder model: customer, CreditVivo, bureau.
- All screens render through a shared state renderer.
- Findings are customer-safe shaped: last 4 only, possible issue language, no raw report text.
- Admin review remains a gate before dispute preparation.

## Integration Caution

Claude says the package was built for:

`root Vite + React + TypeScript`

The current Codex-confirmed workspace target is:

`CommonJS Node/server.js app with root static files`

Current UI files include:

- `index.html`
- `admin.html`
- `workflow-admin.html`
- `client-status.html`
- `styles.css`
- `script.js`

Backend routes are:

- `server.js`
- `src/app.js`

Do not merge the package directly until Tim/Codex decide whether CreditVivo is staying static/Node for now or adding a separate Vite/React frontend package.

## Claude's Known Limitations

Claude could not run:

- `npm install`
- build
- tests
- browser screenshots

So Codex must treat first integration as real verification.

## Codex Verification Checklist

When Tim provides the zip/package:

1. Inspect package structure and dependencies.
2. Confirm whether it assumes Vite, React, TypeScript, React Router, or other dependencies not currently in `package.json`.
3. Run install/build/tests in an isolated branch/folder.
4. Check for secrets or real customer data.
5. Check account masking assumptions.
6. Check no auto-send behavior.
7. Check role gates are enforced server-side before production use.
8. Decide integration path:
   - keep as design reference,
   - port selected screens to static Node app,
   - add separate frontend app,
   - or reject/rework.

## Current Codex Decision

Do not integrate yet.

Use Claude's package as architecture input until the actual zip is uploaded and verified.
