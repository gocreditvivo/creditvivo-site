from __future__ import annotations

from typing import Any

try:
    from .rules_engine import get_rule_pack
except ImportError:
    from rules_engine import get_rule_pack


def recommend_market_opportunities(
    location: str = "DMV",
    product_focus: str | None = None,
) -> dict[str, Any]:
    rules = get_rule_pack("market_ai_rules")
    focus = (product_focus or "").strip().lower()
    segments = rules.get("market_segments", [])
    if focus:
        filtered = [
            segment for segment in segments
            if focus in str(segment.get("name", "")).lower()
            or focus in str(segment.get("audience", "")).lower()
        ]
    else:
        filtered = segments
    if not filtered:
        filtered = segments[:2]
    return {
        "ok": True,
        "service": "cv-market-growth-ai",
        "location": location or rules.get("default_location", "DMV"),
        "product_focus": product_focus,
        "opportunities": filtered,
        "competitor_learning_rules": rules.get("competitor_learning_rules", []),
        "approval_required_before_campaign_launch": True,
    }
