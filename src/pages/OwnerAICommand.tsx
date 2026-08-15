import { useEffect, useMemo, useState } from 'react';
import { authenticatedFetch } from '../lib/authenticatedFetch';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Clock,
  Database,
  DollarSign,
  RefreshCcw,
  ShieldCheck,
  Target,
  TrendingUp,
  Wifi,
} from 'lucide-react';

type FetchState = 'loading' | 'live' | 'fallback';

type GrowthBrief = {
  revenue_goal?: {
    monthly_target?: number;
    current_mrr?: number;
    paid_customer_gap?: number;
  };
  growth_brief?: {
    snapshot?: {
      visitors?: number;
      leads?: number;
      free_scans_started?: number;
      free_scans_completed?: number;
      paid_customers?: number;
      monthly_recurring_revenue?: number;
      cancellations?: number;
      ad_spend?: number;
    };
    million_month_target?: {
      monthly_goal?: number;
      paid_customers_needed?: number;
      paid_customer_gap?: number;
      blended_arpu?: number;
    };
    recommended_actions?: Array<{ issue: string; insight: string; action: string }>;
  };
  operator_brief?: {
    actions?: Array<{
      area: string;
      event_type: string;
      severity: string;
      recommended_action: string;
      approval_required: boolean;
    }>;
  };
  top_actions?: Array<{
    mission: string;
    priority: string;
    issue: string;
    recommended_action: string;
    approval_required: boolean;
  }>;
};

type LiveAccessBrief = {
  counts?: {
    tools?: number;
    by_priority?: Record<string, number>;
    by_category?: Record<string, number>;
  };
  first_30_day_setup_order?: string[];
  approval_rules?: string[];
};

type CrossAiBrief = {
  directives?: Array<{
    ai_name: string;
    owner_brief_line: string;
    alert_growth_ai_when: string[];
  }>;
  weekly_growth_command_questions?: string[];
};

type AdBrief = {
  counts?: {
    channels?: number;
    ad_creatives?: number;
    creative_by_channel?: Record<string, number>;
  };
  launch_sequence?: string[];
};

type ProblemBrief = {
  example_questions?: string[];
};

type ForensicSearchResult = {
  query?: string;
  owner_brief?: {
    best_first_search?: string;
    why?: string;
    campaign_to_use?: string;
    next_action?: string;
    verification?: string;
  };
  selected_lanes?: Array<{
    name: string;
    purpose: string;
    campaign_mapping: string;
  }>;
};

type DashboardData = {
  command: GrowthBrief | null;
  liveAccess: LiveAccessBrief | null;
  crossAi: CrossAiBrief | null;
  ads: AdBrief | null;
  problemSolver: ProblemBrief | null;
};

const fallbackData: DashboardData = {
  command: {
    revenue_goal: { monthly_target: 1000000, current_mrr: 0, paid_customer_gap: 10527 },
    growth_brief: {
      snapshot: {
        visitors: 0,
        leads: 0,
        free_scans_started: 0,
        free_scans_completed: 0,
        paid_customers: 0,
        monthly_recurring_revenue: 0,
        cancellations: 0,
        ad_spend: 0,
      },
      million_month_target: {
        monthly_goal: 1000000,
        paid_customers_needed: 10527,
        paid_customer_gap: 10527,
        blended_arpu: 95,
      },
      recommended_actions: [
        {
          issue: 'Live tracking not connected yet',
          insight: 'Growth AI can plan, but it needs live website, scanner, payment, ad, and referral data to learn.',
          action: 'Connect event tracking, Supabase, Render cron jobs, GA4, Search Console, Stripe, and Google Ads reporting.',
        },
      ],
    },
    top_actions: [
      {
        mission: 'Growth AI',
        priority: 'revenue_growth',
        issue: 'Tracking foundation',
        recommended_action: 'Connect live data so Growth AI can report real customer movement.',
        approval_required: false,
      },
    ],
  },
  liveAccess: {
    counts: { tools: 13, by_priority: { phase_1_must_have: 6 }, by_category: {} },
    first_30_day_setup_order: [
      'Credit Vivo first-party event tracking',
      'Supabase Postgres',
      'Render Cron Jobs',
      'Google Analytics 4 Data API',
      'Google Search Console API',
      'Stripe API and webhooks',
      'Google Ads API read-only reporting',
      'SendGrid founder daily brief',
    ],
    approval_rules: [
      'Read-only reporting can be automated.',
      'Ad launches, outreach sends, pricing changes, and customer messages require owner approval.',
    ],
  },
  crossAi: {
    directives: [
      { ai_name: 'Scanner AI', owner_brief_line: 'Scanner AI tells Growth AI which campaigns create real completed scans.', alert_growth_ai_when: ['scan completion rate drops'] },
      { ai_name: 'Retention AI', owner_brief_line: 'Retention AI tells Growth AI whether new customers are staying and seeing progress.', alert_growth_ai_when: ['cancellation risk rises'] },
      { ai_name: 'Operator AI', owner_brief_line: 'Operator AI tells Growth AI when the machine is broken.', alert_growth_ai_when: ['website or scanner is down'] },
    ],
    weekly_growth_command_questions: [
      'Which campaign created the most completed scans?',
      'Which source created the most paid upgrades?',
      'What should be scaled, paused, or fixed this week?',
    ],
  },
  ads: {
    counts: {
      channels: 7,
      ad_creatives: 8,
      creative_by_channel: {
        'Google Search': 2,
        'Microsoft/Bing Search': 1,
        'Meta Facebook/Instagram': 1,
        Reddit: 1,
        TikTok: 1,
        YouTube: 1,
        'Partner/referral ads': 1,
      },
    },
    launch_sequence: [
      'Set up GA4, Search Console, and conversion events first.',
      'Launch search campaigns with exact and phrase-match high-intent keywords.',
      'Launch partner/referral links with tracked source codes.',
    ],
  },
  problemSolver: {
    example_questions: [
      'Why are leads not starting the scanner?',
      'Which ad should we run first?',
      'Why are free users not upgrading?',
    ],
  },
};

