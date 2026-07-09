const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const DATA_FILES = [
  path.join(ROOT, "data", "ceo-memory.test.json"),
  path.join(ROOT, "data", "ceo-actions.test.json"),
  path.join(ROOT, "data", "ceo-audit.test.json")
];
const PORT = 8916;
const BASE = `http://127.0.0.1:${PORT}`;
const ADMIN_TOKEN = "ceo-ai-test-token";
const FOUNDER_DEVICE_KEY = "ceo-ai-test-device";
const FOUNDER_PHONE_LAST4 = "1234";
const FOUNDER_PHONE_SHA256 = "test-founder-phone-hash";

const originals = DATA_FILES.map((file) => ({
  file,
  exists: fs.existsSync(file),
  data: fs.existsSync(file) ? fs.readFileSync(file, "utf8") : null
}));

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function json(pathname, options = {}) {
  const response = await fetch(`${BASE}${pathname}`, options);
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

async function run() {
  const server = spawn(process.execPath, ["server.js"], {
    cwd: ROOT,
      env: {
        ...process.env,
        PORT: String(PORT),
        ADMIN_TOKEN,
        FOUNDER_DEVICE_KEY,
        FOUNDER_PHONE_LAST4,
        FOUNDER_PHONE_SHA256,
        NODE_ENV: "test"
      },
    stdio: "ignore",
    windowsHide: true
  });

  try {
    await waitForServer();
    const checks = [];
    const auth = {
      "X-Admin-Token": ADMIN_TOKEN,
      "X-Founder-Device-Key": FOUNDER_DEVICE_KEY,
      "X-Founder-Phone-Last4": FOUNDER_PHONE_LAST4,
      "X-Founder-Phone-Sha256": FOUNDER_PHONE_SHA256
    };
    const tokenOnly = { "X-Admin-Token": ADMIN_TOKEN };

    const record = async (name, fn) => {
      await fn();
      checks.push(name);
    };

    await record("CEO status requires founder token", async () => {
      const { response, body } = await json("/api/ceo/status");
      assert(response.status === 401, "status must be locked");
      assert(body.ok === false, "locked body");
    });

    await record("CEO status requires founder device allowlist", async () => {
      const { response, body } = await json("/api/ceo/status", { headers: tokenOnly });
      assert(response.status === 401, "status must require device");
      assert(body.errors[0].includes("MiniTim founder device"), "device lock message");
    });

    await record("CEO page is served", async () => {
      const response = await fetch(`${BASE}/ceo.html`);
      const text = await response.text();
      assert(response.status === 200, "ceo page status");
      assert(text.includes("MiniTim"), "MiniTim page title");
      assert(text.includes("Execution waits for you"), "approval copy");
      assert(text.includes("Founder device key"), "device gate");
      assert(text.includes("Founder phone"), "phone gate");
    });

    await record("CEO status exposes approval-gated autonomy", async () => {
      const { response, body } = await json("/api/ceo/status", { headers: auth });
      assert(response.status === 200, "status ok");
      assert(body.autonomyPolicy === "approval-gated", "approval gated");
      assert(body.assistantName === "MiniTim", "assistant name");
      assert(body.founderOnlyMode === "founder-token-plus-device-key", "founder device only");
      assert(body.aiProvider === "rules-fallback", "rules fallback without key");
      assert(body.sms.configured === false, "sms disabled without env");
      assert(body.deepLearningStatus.includes("configure-openai-api-key"), "openai key guidance");
      assert(body.blockedExternalActions.includes("publish_ad"), "ads blocked");
      assert(body.guards.some((item) => item.includes("No autonomous external actions")), "guardrail");
    });

    await record("Phone ping requires Twilio configuration", async () => {
      const { response, body } = await json("/api/ceo/ping-phone", {
        method: "POST",
        headers: { ...auth, "Content-Type": "application/json" },
        body: JSON.stringify({ message: "MiniTim test" })
      });
      assert(response.status === 200, "ping route responds");
      assert(body.ok === false, "ping blocked without config");
      assert(body.errors[0].includes("Twilio SMS is not configured"), "twilio config message");
    });

    await record("Low-risk founder chat does not create approval item", async () => {
      const { response, body } = await json("/api/ceo/chat", {
        method: "POST",
        headers: { ...auth, "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Summarize what the company should improve this week." })
      });
      assert(response.status === 200, "chat ok");
      assert(body.ok === true, "chat body ok");
      assert(body.aiProvider === "rules-fallback", "chat fallback provider");
      assert(body.risk === "low", "low risk");
      assert(body.approvalAction === null, "no approval action");
    });

    await record("Sensitive founder chat creates approval item and blocks external actions", async () => {
      const { response, body } = await json("/api/ceo/chat", {
        method: "POST",
        headers: { ...auth, "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Go ahead and send emails to partners and publish ads." })
      });
      assert(response.status === 200, "sensitive chat ok");
      assert(body.risk === "high", "high risk");
      assert(body.approvalAction.status === "pending_founder_approval", "pending action");
      assert(body.blockedActions.includes("send_email"), "email blocked");
      assert(body.blockedActions.includes("publish_ad"), "ads blocked");
    });

    await record("Pending action appears in status and can be rejected", async () => {
      const before = await json("/api/ceo/status", { headers: auth });
      const action = before.body.pendingActions[0];
      assert(action, "pending action exists");

      const decision = await json(`/api/ceo/actions/${action.id}`, {
        method: "POST",
        headers: { ...auth, "Content-Type": "application/json" },
        body: JSON.stringify({ decision: "reject" })
      });
      assert(decision.response.status === 200, "decision status");
      assert(decision.body.action.status === "rejected_by_founder", "rejected");

      const after = await json("/api/ceo/status", { headers: auth });
      assert(after.body.pendingActions.length === 0, "no pending after rejection");
      assert(after.body.auditCount >= 3, "audit entries");
      assert(after.body.latestAuditHash, "audit hash exists");
    });

    console.log(JSON.stringify({ ok: true, checks: checks.length, passed: checks }, null, 2));
  } finally {
    server.kill();
    await sleep(250);
    originals.forEach(({ file, exists, data }) => {
      if (exists) fs.writeFileSync(file, data);
      else if (fs.existsSync(file)) fs.rmSync(file);
    });
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
