const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const DATA_FILE = path.join(ROOT, "data", "workflows.test.json");
const LEADS_FILE = path.join(ROOT, "data", "leads.test.json");
const PORT = 8916;
const BASE = `http://127.0.0.1:${PORT}`;
const ADMIN_TOKEN = "workflow-smoke-admin-token";

const originalExists = fs.existsSync(DATA_FILE);
const originalData = originalExists ? fs.readFileSync(DATA_FILE, "utf8") : null;
const originalLeadsExists = fs.existsSync(LEADS_FILE);
const originalLeadsData = originalLeadsExists ? fs.readFileSync(LEADS_FILE, "utf8") : null;

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

function adminHeaders() {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-Admin-Token": ADMIN_TOKEN
  };
}

async function run() {
  if (fs.existsSync(DATA_FILE)) fs.unlinkSync(DATA_FILE);
  if (fs.existsSync(LEADS_FILE)) fs.unlinkSync(LEADS_FILE);

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

    const denied = await json("/api/workflows");
    assert(denied.response.status === 401, "workflow API must require admin token");

    const list = await json("/api/workflows", { headers: adminHeaders() });
    assert(list.response.status === 200 && list.body.ok, "workflow list should load");
    assert(list.body.count === 5, "workflow API should seed five demo records");
    assert(list.body.summary.attorneyReview === 1, "summary should count attorney review records");

    const first = list.body.workflows[0];
    const update = await json(`/api/workflows/${first.id}/safe-update`, { headers: adminHeaders() });
    assert(update.response.status === 200 && update.body.ok, "safe update should generate");
    assert(update.body.message.includes("Results are not guaranteed"), "safe update must avoid guarantee language");

    const completed = await json(`/api/workflows/${first.id}/complete`, {
      method: "POST",
      headers: adminHeaders(),
      body: "{}"
    });
    assert(completed.response.status === 200 && completed.body.ok, "complete action should persist");
    assert(completed.body.workflow.completedActions.length === 1, "completed action should be logged");

    const leadCreate = await json("/api/leads", {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Promote Lead",
        email: "promote@example.com",
        phone: "555-0144",
        goal: "Auto approval",
        scoreRange: "580-639",
        planInterest: "Free Review",
        preferredContact: "Email",
        notes: "Workflow promotion smoke test.",
        companyWebsite: "",
        source: "workflow-smoke"
      })
    });
    assert(leadCreate.response.status === 201 && leadCreate.body.ok, "lead should be created");

    const promoted = await json(`/api/leads/${leadCreate.body.lead.id}/promote`, {
      method: "POST",
      headers: adminHeaders(),
      body: "{}"
    });
    assert(promoted.response.status === 201 && promoted.body.ok, "lead should promote to workflow");
    assert(promoted.body.workflow.track === "repair-review", "promotion should map score range to repair track");
    assert(promoted.body.lead.workflowId === promoted.body.workflow.id, "lead should store workflow id");

    const promotedAgain = await json(`/api/leads/${leadCreate.body.lead.id}/promote`, {
      method: "POST",
      headers: adminHeaders(),
      body: "{}"
    });
    assert(promotedAgain.response.status === 200 && promotedAgain.body.alreadyPromoted, "promotion should be idempotent");

    const clientStatus = await json(`/api/client/workflows/${promoted.body.workflow.id}`);
    assert(clientStatus.response.status === 200 && clientStatus.body.ok, "client-safe workflow should load");
    assert(clientStatus.body.workflow.id === promoted.body.workflow.id, "client-safe workflow should match id");
    assert(clientStatus.body.workflow.expectations.includes("Results are not guaranteed"), "client status should include safe expectations");
    assert(clientStatus.body.workflow.owner === undefined, "client status must not expose admin owner");
    assert(clientStatus.body.workflow.completedActions === undefined, "client status must not expose admin action history");

    console.log("Workflow API smoke passed.");
  } finally {
    server.kill();
    if (originalExists) {
      fs.writeFileSync(DATA_FILE, originalData);
    } else if (fs.existsSync(DATA_FILE)) {
      fs.unlinkSync(DATA_FILE);
    }
    if (originalLeadsExists) {
      fs.writeFileSync(LEADS_FILE, originalLeadsData);
    } else if (fs.existsSync(LEADS_FILE)) {
      fs.unlinkSync(LEADS_FILE);
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
