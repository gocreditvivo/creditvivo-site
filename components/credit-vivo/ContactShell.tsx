import Link from "next/link";
import {
  CREDIT_VIVO_EMAILS,
  EMAIL_DISCLOSURE,
  EMAIL_FEATURE_FLAGS,
  EMAIL_SAFETY_RULES,
} from "@/lib/credit-vivo/email";

type ContactShellProps = {
  title: string;
  subtitle: string;
  primaryEmail: keyof typeof CREDIT_VIVO_EMAILS;
  children?: React.ReactNode;
};

export function ContactShell({ title, subtitle, primaryEmail, children }: ContactShellProps) {
  const email = CREDIT_VIVO_EMAILS[primaryEmail];

  return (
    <main className="min-h-screen bg-slate-50">
      <section className="mx-auto max-w-5xl px-6 py-10 lg:px-8">
        <nav className="mb-8 flex flex-wrap gap-3 text-sm font-semibold text-slate-700">
          <Link href="/" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Home
          </Link>
          <Link href="/member" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Member Portal
          </Link>
          <Link href="/contact" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Contact
          </Link>
          <Link href="/support" className="rounded-lg border border-slate-200 bg-white px-3 py-2">
            Support
          </Link>
        </nav>

        <div className="rounded-lg bg-gradient-to-br from-slate-950 to-emerald-900 p-8 text-white">
          <p className="text-sm font-semibold text-emerald-200">Credit Vivo</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight">{title}</h1>
          <p className="mt-4 max-w-3xl text-slate-200">{subtitle}</p>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_0.85fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-2xl font-bold text-slate-950">Best contact</h2>
            <a className="mt-4 block text-lg font-bold text-emerald-700" href={`mailto:${email}`}>
              {email}
            </a>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              Please do not email SSNs, full DOBs, full account numbers, passwords, IDs, or credit
              report files. Use the secure member upload flow when it is connected and approved.
            </p>
            <div className="mt-6">{children}</div>
          </section>

          <aside className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-xl font-bold text-slate-950">Email safety defaults</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Provider</dt>
                <dd className="font-bold text-slate-950">{EMAIL_FEATURE_FLAGS.provider}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Sending</dt>
                <dd className="font-bold text-slate-950">
                  {EMAIL_FEATURE_FLAGS.enableEmailSending ? "Enabled" : "Disabled"}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Marketing</dt>
                <dd className="font-bold text-slate-950">
                  {EMAIL_FEATURE_FLAGS.enableMarketingEmails ? "Enabled" : "Disabled"}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Dispute auto-send</dt>
                <dd className="font-bold text-slate-950">
                  {EMAIL_FEATURE_FLAGS.enableDisputeEmailAutoSend ? "Enabled" : "Disabled"}
                </dd>
              </div>
            </dl>
            <ul className="mt-5 space-y-2 text-sm leading-6 text-slate-600">
              {EMAIL_SAFETY_RULES.map((rule) => (
                <li key={rule}>- {rule}</li>
              ))}
            </ul>
            <p className="mt-5 text-xs leading-5 text-slate-500">{EMAIL_DISCLOSURE}</p>
          </aside>
        </div>
      </section>
    </main>
  );
}

