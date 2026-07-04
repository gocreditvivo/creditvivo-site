"use client";

import { useMemo, useState } from "react";

type ScanResult = {
  result?: {
    summary?: {
      totalTradelines: number;
      negativeTradelines: number;
      issuesFound: number;
      needsAdminReview: number;
    };
    selfCheck?: {
      overallStatus: string;
      warnings: string[];
    };
    negativeTradelines?: Array<{
      creditorName: string;
      bureau: string;
      negativeReason?: string;
      confidenceScore: number;
    }>;
    issues?: Array<{
      issueType: string;
      plainEnglishFinding: string;
      recommendedAction: string;
      disputeStrengthScore: number;
    }>;
  };
  error?: string;
};

const sampleText = `Experian Credit Report

Account Name: MIDLAND CREDIT MANAGEMENT
Account Number: ****8933
Account Type: Collection
Status: Collection Account
Balance: $1,473
Date Opened: 02/17/2022
Date Reported: 06/25/2026
Remarks: Account placed for collection

Equifax Credit Report

CREDIT ONE BANK
Account Number: *6902
Account Type: Credit Card
Status: Charged off as bad debt
Balance: $488
Past Due: $60
Date Opened: 12/27/2022
Date Reported: 03/11/2026
Payment History: 30 days late as of Aug 2023`;

export function CVBrainUploadTester() {
  const [rawText, setRawText] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const canRun = useMemo(() => rawText.trim().length >= 40, [rawText]);

  async function runScan() {
    if (!canRun) return;
    setIsRunning(true);
    setResult(null);
    try {
      const response = await fetch("/api/reports/parse-tradelines", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rawText }),
      });
      const payload = await response.json();
      setResult(payload);
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Scanner request failed." });
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="mt-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-sm">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <p className="text-sm font-bold text-emerald-700">CV Brain Scanner API Test</p>
          <h2 className="mt-2 text-2xl font-black text-slate-950">Run extracted text through the scanner layer</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            This browser test accepts extracted report text only. Real PDF parsing remains in the approved FastAPI scanner backend with admin review and production gates.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setRawText(sampleText)}
          className="rounded-full border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50"
        >
          Load synthetic test
        </button>
      </div>

      <textarea
        value={rawText}
        onChange={(event) => setRawText(event.target.value)}
        placeholder="Paste extracted credit report text here for CV Brain route testing."
        className="mt-5 min-h-56 w-full rounded-2xl border border-slate-200 p-4 text-sm leading-6 text-slate-800 outline-none focus:border-emerald-500"
      />

      <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center">
        <button
          type="button"
          disabled={!canRun || isRunning}
          onClick={runScan}
          className="rounded-full bg-slate-950 px-5 py-3 text-sm font-bold text-white disabled:bg-slate-300"
        >
          {isRunning ? "Running scanner..." : "Run CV Brain scan"}
        </button>
        <p className="text-xs leading-5 text-slate-500">
          Draft review only. No disputes, letters, mail, complaints, or legal escalation are sent from this test.
        </p>
      </div>

      {result?.error ? (
        <div className="mt-5 rounded-2xl border border-red-100 bg-red-50 p-4 text-sm font-semibold text-red-700">{result.error}</div>
      ) : null}

      {result?.result ? (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl bg-slate-50 p-4">
            <h3 className="font-bold text-slate-950">Self-check</h3>
            <p className="mt-2 text-sm text-slate-700">Status: {result.result.selfCheck?.overallStatus || "unknown"}</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              {(result.result.selfCheck?.warnings || ["No warnings returned."]).map((warning) => (
                <li key={warning}>- {warning}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <h3 className="font-bold text-slate-950">Summary</h3>
            <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
              {Object.entries(result.result.summary || {}).map(([key, value]) => (
                <div key={key}>
                  <dt className="text-slate-500">{key}</dt>
                  <dd className="font-black text-slate-950">{String(value)}</dd>
                </div>
              ))}
            </dl>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 lg:col-span-2">
            <h3 className="font-bold text-slate-950">Negative tradelines detected</h3>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(result.result.negativeTradelines || []).map((line) => (
                <div key={`${line.bureau}-${line.creditorName}-${line.negativeReason}`} className="rounded-xl bg-white p-3 text-sm">
                  <p className="font-bold text-slate-950">{line.creditorName}</p>
                  <p className="text-slate-600">{line.bureau} / {line.negativeReason || "review signal"} / confidence {line.confidenceScore}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
