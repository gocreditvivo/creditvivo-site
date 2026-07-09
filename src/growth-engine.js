const { engine } = require("./config");

const growthVersion = "cv-growth-retention-v0.1.0";

const channels = [
  {
    id: "google-search",
    name: "Google Search",
    intent: "high",
    bestFor: ["Auto approval", "Mortgage readiness", "Apartment approval", "Identity theft help"],
    approvalRequired: true
  },
  {
    id: "meta-retargeting",
    name: "Meta Retargeting",
    intent: "medium",
    bestFor: ["General credit clarity", "Credit card or loan"],
    approvalRequired: true
  },
  {
    id: "tiktok-education",
    name: "TikTok Education",
    intent: "discovery",
    bestFor: ["General credit clarity", "Auto approval", "Apartment approval"],
    approvalRequired: true
  },
  {
    id: "youtube-explainers",
    name: "YouTube Explainers",
    intent: "education",
    bestFor: ["Mortgage readiness", "Identity theft help", "General credit clarity"],
    approvalRequired: true
  },
  {
    id: "partner-referrals",
    name: "Partner Referrals",
    intent: "high",
    bestFor: ["Auto approval", "Mortgage readiness", "Apartment approval"],
    approvalRequired: true
  },
  {
    id: "seo-local-pages",
    name: "SEO Local Pages",
    intent: "compounding",
    bestFor: ["Auto approval", "Mortgage readiness", "Apartment approval", "General credit clarity"],
    approvalRequired: false
  },
  {
    id: "email-lifecycle",
    name: "Email Lifecycle",
    intent: "retention",
    bestFor: ["Auto approval", "Mortgage readiness", "Apartment approval", "Credit card or loan", "Identity theft help", "General credit clarity"],
    approvalRequired: false
  }
];

const compliantAngles = {
  "Auto approval": {
    headline: "Get credit-ready before the dealer.",
    offer: "Start with a free credit path review.",
    landingPage: "/#start"
  },
  "Mortgage readiness": {
    headline: "Prepare your credit before the mortgage review.",
    offer: "See your next best credit-readiness steps.",
    landingPage: "/#start"
  },
  "Apartment approval": {
    headline: "Know what may affect rental approval.",
    offer: "Start with a simple credit path review.",
    landingPage: "/#start"
  },
  "Credit card or loan": {
    headline: "Build toward stronger credit options.",
    offer: "Review, build, track, and protect your path.",
    landingPage: "/#start"
  },
  "Identity theft help": {
    headline: "Organize possible identity-theft credit issues.",
    offer: "Start with a guided review.",
    landingPage: "/#start"
  },
  "General credit clarity": {
    headline: "Find your credit path in plain English.",
    offer: "Start free and see your next steps.",
    landingPage: "/#start"
  }
};

function summarizeLeads(leads) {
  const summary = {
    count: leads.length,
    byGoal: {},
    byPlan: {},
    byScoreRange: {},
    topGoal: null,
    topPlan: null
  };

  for (const lead of leads) {
    summary.byGoal[lead.goal] = (summary.byGoal[lead.goal] || 0) + 1;
    summary.byPlan[lead.planInterest] = (summary.byPlan[lead.planInterest] || 0) + 1;
    summary.byScoreRange[lead.scoreRange] = (summary.byScoreRange[lead.scoreRange] || 0) + 1;
  }

  summary.topGoal = Object.entries(summary.byGoal).sort((a, b) => b[1] - a[1])[0]?.[0] || "General credit clarity";
  summary.topPlan = Object.entries(summary.byPlan).sort((a, b) => b[1] - a[1])[0]?.[0] || "Free Review";
  return summary;
}

function channelFit(goal) {
  return channels
    .filter((channel) => channel.bestFor.includes(goal))
    .map((channel) => ({
      ...channel,
      recommendedBudgetShare: channel.intent === "high" ? 30 : channel.intent === "compounding" ? 20 : 15
    }));
}

function buildGrowthPlan(leads, options = {}) {
  const summary = summarizeLeads(leads);
  const goal = options.goal || summary.topGoal || "General credit clarity";
  const budget = Number(options.monthlyBudget || 0);
  const angle = compliantAngles[goal] || compliantAngles["General credit clarity"];
  const fit = channelFit(goal);

  return {
    ok: true,
    growthVersion,
    modelVersion: engine.modelVersion,
    mode: "approval-gated-automation",
    note: "This plan recommends and simulates campaigns. It does not publish ads or spend money without explicit approval.",
    audience: goal,
    leadSummary: summary,
    compliantAngle: angle,
    channelPlan: fit.map((channel) => ({
      id: channel.id,
      name: channel.name,
      intent: channel.intent,
      approvalRequired: channel.approvalRequired,
      monthlyBudget: budget ? Math.round((budget * channel.recommendedBudgetShare) / 100) : 0
    })),
    nextActions: [
      "Create landing-page variant for top audience.",
      "Draft ad copy with compliance review.",
      "Set bounded monthly budget and stop-loss limits.",
      "Run A/B test in test mode before any live spend.",
      "Review CPL, booked-call rate, plan interest, and complaint rate."
    ]
  };
}

function retentionPlan(leads) {
  const summary = summarizeLeads(leads);
  const segments = [
    {
      id: "new-free-review",
      trigger: "Lead submitted but no plan selected beyond Free Review",
      action: "Send education sequence: report review, score factors, next-step checklist.",
      cadence: "day 0, day 2, day 7"
    },
    {
      id: "plus-build-track",
      trigger: "Plus interest",
      action: "Offer dashboard walkthrough, builder-tool education, and dispute tracker setup.",
      cadence: "day 0, day 3, weekly"
    },
    {
      id: "pro-protect-prepare",
      trigger: "Pro interest",
      action: "Offer identity protection workflow, approval-readiness checklist, and priority review.",
      cadence: "day 0, day 1, weekly"
    },
    {
      id: "legal-eligibility",
      trigger: "Legal+ interest or identity-theft goal",
      action: "Collect documents safely in future portal and route for eligibility review.",
      cadence: "same day"
    }
  ];

  return {
    ok: true,
    growthVersion,
    modelVersion: engine.modelVersion,
    mode: "retention-recommendations",
    leadSummary: summary,
    segments,
    retentionKpis: ["activation rate", "dashboard return rate", "plan upgrade rate", "churn risk", "complaint rate", "referral rate"]
  };
}

function automationStatus() {
  return {
    ok: true,
    growthVersion,
    modelVersion: engine.modelVersion,
    capabilities: [
      "lead segmentation",
      "channel recommendations",
      "campaign simulation",
      "retention sequences",
      "compliance-safe copy angles",
      "approval-gated ad execution design"
    ],
    blockedAutomation: [
      "unbounded ad spend",
      "posting to external ad platforms without approval",
      "guaranteed score/deletion/approval claims",
      "using sensitive credit data for ad targeting"
    ]
  };
}

module.exports = { automationStatus, buildGrowthPlan, retentionPlan, summarizeLeads };
