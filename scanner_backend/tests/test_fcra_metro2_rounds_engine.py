from fcra_metro2_rounds_engine import (
    DEFAULT_TRACKING_RULES,
    build_possible_rule_issues,
    build_round_tracker_rows,
    get_next_round_action,
    get_possible_consequences,
    normalize_issue_type,
)


def test_round_engine_maps_cross_bureau_issue_to_possible_rule_issue():
    issues = [
        {
            "id": "issue_balance",
            "issue_type": "cross_bureau_balance_mismatch",
            "severity": "medium",
            "customer_label": "Balance differs across bureaus",
            "admin_explanation": "Cross-bureau group has different balances. Verify source records.",
            "suggested_round": "Round 3 - Bureau Match Review",
            "related_tradeline_ids": ["tl_1"],
            "evidence": [
                {
                    "bureau": "Experian",
                    "page": 2,
                    "snippet": "Balance $1,234",
                }
            ],
        }
    ]
    tradelines = [{"id": "tl_1", "account_name": "MIDLAND CREDIT MANAGEMENT", "bureau": "Experian"}]

    result = build_possible_rule_issues(issues, tradelines)

    assert result[0]["issueType"] == "balance_mismatch"
    assert result[0]["possibleFCRARules"] == ["FCRA 611", "FCRA 623(a)(2)", "FCRA 623(b)"]
    assert result[0]["roundDetected"] == 3
    assert result[0]["nextStep"] == "FCRA / Metro 2 possible rule issue dispute"
    assert result[0]["escalationRecommended"] is True
    assert result[0]["automaticSendAllowed"] is False
    assert result[0]["customerApprovalRequired"] is True
    assert "CFPB escalation review" in result[0]["possibleConsequences"]


def test_round_engine_default_tracking_rules_keep_approval_gates():
    assert DEFAULT_TRACKING_RULES["trackDisputeNotationAfterRound1"] is True
    assert DEFAULT_TRACKING_RULES["missingDisputeNotationFlag"] == "Missing Notice of Dispute"
    assert DEFAULT_TRACKING_RULES["automaticSendAllowed"] is False
    assert DEFAULT_TRACKING_RULES["customerApprovalRequired"] is True
    assert DEFAULT_TRACKING_RULES["adminReviewRequired"] is True


def test_round_helpers_and_workbook_rows_are_safe_language():
    issue = {"roundDetected": 5}

    assert normalize_issue_type("duplicate_overlap_review") == "duplicate_reporting"
    assert get_next_round_action(issue) == "CFPB / State AG / CEO escalation packet for admin review"
    assert "Attorney review recommended" in get_possible_consequences(issue)

    rows = build_round_tracker_rows([
        {
            "errorFound": "Status differs across bureaus",
            "whyWrong": "Different status values need source-document review.",
            "fixRequested": "fix",
            "possibleFCRARules": ["FCRA 611"],
            "possibleMetro2Rules": ["Account status/payment rating should match verified account condition"],
            "evidenceRefs": ["Experian / page 1: Status Open"],
            "roundDetected": 3,
            "nextStep": "FCRA / Metro 2 possible rule issue dispute",
            "escalationRisk": "high",
            "possibleConsequences": ["Correction"],
            "action": "Fix",
            "customerApprovalRequired": True,
            "adminReviewRequired": True,
            "complianceReviewRequired": True,
            "automaticSendAllowed": False,
        }
    ])

    assert rows[0][:5] == [
        "Error Found",
        "Why Wrong",
        "Fix Requested",
        "Possible FCRA Rule",
        "Possible Metro 2 Rule",
    ]
    assert rows[1][-1] == "No"
    assert "violation proven" not in " ".join(str(cell).lower() for row in rows for cell in row)
