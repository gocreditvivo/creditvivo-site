# Credit Vivo Load Benchmark

## Result

- Status: **PASS**
- Requests: **250**
- Concurrency: **25**
- Errors: **0**
- Throughput: **2606.7 req/s**
- p50: **7 ms**
- p95: **24 ms**
- p99: **27 ms**

## Notes

This is a local lightweight load test against `/api/health`. Production needs k6/Artillery tests against deployed infrastructure, lead submission, admin reads, auth, and queue behavior.
