const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "..", "BENCHMARK_TOOLKIT_REPORT.md");
const commands = [
  [process.execPath, ["tests/web-quality-audit.js"], "Web quality audit"],
  [process.execPath, ["tests/security-baseline-audit.js"], "Security baseline audit"],
  [process.execPath, ["tests/security-breach-audit.js"], "Security breach/failover audit"],
  [process.execPath, ["tests/debug-engine-audit.js"], "Debug scanner audit"],
  [process.execPath, ["tests/load-benchmark.js"], "Load benchmark"],
  [process.execPath, ["tests/competitor-benchmark-report.js"], "Competitor benchmark"],
  [process.execPath, ["tests/knowledge-engine-audit.js"], "Knowledge engine audit"],
  [process.execPath, ["tests/smoke-security.js"], "Smoke/security regression"]
];

const results = commands.map(([cmd, args, label]) => {
  const result = spawnSync(cmd, args, {
    cwd: path.join(__dirname, ".."),
    encoding: "utf8"
  });
  return {
    label,
    status: result.status,
    ok: result.status === 0,
    stdout: String(result.stdout || "").trim(),
    stderr: String(result.stderr || result.error?.message || "").trim()
  };
});

const report = `# Credit Vivo Benchmark Toolkit Report

## Summary

${results.map((item) => `- ${item.ok ? "PASS" : "FAIL"}: ${item.label}`).join("\n")}

## Tool Reports

- [WEB_QUALITY_AUDIT.md](./WEB_QUALITY_AUDIT.md)
- [SECURITY_BASELINE_AUDIT.md](./SECURITY_BASELINE_AUDIT.md)
- [SECURITY_BREACH_AUDIT_REPORT.md](./SECURITY_BREACH_AUDIT_REPORT.md)
- [DEBUG_HEALTH_REPORT.md](./DEBUG_HEALTH_REPORT.md)
- [LOAD_BENCHMARK_REPORT.md](./LOAD_BENCHMARK_REPORT.md)
- [COMPETITOR_BENCHMARK_SCORECARD.md](./COMPETITOR_BENCHMARK_SCORECARD.md)
- [KNOWLEDGE_ENGINE_REPORT.md](./KNOWLEDGE_ENGINE_REPORT.md)

## Raw Results

${results.map((item) => `### ${item.label}\n\nStatus: ${item.status}\n\n\`\`\`text\n${item.stdout || item.stderr || "No output"}\n\`\`\``).join("\n\n")}

## Next External Tools To Plug In

- Playwright for full browser journey automation.
- Lighthouse for performance/accessibility/SEO scoring.
- OWASP ZAP for dynamic security scanning.
- k6 or Artillery for deployed API load testing.
- Semgrep/Snyk for static and dependency security scanning.
- Hotjar/Clarity after launch for real customer behavior.
`;

fs.writeFileSync(OUT, report);
console.log(JSON.stringify({ ok: results.every((item) => item.ok), report: OUT, results: results.map(({ label, ok }) => ({ label, ok })) }, null, 2));
if (results.some((item) => !item.ok)) process.exit(1);
