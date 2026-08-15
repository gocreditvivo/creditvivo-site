from io import BytesIO
import shutil
from pathlib import Path
import hashlib

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Keep the generated workbook path below the legacy Windows MAX_PATH limit.
    storage = Path.cwd() / "t" / hashlib.sha256(str(tmp_path).encode()).hexdigest()[:6]
    shutil.rmtree(storage, ignore_errors=True)
    monkeypatch.setattr(main, "STORAGE_ROOT", storage)
    monkeypatch.setattr(main, "UPLOADS", storage / "uploads")
    monkeypatch.setattr(main, "OUTPUT", storage / "output")
    monkeypatch.setattr(main, "HEALTH_AUDIT_LOG", storage / "audit" / "health.jsonl")
    main.UPLOADS.mkdir(parents=True)
    main.OUTPUT.mkdir(parents=True)
    monkeypatch.setattr(main, "WRITE_RAW_TEXT", False)
    monkeypatch.setattr(main, "RETAIN_UPLOADS", False)
    monkeypatch.setattr(main, "require_scanner_health_or_block", lambda: {"ok": True, "mode": "synthetic_test"})
    monkeypatch.setattr(
        main,
        "authenticate_scanner_request",
        lambda *_args: main.AuthenticatedPrincipal(user_id="synthetic-user", tenant_id="synthetic-tenant"),
    )
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
    yield TestClient(main.app)
    shutil.rmtree(storage, ignore_errors=True)


def remaining_jobs():
    uploads = list(main.UPLOADS.rglob("scan_*")) if main.UPLOADS.exists() else []
    outputs = list(main.OUTPUT.rglob("scan_*")) if main.OUTPUT.exists() else []
    return uploads + outputs


def test_synthetic_txt_upload_runs_without_raw_text_persistence(client):
    report = b"""Experian Credit Report
SYNTHETIC BANK
Account Number: 1234567890
Account Type: Collection
Balance: $50
Status: Collection
"""
    response = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic-report.txt", report, "text/plain")},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["review_items_count"] >= 1
    assert payload["raw_text_files"] == []
    assert "1234567890" not in response.text
    assert not list(main.UPLOADS.rglob("scan_*"))


@pytest.mark.parametrize(
    ("filename", "content", "content_type", "expected_status"),
    [
        ("fake.pdf", b"not a pdf", "application/pdf", 400),
        ("blank.txt", b"   \n", "text/plain", 422),
        ("binary.txt", b"abc\x00def", "text/plain", 400),
        ("report.exe", b"synthetic", "application/octet-stream", 400),
    ],
)
def test_invalid_uploads_fail_closed_and_cleanup(client, filename, content, content_type, expected_status):
    response = client.post(
        "/api/scanner/parse",
        files={"files": (filename, content, content_type)},
    )

    assert response.status_code == expected_status, response.text
    assert remaining_jobs() == []


def test_oversized_upload_is_removed(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_FILE_BYTES", 8)
    response = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic-report.txt", b"123456789", "text/plain")},
    )

    assert response.status_code == 413, response.text
    assert remaining_jobs() == []


def test_encrypted_and_blank_pdfs_are_rejected_and_removed(client):
    encrypted_buffer = BytesIO()
    encrypted = PdfWriter()
    encrypted.add_blank_page(width=72, height=72)
    encrypted.encrypt("synthetic-password")
    encrypted.write(encrypted_buffer)

    blank_buffer = BytesIO()
    blank = PdfWriter()
    blank.add_blank_page(width=72, height=72)
    blank.write(blank_buffer)

    for name, content in (
        ("encrypted.pdf", encrypted_buffer.getvalue()),
        ("blank.pdf", blank_buffer.getvalue()),
    ):
        response = client.post(
            "/api/scanner/parse",
            files={"files": (name, content, "application/pdf")},
        )
        assert response.status_code == 422, response.text
        assert remaining_jobs() == []
