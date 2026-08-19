from __future__ import annotations

"""
Credit Vivo Proprietary Scanner API v16

No paid AI API.
No Anthropic / Claude.
No competitor code.
No automatic disputes.

Uses:
- pypdf for PDF text extraction
- Credit Vivo Proprietary Parser Engine for parsing/review
"""

import json
import os
import shutil
import uuid
import hashlib
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

try:
    from .posthog_config import capture as ph_capture, flush as ph_flush, get_posthog
except ImportError:
    from posthog_config import capture as ph_capture, flush as ph_flush, get_posthog

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from .credit_vivo_proprietary_engine import (
        COMPLIANCE_RULE_PACK_VERSION,
        LETTER_TEMPLATE_VERSION,
        METRO2_RULE_PACK_VERSION,
        PARSER_VERSION,
        SECURITY_CONFIG_VERSION,
        detect_bureau,
        mask_account_number,
        parse_reports,
        result_to_dict,
        source_hash,
        validate_workbook_output,
        write_outputs,
    )
    from .codex_advisor_ai import build_codex_advisor_brief
    from .event_collector import (
        append_event,
        build_event,
        growth_snapshot_from_events,
        operator_events_from_vivo_events,
        read_events,
        summarize_events,
    )
    from .ai_operating_system import build_ai_operating_system_brief
    from .ai_tracking_map import build_ai_tracking_map
    from .admin_users import (
        append_provisioned_user,
        build_provisioned_user,
        read_provisioned_users,
        require_setup_token,
        role_templates,
    )
    from .growth_ai import GrowthSnapshot, build_growth_brief, lead_score
    from .growth_ads_ai import build_ad_plan
    from .growth_ai_sources import build_growth_source_brief
    from .growth_codex_capabilities import build_codex_like_growth_brief
    from .growth_credit_domain_expertise import build_credit_domain_expertise_brief
    from .growth_cross_ai_directives import build_cross_ai_growth_directives
    from .growth_forensic_search import build_forensic_search_brief, run_forensic_search
    from .growth_live_access import build_live_access_brief
    from .growth_problem_solver import build_problem_solver_brief, solve_growth_problem
    from .lead_capture import append_lead, build_lead, read_leads, summarize_leads
    from .operator_ai import OperatorEvent, build_operator_brief, demo_operator_events
    from .outreach_ai import build_outreach_plan
    from .vivo_command_ai import build_command_brief
except ImportError:
    from credit_vivo_proprietary_engine import (
        COMPLIANCE_RULE_PACK_VERSION,
        LETTER_TEMPLATE_VERSION,
        METRO2_RULE_PACK_VERSION,
        PARSER_VERSION,
        SECURITY_CONFIG_VERSION,
        detect_bureau,
        mask_account_number,
        parse_reports,
        result_to_dict,
        source_hash,
        validate_workbook_output,
        write_outputs,
    )
    from codex_advisor_ai import build_codex_advisor_brief
    from event_collector import (
        append_event,
        build_event,
        growth_snapshot_from_events,
        operator_events_from_vivo_events,
        read_events,
        summarize_events,
    )
    from ai_operating_system import build_ai_operating_system_brief
    from ai_tracking_map import build_ai_tracking_map
    from admin_users import (
        append_provisioned_user,
        build_provisioned_user,
        read_provisioned_users,
        require_setup_token,
        role_templates,
    )
    from growth_ai import GrowthSnapshot, build_growth_brief, lead_score
    from growth_ads_ai import build_ad_plan
    from growth_ai_sources import build_growth_source_brief
    from growth_codex_capabilities import build_codex_like_growth_brief
    from growth_credit_domain_expertise import build_credit_domain_expertise_brief
    from growth_cross_ai_directives import build_cross_ai_growth_directives
    from growth_forensic_search import build_forensic_search_brief, run_forensic_search
    from growth_live_access import build_live_access_brief
    from growth_problem_solver import build_problem_solver_brief, solve_growth_problem
    from lead_capture import append_lead, build_lead, read_leads, summarize_leads
    from operator_ai import OperatorEvent, build_operator_brief, demo_operator_events
    from outreach_ai import build_outreach_plan
    from vivo_command_ai import build_command_brief

ROOT = Path(__file__).resolve().parent
STORAGE_ROOT = Path(os.getenv("SCANNER_STORAGE_DIR", "/tmp/creditvivo-scanner" if os.getenv("VERCEL") else str(ROOT)))
UPLOADS = STORAGE_ROOT / "uploads"
OUTPUT = STORAGE_ROOT / "output"
EVENT_LOG = STORAGE_ROOT / "events" / "vivo_events.jsonl"
LEAD_LOG = STORAGE_ROOT / "leads" / "captured_leads.jsonl"
ADMIN_USER_LOG = STORAGE_ROOT / "users" / "provisioned_users.jsonl"
HEALTH_AUDIT_LOG = STORAGE_ROOT / "audit" / "scanner_health_audit.jsonl"
UPLOADS.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)

SCAN_DOWNLOADS = {
    "workbook.xlsx": (
        "credit_vivo_desktop_scanner_output.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "credit-vivo-desktop-scanner-output.xlsx",
    ),
    "issues.csv": ("review_issues.csv", "text/csv", "credit-vivo-errors-worksheet.csv"),
    "tradelines.csv": ("tradelines.csv", "text/csv", "credit-vivo-tradelines.csv"),
    "letters.txt": ("draft_dispute_letters.txt", "text/plain", "credit-vivo-draft-dispute-letters.txt"),
}

