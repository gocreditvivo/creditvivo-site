import Link from "next/link";
import {
  sampleFindings,
  sampleNegativeAccounts,
  samplePositiveAccounts,
  progressSteps,
} from "@/lib/credit-vivo-sample-data";

const safeDisclosure =
  "Results are not guaranteed. Attorney support may be available for eligible unresolved credit-reporting issues. Credit Vivo does not provide legal advice.";

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700">
      {children}
    </span>
  );
}

function PrimaryButton({ href = "/upload", children = "Start Free Credit Review" }) {
  return (
    <Link
      href={href}
      className="inline-flex items-center justify-center rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-950/20 transition hover:-translate-y-0.5 hover:bg-slate-800"
    >
      {children}
    </Link>
  );
}

function SecondaryButton({ href = "/how-it-works", children = "See How It Works" }) {
  return (
    <Link
      href={href}
      className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-800 transition hover:-translate-y-0.5 hover:border-emerald-300 hover:text-emerald-700"
    >
      {children}
    </Link>
  );
}

function SectionShell({
  eyebrow,
  title,
  subtitle,
  children,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
      <div className="mx-auto max-w-3xl text-center">
        {eyebrow && <Badge>{eyebrow}</Badge>}
        <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
          {title}
        </h2>
        {subtitle && (
          <p className="mt-4 text-base leading-7 text-slate-600">{subtitle}</p>
        )}
      </div>
      <div className="mt-10">{children}</div>
    </section>
  );
}

