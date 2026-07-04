from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Mapping


ISSUE_TYPES = {
    "identity_mismatch",
    "balance_mismatch",
    "status_mismatch",
    "date_mismatch",
    "missing_dofd",
    "possible_reaging",
    "missing_dispute_notice",
    "unverified_after_dispute",
    "paid_reporting_unpaid",
    "duplicate_reporting",
    "identity_theft_reporting",
    "wrong_responsibility",
    "outdated_negative",
    "account_verification_review",
}

FCRA_RULE_MAP = {
    "identity_mismatch": ["FCRA 607(b)", "FCRA 611"],
    "balance_mismatch": ["FCRA 611", "FCRA 623(a)(2)", "FCRA 623(b)"],
    "status_mismatch": ["FCRA 611", "FCRA 623(a)(2)", "FCRA 623(b)"],
    "date_mismatch": ["FCRA 611", "FCRA 623(a)(2)", "FCRA 623(b)"],
    "missing_dofd": ["FCRA 623(a)(5)"],
    "possible_reaging": ["FCRA 605", "FCRA 623(a)(5)"],
    "missing_dispute_notice": ["FCRA 623(a)(3)", "FCRA 611"],
    "unverified_after_dispute": ["FCRA 611", "FCRA 623(b)"],
    "paid_reporting_unpaid": ["FCRA 611", "FCRA 623(a)(2)"],
    "duplicate_reporting": ["FCRA 607(b)", "FCRA 623(a)(2)"],
    "identity_theft_reporting": ["FCRA 605B", "FCRA 623(a)(6)"],
    "wrong_responsibility": ["FCRA 611", "FCRA 623(a)(2)"],
    "outdated_negative": ["FCRA 605"],
    "account_verification_review": ["FCRA 611", "FCRA 623(a)(2)", "FCRA 623(b)"],
}

METRO2_RULE_MAP = {
    "identity_mismatch": ["Consumer identity fields should identify the correct consumer"],
    "balance_mismatch": ["Balance/current balance fields should match verified account condition"],
    "status_mismatch": ["Account status/payment rating should match verified account condition"],
    "date_mismatch": ["Date opened/reported/updated/closed/DOFD fields should be accurate"],
    "missing_dofd": ["DOFD should support the negative reporting timeline"],
    "possible_reaging": ["DOFD/reporting timeline should not be reset improperly"],
    "missing_dispute_notice": ["Compliance condition/dispute code should reflect consumer dispute after notice"],
    "unverified_after_dispute": ["Verified reporting should be supported by account-level records"],
    "paid_reporting_unpaid": ["Status and balance should reflect paid/settled condition"],
    "duplicate_reporting": ["Transferred/sold/collection reporting should not create misleading duplicate debt"],
    "identity_theft_reporting": ["Consumer information indicator and fraud-block workflow should match supporting proof"],
    "wrong_responsibility": ["ECOA/responsibility code should reflect correct liability"],
    "outdated_negative": ["Reporting timeline should not exceed the supported permissible reporting period"],
    "account_verification_review": ["Core Metro 2 account fields should be accurate, complete, current, and supportable"],
}

DEFAULT_TRACKING_RULES = {
    "trackDisputeNotationAfterRound1": True,
    "disputeNotationCheckWindow": "next_report_update",
    "missingDisputeNotationFlag": "Missing Notice of Dispute",
    "addToRound2IfMissing": True,
    "escalationRisk": "high",
    "customerApprovalRequired": True,
    "adminReviewRequired": True,
    "automaticSendAllowed": False,
}

ISSUE_TYPE_ALIASES = {
    "cross_bureau_balance_mismatch": "balance_mismatch",
    "cross_bureau_status_mismatch": "status_mismatch",
    "cross_bureau_date_mismatch": "date_mismatch",
    "reage_dofd_missing_review": "missing_dofd",
    "missing_dofd_review": "missing_dofd",
    "reage_timeline_review": "possible_reaging",
    "removal_obsolescence_date_missing": "outdated_negative",
    "duplicate_overlap_review": "duplicate_reporting",
    "fcra_nod_dispute_notation_review": "missing_dispute_notice",
    "closed_sold_balance_review": "balance_mismatch",
    "paid_collection_reporting_review": "paid_reporting_unpaid",
    "account_identifier_mismatch": "identity_mismatch",
    "identity_cleanup_review": "identity_mismatch",
    "account_type_classification_mismatch": "account_verification_review",
    "original_creditor_missing_or_inconsistent": "account_verification_review",
    "remark_narrative_code_inconsistency": "account_verification_review",
    "payment_history_inconsistency": "status_mismatch",
    "major_delinquency_date_missing": "date_mismatch",
    "collection_review": "account_verification_review",
    "chargeoff_review": "account_verification_review",
    "entity_compliance_review": "account_verification_review",
}

