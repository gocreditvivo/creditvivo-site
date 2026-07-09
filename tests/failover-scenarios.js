const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "..", "FAILOVER_1000_SCENARIO_REPORT.md");
const SCENARIOS = 1000;

const domains = [
  "website",
  "lead-api",
  "admin-auth",
  "storage",
  "growth-engine",
  "strategic-intelligence",
  "customer-support",
  "compliance",
  "vendor-credit-data",
  "vendor-identity-protection",
  "vendor-builder",
  "attorney-network",
  "payments",
  "marketing",
  "macro-economy",
  "security"
];

const failures = {
  website: ["page down", "mobile overflow", "form friction", "slow load", "unclear copy"],
  "lead-api": ["validation outage", "rate-limit false positive", "malformed payload spike", "API timeout", "submission duplicate"],
  "admin-auth": ["token lost", "bad token lockout", "session confusion", "role missing", "unauthorized attempt"],
  storage: ["write failure", "corrupt JSON", "disk full", "backup missing", "read latency"],
  "growth-engine": ["bad channel recommendation", "overweights paid social", "bad budget simulation", "low-quality lead spike", "creative fatigue"],
  "strategic-intelligence": ["stale competitor assumptions", "bad macro assumption", "overoptimistic forecast", "missing KPI", "wrong launch budget"],
  "customer-support": ["lead response delay", "script confusion", "high call volume", "angry customer", "unanswered Legal+ question"],
  compliance: ["risky score claim", "risky deletion claim", "attorney wording risk", "advance-fee risk", "testimonial substantiation gap"],
  "vendor-credit-data": ["provider outage", "pricing increase", "data mismatch", "consent issue", "API contract delay"],
  "vendor-identity-protection": ["coverage gap", "claims confusion", "API outage", "support handoff issue", "insurance wording issue"],
  "vendor-builder": ["bank partner delay", "tradeline reporting issue", "eligibility confusion", "cost increase", "bureau coverage mismatch"],
  "attorney-network": ["state coverage gap", "capacity bottleneck", "conflict check delay", "quality inconsistency", "fee structure issue"],
  payments: ["processor decline spike", "chargeback spike", "subscription failure", "refund confusion", "billing compliance review"],
  marketing: ["CPL spike", "ad disapproval", "low-quality traffic", "partner lead drop", "brand trust concern"],
  "macro-economy": ["credit tightening", "rising unemployment", "inflation pressure", "consumer cash stress", "lender approval drop"],
  security: ["credential stuffing", "data exposure attempt", "dependency vulnerability", "missing audit log", "phishing risk"]
};

const playbooks = {
  website: "Serve static fallback page, keep phone/email capture, rollback latest content, monitor conversion.",
  "lead-api": "Queue submissions client-side where possible, show safe retry, preserve idempotency, alert operator.",
  "admin-auth": "Use break-glass admin procedure, rotate token, require MFA in production, log access.",
  storage: "Switch to read-only mode, restore from backup, stop writes, migrate to encrypted managed database.",
  "growth-engine": "Freeze spend recommendations, route to manual review, compare against KPI thresholds.",
  "strategic-intelligence": "Mark assumptions stale, refresh market data, keep forecasts scenario-based.",
  "customer-support": "Trigger priority queue, use approved scripts, escalate Legal+ and identity-theft cases.",
  compliance: "Pause affected copy/campaign, run compliance review, replace risky wording, document approval.",
  "vendor-credit-data": "Use manual upload/waitlist fallback, notify customer, avoid bureau credential collection.",
  "vendor-identity-protection": "Route to manual identity-theft checklist and partner status page.",
  "vendor-builder": "Hide builder availability claim, show eligibility waitlist, preserve repair/protect path.",
  "attorney-network": "Route to eligibility waitlist, show state coverage, avoid representation promise.",
  payments: "Pause upgrades, preserve free review, reconcile subscriptions, review billing language.",
  marketing: "Pause bad channel, shift to SEO/partners/email, tighten targeting and compliance copy.",
  "macro-economy": "Shift message to readiness/protection, protect cash, lower CAC channels, monitor churn.",
  security: "Disable affected access, rotate secrets, inspect logs, notify per incident plan if required."
};

