from __future__ import annotations

"""
Credit Vivo Proprietary Scanner API v18.1.7

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
import hmac
import hashlib
import secrets
import time
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Dict, List

from fastapi import Cookie, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from .credit_vivo_proprietary_engine import (
        detect_bureau,
        parse_reports,
        result_to_dict,
        write_outputs,
    )
    from .report_ingestion import build_uploaded_pdf_ingestion, normalize_ingestion_items
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
    from .cv_market_growth_ai import (
        generate_founder_summary,
        get_growth_dashboard,
        recommend_market_opportunities,
    )
    from .campaign_builder_engine import build_campaign, compliance_check_message
    from .consent_log_engine import log_consent
    from .growth_approval_queue import create_approval_item
    from .lead_intelligence_engine import score_lead
    from .partner_referral_engine import track_partner_referral
    from .revenue_attribution_engine import attribute_revenue
    from .market_ai_studio import (
        LEARNING_TOPICS,
        build_market_ai_dashboard,
        build_market_templates,
        check_marketing_compliance,
        create_render_job,
        generate_learning_storyboard,
        generate_video_script,
        get_topic,
        sample_market_assets,
    )
except ImportError:
    from credit_vivo_proprietary_engine import (
        detect_bureau,
        parse_reports,
        result_to_dict,
        write_outputs,
    )
    from report_ingestion import build_uploaded_pdf_ingestion, normalize_ingestion_items
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
    from cv_market_growth_ai import (
        generate_founder_summary,
        get_growth_dashboard,
        recommend_market_opportunities,
    )
    from campaign_builder_engine import build_campaign, compliance_check_message
    from consent_log_engine import log_consent
    from growth_approval_queue import create_approval_item
    from lead_intelligence_engine import score_lead
    from partner_referral_engine import track_partner_referral
    from revenue_attribution_engine import attribute_revenue
    from market_ai_studio import (
        LEARNING_TOPICS,
        build_market_ai_dashboard,
        build_market_templates,
        check_marketing_compliance,
        create_render_job,
        generate_learning_storyboard,
        generate_video_script,
        get_topic,
        sample_market_assets,
    )

ROOT = Path(__file__).resolve().parent
STORAGE_ROOT = Path(os.getenv("SCANNER_STORAGE_DIR", "/tmp/creditvivo-scanner" if os.getenv("VERCEL") else str(ROOT)))
UPLOADS = STORAGE_ROOT / "uploads"
OUTPUT = STORAGE_ROOT / "output"
EVENT_LOG = STORAGE_ROOT / "events" / "vivo_events.jsonl"
LEAD_LOG = STORAGE_ROOT / "leads" / "captured_leads.jsonl"
ADMIN_USER_LOG = STORAGE_ROOT / "users" / "provisioned_users.jsonl"
GROWTH_ROOT = STORAGE_ROOT / "growth"
ADMIN_AUTH_ROOT = STORAGE_ROOT / "admin_auth"
AUDIT_LOG = STORAGE_ROOT / "audit" / "security_events.jsonl"
LOCAL_ADMIN_CREDENTIALS = ADMIN_AUTH_ROOT / "local_founder_login.json"
LOCAL_ADMIN_SESSION_SECRET = ADMIN_AUTH_ROOT / "local_session_secret.txt"
APPROVAL_QUEUE_LOG = GROWTH_ROOT / "approval_queue.jsonl"
CONSENT_LOG = GROWTH_ROOT / "consent_log.jsonl"
PARTNER_REFERRAL_LOG = GROWTH_ROOT / "partner_referrals.jsonl"
REVENUE_ATTRIBUTION_LOG = GROWTH_ROOT / "revenue_attribution.jsonl"
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
    "vault.json": ("document_vault/document_vault_manifest.json", "application/json", "credit-vivo-document-vault-manifest.json"),
    "packet-comparison.json": ("document_vault/three_bureau_comparison_attachment.json", "application/json", "credit-vivo-3b-comparison-attachment.json"),
}


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def is_production() -> bool:
    return os.getenv("SCANNER_ENVIRONMENT", "").strip().lower() == "production"


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def auth_provider_name() -> str:
    return os.getenv("CREDITVIVO_AUTH_PROVIDER", "").strip().lower()


def production_auth_configured() -> bool:
    provider = auth_provider_name()
    if provider and provider not in {"local", "local-dev", "local_dev", "local-dev-until-supabase-auth0-or-clerk"}:
        return True
    return bool(os.getenv("SUPABASE_URL") or os.getenv("AUTH0_DOMAIN") or os.getenv("CLERK_SECRET_KEY"))


def encryption_ready() -> bool:
    key = os.getenv("CREDITVIVO_STORAGE_ENCRYPTION_KEY", "")
    return len(key.strip()) >= 32 and os.getenv("CREDITVIVO_STORAGE_ENCRYPTION_ENABLED", "").lower() == "true"


def production_scanner_shell_protected() -> bool:
    return env_bool("SCANNER_REQUIRE_LOGIN_FOR_SCANNER", default=True)


def api_docs_protected() -> bool:
    return env_bool("SCANNER_PROTECT_DOCS", default=True) or is_production()


def email_safety_config() -> dict:
    return {
        "provider": os.getenv("EMAIL_PROVIDER", "disabled"),
        "from": os.getenv("EMAIL_FROM", "no-reply@creditvivo.com"),
        "support_email": os.getenv("SUPPORT_EMAIL", "support@creditvivo.com"),
        "privacy_email": os.getenv("PRIVACY_EMAIL", "privacy@creditvivo.com"),
        "security_email": os.getenv("SECURITY_EMAIL", "security@creditvivo.com"),
        "social_email": os.getenv("SOCIAL_EMAIL", "social@creditvivo.com"),
        "email_sending_enabled": env_bool("ENABLE_EMAIL_SENDING", default=False),
        "marketing_emails_enabled": env_bool("ENABLE_MARKETING_EMAILS", default=False),
        "dispute_email_auto_send_enabled": env_bool("ENABLE_DISPUTE_EMAIL_AUTO_SEND", default=False),
    }


def staging_safety_config() -> dict:
    app_env = os.getenv("APP_ENV") or os.getenv("SCANNER_ENVIRONMENT", "local")
    is_staging = app_env.lower() == "staging"
    return {
        "environment_name": "Credit Vivo Staging Safe Mode" if is_staging else app_env,
        "is_staging": is_staging,
        "synthetic_reports_only": env_bool("SCANNER_USE_SYNTHETIC_REPORTS", default=is_staging),
        "allow_real_customer_data": env_bool("SCANNER_ALLOW_REAL_CUSTOMER_DATA", default=not is_staging),
        "payments_mode": os.getenv("PAYMENTS_MODE", "test" if is_staging else "disabled"),
        "stripe_mode": os.getenv("STRIPE_MODE", "test" if is_staging else "disabled"),
        "external_calls_enabled": env_bool("ENABLE_EXTERNAL_CALLS", default=False),
        "auto_send_enabled": env_bool("ENABLE_AUTO_SEND", default=False),
        "customer_final_result_without_qa": env_bool("ENABLE_CUSTOMER_FINAL_RESULT_WITHOUT_QA", default=False),
        "letters_without_verified_issue": env_bool("ENABLE_LETTERS_WITHOUT_VERIFIED_ISSUE", default=False),
        "complaints_without_approval": env_bool("ENABLE_COMPLAINTS_WITHOUT_APPROVAL", default=False),
        "attorney_escalation_without_approval": env_bool("ENABLE_ATTORNEY_ESCALATION_WITHOUT_APPROVAL", default=False),
    }


def append_audit_event(event_type: str, *, request: Request | None = None, user: str | None = None, outcome: str = "ok", detail: dict | None = None) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "outcome": outcome,
        "user": user or "",
        "path": getattr(getattr(request, "url", None), "path", "") if request else "",
        "method": getattr(request, "method", "") if request else "",
        "client": getattr(getattr(request, "client", None), "host", "") if request else "",
        "detail": detail or {},
    }
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def ensure_local_admin_credentials() -> dict:
    ADMIN_AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    env_username = os.getenv("CREDITVIVO_ADMIN_USERNAME")
    env_password = os.getenv("CREDITVIVO_ADMIN_PASSWORD")
    if env_username and env_password:
        salt = "env"
        return {
            "username": env_username,
            "password": env_password,
            "password_hash": _hash_password(env_password, salt),
            "salt": salt,
            "role": "founder",
            "source": "environment",
        }
    if is_production():
        raise RuntimeError("Production founder login requires a production auth provider or explicit secret-backed admin credentials.")
    if LOCAL_ADMIN_CREDENTIALS.exists():
        return json.loads(LOCAL_ADMIN_CREDENTIALS.read_text(encoding="utf-8"))

    password = secrets.token_urlsafe(12)
    salt = secrets.token_hex(12)
    credentials = {
        "username": "founder@creditvivo.local",
        "password": password,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "role": "founder",
        "source": "local_generated",
        "note": "Local development credential only. Replace with production auth before launch.",
    }
    LOCAL_ADMIN_CREDENTIALS.write_text(json.dumps(credentials, indent=2), encoding="utf-8")
    return credentials


def admin_session_secret() -> str:
    ADMIN_AUTH_ROOT.mkdir(parents=True, exist_ok=True)
    env_secret = os.getenv("ADMIN_SESSION_SECRET")
    if env_secret:
        return env_secret
    if is_production():
        raise RuntimeError("ADMIN_SESSION_SECRET must be configured in production.")
    if LOCAL_ADMIN_SESSION_SECRET.exists():
        return LOCAL_ADMIN_SESSION_SECRET.read_text(encoding="utf-8").strip()
    secret = secrets.token_urlsafe(32)
    LOCAL_ADMIN_SESSION_SECRET.write_text(secret, encoding="utf-8")
    return secret


def verify_admin_credentials(username: str, password: str) -> bool:
    credentials = ensure_local_admin_credentials()
    salt = credentials.get("salt", "")
    expected_hash = credentials.get("password_hash", "")
    return (
        hmac.compare_digest(username.strip().lower(), str(credentials.get("username", "")).lower())
        and hmac.compare_digest(_hash_password(password, salt), expected_hash)
    )


def create_admin_session(username: str, max_age_seconds: int = 8 * 60 * 60) -> str:
    expires = int(time.time()) + max_age_seconds
    payload = f"{username}|founder|{expires}"
    signature = hmac.new(admin_session_secret().encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}|{signature}"


def read_admin_session(token: str | None) -> dict | None:
    if not token or not isinstance(token, str):
        return None
    parts = token.split("|")
    if len(parts) != 4:
        return None
    username, role, expires_raw, signature = parts
    payload = f"{username}|{role}|{expires_raw}"
    expected = hmac.new(admin_session_secret().encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        expires = int(expires_raw)
    except ValueError:
        return None
    if expires < int(time.time()):
        return None
    return {"username": username, "role": role, "expires": expires}


def admin_login_html(error: str = "") -> HTMLResponse:
    try:
        credentials = ensure_local_admin_credentials()
    except RuntimeError as exc:
        return HTMLResponse(f"""
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Production Login Not Configured | Credit Vivo</title></head>
<body style="font-family:Inter,Segoe UI,Arial,sans-serif;background:#f6f7f9;color:#17202a;padding:32px;">
<main style="max-width:680px;margin:0 auto;background:white;border:1px solid #d8dde6;border-radius:8px;padding:24px;">
<h1>Production Login Not Configured</h1>
<p>{escape(str(exc))}</p>
<p>Configure Supabase, Auth0, Clerk, or secret-backed admin credentials before using the founder backend in production.</p>
</main></body></html>
""", status_code=503)
    safe_error = f'<div class="error">{escape(error)}</div>' if error else ""
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Founder Login | Credit Vivo</title>
  <style>
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; font-family:Inter, Segoe UI, Arial, sans-serif; background:#f6f7f9; color:#17202a; }}
    main {{ width:min(440px, calc(100% - 32px)); background:#fff; border:1px solid #d8dde6; border-radius:8px; padding:24px; box-shadow:0 10px 24px rgba(28,39,58,.08); }}
    h1 {{ margin:0 0 8px; font-size:26px; }}
    p {{ margin:0 0 16px; color:#56616f; line-height:1.5; }}
    label {{ display:block; font-weight:700; margin:12px 0 6px; }}
    input {{ width:100%; box-sizing:border-box; padding:12px; border:1px solid #cbd5e1; border-radius:8px; font-size:15px; }}
    button {{ margin-top:16px; width:100%; border:0; border-radius:8px; padding:12px 16px; background:#0d5c75; color:#fff; font-weight:800; cursor:pointer; }}
    .note {{ background:#eef8fb; border-left:4px solid #0d5c75; padding:10px; margin-top:14px; color:#344054; }}
    .error {{ background:#fff7ed; border-left:4px solid #9a3412; padding:10px; margin:12px 0; color:#7c2d12; }}
    code {{ overflow-wrap:anywhere; }}
  </style>
</head>
<body>
  <main>
    <h1>Founder Login</h1>
    <p>Local backend access for Credit Vivo founder/admin testing.</p>
    {safe_error}
    <form method="post" action="/admin/login">
      <label for="username">Email</label>
      <input id="username" name="username" type="email" autocomplete="username" value="{escape(str(credentials.get("username", "")))}" required>
      <label for="password">Password</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required>
      <button type="submit">Log In</button>
    </form>
    <div class="note">Local development only. Production must use secure auth, role permissions, 2FA, audit logs, and encrypted storage.</div>
  </main>
</body>
</html>
""")


def admin_login_redirect() -> RedirectResponse:
    return RedirectResponse("/founder-login", status_code=303)


def scanner_job_dir(job_id: str) -> Path:
    if not job_id.startswith("scan_") or any(ch in job_id for ch in ("/", "\\", "..")):
        raise HTTPException(status_code=400, detail="Invalid scanner job id.")
    return OUTPUT / job_id


MAX_FILES = env_int("SCANNER_MAX_FILES", 3)
MAX_FILE_MB = env_int("SCANNER_MAX_FILE_MB", 25)
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024
RETAIN_UPLOADS = env_bool("SCANNER_RETAIN_UPLOADS", default=False)
WRITE_RAW_TEXT = env_bool("SCANNER_WRITE_RAW_TEXT", default=False)
RETENTION_DAYS = env_int("SCANNER_RETENTION_DAYS", 30)
RATE_LIMIT_WINDOW_SECONDS = env_int("SCANNER_RATE_LIMIT_WINDOW_SECONDS", 60)
RATE_LIMIT_MAX_LOGIN = env_int("SCANNER_RATE_LIMIT_MAX_LOGIN", 10)
RATE_LIMIT_MAX_UPLOAD = env_int("SCANNER_RATE_LIMIT_MAX_UPLOAD", 6)
RATE_LIMIT_MAX_ADMIN = env_int("SCANNER_RATE_LIMIT_MAX_ADMIN", 120)
ALLOWED_PDF_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream", "binary/octet-stream"}
LIVE_CREDITVIVO_HOME_URL = os.getenv("LIVE_CREDITVIVO_HOME_URL", "https://www.creditvivo.com/")
LIVE_CREDITVIVO_SCAN_URL = os.getenv("LIVE_CREDITVIVO_SCAN_URL", "https://www.creditvivo.com/scan")
LIVE_CREDITVIVO_LOGIN_URL = os.getenv("LIVE_CREDITVIVO_LOGIN_URL", "https://www.creditvivo.com/dashboard")

