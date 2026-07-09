const fs = require("fs");
const path = require("path");
const { withTestServer } = require("./lib/test-server");

const OUT = path.join(__dirname, "..", "LOAD_BENCHMARK_REPORT.md");
const TOTAL = Number(process.env.LOAD_REQUESTS || 250);
const CONCURRENCY = Number(process.env.LOAD_CONCURRENCY || 25);

function percentile(values, p) {
  const sorted = values.slice().sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))] || 0;
}

async function worker(baseUrl, queue, results) {
  while (queue.length) {
    const index = queue.pop();
    const start = performance.now();
    try {
      const response = await fetch(`${baseUrl}/api/health`);
      const elapsed = performance.now() - start;
      results.push({ index, ok: response.ok, status: response.status, elapsed });
    } catch (error) {
      const elapsed = performance.now() - start;
      results.push({ index, ok: false, status: 0, elapsed, error: error.message });
    }
  }
}

async function run() {
  await withTestServer(8916, async ({ baseUrl }) => {
    const queue = Array.from({ length: TOTAL }, (_, i) => i);
    const results = [];
    const start = performance.now();
    await Promise.all(Array.from({ length: CONCURRENCY }, () => worker(baseUrl, queue, results)));
    const totalElapsed = performance.now() - start;
    const times = results.map((item) => item.elapsed);
    const errors = results.filter((item) => !item.ok);

    const metrics = {
      totalRequests: TOTAL,
      concurrency: CONCURRENCY,
      ok: errors.length === 0,
      errors: errors.length,
      totalMs: Math.round(totalElapsed),
      requestsPerSecond: Math.round((TOTAL / (totalElapsed / 1000)) * 10) / 10,
      p50Ms: Math.round(percentile(times, 0.5)),
      p95Ms: Math.round(percentile(times, 0.95)),
      p99Ms: Math.round(percentile(times, 0.99))
    };

    const report = `# Credit Vivo Load Benchmark

## Result

- Status: **${metrics.ok ? "PASS" : "FAIL"}**
- Requests: **${metrics.totalRequests}**
- Concurrency: **${metrics.concurrency}**
- Errors: **${metrics.errors}**
- Throughput: **${metrics.requestsPerSecond} req/s**
- p50: **${metrics.p50Ms} ms**
- p95: **${metrics.p95Ms} ms**
- p99: **${metrics.p99Ms} ms**

## Notes

This is a local lightweight load test against \`/api/health\`. Production needs k6/Artillery tests against deployed infrastructure, lead submission, admin reads, auth, and queue behavior.
`;

    fs.writeFileSync(OUT, report);
    console.log(JSON.stringify({ ...metrics, report: OUT }, null, 2));
    if (!metrics.ok) process.exitCode = 1;
  });
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
