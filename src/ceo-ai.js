const crypto = require("crypto");
const { ai, app, engine, storage } = require("./config");
const { readJson, writeJson, readLeads, storageDiagnostics } = require("./storage");
const { buildGrowthPlan, retentionPlan } = require("./growth-engine");
const { knowledgeMaterials } = require("./knowledge-engine");
const { readLatestDebugReport } = require("./debug-engine");
const { smsStatus } = require("./sms");

const CEO_VERSION = "minitim-founder-ai-v0.2.0";
const FOUNDER_ONLY = "founder-token-plus-device-key";

const SENSITIVE_ACTIONS = [
  "send_email",
  "publish_ad",
  "change_dns",
  "charge_card",
  "refund_payment",
  "export_customer_data",
  "delete_record",
  "legal_claim",
  "contact_partner",
  "change_security_policy"
];

const DOMAIN_GUARDS = [
  "No autonomous external actions.",
  "No credit repair guarantees.",
  "No legal advice without attorney review.",
  "No customer PII in ordinary prompts or logs.",
  "No funds, ads, DNS, email, or data exports without founder approval.",
  "No self-modifying code in production."
];

function now() {
  return new Date().toISOString();
}

function id(prefix) {
  return `${prefix}_${Date.now().toString(36)}_${crypto.randomBytes(4).toString("hex")}`;
}

function hashRecord(record, previousHash = "genesis") {
  return crypto
    .createHash("sha256")
    .update(`${previousHash}:${JSON.stringify(record)}`)
    .digest("hex");
}

function readMemory() {
  return readJson(storage.ceoMemoryFile);
}

function writeMemory(memory) {
  writeJson(storage.ceoMemoryFile, memory.slice(-200));
}

function readActions() {
  return readJson(storage.ceoActionsFile);
}

function writeActions(actions) {
  writeJson(storage.ceoActionsFile, actions);
}

function readAudit() {
  return readJson(storage.ceoAuditFile);
}

function appendAudit(event) {
  const audit = readAudit();
  const previous = audit[audit.length - 1]?.hash || "genesis";
  const entry = {
    id: id("audit"),
    at: now(),
    actor: "founder",
    event,
    previousHash: previous
  };
  entry.hash = hashRecord(entry, previous);
  audit.push(entry);
  writeJson(storage.ceoAuditFile, audit.slice(-500));
  return entry;
}

function classifyIntent(message) {
  const text = String(message || "").toLowerCase();
  if (/email|inbox|gmail|workspace|support@|legal@|billing@/.test(text)) return "workspace_admin";
  if (/security|hack|breach|mfa|2fa|private|domain|dns/.test(text)) return "security";
  if (/ad|marketing|lead|customer|get customer|growth|campaign/.test(text)) return "growth";
  if (/law|attorney|compliance|fcra|croa|audit|legal/.test(text)) return "compliance";
  if (/money|price|revenue|budget|investor|valuation|funding/.test(text)) return "finance";
  if (/build|backend|frontend|deploy|api|database|engine|model/.test(text)) return "product_tech";
  return "operator";
}

function riskLevel(message) {
  const text = String(message || "").toLowerCase();
  if (/password|ssn|social security|bank account|routing|credit card|private key|api key/.test(text)) return "critical";
  if (/send|publish|delete|charge|refund|dns|domain|export|attorney|legal claim|lawsuit/.test(text)) return "high";
  if (/customer|lead|pricing|ad|compliance|security/.test(text)) return "medium";
  return "low";
}

