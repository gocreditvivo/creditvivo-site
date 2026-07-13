-- Credit Vivo A+ engine foundation.
-- Apply to staging first. Do not apply to production without Tim approval.
-- This migration stores only structured workflow metadata. Do not store raw
-- credit report text, full SSNs, full DOBs, full account numbers, or public
-- document URLs.

create extension if not exists pgcrypto;

create or replace function public.credit_vivo_role()
returns text
language sql
stable
as $$
  select coalesce(
    nullif((select auth.jwt()) -> 'app_metadata' ->> 'credit_vivo_role', ''),
    'customer'
  );
$$;

create or replace function public.credit_vivo_is_admin()
returns boolean
language sql
stable
as $$
  select public.credit_vivo_role() in ('admin', 'founder', 'compliance_admin');
$$;

create table if not exists public.customers (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  display_name text,
  email text,
  phone_last4 text,
  status text not null default 'active',
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create or replace function public.credit_vivo_can_access_customer(customer_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.customers c
    where c.id = customer_uuid
      and (
        c.user_id = (select auth.uid())
        or public.credit_vivo_is_admin()
      )
  );
$$;

create table if not exists public.credit_reports (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  report_label text not null default 'consumer_credit_report',
  source_type text not null default 'uploaded_pdf',
  parser_engine text not null default 'credit_vivo_native_parser',
  process_mode text not null default 'process_only',
  status text not null default 'draft_review',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.report_uploads (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  credit_report_id uuid references public.credit_reports(id) on delete cascade,
  file_name text not null,
  file_type text not null,
  storage_bucket text not null default 'document-vault',
  storage_path text not null,
  sha256_hash text,
  upload_status text not null default 'received',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.bureau_reports (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  credit_report_id uuid not null references public.credit_reports(id) on delete cascade,
  bureau text not null check (bureau in ('Experian', 'Equifax', 'TransUnion', 'Unknown')),
  detected_confidence numeric(5, 4),
  normalized_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.tradelines (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  credit_report_id uuid not null references public.credit_reports(id) on delete cascade,
  bureau_report_id uuid references public.bureau_reports(id) on delete set null,
  bureau text not null default 'Unknown',
  account_name text,
  account_number_last4 text,
  account_type text,
  creditor_classification text,
  original_creditor text,
  status text,
  balance_cents integer,
  past_due_cents integer,
  date_opened date,
  date_reported date,
  date_last_active date,
  payment_status text,
  confidence_score numeric(5, 4),
  evidence_snippet text,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.negative_tradelines (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  tradeline_id uuid references public.tradelines(id) on delete cascade,
  negative_type text not null,
  severity text not null default 'review',
  recency_band text,
  bureau_coverage text[] not null default array[]::text[],
  possible_issue text,
  dispute_strength_score numeric(5, 4),
  status text not null default 'needs_review',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.bureau_comparisons (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  credit_report_id uuid not null references public.credit_reports(id) on delete cascade,
  comparison_key text not null,
  matched_bureaus text[] not null default array[]::text[],
  missing_bureaus text[] not null default array[]::text[],
  mismatch_summary jsonb not null default '{}'::jsonb,
  risk_status text not null default 'review',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ai_findings (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  credit_report_id uuid references public.credit_reports(id) on delete cascade,
  related_record_id uuid,
  finding_type text not null,
  summary text not null,
  confidence_score numeric(5, 4),
  safe_customer_language text not null,
  admin_notes text,
  status text not null default 'draft_review',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.dispute_cases (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  case_status text not null default 'draft_review',
  compliance_status text not null default 'blocked_until_review',
  customer_approved_at timestamptz,
  admin_approved_at timestamptz,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.dispute_items (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  dispute_case_id uuid not null references public.dispute_cases(id) on delete cascade,
  negative_tradeline_id uuid references public.negative_tradelines(id) on delete set null,
  action_type text not null default 'bureau_dispute',
  draft_letter_text text,
  packet_status text not null default 'draft_only',
  send_status text not null default 'not_sent',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.document_vault (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  related_record_id uuid,
  document_type text not null,
  storage_bucket text not null default 'document-vault',
  storage_path text not null,
  file_name text not null,
  mime_type text,
  sha256_hash text,
  public_url text,
  vault_status text not null default 'private',
  created_at timestamptz not null default timezone('utc', now()),
  constraint document_vault_no_public_url check (public_url is null)
);

create table if not exists public.customer_approval_logs (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  action_type text not null,
  related_record_id uuid,
  approval_text text not null,
  approvals_reviewer text not null default 'auto_review',
  approved_at timestamptz not null default timezone('utc', now()),
  ip_address inet,
  user_agent text
);

create table if not exists public.admin_approval_logs (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  action_type text not null,
  related_record_id uuid,
  approval_text text not null,
  approvals_reviewer text not null default 'auto_review',
  approved_by uuid references auth.users(id) on delete set null,
  approved_at timestamptz not null default timezone('utc', now()),
  ip_address inet,
  user_agent text
);

create table if not exists public.compliance_review_logs (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references public.customers(id) on delete cascade,
  action_type text not null,
  related_record_id uuid,
  review_status text not null default 'blocked',
  blocked_reasons text[] not null default array[]::text[],
  safe_wording_passed boolean not null default false,
  reviewer_role text not null default 'compliance_admin',
  approvals_reviewer text not null default 'auto_review',
  reviewed_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references public.customers(id) on delete set null,
  actor_user_id uuid references auth.users(id) on delete set null,
  actor_role text,
  action_type text not null,
  related_record_id uuid,
  event_summary text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ai_learning_events (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references public.customers(id) on delete set null,
  source_type text not null,
  source_record_id uuid,
  correction_summary text not null,
  human_review_status text not null default 'pending_review',
  model_update_status text not null default 'not_applied',
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.scanner_corrections (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references public.customers(id) on delete set null,
  credit_report_id uuid references public.credit_reports(id) on delete cascade,
  field_name text not null,
  scanner_value text,
  corrected_value text,
  correction_reason text,
  reviewer_user_id uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.compliance_blocked_phrases (
  id uuid primary key default gen_random_uuid(),
  phrase text not null unique,
  severity text not null default 'block',
  created_at timestamptz not null default timezone('utc', now())
);

insert into public.compliance_blocked_phrases (phrase, severity)
values
  ('guaranteed deletion', 'block'),
  ('guaranteed score increase', 'block'),
  ('will be deleted', 'block'),
  ('will increase your score', 'block'),
  ('erase bad credit', 'block'),
  ('approved for legal action', 'block'),
  ('lawsuit guaranteed', 'block'),
  ('100% guaranteed', 'block')
on conflict (phrase) do nothing;

create index if not exists customers_user_id_idx on public.customers(user_id);
create index if not exists credit_reports_customer_id_idx on public.credit_reports(customer_id);
create index if not exists report_uploads_customer_id_idx on public.report_uploads(customer_id);
create index if not exists bureau_reports_customer_id_idx on public.bureau_reports(customer_id);
create index if not exists tradelines_customer_id_idx on public.tradelines(customer_id);
create index if not exists negative_tradelines_customer_id_idx on public.negative_tradelines(customer_id);
create index if not exists bureau_comparisons_customer_id_idx on public.bureau_comparisons(customer_id);
create index if not exists ai_findings_customer_id_idx on public.ai_findings(customer_id);
create index if not exists dispute_cases_customer_id_idx on public.dispute_cases(customer_id);
create index if not exists dispute_items_customer_id_idx on public.dispute_items(customer_id);
create index if not exists document_vault_customer_id_idx on public.document_vault(customer_id);
create index if not exists customer_approval_logs_customer_id_idx on public.customer_approval_logs(customer_id);
create index if not exists admin_approval_logs_customer_id_idx on public.admin_approval_logs(customer_id);
create index if not exists compliance_review_logs_customer_id_idx on public.compliance_review_logs(customer_id);
create index if not exists audit_logs_customer_id_idx on public.audit_logs(customer_id);
create index if not exists ai_learning_events_customer_id_idx on public.ai_learning_events(customer_id);
create index if not exists scanner_corrections_customer_id_idx on public.scanner_corrections(customer_id);

alter table public.customers enable row level security;
alter table public.credit_reports enable row level security;
alter table public.report_uploads enable row level security;
alter table public.bureau_reports enable row level security;
alter table public.tradelines enable row level security;
alter table public.negative_tradelines enable row level security;
alter table public.bureau_comparisons enable row level security;
alter table public.ai_findings enable row level security;
alter table public.dispute_cases enable row level security;
alter table public.dispute_items enable row level security;
alter table public.document_vault enable row level security;
alter table public.customer_approval_logs enable row level security;
alter table public.admin_approval_logs enable row level security;
alter table public.compliance_review_logs enable row level security;
alter table public.audit_logs enable row level security;
alter table public.ai_learning_events enable row level security;
alter table public.scanner_corrections enable row level security;
alter table public.compliance_blocked_phrases enable row level security;

drop policy if exists "cv customers own or admin read" on public.customers;
create policy "cv customers own or admin read"
  on public.customers for select to authenticated
  using (user_id = (select auth.uid()) or public.credit_vivo_is_admin());

drop policy if exists "cv customers own insert" on public.customers;
create policy "cv customers own insert"
  on public.customers for insert to authenticated
  with check (user_id = (select auth.uid()) or public.credit_vivo_is_admin());

drop policy if exists "cv customers admin update" on public.customers;
create policy "cv customers admin update"
  on public.customers for update to authenticated
  using (public.credit_vivo_is_admin())
  with check (public.credit_vivo_is_admin());

do $$
declare
  table_name text;
begin
  foreach table_name in array array[
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
    'scanner_corrections'
  ]
  loop
    execute format('drop policy if exists "cv %I customer or admin read" on public.%I', table_name, table_name);
    execute format(
      'create policy "cv %I customer or admin read" on public.%I for select to authenticated using (public.credit_vivo_can_access_customer(customer_id))',
      table_name,
      table_name
    );

    execute format('drop policy if exists "cv %I admin insert" on public.%I', table_name, table_name);
    execute format(
      'create policy "cv %I admin insert" on public.%I for insert to authenticated with check (public.credit_vivo_can_access_customer(customer_id) and public.credit_vivo_is_admin())',
      table_name,
      table_name
    );

    execute format('drop policy if exists "cv %I admin update" on public.%I', table_name, table_name);
    execute format(
      'create policy "cv %I admin update" on public.%I for update to authenticated using (public.credit_vivo_can_access_customer(customer_id) and public.credit_vivo_is_admin()) with check (public.credit_vivo_can_access_customer(customer_id) and public.credit_vivo_is_admin())',
      table_name,
      table_name
    );
  end loop;
end $$;

drop policy if exists "cv blocked phrases authenticated read" on public.compliance_blocked_phrases;
create policy "cv blocked phrases authenticated read"
  on public.compliance_blocked_phrases for select to authenticated
  using (true);

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'document-vault',
  'document-vault',
  false,
  26214400,
  array['application/pdf', 'image/jpeg', 'image/png', 'image/heic']
)
on conflict (id) do update
set public = false,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "cv document vault owner read" on storage.objects;
create policy "cv document vault owner read"
  on storage.objects for select to authenticated
  using (
    bucket_id = 'document-vault'
    and exists (
      select 1
      from public.document_vault dv
      where dv.storage_bucket = bucket_id
        and dv.storage_path = name
        and public.credit_vivo_can_access_customer(dv.customer_id)
    )
  );

drop policy if exists "cv document vault admin write" on storage.objects;
create policy "cv document vault admin write"
  on storage.objects for insert to authenticated
  with check (
    bucket_id = 'document-vault'
    and public.credit_vivo_is_admin()
  );
