import Link from "next/link";
import { CREDIT_VIVO_EMAILS } from "@/lib/credit-vivo/email";
import { creditVivoConfig } from "@/lib/credit-vivo/config";

type Section = {
  title: string;
  body: string;
};

export function LegalPageShell({
  title,
  subtitle,
  sections,
}: {
  title: string;
  subtitle: string;
  sections: Section[];
}) {
  return (
    <main className="min-h-screen bg-slate-50">
      <section className="mx-auto max-w-5xl px-6 py-12 lg:px-8">
        <Link href="/" className="text-sm font-bold text-emerald-700">
          Credit Vivo
        </Link>
        <div className="mt-6 rounded-lg bg-slate-950 p-8 text-white">
          <p className="text-sm font-semibold text-emerald-200">Compliance starter page</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight">{title}</h1>
          <p className="mt-4 max-w-3xl text-slate-300">{subtitle}</p>
          <p className="mt-5 text-xs leading-5 text-slate-400">{creditVivoConfig.disclosure}</p>
        </div>

        <div className="mt-8 grid gap-4">
          {sections.map((section) => (
            <section key={section.title} className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="text-xl font-bold text-slate-950">{section.title}</h2>
              <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-650">{section.body}</p>
            </section>
          ))}
        </div>

        <div className="mt-8 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm leading-7 text-amber-950">
          These starter notices are not legal advice and should be reviewed by qualified counsel before live launch,
          payment collection, or final customer onboarding.
        </div>
      </section>
    </main>
  );
}

export const privacySections: Section[] = [
  {
    title: "Information We Collect",
    body: "Credit Vivo may collect information you provide directly, such as name, email, phone number, account login information, uploaded credit reports, documents, dispute approvals, messages, and support requests.",
  },
  {
    title: "Credit Report Information",
    body: "Credit report information is treated as sensitive information. Credit Vivo uses this information to provide credit report review, possible issue detection, draft dispute preparation, progress tracking, and related customer support.",
  },
  {
    title: "How We Use Information",
    body: "We use customer information to operate the member portal, review possible report errors, prepare customer-reviewed draft materials, provide support, maintain audit records, and improve security.",
  },
  {
    title: "How We Share Information",
    body: "Credit Vivo does not sell customer credit report data. Sensitive information should be shared externally only when necessary for an approved customer action and after required review.",
  },
  {
    title: "Sensitive Data Protection",
    body: "Credit reports, IDs, account numbers, SSNs, DOBs, scanner outputs, raw evidence, and workbooks must be handled through approved secure systems with role-based access.",
  },
  {
    title: "Data Retention",
    body: "Credit Vivo keeps customer information only as long as needed to provide services, meet legal or compliance obligations, resolve disputes, maintain audit records, and support customer requests.",
  },
  {
    title: "Customer Choices",
    body: `Customers may contact ${CREDIT_VIVO_EMAILS.privacy} to ask about privacy questions, account closure, or data deletion options, subject to legal and operational requirements.`,
  },
  {
    title: "Security Measures",
    body: "Credit Vivo uses security controls designed to protect sensitive customer information. Customer credit report data should not be sent through ordinary email unless specifically authorized and necessary.",
  },
  {
    title: "State Privacy Rights",
    body: "State privacy rights may vary. Credit Vivo will review applicable privacy requests and respond through approved support channels.",
  },
  {
    title: "Contact Information",
    body: `Privacy: ${CREDIT_VIVO_EMAILS.privacy}\nSecurity: ${CREDIT_VIVO_EMAILS.security}\nSupport: ${CREDIT_VIVO_EMAILS.support}`,
  },
];

