import json
import shutil
from pathlib import Path
import hashlib

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    storage = Path.cwd() / "ti" / hashlib.sha256(str(tmp_path).encode()).hexdigest()[:6]
    shutil.rmtree(storage, ignore_errors=True)
    monkeypatch.setattr(main, "STORAGE_ROOT", storage)
    monkeypatch.setattr(main, "UPLOADS", storage / "uploads")
    monkeypatch.setattr(main, "OUTPUT", storage / "output")
    monkeypatch.setattr(main, "HEALTH_AUDIT_LOG", storage / "audit" / "health.jsonl")
    main.UPLOADS.mkdir(parents=True)
    main.OUTPUT.mkdir(parents=True)
    monkeypatch.setattr(main, "WRITE_RAW_TEXT", False)
    monkeypatch.setattr(main, "RETAIN_UPLOADS", False)
    monkeypatch.setattr(main, "RETAIN_OUTPUTS", True)
    monkeypatch.setattr(main, "MAX_SCANS_PER_USER_MINUTE", 1000)
    main.SCAN_RATE_BUCKETS.clear()
    monkeypatch.setattr(main, "require_scanner_health_or_block", lambda: {"ok": True, "mode": "synthetic_test"})

    principals = {
        "Bearer alice": main.AuthenticatedPrincipal("alice", "tenant-a"),
        "Bearer bob": main.AuthenticatedPrincipal("bob", "tenant-b"),
        "Bearer teammate": main.AuthenticatedPrincipal("teammate", "tenant-a"),
    }

    def authenticate(header):
        if header not in principals:
            raise HTTPException(status_code=401, detail="Authentication is required.")
        return principals[header]

    monkeypatch.setattr(main, "authenticate_scanner_request", authenticate)
    monkeypatch.setattr(
        main,
        "persist_scan_record",
        lambda _auth, _principal, _job, artifact: {
            "case_id": "synthetic-case",
            "scan_id": "synthetic-scan",
            "artifact_sha256": artifact,
        },
    )
    monkeypatch.setattr(main, "persist_scan_artifacts", lambda *_args: None)
    monkeypatch.setattr(main, "read_secure_scan_artifact", lambda *_args: None)
    yield TestClient(main.app)
    shutil.rmtree(storage, ignore_errors=True)


def test_job_results_are_bound_to_exact_authenticated_owner(client):
    report = b"""Experian Credit Report
SYNTHETIC BANK
Account Number: 1234567890
Account Type: Collection
Balance: $50
Status: Collection
"""
    created = client.post(
        "/api/scanner/parse",
        headers={"Authorization": "Bearer alice"},
        files={"files": ("synthetic-report.txt", report, "text/plain")},
    )
    assert created.status_code == 200, created.text
    job_id = created.json()["job_id"]

    assert client.get(f"/api/scanner/result/{job_id}").status_code == 401
    assert client.get(f"/api/scanner/result/{job_id}", headers={"Authorization": "Bearer bob"}).status_code == 404
    assert client.get(f"/api/scanner/result/{job_id}", headers={"Authorization": "Bearer teammate"}).status_code == 404
    owner_result = client.get(f"/api/scanner/result/{job_id}", headers={"Authorization": "Bearer alice"})
    assert owner_result.status_code == 200
    assert "1234567890" not in owner_result.text


def test_scanner_job_path_never_contains_raw_identity(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "OUTPUT", tmp_path / "output")
    principal = main.AuthenticatedPrincipal("alice@example.test", "tenant-secret-name")
    path = main.scanner_job_dir("scan_123456789abc", principal)
    assert "alice" not in str(path)
    assert "tenant-secret-name" not in str(path)
    assert path.is_relative_to(main.OUTPUT)


def test_synthetic_test_token_requires_valid_hmac(monkeypatch):
    import hashlib
    import hmac

    monkeypatch.setenv("SCANNER_ENVIRONMENT", "test")
    monkeypatch.setenv("SCANNER_ALLOW_TEST_TOKENS", "true")
    monkeypatch.setenv("SCANNER_TEST_AUTH_SECRET", "synthetic-secret")
    signature = hmac.new(b"synthetic-secret", b"alice.tenant-a", hashlib.sha256).hexdigest()
    principal = main.authenticate_scanner_request(f"Bearer test.alice.tenant-a.{signature}")
    assert principal.user_id == "alice"
    assert principal.tenant_id == "tenant-a"

    with pytest.raises(HTTPException) as exc:
        main.authenticate_scanner_request("Bearer test.alice.tenant-a.invalid")
    assert exc.value.status_code == 401


def test_partial_remote_artifact_upload_is_rolled_back(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    job_dir = tmp_path / "uploads"
    out_dir.mkdir()
    job_dir.mkdir()
    (out_dir / "scan_result_summary.json").write_text("{}", encoding="utf-8")
    (out_dir / "credit_vivo_parser_result.json").write_text("{}", encoding="utf-8")
    (job_dir / "source_1.txt").write_text("synthetic source", encoding="utf-8")
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic-service-key")

    class FakeResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    calls = {"post": 0, "deleted": None}

    def fake_post(*_args, **_kwargs):
        calls["post"] += 1
        return FakeResponse(200 if calls["post"] == 1 else 500)

    def fake_delete(*_args, **kwargs):
        calls["deleted"] = kwargs.get("json", {}).get("prefixes")
        return FakeResponse(200)

    monkeypatch.setattr(main.requests, "post", fake_post)
    monkeypatch.setattr(main.requests, "delete", fake_delete)
    with pytest.raises(HTTPException):
        main.persist_scan_artifacts(
            "Bearer synthetic",
            main.AuthenticatedPrincipal("owner", "tenant"),
            {"case_id": "case", "scan_id": "scan"},
            out_dir,
            job_dir,
        )
    assert len(calls["deleted"]) == 1
    assert calls["deleted"][0].endswith("scan_result_summary.json")


def test_original_source_bytes_are_retained_privately_with_sha256(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    job_dir = tmp_path / "uploads"
    out_dir.mkdir()
    job_dir.mkdir()
    (out_dir / "scan_result_summary.json").write_text("{}", encoding="utf-8")
    (out_dir / "credit_vivo_parser_result.json").write_text("{}", encoding="utf-8")
    source_bytes = b"synthetic original report bytes"
    (job_dir / "source_1.txt").write_bytes(source_bytes)
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic-service-key")

    class FakeResponse:
        status_code = 200

    captured = {}
    monkeypatch.setattr(main.requests, "post", lambda *_args, **_kwargs: FakeResponse())
    monkeypatch.setattr(
        main,
        "_supabase_service_request",
        lambda _method, _resource, **kwargs: captured.update({"rows": kwargs["json_body"]}) or [],
    )
    main.persist_scan_artifacts(
        "Bearer synthetic",
        main.AuthenticatedPrincipal("owner", "tenant"),
        {"case_id": "case", "scan_id": "scan"},
        out_dir,
        job_dir,
    )
    source_row = next(row for row in captured["rows"] if row["artifact_kind"] == "source_1")
    assert source_row["sha256"] == hashlib.sha256(source_bytes).hexdigest()
    assert source_row["object_path"].startswith("owner/case/scan/source_1")
