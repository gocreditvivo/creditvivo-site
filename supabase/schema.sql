create extension if not exists pgcrypto;

create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  full_name text,
  email text,
  phone text,
  state text,
  role text default 'customer',
  created_at timestamptz default now()
);

create table if not exists credit_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  file_url text not null,
  original_filename text,
  report_type text,
  detected_bureaus text[],
  raw_text text,
  scan_status text default 'uploaded',
  extraction_confidence numeric,
  scanner_version text,
  self_check_status text default 'pending',
  customer_findings_released boolean default false,
  uploaded_at timestamptz default now()
);

create table if not exists tradelines (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  report_id uuid references credit_reports(id),
  bureau text,
  creditor_name text,
  account_number_masked text,
  account_type text,
  account_status text,
  balance text,
  past_due text,
  date_opened text,
  date_closed text,
  date_reported text,
  last_payment_date text,
  charge_off_date text,
  collection_date text,
  original_creditor text,
  collection_agency text,
  creditor_classification text,
  payment_history text,
  remarks text,
  is_negative boolean default false,
  negative_reason text,
  raw_text_snippet text,
  confidence_score numeric,
  created_at timestamptz default now()
);

create table if not exists bureau_comparisons (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  normalized_account_key text,
  transunion_data jsonb,
  experian_data jsonb,
  equifax_data jsonb,
  mismatches jsonb,
  issue_summary text,
  confidence_score numeric,
  created_at timestamptz default now()
);

create table if not exists credit_issues (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  tradeline_id uuid references tradelines(id),
  comparison_id uuid references bureau_comparisons(id),
  issue_type text,
  issue_description text,
  bureau text,
  severity text,
  dispute_strength_score integer,
  recommended_action text,
  possible_fcra_rules text[],
  possible_metro2_rules text[],
  evidence_refs text[],
  self_check_status text default 'pending',
  customer_selected boolean default false,
  admin_review_status text default 'pending',
  compliance_review_status text default 'pending',
  created_at timestamptz default now()
);

create table if not exists disputes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  issue_id uuid references credit_issues(id),
  bureau text,
  furnisher text,
  dispute_reason text,
  letter_body text,
  status text default 'draft',
  customer_approved boolean default false,
  admin_approved boolean default false,
  compliance_approved boolean default false,
  automatic_send_allowed boolean default false,
  mailing_allowed boolean default false,
  sent_at timestamptz,
  response_due_at timestamptz,
  created_at timestamptz default now()
);

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  dispute_id uuid references disputes(id),
  document_type text,
  file_url text,
  status text default 'stored',
  created_at timestamptz default now()
);

create table if not exists attorney_support_queue (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  dispute_id uuid references disputes(id),
  issue_id uuid references credit_issues(id),
  reason text,
  summary text,
  evidence_packet_url text,
  status text default 'review_queue_preview',
  customer_approval_required boolean default true,
  admin_review_required boolean default true,
  compliance_review_required boolean default true,
  automatic_escalation_allowed boolean default false,
  created_at timestamptz default now()
);

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  actor_role text,
  action text,
  metadata jsonb,
  created_at timestamptz default now()
);

create table if not exists score_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  starting_score integer,
  current_score integer,
  goal_score integer,
  score_source text,
  goal_reason text,
  last_updated timestamptz default now(),
  created_at timestamptz default now()
);

create table if not exists score_impact_estimates (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  tradeline_id uuid references tradelines(id),
  issue_id uuid references credit_issues(id),
  impact_level text,
  possible_min integer,
  possible_max integer,
  priority_score integer,
  explanation text,
  next_action text,
  created_at timestamptz default now()
);

create table if not exists score_scenarios (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  scenario_name text,
  selected_account_ids text[],
  possible_min integer,
  possible_max integer,
  headline text,
  explanation text,
  created_at timestamptz default now()
);
