export const creditVivoConfig = {
  demoMode: process.env.NEXT_PUBLIC_CREDIT_VIVO_DEMO_MODE === "true",
  requireProductionGates:
    process.env.NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_PRODUCTION_GATES !== "false",
  apiBaseUrl: process.env.NEXT_PUBLIC_CREDIT_VIVO_API_BASE_URL || "",
  requireAuth: process.env.NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_AUTH !== "false",
  disclosure:
    "Results are not guaranteed. Attorney support may be available for eligible unresolved credit-reporting issues. Credit Vivo does not provide legal advice.",
  productionRules: {
    demoModeOffByDefault: true,
    noRealDataInFrontend: true,
    noAutoSend: true,
    draftOnlyLetters: true,
    customerApprovalRequired: true,
    adminApprovalRequiredForEscalation: true,
    findingsBlockedUnlessGatesPass: true,
    lettersBlockedUnlessGatesPass: true,
    rawReportsHiddenFromCustomerUI: true,
  },
} as const;

export function defaultProductionGate(message?: string) {
  return {
    demoMode: creditVivoConfig.demoMode,
    scannerConnected: Boolean(creditVivoConfig.apiBaseUrl),
    healthCheckPassed: false,
    groundTruthPassed: false,
    qaVerificationPassed: false,
    securityAuditPassed: false,
    productionGatePassed: false,
    customerDataAllowed: false,
    message:
      message ||
      "Production mode is active. Customer credit data is blocked until backend scanner gates pass.",
  };
}

export function allProductionGatesPassed(gate: {
  healthCheckPassed?: boolean;
  groundTruthPassed?: boolean;
  qaVerificationPassed?: boolean;
  securityAuditPassed?: boolean;
  productionGatePassed?: boolean;
}) {
  return Boolean(
    gate.healthCheckPassed &&
      gate.groundTruthPassed &&
      gate.qaVerificationPassed &&
      gate.securityAuditPassed &&
      gate.productionGatePassed
  );
}
