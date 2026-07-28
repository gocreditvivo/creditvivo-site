'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import BrandLogo from './BrandLogo';
import { demoCase } from './demoCase';
import { logEvent } from './eventLog';

const STORAGE_KEY = 'creditVivoDemoCase';

const shell = { fontFamily: 'var(--cv-font)', background: 'linear-gradient(180deg, #fffdf5 0%, #f0fdf4 48%, #eef9ff 100%)', minHeight: '100vh', color: '#102033', padding: '32px 7% 70px' };
const card = { background: 'rgba(255,255,255,.94)', border: '1px solid #cfeee0', borderRadius: 8, padding: 20, boxShadow: '0 18px 42px rgba(16,32,51,.09)' };
const button = { border: 0, borderRadius: 8, padding: '11px 14px', fontWeight: 900, cursor: 'pointer', background: 'linear-gradient(135deg, #0f766e, #12b981)', color: 'white', boxShadow: '0 14px 28px rgba(18,185,129,.24)' };

function getCase() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || demoCase;
  } catch {
    return demoCase;
  }
}

function downloadFindings(caseData) {
  const exportData = {
    exportedAt: new Date().toISOString(),
    caseId: caseData.caseId,
    consumerName: caseData.consumerName,
    consumerEmail: caseData.consumerEmail,
    status: caseData.status,
    findings: caseData.findings || [],
  };
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `credit-vivo-findings-${caseData.caseId || new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function FindingsClient() {
  const [caseData, setCaseData] = useState(demoCase);

  useEffect(() => {
    const loadedCase = getCase();
    setCaseData(loadedCase);
    logEvent('page_viewed', {
      area: 'Findings',
      page: '/findings',
      caseId: loadedCase.caseId,
      consumerName: loadedCase.consumerName,
      consumerEmail: loadedCase.consumerEmail,
      findingCount: loadedCase.findings?.length || 0,
    });
  }, []);

  return (
    <main style={shell}>
      <nav style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 28, alignItems: 'center', background: 'rgba(255,255,255,.78)', border: '1px solid #cfeee0', borderRadius: 8, padding: '12px 14px', boxShadow: '0 12px 28px rgba(16,32,51,.06)' }}>
        <BrandLogo />
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/scan">Upload</Link>
          <Link href="/chat">Chat</Link>
          <Link href="/messages">Messages</Link>
          <Link href="/monthly">Monthly</Link>
          <Link href="/vault">Vault</Link>
          <Link href="/disputes">Disputes</Link>
        </div>
      </nav>

      <section style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', gap: 16, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ fontSize: 42, marginBottom: 8 }}>Findings</h1>
          <p style={{ color: '#475569', maxWidth: 760, lineHeight: 1.65 }}>
            This is the customer view. It explains possible problems without showing raw forensic scanner logs, Metro 2 internals, or legal conclusions.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            downloadFindings(caseData);
            logEvent('findings_downloaded', {
              area: 'Findings',
              caseId: caseData.caseId,
              findingCount: caseData.findings?.length || 0,
            });
          }}
          style={button}
        >
          Download Findings
        </button>
      </section>

      <section style={{ display: 'grid', gap: 16, marginTop: 24 }}>
        {caseData.findings.map((finding) => (
          <article key={finding.id} style={card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
              <div>
                <h2 style={{ margin: '0 0 8px' }}>{finding.account}</h2>
                <p style={{ margin: 0, color: '#475569' }}>{finding.category}</p>
              </div>
              <span style={{ alignSelf: 'start', background: finding.severity.includes('Very') ? '#fee2e2' : '#fef3c7', color: finding.severity.includes('Very') ? '#991b1b' : '#92400e', borderRadius: 999, padding: '7px 11px', fontWeight: 900 }}>{finding.severity}</span>
            </div>
            <p style={{ color: '#111827', lineHeight: 1.65 }}>{finding.customerSummary}</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 12 }}>
              <div style={{ background: '#eef9ff', borderRadius: 8, padding: 14 }}><strong>Bureau view</strong><p style={{ color: '#475569' }}>{finding.bureauView}</p></div>
              <div style={{ background: '#ecfdf5', borderRadius: 8, padding: 14 }}><strong>Recommended action</strong><p style={{ color: '#047857' }}>{finding.nextStep}</p></div>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
