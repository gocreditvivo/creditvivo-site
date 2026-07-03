import Link from "next/link";

type GateStatus = "passed" | "needs_review" | "failed" | "blocked";

type ProductionGateItem = {
  id: string;
  title: string;
  plainEnglishLabel: string;
  status: GateStatus;
  score: number;
  checks: {
    id: string;
    label: string;
    status: GateStatus;
    whyItMatters: string;
    fixRequired?: string;
  }[];
};

type CriticalFix = {
  id: string;
  title: string;
  whyItMatters: string;
  owner: string;
  status: GateStatus;
  priority: "Critical" | "High" | "Medium" | "Low";
  nextAction: string;
};

type ProductionCertificationPayload = {
  overallStatus: GateStatus;
  launchRecommendation: "ready" | "controlled_beta" | "blocked";
  plainEnglishSummary: string;
  gates: ProductionGateItem[];
  criticalFixes: CriticalFix[];
  todayActions: string[];
  customerPipeline: { stage: string; count: number }[];
  approvalQueue: { label: string; count: number }[];
  scannerTrust: {
    lastVerificationStatus: GateStatus;
    v9Match: GateStatus;
    groundTruth: GateStatus;
    securityAudit: GateStatus;
    productionGate: GateStatus;
    summary: string;
  };
};

const productionCertificationMock: ProductionCertificationPayload = {
  overallStatus: "blocked",
  launchRecommendation: "blocked",
  plainEnglishSummary:
    "Credit Vivo is not ready for live customers yet. Scanner accuracy is improving, but ground-truth validation, production gate, and security audit must be completed first.",
  gates: [
    {
      id: "scanner",
      title: "Scanner Accuracy",
      plainEnglishLabel: "Can we trust the scan?",
      status: "needs_review",
      score: 82,
      checks: [
        {
          id: "bureau",
          label: "3 bureaus detected correctly",
          status: "passed",
          whyItMatters: "Prevents accounts from being placed under the wrong bureau.",
        },
        {
          id: "negative",
          label: "Negative accounts captured",
          status: "needs_review",
          whyItMatters: "Makes sure score-impacting accounts are not missed.",
        },
        {
          id: "positive",
          label: "Positive accounts protected",
          status: "passed",
          whyItMatters: "Prevents good accounts from being disputed by mistake.",
        },
        {
          id: "v9",
          label: "v9 workbook matches template",
          status: "failed",
          whyItMatters: "Founder/admin output must match the approved forensic layout.",
          fixRequired: "Expand workbook depth and add v9 title/header rows.",
        },
      ],
    },
    {
      id: "ground-truth",
      title: "Ground Truth",
      plainEnglishLabel: "Does the workbook match the raw reports?",
      status: "blocked",
      score: 40,
      checks: [
        {
          id: "raw-json",
          label: "Raw report to JSON matched",
          status: "blocked",
          whyItMatters: "Confirms the scanner output matches the uploaded reports.",
          fixRequired: "Build raw PDF → JSON validation.",
        },
        {
          id: "json-workbook",
          label: "JSON to workbook matched",
          status: "blocked",
          whyItMatters: "Prevents workbook errors from reaching customers.",
          fixRequired: "Build JSON → workbook validation.",
        },
      ],
    },
    {
      id: "compliance",
      title: "Compliance",
      plainEnglishLabel: "Are our words and approval rules safe?",
      status: "needs_review",
      score: 88,
      checks: [
        {
          id: "draft-only",
          label: "Letters draft-only",
          status: "passed",
          whyItMatters: "No customer letter should go out without approval.",
        },
        {
          id: "no-guarantees",
          label: "No guarantee language",
          status: "passed",
          whyItMatters: "Keeps marketing and portal language safer.",
        },
        {
          id: "attorney",
          label: "Attorney wording safe",
          status: "passed",
          whyItMatters: "Attorney support must be eligibility-based.",
        },
      ],
    },
    {
      id: "security",
      title: "Security",
      plainEnglishLabel: "Is customer data protected?",
      status: "blocked",
      score: 65,
      checks: [
        {
          id: "upload",
          label: "Secure upload backend",
          status: "blocked",
          whyItMatters: "Credit reports must not be handled by unsafe storage.",
          fixRequired: "Connect encrypted upload storage and audit logs.",
        },
        {
          id: "audit",
          label: "Audit logs",
          status: "needs_review",
          whyItMatters: "Every sensitive action must be traceable.",
        },
      ],
    },
    {
      id: "operations",
      title: "Operations",
      plainEnglishLabel: "Can the team handle real customers safely?",
      status: "needs_review",
      score: 75,
      checks: [
        {
          id: "contact-board",
          label: "Contact board ready",
          status: "needs_review",
          whyItMatters: "Leads and customers need clear next actions.",
        },
        {
          id: "email",
          label: "Production email setup",
          status: "needs_review",
          whyItMatters: "Customers need trusted support communication.",
        },
      ],
    },
  ],
  criticalFixes: [
    {
      id: "fix-gt",
      title: "Add Ground Truth Validation",
      whyItMatters: "Prevents wrong scanner results from reaching customers.",
      owner: "Engineering",
      status: "blocked",
      priority: "Critical",
      nextAction: "Send to Codex",
    },
    {
      id: "fix-prod",
      title: "Add Production Gate",
      whyItMatters: "Blocks customer results unless all checks pass.",
      owner: "Engineering",
      status: "blocked",
      priority: "Critical",
      nextAction: "Build gate",
    },
    {
      id: "fix-security",
      title: "Connect Secure Upload Backend",
      whyItMatters: "Customer reports need encrypted storage and audit logs.",
      owner: "Security/Engineering",
      status: "blocked",
      priority: "Critical",
      nextAction: "Connect backend",
    },
  ],
  todayActions: [
    "Do not launch while red gates are active.",
    "Send Ground Truth Validation task to Codex.",
    "Review secure upload backend plan.",
    "Confirm production email DNS setup.",
  ],
  customerPipeline: [
    { stage: "New Leads", count: 0 },
    { stage: "Report Needed", count: 0 },
    { stage: "Scan Ready", count: 0 },
    { stage: "Findings Ready", count: 0 },
    { stage: "Drafts Ready", count: 0 },
    { stage: "Active Customers", count: 0 },
    { stage: "Waiting for Response", count: 0 },
  ],
  approvalQueue: [
    { label: "Customer approvals", count: 0 },
    { label: "Admin approvals", count: 0 },
    { label: "Risky wording blocked", count: 0 },
    { label: "Attorney review candidates", count: 0 },
  ],
  scannerTrust: {
    lastVerificationStatus: "failed",
    v9Match: "failed",
    groundTruth: "blocked",
    securityAudit: "blocked",
    productionGate: "blocked",
    summary:
      "Scanner output contains major account groups, but it is missing Ground Truth Validation, Security Audit Summary, Production Gate, and full v9 depth.",
  },
};

