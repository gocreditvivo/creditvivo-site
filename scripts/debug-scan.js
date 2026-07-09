const { runDebugScan } = require("../src/debug-engine");

const scan = runDebugScan({ mode: process.env.CV_DEBUG_MODE || "cli", writeReport: true });
console.log(JSON.stringify({
  ok: scan.ok,
  status: scan.status,
  grade: scan.grade,
  failed: scan.summary.failed,
  report: "DEBUG_HEALTH_REPORT.md"
}, null, 2));

if (scan.summary.critical > 0) process.exitCode = 1;
