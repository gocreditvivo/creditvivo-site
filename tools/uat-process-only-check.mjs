import { readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = process.cwd();
const mustContain = [
  ['src/App.tsx', '/member/dashboard'],
  ['src/App.tsx', '/founder/uat-1-35-report'],
  ['src/lib/processOnlyMode.ts', 'PROCESS_ONLY_MODE: true'],
  ['src/lib/processOnlyMode.ts', 'PRODUCTION_SEND_MODE: false'],
  ['src/lib/processOnlyTestData.ts', 'uatSteps'],
  ['src/pages/FounderProcessPage.tsx', 'UatScorecard'],
  ['src/pages/MemberProcessPage.tsx', 'Real upload blocked'],
];
const forbidden = [
  ['src/App.tsx', '/admin-review'],
  ['src/pages/MemberProcessPage.tsx', 'localStorage'],
  ['src/pages/FounderProcessPage.tsx', 'localStorage'],
  ['src/pages/MemberProcessPage.tsx', 'createObjectURL'],
  ['src/pages/FounderProcessPage.tsx', 'createObjectURL'],
];
let failed = false;
for (const [file, text] of mustContain) {
  const body = readFileSync(join(root, file), 'utf8');
  if (!body.includes(text)) { console.error(`FAIL missing ${text} in ${file}`); failed = true; }
}
for (const [file, text] of forbidden) {
  const body = readFileSync(join(root, file), 'utf8');
  if (body.includes(text)) { console.error(`FAIL forbidden ${text} in ${file}`); failed = true; }
}
const routeCount = (readFileSync(join(root, 'src/lib/processOnlyTestData.ts'), 'utf8').match(/^  \{ step:/gm) || []).length;
if (routeCount !== 35) { console.error(`FAIL expected 35 UAT steps, found ${routeCount}`); failed = true; }
if (failed) process.exit(1);
console.log('PASS process-only UAT static checks');

