const crypto = require("crypto");

const allowedStages = new Set([
  "intake-review",
  "waiting-client-docs",
  "documents-received",
  "analysis-in-progress",
  "needs-more-evidence",
  "action-plan-ready",
  "client-approved-plan",
  "dispute-drafting",
  "compliance-review",
  "sent-to-client",
  "sent-to-bureau-or-furnisher",
  "waiting-response",
  "response-received",
  "updated-plan",
  "monthly-follow-up",
  "closed-complete",
  "closed-inactive",
  "attorney-review-lead"
]);

const demoWorkflows = [
  {
    name: "Maria L.",
    goal: "Auto loan in 60 days",
    stage: "waiting-client-docs",
    track: "repair-review",
    risk: "normal",
    owner: "Tim",
    due: "2026-07-12",
    next: "Request Experian report and collection letter.",
    docs: ["Equifax report", "TransUnion report"],
    missing: ["Experian report", "collection letter"],
    issues: "4 possible reporting issues need evidence review",
    contact: "Text"
  },
  {
    name: "Derrick P.",
    goal: "Apartment approval",
    stage: "analysis-in-progress",
    track: "prepare-track",
    risk: "normal",
    owner: "Reviewer",
    due: "2026-07-10",
    next: "Separate accurate negative items from possible duplicate collection reporting.",
    docs: ["Three-bureau report", "denial letter"],
    missing: [],
    issues: "1 duplicate collection lead, 2 build-plan items",
    contact: "Email"
  },
  {
    name: "Samantha R.",
    goal: "Unknown account / fraud concern",
    stage: "attorney-review-lead",
    track: "protect-track",
    risk: "attorney-review",
    owner: "Founder",
    due: "2026-07-09",
    next: "Prepare attorney eligibility packet; do not give legal conclusion.",
    docs: ["Credit report", "FTC identity theft report"],
    missing: ["Creditor response letter"],
    issues: "Identity theft and repeated verified reporting concern",
    contact: "Phone"
  },
  {
    name: "Kevin T.",
    goal: "Mortgage readiness",
    stage: "monthly-follow-up",
    track: "prepare-track",
    risk: "normal",
    owner: "Support",
    due: "2026-07-08",
    next: "Send monthly update and request new report snapshot.",
    docs: ["Prior action plan", "utilization worksheet"],
    missing: ["Updated report snapshot"],
    issues: "Build plan and utilization follow-up",
    contact: "Email"
  },
  {
    name: "Alicia B.",
    goal: "Review possible outdated items",
    stage: "action-plan-ready",
    track: "repair-review",
    risk: "normal",
    owner: "Tim",
    due: "2026-07-11",
    next: "Review action plan with client before any dispute drafting.",
    docs: ["Three-bureau report", "payment proof"],
    missing: [],
    issues: "2 possible outdated/incomplete reporting items",
    contact: "Text"
  }
];

function cleanText(value, maxLength = 240) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maxLength);
}

function cleanList(value) {
  if (!Array.isArray(value)) return [];
  return value.map((item) => cleanText(item, 120)).filter(Boolean).slice(0, 12);
}

function normalizeWorkflow(input, existing = {}) {
  const now = new Date().toISOString();
  const stage = cleanText(input.stage || existing.stage || "intake-review", 60);
  return {
    id: existing.id || input.id || crypto.randomUUID(),
    createdAt: existing.createdAt || now,
    updatedAt: now,
    name: cleanText(input.name || existing.name, 80),
    goal: cleanText(input.goal || existing.goal, 120),
    stage: allowedStages.has(stage) ? stage : "intake-review",
    track: cleanText(input.track || existing.track || "repair-review", 60),
    risk: cleanText(input.risk || existing.risk || "normal", 40),
    owner: cleanText(input.owner || existing.owner || "Tim", 60),
    due: cleanText(input.due || existing.due, 20),
    next: cleanText(input.next || existing.next, 220),
    docs: cleanList(input.docs || existing.docs),
    missing: cleanList(input.missing || existing.missing),
    issues: cleanText(input.issues || existing.issues, 220),
    contact: cleanText(input.contact || existing.contact || "Email", 40),
    completedActions: Array.isArray(existing.completedActions) ? existing.completedActions : []
  };
}