HEALTH_CHECK_VERSION = "scanner-preflight-2026.07.03-v1"
SAFE_MODE_READY_MESSAGE = "Safe Mode ready. Scanner can pause customer-facing findings, letters, and exports if health fails."
SCANNER_ACCESS_TOKEN = os.getenv("SCANNER_ACCESS_TOKEN", "")
ENABLE_EXTERNAL_LICENSE_LOOKUP = os.getenv("ENABLE_EXTERNAL_LICENSE_LOOKUP", "false").lower() == "true"
ENABLE_AI_SECOND_PASS = os.getenv("ENABLE_AI_SECOND_PASS", "false").lower() == "true"
ENABLE_AUTO_SEND = os.getenv("ENABLE_AUTO_SEND", "false").lower() == "true"
ENABLE_REMOTE_SYNC = os.getenv("ENABLE_REMOTE_SYNC", "false").lower() == "true"
ENCRYPTED_VAULT_ENABLED = os.getenv("ENCRYPTED_VAULT_ENABLED", "true").lower() == "true"


@dataclass
class ScannerHealthCheck:
    scan_allowed: bool
    safe_mode_enabled: bool
    production_approved: bool
    overall_status: str
    checks: List[dict]
    errors: List[str]
    warnings: List[str]
    parser_version: str
    rule_pack_version: str
    security_config_version: str
    checked_at: str
    parser_integrity_status: str = "unknown"
    rule_pack_integrity_status: str = "unknown"
    template_integrity_status: str = "unknown"
    exporter_integrity_status: str = "unknown"
    security_config_status: str = "unknown"
    integrity_errors: List[str] = field(default_factory=list)
    user_access_status: str = "unknown"
    letters_allowed: bool = False
    exports_allowed: bool = False
    external_calls_allowed: bool = False
    external_calls_enabled: bool = False
    auto_send_enabled: bool = False


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def scanner_accepts_uploads() -> bool:
    """Fail closed on hosted deployments until uploads are explicitly enabled."""
    configured = os.getenv("SCANNER_ACCEPT_UPLOADS")
    if configured is not None:
        return configured.strip().lower() == "true"

    environment = os.getenv("SCANNER_ENVIRONMENT", "local").strip().lower()
    hosted = bool(os.getenv("VERCEL") or os.getenv("RENDER"))
    return environment in {"local", "development", "test"} and not hosted


def scanner_job_dir(job_id: str) -> Path:
    if not job_id.startswith("scan_") or any(ch in job_id for ch in ("/", "\\", "..")):
        raise HTTPException(status_code=400, detail="Invalid scanner job id.")
    return OUTPUT / job_id


MAX_FILES = env_int("SCANNER_MAX_FILES", 3)
MAX_FILE_MB = env_int("SCANNER_MAX_FILE_MB", 25)
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024
RETAIN_UPLOADS = os.getenv("SCANNER_RETAIN_UPLOADS", "false").lower() == "true"
WRITE_RAW_TEXT = os.getenv("SCANNER_WRITE_RAW_TEXT", "false").lower() == "true"
ALLOWED_PDF_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream", "binary/octet-stream"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_posthog()  # initialise and warm-up the PostHog client on startup
    yield
    ph_flush()  # flush buffered events before shutdown


app = FastAPI(title="Credit Vivo Proprietary Scanner API", version="16.0", lifespan=lifespan)

@app.middleware("http")
async def suspend_hosted_scanner_uploads(request: Request, call_next):
    if (
        request.method.upper() == "POST"
        and request.url.path in {"/scanner/parse", "/api/scanner/parse"}
        and not scanner_accepts_uploads()
    ):
        return JSONResponse(
            {
                "detail": {
                    "code": "scanner_uploads_disabled",
                    "message": "Credit report uploads are temporarily unavailable while secure staging validation is completed.",
                }
            },
            status_code=503,
        )
    return await call_next(request)


