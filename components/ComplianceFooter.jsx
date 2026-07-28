import Link from "next/link";

const complianceLinks = [
  ["Privacy", "/privacy"],
  ["Terms", "/terms"],
  ["Disclosure", "/disclosure"],
  ["FAQ", "/faq"],
  ["Chat", "/chat"],
];

export default function ComplianceFooter() {
  return (
    <footer className="cv-compliance-footer">
      <div>
        <strong>Credit Vivo</strong>
        <p>
          Results vary. Credit Vivo does not guarantee removals, approvals, or credit score increases.
          You may dispute inaccurate credit report information directly with the credit bureaus at no cost.
        </p>
      </div>
      <nav aria-label="Compliance links">
        {complianceLinks.map(([label, href]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </footer>
  );
}
