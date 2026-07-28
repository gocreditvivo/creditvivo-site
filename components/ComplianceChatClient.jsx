'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import BrandLogo from './BrandLogo';
import { logEvent } from './eventLog';

const QA_STORAGE_KEY = 'creditvivo_chat_saved_qa';

const starterQuestions = [
  'Look up status for CV-DEMO-1001',
  'Look up customer Maria Lopez',
  'What is Jayden Smith account status?',
  'What happens after I upload my credit report?',
  'Can I dispute credit report errors myself?',
  'What documents might Credit Vivo need?',
  'How does Credit Vivo handle collections?',
  'Why do results vary?',
  'When should something go to attorney review?',
];

const sourceLabels = {
  'ftc.gov': 'FTC',
  'consumerfinance.gov': 'CFPB',
  'consumer.ftc.gov': 'FTC Consumer Advice',
};

function getSourceLabel(url) {
  try {
    const host = new URL(url).hostname.replace(/^www\./, '');
    return sourceLabels[host] || host;
  } catch {
    return 'Source';
  }
}

const shell = {
  fontFamily: 'var(--cv-font)',
  background: 'linear-gradient(180deg, #fffdf5 0%, #f0fdf4 48%, #eef9ff 100%)',
  color: '#102033',
  minHeight: '100vh',
  padding: '34px 7% 70px',
};

const card = {
  background: 'rgba(255,255,255,.94)',
  border: '1px solid #cfeee0',
  borderRadius: 8,
  padding: 22,
  boxShadow: '0 18px 42px rgba(16,32,51,.09)',
};

const button = {
  border: 0,
  borderRadius: 8,
  padding: '12px 15px',
  fontWeight: 900,
  cursor: 'pointer',
  background: '#0f766e',
  color: 'white',
};

