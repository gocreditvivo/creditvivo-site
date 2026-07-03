from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

try:
    from .bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from .fcra_rights_reference import build_fcra_rights_reference
except ImportError:
    from bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from fcra_rights_reference import build_fcra_rights_reference


class ApprovalLevel(str, Enum):
    AUTO_SAFE = "auto_safe"
    FOUNDER_APPROVAL = "founder_approval"
    COMPLIANCE_APPROVAL = "compliance_approval"
    ATTORNEY_APPROVAL = "attorney_approval"


@dataclass(frozen=True)
class OperatorEvent:
    area: str
    event_type: str
    severity: str
    detail: str
    customer_id: str | None = None


AUTOMATION_POLICY: Dict[str, ApprovalLevel] = {
    "website_health_check": ApprovalLevel.AUTO_SAFE,
    "scanner_health_check": ApprovalLevel.AUTO_SAFE,
    "create_internal_task": ApprovalLevel.AUTO_SAFE,
    "draft_customer_message": ApprovalLevel.AUTO_SAFE,
    "draft_growth_campaign": ApprovalLevel.AUTO_SAFE,
    "security_review": ApprovalLevel.FOUNDER_APPROVAL,
    "send_customer_message": ApprovalLevel.FOUNDER_APPROVAL,
    "change_pricing": ApprovalLevel.FOUNDER_APPROVAL,
    "issue_refund": ApprovalLevel.FOUNDER_APPROVAL,
    "send_dispute_letter": ApprovalLevel.COMPLIANCE_APPROVAL,
    "send_furnisher_letter": ApprovalLevel.COMPLIANCE_APPROVAL,
    "submit_cfpb_complaint": ApprovalLevel.COMPLIANCE_APPROVAL,
    "submit_state_consumer_complaint": ApprovalLevel.COMPLIANCE_APPROVAL,
    "prepare_fcra_regulator_routing": ApprovalLevel.COMPLIANCE_APPROVAL,
    "change_legal_disclosure": ApprovalLevel.ATTORNEY_APPROVAL,
    "refer_to_attorney": ApprovalLevel.ATTORNEY_APPROVAL,
}


def priority_score(event: OperatorEvent) -> int:
    severity_points = {
        "critical": 100,
        "high": 75,
        "medium": 45,
        "low": 20,
    }
    area_points = {
        "security": 30,
        "compliance": 25,
        "scanner": 20,
        "payments": 20,
        "customer": 15,
        "growth": 10,
        "website": 10,
    }
    return severity_points.get(event.severity, 20) + area_points.get(event.area, 0)


def approval_for_action(action_type: str) -> ApprovalLevel:
    return AUTOMATION_POLICY.get(action_type, ApprovalLevel.FOUNDER_APPROVAL)


def recommend_operator_action(event: OperatorEvent) -> Dict[str, object]:
    action_type = "create_internal_task"
    action = "Create an internal review task."

    if event.area == "website" and event.event_type == "down":
        action_type = "website_health_check"
        action = "Recheck site, verify latest deploy, and alert founder if still down."
    elif event.area == "scanner" and event.event_type in {"down", "parse_failed"}:
        action_type = "scanner_health_check"
        action = "Check scanner health, review parse failure, and create engineering task."
    elif event.area == "customer" and event.event_type == "stuck":
        action_type = "draft_customer_message"
        action = "Draft a plain-English progress update for founder approval before sending."
    elif event.area == "payments" and event.event_type == "failed_payment":
        action_type = "draft_customer_message"
        action = "Draft payment update and flag account for billing review."
    elif event.area == "growth" and event.event_type == "campaign_needed":
        action_type = "draft_growth_campaign"
        action = "Draft a campaign test with audience, offer, channel, and success metric."
    elif event.area == "compliance":
        action_type = "prepare_fcra_regulator_routing"
        action = "Prepare FCRA rights, regulator, CFPB/FTC/state, and approval review package before any letter or complaint is sent."
    elif event.area == "security":
        action_type = "security_review"
        action = "Create urgent security task and block automated customer-facing actions."

    approval = approval_for_action(action_type)

    return {
        "area": event.area,
        "event_type": event.event_type,
        "severity": event.severity,
        "detail": event.detail,
        "customer_id": event.customer_id,
        "priority_score": priority_score(event),
        "recommended_action_type": action_type,
        "recommended_action": action,
        "approval_required": approval != ApprovalLevel.AUTO_SAFE,
        "approval_level": approval.value,
    }


def build_operator_brief(events: List[OperatorEvent]) -> Dict[str, object]:
    actions = [recommend_operator_action(event) for event in events]
    actions.sort(key=lambda item: item["priority_score"], reverse=True)
    fcra_rights = build_fcra_rights_reference()
    bureau_reference = build_bureau_debt_collection_reference()

    return {
        "ok": True,
        "service": "credit-vivo-operator-ai",
        "mode": "watch_recommend_approve",
        "automation_rule": "AI may monitor, draft, and create safe internal tasks. Customer-facing, payment, dispute, compliance, and attorney actions require approval.",
        "events_reviewed": len(events),
        "actions": actions,
        "fcra_rights_reference": {
            "plain_english_note": fcra_rights["source_notes"]["plain_english_note"],
            "maryland_rights_summary": fcra_rights["maryland_consumer_rights"]["plain_english_summary"],
            "ai_rules": fcra_rights["ai_rules"],
        },
        "bureau_debt_collection_reference": {
            "experian_outcomes": [item["outcome"] for item in bureau_reference["experian_dispute_outcomes"]],
            "fdcpa_rule_count": len(bureau_reference["fdcpa_collection_rules"]),
            "ai_rules": bureau_reference["ai_rules"],
        },
        "auto_safe_count": sum(1 for action in actions if action["approval_level"] == ApprovalLevel.AUTO_SAFE.value),
        "approval_required_count": sum(1 for action in actions if action["approval_required"]),
    }


def demo_operator_events() -> List[OperatorEvent]:
    return [
        OperatorEvent(
            area="scanner",
            event_type="parse_failed",
            severity="high",
            detail="Three report uploads failed in the last hour.",
        ),
        OperatorEvent(
            area="customer",
            event_type="stuck",
            severity="medium",
            detail="Customer started scan but has no visible next step after 7 days.",
            customer_id="demo_customer_1024",
        ),
        OperatorEvent(
            area="growth",
            event_type="campaign_needed",
            severity="low",
            detail="Auto-loan denial content is getting visits but no campaign exists yet.",
        ),
        OperatorEvent(
            area="compliance",
            event_type="letter_ready",
            severity="high",
            detail="Dispute letter is drafted and needs compliance review before sending.",
            customer_id="demo_customer_2048",
        ),
    ]
