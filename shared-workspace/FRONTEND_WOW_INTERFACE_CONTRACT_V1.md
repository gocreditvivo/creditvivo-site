# Credit Vivo Frontend WOW — Interface Contract v1

**Contract version:** `frontend-wow-contract-v1`  
**Prepared:** 2026-07-26  
**Branch:** `codex/frontend-wow-integration-v1`  
**Base:** `coordination/frontend-wow-readiness-2026-07-26`  
**Audience:** Claude frontend lane, ChatGPT coordination, Tim Do  
**Release status:** Preview contract only. No production approval.

This contract records what the current repository actually supports and the boundary Claude may build against. Unknown or unsafe behavior is blocked rather than inferred.

## 1. Current route inventory

Public layout routes:

- `/`
- `/why`
- `/pricing`
- `/faq`
- `/learning`
- `/join`
- `/signup` (same current component as `/join`)
- `/reviews`
- `/compliance`
- `/privacy`
- `/terms`
- `/disclosure`
- `/investor-demo`
- `/auto-loan-denial`
- `/mortgage-readiness`
- `/apartment-denial`
- `/collection-not-mine`
- `/status`

Current dashboard-layout routes (not authenticated or role-gated today):

- `/dashboard`
- `/login` (currently renders the dashboard, not a login flow)
- `/scan`
- `/findings`
- `/founder-health`
- `/owner-ai`
- `/growth-ai`
- `/admin-review`
- `/bank-link`

There is no explicit 404 route. Founder/admin and customer routes currently share one unguarded layout.

## 2. Available backend endpoints

Frontend-supported scanner endpoints:

- `GET /api/health`
- `GET /api/scanner/health`
- `POST /api/scanner/parse`
- `GET /api/scanner/result/{job_id}`
- `GET /api/scanner/result/{job_id}/full`
- `GET /api/scanner/result/{job_id}/download/{download_name}` where `download_name` is `workbook.xlsx`, `issues.csv`, `tradelines.csv`, or `letters.txt`

Existing backend endpoints that are not approved as customer frontend contracts:

- `GET /api/admin/users/setup`
- `POST /api/admin/users/create`
- `GET /api/admin/users/list`
- `POST /api/events/track`
- `GET /api/events/summary`
- `POST /api/leads/capture`
- `GET /api/leads/summary`
- growth/operator/owner endpoints under `/api/growth-ai/*`, `/api/operator-ai/*`, and `/api/vivo-command/*`

These non-scanner endpoints use local/file-backed storage or setup tokens and are not a substitute for production auth, tenancy, or RLS.

## 3. Request and response examples

Scanner upload request:

```http
POST /api/scanner/parse
Content-Type: multipart/form-data
X-Credit-Vivo-Scanner-Token: SERVER-MEDIATED-ONLY
X-Credit-Vivo-Device-Id: trusted-device-id

files=<one-to-three PDF files>
use_ai_second_pass=false
```

The scanner token must never be compiled into Vite client code. Until a server-side authenticated proxy exists, production scanner upload is `blocked_integration`; preview must use clearly labeled synthetic data.

Successful response excerpt:

```json
{
  "job_id": "scan_12hexchars",
  "files": [{"filename":"synthetic-report.pdf","bureau":"Experian","status":"extracted"}],
  "ai_second_pass": false,
  "paid_ai_used": false,
  "status": {
    "mode": "credit_vivo_proprietary_engine_v16",
    "message": "Parsed using Credit Vivo proprietary rule engine. No paid AI API used."
  },
  "review_items_count": 1,
  "review_items_preview": [],
  "issues_count": 0,
  "issues_preview": [],
  "recommended_letter_queue": [],
  "fcra_review": []
}
```

Blocked response shape:

```json
{
  "detail": {
    "ok": false,
    "blocked": true,
    "safe_mode": true,
    "message": "Scanner access check failed. No scan, letters, exports, or customer-facing findings are allowed."
  }
}
```

## 4. TypeScript interfaces

Claude may consume the existing scanner types in `src/lib/scannerApi.ts`, but new UI work should program to this additive boundary:

