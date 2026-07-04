import Link from "next/link";
import type {
  CustomerDocument,
  CustomerTask,
  DraftLetter,
  IdentityVerification,
  MemberPortalPayload,
  PortalStatus,
  ProgressMilestone,
  ReviewAccount,
} from "@/types/credit-vivo-member";
import { creditVivoConfig } from "@/lib/credit-vivo/config";
import { CVBrainUploadTester } from "@/components/member-portal/CVBrainUploadTester";

const navItems = [
  ["Overview", "/member"],
  ["Upload", "/member/upload"],
  ["Findings", "/member/findings"],
  ["Accounts", "/member/accounts"],
  ["Disputes", "/member/disputes"],
  ["Progress", "/member/progress"],
  ["Documents", "/member/documents"],
  ["Messages", "/member/messages"],
  ["Security", "/member/security"],
];

function statusClass(status: PortalStatus | string) {
  const lower = String(status).toLowerCase();
  if (lower.includes("complete") || lower.includes("passed")) return "bg-emerald-100 text-emerald-700";
  if (lower.includes("current") || lower.includes("review") || lower.includes("pending")) return "bg-amber-100 text-amber-800";
  if (lower.includes("blocked") || lower.includes("fail")) return "bg-red-100 text-red-700";
  return "bg-slate-100 text-slate-500";
}

function priorityClass(priority: string) {
  if (priority === "High") return "bg-red-50 text-red-700 border-red-100";
  if (priority === "Medium") return "bg-amber-50 text-amber-800 border-amber-100";
  if (priority === "Hold") return "bg-slate-50 text-slate-600 border-slate-100";
  return "bg-emerald-50 text-emerald-700 border-emerald-100";
}

function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
      <h3 className="text-xl font-bold text-slate-950">{title}</h3>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-600">{message}</p>
    </div>
  );
}

