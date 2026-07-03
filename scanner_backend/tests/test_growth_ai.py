from growth_ai import GrowthSnapshot, build_growth_brief, lead_score, score_growth_health


def test_growth_health_metrics_calculate_funnel_rates():
    snapshot = GrowthSnapshot(
        visitors=1000,
        leads=100,
        free_scans_started=50,
        free_scans_completed=25,
        paid_customers=5,
        cancellations=1,
        ad_spend=500,
    )

    metrics = score_growth_health(snapshot)

    assert metrics["visitor_to_lead_rate"] == 10
    assert metrics["lead_to_scan_start_rate"] == 50
    assert metrics["scan_completion_rate"] == 50
    assert metrics["free_scan_to_paid_rate"] == 20
    assert metrics["cost_per_lead"] == 5
    assert metrics["cost_per_paid_customer"] == 100


def test_lead_score_flags_high_priority_customer():
    result = lead_score({
        "denied_for_credit": True,
        "started_scan": True,
        "viewed_pricing": True,
    })

    assert result["score"] == 75
    assert result["priority"] == "high"
    assert len(result["matched_signals"]) == 3


def test_growth_brief_recommends_tracking_when_no_traffic():
    brief = build_growth_brief(GrowthSnapshot())

    assert brief["ok"] is True
    assert brief["mode"] == "rule_based_foundation"
    assert brief["million_month_target"]["paid_customers_needed"] == 10527
    assert brief["recommended_actions"][0]["issue"] == "No traffic data yet"
    assert "Join Free clicks" in brief["next_data_to_connect"]


def test_growth_brief_flags_low_upgrade_rate():
    brief = build_growth_brief(
        GrowthSnapshot(
            visitors=10000,
            leads=1000,
            free_scans_started=500,
            free_scans_completed=400,
            paid_customers=10,
        )
    )

    issues = {action["issue"] for action in brief["recommended_actions"]}

    assert "Free users are not upgrading" in issues
