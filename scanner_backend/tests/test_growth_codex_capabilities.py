from growth_codex_capabilities import build_codex_like_growth_brief


def test_codex_like_growth_brief_includes_core_capabilities():
    brief = build_codex_like_growth_brief()
    names = {capability["name"] for capability in brief["capabilities"]}

    assert "Mission planning" in names
    assert "Research synthesis" in names
    assert "Problem diagnosis" in names
    assert "Verification after action" in names
    assert "Codex advisor handoff" in names


def test_codex_like_growth_brief_identifies_missing_runtime_needs():
    brief = build_codex_like_growth_brief()
    next_steps = " ".join(brief["next_build_steps"])

    assert "live analytics" in next_steps
    assert "persistent experiment memory" in next_steps
    assert "owner approval queue" in next_steps
    assert "Codex SDK" in next_steps


def test_codex_like_growth_brief_has_maturity_counts():
    brief = build_codex_like_growth_brief()

    assert brief["ok"] is True
    assert brief["maturity_counts"]["foundation_ready"] >= 1
    assert brief["service"] == "credit-vivo-growth-codex-like-capabilities"