function ProductionGateBanner({ payload }: { payload: MemberPortalPayload }) {
  const gate = payload.productionGate;
  const ok = gate.customerDataAllowed;

  return (
    <div className={`rounded-3xl border p-5 ${ok ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}`}>
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <p className={`text-sm font-bold ${ok ? "text-emerald-900" : "text-amber-900"}`}>
            {ok ? "Production gates passed" : "Production gate active"}
          </p>
          <p className={`mt-1 text-sm ${ok ? "text-emerald-800" : "text-amber-800"}`}>{gate.message}</p>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs md:grid-cols-5">
          {[
            ["Health", gate.healthCheckPassed],
            ["Ground Truth", gate.groundTruthPassed],
            ["QA", gate.qaVerificationPassed],
            ["Security", gate.securityAuditPassed],
            ["Production", gate.productionGatePassed],
          ].map(([label, passed]) => (
            <span key={String(label)} className="rounded-full bg-white px-3 py-2 font-semibold text-slate-700">
              {label}: {passed ? "Pass" : "Blocked"}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export function MemberShell({
  payload,
  title,
  subtitle,
  children,
}: {
  payload: MemberPortalPayload;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  const profileName = payload.profile?.name || "Member";

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 lg:px-8">
          <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
            <Link href="/member" className="text-2xl font-black tracking-tight text-slate-950">
              Credit <span className="text-emerald-600">Vivo</span>
            </Link>
            <nav className="flex flex-wrap gap-2">
              {navItems.map(([label, href]) => (
                <Link
                  key={href}
                  href={href}
                  className="rounded-full px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-emerald-50 hover:text-emerald-700"
                >
                  {label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        <div className="rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-900 p-8 text-white shadow-xl">
          <p className="text-sm font-semibold text-emerald-200">Member Portal</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight">{title.replace("{name}", profileName)}</h1>
          <p className="mt-3 max-w-3xl text-slate-300">{subtitle}</p>
          <p className="mt-5 text-xs leading-5 text-slate-400">{creditVivoConfig.disclosure}</p>
        </div>

        <div className="mt-6">
          <ProductionGateBanner payload={payload} />
        </div>

        <div className="mt-8">{children}</div>
      </section>
    </main>
  );
}

export function MemberOverviewPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell
      payload={payload}
      title="Welcome back, {name}"
      subtitle="Track your review, approve drafts, and see the next step. No letters are sent without your approval."
    >
      {payload.stats.length === 0 ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_0.85fr]">
          <CustomerTasksCard tasks={payload.customerTasks || []} />
          <IdentityVerificationCard verification={payload.identityVerification} />
          <div className="lg:col-span-2">
            <MilestonesCard milestones={payload.progressMilestones || []} />
          </div>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {payload.stats.map((stat) => (
              <div key={stat.label} className="rounded-3xl bg-white p-6 shadow-sm">
                <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                <p className="mt-2 text-3xl font-black text-slate-950">{stat.value}</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">{stat.detail}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <NextActionCard payload={payload} />
              <div className="mt-6">
                <AccountsPreview accounts={payload.reviewAccounts} />
              </div>
            </div>
            <ProgressCard payload={payload} />
          </div>
        </>
      )}
    </MemberShell>
  );
}

function NextActionCard({ payload }: { payload: MemberPortalPayload }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-emerald-700">Next action</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">
            {payload.profile?.nextAction || "Connect approved scanner backend"}
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Findings and drafts stay hidden until production gates pass.
          </p>
        </div>
        <Link href="/member/security" className="rounded-full bg-slate-950 px-5 py-3 text-center text-sm font-bold text-white hover:bg-slate-800">
          View gates
        </Link>
      </div>
    </div>
  );
}

function AccountsPreview({ accounts }: { accounts: ReviewAccount[] }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Accounts to review</h2>
      <div className="mt-5 space-y-4">
        {accounts.length === 0 ? (
          <EmptyState title="No findings released" message="Customer findings are blocked until the scanner backend passes every production gate." />
        ) : (
          accounts.slice(0, 4).map((account) => <AccountCard key={account.id} account={account} />)
        )}
      </div>
    </div>
  );
}

function AccountCard({ account }: { account: ReviewAccount }) {
  return (
    <div className="rounded-2xl border border-slate-100 p-5">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-full border px-3 py-1 text-xs font-bold ${priorityClass(account.priority)}`}>
              {account.priority}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">
              {account.status}
            </span>
          </div>
          <h3 className="mt-3 text-lg font-bold text-slate-950">{account.name}</h3>
          <p className="mt-1 text-sm font-medium text-slate-500">{account.type}</p>
          <p className="mt-3 text-sm leading-6 text-slate-600">{account.customerSummary}</p>
          <p className="mt-3 text-sm font-semibold text-slate-700">Next: {account.nextStep}</p>
        </div>
      </div>
    </div>
  );
}

function ProgressCard({ payload }: { payload: MemberPortalPayload }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Progress tracker</h2>
      <div className="mt-6 space-y-5">
        {payload.progressSteps.length === 0 ? (
          <EmptyState title="No progress yet" message="Progress appears after backend connection." />
        ) : (
          payload.progressSteps.map((step, index) => (
            <div key={step.title} className="flex gap-4">
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                step.status === "complete" ? "bg-emerald-600 text-white" :
                step.status === "current" ? "bg-slate-950 text-white" :
                step.status === "blocked" ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-400"
              }`}>
                {index + 1}
              </div>
              <div>
                <p className="font-semibold text-slate-950">{step.title}</p>
                <p className="text-sm leading-6 text-slate-500">{step.description}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function CustomerTasksCard({ tasks }: { tasks: CustomerTask[] }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Customer tasks</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        These are the next safe steps before any report review or customer-approved dispute prep can move forward.
      </p>
      <div className="mt-5 space-y-3">
        {tasks.length === 0 ? (
          <EmptyState title="No tasks loaded" message="Customer tasks appear after the portal backend is connected." />
        ) : (
          tasks.map((task) => (
            <div key={task.title} className="rounded-2xl border border-slate-100 p-4">
              <div className="flex flex-col justify-between gap-2 md:flex-row md:items-start">
                <div>
                  <h3 className="font-bold text-slate-950">{task.title}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{task.detail}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(task.status)}`}>
                  {task.status}
                </span>
              </div>
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{task.dueLabel}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function IdentityVerificationCard({ verification }: { verification?: IdentityVerification }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
        <div>
          <h2 className="text-2xl font-bold text-slate-950">Identity verification</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {verification?.summary || "Identity verification backend is not connected yet."}
          </p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(verification?.status || "blocked")}`}>
          {verification?.status || "blocked"}
        </span>
      </div>
      <div className="mt-5 space-y-3">
        {(verification?.checks || []).map((check) => (
          <div key={check.label} className="flex flex-col justify-between gap-2 rounded-2xl bg-slate-50 p-4 md:flex-row md:items-start">
            <div>
              <h3 className="font-bold text-slate-900">{check.label}</h3>
              <p className="mt-1 text-sm leading-6 text-slate-600">{check.note}</p>
            </div>
            <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(check.status)}`}>{check.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MilestonesCard({ milestones }: { milestones: ProgressMilestone[] }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Progress milestones</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        Credit Vivo tracks progress by verified steps, not guaranteed outcomes. Results vary and accurate information may remain.
      </p>
      <div className="mt-5 grid gap-4 lg:grid-cols-4">
        {milestones.length === 0 ? (
          <EmptyState title="No milestones loaded" message="Progress milestones appear after backend connection." />
        ) : (
          milestones.map((milestone) => (
            <div key={milestone.phase} className="rounded-2xl border border-slate-100 p-4">
              <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${statusClass(milestone.status)}`}>
                {milestone.status}
              </span>
              <h3 className="mt-3 font-bold text-slate-950">{milestone.phase}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{milestone.customerView}</p>
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{milestone.adminGate}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export function UploadPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Upload your credit reports" subtitle="Secure upload is disabled until the approved backend and encrypted storage are connected.">
      <div className="grid gap-4 md:grid-cols-3">
        {payload.uploads.map((upload) => (
          <div key={upload.bureau} className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-center shadow-sm">
            <h3 className="text-xl font-bold text-slate-950">{upload.bureau}</h3>
            <span className={`mt-3 inline-flex rounded-full px-3 py-1 text-xs font-bold ${statusClass(upload.status)}`}>
              {upload.status}
            </span>
            <p className="mt-3 text-sm text-slate-600">{upload.note}</p>
            <button disabled className="mt-5 rounded-full bg-slate-300 px-5 py-2 text-sm font-semibold text-white">
              Upload disabled
            </button>
          </div>
        ))}
      </div>
      <CVBrainUploadTester />
    </MemberShell>
  );
}

export function FindingsPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Your AI credit review" subtitle="Findings appear only after scanner health check and ground-truth validation pass.">
      {payload.reviewAccounts.length === 0 ? (
        <EmptyState title="Findings blocked" message="Production mode is active. Customer findings will appear after the approved scanner backend passes all gates." />
      ) : (
        <AccountsPreview accounts={payload.reviewAccounts} />
      )}
    </MemberShell>
  );
}

export function AccountsPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Accounts to review" subtitle="Customer-safe account review. No legal conclusions.">
      <div className="space-y-4">
        {payload.reviewAccounts.length === 0 ? (
          <EmptyState title="No accounts released" message="Accounts are hidden until the scanner passes health check, ground-truth validation, QA, security audit, and production gate." />
        ) : (
          payload.reviewAccounts.map((account) => <AccountCard key={account.id} account={account} />)
        )}
      </div>
    </MemberShell>
  );
}

export function DisputesPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Review dispute drafts" subtitle="All letters are draft-only and require approval. No auto-send.">
      <div className="space-y-4">
        {payload.draftLetters.length === 0 ? (
          <EmptyState title="No drafts released" message="Drafts are blocked until verified issue objects exist and scanner gates pass." />
        ) : (
          payload.draftLetters.map((letter) => <DraftLetterCard key={letter.id} letter={letter} />)
        )}
      </div>
    </MemberShell>
  );
}

function DraftLetterCard({ letter }: { letter: DraftLetter }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
        <div>
          <p className="text-sm font-semibold text-emerald-700">{letter.type}</p>
          <h3 className="mt-1 text-xl font-bold text-slate-950">{letter.account}</h3>
          <p className="mt-3 text-sm leading-6 text-slate-600">{letter.summary}</p>
        </div>
        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
          {letter.status}
        </span>
      </div>
      <label className="mt-5 flex items-start gap-3 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
        <input type="checkbox" className="mt-1" />
        I understand this is a draft and no letter is sent until I approve it.
      </label>
      <button disabled className="mt-4 rounded-full bg-slate-300 px-5 py-2 text-sm font-bold text-white">
        Approval disabled until backend is connected
      </button>
    </div>
  );
}

export function ProgressPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Track progress" subtitle="Follow your file from upload to response and next step.">
      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <ProgressCard payload={payload} />
        <MilestonesCard milestones={payload.progressMilestones || []} />
      </div>
    </MemberShell>
  );
}

