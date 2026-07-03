from growth_forensic_search import build_forensic_search_brief, run_forensic_search


def test_forensic_search_brief_has_core_lanes():
    brief = build_forensic_search_brief()
    lane_names = {lane["name"] for lane in brief["lanes"]}

    assert "Credit report error demand" in lane_names
    assert "Auto loan denial demand" in lane_names
    assert "Mortgage readiness demand" in lane_names
    assert "Competitor weakness search" in lane_names


def test_forensic_search_run_maps_query_to_auto_lane():
    result = run_forensic_search("Find auto loan denial demand")

    assert result["ok"] is True
    assert result["selected_lanes"][0]["campaign_mapping"] == "/auto-loan-denial"
    assert "metric_to_watch" in result["output_fields"]


def test_forensic_search_run_returns_owner_brief():
    result = run_forensic_search("Find competitor complaint weaknesses")

    assert result["owner_brief"]["campaign_to_use"]
    assert "Join Free" in result["owner_brief"]["next_action"]
    assert result["service"] == "credit-vivo-growth-forensic-search"
