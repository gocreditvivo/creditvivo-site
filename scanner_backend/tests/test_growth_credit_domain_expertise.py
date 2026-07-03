from growth_credit_domain_expertise import build_credit_domain_expertise_brief


def test_credit_domain_expertise_includes_required_topics():
    brief = build_credit_domain_expertise_brief()
    topics = {topic["topic"] for topic in brief["topics"]}

    assert "FCRA" in topics
    assert "FACTA" in topics
    assert "Metro 2" in topics
    assert "Credit report dispute process" in topics
    assert "FCRA federal and state rights routing" in topics
    assert "FDCPA debt collection conduct" in topics
    assert "Soft pull vs hard pull" in topics


def test_credit_domain_expertise_supports_growth_use_cases():
    brief = build_credit_domain_expertise_brief()
    uses = " ".join(brief["how_growth_ai_uses_this"])

    assert "customer-facing language" in uses
    assert "ads and landing pages" in uses
    assert "scanner findings" in uses
    assert brief["service"] == "credit-vivo-growth-credit-domain-expertise"


def test_credit_domain_expertise_has_customer_angles():
    brief = build_credit_domain_expertise_brief()

    assert any("Collection" in angle for angle in brief["example_customer_angles"])
    assert any("auto loan" in angle for angle in brief["example_customer_angles"])


def test_credit_domain_expertise_includes_state_rights_reference():
    brief = build_credit_domain_expertise_brief()
    reference = brief["fcra_rights_reference"]

    assert "state Attorney General" in reference["plain_english_note"]
    assert "Texas" in reference["state_notice_states"]
    assert reference["federal_consumer_rights_count"] >= 10
    assert "Maryland consumers" in reference["maryland_rights_summary"]


def test_credit_domain_expertise_includes_bureau_and_fdcpa_reference():
    brief = build_credit_domain_expertise_brief()
    reference = brief["bureau_debt_collection_reference"]

    assert "Deleted" in reference["experian_outcomes"]
    assert "Remains" in reference["experian_outcomes"]
    assert reference["fdcpa_rule_count"] >= 10
