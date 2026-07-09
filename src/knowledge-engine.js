const knowledgeVersion = "cv-knowledge-engine-v0.1.0";
const lastReviewed = "2026-07-07";

const sources = [
  {
    id: "ftc-croa",
    name: "FTC Credit Repair Organizations Act",
    category: "credit-repair-compliance",
    url: "https://www.ftc.gov/legal-library/browse/statutes/credit-repair-organizations-act",
    engineUse: "Claims, pricing, contracts, cancellation, and credit-repair service boundaries."
  },
  {
    id: "ftc-safeguards",
    name: "FTC Safeguards Rule",
    category: "security",
    url: "https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know",
    engineUse: "Information-security program, vendor oversight, access controls, encryption, monitoring, and incident response."
  },
  {
    id: "ftc-frca",
    name: "FTC Fair Credit Reporting Act",
    category: "credit-reporting",
    url: "https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act",
    engineUse: "Dispute workflows, consumer report handling, permissible use, and furnisher/bureau process design."
  },
  {
    id: "cfpb-dispute",
    name: "CFPB Credit Report Dispute Guidance",
    category: "consumer-workflow",
    url: "https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/",
    engineUse: "Customer education, dispute steps, evidence gathering, and bureau routing."
  },
  {
    id: "cfpb-1033",
    name: "CFPB Personal Financial Data Rights",
    category: "open-banking",
    url: "https://www.consumerfinance.gov/personal-financial-data-rights/",
    engineUse: "Future consumer-authorized data access, data portability, third-party access, and privacy-by-design."
  },
  {
    id: "nist-ai-rmf",
    name: "NIST AI Risk Management Framework",
    category: "ai-governance",
    url: "https://www.nist.gov/itl/ai-risk-management-framework",
    engineUse: "AI governance, map/measure/manage controls, human oversight, bias, privacy, and auditability."
  },
  {
    id: "owasp-top-10",
    name: "OWASP Top 10",
    category: "application-security",
    url: "https://owasp.org/www-project-top-ten/",
    engineUse: "Web security priorities, access control, injection, auth, logging, and secure design."
  },
  {
    id: "owasp-asvs",
    name: "OWASP Application Security Verification Standard",
    category: "application-security",
    url: "https://owasp.org/www-project-application-security-verification-standard/",
    engineUse: "Security acceptance criteria for production web application controls."
  }
];

const complianceMaterials = [
  {
    area: "Credit repair claims",
    status: "required-before-scale",
    engineRule: "Block guaranteed score, deletion, approval, and timeline language.",
    owner: "Compliance counsel + marketing",
    sourceIds: ["ftc-croa"]
  },
  {
    area: "Customer contract and cancellation",
    status: "required-before-paid-repair",
    engineRule: "Do not launch paid credit-repair services without counsel-approved contract, scope, cancellation, and billing timing.",
    owner: "Compliance counsel",
    sourceIds: ["ftc-croa"]
  },
  {
    area: "Dispute evidence",
    status: "required-before-disputes",
    engineRule: "Only generate fact-supported workflows for inaccurate, incomplete, outdated, unverifiable, duplicate, mixed-file, or fraud-related items.",
    owner: "Operations + attorney network",
    sourceIds: ["ftc-frca", "cfpb-dispute"]
  },
  {
    area: "Attorney network language",
    status: "required-before-legal-plus",
    engineRule: "Use eligibility/review language until representation is confirmed by a licensed attorney.",
    owner: "Legal operations",
    sourceIds: ["ftc-croa"]
  },
  {
    area: "Sensitive data handling",
    status: "required-before-real-customers",
    engineRule: "Public forms must not collect SSNs, full DOB, bureau credentials, full account numbers, IDs, signatures, or report uploads.",
    owner: "Security + engineering",
    sourceIds: ["ftc-safeguards"]
  },
  {
    area: "State launch map",
    status: "required-before-national-launch",
    engineRule: "Gate launch by state-specific credit repair licensing, bonding, registration, fee, and telemarketing requirements.",
    owner: "Compliance counsel",
    sourceIds: ["ftc-croa"]
  }
];