ISSUE_ACTIONS = {
    "identity_mismatch": "fix",
    "balance_mismatch": "fix",
    "status_mismatch": "fix",
    "date_mismatch": "fix",
    "missing_dofd": "fix",
    "possible_reaging": "fix",
    "missing_dispute_notice": "fix",
    "unverified_after_dispute": "delete_if_unverifiable",
    "paid_reporting_unpaid": "fix",
    "duplicate_reporting": "delete_if_unverifiable",
    "identity_theft_reporting": "delete_if_unverifiable",
    "wrong_responsibility": "fix",
    "outdated_negative": "delete_if_unverifiable",
    "account_verification_review": "needs_review",
}


@dataclass
class PossibleRuleIssue:
    id: str
    accountId: str
    bureau: str
    furnisherName: str
    issueType: str
    errorFound: str
    whyWrong: str
    fixRequested: str
    possibleFCRARules: list[str]
    possibleMetro2Rules: list[str]
    evidenceRefs: list[str]
    roundDetected: int
    severity: str
    escalationRecommended: bool
    attorneyReviewRecommended: bool
    nextStep: str
    escalationRisk: str
    possibleConsequences: list[str]
    action: str
    customerApprovalRequired: bool = True
    adminReviewRequired: bool = True
    complianceReviewRequired: bool = True
    automaticSendAllowed: bool = False


def normalize_issue_type(issue_type: str) -> str:
    normalized = (issue_type or "").strip().lower()
    if normalized in ISSUE_TYPES:
        return normalized
    if normalized.startswith("negative_"):
        return "account_verification_review"
    return ISSUE_TYPE_ALIASES.get(normalized, "account_verification_review")


def get_next_round_action(issue: Mapping[str, Any] | PossibleRuleIssue) -> str:
    round_detected = int(_get(issue, "roundDetected", _get(issue, "round_detected", 1)) or 1)
    actions = {
        1: "Identity cleanup / account verification / debt validation",
        2: "Repeat identity fix + add 3 strongest CRA field mismatches",
        3: "FCRA / Metro 2 possible rule issue dispute",
        4: "Method of verification request",
        5: "CFPB / State AG / CEO escalation packet for admin review",
        6: "Attorney review packet",
    }
    return actions.get(round_detected, "Needs admin review")


def get_possible_consequences(issue: Mapping[str, Any] | PossibleRuleIssue) -> list[str]:
    round_detected = int(_get(issue, "roundDetected", _get(issue, "round_detected", 1)) or 1)
    consequences = [
        "Correction",
        "Deletion if unverifiable",
        "Dispute notation update",
    ]
    if round_detected >= 3:
        consequences.extend(["CFPB escalation review", "State AG escalation review"])
    if round_detected >= 4:
        consequences.append("Method of verification request")
    if round_detected >= 5:
        consequences.extend([
            "CEO escalation packet",
            "Attorney review recommended",
            "Possible negligent/willful noncompliance review",
        ])
    return consequences