function nextActionsFor(intent, message) {
  const base = {
    workspace_admin: [
      "Verify support inbox routing with test emails for every alias.",
      "Remove the extra SupportLegal label after confirming no filters use it.",
      "Create response templates for support, legal, security, billing, partners, and investors."
    ],
    security: [
      "Require MFA on every admin account.",
      "Rotate any default admin tokens before production.",
      "Move audit logs and customer data to encrypted managed storage before real customers."
    ],
    growth: [
      "Build an approval-gated campaign board before running ads.",
      "Track every lead by source, cost, stage, and retention risk.",
      "Use compliant benefits language and avoid guaranteed score outcomes."
    ],
    compliance: [
      "Route credit repair claims through compliance review before publishing.",
      "Create attorney-review status flags for legal escalation content.",
      "Keep signed consent, cancellation, and service-scope artifacts audit-ready."
    ],
    finance: [
      "Keep launch budget, burn, runway, CAC, LTV, and cash-control dashboards in one founder view.",
      "Separate operating funds, tax reserves, customer payments, and vendor spend.",
      "Require founder approval for spend outside approved budgets."
    ],
    product_tech: [
      "Use role-based auth, encrypted document storage, and immutable audit logs before real credit files.",
      "Keep AI suggestions separate from approved actions.",
      "Add model evals for compliance, privacy, and hallucination risk."
    ],
    operator: [
      "Turn the request into a task, assign a risk level, and decide whether it needs founder approval.",
      "Check business, compliance, security, and customer impact before action.",
      "Log the decision for future founder review."
    ]
  };

  const actions = base[intent] || base.operator;
  if (riskLevel(message) === "high" || riskLevel(message) === "critical") {
    return ["Stop before external action; create approval item first.", ...actions];
  }
  return actions;
}

function buildContext() {
  const leads = readLeads();
  const knowledge = knowledgeMaterials();
  const latestDebug = readLatestDebugReport();
  const growth = buildGrowthPlan(leads, { monthlyBudget: 3000 });
  const retention = retentionPlan(leads);
  return {
    app: {
      name: app.name,
      version: app.version,
      mode: app.env,
      aiMode: engine.mode,
      allowSelfModify: engine.allowSelfModify
    },
    leadCount: leads.length,
    debugStatus: latestDebug.exists ? latestDebug.scan.status : "no-debug-run",
    growthMode: growth.mode,
    retentionSegments: retention.segments.length,
    installedComplianceGates: knowledge.complianceMaterials.length,
    storage: storageDiagnostics()
  };
}

function extractOutputText(data) {
  if (typeof data.output_text === "string") return data.output_text;
  const chunks = [];
  (data.output || []).forEach((item) => {
    (item.content || []).forEach((content) => {
      if (typeof content.text === "string") chunks.push(content.text);
      if (typeof content.output_text === "string") chunks.push(content.output_text);
    });
  });
  return chunks.join("\n").trim();
}

