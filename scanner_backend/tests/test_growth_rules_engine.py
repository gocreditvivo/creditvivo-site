from rules_engine import get_rule_pack, load_all_rules, load_yaml_rule_file


GROWTH_RULE_KEYS = {
    "growth_ai_skills",
    "market_ai_rules",
    "growth_compliance_rules",
    "partner_referral_rules",
    "revenue_attribution_rules",
    "approval_queue_rules",
    "campaign_timing_rules",
}


def test_growth_rule_files_load():
    rules = load_all_rules()

    assert GROWTH_RULE_KEYS.issubset(rules.keys())
    for key in GROWTH_RULE_KEYS:
        assert get_rule_pack(key)


def test_growth_compliance_rules_have_required_guardrails():
    rules = load_yaml_rule_file("growth_compliance_rules.yml")

    assert "guaranteed score increase" in rules["blocked_phrases"]
    assert "results vary" in rules["safe_phrases"]
    assert rules["attorney_wording"] == "Attorney support may be available for eligible unresolved credit-reporting issues."
