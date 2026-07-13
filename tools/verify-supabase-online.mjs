import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL;
const anonKey = process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY;

const forbiddenPublicSecretNames = [
  'VITE_SUPABASE_SERVICE_ROLE_KEY',
  'VITE_SERVICE_ROLE_KEY',
  'NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY',
  'NEXT_PUBLIC_SERVICE_ROLE_KEY',
];

const expectedTables = [
  'customers',
  'credit_reports',
  'report_uploads',
  'bureau_reports',
  'tradelines',
  'negative_tradelines',
  'bureau_comparisons',
  'ai_findings',
  'dispute_cases',
  'dispute_items',
  'document_vault',
  'customer_approval_logs',
  'admin_approval_logs',
  'compliance_review_logs',
  'audit_logs',
  'ai_learning_events',
  'scanner_corrections',
  'compliance_blocked_phrases',
];

const sensitiveTables = expectedTables.filter((table) => table !== 'compliance_blocked_phrases');

let failed = false;

for (const name of forbiddenPublicSecretNames) {
  if (process.env[name]) {
    console.error(`FAIL ${name} must never be configured. Service role keys must be server-side only.`);
    failed = true;
  }
}

if (!supabaseUrl || !anonKey) {
  console.log('BLOCKED Supabase online verification needs VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY or SUPABASE_URL and SUPABASE_ANON_KEY.');
  console.log('BLOCKED No service-role key is needed or allowed for this verifier.');
  process.exit(failed ? 1 : 0);
}

if (process.env.SUPABASE_SERVICE_ROLE_KEY) {
  console.log('NOTICE SUPABASE_SERVICE_ROLE_KEY is present in this shell but will not be used by this verifier.');
}

const supabase = createClient(supabaseUrl, anonKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});

for (const table of expectedTables) {
  const { data, error } = await supabase.from(table).select('id').limit(1);

  if (error) {
    const message = `${error.code || 'NO_CODE'} ${error.message || ''}`;
    if (message.includes('relation') || message.includes('does not exist') || error.code === 'PGRST205') {
      console.error(`FAIL missing expected table or REST exposure: ${table} (${message})`);
      failed = true;
      continue;
    }

    console.log(`PASS ${table}: public anonymous read blocked or restricted (${message})`);
    continue;
  }

  if (sensitiveTables.includes(table) && Array.isArray(data) && data.length > 0) {
    console.error(`FAIL ${table}: anonymous public read returned rows. Sensitive customer tables must not expose data.`);
    failed = true;
    continue;
  }

  console.log(`PASS ${table}: table reachable and no anonymous sensitive data exposed.`);
}

if (failed) process.exit(1);

console.log('PASS Supabase online anonymous/RLS smoke verification complete.');
