import Link from "next/link";

const complianceLinks = [
  ["Privacy", "/privacy"],
  ["Terms", "/terms"],
  ["Disclosure", "/disclosure"],
  ["FAQ", "/faq"],
  ["Client login", "/login"],
];

export default function ComplianceFooter() {
  return (
    <footer className="cv-compliance-footer">
      <div className="cv-footer-brand">
        <strong>CreditVivo</strong>
        <span>Secure. Transparent. Human-first.</span>
      </div>
      <nav aria-label="Compliance links">
        {complianceLinks.map(([label, href]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </footer>
  );
}