function MiniDashboard() {
  const items = [
    ["Score Goal", "Better credit readiness"],
    ["Possible Errors", "6 to review"],
    ["Disputes Ready", "5 drafts"],
    ["Progress", "Step 3 of 8"],
  ];

  return (
    <div className="relative rounded-3xl border border-white/70 bg-white/85 p-4 shadow-2xl shadow-emerald-950/10 backdrop-blur">
      <div className="rounded-2xl bg-gradient-to-br from-slate-950 to-emerald-900 p-5 text-white">
        <p className="text-sm text-emerald-200">Credit Vivo Dashboard</p>
        <h3 className="mt-2 text-2xl font-bold">Your review is moving.</h3>
        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {items.map(([label, value]) => (
            <div key={label} className="rounded-2xl bg-white/10 p-4">
              <p className="text-xs uppercase tracking-wide text-emerald-100">{label}</p>
              <p className="mt-2 text-lg font-semibold">{value}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-4 rounded-2xl border border-slate-100 bg-slate-50 p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-900">Next step</p>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
            Review drafts
          </span>
        </div>
        <div className="mt-3 h-2 rounded-full bg-slate-200">
          <div className="h-2 w-2/5 rounded-full bg-emerald-500" />
        </div>
      </div>
    </div>
  );
}

export function CreditVivoHome() {
  const benefits = [
    ["Car loans", "Better credit may help with stronger auto financing options."],
    ["Home goals", "Work toward better mortgage readiness."],
    ["Apartments", "Improve your file before rental applications."],
    ["Credit cards", "Build toward better credit opportunities."],
    ["Insurance", "Credit may affect certain insurance-related pricing factors."],
    ["Jobs", "Some employers may review credit-related background information where allowed."],
  ];

  const features = [
    "Negative account review",
    "3-bureau comparison",
    "Possible error detection",
    "Dispute draft builder",
    "Progress tracker",
    "Score-goal guidance",
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-emerald-50/40 to-white">
      <section className="mx-auto grid max-w-7xl items-center gap-12 px-6 py-20 lg:grid-cols-2 lg:px-8 lg:py-28">
        <div>
          <Badge>AI Credit Boost + Attorney Support</Badge>
          <h1 className="mt-6 text-5xl font-bold tracking-tight text-slate-950 sm:text-6xl">
            Better credit can open better doors.
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Credit Vivo uses AI to review your credit report, find possible errors,
            build dispute drafts, and track your progress.
          </p>
          <p className="mt-4 text-base font-semibold text-emerald-700">
            Find errors. Build disputes. Track progress.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <PrimaryButton />
            <SecondaryButton />
          </div>
          <p className="mt-6 max-w-xl text-xs leading-5 text-slate-500">
            {safeDisclosure}
          </p>
        </div>
        <MiniDashboard />
      </section>

      <SectionShell
        eyebrow="Score-goal focused"
        title="Better credit can help you move forward."
        subtitle="Credit Vivo helps you understand what may be affecting your credit file before important life decisions."
      >
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {benefits.map(([title, text]) => (
            <div key={title} className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
                ✓
              </div>
              <h3 className="text-lg font-bold text-slate-950">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        eyebrow="How it works"
        title="Simple steps. Smarter credit review."
      >
        <div className="grid gap-4 md:grid-cols-5">
          {["Upload your report", "AI reviews your file", "Review your findings", "Approve dispute drafts", "Track progress"].map((step, idx) => (
            <div key={step} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-950 text-sm font-bold text-white">
                {idx + 1}
              </div>
              <h3 className="mt-4 text-base font-bold text-slate-950">{step}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {idx === 0 && "Start with your Equifax, Experian, and TransUnion reports."}
                {idx === 1 && "We look for negative items, possible errors, and score-impacting factors."}
                {idx === 2 && "See what may need attention in simple language."}
                {idx === 3 && "No letters are sent without your approval."}
                {idx === 4 && "Follow updates, responses, and next steps."}
              </p>
            </div>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        eyebrow="AI Credit Boost"
        title="AI helps spot what may be holding your score back."
        subtitle="Credit Vivo reviews account status, balances, late payments, collections, charge-offs, and bureau differences to help identify possible reporting issues."
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div key={feature} className="rounded-2xl border border-emerald-100 bg-white p-5 text-sm font-semibold text-slate-800 shadow-sm">
              {feature}
            </div>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        eyebrow="Attorney support"
        title="Attorney support may be available when issues remain unresolved."
        subtitle="If eligible credit-reporting issues remain unresolved after the dispute process, attorney support may be available for review."
      >
        <div className="mx-auto max-w-3xl rounded-3xl border border-emerald-200 bg-emerald-50 p-8 text-center">
          <p className="text-lg font-semibold text-emerald-900">
            Attorney support may be available for eligible unresolved credit-reporting issues.
          </p>
        </div>
      </SectionShell>

      <FooterDisclosure />
    </main>
  );
}

export function CustomerDashboard() {
  const cards = [
    ["Score goal", sampleFindings.scoreGoal],
    ["Negative items", String(sampleFindings.negativeItemsFound)],
    ["Possible errors", String(sampleFindings.possibleErrors)],
    ["Drafts ready", String(sampleFindings.disputeDraftsReady)],
    ["Positive accounts kept", String(sampleFindings.positiveAccountsKept)],
    ["Next step", sampleFindings.nextStep],
  ];

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col justify-between gap-4 rounded-3xl bg-slate-950 p-8 text-white md:flex-row md:items-end">
          <div>
            <Badge>Customer Portal</Badge>
            <h1 className="mt-5 text-4xl font-bold">Your Credit Vivo review</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              Simple progress, clear next steps, and no letters sent without your approval.
            </p>
          </div>
          <PrimaryButton href="/disputes">Review Drafts</PrimaryButton>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cards.map(([label, value]) => (
            <div key={label} className="rounded-3xl bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className="mt-2 text-2xl font-bold text-slate-950">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <NegativeAccountList compact />
          <ProgressTimeline />
        </div>
      </div>
    </main>
  );
}

export function UploadPage() {
  const bureaus = ["Equifax", "Experian", "TransUnion"];
  return (
    <PortalPageShell title="Upload your credit report" subtitle="Add your Equifax, Experian, and TransUnion reports for the most complete review.">
      <div className="grid gap-4 md:grid-cols-3">
        {bureaus.map((bureau) => (
          <div key={bureau} className="rounded-3xl border border-dashed border-emerald-300 bg-white p-6 text-center shadow-sm">
            <h3 className="text-xl font-bold text-slate-950">{bureau}</h3>
            <p className="mt-2 text-sm text-slate-600">Not uploaded</p>
            <button className="mt-5 rounded-full bg-emerald-600 px-5 py-2 text-sm font-semibold text-white">
              Upload {bureau}
            </button>
          </div>
        ))}
      </div>
    </PortalPageShell>
  );
}

export function FindingsPage() {
  return (
    <PortalPageShell title="Your AI credit review" subtitle="Here is a simple summary of what Credit Vivo may find.">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          ["Negative items found", "9"],
          ["Possible errors", "6"],
          ["Dispute drafts ready", "5"],
          ["Positive accounts kept", "5"],
        ].map(([label, value]) => (
          <div key={label} className="rounded-3xl bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-3xl font-bold text-slate-950">{value}</p>
          </div>
        ))}
      </div>
    </PortalPageShell>
  );
}

export function NegativeAccountsPage() {
  return (
    <PortalPageShell title="Negative accounts" subtitle="Review possible score-impacting items. No legal conclusions are shown here.">
      <NegativeAccountList />
    </PortalPageShell>
  );
}

export function DisputesPage() {
  return (
    <PortalPageShell title="Review dispute drafts" subtitle="No letters are sent until you approve them.">
      <div className="space-y-4">
        {sampleNegativeAccounts.slice(0, 3).map((account) => (
          <div key={account.name} className="rounded-3xl bg-white p-6 shadow-sm">
            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
              <div>
                <p className="text-sm font-semibold text-emerald-700">{account.type}</p>
                <h3 className="mt-1 text-xl font-bold text-slate-950">{account.name}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{account.nextStep}</p>
              </div>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
                Draft only
              </span>
            </div>
            <label className="mt-5 flex items-start gap-3 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
              <input type="checkbox" className="mt-1" />
              I understand this is a draft and no letter is sent until I approve it.
            </label>
          </div>
        ))}
      </div>
    </PortalPageShell>
  );
}

export function ProgressPage() {
  return (
    <PortalPageShell title="Track progress" subtitle="Follow your file from upload to response and next step.">
      <ProgressTimeline />
    </PortalPageShell>
  );
}

export function FAQPage() {
  const faqs = [
    ["Is this credit repair?", "Credit Vivo helps review your credit report, identify possible errors, prepare dispute drafts, and track your progress. Results are not guaranteed."],
    ["Will my score increase?", "Credit Vivo is designed to help you work toward better credit, but results are not guaranteed."],
    ["Are letters sent automatically?", "No. Dispute letters are drafts until you review and approve them."],
    ["Is attorney support included?", "Attorney support may be available for eligible unresolved credit-reporting issues."],
    ["What reports do I need?", "For the best review, upload reports from Equifax, Experian, and TransUnion."],
  ];

  return (
    <PortalPageShell title="Frequently asked questions" subtitle="Simple answers before you start.">
      <div className="space-y-4">
        {faqs.map(([q, a]) => (
          <div key={q} className="rounded-3xl bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-950">{q}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{a}</p>
          </div>
        ))}
      </div>
    </PortalPageShell>
  );
}

function NegativeAccountList({ compact = false }: { compact?: boolean }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Accounts to review</h2>
      <div className="mt-5 space-y-4">
        {sampleNegativeAccounts.slice(0, compact ? 3 : sampleNegativeAccounts.length).map((account) => (
          <div key={account.name} className="rounded-2xl border border-slate-100 p-4">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
                  {account.priority} priority
                </p>
                <h3 className="mt-1 font-bold text-slate-950">{account.name}</h3>
                <p className="mt-1 text-sm text-slate-500">{account.bureaus}</p>
                <p className="mt-3 text-sm leading-6 text-slate-600">{account.why}</p>
              </div>
              <Link href="/disputes" className="rounded-full bg-slate-950 px-4 py-2 text-center text-sm font-semibold text-white">
                Review
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProgressTimeline() {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-950">Progress tracker</h2>
      <div className="mt-6 space-y-4">
        {progressSteps.map((step, index) => (
          <div key={step.label} className="flex gap-4">
            <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
              step.status === "complete" ? "bg-emerald-600 text-white" :
              step.status === "current" ? "bg-slate-950 text-white" :
              "bg-slate-100 text-slate-400"
            }`}>
              {index + 1}
            </div>
            <div>
              <p className="font-semibold text-slate-950">{step.label}</p>
              <p className="text-sm text-slate-500">{step.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PortalPageShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 rounded-3xl bg-white p-8 shadow-sm">
          <Badge>Credit Vivo Portal</Badge>
          <h1 className="mt-5 text-4xl font-bold tracking-tight text-slate-950">{title}</h1>
          <p className="mt-3 max-w-2xl text-slate-600">{subtitle}</p>
        </div>
        {children}
      </div>
    </main>
  );
}

export function FooterDisclosure() {
  return (
    <footer className="border-t border-slate-100 bg-white px-6 py-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-bold text-slate-950">Credit Vivo</p>
          <p className="mt-2 max-w-3xl">{safeDisclosure}</p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/faq" className="hover:text-slate-950">FAQ</Link>
          <Link href="#" className="hover:text-slate-950">Privacy Notice</Link>
          <Link href="#" className="hover:text-slate-950">Terms</Link>
          <Link href="#" className="hover:text-slate-950">Disclosures</Link>
          <Link href="#" className="hover:text-slate-950">Contact</Link>
        </div>
      </div>
    </footer>
  );
}