async function callOpenAI({ message, intent, risk, context }) {
  if (!ai.openaiApiKey) return null;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ai.requestTimeoutMs);
  const instructions = [
    "You are MiniTim, Credit Vivo's founder-only CEO Mirror AI.",
    "Speak directly to the founder with concise executive judgment.",
    "You can advise, prioritize, draft, and identify risks.",
    "You cannot claim to have sent emails, published ads, changed DNS, charged money, contacted customers, contacted partners, accessed private files, or executed external actions.",
    "Any sensitive action must be framed as a pending approval item.",
    "Avoid credit repair guarantees, legal advice, or claims that accurate negative information can always be removed.",
    "Keep customer data, passwords, API keys, SSNs, credit reports, and banking data out of ordinary responses.",
    "Return practical next steps for Credit Vivo."
  ].join("\n");

  try {
    const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      signal: controller.signal,
      headers: {
        Authorization: `Bearer ${ai.openaiApiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: ai.openaiModel,
        instructions,
        input: [
          `Founder request: ${message}`,
          `Classified intent: ${intent}`,
          `Risk level: ${risk}`,
          `Current system context: ${JSON.stringify(context)}`
        ].join("\n\n"),
        reasoning: { effort: risk === "critical" || risk === "high" ? "medium" : "low" },
        text: { verbosity: "low" }
      })
    });

    const data = await response.json();
    if (!response.ok) {
      return {
        provider: "openai-error-fallback",
        text: "",
        error: data.error?.message || "OpenAI request failed."
      };
    }

    return {
      provider: "openai-responses",
      model: ai.openaiModel,
      text: extractOutputText(data),
      responseId: data.id || null
    };
  } catch (error) {
    return {
      provider: "openai-error-fallback",
      text: "",
      error: error.name === "AbortError" ? "OpenAI request timed out." : "OpenAI request failed."
    };
  } finally {
    clearTimeout(timeout);
  }
}

function createApprovalAction({ title, description, category, risk, sourceMessage }) {
  const actions = readActions();
  const action = {
    id: id("action"),
    createdAt: now(),
    status: "pending_founder_approval",
    category,
    risk,
    title,
    description,
    sourceMessage: String(sourceMessage || "").slice(0, 1000),
    approvalRequired: true,
    blockedExternalEffects: SENSITIVE_ACTIONS
  };
  actions.push(action);
  writeActions(actions);
  appendAudit({ type: "action_created", actionId: action.id, category, risk });
  return action;
}

async function founderChat(input = {}) {
  const message = String(input.message || "").trim().slice(0, 2000);
  if (!message) {
    return { ok: false, errors: ["Message is required."] };
  }

  const intent = classifyIntent(message);
  const risk = riskLevel(message);
  const context = buildContext();
  const memory = readMemory();
  const shouldQueue = risk === "high" || risk === "critical" || /do it|go ahead|execute|send|publish|delete|change|charge/i.test(message);

  const action = shouldQueue
    ? createApprovalAction({
        title: `Founder approval needed: ${intent.replace("_", " ")}`,
        description: "CEO AI prepared guidance but blocked external execution until the founder approves the exact action.",
        category: intent,
        risk,
        sourceMessage: message
      })
    : null;

  const modelResult = await callOpenAI({ message, intent, risk, context });
  const modelText = modelResult?.text && modelResult.text.trim()
    ? modelResult.text.trim()
    : "";

  const response = {
    ok: true,
    ceoVersion: CEO_VERSION,
    assistantName: "MiniTim",
    aiProvider: modelResult?.provider || "rules-fallback",
    aiModel: modelResult?.model || null,
    aiError: modelResult?.error || null,
    founderOnly: true,
    intent,
    risk,
    summary: `I read this as a ${intent.replace("_", " ")} request with ${risk} risk.`,
    answer: modelText ? [modelText] : [
      "I can act as Credit Vivo's founder-only mirror AI: organize decisions, spot risk, draft actions, and keep the company moving.",
      "For fintech quality, I will separate advice from execution. Sensitive actions go to an approval queue before anything external happens.",
      "The current MVP is local and rules-driven. A production version should add SSO/MFA, encrypted database storage, model gateway logging, role-based access, and attorney/compliance review gates."
    ],
    nextActions: nextActionsFor(intent, message),
    blockedActions: risk === "low" ? [] : SENSITIVE_ACTIONS,
    approvalAction: action,
    context
  };

    memory.push({
    id: id("memory"),
    at: now(),
    founderMessage: message,
    intent,
    risk,
    queuedActionId: action?.id || null,
    responseSummary: response.summary,
    aiProvider: response.aiProvider
  });
  writeMemory(memory);
  appendAudit({ type: "founder_chat", intent, risk, queuedActionId: action?.id || null });
  return response;
}

function ceoStatus() {
  const actions = readActions();
  const audit = readAudit();
  return {
    ok: true,
    assistantName: "MiniTim",
    ceoVersion: CEO_VERSION,
    founderOnlyMode: FOUNDER_ONLY,
    securityPosture: "mvp-founder-device-locked-production-needs-sms-passkey-managed-auth",
    aiProvider: ai.provider,
    aiModel: ai.openaiModel,
    deepLearningStatus: ai.openaiApiKey
      ? "openai-responses-enabled-no-autonomous-training-on-private-data"
      : "rules-fallback-configure-openai-api-key-for-live-model-chat",
    autonomyPolicy: "approval-gated",
    guards: DOMAIN_GUARDS,
    blockedExternalActions: SENSITIVE_ACTIONS,
    pendingActions: actions.filter((action) => action.status === "pending_founder_approval"),
    auditCount: audit.length,
    latestAuditHash: audit[audit.length - 1]?.hash || null,
    sms: smsStatus(),
    context: buildContext()
  };
}

function updateAction(actionId, decision) {
  const actions = readActions();
  const action = actions.find((item) => item.id === actionId);
  if (!action) return { ok: false, errors: ["Action not found."] };

  const normalized = decision === "approve" ? "approved_by_founder" : "rejected_by_founder";
  action.status = normalized;
  action.decidedAt = now();
  action.note = normalized === "approved_by_founder"
    ? "Approved for manual execution. External automation remains disabled in MVP."
    : "Rejected by founder.";
  writeActions(actions);
  appendAudit({ type: "action_decision", actionId, status: normalized });
  return { ok: true, action };
}

module.exports = { ceoStatus, founderChat, updateAction };