export const termsSections: Section[] = [
  {
    title: "Acceptance of Terms",
    body: "By using Credit Vivo, you agree to use the service only for lawful credit report review, document upload, and customer-approved progress tracking purposes.",
  },
  {
    title: "Services Provided",
    body: "Credit Vivo helps consumers review credit report information, identify possible reporting issues, prepare dispute drafts for customer review, and track progress.",
  },
  {
    title: "No Guarantee of Results",
    body: "Results are not guaranteed. Credit Vivo does not guarantee that your credit score will increase, that any item will be removed, or that you will qualify for credit, housing, employment, insurance, or financing.",
  },
  {
    title: "No Legal Advice",
    body: "Credit Vivo does not provide legal advice. Attorney support may be available for eligible unresolved credit-reporting issues, but attorney support is not automatic and is not guaranteed.",
  },
  {
    title: "Customer Responsibilities",
    body: "Customers are responsible for providing accurate information, uploading only reports they are legally authorized to provide, reviewing drafts, and approving any next steps before action.",
  },
  {
    title: "Report Upload Authorization",
    body: "By uploading your credit report, you authorize Credit Vivo to review the information you provide for the purpose of identifying possible reporting issues, preparing customer-reviewed draft dispute materials, and tracking your progress.",
  },
  {
    title: "Draft Letters and Approval",
    body: "No dispute letter, debt validation request, complaint packet, or attorney review packet will be sent unless the customer approves it and Credit Vivo completes required admin/compliance review.",
  },
  {
    title: "Fees and Billing",
    body: "Live payment collection for credit improvement services should not be enabled until the written agreement, cancellation language, refund policy, CROA review, and state-law review are complete.",
  },
  {
    title: "Cancellation and Refunds",
    body: "You may cancel your Credit Vivo service according to the terms of your agreement and applicable law. Refund eligibility depends on your agreement, timing, services already performed, and applicable law.",
  },
  {
    title: "Privacy and Security",
    body: "Customer credit report information, identity documents, account numbers, and scanner outputs are sensitive and should be handled only through approved systems.",
  },
  {
    title: "Prohibited Use",
    body: "Do not upload another person's credit report without proper authorization. Do not use Credit Vivo to create false disputes, false identity-theft claims, or unsupported complaint packets.",
  },
  {
    title: "Contact Information",
    body: `Support: ${CREDIT_VIVO_EMAILS.support}\nLegal: ${CREDIT_VIVO_EMAILS.legal}\nBilling: ${CREDIT_VIVO_EMAILS.billing}`,
  },
];

export const disclosureSections: Section[] = [
  {
    title: "Results Not Guaranteed",
    body: "Credit Vivo helps identify possible credit-reporting issues and prepare draft materials for customer review. Credit Vivo cannot guarantee that any item will be corrected, updated, removed, or changed, and cannot guarantee any score increase or approval outcome.",
  },
  {
    title: "No Legal Advice",
    body: "Credit Vivo is not a law firm and does not provide legal advice.",
  },
  {
    title: "Attorney Support Eligibility",
    body: "Attorney support may be available for eligible unresolved credit-reporting issues. Attorney support is not automatic and is not guaranteed.",
  },
  {
    title: "Credit Bureau / Furnisher Responses",
    body: "Credit report results depend on the information in your credit files, responses from credit bureaus and furnishers, and other factors outside Credit Vivo's control.",
  },
  {
    title: "Customer Approval Required",
    body: "Customer approval, admin review, and compliance review are required before dispute prep, complaint packets, attorney review packets, or external sharing moves forward.",
  },
  {
    title: "Credit Score Factors",
    body: "Credit scores are affected by many factors. Accurate, current, and verifiable information may remain on a credit report.",
  },
  {
    title: "Third-Party Services",
    body: "Some production workflows may rely on third-party services for secure storage, identity verification, payments, email delivery, or credit monitoring. Those services require separate setup and review.",
  },
  {
    title: "Security and Data Handling",
    body: "Sensitive credit report information should be handled through approved secure systems and should not be uploaded to public AI tools, GitHub, ordinary cloud folders, or personal accounts.",
  },
  {
    title: "Contact",
    body: `Support: ${CREDIT_VIVO_EMAILS.support}\nPrivacy: ${CREDIT_VIVO_EMAILS.privacy}\nSecurity: ${CREDIT_VIVO_EMAILS.security}`,
  },
];

export const cancellationRefundSections: Section[] = [
  {
    title: "Cancellation Requests",
    body: "You may cancel your Credit Vivo service according to the terms of your agreement and applicable law. If you request cancellation, Credit Vivo will stop future work that has not yet been approved or performed.",
  },
  {
    title: "Refund Review",
    body: "Refund eligibility depends on your agreement, the timing of your request, services already performed, and applicable law.",
  },
  {
    title: "No Guaranteed Outcome",
    body: "Credit Vivo does not guarantee removals, score increases, credit approvals, financing approvals, housing approvals, or any specific result.",
  },
  {
    title: "Payment Compliance Hold",
    body: "Live payment collection for credit improvement services should remain disabled until agreement language, cancellation terms, refund policy, CROA review, and state-law review are complete.",
  },
  {
    title: "Contact",
    body: `Billing: ${CREDIT_VIVO_EMAILS.billing}\nSupport: ${CREDIT_VIVO_EMAILS.support}`,
  },
];
