const fs = require("fs");
const path = require("path");
const { recommendationFor } = require("../src/lead-engine");
const { buildGrowthPlan, retentionPlan, summarizeLeads } = require("../src/growth-engine");

const OUT = path.join(__dirname, "..", "CUSTOMER_SCENARIO_REPORT.md");
const SCENARIOS = 1000;

const goals = [
  "Auto approval",
  "Mortgage readiness",
  "Apartment approval",
  "Credit card or loan",
  "Identity theft help",
  "General credit clarity"
];

const scoreRanges = ["Under 580", "580-639", "640-699", "700+", "Not sure"];
const plans = ["Free Review", "Plus - $59/mo", "Pro - $99/mo", "Legal+ eligibility"];
const channels = ["google-search", "tiktok-education", "partner-referral", "seo", "youtube", "meta-retargeting", "direct"];

const psychProfiles = [
  { id: "urgent-denied", trigger: "recent denial", fear: "another rejection", need: "fast clarity", trustBarrier: "scam fear" },
  { id: "planner", trigger: "future purchase", fear: "not being ready", need: "step-by-step roadmap", trustBarrier: "too much jargon" },
  { id: "ashamed-avoider", trigger: "collections anxiety", fear: "being judged", need: "respectful language", trustBarrier: "embarrassment" },
  { id: "identity-victim", trigger: "fraud alert", fear: "loss of control", need: "protection and documentation", trustBarrier: "privacy concern" },
  { id: "skeptic", trigger: "saw an ad", fear: "wasting money", need: "proof and transparency", trustBarrier: "credit repair reputation" },
  { id: "thin-file-builder", trigger: "no credit history", fear: "stuck without options", need: "builder tools", trustBarrier: "does this count" }
];

function pick(list, i, salt = 0) {
  return list[(i * 37 + salt * 11) % list.length];
}

function weightedScore(i, profile) {
  if (profile.id === "urgent-denied") return pick(["Under 580", "580-639", "640-699"], i, 2);
  if (profile.id === "planner") return pick(["580-639", "640-699", "700+", "Not sure"], i, 3);
  if (profile.id === "ashamed-avoider") return pick(["Under 580", "580-639", "Not sure"], i, 4);
  if (profile.id === "identity-victim") return pick(["Under 580", "580-639", "640-699", "Not sure"], i, 5);
  if (profile.id === "thin-file-builder") return pick(["Not sure", "640-699", "700+"], i, 6);
  return pick(scoreRanges, i, 7);
}

function weightedGoal(i, profile) {
  if (profile.id === "urgent-denied") return pick(["Auto approval", "Apartment approval", "Credit card or loan"], i, 2);
  if (profile.id === "planner") return pick(["Mortgage readiness", "Auto approval", "Credit card or loan"], i, 3);
  if (profile.id === "identity-victim") return "Identity theft help";
  if (profile.id === "thin-file-builder") return pick(["Credit card or loan", "General credit clarity"], i, 4);
  return pick(goals, i, 5);
}

function planFor(profile, scoreRange, i) {
  if (profile.id === "identity-victim") return pick(["Pro - $99/mo", "Legal+ eligibility"], i, 1);
  if (profile.id === "skeptic") return pick(["Free Review", "Plus - $59/mo"], i, 2);
  if (["Under 580", "580-639"].includes(scoreRange)) return pick(["Plus - $59/mo", "Pro - $99/mo", "Free Review"], i, 3);
  return pick(plans, i, 4);
}

function scenario(i) {
  const profile = pick(psychProfiles, i, 1);
  const scoreRange = weightedScore(i, profile);
  const goal = weightedGoal(i, profile);
  const planInterest = planFor(profile, scoreRange, i);
  const lead = {
    id: `scenario-${String(i + 1).padStart(4, "0")}`,
    createdAt: new Date(Date.UTC(2026, 6, 7, 12, i % 60, 0)).toISOString(),
    status: "new",
    name: `Scenario ${i + 1}`,
    email: `scenario${i + 1}@example.com`,
    phone: "",
    goal,
    scoreRange,
    planInterest,
    preferredContact: pick(["Email", "Phone", "Text"], i, 9),
    source: pick(channels, i, 10),
    notes: `${profile.trigger}; ${profile.need}`,
    psychProfile: profile.id,
    fear: profile.fear,
    trustBarrier: profile.trustBarrier
  };
  return { ...lead, recommendation: recommendationFor(lead) };
}

