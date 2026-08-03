import { ArrowRight, CheckCircle, Gauge, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react';
import type { ScannerParseResult } from '../lib/scannerApi';
import {
  buildCreditBlockers,
  buildSimulatorScenarios,
  getScoreProfile,
  getScoreProgress,
  type CreditBlocker,
} from '../lib/creditComebackSimulator';

type Props = {
  result: ScannerParseResult | null;
  compact?: boolean;
};

function RangePill({ range }: { range: [number, number] }) {
  const [low, high] = range;
  const label = high <= 0 ? 'Build scan first' : `+${low} to +${high} pts`;

  return (
    <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-extrabold text-emerald-700 ring-1 ring-emerald-100">
      {label}
    </span>
  );
}

function ImpactBadge({ level }: { level: CreditBlocker['impactLevel'] }) {
  const classes =
    level === 'Very High'
      ? 'bg-rose-50 text-rose-700 ring-rose-100'
      : level === 'High'
        ? 'bg-amber-50 text-amber-700 ring-amber-100'
        : level === 'Medium'
          ? 'bg-sky-50 text-sky-700 ring-sky-100'
          : 'bg-navy-50 text-navy-500 ring-navy-100';

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wide ring-1 ${classes}`}>
      {level} impact
    </span>
  );
}

export default function CreditComebackSimulator({ result, compact = false }: Props) {
  const profile = getScoreProfile();
  const progress = getScoreProgress(profile);
  const blockers = buildCreditBlockers(result);
  const scenarios = buildSimulatorScenarios(blockers);
  const topBlockers = blockers.slice(0, compact ? 3 : 5);

  return (
    <section className="overflow-hidden rounded-2xl border border-emerald-100 bg-white shadow-sm shadow-emerald-900/5">
      <div className="bg-gradient-to-br from-navy-950 via-navy-900 to-emerald-950 p-5 text-white sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="mb-2 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-extrabold uppercase tracking-widest text-emerald-100 ring-1 ring-white/10">
              <Sparkles size={13} /> Credit Comeback Simulator
            </p>
            <h2 className="text-2xl font-extrabold leading-tight sm:text-3xl">
              See what may be holding your FICO score back.
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Credit Vivo ties your scanner findings to a score-impact view so you can see your top credit blockers, possible score movement, and next best action.
            </p>
          </div>

          <div className="rounded-xl border border-white/10 bg-white/10 p-4 backdrop-blur lg:min-w-[260px]">
            <div className="mb-3 flex items-center justify-between text-xs font-semibold text-slate-300">
              <span>Possible comeback progress</span>
              <span>{progress.currentProgress}%</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-white/15">
              <div
                className="h-full rounded-full bg-emerald-300 transition-all duration-700"
                style={{ width: `${progress.currentProgress}%` }}
              />
            </div>
            <p className="mt-3 text-[11px] leading-5 text-slate-300">
              +{progress.gained} points tracked toward a {profile.goalScore} goal. {progress.remaining} points to go.
            </p>
          </div>
        </div>
      </div>

      <div className="p-5 sm:p-6">
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {[
            { label: 'Starting score', value: profile.startingScore, icon: Gauge },
            { label: 'Current score', value: profile.currentScore, icon: TrendingUp },
            { label: 'Goal score', value: profile.goalScore, icon: CheckCircle },
            { label: 'Possible path', value: '100 pts', icon: Sparkles },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="rounded-xl border border-navy-100 bg-navy-50/40 p-4">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-white text-emerald-700 shadow-sm">
                <Icon size={17} />
              </div>
              <p className="text-2xl font-extrabold text-navy-950">{value}</p>
              <p className="mt-1 text-[11px] font-semibold uppercase tracking-wide text-navy-400">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="rounded-xl border border-navy-100 bg-white p-5">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-extrabold text-navy-950">Top credit blockers</h3>
                <p className="mt-1 text-xs leading-5 text-navy-500">
                  Ranked from your scanner findings by possible score impact, severity, bureau coverage, and review strength.
                </p>
              </div>
              <RangePill range={scenarios[3]?.range || [0, 0]} />
            </div>

            {topBlockers.length ? (
              <div className="space-y-3">
                {topBlockers.map((item) => (
                  <div key={item.id} className="rounded-xl border border-navy-100 bg-navy-50/40 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-extrabold text-navy-900">{item.accountName}</p>
                        <p className="mt-1 text-xs text-navy-500">
                          {item.bureau} • {item.accountType} • {item.status}
                        </p>
                      </div>
                      <ImpactBadge level={item.impactLevel} />
                    </div>

                    <p className="mt-3 text-sm leading-6 text-navy-700">{item.reason}</p>

                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <RangePill range={item.possibleRange} />
                      <span className="rounded-full bg-white px-3 py-1 text-[11px] font-bold text-navy-500 ring-1 ring-navy-100">
                        Next: {item.nextAction}
                      </span>
                    </div>

                    {item.supportingSignals.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {item.supportingSignals.map((signal) => (
                          <span key={signal} className="rounded-md bg-white px-2 py-1 text-[10px] font-semibold text-navy-500 ring-1 ring-navy-100">
                            {signal}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-navy-200 bg-navy-50/40 p-6 text-center">
                <p className="text-sm font-bold text-navy-800">Run your first scan to unlock score-impact estimates.</p>
                <p className="mt-2 text-xs leading-5 text-navy-500">
                  The simulator is powered by scanner findings, not random guesses.
                </p>
              </div>
            )}
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border border-emerald-100 bg-emerald-50/60 p-5">
              <h3 className="text-sm font-extrabold text-navy-950">What-if scenarios</h3>
              <div className="mt-4 space-y-3">
                {scenarios.map((scenario) => (
                  <div key={scenario.id} className="rounded-lg bg-white p-4 ring-1 ring-emerald-100">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-extrabold text-navy-900">{scenario.label}</p>
                      <RangePill range={scenario.range} />
                    </div>
                    <p className="mt-2 text-[11px] leading-5 text-navy-500">{scenario.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-navy-100 bg-white p-5">
              <div className="mb-3 flex items-center gap-2">
                <ShieldCheck size={16} className="text-sky-600" />
                <h3 className="text-sm font-extrabold text-navy-950">How to read this</h3>
              </div>
              <p className="text-xs leading-6 text-navy-500">
                These are estimated score-impact ranges based on public scoring factors and Credit Vivo scanner data. The exact FICO formula is proprietary, so this tool is designed to guide priorities, not promise a fixed score change.
              </p>
            </div>

            {!compact && (
              <a href="/findings" className="flex items-center justify-center gap-2 rounded-xl bg-navy-950 px-5 py-3 text-sm font-extrabold text-white shadow-lg shadow-navy-900/20 transition hover:-translate-y-0.5 hover:bg-navy-900">
                Review scanner findings
                <ArrowRight size={15} />
              </a>
            )}
          </aside>
        </div>
      </div>
    </section>
  );
}