```ts
export type DataMode = 'synthetic_demo' | 'live_backend' | 'unavailable';
export type UserRole = 'customer' | 'support' | 'admin' | 'owner';
export type ImportStatus =
  | 'not_started' | 'selecting_files' | 'uploading' | 'extracting'
  | 'analyzing' | 'completed' | 'failed' | 'blocked';
export type ScannerStatus =
  | 'idle' | 'queued' | 'preflight' | 'parsing' | 'grouping'
  | 'findings_ready' | 'failed' | 'blocked_safe_mode';
export type ApprovalDecision = 'pending' | 'approved' | 'held' | 'rejected';
export type TimelineStatus =
  | 'not_started' | 'current' | 'completed' | 'waiting_customer'
  | 'waiting_admin' | 'blocked' | 'failed';

export interface IntegrationMeta {
  contractVersion: 'frontend-wow-contract-v1';
  dataMode: DataMode;
  synthetic: boolean;
  source: 'credit_vivo_scanner_v16' | 'frontend_mock_v1' | 'none';
  generatedAt: string;
}

export interface FindingView {
  id: string;
  accountId?: string;
  bureau?: 'Experian' | 'Equifax' | 'TransUnion' | 'Unknown';
  category: string;
  title: string;
  possibleIssue: true;
  customerExplanation: string;
  sourceFields: Array<{ field: string; value: string; source?: string }>;
  differenceDetected?: string;
  documentsNeeded: string[];
  nextStep: string;
  requiresAdminReview: boolean;
  legalConclusion: false;
  confidence?: 'low' | 'medium' | 'high';
}

export interface CustomerApproval {
  findingId: string;
  decision: ApprovalDecision;
  decidedAt?: string;
  decisionBy?: string;
  note?: string;
  authorizationForAutomaticDispute: false;
}

export interface TimelineItem {
  id: string;
  kind: 'imported' | 'analyzed' | 'findings_ready' | 'customer_decision'
    | 'admin_review' | 'preparation' | 'submitted' | 'response' | 'next_action';
  status: TimelineStatus;
  label: string;
  occurredAt?: string;
  blockedReason?: string;
  synthetic: boolean;
}
```

## 5. Permitted status values

Use only the values in the interfaces above for new WOW flow state. Do not derive progress from timers and present it as live backend work. Existing backend `status.mode` and `status.message` are display metadata, not a complete lifecycle state machine.

## 6. Scanner/import lifecycle events

Permitted event names:

- `report_import_started`
- `report_upload_completed`
- `report_extraction_started`
- `report_extraction_completed`
- `scanner_preflight_started`
- `scanner_preflight_blocked`
- `scanner_analysis_started`
- `scanner_analysis_completed`
- `findings_ready`
- `customer_decision_recorded`
- `admin_review_started`
- `admin_review_completed`
- `dispute_draft_prepared`
- `dispute_submitted` (only after an externally confirmed submission)
- `bureau_response_recorded`
- `next_action_recorded`

Every event requires `eventId`, `eventType`, `occurredAt`, `actorRole`, `customerId` or tenant-scoped subject identifier, `dataMode`, `synthetic`, `source`, `correlationId`, and safe metadata. Never log report text, full account numbers, SSN, DOB, auth tokens, or PDFs.

The existing `/api/events/track` endpoint is not approved for customer workflow audit history because it lacks the demonstrated authenticated tenant boundary and immutable audit guarantees.

## 7. Findings data structure

Use `FindingView`. A finding is always a **possible issue for review**, never a legal violation, guaranteed error, deletion promise, or score-impact prediction. `legalConclusion` must remain `false`. Any confidence value describes parser/review confidence only and must not be shown as legal confidence or expected score impact.

## 8. Customer approval structure

Use `CustomerApproval`. Approval authorizes only the explicitly described next review/preparation step. It does not authorize automatic dispute submission. `authorizationForAutomaticDispute` is fixed to `false` for this phase.

## 9. Timeline status structure

Use `TimelineItem`. `submitted` may be `completed` only when a real submission system or an authorized administrator records confirmed evidence. Synthetic timelines must keep `synthetic: true` on every item and display a persistent demo label.

## 10. Authentication assumptions

Confirmed current state:

- No frontend auth provider or session guard is wired in `src/App.tsx`.
- `/login` renders the dashboard.
- Customer, admin, founder, and owner routes are reachable without a route guard.
- Backend scanner production access uses a shared scanner token plus device ID, which cannot safely be placed in a browser bundle.
- Admin user provisioning explicitly states that full production login still requires an auth provider.

Therefore all protected routes are preview-only until authenticated server-side session validation and tenant/role authorization are implemented.

## 11. Role definitions

- `customer`: may access only their own onboarding, imports, findings, approvals, documents, and timeline.
- `support`: may access assigned customer support metadata; no scanner-rule, security-policy, user-provisioning, or submission authority.
- `admin`: may review tenant-scoped cases and prepare approved drafts; no owner-only settings or production release authority.
- `owner`: founder-authorized operational access; production release still requires Tim Do's written approval.

Frontend role display is not authorization. Server endpoints and database policies must enforce role and ownership.

## 12. Error codes and blocked states

Normalize UI errors to:

- `AUTH_REQUIRED`
- `FORBIDDEN_ROLE`
- `TENANT_MISMATCH`
- `SCANNER_NOT_CONFIGURED`
- `SCANNER_PREFLIGHT_BLOCKED`
- `SCANNER_ACCESS_BLOCKED`
- `INVALID_FILE_TYPE`
- `FILE_TOO_LARGE`
- `TOO_MANY_FILES`
- `EMPTY_FILE`
- `RESULT_NOT_FOUND`
- `NETWORK_ERROR`
- `BACKEND_UNAVAILABLE`
- `PRODUCTION_WRITE_BLOCKED`
- `UNKNOWN_ERROR`

