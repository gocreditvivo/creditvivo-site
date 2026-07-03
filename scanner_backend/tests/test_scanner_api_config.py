import asyncio
from main import (
    LIVE_CREDITVIVO_LOGIN_URL,
    LIVE_CREDITVIVO_SCAN_URL,
    create_admin_session,
    ensure_local_admin_credentials,
    admin_backend_summary,
    admin_backend_summary_api,
    admin_backend_inventory_api,
    admin_backend_home,
    admin_login_html,
    admin_operating_architecture_api,
    admin_production_certification_api,
    admin_production_certification_page,
    backend_production_certification,
    creditvivo_operating_architecture,
    email_safety_config,
    founder_backend_inventory,
    health,
    latest_scanner_job_id,
    member_portal_api,
    member_portal_payload,
    production_readiness_checks,
    admin_production_readiness_api,
    scanner_download_links_html,
    protect_founder_admin_routes,
    staging_safety_config,
)
from fastapi.responses import JSONResponse


def founder_session_cookie() -> str:
    credentials = ensure_local_admin_credentials()
    return create_admin_session(credentials["username"])


class FakeUrl:
    def __init__(self, path: str):
        self.path = path


class FakeRequest:
    def __init__(self, path: str, headers: dict | None = None, cookies: dict | None = None):
        self.url = FakeUrl(path)
        self.headers = headers or {}
        self.cookies = cookies or {}


async def fake_call_next(_request):
    return JSONResponse({"ok": True})


def test_scanner_uses_production_safe_storage_defaults():
    status = health()

    assert status["write_raw_text"] is False
    assert status["retain_uploads"] is False
    assert status["scanner_shell_requires_login"] is True
    assert status["email_provider"] == "disabled"
    assert status["email_sending_enabled"] is False
    assert status["marketing_emails_enabled"] is False
    assert status["dispute_email_auto_send_enabled"] is False
    assert status["external_calls_enabled"] is False
    assert status["auto_send_enabled"] is False
    assert status["pdf_text_engine"] == "pypdf"


def test_email_safety_defaults_are_no_send():
    config = email_safety_config()

    assert config["provider"] == "disabled"
    assert config["from"] == "no-reply@creditvivo.com"
    assert config["support_email"] == "support@creditvivo.com"
    assert config["privacy_email"] == "privacy@creditvivo.com"
    assert config["security_email"] == "security@creditvivo.com"
    assert config["email_sending_enabled"] is False
    assert config["marketing_emails_enabled"] is False
    assert config["dispute_email_auto_send_enabled"] is False


def test_staging_safety_defaults_are_no_send_and_no_external_calls():
    config = staging_safety_config()

    assert config["is_staging"] is False
    assert config["payments_mode"] == "disabled"
    assert config["stripe_mode"] == "disabled"
    assert config["external_calls_enabled"] is False
    assert config["auto_send_enabled"] is False
    assert config["customer_final_result_without_qa"] is False
    assert config["letters_without_verified_issue"] is False
    assert config["complaints_without_approval"] is False
    assert config["attorney_escalation_without_approval"] is False