function countBy(items, key) {
  return items.reduce((acc, item) => {
    const value = typeof key === "function" ? key(item) : item[key];
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function topEntries(obj, limit = 10) {
  return Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, limit);
}

function riskScore(lead) {
  let score = 0;
  if (lead.trustBarrier === "scam fear") score += 25;
  if (lead.trustBarrier === "privacy concern") score += 25;
  if (lead.planInterest === "Legal+ eligibility") score += 15;
  if (lead.scoreRange === "Not sure") score += 10;
  if (lead.psychProfile === "ashamed-avoider") score += 20;
  if (lead.source === "tiktok-education") score += 8;
  return Math.min(100, score);
}

function opportunity(lead) {
  if (lead.goal === "Identity theft help") return "Protection + legal eligibility pathway";
  if (lead.goal === "Auto approval") return "Dealer-prep readiness funnel";
  if (lead.goal === "Mortgage readiness") return "Mortgage readiness partner funnel";
  if (lead.goal === "Apartment approval") return "Rental approval readiness funnel";
  if (lead.psychProfile === "thin-file-builder") return "Builder tools education";
  return "Credit clarity lifecycle";
}

function mdTable(entries, headers) {
  const rows = entries.map((row) => `| ${row.map(String).join(" | ")} |`).join("\n");
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows}`;
}

function run() {
  const leads = Array.from({ length: SCENARIOS }, (_, i) => scenario(i));
  const summary = summarizeLeads(leads);
  const growth = buildGrowthPlan(leads, { monthlyBudget: 3000 });
  const retention = retentionPlan(leads);
  const risks = leads.map((lead) => ({ ...lead, riskScore: riskScore(lead), opportunity: opportunity(lead) }));

  const byPsych = countBy(risks, "psychProfile");
  const byRiskBand = countBy(risks, (lead) => lead.riskScore >= 50 ? "high" : lead.riskScore >= 25 ? "medium" : "low");
  const byOpportunity = countBy(risks, "opportunity");
  const highRisk = risks.filter((lead) => lead.riskScore >= 50);
  const legalPlus = risks.filter((lead) => lead.planInterest === "Legal+ eligibility");
  const identity = risks.filter((lead) => lead.goal === "Identity theft help");
  const conversionLikely = risks.filter((lead) => ["Plus - $59/mo", "Pro - $99/mo", "Legal+ eligibility"].includes(lead.planInterest));

  const recommendations = [
    "Add a customer-facing quiz before the form so unsure customers feel guided, not judged.",
    "Create separate landing paths for auto, mortgage, apartment, identity theft, and credit-card/loan readiness.",
    "Show privacy and security reassurance beside every future upload or account step.",
    "Keep Legal+ eligibility after intake, not as a hard-sold public promise.",
    "Add proof modules: process transparency, founder mission, security posture, and documented case studies once available.",
    "Add nurture journeys by psychology profile: urgent denial, planner, ashamed avoider, identity victim, skeptic, thin-file builder.",
    "Build a customer portal next; trust increases when users can see status, tasks, and next actions.",
    "Add partner funnels for dealerships, loan officers, rental agents, and mortgage brokers.",
    "Use AI to draft next-step explanations, but require compliance review before any dispute/legal action.",
    "Measure complaint rate and refund/cancel reasons as first-class growth metrics, not afterthoughts."
  ];

  const failureModes = [
    "Trust collapse if customers think CV is promising deletions or approvals.",
    "Drop-off if the first form feels too much like a sales lead form and not enough like a helpful review.",
    "Privacy fear if customers are asked for sensitive data too early.",
    "Legal risk if attorney language implies automatic representation.",
    "Retention loss after repair if the product does not shift customers into build/protect/prepare mode.",
    "Low-quality leads from broad paid social if ads are too generic.",
    "Operational overload if Legal+ leads are not triaged by eligibility rules.",
    "Brand dilution if pricing feels cheap while claiming attorney authority.",
    "Compliance risk if future testimonials imply typical guaranteed outcomes.",
    "Scaling risk if local JSON/admin-token design is used with real customer data."
  ];

  const report = `# Credit Vivo 1,000-Customer Scenario Test

## Summary

Generated and tested **${SCENARIOS} customer scenarios** across goals, score ranges, plan interest, source channels, and psychology profiles.

This is a synthetic stress test of the current engine and business model. It does not use real customer data.

## Aggregate Results

- Total scenarios: **${SCENARIOS}**
- Likely paid-intent scenarios: **${conversionLikely.length}**
- Legal+ interest scenarios: **${legalPlus.length}**
- Identity-theft scenarios: **${identity.length}**
- High trust-risk scenarios: **${highRisk.length}**
- Top goal: **${summary.topGoal}**
- Top plan interest: **${summary.topPlan}**

## Customer Psychology Distribution

${mdTable(topEntries(byPsych), ["Psychology profile", "Scenarios"])}

## Goal Distribution

${mdTable(topEntries(summary.byGoal), ["Goal", "Scenarios"])}

## Score Range Distribution

${mdTable(topEntries(summary.byScoreRange), ["Score range", "Scenarios"])}

## Plan Interest Distribution

${mdTable(topEntries(summary.byPlan), ["Plan", "Scenarios"])}

## Trust Risk Bands

${mdTable(topEntries(byRiskBand), ["Risk band", "Scenarios"])}

## Opportunity Map

${mdTable(topEntries(byOpportunity), ["Opportunity", "Scenarios"])}

## Growth Engine Output

- Mode: **${growth.mode}**
- Audience: **${growth.audience}**
- Angle: **${growth.compliantAngle.headline}**
- Guardrail: **${growth.note}**
- Recommended channels: **${growth.channelPlan.map((channel) => channel.name).join(", ")}**

## Retention Engine Output

Retention segments:

${retention.segments.map((segment) => `- **${segment.id}:** ${segment.action}`).join("\n")}

KPIs to track:

${retention.retentionKpis.map((kpi) => `- ${kpi}`).join("\n")}

## How Credit Vivo Can Be Better

${recommendations.map((item, index) => `${index + 1}. ${item}`).join("\n")}

## How Credit Vivo Can Fail

${failureModes.map((item, index) => `${index + 1}. ${item}`).join("\n")}

## Business Model Insight

Credit Vivo should not act like a one-time credit repair shop. The strongest model is:

**Free review -> paid guided path -> builder/protection retention -> Legal+ eligibility for qualified unresolved issues -> approval-readiness partner ecosystem.**

This keeps customers after repair because they still need monitoring, builder tools, identity protection, and readiness for future approvals.

## Innovation Insight

The best innovation is not "AI does everything." It is:

- AI explains and organizes.
- The customer always sees the next step.
- Compliance gates stop unsafe claims.
- Attorney-supported review is reserved for eligible cases.
- Growth automation recommends and simulates, but real spend requires approval.
- The engine learns from aggregate behavior without exposing or exploiting sensitive credit data.

## Next Build Recommendations

1. Add a public guided quiz before the full form.
2. Add source tracking fields to URLs.
3. Add admin filters by goal, plan interest, source, and risk band.
4. Add customer status lifecycle: new, contacted, booked, enrolled, active, retained, escalated.
5. Add retention sequence templates for each psychology profile.
6. Add partner pages for auto, mortgage, apartment, and identity theft.
7. Replace local JSON with encrypted database before real data.
8. Replace admin token with auth/MFA before real operations.
`;

  fs.writeFileSync(OUT, report);

  console.log(JSON.stringify({
    ok: true,
    scenarios: SCENARIOS,
    paidIntent: conversionLikely.length,
    legalPlus: legalPlus.length,
    identityTheft: identity.length,
    highTrustRisk: highRisk.length,
    report: OUT
  }, null, 2));
}

run();