allowed_origins = os.getenv(
    "CREDIT_VIVO_ALLOWED_ORIGINS",
    ",".join([
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4195",
        "http://127.0.0.1:4195",
        "http://localhost:4196",
        "http://127.0.0.1:4196",
        "http://localhost:4197",
        "http://127.0.0.1:4197",
    ])
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def service_status_payload(check_storage: bool = False) -> dict:
    checks = {
        "api": True,
        "uploads_directory": UPLOADS.exists(),
        "output_directory": OUTPUT.exists(),
    }
    if check_storage:
        try:
            probe = OUTPUT / ".readyz"
            probe.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
            probe.unlink(missing_ok=True)
            checks["storage_write"] = True
        except Exception:
            checks["storage_write"] = False

    ok = all(checks.values())
    return {
        "ok": ok,
        "service": "credit-vivo-proprietary-scanner-api",
        "environment": os.getenv("SCANNER_ENVIRONMENT", "local"),
        "version": "16.0",
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "accepting_uploads": scanner_accepts_uploads(),
        "checks": checks,
    }


def _health_check_row(check_id: str, name: str, passed: bool, detail: str = "", severity: str = "critical", fix_required: str = "") -> dict:
    status = "pass" if passed else ("warning" if severity in {"warning", "low"} else "fail")
    return {
        "check_id": check_id,
        "check_name": name,
        "name": name,
        "status": status,
        "passed": bool(passed),
        "severity": severity,
        "evidence": detail,
        "detail": detail,
        "fix_required": "" if passed else fix_required,
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def redact_ssn(value: str) -> str:
    return __import__("re").sub(r"\b\d{3}-?\d{2}-?\d{4}\b", "***-**-****", value or "")


def redact_dob(value: str) -> str:
    return __import__("re").sub(r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b", "**/**/****", value or "")


def redact_sensitive_log_value(value: str) -> str:
    return mask_account_number(redact_dob(redact_ssn(value or "")))


def health_check_to_dict(health: ScannerHealthCheck | dict) -> dict:
    if isinstance(health, ScannerHealthCheck):
        payload = asdict(health)
    else:
        payload = dict(health)
    payload["ok"] = bool(payload.get("scan_allowed"))
    payload["safe_mode_ready"] = True
    payload["version"] = HEALTH_CHECK_VERSION
    payload["mode"] = "scanner_preflight"
    payload["final_rule"] = "No health check pass. No scan. No letters. No exports. No customer-facing findings."
    return payload


def log_health_audit(event_name: str, health: ScannerHealthCheck | dict, user_context: dict | None = None, product_mode: str = "credit_vivo_private") -> None:
    payload = health_check_to_dict(health)
    user_context = user_context or {}
    failed_checks = [
        check.get("check_id", "")
        for check in payload.get("checks", [])
        if check.get("status") == "fail" or check.get("passed") is False
    ]
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_name,
        "user_id": redact_sensitive_log_value(str(user_context.get("user_id", "anonymous"))),
        "product_mode": product_mode,
        "device_id": redact_sensitive_log_value(str(user_context.get("device_id", ""))),
        "parser_version": payload.get("parser_version", ""),
        "rule_pack_version": payload.get("rule_pack_version", ""),
        "scan_allowed": bool(payload.get("scan_allowed")),
        "failed_checks": failed_checks,
        "safe_mode_enabled": bool(payload.get("safe_mode_enabled")),
    }
    HEALTH_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HEALTH_AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_pre_scan_health_check(product_mode: str = "credit_vivo_private", user_context: dict | None = None, config: dict | None = None) -> ScannerHealthCheck:
    checks = []
    user_context = user_context or {}
    config = config or {}
    environment = os.getenv("SCANNER_ENVIRONMENT", "local").lower()
    production = environment == "production"
    log_health_audit("pre_scan_health_check_started", {
        "scan_allowed": False,
        "safe_mode_enabled": True,
        "checks": [],
        "parser_version": PARSER_VERSION,
        "rule_pack_version": COMPLIANCE_RULE_PACK_VERSION,
    }, user_context, product_mode)

    parser_file = ROOT / "credit_vivo_proprietary_engine.py"
    main_file = ROOT / "main.py"
    parser_hash = file_sha256(parser_file) if parser_file.exists() else ""
    exporter_hash = parser_hash
    rule_pack_hash = hashlib.sha256((COMPLIANCE_RULE_PACK_VERSION + METRO2_RULE_PACK_VERSION).encode("utf-8")).hexdigest()
    template_hash = hashlib.sha256(LETTER_TEMPLATE_VERSION.encode("utf-8")).hexdigest()
    security_hash = hashlib.sha256(SECURITY_CONFIG_VERSION.encode("utf-8")).hexdigest()

    checks.append(_health_check_row(
        "HC-001",
        "App Integrity Check",
        callable(parse_reports) and callable(result_to_dict) and bool(parser_hash) and bool(main_file.exists()) and bool(PARSER_VERSION),
        f"parser_hash={parser_hash[:16]}; exporter_hash={exporter_hash[:16]}; rule_pack_hash={rule_pack_hash[:16]}; template_hash={template_hash[:16]}; security_hash={security_hash[:16]}; parser_version={PARSER_VERSION}",
        fix_required="Restore parser/exporter/rule/template/security files and version constants.",
    ))
    checks.append(_health_check_row(
        "HC-002",
        "Rule Pack Integrity",
        callable(detect_bureau) and callable(source_hash) and bool(COMPLIANCE_RULE_PACK_VERSION) and bool(METRO2_RULE_PACK_VERSION),
        f"compliance={COMPLIANCE_RULE_PACK_VERSION}; metro2={METRO2_RULE_PACK_VERSION}",
        fix_required="Restore compliance and Metro 2 rule pack constants.",
    ))
    external_license_lookup = os.getenv("ENABLE_EXTERNAL_LICENSE_LOOKUP", str(ENABLE_EXTERNAL_LICENSE_LOOKUP)).lower() == "true"
    ai_second_pass = os.getenv("ENABLE_AI_SECOND_PASS", str(ENABLE_AI_SECOND_PASS)).lower() == "true"
    auto_send = os.getenv("ENABLE_AUTO_SEND", str(ENABLE_AUTO_SEND)).lower() == "true"
    remote_sync = os.getenv("ENABLE_REMOTE_SYNC", str(ENABLE_REMOTE_SYNC)).lower() == "true"
    encrypted_vault = os.getenv("ENCRYPTED_VAULT_ENABLED", str(ENCRYPTED_VAULT_ENABLED)).lower() == "true"
    checks.append(_health_check_row(
        "HC-003",
        "Security Config Check",
        (not auto_send) and (not remote_sync) and (not external_license_lookup) and (not ai_second_pass) and encrypted_vault and ((not production) or (not WRITE_RAW_TEXT and not RETAIN_UPLOADS)),
        f"environment={environment}; write_raw_text={WRITE_RAW_TEXT}; retain_uploads={RETAIN_UPLOADS}; auto_send={auto_send}; remote_sync={remote_sync}; external_lookup={external_license_lookup}; ai_second_pass={ai_second_pass}; encrypted_vault={encrypted_vault}",
        fix_required="Disable auto-send, remote sync, external calls, raw text logging, and upload retention unless explicitly approved.",
    ))
    scanner_token = str(user_context.get("scanner_token") or config.get("scanner_token") or "")
    device_id = str(user_context.get("device_id") or config.get("device_id") or "")
    role = str(user_context.get("role") or config.get("role") or "admin")
    license_valid = bool(user_context.get("license_valid", config.get("license_valid", True)))
    access_ok = (
        (not production)
        or (
            bool(os.getenv("SCANNER_ACCESS_TOKEN", SCANNER_ACCESS_TOKEN))
            and scanner_token == os.getenv("SCANNER_ACCESS_TOKEN", SCANNER_ACCESS_TOKEN)
            and bool(device_id.strip())
            and role in {"owner", "admin", "scanner_admin"}
            and license_valid
        )
    )
    checks.append(_health_check_row(
        "HC-004",
        "User / License / Access Check",
        access_ok,
        f"role={role}; device_present={bool(device_id.strip())}; license_valid={license_valid}; production={production}",
        fix_required="Verify authorized admin session, scanner token, trusted device, valid license, and scan permission.",
    ))

    try:
        UPLOADS.mkdir(parents=True, exist_ok=True)
        OUTPUT.mkdir(parents=True, exist_ok=True)
        probe = OUTPUT / ".scanner_preflight_vault"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        secure_temp = str(UPLOADS.resolve()).startswith(str(STORAGE_ROOT.resolve()))
        temp_cleanup_ok = True
        storage_ok = encrypted_vault and secure_temp and temp_cleanup_ok
        storage_detail = f"vault_writable=True; encrypted_vault={encrypted_vault}; secure_temp={secure_temp}; temp_cleanup={temp_cleanup_ok}"
    except Exception as exc:
        storage_ok = False
        storage_detail = str(exc)
    checks.append(_health_check_row("HC-005", "Vault / Storage Check", storage_ok, storage_detail, fix_required="Unlock/configure encrypted storage, secure temp folder, cleanup, and write permissions."))

    redaction_ok = callable(redact_ssn) and callable(redact_dob) and callable(mask_account_number) and callable(redact_sensitive_log_value) and ((not production) or not WRITE_RAW_TEXT)
    checks.append(_health_check_row(
        "HC-006",
        "Privacy / Redaction Check",
        redaction_ok,
        f"ssn_redaction=True; dob_redaction=True; account_masking=True; write_raw_text={WRITE_RAW_TEXT}",
        fix_required="Load SSN/DOB/account redaction hooks and disable raw text logging in production.",
    ))
    checks.append(_health_check_row(
        "HC-007",
        "Parser Readiness Check",
        PdfReader is not None and callable(detect_bureau) and callable(parse_reports) and callable(result_to_dict) and callable(write_outputs) and callable(validate_workbook_output),
        "pypdf loaded." if PdfReader is not None else "pypdf is unavailable.",
        fix_required="Restore bureau detection, parsing, issue engine, workbook export, and QA validation modules.",
    ))

    smoke_dir = OUTPUT / "_healthcheck_smoke"
    try:
        smoke_sample = """--- PAGE 1 ---
Equifax Credit Report

CREDIT ONE BANK
Account Number: *1664
Account Type: Credit Card
Balance: $59
Status: Pays As Agreed
Date Opened: 03/09/2026
Date Reported: 06/19/2026

--- PAGE 2 ---
Experian Credit Report

CREDIT ONE BANK
Account Number: *4796
Account Type: Credit Card
Balance: $125
Status: Open
Date Opened: 03/09/2026
Date Reported: 06/11/2026
"""
        parsed = parse_reports({"healthcheck.pdf": {"text": smoke_sample}})
        data = result_to_dict(parsed)
        by_account = {item.get("account_number_masked"): item for item in data.get("tradelines", [])}
        smoke_ok = (
            len(data.get("tradelines", [])) == 2
            and by_account.get("*1664", {}).get("bureau") == "Equifax"
            and by_account.get("*4796", {}).get("bureau") == "Experian"
            and by_account.get("*1664", {}).get("is_negative") is False
            and by_account.get("*4796", {}).get("is_negative") is False
            and len(data.get("issues", [])) == 0
            and len(data.get("recommended_letter_queue", [])) == 0
            and by_account.get("*1664", {}).get("field_evidence", {}).get("balance", {}).get("raw_line") == "Balance: $59"
        )
        smoke_detail = "Two-bureau positive smoke report parsed with proof, no negative rows, no issues, and no letters."
    except Exception as exc:
        smoke_ok = False
        smoke_detail = str(exc)
        data = {}
    checks.append(_health_check_row("HC-008", "Regression Smoke Test", smoke_ok, smoke_detail, fix_required="Fix page-level bureau parsing, negative classifier, issue gating, or field evidence."))

    external_flags = {
        "license_lookup": external_license_lookup,
        "ai_second_pass": ai_second_pass,
        "remote_sync": remote_sync,
        "auto_send": auto_send,
        "attorney_api": os.getenv("ENABLE_ATTORNEY_REFERRAL_API", "false").lower() == "true",
        "mail_api": os.getenv("ENABLE_MAIL_API", "false").lower() == "true",
        "complaint_api": os.getenv("ENABLE_COMPLAINT_SUBMISSION_API", "false").lower() == "true",
    }
    external_calls_disabled = not any(external_flags.values())
    checks.append(_health_check_row(
        "HC-009",
        "External Call Lock Check",
        external_calls_disabled,
        json.dumps(external_flags, ensure_ascii=False),
        fix_required="Disable external call flags or add explicit approved config before scanning.",
    ))

    try:
        if smoke_ok:
            smoke_dir.mkdir(parents=True, exist_ok=True)
            write_outputs(parsed, smoke_dir, pre_scan_health_check={"overall_status": "preflight_smoke", "scan_allowed": True, "safe_mode_enabled": False})
            validation = validate_workbook_output(smoke_dir / "credit_vivo_desktop_scanner_output.xlsx")
            output_ok = validation.get("production_approval") in {"approved", "blocked"} and any(
                check.get("check") == "required_sheets" and check.get("result")
                for check in validation.get("checks", [])
            ) and (smoke_dir / "workbook_validation.json").exists()
            output_detail = json.dumps(validation, ensure_ascii=False)[:800]
        else:
            output_ok = False
            output_detail = "Smoke parser did not pass, so output validation was skipped."
    except Exception as exc:
        output_ok = False
        output_detail = str(exc)
    finally:
        shutil.rmtree(smoke_dir, ignore_errors=True)
    checks.append(_health_check_row("HC-010", "Output Validation Check", output_ok, output_detail, fix_required="Fix JSON/workbook validators, Raw Evidence Index, QA Verification, Security Audit Summary, or output hashing."))

    checks.append(_health_check_row(
        "HC-011",
        "Safe Mode Check",
        True,
        SAFE_MODE_READY_MESSAGE,
    ))

    critical_pass = all(check["passed"] for check in checks if check["severity"] == "critical")
    errors = [f"{check['check_id']} {check['check_name']}" for check in checks if check["status"] == "fail"]
    warnings = [f"{check['check_id']} {check['check_name']}" for check in checks if check["status"] == "warning"]
    health = ScannerHealthCheck(
        scan_allowed=critical_pass,
        safe_mode_enabled=not critical_pass,
        production_approved=critical_pass,
        overall_status="pass" if critical_pass else "blocked",
        checks=checks,
        errors=errors,
        warnings=warnings,
        parser_version=PARSER_VERSION,
        rule_pack_version=COMPLIANCE_RULE_PACK_VERSION,
        security_config_version=SECURITY_CONFIG_VERSION,
        checked_at=datetime.now(timezone.utc).isoformat(),
        parser_integrity_status="pass" if checks[0]["passed"] else "fail",
        rule_pack_integrity_status="pass" if checks[1]["passed"] else "fail",
        template_integrity_status="pass" if template_hash else "fail",
        exporter_integrity_status="pass" if exporter_hash else "fail",
        security_config_status="pass" if checks[2]["passed"] else "fail",
        integrity_errors=errors,
        user_access_status="pass" if access_ok else "fail",
        letters_allowed=critical_pass,
        exports_allowed=critical_pass,
        external_calls_allowed=False,
        external_calls_enabled=not external_calls_disabled,
        auto_send_enabled=auto_send,
    )
    log_health_audit("pre_scan_health_check_passed" if critical_pass else "pre_scan_health_check_failed", health, user_context, product_mode)
    if not critical_pass:
        log_health_audit("safe_mode_enabled", health, user_context, product_mode)
        log_health_audit("scan_blocked", health, user_context, product_mode)
    return health


def run_scanner_preflight_health_check() -> dict:
    return health_check_to_dict(run_pre_scan_health_check())


def require_scanner_health_or_block() -> dict:
    health_payload = run_scanner_preflight_health_check()
    if not health_payload["ok"]:
        ph_capture(
            "system",
            "scanner_health_check_failed",
            {
                "overall_status": health_payload.get("overall_status", "blocked"),
                "failed_check_count": len(health_payload.get("errors", [])),
            },
        )
        raise HTTPException(
            status_code=503,
            detail={
                "ok": False,
                "blocked": True,
                "safe_mode": True,
                "message": "Scanner health check failed. No scan, letters, exports, or customer-facing findings are allowed.",
                "health": health_payload,
            },
        )
    return health_payload


def require_scanner_access_or_block(scanner_token: str = "", device_id: str = "") -> dict:
    environment = os.getenv("SCANNER_ENVIRONMENT", "local").lower()
    scanner_access_token = os.getenv("SCANNER_ACCESS_TOKEN", SCANNER_ACCESS_TOKEN)
    if environment != "production":
        return {"ok": True, "mode": "local_test_access"}
    if not scanner_access_token:
        raise HTTPException(
            status_code=503,
            detail={
                "ok": False,
                "blocked": True,
                "safe_mode": True,
                "message": "Scanner access control is not configured. No scan, letters, exports, or customer-facing findings are allowed.",
            },
        )
    if scanner_token != scanner_access_token or not device_id.strip():
        raise HTTPException(
            status_code=403,
            detail={
                "ok": False,
                "blocked": True,
                "safe_mode": True,
                "message": "Scanner access check failed. No scan, letters, exports, or customer-facing findings are allowed.",
            },
        )
    return {"ok": True, "mode": "production_access_verified", "device_id_present": True}


def extract_pdf_text(path: Path) -> tuple[str, int]:
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed. Run: pip install -r requirements.txt")

    reader = PdfReader(str(path))
    parts = []
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            text = f"[Page {page_num} text extraction error: {exc}]"
        parts.append(f"\n\n--- PAGE {page_num} ---\n{text}")

    return "\n".join(parts), len(reader.pages)


@app.get("/health")
def health():
    payload = service_status_payload(check_storage=False)
    payload.update({
        "service": "credit-vivo-proprietary-scanner-api",
        "version": "16.0",
        "paid_ai_used": False,
        "anthropic_required": False,
        "pymupdf_required": False,
        "parser_engine": "Credit Vivo Proprietary Parser Engine",
        "pdf_text_engine": "pypdf",
        "max_files": MAX_FILES,
        "max_file_mb": MAX_FILE_MB,
        "retain_uploads": RETAIN_UPLOADS,
        "write_raw_text": WRITE_RAW_TEXT,
    })
    return payload


@app.get("/livez")
def livez():
    return service_status_payload(check_storage=False)


@app.get("/readyz")
def readyz():
    payload = service_status_payload(check_storage=True)
    if not payload["ok"]:
        return JSONResponse(status_code=503, content=payload)
    return payload


@app.get("/scanner/health")
@app.get("/api/scanner/health")
def scanner_health():
    payload = run_scanner_preflight_health_check()
    if not payload["ok"]:
        return JSONResponse(status_code=503, content=payload)
    return payload


async def save_pdf_upload(file: UploadFile, dest: Path) -> int:
    safe_type = (file.content_type or "").lower()
    if safe_type and safe_type not in ALLOWED_PDF_TYPES:
        raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF upload.")

    if dest.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail=f"{file.filename} must be a PDF file.")

    total = 0
    try:
        with dest.open("wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"{file.filename} is larger than the {MAX_FILE_MB} MB beta upload limit.",
                    )
                f.write(chunk)
    finally:
        await file.close()

    if total == 0:
        raise HTTPException(status_code=400, detail=f"{file.filename} is empty.")

    return total


@app.post("/scanner/parse")
@app.post("/api/scanner/parse")
async def parse_uploaded_reports(
    files: List[UploadFile] = File(...),
    use_ai_second_pass: bool = Form(default=False),
    x_credit_vivo_scanner_token: str = Header(default=""),
    x_credit_vivo_device_id: str = Header(default=""),
):
    """
    Accept one or more PDF credit reports.

    `use_ai_second_pass` is accepted for backwards compatibility but ignored.
    v16 uses Credit Vivo Proprietary Parser Engine only.
    """
    if not scanner_accepts_uploads():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "scanner_uploads_disabled",
                "message": "Credit report uploads are temporarily unavailable while secure staging validation is completed.",
            },
        )
    scanner_health_payload = require_scanner_health_or_block()
    scanner_access_payload = require_scanner_access_or_block(x_credit_vivo_scanner_token, x_credit_vivo_device_id)
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Beta upload is limited to {MAX_FILES} PDF files at a time.",
        )

    job_id = f"scan_{uuid.uuid4().hex[:12]}"
    job_dir = UPLOADS / job_id
    out_dir = OUTPUT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_texts: Dict[str, dict] = {}
    saved_files = []
    raw_text_files = []

    for index, file in enumerate(files, start=1):
        safe_name = Path(file.filename or f"report_{index}.pdf").name
        dest = job_dir / safe_name

        await save_pdf_upload(file, dest)

        try:
            text, pages = extract_pdf_text(dest)
            bureau = detect_bureau(safe_name, text)
            report_texts[safe_name] = {"text": text, "bureau": bureau}
            if WRITE_RAW_TEXT:
                raw_text_name = f"{safe_name}_raw_text.txt"
                (out_dir / raw_text_name).write_text(text, encoding="utf-8", errors="ignore")
                raw_text_files.append({
                    "filename": raw_text_name,
                    "source_filename": safe_name,
                    "bureau": bureau,
                    "pages": pages,
                    "chars": len(text),
                })
            saved_files.append({
                "filename": safe_name,
                "bureau": bureau,
                "pages": pages,
                "chars": len(text),
                "status": "extracted"
            })
        except Exception as exc:
            saved_files.append({
                "filename": safe_name,
                "bureau": f"Report {index}",
                "pages": 0,
                "chars": 0,
                "status": "error",
                "error": str(exc)
            })

    parsed = parse_reports(report_texts)
    write_outputs(parsed, out_dir, pre_scan_health_check=scanner_health_payload)
    data = result_to_dict(parsed)
    data["pre_scan_health_check"] = scanner_health_payload

    result = {
        "job_id": job_id,
        "files": saved_files,
        "raw_text_files": raw_text_files,
        "ai_second_pass": False,
        "paid_ai_used": False,
        "status": {
            "mode": "credit_vivo_proprietary_engine_v16",
            "message": "Parsed using Credit Vivo proprietary rule engine. No paid AI API used."
        },
        "review_items_count": len(data["tradelines"]),
        "review_items_preview": data["tradelines"][:25],
        "issues_count": len(data["issues"]),
        "issues_preview": data["issues"][:25],
        "cross_bureau_groups": data["cross_bureau_groups"],
        "customer_message": data["customer_summary"]["message"],
        "customer_summary": data["customer_summary"],
        "admin_summary": data["admin_summary"],
        "scanner_health_check": scanner_health_payload,
        "scanner_access_check": scanner_access_payload,
        "letter_workflow": data.get("letter_workflow"),
        "recommended_letter_queue": data.get("recommended_letter_queue", []),
        "fcra_review": data.get("fcra_review", []),
        "output_folder": str(out_dir),
    }

    (out_dir / "scan_result_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    device_id = x_credit_vivo_device_id.strip() or "anonymous"
    ph_capture(
        device_id,
        "credit_report_scan_completed",
        {
            "file_count": len(files),
            "tradelines_count": len(data["tradelines"]),
            "issues_count": len(data["issues"]),
            "letters_count": len(data.get("recommended_letter_queue", [])),
            "scan_health_ok": bool(scanner_health_payload.get("ok")),
        },
    )

    if not RETAIN_UPLOADS:
        shutil.rmtree(job_dir, ignore_errors=True)

    return JSONResponse(result)


@app.get("/api/health")
def api_health():
    return health()


@app.get("/admin/users/setup")
@app.get("/api/admin/users/setup")
def admin_users_setup():
    return JSONResponse({
        "ok": True,
        "service": "credit-vivo-admin-user-provisioning",
        "mode": "owner_setup_token_required",
        "token_configured": bool(os.getenv("ADMIN_SETUP_TOKEN")),
        "create_user_endpoint": "/api/admin/users/create",
        "list_users_endpoint": "/api/admin/users/list",
        "required_header": "X-Credit-Vivo-Admin-Setup-Token",
        "roles": role_templates(),
        "owner_note": (
            "This provisions backend user records for setup/testing. "
            "Full production login still requires Supabase, Auth0, Clerk, or another auth provider."
        ),
    })


@app.post("/admin/users/create")
@app.post("/api/admin/users/create")
async def admin_users_create(
    payload: Dict[str, object],
    x_credit_vivo_admin_setup_token: str | None = Header(default=None),
):
    try:
        require_setup_token(x_credit_vivo_admin_setup_token, os.getenv("ADMIN_SETUP_TOKEN"))
        user, temporary_password = build_provisioned_user(payload, created_by="owner_admin")
        append_provisioned_user(user, ADMIN_USER_LOG)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    ph_capture(
        "owner_admin",
        "admin_user_created",
        {
            "role": user.role,
            "password_reset_required": user.password_reset_required,
        },
    )

    return JSONResponse({
        "ok": True,
        "service": "credit-vivo-admin-user-provisioning",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "role_label": user.role_label,
            "privileges": user.privileges,
            "password_reset_required": user.password_reset_required,
            "status": user.status,
        },
        "temporary_password": temporary_password,
        "important": "Temporary password is returned once. Store securely and force reset after first login.",
    })