SCANNER_API_VERSION = "18.1.7"

app = FastAPI(
    title="Credit Vivo Proprietary Scanner API",
    version=SCANNER_API_VERSION,
    docs_url=None if is_production() else "/docs",
    redoc_url=None if is_production() else "/redoc",
    openapi_url=None if is_production() else "/openapi.json",
)

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
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Credit-Vivo-Admin-Setup-Token"],
)

RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}


def rate_limit_group(path: str) -> tuple[str, int] | None:
    if path in {"/admin/login", "/api/admin/login", "/founder-login", "/api/founder-login"}:
        return ("login", RATE_LIMIT_MAX_LOGIN)
    if path in {"/scanner/parse", "/api/scanner/parse"}:
        return ("upload", RATE_LIMIT_MAX_UPLOAD)
    if path.startswith(("/admin", "/api/admin", "/growth-ai", "/api/growth-ai", "/market-ai", "/api/market", "/operator-ai", "/api/operator-ai", "/vivo-command", "/api/vivo-command")):
        return ("admin", RATE_LIMIT_MAX_ADMIN)
    return None


def rate_limit_allowed(request: Request) -> bool:
    group = rate_limit_group(request.url.path)
    if not group:
        return True
    name, limit = group
    client = getattr(getattr(request, "client", None), "host", "unknown")
    key = f"{name}:{client}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    bucket = [ts for ts in RATE_LIMIT_BUCKETS.get(key, []) if ts >= window_start]
    if len(bucket) >= limit:
        RATE_LIMIT_BUCKETS[key] = bucket
        return False
    bucket.append(now)
    RATE_LIMIT_BUCKETS[key] = bucket
    return True

ADMIN_PUBLIC_PATHS = {
    "/admin/login",
    "/api/admin/login",
    "/founder-login",
    "/api/founder-login",
    "/admin/logout",
    "/api/admin/logout",
    "/founder-logout",
    "/api/founder-logout",
}


@app.middleware("http")
async def protect_founder_admin_routes(request: Request, call_next):
    path = request.url.path
    if not rate_limit_allowed(request):
        append_audit_event("rate_limit_blocked", request=request, outcome="blocked", detail={"path": path})
        return JSONResponse({"ok": False, "error": "rate_limit_exceeded"}, status_code=429)

    protected = (
        path == "/admin"
        or path == "/api/admin"
        or path.startswith("/admin/")
        or path.startswith("/api/admin/")
        or path == "/founder"
        or path == "/api/founder"
        or path.startswith("/founder/")
        or path.startswith("/api/founder/")
        or path.startswith("/scanner/result/")
        or path.startswith("/api/scanner/result/")
        or path == "/findings"
        or path.startswith("/findings/")
        or path == "/api/findings"
        or path.startswith("/api/findings/")
        or path == "/dashboard/documents"
        or path == "/dashboard/letters"
        or path == "/api/dashboard/documents"
        or path == "/api/dashboard/letters"
        or path.startswith("/growth-ai/")
        or path.startswith("/api/growth-ai/")
        or path == "/market-ai"
        or path.startswith("/market-ai/")
        or path.startswith("/api/market/")
        or path.startswith("/operator-ai/")
        or path.startswith("/api/operator-ai/")
        or path.startswith("/vivo-command/")
        or path.startswith("/api/vivo-command/")
        or path.startswith("/events/")
        or path.startswith("/api/events/")
        or path.startswith("/leads/")
        or path.startswith("/api/leads/")
        or path in {"/docs", "/redoc", "/openapi.json"} and api_docs_protected()
        or path in {"/scanner", "/api/scanner", "/scan", "/api/scan"} and production_scanner_shell_protected()
        or path in {"/scanner/parse", "/api/scanner/parse", "/scanner/latest/copy-to-desktop"}
    )
    if protected and path not in ADMIN_PUBLIC_PATHS and not read_admin_session(request.cookies.get("cv_admin_session")):
        append_audit_event("auth_required", request=request, outcome="blocked", detail={"path": path})
        if path.startswith("/api/") or "application/json" in request.headers.get("accept", ""):
            return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/founder-login"}, status_code=401)
        return RedirectResponse("/founder-login", status_code=303)
    return await call_next(request)


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
    email_config = email_safety_config()
    staging_config = staging_safety_config()
    return {
        "ok": True,
        "service": "credit-vivo-proprietary-scanner-api",
        "version": SCANNER_API_VERSION,
        "environment": os.getenv("SCANNER_ENVIRONMENT", "local"),
        "app_env": os.getenv("APP_ENV", os.getenv("SCANNER_ENVIRONMENT", "local")),
        "staging_safe_mode": staging_config["is_staging"],
        "synthetic_reports_only": staging_config["synthetic_reports_only"],
        "allow_real_customer_data": staging_config["allow_real_customer_data"],
        "payments_mode": staging_config["payments_mode"],
        "stripe_mode": staging_config["stripe_mode"],
        "external_calls_enabled": staging_config["external_calls_enabled"],
        "auto_send_enabled": staging_config["auto_send_enabled"],
        "production_mode": is_production(),
        "paid_ai_used": False,
        "anthropic_required": False,
        "pymupdf_required": False,
        "parser_engine": "Credit Vivo Proprietary Parser Engine",
        "pdf_text_engine": "pypdf",
        "max_files": MAX_FILES,
        "max_file_mb": MAX_FILE_MB,
        "retain_uploads": RETAIN_UPLOADS,
        "write_raw_text": WRITE_RAW_TEXT,
        "scanner_shell_requires_login": production_scanner_shell_protected(),
        "email_provider": email_config["provider"],
        "email_sending_enabled": email_config["email_sending_enabled"],
        "marketing_emails_enabled": email_config["marketing_emails_enabled"],
        "dispute_email_auto_send_enabled": email_config["dispute_email_auto_send_enabled"],
    }


def member_portal_payload() -> dict:
    gate_message = "Customer data remains blocked until production auth, encrypted storage, scanner QA, and security gates pass."
    return {
        "profile": None,
        "stats": [],
        "uploads": [
            {"bureau": "Equifax", "status": "blocked", "note": "Secure backend required before upload."},
            {"bureau": "Experian", "status": "blocked", "note": "Secure backend required before upload."},
            {"bureau": "TransUnion", "status": "blocked", "note": "Secure backend required before upload."},
        ],
        "reviewAccounts": [],
        "positiveAccounts": [],
        "draftLetters": [],
        "progressSteps": [
            {
                "title": "Production gate active",
                "description": "Customer findings remain blocked until scanner health check, ground-truth validation, QA, security audit, and production gate pass.",
                "status": "blocked",
            }
        ],
        "progressMilestones": [
            {
                "phase": "Profile setup",
                "status": "current",
                "customerView": "Confirm contact details and credit goal before report review begins.",
                "adminGate": "Customer profile must be complete and consent must be logged.",
            },
            {
                "phase": "Identity and files",
                "status": "blocked",
                "customerView": "Upload identity, address, report, and supporting documents through secure intake.",
                "adminGate": "Admin must verify file ownership, readability, and document match before use.",
            },
            {
                "phase": "Report review",
                "status": "blocked",
                "customerView": "Possible report errors appear only after scanner and QA checks pass.",
                "adminGate": "Native parser output, evidence snippets, and confidence checks must pass review.",
            },
            {
                "phase": "Customer approvals",
                "status": "blocked",
                "customerView": "Review documented next steps and approve draft dispute prep before action.",
                "adminGate": "Customer approval, admin review, and compliance review are required.",
            },
        ],
        "messages": [],
        "documents": [
            {
                "name": "Government ID",
                "type": "Identity",
                "status": "needs_review",
                "visibility": "Customer + admin",
                "requiredFor": "Identity verification",
                "verifiedBy": "admin",
                "canUseForPrep": False,
                "note": "Must be readable, unexpired, and match the customer profile before any file review moves forward.",
            },
            {
                "name": "Proof of address",
                "type": "Address",
                "status": "pending",
                "visibility": "Customer + admin",
                "requiredFor": "Bureau correspondence and profile match",
                "verifiedBy": "admin",
                "canUseForPrep": False,
                "note": "Accepted examples include a recent utility bill, bank statement, or lease page showing name and address.",
            },
            {
                "name": "Three-bureau credit report",
                "type": "Credit report",
                "status": "blocked",
                "visibility": "Controlled report file",
                "requiredFor": "Plain-English review and scanner analysis",
                "verifiedBy": "system",
                "canUseForPrep": False,
                "note": "Raw report files stay hidden from customer UI until secure storage and access controls are approved.",
            },
            {
                "name": "Supporting documents",
                "type": "Evidence",
                "status": "pending",
                "visibility": "Customer + admin",
                "requiredFor": "Documented next steps",
                "verifiedBy": "admin",
                "canUseForPrep": False,
                "note": "Examples: creditor letters, paid receipts, court documents, FTC report, or police report when applicable.",
            },
        ],
        "identityVerification": {
            "status": "needs_review",
            "summary": "Identity verification is not complete. Credit Vivo must verify ID, address, and report ownership before using uploaded files.",
            "checks": [
                {"label": "Government ID", "status": "needs_review", "note": "Awaiting admin review and expiration check."},
                {"label": "Selfie/liveness", "status": "pending", "note": "Future vendor or manual review step; not connected yet."},
                {"label": "Address match", "status": "pending", "note": "Proof of address must match the customer profile."},
                {"label": "Report ownership", "status": "blocked", "note": "Credit report must match verified identity before scanner output is released."},
            ],
        },
        "customerTasks": [
            {
                "title": "Confirm profile information",
                "status": "current",
                "dueLabel": "Before review starts",
                "detail": "Confirm legal name, contact details, address, and credit goal. Sensitive IDs stay hidden.",
            },
            {
                "title": "Upload required documents",
                "status": "pending",
                "dueLabel": "Secure upload required",
                "detail": "Government ID, proof of address, three-bureau report, and supporting documents if available.",
            },
            {
                "title": "Wait for admin verification",
                "status": "blocked",
                "dueLabel": "Admin review",
                "detail": "Files are not used for dispute prep until system checks, admin review, and compliance gates pass.",
            },
        ],
        "productionGate": {
            "demoMode": False,
            "scannerConnected": True,
            "healthCheckPassed": True,
            "groundTruthPassed": False,
            "qaVerificationPassed": False,
            "securityAuditPassed": False,
            "productionGatePassed": False,
            "customerDataAllowed": False,
            "message": gate_message,
        },
    }


@app.get("/member/portal")
def member_portal_api():
    return JSONResponse(member_portal_payload())


def latest_scanner_job_id() -> str | None:
    jobs = [
        path
        for path in OUTPUT.iterdir()
        if (
            path.is_dir()
            and path.name.startswith("scan_")
            and (path / "scan_result_summary.json").exists()
            and (path / "credit_vivo_desktop_scanner_output.xlsx").exists()
        )
    ]
    if not jobs:
        return None
    return max(jobs, key=lambda path: path.stat().st_mtime).name


