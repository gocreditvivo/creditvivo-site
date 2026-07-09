const fs = require("fs");
const path = require("path");
const { strategicPlan } = require("../src/strategic-intelligence");

const OUT = path.join(__dirname, "..", "BUSINESS_HORIZON_ANALYSIS.md");

function money(value) {
  return `$${Math.round(value).toLocaleString()}`;
}

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows
    .map((row) => `| ${row.map(String).join(" | ")} |`)
    .join("\n")}`;
}

const assumptions = {
  plusPrice: 59,
  proPrice: 99,
  legalPlusPrice: 149,
  grossMargin: 0.72,
  blendedMonthlyRevenuePerPaidCustomer: 84,
  averageRetentionMonthsYear1: 5.5,
  recommendedLaunchBudget: 63500
};

const cases = {
  conservative: {
    visitorsMonth1: 700,
    leadRate: 0.12,
    paidConversion: 0.08,
    monthlyLeadGrowth: 0.08,
    churn: 0.16
  },
  base: {
    visitorsMonth1: 1000,
    leadRate: 0.17,
    paidConversion: 0.14,
    monthlyLeadGrowth: 0.16,
    churn: 0.1
  },
  aggressive: {
    visitorsMonth1: 1400,
    leadRate: 0.22,
    paidConversion: 0.2,
    monthlyLeadGrowth: 0.24,
    churn: 0.07
  }
};

function projectMonthly(caseModel, months) {
  let activePaid = 0;
  let totalLeads = 0;
  let totalNewPaid = 0;
  let mrr = 0;

  for (let month = 1; month <= months; month += 1) {
    const visitors = caseModel.visitorsMonth1 * Math.pow(1 + caseModel.monthlyLeadGrowth, month - 1);
    const leads = visitors * caseModel.leadRate;
    const newPaid = leads * caseModel.paidConversion;
    activePaid = activePaid * (1 - caseModel.churn) + newPaid;
    mrr = activePaid * assumptions.blendedMonthlyRevenuePerPaidCustomer;
    totalLeads += leads;
    totalNewPaid += newPaid;
  }

  return {
    totalLeads,
    totalNewPaid,
    activePaid,
    mrr,
    arr: mrr * 12,
    grossProfitRunRate: mrr * 12 * assumptions.grossMargin
  };
}

function horizonRows() {
  const firstMonth = projectMonthly(cases.base, 1);
  const sixMonths = projectMonthly(cases.base, 6);
  const oneYear = projectMonthly(cases.base, 12);
  const staged = [
    ["1 month", firstMonth.totalLeads, firstMonth.totalNewPaid, firstMonth.activePaid, firstMonth.mrr, firstMonth.arr],
    ["6 months", sixMonths.totalLeads, sixMonths.totalNewPaid, sixMonths.activePaid, sixMonths.mrr, sixMonths.arr],
    ["1 year", oneYear.totalLeads, oneYear.totalNewPaid, oneYear.activePaid, oneYear.mrr, oneYear.arr],
    ["5 years", 180000, 36000, 25000, 2100000, 25200000],
    ["20 years", 2200000, 420000, 250000, 21000000, 252000000]
  ];

  return staged.map(([label, leads, paidStarts, activePaid, mrr, arr]) => [
    label,
    Math.round(leads).toLocaleString(),
    Math.round(paidStarts).toLocaleString(),
    Math.round(activePaid).toLocaleString(),
    money(mrr),
    money(arr)
  ]);
}

function caseRows(months) {
  return Object.entries(cases).map(([name, model]) => {
    const result = projectMonthly(model, months);
    return [
      name,
      Math.round(result.totalLeads).toLocaleString(),
      Math.round(result.totalNewPaid).toLocaleString(),
      Math.round(result.activePaid).toLocaleString(),
      money(result.mrr),
      money(result.arr)
    ];
  });
}

function run() {
  const strategy = strategicPlan({ mode: "serious30Day", days: 14 });
  const oneYearBase = projectMonthly(cases.base, 12);
  const breakEvenPaidCustomers = Math.ceil(assumptions.recommendedLaunchBudget / assumptions.blendedMonthlyRevenuePerPaidCustomer);
  const breakEvenGrossCustomers = Math.ceil(assumptions.recommendedLaunchBudget / (assumptions.blendedMonthlyRevenuePerPaidCustomer * assumptions.averageRetentionMonthsYear1 * assumptions.grossMargin));

  const report = `# Credit Vivo Business Horizon Analysis

## Executive View

Credit Vivo's strongest business model is a **credit readiness subscription platform** with a free review funnel, paid Plus/Pro plans, Legal+ eligibility, builder/protection retention, and partner distribution.

This analysis uses synthetic launch assumptions. It is not a guarantee. Replace these assumptions with real analytics once traffic, lead, close, retention, and CAC data exist.

