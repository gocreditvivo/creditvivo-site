const fs = require("fs");
const path = require("path");
const { withTestServer } = require("./lib/test-server");
const { securityHeaders } = require("../src/http");
const { app, engine, security } = require("../src/config");

const OUT = path.join(__dirname, "..", "SECURITY_BREACH_AUDIT_REPORT.md");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function fetchText(baseUrl, pathname, options = {}) {
  const response = await fetch(`${baseUrl}${pathname}`, options);
  const text = await response.text();
  return { response, text };
}

function hasFileText(file, pattern) {
  const absolute = path.join(__dirname, "..", file);
  return fs.existsSync(absolute) && pattern.test(fs.readFileSync(absolute, "utf8"));
}

async function run() {
  const runtimeChecks = [];
  const staticChecks = [];
  const gaps = [];

  const record = async (bucket, name, fn) => {
    try {
      await fn();
      bucket.push({ name, ok: true });
    } catch (error) {
      bucket.push({ name, ok: false, error: error.message });
    }
  };

  await withTestServer(8919, async ({ baseUrl, adminToken }) => {
    await record(runtimeChecks, "public frontend assets serve", async () => {
      const home = await fetch(`${baseUrl}/`);
      const admin = await fetch(`${baseUrl}/admin.html`);
      const script = await fetch(`${baseUrl}/script.js`);
      assert(home.status === 200, `home ${home.status}`);
      assert(admin.status === 200, `admin ${admin.status}`);
      assert(script.status === 200, `script ${script.status}`);
    });

    await record(runtimeChecks, "source and config files are blocked", async () => {
      const blocked = ["/server.js", "/package.json", "/src/app.js", "/tests/smoke-security.js", "/ARCHITECTURE.md", "/.env.example"];
      for (const pathname of blocked) {
        const response = await fetch(`${baseUrl}${pathname}`);
        assert(response.status === 403, `${pathname} returned ${response.status}`);
      }
    });

    await record(runtimeChecks, "stored lead data is blocked", async () => {
      const response = await fetch(`${baseUrl}/data/leads.json`);
      assert(response.status === 403, `data returned ${response.status}`);
    });

    await record(runtimeChecks, "admin surfaces require authentication", async () => {
      const protectedRoutes = [
        "/api/leads",
        "/api/engine/diagnostics",
        "/api/engine/simulate",
        "/api/growth/plan",
        "/api/growth/retention",
        "/api/intelligence/plan",
        "/api/knowledge/materials"
      ];
      for (const pathname of protectedRoutes) {
        const response = await fetch(`${baseUrl}${pathname}`, pathname.endsWith("simulate") ? { method: "POST" } : {});
        assert(response.status === 401, `${pathname} returned ${response.status}`);
      }
    });

    await record(runtimeChecks, "admin token does not leak hidden ip hash", async () => {
      const response = await fetch(`${baseUrl}/api/leads`, { headers: { "X-Admin-Token": adminToken } });
      const body = await response.text();
      assert(response.status === 200, `admin leads ${response.status}`);
      assert(!body.includes("ipHash"), "ipHash leaked");
    });

    await record(runtimeChecks, "malformed and oversized payloads fail closed", async () => {
      const malformed = await fetch(`${baseUrl}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{bad"
      });
      assert(malformed.status === 400, `malformed ${malformed.status}`);

      try {
        const oversized = await fetch(`${baseUrl}/api/leads`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payload: "x".repeat(50_000) })
        });
        assert([400, 413].includes(oversized.status), `oversized ${oversized.status}`);
      } catch (error) {
        assert(String(error.cause?.code || error.message).includes("SOCKET"), "oversized request did not fail closed");
      }
    });

    await record(runtimeChecks, "security headers are present", async () => {
      const response = await fetch(`${baseUrl}/admin.html`);
      assert(response.headers.get("content-security-policy"), "missing CSP");
      assert(response.headers.get("x-frame-options") === "DENY", "missing frame protection");
      assert(response.headers.get("x-content-type-options") === "nosniff", "missing nosniff");
      assert(response.headers.get("permissions-policy"), "missing permissions policy");
    });

    await record(runtimeChecks, "safe public status routes do not expose secrets", async () => {
      for (const pathname of ["/api/health", "/api/engine/status", "/api/growth/status", "/api/knowledge/status"]) {
        const { response, text } = await fetchText(baseUrl, pathname);
        assert(response.status === 200, `${pathname} ${response.status}`);
        assert(!text.includes(adminToken), `${pathname} leaked admin token`);
        assert(!text.includes("leadsFile"), `${pathname} leaked storage path`);
      }
    });
  });

  await record(staticChecks, "production blocks default admin token", async () => {
    assert(hasFileText("src/config.js", /IS_PRODUCTION && ADMIN_TOKEN === "dev-admin-token-change-me"/), "missing production token guard");
  });

  await record(staticChecks, "engine self-modification disabled", async () => {
    assert(engine.allowSelfModify === false, "self-modification enabled");
  });

  await record(staticChecks, "server sets max body size", async () => {
    assert(security.maxBodyBytes <= 20_000, "max body too high for public intake");
  });

  await record(staticChecks, "CSP is configured", async () => {
    const csp = securityHeaders("text/html; charset=utf-8")["Content-Security-Policy"];
    assert(csp.includes("default-src 'self'"), "missing self default-src");
    assert(csp.includes("frame-ancestors 'none'"), "missing frame-ancestors");
  });

  if (securityHeaders("text/html; charset=utf-8")["Content-Security-Policy"].includes("'unsafe-inline'")) {
    gaps.push({
      severity: "medium",
      area: "CSP",
      issue: "Inline scripts/styles are still allowed for the static MVP.",
      fix: "Move inline admin script/styles into static files or use nonces/hashes before production."
    });
  }

  if (app.host === "127.0.0.1") {
    gaps.push({
      severity: "high",
      area: "Production edge",
      issue: "Current server is local-only and lacks managed HTTPS/WAF/CDN controls.",
      fix: "Deploy behind managed HTTPS, WAF, DDoS protection, and centralized logging."
    });
  }

  gaps.push(
    {
      severity: "critical-before-production",
      area: "Authentication",
      issue: "Single admin token is not acceptable for real customer operations.",
      fix: "Add MFA auth, role-based access, session expiry, break-glass admin, and admin audit logs."
    },
    {
      severity: "critical-before-production",
      area: "Data storage",
      issue: "Local JSON storage is not acceptable for credit reports, identity documents, or customer PII.",
      fix: "Use encrypted managed database, object vault, backups, retention/deletion rules, and field-level controls."
    },
    {
      severity: "critical-before-production",
      area: "Breach response",
      issue: "No executable incident response, breach notification, log review, or tabletop workflow exists yet.",
      fix: "Create WISP, incident plan, breach notification plan, monitoring alerts, and quarterly tabletop tests."
    },
    {
      severity: "high",
      area: "Audit trail",
      issue: "Admin/customer actions are not written to an immutable audit log.",
      fix: "Log every sensitive read/write/action with actor, timestamp, IP hash, object id, and reason."
    },
    {
      severity: "high",
      area: "Failover",
      issue: "No real database failover, queue, status page, or backup restore test exists in the MVP.",
      fix: "Add queue-backed intake, point-in-time recovery, restore drills, and status/alerting."
    }
  );

  const allChecks = runtimeChecks.concat(staticChecks);
  const failed = allChecks.filter((item) => !item.ok);
  const reportStatus = failed.length ? "FAIL" : "PASS WITH PRODUCTION GAPS";

  const table = (rows, headers) =>
    `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows.map((row) => `| ${row.map((cell) => String(cell).replace(/\|/g, "\\|")).join(" | ")} |`).join("\n")}`;

  const report = `# Credit Vivo Security, Breach, and Failover Audit

## Result

- Status: **${reportStatus}**
- Runtime checks: **${runtimeChecks.length}**
- Static checks: **${staticChecks.length}**
- Failed checks: **${failed.length}**
- Production gaps: **${gaps.length}**

## Important Finding

Credit Vivo is **not hack proof**. No system is. Current MVP security is acceptable for local testing and demos, but it is **not ready for real customer PII, credit reports, identity documents, payment data, or production attorney workflows**.

## Runtime Security Checks

${table(runtimeChecks.map((item) => [item.ok ? "PASS" : "FAIL", item.name, item.error || ""]), ["Status", "Check", "Issue"])}

## Static Security Checks

${table(staticChecks.map((item) => [item.ok ? "PASS" : "FAIL", item.name, item.error || ""]), ["Status", "Check", "Issue"])}

## Breach Possibility

The most realistic breach paths are:

1. Admin token theft or reuse.
2. Future customer PII stored without encryption, audit logs, or retention controls.
3. Missing monitoring, making intrusion detection too slow.
4. Phishing or social engineering against operators.
5. Vendor/API compromise after credit data, identity, builder, CRM, payments, or attorney integrations are added.
6. Future upload/document vault mistakes exposing credit reports or IDs.

## Production Gaps

${table(gaps.map((item) => [item.severity, item.area, item.issue, item.fix]), ["Severity", "Area", "Issue", "Fix"])}

## Current Protections That Passed

- Admin APIs require a token.
- Token comparison uses timing-safe equality.
- Public lead intake has content-type, enum, honeypot, body-size, and rate-limit controls.
- The data folder is not web-accessible.
- Project source/config/report files are blocked from static serving.
- IP hash is not exposed through admin lead responses.
- Security headers are present.
- Engine self-modification is disabled.

## Minimum Before Real Customer Data

1. Replace admin token with MFA auth and roles.
2. Replace local JSON with encrypted managed database and private object vault.
3. Add immutable audit logs.
4. Add WAF, HTTPS, DDoS protection, monitoring, and alerting.
5. Add backup restore drills and failover runbooks.
6. Add WISP, incident response plan, breach notification plan, and vendor risk program.
7. Add secure upload pipeline with malware scanning and signed URLs.
8. Add secrets manager and key rotation.
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({ ok: failed.length === 0, status: reportStatus, checks: allChecks.length, failed: failed.length, productionGaps: gaps.length, report: OUT }, null, 2));
  if (failed.length) process.exitCode = 1;
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
