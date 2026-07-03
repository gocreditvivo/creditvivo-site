from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AiTrackingSpec:
    ai_name: str
    owner_question: str
    tracks: List[str]
    result_metrics: List[str]
    alerts: List[str]
    dashboard_section: str


AI_TRACKING_SPECS: List[AiTrackingSpec] = [
    AiTrackingSpec(
        ai_name="Growth AI",
        owner_question="Are we getting customers and moving toward $1M/month?",
        tracks=[
            "website_visit",
            "join_clicked",
            "lead_created",
            "pricing_viewed",
            "paid_upgrade",
            "customer_cancelled",
            "ad_spend",
            "referral_signup",
            "campaign_source",
        ],
        result_metrics=[
            "monthly recurring revenue",
            "paid customer gap",
            "visitor-to-lead rate",
            "free-scan-to-paid rate",
            "cost per lead",
            "cost per paid customer",
            "best and worst campaign",
        ],
        alerts=[
            "no traffic data",
            "low visitor-to-lead rate",
            "free users not upgrading",
            "ad spend too high",
            "weekly growth target missed",
        ],
        dashboard_section="Owner AI / Growth AI",
    ),
    AiTrackingSpec(
        ai_name="Scanner AI",
        owner_question="Are customers completing scans and getting useful findings?",
        tracks=[
            "scan_started",
            "scan_completed",
            "scan_failed",
            "finding_count",
            "finding_category",
            "bureau_count",
            "customer_goal",
        ],
        result_metrics=[
            "scan start count",
            "scan completion rate",
            "scan failure rate",
            "top finding categories",
            "campaigns producing completed scans",
        ],
        alerts=[
            "scanner completion drops",
            "scanner errors increase",
            "campaign sends leads but few scans complete",
            "same finding category repeats",
        ],
        dashboard_section="Owner AI / Scanner Feed",
    ),
    AiTrackingSpec(
        ai_name="Dispute AI",
        owner_question="Which findings become serious dispute or escalation value?",
        tracks=[
            "draft_dispute_created",
            "dispute_category",
            "bureau_or_furnisher_path",
            "evidence_packet_ready",
            "repeat_verified_item",
            "escalation_candidate",
            "customer_approved_next_step",
            "dispute_letter_ready",
        ],
        result_metrics=[
            "draft disputes created",
            "evidence packets ready",
            "customer approvals",
            "escalation candidates",
            "repeat verified items",
        ],
        alerts=[
            "many customers have same dispute category",
            "letter ready needs approval",
            "customers stall before approval",
            "verified items repeat",
        ],
        dashboard_section="Owner AI / Dispute Feed",
    ),
    AiTrackingSpec(
        ai_name="Retention AI",
        owner_question="Who is stuck, likely to cancel, or ready for a next step?",
        tracks=[
            "customer_stuck",
            "days_since_progress",
            "cancellation_risk",
            "support_issue_count",
            "failed_payment",
            "upgrade_ready",
            "attorney_access_interest",
        ],
        result_metrics=[
            "customers likely to cancel",
            "customers needing attention",
            "upgrade-ready customers",
            "legal-access interest",
            "failed payments",
        ],
        alerts=[
            "customer stuck 7 days",
            "cancellation risk rises",
            "failed payment",
            "same support issue repeats",
        ],
        dashboard_section="Owner AI / Retention Feed",
    ),
    AiTrackingSpec(
        ai_name="Operator AI",
        owner_question="Is the website, scanner, tracking, and payment machine working?",
        tracks=[
            "website_down",
            "latest_deploy_status",
            "scanner_api_health",
            "lead_capture_errors",
            "payment_webhook_errors",
            "ad_tracking_errors",
            "form_submission_errors",
            "scan_failed",
        ],
        result_metrics=[
            "site status",
            "scanner API status",
            "deploy status",
            "form error count",
            "tracking error count",
            "open system issues",
        ],
        alerts=[
            "website down",
            "scanner API fails",
            "Join Free form errors",
            "payment or tracking events stop",
        ],
        dashboard_section="Owner AI / System Health",
    ),
    AiTrackingSpec(
        ai_name="Compliance Guard AI",
        owner_question="Are public actions, wording, approvals, and sensitive data safe enough to review?",
        tracks=[
            "risky_ad_copy_flag",
            "guarantee_language_flag",
            "attorney_wording_flag",
            "state_launch_review_needed",
            "approval_missing",
            "consent_missing",
            "sensitive_data_exposure_flag",
        ],
        result_metrics=[
            "risky copy flags",
            "approval missing count",
            "consent missing count",
            "state review needed count",
            "sensitive data flags",
        ],
        alerts=[
            "ad copy makes outcome promises",
            "attorney wording too broad",
            "customer-facing action lacks approval",
            "sensitive data exposure risk",
        ],
        dashboard_section="Owner AI / Approval & Risk",
    ),
    AiTrackingSpec(
        ai_name="Vivo Command AI",
        owner_question="What should the owner look at today?",
        tracks=[
            "top_growth_action",
            "revenue_gap",
            "paid_customer_gap",
            "system_blockers",
            "approval_queue",
            "weekly_growth_score",
            "12_month_goal_progress",
        ],
        result_metrics=[
            "top three actions",
            "revenue gap",
            "paid customer gap",
            "approval queue",
            "system blockers",
            "weekly growth score",
        ],
        alerts=[
            "weekly target missed",
            "revenue gap increases",
            "cross-AI blocker prevents growth",
            "owner approval waiting",
        ],
        dashboard_section="Owner AI / Command Brief",
    ),
]


def tracking_spec_to_dict(spec: AiTrackingSpec) -> Dict[str, object]:
    return spec.__dict__


def build_ai_tracking_map() -> Dict[str, object]:
    return {
        "ok": True,
        "service": "credit-vivo-ai-tracking-map",
        "plain_english_summary": "Each AI has its own tracking lane. Growth AI owns revenue movement, Scanner AI owns scan/finding movement, Dispute AI owns dispute value, Retention AI owns customer progress, Operator AI owns system health, Compliance Guard owns approval/risk, and Vivo Command AI summarizes everything for the owner.",
        "tracking_specs": [tracking_spec_to_dict(spec) for spec in AI_TRACKING_SPECS],
        "shared_owner_dashboard": "/owner-ai",
        "minimum_live_events_to_connect_first": [
            "website_visit",
            "join_clicked",
            "lead_created",
            "scan_started",
            "scan_completed",
            "scan_failed",
            "pricing_viewed",
            "paid_upgrade",
            "customer_cancelled",
            "customer_stuck",
        ],
    }
