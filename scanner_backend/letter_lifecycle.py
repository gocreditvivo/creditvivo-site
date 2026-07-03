from __future__ import annotations

"""
Credit Vivo v18 Letter Lifecycle foundation.

Pure service module only. It prepares draft-only recommendations, approval-gated
Lob packet previews, and response classifications. It does not send mail, file
complaints, call Lob, or use paid AI APIs.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class LetterLifecycleStatus(str, Enum):
    SCAN_COMPLETED = "scan_completed"
    DRAFT_READY = "draft_ready"
    CUSTOMER_REVIEW_PENDING = "customer_review_pending"
    CUSTOMER_APPROVED = "customer_approved"
    CUSTOMER_REJECTED = "customer_rejected"
    ADMIN_REVIEW_PENDING = "admin_review_pending"
    ADMIN_APPROVED = "admin_approved"
    LOB_PACKET_READY = "lob_packet_ready"
    SENT_TO_LOB = "sent_to_lob"
    MAILED = "mailed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RESPONSE_WAITING = "response_waiting"
    RESPONSE_UPLOADED = "response_uploaded"
    RESPONSE_REVIEW_PENDING = "response_review_pending"
    NEXT_STEP_RECOMMENDED = "next_step_recommended"
    RESOLVED_UPDATED = "resolved_updated"
    RESOLVED_REMOVED = "resolved_removed"
    RESOLVED_VERIFIED = "resolved_verified"
    NO_RESPONSE_REVIEW_NEEDED = "no_response_review_needed"
    COMPLAINT_PACKET_READY = "complaint_packet_ready"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class LetterType(str, Enum):
    BUREAU_REVIEW_DISPUTE = "bureau_review_dispute"
    FURNISHER_DIRECT_DISPUTE = "furnisher_direct_dispute"
    DEBT_VALIDATION = "debt_validation"
    REINVESTIGATION = "reinvestigation"
    METHOD_OF_VERIFICATION = "method_of_verification"
    DOCUMENTED_FOLLOW_UP = "documented_follow_up"
    COMPLAINT_PREPARATION_PACKET = "complaint_preparation_packet"


class ResponseClassification(str, Enum):
    VERIFIED = "verified"
    UPDATED = "updated"
    REMOVED = "removed"
    PARTIALLY_UPDATED = "partially_updated"
    REQUEST_FOR_MORE_INFORMATION = "request_for_more_information"
    FRIVOLOUS_OR_IRRELEVANT_NOTICE = "frivolous_or_irrelevant_notice"
    NO_RESPONSE = "no_response"
    UNKNOWN_NEEDS_ADMIN_REVIEW = "unknown_needs_admin_review"


class LetterLifecycleMode(str, Enum):
    APPROVAL_REQUIRED = "approval_required"
    AUTO_PREPARE = "auto_prepare"


@dataclass
class DraftLetter:
    letter_id: str
    letter_type: str
    issue_id: str
    status: str
    subject: str
    recipient_type: str
    account_ids: list[str] = field(default_factory=list)
    issue_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    draft_body: str = ""
    customer_approval_required: bool = True
    admin_review_required: bool = True
    compliance_review_required: bool = True
    send_automatically: bool = False
    complaint_filing_automated: bool = False
    legal_advice: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class LobPacketPreview:
    customer_id: str
    report_id: str
    letter_id: str
    letter_type: str
    recipient_type: str
    recipient_name: str
    recipient_address: dict[str, str]
    sender_name: str
    sender_address: dict[str, str]
    account_ids: list[str]
    issue_ids: list[str]
    evidence_ids: list[str]
    letter_html_or_pdf_reference: str
    customer_approval_timestamp: str | None
    admin_approval_timestamp: str | None
    compliance_review_status: str
    lob_id: str | None = None
    lob_status: str = "not_submitted"
    delivery_event_log: list[dict[str, Any]] = field(default_factory=list)
    blocked: bool = True
    block_reasons: list[str] = field(default_factory=list)


def _safe_text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def normalize_lifecycle_mode(requested_mode: str | None) -> dict[str, Any]:
    mode = _safe_text(requested_mode, LetterLifecycleMode.APPROVAL_REQUIRED.value).lower()
    if mode in {"auto_send", "autosend", "send_automatically", "automatic_send"}:
        return {
            "requested_mode": requested_mode,
            "effective_mode": LetterLifecycleMode.AUTO_PREPARE.value,
            "send_enabled": False,
            "automatic_send_blocked": True,
            "block_reasons": [
                "automatic_send_not_allowed",
                "customer_approval_required",
                "admin_review_required",
                "compliance_review_approved_required",
            ],
            "message": "Auto-send is not available. Credit Vivo can auto-prepare drafts and packet previews only.",
        }
    if mode == LetterLifecycleMode.AUTO_PREPARE.value:
        return {
            "requested_mode": requested_mode,
            "effective_mode": LetterLifecycleMode.AUTO_PREPARE.value,
            "send_enabled": False,
            "automatic_send_blocked": True,
            "block_reasons": ["sending_requires_customer_admin_and_compliance_approval"],
            "message": "Drafts and packet previews can be prepared, but nothing is sent automatically.",
        }
    return {
        "requested_mode": requested_mode,
        "effective_mode": LetterLifecycleMode.APPROVAL_REQUIRED.value,
        "send_enabled": False,
        "automatic_send_blocked": True,
        "block_reasons": ["manual_approval_workflow"],
        "message": "Drafts wait for customer approval, admin review, and compliance approval.",
    }


def _issue_blob(issue_data: dict[str, Any]) -> str:
    parts = [
        issue_data.get("issue_type", ""),
        issue_data.get("customer_label", ""),
        issue_data.get("customer_explanation", ""),
        issue_data.get("admin_explanation", ""),
    ]
    return " ".join(_safe_text(part).lower() for part in parts)


def recommend_letter_type(issue_data: dict[str, Any]) -> str:
    blob = _issue_blob(issue_data)
    if "debt validation" in blob or "collection" in blob or "collector" in blob or "debt buyer" in blob:
        return LetterType.DEBT_VALIDATION.value
    if "verified" in blob or "method of verification" in blob:
        return LetterType.METHOD_OF_VERIFICATION.value
    if "reinvestigation" in blob or "reinvestigate" in blob:
        return LetterType.REINVESTIGATION.value
    if "furnisher" in blob or "direct dispute" in blob:
        return LetterType.FURNISHER_DIRECT_DISPUTE.value
    if "complaint" in blob or "no response" in blob:
        return LetterType.COMPLAINT_PREPARATION_PACKET.value
    if "follow" in blob:
        return LetterType.DOCUMENTED_FOLLOW_UP.value
    return LetterType.BUREAU_REVIEW_DISPUTE.value


def _recipient_type_for(letter_type: str) -> str:
    if letter_type == LetterType.DEBT_VALIDATION.value:
        return "debt_collector_or_debt_buyer"
    if letter_type == LetterType.FURNISHER_DIRECT_DISPUTE.value:
        return "furnisher"
    if letter_type == LetterType.COMPLAINT_PREPARATION_PACKET.value:
        return "internal_compliance_review"
    return "credit_bureau"


def _letter_subject(letter_type: str, issue_data: dict[str, Any]) -> str:
    account_name = _safe_text(issue_data.get("account_name") or issue_data.get("customer_label"), "report item")
    subjects = {
        LetterType.BUREAU_REVIEW_DISPUTE.value: "Draft bureau review request",
        LetterType.FURNISHER_DIRECT_DISPUTE.value: "Draft furnisher direct dispute",
        LetterType.DEBT_VALIDATION.value: "Draft debt validation request",
        LetterType.REINVESTIGATION.value: "Draft reinvestigation request",
        LetterType.METHOD_OF_VERIFICATION.value: "Draft method of verification request",
        LetterType.DOCUMENTED_FOLLOW_UP.value: "Draft documented follow-up package",
        LetterType.COMPLAINT_PREPARATION_PACKET.value: "Draft complaint preparation packet",
    }
    return f"{subjects.get(letter_type, 'Draft review request')} - {account_name}"


def build_draft_letter(scanner_issue_data: dict[str, Any], lifecycle_mode: str | None = None) -> dict[str, Any]:
    issue_id = _safe_text(scanner_issue_data.get("id") or scanner_issue_data.get("issue_id"), "issue_unknown")
    letter_type = _safe_text(scanner_issue_data.get("letter_type")) or recommend_letter_type(scanner_issue_data)
    recipient_type = _recipient_type_for(letter_type)
    customer_label = _safe_text(scanner_issue_data.get("customer_label"), "possible report error")
    explanation = _safe_text(scanner_issue_data.get("customer_explanation"), "This item needs plain-English review.")
    account_ids = list(scanner_issue_data.get("related_tradeline_ids") or scanner_issue_data.get("account_ids") or [])
    evidence = scanner_issue_data.get("evidence") or []
    evidence_ids = [
        _safe_text(item.get("id") or item.get("tradeline_id") or item.get("bureau"), f"evidence_{index}")
        for index, item in enumerate(evidence, start=1)
        if isinstance(item, dict)
    ]

    draft_body = "\n\n".join([
        "DRAFT ONLY - CUSTOMER APPROVAL AND ADMIN REVIEW REQUIRED.",
        "Credit Vivo is preparing this as customer-approved dispute prep. Nothing is sent automatically.",
        f"Review topic: {customer_label}.",
        f"Plain-English review note: {explanation}",
        "Requested action: Please investigate, verify, update, or correct only information that is inaccurate, incomplete, outdated, duplicate, or unverifiable based on the supporting documents.",
        "Important: Accurate, current, and verifiable information may remain. Results vary. This draft is not legal advice and Credit Vivo is not a law firm.",
    ])

    letter = DraftLetter(
        letter_id=f"letter_{issue_id}_{letter_type}",
        letter_type=letter_type,
        issue_id=issue_id,
        status=LetterLifecycleStatus.DRAFT_READY.value,
        subject=_letter_subject(letter_type, scanner_issue_data),
        recipient_type=recipient_type,
        account_ids=account_ids,
        issue_ids=[issue_id],
        evidence_ids=evidence_ids,
        draft_body=draft_body,
    )
    data = asdict(letter)
    data["lifecycle_mode"] = normalize_lifecycle_mode(lifecycle_mode)
    return data


def build_lifecycle_plan(scanner_issue_data: dict[str, Any], requested_mode: str | None = None) -> dict[str, Any]:
    mode = normalize_lifecycle_mode(requested_mode)
    letter = build_draft_letter(scanner_issue_data, lifecycle_mode=mode["effective_mode"])
    return {
        "mode": mode,
        "letter": letter,
        "next_required_reviews": [
            "customer_review",
            "admin_review",
            "compliance_review",
        ],
        "automatic_actions": [],
        "send_available": False,
    }


def can_prepare_lob_packet(
    letter_status: str,
    customer_approval: bool,
    admin_approval: bool,
    compliance_review_status: str,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if letter_status not in {
        LetterLifecycleStatus.CUSTOMER_APPROVED.value,
        LetterLifecycleStatus.ADMIN_APPROVED.value,
        LetterLifecycleStatus.LOB_PACKET_READY.value,
    }:
        reasons.append("letter_status_not_approval_ready")
    if not customer_approval:
        reasons.append("customer_approval_required")
    if not admin_approval:
        reasons.append("admin_review_required")
    if compliance_review_status != "approved":
        reasons.append("compliance_review_approved_required")
    return (not reasons, reasons)


def build_lob_packet_preview(letter_data: dict[str, Any], packet_data: dict[str, Any] | None = None) -> dict[str, Any]:
    packet_data = packet_data or {}
    customer_approval_timestamp = packet_data.get("customer_approval_timestamp")
    admin_approval_timestamp = packet_data.get("admin_approval_timestamp")
    compliance_review_status = _safe_text(packet_data.get("compliance_review_status"), "pending")
    can_prepare, reasons = can_prepare_lob_packet(
        _safe_text(letter_data.get("status"), LetterLifecycleStatus.DRAFT_READY.value),
        bool(customer_approval_timestamp),
        bool(admin_approval_timestamp),
        compliance_review_status,
    )
    packet = LobPacketPreview(
        customer_id=_safe_text(packet_data.get("customer_id"), "customer_pending"),
        report_id=_safe_text(packet_data.get("report_id"), "report_pending"),
        letter_id=_safe_text(letter_data.get("letter_id"), "letter_pending"),
        letter_type=_safe_text(letter_data.get("letter_type"), "draft_letter"),
        recipient_type=_safe_text(packet_data.get("recipient_type") or letter_data.get("recipient_type"), "recipient_pending"),
        recipient_name=_safe_text(packet_data.get("recipient_name"), "Recipient pending"),
        recipient_address=dict(packet_data.get("recipient_address") or {}),
        sender_name=_safe_text(packet_data.get("sender_name"), "Sender pending"),
        sender_address=dict(packet_data.get("sender_address") or {}),
        account_ids=list(letter_data.get("account_ids") or packet_data.get("account_ids") or []),
        issue_ids=list(letter_data.get("issue_ids") or packet_data.get("issue_ids") or []),
        evidence_ids=list(letter_data.get("evidence_ids") or packet_data.get("evidence_ids") or []),
        letter_html_or_pdf_reference=_safe_text(packet_data.get("letter_html_or_pdf_reference"), "draft_reference_pending"),
        customer_approval_timestamp=_safe_text(customer_approval_timestamp) or None,
        admin_approval_timestamp=_safe_text(admin_approval_timestamp) or None,
        compliance_review_status=compliance_review_status,
        blocked=not can_prepare,
        block_reasons=reasons,
    )
    return asdict(packet)


def classify_response_text(response_text: str) -> str:
    text = _safe_text(response_text).lower()
    if not text:
        return ResponseClassification.NO_RESPONSE.value
    if any(term in text for term in ["deleted", "removed", "will be removed", "has been removed"]):
        return ResponseClassification.REMOVED.value
    if any(term in text for term in ["verified as accurate", "verified", "verified and remains", "remains unchanged"]):
        return ResponseClassification.VERIFIED.value
    if any(term in text for term in ["partially updated", "some information", "partially corrected"]):
        return ResponseClassification.PARTIALLY_UPDATED.value
    if any(term in text for term in ["updated", "corrected", "modified", "revised"]):
        return ResponseClassification.UPDATED.value
    if any(term in text for term in ["additional information", "more information", "send documentation", "provide proof"]):
        return ResponseClassification.REQUEST_FOR_MORE_INFORMATION.value
    if any(term in text for term in ["frivolous", "irrelevant", "suspicious", "stalling"]):
        return ResponseClassification.FRIVOLOUS_OR_IRRELEVANT_NOTICE.value
    return ResponseClassification.UNKNOWN_NEEDS_ADMIN_REVIEW.value


def recommend_next_step(response_classification: str) -> dict[str, str]:
    mapping = {
        ResponseClassification.VERIFIED.value: (
            LetterLifecycleStatus.RESPONSE_REVIEW_PENDING.value,
            "Admin should compare the response against the original evidence and decide whether a method of verification or documented follow-up draft is appropriate.",
        ),
        ResponseClassification.UPDATED.value: (
            LetterLifecycleStatus.RESOLVED_UPDATED.value,
            "Admin should verify the updated report fields and save before/after documentation.",
        ),
        ResponseClassification.REMOVED.value: (
            LetterLifecycleStatus.RESOLVED_REMOVED.value,
            "Admin should confirm the item no longer appears and document the result without promising similar outcomes.",
        ),
        ResponseClassification.PARTIALLY_UPDATED.value: (
            LetterLifecycleStatus.NEXT_STEP_RECOMMENDED.value,
            "Admin should identify which fields remain inconsistent and prepare a focused follow-up draft if supported.",
        ),
        ResponseClassification.REQUEST_FOR_MORE_INFORMATION.value: (
            LetterLifecycleStatus.NEXT_STEP_RECOMMENDED.value,
            "Ask the customer for specific supporting documents before any additional draft is prepared.",
        ),
        ResponseClassification.FRIVOLOUS_OR_IRRELEVANT_NOTICE.value: (
            LetterLifecycleStatus.RESPONSE_REVIEW_PENDING.value,
            "Admin/compliance should review whether the response addressed the documented issue before preparing any next-step draft.",
        ),
        ResponseClassification.NO_RESPONSE.value: (
            LetterLifecycleStatus.NO_RESPONSE_REVIEW_NEEDED.value,
            "Admin should confirm delivery dates and timing before preparing a documented no-response follow-up package.",
        ),
    }
    status, next_step = mapping.get(
        response_classification,
        (
            LetterLifecycleStatus.RESPONSE_REVIEW_PENDING.value,
            "Admin review is required before recommending any next step.",
        ),
    )
    return {
        "response_classification": response_classification,
        "recommended_status": status,
        "next_step": next_step,
        "automatic_action_taken": "none",
        "approval_required": "customer approval and admin review required before action",
    }
