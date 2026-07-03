from pathlib import Path

from campaign_builder_engine import build_campaign, compliance_check_message
from consent_log_engine import log_consent
from cv_market_growth_ai import DASHBOARD_KEYS, generate_founder_summary, get_growth_dashboard
from growth_approval_queue import create_approval_item
from lead_intelligence_engine import recommend_next_action, score_lead
from main import admin_growth_health
from market_ai import recommend_market_opportunities
from partner_referral_engine import track_partner_referral
from revenue_attribution_engine import attribute_revenue


def test_compliance_guard_blocks_unsafe_phrases():
    result = compliance_check_message("We promise guaranteed approval and instant results.", "sms")

    assert result["ok"] is False
    assert "guaranteed approval" in result["blocked_phrases"]
    assert "instant results" in result["blocked_phrases"]
    assert result["approval_required"] is True


def test_campaign_builder_creates_draft_only_campaign():
    campaign = build_campaign("Rent Ready", "Apartment applicants", "email")

    assert campaign["status"] == "draft_ready"
    assert campaign["approval_required"] is True
    assert campaign["can_send_now"] is False
    assert campaign["compliance"]["ok"] is True


def test_approval_queue_required_for_customer_facing_messages(tmp_path: Path):
    item = create_approval_item(
        "customer_message",
        "Review recommended. Results vary.",
        "medium",
        tmp_path / "approval.jsonl",
    )

    assert item["status"] == "founder_review_pending"
    assert item["approval_required"] is True
    assert item["can_send_now"] is False
    assert (tmp_path / "approval.jsonl").exists()


def test_consent_log_records_timestamp_and_channel(tmp_path: Path):
    record = log_consent(
        "customer_1",
        "marketing_sms",
        "sms",
        "Customer agreed to receive Credit Vivo updates.",
        tmp_path / "consent.jsonl",
    )

    assert record["timestamp"]
    assert record["channel"] == "sms"
    assert (tmp_path / "consent.jsonl").exists()


def test_revenue_attribution_stores_source_campaign_partner(tmp_path: Path):
    record = attribute_revenue(
        "customer_1",
        "referral_partner",
        "Rent Ready",
        "partner_1",
        99,
        tmp_path / "revenue.jsonl",
    )

    assert record["source"] == "referral_partner"
    assert record["campaign"] == "Rent Ready"
    assert record["partner_id"] == "partner_1"
    assert record["amount"] == 99.0


def test_partner_referral_and_lead_intelligence():
    referral = track_partner_referral("partner_1", "lead_1", "converted")
    lead = score_lead({
        "goal": "Need rent ready review",
        "uploaded_report": True,
        "denied_for_credit": True,
        "consent_to_contact": True,
    })
    action = recommend_next_action({"goal": "Need rent ready review", "uploaded_report": True})

    assert referral["status"] == "converted"
    assert lead["category"] == "Rent Ready"
    assert action["can_contact_now"] is False


def test_founder_dashboard_returns_required_keys(tmp_path: Path):
    dashboard = get_growth_dashboard(tmp_path)

    assert dashboard["ok"] is True
    assert set(DASHBOARD_KEYS).issubset(dashboard["dashboard"].keys())
    assert generate_founder_summary(tmp_path)["required_review"]


def test_market_ai_returns_opportunities():
    result = recommend_market_opportunities(location="DMV", product_focus="mortgage")

    assert result["ok"] is True
    assert result["opportunities"]
    assert result["approval_required_before_campaign_launch"] is True


def test_admin_growth_api_health_route_works():
    response = admin_growth_health()

    assert response.status_code == 200
    assert response.body