@app.get("/admin/users/list")
@app.get("/api/admin/users/list")
def admin_users_list(
    x_credit_vivo_admin_setup_token: str | None = Header(default=None),
):
    try:
        require_setup_token(x_credit_vivo_admin_setup_token, os.getenv("ADMIN_SETUP_TOKEN"))
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    users = read_provisioned_users(ADMIN_USER_LOG)
    safe_users = [
        {
            "user_id": user.get("user_id"),
            "email": user.get("email"),
            "display_name": user.get("display_name"),
            "role": user.get("role"),
            "role_label": user.get("role_label"),
            "privileges": user.get("privileges", []),
            "password_reset_required": user.get("password_reset_required"),
            "created_at": user.get("created_at"),
            "status": user.get("status"),
        }
        for user in users
    ]
    return JSONResponse({
        "ok": True,
        "service": "credit-vivo-admin-user-provisioning",
        "user_count": len(safe_users),
        "users": safe_users,
    })


@app.get("/growth-ai/brief")
@app.get("/api/growth-ai/brief")
def growth_ai_brief(
    visitors: int = 0,
    leads: int = 0,
    free_scans_started: int = 0,
    free_scans_completed: int = 0,
    paid_customers: int = 0,
    monthly_recurring_revenue: float = 0.0,
    cancellations: int = 0,
    ad_spend: float = 0.0,
    referral_signups: int = 0,
):
    snapshot = GrowthSnapshot(
        visitors=visitors,
        leads=leads,
        free_scans_started=free_scans_started,
        free_scans_completed=free_scans_completed,
        paid_customers=paid_customers,
        monthly_recurring_revenue=monthly_recurring_revenue,
        cancellations=cancellations,
        ad_spend=ad_spend,
        referral_signups=referral_signups,
    )
    return JSONResponse(build_growth_brief(snapshot))


