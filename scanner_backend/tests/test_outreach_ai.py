from outreach_ai import build_outreach_plan, compile_partner_contacts


CONTACTS = [
    {
        "name": "Virginia Auto Dealers Association",
        "partner_type": "Auto dealer association",
        "email": "TeamVADA@vada.com",
        "fit_reason": "Dealers see customers denied for financing.",
        "source": "public_business_contact",
    },
    {
        "name": "Duplicate",
        "partner_type": "Auto dealer association",
        "email": "teamvada@vada.com",
        "fit_reason": "Duplicate email should be skipped.",
        "source": "public_business_contact",
    },
    {
        "name": "Missing email",
        "partner_type": "Realtor association",
        "email": "",
        "fit_reason": "Missing email should be skipped.",
        "source": "public_business_contact",
    },
]


def test_compile_partner_contacts_deduplicates_and_skips_missing_email():
    contacts = compile_partner_contacts(CONTACTS)

    assert len(contacts) == 1
    assert contacts[0].email == "teamvada@vada.com"


def test_outreach_plan_notifies_owner_and_blocks_without_approval():
    plan = build_outreach_plan(CONTACTS)

    assert plan["ok"] is True
    assert plan["workflow"] == "compile_notify_execute"
    assert plan["owner_notification"]["approval_required"] is True
    assert plan["execution_queue"]["can_send_now"] is False
    assert plan["execution_queue"]["tasks"][0]["status"] == "approval_required"


def test_outreach_plan_executes_only_after_owner_approval():
    plan = build_outreach_plan(CONTACTS, owner_approved=True)

    assert plan["execution_queue"]["can_send_now"] is False
    assert plan["execution_queue"]["automatic_sending"] is False
    assert plan["execution_queue"]["status"] == "ready_for_owner_export"
    assert plan["execution_queue"]["tasks"][0]["action"] == "owner_approved_partner_outreach_draft"
    assert plan["execution_queue"]["tasks"][0]["status"] == "ready_for_manual_export"
