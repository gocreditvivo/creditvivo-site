export type PortalStatus = "complete" | "current" | "pending" | "needs_review" | "blocked";

export type ProductionGate = {
  demoMode: boolean;
  scannerConnected: boolean;
  healthCheckPassed: boolean;
  groundTruthPassed: boolean;
  qaVerificationPassed: boolean;
  securityAuditPassed: boolean;
  productionGatePassed: boolean;
  customerDataAllowed: boolean;
  message: string;
};

export type MemberProfile = {
  name: string;
  plan: string;
  scoreGoal: string;
  reportDate: string;
  nextAction: string;
};

export type PortalStat = {
  label: string;
  value: string;
  detail: string;
};

export type ReportUpload = {
  bureau: "Equifax" | "Experian" | "TransUnion";
  status: PortalStatus;
  uploadedAt?: string;
  note: string;
};

export type ReviewAccount = {
  id: string;
  name: string;
  type: string;
  bureaus: string[];
  priority: "High" | "Medium" | "Low" | "Hold";
  status: string;
  customerSummary: string;
  nextStep: string;
  draftReady: boolean;
};

export type DraftLetter = {
  id: string;
  account: string;
  type: string;
  status: string;
  summary: string;
  approvalRequired: boolean;
};

export type ProgressStep = {
  title: string;
  description: string;
  status: PortalStatus;
};

export type PortalMessage = {
  from: string;
  subject: string;
  body: string;
  date: string;
};

export type CustomerDocument = {
  name: string;
  type: string;
  status: string;
  visibility: string;
  requiredFor?: string;
  verifiedBy?: "system" | "admin" | "vendor" | "not_started";
  canUseForPrep?: boolean;
  note?: string;
};

export type IdentityVerification = {
  status: PortalStatus;
  summary: string;
  checks: {
    label: string;
    status: PortalStatus;
    note: string;
  }[];
};

export type CustomerTask = {
  title: string;
  status: PortalStatus;
  dueLabel: string;
  detail: string;
};

export type ProgressMilestone = {
  phase: string;
  status: PortalStatus;
  customerView: string;
  adminGate: string;
};

export type MemberPortalPayload = {
  profile: MemberProfile | null;
  stats: PortalStat[];
  uploads: ReportUpload[];
  reviewAccounts: ReviewAccount[];
  positiveAccounts: string[];
  draftLetters: DraftLetter[];
  progressSteps: ProgressStep[];
  progressMilestones?: ProgressMilestone[];
  messages: PortalMessage[];
  documents: CustomerDocument[];
  identityVerification?: IdentityVerification;
  customerTasks?: CustomerTask[];
  productionGate: ProductionGate;
};
