from pathlib import Path

from fastapi.testclient import TestClient

import main


CASE_ID = "00000000-0000-4000-8000-000000000001"
SCAN_ID = "00000000-0000-4000-8000-000000000002"
ARTIFACT_HASH = "a" * 64


def make_client(monkeypatch):
    monkeypatch.setattr(
        main,
        "authenticate_scanner_request",
        lambda _auth: main.AuthenticatedPrincipal("00000000-0000-4000-8000-000000000003", "tenant-a", "admin"),
    )
    return TestClient(main.app)


def test_approval_uses_one_atomic_current_artifact_rpc(monkeypatch):
    client = make_client(monkeypatch)
    calls = []

    def fake_request(method, resource, authorization, **kwargs):
        calls.append((method, resource, kwargs["json_body"]))
        return {"id": "approval-id", "artifact_sha256": ARTIFACT_HASH}

    monkeypatch.setattr(main, "_supabase_user_request", fake_request)
    response = client.post(
        f"/api/cases/{CASE_ID}/approve",
        headers={"Authorization": "Bearer synthetic"},
        json={"scan_id": SCAN_ID, "artifact_sha256": ARTIFACT_HASH, "approval_scope": "generate_drafts"},
    )
    assert response.status_code == 200
    assert calls == [(
        "POST",
        "rpc/record_credit_approval",
        {
            "p_case_id": CASE_ID,
            "p_scan_id": SCAN_ID,
            "p_artifact_sha256": ARTIFACT_HASH,
            "p_approval_scope": "generate_drafts",
        },
    )]


def test_case_transition_uses_one_atomic_rpc(monkeypatch):
    client = make_client(monkeypatch)
    calls = []

    def fake_request(method, resource, authorization, **kwargs):
        calls.append((method, resource, kwargs["json_body"]))
        return {"id": CASE_ID, "status": "sent"}

    monkeypatch.setattr(main, "_supabase_user_request", fake_request)
    response = client.patch(
        f"/api/cases/{CASE_ID}/status",
        headers={"Authorization": "Bearer synthetic"},
        json={"status": "sent"},
    )
    assert response.status_code == 200
    assert calls == [(
        "POST", "rpc/transition_credit_case", {"p_case_id": CASE_ID, "p_status": "sent"}
    )]


def test_invalid_artifact_hash_fails_before_persistence(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.setattr(
        main,
        "_supabase_user_request",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("persistence should not run")),
    )
    response = client.post(
        f"/api/cases/{CASE_ID}/approve",
        headers={"Authorization": "Bearer synthetic"},
        json={"scan_id": SCAN_ID, "artifact_sha256": "bad", "approval_scope": "generate_drafts"},
    )
    assert response.status_code == 400


def test_migration_denies_direct_writes_and_binds_atomic_transition_to_current_scan():
    migration = (
        Path(__file__).parents[2]
        / "supabase"
        / "migrations"
        / "20260815070000_technical_rc_security_and_workflow.sql"
    ).read_text(encoding="utf-8")
    assert 'FOR ALL TO authenticated' not in migration
    assert 'REVOKE INSERT, UPDATE, DELETE ON public.credit_cases FROM authenticated' in migration
    assert 'REVOKE INSERT, UPDATE, DELETE ON public.customer_approvals FROM authenticated' in migration
    assert 'JOIN public.credit_scans s ON s.id = current_case.current_scan_id' in migration
    assert 'a.scan_id = current_case.current_scan_id' in migration
    assert 'a.artifact_sha256 = s.artifact_sha256' in migration
    assert "'case_status_changed'" in migration
    assert 'revoke_credit_approval' in migration
    assert "'customer_approval_revoked'" in migration
    assert 'SECURITY DEFINER' in migration