const technologyStack = [
  {
    layer: "Identity and access",
    needNow: "Admin/customer auth with MFA, role-based access, secure sessions, and account recovery.",
    productionCandidate: "OIDC provider such as Clerk, Auth0, Descope, or managed enterprise auth.",
    why: "Credit and identity workflows are sensitive; admin token is acceptable only for local MVP."
  },
  {
    layer: "Data platform",
    needNow: "Encrypted managed database, separate PII tables, field-level encryption for high-risk fields, backups, retention rules.",
    productionCandidate: "Postgres with managed encryption, audit tables, and least-privilege service roles.",
    why: "Local JSON cannot handle regulated customer records, reporting, or audit needs."
  },
  {
    layer: "Document vault",
    needNow: "Private object storage, malware scanning, signed URLs, document classification, and deletion workflows.",
    productionCandidate: "Encrypted object storage with KMS, AV scanning queue, and short-lived access links.",
    why: "Credit reports, IDs, dispute evidence, and identity-theft proof need strict controls."
  },
  {
    layer: "Workflow engine",
    needNow: "State machine for intake, evidence review, dispute prep, attorney eligibility, bureau response, and customer updates.",
    productionCandidate: "Queue-backed workflow runner with immutable status history.",
    why: "Credit repair operations fail when tasks are hidden in inboxes or manual spreadsheets."
  },
  {
    layer: "AI governance",
    needNow: "Prompt/version registry, output review, risk scoring, refusal rules, evidence binding, and audit logs.",
    productionCandidate: "AI gateway/provider abstraction with evals, human approval, and red-team test suites.",
    why: "AI should assist review and routing; it must not make unsupported legal or credit claims."
  },
  {
    layer: "Observability and security",
    needNow: "Central logs, security events, rate limits, anomaly detection, backups, and incident runbooks.",
    productionCandidate: "SIEM/log drain, WAF, vulnerability scanner, alerting, and tested incident response.",
    why: "Trust depends on early detection and controlled response."
  },
  {
    layer: "Data integrations",
    needNow: "Vendor due diligence for credit data, identity protection, credit builder, payments, CRM, email/SMS.",
    productionCandidate: "Consent-based APIs, data minimization, vendor risk register, and contract review.",
    why: "Third-party integrations become compliance and security obligations."
  }
];

const innovationRoadmap = [
  {
    name: "Credit readiness graph",
    horizon: "0-6 months",
    value: "Turns score range, goals, documents, disputes, and plan history into clear next-best actions.",
    guardrail: "No approval guarantees; recommendations must be explainable."
  },
  {
    name: "Evidence-bound AI dispute assistant",
    horizon: "3-9 months",
    value: "Drafts issue summaries only from uploaded evidence and report facts.",
    guardrail: "Human approval and audit trail required before any customer or bureau communication."
  },
  {
    name: "Attorney eligibility router",
    horizon: "3-9 months",
    value: "Identifies unresolved, documented, eligible issues for attorney-supported review.",
    guardrail: "No attorney-client relationship implied until counsel confirms representation."
  },
  {
    name: "Open banking readiness signals",
    horizon: "6-18 months",
    value: "Uses consumer-authorized financial data to help customers prepare for auto, mortgage, and loan readiness.",
    guardrail: "Use consent, minimization, revocation, and source-specific data-use controls."
  },
  {
    name: "Retention AI coach",
    horizon: "0-6 months",
    value: "Keeps customers engaged after repair with protect, build, prepare, and monitor journeys.",
    guardrail: "Marketing messages need consent, frequency caps, and compliance-reviewed templates."
  },
  {
    name: "Compliance autopilot",
    horizon: "6-12 months",
    value: "Scans copy, scripts, workflows, and backend flags before release.",
    guardrail: "Advisory only; counsel remains final authority for legal interpretation."
  }
];

const installPlan = [
  {
    priority: 1,
    item: "Production auth + roles",
    action: "Replace single admin token with MFA auth, roles, and separate customer/admin surfaces.",
    acceptance: "Every admin route has role checks, session expiry, and audit logging."
  },
  {
    priority: 2,
    item: "Encrypted data model",
    action: "Move leads and future customer files from local JSON to encrypted database and object vault.",
    acceptance: "PII is encrypted, access is logged, backups exist, and public web cannot read stored data."
  },
  {
    priority: 3,
    item: "Compliance release gate",
    action: "Run lawyer AI audit, web quality, security baseline, smoke, and benchmark tests before launch.",
    acceptance: "A release blocks on blocker/high compliance findings or failed security checks."
  },
  {
    priority: 4,
    item: "Workflow engine",
    action: "Add customer lifecycle states, task queues, evidence checklist, response tracking, and operator notes.",
    acceptance: "Every customer has visible status, next action, owner, and event history."
  },
  {
    priority: 5,
    item: "AI evidence controls",
    action: "Bind AI recommendations to customer-provided facts, documents, and report items.",
    acceptance: "Every AI output shows source evidence, confidence, reviewer, and approval status."
  }
];

function knowledgeMaterials() {
  return {
    ok: true,
    knowledgeVersion,
    lastReviewed,
    notice: "AI-assisted research and compliance planning. This is not legal advice; counsel must approve legal, pricing, contract, and launch decisions.",
    sources,
    complianceMaterials,
    technologyStack,
    innovationRoadmap,
    installPlan
  };
}

function knowledgeSummary() {
  return {
    ok: true,
    knowledgeVersion,
    lastReviewed,
    sourceCount: sources.length,
    complianceMaterialCount: complianceMaterials.length,
    technologyLayerCount: technologyStack.length,
    innovationCount: innovationRoadmap.length,
    topPriorities: installPlan.slice(0, 3).map((item) => item.item)
  };
}

module.exports = {
  knowledgeVersion,
  knowledgeMaterials,
  knowledgeSummary,
  sources,
  complianceMaterials,
  technologyStack,
  innovationRoadmap,
  installPlan
};
