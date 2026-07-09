const fs = require("fs");
const path = require("path");
const { runDebugScan, readLatestDebugReport, REPORT_MD, REPORT_JSON } = require("../src/debug-engine");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function run() {
  const scan = runDebugScan({ mode: "test", writeReport: true });
  const latest = readLatestDebugReport();

  assert(scan.debugVersion === "cv-debug-scanner-v0.1.0", "debug version");
  assert(scan.summary.checks >= 10, "scan coverage");
  assert(scan.checks.some((item) => item.id === "self-modify-disabled" && item.ok), "self-modify check");
  assert(scan.checks.some((item) => item.id === "lead-file-parseable"), "lead parse check exists");
  assert(scan.checks.some((item) => item.id === "mfa-auth" && !item.ok), "production auth gap");
  assert(["healthy-for-mvp-blocked-for-production", "healthy-with-gaps"].includes(scan.status), "expected scanner status");
  assert(fs.existsSync(REPORT_JSON), "json report exists");
  assert(fs.existsSync(REPORT_MD), "markdown report exists");
  assert(latest.ok === true && latest.exists === true, "latest report");

  console.log(JSON.stringify({
    ok: true,
    status: scan.status,
    grade: scan.grade,
    checks: scan.summary.checks,
    failed: scan.summary.failed,
    report: REPORT_MD
  }, null, 2));
}

try {
  run();
} catch (error) {
  console.error(error);
  process.exit(1);
}
