"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import BrandLogo from "./BrandLogo";

const defaultEvidence = `Paste a build error, test output, dependency audit, or scanner verification note here.

Do not paste customer reports, SSNs, IDs, account numbers, passwords, API keys, or payment information.`;

const planAreas = [
  ["build", "Fix the build"],
  ["scanner", "Verify scanner"],
  ["compliance", "Review compliance"],
  ["release", "Check release"],
];

function StatusBadge({ children, tone = "neutral" }) {
  return <span className={`cv-agent-badge ${tone}`}>{children}</span>;
}

function Stat({ label, value, tone }) {
  return (
    <div className={`cv-agent-stat ${tone || ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function BuildAgentClient() {
  const [snapshot, setSnapshot] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [plan, setPlan] = useState(null);
  const [evidence, setEvidence] = useState(defaultEvidence);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const readiness = useMemo(() => {
    if (!snapshot) return { label: "Not checked", tone: "neutral" };
    if (snapshot.blockers?.length) return { label: "Blocked", tone: "danger" };
    return { label: "Review required", tone: "warning" };
  }, [snapshot]);

  async function callAgent(payload, key) {
    setBusy(key);
    setError("");
    try {
      const response = await fetch("/api/build-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Build Agent request failed.");
      return data;
    } catch (requestError) {
      setError(requestError.message || "Build Agent is unavailable.");
      return null;
    } finally {
      setBusy("");
    }
  }

  async function refreshSnapshot() {
    const data = await callAgent({ action: "snapshot" }, "snapshot");
    if (data?.snapshot) setSnapshot(data.snapshot);
  }

  async function analyze() {
    const data = await callAgent({ action: "analyze", input: evidence }, "analyze");
    if (data?.analysis) setAnalysis(data.analysis);
  }

  async function createPlan(area) {
    const data = await callAgent({ action: "plan", area }, `plan-${area}`);
    if (data?.plan) setPlan(data.plan);
  }

  useEffect(() => {
    refreshSnapshot();
  }, []);

  return (
    <main className="cv-agent-page">
      <nav className="cv-agent-nav">
        <BrandLogo />
        <div>
          <Link href="/">Website</Link>
          <Link href="/dashboard">Portal</Link>
          <Link href="/chat">Compliance Chat</Link>
        </div>
      </nav>

      <header className="cv-agent-hero">
        <div>
          <p className="cv-agent-kicker">Internal operations workspace</p>
          <h1>Build &amp; Compliance Copilot</h1>
          <p>
            Read-only diagnosis for the Credit Vivo team. It reviews repository evidence,
            identifies blockers, and prepares an approval-controlled next step.
          </p>
        </div>
        <div className="cv-agent-hero-status">
          <span>Current gate</span>
          <StatusBadge tone={readiness.tone}>{readiness.label}</StatusBadge>
          <small>No automatic edits, merges, deployments, disputes, or customer-data processing.</small>
        </div>
      </header>

      {error ? <div className="cv-agent-alert danger">{error}</div> : null}

      <section className="cv-agent-grid">
        <article className="cv-agent-panel cv-agent-snapshot">
          <div className="cv-agent-panel-heading">
            <div>
              <p className="cv-agent-kicker">Live local evidence</p>
              <h2>Repository snapshot</h2>
            </div>
            <button onClick={refreshSnapshot} disabled={Boolean(busy)}>
              {busy === "snapshot" ? "Checking…" : "Refresh"}
            </button>
          </div>

          <div className="cv-agent-stats">
            <Stat label="Working-tree changes" value={snapshot?.workingTree?.total ?? "—"} tone={snapshot?.workingTree?.total ? "danger" : "safe"} />
            <Stat label="Behind main" value={snapshot?.divergence?.behindMain ?? "—"} tone={snapshot?.divergence?.behindMain ? "warning" : "safe"} />
            <Stat label="Modified" value={snapshot?.workingTree?.modified ?? "—"} />
            <Stat label="Deleted" value={snapshot?.workingTree?.deleted ?? "—"} />
            <Stat label="Untracked" value={snapshot?.workingTree?.untracked ?? "—"} />
            <Stat label="Build script" value={snapshot?.package?.scripts?.includes("build") ? "Present" : "Missing"} tone={snapshot?.package?.scripts?.includes("build") ? "safe" : "danger"} />
          </div>

          <dl className="cv-agent-details">
            <div><dt>Branch</dt><dd>{snapshot?.branch || "Not checked"}</dd></div>
            <div><dt>HEAD</dt><dd>{snapshot?.head || "Not checked"}</dd></div>
            <div><dt>Package</dt><dd>{snapshot?.package ? `${snapshot.package.name} ${snapshot.package.version}` : "Not checked"}</dd></div>
          </dl>

          <div className="cv-agent-blockers">
            <h3>Observed blockers</h3>
            {snapshot?.blockers?.length ? (
              <ul>{snapshot.blockers.map((item) => <li key={item}>{item}</li>)}</ul>
            ) : (
              <p>Run the snapshot to collect local evidence.</p>
            )}
          </div>
        </article>

        <aside className="cv-agent-panel cv-agent-guardrails">
          <p className="cv-agent-kicker">Hard limits</p>
          <h2>Agent permissions</h2>
          <ul>
            <li><strong>Allowed:</strong> repository reads, safe Git inspection, evidence analysis, and task planning.</li>
            <li><strong>Blocked:</strong> customer reports, production writes, automatic fixes, merges, and deployments.</li>
            <li><strong>Blocked:</strong> dispute, letter, complaint, email, or legal-action sending.</li>
            <li><strong>Required:</strong> synthetic fixtures and named human approval before changes.</li>
          </ul>
          <div className="cv-agent-approval">
            <span>Human approval</span>
            <strong>Required for every change</strong>
          </div>
        </aside>
      </section>

      <section className="cv-agent-panel cv-agent-evidence">
        <div className="cv-agent-panel-heading">
          <div>
            <p className="cv-agent-kicker">Evidence analyst</p>
            <h2>Analyze a build or scanner result</h2>
          </div>
          <StatusBadge>Redaction enabled</StatusBadge>
        </div>
        <textarea
          value={evidence}
          onChange={(event) => setEvidence(event.target.value)}
          maxLength={8000}
          aria-label="Build or scanner evidence"
        />
        <div className="cv-agent-action-row">
          <button onClick={analyze} disabled={Boolean(busy) || !evidence.trim()}>
            {busy === "analyze" ? "Analyzing…" : "Analyze evidence"}
          </button>
          <span>{evidence.length.toLocaleString()} / 8,000 characters</span>
        </div>

        {analysis ? (
          <div className="cv-agent-analysis">
            <div className="cv-agent-verdict">
              <span>Verdict</span>
              <StatusBadge tone={analysis.verdict === "BLOCKED" ? "danger" : analysis.verdict === "NEEDS_REPAIR" ? "warning" : "neutral"}>
                {analysis.verdict}
              </StatusBadge>
            </div>
            <div className="cv-agent-finding-list">
              {analysis.findings.map((finding) => (
                <article key={finding.id}>
                  <StatusBadge tone={finding.severity === "P0" ? "danger" : finding.severity === "P1" ? "warning" : "neutral"}>
                    {finding.severity}
                  </StatusBadge>
                  <div>
                    <h3>{finding.title}</h3>
                    <p>{finding.next}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="cv-agent-panel">
        <div className="cv-agent-panel-heading">
          <div>
            <p className="cv-agent-kicker">Next-task planner</p>
            <h2>Prepare one controlled work plan</h2>
          </div>
          <StatusBadge tone="warning">Approval before action</StatusBadge>
        </div>
        <div className="cv-agent-plan-buttons">
          {planAreas.map(([area, label]) => (
            <button key={area} onClick={() => createPlan(area)} disabled={Boolean(busy)}>
              {busy === `plan-${area}` ? "Preparing…" : label}
            </button>
          ))}
        </div>
        {plan ? (
          <div className="cv-agent-plan">
            <h3>{plan.title}</h3>
            <ol>{plan.steps.map((step) => <li key={step}>{step}</li>)}</ol>
            <p><strong>Definition of done:</strong> {plan.definitionOfDone}</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
