const intelligenceVersion = "cv-strategic-intelligence-v0.1.0";

const competitors = [
  {
    name: "Dovly",
    model: "AI-guided app, free-first, build/monitor/protect",
    strength: "simple onboarding and low-cost acquisition",
    weakness: "less attorney authority and less premium trust signal",
    cvCounter: "match simplicity, add attorney-supported escalation and approval readiness"
  },
  {
    name: "Lexington Law",
    model: "law-firm backed credit repair",
    strength: "legal authority and category awareness",
    weakness: "regulatory baggage in credit repair category and premium old-school feel",
    cvCounter: "use legal authority carefully with transparent, app-based workflows"
  },
  {
    name: "Credit Saint",
    model: "tiered traditional credit repair",
    strength: "clear packages and consumer comparison appeal",
    weakness: "less modern AI/customer portal positioning",
    cvCounter: "keep pricing clarity, make product feel more fintech and retention-driven"
  },
  {
    name: "Credit Karma / marketplaces",
    model: "free credit data and financial offers",
    strength: "massive distribution and free utility",
    weakness: "ad/offer marketplace, not deep repair workflow",
    cvCounter: "own guided credit readiness and escalation workflow"
  },
  {
    name: "Self / Kikoff / builder apps",
    model: "credit builder products",
    strength: "clear builder utility",
    weakness: "not full repair/protect/legal readiness",
    cvCounter: "bundle builder lane into broader repair/protect/prepare system"
  }
];

const macroScenarios = [
  {
    name: "Soft landing",
    trigger: "stable unemployment, easing inflation, steady approvals",
    businessAction: "scale SEO, partner referrals, and Plus plan activation",
    budgetBias: "growth",
    customerMessage: "prepare before your next approval"
  },
  {
    name: "Credit tightening",
    trigger: "higher denial rates, tighter underwriting, higher delinquency",
    businessAction: "shift spend to approval-readiness and denial-recovery funnels",
    budgetBias: "efficiency",
    customerMessage: "know your credit path before applying again"
  },
  {
    name: "Recession stress",
    trigger: "rising unemployment, rising collections, lower consumer confidence",
    businessAction: "protect cash, focus on low-CAC SEO/partners, expand hardship education",
    budgetBias: "defensive",
    customerMessage: "organize, protect, and plan your next step"
  },
  {
    name: "automation/regulatory reset",
    trigger: "new automation, privacy, credit repair, or marketing enforcement",
    businessAction: "slow automation, raise compliance review, update disclosures and audit logs",
    budgetBias: "compliance",
    customerMessage: "transparent tools with human review where needed"
  }
];

const launchBudgets = {
  lean14Day: {
    name: "Lean 14-day launch",
    total: 18500,
    lineItems: {
      legalComplianceReview: 3500,
      brandLandingCopyQA: 1500,
      productionHostingAuthDatabase: 2500,
      CRMEmailSMSSetup: 1800,
      analyticsTracking: 900,
      creativeAssets: 1800,
      paidSearchTest: 3000,
      paidSocialRetargetingTest: 1500,
      localPartnerOutreach: 1200,
      contingency: 2800
    }
  },
  serious30Day: {
    name: "Serious 30-day launch",
    total: 63500,
    lineItems: {
      legalComplianceStateReview: 10000,
      productionAppAuthDatabaseSecurity: 12000,
      CRMMarketingAutomation: 5000,
      analyticsCallTrackingAttribution: 3500,
      brandDesignCreative: 5000,
      googleSearch: 12000,
      metaTikTokRetargeting: 6000,
      youtubeEducation: 3000,
      partnerDevelopment: 3500,
      supportOperations: 2500,
      contingency: 10000
    }
  },
  investor90Day: {
    name: "Investor-grade 90-day launch",
    total: 245000,
    lineItems: {
      legalComplianceAndContracts: 35000,
      productionEngineeringSecurity: 55000,
      customerPortalMVP: 30000,
      dataVendorsAndIdentityBuilderDueDiligence: 20000,
      CRMAnalyticsDataWarehouse: 15000,
      creativeVideoLandingPages: 18000,
      paidMediaTesting: 45000,
      partnerSales: 12000,
      supportOpsQA: 10000,
      contingency: 5000
    }
  }
};