function workflowFromLead(lead) {
  const escalations = lead.recommendation?.escalations || [];
  let track = "prepare-track";
  let stage = "intake-review";
  let risk = "normal";
  let next = "Complete intake review and classify the file before requesting documents.";
  const missing = [];
  const docs = [];

  if (lead.goal === "Identity theft help" || escalations.includes("identity-protection-review")) {
    track = "protect-track";
    stage = "waiting-client-docs";
    missing.push("three-bureau credit report", "identity theft or fraud documentation if already available");
    next = "Request reports and fraud/identity documents through a secure process.";
  } else if (lead.planInterest === "Legal+ eligibility" || escalations.includes("attorney-supported-eligibility-review")) {
    track = "attorney-review-lead";
    stage = "attorney-review-lead";
    risk = "attorney-review";
    missing.push("case documents or creditor letters");
    next = "Prepare attorney eligibility packet; do not give legal conclusion.";
  } else if (escalations.includes("document-first-report-review") || ["Under 580", "580-639"].includes(lead.scoreRange)) {
    track = "repair-review";
    stage = "waiting-client-docs";
    missing.push("Equifax report", "Experian report", "TransUnion report");
    next = "Request three-bureau reports and any creditor/collection letters through a secure process.";
  } else if (["700+", "640-699"].includes(lead.scoreRange)) {
    track = "prepare-track";
    next = "Review goal timeline and build approval-readiness checklist.";
  }

  return normalizeWorkflow({
    name: lead.name,
    goal: lead.goal,
    stage,
    track,
    risk,
    owner: "Tim",
    due: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    next,
    docs,
    missing,
    issues: "New lead promoted from website intake. Needs human review before any dispute action.",
    contact: lead.preferredContact || "Email"
  });
}

function seedWorkflows(readWorkflows, writeWorkflows) {
  const existing = readWorkflows();
  if (existing.length) return existing;
  const seeded = demoWorkflows.map((record) => normalizeWorkflow(record));
  writeWorkflows(seeded);
  return seeded;
}

function workflowSummary(records) {
  return {
    active: records.filter((record) => !record.stage.startsWith("closed-")).length,
    needDocuments: records.filter((record) => record.missing.length).length,
    attorneyReview: records.filter((record) => record.stage === "attorney-review-lead").length,
    followUpsDue: records.filter((record) => record.stage === "monthly-follow-up").length
  };
}

function buildSafeUpdate(record) {
  return [
    `Quick CreditVivo update for ${record.name}:`,
    `Current stage: ${record.stage}.`,
    `Next step: ${record.next}`,
    record.missing.length
      ? `We still need: ${record.missing.join(", ")}.`
      : "We do not need additional documents from you right now.",
    "CreditVivo reviews possible inaccurate, incomplete, outdated, duplicate, unverifiable, mixed-file, or fraud-related reporting. Results are not guaranteed and depend on the facts, evidence, and bureau/furnisher investigation."
  ].join(" ");
}

function safeClientWorkflow(record) {
  return {
    id: record.id,
    name: record.name,
    goal: record.goal,
    stage: record.stage,
    track: record.track,
    next: record.next,
    due: record.due,
    missingCount: record.missing.length,
    missing: record.missing,
    contact: record.contact,
    updatedAt: record.updatedAt,
    expectations:
      "CreditVivo reviews possible inaccurate, incomplete, outdated, duplicate, unverifiable, mixed-file, or fraud-related reporting. Results are not guaranteed and depend on the facts, evidence, and bureau/furnisher investigation.",
    sensitiveDataWarning:
      "Do not send Social Security numbers, bureau passwords, IDs, full account numbers, or credit report files through ordinary text or email."
  };
}

function markNextActionDone(records, id) {
  const index = records.findIndex((record) => record.id === id);
  if (index === -1) return { records, record: null };
  const existing = records[index];
  const completedActions = [
    ...(existing.completedActions || []),
    {
      completedAt: new Date().toISOString(),
      action: existing.next || "Next action"
    }
  ];
  const updated = {
    ...existing,
    updatedAt: new Date().toISOString(),
    completedActions,
    next: "Set the next workflow action.",
    stage: existing.stage === "monthly-follow-up" ? "updated-plan" : existing.stage
  };
  const nextRecords = records.slice();
  nextRecords[index] = updated;
  return { records: nextRecords, record: updated };
}

module.exports = {
  allowedStages,
  buildSafeUpdate,
  markNextActionDone,
  normalizeWorkflow,
  safeClientWorkflow,
  seedWorkflows,
  workflowFromLead,
  workflowSummary
};
