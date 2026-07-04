import { LegalPageShell, privacySections } from "@/components/credit-vivo/LegalContentPages";

export default function Page() {
  return (
    <LegalPageShell
      title="Privacy Notice"
      subtitle="How Credit Vivo handles customer information, credit report data, documents, privacy requests, and security expectations."
      sections={privacySections}
    />
  );
}
