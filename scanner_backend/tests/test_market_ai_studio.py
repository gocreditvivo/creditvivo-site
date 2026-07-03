import asyncio

import main
from market_ai_studio import (
    build_market_ai_dashboard,
    check_marketing_compliance,
    create_render_job,
    generate_learning_storyboard,
    generate_video_script,
    get_topic,
    sample_market_assets,
)


def _run(coro):
    return asyncio.run(coro)


def test_market_ai_pages_load_without_stock_dependency():
    responses = [
        main.market_ai_home(),
        main.market_ai_subpage(),
    ]
    for response in responses:
        text = response.body.decode("utf-8")
        assert response.status_code == 200
        assert "Credit Vivo Market AI" in text
        assert "No auto-publishing" in text
        assert "Stock Dependencies</p><h2>0" in text


def test_market_ai_assets_are_owned_approval_gated():
    dashboard = build_market_ai_dashboard()
    assets = sample_market_assets()
    assert dashboard["asset_policy"]["outside_stock_footage_dependencies"] is False
    assert dashboard["asset_policy"]["raw_credit_report_access_allowed"] is False
    assert assets
    assert all(asset["source"] == "Credit Vivo generated" for asset in assets)
    assert all(asset["approval_required"] is True for asset in assets)
    assert all(asset["auto_publish_allowed"] is False for asset in assets)
    assert all(asset["uses_stock_assets"] is False for asset in assets)


def test_market_ai_compliance_blocks_banned_phrase():
    result = check_marketing_compliance("Guaranteed score increase and approved for mortgage.")
    assert result["ok"] is False
    assert {flag["phrase"] for flag in result["flags"]} >= {"guaranteed score increase", "approved for mortgage"}
    assert result["auto_publish_allowed"] is False


def test_market_ai_storyboard_and_script_are_12_scene_safe_outputs():
    topic = get_topic("three-bureau-comparison")
    storyboard = generate_learning_storyboard(topic)
    script = generate_video_script(topic)
    assert storyboard["topic_id"] == "three-bureau-comparison"
    assert len(storyboard["scenes"]) == 12
    assert storyboard["uses_stock_assets"] is False
    assert storyboard["auto_publish_allowed"] is False
    assert script["approval_required"] is True
    assert script["auto_publish_allowed"] is False


def test_market_ai_render_job_is_preview_only():
    job = create_render_job({"asset_id": "market-demo-1", "template_id": "weekly-report-refresh-3min", "format": "9:16"})
    assert job["status"] == "Queued For Review"
    assert job["auto_publish_allowed"] is False
    assert job["approval_required_before_export"] is True


def test_market_ai_api_functions_return_expected_shapes():
    assets_response = main.market_assets_api()
    assets = assets_response.body.decode("utf-8")
    assert "market-demo-1" in assets
    compliance_response = _run(main.market_compliance_check_api({"text": "delete anything"}))
    assert "banned_phrase" in compliance_response.body.decode("utf-8")
    storyboard_response = _run(main.market_generate_storyboard_api({"topic_id": "free-weekly-reports"}))
    assert '"scene":12' in storyboard_response.body.decode("utf-8").replace(" ", "")
