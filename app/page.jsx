import BrandLogo from "../components/BrandLogo";

const navLinks = [
  ["Free Scan", "/scan"],
  ["Dashboard", "/dashboard"],
  ["Findings", "/findings"],
  ["Chat", "/chat"],
  ["Monthly", "/monthly"],
  ["Pricing", "/pricing"],
  ["Login", "/login"],
];

const steps = [
  ["Upload", "Add a credit report or start with a guided launch-preview upload."],
  ["Understand", "See simple findings in plain English, without backend scanner noise."],
  ["Act", "Move through Prep, Round 1, response tracking, and the next best step."],
  ["Grow", "Track monthly updates, documents, messages, and credit-building guidance."],
];

const signals = [
  ["Simple portal", "Ready", "Customers always know what is happening next."],
  ["Compliance chat", "Ready", "Safe answers for uploads, findings, disputes, and next steps."],
  ["Friendly updates", "Preview", "Portal updates are ready. Email and text delivery connect after vendor setup."],
  ["Staged rounds", "Ready", "We do not rush every possible issue at once."],
];

export default function HomePage() {
  return (
    <main className="cv-page">
      <nav className="cv-nav" style={{ display: "flex", justifyContent: "space-between", padding: "18px 7%", alignItems: "center", gap: 16, position: "sticky", top: 0, zIndex: 10 }}>
        <BrandLogo />
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
          {navLinks.map(([label, href]) => (
            <a key={href} href={href}>{label}</a>
          ))}
        </div>
      </nav>

      <section
        style={{
          minHeight: 620,
          display: "grid",
          alignItems: "center",
          padding: "64px 7% 58px",
          backgroundImage: "linear-gradient(90deg, rgba(255,253,245,.97) 0%, rgba(255,253,245,.9) 35%, rgba(255,253,245,.18) 70%), url('/brand/credit-vivo-hero.png')",
          backgroundSize: "cover",
          backgroundPosition: "center right",
          borderBottom: "1px solid #cfeee0",
        }}
      >
        <div style={{ maxWidth: 650 }}>
          <p style={{ display: "inline-block", background: "#dcfce7", color: "#047857", padding: "8px 12px", borderRadius: 999, fontWeight: 900 }}>
            Launch preview ready
          </p>
          <h1 style={{ fontSize: 58, lineHeight: 1.02, margin: "18px 0", maxWidth: 620, letterSpacing: 0 }}>
            Credit Vivo
          </h1>
          <p style={{ fontSize: 19, color: "#334155", maxWidth: 610, lineHeight: 1.65 }}>
            A friendly credit report portal that helps customers upload reports, understand possible issues, follow dispute rounds, and see monthly progress. Unconnected features are clearly marked before launch.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 24 }}>
            <a href="/scan" className="cv-primary-link">Start Free Credit Scan</a>
            <a href="/dashboard" className="cv-secondary-link">View Customer Portal</a>
            <a href="/chat" className="cv-secondary-link">Ask Compliance Chat</a>
          </div>
        </div>
      </section>

      <section style={{ padding: "34px 7% 72px", display: "grid", gap: 24 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16 }}>
          {signals.map(([title, status, copy]) => (
            <div key={title} className="cv-card" style={{ padding: 22 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
                <h2 style={{ margin: "0 0 8px", fontSize: 22 }}>{title}</h2>
                <span className={`cv-status-chip ${status === "Ready" ? "ready" : "soon"}`}>{status}</span>
              </div>
              <p style={{ margin: 0, color: "#557184", lineHeight: 1.55 }}>{copy}</p>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(280px,.72fr)", gap: 20, alignItems: "start" }}>
          <section className="cv-card" style={{ padding: 26 }}>
            <p style={{ color: "#0f766e", fontWeight: 900, marginTop: 0 }}>How Credit Vivo works</p>
            <div style={{ display: "grid", gap: 14 }}>
              {steps.map(([title, copy], index) => (
                <div key={title} style={{ display: "grid", gridTemplateColumns: "44px minmax(0,1fr)", gap: 14, alignItems: "start", borderTop: index ? "1px solid #dff4e9" : 0, paddingTop: index ? 14 : 0 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 999, display: "grid", placeItems: "center", background: index === 0 ? "#dcfce7" : index === 1 ? "#e0f2fe" : index === 2 ? "#fef3c7" : "#ffe4e6", color: "#0f4f4a", fontWeight: 950 }}>
                    {index + 1}
                  </span>
                  <div>
                    <h3 style={{ margin: "0 0 5px" }}>{title}</h3>
                    <p style={{ margin: 0, color: "#557184", lineHeight: 1.55 }}>{copy}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <aside className="cv-card" style={{ padding: 26, background: "linear-gradient(180deg, #ecfdf5, #ffffff)" }}>
            <h2 style={{ marginTop: 0 }}>Built for the marathon</h2>
            <p style={{ color: "#557184", lineHeight: 1.65 }}>
              Credit improvement is a process. Customers need clear steps, regular updates, and honest guidance more than a confusing scanner screen.
            </p>
            <a href="/monthly" className="cv-primary-link">See Monthly Update</a>
          </aside>
        </div>
      </section>
    </main>
  );
}
