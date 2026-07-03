from pathlib import Path

from event_collector import (
    append_event,
    build_event,
    growth_snapshot_from_events,
    operator_events_from_vivo_events,
    read_events,
    summarize_events,
)


def test_event_log_round_trip(tmp_path: Path):
    event_file = tmp_path / "events.jsonl"
    event = build_event({
        "event_type": "paid_upgrade",
        "source": "pricing_page",
        "customer_id": "customer_1",
        "amount": 59,
    })

    append_event(event, event_file)
    events = read_events(event_file)

    assert len(events) == 1
    assert events[0].event_type == "paid_upgrade"
    assert events[0].amount == 59


def test_growth_snapshot_from_events_counts_funnel():
    events = [
        build_event({"event_type": "website_visit", "source": "google"}),
        build_event({"event_type": "lead_created", "source": "google"}),
        build_event({"event_type": "scan_started", "source": "scanner"}),
        build_event({"event_type": "scan_completed", "source": "scanner"}),
        build_event({"event_type": "paid_upgrade", "source": "pricing", "amount": 29}),
        build_event({"event_type": "ad_spend", "source": "google_ads", "amount": 100}),
        build_event({"event_type": "customer_cancelled", "source": "billing"}),
        build_event({"event_type": "referral_signup", "source": "partner"}),
    ]

    snapshot = growth_snapshot_from_events(events)

    assert snapshot.visitors == 1
    assert snapshot.leads == 2
    assert snapshot.free_scans_started == 1
    assert snapshot.free_scans_completed == 1
    assert snapshot.paid_customers == 1
    assert snapshot.monthly_recurring_revenue == 29
    assert snapshot.ad_spend == 100
    assert snapshot.referral_signups == 1


def test_operator_events_from_vivo_events_flags_sensitive_work():
    events = [
        build_event({"event_type": "scan_failed", "source": "scanner", "customer_id": "customer_1"}),
        build_event({"event_type": "dispute_letter_ready", "source": "scanner", "customer_id": "customer_2"}),
    ]

    operator_events = operator_events_from_vivo_events(events)

    assert len(operator_events) == 2
    assert operator_events[0].area == "scanner"
    assert operator_events[1].area == "compliance"


def test_summarize_events_groups_by_type_and_source():
    events = [
        build_event({"event_type": "website_visit", "source": "google"}),
        build_event({"event_type": "website_visit", "source": "google"}),
        build_event({"event_type": "lead_created", "source": "facebook"}),
    ]

    summary = summarize_events(events)

    assert summary["event_count"] == 3
    assert summary["by_type"]["website_visit"] == 2
    assert summary["by_source"]["google"] == 2
