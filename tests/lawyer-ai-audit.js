const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const OUT = path.join(ROOT, "LAWYER_AI_AUDIT_REPORT.md");

const filesToAudit = [
  "index.html",
  "admin.html",
  "script.js",
  "server.js",
  "src/app.js",
  "src/lead-engine.js",
  "src/growth-engine.js",
  "src/strategic-intelligence.js",
  "PRODUCTION.md",
  "ARCHITECTURE.md"
];

const rules = [
  {
    id: "CROA-GUARANTEE-SCORE",
    severity: "blocker",
    pattern: /\bguarantee(?:d|s)?\b.{0,60}\b(score|increase|approval|deletion|remove|removal)\b/i,
    why: "Credit repair materials should not promise guaranteed score increases, approvals, removals, deletions, or timelines.",
    fix: "Use 'designed to help review, organize, track, and address possible inaccurate or unverifiable information.'"
  },
  {
    id: "CROA-REMOVE-ACCURATE",
    severity: "blocker",
    pattern: /\b(remove|delete|erase)\b.{0,60}\b(accurate|valid|legitimate)\b/i,
    why: "Do not imply accurate negative information can be removed.",
    fix: "Limit disputes to possible inaccurate, unverifiable, outdated, incomplete, duplicate, mixed-file, or fraud-related items."
  },
  {
    id: "LEGAL-AUTO-REPRESENTATION",
    severity: "high",
    pattern: /\b(our attorneys|your attorney|lawyer will|attorney will)\b/i,
    why: "Attorney language can imply legal representation or guaranteed legal action.",
    fix: "Use 'attorney-supported review may be available for eligible unresolved issues.'"
  },
  {
    id: "BILLING-ADVANCE-FEE",
    severity: "high",
    pattern: /\b(pay now|start today for|first payment|setup fee|initial working fee)\b/i,
    why: "Credit repair services have advance-fee and billing-timing risk under CROA/TSR fact patterns.",
    fix: "Separate membership tools from credit repair services and require counsel-reviewed billing flow."
  },
  {
    id: "SENSITIVE-DATA-COLLECTION",
    severity: "high",
    pattern: /\b(SSN|social security|bureau login|credit report upload|full account number|date of birth|driver.?s license)\b/i,
    why: "Sensitive-data collection requires secure authenticated portal, retention controls, and safeguards.",
    fix: "Keep public intake low-risk; collect sensitive data only in a secure portal."
  },
  {
    id: "AI-OVERCLAIM",
    severity: "medium",
    pattern: /\b(AI|engine)\b.{0,80}\b(fix|repair|remove|force|guarantee|automatic disputes)\b/i,
    why: "AI claims should not imply autonomous legal/credit repair action without review.",
    fix: "Frame AI as review, organization, explanation, and routing support."
  },
  {
    id: "ADS-AUTO-SPEND",
    severity: "medium",
    pattern: /\b(auto(?:mate|mated|matically).{0,80}(spend|ads|publish|post)|run ads to all)\b/i,
    why: "Ad spend and external posting should be approval-gated with budget caps and compliance-reviewed copy.",
    fix: "Keep campaign planning/simulation separate from real ad execution."
  }
];

const safeContextPatterns = [
  /\b(do not|does not|don't|cannot|can't|must not|should not|avoid|blocked|unbounded|without approval|require approval|not legal advice|not replace|no guaranteed)\b/i,
  /\b(required signal|warning|safety|guardrail|risk|gap|before real customer data)\b/i
];

const requiredPositiveSignals = [
  {
    id: "PUBLIC-SENSITIVE-DATA-WARNING",
    file: "index.html",
    text: "Do not enter your Social Security number",
    severity: "medium",
    why: "Public lead capture should warn users not to submit sensitive data."
  },
  {
    id: "ADMIN-PROTECTED",
    file: "src/app.js",
    text: "Admin access required",
    severity: "high",
    why: "Admin APIs must be protected."
  },
  {
    id: "SECURITY-HEADERS",
    file: "src/http.js",
    text: "Content-Security-Policy",
    severity: "medium",
    why: "Security headers are part of baseline web hardening."
  },
  {
    id: "SELF-MODIFY-DISABLED",
    file: "src/lead-engine.js",
    text: "allowSelfModify",
    severity: "medium",
    why: "Fintech automation should not self-modify without approval and version control."
  },
  {
    id: "PRODUCTION-DATABASE-GAP-DOCUMENTED",
    file: "PRODUCTION.md",
    text: "encrypted managed database",
    severity: "high",
    why: "Local JSON storage must be replaced before real customer data."
  }
];

function read(file) {
  const absolute = path.join(ROOT, file);
  return fs.existsSync(absolute) ? fs.readFileSync(absolute, "utf8") : "";
}

function lineFor(content, index) {
  return content.slice(0, index).split(/\r?\n/).length;
}

function lineTextFor(content, index) {
  const before = content.lastIndexOf("\n", index);
  const after = content.indexOf("\n", index);
  const start = before === -1 ? 0 : before + 1;
  const end = after === -1 ? content.length : after;
  return content.slice(start, end);
}

