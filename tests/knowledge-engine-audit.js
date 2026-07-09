const fs = require("fs");
const path = require("path");
const {
  knowledgeMaterials,
  knowledgeSummary,
  sources,
  complianceMaterials,
  technologyStack,
  innovationRoadmap,
  installPlan
} = require("../src/knowledge-engine");

const OUT = path.join(__dirname, "..", "KNOWLEDGE_ENGINE_REPORT.md");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function source(id) {
  return sources.find((item) => item.id === id);
}

function run() {
  const materials = knowledgeMaterials();
  const summary = knowledgeSummary();

  assert(materials.ok === true, "materials ok");
  assert(summary.ok === true, "summary ok");
  assert(summary.sourceCount >= 8, "source coverage");
  assert(source("ftc-croa"), "CROA source");
  assert(source("ftc-safeguards"), "Safeguards source");
  assert(source("cfpb-1033"), "CFPB 1033 source");
  assert(source("nist-ai-rmf"), "NIST AI RMF source");
  assert(source("owasp-top-10"), "OWASP Top 10 source");
  assert(source("owasp-asvs"), "OWASP ASVS source");
  assert(complianceMaterials.some((item) => item.area === "Credit repair claims"), "credit repair claims gate");
  assert(complianceMaterials.some((item) => item.area === "Sensitive data handling"), "sensitive data gate");
  assert(technologyStack.some((item) => item.layer === "Identity and access"), "auth layer");
  assert(technologyStack.some((item) => item.layer === "AI governance"), "AI governance layer");
  assert(innovationRoadmap.some((item) => item.name === "Evidence-bound AI dispute assistant"), "evidence-bound AI");
  assert(installPlan[0].item === "Production auth + roles", "first priority auth");

  const report = `# Credit Vivo Knowledge Engine Report

## Result

- Status: **PASS**
- Knowledge version: **${materials.knowledgeVersion}**
- Last reviewed: **${materials.lastReviewed}**
- Sources installed: **${sources.length}**
- Compliance gates: **${complianceMaterials.length}**
- Technology layers: **${technologyStack.length}**
- Innovation tracks: **${innovationRoadmap.length}**

## Installed Materials

### Compliance

${complianceMaterials.map((item) => `- **${item.area}:** ${item.engineRule}`).join("\n")}

### Technology

${technologyStack.map((item) => `- **${item.layer}:** ${item.needNow}`).join("\n")}

### Innovation

${innovationRoadmap.map((item) => `- **${item.name}:** ${item.value}`).join("\n")}

## Official / Standards Sources

${sources.map((item) => `- [${item.name}](${item.url}) - ${item.engineUse}`).join("\n")}

## Next Build Priorities

${installPlan.map((item) => `${item.priority}. **${item.item}:** ${item.acceptance}`).join("\n")}

## Notice

${materials.notice}
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({ ok: true, report: OUT, checks: 12 }, null, 2));
}

try {
  run();
} catch (error) {
  console.error(error);
  process.exit(1);
}