function statusStyle(status: GateStatus) {
  if (status === "passed") return "bg-emerald-100 text-emerald-800 border-emerald-200";
  if (status === "needs_review") return "bg-amber-100 text-amber-800 border-amber-200";
  return "bg-red-100 text-red-800 border-red-200";
}

function statusLabel(status: GateStatus) {
  if (status === "passed") return "Passed";
  if (status === "needs_review") return "Needs Review";
  if (status === "failed") return "Failed";
  return "Blocked";
}

function scoreColor(score: number) {
  if (score >= 90) return "bg-emerald-500";
  if (score >= 75) return "bg-amber-500";
  return "bg-red-500";
}

export default function ProductionCertificationPage({
  payload = productionCertificationMock,
}: {
  payload?: ProductionCertificationPayload;
}) {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="grid min-h-screen lg:grid-cols-[280px_1fr]">
        <aside className="border-r border-slate-200 bg-white p-5">
          <div className="text-2xl font-black text-slate-950">
            Credit <span className="text-emerald-600">Vivo</span>
          </div>
          <p className="mt-1 text-sm text-slate-500">Founder Command Center</p>

          <nav className="mt-8 space-y-6 text-sm">
            {[
              ["Command Center", ["Overview", "Production Certification", "Launch Checklist", "Today’s Actions"]],
              ["Customers", ["Contact Board", "Customers", "Report Uploads", "Findings Ready", "Draft Approvals"]],
              ["Scanner", ["Scanner Health", "Scan Jobs", "v9 Workbook", "Ground Truth", "QA Verification"]],
              ["Disputes", ["Draft Letters", "Approval Queue", "Mail Tracking", "Responses", "Attorney Review"]],
              ["Compliance", ["Compliance Dashboard", "Security Audit", "Vendor Risk", "Audit Logs"]],
            ].map(([section, items]) => (
              <div key={section as string}>
                <p className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-400">{section}</p>
                <div className="space-y-1">
                  {(items as string[]).map((item) => (
                    <a
                      key={item}
                      className={`block rounded-xl px-3 py-2 font-semibold ${
                        item === "Production Certification"
                          ? "bg-emerald-50 text-emerald-700"
                          : "text-slate-600 hover:bg-slate-50"
                      }`}
                      href="#"
                    >
                      {item}
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        </aside>

        <section className="p-6 lg:p-8">
          <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
            <div>
              <div className={`inline-flex rounded-full border px-3 py-1 text-sm font-bold ${statusStyle(payload.overallStatus)}`}>
                {statusLabel(payload.overallStatus)}
              </div>
              <h1 className="mt-4 text-4xl font-black tracking-tight text-slate-950">
                Production Certification
              </h1>
              <p className="mt-2 max-w-3xl text-slate-600">
                A simple launch-readiness view for scanner accuracy, security, compliance, and customer safety.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button className="rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white">Export Report</button>
              <button className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700">Send to Codex</button>
              <button className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700">Mark Reviewed</button>
            </div>
          </div>

          <div className="mt-8 rounded-3xl border border-red-200 bg-red-50 p-6">
            <p className="text-sm font-bold uppercase tracking-wide text-red-700">Launch recommendation</p>
            <h2 className="mt-2 text-3xl font-black text-red-950">
              Credit Vivo is not production-ready yet.
            </h2>
            <p className="mt-3 max-w-4xl text-red-800">{payload.plainEnglishSummary}</p>
          </div>

          <div className="mt-8 grid gap-4 xl:grid-cols-5">
            {payload.gates.map((gate) => (
              <GateCard key={gate.id} gate={gate} />
            ))}
          </div>

          <div className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_.9fr]">
            <CriticalFixes fixes={payload.criticalFixes} />
            <TodayActions actions={payload.todayActions} />
          </div>

          <div className="mt-8 grid gap-6 xl:grid-cols-3">
            <ScannerTrustPanel payload={payload} />
            <PipelineSnapshot payload={payload} />
            <ApprovalSnapshot payload={payload} />
          </div>
        </section>
      </div>
    </main>
  );
}

function GateCard({ gate }: { gate: ProductionGateItem }) {
  return (
    <div className="rounded-3xl bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-bold text-slate-950">{gate.title}</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">{gate.plainEnglishLabel}</p>
        </div>
        <span className={`rounded-full border px-2.5 py-1 text-xs font-bold ${statusStyle(gate.status)}`}>
          {statusLabel(gate.status)}
        </span>
      </div>
      <div className="mt-5">
        <div className="flex items-center justify-between text-xs font-bold text-slate-500">
          <span>Score</span>
          <span>{gate.score}%</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-slate-100">
          <div className={`h-2 rounded-full ${scoreColor(gate.score)}`} style={{ width: `${gate.score}%` }} />
        </div>
      </div>
      <div className="mt-5 space-y-2">
        {gate.checks.slice(0, 3).map((check) => (
          <div key={check.id} className="flex items-start gap-2 text-xs">
            <span className={`mt-0.5 h-2.5 w-2.5 rounded-full ${
              check.status === "passed" ? "bg-emerald-500" :
              check.status === "needs_review" ? "bg-amber-500" : "bg-red-500"
            }`} />
            <span className="text-slate-600">{check.label}</span>
          </div>
        ))}
      </div>
      <button className="mt-5 w-full rounded-full border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700">
        View Details
      </button>
    </div>
  );
}

function CriticalFixes({ fixes }: { fixes: CriticalFix[] }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-black text-slate-950">What must be fixed before launch</h2>
      <div className="mt-5 space-y-4">
        {fixes.map((fix) => (
          <div key={fix.id} className="rounded-2xl border border-slate-100 p-4">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
              <div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-700">{fix.priority}</span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{fix.owner}</span>
                </div>
                <h3 className="mt-3 text-lg font-bold text-slate-950">{fix.title}</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">{fix.whyItMatters}</p>
              </div>
              <button className="rounded-full bg-slate-950 px-4 py-2 text-sm font-bold text-white">
                {fix.nextAction}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TodayActions({ actions }: { actions: string[] }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-black text-slate-950">Today’s Actions</h2>
      <div className="mt-5 space-y-3">
        {actions.map((action) => (
          <div key={action} className="rounded-2xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-700">{action}</p>
            <div className="mt-3 flex gap-2">
              <button className="rounded-full bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white">Done</button>
              <button className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-slate-600">Snooze</button>
              <button className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-slate-600">Assign</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScannerTrustPanel({ payload }: { payload: ProductionCertificationPayload }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-black text-slate-950">Can I trust the scanner?</h2>
      <p className="mt-3 text-sm leading-6 text-slate-600">{payload.scannerTrust.summary}</p>
      <div className="mt-5 space-y-2">
        {[
          ["v9 Match", payload.scannerTrust.v9Match],
          ["Ground Truth", payload.scannerTrust.groundTruth],
          ["Security Audit", payload.scannerTrust.securityAudit],
          ["Production Gate", payload.scannerTrust.productionGate],
        ].map(([label, status]) => (
          <div key={label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
            <span className="text-sm font-semibold text-slate-700">{label}</span>
            <span className={`rounded-full border px-3 py-1 text-xs font-bold ${statusStyle(status as GateStatus)}`}>
              {statusLabel(status as GateStatus)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function PipelineSnapshot({ payload }: { payload: ProductionCertificationPayload }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-black text-slate-950">Customer Pipeline</h2>
      <div className="mt-5 space-y-2">
        {payload.customerPipeline.map((item) => (
          <div key={item.stage} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
            <span className="text-sm font-semibold text-slate-700">{item.stage}</span>
            <span className="text-lg font-black text-slate-950">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ApprovalSnapshot({ payload }: { payload: ProductionCertificationPayload }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-black text-slate-950">Approval Queue</h2>
      <p className="mt-2 text-sm text-slate-600">Inactive until scanner gates pass.</p>
      <div className="mt-5 space-y-2">
        {payload.approvalQueue.map((item) => (
          <div key={item.label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
            <span className="text-sm font-semibold text-slate-700">{item.label}</span>
            <span className="text-lg font-black text-slate-950">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
