const fs = require("fs");
const http = require("http");
const path = require("path");
const { app, security } = require("./config");
const { MIME_TYPES, securityHeaders, sendJson } = require("./http");
const { isAdmin, isFounderDevice, isRateLimited, hashIp } = require("./security");
const {
  ensureStore,
  readLeads,
  readWorkflows,
  writeLeads,
  writeWorkflows,
  storageDiagnostics
} = require("./storage");
const { buildLead, engineStatus, selfDiagnostics, recommendationFor } = require("./lead-engine");
const { automationStatus, buildGrowthPlan, retentionPlan } = require("./growth-engine");
const { strategicPlan } = require("./strategic-intelligence");
const { knowledgeMaterials, knowledgeSummary } = require("./knowledge-engine");
const { readLatestDebugReport, runDebugScan } = require("./debug-engine");
const { ceoStatus, founderChat, updateAction } = require("./ceo-ai");
const { sendFounderSms } = require("./sms");
const { operatingStatus } = require("./operating-system");
const { cvEngineStatus } = require("./cv-engine");
const {
  buildSafeUpdate,
  markNextActionDone,
  normalizeWorkflow,
  safeClientWorkflow,
  seedWorkflows,
  workflowFromLead,
  workflowSummary
} = require("./workflow-engine");

const PUBLIC_FILES = new Set([
  "/index.html",
  "/admin.html",
  "/ceo.html",
  "/client-status.html",
  "/creditvivo-command.html",
  "/workflow-admin.html",
  "/CREDITVIVO_CLIENT_WORKFLOW.md",
  "/CREDITVIVO_MASTER_OPERATING_CHECKLIST.md",
  "/CREDITVIVO_SALES_AND_ONBOARDING_SCRIPT.md",
  "/CREDITVIVO_FOLLOWUP_TEMPLATE_PACK.md",
  "/CV_ENGINE_BLUEPRINT_DOVLY_PLUS_2026-07-08.md",
  "/DOVLY_VS_CREDITVIVO_DEEP_BENCHMARK_2026-07-08.md",
  "/PARTNER_OUTREACH_TEMPLATES.md",
  "/script.js",
  "/styles.css"
]);
const PUBLIC_PREFIXES = ["/assets/", "/images/"];

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > security.maxBodyBytes) {
        reject(new Error("Payload too large"));
        req.destroy();
      }
    });
    req.on("end", () => resolve(body));
    req.on("error", reject);
  });
}

function safeLead(lead) {
  const { ipHash, ...safe } = lead;
  return safe;
}

function hasMiniTimAccess(req) {
  return isAdmin(req) && isFounderDevice(req);
}

function serveFile(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
  const filePath = path.normalize(path.join(app.root, pathname));
  const isPublicAsset = PUBLIC_FILES.has(pathname) || PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix));

  if (!filePath.startsWith(app.root) || !isPublicAsset || filePath.includes(`${path.sep}data${path.sep}`)) {
    res.writeHead(403, securityHeaders("text/plain; charset=utf-8"));
    res.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, securityHeaders("text/plain; charset=utf-8"));
      res.end("Not found");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, securityHeaders(MIME_TYPES[ext] || "application/octet-stream"));
    res.end(data);
  });
}

