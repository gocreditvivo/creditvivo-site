import { LegalPageShell, cancellationRefundSections } from "@/components/credit-vivo/LegalContentPages";

export default function Page() {
  return (
    <LegalPageShell
      title="Cancellation / Refund Policy"
      subtitle="Starter cancellation and refund language pending attorney review."
      sections={cancellationRefundSections}
    />
  );
}
