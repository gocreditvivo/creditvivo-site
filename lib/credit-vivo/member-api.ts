import type { MemberPortalPayload } from "@/types/credit-vivo-member";
import {
  allProductionGatesPassed,
  creditVivoConfig,
  defaultProductionGate,
} from "./config";

const lockedPayload: MemberPortalPayload = {
  profile: null,
  stats: [],
  uploads: [
    { bureau: "Equifax", status: "blocked", note: "Secure backend required before upload." },
    { bureau: "Experian", status: "blocked", note: "Secure backend required before upload." },
    { bureau: "TransUnion", status: "blocked", note: "Secure backend required before upload." },
  ],
  reviewAccounts: [],
  positiveAccounts: [],
  draftLetters: [],
  progressSteps: [
    {
      title: "Production gate active",
      description:
        "Customer findings remain blocked until scanner health check, ground-truth validation, QA, security audit, and production gate pass.",
      status: "blocked",
    },
  ],
  progressMilestones: [
    {
      phase: "Profile setup",
      status: "current",
      customerView: "Confirm contact details and credit goal before report review begins.",
      adminGate: "Customer profile must be complete and consent must be logged.",
    },
    {
      phase: "Identity and files",
      status: "blocked",
      customerView: "Upload identity, address, report, and supporting documents through secure intake.",
      adminGate: "Admin must verify file ownership, readability, and document match before use.",
    },
    {
      phase: "Report review",
      status: "blocked",
      customerView: "Possible report errors appear only after scanner and QA checks pass.",
      adminGate: "Native parser output, evidence snippets, and confidence checks must pass review.",
    },
    {
      phase: "Customer approvals",
      status: "blocked",
      customerView: "Review documented next steps and approve draft dispute prep before action.",
      adminGate: "Customer approval, admin review, and compliance review are required.",
    },
  ],
  messages: [],
  documents: [
    {
      name: "Government ID",
      type: "Identity",
      status: "needs_review",
      visibility: "Customer + admin",
      requiredFor: "Identity verification",
      verifiedBy: "admin",
      canUseForPrep: false,
      note: "Must be readable, unexpired, and match the customer profile before any file review moves forward.",
    },
    {
      name: "Proof of address",
      type: "Address",
      status: "pending",
      visibility: "Customer + admin",
      requiredFor: "Bureau correspondence and profile match",
      verifiedBy: "admin",
      canUseForPrep: false,
      note: "Accepted examples include a recent utility bill, bank statement, or lease page showing name and address.",
    },
    {
      name: "Three-bureau credit report",
      type: "Credit report",
      status: "blocked",
      visibility: "Controlled report file",
      requiredFor: "Plain-English review and scanner analysis",
      verifiedBy: "system",
      canUseForPrep: false,
      note: "Raw report files stay hidden from customer UI until secure storage and access controls are approved.",
    },
    {
      name: "Supporting documents",
      type: "Evidence",
      status: "pending",
      visibility: "Customer + admin",
      requiredFor: "Documented next steps",
      verifiedBy: "admin",
      canUseForPrep: false,
      note: "Examples: creditor letters, paid receipts, court documents, FTC report, or police report when applicable.",
    },
  ],
  identityVerification: {
    status: "needs_review",
    summary:
      "Identity verification is not complete. Credit Vivo must verify ID, address, and report ownership before using uploaded files.",
    checks: [
      { label: "Government ID", status: "needs_review", note: "Awaiting admin review and expiration check." },
      { label: "Selfie/liveness", status: "pending", note: "Future vendor or manual review step; not connected yet." },
      { label: "Address match", status: "pending", note: "Proof of address must match the customer profile." },
      { label: "Report ownership", status: "blocked", note: "Credit report must match verified identity before scanner output is released." },
    ],
  },
  customerTasks: [
    {
      title: "Confirm profile information",
      status: "current",
      dueLabel: "Before review starts",
      detail: "Confirm legal name, contact details, address, and credit goal. Sensitive IDs stay hidden.",
    },
    {
      title: "Upload required documents",
      status: "pending",
      dueLabel: "Secure upload required",
      detail: "Government ID, proof of address, three-bureau report, and supporting documents if available.",
    },
    {
      title: "Wait for admin verification",
      status: "blocked",
      dueLabel: "Admin review",
      detail: "Files are not used for dispute prep until system checks, admin review, and compliance gates pass.",
    },
  ],
  productionGate: defaultProductionGate(),
};

function sanitizePayload(data: MemberPortalPayload): MemberPortalPayload {
  const gate = data.productionGate || defaultProductionGate("Missing production gate from backend.");

  const gatesPassed = allProductionGatesPassed(gate);
  const customerDataAllowed =
    gatesPassed && Boolean(gate.customerDataAllowed) && !creditVivoConfig.demoMode;

  if (!customerDataAllowed) {
    return {
      ...data,
      reviewAccounts: [],
      draftLetters: [],
      documents: data.documents?.filter((doc) => doc.visibility !== "Raw credit report") || [],
      productionGate: {
        ...gate,
        customerDataAllowed: false,
        message:
          gate.message ||
          "Customer findings are blocked until all production scanner gates pass.",
      },
    };
  }

  return {
    ...data,
    productionGate: {
      ...gate,
      customerDataAllowed: true,
      message: gate.message || "Production gates passed. Customer-safe findings are available.",
    },
  };
}

export async function getMemberPortalPayload(): Promise<MemberPortalPayload> {
  if (creditVivoConfig.demoMode) {
    return {
      ...lockedPayload,
      productionGate: defaultProductionGate(
        "Demo mode is not enabled for this production build. Customer data remains blocked."
      ),
    };
  }

  if (!creditVivoConfig.apiBaseUrl) {
    return lockedPayload;
  }

  try {
    const response = await fetch(`${creditVivoConfig.apiBaseUrl}/member/portal`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      return {
        ...lockedPayload,
        productionGate: defaultProductionGate("Backend API unavailable or not approved."),
      };
    }

    const data = (await response.json()) as MemberPortalPayload;
    return sanitizePayload(data);
  } catch {
    return {
      ...lockedPayload,
      productionGate: defaultProductionGate("Backend API unavailable. Customer data remains blocked."),
    };
  }
}