def build_possible_rule_issues(
    issues: list[Any],
    tradelines: list[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    tradeline_index = {str(t.get("id", "")): t for t in tradelines or []}
    return [
        asdict(build_possible_rule_issue(issue, tradeline_index))
        for issue in issues
    ]


def build_possible_rule_issue(
    issue: Any,
    tradeline_index: Mapping[str, Mapping[str, Any]] | None = None,
) -> PossibleRuleIssue:
    issue_id = str(_get(issue, "id", ""))
    related_ids = list(_get(issue, "related_tradeline_ids", []) or [])
    account_id = related_ids[0] if related_ids else issue_id
    tradeline = (tradeline_index or {}).get(account_id, {})
    issue_type = normalize_issue_type(str(_get(issue, "issue_type", "")))
    round_detected = _round_from_issue(issue)
    severity = _safe_severity(str(_get(issue, "severity", "medium")))
    bureau = _first_bureau(issue, tradeline)
    furnisher_name = str(tradeline.get("account_name") or tradeline.get("furnisherName") or "")
    rule_seed = {
        "roundDetected": round_detected,
    }
    escalation_recommended = round_detected >= 3 or severity in {"high", "critical"}
    attorney_review_recommended = round_detected >= 6 or severity == "critical"
    action = ISSUE_ACTIONS.get(issue_type, "needs_review")

    return PossibleRuleIssue(
        id=f"rule_{issue_id}" if issue_id else "rule_needs_review",
        accountId=account_id,
        bureau=bureau,
        furnisherName=furnisher_name,
        issueType=issue_type,
        errorFound=_error_found(issue),
        whyWrong=_why_wrong(issue),
        fixRequested=action,
        possibleFCRARules=FCRA_RULE_MAP.get(issue_type, FCRA_RULE_MAP["account_verification_review"]),
        possibleMetro2Rules=METRO2_RULE_MAP.get(issue_type, METRO2_RULE_MAP["account_verification_review"]),
        evidenceRefs=_evidence_refs(issue),
        roundDetected=round_detected,
        severity=severity,
        escalationRecommended=escalation_recommended,
        attorneyReviewRecommended=attorney_review_recommended,
        nextStep=get_next_round_action(rule_seed),
        escalationRisk=_escalation_risk(round_detected, severity),
        possibleConsequences=get_possible_consequences(rule_seed),
        action=_action_label(action),
    )


def build_round_tracker_rows(possible_rule_issues: list[Mapping[str, Any]]) -> list[list[object]]:
    return [
        [
            "Error Found",
            "Why Wrong",
            "Fix Requested",
            "Possible FCRA Rule",
            "Possible Metro 2 Rule",
            "Evidence",
            "Round Detected",
            "Next Step",
            "Escalation Risk",
            "Possible Consequence",
            "Action: Fix / Delete / Keep / Needs Review",
            "Customer Approval Required",
            "Admin Review Required",
            "Compliance Review Required",
            "Automatic Send Allowed",
        ],
        *[
            [
                row.get("errorFound", ""),
                row.get("whyWrong", ""),
                row.get("fixRequested", ""),
                "; ".join(row.get("possibleFCRARules", []) or []),
                "; ".join(row.get("possibleMetro2Rules", []) or []),
                "; ".join(row.get("evidenceRefs", []) or []),
                row.get("roundDetected", ""),
                row.get("nextStep", ""),
                row.get("escalationRisk", ""),
                "; ".join(row.get("possibleConsequences", []) or []),
                row.get("action", ""),
                "Yes" if row.get("customerApprovalRequired") else "No",
                "Yes" if row.get("adminReviewRequired") else "No",
                "Yes" if row.get("complianceReviewRequired") else "No",
                "Yes" if row.get("automaticSendAllowed") else "No",
            ]
            for row in possible_rule_issues
        ],
    ]


def _get(issue: Any, key: str, default: Any = None) -> Any:
    if isinstance(issue, Mapping):
        return issue.get(key, default)
    return getattr(issue, key, default)


def _round_from_issue(issue: Any) -> int:
    explicit = _get(issue, "roundDetected", _get(issue, "round_detected"))
    if explicit:
        return max(1, min(6, int(explicit)))
    suggested = str(_get(issue, "suggested_round", ""))
    match = re.search(r"round\s*(\d)", suggested, flags=re.I)
    if match:
        return max(1, min(6, int(match.group(1))))
    return 1


def _safe_severity(value: str) -> str:
    value = (value or "medium").lower()
    return value if value in {"low", "medium", "high", "critical"} else "medium"


def _first_bureau(issue: Any, tradeline: Mapping[str, Any]) -> str:
    if tradeline.get("bureau"):
        return str(tradeline.get("bureau", "")).lower()
    evidence = _get(issue, "evidence", []) or []
    if evidence:
        first = evidence[0]
        return str(_get(first, "bureau", "unknown") or "unknown").lower()
    return "unknown"


def _evidence_refs(issue: Any) -> list[str]:
    refs = []
    for item in _get(issue, "evidence", []) or []:
        bureau = _get(item, "bureau", "")
        page = _get(item, "page", "")
        snippet = str(_get(item, "snippet", "") or "").replace("\n", " ").strip()
        snippet = snippet[:180]
        label = " / ".join(str(part) for part in [bureau, f"page {page}" if page else "source snippet"] if part)
        refs.append(f"{label}: {snippet}" if snippet else label)
    return refs


def _error_found(issue: Any) -> str:
    return str(_get(issue, "customer_label", "") or _get(issue, "issue_type", "") or "Possible report error")


def _why_wrong(issue: Any) -> str:
    return str(
        _get(issue, "admin_explanation", "")
        or _get(issue, "customer_explanation", "")
        or "Needs source-document review before any customer-approved dispute prep."
    )


def _escalation_risk(round_detected: int, severity: str) -> str:
    if round_detected >= 5 or severity == "critical":
        return "critical"
    if round_detected >= 3 or severity == "high":
        return "high"
    if round_detected == 2 or severity == "medium":
        return "medium"
    return "low"


def _action_label(action: str) -> str:
    labels = {
        "fix": "Fix",
        "delete_if_unverifiable": "Delete if unverifiable",
        "keep": "Keep",
        "needs_review": "Needs Review",
    }
    return labels.get(action, "Needs Review")