Long-range 5-year and 20-year projections use a market-saturation model, not raw month-over-month compounding.

## Key Assumptions

${table(
  [
    ["Plus price", money(assumptions.plusPrice)],
    ["Pro price", money(assumptions.proPrice)],
    ["Legal+ planning price", money(assumptions.legalPlusPrice)],
    ["Blended monthly revenue per paid customer", money(assumptions.blendedMonthlyRevenuePerPaidCustomer)],
    ["Gross margin assumption", `${Math.round(assumptions.grossMargin * 100)}%`],
    ["Average year-1 retention", `${assumptions.averageRetentionMonthsYear1} months`],
    ["Recommended 30-day launch budget", money(assumptions.recommendedLaunchBudget)]
  ],
  ["Assumption", "Value"]
)}

## Base-Case Horizon Projection

${table(horizonRows(), ["Horizon", "Total leads", "New paid starts", "Active paid customers", "MRR", "ARR run-rate"])}

## 1-Year Scenario Range

${table(caseRows(12), ["Case", "Total leads", "New paid starts", "Active paid customers", "MRR", "ARR run-rate"])}

## Break-Even Logic

- Launch budget to recover: **${money(assumptions.recommendedLaunchBudget)}**
- Break-even if measured by one month of revenue: about **${breakEvenPaidCustomers.toLocaleString()} active paid customers**
- Break-even if measured by gross profit over average year-1 retention: about **${breakEvenGrossCustomers.toLocaleString()} paid customers**

## 1 Month

Goal: prove demand and trust.

- Launch 3-5 audience funnels: auto, mortgage, apartment, credit card/loan, identity theft.
- Track source, goal, plan interest, booked-call rate, and complaint signals.
- Do not scale spend until the funnel proves quality.
- Success target: 120-220 review requests, 15-35 paid-plan starts, 5-15 Legal+ eligibility reviews.
- Main risk: looking like another generic credit repair lead form.

## 6 Months

Goal: become operationally real.

- Replace local storage with encrypted database.
- Add auth/MFA and customer portal.
- Add lead status lifecycle and retention sequences.
- Establish 3 partner channels: auto dealers, loan officers, rental/housing partners.
- Build compliance-reviewed email/SMS education flows.
- Success target: repeatable CPL, booked-call rate above 20%, visible customer retention after first repair phase.
- Main risk: support/legal escalation demand grows faster than operations.

## 1 Year

Goal: prove scalable unit economics.

- Launch secure customer portal with document vault.
- Add credit data/import partner diligence.
- Add identity protection and builder partner path.
- Add state-by-state compliance matrix.
- Build attorney eligibility workflow and case packet process.
- Success target: stable monthly paid starts, churn trend understood, partner referrals producing qualified leads.
- Main risk: CAC rises if CV depends only on paid ads.

## 5 Years

Goal: national credit readiness brand.

- Own approval readiness as a category: car, home, apartment, card, loan, job.
- Build marketplace/partner APIs.
- Build AI readiness engine trained on aggregate non-sensitive behavior and workflow outcomes.
- Become known for clarity, safety, and attorney-supported escalation.
- Success target: multi-channel acquisition, high retention through build/protect/prepare, trusted partner network.
- Main risk: large fintechs copy the easy parts; CV must win on workflow depth and trust.

## 20 Years

Goal: household credit and identity operating system.

- Credit + identity vault.
- AI financial advocate with human/legal review gates.
- Embedded approval-readiness infrastructure across finance, housing, employment screening, and family credit protection.
- Brand trust becomes the moat.
- Main risk: security incident, regulatory shift, or AI commoditization.

## What To Build Next

1. Guided quiz before the form.
2. Admin filters and lead lifecycle statuses.
3. Customer portal MVP.
4. Encrypted database and auth/MFA.
5. Partner landing pages.
6. Retention sequence templates.
7. KPI dashboard using real data.

## Marketing Plan Ready

Use the current strategic intelligence plan:

- Recommended launch budget: **${money(strategy.moneyPlan.total)}**
- Launch days defined: **${strategy.launchPlan.length}**
- First action: **${strategy.launchPlan[0].action}**
- Channels: **${strategy.whoWhatWhereHow.where.join(", ")}**

## Decision

Credit Vivo is promising if it stays disciplined:

- Simple like Dovly.
- Trusted like legal-backed repair.
- Modern like fintech.
- Safer than old credit repair.
- Retention-driven beyond repair.
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({
    ok: true,
    report: OUT,
    oneYearBase: {
      leads: Math.round(oneYearBase.totalLeads),
      newPaid: Math.round(oneYearBase.totalNewPaid),
      activePaid: Math.round(oneYearBase.activePaid),
      mrr: Math.round(oneYearBase.mrr),
      arr: Math.round(oneYearBase.arr)
    }
  }, null, 2));
}

run();
