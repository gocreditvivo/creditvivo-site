from growth_live_access import build_live_access_brief


def test_live_access_has_must_have_tools():
    brief = build_live_access_brief()
    names = {tool["name"] for tool in brief["tools"]}

    assert "Credit Vivo first-party event tracking" in names
    assert "Google Analytics 4 Data API" in names
    assert "Google Search Console API" in names
    assert "Stripe API and webhooks" in names
    assert "Supabase Postgres" in names
    assert "Render Cron Jobs" in names


def test_live_access_counts_priorities():
    brief = build_live_access_brief()

    assert brief["ok"] is True
    assert brief["counts"]["tools"] >= 10
    assert brief["counts"]["by_priority"]["phase_1_must_have"] >= 5
    assert brief["service"] == "credit-vivo-growth-live-access-map"


def test_live_access_has_approval_rules():
    brief = build_live_access_brief()
    rules = " ".join(brief["approval_rules"])

    assert "Read-only reporting can be automated" in rules
    assert "owner approval" in rules
    assert "Ad launches" in rules
