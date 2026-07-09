const operatingVersion = "cv-operating-system-v0.1.0";

const productLayers = [
  {
    id: "repair",
    name: "Repair",
    status: "mvp-live",
    customerValue: "AI intake, report-review readiness, dispute tracking, and attorney-supported eligibility routing.",
    nextBuild: "Connect secure document upload and customer authorization records."
  },
  {
    id: "build",
    name: "Build",
    status: "partner-needed",
    customerValue: "Credit builder, payment reporting, and goal-based readiness education.",
    nextBuild: "Select a compliant credit-builder or rent/utility reporting partner."
  },
  {
    id: "protect",
    name: "Protect",
    status: "partner-needed",
    customerValue: "Identity-theft response workflow, monitoring education, and future protection bundle.",
    nextBuild: "Add identity monitoring, restoration, and insurance partner terms."
  },
  {
    id: "retain",
    name: "Retain",
    status: "mvp-live",
    customerValue: "Lifecycle recommendations after repair: monitor, build, prepare, and protect.",
    nextBuild: "Automate email/SMS lifecycle only after consent and A2P campaign approval."
  }
];

const launchGates = [
  {
    id: "twilio-a2p",
    name: "Twilio A2P",
    status: "waiting",
    detail: "Individual profile is approved; A2P brand is still in review; campaign registration is locked."
  },
  {
    id: "entity-dba",
    name: "Entity and DBA records",
    status: "verify",
    detail: "Confirm legal entity, DBA usage, EIN records, and state filings before customer-facing SMS."
  },
  {
    id: "attorney-network",
    name: "Attorney network",
    status: "partner-needed",
    detail: "Finalize attorney engagement model, scope, review criteria, and customer disclosures."
  },
  {
    id: "credit-builder",
    name: "Credit builder partner",
    status: "partner-needed",
    detail: "Choose partner model before advertising tradeline, credit line, or payment-reporting benefits."
  },
  {
    id: "identity-protection",
    name: "Identity protection",
    status: "partner-needed",
    detail: "Add monitoring/restoration/insurance partner before positioning protection as a paid benefit."
  }
];

const benchmarkFindings = [
  {
    competitor: "Dovly",
    strength: "Simple mobile-first credit repair, monitoring, builder/protection bundle, and easy free entry.",
    cvCounter: "Add attorney-supported escalation and a clearer approval-readiness dashboard.",
    gap: "Credit builder and identity-protection partners are not yet live."
  },
  {
    competitor: "Lexington Law / CreditRepair.com",
    strength: "Known legal-backed credit repair model, large operations, and consumer familiarity.",
    cvCounter: "Use AI organization and dashboard clarity while keeping legal review eligibility controlled.",
    gap: "Attorney network, service scope, written terms, and state requirements still need final approval."
  },
  {
    competitor: "Credit Saint",
    strength: "Clear package names, service tiers, and reputation-focused onboarding.",
    cvCounter: "Keep pricing premium but sell credit readiness, monitoring, and support instead of broad promises.",
    gap: "Paid subscription launch must be reviewed against credit-repair advance-fee rules."
  }
];

const launchReadiness = {
  demoWaitlist: "A-",
  paidPublicLaunch: "Not ready",
  fintechProduction: "Not ready",
  reason: "The site and local engine are strong for demo/waitlist. Paid launch needs Twilio A2P approval, legal/entity/DBA verification, attorney network terms, partner-backed builder/protection products, production auth, managed encrypted storage, monitoring, and counsel-reviewed customer agreements."
};

function operatingStatus() {
  return {
    ok: true,
    operatingVersion,
    position: "Repair + Build + Protect + Retain",
    benchmark: "Dovly-style simplicity with Credit Vivo attorney-supported escalation.",
    launchReadiness,
    benchmarkFindings,
    productLayers,
    launchGates,
    nextActions: [
      "Wait for Twilio A2P brand approval, then register the campaign.",
      "Confirm BQN DBA/Credit Vivo legal positioning before live SMS copy.",
      "Build secure customer portal upload and authorization flow.",
      "Shortlist credit-builder and identity-protection partners.",
      "Keep public claims focused on review, organization, monitoring, and eligibility."
    ]
  };
}

module.exports = { operatingStatus, productLayers, launchGates };
