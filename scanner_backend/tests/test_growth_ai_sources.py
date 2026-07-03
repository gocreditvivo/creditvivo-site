from growth_ai_sources import build_growth_source_brief


def test_growth_ai_sources_include_safe_public_partner_leads():
    brief = build_growth_source_brief()

    assert brief["ok"] is True
    assert brief["counts"]["public_partner_leads"] >= 10
    assert "Do not scrape or email private consumers" in brief["guardrail"]


def test_growth_ai_sources_include_owned_and_public_data_sources():
    brief = build_growth_source_brief()
    categories = {source["category"] for source in brief["data_sources"]}

    assert "owned_website" in categories
    assert "owned_analytics" in categories
    assert "public_partner_directory" in categories


def test_growth_ai_sources_include_market_signal_sources_with_blocks():
    brief = build_growth_source_brief()
    market_categories = {source["category"] for source in brief["market_signal_sources"]}
    blocked_uses = " ".join(source["blocked_use"] for source in brief["market_signal_sources"])

    assert "government_complaint_data" in market_categories
    assert "public_record_high_sensitivity" in market_categories
    assert "public_discussion_research" in market_categories
    assert "search_demand" in market_categories
    assert "Do not build a direct marketing list" in blocked_uses
    assert "Do not scrape usernames" in blocked_uses


def test_growth_ai_sources_map_leads_to_campaign_pages():
    brief = build_growth_source_brief()
    campaigns = brief["counts"]["recommended_campaigns"]

    assert "/auto-loan-denial" in campaigns
    assert "/mortgage-readiness" in campaigns
    assert "/collection-not-mine" in campaigns
