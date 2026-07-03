from growth_ads_ai import build_ad_plan


def test_growth_ads_ai_creates_multi_channel_ad_plan():
    plan = build_ad_plan()

    assert plan["ok"] is True
    assert plan["counts"]["channels"] >= 7
    assert plan["counts"]["ad_creatives"] >= 8
    assert "Google Search" in plan["counts"]["creative_by_channel"]


def test_growth_ads_ai_requires_approval_before_spend():
    plan = build_ad_plan()

    assert "approval is required before launch or spend" in plan["guardrail"]
    assert plan["mode"] == "draft_review_launch_measure"


def test_growth_ads_ai_uses_compliant_customer_facing_language():
    plan = build_ad_plan()
    all_copy = " ".join(
        f"{creative['headline']} {creative['body']} {creative['compliance_note']}"
        for creative in plan["ad_creatives"]
    ).lower()

    assert "no hard pull" in all_copy
    assert "no guarantee" in all_copy
    assert "delete negative items" not in all_copy
    assert "boost your score" not in all_copy
