const fs = require("fs");
const path = require("path");
const { withTestServer } = require("./lib/test-server");

const OUT = path.join(__dirname, "..", "SECURITY_BASELINE_AUDIT.md");

async function run() {
  await withTestServer(8915, async ({ baseUrl, adminToken }) => {
    const checks = [];
    const failures = [];
    const record = async (name, fn) => {
      try {
        await fn();
        checks.push({ name, ok: true });
      } catch (error) {
        checks.push({ name, ok: false, error: error.message });
        failures.push(`${name}: ${error.message}`);
      }
    };
    const must = (condition, message) => {
      if (!condition) throw new Error(message);
    };

    await record("security headers on admin", async () => {
      const response = await fetch(`${baseUrl}/admin.html`);
      must(response.headers.get("content-security-policy"), "missing CSP");
      must(response.headers.get("x-frame-options") === "DENY", "missing X-Frame-Options DENY");
      must(response.headers.get("x-content-type-options") === "nosniff", "missing nosniff");
    });

    await record("leads API locked", async () => {
      const response = await fetch(`${baseUrl}/api/leads`);
      must(response.status === 401, `expected 401, got ${response.status}`);
    });

    await record("diagnostics API locked", async () => {
      const response = await fetch(`${baseUrl}/api/engine/diagnostics`);
      must(response.status === 401, `expected 401, got ${response.status}`);
    });

    await record("strategic API locked", async () => {
      const response = await fetch(`${baseUrl}/api/intelligence/plan`);
      must(response.status === 401, `expected 401, got ${response.status}`);
    });

    await record("data directory blocked", async () => {
      const response = await fetch(`${baseUrl}/data/leads.json`);
      must(response.status === 403, `expected 403, got ${response.status}`);
    });

    await record("path traversal blocked", async () => {
      const response = await fetch(`${baseUrl}/..%2Fserver.js`);
      must([403, 404].includes(response.status), `expected 403/404, got ${response.status}`);
    });

    await record("admin token works without leaking ip hash", async () => {
      const response = await fetch(`${baseUrl}/api/leads`, { headers: { "X-Admin-Token": adminToken } });
      const body = await response.json();
      must(response.status === 200, `expected 200, got ${response.status}`);
      must(JSON.stringify(body).includes("ipHash") === false, "ipHash leaked");
    });

    await record("honeypot spam rejected", async () => {
      const response = await fetch(`${baseUrl}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Bot",
          email: "bot@example.com",
          goal: "Auto approval",
          scoreRange: "580-639",
          planInterest: "Free Review",
          preferredContact: "Email",
          companyWebsite: "spam.example"
        })
      });
      must(response.status === 400, `expected 400, got ${response.status}`);
    });

    const report = `# Credit Vivo Security Baseline Audit

## Result

- Status: **${failures.length ? "FAIL" : "PASS"}**
- Checks: **${checks.length}**
- Failures: **${failures.length}**

## Passed/Failed Checks

${checks.map((item) => `- ${item.ok ? "PASS" : "FAIL"}: ${item.name}${item.error ? ` - ${item.error}` : ""}`).join("\n")}

## Failures

${failures.length ? failures.map((item) => `- ${item}`).join("\n") : "- None"}
`;

    fs.writeFileSync(OUT, report);
    console.log(JSON.stringify({ ok: failures.length === 0, checks: checks.length, failures: failures.length, report: OUT }, null, 2));
    if (failures.length) process.exitCode = 1;
  });
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