A blocked state is not a generic error: it must preserve the reason, prevent progression, show a safe next step, and emit no fake completion event.

## 13. Mock service contract

```ts
export interface WowJourneyService {
  readonly mode: DataMode;
  startImport(input: { files?: File[]; syntheticScenarioId?: string }): Promise<{ jobId: string; status: ImportStatus; meta: IntegrationMeta }>;
  getScannerState(jobId: string): Promise<{ status: ScannerStatus; message: string; meta: IntegrationMeta }>;
  getFindings(jobId: string): Promise<{ findings: FindingView[]; meta: IntegrationMeta }>;
  recordCustomerDecision(input: CustomerApproval): Promise<{ approval: CustomerApproval; meta: IntegrationMeta }>;
  getTimeline(subjectId: string): Promise<{ items: TimelineItem[]; meta: IntegrationMeta }>;
}
```

Mock IDs must be deterministic, use fictional names and account identifiers, persist only in browser memory/session storage for preview, perform no network writes, and return `dataMode: 'synthetic_demo'`, `synthetic: true`, and `source: 'frontend_mock_v1'` on every response.

## 14. Which data is actually live

Potentially live when the backend is configured and access requirements are satisfied:

- scanner service health/preflight
- PDF upload and parser output
- job result retrieval and generated downloads
- file-backed lead/event/admin/growth endpoints (not approved as customer production contracts)

No live claim is made until the endpoint is tested in the target preview environment.

## 15. Which data must remain mocked

Until auth, tenancy, RLS, durable workflow storage, and audit controls are implemented and verified:

- signup/login/session
- customer profile and disclosures/agreement acceptance
- customer/admin role assignment
- customer-specific dashboard
- approval persistence
- admin review queue
- dispute preparation workflow state
- dispute submission
- bureau responses
- progress timeline
- founder operational metrics
- bank connection
- score changes, outcomes, confidence percentages, or customer results

## 16. Known integration blockers

1. No authenticated frontend session or server-verified role guard.
2. Customer and admin/founder routes are not separated by authorization.
3. Production scanner requires secret token/device headers; current `src/lib/scannerApi.ts` sends neither. A browser must not receive the shared token.
4. Scanner results are stored in browser `localStorage`, which is not an approved location for live credit-report findings or raw evidence.
5. Current result URLs are job-ID based and show no demonstrated customer ownership check.
6. No demonstrated Supabase schema/RLS contract for this journey.
7. Existing file-backed events are not an immutable tenant-scoped audit log.
8. Backend defaults `SCANNER_WRITE_RAW_TEXT` to `true`; production health blocks this, but preview configuration must still be independently verified.
9. Vercel serverless local filesystem is ephemeral; durable customer workflow state is not established.
10. Claude acknowledgement/package and exact owned-file list are still pending.

## 17. Exact shared files Claude may consume

Read/consume without modifying unless written transfer is recorded:

- `shared-workspace/FRONTEND_WOW_INTERFACE_CONTRACT_V1.md`
- `src/lib/scannerApi.ts`
- `src/lib/scanStorage.ts` (demo shape reference only; not approved for live sensitive data)
- `src/App.tsx` (route inventory reference)
- `AGENTS.md`
- `shared-workspace/TEAM_HANDOFF_PROTOCOL.md`
- `shared-workspace/TEAM_ACTIVE_HANDOFF.md`
- `shared-workspace/FRONTEND_WOW_BUILD_READINESS_2026-07-26.md`

## 18. Exact files Codex owns

- `shared-workspace/FRONTEND_WOW_INTERFACE_CONTRACT_V1.md`
- future additive contracts under `src/contracts/creditVivoJourney.ts`
- future backend adapter code under `src/services/scanner/` only after confirming no Claude overlap
- `scanner_backend/**`
- `api/**`
- `supabase/**`
- security/test evidence and integration tests explicitly added under a non-Claude path such as `tests/integration/**`
- `vercel.json` and backend/deployment configuration, subject to preview-only and founder approval gates

## 19. Exact files Codex will not modify

Without a written transfer from Claude/ChatGPT, Codex will not modify:

- `src/pages/**`
- `src/components/**`
- `src/journey/**`
- `src/dashboard/customer/**`
- `src/dashboard/founder/**`
- `src/state/journeyMachine.*`
- `src/mocks/**`
- `tests/frontend/**`
- visual tokens, CSS, copy, layout, motion, or Claude-owned accessibility implementation

## Required architecture decision before live integration

Select and document a server-mediated authenticated scanner adapter and tenant-scoped durable storage model. The adapter must derive customer identity from the server session, keep scanner secrets server-side, bind every job/result/download to the authorized customer/tenant, enforce role checks, emit redacted audit events, and deny production writes in preview. Supabase/RLS changes require a separate architecture checkpoint and review before implementation.
