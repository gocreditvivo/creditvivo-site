export const CREDIT_VIVO_APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || process.env.APP_ENV || "local";

export const STAGING_RULES = {
  name: "Credit Vivo Staging Safe Mode",
  isStaging: CREDIT_VIVO_APP_ENV === "staging",
  demoMode: false,
  syntheticReportsOnly: true,
  allowRealCustomerData: false,
  paymentsMode: "test",
  emailSending: false,
  marketingEmails: false,
  disputeEmailAutoSend: false,
  autoSend: false,
  externalCalls: false,
  requireProductionGates: true,
  customerFinalResultWithoutQa: false,
  lettersWithoutVerifiedIssue: false,
  complaintsWithoutApproval: false,
  attorneyEscalationWithoutApproval: false,
} as const;

export const STAGING_BANNER_TEXT =
  "STAGING SAFE MODE - Synthetic data only. Do not use real customer reports.";

export const STAGING_SAFE_MODE_SUMMARY = [
  "No real customer data.",
  "No real payments.",
  "No real emails.",
  "No auto-send.",
  "Customer findings stay blocked until scanner gates pass.",
] as const;

