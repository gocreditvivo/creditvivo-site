"use client";

import { useMemo, useState } from "react";
import type { ImpactEstimate, ScannerNegativeAccount, ScoreProfile } from "@/types/score-simulator";
import {
  buildScoreSummary,
  describeNextAction,
  estimateAllImpacts,
  estimateScenario,
} from "@/lib/score-impact-engine";

type Props = {
  profile: ScoreProfile;
  accounts: ScannerNegativeAccount[];
};

type ScenarioMode = "selected" | "all" | "utilization";

function cn(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function formatAction(action: ImpactEstimate["nextAction"]) {
  return describeNextAction(action);
}

function impactClass(level: string) {
  if (level === "very_high") return "bg-red-100 text-red-800";
  if (level === "high") return "bg-orange-100 text-orange-800";
  if (level === "medium") return "bg-amber-100 text-amber-800";
  return "bg-emerald-100 text-emerald-800";
}

function scoreTone(score: number) {
  if (score >= 740) return "Excellent path";
  if (score >= 670) return "Strong path";
  if (score >= 620) return "Rebuilding path";
  return "Comeback path";
}

function ScoreCard({ label, value, note, active }: { label: string; value: number; note: string; active?: boolean }) {
  return (
    <div className={cn("rounded-2xl border bg-white p-4", active ? "border-emerald-300 shadow-sm" : "border-slate-200")}>
      <p className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-4xl font-black text-slate-950">{value}</p>
      <p className="mt-2 text-sm text-slate-600">{note}</p>
    </div>
  );
}

export function CreditComebackSimulator({ profile, accounts }: Props) {
  const impacts = useMemo(() => estimateAllImpacts(accounts, profile), [accounts, profile]);
  const summary = useMemo(() => buildScoreSummary(profile, accounts), [accounts, profile]);
  const [selected, setSelected] = useState<string[]>(impacts.slice(0, 3).map((impact) => impact.accountId));
  const [scenarioMode, setScenarioMode] = useState<ScenarioMode>("selected");

  const selectedScenario = useMemo(
    () => estimateScenario("Selected credit blockers", selected, accounts, profile),
    [selected, accounts, profile],
  );

  const allScenario = useMemo(
    () => estimateScenario("All detected negative items", accounts.map((account) => account.id), accounts, profile),
    [accounts, profile],
  );

  const activeScenario = scenarioMode === "all"
    ? allScenario
    : scenarioMode === "utilization" && summary.utilizationScenario
      ? summary.utilizationScenario
      : selectedScenario;

  const goalDistance = Math.max(profile.goalScore - profile.currentScore, 0);
  const gained = Math.max(profile.currentScore - profile.startingScore, 0);
  const progressPct = Math.min(100, Math.max(0, (gained / Math.max(profile.goalScore - profile.startingScore, 1)) * 100));

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
    setScenarioMode("selected");
  };

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-black uppercase tracking-wide text-emerald-700">AI Credit Boost + Attorney Support</p>
            <h2 className="mt-2 text-3xl font-black tracking-tight text-slate-950 md:text-4xl">Your credit comeback starts here.</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 md:text-base">
              See what may be holding your FICO score back. Credit Vivo uses scanner findings, severity, recency, bureau coverage, utilization, and dispute strength to estimate possible score movement ranges.
            </p>
          </div>
          <div className="rounded-2xl bg-slate-950 p-4 text-white lg:min-w-72">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-200">Possible path</p>
            <p className="mt-2 text-3xl font-black">+{activeScenario.possibleMin} to +{activeScenario.possibleMax}</p>
            <p className="mt-2 text-sm leading-5 text-slate-200">Estimated range only. Results vary and accurate information may remain.</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <ScoreCard label="Where you started" value={profile.startingScore} note={scoreTone(profile.startingScore)} />
          <ScoreCard label="Where you are now" value={profile.currentScore} note={`${gained} points tracked so far`} active />
          <ScoreCard label="Goal score" value={profile.goalScore} note={`${goalDistance} points away`} />
        </div>

        <div className="mt-6">
          <div className="flex items-center justify-between gap-3 text-sm font-bold text-slate-700">
            <span>Move toward a stronger FICO score</span>
            <span>{Math.round(progressPct)}%</span>
          </div>
          <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-emerald-500" style={{ width: `${progressPct}%` }} />
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
          <p className="text-sm font-black uppercase tracking-wide text-blue-700">What-if simulator</p>
          <h3 className="mt-2 text-2xl font-black text-slate-950">{activeScenario.headline}</h3>
          <p className="mt-3 text-sm leading-6 text-slate-600">{activeScenario.explanation}</p>

          <div className="mt-5 grid gap-3">
            <button
              type="button"
              onClick={() => setScenarioMode("selected")}
              className={cn(
                "rounded-2xl border p-4 text-left",
                scenarioMode === "selected" ? "border-blue-500 bg-blue-50" : "border-slate-200 hover:bg-slate-50",
              )}
            >
              <p className="font-black text-slate-950">What if selected items are resolved?</p>
              <p className="mt-1 text-sm text-slate-600">Estimate selected scanner findings corrected, updated, or removed when appropriate.</p>
            </button>
            <button
              type="button"
              onClick={() => setScenarioMode("all")}
              className={cn(
                "rounded-2xl border p-4 text-left",
                scenarioMode === "all" ? "border-blue-500 bg-blue-50" : "border-slate-200 hover:bg-slate-50",
              )}
            >
              <p className="font-black text-slate-950">What if all detected negatives are resolved?</p>
              <p className="mt-1 text-sm text-slate-600">Estimate the full scanner-tied comeback path with diminishing returns.</p>
            </button>
            <button
              type="button"
              disabled={!summary.utilizationScenario}
              onClick={() => setScenarioMode("utilization")}
              className={cn(
                "rounded-2xl border p-4 text-left disabled:cursor-not-allowed disabled:opacity-50",
                scenarioMode === "utilization" ? "border-blue-500 bg-blue-50" : "border-slate-200 hover:bg-slate-50",
              )}
            >
              <p className="font-black text-slate-950">What if utilization drops below 30%?</p>
              <p className="mt-1 text-sm text-slate-600">Estimate revolving utilization improvement where scanner/account data supports it.</p>
            </button>
          </div>

          <div className="mt-5 rounded-2xl bg-amber-50 p-4 text-sm leading-6 text-amber-900">
            This simulator does not reproduce the exact FICO formula. It estimates possible movement from public scoring factors and Credit Vivo scanner findings.
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-blue-700">Top credit blockers</p>
              <h3 className="mt-2 text-2xl font-black text-slate-950">Ranked by estimated impact</h3>
            </div>
            <button
              type="button"
              onClick={() => {
                setSelected(impacts.slice(0, 5).map((impact) => impact.accountId));
                setScenarioMode("selected");
              }}
              className="rounded-full bg-slate-950 px-4 py-2 text-sm font-bold text-white hover:bg-slate-800"
            >
              Select top 5
            </button>
          </div>

          <div className="mt-5 space-y-3">
            {impacts.map((impact, index) => {
              const account = accounts.find((item) => item.id === impact.accountId);
              if (!account) return null;
              const checked = selected.includes(account.id);

              return (
                <button
                  key={account.id}
                  type="button"
                  onClick={() => toggle(account.id)}
                  className={cn(
                    "w-full rounded-2xl border p-4 text-left transition",
                    checked ? "border-blue-500 bg-blue-50" : "border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/40",
                  )}
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-full bg-slate-950 px-2.5 py-1 text-xs font-black text-white">#{index + 1}</span>
                        <span className="text-lg font-black text-slate-950">{account.creditorName}</span>
                        <span className={cn("rounded-full px-3 py-1 text-xs font-black capitalize", impactClass(impact.impactLevel))}>
                          {impact.impactLevel.replace("_", " ")}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-slate-600">
                        {account.accountType.replaceAll("_", " ")} / {account.bureaus.join(", ")}
                      </p>
                    </div>
                    <div className="rounded-2xl bg-white px-4 py-3 text-center shadow-sm">
                      <p className="text-xs font-bold text-slate-500">Estimated range</p>
                      <p className="text-xl font-black text-slate-950">+{impact.possibleMin} to +{impact.possibleMax}</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{impact.explanation}</p>
                  <p className="mt-3 text-sm font-black text-blue-800">Next: {formatAction(impact.nextAction)}</p>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
        <p className="text-sm font-black uppercase tracking-wide text-emerald-700">What Credit Vivo is doing next</p>
        <div className="mt-4 grid gap-3 md:grid-cols-5">
          {["Review account", "Build dispute", "Upload document", "Reduce utilization", "Attorney Support"].map((action) => (
            <div key={action} className="rounded-2xl bg-slate-50 p-4">
              <p className="font-black text-slate-950">{action}</p>
              <p className="mt-2 text-sm leading-5 text-slate-600">Customer approval, admin review, and compliance review stay required where applicable.</p>
            </div>
          ))}
        </div>
        <p className="mt-5 text-sm leading-6 text-slate-600">
          Find errors. Build disputes. See results. All score movement is estimated, results vary, and Credit Vivo does not guarantee score increases, deletions, approvals, or legal outcomes.
        </p>
      </div>
    </section>
  );
}