async function fetchJson<T>(url: string): Promise<T> {
  const response = await authenticatedFetch(url);
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json() as Promise<T>;
}

function formatMoney(value = 0) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value = 0) {
  return new Intl.NumberFormat('en-US').format(value);
}

function statusBadge(state: FetchState) {
  if (state === 'live') return 'bg-emerald-50 text-emerald-700 border-emerald-100';
  if (state === 'loading') return 'bg-sky-50 text-sky-700 border-sky-100';
  return 'bg-amber-50 text-amber-700 border-amber-100';
}

export default function OwnerAICommand() {
  const [data, setData] = useState<DashboardData>(fallbackData);
  const [state, setState] = useState<FetchState>('loading');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchState, setSearchState] = useState<'idle' | 'running' | 'done' | 'error'>('idle');
  const [searchResult, setSearchResult] = useState<ForensicSearchResult | null>(null);

  async function loadDashboard() {
    setState((current) => (current === 'live' ? 'live' : 'loading'));
    setError(null);
    const results = await Promise.allSettled([
      fetchJson<GrowthBrief>('/api/vivo-command/live'),
      fetchJson<LiveAccessBrief>('/api/growth-ai/live-access'),
      fetchJson<CrossAiBrief>('/api/growth-ai/cross-ai-directives'),
      fetchJson<AdBrief>('/api/growth-ai/ad-plan'),
      fetchJson<ProblemBrief>('/api/growth-ai/problem-solver'),
    ]);

    const [command, liveAccess, crossAi, ads, problemSolver] = results;
    const nextData: DashboardData = {
      command: command.status === 'fulfilled' ? command.value : fallbackData.command,
      liveAccess: liveAccess.status === 'fulfilled' ? liveAccess.value : fallbackData.liveAccess,
      crossAi: crossAi.status === 'fulfilled' ? crossAi.value : fallbackData.crossAi,
      ads: ads.status === 'fulfilled' ? ads.value : fallbackData.ads,
      problemSolver: problemSolver.status === 'fulfilled' ? problemSolver.value : fallbackData.problemSolver,
    };

    setData(nextData);
    setLastUpdated(new Date());

    const failed = results.filter((result) => result.status === 'rejected').length;
    if (failed > 0) {
      setState('fallback');
      setError(`${failed} live AI feed${failed === 1 ? '' : 's'} not connected yet. Showing the best available fallback view.`);
    } else {
      setState('live');
    }
  }

  async function runGrowthSearch() {
    setSearchState('running');
    setSearchResult(null);

    try {
      const response = await authenticatedFetch('/api/growth-ai/forensic-search/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'Find the strongest growth opportunity for Credit Vivo this week',
        }),
      });

      if (!response.ok) throw new Error(`Growth search returned ${response.status}`);

      const result = (await response.json()) as ForensicSearchResult;
      setSearchResult(result);
      setSearchState('done');
    } catch {
      setSearchState('error');
    }
  }

  useEffect(() => {
    void loadDashboard();
    const interval = window.setInterval(() => {
      void loadDashboard();
    }, 30000);
    return () => window.clearInterval(interval);
  }, []);

  const snapshot = data.command?.growth_brief?.snapshot;
  const goal = data.command?.growth_brief?.million_month_target;
  const currentMrr = data.command?.revenue_goal?.current_mrr ?? snapshot?.monthly_recurring_revenue ?? 0;
  const monthlyGoal = data.command?.revenue_goal?.monthly_target ?? goal?.monthly_goal ?? 1000000;
  const paidGap = data.command?.revenue_goal?.paid_customer_gap ?? goal?.paid_customer_gap ?? 10527;
  const percentToGoal = monthlyGoal > 0 ? Math.min(100, Math.round((currentMrr / monthlyGoal) * 10000) / 100) : 0;
  const topActions = data.command?.top_actions ?? [];
  const growthActions = data.command?.growth_brief?.recommended_actions ?? [];

  const connectionRows = useMemo(() => {
    const setup = data.liveAccess?.first_30_day_setup_order ?? [];
    return setup.map((item, index) => ({
      name: item,
      status: index < 3 ? 'Next' : 'Queued',
    }));
  }, [data.liveAccess]);

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-emerald-600">
            Owner AI Command Center
          </p>
          <h1 className="text-xl font-bold text-navy-900">Real-time AI results cockpit</h1>
          <p className="mt-1 max-w-2xl text-sm leading-relaxed text-navy-500">
            A plain-English view of Growth AI, Vivo Command AI, live data access, alerts, and the path to $1M/month.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider ${statusBadge(state)}`}>
            <Wifi size={12} />
            {state === 'live' ? 'Live feeds' : state === 'loading' ? 'Checking feeds' : 'Fallback view'}
          </span>
          <button
            type="button"
            onClick={() => void loadDashboard()}
            className="inline-flex items-center gap-2 rounded-lg border border-navy-100 bg-white px-3 py-2 text-xs font-bold text-navy-700 hover:bg-navy-50"
          >
            <RefreshCcw size={13} />
            Refresh
          </button>
          <button
            type="button"
            onClick={() => void runGrowthSearch()}
            disabled={searchState === 'running'}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-bold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300"
          >
            <TrendingUp size={13} />
            {searchState === 'running' ? 'Searching' : 'Run Growth Search'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-5 rounded-xl border border-amber-100 bg-amber-50 p-4 text-xs leading-relaxed text-amber-900">
          <strong>Owner note:</strong> {error}
        </div>
      )}

      {searchResult?.owner_brief && (
        <section className="mb-5 rounded-xl border border-emerald-100 bg-emerald-50/70 p-5">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white">
              <TrendingUp size={18} className="text-emerald-700" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-navy-900">Growth Search result</h2>
              <p className="text-xs text-navy-500">Best opportunity Growth AI found for this run.</p>
            </div>
          </div>
          <div className="grid gap-3 lg:grid-cols-3">
            <div className="rounded-xl border border-emerald-100 bg-white p-4">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">Focus</p>
              <p className="mt-1 text-sm font-bold text-navy-900">{searchResult.owner_brief.best_first_search}</p>
              <p className="mt-2 text-xs leading-relaxed text-navy-500">{searchResult.owner_brief.why}</p>
            </div>
            <div className="rounded-xl border border-emerald-100 bg-white p-4">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">Campaign</p>
              <p className="mt-1 text-sm font-bold text-navy-900">{searchResult.owner_brief.campaign_to_use}</p>
              <p className="mt-2 text-xs leading-relaxed text-navy-500">{searchResult.owner_brief.next_action}</p>
            </div>
            <div className="rounded-xl border border-emerald-100 bg-white p-4">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">How we judge it</p>
              <p className="mt-1 text-xs leading-relaxed text-navy-500">{searchResult.owner_brief.verification}</p>
            </div>
          </div>
        </section>
      )}

      {searchState === 'error' && (
        <div className="mb-5 rounded-xl border border-amber-100 bg-amber-50 p-4 text-xs leading-relaxed text-amber-900">
          <strong>Growth Search could not connect yet.</strong> The dashboard is still usable, but the backend search endpoint needs to be available.
        </div>
      )}

      <div className="mb-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-emerald-100 bg-white p-5">
          <div className="mb-3 flex items-center justify-between">
            <DollarSign size={18} className="text-emerald-700" />
            <span className="rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold text-emerald-700">12 month goal</span>
          </div>
          <p className="text-2xl font-extrabold text-navy-900">{formatMoney(currentMrr)}</p>
          <p className="mt-1 text-[11px] text-navy-500">current monthly revenue tracked</p>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-navy-100">
            <div className="h-full rounded-full bg-emerald-600" style={{ width: `${percentToGoal}%` }} />
          </div>
          <p className="mt-2 text-[11px] text-navy-400">{percentToGoal}% of {formatMoney(monthlyGoal)} goal</p>
        </div>

        <div className="rounded-xl border border-sky-100 bg-white p-5">
          <div className="mb-3 flex items-center justify-between">
            <Target size={18} className="text-sky-700" />
            <span className="rounded-full bg-sky-50 px-2 py-1 text-[10px] font-bold text-sky-700">Gap</span>
          </div>
          <p className="text-2xl font-extrabold text-navy-900">{formatNumber(paidGap)}</p>
          <p className="mt-1 text-[11px] text-navy-500">paid customers still needed</p>
          <p className="mt-4 text-[11px] leading-relaxed text-navy-400">
            Based on the current planning average of about {formatMoney(goal?.blended_arpu ?? 95)} per paid customer.
          </p>
        </div>

        <div className="rounded-xl border border-violet-100 bg-white p-5">
          <div className="mb-3 flex items-center justify-between">
            <BarChart3 size={18} className="text-violet-700" />
            <span className="rounded-full bg-violet-50 px-2 py-1 text-[10px] font-bold text-violet-700">Funnel</span>
          </div>
          <p className="text-2xl font-extrabold text-navy-900">{formatNumber(snapshot?.free_scans_completed ?? 0)}</p>
          <p className="mt-1 text-[11px] text-navy-500">completed scans tracked</p>
          <p className="mt-4 text-[11px] leading-relaxed text-navy-400">
            {formatNumber(snapshot?.leads ?? 0)} leads, {formatNumber(snapshot?.free_scans_started ?? 0)} scans started.
          </p>
        </div>

        <div className="rounded-xl border border-amber-100 bg-white p-5">
          <div className="mb-3 flex items-center justify-between">
            <Clock size={18} className="text-amber-700" />
            <span className="rounded-full bg-amber-50 px-2 py-1 text-[10px] font-bold text-amber-700">Refresh</span>
          </div>
          <p className="text-2xl font-extrabold text-navy-900">30s</p>
          <p className="mt-1 text-[11px] text-navy-500">dashboard polling interval</p>
          <p className="mt-4 text-[11px] leading-relaxed text-navy-400">
            Last checked: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'starting now'}
          </p>
        </div>
      </div>

      <div className="mb-5 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-xl border border-navy-100 bg-white p-5">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <TrendingUp size={18} className="text-emerald-700" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-navy-900">AI next actions</h2>
              <p className="text-xs text-navy-400">What the AI thinks needs owner attention.</p>
            </div>
          </div>
          <div className="grid gap-3">
            {[...topActions, ...growthActions.map((action) => ({
              mission: 'Growth AI',
              priority: 'growth',
              issue: action.issue,
              recommended_action: action.action,
              approval_required: false,
            }))].slice(0, 6).map((action, index) => (
              <div key={`${action.issue}-${index}`} className="rounded-xl border border-navy-100 bg-navy-50/40 p-4">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-white px-2 py-0.5 text-[10px] font-bold text-navy-600">{action.mission}</span>
                  <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">{action.priority}</span>
                  {action.approval_required && (
                    <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-700">Owner approval</span>
                  )}
                </div>
                <h3 className="text-xs font-bold text-navy-900">{action.issue}</h3>
                <p className="mt-1 text-xs leading-relaxed text-navy-500">{action.recommended_action}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-navy-100 bg-white p-5">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-50">
              <Database size={18} className="text-sky-700" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-navy-900">Live access setup</h2>
              <p className="text-xs text-navy-400">{data.liveAccess?.counts?.tools ?? 13} data/tool connections mapped.</p>
            </div>
          </div>
          <div className="grid gap-2">
            {connectionRows.slice(0, 8).map((row) => (
              <div key={row.name} className="flex items-center justify-between gap-3 rounded-lg border border-navy-100 bg-navy-50/30 px-3 py-2">
                <span className="text-xs font-semibold text-navy-700">{row.name}</span>
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${row.status === 'Next' ? 'bg-emerald-50 text-emerald-700' : 'bg-navy-100 text-navy-500'}`}>
                  {row.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="mb-5 grid gap-4 xl:grid-cols-3">
        <section className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-5">
          <div className="mb-4 flex items-center gap-3">
            <CheckCircle size={18} className="text-emerald-700" />
            <h2 className="text-sm font-bold text-navy-900">Cross-AI feeds</h2>
          </div>
          <div className="grid gap-3">
            {(data.crossAi?.directives ?? []).slice(0, 6).map((directive) => (
              <div key={directive.ai_name} className="rounded-xl border border-emerald-100 bg-white p-4">
                <h3 className="text-xs font-bold text-navy-900">{directive.ai_name}</h3>
                <p className="mt-1 text-[11px] leading-relaxed text-navy-500">{directive.owner_brief_line}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-violet-100 bg-violet-50/50 p-5">
          <div className="mb-4 flex items-center gap-3">
            <Activity size={18} className="text-violet-700" />
            <h2 className="text-sm font-bold text-navy-900">Ad engine</h2>
          </div>
          <div className="mb-4 grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-violet-100 bg-white p-4">
              <p className="text-2xl font-bold text-navy-900">{data.ads?.counts?.channels ?? 7}</p>
              <p className="text-[11px] text-navy-400">channels</p>
            </div>
            <div className="rounded-xl border border-violet-100 bg-white p-4">
              <p className="text-2xl font-bold text-navy-900">{data.ads?.counts?.ad_creatives ?? 8}</p>
              <p className="text-[11px] text-navy-400">starter ads</p>
            </div>
          </div>
          <div className="grid gap-2">
            {(data.ads?.launch_sequence ?? []).slice(0, 4).map((item) => (
              <div key={item} className="flex gap-2 text-xs leading-relaxed text-navy-600">
                <CheckCircle size={13} className="mt-0.5 flex-shrink-0 text-violet-700" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-amber-100 bg-amber-50/60 p-5">
          <div className="mb-4 flex items-center gap-3">
            <AlertTriangle size={18} className="text-amber-700" />
            <h2 className="text-sm font-bold text-navy-900">Ask Growth AI</h2>
          </div>
          <div className="grid gap-2">
            {(data.problemSolver?.example_questions ?? []).slice(0, 5).map((question) => (
              <div key={question} className="rounded-xl border border-amber-100 bg-white p-3 text-xs font-semibold text-navy-700">
                {question}
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-xl border border-white bg-white/70 p-3">
            <div className="flex gap-2 text-xs leading-relaxed text-navy-600">
              <ShieldCheck size={14} className="mt-0.5 flex-shrink-0 text-amber-700" />
              <span>AI can recommend and draft. Owner approves spend, sends, pricing, and public sensitive changes.</span>
            </div>
          </div>
        </section>
      </div>

      <section className="rounded-xl border border-sky-100 bg-white p-5">
        <h2 className="mb-3 text-sm font-bold text-navy-900">Weekly founder questions</h2>
        <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {(data.crossAi?.weekly_growth_command_questions ?? []).map((question) => (
            <div key={question} className="rounded-xl border border-sky-100 bg-sky-50/40 p-3 text-xs font-semibold text-navy-700">
              {question}
            </div>
          ))}
        </div>
      </section>

      <section className="mt-5 rounded-xl border border-navy-100 bg-white p-5">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy-50">
            <Database size={18} className="text-navy-700" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-navy-900">Where Credit Vivo stores information</h2>
            <p className="text-xs text-navy-400">Owner-friendly map of what belongs where.</p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {[
            ['Website code', 'GitHub keeps the official code history and backup for the site.'],
            ['Live website', 'Vercel serves the customer-facing pages like Join, Pricing, and Learning.'],
            ['Scanner backend', 'Render runs the API that parses reports, tracks events, and powers AI dashboards.'],
            ['Customer data', 'A production database such as Supabase should store accounts, leads, scans, disputes, payments, and partner referrals.'],
          ].map(([title, detail]) => (
            <div key={title} className="rounded-xl border border-navy-100 bg-navy-50/30 p-4">
              <h3 className="text-xs font-bold text-navy-900">{title}</h3>
              <p className="mt-2 text-xs leading-relaxed text-navy-500">{detail}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