export default function ComplianceChatClient() {
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [defaultQa, setDefaultQa] = useState([]);
  const [savedQa, setSavedQa] = useState([]);
  const [thread, setThread] = useState([
    {
      role: 'assistant',
      text: 'Hi, I am the Credit Vivo compliance assistant. I can explain the portal, uploads, findings, disputes, documents, and safe next steps. I cannot give legal advice or promise results.',
      nextStep: 'Ask a question or choose a starter question.',
      status: 'ok',
      suggestions: ['Look up my case status', 'What should I upload next?', 'Explain Credit Vivo simply'],
    },
  ]);

  const hasBlocked = useMemo(() => thread.some((item) => item.status === 'blocked'), [thread]);

  useEffect(() => {
    try {
      const saved = JSON.parse(window.localStorage.getItem(QA_STORAGE_KEY) || '[]');
      setSavedQa(Array.isArray(saved) ? saved.slice(0, 8) : []);
    } catch {
      setSavedQa([]);
    }

    fetch('/api/chatbot')
      .then((response) => response.json())
      .then((data) => setDefaultQa(Array.isArray(data.defaultQa) ? data.defaultQa : []))
      .catch(() => setDefaultQa([]));
  }, []);

  function storeQa(question, answerData) {
    const nextEntry = {
      id: `${Date.now()}`,
      question,
      answer: answerData.answer || '',
      topic: answerData.topic || answerData.status || 'Credit Vivo AI',
      status: answerData.status || 'ok',
      nextStep: answerData.nextStep || '',
      sources: answerData.sources || [],
    };

    setSavedQa((current) => {
      const deduped = current.filter((item) => item.question.toLowerCase() !== question.toLowerCase());
      const updated = [nextEntry, ...deduped].slice(0, 8);
      window.localStorage.setItem(QA_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }

  function clearSavedQa() {
    window.localStorage.removeItem(QA_STORAGE_KEY);
    setSavedQa([]);
  }

  async function askChatbot(nextMessage) {
    const clean = String(nextMessage || message).trim();
    if (!clean || busy) return;

    setMessage('');
    setBusy(true);
    setThread((current) => [...current, { role: 'user', text: clean }]);
    logEvent('chatbot_question_submitted', {
      area: 'Compliance Chat',
      notesLength: clean.length,
    });

    try {
      const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: clean }),
      });
      const data = await response.json();
      storeQa(clean, data);
      setThread((current) => [
        ...current,
        {
          role: 'assistant',
          text: data.answer || 'I could not answer that safely. Please ask staff to review.',
          nextStep: data.nextStep || '',
          status: data.status || 'ok',
          topic: data.topic || '',
          sources: data.sources || [],
          suggestions: data.suggestions || [],
          guard: data.guard,
        },
      ]);
      logEvent('chatbot_answer_returned', {
        area: 'Compliance Chat',
        status: data.status || 'ok',
      });
    } catch {
      setThread((current) => [
        ...current,
        {
          role: 'assistant',
          text: 'The chatbot service is unavailable right now. Please try again or contact staff.',
          nextStep: 'Use the portal navigation for upload, findings, or messages.',
          status: 'error',
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    askChatbot();
  }

  return (
    <main style={shell}>
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, marginBottom: 30, background: 'rgba(255,255,255,.78)', border: '1px solid #cfeee0', borderRadius: 8, padding: '12px 14px', boxShadow: '0 12px 28px rgba(16,32,51,.06)' }}>
        <BrandLogo />
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/scan">Upload</Link>
          <Link href="/findings">Findings</Link>
          <Link href="/messages">Messages</Link>
          <Link href="/faq">FAQ</Link>
        </div>
      </nav>

      <section style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(300px,.42fr)', gap: 20, alignItems: 'start' }}>
        <div>
          <p className="cv-status-chip ready">Compliance guard active</p>
          <h1 style={{ fontSize: 42, lineHeight: 1.08, margin: '16px 0 10px' }}>Ask Credit Vivo safely.</h1>
          <p style={{ color: '#475569', fontSize: 17, lineHeight: 1.65, maxWidth: 820 }}>
            This assistant explains Credit Vivo steps in plain English and blocks unsafe credit repair claims. It does not provide legal advice, guarantee results, or collect sensitive documents in chat.
          </p>

          <section style={{ ...card, marginTop: 22, display: 'grid', gap: 14 }}>
            <div style={{ display: 'grid', gap: 12, maxHeight: 560, overflowY: 'auto', paddingRight: 4 }}>
              {thread.map((item, index) => (
                <article
                  key={`${item.role}-${index}`}
                  style={{
                    justifySelf: item.role === 'user' ? 'end' : 'start',
                    maxWidth: item.role === 'user' ? '78%' : '92%',
                    background: item.role === 'user' ? '#0f766e' : item.status === 'blocked' ? '#fef2f2' : '#f8fafc',
                    color: item.role === 'user' ? 'white' : '#102033',
                    border: item.status === 'blocked' ? '1px solid #fecaca' : '1px solid #dbeafe',
                    borderRadius: 8,
                    padding: 14,
                    lineHeight: 1.55,
                    whiteSpace: 'pre-line',
                  }}
                >
                  <strong>{item.role === 'user' ? 'You' : 'Credit Vivo AI'}</strong>
                  {item.topic && (
                    <span style={{ marginLeft: 8, color: '#64748b', fontSize: 12, fontWeight: 800 }}>
                      {item.topic}
                    </span>
                  )}
                  <p style={{ margin: '8px 0 0' }}>{item.text}</p>
                  {item.nextStep && <p style={{ margin: '10px 0 0', color: item.role === 'user' ? 'white' : '#047857', fontWeight: 900 }}>Next: {item.nextStep}</p>}
                  {item.sources?.length > 0 && (
                    <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      {item.sources.map((source) => (
                        <a
                          key={source}
                          href={source}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            border: '1px solid #bae6fd',
                            borderRadius: 8,
                            color: '#0369a1',
                            background: '#f0f9ff',
                            padding: '5px 8px',
                            fontSize: 12,
                            fontWeight: 900,
                            textDecoration: 'none',
                          }}
                        >
                          {getSourceLabel(source)}
                        </a>
                      ))}
                    </div>
                  )}
                  {item.suggestions?.length > 0 && (
                    <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      {item.suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          type="button"
                          onClick={() => askChatbot(suggestion)}
                          style={{
                            border: '1px solid #bbf7d0',
                            borderRadius: 8,
                            color: '#047857',
                            background: 'white',
                            padding: '6px 9px',
                            fontSize: 12,
                            fontWeight: 900,
                            cursor: 'pointer',
                          }}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) auto', gap: 10, borderTop: '1px solid #dff4e9', paddingTop: 14 }}>
              <input
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Tell me what is going on: account status, upload, dispute, collection, score, pricing..."
                maxLength={1200}
                style={{ border: '1px solid #cbd5e1', borderRadius: 8, padding: 13, minWidth: 0 }}
              />
              <button type="submit" disabled={busy} style={{ ...button, opacity: busy ? .7 : 1 }}>{busy ? 'Checking...' : 'Ask'}</button>
            </form>
          </section>
        </div>

        <aside style={{ display: 'grid', gap: 16 }}>
          <section style={card}>
            <h2 style={{ marginTop: 0 }}>Default Q&A</h2>
            <div style={{ display: 'grid', gap: 8 }}>
              {[...starterQuestions, ...defaultQa.map((item) => item.question)].slice(0, 8).map((question) => (
                <button
                  key={question}
                  type="button"
                  onClick={() => askChatbot(question)}
                  style={{ textAlign: 'left', border: '1px solid #dbeafe', background: '#f8fafc', borderRadius: 8, padding: 12, cursor: 'pointer', color: '#102033', fontWeight: 800 }}
                >
                  {question}
                </button>
              ))}
            </div>
          </section>

          <section style={{ ...card, background: '#f8fafc' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
              <h2 style={{ margin: 0 }}>Saved Q&A</h2>
              {savedQa.length > 0 && (
                <button type="button" onClick={clearSavedQa} style={{ border: '1px solid #cbd5e1', borderRadius: 8, background: 'white', padding: '7px 9px', cursor: 'pointer', fontWeight: 800 }}>
                  Clear
                </button>
              )}
            </div>
            <div style={{ display: 'grid', gap: 10, marginTop: 12 }}>
              {savedQa.length === 0 && (
                <p style={{ color: '#64748b', lineHeight: 1.55, margin: 0 }}>
                  Tested chatbot questions will save here on this device.
                </p>
              )}
              {savedQa.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => askChatbot(item.question)}
                  style={{ textAlign: 'left', border: '1px solid #dbeafe', background: 'white', borderRadius: 8, padding: 12, cursor: 'pointer', color: '#102033' }}
                >
                  <strong style={{ display: 'block', marginBottom: 4 }}>{item.question}</strong>
                  <span style={{ color: ['blocked', 'not_found'].includes(item.status) ? '#b91c1c' : '#047857', fontSize: 12, fontWeight: 900 }}>
                    {item.topic}
                  </span>
                </button>
              ))}
            </div>
          </section>

          <section style={{ ...card, background: hasBlocked ? '#fef2f2' : '#fffbeb' }}>
            <h2 style={{ marginTop: 0 }}>Guardrails</h2>
            <ul style={{ color: '#475569', lineHeight: 1.7, paddingLeft: 20 }}>
              <li>No guaranteed removals, approvals, score increases, or timelines.</li>
              <li>No legal advice or lawsuit predictions.</li>
              <li>No help with false disputes or CPN/new identity requests.</li>
              <li>No SSNs, full DOBs, ID numbers, bureau passwords, or payment data in chat.</li>
            </ul>
          </section>

          <section style={{ ...card, background: '#ecfdf5' }}>
            <h2 style={{ marginTop: 0 }}>Staff Review</h2>
            <p style={{ color: '#047857', lineHeight: 1.6 }}>
              If a customer asks about identity theft, legal rights, debt collector conduct, attorney escalation, or sensitive documents, route the issue to human review before action.
            </p>
          </section>
        </aside>
      </section>
    </main>
  );
}