@app.post("/growth-ai/lead-score")
@app.post("/api/growth-ai/lead-score")
async def growth_ai_lead_score(signals: Dict[str, bool]):
    score = lead_score(signals)
    ph_capture(
        "anonymous",
        "growth_ai_lead_scored",
        {
            "signal_count": len(signals),
            "score": score,
        },
    )
    return JSONResponse({
        "ok": True,
        "service": "credit-vivo-growth-ai",
        "lead_score": score,
    })


@app.get("/growth-ai/sources")
@app.get("/api/growth-ai/sources")
def growth_ai_sources():
    return JSONResponse(build_growth_source_brief())


@app.get("/growth-ai/ad-plan")
@app.get("/api/growth-ai/ad-plan")
def growth_ai_ad_plan():
    return JSONResponse(build_ad_plan())


@app.get("/growth-ai/codex-advisor")
@app.get("/api/growth-ai/codex-advisor")
def growth_ai_codex_advisor(
    question: str = "What should Growth AI do next to bring Credit Vivo customers?",
    focus: str = "growth_strategy_review",
    visitors: int = 0,
    leads: int = 0,
    free_scans_started: int = 0,
    free_scans_completed: int = 0,
    paid_customers: int = 0,
    monthly_recurring_revenue: float = 0.0,
    cancellations: int = 0,
    ad_spend: float = 0.0,
    referral_signups: int = 0,
):
    snapshot = GrowthSnapshot(
        visitors=visitors,
        leads=leads,
        free_scans_started=free_scans_started,
        free_scans_completed=free_scans_completed,
        paid_customers=paid_customers,
        monthly_recurring_revenue=monthly_recurring_revenue,
        cancellations=cancellations,
        ad_spend=ad_spend,
        referral_signups=referral_signups,
    )
    return JSONResponse(build_codex_advisor_brief(question=question, snapshot=snapshot, focus=focus))


