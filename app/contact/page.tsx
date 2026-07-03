import { ContactShell } from "@/components/credit-vivo/ContactShell";
import { CREDIT_VIVO_EMAILS } from "@/lib/credit-vivo/email";

export default function Page() {
  return (
    <ContactShell
      title="Contact Credit Vivo"
      subtitle="Use support for customer questions, billing questions, and member portal help."
      primaryEmail="support"
    >
      <div className="grid gap-3 text-sm text-slate-700">
        <p>
          General support:{" "}
          <a className="font-bold text-emerald-700" href={`mailto:${CREDIT_VIVO_EMAILS.support}`}>
            {CREDIT_VIVO_EMAILS.support}
          </a>
        </p>
        <p>
          Billing:{" "}
          <a className="font-bold text-emerald-700" href={`mailto:${CREDIT_VIVO_EMAILS.billing}`}>
            {CREDIT_VIVO_EMAILS.billing}
          </a>
        </p>
        <p>
          Dispute support:{" "}
          <a className="font-bold text-emerald-700" href={`mailto:${CREDIT_VIVO_EMAILS.disputes}`}>
            {CREDIT_VIVO_EMAILS.disputes}
          </a>
        </p>
      </div>
    </ContactShell>
  );
}

