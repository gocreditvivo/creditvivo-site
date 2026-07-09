const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const DATA_FILE = path.join(ROOT, "data", "leads.test.json");
const PORT = 8922;
const BASE = `http://127.0.0.1:${PORT}`;
const ADMIN_TOKEN = "smoke-test-admin-token";

const originalExists = fs.existsSync(DATA_FILE);
const originalData = originalExists ? fs.readFileSync(DATA_FILE, "utf8") : null;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function request(pathname, options = {}) {
  return fetch(`${BASE}${pathname}`, options);
}

async function json(pathname, options = {}) {
  const response = await request(pathname, options);
  const body = await response.json();
  return { response, body };
}

async function waitForServer() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const { response, body } = await json("/api/health");
      if (response.status === 200 && body.ok) return;
    } catch {
      await sleep(150);
    }
  }
  throw new Error("Server did not start.");
}

function lead(overrides = {}) {
  return {
    name: "Smoke Test",
    email: "smoke@example.com",
    phone: "555-0111",
    goal: "Auto approval",
    scoreRange: "580-639",
    planInterest: "Plus - $59/mo",
    preferredContact: "Email",
    notes: "Automated verification only.",
    source: "smoke-test",
    ...overrides
  };
}

async function run() {
  const server = spawn(process.execPath, ["server.js"], {
    cwd: ROOT,
    env: {
      ...process.env,
      PORT: String(PORT),
      ADMIN_TOKEN,
      NODE_ENV: "test"
    },
    stdio: "ignore",
    windowsHide: true
  });

  try {
    await waitForServer();

    const checks = [];
    const record = async (name, fn) => {
      await fn();
      checks.push(name);
    };

    await record("health route returns ok", async () => {
      const { response, body } = await json("/api/health");
      assert(response.status === 200, "health status");
      assert(body.ok === true, "health ok");
      assert(body.version === "0.2.0", "platform version");
      assert(body.testMode === true, "test mode");
    });

    await record("engine status returns model version", async () => {
      const { response, body } = await json("/api/engine/status");
      assert(response.status === 200, "engine status");
      assert(body.modelVersion === "cv-readiness-rules-v0.2.0", "model version");
      assert(body.allowSelfModify === false, "self modify disabled");
    });

    await record("growth status exposes approval-gated automation", async () => {
      const { response, body } = await json("/api/growth/status");
      assert(response.status === 200, "growth status");
      assert(body.growthVersion === "cv-growth-retention-v0.1.0", "growth version");
      assert(body.capabilities.includes("channel recommendations"), "channel recommendations");
      assert(body.blockedAutomation.includes("unbounded ad spend"), "blocks unbounded spend");
    });

    await record("knowledge status exposes installed materials summary", async () => {
      const { response, body } = await json("/api/knowledge/status");
      assert(response.status === 200, "knowledge status");
      assert(body.knowledgeVersion === "cv-knowledge-engine-v0.1.0", "knowledge version");
      assert(body.sourceCount >= 8, "knowledge sources");
      assert(body.topPriorities.includes("Production auth + roles"), "knowledge priorities");
    });

    await record("operating status exposes repair build protect retain plan", async () => {
      const { response, body } = await json("/api/ops/status");
      assert(response.status === 200, "ops status");
      assert(body.operatingVersion === "cv-operating-system-v0.1.0", "ops version");
      assert(body.position === "Repair + Build + Protect + Retain", "ops position");
      assert(body.launchReadiness.paidPublicLaunch === "Not ready", "paid launch gate");
      assert(body.benchmarkFindings.some((item) => item.competitor === "Dovly"), "dovly benchmark");
      assert(body.productLayers.some((item) => item.id === "build" && item.status === "partner-needed"), "build partner gate");
      assert(body.launchGates.some((item) => item.id === "twilio-a2p" && item.status === "waiting"), "twilio gate");
    });

    await record("CV engine status exposes Dovly benchmark layers", async () => {
      const { response, body } = await json("/api/cv-engine/status");
      assert(response.status === 200, "cv engine status");
      assert(body.ok === true, "cv engine ok");
      assert(body.layers.some((layer) => layer.id === "dispute-readiness"), "dispute readiness layer");
      assert(body.guardrails.some((item) => item.includes("No score guarantees")), "score guarantee guardrail");
    });

    await record("strategic intelligence requires admin token", async () => {
      const { response } = await json("/api/intelligence/plan");
      assert(response.status === 401, "intelligence locked");
    });

    await record("knowledge materials require admin token", async () => {
      const { response } = await json("/api/knowledge/materials");
      assert(response.status === 401, "knowledge materials locked");
    });

    await record("debug scanner requires admin token", async () => {
      const latest = await json("/api/debug/latest");
      const runScan = await json("/api/debug/run", { method: "POST" });
      assert(latest.response.status === 401, "debug latest locked");
      assert(runScan.response.status === 401, "debug run locked");
    });

    await record("home page serves", async () => {
      const response = await request("/");
      const text = await response.text();
      assert(response.status === 200, "home status");
      assert(text.includes("AI Precision. Attorney Authority."), "hero copy");
      assert(text.includes("Repair. Build. Protect. Stay ready."), "operating roadmap copy");
      assert(text.includes("Paid launch and partner-backed features require completed onboarding"), "paid launch gate copy");
    });

    await record("admin page serves locked UI", async () => {
      const response = await request("/admin.html");
      const text = await response.text();
      assert(response.status === 200, "admin status");
      assert(text.includes("Admin token"), "admin token prompt");
      assert(text.includes("CV operating system"), "ops panel");
    });

    await record("security headers are present", async () => {
      const response = await request("/admin.html");
      assert(response.headers.get("content-security-policy"), "missing CSP");
      assert(response.headers.get("x-frame-options") === "DENY", "missing frame block");
      assert(response.headers.get("x-content-type-options") === "nosniff", "missing nosniff");
    });

    await record("admin API blocks unauthenticated reads", async () => {
      const { response, body } = await json("/api/leads");
      assert(response.status === 401, "unauth leads status");
      assert(body.ok === false, "unauth leads body");
    });

    await record("lead API rejects wrong content type", async () => {
      const { response } = await json("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: "bad"
      });
      assert(response.status === 415, "wrong content type");
    });

    await record("lead API rejects invalid email", async () => {
      const { response } = await json("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead({ email: "bad-email" }))
      });
      assert(response.status === 400, "invalid email status");
    });

    await record("lead API rejects invalid enum", async () => {
      const { response } = await json("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead({ scoreRange: "999" }))
      });
      assert(response.status === 400, "invalid enum status");
    });

    await record("lead API rejects honeypot spam", async () => {
      const { response } = await json("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead({ companyWebsite: "spam.example" }))
      });
      assert(response.status === 400, "honeypot status");
    });

    await record("lead API accepts valid lead", async () => {
      const { response, body } = await json("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead())
      });
      assert(response.status === 201, "create lead status");
      assert(body.ok === true, "create lead ok");
      assert(body.lead.status === "new", "lead status");
    });

    await record("admin API returns leads with valid token", async () => {
      const { response, body } = await json("/api/leads", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "authed leads status");
      assert(body.ok === true, "authed leads ok");
      assert(body.count >= 1, "authed leads count");
      const smokeLead = body.leads.find((item) => item.email === "smoke@example.com");
      assert(smokeLead, "smoke lead present");
      assert(!("ipHash" in smokeLead), "ipHash leaked");
      assert(smokeLead.recommendation.modelVersion === "cv-readiness-rules-v0.2.0", "lead recommendation");
    });

    await record("growth plan requires admin token", async () => {
      const { response } = await json("/api/growth/plan");
      assert(response.status === 401, "growth plan locked");
    });

    await record("growth plan recommends bounded channels", async () => {
      const { response, body } = await json("/api/growth/plan?monthlyBudget=3000", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "growth plan status");
      assert(body.mode === "approval-gated-automation", "growth approval mode");
      assert(body.channelPlan.length > 0, "channel plan");
      assert(body.note.includes("does not publish ads"), "no external publishing");
    });

    await record("retention plan requires admin token", async () => {
      const { response } = await json("/api/growth/retention");
      assert(response.status === 401, "retention locked");
    });

    await record("retention plan returns segments", async () => {
      const { response, body } = await json("/api/growth/retention", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "retention status");
      assert(body.segments.length >= 4, "retention segments");
      assert(body.retentionKpis.includes("churn risk"), "retention kpis");
    });

    await record("strategic intelligence returns launch budget and horizons", async () => {
      const { response, body } = await json("/api/intelligence/plan?mode=serious30Day&days=14", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "intelligence status");
      assert(body.moneyPlan.total === 63500, "serious budget");
      assert(body.launchPlan.length === 14, "14-day plan");
      assert(body.horizons.length === 4, "horizon plan");
      assert(body.competitors.length >= 5, "competitor tracking");
    });

    await record("knowledge materials return compliance and technology data", async () => {
      const { response, body } = await json("/api/knowledge/materials", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "knowledge materials status");
      assert(body.complianceMaterials.some((item) => item.area === "Credit repair claims"), "claims gate");
      assert(body.technologyStack.some((item) => item.layer === "AI governance"), "AI governance");
      assert(body.innovationRoadmap.some((item) => item.name === "Compliance autopilot"), "compliance autopilot");
    });

    await record("debug scanner runs and reports production gaps", async () => {
      const { response, body } = await json("/api/debug/run", {
        method: "POST",
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "debug run status");
      assert(body.debugVersion === "cv-debug-scanner-v0.1.0", "debug version");
      assert(body.summary.checks >= 10, "debug checks");
      assert(body.status === "healthy-for-mvp-blocked-for-production", "debug status");
      assert(body.recommendedNextActions.some((item) => item.id === "mfa-auth"), "debug action");
    });

    await record("engine diagnostics requires admin token", async () => {
      const { response } = await json("/api/engine/diagnostics");
      assert(response.status === 401, "diagnostics locked");
    });

    await record("engine diagnostics returns advisory self-audit", async () => {
      const { response, body } = await json("/api/engine/diagnostics", {
        headers: { "X-Admin-Token": ADMIN_TOKEN }
      });
      assert(response.status === 200, "diagnostics status");
      assert(body.ok === true, "diagnostics ok");
      assert(Array.isArray(body.recommendedUpgrades), "recommended upgrades");
      assert(body.findings.some((item) => item.includes("Self-update is advisory")), "safe self-update advisory");
    });

    await record("engine simulation returns readiness recommendation", async () => {
      const { response, body } = await json("/api/engine/simulate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": ADMIN_TOKEN
        },
        body: JSON.stringify(lead({ goal: "Identity theft help", scoreRange: "Under 580" }))
      });
      assert(response.status === 200, "simulate status");
      assert(body.recommendation.readinessTier === "rebuild", "simulate tier");
      assert(body.recommendation.escalations.includes("identity-protection-review"), "simulate escalation");
    });

    await record("data directory is not web-accessible", async () => {
      const response = await request("/data/leads.json");
      assert(response.status === 403, "data route blocked");
    });

    await record("oversized payload is rejected", async () => {
      try {
        const response = await request("/api/leads", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payload: "x".repeat(25_000) })
        });
        assert([400, 413].includes(response.status), "oversized payload status");
      } catch (error) {
        assert(String(error.cause?.code || error.message).includes("SOCKET"), "oversized payload closed connection");
      }
    });

    console.log(JSON.stringify({ ok: true, checks: checks.length, passed: checks }, null, 2));
  } finally {
    server.kill();
    await sleep(250);
    if (originalExists) {
      fs.writeFileSync(DATA_FILE, originalData);
    } else if (fs.existsSync(DATA_FILE)) {
      fs.rmSync(DATA_FILE);
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
