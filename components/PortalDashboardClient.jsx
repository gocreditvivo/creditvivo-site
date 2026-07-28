'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import BrandLogo from './BrandLogo';
import { demoCase } from './demoCase';
import { logEvent } from './eventLog';

const STORAGE_KEY = 'creditVivoDemoCase';
const CASES_KEY = 'creditVivoDemoCases';

function loadCase() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : demoCase;
  } catch {
    return demoCase;
  }
}

function loadCases() {
  try {
    const raw = localStorage.getItem(CASES_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return parsed.length ? parsed : [loadCase()];
  } catch {
    return [demoCase];
  }
}

function firstName(value) {
  return String(value || 'there').trim().split(/\s+/)[0] || 'there';
}

function scoreTrend(scoreProgress) {
  if (!scoreProgress?.length) return 0;
  const first = scoreProgress[0]?.score || 0;
  const latest = scoreProgress[scoreProgress.length - 1]?.score || first;
  return latest - first;
}

export default function PortalDashboardClient() {
  const [caseData, setCaseData] = useState(demoCase);
  const [cases, setCases] = useState([demoCase]);
  const [selectedFile, setSelectedFile] = useState('');

  useEffect(() => {
    const loadedCase = loadCase();
    setCaseData(loadedCase);
    setCases(loadCases());
    logEvent('page_viewed', {
      area: 'Dashboard',
      page: '/dashboard',
      caseId: loadedCase.caseId,
      consumerName: loadedCase.consumerName,
      consumerEmail: loadedCase.consumerEmail,
    });
  }, []);

  function switchCase(nextCase) {
    setCaseData(nextCase);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextCase));
    logEvent('case_switched', {
      area: 'Dashboard',
      caseId: nextCase.caseId,
      consumerName: nextCase.consumerName,
      consumerEmail: nextCase.consumerEmail,
    });
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];
    setSelectedFile(file?.name || '');
    logEvent('dashboard_upload_selected', {
      area: 'Dashboard',
      page: '/dashboard',
      hasFile: Boolean(file),
      reportType: file?.type || '',
      reportSize: file?.size || 0,
    });
  }

  const displayName = firstName(caseData.consumerName);
  const trend = scoreTrend(caseData.scoreProgress);
  const findings = caseData.findings?.length ? caseData.findings : [];
  const documents = caseData.documents?.length ? caseData.documents : [];
  const waitingDocuments = documents.filter((doc) => doc.status === 'Needed').length;

  const bureauScores = useMemo(() => {
    const latestScore =
      caseData.scoreProgress?.[caseData.scoreProgress.length - 1]?.score ||
      caseData.healthScore ||
      640;

    return [
      {
        bureau: 'Experian',
        score: latestScore + 3,
        movement: trend >= 0 ? `+${Math.max(3, trend)}` : String(trend),
        status: 'Updated from latest report',
      },
      {
        bureau: 'Equifax',
        score: Math.max(300, latestScore - 6),
        movement: trend >= 0 ? `+${Math.max(2, trend - 2)}` : String(trend),
        status: 'Updated from latest report',
      },
      {
        bureau: 'TransUnion',
        score: latestScore + 8,
        movement: trend >= 0 ? `+${Math.max(4, trend + 1)}` : String(trend),
        status: 'Updated from latest report',
      },
    ];
  }, [caseData.healthScore, caseData.scoreProgress, trend]);

  const disputeStatuses = [
    ['Awaiting bureau response', Math.max(1, caseData.activeDisputes - 3), 'amber'],
    ['Needs your review', Math.max(1, waitingDocuments), 'blue'],
    ['Updated this week', Math.min(2, findings.length || 2), 'green'],
    ['Resolved or archived', 1, 'slate'],
  ];

  const nextSteps = [
    {
      title: 'Upload your newest credit report',
      detail: 'Your specialist can compare what changed across all three bureaus.',
      action: 'Upload',
      href: '/scan',
      priority: 'Action needed',
    },
    {
      title: 'Review dispute-ready findings',
      detail: 'Confirm report items before any next step is prepared.',
      action: 'Review',
      href: '/findings',
      priority: 'Due soon',
    },
    {
      title: 'Add identity support documents',
      detail: `${waitingDocuments || 2} document items can help support identity cleanup and verification.`,
      action: 'Open vault',
      href: '/vault',
      priority: 'Open',
    },
  ];

  return (
    <main className="cv-portal-shell">
      <nav className="cv-portal-nav" aria-label="Customer portal navigation">
        <BrandLogo />
        <div className="cv-portal-links">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/disputes">Disputes</Link>
          <Link href="/findings">Findings</Link>
          <Link href="/chat">Chat</Link>
          <Link href="/messages">Messages</Link>
          <Link href="/vault">Vault</Link>
        </div>
        <span className="cv-secure-chip">Secure portal</span>
      </nav>

      <section className="cv-dashboard-hero">
        <div>
          <span className="cv-eyebrow">Customer dashboard</span>
          <h1>Welcome back, {displayName}.</h1>
          <p>
            Case {caseData.caseId} is in {String(caseData.status).toLowerCase()}. Your
            dashboard shows score snapshots, active review items, and the next secure action.
          </p>
        </div>
        <div className="cv-hero-actions">
          <Link href="/messages" className="cv-secondary-link">Message support</Link>
          <Link href="/scan" className="cv-primary-link">Upload Report</Link>
        </div>
      </section>

      <section className="cv-score-section" aria-labelledby="bureau-scores">
        <div className="cv-section-heading">
          <div>
            <span className="cv-eyebrow">Credit score snapshot</span>
            <h2 id="bureau-scores">Three-bureau overview</h2>
          </div>
          <p>Scores update when a new report is reviewed. Results vary by bureau and model.</p>
        </div>

        <div className="cv-score-grid">
          {bureauScores.map((score) => (
            <Link href="/findings" className="cv-score-card" key={score.bureau}>
              <span>{score.bureau}</span>
              <strong>{score.score}</strong>
              <small>{score.movement} since first review</small>
              <em>{score.status}</em>
            </Link>
          ))}
        </div>
      </section>

      <section className="cv-dashboard-grid">
        <div className="cv-dashboard-main">
          <article className="cv-card cv-dashboard-card">
            <div className="cv-card-heading">
              <div>
                <span className="cv-eyebrow">Active disputes</span>
                <h2>{caseData.activeDisputes} active review items</h2>
                <p>{caseData.potentialIssues} possible report issues are organized for review.</p>
              </div>
              <Link href="/disputes" className="cv-small-action">View Dispute Status</Link>
            </div>

            <div className="cv-status-grid">
              {disputeStatuses.map(([label, value, tone]) => (
                <div className={`cv-status-card ${tone}`} key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </article>

          <article className="cv-card cv-dashboard-card">
            <div className="cv-card-heading">
              <div>
                <span className="cv-eyebrow">Next steps</span>
                <h2>Your action list</h2>
              </div>
              <span className="cv-secure-chip">Client approval required</span>
            </div>

            <div className="cv-next-list">
              {nextSteps.map((step) => (
                <Link href={step.href} className="cv-next-row" key={step.title}>
                  <span>
                    <strong>{step.title}</strong>
                    <small>{step.detail}</small>
                  </span>
                  <em>{step.priority}</em>
                  <b>{step.action}</b>
                </Link>
              ))}
            </div>
          </article>

          <article className="cv-card cv-dashboard-card">
            <div className="cv-card-heading">
              <div>
                <span className="cv-eyebrow">Recent activity</span>
                <h2>Progress log</h2>
              </div>
              <Link href="/events" className="cv-small-action">Open event log</Link>
            </div>

            <div className="cv-activity-list">
              {caseData.updates.map((update) => (
                <div className="cv-activity-item" key={`${update.time}-${update.title}`}>
                  <span aria-hidden="true" />
                  <div>
                    <strong>{update.title}</strong>
                    <p>{update.body}</p>
                    <small>{update.channel} - {update.time}</small>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </div>

        <aside className="cv-dashboard-side">
          <article className="cv-card cv-upload-card">
            <div className="cv-card-heading">
              <div>
                <span className="cv-eyebrow">Secure upload</span>
                <h2>Add a new credit report</h2>
              </div>
            </div>

            <label className="cv-upload-drop">
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
              <strong>{selectedFile || 'Choose a file to upload'}</strong>
              <span>PDF, JPG, and PNG files are accepted.</span>
              <small>Only upload your own credit report through this secure workflow.</small>
            </label>

            <Link href="/scan" className="cv-primary-link cv-full-action">Continue Upload</Link>
            <p className="cv-security-note">
              Do not upload bureau passwords or unrelated identity documents here. Use the Vault
              for identity support files.
            </p>
          </article>

          <article className="cv-card cv-dashboard-card">
            <span className="cv-eyebrow">Document readiness</span>
            <h2>Required documents</h2>
            <div className="cv-doc-list">
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.name}>
                  <span>
                    <strong>{doc.name}</strong>
                    <small>{doc.type}</small>
                  </span>
                  <em>{doc.status}</em>
                </div>
              ))}
            </div>
            <Link href="/vault" className="cv-small-action cv-side-link">Open secure vault</Link>
          </article>

          <article className="cv-card cv-dashboard-card">
            <span className="cv-eyebrow">Demo case switcher</span>
            <h2>Test consumers</h2>
            <div className="cv-case-list">
              {cases.map((item) => (
                <button
                  key={item.caseId}
                  type="button"
                  onClick={() => switchCase(item)}
                  className={item.caseId === caseData.caseId ? 'active' : ''}
                >
                  <strong>{item.consumerName}</strong>
                  <span>{item.consumerEmail}</span>
                </button>
              ))}
            </div>
          </article>
        </aside>
      </section>
    </main>
  );
}
