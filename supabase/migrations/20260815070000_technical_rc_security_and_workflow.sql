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

ALTER TABLE public.credit_cases ADD COLUMN IF NOT EXISTS current_scan_id UUID;
ALTER TABLE public.credit_cases DROP CONSTRAINT IF EXISTS credit_cases_current_scan_id_fkey;
ALTER TABLE public.credit_cases ADD CONSTRAINT credit_cases_current_scan_id_fkey
    FOREIGN KEY (current_scan_id) REFERENCES public.credit_scans(id) ON DELETE RESTRICT;

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

CREATE POLICY "Owners read their cases" ON public.credit_cases
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners read their scans" ON public.credit_scans
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners read their approvals" ON public.customer_approvals
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners read their scan artifacts" ON public.scan_artifacts
    FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY "Owners read their audit events" ON public.case_audit_events
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

REVOKE INSERT, UPDATE, DELETE ON public.credit_cases FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.credit_scans FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.customer_approvals FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.scan_artifacts FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.case_audit_events FROM authenticated;
GRANT SELECT ON public.credit_cases, public.credit_scans, public.customer_approvals,
    public.scan_artifacts, public.case_audit_events TO authenticated;

CREATE UNIQUE INDEX IF NOT EXISTS one_active_approval_per_scope
    ON public.customer_approvals (case_id, scan_id, approval_scope)
    WHERE revoked_at IS NULL;

CREATE OR REPLACE FUNCTION public.record_credit_approval(
    p_case_id UUID, p_scan_id UUID, p_artifact_sha256 TEXT, p_approval_scope TEXT
) RETURNS public.customer_approvals
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
    approval public.customer_approvals;
BEGIN
    IF p_approval_scope NOT IN ('review_findings', 'generate_drafts', 'send_dispute') THEN
        RAISE EXCEPTION 'invalid approval scope';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM public.credit_cases c
        JOIN public.credit_scans s ON s.id = c.current_scan_id
        WHERE c.id = p_case_id AND c.owner_id = auth.uid()
          AND s.id = p_scan_id AND s.owner_id = auth.uid()
          AND s.artifact_sha256 = lower(p_artifact_sha256)
    ) THEN
        RAISE EXCEPTION 'approval does not match current owned scan';
    END IF;
    INSERT INTO public.customer_approvals (
        case_id, scan_id, owner_id, artifact_sha256, approval_scope
    ) VALUES (p_case_id, p_scan_id, auth.uid(), lower(p_artifact_sha256), p_approval_scope)
    RETURNING * INTO approval;
    INSERT INTO public.case_audit_events (case_id, owner_id, event_type, event_payload)
    VALUES (p_case_id, auth.uid(), 'customer_approval_recorded',
        jsonb_build_object('scan_id', p_scan_id, 'scope', p_approval_scope, 'artifact_sha256', lower(p_artifact_sha256)));
    RETURN approval;
END;
$$;

CREATE OR REPLACE FUNCTION public.transition_credit_case(p_case_id UUID, p_status TEXT)
RETURNS public.credit_cases
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
    current_case public.credit_cases;
    updated_case public.credit_cases;
    required_scope TEXT;
    trusted_role TEXT;
BEGIN
    SELECT * INTO current_case FROM public.credit_cases
    WHERE id = p_case_id AND owner_id = auth.uid() FOR UPDATE;
    IF current_case.id IS NULL THEN RAISE EXCEPTION 'case not found'; END IF;
    IF NOT (
        (current_case.status = 'draft' AND p_status = 'review') OR
        (current_case.status = 'review' AND p_status = 'approved') OR
        (current_case.status = 'approved' AND p_status = 'sent') OR
        (current_case.status = 'sent' AND p_status = 'response_received') OR
        (current_case.status = 'response_received' AND p_status = 'closed')
    ) THEN RAISE EXCEPTION 'invalid case transition'; END IF;
    IF p_status IN ('approved', 'sent') THEN
        required_scope := CASE WHEN p_status = 'approved' THEN 'generate_drafts' ELSE 'send_dispute' END;
        IF NOT EXISTS (
            SELECT 1 FROM public.customer_approvals a
            JOIN public.credit_scans s ON s.id = current_case.current_scan_id
            WHERE a.case_id = current_case.id AND a.scan_id = current_case.current_scan_id
              AND a.owner_id = auth.uid() AND a.approval_scope = required_scope
              AND a.revoked_at IS NULL AND a.artifact_sha256 = s.artifact_sha256
        ) THEN RAISE EXCEPTION 'matching current-artifact approval required'; END IF;
    END IF;
    IF p_status = 'sent' THEN
        trusted_role := coalesce(auth.jwt() -> 'app_metadata' ->> 'role', '');
        IF trusted_role NOT IN ('founder', 'admin') THEN RAISE EXCEPTION 'admin review required'; END IF;
    END IF;
    UPDATE public.credit_cases SET status = p_status, updated_at = now()
    WHERE id = current_case.id RETURNING * INTO updated_case;
    INSERT INTO public.case_audit_events (case_id, owner_id, event_type, event_payload)
    VALUES (current_case.id, auth.uid(), 'case_status_changed',
        jsonb_build_object('from', current_case.status, 'to', p_status, 'scan_id', current_case.current_scan_id));
    RETURN updated_case;
END;
$$;

CREATE OR REPLACE FUNCTION public.revoke_credit_approval(p_case_id UUID, p_approval_id UUID)
RETURNS public.customer_approvals
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
    revoked public.customer_approvals;
BEGIN
    UPDATE public.customer_approvals
    SET revoked_at = now()
    WHERE id = p_approval_id AND case_id = p_case_id AND owner_id = auth.uid() AND revoked_at IS NULL
    RETURNING * INTO revoked;
    IF revoked.id IS NULL THEN RAISE EXCEPTION 'active approval not found'; END IF;
    INSERT INTO public.case_audit_events (case_id, owner_id, event_type, event_payload)
    VALUES (p_case_id, auth.uid(), 'customer_approval_revoked',
        jsonb_build_object('approval_id', p_approval_id, 'scan_id', revoked.scan_id, 'scope', revoked.approval_scope));
    RETURN revoked;
END;
$$;

REVOKE ALL ON FUNCTION public.record_credit_approval(UUID, UUID, TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.transition_credit_case(UUID, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.revoke_credit_approval(UUID, UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.record_credit_approval(UUID, UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.transition_credit_case(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.revoke_credit_approval(UUID, UUID) TO authenticated;

-- Customer artifacts live in a private bucket and must begin with auth.uid().
INSERT INTO storage.buckets (id, name, public)
VALUES ('credit-report-artifacts', 'credit-report-artifacts', false)
ON CONFLICT (id) DO UPDATE SET public = false;

CREATE POLICY "Owners read private credit artifacts" ON storage.objects
    FOR SELECT TO authenticated
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