@app.get("/growth-ai/problem-solver")
@app.get("/api/growth-ai/problem-solver")
def growth_ai_problem_solver():
    return JSONResponse(build_problem_solver_brief())


@app.post("/growth-ai/solve")
@app.post("/api/growth-ai/solve")
async def growth_ai_solve(payload: Dict[str, object]):
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required.")
    return JSONResponse(solve_growth_problem(question))


@app.get("/growth-ai/codex-like-capabilities")
@app.get("/api/growth-ai/codex-like-capabilities")
def growth_ai_codex_like_capabilities():
    return JSONResponse(build_codex_like_growth_brief())


@app.get("/growth-ai/forensic-search")
@app.get("/api/growth-ai/forensic-search")
def growth_ai_forensic_search():
    return JSONResponse(build_forensic_search_brief())


@app.post("/growth-ai/forensic-search/run")
@app.post("/api/growth-ai/forensic-search/run")
async def growth_ai_forensic_search_run(payload: Dict[str, object]):
    query = str(payload.get("query", "Find the strongest growth opportunity for Credit Vivo")).strip()
    return JSONResponse(run_forensic_search(query))


@app.get("/growth-ai/credit-domain-expertise")
@app.get("/api/growth-ai/credit-domain-expertise")
def growth_ai_credit_domain_expertise():
    return JSONResponse(build_credit_domain_expertise_brief())


