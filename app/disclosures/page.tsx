import { LegalPageShell, disclosureSections } from "@/components/credit-vivo/LegalContentPages";

export default function Page() {
  return (
    <LegalPageShell
      title="Disclosures"
      subtitle="Important limits, approval gates, and safe expectations for Credit Vivo services."
      sections={disclosureSections}
    />
  );
}
