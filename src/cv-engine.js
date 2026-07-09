const engineLayers = [
  {
    id: "intake-engine",
    name: "CV Intake Engine",
    status: "started",
    dovlyBenchmark: "Fast signup and AI roadmap",
    cvAdvantage: "Goal, timeline, risk, and partner-aware intake",
    nextBuild: "Connect intake answers to workflow priority and client tasks."
  },
  {
    id: "workflow-engine",
    name: "CV Workflow Engine",
    status: "started",
    dovlyBenchmark: "App progress and dispute cadence",
    cvAdvantage: "Admin/client workflow with next action, owner, due date, and compliance status",
    nextBuild: "Add durable status history and task assignment."
  },
  {
    id: "evidence-engine",
    name: "CV Evidence Engine",
    status: "not-built",
    dovlyBenchmark: "AI flags report issues",
    cvAdvantage: "Every issue must tie to uploaded evidence or report facts",
    nextBuild: "Build secure upload and document classification."
  },
  {
    id: "report-parser",
    name: "CV Report Parser",
    status: "not-built",
    dovlyBenchmark: "TransUnion report connection",
    cvAdvantage: "Designed for three-bureau comparison and manual upload first",
    nextBuild: "Parse report files into tradelines and bureau differences."
  },
  {
    id: "issue-classifier",
    name: "CV Issue Classifier",
    status: "designed",
    dovlyBenchmark: "Automated dispute optimization",
    cvAdvantage: "Classifies inaccurate, incomplete, outdated, duplicate, unverifiable, mixed-file, fraud, or accurate negative items",
    nextBuild: "Create issue records from parsed report data."
  },
  {
    id: "dispute-readiness",
    name: "CV Dispute Readiness Engine",
    status: "not-built",
    dovlyBenchmark: "Optimal number of disputes monthly",
    cvAdvantage: "Blocks unsupported disputes and scores readiness before drafting",
    nextBuild: "Add 0-5 readiness scoring with human review."
  },
  {
    id: "goal-readiness",
    name: "CV Goal Readiness Engine",
    status: "not-built",
    dovlyBenchmark: "Mortgage and credit goal content/tools",
    cvAdvantage: "Auto, mortgage, apartment, job, and funding-specific action plans",
    nextBuild: "Add goal plan templates and partner routing rules."
  },
  {
    id: "partner-engine",
    name: "CV Partner Engine",
    status: "not-built",
    dovlyBenchmark: "Consumer app distribution",
    cvAdvantage: "Mortgage, auto, rental, tax/accounting, and local professional referrals",
    nextBuild: "Track referral source, consent, and readiness milestone."
  },
  {
    id: "compliance-gate",
    name: "CV Compliance Gate",
    status: "started",
    dovlyBenchmark: "Marketing proof and app claims",
    cvAdvantage: "Conservative no-guarantee language and attorney-review routing",
    nextBuild: "Run every script/message/dispute draft through a rules checklist."
  }
];

function cvEngineStatus() {
  const started = engineLayers.filter((layer) => layer.status === "started").length;
  const designed = engineLayers.filter((layer) => layer.status === "designed").length;
  const notBuilt = engineLayers.filter((layer) => layer.status === "not-built").length;

  return {
    ok: true,
    name: "CreditVivo CV Engine",
    positioning:
      "Evidence-first credit readiness workflow for consumers with real approval goals and messy files.",
    benchmark:
      "Dovly wins the mass-market app lane; CreditVivo should win the guided workflow, partner, and evidence-review lane.",
    counts: { started, designed, notBuilt, total: engineLayers.length },
    layers: engineLayers,
    nextBuildOrder: [
      "secure authentication",
      "secure document vault",
      "production database",
      "document classifier",
      "report parser",
      "issue classifier",
      "dispute readiness scoring",
      "partner referral tracking",
      "client portal tasks/messages",
      "evidence-bound AI summaries"
    ],
    guardrails: [
      "No score guarantees.",
      "No deletion guarantees.",
      "No approval guarantees.",
      "No unsupported disputes.",
      "No fake fraud or identity theft claims.",
      "No sensitive data through public forms, ordinary SMS, or unsecured email.",
      "Human review before high-risk dispute/legal escalation."
    ]
  };
}

module.exports = { cvEngineStatus, engineLayers };