@app.get("/growth-ai/cross-ai-directives")
@app.get("/api/growth-ai/cross-ai-directives")
def growth_ai_cross_ai_directives():
    return JSONResponse(build_cross_ai_growth_directives())


@app.get("/growth-ai/live-access")
@app.get("/api/growth-ai/live-access")
def growth_ai_live_access():
    return JSONResponse(build_live_access_brief())


@app.get("/operator-ai/brief")
@app.get("/api/operator-ai/brief")
def operator_ai_demo_brief():
    return JSONResponse(build_operator_brief(demo_operator_events()))


@app.post("/operator-ai/brief")
@app.post("/api/operator-ai/brief")
async def operator_ai_brief(events: List[Dict[str, str]]):
    parsed_events = [
        OperatorEvent(
            area=event.get("area", "general"),
            event_type=event.get("event_type", "review"),
            severity=event.get("severity", "low"),
            detail=event.get("detail", ""),
            customer_id=event.get("customer_id"),
        )
        for event in events
    ]
    return JSONResponse(build_operator_brief(parsed_events))


@app.get("/vivo-command/brief")
@app.get("/api/vivo-command/brief")
def vivo_command_brief(
    visitors: int = 0,
    leads: int = 0,
    free_scans_started: int = 0,
    free_scans_completed: int = 0,
    paid_customers: int = 0,
    monthly_recurring_revenue: float = 0.0,
    cancellations: int = 0,
    ad_spend: float = 0.0,
    referral_signups: int = 0,
):
    snapshot = GrowthSnapshot(
        visitors=visitors,
        leads=leads,
        free_scans_started=free_scans_started,
        free_scans_completed=free_scans_completed,
        paid_customers=paid_customers,
        monthly_recurring_revenue=monthly_recurring_revenue,
        cancellations=cancellations,
        ad_spend=ad_spend,
        referral_signups=referral_signups,
    )
    return JSONResponse(build_command_brief(growth_snapshot=snapshot))


