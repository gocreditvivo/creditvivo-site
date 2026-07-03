from ai_operating_system import AI_ROLE_CAPABILITIES, build_ai_operating_system_brief


def test_ai_operating_system_defines_all_core_roles():
    role_ids = {role.role_id for role in AI_ROLE_CAPABILITIES}

    assert "growth_ai" in role_ids
    assert "scanner_ai" in role_ids
    assert "dispute_ai" in role_ids
    assert "retention_ai" in role_ids
    assert "operator_ai" in role_ids
    assert "compliance_guard_ai" in role_ids


def test_ai_operating_system_keeps_sensitive_actions_approval_gated():
    brief = build_ai_operating_system_brief()
    all_blocked_actions = [
        action
        for role in brief["roles"]
        for action in role["cannot_do_without_approval"]
    ]

    assert "scrape private consumer contacts" in all_blocked_actions
    assert "send disputes" in all_blocked_actions
    assert "send customer messages" in all_blocked_actions
    assert "approve legal disclosures" in all_blocked_actions


def test_ai_operating_system_requires_verification_and_private_data_protection():
    brief = build_ai_operating_system_brief()
    principles = {standard["principle"] for standard in brief["standards"]}

    assert "Verify after action" in principles
    assert "Private data protection" in principles
    assert brief["standard"] == "mission_oriented_verify_after_action_approval_gated"


def test_ai_operating_system_includes_fcra_rights_reference():
    brief = build_ai_operating_system_brief()
    reference = brief["fcra_rights_reference"]

    assert "Bureau of Consumer Financial Protection" in " ".join(reference["federal_agencies"])
    assert "Virginia" in reference["state_notice_states"]
    assert any("state rights" in rule for rule in reference["ai_rules"])
    assert reference["federal_consumer_rights_count"] >= 10
    assert "Maryland consumers" in reference["maryland_rights_summary"]


def test_ai_operating_system_includes_bureau_and_fdcpa_reference():
    brief = build_ai_operating_system_brief()
    reference = brief["bureau_debt_collection_reference"]

    assert reference["bureau_count"] == 3
    assert "Remains" in reference["experian_outcomes"]
    assert "Verified and updated" in reference["experian_outcomes"]
    assert reference["fdcpa_rule_count"] >= 10
    assert any("approval-gated" in rule for rule in reference["ai_rules"])
