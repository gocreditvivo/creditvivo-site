import pytest
from fastapi import HTTPException

from main import health, require_scanner_access_or_block, require_scanner_health_or_block, run_scanner_preflight_health_check


def test_scanner_saves_raw_text_by_default():
    status = health()

    assert status["write_raw_text"] is True
    assert status["pdf_text_engine"] == "pypdf"


def test_scanner_preflight_health_check_passes_locally():
    status = run_scanner_preflight_health_check()

    assert status["ok"] is True
    assert status["safe_mode_ready"] is True
    names = {check["name"] for check in status["checks"]}
    assert "parser integrity" in names
    assert "rule pack integrity" in names
    assert "security config" in names
    assert "user/license/device access" in names
    assert "encrypted vault/storage" in names
    assert "redaction hooks" in names
    assert "parser modules" in names
    assert "regression smoke test" in names
    assert "external calls disabled" in names
    assert "output validation" in names
    assert "Safe Mode readiness" in names
    assert "No health check pass" in status["final_rule"]


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
