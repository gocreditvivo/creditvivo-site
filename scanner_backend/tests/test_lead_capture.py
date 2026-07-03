from pathlib import Path

import pytest

from lead_capture import append_lead, build_lead, read_leads, summarize_leads


def test_build_lead_requires_valid_email_and_consent():
    lead = build_lead({
        "email": "Jane@example.com",
        "first_name": "Jane",
        "goal": "Buy a car",
        "campaign": "auto-loan-denial",
        "source": "campaign_join_page",
        "consent_to_contact": True,
    })

    assert lead.email == "jane@example.com"
    assert lead.consent_to_contact is True
    assert lead.campaign == "auto-loan-denial"


def test_build_lead_rejects_bad_email():
    with pytest.raises(ValueError, match="valid email"):
        build_lead({
            "email": "bad-email",
            "first_name": "Jane",
            "goal": "Buy a car",
            "consent_to_contact": True,
        })


def test_build_lead_requires_contact_consent():
    with pytest.raises(ValueError, match="Consent"):
        build_lead({
            "email": "jane@example.com",
            "first_name": "Jane",
            "goal": "Buy a car",
            "consent_to_contact": False,
        })


def test_lead_log_round_trip_and_summary(tmp_path: Path):
    lead_file = tmp_path / "leads.jsonl"
    append_lead(build_lead({
        "email": "jane@example.com",
        "first_name": "Jane",
        "goal": "Buy a car",
        "campaign": "auto-loan-denial",
        "source": "campaign_join_page",
        "consent_to_contact": True,
    }), lead_file)

    leads = read_leads(lead_file)
    summary = summarize_leads(leads)

    assert len(leads) == 1
    assert summary["lead_count"] == 1
    assert summary["by_campaign"]["auto-loan-denial"] == 1
    assert summary["by_goal"]["Buy a car"] == 1
