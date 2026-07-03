from __future__ import annotations

from typing import Any


LEAD_CATEGORIES = [
    "Rent Ready",
    "Mortgage Ready",
    "Auto Loan Ready",
    "Credit Card Ready",
    "Business Funding Ready",
    "General Credit Review",
    "Attorney Support Review",
]


def _has_signal(lead_data: dict[str, Any], *keys: str) -> bool:
    return any(bool(lead_data.get(key)) for key in keys)


def score_lead(lead_data: dict[str, Any]) -> dict[str, Any]:
    goal = str(lead_data.get("goal") or lead_data.get("category") or "").lower()
    source = str(lead_data.get("source") or "").lower()
    matched: list[dict[str, Any]] = []
    score = 0

    scoring_rules = [
        ("uploaded_report", 25, "Uploaded or started a credit report review."),
        ("denied_for_credit", 25, "Reported a recent denial or urgent credit need."),
        ("viewed_pricing", 15, "Viewed pricing or paid options."),
        ("referral_partner", 15, "Came through a trust-based referral source."),
        ("consent_to_contact", 10, "Provided consent for follow-up."),
        ("attorney_support_interest", 10, "May need unresolved issue review."),
    ]
    for key, points, reason in scoring_rules:
        if _has_signal(lead_data, key):
            score += points
            matched.append({"signal": key, "points": points, "reason": reason})

    if "rent" in goal or "apartment" in goal:
        category = "Rent Ready"
        score += 10
    elif "mortgage" in goal or "home" in goal:
        category = "Mortgage Ready"
        score += 10
    elif "auto" in goal or "car" in goal:
        category = "Auto Loan Ready"
        score += 10
    elif "card" in goal:
        category = "Credit Card Ready"
        score += 5
    elif "business" in goal or "funding" in goal:
        category = "Business Funding Ready"
        score += 10
    elif "attorney" in goal or _has_signal(lead_data, "attorney_support_interest"):
        category = "Attorney Support Review"
        score += 10
    else:
        category = "General Credit Review"

    if "partner" in source or _has_signal(lead_data, "referral_partner"):
        score += 5

    if score >= 70:
        priority = "high"
    elif score >= 35:
        priority = "medium"
    else:
        priority = "low"

    return {
        "ok": True,
        "score": min(score, 100),
        "priority": priority,
        "category": category,
        "matched_signals": matched,
        "approval_required_before_outreach": True,
    }


def recommend_next_action(lead_data: dict[str, Any]) -> dict[str, Any]:
    lead = score_lead(lead_data)
    category = lead["category"]
    if lead["priority"] == "high":
        action = "Create a founder-reviewed follow-up draft and review scanner status."
    elif category in {"Rent Ready", "Mortgage Ready", "Auto Loan Ready"}:
        action = f"Prepare a {category} education draft with results-vary language."
    else:
        action = "Invite the customer to complete a credit report review after consent is verified."
    return {
        "ok": True,
        "lead_score": lead,
        "recommended_action": action,
        "status": "founder_review_pending",
        "can_contact_now": False,
        "guardrail": "No customer outreach is sent automatically.",
    }
