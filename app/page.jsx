import Link from "next/link";
import BrandLogo from "../components/BrandLogo";

const steps = [
  ["Get your reports", "Securely import your Experian, Equifax, and TransUnion reports."],
  ["Start a secure review", "Review your reports in one private, guided workspace."],
  ["Understand possible review points", "See plain-English findings that may deserve a closer look."],
  ["Organize supporting records", "Keep statements, letters, and notes connected to the right item."],
  ["Approve each next step", "You stay in control before any dispute support moves forward."],
  ["Track responses and updates", "Follow bureau and furnisher replies without juggling spreadsheets."],
];

const plans = [
  {
    name: "Free Scan",
    copy: "Start with a secure review of your reports.",
    features: ["Import 3-bureau reports", "Plain-English summary", "Possible review points", "Portal access"],
    action: "Get started",
    href: "/scan",
  },
  {
    name: "AI Guided",
    copy: "Go deeper with evidence and response tools.",
    features: ["Everything in Free Scan", "Unlimited review points", "Evidence organizer", "Response tracking"],
    action: "Explore guided review",
    href: "/pricing",
    featured: true,
  },
  {
    name: "Plus Managed",
    copy: "Get expert guidance while you stay in control.",
    features: ["Everything in AI Guided", "Expert case review", "Strategy recommendations", "Ongoing tracking"],
    action: "See plan details",
    href: "/pricing",
  },
  {
    name: "Legal Review",
    copy: "A separate attorney path for eligible matters.",
    features: ["Eligibility screening", "Independent attorney review", "Separate engagement", "Clear next steps"],
    action: "Learn more",
    href: "/pricing",
  },
];

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m5 12 4 4L19 6" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

