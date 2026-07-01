import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle,
  FileText,
  Loader2,
  Lock,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  Zap,
} from 'lucide-react';
import { parseCreditReports } from '../lib/scannerApi';
import { getDemoScanResult, saveLastScanResult } from '../lib/scanStorage';

const scanSteps = [
  'Checking Metro 2 reporting fields...',
  'Comparing bureau dates and balances...',
  'Grouping possible FCRA review points...',
  'Preparing a plain-English review plan...',
  'Preview ready.',
];

const demoFindings = [
  {
    title: 'Late Payment Review - Capital One',
    label: 'Needs review',
    copy:
      'The demo flow flags date and payment-history differences for customer and admin review before any dispute is prepared.',
  },
  {
    title: 'Collection Review - Portfolio Recovery',
    label: 'Needs review',
    copy:
      'The demo flow organizes ownership, balance, and verification questions so the next step is clear and documented.',
  },
];

export default function FreeScan() {
  const navigate = useNavigate();
  const [files, setFiles] = useState<File[]>([]);
  const [isReviewing, setIsReviewing] = useState(false);
  const [demoStage, setDemoStage] = useState<'intro' | 'scanning' | 'results'>('intro');
  const [demoStep, setDemoStep] = useState(0);
  const [error, setError] = useState('');

  const selectedFileText = useMemo(() => {
    if (!files.length) return 'No files selected yet';
    if (files.length === 1) return files[0].name;
    return `${files.length} files selected`;
  }, [files]);

  const demoProgress = useMemo(() => {
    if (demoStage === 'results') return 100;
    if (demoStage === 'intro') return 0;
    return Math.min(100, Math.round(((demoStep + 1) / scanSteps.length) * 100));
  }, [demoStage, demoStep]);

  useEffect(() => {
    if (demoStage !== 'scanning') return undefined;

    const timer = window.setInterval(() => {
      setDemoStep((current) => {
        if (current >= scanSteps.length - 1) {
          window.clearInterval(timer);
          window.setTimeout(() => setDemoStage('results'), 450);
          return current;
        }

        return current + 1;
      });
    }, 900);

    return () => window.clearInterval(timer);
  }, [demoStage]);

  async function handleStartCheckIn() {
    setError('');

    if (!files.length) {
      setError('Please select at least one credit report PDF.');
      return;
    }

    setIsReviewing(true);

    try {
      const result = await parseCreditReports(files, false);
      saveLastScanResult(result);
      navigate('/findings');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Scanner request failed.';
      setError(
        `${message} If you are reviewing the beta site, use "Load demo findings" to preview the customer flow.`
      );
    } finally {
      setIsReviewing(false);
    }
  }

  function handleDemo() {
    const demo = getDemoScanResult();
    saveLastScanResult(demo);
    navigate('/findings');
  }

  function handleStartDemoScan() {
    setError('');
    setDemoStep(0);
    setDemoStage('scanning');
  }

  return (
    <div className="-m-6 min-h-screen bg-navy-950 text-white md:-m-8">
      <section className="relative overflow-hidden px-5 py-10 sm:px-8 lg:px-10">
        <div className="absolute inset-x-0 top-0 h-64 bg-[linear-gradient(110deg,rgba(5,150,105,.24),rgba(14,165,233,.18),rgba(251,113,133,.12))]" />

        <div className="relative mx-auto grid max-w-6xl gap-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(340px,.92fr)] lg:items-stretch">
          <div className="flex min-h-[580px] flex-col justify-center py-10">
            <p className="mb-3 inline-flex w-fit items-center gap-2 rounded-lg border border-teal-300/20 bg-white/8 px-3 py-2 text-[11px] font-semibold uppercase tracking-widest text-teal-200">
              <Sparkles size={14} />
              Free AI credit check-in
            </p>
            <h1 className="max-w-3xl text-4xl font-extrabold leading-tight tracking-normal text-white sm:text-5xl lg:text-6xl">
              We measure progress by one metric.{' '}
              <span className="text-teal-300">Your next clear step.</span>
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
              Upload a credit report PDF or preview the demo scan. Credit Vivo organizes possible
              reporting issues in plain English, prepares draft dispute materials for review, and
              keeps every action approval-first.
            </p>

            <div className="mt-7 flex flex-wrap gap-3 text-sm font-semibold text-slate-300">
              {[
                ['No hard pull to start', ShieldCheck],
                ['Metro 2 review signals', Search],
                ['Nothing sent without approval', Lock],
              ].map(([text, Icon]) => (
                <div key={text as string} className="flex items-center gap-2 rounded-lg bg-white/8 px-3 py-2 ring-1 ring-white/10">
                  <Icon size={16} className="text-teal-300" />
                  <span>{text as string}</span>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleStartDemoScan}
                disabled={demoStage === 'scanning'}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-teal-400 px-6 py-3.5 text-sm font-extrabold text-navy-950 shadow-xl shadow-teal-950/30 transition-all hover:-translate-y-0.5 hover:bg-teal-300 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {demoStage === 'scanning' ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Running demo scan...
                  </>
                ) : (
                  <>
                    Start Free AI Comeback Scan
                    <Zap size={16} />
                  </>
                )}
              </button>
              <a
                href="#upload-report"
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/14 bg-white/8 px-6 py-3.5 text-sm font-bold text-white transition-all hover:-translate-y-0.5 hover:bg-white/12"
              >
                Upload PDF instead
                <ArrowRight size={16} />
              </a>
            </div>

            <p className="mt-4 text-xs uppercase tracking-widest text-slate-500">
              Demo takes a few seconds. Real scans depend on the connected parser.
            </p>
          </div>

          <div className="flex items-center">
            <div className="w-full rounded-xl border border-white/10 bg-slate-900/82 p-5 shadow-2xl shadow-black/30">
              {demoStage === 'intro' && (
                <div className="py-6 text-center">
                  <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full border-4 border-teal-400 bg-slate-800 shadow-[0_0_34px_rgba(45,212,191,.22)]">
                    <Search size={34} className="text-teal-300" />
                  </div>
                  <h2 className="text-2xl font-extrabold">Preview the scan experience</h2>
                  <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-400">
                    See the customer-facing flow before uploading a real report. The sample data is
                    fictional and for product preview only.
                  </p>
                </div>
              )}

              {demoStage === 'scanning' && (
                <div className="py-8 text-center">
                  <div className="relative mx-auto mb-7 h-24 w-24">
                    <div className="absolute inset-0 animate-ping rounded-full bg-teal-400 opacity-20" />
                    <div className="relative flex h-full w-full items-center justify-center rounded-full border-4 border-teal-400 bg-slate-800 shadow-[0_0_34px_rgba(45,212,191,.22)]">
                      <Zap size={34} className="animate-pulse text-teal-300" />
                    </div>
                  </div>

                  <h2 className="text-2xl font-extrabold">Analyzing report signals...</h2>
                  <p className="mt-3 h-6 font-mono text-sm text-teal-300">{scanSteps[demoStep]}</p>

                  <div className="mt-7 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-teal-400 transition-all duration-700"
                      style={{ width: `${demoProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {demoStage === 'results' && (
                <div className="text-slate-950">
                  <div className="rounded-lg bg-white p-5 text-center">
                    <h2 className="text-2xl font-extrabold text-navy-950">Your review plan is ready</h2>
                    <p className="mt-2 text-sm text-navy-500">
                      The demo found <strong className="text-rose-600">2 review items</strong> to
                      organize before any next step is approved.
                    </p>
                  </div>

                  <div className="mt-4 space-y-3">
                    {demoFindings.map((finding) => (
                      <div key={finding.title} className="rounded-lg border-l-4 border-rose-500 bg-white p-4 shadow-sm">
                        <div className="flex flex-wrap items-start justify-between gap-2">
                          <h3 className="text-base font-extrabold text-navy-950">{finding.title}</h3>
                          <span className="rounded-md bg-rose-50 px-2 py-1 text-[11px] font-extrabold uppercase tracking-wide text-rose-700">
                            {finding.label}
                          </span>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-navy-600">{finding.copy}</p>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={handleDemo}
                    className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-teal-500 px-5 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-teal-900/20 transition-all hover:-translate-y-0.5 hover:bg-teal-400"
                  >
                    View full demo findings
                    <ArrowRight size={16} />
                  </button>

                  <div className="mt-4 rounded-lg bg-navy-950 p-5 text-center text-white">
                    <Lock size={26} className="mx-auto mb-2 text-teal-300" />
                    <h4 className="font-extrabold">Need attorney review later?</h4>
                    <p className="mt-1 text-sm leading-6 text-slate-300">
                      Legal escalation is separate and only appropriate after review history and
                      documentation support it.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section id="upload-report" className="bg-slate-50 px-5 py-10 text-navy-900 sm:px-8 lg:px-10">
        <div className="mx-auto grid max-w-6xl gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="rounded-xl border border-navy-100/70 bg-white p-6 shadow-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-sky-50">
              <Upload size={20} className="text-sky-600" />
            </div>

            <h2 className="mb-2 text-lg font-extrabold text-navy-950">
              Upload or connect your report
            </h2>
            <p className="mb-5 max-w-2xl text-sm leading-7 text-navy-500">
              For your first real test, start with one bureau report. The scanner accepts PDF
              reports only, up to 3 files and 25 MB per file.
            </p>

            <div className="mb-5 rounded-lg border border-amber-100 bg-amber-50 p-3">
              <div className="flex gap-2 text-xs leading-relaxed text-amber-900">
                <AlertCircle size={15} className="mt-0.5 flex-shrink-0" />
                <p>
                  Real credit reports contain sensitive personal data. Use your own report or a
                  report you have permission to test. Uploaded PDFs are not retained after parsing
                  unless retention is intentionally turned on.
                </p>
              </div>
            </div>

            <label className="block cursor-pointer rounded-xl border border-dashed border-navy-200 bg-navy-50/40 p-5 transition-colors hover:bg-sky-50/40">
              <input
                type="file"
                accept="application/pdf,.pdf"
                multiple
                className="hidden"
                onChange={(event) => {
                  const selected = Array.from(event.target.files || []);
                  setFiles(selected);
                  setError('');
                }}
              />
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-navy-100 bg-white">
                  <FileText size={16} className="text-sky-600" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-navy-800">
                    Choose PDF reports
                  </p>
                  <p className="text-[11px] text-navy-400">
                    Experian, Equifax, TransUnion, or multi-bureau reports
                  </p>
                </div>
              </div>
            </label>

            <div className="mt-4 flex items-center gap-2 text-xs text-navy-500">
              <CheckCircle size={14} className="text-mint-600" />
              <span>{selectedFileText}</span>
            </div>

            {error && (
              <div className="mt-4 flex gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-xs text-red-700">
                <AlertCircle size={15} className="mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="mt-5 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleStartCheckIn}
                disabled={isReviewing}
                className="btn-primary py-2.5 text-xs disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isReviewing ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Reviewing your Credit Check-In...
                  </>
                ) : (
                  <>
                    Start Credit Check-In
                    <ArrowRight size={14} />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleDemo}
                disabled={isReviewing}
                className="rounded-lg border border-navy-100 px-4 py-2.5 text-xs font-semibold text-navy-600 transition-colors hover:bg-navy-50"
              >
                Load demo findings
              </button>
            </div>
          </div>

          <div className="h-fit rounded-xl border border-navy-100/70 bg-white p-5 shadow-sm">
            <h2 className="mb-3 text-sm font-bold text-navy-900">
              What happens next
            </h2>
            <div className="space-y-3">
              {[
                'Credit Vivo extracts report text.',
                'Possible errors are grouped by bureau and account.',
                'Findings appear in a worksheet-style review flow.',
                'Draft dispute letters are prepared for review.',
                'Nothing is mailed, disputed, or escalated without approval.',
              ].map((step, index) => (
                <div key={step} className="flex gap-3">
                  <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-lg bg-sky-50 text-[11px] font-bold text-sky-700">
                    {index + 1}
                  </div>
                  <p className="text-xs leading-relaxed text-navy-500">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
