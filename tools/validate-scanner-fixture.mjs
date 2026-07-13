import { readFileSync } from 'node:fs';
const fixture = readFileSync('src/lib/processOnlyTestData.ts', 'utf8');
const required = ['Experian', 'Equifax', 'TransUnion', 'account_number_masked', 'confidence_score', 'possible_issue'];
const missing = required.filter((item) => !fixture.includes(item));
if (missing.length) { console.error(`FAIL scanner fixture missing: ${missing.join(', ')}`); process.exit(1); }
if (/\b\d{3}-\d{2}-\d{4}\b/.test(fixture)) { console.error('FAIL fixture contains SSN-like value'); process.exit(1); }
console.log('PASS scanner fixture validation');