def desktop_output_root() -> Path:
    user_profile = Path(os.getenv("USERPROFILE", str(Path.home())))
    candidates = [
        user_profile / "OneDrive" / "Desktop",
        user_profile / "Desktop",
        Path.home() / "Desktop",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate / "Credit Vivo Scanner Outputs"
    return ROOT / "desktop_outputs"


def copy_scanner_outputs_to_desktop(job_id: str | None = None) -> dict:
    selected_job = job_id or latest_scanner_job_id()
    if not selected_job:
        raise HTTPException(status_code=404, detail="No scanner output job found.")
    source_dir = scanner_job_dir(selected_job)
    if not source_dir.exists():
        raise HTTPException(status_code=404, detail="Scanner output folder not found.")

    destination_dir = desktop_output_root() / selected_job
    destination_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for key, (filename, _media_type, download_filename) in SCAN_DOWNLOADS.items():
        source_file = source_dir / filename
        if source_file.exists():
            destination_file = destination_dir / download_filename
            shutil.copy2(source_file, destination_file)
            copied.append({
                "download_key": key,
                "filename": download_filename,
                "path": str(destination_file),
            })
    return {
        "ok": True,
        "job_id": selected_job,
        "folder": str(destination_dir),
        "copied": copied,
    }


def scanner_download_links_html(job_id: str | None) -> str:
    if not job_id:
        return "<p>No scanner outputs yet. Run a scan to create workbook and CSV files.</p>"
    links = [
        ("Workbook", "workbook.xlsx"),
        ("Issues CSV", "issues.csv"),
        ("Tradelines CSV", "tradelines.csv"),
        ("Draft Letters", "letters.txt"),
        ("Document Vault Manifest", "vault.json"),
        ("3B Packet Attachment JSON", "packet-comparison.json"),
    ]
    items = "\n".join(
        f'<a class="download" target="_blank" rel="noopener" href="/scanner/result/{job_id}/download/{name}">{label}</a>'
        for label, name in links
    )
    return (
        f'<p>Latest backend test job: <strong>{escape(job_id)}</strong></p>'
        f'<div class="downloads">{items}</div>'
        '<button id="copyLatestButton" type="button">Copy latest outputs to Desktop</button>'
        '<div id="copyStatus" class="status"></div>'
    )


def latest_full_scan_result() -> dict:
    job_id = latest_scanner_job_id()
    if not job_id:
        return {"job_id": None, "data": {}, "summary": {}}
    full_path = scanner_job_dir(job_id) / "credit_vivo_parser_result.json"
    summary_path = scanner_job_dir(job_id) / "scan_result_summary.json"
    data = json.loads(full_path.read_text(encoding="utf-8")) if full_path.exists() else {}
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    return {"job_id": job_id, "data": data, "summary": summary}


def cleanup_storage(retention_days: int | None = None, dry_run: bool = True) -> dict:
    days = RETENTION_DAYS if retention_days is None else max(int(retention_days), 0)
    cutoff = time.time() - (days * 24 * 60 * 60)
    roots = [UPLOADS, OUTPUT]
    deleted: list[str] = []
    candidates: list[str] = []
    bytes_reclaimable = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.iterdir():
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime > cutoff:
                continue
            candidates.append(str(path))
            if path.is_dir():
                files = [item for item in path.rglob("*") if item.is_file()]
                bytes_reclaimable += sum(item.stat().st_size for item in files if item.exists())
                if not dry_run:
                    shutil.rmtree(path, ignore_errors=True)
                    deleted.append(str(path))
            else:
                bytes_reclaimable += path.stat().st_size
                if not dry_run:
                    path.unlink(missing_ok=True)
                    deleted.append(str(path))
    return {
        "ok": True,
        "dry_run": dry_run,
        "retention_days": days,
        "candidate_count": len(candidates),
        "deleted_count": len(deleted),
        "bytes_reclaimable": bytes_reclaimable,
        "candidates": candidates[:200],
        "deleted": deleted[:200],
    }


def admin_backend_summary() -> dict:
    latest = latest_full_scan_result()
    data = latest.get("data", {})
    summary = latest.get("summary", {})
    pre_output = data.get("pre_output_verification", {})
    packet_system = data.get("cfpb_packet_system", {})
    security = packet_system.get("security", {})
    return {
        "service": "credit-vivo-founder-admin-backend",
        "api_version": SCANNER_API_VERSION,
        "latest_job_id": latest.get("job_id"),
        "scanner_version": data.get("version") or summary.get("admin_summary", {}).get("version"),
        "review_items": len(data.get("tradelines", [])) or summary.get("review_items_count", 0),
        "possible_issues": len(data.get("issues", [])) or summary.get("issues_count", 0),
        "draft_letter_queue": len(data.get("recommended_letter_queue", [])),
        "packet_count": len(packet_system.get("dispute_packets", [])),
        "document_vault_records": len(packet_system.get("document_vault", {}).get("records", [])),
        "pre_output_status": pre_output.get("status", "not_available"),
        "scanner_skills": [row.get("skill_id", "") for row in data.get("scanner_skill_map", [])],
        "paid_ai_used": bool(data.get("paid_ai_used") or summary.get("paid_ai_used")),
        "automatic_mailing_enabled": bool(security.get("automatic_mailing_enabled", False)),
        "automatic_complaint_submission_enabled": bool(security.get("automatic_complaint_submission_enabled", False)),
        "approval_required": True,
        "customer_admin_split": True,
        "local_backend_only": True,
    }


def creditvivo_operating_architecture(summary: dict | None = None) -> dict:
    summary = summary or admin_backend_summary()
    return {
        "service": "credit-vivo-operating-architecture",
        "version": SCANNER_API_VERSION,
        "operating_model": "founder_admin_control_center",
        "principles": [
            "Founder/admin visibility first.",
            "Customer-facing surfaces show plain-English status, not raw backend internals.",
            "Evidence and approval gates are required before dispute prep moves forward.",
            "Draft, review, approve, then prepare; this backend does not auto-send.",
        ],
        "domains": [
            {
                "domain_id": "scanner_engine",
                "name": "Scanner and Report Intelligence",
                "owner_role": "admin",
                "status": "active",
                "tools": ["Scanner Test Hub", "Findings Review", "3-Bureau Compare", "Workbook Export"],
                "data": ["Uploaded PDFs", "Parser Result JSON", "Tradelines CSV", "Review Issues CSV", "Workbook Output"],
                "skills": ["Native parser", "Report ingestion", "Issue detection", "Cross-bureau matching", "Evidence snippets", "Confidence scoring"],
                "resources": ["rules/", "credit_vivo_proprietary_engine.py", "report_ingestion.py", "output/{scan_id}/"],
                "workflow": "upload_report -> extract_text -> normalize_tradelines -> detect_possible_issues -> verify_output -> founder_review",
                "guardrail": "Consumer credit reports only; draft review data only.",
            },
            {
                "domain_id": "letter_lifecycle",
                "name": "Letter and Packet Lifecycle",
                "owner_role": "admin_compliance",
                "status": "active",
                "tools": ["Admin Letters", "Customer Letters Preview", "Document Vault", "Packet Attachments"],
                "data": ["Draft letter queue", "Packet checklist", "Document vault manifest", "Lob tracking placeholders"],
                "skills": ["Letter type recommendation", "Draft packet preparation", "Approval gating", "Compliance block reasons"],
                "resources": ["letter_lifecycle.py", "cfpb_packet_vault.py", "document_vault/"],
                "workflow": "possible_issue -> recommended_letter_type -> draft_packet -> customer_approval -> admin_review -> compliance_review -> lob_ready_packet",
                "guardrail": "No mail, dispute, complaint, or legal escalation is sent from scanner output.",
            },
            {
                "domain_id": "client_portal",
                "name": "Customer Portal and Approval Experience",
                "owner_role": "customer_success",
                "status": "planned_backend_preview",
                "tools": ["Customer Documents Preview", "Customer Letters Preview"],
                "data": ["Customer summary", "Document status", "Letter approval status", "Next steps"],
                "skills": ["Plain-English summaries", "Approval prompts", "Document request status"],
                "resources": ["dashboard documents routes", "dashboard letters routes"],
                "workflow": "admin_reviewed_output -> customer_plain_english_view -> customer_approval_or_question -> admin_queue_update",
                "guardrail": "Customers should not see unsupported guarantees or raw parser internals.",
            },
            {
                "domain_id": "growth_engine",
                "name": "Growth, Leads, and Attribution",
                "owner_role": "founder",
                "status": "active_draft_only",
                "tools": ["Growth Admin", "Growth AI Brief", "Lead Score", "Campaign Build", "Compliance Check", "Revenue Attribution"],
                "data": ["Lead signals", "Campaign drafts", "Consent logs", "Partner referrals", "Revenue attribution", "Event logs"],
                "skills": ["Lead scoring", "Campaign drafting", "Compliance phrase checks", "Referral tracking", "Attribution review"],
                "resources": ["growth_ai.py", "lead_intelligence_engine.py", "campaign_builder_engine.py", "consent_log_engine.py"],
                "workflow": "capture_signal -> score_lead -> draft_campaign_or_outreach -> compliance_check -> founder_approval -> manual_export",
                "guardrail": "Draft-only; no automatic outreach or paid ad launch.",
            },
            {
                "domain_id": "market_ai_studio",
                "name": "Market AI Studio and Creative Ops",
                "owner_role": "founder_marketing",
                "status": "active_draft_only",
                "tools": ["Market AI Studio", "Assets", "Images", "Videos", "Campaigns", "Review", "Approved"],
                "data": ["Creative assets", "Storyboard drafts", "Scripts", "Compliance flags", "Brand settings"],
                "skills": ["Creative planning", "Script drafting", "Storyboard drafting", "Marketing compliance review"],
                "resources": ["market_ai_studio.py", "market_ai.py", "lib/market/complianceRules.js"],
                "workflow": "brief -> draft_asset -> compliance_check -> founder_review -> approved_library",
                "guardrail": "No unsafe claims; approved means ready for human publishing review, not auto-published.",
            },
            {
                "domain_id": "operator_command",
                "name": "Operator AI and Vivo Command",
                "owner_role": "founder_ops",
                "status": "active",
                "tools": ["Operator AI Brief", "Vivo Command Brief", "AI Operating System", "AI Tracking Map", "Live Command"],
                "data": ["Operating events", "Role capabilities", "Tracking map", "Growth snapshot"],
                "skills": ["Operations summary", "Role coordination", "Event review", "Priority recommendations"],
                "resources": ["operator_ai.py", "vivo_command_ai.py", "ai_operating_system.py", "ai_tracking_map.py"],
                "workflow": "events -> summary -> role_brief -> founder_decision -> approved_task",
                "guardrail": "AI can recommend and organize; founder/admin approval controls execution.",
            },
            {
                "domain_id": "admin_security_compliance",
                "name": "Admin, Security, and Compliance Controls",
                "owner_role": "founder",
                "status": "local_ready_production_blocked",
                "tools": ["Founder Login", "Admin Users", "Backend Inventory", "Production Readiness", "Health"],
                "data": ["Session cookie", "Provisioned user log", "Readiness gates", "Compliance guard rules"],
                "skills": ["Role separation", "Route protection", "Launch blocking", "Safe language checks"],
                "resources": ["admin_users.py", "rules/compliance_guard_rules.yml", "ENV_EXAMPLE.env", "render.yaml"],
                "workflow": "login -> review_inventory -> inspect_readiness -> configure_prod_auth_storage_encryption -> launch_review",
                "guardrail": "Production stays blocked until auth, encryption, durable storage, setup token, and audit logging are configured.",
            },
            {
                "domain_id": "staging_uat",
                "name": "Staging UAT and Safe-Mode Testing",
                "owner_role": "founder",
                "status": "active_controlled_testing",
                "tools": ["Staging Signup", "Staging Checkout", "UAT Smoke Test", "Synthetic Report Fixtures"],
                "data": ["Seeded test users", "Synthetic report fixture placeholders", "Safe-mode environment flags"],
                "skills": ["Production-like route testing", "No-real-data validation", "Payment/email off-mode checks"],
                "resources": [".env.staging.example", "tests/fixtures/staging-users.json", "tests/fixtures/synthetic-reports/", "scripts/uat-smoke.mjs"],
                "workflow": "staging_env -> seeded_test_user -> synthetic_report -> member_portal_gate -> admin_certification_review",
                "guardrail": "No real customer data, no real payments, no real emails, no external sends.",
            },
        ],
        "shared_resources": [
            {"name": "Rules Library", "path": "scanner_backend/rules/", "type": "yaml_rules", "status": "active"},
            {"name": "Project Docs", "path": "docs/", "type": "handoff_and_roadmap_docs", "status": "active"},
            {"name": "Backend Tests", "path": "scanner_backend/tests/", "type": "verification_suite", "status": "active"},
            {"name": "Render Blueprint", "path": "render.yaml", "type": "deployment_config", "status": "configured_for_review"},
            {"name": "Environment Example", "path": "scanner_backend/ENV_EXAMPLE.env", "type": "production_env_template", "status": "active"},
            {"name": "Staging UAT Checklist", "path": "docs/staging/STAGING_UAT_CHECKLIST.md", "type": "controlled_testing_checklist", "status": "active"},
        ],
        "integrations": [
            {"name": "creditvivo.com", "status": "link_placeholder", "needed_for_live": "Route /founder or app.creditvivo.com to this backend behind production auth."},
            {"name": "Production Auth", "status": "missing", "needed_for_live": "Supabase, Auth0, Clerk, or equivalent with 2FA."},
            {"name": "Durable Encrypted Storage", "status": "missing_local", "needed_for_live": "Encrypted storage for reports, raw text, workbooks, packets, and audit logs."},
            {"name": "Mail/Lob", "status": "not_integrated", "needed_for_live": "Only prepare packets after approval; sending must remain a separate approved production workflow."},
            {"name": "Paid AI APIs", "status": "not_required", "needed_for_live": "Native scanner remains default; no paid AI dependency added."},
        ],
        "permissions": [
            {"role": "Founder", "access": "All domains, readiness, architecture, growth, market, scanner outputs.", "production_requirement": "2FA and audit logs."},
            {"role": "Admin", "access": "Scanner jobs, findings, documents, letters, customer status support.", "production_requirement": "Role-scoped login."},
            {"role": "Compliance", "access": "Review queues, blocked language, approval gates, packet readiness.", "production_requirement": "Review/audit trail."},
            {"role": "Customer", "access": "Plain-English summaries, document status, approval prompts.", "production_requirement": "Customer auth and consent controls."},
        ],
        "summary_counts": {
            "domains": 8,
            "latest_job_id": summary.get("latest_job_id"),
            "possible_issues": summary.get("possible_issues"),
            "draft_letter_queue": summary.get("draft_letter_queue"),
        },
    }


def founder_backend_inventory(summary: dict | None = None) -> dict:
    summary = summary or admin_backend_summary()
    architecture = creditvivo_operating_architecture(summary)
    job_id = summary.get("latest_job_id") or ""
    job_dir = scanner_job_dir(job_id) if job_id else None

    def present(path: Path | None) -> str:
        return "Available" if path and path.exists() else "Missing"

    data_sources = [
        {
            "name": "Latest Scanner Job",
            "status": "Available" if job_id else "Missing",
            "location": job_id or "Run a scanner job first.",
            "use": "Current default backend output for founder review.",
        },
        {
            "name": "Parser Result JSON",
            "status": present(job_dir / "credit_vivo_parser_result.json" if job_dir else None),
            "location": f"output/{job_id}/credit_vivo_parser_result.json" if job_id else "",
            "use": "Raw structured scanner output used by dashboards and workbook exports.",
        },
        {
            "name": "Desktop Workbook Output",
            "status": present(job_dir / "credit_vivo_desktop_scanner_output.xlsx" if job_dir else None),
            "location": f"/scanner/result/{job_id}/download/workbook.xlsx" if job_id else "",
            "use": "Founder/admin workbook for inspection and QA.",
        },
        {
            "name": "Review Issues CSV",
            "status": present(job_dir / "review_issues.csv" if job_dir else None),
            "location": f"/scanner/result/{job_id}/download/issues.csv" if job_id else "",
            "use": "Possible report errors and review findings.",
        },
        {
            "name": "Tradelines CSV",
            "status": present(job_dir / "tradelines.csv" if job_dir else None),
            "location": f"/scanner/result/{job_id}/download/tradelines.csv" if job_id else "",
            "use": "Normalized consumer credit report tradeline data.",
        },
        {
            "name": "Document Vault Manifest",
            "status": present(job_dir / "document_vault" / "document_vault_manifest.json" if job_dir else None),
            "location": f"/scanner/result/{job_id}/download/vault.json" if job_id else "",
            "use": "Server-side evidence/document inventory.",
        },
        {
            "name": "Growth/Event Logs",
            "status": "Available" if EVENT_LOG.parent.exists() and GROWTH_ROOT.exists() else "Review",
            "location": str(GROWTH_ROOT),
            "use": "Local founder-side growth, consent, approval, and attribution logs.",
        },
    ]
    tools = [
        {"name": "Scanner Test Hub", "route": "/scanner", "status": "Connected", "use": "Upload/test consumer credit reports."},
        {"name": "Findings Review", "route": "/findings", "status": "Connected", "use": "Review possible report errors."},
        {"name": "3-Bureau Compare", "route": "/findings/compare", "status": "Connected", "use": "Compare bureau fields and evidence."},
        {"name": "Letter Queue", "route": "/admin/letters", "status": "Connected", "use": "Draft-only letter packet review."},
        {"name": "Document Vault", "route": "/admin/documents", "status": "Connected", "use": "Admin evidence/document manifest review."},
        {"name": "Customer Preview", "route": "/dashboard/letters", "status": "Connected", "use": "Customer-facing approval/status preview."},
        {"name": "Growth Admin", "route": "/admin/growth/dashboard", "status": "Connected", "use": "Founder-side growth and attribution controls."},
        {"name": "Market AI Studio", "route": "/market-ai", "status": "Connected", "use": "Draft campaign and market asset workspace."},
        {"name": "Production Readiness", "route": "/admin/production-readiness", "status": "Connected", "use": "Launch gates and missing production setup."},
        {"name": "Backend Summary JSON", "route": "/admin/backend-summary", "status": "Connected", "use": "Machine-readable backend status."},
        {"name": "Backend Inventory JSON", "route": "/admin/backend-inventory", "status": "Connected", "use": "Machine-readable data, tools, and skills inventory."},
        {"name": "Operating Architecture JSON", "route": "/admin/operating-architecture", "status": "Connected", "use": "Machine-readable all-domain architecture map."},
        {"name": "FastAPI Docs", "route": "/docs", "status": "Connected", "use": "Developer route reference for testing."},
    ]
    skills = [
        {"name": "Native Credit Vivo Parser", "status": "Default", "use": "Consumer credit report parsing without paid AI."},
        {"name": "Report Ingestion Layer", "status": "Available", "use": "Normalizes uploaded PDFs now and prepares future text/JSON/API input."},
        {"name": "Tradeline Normalization", "status": "Available", "use": "Maps report inputs into the current review schema."},
        {"name": "Evidence Snippets", "status": "Available", "use": "Keeps supporting text for plain-English review."},
        {"name": "Confidence Scoring", "status": "Available", "use": "Flags stronger and weaker findings for review."},
        {"name": "Issue Detection", "status": "Available", "use": "Finds possible report errors and inconsistencies."},
        {"name": "Cross-Bureau Matching", "status": "Available", "use": "Connects matching accounts across Experian, Equifax, and TransUnion."},
        {"name": "3-Bureau Comparison", "status": "Available", "use": "Shows bureau-by-bureau differences before output."},
        {"name": "Workbook Output QA", "status": "Available", "use": "Checks output against backend workbook expectations."},
        {"name": "Customer Summary", "status": "Available", "use": "Plain-English customer-facing review content."},
        {"name": "Admin Summary", "status": "Available", "use": "Founder/admin review counts, status, and next steps."},
        {"name": "Letter Lifecycle", "status": "Approval-Gated", "use": "Creates draft-only packets that require customer/admin/compliance review."},
        {"name": "Compliance Guardrails", "status": "Enabled", "use": "Blocks automatic sending and unsafe claim patterns."},
        {"name": "Growth/Market Tools", "status": "Draft-Only", "use": "Founder-side growth ideas, lead scoring, compliance checks, and approvals."},
    ]
    output_skills = [
        {"name": skill, "status": "Output Enabled", "use": "Declared by latest scanner output."}
        for skill in summary.get("scanner_skills", [])
    ]
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
        "summary": summary,
        "architecture": architecture,
        "data_sources": data_sources,
        "tools": tools,
        "skills": skills + output_skills,
        "guardrails": [
            "Draft review data only.",
            "Customer approval, admin review, and compliance review are required before dispute prep moves forward.",
            "No automatic mailing, complaints, legal escalation, or guaranteed outcomes.",
            "Credit Vivo is not a law firm and does not provide legal advice.",
        ],
    }