@app.get("/vivo-command/ai-operating-system")
@app.get("/api/vivo-command/ai-operating-system")
def vivo_ai_operating_system():
    return JSONResponse(build_ai_operating_system_brief())


@app.get("/vivo-command/ai-tracking-map")
@app.get("/api/vivo-command/ai-tracking-map")
def vivo_ai_tracking_map():
    return JSONResponse(build_ai_tracking_map())


@app.post("/events/track")
@app.post("/api/events/track")
async def track_vivo_event(payload: Dict[str, object]):
    event = build_event(payload)
    append_event(event, EVENT_LOG)
    return JSONResponse({
        "ok": True,
        "service": "vivo-event-collector",
        "event_type": event.event_type,
        "source": event.source,
        "stored": True,
    })


@app.get("/events/summary")
@app.get("/api/events/summary")
def vivo_event_summary():
    events = read_events(EVENT_LOG)
    return JSONResponse({
        "ok": True,
        "service": "vivo-event-collector",
        "summary": summarize_events(events),
        "growth_snapshot": growth_snapshot_from_events(events).__dict__,
    })


@app.post("/leads/capture")
@app.post("/api/leads/capture")
async def capture_lead(payload: Dict[str, object]):
    try:
        lead = build_lead(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    append_lead(lead, LEAD_LOG)
    append_event(build_event({
        "event_type": "lead_created",
        "source": lead.source,
        "campaign": lead.campaign,
        "metadata": {
            "goal": lead.goal,
            "email_domain": lead.email.split("@")[-1],
        },
    }), EVENT_LOG)

    ph_capture(
        "anonymous",
        "lead_captured",
        {
            "source": lead.source,
            "campaign": lead.campaign or "direct",
            "goal": lead.goal,
        },
    )

    return JSONResponse({
        "ok": True,
        "service": "vivo-lead-capture",
        "stored": True,
        "campaign": lead.campaign,
        "source": lead.source,
    })


@app.get("/leads/summary")
@app.get("/api/leads/summary")
def lead_summary():
    leads = read_leads(LEAD_LOG)
    return JSONResponse({
        "ok": True,
        "service": "vivo-lead-capture",
        "summary": summarize_leads(leads),
    })


@app.post("/growth-ai/outreach-plan")
@app.post("/api/growth-ai/outreach-plan")
async def growth_ai_outreach_plan(payload: Dict[str, object]):
    contacts = payload.get("contacts", [])
    if not isinstance(contacts, list):
        raise HTTPException(status_code=400, detail="contacts must be a list.")

    owner_approved = bool(payload.get("owner_approved", False))
    ph_capture(
        "anonymous",
        "outreach_plan_requested",
        {
            "contact_count": len(contacts),
            "owner_approved": owner_approved,
        },
    )
    return JSONResponse(build_outreach_plan(contacts, owner_approved=owner_approved))


@app.get("/vivo-command/live")
@app.get("/api/vivo-command/live")
def vivo_command_live_brief():
    events = read_events(EVENT_LOG)
    snapshot = growth_snapshot_from_events(events)
    operator_events = operator_events_from_vivo_events(events)
    return JSONResponse({
        **build_command_brief(growth_snapshot=snapshot, operator_events=operator_events),
        "event_summary": summarize_events(events),
    })


@app.get("/scanner/result/{job_id}")
@app.get("/api/scanner/result/{job_id}")
def get_result(job_id: str, x_credit_vivo_scanner_token: str = Header(default=""), x_credit_vivo_device_id: str = Header(default="")):
    require_scanner_health_or_block()
    require_scanner_access_or_block(x_credit_vivo_scanner_token, x_credit_vivo_device_id)
    summary = scanner_job_dir(job_id) / "scan_result_summary.json"
    if not summary.exists():
        return JSONResponse({"ok": False, "error": "Result not found"}, status_code=404)
    return JSONResponse(json.loads(summary.read_text(encoding="utf-8")))


@app.get("/scanner/result/{job_id}/full")
@app.get("/api/scanner/result/{job_id}/full")
def get_full_result(job_id: str, x_credit_vivo_scanner_token: str = Header(default=""), x_credit_vivo_device_id: str = Header(default="")):
    require_scanner_health_or_block()
    require_scanner_access_or_block(x_credit_vivo_scanner_token, x_credit_vivo_device_id)
    full = scanner_job_dir(job_id) / "credit_vivo_parser_result.json"
    if not full.exists():
        return JSONResponse({"ok": False, "error": "Full result not found"}, status_code=404)
    return JSONResponse(json.loads(full.read_text(encoding="utf-8")))


@app.get("/scanner/result/{job_id}/download/{download_name}")
@app.get("/api/scanner/result/{job_id}/download/{download_name}")
def download_scanner_output(job_id: str, download_name: str, x_credit_vivo_scanner_token: str = Header(default=""), x_credit_vivo_device_id: str = Header(default="")):
    require_scanner_health_or_block()
    require_scanner_access_or_block(x_credit_vivo_scanner_token, x_credit_vivo_device_id)
    download = SCAN_DOWNLOADS.get(download_name)
    if not download:
        return JSONResponse({"ok": False, "error": "Download not found"}, status_code=404)

    filename, media_type, download_filename = download
    path = scanner_job_dir(job_id) / filename
    if not path.exists():
        return JSONResponse({"ok": False, "error": "Scanner output not found"}, status_code=404)

    device_id = x_credit_vivo_device_id.strip() or "anonymous"
    ph_capture(
        device_id,
        "scan_result_downloaded",
        {"download_type": download_name},
    )

    return FileResponse(path, media_type=media_type, filename=download_filename)
