# Codex Handoff — Credit Vivo production-readiness pass

**Date:** 2026-07-28
**Branch delivered:** `fix/next-production-ready`
**Head commit:** `1a7920e`
**Prepared by:** Claude (Cowork) senior-audit + fix session

---

## TL;DR for the next agent

The repo was a broken half-migration (Vite SPA + Next.js mixed in one working tree, build failing). It now **builds green as a pure Next.js 15 app** and all required public routes return 200. Work is committed on `fix/next-production-ready`. `main` is untouched. **Nothing is pushed yet.**

Do not `git reset --hard`, `git checkout .`, or `git pull` on this branch without reading "Recovery safety" below — the pre-fix state is preserved in one snapshot commit and must not be lost.

---

## Verified status (evidence, not optimism)

- `npm run build` → **exit 0**, "Compiled successfully", 24 routes prerendered (Next.js 15.5.22).
- Production server (`next start`) HTTP checks: `/` 200, `/scan` 200, `/chat` 200, `/member` 200, `/findings` 200.
- `npm audit --omit=dev` → 3 high-severity advisories remain (see "Security" — do NOT force-fix).

---

## What was changed (and why)

1. **Decided architecture = Next.js 15 App Router.** The committed history (`main` / `origin/main`) was a Vite + React 18 + react-router-dom + lucide-react + tailwind + supabase SPA. The working tree had already been rewritten to Next.js 15 + React 19 (root `app/` tree, API routes, new `package.json`). We finished the Next.js migration rather than revert.

2. **Removed the orphaned Vite SPA under `src/`.** It was the sole cause of the build failure: Next was compiling `src/pages/*` as a Pages Router, and those files import `react-router-dom` / `lucide-react`, which the new `package.json` dropped. Confirmed first that the root `app/` tree imports nothing from `src/` (only from root `components/`). Removed the entire `src/` directory.

3. **Added `app/member/page.jsx`.** `/member` was a required public route with no directory (404). Added a member-portal landing page in the app house style (BrandLogo, `var(--cv-font)`, gradient), linking to dashboard / findings / scan / disputes / monthly / messages / vault / chat.

4. **Repaired the install and patched Next.** `node_modules/.bin/next` was missing; ran `npm install` to regenerate shims and restore the TS dev deps Next needs. `npm audit fix` bumped Next 15.5.19 → **15.5.22** (latest 15.x backport patch).

5. **`.gitignore` hygiene.** Added `.next/`, `next-env.d.ts`, `tsconfig.tsbuildinfo`, and `next-dev*.log`; untracked the dev logs that had been committed.

---

## Recovery safety (read before any git surgery)

- Commit `083d421` ("Snapshot: in-progress Next.js migration before production-readiness fixes") captures the **entire pre-fix working tree**, including the full `src/` Vite SPA and the `build-agent` files. If anything here needs to come back, recover it from `083d421`, e.g. `git checkout 083d421 -- src/`.
- The fix commit is `1a7920e` on top of that snapshot.
- `main` still points at `e85085a` and was not modified.

---

## Current git position

- Local `main` (`e85085a`) is **14+ commits behind** `origin/main`. The remote-tracking ref is stale — real `origin/main` is `edb51f0` (was `ba69131` locally). A `git fetch` will show it further behind.
- This fix branch is built on `e85085a`, NOT on current `origin/main`. **Before merging, reconcile with the current remote** — `origin/main` advanced independently (homepage redesign work) while this migration was done on an old base.
- Relevant remote branches you own: `codex/website-redesign-v1` (`be5bf74`), `codex/credit-vivo-scanner-portal-foundation` (`67a7b1a`), plus ~10 other `codex/*` / `coordination/*` / `posthog/*` branches.

---

## ⚠️ Concurrent-edit warning

While this fix was running, an external process on the machine (another codex agent or an open editor) modified the repo mid-session: it **deleted `app/build-agent/page.jsx`, `app/api/build-agent/route.js`, and `components/BuildAgentClient.jsx`, and modified `app/globals.css`** — none of which were this session's changes. The green build reflects the build-agent feature being gone.

**Action needed:** confirm whether removing the "build agent" page was intentional. If NOT, restore it from the snapshot:
`git checkout 083d421 -- app/build-agent app/api/build-agent components/BuildAgentClient.jsx`
…then re-add its nav link and re-run `npm run build`. Also ensure only one agent/editor writes to this working tree at a time, or commits will collide.

---

## Security (do NOT auto-fix)

`npm audit --omit=dev` reports 3 high-severity advisories, all transitive deps bundled inside Next.js (`postcss`, `sharp`) plus Next itself. **Do not run `npm audit fix --force`** — its only offered fix downgrades to `next@9.3.3`, which destroys the app. No stable Next release clears these yet (the advisory range covers up to the current `latest` 16.2.12; the patch is only in `16.3.0-preview`/canary). Revisit when Next 16.3 ships stable, then upgrade and re-audit. `sharp@0.34.5`'s native install script was not auto-approved (`npm approve-scripts sharp` if image optimization is needed at runtime).

---

## Suggested next steps for codex

1. Confirm/settle the build-agent deletion question above.
2. Reconcile `fix/next-production-ready` against current `origin/main` (`edb51f0`) — port the homepage redesign work or rebase, resolving the Vite→Next divergence.
3. Wire real backends for the launch-preview features currently stubbed (scan, chatbot, disputes, messages) — see `app/api/*`.
4. Open a PR from the reconciled branch into `main`; require a green `npm run build` in CI.
5. Keep only one automated agent writing to this working tree at a time.
