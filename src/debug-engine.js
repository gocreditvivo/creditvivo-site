const fs = require("fs");
const path = require("path");
const { app, engine, security, storage } = require("./config");
const { storageDiagnostics } = require("./storage");

const debugVersion = "cv-debug-scanner-v0.1.0";
const REPORT_JSON = path.join(storage.dataDir, "debug-latest.json");
const REPORT_MD = path.join(app.root, "DEBUG_HEALTH_REPORT.md");

function check(id, severity, area, ok, message, fix) {
  return { id, severity, area, ok: Boolean(ok), message, fix };
}

function exists(relativePath) {
  return fs.existsSync(path.join(app.root, relativePath));
}

function parseLeadsFile(leadsFile) {
  try {
    const parsed = JSON.parse(fs.readFileSync(leadsFile, "utf8"));
    return Array.isArray(parsed);
  } catch {
    return false;
  }
}

function runDebugScan({ mode = "manual", writeReport = false } = {}) {
  const storageState = storageDiagnostics();
  const checks = [
    check(
      "server-version",
      "low",
      "runtime",
      app.version === "0.2.0",
      `Platform version is ${app.version}.`,
      "Keep version aligned with release notes."
    ),
    check(
      "self-modify-disabled",
      "critical",
      "ai-safety",
      engine.allowSelfModify === false,
      "Engine self-modification is disabled.",
      "Keep production AI advisory-only with human approval."
    ),
    check(
      "default-admin-token-production-guard",
      "critical",
      "auth",
      !app.isProduction || security.adminToken !== "dev-admin-token-change-me",
      app.isProduction ? "Production admin token is not the default." : "Development mode uses local admin-token guard.",
      "Use MFA auth and rotate long secrets before production."
    ),
    check(
      "storage-directory",
      "high",
      "storage",
      storageState.dataDirExists && storageState.leadsFileExists,
      "Storage directory and lead file exist.",
      "Use encrypted managed storage before real customer data."
    ),
    check(
      "lead-file-parseable",
      "high",
      "storage",
      parseLeadsFile(storageState.leadsFile),
      "Lead store parses as a JSON array.",
      "Restore from backup or quarantine corrupt file."
    ),
    check(
      "public-site-files",
      "medium",
      "frontend",
      ["index.html", "admin.html", "script.js"].every(exists),
      "Core public/admin frontend files exist.",
      "Restore missing frontend files before launch."
    ),
    check(
      "compliance-reports",
      "high",
      "compliance",
      ["LAWYER_AI_AUDIT_REPORT.md", "KNOWLEDGE_ENGINE_REPORT.md"].every(exists),
      "Compliance and knowledge reports exist.",
      "Run lawyer AI and knowledge audits."
    ),
    check(
      "security-reports",
      "high",
      "security",
      ["SECURITY_BASELINE_AUDIT.md", "SECURITY_BREACH_AUDIT_REPORT.md", "FAILOVER_1000_SCENARIO_REPORT.md"].every(exists),
      "Security, breach, and failover reports exist.",
      "Run security baseline, breach audit, and failover tests."
    ),
    check(
      "managed-database",
      "critical-before-production",
      "production-readiness",
      storageState.adapter !== "local-json-atomic",
      "Current storage adapter is local-json-atomic.",
      "Replace with encrypted managed database before real customer PII."
    ),
    check(
      "mfa-auth",
      "critical-before-production",
      "production-readiness",
      false,
      "MFA/RBAC auth is not installed yet.",
      "Replace admin token with MFA, roles, sessions, and access reviews."
    ),
    check(
      "immutable-audit-log",
      "critical-before-production",
      "production-readiness",
      false,
      "Immutable audit logging is not installed yet.",
      "Log sensitive reads/writes/actions with actor, object, reason, and timestamp."
    ),
    check(
      "monitoring-alerting",
      "high",
      "production-readiness",
      false,
      "Runtime monitoring and alerting are not installed yet.",
      "Add log drain, alerts, uptime checks, and incident escalation."
    )
  ];

  const failed = checks.filter((item) => !item.ok);
  const blockers = failed.filter((item) => item.severity === "critical");
  const productionBlockers = failed.filter((item) => item.severity === "critical-before-production");
  const high = failed.filter((item) => item.severity === "high");

  const scan = {
    ok: blockers.length === 0,
    debugVersion,
    mode,
    ranAt: new Date().toISOString(),
    summary: {
      checks: checks.length,
      passed: checks.length - failed.length,
      failed: failed.length,
      critical: blockers.length,
      criticalBeforeProduction: productionBlockers.length,
      high: high.length
    },
    grade: gradeFor({ blockers, productionBlockers, high }),
    status: statusFor({ blockers, productionBlockers, high }),
    checks,
    recommendedNextActions: nextActions(failed),
    note: "This scanner is advisory. It reports risk and health issues; it does not self-fix or replace security/compliance review."
  };

  if (writeReport) writeDebugReport(scan);
  return scan;
}