function pick(list, i, salt = 0) {
  return list[(i * 41 + salt * 17) % list.length];
}

function severity(domain, failure, i) {
  let score = 20 + ((i * 13) % 45);
  if (["security", "compliance", "payments", "storage"].includes(domain)) score += 25;
  if (["data exposure attempt", "risky deletion claim", "advance-fee risk", "write failure", "corrupt JSON"].includes(failure)) score += 20;
  if (["macro-economy", "vendor-credit-data", "attorney-network"].includes(domain)) score += 10;
  return Math.min(100, score);
}

function band(score) {
  if (score >= 85) return "critical";
  if (score >= 65) return "high";
  if (score >= 40) return "medium";
  return "low";
}

function rto(domain, severityBand) {
  if (severityBand === "critical") return "0-2 hours";
  if (severityBand === "high") return "same business day";
  if (["security", "compliance", "payments"].includes(domain)) return "same business day";
  if (severityBand === "medium") return "1-3 days";
  return "next sprint";
}

function scenario(i) {
  const domain = pick(domains, i, 3);
  const failure = pick(failures[domain], i, 7);
  const score = severity(domain, failure, i);
  const severityBand = band(score);
  return {
    id: `failover-${String(i + 1).padStart(4, "0")}`,
    domain,
    failure,
    severity: severityBand,
    score,
    rto: rto(domain, severityBand),
    fallback: playbooks[domain],
    customerImpact: customerImpact(domain, failure),
    businessImpact: businessImpact(domain, failure)
  };
}

function customerImpact(domain, failure) {
  if (domain === "security") return "trust risk; possible account lockdown or notification workflow";
  if (domain === "compliance") return "trust/legal risk; affected message or campaign must pause";
  if (domain === "website" || domain === "lead-api") return "lead may not complete free review";
  if (domain.includes("vendor")) return "customer path may delay or switch to manual review";
  if (domain === "attorney-network") return "Legal+ eligibility may waitlist by state/capacity";
  if (domain === "macro-economy") return "customer urgency rises but ability to pay may drop";
  return "workflow delay or operator review needed";
}

function businessImpact(domain, failure) {
  if (domain === "marketing") return "CAC rises or lead quality falls";
  if (domain === "payments") return "revenue collection or churn risk";
  if (domain === "storage") return "data integrity and operations risk";
  if (domain === "strategic-intelligence") return "bad decisions if assumptions are not refreshed";
  if (domain === "growth-engine") return "wasted spend if recommendations are not approval-gated";
  return "conversion, retention, trust, or operational capacity risk";
}

