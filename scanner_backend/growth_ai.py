from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GrowthSnapshot:
    visitors: int = 0
    leads: int = 0
    free_scans_started: int = 0
    free_scans_completed: int = 0
    paid_customers: int = 0
    monthly_recurring_revenue: float = 0.0
    cancellations: int = 0
    ad_spend: float = 0.0
    referral_signups: int = 0


def percent(numerator: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def money_per_item(amount: float, count: int) -> float:
    if count <= 0:
        return 0.0
    return round(amount / count, 2)


def score_growth_health(snapshot: GrowthSnapshot) -> Dict[str, float]:
    return {
        "visitor_to_lead_rate": percent(snapshot.leads, snapshot.visitors),
        "lead_to_scan_start_rate": percent(snapshot.free_scans_started, snapshot.leads),
        "scan_completion_rate": percent(snapshot.free_scans_completed, snapshot.free_scans_started),
        "free_scan_to_paid_rate": percent(snapshot.paid_customers, snapshot.free_scans_completed),
        "monthly_churn_signal": percent(snapshot.cancellations, max(snapshot.paid_customers, 1)),
        "cost_per_lead": money_per_item(snapshot.ad_spend, snapshot.leads),
        "cost_per_paid_customer": money_per_item(snapshot.ad_spend, snapshot.paid_customers),
    }


def lead_score(signals: Dict[str, bool]) -> Dict[str, object]:
    scoring_rules = [
        ("denied_for_credit", 30, "Clear urgent pain point"),
        ("started_scan", 25, "Took action inside Credit Vivo"),
        ("viewed_pricing", 20, "Considering paid help"),
        ("viewed_attorney_access", 20, "May need escalation"),
        ("read_dispute_content", 15, "Researching a credit problem"),
        ("referral_partner", 15, "Came through trust-based channel"),
        ("unfinished_scan", 10, "Warm lead needing follow-up"),
    ]

    matched = []
    total = 0
    for key, points, reason in scoring_rules:
        if signals.get(key, False):
            total += points
            matched.append({"signal": key, "points": points, "reason": reason})

    if total >= 70:
        priority = "high"
    elif total >= 35:
        priority = "medium"
    else:
        priority = "low"

    return {"score": total, "priority": priority, "matched_signals": matched}


def recommend_growth_actions(snapshot: GrowthSnapshot) -> List[Dict[str, str]]:
    metrics = score_growth_health(snapshot)
    actions: List[Dict[str, str]] = []

    if snapshot.visitors == 0:
        actions.append({
            "issue": "No traffic data yet",
            "insight": "Growth AI cannot optimize without visitor and source tracking.",
            "action": "Connect analytics, Join Free clicks, scan starts, and referral source tracking.",
        })
        return actions

    if metrics["visitor_to_lead_rate"] < 3:
        actions.append({
            "issue": "Low visitor-to-lead conversion",
            "insight": "People may not understand the free Credit Check-In fast enough.",
            "action": "Test clearer homepage and article calls-to-action for Join Free.",
        })

    if snapshot.leads > 0 and metrics["lead_to_scan_start_rate"] < 25:
        actions.append({
            "issue": "Leads are not starting the scanner",
            "insight": "The first scanner step may feel unclear or too much work.",
            "action": "Simplify scanner start and add plain-English trust text before upload.",
        })

    if snapshot.free_scans_started > 0 and metrics["scan_completion_rate"] < 60:
        actions.append({
            "issue": "Scans are not being completed",
            "insight": "Customers may be dropping off during upload or report review.",
            "action": "Send an approved reminder and show a progress state after scan start.",
        })

    if snapshot.free_scans_completed > 0 and metrics["free_scan_to_paid_rate"] < 8:
        actions.append({
            "issue": "Free users are not upgrading",
            "insight": "Customers may not see why paid guidance or escalation matters.",
            "action": "Add a plain-English next-step summary after findings with AI Guided and Vivo Plus options.",
        })

    if metrics["monthly_churn_signal"] > 8:
        actions.append({
            "issue": "Cancellation risk is high",
            "insight": "Customers may cancel before seeing visible progress.",
            "action": "Trigger retention updates for customers with no visible progress in 7 days.",
        })

    if snapshot.ad_spend > 0 and metrics["cost_per_paid_customer"] > 150:
        actions.append({
            "issue": "Paid acquisition may be too expensive",
            "insight": "Ads are not converting profitably yet.",
            "action": "Pause weak campaigns and prioritize referral partners and search content.",
        })

    if not actions:
        actions.append({
            "issue": "Growth funnel is healthy",
            "insight": "The current funnel has no major rule-based warning.",
            "action": "Scale the best channel carefully and keep watching cancellation risk.",
        })

    return actions


def build_growth_brief(snapshot: GrowthSnapshot) -> Dict[str, object]:
    million_goal = 1000000
    blended_arpu = 95
    paid_needed = (million_goal + blended_arpu - 1) // blended_arpu
    current_gap = max(int(paid_needed - snapshot.paid_customers), 0)

    return {
        "ok": True,
        "service": "credit-vivo-growth-ai",
        "mode": "rule_based_foundation",
        "disclaimer": "This engine recommends growth actions. It does not guarantee revenue.",
        "snapshot": snapshot.__dict__,
        "metrics": score_growth_health(snapshot),
        "million_month_target": {
            "monthly_goal": million_goal,
            "blended_arpu": blended_arpu,
            "paid_customers_needed": int(paid_needed),
            "current_paid_customers": snapshot.paid_customers,
            "paid_customer_gap": current_gap,
        },
        "recommended_actions": recommend_growth_actions(snapshot),
        "next_data_to_connect": [
            "website visitors by source",
            "Join Free clicks",
            "scan started",
            "scan completed",
            "paid upgrade",
            "cancellation",
            "ad spend",
            "referral partner source",
        ],
    }
