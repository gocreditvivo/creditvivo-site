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
  tradeline_id uuid,
  issue_id uuid,
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
