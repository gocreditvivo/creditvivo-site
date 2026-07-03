from codex_advisor_ai import CODEX_ADVISOR_SKILLS, build_codex_advisor_brief


def test_codex_advisor_defines_growth_advice_skills():
    skill_names = {skill.name for skill in CODEX_ADVISOR_SKILLS}

    assert "growth_strategy_review" in skill_names
    assert "ad_copy_review" in skill_names
    assert "funnel_diagnostics" in skill_names
    assert "measurement_plan" in skill_names


def test_codex_advisor_builds_prompt_with_growth_context():
    brief = build_codex_advisor_brief(
        question="Which ad should Credit Vivo launch first?",
        focus="ad_copy_review",
    )

    prompt = brief["codex_prompt"]

    assert brief["service"] == "credit-vivo-codex-advisor-bridge"
    assert "Credit Vivo Growth AI" in prompt
    assert "Which ad should Credit Vivo launch first?" in prompt
    assert "Required output" in prompt
    assert "owner approval" in brief["approval_rule"].lower()


def test_codex_advisor_states_direct_connection_needs_sdk_setup():
    brief = build_codex_advisor_brief()

    assert "Codex SDK" in brief["codex_capability_path"]["next"]
    assert "task queue" in brief["codex_capability_path"]["future"]
