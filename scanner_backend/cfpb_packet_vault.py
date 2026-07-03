from __future__ import annotations

"""
CFPB-style packet, Lob tracking placeholder, and document vault planning layer.

This module prepares evidence-backed packet metadata only. It does not send mail,
submit complaints, call Lob, or store sensitive documents in browser storage.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re


CFPB_LETTER_STANDARD_ID = "LETTER-CFPB-001"
MAIL_PACKET_RULE_ID = "MAIL-PACKET-001"
MAIL_EVIDENCE_RULE_ID = "MAIL-EVIDENCE-001"
IDENTITY_PACKET_RULE_ID = "IDENTITY-PACKET-001"
ATTACH_3B_RULE_ID = "ATTACH-3B-001"
DOC_VAULT_RULE_ID = "DOC-VAULT-001"
LOB_MAIL_RULE_ID = "LOB-MAIL-001"
ESIGN_RULE_ID = "ESIGN-001"
RAW_LETTER_RULE_ID = "RAW-LETTER-001"

PACKET_DASHBOARD_STATUSES = [
    "Draft Ready",
    "Evidence Needed",
    "ID Needed",
    "Proof of Address Needed",
    "Comparison Attachment Ready",
    "Report Page Attached",
    "Sensitive Data Review",
    "Customer Approval Needed",
    "Admin Approval Needed",
    "Approved",
    "Queued for Lob",
    "Mailed",
    "Delivered",
    "Waiting for Response",
    "Response Received",
    "Verified - Needs Review",
    "Updated - Review Needed",
    "Deleted / Removed",
    "Follow-Up Ready",
    "Complaint Packet Ready",
    "Attorney Review Candidate",
    "Closed",
]

LOB_TRACKING_STATUSES = [
    "Draft",
    "Approved",
    "Queued for Mailing",
    "Sent to Lob",
    "Printed",
    "Mailed",
    "In Transit",
    "Delivered",
    "Returned",
    "Failed",
    "Needs Review",
    "Follow-Up Ready",
]

SENSITIVE_DOCUMENT_TYPES = {
    "government_id_copy",
    "proof_of_address",
    "raw_credit_report_excerpt",
    "supporting_evidence",
    "customer_esign_authorization",
}


@dataclass
class PacketGate:
    customer_esign_required: bool = True
    customer_esign_recorded: bool = False
    admin_approval_required: bool = True
    admin_approval_recorded: bool = False
    sensitive_data_review_required: bool = True
    sensitive_data_review_passed: bool = False
    lob_api_configured_server_side: bool = False
    production_mode_confirmed: bool = False
    mailing_allowed: bool = False
    block_reasons: list[str] = field(default_factory=list)


def _safe(value: Any, default: str = "") -> str:
    return str(value if value is not None else default).strip()


def _mask_account(value: Any) -> str:
    text = _safe(value)
    if not text:
        return ""
    if "*" in text or "X" in text.upper():
        return text
    digits = re.sub(r"\D", "", text)
    if len(digits) <= 4:
        return f"*{digits}" if digits else text
    return "*" * max(len(digits) - 4, 4) + digits[-4:]


def _raw_field(item: dict[str, Any], key: str) -> str:
    if key == "account_number":
        return _safe(item.get("account_number_masked") or _mask_account(item.get("account_number")))
    return _safe(item.get(key))


def _issue_label(issue_type: str, label: str) -> str:
    blob = f"{issue_type} {label}".lower()
    if "balance" in blob:
        return "Balance review"
    if "status" in blob or "payment" in blob:
        return "Status review"
    if "dofd" in blob or "date" in blob or "removal" in blob or "timeline" in blob:
        return "Timeline review"
    if "original creditor" in blob:
        return "Original creditor review"
    if "duplicate" in blob:
        return "Duplicate review"
    if "license" in blob:
        return "License review"
    if "authority" in blob:
        return "Authority review"
    if "dispute" in blob:
        return "Dispute note review"
    if "missing" in blob or "blank" in blob:
        return "Missing info"
    if "mismatch" in blob or "differs" in blob:
        return "Does not match"
    if "validation" in blob or "collection" in blob:
        return "Needs validation"
    return "Does not match"


def _entity_status(entity_rows: list[dict[str, Any]], items: list[dict[str, Any]]) -> dict[str, str]:
    tradeline_ids = {_safe(item.get("id")) for item in items}
    matches = [row for row in entity_rows if _safe(row.get("tradeline_id")) in tradeline_ids]
    if not matches:
        return {
            "license_authority_status": "License/business status review needed.",
            "business_registry_status": "Manual review needed",
            "debt_collector_license_status": "Manual review needed if applicable",
            "last_checked_date": "",
            "source_link": "",
            "manual_review_needed": "Yes",
        }
    source_links = []
    for row in matches[:3]:
        for key in ("business_registry_search_link", "state_license_search_link", "debt_collector_license_search_link", "nmls_search_link"):
            if row.get(key):
                source_links.append(_safe(row.get(key)))
    return {
        "license_authority_status": "License/business status review needed.",
        "business_registry_status": "Manual review needed",
        "debt_collector_license_status": "Manual review needed if applicable",
        "last_checked_date": matches[0].get("last_checked_date", ""),
        "source_link": " | ".join(dict.fromkeys(source_links[:4])),
        "manual_review_needed": "Yes",
    }


def _group_items(data: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    tradelines = list(data.get("tradelines", []))
    by_id = {_safe(item.get("id")): item for item in tradelines}
    used: set[str] = set()
    groups: list[tuple[str, list[dict[str, Any]]]] = []
    for group in data.get("cross_bureau_groups", []):
        items = [by_id[tid] for tid in group.get("tradeline_ids", []) if tid in by_id]
        if items:
            group_id = _safe(group.get("group_id"), f"group_{len(groups)+1:02d}")
            groups.append((group_id, items))
            used.update(_safe(item.get("id")) for item in items)
    for item in tradelines:
        item_id = _safe(item.get("id"))
        if item_id not in used:
            groups.append((item_id or f"single_{len(groups)+1:02d}", [item]))
    return groups


def build_three_bureau_comparison_attachment(data: dict[str, Any]) -> list[dict[str, Any]]:
    issues = list(data.get("issues", []))
    entity_rows = list(data.get("entity_compliance_intelligence", []))
    rows: list[dict[str, Any]] = []
    for group_id, items in _group_items(data):
        ids = {_safe(item.get("id")) for item in items}
        related = [issue for issue in issues if ids & set(issue.get("related_tradeline_ids", []))]
        main_issue = _issue_label(
            _safe(related[0].get("issue_type")) if related else "",
            _safe(related[0].get("customer_label")) if related else "Needs validation",
        )
        by_bureau = {item.get("bureau"): item for item in items}
        entity_status = _entity_status(entity_rows, items)
        account_name = "; ".join(sorted({_safe(item.get("account_name")) for item in items if item.get("account_name")})) or "Review item"
        for field_key, field_label in [
            ("account_name", "Account name"),
            ("account_number", "Masked account number"),
            ("account_type", "Account type"),
            ("status", "Status"),
            ("balance", "Balance"),
            ("date_of_first_delinquency", "Date of first delinquency"),
            ("estimated_removal_date", "Estimated removal date"),
            ("original_creditor", "Original creditor"),
            ("remarks", "Remarks"),
        ]:
            eq = _raw_field(by_bureau.get("Equifax", {}), field_key)
            ex = _raw_field(by_bureau.get("Experian", {}), field_key)
            tr = _raw_field(by_bureau.get("TransUnion", {}), field_key)
            if not any([eq, ex, tr]):
                continue
            rows.append({
                "group_id": group_id,
                "account_field": f"{account_name} / {field_label}",
                "equifax_raw_value": eq,
                "experian_raw_value": ex,
                "transunion_raw_value": tr,
                "main_issue": main_issue,
                "license_authority_status": entity_status["license_authority_status"],
                "business_registry_status": entity_status["business_registry_status"],
                "debt_collector_license_status": entity_status["debt_collector_license_status"],
                "last_checked_date": entity_status["last_checked_date"],
                "source_link": entity_status["source_link"],
                "manual_review_needed": entity_status["manual_review_needed"],
                "evidence_source": "; ".join(sorted({_safe(item.get("source_filename")) for item in items if item.get("source_filename")})),
                "recommended_action": "Verify raw report value, source records, license/authority status, and customer approval before use.",
                "source_report_date": "; ".join(sorted({_safe(item.get("sourceReportDate") or item.get("source_report_date")) for item in items if item.get("sourceReportDate") or item.get("source_report_date")})),
                "source_page_section": "; ".join(sorted({
                    f"{item.get('bureau', 'Report')} p.{item.get('page_start') or item.get('sourcePageHint') or ''}"
                    for item in items
                })),
                "masked_account_number": "; ".join(sorted({_mask_account(item.get("account_number") or item.get("account_number_masked")) for item in items if item.get("account_number") or item.get("account_number_masked")})),
                "raw_data_integrity": "Raw bureau values preserved exactly as parsed; normalized alias is not used for quoted evidence.",
            })
    return rows[:120]


def _documents_for_packet(packet_type: str) -> list[dict[str, Any]]:
    base = [
        ("cfpb_style_letter_pdf", "CFPB-style draft letter", True),
        ("three_bureau_comparison_attachment", "3-bureau comparison attachment", True),
        ("raw_credit_report_excerpt", "Relevant credit report page/excerpt", True),
        ("supporting_evidence", "Supporting evidence", False),
        ("customer_esign_authorization", "Customer e-sign authorization record", True),
        ("admin_approval_record", "Admin approval record", True),
        ("lob_mail_tracking_record", "Lob mail tracking record after mailing", False),
    ]
    if packet_type == "bureau_dispute":
        base.insert(1, ("government_id_copy", "Government ID copy, when needed", False))
        base.insert(2, ("proof_of_address", "Proof of address, when needed", False))
    if packet_type in {"debt_validation_request", "collector_validation"}:
        base.extend([
            ("license_authority_search_result", "License/authority search result if applicable", True),
            ("original_creditor_request", "Request for original creditor", True),
            ("itemized_balance_request", "Request for itemized balance", True),
            ("ownership_assignment_chain_request", "Request for ownership/assignment chain", True),
            ("dofd_request", "Request for Date of First Delinquency", True),
        ])
    if packet_type == "method_of_verification_request":
        base.extend([
            ("prior_investigation_response", "Prior investigation response", True),
            ("prior_dispute_delivery_proof", "Prior dispute delivery proof", True),
            ("verification_method_request", "Request for method of verification details", True),
        ])
    if packet_type == "reinvestigation_request":
        base.extend([
            ("prior_dispute_packet", "Prior dispute packet", True),
            ("new_or_unreviewed_evidence", "New or unreviewed evidence", False),
            ("reinvestigation_request_detail", "Specific reinvestigation request detail", True),
        ])
    if packet_type == "escalation_follow_up":
        base.extend([
            ("full_dispute_timeline", "Full dispute timeline", True),
            ("prior_response_chain", "Prior response chain", True),
            ("verified_escalation_address", "Verified escalation address", True),
        ])
    if packet_type == "attorney_review_summary":
        base.extend([
            ("full_dispute_history", "Full dispute history", True),
            ("damages_or_denial_evidence", "Damages or denial evidence, if available", False),
            ("admin_review_summary", "Admin review summary", True),
        ])
    if packet_type == "complaint_preparation_packet":
        base = [
            ("complaint_summary", "Complaint summary", True),
            ("original_dispute_letter", "Original dispute letter", True),
            ("follow_up_letter", "Follow-up letter if any", False),
            ("lob_delivery_proof", "Lob delivery proof", False),
            ("bureau_furnisher_collector_response", "Bureau/furnisher/collector response", False),
            ("three_bureau_comparison_attachment", "3-bureau comparison attachment", True),
            ("raw_credit_report_excerpt", "Relevant report pages/excerpts", True),
            ("supporting_evidence", "Evidence", False),
            ("timeline", "Timeline", True),
            ("customer_esign_authorization", "Customer e-sign authorization", True),
            ("admin_review_notes", "Admin review notes", True),
        ]
    return [
        {
            "document_type": doc_type,
            "label": label,
            "required_before_mailing": required,
            "status": "missing" if required else "optional",
            "server_side_only": doc_type in SENSITIVE_DOCUMENT_TYPES,
            "browser_local_storage_allowed": False,
        }
        for doc_type, label, required in base
    ]


def build_packet_gate(env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or {}
    gate = PacketGate()
    gate.lob_api_configured_server_side = bool(env.get("LOB_API_KEY"))
    gate.production_mode_confirmed = env.get("LOB_TEST_MODE", "true").lower() == "false"
    gate.block_reasons = [
        "customer_esign_required",
        "admin_approval_required",
        "sensitive_data_review_required",
    ]
    if not gate.lob_api_configured_server_side:
        gate.block_reasons.append("lob_api_key_not_configured_server_side")
    if not gate.production_mode_confirmed:
        gate.block_reasons.append("lob_test_mode_or_preview_mode_active")
    gate.mailing_allowed = False
    return asdict(gate)


def _letter_body(letter_type: str, finding: dict[str, Any], packet: dict[str, Any]) -> str:
    account_name = _safe(finding.get("account_name") or finding.get("customer_label"), "Disputed account")
    bureau = _safe(finding.get("bureau"), "[Bureau]")
    field_name = _safe(finding.get("field_name") or finding.get("customer_label"), "[Field disputed]")
    reported_value = _safe(finding.get("reported_value"), "[Exact raw reported value]")
    masked_account = _mask_account(finding.get("account_number") or finding.get("masked_account_number"))
    notice = (
        "If you continue furnishing this information to any consumer reporting agency, please report that the account is disputed by the consumer."
        if letter_type in {"furnisher_dispute", "collector_validation"}
        else "Please ensure this account is marked as disputed by the consumer while the investigation is pending and in any continued reporting, as required by applicable credit reporting law."
    )
    return "\n".join([
        "DRAFT ONLY - CUSTOMER E-SIGN APPROVAL AND ADMIN REVIEW REQUIRED.",
        "",
        "I am disputing the following information in my credit report.",
        "",
        f"Account: {account_name}",
        f"Masked account number: {masked_account}",
        f"Bureau: {bureau}",
        f"Field disputed: {field_name}",
        f"Reported value: {reported_value}",
        f"Reason for dispute: {_safe(finding.get('reason'), 'This field requires verification against source records because it may be inaccurate, incomplete, inconsistent, or unverifiable.')}",
        f"Supporting documents enclosed: {', '.join(packet.get('attachment_labels', [])) or '3-bureau comparison attachment; relevant report excerpt; supporting evidence if available'}",
        "Requested action: Please investigate, verify, correct, update, or remove information that cannot be verified as accurate, complete, and current.",
        "",
        notice,
        "",
        "Customer signature/e-sign reference: [Pending customer e-sign authorization]",
    ])


def buildBureauDisputeLetter(finding: dict[str, Any], packet: dict[str, Any]) -> str:
    return _letter_body("bureau_dispute", finding, packet)


def buildFurnisherDisputeLetter(finding: dict[str, Any], packet: dict[str, Any]) -> str:
    return _letter_body("furnisher_dispute", finding, packet)


def buildCollectorValidationLetter(finding: dict[str, Any], packet: dict[str, Any]) -> str:
    body = _letter_body("collector_validation", finding, packet)
    return body + "\n\nPlease also provide the original creditor, itemized balance, ownership/assignment chain, and Date of First Delinquency support."


def buildFollowUpLetter(finding: dict[str, Any], priorResponse: dict[str, Any], packet: dict[str, Any]) -> str:
    body = _letter_body("follow_up", finding, packet)
    return body + f"\n\nPrior response summary: {_safe(priorResponse.get('summary'), '[Pending response review]')}"


def buildComplaintPacket(finding: dict[str, Any], timeline: list[dict[str, Any]], packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_type": "complaint_preparation_packet",
        "status": "Complaint Packet Ready",
        "auto_submit": False,
        "finding": finding,
        "timeline": timeline,
        "packet": packet,
        "required_notice": "Do not auto-submit complaints. Customer approval, admin review, and production workflow approval are required.",
    }


def build_cfpb_packet_system(data: dict[str, Any], env: dict[str, str] | None = None) -> dict[str, Any]:
    comparison_rows = build_three_bureau_comparison_attachment(data)
    gate = build_packet_gate(env)
    packets: list[dict[str, Any]] = []
    packet_type_map = {
        "debt_validation_request": "collector_validation",
        "method_of_verification_request": "method_of_verification_request",
        "reinvestigation_request": "reinvestigation_request",
        "escalation_follow_up": "escalation_follow_up",
        "complaint_preparation_packet": "complaint_preparation_packet",
        "attorney_review_summary": "attorney_review_summary",
    }
    for index, letter in enumerate(data.get("recommended_letter_queue", []), start=1):
        letter_type = _safe(letter.get("letter_type"), "bureau_dispute")
        packet_type = packet_type_map.get(letter_type, letter_type)
        documents = _documents_for_packet(packet_type)
        attachment_labels = [doc["label"] for doc in documents if doc["required_before_mailing"]]
        finding = {
            "issue_id": letter.get("issue_id", ""),
            "customer_label": letter.get("customer_label", ""),
            "account_name": letter.get("account_name", ""),
            "field_name": letter.get("customer_label", ""),
            "reported_value": "[Use exact raw bureau value from comparison attachment]",
            "reason": "Field-specific CFPB-style review prepared from scanner evidence.",
        }
        packet = {"attachment_labels": attachment_labels}
        if letter.get("draft_letter_body"):
            letter_body = _safe(letter.get("draft_letter_body"))
        elif packet_type == "furnisher_direct_dispute":
            letter_body = buildFurnisherDisputeLetter(finding, packet)
        elif packet_type == "collector_validation":
            letter_body = buildCollectorValidationLetter(finding, packet)
        elif packet_type == "complaint_preparation_packet":
            letter_body = json.dumps(buildComplaintPacket(finding, [], packet), ensure_ascii=False)
        else:
            letter_body = buildBureauDisputeLetter(finding, packet)
        packets.append({
            "packet_id": f"cfpb_packet_{index:04d}",
            "source_letter_id": letter.get("letter_id", f"letter_{index:04d}"),
            "packet_type": packet_type,
            "rule_ids": [CFPB_LETTER_STANDARD_ID, MAIL_PACKET_RULE_ID, MAIL_EVIDENCE_RULE_ID, ATTACH_3B_RULE_ID, DOC_VAULT_RULE_ID, LOB_MAIL_RULE_ID, ESIGN_RULE_ID, RAW_LETTER_RULE_ID],
            "status": "Customer Approval Needed",
            "customer_view_status": "Draft letter packet ready for review. Nothing has been mailed.",
            "admin_view_status": "Lob-ready draft packet prepared with approval gates, comparison attachment, raw values, license/auth status, evidence source, and dispute issue.",
            "documents": documents,
            "packet_gate": gate,
            "lob_ready_preview": letter.get("lob_ready_preview", {}),
            "lob_tracking": {
                "lob_id": None,
                "tracking_number": None,
                "delivery_status": "Draft",
                "webhook_event": None,
                "error_message": None,
                "response_deadline": None,
                "next_action": "Record customer e-sign, admin approval, sensitive data review, then queue only in approved production workflow.",
            },
            "draft_letter_body": letter_body,
            "letter_subject": letter.get("letter_subject", ""),
            "letter_type_label": letter.get("letter_type_label", packet_type.replace("_", " ").title()),
            "mailing_allowed": False,
            "auto_send": False,
            "auto_file_complaint": False,
        })
    vault_records = []
    for packet in packets:
        for doc in packet["documents"]:
            vault_records.append({
                "document_id": f"vault_{packet['packet_id']}_{doc['document_type']}",
                "case_id": "case_pending",
                "customer_id": "customer_pending",
                "document_type": doc["document_type"],
                "letter_type": packet["packet_type"],
                "recipient": "pending",
                "date_created": datetime.now(timezone.utc).isoformat(),
                "customer_approved_date": None,
                "admin_approved_date": None,
                "lob_mail_id": None,
                "tracking_number": None,
                "delivery_status": "Draft",
                "response_deadline": None,
                "stored_evidence": doc["status"],
                "next_action": "Collect/verify document server-side before mailing.",
                "viewed_by": [],
                "last_accessed": None,
                "retention_status": "preview_manifest_only_until_secure_storage_is_configured",
                "server_side_only": doc["server_side_only"],
                "browser_local_storage_allowed": False,
            })
    return {
        "version": "cfpb_packet_vault_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rules": {
            CFPB_LETTER_STANDARD_ID: "All letters use CFPB-style field-specific structure.",
            MAIL_PACKET_RULE_ID: "Packets require letter, evidence, comparison, approval, and tracking records.",
            DOC_VAULT_RULE_ID: "Outgoing/incoming documents are represented in a server-side vault manifest.",
            LOB_MAIL_RULE_ID: "Lob tracking is placeholder/draft until approvals and server-side keys exist.",
            ESIGN_RULE_ID: "Mailing is blocked until customer e-sign approval is recorded.",
        },
        "dashboard_statuses": PACKET_DASHBOARD_STATUSES,
        "lob_tracking_statuses": LOB_TRACKING_STATUSES,
        "three_bureau_comparison_attachment": comparison_rows,
        "dispute_packets": packets,
        "document_vault": {
            "rule_id": DOC_VAULT_RULE_ID,
            "storage_mode": "server_side_preview_manifest",
            "production_requirements": [
                "customer login/auth",
                "admin permissions",
                "secure server-side storage",
                "document encryption",
                "audit logs",
                "customer e-sign authorization",
                "Lob API keys configured server-side only",
                "privacy/compliance/legal review",
            ],
            "customer_sections": ["Customer Documents", "Sent Letters", "Delivery Tracking", "Responses", "Follow-Ups", "Evidence", "Escalation Packets"],
            "records": vault_records,
        },
        "security": {
            "raw_evidence_layer": "Raw bureau values are preserved separately and not rewritten.",
            "normalized_analysis_layer": "Normalized aliases may be used for grouping/admin notes only.",
            "local_storage_sensitive_docs_allowed": False,
            "automatic_mailing_enabled": False,
            "automatic_complaint_submission_enabled": False,
        },
    }


def save_document_vault_artifacts(data: dict[str, Any], out_dir: Path) -> None:
    packet_system = data.get("cfpb_packet_system") or {}
    vault_dir = out_dir / "document_vault"
    packets_dir = vault_dir / "packets"
    vault_dir.mkdir(parents=True, exist_ok=True)
    packets_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "document_vault_manifest.json").write_text(
        json.dumps(packet_system.get("document_vault", {}), indent=2),
        encoding="utf-8",
    )
    (vault_dir / "three_bureau_comparison_attachment.json").write_text(
        json.dumps(packet_system.get("three_bureau_comparison_attachment", []), indent=2),
        encoding="utf-8",
    )
    for packet in packet_system.get("dispute_packets", []):
        packet_id = _safe(packet.get("packet_id"), "packet_pending")
        (packets_dir / f"{packet_id}.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")