function gradeFor({ blockers, productionBlockers, high }) {
  if (blockers.length) return "C";
  if (productionBlockers.length >= 3) return "B for MVP, not production-ready";
  if (high.length) return "A- with gaps";
  return "A";
}

function statusFor({ blockers, productionBlockers, high }) {
  if (blockers.length) return "needs-immediate-fix";
  if (productionBlockers.length) return "healthy-for-mvp-blocked-for-production";
  if (high.length) return "healthy-with-gaps";
  return "healthy";
}

function nextActions(failed) {
  return failed
    .slice()
    .sort((a, b) => severityRank(b.severity) - severityRank(a.severity))
    .slice(0, 8)
    .map((item) => ({
      id: item.id,
      area: item.area,
      severity: item.severity,
      action: item.fix
    }));
}

function severityRank(severity) {
  return {
    critical: 5,
    "critical-before-production": 4,
    high: 3,
    medium: 2,
    low: 1
  }[severity] || 0;
}

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows
    .map((row) => `| ${row.map((cell) => String(cell).replace(/\|/g, "\\|")).join(" | ")} |`)
    .join("\n")}`;
}

function markdownReport(scan) {
  return `# Credit Vivo Debug Health Report

## Result

- Status: **${scan.status}**
- Grade: **${scan.grade}**
- Ran at: **${scan.ranAt}**
- Checks: **${scan.summary.checks}**
- Passed: **${scan.summary.passed}**
- Failed: **${scan.summary.failed}**

## Checks

${table(
  scan.checks.map((item) => [item.ok ? "PASS" : "WATCH", item.severity, item.area, item.id, item.message, item.fix]),
  ["Status", "Severity", "Area", "ID", "Message", "Fix"]
)}

## Next Actions

${scan.recommendedNextActions.map((item, index) => `${index + 1}. **${item.area}:** ${item.action}`).join("\n") || "- None"}

## Note

${scan.note}
`;
}

function writeDebugReport(scan) {
  if (!fs.existsSync(storage.dataDir)) fs.mkdirSync(storage.dataDir, { recursive: true });
  fs.writeFileSync(REPORT_JSON, `${JSON.stringify(scan, null, 2)}\n`, { mode: 0o600 });
  fs.writeFileSync(REPORT_MD, markdownReport(scan));
}

function readLatestDebugReport() {
  if (!fs.existsSync(REPORT_JSON)) {
    return { ok: true, exists: false, message: "No debug scan has run yet." };
  }
  try {
    return { ok: true, exists: true, scan: JSON.parse(fs.readFileSync(REPORT_JSON, "utf8")) };
  } catch {
    return { ok: false, exists: true, errors: ["Latest debug report could not be parsed."] };
  }
}

module.exports = {
  debugVersion,
  runDebugScan,
  readLatestDebugReport,
  writeDebugReport,
  REPORT_JSON,
  REPORT_MD
};