def production_readiness_checks(summary: dict | None = None) -> dict:
    summary = summary or admin_backend_summary()
    email_config = email_safety_config()
    staging_config = staging_safety_config()

    def check(key: str, label: str, status: str, detail: str, severity: str = "info") -> dict:
        return {
            "key": key,
            "label": label,
            "status": status,
            "severity": severity,
            "detail": detail,
        }

    auth_configured = production_auth_configured()
    storage_dir = os.getenv("SCANNER_STORAGE_DIR", "")
    storage_external = bool(storage_dir) and not storage_dir.replace("\\", "/").startswith("/tmp/")
    encryption_configured = encryption_ready()
    admin_setup_token = bool(os.getenv("ADMIN_SETUP_TOKEN"))
    session_secret_configured = bool(os.getenv("ADMIN_SESSION_SECRET"))
    docs_locked = is_production() or os.getenv("SCANNER_PROTECT_DOCS", "").lower() == "true"
    scanner_shell_locked = production_scanner_shell_protected()
    latest_job_ready = bool(summary.get("latest_job_id") and summary.get("pre_output_status") in {"pass", "pass_with_review"})
    automatic_actions_disabled = not summary.get("automatic_mailing_enabled") and not summary.get("automatic_complaint_submission_enabled")
    email_actions_disabled = (
        email_config["provider"] == "disabled"
        and not email_config["email_sending_enabled"]
        and not email_config["marketing_emails_enabled"]
        and not email_config["dispute_email_auto_send_enabled"]
    )
    unsafe_staging_flags = [
        staging_config["allow_real_customer_data"],
        staging_config["external_calls_enabled"],
        staging_config["auto_send_enabled"],
        staging_config["customer_final_result_without_qa"],
        staging_config["letters_without_verified_issue"],
        staging_config["complaints_without_approval"],
        staging_config["attorney_escalation_without_approval"],
    ]

    checks = [
        check(
            "auth_provider",
            "Production login provider",
            "pass" if auth_configured else "blocker",
            "Auth provider environment is configured." if auth_configured else "Configure Supabase, Auth0, Clerk, or another production auth provider before launch.",
            "blocker",
        ),
        check(
            "session_secret",
            "Session secret",
            "pass" if session_secret_configured or not is_production() else "blocker",
            "ADMIN_SESSION_SECRET is configured." if session_secret_configured else "Local generated session secret is allowed only outside production.",
            "blocker",
        ),
        check(
            "admin_setup_token",
            "Admin setup token",
            "pass" if admin_setup_token else "blocker",
            "ADMIN_SETUP_TOKEN is configured." if admin_setup_token else "Set ADMIN_SETUP_TOKEN before allowing admin user provisioning outside local testing.",
            "blocker",
        ),
        check(
            "role_model",
            "Role separation",
            "pass" if summary.get("customer_admin_split") else "blocker",
            "Customer, admin, founder, and compliance surfaces are separated in the backend hub.",
            "blocker",
        ),
        check(
            "scanner_latest_job",
            "Completed scanner job",
            "pass" if latest_job_ready else "review",
            f"Latest completed scanner job: {summary.get('latest_job_id')} with status {summary.get('pre_output_status')}." if latest_job_ready else "Run a completed scanner job with workbook output before launch review.",
            "high",
        ),
        check(
            "automatic_actions",
            "Automatic sending disabled",
            "pass" if automatic_actions_disabled else "blocker",
            "Automatic mailing and complaint submission are disabled." if automatic_actions_disabled else "Disable automatic mailing and complaint submission before launch.",
            "blocker",
        ),
        check(
            "approval_gates",
            "Approval gates",
            "pass" if summary.get("approval_required") else "blocker",
            "Customer approval and admin review remain required before action.",
            "blocker",
        ),
        check(
            "storage",
            "Production storage",
            "pass" if storage_external else "review",
            "SCANNER_STORAGE_DIR is configured outside temporary storage." if storage_external else "Temporary/local storage is active. Configure durable encrypted production storage before launch.",
            "high",
        ),
        check(
            "encryption",
            "Sensitive data encryption",
            "pass" if encryption_configured else "blocker",
            "Storage encryption support is explicitly enabled with a long key." if encryption_configured else "Configure actual encryption/key management for reports, IDs, documents, and raw text before launch.",
            "blocker",
        ),
        check(
            "api_docs",
            "API docs exposure",
            "pass" if docs_locked else "review",
            "FastAPI docs/OpenAPI are disabled or protected in production mode." if docs_locked else "Protect /docs and /openapi.json before production.",
            "high",
        ),
        check(
            "scanner_shell_auth",
            "Scanner shell login",
            "pass" if scanner_shell_locked else "review",
            "Scanner upload page requires login." if scanner_shell_locked else "Public scanner shell is local/demo only. Require login before production customer testing.",
            "high",
        ),
        check(
            "rate_limits",
            "Basic rate limits",
            "pass" if RATE_LIMIT_MAX_LOGIN > 0 and RATE_LIMIT_MAX_UPLOAD > 0 else "blocker",
            "Login, upload, and admin API rate limit buckets are configured.",
            "high",
        ),
        check(
            "paid_ai",
            "Paid AI dependency",
            "pass" if not summary.get("paid_ai_used") else "review",
            "Native parser remains default; paid AI is not required.",
            "medium",
        ),
        check(
            "email_sending",
            "Email sending disabled",
            "pass" if email_actions_disabled else "blocker",
            "Email provider is disabled and marketing/dispute auto-send flags are off." if email_actions_disabled else "Disable email provider, marketing emails, and dispute email auto-send before launch certification.",
            "blocker",
        ),
        check(
            "staging_safe_mode",
            "Staging safe mode",
            "pass" if not staging_config["is_staging"] or (staging_config["synthetic_reports_only"] and not any(unsafe_staging_flags)) else "blocker",
            "Staging uses synthetic data, no real customer data, no external calls, and no auto-send." if staging_config["is_staging"] else "Not running in staging mode.",
            "blocker",
        ),
        check(
            "audit_logs",
            "Audit trails",
            "pass" if AUDIT_LOG.parent.exists() else "review",
            "Security audit log path is present." if AUDIT_LOG.parent.exists() else "Configure durable production audit logging before launch.",
            "high",
        ),
    ]
    blockers = [item for item in checks if item["status"] == "blocker"]
    review = [item for item in checks if item["status"] == "review"]
    return {
        "ready_for_production": not blockers,
        "status": "blocked" if blockers else "review_needed" if review else "ready",
        "blocker_count": len(blockers),
        "review_count": len(review),
        "checks": checks,
    }


def backend_production_certification(summary: dict | None = None) -> dict:
    summary = summary or admin_backend_summary()
    readiness = production_readiness_checks(summary)
    architecture = creditvivo_operating_architecture(summary)
    email_config = email_safety_config()
    staging_config = staging_safety_config()
    blocker_keys = {item["key"] for item in readiness.get("checks", []) if item.get("status") == "blocker"}
    review_keys = {item["key"] for item in readiness.get("checks", []) if item.get("status") == "review"}

    def component(name: str, route: str, status: str, detail: str, blockers: list[str] | None = None) -> dict:
        return {
            "name": name,
            "route": route,
            "status": status,
            "detail": detail,
            "blockers": blockers or [],
        }

    live_blockers = sorted(blocker_keys | review_keys)
    safe_defaults_pass = (
        not WRITE_RAW_TEXT
        and not RETAIN_UPLOADS
        and production_scanner_shell_protected()
        and api_docs_protected()
        and not summary.get("paid_ai_used")
        and not summary.get("automatic_mailing_enabled")
        and not summary.get("automatic_complaint_submission_enabled")
        and summary.get("approval_required")
        and email_config["provider"] == "disabled"
        and not email_config["email_sending_enabled"]
        and not email_config["marketing_emails_enabled"]
        and not email_config["dispute_email_auto_send_enabled"]
        and not staging_config["external_calls_enabled"]
        and not staging_config["auto_send_enabled"]
        and not staging_config["customer_final_result_without_qa"]
        and not staging_config["letters_without_verified_issue"]
        and not staging_config["complaints_without_approval"]
        and not staging_config["attorney_escalation_without_approval"]
    )

    components = [
        component(
            "Founder/Admin Command Center",
            "/admin",
            "certified_controlled_testing",
            "Founder workflow, route menu, production readiness, inventory, and guardrails are available behind founder login.",
        ),
        component(
            "Scanner Engine",
            "/scanner",
            "certified_controlled_testing" if production_scanner_shell_protected() and not WRITE_RAW_TEXT else "needs_review",
            "Native parser remains default. Scanner shell requires login by default. Raw text output is off by default.",
            [] if production_scanner_shell_protected() and not WRITE_RAW_TEXT else ["scanner_shell_auth", "raw_text_storage"],
        ),
        component(
            "Letter Lifecycle",
            "/admin/letters",
            "certified_controlled_testing" if not summary.get("automatic_mailing_enabled") else "blocked",
            "Draft-only packets remain approval-gated. No automatic mailing is enabled.",
            [] if not summary.get("automatic_mailing_enabled") else ["automatic_actions"],
        ),
        component(
            "Document Vault",
            "/admin/documents",
            "certified_controlled_testing" if not RETAIN_UPLOADS else "needs_review",
            "Upload retention is off by default. Durable encrypted production storage is still required before live launch.",
            ["storage", "encryption"] if not encryption_ready() else [],
        ),
        component(
            "Member Portal Preview",
            "http://127.0.0.1:3000/member",
            "certified_safe_empty_state",
            "Demo/mock data is off by default and customer findings remain hidden until backend gates pass.",
        ),
        component(
            "Growth and Market Tools",
            "/admin/growth/dashboard",
            "certified_draft_only",
            "Growth and creative tools are draft/review surfaces only. No automatic outreach, ads, or publishing is enabled.",
        ),
        component(
            "API Docs",
            "/docs",
            "protected_by_default" if api_docs_protected() else "needs_review",
            "Developer route docs are protected by founder login by default.",
            [] if api_docs_protected() else ["api_docs"],
        ),
        component(
            "Production Email",
            "/contact",
            "certified_no_send_default" if email_config["provider"] == "disabled" and not email_config["email_sending_enabled"] else "blocked",
            "Production email structure is documented, contact routes use support/privacy/security addresses, and app email sending remains disabled by default.",
            [] if email_config["provider"] == "disabled" and not email_config["email_sending_enabled"] else ["email_sending"],
        ),
        component(
            "Staging UAT Safe Mode",
            "http://127.0.0.1:3000/signup",
            "certified_controlled_testing" if not staging_config["is_staging"] or (staging_config["synthetic_reports_only"] and not staging_config["allow_real_customer_data"]) else "blocked",
            "Staging flow is configured for synthetic reports, test payments, email off-mode, and no external calls.",
            [] if not staging_config["is_staging"] or (staging_config["synthetic_reports_only"] and not staging_config["allow_real_customer_data"]) else ["staging_safe_mode"],
        ),
        component(
            "Production Launch",
            "/admin/production-readiness",
            "blocked_for_live" if live_blockers else "ready_for_launch_review",
            "Live production launch remains blocked until all readiness gates pass. This certificate does not replace legal, security, or compliance review.",
            live_blockers,
        ),
    ]
    return {
        "service": "credit-vivo-backend-production-certification",
        "version": SCANNER_API_VERSION,
        "certificate_scope": "controlled_local_backend_testing",
        "live_production_certified": False if live_blockers else True,
        "controlled_testing_certified": safe_defaults_pass,
        "safe_defaults": {
            "raw_text_storage": "off" if not WRITE_RAW_TEXT else "on",
            "upload_retention": "off" if not RETAIN_UPLOADS else "on",
            "scanner_shell_login_required": production_scanner_shell_protected(),
            "api_docs_protected": api_docs_protected(),
            "paid_ai": "off" if not summary.get("paid_ai_used") else "on",
            "automatic_mailing": "off" if not summary.get("automatic_mailing_enabled") else "on",
            "automatic_complaints": "off" if not summary.get("automatic_complaint_submission_enabled") else "on",
            "approval_required": bool(summary.get("approval_required")),
            "email_provider": email_config["provider"],
            "email_sending": "off" if not email_config["email_sending_enabled"] else "on",
            "marketing_emails": "off" if not email_config["marketing_emails_enabled"] else "on",
            "dispute_email_auto_send": "off" if not email_config["dispute_email_auto_send_enabled"] else "on",
            "staging_safe_mode": staging_config["is_staging"],
            "synthetic_reports_only": staging_config["synthetic_reports_only"],
            "real_customer_data": "blocked" if not staging_config["allow_real_customer_data"] else "allowed",
            "payments_mode": staging_config["payments_mode"],
            "stripe_mode": staging_config["stripe_mode"],
            "external_calls": "off" if not staging_config["external_calls_enabled"] else "on",
            "auto_send": "off" if not staging_config["auto_send_enabled"] else "on",
            "customer_final_result_without_qa": "off" if not staging_config["customer_final_result_without_qa"] else "on",
            "letters_without_verified_issue": "off" if not staging_config["letters_without_verified_issue"] else "on",
            "complaints_without_approval": "off" if not staging_config["complaints_without_approval"] else "on",
            "attorney_escalation_without_approval": "off" if not staging_config["attorney_escalation_without_approval"] else "on",
        },
        "components": components,
        "production_blockers": live_blockers,
        "domains": [domain.get("name", "") for domain in architecture.get("domains", [])],
        "disclaimer": "Production certification here means controlled backend readiness checks. Live launch still requires production auth, 2FA, encrypted durable storage, real secrets, audit retention, and legal/compliance review.",
    }