function isSafeContext(content, index) {
  const lines = content.split(/\r?\n/);
  const lineNumber = lineFor(content, index);
  const context = lines.slice(Math.max(0, lineNumber - 3), Math.min(lines.length, lineNumber + 2)).join(" ");
  return safeContextPatterns.some((pattern) => pattern.test(context));
}

function auditFile(file) {
  const content = read(file);
  const findings = [];
  for (const rule of rules) {
    const match = rule.pattern.exec(content);
    if (match && !isSafeContext(content, match.index)) {
      findings.push({
        id: rule.id,
        severity: rule.severity,
        file,
        line: lineFor(content, match.index),
        snippet: match[0].replace(/\s+/g, " ").slice(0, 160),
        why: rule.why,
        fix: rule.fix
      });
    }
  }
  return findings;
}

function positiveSignalFindings() {
  return requiredPositiveSignals
    .filter((signal) => !read(signal.file).includes(signal.text))
    .map((signal) => ({
      id: signal.id,
      severity: signal.severity,
      file: signal.file,
      line: 1,
      snippet: `Missing required signal: ${signal.text}`,
      why: signal.why,
      fix: "Add or restore this control before production."
    }));
}

function severityRank(severity) {
  return { blocker: 4, high: 3, medium: 2, low: 1 }[severity] || 0;
}

function recommendation(findings) {
  if (findings.some((finding) => finding.severity === "blocker")) return "BLOCK";
  if (findings.some((finding) => finding.severity === "high")) return "REVISE";
  if (findings.some((finding) => finding.severity === "medium")) return "REVIEW";
  return "PASS";
}

function table(rows, headers) {
  return `| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows
    .map((row) => `| ${row.map((cell) => String(cell).replace(/\|/g, "\\|")).join(" | ")} |`)
    .join("\n")}`;
}

function run() {
  const findings = filesToAudit.flatMap(auditFile).concat(positiveSignalFindings());
  findings.sort((a, b) => severityRank(b.severity) - severityRank(a.severity));

  const bySeverity = findings.reduce((acc, finding) => {
    acc[finding.severity] = (acc[finding.severity] || 0) + 1;
    return acc;
  }, {});

  const report = `# Credit Vivo Lawyer AI Audit Report

## Important Notice

This is an AI-assisted legal/compliance and product-risk audit. It is **not legal advice** and does not replace a licensed attorney. Credit Vivo should have qualified counsel review CROA, FCRA, TSR, state credit repair laws, attorney-network structure, contracts, pricing, ads, testimonials, privacy, and data-security obligations before launch.

## Result

- Recommendation: **${recommendation(findings)}**
- Findings: **${findings.length}**
- Blockers: **${bySeverity.blocker || 0}**
- High: **${bySeverity.high || 0}**
- Medium: **${bySeverity.medium || 0}**
- Low: **${bySeverity.low || 0}**

## Findings

${findings.length
  ? table(
      findings.map((finding) => [
        finding.severity,
        finding.id,
        `${finding.file}:${finding.line}`,
        finding.snippet,
        finding.fix
      ]),
      ["Severity", "Rule", "Location", "Snippet", "Fix"]
    )
  : "No automated findings found."}

## Business + Legal Review Areas

1. **CROA/credit repair:** no advance-fee risk, written contract, cancellation rights, truthful services.
2. **FCRA:** dispute workflows must be fact-supported; no false identity-theft or dispute claims.
3. **Attorney network:** avoid implying representation until an attorney-client relationship exists.
4. **Advertising:** no guaranteed approvals, score increases, removals, or timelines.
5. **Pricing:** separate software/education/monitoring membership from repair services with counsel-reviewed billing.
6. **Privacy/security:** replace local JSON with encrypted managed database before real customer data.
7. **AI governance:** AI may organize/explain/recommend; legal/credit actions need human approval and audit trails.
8. **State law:** credit repair licensing/bonding/registration varies by state and must be checked before national launch.

## Official Sources Checked

- FTC Credit Repair Organizations Act: https://www.ftc.gov/legal-library/browse/statutes/credit-repair-organizations-act
- CFPB Lexington Law / CreditRepair.com enforcement: https://www.consumerfinance.gov/enforcement/payments-harmed-consumers/payments-by-case/lexlaw/
- FTC Safeguards Rule: https://www.ftc.gov/legal-library/browse/rules/safeguards-rule
- FTC FCRA: https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act
- CFPB credit report dispute guidance: https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/

## Counsel Handoff

Ask counsel to review:

- Website and pricing copy.
- Intake form and sensitive-data warning.
- Subscription/payment timing.
- Legal+ and attorney-supported review language.
- Customer agreement, cancellation, privacy, terms, and disclosures.
- State-by-state launch map.
- Vendor contracts for credit data, identity protection, builder tools, payments, CRM, and attorneys.
`;

  fs.writeFileSync(OUT, report);
  console.log(JSON.stringify({ ok: recommendation(findings) !== "BLOCK", recommendation: recommendation(findings), findings: findings.length, report: OUT }, null, 2));
  if (recommendation(findings) === "BLOCK") process.exitCode = 1;
}

run();
