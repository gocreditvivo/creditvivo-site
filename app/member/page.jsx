import BrandLogo from "../../components/BrandLogo";

export const metadata = {
  title: "Member Area",
  description: "Your Credit Vivo member area — scan results, findings, disputes, monthly updates, and your document vault.",
};

const memberLinks = [
  ["Dashboard", "/dashboard", "Your portal home: current stage, next step, and progress at a glance."],
  ["Findings", "/findings", "Plain-English review of possible issues found on your credit report."],
  ["Free Scan", "/scan", "Start or re-run a launch-preview scan of your credit report."],
  ["Disputes", "/disputes", "Track dispute prep, rounds, and responses as they move forward."],
  ["Monthly Updates", "/monthly", "See month-over-month progress and guidance."],
  ["Messages", "/messages", "Read updates and messages tied to your account."],
  ["Document Vault", "/vault", "Securely keep the documents connected to your case."],
  ["Compliance Chat", "/chat", "Ask safe questions about uploads, findings, disputes, and next steps."],
];

export default function MemberPage() {
  return (
    <main style={{ fontFamily: "var(--cv-font)", background: "linear-gradient(180deg, #fffdf5 0%, #f0fdf4 48%, #eef9ff 100%)", minHeight: "100vh", padding: "32px 7% 70px", color: "#102033" }}>
      <BrandLogo />
      <h1 style={{ fontSize: 42, marginBottom: 6 }}>Member area</h1>
      <p style={{ fontSize: 18, color: "#334155", maxWidth: 720, lineHeight: 1.6, marginTop: 0 }}>
        Everything for your Credit Vivo account in one place. Pick up where you left off, or jump straight to a section below.
      </p>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16, maxWidth: 960, marginTop: 26 }}>
        {memberLinks.map(([title, href, body]) => (
          <a
            key={href}
            href={href}
            style={{
              display: "block",
              background: "rgba(255,255,255,.94)",
              border: "1px solid #cfeee0",
              borderRadius: 10,
              padding: 20,
              textDecoration: "none",
              color: "#102033",
              boxShadow: "0 18px 42px rgba(16,32,51,.07)",
            }}
          >
            <h2 style={{ fontSize: 20, margin: "0 0 6px" }}>{title}</h2>
            <p style={{ fontSize: 15, color: "#334155", lineHeight: 1.55, margin: 0 }}>{body}</p>
          </a>
        ))}
      </section>

      <p style={{ fontSize: 14, color: "#64748b", maxWidth: 720, lineHeight: 1.6, marginTop: 28 }}>
        Not signed in yet? <a href="/login" style={{ color: "#047857", fontWeight: 700 }}>Log in</a> or{" "}
        <a href="/signup" style={{ color: "#047857", fontWeight: 700 }}>create your free account</a>. This is a launch preview:
        some features are marked as connecting after vendor setup and do not yet send real disputes, mail, or messages.
      </p>
    </main>
  );
}
