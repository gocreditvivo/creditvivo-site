import { Link } from 'react-router-dom';
import { AlertCircle, ArrowRight, CheckCircle, Download, FileSearch, ShieldCheck } from 'lucide-react';
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

function downloadFindings(result: NonNullable<ReturnType<typeof getLastScanResult>>) {
  const exportData = {
    exportedAt: new Date().toISOString(),
    jobId: result.job_id,
    status: result.status,
    summary: result.customer_summary,
    files: result.files || [],
    reviewItemsCount: result.review_items_count || 0,
    reviewItemsPreview: result.review_items_preview || [],
    issuesCount: result.issues_count || 0,
    issuesPreview: result.issues_preview || [],
    crossBureauGroups: result.cross_bureau_groups || [],
  };
  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `credit-vivo-findings-${result.job_id || new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function Findings() {
  const result = getLastScanResult();

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

  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-widest text-sky-600 mb-1">
        Member Flow
      </p>
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-navy-900 mb-1">
            Your Findings are organized.
          </h1>
          <p className="text-sm text-navy-400 max-w-2xl">
            {result.customer_summary?.message ||
              result.customer_message ||
              'Credit Vivo organized your review items. Nothing is sent without approval.'}
          </p>
        </div>
        <button
          type="button"
          onClick={() => downloadFindings(result)}
          className="btn-primary text-xs py-2.5 justify-center shrink-0"
        >
          Download Findings
          <Download size={14} />
        </button>
      </div>

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
                  className="flex items-center justify-between py-3 px-4 bg-navy-50/50 rounded-lg"
                >
                  <span className="text-sm font-medium text-navy-700">{cat}</span>
                  <span className="text-[11px] text-navy-400">
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
                  <div>
                    <p className="text-sm font-semibold text-navy-800">
                      {issue.customer_label}
                    </p>
                    <p className="text-xs text-navy-500 mt-1 leading-relaxed">
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
    </div>
  );
}
