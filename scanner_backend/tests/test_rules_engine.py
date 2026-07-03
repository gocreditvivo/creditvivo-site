from rules_engine import EXPECTED_RULE_FILES, get_rule_pack, load_all_rules, load_yaml_rule_file


def test_all_yaml_rule_files_load():
    for filename in EXPECTED_RULE_FILES.values():
        payload = load_yaml_rule_file(filename)
        assert isinstance(payload, dict)
        assert payload


def test_load_all_rules_returns_expected_keys():
    rules = load_all_rules()
    assert set(rules) == set(EXPECTED_RULE_FILES)


def test_no_rule_pack_is_empty():
    for rule_name, payload in load_all_rules().items():
        assert payload, rule_name
        assert get_rule_pack(rule_name) == payload

