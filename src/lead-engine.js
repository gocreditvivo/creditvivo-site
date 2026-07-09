const crypto = require("crypto");
const { engine } = require("./config");

const allowed = {
  goals: [
    "Auto approval",
    "Mortgage readiness",
    "Apartment approval",
    "Credit card or loan",
    "Identity theft help",
    "General credit clarity"
  ],
  scoreRanges: ["Under 580", "580-639", "640-699", "700+", "Not sure"],
  plans: ["Free Review", "Plus - $59/mo", "Pro - $99/mo", "Legal+ eligibility"],
  contactPreferences: ["Email", "Phone", "Text"]
};

const readinessRules = {
  "Under 580": { tier: "rebuild", path: "Review + Repair + Protect", priority: 85 },
  "580-639": { tier: "repair-build", path: "Review + Repair + Build", priority: 70 },
  "640-699": { tier: "optimize", path: "Optimize + Build + Prepare", priority: 55 },
  "700+": { tier: "protect", path: "Maintain + Monitor + Protect", priority: 35 },
  "Not sure": { tier: "clarify", path: "Scan + Clarify + Plan", priority: 60 }
};

function cleanText(value, maxLength = 160) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maxLength);
}

function cleanPhone(value) {
  return String(value || "")
    .replace(/[^\d()+\-\s.]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 32);
}

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function recommendationFor(lead) {
  const base = readinessRules[lead.scoreRange] || readinessRules["Not sure"];
  const escalations = [];

  if (lead.goal === "Identity theft help") escalations.push("identity-protection-review");
  if (lead.planInterest === "Legal+ eligibility") escalations.push("attorney-supported-eligibility-review");
  if (["Under 580", "580-639"].includes(lead.scoreRange)) escalations.push("document-first-report-review");

  return {
    modelVersion: engine.modelVersion,
    mode: engine.mode,
    readinessTier: base.tier,
    recommendedPath: base.path,
    priorityScore: Math.min(100, base.priority + escalations.length * 5),
    escalations,
    nextAction: "review-request-intake"
  };
}

function buildLead(input, req, hashIp) {
  const lead = {
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
    status: "new",
    name: cleanText(input.name, 80),
    email: cleanText(input.email, 120).toLowerCase(),
    phone: cleanPhone(input.phone),
    goal: cleanText(input.goal, 80),
    scoreRange: cleanText(input.scoreRange, 40),
    planInterest: cleanText(input.planInterest, 40),
    preferredContact: cleanText(input.preferredContact || "Email", 40),
    source: cleanText(input.source || "website", 80),
    notes: cleanText(input.notes, 280),
    ipHash: hashIp(req)
  };

  const errors = [];
  if (lead.name.length < 2) errors.push("Name is required.");
  if (!isEmail(lead.email)) errors.push("A valid email is required.");
  if (!allowed.goals.includes(lead.goal)) errors.push("Choose a valid credit goal.");
  if (!allowed.scoreRanges.includes(lead.scoreRange)) errors.push("Choose a valid score range.");
  if (!allowed.plans.includes(lead.planInterest)) errors.push("Choose a valid plan interest.");
  if (!allowed.contactPreferences.includes(lead.preferredContact)) errors.push("Choose a valid contact preference.");
  if (cleanText(input.companyWebsite, 120)) errors.push("Unable to save this review request.");

  const recommendation = errors.length ? null : recommendationFor(lead);
  return { lead: { ...lead, recommendation }, errors };
}

function engineStatus() {
  return {
    ok: true,
    modelVersion: engine.modelVersion,
    mode: engine.mode,
    allowSelfModify: engine.allowSelfModify,
    supportedGoals: allowed.goals,
    supportedScoreRanges: allowed.scoreRanges,
    supportedPlans: allowed.plans
  };
}

function selfDiagnostics({ app, storage }) {
  const findings = [];
  if (app.isProduction && app.host === "127.0.0.1") findings.push("Production should bind behind a managed HTTPS reverse proxy.");
  if (storage.adapter === "local-json-atomic") findings.push("Replace local JSON with encrypted managed database before real customer data.");
  if (!engine.allowSelfModify) findings.push("Self-update is advisory only: engine reports recommended fixes but does not rewrite code.");

  return {
    ok: true,
    modelVersion: engine.modelVersion,
    mode: engine.mode,
    app,
    storage,
    findings,
    recommendedUpgrades: [
      "managed encrypted database",
      "OIDC admin/customer auth with MFA",
      "AI provider abstraction with human approval gates",
      "knowledge engine for compliance, technology, and innovation materials",
      "immutable audit log",
      "queue-backed workflow engine",
      "security monitoring and alerting"
    ]
  };
}

module.exports = { allowed, buildLead, recommendationFor, engineStatus, selfDiagnostics };
