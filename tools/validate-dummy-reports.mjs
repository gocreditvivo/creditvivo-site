import { readFileSync } from 'node:fs';

const fixture = readFileSync('src/lib/dummyCreditReports.ts', 'utf8');
const requiredIssueTypes = [
  'bankruptcy',
  'medical_collection',
  'mortgage_late',
  'reaging',
  'charge_off',
  'duplicate_collection',
  'bureau_mismatch',
  'thin_file',
  'high_utilization',
  'identity_mismatch',
];

let failed = false;
const reportCount = (fixture.match(/id: 'cv-test-\d{3}'/g) || []).length;
if (reportCount !== 10) {
  console.error(`FAIL expected 10 dummy reports, found ${reportCount}`);
  failed = true;
}

for (const issue of requiredIssueTypes) {
  if (!fixture.includes(`'${issue}'`)) {
    console.error(`FAIL missing dummy issue type: ${issue}`);
    failed = true;
  }
}

for (const bureau of ['Experian', 'Equifax', 'TransUnion']) {
  if (!fixture.includes(bureau)) {
    console.error(`FAIL missing bureau: ${bureau}`);
    failed = true;
  }
}

for (const requiredText of ['draft_letter_preview', 'email_preview', 'tracking_stages', 'score_start', 'score_current', 'score_goal']) {
  if (!fixture.includes(requiredText)) {
    console.error(`FAIL missing required report field: ${requiredText}`);
    failed = true;
  }
}

if (/\b\d{3}-\d{2}-\d{4}\b/.test(fixture)) {
  console.error('FAIL dummy reports contain SSN-like value');
  failed = true;
}

if (/\b\d{9,}\b/.test(fixture)) {
  console.error('FAIL dummy reports contain long unmasked number');
  failed = true;
}

if (failed) process.exit(1);
console.log('PASS dummy credit report validation');
