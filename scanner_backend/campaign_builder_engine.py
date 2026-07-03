from __future__ import annotations

from typing import Any

try:
    from .rules_engine import get_rule_pack
except ImportError:
    from rules_engine import get_rule_pack


CAMPAIGN_TYPES = [
    "Rent Ready",
    "Mortgage Ready",
    "Auto Loan Ready",
    "Better Credit, Better Options",
    "Free Credit Report Education",
    "Negative Account Review",
    "Attorney Support Awareness",
    "Partner Referral Campaign",
    "Re-Engagement Campaign",
]


def compliance_check_message(message: str, channel: str = "general") -> dict[str, Any]:
    rules = get_rule_pack("growth_compliance_rules")
    lowered = (message or "").lower()
    blocked = [phrase for phrase in rules.get("blocked_phrases", []) if phrase.lower() in lowered]
    attorney_wording = rules.get("attorney_wording")
    attorney_wording_required = "attorney" in lowered and attorney_wording not in message
    return {
        "ok": not blocked and not attorney_wording_required,
        "channel": channel,
        "blocked_phrases": blocked,
        "attorney_wording_required": attorney_wording_required,
        "required_attorney_wording": attorney_wording if attorney_wording_required else None,
        "safe_phrases": rules.get("safe_phrases", []),
        "guardrails": rules.get("guardrails", []),
        "approval_required": True,
    }


def build_campaign(
    campaign_goal: str,
    audience: str,
    channel: str,
    language: str = "en",
) -> dict[str, Any]:
    goal = campaign_goal.strip() or "Better Credit, Better Options"
    audience_value = audience.strip() or "Credit Vivo prospects"
    channel_value = channel.strip().lower() or "email"
    headline = goal if goal in CAMPAIGN_TYPES else f"{goal} Campaign"
    body = (
        f"{audience_value}: review possible report errors, understand credit readiness, "
        "and remember that results vary. Accurate, current, and verifiable information may remain."
    )
    if "attorney" in goal.lower():
        body += " Attorney support may be available for eligible unresolved credit-reporting issues."

    check = compliance_check_message(body, channel_value)
    return {
        "ok": True,
        "service": "cv-market-growth-ai",
        "campaign_goal": goal,
        "campaign_type": goal if goal in CAMPAIGN_TYPES else "Better Credit, Better Options",
        "audience": audience_value,
        "channel": channel_value,
        "language": language,
        "status": "draft_ready",
        "approval_required": True,
        "can_send_now": False,
        "draft": {
            "headline": headline,
            "message": body,
            "call_to_action": "Start with a Credit Vivo review.",
        },
        "compliance": check,
        "next_step": "Founder review and compliance approval required before publishing or outreach.",
    }