async function handleApi(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === "GET" && url.pathname === "/api/health") {
    sendJson(res, 200, {
      ok: true,
      service: app.name,
      version: app.version,
      mode: app.env,
      testMode: app.isTest,
      time: new Date().toISOString()
    });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/engine/status") {
    sendJson(res, 200, engineStatus());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/growth/status") {
    sendJson(res, 200, automationStatus());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/knowledge/status") {
    sendJson(res, 200, knowledgeSummary());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/ops/status") {
    sendJson(res, 200, operatingStatus());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/cv-engine/status") {
    sendJson(res, 200, cvEngineStatus());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/knowledge/materials") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, knowledgeMaterials());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/ceo/status") {
    if (!hasMiniTimAccess(req)) {
      sendJson(res, 401, { ok: false, errors: ["MiniTim founder device access required."] });
      return;
    }
    sendJson(res, 200, ceoStatus());
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/ceo/chat") {
    if (!hasMiniTimAccess(req)) {
      sendJson(res, 401, { ok: false, errors: ["MiniTim founder device access required."] });
      return;
    }
    try {
      const input = JSON.parse(await readBody(req) || "{}");
      sendJson(res, 200, await founderChat(input));
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to process founder request."] });
    }
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/ceo/ping-phone") {
    if (!hasMiniTimAccess(req)) {
      sendJson(res, 401, { ok: false, errors: ["MiniTim founder device access required."] });
      return;
    }
    try {
      const input = JSON.parse(await readBody(req) || "{}");
      const message = input.message || "MiniTim test: Credit Vivo founder SMS is connected.";
      sendJson(res, 200, await sendFounderSms(message));
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to send founder SMS."] });
    }
    return;
  }

  if (req.method === "POST" && url.pathname.startsWith("/api/ceo/actions/")) {
    if (!hasMiniTimAccess(req)) {
      sendJson(res, 401, { ok: false, errors: ["MiniTim founder device access required."] });
      return;
    }
    try {
      const actionId = url.pathname.split("/").pop();
      const input = JSON.parse(await readBody(req) || "{}");
      sendJson(res, 200, updateAction(actionId, input.decision));
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to update action."] });
    }
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/debug/latest") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, readLatestDebugReport());
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/debug/run") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, runDebugScan({ mode: "admin-api", writeReport: true }));
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/intelligence/plan") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, strategicPlan({
      mode: url.searchParams.get("mode") || "serious30Day",
      days: Number(url.searchParams.get("days") || 14)
    }));
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/engine/diagnostics") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, selfDiagnostics({ app, storage: storageDiagnostics() }));
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/engine/simulate") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    try {
      const input = JSON.parse(await readBody(req) || "{}");
      sendJson(res, 200, { ok: true, recommendation: recommendationFor(input) });
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to simulate this request."] });
    }
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/growth/plan") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, buildGrowthPlan(readLeads(), {
      goal: url.searchParams.get("goal"),
      monthlyBudget: url.searchParams.get("monthlyBudget")
    }));
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/growth/retention") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    sendJson(res, 200, retentionPlan(readLeads()));
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/leads") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }

    const leads = readLeads().slice().reverse().map(safeLead);
    sendJson(res, 200, { ok: true, count: leads.length, leads });
    return;
  }

  if (req.method === "POST" && url.pathname.startsWith("/api/leads/") && url.pathname.endsWith("/promote")) {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    const id = url.pathname.split("/")[3];
    const leads = readLeads();
    const leadIndex = leads.findIndex((record) => record.id === id);
    if (leadIndex === -1) {
      sendJson(res, 404, { ok: false, errors: ["Lead not found."] });
      return;
    }
    const lead = leads[leadIndex];
    if (lead.workflowId) {
      const existingWorkflow = readWorkflows().find((record) => record.id === lead.workflowId);
      sendJson(res, 200, {
        ok: true,
        alreadyPromoted: true,
        workflow: existingWorkflow || null,
        lead: safeLead(lead)
      });
      return;
    }
    const workflow = workflowFromLead(lead);
    const workflows = readWorkflows();
    workflows.push(workflow);
    writeWorkflows(workflows);
    leads[leadIndex] = {
      ...lead,
      status: "promoted-to-workflow",
      workflowId: workflow.id,
      promotedAt: new Date().toISOString()
    };
    writeLeads(leads);
    sendJson(res, 201, {
      ok: true,
      workflow,
      lead: safeLead(leads[leadIndex])
    });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/workflows") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    const workflows = seedWorkflows(readWorkflows, writeWorkflows);
    sendJson(res, 200, {
      ok: true,
      count: workflows.length,
      summary: workflowSummary(workflows),
      workflows
    });
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/workflows") {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    try {
      const input = JSON.parse(await readBody(req) || "{}");
      const workflow = normalizeWorkflow(input);
      if (!workflow.name || !workflow.goal || !workflow.next) {
        sendJson(res, 400, { ok: false, errors: ["Name, goal, and next action are required."] });
        return;
      }
      const workflows = readWorkflows();
      workflows.push(workflow);
      writeWorkflows(workflows);
      sendJson(res, 201, { ok: true, workflow });
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to create workflow record."] });
    }
    return;
  }

  if (req.method === "GET" && url.pathname.startsWith("/api/workflows/") && url.pathname.endsWith("/safe-update")) {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    const id = url.pathname.split("/")[3];
    const workflows = seedWorkflows(readWorkflows, writeWorkflows);
    const workflow = workflows.find((record) => record.id === id);
    if (!workflow) {
      sendJson(res, 404, { ok: false, errors: ["Workflow record not found."] });
      return;
    }
    sendJson(res, 200, { ok: true, message: buildSafeUpdate(workflow), workflow });
    return;
  }

  if (req.method === "GET" && url.pathname.startsWith("/api/client/workflows/")) {
    const id = url.pathname.split("/")[4];
    const workflow = readWorkflows().find((record) => record.id === id);
    if (!workflow) {
      sendJson(res, 404, { ok: false, errors: ["Workflow status not found."] });
      return;
    }
    sendJson(res, 200, { ok: true, workflow: safeClientWorkflow(workflow) });
    return;
  }

  if (req.method === "POST" && url.pathname.startsWith("/api/workflows/") && url.pathname.endsWith("/complete")) {
    if (!isAdmin(req)) {
      sendJson(res, 401, { ok: false, errors: ["Admin access required."] });
      return;
    }
    const id = url.pathname.split("/")[3];
    const { records, record } = markNextActionDone(seedWorkflows(readWorkflows, writeWorkflows), id);
    if (!record) {
      sendJson(res, 404, { ok: false, errors: ["Workflow record not found."] });
      return;
    }
    writeWorkflows(records);
    sendJson(res, 200, { ok: true, workflow: record, summary: workflowSummary(records) });
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/leads") {
    try {
      if (isRateLimited(req)) {
        sendJson(res, 429, { ok: false, errors: ["Too many requests. Please try again later."] });
        return;
      }

      if (!String(req.headers["content-type"] || "").includes("application/json")) {
        sendJson(res, 415, { ok: false, errors: ["Use application/json."] });
        return;
      }

      const input = JSON.parse(await readBody(req) || "{}");
      const { lead, errors } = buildLead(input, req, hashIp);
      if (errors.length) {
        sendJson(res, 400, { ok: false, errors });
        return;
      }

      const leads = readLeads();
      leads.push(lead);
      writeLeads(leads);
      sendJson(res, 201, {
        ok: true,
        lead: {
          id: lead.id,
          createdAt: lead.createdAt,
          status: lead.status,
          name: lead.name,
          goal: lead.goal,
          scoreRange: lead.scoreRange,
          planInterest: lead.planInterest,
          recommendation: lead.recommendation
        }
      });
    } catch {
      sendJson(res, 400, { ok: false, errors: ["Unable to save this review request."] });
    }
    return;
  }

  sendJson(res, 404, { ok: false, errors: ["API route not found."] });
}

function createServer() {
  ensureStore();
  return http.createServer((req, res) => {
    if (req.url.startsWith("/api/")) {
      handleApi(req, res);
      return;
    }
    serveFile(req, res);
  });
}

module.exports = { createServer };
