import { Link } from 'react-router-dom';
import { AlertCircle, ArrowRight, CheckCircle, Clock, Download, FileSearch, MailCheck, Route, ShieldCheck } from 'lucide-react';
import { downloadScannerOutput, getScannerOutputDownloadUrl } from '../lib/scannerApi';
import { getLastScanResult } from '../lib/scanStorage';

const categoryNames = [
  'Profile Cleanup',
  'Collection Review',
  'Bureau Match Review',
  'Reporting Accuracy Review',
  'Factual Review',
  'Needs Admin Review',
];

function countCategory(label: string, result: ReturnType<typeof getLastScanResult>) {
  if (!result) return 0;

  if (label === 'Needs Admin Review') {
    return result.review_items_preview.filter((item) => item.needs_admin_review).length;
  }

  const fromIssues = (result.issues_preview || []).filter((issue) => {
    const combined = `${issue.customer_label} ${issue.suggested_round} ${issue.issue_type}`.toLowerCase();
    return combined.includes(label.toLowerCase().replace(' review', ''));
  }).length;

  const fromItems = result.review_items_preview.filter((item) => {
    const combined = `${item.account_type || ''} ${item.status || ''} ${item.pay_status || ''} ${item.remarks || ''}`.toLowerCase();

    if (label === 'Collection Review') return combined.includes('collection');
    if (label === 'Reporting Accuracy Review') {
      return (
        combined.includes('charge') ||
        combined.includes('transferred') ||
        combined.includes('sold') ||
        combined.includes('closed')
      );
    }
    return false;
  }).length;

  return Math.max(fromIssues, fromItems);
}

function formatLabel(value: string) {
  return value.replace(/_/g, ' ');
}

