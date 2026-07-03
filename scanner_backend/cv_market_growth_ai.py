from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .campaign_builder_engine import build_campaign, compliance_check_message
    from .consent_log_engine import log_consent
    from .growth_approval_queue import create_approval_item
    from .lead_intelligence_engine import recommend_next_action, score_lead
    from .market_ai import recommend_market_opportunities
    from .partner_referral_engine import track_partner_referral
    from .revenue_attribution_engine import attribute_revenue
except ImportError:
    from campaign_builder_engine import build_campaign, compliance_check_message
    from consent_log_engine import log_consent
    from growth_approval_queue import create_approval_item
    from lead_intelligence_engine import recommend_next_action, score_lead
    from market_ai import recommend_market_opportunities
    from partner_referral_engine import track_partner_referral
    from revenue_attribution_engine import attribute_revenue


DASHBOARD_KEYS = [
    "new_leads",
    "report_uploads",
    "scanner_completions",
    "dispute_approvals_pending",
    "campaign_drafts_pending_approval",
    "partner_referrals",
    "campaign_conversions",
    "estimated_monthly_recurring_revenue",
    "churn_refund_watch",
    "compliance_flags",
    "recommended_next_actions",
]


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def get_growth_dashboard(storage_dir: Path | None = None) -> dict[str, Any]:
    metrics = {key: 0 for key in DASHBOARD_KEYS if key != "recommended_next_actions"}
    if storage_dir is not None:
        metrics["new_leads"] = _count_jsonl(storage_dir / "leads" / "captured_leads.jsonl")
        metrics["partner_referrals"] = _count_jsonl(storage_dir / "growth" / "partner_referrals.jsonl")
        metrics["campaign_drafts_pending_approval"] = _count_jsonl(storage_dir / "growth" / "approval_queue.jsonl")
        metrics["estimated_monthly_recurring_revenue"] = _sum_revenue(storage_dir / "growth" / "revenue_attribution.jsonl")
    metrics["recommended_next_actions"] = [
        "Review campaign drafts pending founder approval.",
        "Prioritize referral partners tied to Rent Ready, Mortgage Ready, and Auto Loan Ready.",
        "Keep compliance review logged before customer-facing outreach.",
    ]
    return {
        "ok": True,
        "service": "cv-market-growth-ai",
        "mode": "founder_side_command_center",
        "dashboard": metrics,
        "guardrail": "AI recommends. Founder approves. No public or customer outreach is automatic.",
    }


def _sum_revenue(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = 0.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        total += float(json.loads(line).get("amount", 0.0))
    return round(total, 2)


def generate_founder_summary(storage_dir: Path | None = None) -> dict[str, Any]:
    dashboard = get_growth_dashboard(storage_dir)
    return {
        "ok": True,
        "service": "cv-market-growth-ai",
        "summary": "CV Market/Growth AI is ready to recommend leads, campaigns, referrals, and revenue actions for founder review.",
        "dashboard": dashboard["dashboard"],
        "required_review": [
            "Founder approval before public posting.",
            "Founder approval before customer or partner outreach.",
            "Admin review before disputes, letters, complaints, or escalation.",
        ],
    }
