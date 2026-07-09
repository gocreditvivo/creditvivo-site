const fs = require("fs");
const path = require("path");
const { strategicPlan, launchBudgets } = require("../src/strategic-intelligence");

const OUT = path.join(__dirname, "..", "STRATEGIC_INTELLIGENCE_20_YEAR_PLAN.md");

function money(value) {
  return `$${Number(value).toLocaleString()}`;
}

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows.map((row) => `| ${row.join(" | ")} |`).join("\n")}`;
}

function budgetTable(budget) {
  return table(Object.entries(budget.lineItems).map(([key, value]) => [key, money(value)]), ["Line item", "Budget"]);
}

function run() {
  const plan = strategicPlan({ mode: "serious30Day", days: 14 });
  const lean = launchBudgets.lean14Day;
  const serious = launchBudgets.serious30Day;
  const investor = launchBudgets.investor90Day;

  const report = `# Credit Vivo Strategic Intelligence Plan

## Executive Answer

Credit Vivo should launch as a **credit readiness fintech**, not a generic credit repair company.

Operating principle:

**Track everything. Automate recommendations. Require approval before spend, external posting, customer messaging, or legal escalation.**

## Precise Launch Money

Recommended launch budget: **${money(serious.total)} for 30 days**.

Minimum viable launch: **${money(lean.total)} for 14 days**.

Investor-grade 90-day launch: **${money(investor.total)}**.

### Recommended 30-Day Budget

${budgetTable(serious)}

### Lean 14-Day Budget

${budgetTable(lean)}

### Investor 90-Day Budget

${budgetTable(investor)}

## 14-Day Launch Plan

${table(plan.launchPlan.map((item) => [item.day, item.owner, item.action, money(item.cost)]), ["Day", "Owner", "Action", "Cost"])}

## Who / What / Where / How

### Who

${plan.whoWhatWhereHow.who.map((item) => `- ${item}`).join("\n")}

### What

${plan.whoWhatWhereHow.what.map((item) => `- ${item}`).join("\n")}

### Where

${plan.whoWhatWhereHow.where.map((item) => `- ${item}`).join("\n")}

### How

${plan.whoWhatWhereHow.how.map((item) => `- ${item}`).join("\n")}

## Competitor Tracking

${table(plan.competitors.map((c) => [c.name, c.model, c.strength, c.weakness, c.cvCounter]), ["Competitor", "Model", "Strength", "Weakness", "CV counter"])}

## Economic Scenario Prep

${table(plan.macroScenarios.map((s) => [s.name, s.trigger, s.businessAction, s.budgetBias, s.customerMessage]), ["Scenario", "Trigger", "Action", "Budget bias", "Customer message"])}

## 5 / 10 / 15 / 20 Year Future Plan

${table(plan.horizons.map((h) => [h.horizon, h.goal, h.milestones.join("; "), h.risks.join("; "), h.moat]), ["Horizon", "Goal", "Milestones", "Risks", "Moat"])}

## KPI Dashboard

The Strategic Intelligence engine should track:

${plan.trackedKpis.map((kpi) => `- ${kpi}`).join("\n")}

## Launch Decision Rules

- Scale Google Search only if cost per qualified lead is below **$85** after 7 days.
- Scale partner outreach if booked-call rate is above **20%**.
- Pause any ad with complaint rate above **1%** or misleading-claim feedback.
- Push Plus if prospects want build/track help.
- Push Pro only when protection/readiness value is clear.
- Offer Legal+ only after eligibility review.
- Keep emergency cash reserve equal to **3 months** of fixed operating costs.

## First 30 Days Expected Targets

Assuming the **${money(serious.total)}** launch budget:

- 700-1,200 targeted site visitors
- 120-220 review requests
- 35-70 booked calls or high-intent follow-ups
- 15-35 paid-plan starts if offer and follow-up are strong
- 5-15 Legal+ eligibility reviews
- Target blended cost per lead: **$45-$95**
- Target booked-call cost: **$125-$250**

These are planning targets, not guarantees.

## Bank-Grade Warning

Before real customer data or paid scale:

- Replace local JSON with encrypted database.
- Replace admin token with auth/MFA.
- Add consent records, cancellation flow, and contract review.
- Add audit logs and monitoring.
- Add state-law and CROA/FCRA review.
- Add vendor risk review for credit data, builder tools, identity protection, payments, and attorney network.

## Sources And Grounding

This plan uses current regulatory/economic grounding from:

- FTC Credit Repair Organizations Act
- CFPB Lexington Law / CreditRepair.com enforcement history
- FTC Safeguards Rule
- NIST CSF 2.0
- Federal Reserve / FRED economic projection references
- CBO long-term economic outlook references
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({ ok: true, report: OUT, recommendedBudget: serious.total, leanBudget: lean.total, investorBudget: investor.total }, null, 2));
}

run();
