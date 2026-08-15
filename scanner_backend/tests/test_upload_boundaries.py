from io import BytesIO
import shutil
from pathlib import Path
import hashlib

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

import main


def synthetic_text_pdf(lines):
    buffer = BytesIO()
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    font_ref = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})
    })
    stream = DecodedStreamObject()
    commands = ["BT /F1 10 Tf 72 720 Td"]
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({safe}) Tj 0 -14 Td")
    commands.append("ET")
    stream.set_data("\n".join(commands).encode("latin-1"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    writer.write(buffer)
    return buffer.getvalue()


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
    monkeypatch.setattr(main, "MAX_SCANS_PER_USER_MINUTE", 1000)
    main.SCAN_RATE_BUCKETS.clear()
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


def test_synthetic_pdf_extraction_runs_end_to_end_without_filename_leak(client):
    content = synthetic_text_pdf([
        "Experian Credit Report",
        "SYNTHETIC PDF BANK",
        "Account Number: 901234567890",
        "Account Type: Collection",
        "Balance: $75",
        "Status: Collection",
    ])
    response = client.post(
        "/api/scanner/parse",
        files={"files": ("SYNTHETIC-PERSON-9012-3456-7890-private.pdf", content, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    assert "SYNTHETIC-PERSON-9012-3456-7890-private" not in response.text
    assert response.json()["files"][0]["filename"] == "report_1.pdf"
    assert response.json()["review_items_preview"][0]["account_number_masked"] == "*7890"


def test_pdf_page_and_extracted_text_limits_fail_closed(client, monkeypatch):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)
    monkeypatch.setattr(main, "MAX_PDF_PAGES", 1)
    response = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic.pdf", pdf_buffer.getvalue(), "application/pdf")},
    )
    assert response.status_code == 422
    assert remaining_jobs() == []

    monkeypatch.setattr(main, "MAX_EXTRACTED_CHARS", 10)
    response = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic.txt", b"Experian synthetic report text", "text/plain")},
    )
    assert response.status_code == 422
    assert remaining_jobs() == []


def test_authenticated_user_rate_limit_fails_closed(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_SCANS_PER_USER_MINUTE", 1)
    main.SCAN_RATE_BUCKETS.clear()
    report = b"""Experian Credit Report
SYNTHETIC BANK
Account Number: 1234567890
Account Type: Collection
Balance: $50
Status: Collection
"""
    first = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic.txt", report, "text/plain")},
    )
    second = client.post(
        "/api/scanner/parse",
        files={"files": ("synthetic.txt", report, "text/plain")},
    )
    assert first.status_code == 200
    assert second.status_code == 429
