-- CreditVivo Technical RC: owner isolation, private artifacts, immutable approvals,
-- and encrypted-at-rest Plaid secrets. Apply to staging only after review.

CREATE EXTENSION IF NOT EXISTS supabase_vault WITH SCHEMA vault;

CREATE TABLE IF NOT EXISTS public.credit_cases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    owner_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'sent', 'response_received', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.credit_scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES public.credit_cases(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    artifact_sha256 TEXT NOT NULL CHECK (artifact_sha256 ~ '^[a-f0-9]{64}$'),
    scanner_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_id, job_id)
);

CREATE TABLE IF NOT EXISTS public.customer_approvals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES public.credit_cases(id) ON DELETE CASCADE,
    scan_id UUID NOT NULL REFERENCES public.credit_scans(id) ON DELETE RESTRICT,
    owner_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    artifact_sha256 TEXT NOT NULL CHECK (artifact_sha256 ~ '^[a-f0-9]{64}$'),
    approval_scope TEXT NOT NULL CHECK (approval_scope IN ('review_findings', 'generate_drafts', 'send_dispute')),
    approved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ,
    CHECK (revoked_at IS NULL OR revoked_at >= approved_at)
);

CREATE TABLE IF NOT EXISTS public.scan_artifacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID NOT NULL REFERENCES public.credit_scans(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    artifact_kind TEXT NOT NULL,
    object_path TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (scan_id, artifact_kind)
);

CREATE TABLE IF NOT EXISTS public.case_audit_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES public.credit_cases(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.credit_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.case_audit_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Owners manage their cases" ON public.credit_cases
    FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid());
CREATE POLICY "Owners manage their scans" ON public.credit_scans
    FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (
        owner_id = auth.uid() AND EXISTS (
            SELECT 1 FROM public.credit_cases c WHERE c.id = case_id AND c.owner_id = auth.uid()
        )
    );
CREATE POLICY "Owners read and create their approvals" ON public.customer_approvals
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners create their approvals" ON public.customer_approvals
    FOR INSERT TO authenticated WITH CHECK (
        owner_id = auth.uid() AND EXISTS (
            SELECT 1 FROM public.credit_scans s
            WHERE s.id = scan_id AND s.case_id = case_id AND s.owner_id = auth.uid()
              AND s.artifact_sha256 = artifact_sha256
        )
    );
CREATE POLICY "Owners revoke their approvals" ON public.customer_approvals
    FOR UPDATE TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid());
CREATE POLICY "Owners manage their scan artifacts" ON public.scan_artifacts
    FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (
        owner_id = auth.uid() AND EXISTS (
            SELECT 1 FROM public.credit_scans s WHERE s.id = scan_id AND s.owner_id = auth.uid()
        )
    );
CREATE POLICY "Owners read and create audit events" ON public.case_audit_events
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners create audit events" ON public.case_audit_events
    FOR INSERT TO authenticated WITH CHECK (
        owner_id = auth.uid() AND EXISTS (
            SELECT 1 FROM public.credit_cases c WHERE c.id = case_id AND c.owner_id = auth.uid()
        )
    );

-- Customer artifacts live in a private bucket and must begin with auth.uid().
INSERT INTO storage.buckets (id, name, public)
VALUES ('credit-report-artifacts', 'credit-report-artifacts', false)
ON CONFLICT (id) DO UPDATE SET public = false;

CREATE POLICY "Owners read private credit artifacts" ON storage.objects
    FOR SELECT TO authenticated
    USING (bucket_id = 'credit-report-artifacts' AND (storage.foldername(name))[1] = auth.uid()::text);
CREATE POLICY "Owners upload private credit artifacts" ON storage.objects
    FOR INSERT TO authenticated
    WITH CHECK (bucket_id = 'credit-report-artifacts' AND (storage.foldername(name))[1] = auth.uid()::text);
CREATE POLICY "Owners delete private credit artifacts" ON storage.objects
    FOR DELETE TO authenticated
    USING (bucket_id = 'credit-report-artifacts' AND (storage.foldername(name))[1] = auth.uid()::text);

-- Move legacy Plaid access tokens into Supabase Vault. The public table retains
-- only an opaque Vault id, and authenticated callers receive metadata columns only.
ALTER TABLE public.linked_bank_accounts
    ADD COLUMN IF NOT EXISTS plaid_access_token_secret_id UUID;

DO $$
DECLARE
    account_row RECORD;
    new_secret_id UUID;
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'linked_bank_accounts' AND column_name = 'plaid_access_token'
    ) THEN
        FOR account_row IN
            SELECT id, plaid_access_token FROM public.linked_bank_accounts
            WHERE plaid_access_token IS NOT NULL AND plaid_access_token_secret_id IS NULL
        LOOP
            SELECT vault.create_secret(
                account_row.plaid_access_token,
                'creditvivo-plaid-' || account_row.id::text,
                'Migrated by Technical RC security migration'
            ) INTO new_secret_id;
            UPDATE public.linked_bank_accounts
            SET plaid_access_token_secret_id = new_secret_id
            WHERE id = account_row.id;
        END LOOP;
    END IF;
END $$;

REVOKE ALL ON public.linked_bank_accounts FROM authenticated;
GRANT SELECT (id, profile_id, institution_name, plaid_item_id, created_at)
    ON public.linked_bank_accounts TO authenticated;

-- Refuse to remove the plaintext column unless every existing secret moved.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.linked_bank_accounts
        WHERE plaid_access_token IS NOT NULL AND plaid_access_token_secret_id IS NULL
    ) THEN
        RAISE EXCEPTION 'Plaid token migration incomplete; refusing to continue';
    END IF;
END $$;

ALTER TABLE public.linked_bank_accounts DROP COLUMN IF EXISTS plaid_access_token;