export default function Findings() {
  const result = getLastScanResult();

  async function downloadScannerFile(downloadName: 'workbook.xlsx' | 'issues.csv' | 'tradelines.csv' | 'letters.txt', filename: string) {
    const blob = await downloadScannerOutput(result!.job_id, downloadName);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  if (!result) {
    return (
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-widest text-sky-600 mb-1">
          Member Flow
        </p>
        <h1 className="text-xl font-bold text-navy-900 mb-6">
          Your Findings are organized.
        </h1>

        <div className="bg-white rounded-xl p-6 border border-navy-100/60 max-w-xl">
          <div className="w-12 h-12 bg-sky-50 rounded-xl flex items-center justify-center mb-4">
            <FileSearch size={20} className="text-sky-600" />
          </div>
          <h2 className="text-sm font-bold text-navy-900 mb-2">
            No Credit Check-In result yet
          </h2>
          <p className="text-xs text-navy-400 mb-5 leading-relaxed">
            Start a Credit Check-In first, then your findings will appear here.
          </p>
          <Link to="/scan" className="btn-primary text-xs py-2.5">
            Start Credit Check-In
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    );
  }

  const stats = [
    { val: String(result.review_items_count || 0), label: 'review items' },
    { val: String(result.issues_count || result.issues_preview?.length || 0), label: 'review points' },
    { val: String(result.cross_bureau_groups?.length || 0), label: 'bureau matches' },
    { val: '0', label: 'hard pulls' },
  ];
  const letterQueue = result.recommended_letter_queue || [];
  const downloads = [
    {
      label: 'Download desktop workbook',
      detail: 'One Excel file with 3-bureau comparison, Metro 2/FCRA review, errors, draft letters, and tracking tabs.',
      href: getScannerOutputDownloadUrl(result.job_id, 'workbook.xlsx'),
      downloadName: 'workbook.xlsx' as const,
      filename: 'credit-vivo-desktop-scanner-output.xlsx',
      primary: true,
    },
    {
      label: 'Download errors worksheet',
      detail: 'CSV opens in Excel and shows each scanner review point.',
      href: getScannerOutputDownloadUrl(result.job_id, 'issues.csv'),
      downloadName: 'issues.csv' as const,
      filename: 'credit-vivo-errors-worksheet.csv',
    },
    {
      label: 'Download tradelines',
      detail: 'CSV list of accounts and report details found by the scanner.',
      href: getScannerOutputDownloadUrl(result.job_id, 'tradelines.csv'),
      downloadName: 'tradelines.csv' as const,
      filename: 'credit-vivo-tradelines.csv',
    },
    {
      label: 'Download draft letters',
      detail: 'Plain-text packet of draft dispute letters for review.',
      href: getScannerOutputDownloadUrl(result.job_id, 'letters.txt'),
      downloadName: 'letters.txt' as const,
      filename: 'credit-vivo-draft-dispute-letters.txt',
    },
  ];
  const scenarioCards = [
    {
      title: 'Bureau dispute',
      body: 'Used when the report shows wrong balance, status, date, duplicate item, or bureau mismatch.',
      next: 'Draft bureau letter, include FCRA notice, wait for response.',
    },
    {
      title: 'Furnisher dispute',
      body: 'Used when the creditor, collector, or debt buyer needs to prove what they are reporting.',
      next: 'Ask for basis of reporting, balance support, payment history, and ownership records.',
    },
    {
      title: 'MOV escalation',
      body: 'Used when the bureau says Verified but the scanner still sees a flaw.',
      next: 'Request method of verification and prepare Strategy B follow-up.',
    },
    {
      title: 'Attorney review',
      body: 'Used for stronger files with repeated verification, strong evidence, or unresolved reporting harm.',
      next: 'Prepare history, delivery proof, responses, and evidence packet.',
    },
  ];
  const trackingSteps: Array<[string, string, boolean]> = [
    ['Drafted', 'Scanner created draft review items', true],
    ['Customer review', 'Customer approval and authorization required', false],
    ['Mailed', 'Certified tracking number saved after mailing', false],
    ['Waiting', 'Response deadline and follow-up dates tracked', false],
    ['Escalation', 'MOV, CFPB/state, or attorney review if needed', false],
  ];

  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-widest text-sky-600 mb-1">
        Member Flow
      </p>
      <h1 className="text-xl font-bold text-navy-900 mb-1">
        Your Findings are organized.
      </h1>
      <p className="text-sm text-navy-400 mb-6 max-w-2xl">
        {result.customer_summary?.message ||
          result.customer_message ||
          'Credit Vivo organized your review items. Nothing is sent without approval.'}
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-xl p-4 border border-navy-100/60 text-center"
          >
            <p className="text-2xl font-bold text-navy-900">{s.val}</p>
            <p className="text-[11px] text-navy-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <section className="bg-white rounded-xl p-5 border border-navy-100/60 mb-5">
        <div className="flex items-center gap-2 mb-4">
          <Download size={16} className="text-sky-600" />
          <h2 className="text-sm font-bold text-navy-900">Scanner desktop-style outputs</h2>
        </div>
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-3">
          {downloads.map((download) => (
            download.href ? (
              <button
                key={download.label}
                type="button"
                onClick={() => void downloadScannerFile(download.downloadName, download.filename)}
                className={`rounded-lg p-4 border text-left transition ${
                  download.primary
                    ? 'border-sky-200 bg-sky-50/70 hover:border-sky-300 hover:bg-sky-50'
                    : 'border-navy-100/50 bg-navy-50/50 hover:border-sky-200 hover:bg-sky-50/40'
                }`}
              >
                <span className="inline-flex items-center gap-2 text-sm font-semibold text-navy-800">
                  <Download size={14} className="text-sky-600" />
                  {download.label}
                </span>
                <span className="block text-[11px] text-navy-500 mt-1 leading-relaxed">
                  {download.detail}
                </span>
              </button>
            ) : (
              <div
                key={download.label}
                className="min-h-[132px] rounded-xl border border-navy-100/60 bg-navy-50/50 p-5 sm:p-6"
              >
                <span className="inline-flex items-center gap-2 text-sm font-semibold text-navy-500">
                  <Download size={14} className="text-navy-300" />
                  {download.label}
                </span>
                <span className="block text-[11px] text-navy-400 mt-1 leading-relaxed">
                  Available after a real scanner run.
                </span>
              </div>
            )
          ))}
        </div>
        <p className="text-[11px] text-navy-400 mt-4">
          These files are generated for the scan job. Do not email real credit reports or raw exports unless the customer approved it.
        </p>
      </section>

      <div className="grid lg:grid-cols-[minmax(0,1fr)_340px] gap-5">
        <div className="bg-white rounded-xl p-5 border border-navy-100/60">
          <h2 className="text-sm font-bold text-navy-900 mb-3">
            Customer-friendly findings
          </h2>
          <p className="text-xs text-navy-400 mb-4">
            We show simple categories. Backend details stay internal until admin review is needed.
          </p>

          <div className="space-y-2">
            {categoryNames.map((cat) => {
              const count = countCategory(cat, result);
              return (
                <div
                  key={cat}
                  className="grid min-h-[76px] grid-cols-[minmax(0,1fr)_auto] items-center gap-4 rounded-xl border border-navy-100/60 bg-navy-50/50 px-5 py-4"
                >
                  <span className="min-w-0 whitespace-normal break-words text-sm font-semibold leading-relaxed text-navy-700">{cat}</span>
                  <span className="whitespace-nowrap rounded-lg bg-white px-3 py-1.5 text-[11px] font-medium text-navy-500 shadow-sm">
                    {count > 0 ? `${count} item${count === 1 ? '' : 's'}` : 'Clear'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="space-y-5">
          <div className="bg-white rounded-xl p-5 border border-navy-100/60">
            <h2 className="text-sm font-bold text-navy-900 mb-3">
              Files reviewed
            </h2>
            <div className="space-y-2">
              {result.files.map((file) => (
                <div
                  key={`${file.filename}-${file.bureau}`}
                  className="flex items-center gap-2 text-xs text-navy-500"
                >
                  <CheckCircle size={14} className="text-mint-600" />
                  <span>
                    {file.bureau}: {file.filename}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-navy-100/60">
            <h2 className="text-sm font-bold text-navy-900 mb-3">
              Important notice
            </h2>
            <div className="flex gap-2 text-xs text-navy-500 leading-relaxed">
              <ShieldCheck size={16} className="text-sky-600 flex-shrink-0 mt-0.5" />
              <p>
                Findings are review data. Credit Vivo does not send letters or disputes
                automatically. Customer approval and admin review are required.
              </p>
            </div>
          </div>
        </div>
      </div>

      {(result.issues_preview || []).length > 0 && (
        <div className="bg-white rounded-xl p-5 border border-navy-100/60 mt-5">
          <h2 className="text-sm font-bold text-navy-900 mb-3">
            Review points
          </h2>
          <div className="space-y-3">
            {(result.issues_preview || []).slice(0, 6).map((issue) => (
              <div
                key={issue.id}
                className="rounded-lg bg-navy-50/50 p-4 border border-navy-100/50"
              >
                <div className="flex items-start gap-2">
                  <AlertCircle size={15} className="text-sky-600 flex-shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="whitespace-normal break-words text-sm font-semibold leading-relaxed text-navy-800">
                      {issue.customer_label}
                    </p>
                    <p className="mt-2 whitespace-normal break-words text-xs leading-relaxed text-navy-500">
                      {issue.customer_explanation}
                    </p>
                    <p className="text-[11px] text-navy-400 mt-2">
                      {issue.suggested_round} • Confidence: {issue.confidence}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <Link
            to="/admin-review"
            className="inline-flex items-center gap-2 mt-5 text-xs font-semibold text-sky-700 hover:text-sky-800"
          >
            Open internal review view
            <ArrowRight size={13} />
          </Link>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-5 mt-5">
        <section className="bg-white rounded-xl p-5 border border-navy-100/60">
          <div className="flex items-center gap-2 mb-4">
            <Route size={16} className="text-sky-600" />
            <h2 className="text-sm font-bold text-navy-900">Dispute scenarios</h2>
          </div>
          <div className="grid gap-3">
            {scenarioCards.map((scenario) => (
              <div key={scenario.title} className="rounded-lg bg-navy-50/50 p-4 border border-navy-100/50">
                <p className="text-sm font-semibold text-navy-800">{scenario.title}</p>
                <p className="text-xs text-navy-500 mt-1 leading-relaxed">{scenario.body}</p>
                <p className="text-[11px] text-sky-700 mt-2 font-semibold">{scenario.next}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white rounded-xl p-5 border border-navy-100/60">
          <div className="flex items-center gap-2 mb-4">
            <MailCheck size={16} className="text-sky-600" />
            <h2 className="text-sm font-bold text-navy-900">Draft dispute letters</h2>
          </div>
          {letterQueue.length ? (
            <div className="space-y-3">
              {letterQueue.slice(0, 4).map((letter) => (
                <div key={letter.letter_id} className="rounded-lg bg-navy-50/50 p-4 border border-navy-100/50">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-navy-800">
                        {letter.letter_subject || formatLabel(letter.letter_type)}
                      </p>
                      <p className="text-xs text-navy-500 mt-1">{letter.round}</p>
                    </div>
                    <span className="rounded-lg bg-white px-2 py-1 text-[10px] font-bold uppercase text-navy-500">
                      {formatLabel(letter.tracking_status)}
                    </span>
                  </div>
                  <p className="text-[11px] text-navy-400 mt-2">
                    Recipient: {formatLabel(letter.recipient_type)} | Delivery: {formatLabel(letter.delivery_method)}
                  </p>
                  {letter.draft_letter_body && (
                    <details className="mt-3 rounded-lg border border-navy-100 bg-white p-3">
                      <summary className="cursor-pointer text-[11px] font-bold uppercase tracking-wider text-sky-700">
                        View draft letter
                      </summary>
                      <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap rounded-md bg-navy-50 p-3 text-[11px] leading-relaxed text-navy-700">
                        {letter.draft_letter_body}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-navy-500">No draft letters are queued yet.</p>
          )}
        </section>
      </div>

      <section className="bg-white rounded-xl p-5 border border-navy-100/60 mt-5">
        <div className="flex items-center gap-2 mb-4">
          <Clock size={16} className="text-sky-600" />
          <h2 className="text-sm font-bold text-navy-900">Customer tracking</h2>
        </div>
        <div className="grid md:grid-cols-5 gap-3">
          {trackingSteps.map(([title, detail, done]) => (
            <div key={title} className="rounded-lg bg-navy-50/50 p-4 border border-navy-100/50">
              <CheckCircle size={15} className={done ? 'text-mint-600' : 'text-navy-300'} />
              <p className="text-sm font-semibold text-navy-800 mt-2">{title}</p>
              <p className="text-[11px] text-navy-500 mt-1 leading-relaxed">{detail}</p>
            </div>
          ))}
        </div>
        <p className="text-[11px] text-navy-400 mt-4">
          Nothing is mailed, disputed, or escalated automatically. Approval and review are required first.
        </p>
      </section>
    </div>
  );
}
