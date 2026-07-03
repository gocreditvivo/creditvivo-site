from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CrossAiDirective:
    ai_name: str
    mission_for_growth: str
    data_to_send_growth_ai: List[str]
    actions_to_recommend: List[str]
    alert_growth_ai_when: List[str]
    owner_brief_line: str


CROSS_AI_DIRECTIVES: List[CrossAiDirective] = [
    CrossAiDirective(
        ai_name="Scanner AI",
        mission_for_growth="Help Growth AI learn which campaigns produce completed scans and valuable findings.",
        data_to_send_growth_ai=[
            "scan_started",
            "scan_completed",
            "scan_failed",
            "finding_count",
            "finding_category",
            "bureau_count",
            "customer_goal",
            "campaign_source",
        ],
        actions_to_recommend=[
            "improve scanner start copy when scan starts are low",
            "improve upload guidance when scan failures rise",
            "recommend campaign angles from common finding categories",
            "flag findings that create strong paid-plan upgrade moments",
        ],
        alert_growth_ai_when=[
            "scan completion rate drops below target",
            "a campaign sends many leads but few completed scans",
            "a finding category appears repeatedly",
            "scanner errors increase",
        ],
        owner_brief_line="Scanner AI tells Growth AI which campaigns create real report reviews, not just clicks.",
    ),
    CrossAiDirective(
        ai_name="Dispute AI",
        mission_for_growth="Help Growth AI understand which scanner findings turn into serious dispute workflows and paid value.",
        data_to_send_growth_ai=[
            "draft_dispute_created",
            "dispute_category",
            "bureau_or_furnisher_path",
            "evidence_packet_ready",
            "repeat_verified_item",
            "escalation_candidate",
            "customer_approved_next_step",
        ],
        actions_to_recommend=[
            "create content around the most common dispute categories",
            "recommend upsell timing after evidence packet creation",
            "identify serious cases for attorney-ready positioning",
            "show where customers need clearer dispute education",
        ],
        alert_growth_ai_when=[
            "many customers have the same dispute category",
            "customers stall before approving dispute next steps",
            "verified items repeat and need Strategy B messaging",
            "escalation candidates increase",
        ],
        owner_brief_line="Dispute AI tells Growth AI which findings create the strongest next-step value.",
    ),
    CrossAiDirective(
        ai_name="Retention AI",
        mission_for_growth="Protect revenue by reducing cancellation risk and increasing customer progress.",
        data_to_send_growth_ai=[
            "customer_stuck",
            "days_since_progress",
            "cancellation_risk",
            "support_issue_count",
            "failed_payment",
            "upgrade_ready",
            "attorney_access_interest",
        ],
        actions_to_recommend=[
            "send progress update drafts for stuck customers",
            "recommend upgrade only when a clear next-step reason exists",
            "identify cancellation reasons for landing page and product fixes",
            "recommend retention content after scan completion",
        ],
        alert_growth_ai_when=[
            "cancellation risk rises",
            "many customers get stuck at the same step",
            "paid customers show no progress for 7 days",
            "support issues repeat after a campaign launch",
        ],
        owner_brief_line="Retention AI tells Growth AI whether new customers are staying and seeing progress.",
    ),
    CrossAiDirective(
        ai_name="Operator AI",
        mission_for_growth="Keep the growth machine working by watching systems, deploys, API health, and broken flows.",
        data_to_send_growth_ai=[
            "website_down",
            "latest_deploy_status",
            "scanner_api_health",
            "lead_capture_errors",
            "payment_webhook_errors",
            "ad_tracking_errors",
            "form_submission_errors",
        ],
        actions_to_recommend=[
            "pause traffic if landing page or scanner is broken",
            "create engineering task when a growth-critical flow fails",
            "verify tracking after every deploy",
            "alert founder when production issues affect leads or revenue",
        ],
        alert_growth_ai_when=[
            "website is down",
            "scanner API health check fails",
            "Join Free form errors appear",
            "payment or tracking events stop",
        ],
        owner_brief_line="Operator AI tells Growth AI when the machine is broken before we spend money sending traffic.",
    ),
    CrossAiDirective(
        ai_name="Compliance Guard AI",
        mission_for_growth="Help Growth AI move fast without using risky claims, confusing promises, or missing approvals.",
        data_to_send_growth_ai=[
            "risky_ad_copy_flag",
            "guarantee_language_flag",
            "attorney_wording_flag",
            "state_launch_review_needed",
            "approval_missing",
            "consent_missing",
            "sensitive_data_exposure_flag",
        ],
        actions_to_recommend=[
            "rewrite risky ad copy in plain, safer language",
            "route legal-sensitive messaging to owner/legal approval",
            "block public launch when disclosures or approvals are missing",
            "recommend safer education-first wording",
        ],
        alert_growth_ai_when=[
            "ad copy makes outcome promises",
            "attorney/legal language is too broad",
            "a state-specific campaign needs review",
            "customer-facing action lacks approval",
        ],
        owner_brief_line="Compliance Guard AI tells Growth AI which growth moves need safer wording or approval.",
    ),
    CrossAiDirective(
        ai_name="Vivo Command AI",
        mission_for_growth="Combine all AI signals into one founder-level growth command brief.",
        data_to_send_growth_ai=[
            "top_growth_action",
            "revenue_gap",
            "paid_customer_gap",
            "system_blockers",
            "approval_queue",
            "weekly_growth_score",
            "12_month_goal_progress",
        ],
        actions_to_recommend=[
            "rank the top three growth actions",
            "show the weekly path to $1M/month",
            "route owner approvals",
            "summarize what each AI found for Growth AI",
        ],
        alert_growth_ai_when=[
            "weekly growth target is missed",
            "revenue gap increases",
            "a cross-AI blocker prevents growth",
            "owner approval is waiting",
        ],
        owner_brief_line="Vivo Command AI keeps Growth AI aligned with the full company mission.",
    ),
]


def directive_to_dict(directive: CrossAiDirective) -> Dict[str, object]:
    return directive.__dict__


def build_cross_ai_growth_directives() -> Dict[str, object]:
    return {
        "ok": True,
        "service": "credit-vivo-cross-ai-growth-directives",
        "mission": "All Credit Vivo AIs support Growth AI's 12-month mission to reach $1,000,000/month revenue by improving qualified leads, scanner completion, paid upgrades, retention, and safe scaling.",
        "growth_ai_role": "Growth AI owns revenue growth strategy. Other AIs feed it signals, warnings, and recommended fixes.",
        "directives": [directive_to_dict(directive) for directive in CROSS_AI_DIRECTIVES],
        "weekly_growth_command_questions": [
            "Which campaign created the most completed scans?",
            "Which source created the most paid upgrades?",
            "Where did customers get stuck?",
            "What broke technically?",
            "What wording or approval risk needs review?",
            "What should be scaled, paused, or fixed this week?",
        ],
    }