def packet_page_html(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ margin:0; font-family: Inter, Segoe UI, Arial, sans-serif; background:#f6f7f9; color:#17202a; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 28px 18px 44px; }}
    nav {{ display:flex; flex-wrap:wrap; gap:10px; margin: 0 0 18px; }}
    nav a, .button {{ color:#0d5c75; border:1px solid #9cc5d1; background:#f3fbfd; border-radius:8px; padding:8px 10px; text-decoration:none; font-weight:700; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    p {{ color:#56616f; line-height:1.5; }}
    .panel {{ background:#fff; border:1px solid #d8dde6; border-radius:8px; padding:18px; margin-top:14px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; background:#fff; }}
    th, td {{ border:1px solid #e2e7ef; padding:8px; text-align:left; vertical-align:top; }}
    th {{ background:#d1fae5; color:#064e3b; }}
    .guardrail {{ border-left:4px solid #0d5c75; background:#eef8fb; padding:12px; margin:14px 0; color:#344054; }}
    .status {{ display:inline-block; border-radius:999px; padding:4px 8px; background:#fff7ed; color:#9a3412; font-weight:700; }}
  </style>
</head>
<body>
<main>
  <nav>
    <a href="/scanner">Scanner</a>
    <a href="/findings">Findings</a>
    <a href="/findings/compare">3B Compare</a>
    <a href="/findings/letters">Letters</a>
    <a href="/dashboard/documents">Customer Documents</a>
    <a href="/dashboard/letters">Customer Letters</a>
    <a href="/admin/documents">Admin Documents</a>
    <a href="/admin/letters">Admin Letters</a>
  </nav>
  <h1>{escape(title)}</h1>
  <div class="guardrail">Draft review data only. Customer e-sign approval and admin review are required before any dispute, mailing, complaint, Lob mailing, or escalation.</div>
  {body}
</main>
</body>
</html>
""")


def render_table(headers: list[str], rows: list[list[object]], empty: str = "No records yet.") -> str:
    if not rows:
        return f"<p>{escape(empty)}</p>"
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{escape(str(value or ''))}</td>" for value in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


@app.get("/admin/login")
@app.get("/api/admin/login")
@app.get("/founder-login")
@app.get("/api/founder-login")
def admin_login_page():
    return admin_login_html()


@app.post("/admin/login")
@app.post("/api/admin/login")
@app.post("/founder-login")
@app.post("/api/founder-login")
async def admin_login_submit(username: str = Form(...), password: str = Form(...)):
    if not verify_admin_credentials(username, password):
        append_audit_event("admin_login", user=username.strip().lower(), outcome="failed")
        return admin_login_html("Login failed. Check the founder email and password.")
    append_audit_event("admin_login", user=username.strip().lower(), outcome="success")
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(
        "cv_admin_session",
        create_admin_session(username.strip().lower()),
        max_age=8 * 60 * 60,
        httponly=True,
        secure=os.getenv("SCANNER_ENVIRONMENT", "").lower() == "production",
        samesite="lax",
    )
    return response


@app.get("/admin/logout")
@app.get("/api/admin/logout")
@app.get("/founder-logout")
@app.get("/api/founder-logout")
def admin_logout():
    append_audit_event("admin_logout", outcome="success")
    response = RedirectResponse("/founder-login", status_code=303)
    response.delete_cookie("cv_admin_session")
    return response


@app.get("/admin")
@app.get("/api/admin")
@app.get("/founder")
@app.get("/api/founder")
def admin_backend_home(cv_admin_session: str | None = Cookie(default=None)):
    admin_user = read_admin_session(cv_admin_session)
    if not admin_user:
        return admin_login_redirect()
    summary = admin_backend_summary()
    readiness = production_readiness_checks(summary)
    inventory = founder_backend_inventory(summary)
    architecture = inventory.get("architecture", {})
    job_id = summary.get("latest_job_id") or ""
    quick_links = [
        ["Scanner Test Hub", "/scanner", "Run reports and download latest workbook output."],
        ["Latest Workbook", f"/scanner/result/{job_id}/download/workbook.xlsx" if job_id else "/scanner", "Open the latest generated backend workbook."],
        ["Findings Review", "/findings", "Review possible report errors and issue queue."],
        ["3B Compare", "/findings/compare", "Inspect bureau-by-bureau evidence and field differences."],
        ["Admin Letters", "/admin/letters", "Review draft-only packet queue and block reasons."],
        ["Admin Documents", "/admin/documents", "Review server-side document vault manifest."],
        ["Customer Letters Preview", "/dashboard/letters", "See what customer-facing letter status looks like."],
        ["Customer Documents Preview", "/dashboard/documents", "See customer-facing document status."],
        ["Growth Admin", "/admin/growth/dashboard", "Founder growth and attribution controls."],
        ["Market AI Studio", "/market-ai", "Creative, campaign, and market asset workspace."],
        ["Admin Users", "/admin/users/setup", "Owner setup endpoint for admin user provisioning."],
        ["Production Readiness", "/admin/production-readiness", "Launch gates, blockers, and production setup status."],
        ["Production Certificate", "/admin/production-certification", "Controlled-testing certification for backend components."],
        ["Backend Summary JSON", "/admin/backend-summary", "Machine-readable founder/admin backend status."],
        ["Backend Inventory JSON", "/admin/backend-inventory", "Machine-readable data, tools, and skills inventory."],
        ["Operating Architecture JSON", "/admin/operating-architecture", "All-domain tools, skills, resources, permissions, and integrations."],
        ["Health", "/health", "Runtime health and parser configuration."],
        ["API Docs", "/docs", "FastAPI route documentation."],
        ["CreditVivo.com", LIVE_CREDITVIVO_HOME_URL, "Open the live public site."],
        ["Live Dashboard", LIVE_CREDITVIVO_LOGIN_URL, "Open the live dashboard/login-style page."],
        ["Live Scan Page", LIVE_CREDITVIVO_SCAN_URL, "Open the live scan page."],
    ]
    metric_rows = [
        ["API Version", summary.get("api_version", ""), "Local backend runtime."],
        ["Latest Job", summary.get("latest_job_id") or "none", "Current default scanner output."],
        ["Scanner Version", summary.get("scanner_version") or "not available", "Parser result version."],
        ["Review Items", summary.get("review_items", 0), "Parsed tradelines/review items."],
        ["Possible Issues", summary.get("possible_issues", 0), "Possible report errors or inconsistencies."],
        ["Draft Letter Queue", summary.get("draft_letter_queue", 0), "Draft-only packets; not sent."],
        ["Document Vault Records", summary.get("document_vault_records", 0), "Server-side manifest records."],
        ["Pre-Output Status", summary.get("pre_output_status", ""), "Template/raw-data/skills verification result."],
        ["Paid AI Used", "Yes" if summary.get("paid_ai_used") else "No", "Native parser remains default."],
        ["Automatic Mailing", "Enabled" if summary.get("automatic_mailing_enabled") else "Disabled", "Must remain disabled until production approval."],
        ["Automatic Complaints", "Enabled" if summary.get("automatic_complaint_submission_enabled") else "Disabled", "Must remain disabled until production approval."],
    ]
    skills_rows = [
        [skill.get("name", ""), skill.get("status", ""), skill.get("use", "")]
        for skill in inventory.get("skills", [])
    ]
    data_rows = [
        [item.get("name", ""), item.get("status", ""), item.get("location", ""), item.get("use", "")]
        for item in inventory.get("data_sources", [])
    ]
    tool_rows = [
        [item.get("name", ""), item.get("status", ""), item.get("route", ""), item.get("use", "")]
        for item in inventory.get("tools", [])
    ]
    guardrail_rows = [[item] for item in inventory.get("guardrails", [])]
    domain_rows = [
        [
            domain.get("name", ""),
            domain.get("status", ""),
            domain.get("owner_role", ""),
            ", ".join(domain.get("tools", [])),
            ", ".join(domain.get("data", [])),
            ", ".join(domain.get("skills", [])),
            domain.get("guardrail", ""),
        ]
        for domain in architecture.get("domains", [])
    ]
    resource_rows = [
        [item.get("name", ""), item.get("path", ""), item.get("type", ""), item.get("status", "")]
        for item in architecture.get("shared_resources", [])
    ]
    integration_rows = [
        [item.get("name", ""), item.get("status", ""), item.get("needed_for_live", "")]
        for item in architecture.get("integrations", [])
    ]
    permission_rows = [
        [item.get("role", ""), item.get("access", ""), item.get("production_requirement", "")]
        for item in architecture.get("permissions", [])
    ]
    readiness_rows = [
        [
            item.get("label", ""),
            item.get("status", ""),
            item.get("severity", ""),
            item.get("detail", ""),
        ]
        for item in readiness.get("checks", [])
    ]
    role_rows = [
        ["Founder", "Full backend visibility, launch gates, scanner jobs, growth tools, and audit review.", "Production login + 2FA required before launch."],
        ["Admin", "Parser cleanup, findings, documents, letters, customer approval support.", "No automatic mail or complaint filing."],
        ["Compliance", "Language review, approval gates, blocked-phrase review, dispute packet readiness.", "Not legal advice; attorney review needed for legal questions."],
        ["Customer", "Plain-English summaries, document/letter status, approval prompts.", "No raw backend parser internals."],
    ]
    founder_action_links = [
        ["Run Scanner", "/scanner", "Upload/test reports", "primary"],
        ["Review Findings", "/findings", "Possible report errors", "primary"],
        ["Compare 3 Bureaus", "/findings/compare", "Evidence and differences", "primary"],
        ["Draft Letters", "/admin/letters", "Approval-gated queue", "primary"],
        ["Production Gates", "/admin/production-readiness", "Launch blockers", "warning"],
        ["Production Cert", "/admin/production-certification", "Backend component report", "warning"],
        ["Open Member Portal", "http://127.0.0.1:3000/member", "Customer-safe preview", "secondary"],
    ]
    founder_actions_html = "".join(
        f"""
        <a class="action-card {escape(style)}" target="{"_blank" if str(url).startswith("http") else "_self"}" rel="noopener" href="{escape(str(url))}">
          <span>{escape(label)}</span>
          <small>{escape(note)}</small>
        </a>
        """
        for label, url, note, style in founder_action_links
    )
    flow_steps = [
        ["1", "Scan", "Upload consumer credit reports and create verified backend output."],
        ["2", "Review", "Inspect possible report errors, evidence snippets, and cross-bureau differences."],
        ["3", "Prepare Drafts", "Create draft-only letter packets tied to documented scanner findings."],
        ["4", "Approve", "Customer approval, admin review, and compliance review must pass first."],
        ["5", "Packet Ready", "Only then prepare a Lob-ready packet. No mail is sent from this page."],
    ]
    flow_html = "".join(
        f"""
        <div class="flow-step">
          <strong>{escape(number)}</strong>
          <span>{escape(label)}</span>
          <small>{escape(note)}</small>
        </div>
        """
        for number, label, note in flow_steps
    )
    top_metrics = [
        ["Latest Job", summary.get("latest_job_id") or "None", "review" if summary.get("latest_job_id") else "blocked"],
        ["Possible Issues", summary.get("possible_issues", 0), "ready" if summary.get("possible_issues", 0) else "review"],
        ["Draft Queue", summary.get("draft_letter_queue", 0), "ready" if summary.get("draft_letter_queue", 0) else "review"],
        ["Production", readiness.get("status", "unknown").replace("_", " ").title(), "blocked" if readiness.get("blocker_count", 0) else "review"],
        ["Paid AI", "Off" if not summary.get("paid_ai_used") else "Review", "ready" if not summary.get("paid_ai_used") else "blocked"],
        ["Auto Send", "Off" if not summary.get("automatic_mailing_enabled") else "On", "ready" if not summary.get("automatic_mailing_enabled") else "blocked"],
    ]
    top_metrics_html = "".join(
        f"""
        <div class="metric-card {escape(state)}">
          <span>{escape(label)}</span>
          <strong>{escape(str(value))}</strong>
        </div>
        """
        for label, value, state in top_metrics
    )
    readiness_preview_rows = readiness.get("checks", [])[:6]
    readiness_preview_html = "".join(
        f"""
        <div class="gate-row {escape(str(item.get("status", "")))}">
          <span>{escape(str(item.get("label", "")))}</span>
          <strong>{escape(str(item.get("status", "")).replace("_", " ").title())}</strong>
          <small>{escape(str(item.get("detail", "")))}</small>
        </div>
        """
        for item in readiness_preview_rows
    )
    links_html = "".join(
        f"""
        <a class="button" target="{"_blank" if str(url).startswith("http") else "_self"}" rel="noopener" href="{escape(str(url))}">
          <strong>{escape(label)}</strong><span>{escape(note)}</span>
        </a>
        """
        for label, url, note in quick_links
    )
    body = f"""
    <style>
      :root {{ color-scheme: light; }}
      .founder-hero {{ background:linear-gradient(135deg,#07111f,#0b3f37); color:#fff; border-radius:10px; padding:24px; margin:16px 0; }}
      .founder-hero p {{ color:#d9f1ee; max-width:820px; }}
      .founder-hero .eyebrow {{ color:#8ee8d0; font-size:12px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
      .founder-hero h2 {{ margin:8px 0 10px; font-size:30px; line-height:1.12; }}
      .top-menu {{ position:sticky; top:0; z-index:3; background:#ffffffeb; backdrop-filter: blur(8px); border:1px solid #d8dde6; border-radius:10px; padding:10px; display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }}
      .top-menu a {{ color:#0f172a; background:#f8fafc; border:1px solid #d8dde6; border-radius:8px; padding:9px 11px; text-decoration:none; font-weight:800; }}
      .top-menu a:hover, .action-card:hover, .admin-grid .button:hover {{ transform:translateY(-1px); box-shadow:0 8px 18px rgba(15,23,42,.08); }}
      .metrics-strip {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:10px; margin:14px 0; }}
      .metric-card {{ border:1px solid #d8dde6; border-radius:8px; background:#fff; padding:14px; min-height:74px; }}
      .metric-card span {{ display:block; color:#56616f; font-size:12px; font-weight:800; text-transform:uppercase; }}
      .metric-card strong {{ display:block; margin-top:8px; color:#0f172a; font-size:20px; overflow-wrap:anywhere; line-height:1.2; }}
      .metric-card.ready {{ border-color:#a7f3d0; background:#f0fdf4; }}
      .metric-card.review {{ border-color:#fde68a; background:#fffbeb; }}
      .metric-card.blocked {{ border-color:#fed7aa; background:#fff7ed; }}
      .action-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-top:12px; }}
      .action-card {{ display:flex; flex-direction:column; justify-content:center; gap:6px; min-height:86px; border:1px solid #d8dde6; border-radius:8px; background:#fff; padding:16px; text-decoration:none; transition:.16s ease; }}
      .action-card span {{ color:#0f172a; font-weight:900; font-size:16px; }}
      .action-card small {{ color:#56616f; font-weight:700; line-height:1.35; }}
      .action-card.primary {{ border-color:#99f6e4; background:#f0fdfa; }}
      .action-card.warning {{ border-color:#fdba74; background:#fff7ed; }}
      .action-card.secondary {{ border-color:#bfdbfe; background:#eff6ff; }}
      .section-title {{ display:flex; align-items:flex-start; justify-content:space-between; gap:14px; margin:0 0 12px; }}
      .section-title h2 {{ margin:0; }}
      .section-title p {{ margin:2px 0 0; font-size:13px; }}
      .flow {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap:10px; }}
      .flow-step {{ border:1px solid #d8dde6; border-radius:8px; background:#fff; padding:14px; }}
      .flow-step strong {{ display:inline-flex; width:28px; height:28px; border-radius:999px; align-items:center; justify-content:center; background:#0f766e; color:#fff; }}
      .flow-step span {{ display:block; margin-top:10px; color:#0f172a; font-weight:900; }}
      .flow-step small {{ display:block; margin-top:6px; color:#56616f; line-height:1.35; }}
      .gate-list {{ display:grid; gap:8px; }}
      .gate-row {{ display:grid; grid-template-columns: minmax(170px, .7fr) minmax(90px, .35fr) 1.4fr; gap:10px; align-items:start; border:1px solid #e2e7ef; border-radius:8px; background:#fff; padding:10px; }}
      .gate-row span {{ font-weight:900; color:#0f172a; }}
      .gate-row strong {{ color:#334155; }}
      .gate-row small {{ color:#56616f; line-height:1.35; }}
      .gate-row.pass {{ background:#f0fdf4; border-color:#bbf7d0; }}
      .gate-row.review {{ background:#fffbeb; border-color:#fde68a; }}
      .gate-row.blocker {{ background:#fff7ed; border-color:#fed7aa; }}
      .admin-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:12px; margin-top:14px; }}
      .admin-grid .button {{ display:flex; flex-direction:column; gap:4px; min-height:74px; justify-content:center; }}
      .admin-grid span {{ color:#56616f; font-weight:500; line-height:1.35; }}
      .admin-alert {{ border-left:4px solid #9a3412; background:#fff7ed; color:#7c2d12; padding:12px; margin:14px 0; }}
      .admin-ready {{ border-left:4px solid #064e3b; background:#ecfdf5; color:#064e3b; padding:12px; margin:14px 0; }}
      .quiet-note {{ color:#64748b; font-size:13px; margin-top:10px; }}
      @media (max-width: 760px) {{
        .gate-row {{ grid-template-columns:1fr; }}
        .founder-hero h2 {{ font-size:24px; }}
      }}
    </style>
    <div class="top-menu" aria-label="Founder backend menu">
      <a href="#actions">Actions</a>
      <a href="#workflow">Workflow</a>
      <a href="#readiness">Readiness</a>
      <a href="/admin/production-certification">Cert</a>
      <a href="#inventory">Inventory</a>
      <a href="#apps">Apps</a>
      <a href="#guardrails">Guardrails</a>
      <a href="/founder-logout">Log out</a>
    </div>
    <section class="founder-hero">
      <div class="eyebrow">Founder Backend Command Center</div>
      <h2>Run the backend like an operating system, not a pile of links.</h2>
      <p>Use this hub to test the scanner, review possible report errors, inspect draft-only letter queues, check launch blockers, and open the customer-safe member portal preview.</p>
      <p>Signed in as <strong>{escape(admin_user.get("username", ""))}</strong> ({escape(admin_user.get("role", ""))}).</p>
    </section>
    <div class="admin-alert">Production status: {escape(readiness.get("status", "unknown"))}. Blockers: {readiness.get("blocker_count", 0)}. Review items: {readiness.get("review_count", 0)}.</div>
    <div class="admin-ready">Safe default: scanner output is draft review data only. Customer approval, admin review, and compliance review are required before any dispute prep moves forward.</div>
    <div class="metrics-strip">{top_metrics_html}</div>
    <div class="panel" id="actions">
      <div class="section-title">
        <div>
          <h2>Founder Next Actions</h2>
          <p>Most-used backend tasks, in plain English.</p>
        </div>
      </div>
      <div class="action-grid">{founder_actions_html}</div>
      <p class="quiet-note">Production-sensitive actions stay gated. This page helps you review and prepare; it does not send mail, file complaints, or make legal conclusions.</p>
    </div>
    <div class="panel" id="workflow">
      <div class="section-title">
        <div>
          <h2>Backend Workflow</h2>
          <p>The safe operating path from report scan to packet readiness.</p>
        </div>
      </div>
      <div class="flow">{flow_html}</div>
    </div>
    <div class="panel" id="readiness">
      <div class="section-title">
        <div>
          <h2>Production Readiness Snapshot</h2>
          <p>Top launch gates for founder review. Full details remain below.</p>
        </div>
        <a class="button" href="/admin/production-readiness">Open Full Readiness JSON</a>
      </div>
      <div class="gate-list">{readiness_preview_html}</div>
    </div>
    <div class="panel">
      <h2>Founder Metrics</h2>
      {render_table(["Metric", "Value", "Meaning"], metric_rows)}
    </div>
    <div class="panel" id="inventory">
      <h2>Backend Data Inventory</h2>
      {render_table(["Data", "Status", "Location", "Use"], data_rows)}
    </div>
    <div class="panel">
      <h2>Backend Tools</h2>
      {render_table(["Tool", "Status", "Route", "Use"], tool_rows)}
    </div>
    <div class="panel">
      <h2>Operating Domains</h2>
      {render_table(["Domain", "Status", "Owner", "Tools", "Data", "Skills", "Guardrail"], domain_rows)}
    </div>
    <div class="panel">
      <h2>Shared Resources</h2>
      {render_table(["Resource", "Path", "Type", "Status"], resource_rows)}
    </div>
    <div class="panel">
      <h2>Integrations</h2>
      {render_table(["Integration", "Status", "Needed For Live"], integration_rows)}
    </div>
    <div class="panel">
      <h2>Permissions Matrix</h2>
      {render_table(["Role", "Access", "Production Requirement"], permission_rows)}
    </div>
    <div class="panel">
      <h2>Production Readiness</h2>
      {render_table(["Gate", "Status", "Severity", "Detail"], readiness_rows)}
    </div>
    <div class="panel">
      <h2>Role Access Model</h2>
      {render_table(["Role", "Access", "Production Requirement"], role_rows)}
    </div>
    <div class="panel" id="apps">
      <h2>Backend Apps</h2>
      <div class="admin-grid">{links_html}</div>
    </div>
    <div class="panel">
      <h2>Scanner Skills</h2>
      {render_table(["Skill", "Status", "Use"], skills_rows)}
    </div>
    <div class="panel" id="guardrails">
      <h2>Compliance Guardrails</h2>
      {render_table(["Rule"], guardrail_rows)}
    </div>
    """
    return packet_page_html("Founder Admin Backend", body)


@app.get("/admin/backend-summary")
@app.get("/api/admin/backend-summary")
def admin_backend_summary_api(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    return JSONResponse({"ok": True, **admin_backend_summary()})


@app.get("/admin/backend-inventory")
@app.get("/api/admin/backend-inventory")
def admin_backend_inventory_api(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    return JSONResponse({"ok": True, **founder_backend_inventory()})


@app.get("/admin/operating-architecture")
@app.get("/api/admin/operating-architecture")
def admin_operating_architecture_api(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    return JSONResponse({"ok": True, **creditvivo_operating_architecture()})


@app.get("/admin/production-readiness")
@app.get("/api/admin/production-readiness")
def admin_production_readiness_api(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    summary = admin_backend_summary()
    return JSONResponse({"ok": True, "summary": summary, "production_readiness": production_readiness_checks(summary)})


@app.get("/admin/production-certification")
@app.get("/api/admin/production-certification")
def admin_production_certification_page(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return admin_login_redirect()
    certificate = backend_production_certification()
    readiness = production_readiness_checks()
    summary = admin_backend_summary()

    def cert_status_class(status: str) -> str:
        status_text = str(status).lower()
        if "certified" in status_text or "protected" in status_text or "ready" in status_text or status_text == "pass":
            return "cert-ok"
        if "review" in status_text or "no_send" in status_text or "safe_empty" in status_text:
            return "cert-review"
        return "cert-blocked"

    def cert_status_label(status: str) -> str:
        return str(status or "unknown").replace("_", " ").replace("-", " ").title()

    component_rows = [
        [
            item.get("name", ""),
            item.get("status", ""),
            item.get("route", ""),
            item.get("detail", ""),
            ", ".join(item.get("blockers", [])),
        ]
        for item in certificate.get("components", [])
    ]
    safe_rows = [[key.replace("_", " ").title(), value] for key, value in certificate.get("safe_defaults", {}).items()]
    blocker_rows = [[item] for item in certificate.get("production_blockers", [])]
    component_cards = "".join(
        f"""
        <article class="cert-card {cert_status_class(str(item.get("status", "")))}">
          <div class="cert-card-head">
            <h3>{escape(str(item.get("name", "")))}</h3>
            <span>{escape(cert_status_label(str(item.get("status", ""))))}</span>
          </div>
          <p>{escape(str(item.get("detail", "")))}</p>
          <a href="{escape(str(item.get("route", "#")))}">{escape(str(item.get("route", "")))}</a>
          {"<small>Blockers: " + escape(", ".join(item.get("blockers", []))) + "</small>" if item.get("blockers") else "<small>No component-specific blockers.</small>"}
        </article>
        """
        for item in certificate.get("components", [])
    )
    today_actions = [
        "Do not launch to live customers while production blockers remain.",
        "Set up real production auth with 2FA.",
        "Connect durable encrypted storage and key management.",
        "Verify Google Workspace MX, SPF, DKIM, and DMARC before email sending.",
        "Keep dispute, complaint, and email auto-send disabled until approved.",
    ]
    if certificate.get("controlled_testing_certified"):
        today_actions.insert(1, "Continue controlled founder/admin testing with safe defaults on.")
    today_actions_html = "".join(f"<li>{escape(action)}</li>" for action in today_actions)
    gate_cards = "".join(
        f"""
        <div class="gate-card {cert_status_class(str(item.get("status", "")))}">
          <strong>{escape(str(item.get("label", "")))}</strong>
          <span>{escape(cert_status_label(str(item.get("status", ""))))}</span>
          <p>{escape(str(item.get("detail", "")))}</p>
        </div>
        """
        for item in readiness.get("checks", [])
    )
    top_metrics = [
        ["Controlled Testing", "Certified" if certificate.get("controlled_testing_certified") else "Blocked", "cert-ok" if certificate.get("controlled_testing_certified") else "cert-blocked"],
        ["Live Production", "Certified" if certificate.get("live_production_certified") else "Blocked", "cert-ok" if certificate.get("live_production_certified") else "cert-blocked"],
        ["Blockers", readiness.get("blocker_count", 0), "cert-blocked" if readiness.get("blocker_count", 0) else "cert-ok"],
        ["Review Items", readiness.get("review_count", 0), "cert-review" if readiness.get("review_count", 0) else "cert-ok"],
        ["Possible Issues", summary.get("possible_issues", 0), "cert-review"],
        ["Draft Queue", summary.get("draft_letter_queue", 0), "cert-review"],
    ]
    metrics_html = "".join(
        f"""
        <div class="metric-tile {escape(style)}">
          <span>{escape(label)}</span>
          <strong>{escape(str(value))}</strong>
        </div>
        """
        for label, value, style in top_metrics
    )
    body = f"""
    <style>
      .cert-shell {{ display:grid; gap:16px; }}
      .cert-hero {{ border:1px solid #fecaca; background:#fff7ed; border-radius:8px; padding:22px; }}
      .cert-hero.ok {{ border-color:#bbf7d0; background:#f0fdf4; }}
      .cert-hero .eyebrow {{ color:#9a3412; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:.08em; }}
      .cert-hero.ok .eyebrow {{ color:#047857; }}
      .cert-hero h2 {{ margin:8px 0 6px; font-size:30px; line-height:1.1; color:#17202a; }}
      .metrics-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }}
      .metric-tile {{ border:1px solid #d8dde6; border-radius:8px; background:#fff; padding:14px; min-height:74px; }}
      .metric-tile span {{ display:block; color:#56616f; font-size:12px; font-weight:900; text-transform:uppercase; }}
      .metric-tile strong {{ display:block; margin-top:8px; font-size:20px; overflow-wrap:anywhere; }}
      .cert-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }}
      .cert-card, .gate-card {{ border:1px solid #d8dde6; border-radius:8px; background:#fff; padding:14px; }}
      .cert-card-head {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }}
      .cert-card h3 {{ margin:0; font-size:16px; }}
      .cert-card span, .gate-card span {{ border-radius:999px; padding:4px 8px; font-size:11px; font-weight:900; background:#f1f5f9; color:#334155; }}
      .cert-card p, .gate-card p {{ font-size:13px; margin:10px 0; }}
      .cert-card a {{ color:#0d5c75; font-weight:800; font-size:13px; text-decoration:none; }}
      .cert-card small {{ display:block; margin-top:8px; color:#64748b; line-height:1.35; }}
      .cert-ok {{ border-color:#bbf7d0; background:#f0fdf4; }}
      .cert-review {{ border-color:#fde68a; background:#fffbeb; }}
      .cert-blocked {{ border-color:#fed7aa; background:#fff7ed; }}
      .gate-card strong {{ display:block; color:#0f172a; }}
      .action-list {{ margin:0; padding-left:20px; color:#334155; line-height:1.6; }}
      .command-layout {{ display:grid; grid-template-columns: 1fr; gap:14px; }}
      @media (min-width: 1000px) {{
        .command-layout {{ grid-template-columns:1.1fr .9fr; }}
      }}
    </style>
    <div class="cert-shell">
      <section class="cert-hero {"ok" if certificate.get("live_production_certified") else ""}">
        <div class="eyebrow">Founder Command Center</div>
        <h2>{"Live production is certified." if certificate.get("live_production_certified") else "Credit Vivo is not live-production ready yet."}</h2>
        <p>{escape(str(certificate.get("disclaimer", "")))}</p>
      </section>
      <div class="metrics-grid">{metrics_html}</div>
      <div class="command-layout">
        <div class="panel">
          <h2>What Must Happen Next</h2>
          <ol class="action-list">{today_actions_html}</ol>
        </div>
        <div class="panel">
          <h2>Scanner Trust Snapshot</h2>
          <p>Latest job: <strong>{escape(str(summary.get("latest_job_id") or "None"))}</strong></p>
          <p>Pre-output verification: <strong>{escape(str(summary.get("pre_output_status") or "not available"))}</strong></p>
          <p>Native parser remains default. Paid AI remains off. Scanner output remains draft review data only.</p>
        </div>
      </div>
      <div class="panel">
        <h2>Backend Components</h2>
        <div class="cert-grid">{component_cards}</div>
      </div>
      <div class="panel">
        <h2>Production Gates</h2>
        <div class="cert-grid">{gate_cards}</div>
      </div>
    </div>
    <div class="panel">
      <h2>Certification Summary</h2>
      <p><strong>Scope:</strong> {escape(str(certificate.get("certificate_scope", "")))}</p>
      <p><strong>Controlled testing certified:</strong> {escape(str(certificate.get("controlled_testing_certified", False)))}</p>
      <p><strong>Live production certified:</strong> {escape(str(certificate.get("live_production_certified", False)))}</p>
      <div class="guardrail">{escape(str(certificate.get("disclaimer", "")))}</div>
    </div>
    <div class="panel">
      <h2>Safe Defaults Turned On</h2>
      {render_table(["Control", "Setting"], safe_rows)}
    </div>
    <div class="panel">
      <h2>Backend Components</h2>
      {render_table(["Component", "Status", "Route", "Detail", "Blockers"], component_rows)}
    </div>
    <div class="panel">
      <h2>Live Production Blockers</h2>
      {render_table(["Blocker"], blocker_rows, "No live production blockers detected.")}
    </div>
    """
    return packet_page_html("Credit Vivo Backend Production Certification", body)


@app.get("/admin/production-certification.json")
@app.get("/api/admin/production-certification.json")
def admin_production_certification_api(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    return JSONResponse({"ok": True, **backend_production_certification()})


@app.get("/admin/retention/cleanup")
@app.get("/api/admin/retention/cleanup")
def admin_retention_cleanup_preview(
    dry_run: bool = True,
    retention_days: int | None = None,
    cv_admin_session: str | None = Cookie(default=None),
):
    admin_user = read_admin_session(cv_admin_session)
    if not admin_user:
        return JSONResponse({"ok": False, "error": "admin_login_required", "login_url": "/admin/login"}, status_code=401)
    result = cleanup_storage(retention_days=retention_days, dry_run=dry_run)
    append_audit_event(
        "retention_cleanup",
        user=admin_user.get("username", ""),
        outcome="preview" if dry_run else "deleted",
        detail={"retention_days": result["retention_days"], "candidate_count": result["candidate_count"], "deleted_count": result["deleted_count"]},
    )
    return JSONResponse(result)


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
    request: Request,
    files: List[UploadFile] = File(...),
    use_ai_second_pass: bool = Form(default=False),
):
    """
    Accept one or more PDF credit reports.

    `use_ai_second_pass` is accepted for backwards compatibility but ignored.
    v18.1.7 uses Credit Vivo Proprietary Parser Engine only.
    """
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

    ingestion_items = []
    saved_files = []
    raw_text_files = []

    for index, file in enumerate(files, start=1):
        safe_name = Path(file.filename or f"report_{index}.pdf").name
        dest = job_dir / safe_name

        await save_pdf_upload(file, dest)

        try:
            text, pages = extract_pdf_text(dest)
            bureau = detect_bureau(safe_name, text)
            ingestion_items.append(build_uploaded_pdf_ingestion(
                source_filename=safe_name,
                text=text,
                bureau=bureau,
                pages=pages,
                chars=len(text),
            ))
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

    report_texts: Dict[str, dict] = normalize_ingestion_items(ingestion_items)
    parsed = parse_reports(report_texts)
    write_outputs(parsed, out_dir)
    data = result_to_dict(parsed)

    result = {
        "job_id": job_id,
        "files": saved_files,
        "raw_text_files": raw_text_files,
        "ai_second_pass": False,
        "paid_ai_used": False,
        "status": {
            "mode": "credit_vivo_proprietary_engine_v18_1_0",
            "message": "Parsed using Credit Vivo proprietary rule engine v18.1.7 with v9 forensic workbook layout, scanner skills map, approval-gated Lob-ready letter packets, pre-output template/raw-data verification, export QA cleanup flags, raw-exact field display, raw identity cleanup, CFPB packet/vault planning, and decision-readiness mapping. No paid AI API used."
        },
        "review_items_count": len(data["tradelines"]),
        "review_items_preview": data["tradelines"][:25],
        "issues_count": len(data["issues"]),
        "issues_preview": data["issues"][:25],
        "cross_bureau_groups": data["cross_bureau_groups"],
        "customer_message": data["customer_summary"]["message"],
        "customer_summary": data["customer_summary"],
        "decision_readiness": data.get("decision_readiness", []),
        "scanner_skill_map": data.get("scanner_skill_map", []),
        "admin_summary": data["admin_summary"],
        "letter_workflow": data.get("letter_workflow"),
        "recommended_letter_queue": data.get("recommended_letter_queue", []),
        "cfpb_packet_system": {
            "version": data.get("cfpb_packet_system", {}).get("version"),
            "packet_count": len(data.get("cfpb_packet_system", {}).get("dispute_packets", [])),
            "comparison_attachment_rows": len(data.get("cfpb_packet_system", {}).get("three_bureau_comparison_attachment", [])),
            "document_vault_records": len(data.get("cfpb_packet_system", {}).get("document_vault", {}).get("records", [])),
            "automatic_mailing_enabled": data.get("cfpb_packet_system", {}).get("security", {}).get("automatic_mailing_enabled", False),
            "automatic_complaint_submission_enabled": data.get("cfpb_packet_system", {}).get("security", {}).get("automatic_complaint_submission_enabled", False),
        },
        "fcra_review": data.get("fcra_review", []),
        "output_folder": str(out_dir),
    }

    (out_dir / "scan_result_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    if not RETAIN_UPLOADS:
        shutil.rmtree(job_dir, ignore_errors=True)

    append_audit_event("scanner_parse_completed", request=request, outcome="success", detail={"job_id": job_id, "file_count": len(saved_files)})
    return JSONResponse(result)


@app.get("/scanner")
@app.get("/api/scanner")
@app.get("/scan")
@app.get("/api/scan")
def scanner_upload_page():
    latest_downloads = scanner_download_links_html(latest_scanner_job_id())
    live_home_url = escape(LIVE_CREDITVIVO_HOME_URL)
    live_scan_url = escape(LIVE_CREDITVIVO_SCAN_URL)
    live_login_url = escape(LIVE_CREDITVIVO_LOGIN_URL)
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Credit Vivo Scanner</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: #f6f7f9;
      color: #17202a;
    }}
    body {{ margin: 0; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 32px 20px 48px; }}
    .top {{ display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 22px; }}
    h1 {{ font-size: 28px; line-height: 1.15; margin: 0 0 6px; }}
    p {{ margin: 0; color: #56616f; line-height: 1.5; }}
    .panel {{ background: #fff; border: 1px solid #d8dde6; border-radius: 8px; padding: 22px; box-shadow: 0 10px 24px rgba(28, 39, 58, .06); }}
    label {{ display: block; font-weight: 700; margin-bottom: 8px; }}
    input[type=file] {{ width: 100%; padding: 14px; border: 1px dashed #98a2b3; border-radius: 8px; background: #fbfcfd; }}
    button {{ margin-top: 16px; appearance: none; border: 0; border-radius: 8px; padding: 12px 16px; background: #0d5c75; color: white; font-weight: 700; cursor: pointer; }}
    button:disabled {{ background: #8792a2; cursor: wait; }}
    .meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ border: 1px solid #e2e7ef; border-radius: 8px; padding: 12px; background: #fbfcfd; }}
    .metric strong {{ display: block; font-size: 20px; }}
    .results {{ margin-top: 18px; display: none; }}
    .downloads {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    .download {{ display: inline-block; color: #0d5c75; border: 1px solid #9cc5d1; border-radius: 8px; padding: 9px 11px; text-decoration: none; background: #f3fbfd; font-weight: 700; }}
    .direct-links {{ margin-top: 14px; display: grid; gap: 8px; }}
    .direct-links a {{ color: #0d5c75; overflow-wrap: anywhere; }}
    .status {{ margin-top: 14px; white-space: pre-wrap; color: #344054; }}
    .guardrail {{ margin-top: 18px; padding: 12px; border-left: 4px solid #0d5c75; background: #eef8fb; color: #344054; }}
    @media (max-width: 720px) {{ .top, .meta {{ display: block; }} .metric {{ margin-top: 10px; }} }}
  </style>
</head>
<body>
  <main>
    <div class="top">
      <div>
        <h1>Credit Vivo Scanner</h1>
        <p>Upload up to {MAX_FILES} PDF credit reports. Max {MAX_FILE_MB} MB each.</p>
      </div>
      <p>API v18.1.7</p>
    </div>
    <section class="panel">
      <form id="scanForm">
        <label for="files">Credit report PDFs</label>
        <input id="files" name="files" type="file" accept="application/pdf,.pdf" multiple required>
        <button id="submitButton" type="submit">Run Scanner</button>
      </form>
      <div class="guardrail">Scanner output is draft review data only. Customer approval and admin review are required before any dispute, mailing, complaint, or escalation.</div>
      <div class="panel" style="box-shadow:none;margin-top:16px;padding:16px;">
        <h2 style="font-size:18px;margin:0 0 8px;">Latest scanner output</h2>
        {latest_downloads}
      </div>
      <div class="panel" style="box-shadow:none;margin-top:16px;padding:16px;">
        <h2 style="font-size:18px;margin:0 0 8px;">CreditVivo.com backend test links</h2>
        <div class="downloads">
          <a class="download" target="_blank" rel="noopener" href="{live_home_url}">Open CreditVivo.com</a>
          <a class="download" target="_blank" rel="noopener" href="{live_login_url}">Open Live Login / Dashboard</a>
          <a class="download" target="_blank" rel="noopener" href="{live_scan_url}">Open Live Scan Page</a>
        </div>
      </div>
      <div id="status" class="status"></div>
      <div id="results" class="results">
        <div class="meta">
          <div class="metric"><span>Review items</span><strong id="reviewCount">0</strong></div>
          <div class="metric"><span>Possible issues</span><strong id="issueCount">0</strong></div>
          <div class="metric"><span>Files scanned</span><strong id="fileCount">0</strong></div>
        </div>
        <div class="downloads" id="downloads"></div>
      </div>
    </section>
  </main>
  <script>
    const form = document.getElementById("scanForm");
    const statusEl = document.getElementById("status");
    const resultsEl = document.getElementById("results");
    const downloadsEl = document.getElementById("downloads");
    const button = document.getElementById("submitButton");

    form.addEventListener("submit", async (event) => {{
      event.preventDefault();
      const files = document.getElementById("files").files;
      if (!files.length) return;
      const body = new FormData();
      for (const file of files) body.append("files", file);
      button.disabled = true;
      statusEl.textContent = "Running scanner...";
      resultsEl.style.display = "none";
      downloadsEl.innerHTML = "";
      try {{
        const response = await fetch("/scanner/parse", {{ method: "POST", body }});
        const text = await response.text();
        let data = null;
        try {{
          data = text ? JSON.parse(text) : null;
        }} catch (error) {{
          throw new Error(text || "Scanner returned a response that could not be read.");
        }}
        if (!response.ok || !data) {{
          const detail = data && (data.detail || data.error || data.message);
          throw new Error(detail || `Scanner request failed with status ${{response.status}}.`);
        }}
        document.getElementById("reviewCount").textContent = data.review_items_count || 0;
        document.getElementById("issueCount").textContent = data.issues_count || 0;
        document.getElementById("fileCount").textContent = (data.files || []).length;
        const downloads = [
          ["Workbook", "workbook.xlsx"],
          ["Issues CSV", "issues.csv"],
          ["Tradelines CSV", "tradelines.csv"],
          ["Draft Letters", "letters.txt"],
          ["Document Vault Manifest", "vault.json"],
          ["3B Packet Attachment JSON", "packet-comparison.json"],
        ];
        const directLinks = document.createElement("div");
        directLinks.className = "direct-links";
        for (const [label, name] of downloads) {{
          const href = `/scanner/result/${{data.job_id}}/download/${{name}}`;
          const link = document.createElement("a");
          link.className = "download";
          link.href = href;
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = label;
          downloadsEl.appendChild(link);

          const direct = document.createElement("a");
          direct.href = href;
          direct.target = "_blank";
          direct.rel = "noopener";
          direct.textContent = `${{label}} direct link`;
          directLinks.appendChild(direct);
        }}
        downloadsEl.appendChild(directLinks);
        statusEl.textContent = data.customer_message || "Scanner completed.";
        resultsEl.style.display = "block";
      }} catch (error) {{
        statusEl.textContent = "Error: " + error.message;
      }} finally {{
        button.disabled = false;
      }}
    }});

    const copyButton = document.getElementById("copyLatestButton");
    if (copyButton) {{
      copyButton.addEventListener("click", async () => {{
        const copyStatus = document.getElementById("copyStatus");
        copyButton.disabled = true;
        copyStatus.textContent = "Copying latest outputs to Desktop...";
        try {{
          const response = await fetch("/scanner/latest/copy-to-desktop", {{ method: "POST" }});
          const data = await response.json();
          if (!response.ok || !data.ok) throw new Error(data.detail || data.error || "Copy failed.");
          copyStatus.textContent = `Copied ${{data.copied.length}} files to: ${{data.folder}}`;
        }} catch (error) {{
          copyStatus.textContent = "Error: " + error.message;
        }} finally {{
          copyButton.disabled = false;
        }}
      }});
    }}
  </script>
</body>
</html>
""")


@app.post("/scanner/latest/copy-to-desktop")
@app.get("/scanner/latest/copy-to-desktop")
def copy_latest_scanner_outputs():
    return JSONResponse(copy_scanner_outputs_to_desktop())


@app.get("/findings")
@app.get("/api/findings")
def findings_page():
    latest = latest_full_scan_result()
    data = latest["data"]
    rows = [
        [
            issue.get("id", ""),
            issue.get("customer_label", ""),
            issue.get("severity", ""),
            issue.get("confidence", ""),
            ", ".join(issue.get("related_tradeline_ids", [])),
        ]
        for issue in data.get("issues", [])[:100]
    ]
    body = f"""
    <p>Latest job: <strong>{escape(str(latest['job_id'] or 'none'))}</strong></p>
    <div class="panel">
      {render_table(["Issue ID", "Label", "Severity", "Confidence", "Related Tradelines"], rows, "Run a scan to populate findings.")}
    </div>
    """
    return packet_page_html("Findings", body)


@app.get("/findings/compare")
@app.get("/api/findings/compare")
def findings_compare_page():
    latest = latest_full_scan_result()
    packet_system = latest["data"].get("cfpb_packet_system", {})
    rows = [
        [
            row.get("account_field", ""),
            row.get("equifax_raw_value", ""),
            row.get("experian_raw_value", ""),
            row.get("transunion_raw_value", ""),
            row.get("main_issue", ""),
            row.get("license_authority_status", ""),
            row.get("evidence_source", ""),
        ]
        for row in packet_system.get("three_bureau_comparison_attachment", [])[:75]
    ]
    body = f"""
    <p>Latest job: <strong>{escape(str(latest['job_id'] or 'none'))}</strong></p>
    <div class="panel">
      {render_table(["Account / Field", "Equifax Raw Value", "Experian Raw Value", "TransUnion Raw Value", "Main Issue", "License / Authority Status", "Evidence Source"], rows, "No comparison attachment rows yet.")}
    </div>
    """
    return packet_page_html("3-Bureau Comparison Attachment", body)


@app.get("/findings/letters")
@app.get("/api/findings/letters")
def findings_letters_page():
    latest = latest_full_scan_result()
    packets = latest["data"].get("cfpb_packet_system", {}).get("dispute_packets", [])
    rows = [
        [
            packet.get("packet_id", ""),
            packet.get("packet_type", ""),
            packet.get("status", ""),
            packet.get("lob_tracking", {}).get("delivery_status", ""),
            "Yes" if packet.get("packet_gate", {}).get("customer_esign_required") else "No",
            "Yes" if packet.get("packet_gate", {}).get("admin_approval_required") else "No",
            "Yes" if packet.get("mailing_allowed") else "No",
        ]
        for packet in packets[:100]
    ]
    body = f"""
    <p>Latest job: <strong>{escape(str(latest['job_id'] or 'none'))}</strong></p>
    <div class="panel">
      {render_table(["Packet ID", "Packet Type", "Status", "Lob Status", "E-Sign Required", "Admin Required", "Mailing Allowed"], rows, "No packet letters yet.")}
    </div>
    """
    return packet_page_html("CFPB-Style Letters", body)


@app.get("/dashboard/documents")
@app.get("/api/dashboard/documents")
def dashboard_documents_page():
    latest = latest_full_scan_result()
    vault = latest["data"].get("cfpb_packet_system", {}).get("document_vault", {})
    rows = [
        [
            row.get("document_type", ""),
            row.get("letter_type", ""),
            row.get("delivery_status", ""),
            row.get("stored_evidence", ""),
            row.get("next_action", ""),
        ]
        for row in vault.get("records", [])[:100]
    ]
    body = f"""
    <p>Customer view: mailed packet history and evidence status. Sensitive documents are server-side only.</p>
    <div class="panel">
      {render_table(["Document Type", "Letter Type", "Delivery Status", "Stored Evidence", "Next Action"], rows, "No document vault records yet.")}
    </div>
    """
    return packet_page_html("Customer Documents", body)


@app.get("/dashboard/letters")
@app.get("/api/dashboard/letters")
def dashboard_letters_page():
    latest = latest_full_scan_result()
    packets = latest["data"].get("cfpb_packet_system", {}).get("dispute_packets", [])
    rows = [
        [
            packet.get("packet_type", ""),
            packet.get("customer_view_status", ""),
            packet.get("lob_tracking", {}).get("delivery_status", ""),
            "Customer approval needed" if packet.get("packet_gate", {}).get("customer_esign_required") else "Approved",
        ]
        for packet in packets[:100]
    ]
    body = f"""
    <p>Customer letter dashboard. Nothing is mailed from this preview.</p>
    <div class="panel">
      {render_table(["Letter Type", "Packet Status", "Delivery Status", "Approval"], rows, "No customer letters yet.")}
    </div>
    """
    return packet_page_html("Customer Letters", body)


@app.get("/admin/documents")
@app.get("/api/admin/documents")
def admin_documents_page(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return admin_login_redirect()
    latest = latest_full_scan_result()
    vault = latest["data"].get("cfpb_packet_system", {}).get("document_vault", {})
    rows = [
        [
            row.get("document_id", ""),
            row.get("case_id", ""),
            row.get("customer_id", ""),
            row.get("document_type", ""),
            row.get("letter_type", ""),
            row.get("delivery_status", ""),
            row.get("retention_status", ""),
            "Yes" if row.get("server_side_only") else "No",
        ]
        for row in vault.get("records", [])[:150]
    ]
    body = f"""
    <p>Admin document audit trail. Production storage still requires auth, encryption, RBAC, and audit logs.</p>
    <div class="panel">
      {render_table(["Document ID", "Case ID", "Customer ID", "Document Type", "Letter Type", "Delivery Status", "Retention Status", "Server-Side Only"], rows, "No admin document records yet.")}
    </div>
    """
    return packet_page_html("Admin Documents", body)


@app.get("/admin/letters")
@app.get("/api/admin/letters")
def admin_letters_page(cv_admin_session: str | None = Cookie(default=None)):
    if not read_admin_session(cv_admin_session):
        return admin_login_redirect()
    latest = latest_full_scan_result()
    packets = latest["data"].get("cfpb_packet_system", {}).get("dispute_packets", [])
    rows = [
        [
            packet.get("packet_id", ""),
            packet.get("packet_type", ""),
            packet.get("admin_view_status", ""),
            packet.get("lob_tracking", {}).get("tracking_number", ""),
            packet.get("lob_tracking", {}).get("delivery_status", ""),
            "; ".join(packet.get("packet_gate", {}).get("block_reasons", [])),
        ]
        for packet in packets[:150]
    ]
    body = f"""
    <p>Admin letter packet queue. Lob status is a placeholder until approvals and production keys are configured.</p>
    <div class="panel">
      {render_table(["Packet ID", "Packet Type", "Admin Status", "Tracking Number", "Delivery Status", "Block Reasons"], rows, "No admin letter packets yet.")}
    </div>
    """
    return packet_page_html("Admin Letters", body)


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
    return JSONResponse({
        "ok": True,
        "service": "credit-vivo-growth-ai",
        "lead_score": lead_score(signals),
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


@app.get("/admin/growth/health")
def admin_growth_health():
    return JSONResponse({
        "ok": True,
        "service": "cv-market-growth-ai",
        "mode": "founder_side_command_center",
        "draft_only": True,
        "paid_ai_used": False,
        "automatic_outreach": False,
    })


@app.get("/admin/growth/dashboard")
def admin_growth_dashboard():
    return JSONResponse(get_growth_dashboard(STORAGE_ROOT))


@app.post("/admin/growth/lead/score")
async def admin_growth_lead_score(payload: Dict[str, object]):
    return JSONResponse({
        "ok": True,
        "service": "cv-market-growth-ai",
        "lead_score": score_lead(payload),
    })


@app.post("/admin/growth/campaign/build")
async def admin_growth_campaign_build(payload: Dict[str, object]):
    campaign_goal = str(payload.get("campaign_goal", payload.get("goal", "")))
    audience = str(payload.get("audience", "Credit Vivo prospects"))
    channel = str(payload.get("channel", "email"))
    language = str(payload.get("language", "en"))
    campaign = build_campaign(campaign_goal, audience, channel, language=language)
    approval = create_approval_item(
        "ad_campaign" if channel.lower() in {"social", "paid_social", "ad"} else "customer_message",
        campaign["draft"],
        "medium",
        APPROVAL_QUEUE_LOG,
    )
    return JSONResponse({**campaign, "approval_item": approval})


@app.post("/admin/growth/compliance/check")
async def admin_growth_compliance_check(payload: Dict[str, object]):
    message = str(payload.get("message", ""))
    channel = str(payload.get("channel", "general"))
    return JSONResponse(compliance_check_message(message, channel))


@app.post("/admin/growth/approval/create")
async def admin_growth_approval_create(payload: Dict[str, object]):
    item_type = str(payload.get("item_type", "customer_message"))
    content = payload.get("content", "")
    risk_level = str(payload.get("risk_level", "medium"))
    return JSONResponse(create_approval_item(item_type, content, risk_level, APPROVAL_QUEUE_LOG))


@app.post("/admin/growth/consent/log")
async def admin_growth_consent_log(payload: Dict[str, object]):
    return JSONResponse(log_consent(
        str(payload.get("customer_id", "")),
        str(payload.get("consent_type", "marketing")),
        str(payload.get("channel", "unknown")),
        str(payload.get("consent_text", "")),
        CONSENT_LOG,
    ))


@app.post("/admin/growth/partner/referral")
async def admin_growth_partner_referral(payload: Dict[str, object]):
    return JSONResponse(track_partner_referral(
        str(payload.get("partner_id", "")),
        str(payload.get("lead_id", "")),
        str(payload.get("status", "new")),
        PARTNER_REFERRAL_LOG,
    ))


@app.post("/admin/growth/revenue/attribute")
async def admin_growth_revenue_attribute(payload: Dict[str, object]):
    partner_value = payload.get("partner_id")
    return JSONResponse(attribute_revenue(
        str(payload.get("customer_id", "")),
        str(payload.get("source", "direct")),
        str(payload.get("campaign", "unknown")),
        str(partner_value) if partner_value else None,
        float(payload.get("amount", 0.0)),
        REVENUE_ATTRIBUTION_LOG,
    ))


@app.get("/admin/growth/founder-summary")
def admin_growth_founder_summary(
    location: str = "DMV",
    product_focus: str | None = None,
):
    return JSONResponse({
        **generate_founder_summary(STORAGE_ROOT),
        "market_opportunities": recommend_market_opportunities(location, product_focus),
    })


MARKET_AI_PAGE_TITLES = {
    "/market-ai": "Market AI Studio",
    "/market-ai/assets": "Asset Library",
    "/market-ai/images": "Ad Image Builder",
    "/market-ai/animations": "Animation Builder",
    "/market-ai/videos": "Video Studio",
    "/market-ai/learning": "Learning Content",
    "/market-ai/campaigns": "Campaigns",
    "/market-ai/calendar": "Campaign Calendar",
    "/market-ai/review": "Review Queue",
    "/market-ai/approved": "Approved Assets",
    "/market-ai/settings/brand": "Brand Kit",
}


def market_ai_page_html(title: str) -> HTMLResponse:
    dashboard = build_market_ai_dashboard()
    stats = dashboard["stats"]
    cards = "".join(
        f"<article><strong>{escape(asset['title'])}</strong><span>{escape(asset['status'])}</span><p>{escape(asset['topic'])} / {escape(asset['format'])}</p></article>"
        for asset in dashboard["assets"][:6]
    )
    body = f"""
    <html>
      <head>
        <title>Credit Vivo {escape(title)}</title>
        <style>
          body {{ margin:0; font-family: Arial, sans-serif; background:#f8fafc; color:#08122B; }}
          main {{ max-width:1180px; margin:0 auto; padding:32px 18px; }}
          nav a {{ margin-right:14px; color:#1F58FF; font-weight:700; text-decoration:none; }}
          .hero {{ background:linear-gradient(135deg,#08122B,#1F58FF 56%,#2ACF8F); color:white; border-radius:18px; padding:28px; }}
          .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; margin-top:18px; }}
          .stat, article {{ background:white; border:1px solid #dbeafe; border-radius:12px; padding:16px; box-shadow:0 8px 18px rgba(15,23,42,.06); }}
          article span {{ display:inline-block; margin-top:10px; padding:4px 10px; border-radius:999px; background:#fef3c7; color:#92400e; font-size:12px; font-weight:700; }}
          .guardrail {{ margin-top:18px; background:#ecfdf5; border:1px solid #bbf7d0; border-radius:12px; padding:14px; color:#166534; }}
        </style>
      </head>
      <body>
        <main>
          <nav>
            <a href="/market-ai">Studio</a>
            <a href="/market-ai/assets">Assets</a>
            <a href="/market-ai/videos">Videos</a>
            <a href="/market-ai/review">Review</a>
            <a href="/market-ai/settings/brand">Brand</a>
          </nav>
          <section class="hero">
            <p>Credit Vivo Market AI</p>
            <h1>{escape(title)}</h1>
            <p>In-house creative studio for learning videos, ad images, animations, captions, campaigns, and owned brand assets.</p>
          </section>
          <section class="grid">
            <div class="stat"><p>Assets</p><h2>{stats['assets']}</h2></div>
            <div class="stat"><p>Needs Review</p><h2>{stats['needs_review']}</h2></div>
            <div class="stat"><p>Learning Topics</p><h2>{stats['learning_topics']}</h2></div>
            <div class="stat"><p>Stock Dependencies</p><h2>{stats['stock_dependencies']}</h2></div>
          </section>
          <section class="grid">{cards}</section>
          <div class="guardrail">No auto-publishing. No stock footage dependency. Founder/compliance approval is required before public use.</div>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(body)


@app.get("/market-ai")
def market_ai_home():
    return market_ai_page_html("Market AI Studio")


@app.get("/market-ai/assets")
@app.get("/market-ai/images")
@app.get("/market-ai/animations")
@app.get("/market-ai/videos")
@app.get("/market-ai/learning")
@app.get("/market-ai/campaigns")
@app.get("/market-ai/calendar")
@app.get("/market-ai/review")
@app.get("/market-ai/approved")
@app.get("/market-ai/settings/brand")
def market_ai_subpage():
    return market_ai_page_html("Market AI Studio")


@app.get("/api/market/assets")
def market_assets_api():
    return JSONResponse({"ok": True, "assets": sample_market_assets(), "policy": build_market_ai_dashboard()["asset_policy"]})


@app.post("/api/market/assets")
async def market_assets_create_api(payload: Dict[str, object]):
    asset = {
        **payload,
        "asset_id": str(payload.get("asset_id") or uuid.uuid4()),
        "status": payload.get("status", "Needs Review"),
        "created_by": "Market AI",
        "source": "Credit Vivo generated",
        "approval_required": True,
        "auto_publish_allowed": False,
        "uses_stock_assets": False,
    }
    return JSONResponse({"ok": True, "asset": asset})


@app.post("/api/market/compliance-check")
async def market_compliance_check_api(payload: Dict[str, object]):
    return JSONResponse(check_marketing_compliance(str(payload.get("text", ""))))


@app.post("/api/market/generate-storyboard")
async def market_generate_storyboard_api(payload: Dict[str, object]):
    topic = get_topic(str(payload.get("topic_id", "free-weekly-reports")))
    return JSONResponse({"ok": True, "storyboard": generate_learning_storyboard(topic)})


@app.post("/api/market/generate-script")
async def market_generate_script_api(payload: Dict[str, object]):
    topic = get_topic(str(payload.get("topic_id", "free-weekly-reports")))
    return JSONResponse({"ok": True, "script": generate_video_script(topic)})


@app.post("/api/market/render-job")
async def market_render_job_api(payload: Dict[str, object]):
    return JSONResponse({"ok": True, "render_job": create_render_job(dict(payload))})


@app.get("/api/market/templates")
def market_templates_api():
    return JSONResponse({"ok": True, **build_market_templates(), "learning_topics": LEARNING_TOPICS})


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
def get_result(job_id: str):
    summary = scanner_job_dir(job_id) / "scan_result_summary.json"
    if not summary.exists():
        return JSONResponse({"ok": False, "error": "Result not found"}, status_code=404)
    return JSONResponse(json.loads(summary.read_text(encoding="utf-8")))


@app.get("/scanner/result/{job_id}/full")
@app.get("/api/scanner/result/{job_id}/full")
def get_full_result(job_id: str):
    full = scanner_job_dir(job_id) / "credit_vivo_parser_result.json"
    if not full.exists():
        return JSONResponse({"ok": False, "error": "Full result not found"}, status_code=404)
    return JSONResponse(json.loads(full.read_text(encoding="utf-8")))


@app.get("/scanner/result/{job_id}/download/{download_name}")
@app.get("/api/scanner/result/{job_id}/download/{download_name}")
def download_scanner_output(job_id: str, download_name: str):
    download = SCAN_DOWNLOADS.get(download_name)
    if not download:
        return JSONResponse({"ok": False, "error": "Download not found"}, status_code=404)

    filename, media_type, download_filename = download
    path = scanner_job_dir(job_id) / filename
    if not path.exists():
        return JSONResponse({"ok": False, "error": "Scanner output not found"}, status_code=404)

    return FileResponse(path, media_type=media_type, filename=download_filename)
