from letter_lifecycle import (
    LetterLifecycleStatus,
    build_draft_letter,
    build_lifecycle_plan,
    build_lob_packet_preview,
    can_prepare_lob_packet,
    classify_response_text,
    normalize_lifecycle_mode,
    recommend_letter_type,
    recommend_next_step,
)


def sample_issue():
    return {
        "id": "issue_1",
        "issue_type": "collection_review",
        "customer_label": "Collection review",
        "customer_explanation": "Possible report error involving a collector balance.",
        "related_tradeline_ids": ["tl_1"],
        "evidence": [{"id": "ev_1", "bureau": "Experian"}],
    }


def test_recommend_letter_type_from_scanner_issue():
    assert recommend_letter_type(sample_issue()) == "debt_validation"


def test_build_draft_letter_is_safe_and_not_sent():
    letter = build_draft_letter(sample_issue())

    assert letter["status"] == "draft_ready"
    assert letter["send_automatically"] is False
    assert letter["complaint_filing_automated"] is False
    assert letter["customer_approval_required"] is True
    assert letter["admin_review_required"] is True
    assert "DRAFT ONLY" in letter["draft_body"]
    assert "Nothing is sent automatically" in letter["draft_body"]
    assert "not legal advice" in letter["draft_body"]
    assert letter["lifecycle_mode"]["effective_mode"] == "approval_required"
    assert letter["lifecycle_mode"]["send_enabled"] is False


def test_lifecycle_mode_blocks_auto_send_and_uses_auto_prepare():
    mode = normalize_lifecycle_mode("auto_send")

    assert mode["effective_mode"] == "auto_prepare"
    assert mode["send_enabled"] is False
    assert mode["automatic_send_blocked"] is True
    assert "automatic_send_not_allowed" in mode["block_reasons"]


def test_build_lifecycle_plan_has_two_safe_modes():
    approval_plan = build_lifecycle_plan(sample_issue(), "approval_required")
    auto_prepare_plan = build_lifecycle_plan(sample_issue(), "auto_prepare")

    assert approval_plan["mode"]["effective_mode"] == "approval_required"
    assert auto_prepare_plan["mode"]["effective_mode"] == "auto_prepare"
    assert approval_plan["send_available"] is False
    assert auto_prepare_plan["send_available"] is False
    assert auto_prepare_plan["automatic_actions"] == []
    assert auto_prepare_plan["next_required_reviews"] == [
        "customer_review",
        "admin_review",
        "compliance_review",
    ]


def test_lob_packet_blocks_until_all_approvals_exist():
    letter = build_draft_letter(sample_issue())
    packet = build_lob_packet_preview(letter)

    assert packet["blocked"] is True
    assert "customer_approval_required" in packet["block_reasons"]
    assert "admin_review_required" in packet["block_reasons"]
    assert "compliance_review_approved_required" in packet["block_reasons"]
    assert packet["lob_status"] == "not_submitted"
    assert packet["lob_id"] is None


def test_lob_packet_can_be_ready_after_approval_gates():
    letter = build_draft_letter(sample_issue())
    letter["status"] = LetterLifecycleStatus.ADMIN_APPROVED.value
    packet = build_lob_packet_preview(
        letter,
        {
            "customer_id": "customer_1",
            "report_id": "report_1",
            "recipient_name": "Experian",
            "recipient_address": {"line1": "PO Box"},
            "sender_name": "Client Name",
            "sender_address": {"line1": "Client Address"},
            "letter_html_or_pdf_reference": "letters/letter_1.pdf",
            "customer_approval_timestamp": "2026-07-01T12:00:00+00:00",
            "admin_approval_timestamp": "2026-07-01T13:00:00+00:00",
            "compliance_review_status": "approved",
        },
    )

    assert packet["blocked"] is False
    assert packet["block_reasons"] == []


def test_can_prepare_lob_packet_returns_block_reasons():
    can_prepare, reasons = can_prepare_lob_packet("draft_ready", False, True, "approved")

    assert can_prepare is False
    assert "letter_status_not_approval_ready" in reasons
    assert "customer_approval_required" in reasons


def test_classify_response_text_and_next_step():
    classification = classify_response_text("We verified this account as accurate and it remains unchanged.")
    next_step = recommend_next_step(classification)

    assert classification == "verified"
    assert next_step["recommended_status"] == "response_review_pending"
    assert next_step["automatic_action_taken"] == "none"


def test_response_classifier_handles_removed_and_no_response():
    assert classify_response_text("This item has been removed from your credit file.") == "removed"
    assert classify_response_text("") == "no_response"