function PortalPreview({ compact = false }) {
  return (
    <div className={`cv-home-portal ${compact ? "is-compact" : ""}`}>
      <div className="cv-window-bar">
        <span />
        <span />
        <span />
        <strong>CreditVivo portal</strong>
        <small>Secure preview</small>
      </div>
      <div className="cv-portal-preview-body">
        <aside className="cv-preview-sidebar">
          <BrandLogo />
          {["Overview", "Reports", "Review points", "Evidence", "Responses"].map((item, index) => (
            <span className={index === 0 ? "active" : ""} key={item}>{item}</span>
          ))}
        </aside>
        <div className="cv-preview-content">
          <div className="cv-preview-heading">
            <div>
              <small>Your credit workspace</small>
              <h3>Report review</h3>
            </div>
            <span>Updated today</span>
          </div>
          <div className="cv-bureau-row">
            {[
              ["Experian", "Reviewed"],
              ["Equifax", "In review"],
              ["TransUnion", "In review"],
            ].map(([name, status], index) => (
              <div key={name}>
                <b className={`cv-bureau-mark mark-${index}`}>{name[0]}</b>
                <span><strong>{name}</strong><small>{status}</small></span>
              </div>
            ))}
          </div>
          <div className="cv-review-table">
            <div className="cv-table-title">
              <strong>Possible review points</strong>
              <span>View all</span>
            </div>
            {[
              ["Needs review", "Late payment reported 03/2023", "2 records"],
              ["Needs review", "Account balance may be incomplete", "1 record"],
              ["Reviewed", "Collection account â€” payment recorded", "3 records"],
            ].map(([status, item, evidence]) => (
              <div className="cv-table-row" key={item}>
                <span className={status === "Reviewed" ? "reviewed" : ""}>{status}</span>
                <strong>{item}</strong>
                <small>{evidence}</small>
              </div>
            ))}
          </div>
          <div className="cv-progress-line">
            {["Reports received", "AI review complete", "Review points identified", "Your approval", "Responses"].map((item, index) => (
              <div className={index < 3 ? "done" : ""} key={item}>
                <i>{index < 3 ? "âœ“" : index + 1}</i>
                <small>{item}</small>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="cv-home">
      <header className="cv-home-nav">
        <BrandLogo />
        <nav aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#ai-review">AI review</a>
          <a href="#portal">Portal</a>
          <a href="#plans">Plans</a>
          <Link href="/login">Client login</Link>
        </nav>
        <Link href="/scan" className="cv-home-button small">Start free scan</Link>
      </header>

      <section className="cv-home-hero">
        <div className="cv-hero-copy">
          <h1>Credit improvement you can see, prove, and track.</h1>
          <p>
            CreditVivo helps you review your credit reports, spot possible inaccuracies,
            organize evidence, prepare dispute support, and track every bureau and furnisher
            response in one secure portal.
          </p>
          <div className="cv-home-actions">
            <Link href="/scan" className="cv-home-button">Start free scan <ArrowIcon /></Link>
            <Link href="/dashboard" className="cv-home-button secondary">View portal preview</Link>
          </div>
          <p className="cv-hero-note">No hard pull. You approve every next step.</p>
        </div>
        <PortalPreview compact />
      </section>

      <section className="cv-trust-rail" aria-label="CreditVivo commitments">
        {[
          ["shield", "No hard pull", "Reviewing your reports does not impact your score."],
          ["document", "Evidence-based review", "Findings connect to report details and records you provide."],
          ["lock", "Secure document vault", "Keep sensitive records organized in one private workspace."],
          ["scales", "Attorney review if eligible", "Legal services require separate eligibility and engagement."],
        ].map(([icon, title, copy]) => (
          <div key={title}>
            <span className={`cv-line-icon ${icon}`} aria-hidden="true" />
            <p><strong>{title}</strong><small>{copy}</small></p>
          </div>
        ))}
      </section>

      <section className="cv-home-section cv-steps" id="how-it-works">
        <div className="cv-section-intro">
          <h2>A clear path from report to response</h2>
          <p>One guided process keeps the details organized and you in control.</p>
        </div>
        <ol>
          {steps.map(([title, copy], index) => (
            <li key={title}>
              <span>{index + 1}</span>
              <strong>{title}</strong>
              <p>{copy}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="cv-ai-band" id="ai-review">
        <div className="cv-ai-intro">
          <h2>Powerful review behind the scenes. Plain English in front.</h2>
          <p>
            CreditVivo helps surface possible review points, then shows why each item
            deserves attention. The engine stays behind the scenesâ€”no raw parser logs,
            no confusing technical output, and no automatic dispute sending.
          </p>
          <Link href="/faq">How the review works <ArrowIcon /></Link>
        </div>
        <div className="cv-ai-principles">
          {[
            ["01", "Report analysis", "Cross-checks account details, dates, balances, and public-record data."],
            ["02", "Plain-English findings", "Explains each possible review point and why it was flagged."],
            ["03", "Source evidence", "Keeps the relevant report lines and your supporting records together."],
            ["04", "Human approval", "You review and approve each step. Nothing is sent automatically."],
          ].map(([number, title, copy]) => (
            <article key={title}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="cv-home-section cv-portal-section" id="portal">
        <div className="cv-section-intro">
          <h2>Everything connected to the right next step.</h2>
          <p>
            Review a finding, see its source, organize evidence, and follow every response
            in one calm workspace.
          </p>
        </div>
        <div className="cv-portal-detail">
          <article>
            <div className="cv-finding-title">
              <span>Needs review</span>
              <small>Possible review point</small>
            </div>
            <h3>Late payment reported 03/2023</h3>
            <dl>
              <div><dt>Account</dt><dd>ABC Bank Card ending 1234</dd></div>
              <div><dt>Source</dt><dd>Equifax</dd></div>
              <div><dt>Why flagged</dt><dd>Your records may show an on-time payment for the same period.</dd></div>
            </dl>
            <h4>Supporting records</h4>
            {["Bank statement â€” Feb 2023", "Payment confirmation â€” Mar 5, 2023", "Dispute letter draft"].map((item, index) => (
              <p className="cv-evidence-row" key={item}>
                <span>{item}</span>
                <b className={index === 2 ? "draft" : ""}>{index === 2 ? "Draft" : "Uploaded"}</b>
              </p>
            ))}
            <Link href="/findings" className="cv-home-button small">View evidence</Link>
          </article>
          <div className="cv-tracker">
            <div className="cv-tracker-heading">
              <div><small>Bureau &amp; furnisher</small><h3>Response tracker</h3></div>
              <span>Live in your portal</span>
            </div>
            {[
              ["Experian", 2, "In review"],
              ["Equifax", 3, "Replied"],
              ["TransUnion", 1, "Received"],
            ].map(([name, progress, status]) => (
              <div className="cv-tracker-row" key={name}>
                <strong>{name}</strong>
                <div>
                  {[0, 1, 2, 3].map((item) => <i className={item <= progress ? "active" : ""} key={item} />)}
                </div>
                <span>{status}</span>
              </div>
            ))}
            <p>Responses stay attached to the matching account and review point.</p>
          </div>
        </div>
      </section>

      <section className="cv-plans-band" id="plans">
        <div className="cv-section-intro">
          <h2>Choose the level of support you need.</h2>
          <p>Start free. See plan details before you commit to paid support.</p>
        </div>
        <div className="cv-plans-grid">
          {plans.map((plan) => (
            <article className={plan.featured ? "featured" : ""} key={plan.name}>
              <h3>{plan.name}</h3>
              <p>{plan.copy}</p>
              <ul>
                {plan.features.map((feature) => <li key={feature}><CheckIcon />{feature}</li>)}
              </ul>
              <Link href={plan.href} className={`cv-home-button small ${plan.featured ? "" : "secondary"}`}>{plan.action}</Link>
            </article>
          ))}
        </div>
        <p className="cv-plan-note">
          Attorney services require separate eligibility review and attorney engagement.
          Not all matters will qualify.
        </p>
      </section>

      <section className="cv-final-cta">
        <div>
          <h2>Take control of your credit story.</h2>
          <p>Start with a secure review and clear, human-approved next steps.</p>
        </div>
        <div className="cv-home-actions">
          <Link href="/scan" className="cv-home-button">Start free scan</Link>
          <Link href="/dashboard" className="cv-home-button secondary">View portal preview</Link>
        </div>
      </section>
    </main>
  );
}

