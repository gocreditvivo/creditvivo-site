from fastapi.testclient import TestClient

import main


CASE_ID = "00000000-0000-4000-8000-000000000001"
SCAN_ID = "00000000-0000-4000-8000-000000000002"
ARTIFACT_HASH = "a" * 64


def make_client(monkeypatch, role="authenticated"):
    monkeypatch.setattr(
        main,
        "authenticate_scanner_request",
        lambda _auth: main.AuthenticatedPrincipal("00000000-0000-4000-8000-000000000003", "tenant-a", role),
    )
    return TestClient(main.app)


def test_approval_is_rejected_when_artifact_hash_does_not_match(monkeypatch):
    client = make_client(monkeypatch)

    def fake_request(method, resource, authorization, **kwargs):
        if resource == "credit_scans":
            return [{"id": SCAN_ID, "artifact_sha256": ARTIFACT_HASH}]
        raise AssertionError("no write should occur for a mismatched artifact")

    monkeypatch.setattr(main, "_supabase_user_request", fake_request)
    response = client.post(
        f"/api/cases/{CASE_ID}/approve",
        headers={"Authorization": "Bearer synthetic"},
        json={"scan_id": SCAN_ID, "artifact_sha256": "b" * 64, "approval_scope": "generate_drafts"},
    )
    assert response.status_code == 409


def test_approval_records_immutable_artifact_and_audit_event(monkeypatch):
    client = make_client(monkeypatch)
    writes = []

    def fake_request(method, resource, authorization, **kwargs):
        if method == "GET":
            return [{"id": SCAN_ID, "artifact_sha256": ARTIFACT_HASH}]
        writes.append((resource, kwargs["json_body"]))
        return [{"id": "approval-id"}]

    monkeypatch.setattr(main, "_supabase_user_request", fake_request)
    response = client.post(
        f"/api/cases/{CASE_ID}/approve",
        headers={"Authorization": "Bearer synthetic"},
        json={"scan_id": SCAN_ID, "artifact_sha256": ARTIFACT_HASH, "approval_scope": "generate_drafts"},
    )
    assert response.status_code == 200
    assert writes[0][0] == "customer_approvals"
    assert writes[0][1]["artifact_sha256"] == ARTIFACT_HASH
    assert writes[1][0] == "case_audit_events"


def test_sent_transition_requires_send_approval_and_admin(monkeypatch):
    client = make_client(monkeypatch, role="authenticated")

    def fake_request(method, resource, authorization, **kwargs):
        if resource == "credit_cases":
            return [{"id": CASE_ID, "status": "approved"}]
        if resource == "customer_approvals":
            return [{"id": "approval-id"}]
        return []

    monkeypatch.setattr(main, "_supabase_user_request", fake_request)
    response = client.patch(
        f"/api/cases/{CASE_ID}/status",
        headers={"Authorization": "Bearer synthetic"},
        json={"status": "sent"},
    )
    assert response.status_code == 403


def test_invalid_transition_fails_closed(monkeypatch):
    client = make_client(monkeypatch, role="admin")
    monkeypatch.setattr(
        main,
        "_supabase_user_request",
        lambda method, resource, authorization, **kwargs: [{"id": CASE_ID, "status": "review"}],
    )
    response = client.patch(
        f"/api/cases/{CASE_ID}/status",
        headers={"Authorization": "Bearer synthetic"},
        json={"status": "sent"},
    )
    assert response.status_code == 409