def test_staging_safety_mode_blocks_real_data_and_uses_test_modes(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.delenv("SCANNER_USE_SYNTHETIC_REPORTS", raising=False)
    monkeypatch.delenv("SCANNER_ALLOW_REAL_CUSTOMER_DATA", raising=False)
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    monkeypatch.delenv("STRIPE_MODE", raising=False)

    config = staging_safety_config()

    assert config["environment_name"] == "Credit Vivo Staging Safe Mode"
    assert config["is_staging"] is True
    assert config["synthetic_reports_only"] is True
    assert config["allow_real_customer_data"] is False
    assert config["payments_mode"] == "test"
    assert config["stripe_mode"] == "test"
    assert config["external_calls_enabled"] is False
    assert config["auto_send_enabled"] is False


def test_scanner_page_default_links_include_latest_backend_job():
    html = scanner_download_links_html("scan_97fe328cadeb")

    assert "Latest backend test job" in html
    assert "scan_97fe328cadeb" in html
    assert "/scanner/result/scan_97fe328cadeb/download/workbook.xlsx" in html
    assert "Copy latest outputs to Desktop" in html


def test_live_creditvivo_links_default_to_dashboard_and_scan():
    assert LIVE_CREDITVIVO_LOGIN_URL == "https://www.creditvivo.com/dashboard"
    assert LIVE_CREDITVIVO_SCAN_URL == "https://www.creditvivo.com/scan"


def test_admin_backend_summary_has_safety_defaults():
    summary = admin_backend_summary()

    assert summary["service"] == "credit-vivo-founder-admin-backend"
    assert summary["api_version"] == health()["version"]
    assert summary["approval_required"] is True
    assert summary["customer_admin_split"] is True
    assert summary["paid_ai_used"] is False
    assert summary["automatic_mailing_enabled"] is False
    assert summary["automatic_complaint_submission_enabled"] is False


def test_member_portal_payload_is_safe_and_useful_by_default():
    payload = member_portal_payload()

    assert payload["profile"] is None
    assert payload["productionGate"]["customerDataAllowed"] is False
    assert payload["productionGate"]["productionGatePassed"] is False
    assert payload["reviewAccounts"] == []
    assert payload["draftLetters"] == []
    assert payload["identityVerification"]["status"] == "needs_review"
    assert len(payload["documents"]) >= 4
    assert all(document["canUseForPrep"] is False for document in payload["documents"])
    assert any(document["name"] == "Government ID" for document in payload["documents"])
    assert any(task["title"] == "Upload required documents" for task in payload["customerTasks"])
    assert any(milestone["phase"] == "Customer approvals" for milestone in payload["progressMilestones"])


def test_member_portal_api_returns_safe_payload():
    payload = member_portal_api().body.decode("utf-8")

    assert "identityVerification" in payload
    assert "customerTasks" in payload
    assert '"customerDataAllowed":false' in payload
    assert "Government ID" in payload
    assert "Raw report files stay hidden" in payload


def test_production_readiness_has_expected_local_blockers():
    readiness = production_readiness_checks({
        "latest_job_id": "scan_test",
        "pre_output_status": "pass",
        "customer_admin_split": True,
        "automatic_mailing_enabled": False,
        "automatic_complaint_submission_enabled": False,
        "approval_required": True,
        "paid_ai_used": False,
    })

    keys = {item["key"]: item["status"] for item in readiness["checks"]}
    assert keys["automatic_actions"] == "pass"
    assert keys["approval_gates"] == "pass"
    assert keys["auth_provider"] in {"blocker", "pass"}
    assert readiness["status"] in {"blocked", "review_needed", "ready"}


def test_admin_backend_home_links_core_apps():
    html = admin_backend_home(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert "Founder Admin Backend" in html
    assert "Signed in as" in html
    assert "/scanner" in html
    assert "/admin/letters" in html
    assert "/admin/documents" in html
    assert "/admin/growth/dashboard" in html
    assert "/admin/production-readiness" in html
    assert "/admin/production-certification" in html
    assert "/admin/backend-inventory" in html
    assert "Backend Data Inventory" in html
    assert "Backend Tools" in html
    assert "Operating Domains" in html
    assert "Shared Resources" in html
    assert "Integrations" in html
    assert "Permissions Matrix" in html
    assert "Production Readiness" in html
    assert "Role Access Model" in html
    assert "Compliance Guardrails" in html
    assert "https://www.creditvivo.com/dashboard" in html


def test_founder_backend_inventory_includes_data_tools_and_skills():
    inventory = founder_backend_inventory()

    data_names = {item["name"] for item in inventory["data_sources"]}
    tool_names = {item["name"] for item in inventory["tools"]}
    skill_names = {item["name"] for item in inventory["skills"]}

    assert "Latest Scanner Job" in data_names
    assert "Desktop Workbook Output" in data_names
    assert "Scanner Test Hub" in tool_names
    assert "Backend Inventory JSON" in tool_names
    assert "Operating Architecture JSON" in tool_names
    assert "Native Credit Vivo Parser" in skill_names
    assert "Compliance Guardrails" in skill_names
    assert "architecture" in inventory
    assert inventory["guardrails"]


def test_operating_architecture_covers_all_core_domains():
    architecture = creditvivo_operating_architecture()

    domain_ids = {item["domain_id"] for item in architecture["domains"]}
    integration_names = {item["name"] for item in architecture["integrations"]}
    resource_names = {item["name"] for item in architecture["shared_resources"]}

    assert architecture["service"] == "credit-vivo-operating-architecture"
    assert "scanner_engine" in domain_ids
    assert "letter_lifecycle" in domain_ids
    assert "client_portal" in domain_ids
    assert "growth_engine" in domain_ids
    assert "market_ai_studio" in domain_ids
    assert "operator_command" in domain_ids
    assert "admin_security_compliance" in domain_ids
    assert "staging_uat" in domain_ids
    assert "Production Auth" in integration_names
    assert "Backend Tests" in resource_names
    assert all(item["guardrail"] for item in architecture["domains"])


def test_admin_operating_architecture_api_returns_map():
    payload = admin_operating_architecture_api(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert '"ok":true' in payload
    assert "credit-vivo-operating-architecture" in payload
    assert "scanner_engine" in payload
    assert "growth_engine" in payload
    assert "market_ai_studio" in payload


def test_admin_backend_inventory_api_returns_inventory():
    payload = admin_backend_inventory_api(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert '"ok":true' in payload
    assert "data_sources" in payload
    assert "Backend Inventory JSON" in payload
    assert "Native Credit Vivo Parser" in payload


def test_admin_backend_summary_api_returns_ok():
    payload = admin_backend_summary_api(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert '"ok":true' in payload
    assert "credit-vivo-founder-admin-backend" in payload


def test_admin_production_readiness_api_returns_gates():
    payload = admin_production_readiness_api(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert '"ok":true' in payload
    assert "production_readiness" in payload
    assert "auth_provider" in payload
    assert "automatic_actions" in payload


def test_backend_production_certification_reports_safe_defaults():
    certificate = backend_production_certification({
        "latest_job_id": "scan_test",
        "pre_output_status": "pass",
        "customer_admin_split": True,
        "automatic_mailing_enabled": False,
        "automatic_complaint_submission_enabled": False,
        "approval_required": True,
        "paid_ai_used": False,
    })

    assert certificate["service"] == "credit-vivo-backend-production-certification"
    assert certificate["controlled_testing_certified"] is True
    assert certificate["safe_defaults"]["raw_text_storage"] == "off"
    assert certificate["safe_defaults"]["upload_retention"] == "off"
    assert certificate["safe_defaults"]["scanner_shell_login_required"] is True
    assert certificate["safe_defaults"]["api_docs_protected"] is True
    assert certificate["safe_defaults"]["automatic_mailing"] == "off"
    assert certificate["safe_defaults"]["automatic_complaints"] == "off"
    assert certificate["safe_defaults"]["email_provider"] == "disabled"
    assert certificate["safe_defaults"]["email_sending"] == "off"
    assert certificate["safe_defaults"]["marketing_emails"] == "off"
    assert certificate["safe_defaults"]["dispute_email_auto_send"] == "off"
    assert certificate["safe_defaults"]["external_calls"] == "off"
    assert certificate["safe_defaults"]["auto_send"] == "off"
    assert certificate["safe_defaults"]["customer_final_result_without_qa"] == "off"
    assert certificate["safe_defaults"]["letters_without_verified_issue"] == "off"
    assert certificate["safe_defaults"]["complaints_without_approval"] == "off"
    assert certificate["safe_defaults"]["attorney_escalation_without_approval"] == "off"


def test_admin_production_certification_routes_work():
    html = admin_production_certification_page(cv_admin_session=founder_session_cookie()).body.decode("utf-8")
    payload = admin_production_certification_api(cv_admin_session=founder_session_cookie()).body.decode("utf-8")

    assert "Credit Vivo Backend Production Certification" in html
    assert "Safe Defaults Turned On" in html
    assert "Live Production Blockers" in html
    assert '"ok":true' in payload
    assert "credit-vivo-backend-production-certification" in payload


def test_admin_login_required_without_session():
    response = admin_backend_home(cv_admin_session=None)

    assert response.status_code == 303
    assert response.headers["location"] == "/founder-login"


def test_admin_login_page_contains_founder_form():
    html = admin_login_html().body.decode("utf-8")

    assert "Founder Login" in html
    assert 'name="username"' in html
    assert 'name="password"' in html


def test_backend_component_routes_require_founder_login():
    protected_paths = [
        "/findings",
        "/findings/compare",
        "/dashboard/letters",
        "/dashboard/documents",
        "/growth-ai/brief",
        "/market-ai",
        "/operator-ai/brief",
        "/vivo-command/brief",
        "/events/summary",
        "/leads/summary",
    ]

    for path in protected_paths:
        response = asyncio.run(protect_founder_admin_routes(FakeRequest(path), fake_call_next))
        assert response.status_code == 303, path
        assert response.headers["location"] == "/founder-login"


def test_health_remains_open_and_scanner_shell_requires_login():
    health_response = asyncio.run(protect_founder_admin_routes(FakeRequest("/health"), fake_call_next))
    scanner_response = asyncio.run(protect_founder_admin_routes(FakeRequest("/scanner"), fake_call_next))

    assert health_response.status_code == 200
    assert scanner_response.status_code == 303
    assert scanner_response.headers["location"] == "/founder-login"


def test_latest_scanner_job_ignores_incomplete_output_dirs(tmp_path, monkeypatch):
    complete = tmp_path / "scan_complete"
    incomplete = tmp_path / "scan_incomplete_newer"
    complete.mkdir()
    incomplete.mkdir()
    (complete / "scan_result_summary.json").write_text("{}", encoding="utf-8")
    (complete / "credit_vivo_desktop_scanner_output.xlsx").write_bytes(b"xlsx")
    (incomplete / "credit_vivo_parser_result.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr("main.OUTPUT", tmp_path)

    assert latest_scanner_job_id() == "scan_complete"