function countBy(items, key) {
  return items.reduce((acc, item) => {
    const value = typeof key === "function" ? key(item) : item[key];
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function topEntries(obj, limit = 20) {
  return Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, limit);
}

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows.map((row) => `| ${row.map(String).join(" | ")} |`).join("\n")}`;
}

function run() {
  const scenarios = Array.from({ length: SCENARIOS }, (_, i) => scenario(i));
  const byDomain = countBy(scenarios, "domain");
  const bySeverity = countBy(scenarios, "severity");
  const critical = scenarios.filter((item) => item.severity === "critical");
  const high = scenarios.filter((item) => item.severity === "high");
  const topCriticalDomains = countBy(critical, "domain");

  const topRisks = scenarios
    .slice()
    .sort((a, b) => b.score - a.score)
    .slice(0, 15)
    .map((item) => [item.id, item.domain, item.failure, item.severity, item.rto, item.fallback]);

  const report = `# Credit Vivo 1,000 Failover Scenario Report

## Executive Answer

Credit Vivo's failover strategy must protect **trust first**, then **data**, then **cash**, then **growth**.

The system should degrade safely:

1. Keep the public site and free review available.
2. Stop risky automation before it spends, posts, or messages.
3. Lock down admin/customer data during security or storage incidents.
4. Move vendor-dependent workflows to waitlist/manual review.
5. Pause any compliance-risk copy immediately.

## Simulation Summary

- Scenarios run: **${SCENARIOS}**
- Critical scenarios: **${critical.length}**
- High scenarios: **${high.length}**
- Medium/low scenarios: **${SCENARIOS - critical.length - high.length}**

## Severity Distribution

${table(topEntries(bySeverity), ["Severity", "Count"])}

## Domain Distribution

${table(topEntries(byDomain), ["Domain", "Scenarios"])}

## Critical Domain Hotspots

${table(topEntries(topCriticalDomains), ["Domain", "Critical scenarios"])}

## Top 15 Failover Risks

${table(topRisks, ["ID", "Domain", "Failure", "Severity", "RTO", "Fallback"])}

## Recommended Failover Architecture

1. **Public site fallback:** static landing page + phone/email fallback + queue-free review request.
2. **Lead API fallback:** idempotent lead creation, retry-safe queue, alert on write failure.
3. **Storage fallback:** encrypted managed DB, point-in-time recovery, immutable audit log, daily export backup.
4. **Admin fallback:** MFA auth, break-glass account, admin action logs, role-based access.
5. **Growth fallback:** approval-gated campaigns, spend caps, stop-loss rules, manual pause switch.
6. **Compliance fallback:** instant copy/campaign pause, claim review queue, approval records.
7. **Vendor fallback:** manual checklist/waitlist for credit data, builder, identity protection, attorney coverage.
8. **Payment fallback:** preserve free review, pause upgrades, reconcile subscriptions, clear refund path.
9. **Security fallback:** rotate secrets, lock admin sessions, inspect logs, follow incident notification plan.
10. **Macro fallback:** reduce paid spend, shift to SEO/partners, emphasize readiness/protection.

## Minimum Recovery Targets

${table(
  [
    ["Public website", "99.9%", "static fallback immediately", "same hour"],
    ["Lead capture", "99.5%", "retry queue/manual capture", "0-2 hours"],
    ["Admin access", "99.5%", "break-glass admin", "same business day"],
    ["Growth automation", "safe stop", "manual review only", "immediate"],
    ["Compliance incident", "safe stop", "pause affected copy", "immediate"],
    ["Vendor outage", "degraded mode", "manual checklist/waitlist", "same day"],
    ["Security incident", "containment first", "lockdown/rotate/inspect", "0-2 hours"]
  ],
  ["Area", "Target", "Fallback", "Recovery target"]
)}

## What We Have Now

- Public site.
- Lead API.
- Protected admin.
- Growth and strategic engines.
- Test mode.
- Smoke/security tests.
- Local JSON storage.

## Gaps Before Real Production

- No real database failover.
- No real auth/MFA.
- No encrypted backups.
- No audit log.
- No monitoring/alerting.
- No incident response workflow.
- No vendor status integration.
- No payment recovery flow.
- No real message queue.

## Priority Build Plan

1. Replace JSON with encrypted managed database and backups.
2. Add auth/MFA and role-based admin.
3. Add audit log for every admin/customer action.
4. Add queue for lead submissions and lifecycle messages.
5. Add status page and internal alerts.
6. Add campaign kill switch.
7. Add vendor fallback states.
8. Add compliance approval records.

## Business Rule

When failure happens, Credit Vivo should never improvise promises. The safe customer message is:

**We received your request. Your path is being reviewed. We will follow up with the next safe step.**
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({
    ok: true,
    scenarios: SCENARIOS,
    critical: critical.length,
    high: high.length,
    report: OUT
  }, null, 2));
}

run();
