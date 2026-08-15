from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_browser_does_not_persist_scan_results_in_local_storage():
    source = (ROOT / "src" / "lib" / "scanStorage.ts").read_text(encoding="utf-8")
    assert "localStorage" not in source
    assert ".from('credit_scans')" in source
    assert "creditvivo_findings" not in source


def test_privileged_route_uses_only_server_controlled_role_claim():
    source = (ROOT / "src" / "auth" / "RoleProtectedRoute.tsx").read_text(encoding="utf-8")
    assert "app_metadata?.role" in source
    assert "user_metadata?.role" not in source


def test_frontend_security_headers_are_configured():
    vercel = (ROOT / "vercel.json").read_text(encoding="utf-8")
    for header in (
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ):
        assert header in vercel


def test_unused_sky_bell_proxy_is_release_disabled_without_connector_dependency():
    source = (ROOT / "api" / "sky-bell.js").read_text(encoding="utf-8")
    assert "status(404)" in source
    assert "fetch(" not in source
    assert "@vercel/connect" not in source


def test_parser_export_uses_a_killable_wall_clock_deadline():
    source = (ROOT / "scanner_backend" / "main.py").read_text(encoding="utf-8")
    assert "build_scanner_outputs_with_hard_deadline" in source
    assert 'multiprocessing.get_context("spawn")' in source
    assert "process.join(timeout_seconds)" in source
    assert "process.terminate()" in source


def test_scan_persistence_and_rollback_use_server_only_atomic_rpcs():
    source = (ROOT / "scanner_backend" / "main.py").read_text(encoding="utf-8")
    assert '"rpc/create_credit_scan"' in source
    assert '"rpc/rollback_credit_scan"' in source
    assert '"PATCH",\n        "credit_cases"' not in source
    assert "Secure artifact rollback rejected" in source