export function DocumentsPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Document verification" subtitle="Required files must be readable, matched to the customer, and admin-reviewed before use.">
      {payload.documents.length === 0 ? (
        <EmptyState title="No documents released" message="Documents require secure backend storage and access controls." />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <IdentityVerificationCard verification={payload.identityVerification} />
          <div className="space-y-4">
            {payload.documents.map((doc) => <DocumentCard key={doc.name} doc={doc} />)}
          </div>
        </div>
      )}
    </MemberShell>
  );
}

function DocumentCard({ doc }: { doc: CustomerDocument }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h3 className="text-lg font-bold text-slate-950">{doc.name}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">{doc.note || "Awaiting review."}</p>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Required for: {doc.requiredFor || "Customer file"} / Use for prep: {doc.canUseForPrep ? "Yes" : "No"}
          </p>
          <p className="mt-1 text-sm text-slate-600">{doc.type} • {doc.visibility}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(doc.status)}`}>{doc.status}</span>
      </div>
    </div>
  );
}

export function MessagesPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Messages" subtitle="Credit Vivo updates and member support messages appear here.">
      <EmptyState title="Messages backend not connected" message="Messages require authenticated backend storage before production use." />
    </MemberShell>
  );
}

export function ProfilePage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Profile" subtitle="Basic member profile. Sensitive identity details are hidden by default.">
      <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">Profile readiness</h2>
          <dl className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              ["Name", payload.profile?.name || "Not connected"],
              ["Plan", payload.profile?.plan || "Not connected"],
              ["Score goal", payload.profile?.scoreGoal || "Not connected"],
              ["Report date", payload.profile?.reportDate || "Not connected"],
            ].map(([label, value]) => (
              <div key={label}>
                <dt className="text-sm text-slate-500">{label}</dt>
                <dd className="mt-1 font-bold text-slate-950">{value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-5 text-sm leading-6 text-slate-600">
            Full SSN, full ID number, raw credit reports, and bureau credentials should not display in the customer portal.
          </p>
        </div>
        <CustomerTasksCard tasks={payload.customerTasks || []} />
      </div>
    </MemberShell>
  );
}

export function SecurityPage({ payload }: { payload: MemberPortalPayload }) {
  const gate = payload.productionGate;
  const items = [
    ["Demo/mock mode", gate.demoMode ? "On" : "Off"],
    ["Scanner API", gate.scannerConnected ? "Connected" : "Not connected"],
    ["Health check", gate.healthCheckPassed ? "Passed" : "Blocked"],
    ["Ground truth", gate.groundTruthPassed ? "Passed" : "Blocked"],
    ["QA verification", gate.qaVerificationPassed ? "Passed" : "Blocked"],
    ["Security audit", gate.securityAuditPassed ? "Passed" : "Blocked"],
    ["Production gate", gate.productionGatePassed ? "Passed" : "Blocked"],
    ["Auto-send", "Disabled"],
    ["Draft letters", "Approval required"],
  ];

  return (
    <MemberShell payload={payload} title="Security & approvals" subtitle="A+ production controls keep member data and dispute actions protected.">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map(([label, value]) => (
          <div key={label} className="rounded-3xl bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-black text-slate-950">{value}</p>
          </div>
        ))}
      </div>
    </MemberShell>
  );
}

export function SettingsPage({ payload }: { payload: MemberPortalPayload }) {
  return (
    <MemberShell payload={payload} title="Settings" subtitle="Member preferences and notification settings.">
      <EmptyState title="Settings backend not connected" message="Settings require authenticated backend storage before production use." />
    </MemberShell>
  );
}
