const fs = require("fs");
const path = require("path");
const { withTestServer } = require("./lib/test-server");

const OUT = path.join(__dirname, "..", "WEB_QUALITY_AUDIT.md");

function assert(condition, message, failures) {
  if (!condition) failures.push(message);
}

function count(pattern, text) {
  return (text.match(pattern) || []).length;
}

async function run() {
  await withTestServer(8914, async ({ baseUrl }) => {
    const response = await fetch(`${baseUrl}/`);
    const html = await response.text();
    const failures = [];
    const warnings = [];

    assert(response.status === 200, "Home page should return 200.", failures);
    assert(html.includes("<title>Credit Vivo"), "Missing Credit Vivo title.", failures);
    assert(html.includes('name="description"'), "Missing meta description.", failures);
    assert(html.includes("AI Precision. Attorney Authority."), "Missing core slogan.", failures);
    assert(html.includes('id="leadForm"'), "Missing lead form.", failures);
    assert(html.includes("Do not enter your Social Security number"), "Missing sensitive-data warning.", failures);
    assert(html.includes("Plus - $59/mo"), "Missing Plus plan interest option.", failures);
    assert(html.includes("Pro - $99/mo"), "Missing Pro plan interest option.", failures);

    const rejected = [
      "No guarantees. Just a clearer path.",
      "Results vary. Credit Vivo does not guarantee",
      "guaranteed score",
      "guaranteed deletion",
      "guaranteed approval"
    ].filter((phrase) => html.toLowerCase().includes(phrase.toLowerCase()));
    assert(rejected.length === 0, `Rejected/risky phrases found: ${rejected.join(", ")}`, failures);

    const labelCount = count(/<label\b/g, html);
    const inputCount = count(/<(input|select|textarea)\b/g, html);
    assert(labelCount >= 8, "Expected labels for lead form fields.", failures);
    if (inputCount > labelCount + 1) warnings.push("Some hidden/spam-trap inputs may not have visible labels.");

    const navLinks = ["#how", "#customers", "#tools", "#plans", "#start"];
    for (const link of navLinks) assert(html.includes(`href="${link}"`), `Missing nav/CTA link ${link}.`, failures);

    const report = `# Credit Vivo Web Quality Audit

## Result

- Status: **${failures.length ? "FAIL" : "PASS"}**
- Failures: **${failures.length}**
- Warnings: **${warnings.length}**

## Checks

- Home page returns 200
- Title and meta description
- Core slogan
- Lead form
- Sensitive-data warning
- Pricing options
- No rejected guarantee language
- Basic label/form coverage
- Key internal links

## Failures

${failures.length ? failures.map((item) => `- ${item}`).join("\n") : "- None"}

## Warnings

${warnings.length ? warnings.map((item) => `- ${item}`).join("\n") : "- None"}
`;

    fs.writeFileSync(OUT, report);
    console.log(JSON.stringify({ ok: failures.length === 0, failures: failures.length, warnings: warnings.length, report: OUT }, null, 2));
    if (failures.length) process.exitCode = 1;
  });
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
