from ai_tracking_map import build_ai_tracking_map


def test_ai_tracking_map_includes_all_core_ais():
    tracking = build_ai_tracking_map()
    ai_names = {spec["ai_name"] for spec in tracking["tracking_specs"]}

    assert "Growth AI" in ai_names
    assert "Scanner AI" in ai_names
    assert "Dispute AI" in ai_names
    assert "Retention AI" in ai_names
    assert "Operator AI" in ai_names
    assert "Compliance Guard AI" in ai_names
    assert "Vivo Command AI" in ai_names


def test_ai_tracking_map_includes_minimum_events():
    tracking = build_ai_tracking_map()
    events = tracking["minimum_live_events_to_connect_first"]

    assert "join_clicked" in events
    assert "scan_started" in events
    assert "scan_completed" in events
    assert "paid_upgrade" in events
    assert tracking["shared_owner_dashboard"] == "/owner-ai"


def test_ai_tracking_map_has_owner_questions():
    tracking = build_ai_tracking_map()

    for spec in tracking["tracking_specs"]:
        assert spec["owner_question"]
        assert spec["tracks"]
        assert spec["result_metrics"]
