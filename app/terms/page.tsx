import { LegalPageShell, termsSections } from "@/components/credit-vivo/LegalContentPages";

export default function Page() {
  return (
    <LegalPageShell
      title="Terms of Service"
      subtitle="Starter service terms for Credit Vivo's credit report review, draft preparation, and progress tracking workflows."
      sections={termsSections}
    />
  );
}