function horizonPlan() {
  return [
    {
      horizon: "5 years",
      goal: "Become a trusted national credit readiness platform.",
      milestones: ["production portal", "credit data integration", "builder/protection partners", "attorney eligibility network", "SEO and partner channels"],
      risks: ["compliance enforcement", "CAC inflation", "privacy trust"],
      moat: "workflow data, partner distribution, trust, and customer lifecycle"
    },
    {
      horizon: "10 years",
      goal: "Own approval-readiness infrastructure across consumer finance.",
      milestones: ["multi-product marketplace", "embedded partner APIs", "predictive readiness scoring", "enterprise compliance controls"],
      risks: ["large fintech/bureau competition", "AI commoditization"],
      moat: "approval readiness graph and regulated workflow trust"
    },
    {
      horizon: "15 years",
      goal: "Operate as a household credit operating system.",
      milestones: ["family credit protection", "life-event planning", "employment/housing/credit readiness", "bank and employer partnerships"],
      risks: ["macro credit cycles", "data rights shifts"],
      moat: "brand trust and long-term consumer relationship"
    },
    {
      horizon: "20 years",
      goal: "Become default personal credit and identity infrastructure for everyday consumers.",
      milestones: ["AI financial advocate", "identity/credit vault", "regulated partner ecosystem", "international expansion if lawful"],
      risks: ["regulation, platform consolidation, security incidents"],
      moat: "trust, compliance, data portability, and human-reviewed AI"
    }
  ];
}

function dayLaunchPlan(days = 14) {
  const plan = [
    { day: 1, owner: "Founder + compliance counsel", action: "Lock offer, claims, pricing, and Legal+ language.", cost: 1000 },
    { day: 2, owner: "Engineer", action: "Move MVP to production host with auth/database plan.", cost: 1500 },
    { day: 3, owner: "Designer/copy", action: "Create auto, mortgage, apartment, identity theft landing variants.", cost: 1200 },
    { day: 4, owner: "Growth", action: "Set analytics, call tracking, source tracking, CRM stages.", cost: 900 },
    { day: 5, owner: "Compliance", action: "Review ads, pages, intake, pricing, disclaimers, consent.", cost: 1500 },
    { day: 6, owner: "Creative", action: "Create 10 static ads and 5 short video scripts.", cost: 1200 },
    { day: 7, owner: "Partnerships", action: "Build list of 100 auto dealers, loan officers, realtors, rental agents.", cost: 500 },
    { day: 8, owner: "Growth", action: "Launch approval-gated Google Search test.", cost: 750 },
    { day: 9, owner: "Growth", action: "Launch retargeting test only to site visitors.", cost: 400 },
    { day: 10, owner: "Founder", action: "Begin partner outreach and follow-up cadence.", cost: 300 },
    { day: 11, owner: "Support", action: "Set lead response scripts and booking workflow.", cost: 600 },
    { day: 12, owner: "Engineer", action: "Add admin filters and lead status lifecycle.", cost: 1200 },
    { day: 13, owner: "Growth", action: "Review CPL, booked rate, plan interest, complaint signals.", cost: 0 },
    { day: 14, owner: "Founder", action: "Decide scale, pause, or revise by channel.", cost: 0 }
  ];
  return plan.slice(0, Math.min(days, plan.length));
}

function moneyPlan(mode = "serious30Day") {
  return launchBudgets[mode] || launchBudgets.serious30Day;
}

function strategicPlan({ mode = "serious30Day", days = 14 } = {}) {
  return {
    ok: true,
    intelligenceVersion,
    operatingPrinciple: "Track everything, generate recommendations, require approval for spend/external actions.",
    competitors,
    macroScenarios,
    horizons: horizonPlan(),
    launchPlan: dayLaunchPlan(days),
    moneyPlan: moneyPlan(mode),
    whoWhatWhereHow: {
      who: ["Founder/operator", "compliance counsel", "engineer", "growth marketer", "support lead", "partner salesperson"],
      what: ["production secure portal", "approved offer", "lead funnel", "CRM", "analytics", "ad tests", "partner outreach"],
      where: ["Google Search", "SEO pages", "retargeting", "YouTube education", "auto/mortgage/rental partner channels"],
      how: ["approval-gated campaigns", "daily KPI review", "compliance-reviewed copy", "customer lifecycle automation", "partner distribution"]
    },
    trackedKpis: [
      "visitors",
      "form starts",
      "lead completions",
      "cost per lead",
      "booked-call rate",
      "show rate",
      "Plus interest",
      "Pro interest",
      "Legal+ eligibility",
      "activation rate",
      "retention",
      "complaints",
      "refund/cancel reasons"
    ]
  };
}

module.exports = { strategicPlan, competitors, macroScenarios, launchBudgets, intelligenceVersion };
