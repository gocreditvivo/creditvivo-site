import pytest
from fastapi import HTTPException

from main import HEALTH_AUDIT_LOG, health, require_scanner_access_or_block, require_scanner_health_or_block, run_pre_scan_health_check, run_scanner_preflight_health_check


def test_scanner_saves_raw_text_by_default():
    status = health()

    assert status["write_raw_text"] is True
    assert status["pdf_text_engine"] == "pypdf"


def test_scanner_preflight_health_check_passes_locally():
    status = run_scanner_preflight_health_check()

    assert status["ok"] is True
    assert status["scan_allowed"] is True
    assert status["safe_mode_enabled"] is False
    assert status["production_approved"] is True
    names = {check["check_name"] for check in status["checks"]}
    assert "App Integrity Check" in names
    assert "Rule Pack Integrity" in names
    assert "Security Config Check" in names
    assert "User / License / Access Check" in names
    assert "Vault / Storage Check" in names
    assert "Privacy / Redaction Check" in names
    assert "Parser Readiness Check" in names
    assert "Regression Smoke Test" in names
    assert "External Call Lock Check" in names
    assert "Output Validation Check" in names
    assert "Safe Mode Check" in names
    assert "No health check pass" in status["final_rule"]
    assert status["parser_version"]
    assert status["rule_pack_version"]
    assert status["security_config_version"]


def test_scanner_preflight_blocks_when_external_calls_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_AI_SECOND_PASS", "true")

    with pytest.raises(HTTPException) as exc:
        require_scanner_health_or_block()

    assert exc.value.status_code == 503
    assert exc.value.detail["blocked"] is True
    assert exc.value.detail["safe_mode"] is True
    failed = [
        check for check in exc.value.detail["health"]["checks"]
        if check["name"] == "external calls disabled"
        or check["check_name"] == "External Call Lock Check"
    ]
    assert failed and failed[0]["passed"] is False

    monkeypatch.delenv("ENABLE_AI_SECOND_PASS", raising=False)


def test_production_scanner_access_blocks_without_config(monkeypatch):
    monkeypatch.setenv("SCANNER_ENVIRONMENT", "production")

    with pytest.raises(HTTPException) as exc:
        require_scanner_access_or_block("", "")

    assert exc.value.status_code == 503
    assert exc.value.detail["blocked"] is True
    assert exc.value.detail["safe_mode"] is True


def test_health_check_fails_if_auto_send_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTO_SEND", "true")

    status = run_scanner_preflight_health_check()

    assert status["scan_allowed"] is False
    assert status["safe_mode_enabled"] is True
    failed = [check for check in status["checks"] if check["check_name"] == "Security Config Check"]
    assert failed and failed[0]["status"] == "fail"
    monkeypatch.delenv("ENABLE_AUTO_SEND", raising=False)


def test_health_check_logged_without_raw_credit_data():
    before = HEALTH_AUDIT_LOG.read_text(encoding="utf-8") if HEALTH_AUDIT_LOG.exists() else ""

    health = run_pre_scan_health_check(user_context={
        "user_id": "owner-123-45-6789",
        "device_id": "device-01/02/1980",
        "role": "owner",
    })

    assert health.scan_allowed is True
    after = HEALTH_AUDIT_LOG.read_text(encoding="utf-8")
    new_log = after[len(before):]
    assert "123-45-6789" not in new_log
    assert "01/02/1980" not in new_log
    assert "CREDIT ONE BANK" not in new_log
    assert "Balance: $59" not in new_log
