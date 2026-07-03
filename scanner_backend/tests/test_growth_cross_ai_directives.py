from growth_cross_ai_directives import build_cross_ai_growth_directives


def test_cross_ai_directives_include_all_supporting_ais():
    brief = build_cross_ai_growth_directives()
    ai_names = {directive["ai_name"] for directive in brief["directives"]}

    assert "Scanner AI" in ai_names
    assert "Dispute AI" in ai_names
    assert "Retention AI" in ai_names
    assert "Operator AI" in ai_names
    assert "Compliance Guard AI" in ai_names
    assert "Vivo Command AI" in ai_names


def test_cross_ai_directives_support_million_month_mission():
    brief = build_cross_ai_growth_directives()

    assert "$1,000,000/month" in brief["mission"]
    assert brief["growth_ai_role"].startswith("Growth AI owns")
    assert "Which campaign created the most completed scans?" in brief["weekly_growth_command_questions"]


def test_cross_ai_directives_feed_growth_required_data():
    brief = build_cross_ai_growth_directives()
    all_data = " ".join(
        item
        for directive in brief["directives"]
        for item in directive["data_to_send_growth_ai"]
    )

    assert "scan_completed" in all_data
    assert "paid_customer_gap" in all_data
    assert "cancellation_risk" in all_data
    assert "ad_tracking_errors" in all_data
