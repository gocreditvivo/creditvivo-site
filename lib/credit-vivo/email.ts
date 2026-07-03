export const CREDIT_VIVO_EMAILS = {
  founder: "tim@creditvivo.com",
  support: "support@creditvivo.com",
  social: "social@creditvivo.com",
  privacy: "privacy@creditvivo.com",
  legal: "legal@creditvivo.com",
  billing: "billing@creditvivo.com",
  disputes: "disputes@creditvivo.com",
  security: "security@creditvivo.com",
  noReply: "no-reply@creditvivo.com",
} as const;

export const EMAIL_FEATURE_FLAGS = {
  provider: process.env.EMAIL_PROVIDER || "disabled",
  from: process.env.EMAIL_FROM || CREDIT_VIVO_EMAILS.noReply,
  enableEmailSending: process.env.ENABLE_EMAIL_SENDING === "true",
  enableMarketingEmails: process.env.ENABLE_MARKETING_EMAILS === "true",
  enableDisputeEmailAutoSend: process.env.ENABLE_DISPUTE_EMAIL_AUTO_SEND === "true",
} as const;

export const EMAIL_DISCLOSURE =
  "Results are not guaranteed. Attorney support may be available for eligible unresolved credit-reporting issues. Credit Vivo does not provide legal advice.";

export const EMAIL_SAFETY_RULES = [
  "Email sending is disabled by default.",
  "Marketing emails require consent and unsubscribe controls before launch.",
  "Dispute letters, complaint packets, attorney referral packets, credit report attachments, raw scanner workbooks, and raw evidence packets are not sent by default.",
  "Sensitive credit data, full account numbers, SSN, DOB, IDs, and passwords must not be sent through ordinary email.",
] as const;

