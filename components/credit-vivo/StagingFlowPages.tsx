import Link from "next/link";
import { STAGING_RULES, STAGING_SAFE_MODE_SUMMARY } from "@/lib/credit-vivo/staging";
import { CREDIT_VIVO_EMAILS } from "@/lib/credit-vivo/email";

type StagingPageProps = {
  title: string;
  subtitle: string;
  activeStep: string;
  children?: React.ReactNode;
};

const steps = [
  ["Signup", "/signup"],
  ["Plan", "/pricing"],
  ["Checkout", "/checkout"],
  ["Member", "/member"],
  ["Upload", "/member/upload"],
  ["Findings", "/member/findings"],
  ["Approvals", "/member/disputes"],
  ["Admin Cert", "http://127.0.0.1:8082/admin/production-certification"],
] as const;

export function StagingFlowPage({ title, subtitle, activeStep, children }: StagingPageProps) {
  return (
    <main className="min-h-screen bg-slate-50">
      <section className="mx-auto max-w-6xl px-6 py-10 lg:px-8">
        <nav className="mb-8 flex flex-wrap gap-3 text-sm font-semibold text-slate-700">
          <Link href="/" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Home
          </Link>
          <Link href="/signup" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Signup
          </Link>
          <Link href="/pricing" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Pricing
          </Link>
          <Link href="/member" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Member Portal
          </Link>
        </nav>

        <div className="rounded-lg bg-gradient-to-br from-slate-950 to-emerald-900 p-8 text-white">
          <p className="text-sm font-semibold text-emerald-200">{STAGING_RULES.name}</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight">{title}</h1>
          <p className="mt-4 max-w-3xl text-slate-200">{subtitle}</p>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_0.85fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-2xl font-bold text-slate-950">UAT step: {activeStep}</h2>
            <div className="mt-5">{children}</div>
          </section>

          <aside className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-xl font-bold text-slate-950">Staging safe rules</h2>
            <ul className="mt-4 space-y-2 text-sm leading-6 text-slate-600">
              {STAGING_SAFE_MODE_SUMMARY.map((rule) => (
                <li key={rule}>- {rule}</li>
              ))}
            </ul>
            <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
              Use synthetic reports only. For help, contact{" "}
              <a className="font-bold" href={`mailto:${CREDIT_VIVO_EMAILS.support}`}>
                {CREDIT_VIVO_EMAILS.support}
              </a>
              .
            </div>
          </aside>
        </div>

        <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-950">Journey route checks</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {steps.map(([label, href]) => (
              <a
                key={href}
                href={href}
                className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm font-bold text-slate-800"
              >
                {label}
              </a>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

export function SignupStagingPage() {
  return (
    <StagingFlowPage
      title="Create a staging test account"
      subtitle="Use test users only. This page does not collect SSN, DOB, payment keys, or credit report data."
      activeStep="Signup"
    >
      <div className="grid gap-4">
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Test email
          <input
            className="rounded-lg border border-slate-300 px-3 py-2"
            defaultValue="member-test@creditvivo.com"
            readOnly
          />
        </label>
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Credit goal
          <select className="rounded-lg border border-slate-300 px-3 py-2" defaultValue="car">
            <option value="car">Car loan readiness</option>
            <option value="home">Mortgage readiness</option>
            <option value="apartment">Apartment readiness</option>
            <option value="general">General credit readiness</option>
          </select>
        </label>
        <label className="flex gap-3 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
          <input type="checkbox" defaultChecked readOnly />
          I understand this is staging safe mode and I will not use real customer reports.
        </label>
        <Link className="rounded-lg bg-slate-950 px-5 py-3 text-center text-sm font-bold text-white" href="/pricing">
          Continue to test plan
        </Link>
      </div>
    </StagingFlowPage>
  );
}

export function LoginStagingPage() {
  return (
    <StagingFlowPage
      title="Staging login"
      subtitle="Use the seeded test accounts for UAT. Real customer accounts are not allowed in staging."
      activeStep="Login"
    >
      <div className="space-y-3 text-sm text-slate-700">
        <p>
          Customer: <strong>member-test@creditvivo.com</strong>
        </p>
        <p>
          Founder/admin: <strong>founder-test@creditvivo.com</strong>
        </p>
        <Link className="inline-block rounded-lg bg-slate-950 px-5 py-3 text-sm font-bold text-white" href="/member">
          Open member dashboard
        </Link>
      </div>
    </StagingFlowPage>
  );
}

export function PricingStagingPage() {
  return (
    <StagingFlowPage
      title="Choose a test plan"
      subtitle="Pricing can be tested in staging, but live card processing is blocked."
      activeStep="Plan"
    >
      <div className="grid gap-4 md:grid-cols-3">
        {["Review", "Momentum", "Founder UAT"].map((plan) => (
          <div key={plan} className="rounded-lg border border-slate-200 p-5">
            <h3 className="text-lg font-bold text-slate-950">{plan}</h3>
            <p className="mt-2 text-sm text-slate-600">Stripe test mode only.</p>
            <Link className="mt-4 block rounded-lg bg-slate-950 px-4 py-2 text-center text-sm font-bold text-white" href="/checkout">
              Select test plan
            </Link>
          </div>
        ))}
      </div>
    </StagingFlowPage>
  );
}

export function CheckoutStagingPage({ success = false }: { success?: boolean }) {
  return (
    <StagingFlowPage
      title={success ? "Checkout test success" : "Stripe test checkout"}
      subtitle="This staging placeholder confirms test-mode payment flow. No live card processing is enabled."
      activeStep={success ? "Checkout Success" : "Checkout"}
    >
      <div className="space-y-4 text-sm text-slate-700">
        <p>
          Payment mode: <strong>test</strong>
        </p>
        <p>
          Live Stripe keys: <strong>not configured</strong>
        </p>
        <p>
          External calls: <strong>off</strong>
        </p>
        <Link
          className="inline-block rounded-lg bg-slate-950 px-5 py-3 text-sm font-bold text-white"
          href={success ? "/member" : "/checkout/success"}
        >
          {success ? "Open member portal" : "Simulate test success"}
        </Link>
      </div>
    </StagingFlowPage>
  );
}

