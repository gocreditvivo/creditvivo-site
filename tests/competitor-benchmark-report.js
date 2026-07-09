const fs = require("fs");
const path = require("path");
const { strategicPlan } = require("../src/strategic-intelligence");

const OUT = path.join(__dirname, "..", "COMPETITOR_BENCHMARK_SCORECARD.md");

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows.map((row) => `| ${row.map(String).join(" | ")} |`).join("\n")}`;
}

function scoreCompetitor(name) {
  const scores = {
    Dovly: [9, 8, 6, 8, 7],
    "Lexington Law": [6, 7, 9, 6, 6],
    "Credit Saint": [7, 7, 6, 5, 6],
    "Credit Karma / marketplaces": [10, 9, 4, 9, 8],
    "Self / Kikoff / builder apps": [8, 8, 4, 7, 7],
    "Credit Vivo target": [8, 9, 8, 8, 9]
  };
  return scores[name] || [5, 5, 5, 5, 5];
}

function run() {
  const plan = strategicPlan({ mode: "serious30Day", days: 14 });
  const rows = [...plan.competitors.map((item) => item.name), "Credit Vivo target"].map((name) => {
    const [distribution, product, trust, retention, innovation] = scoreCompetitor(name);
    const total = distribution + product + trust + retention + innovation;
    return [name, distribution, product, trust, retention, innovation, total];
  });

  const report = `# Credit Vivo Competitor Benchmark Scorecard

## Scorecard

${table(rows, ["Company", "Distribution", "Product", "Trust", "Retention", "Innovation", "Total / 50"])}

## Reading

- Dovly is strongest in simplicity and free-first acquisition.
- Lexington Law is strongest in legal authority, but the category has regulatory baggage.
- Credit Saint is strongest in package clarity.
- Credit Karma/marketplaces have distribution, but not deep repair/legal workflow.
- Builder apps solve one problem, not the full repair/build/protect/prepare journey.
- Credit Vivo's target edge is a hybrid: simple app + premium fintech trust + attorney-supported escalation.

## CV Must Win On

1. Guided customer path.
2. Approval-readiness positioning.
3. Security and compliance trust.
4. Retention after repair.
5. Attorney-supported escalation without risky promises.
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({ ok: true, report: OUT, competitors: rows.length }, null, 2));
}

run();
