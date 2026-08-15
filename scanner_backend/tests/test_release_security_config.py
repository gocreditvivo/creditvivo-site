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


def test_sky_bell_has_size_and_timeout_limits():
    source = (ROOT / "api" / "sky-bell.js").read_text(encoding="utf-8")
    assert "MAX_REQUEST_BYTES" in source
    assert "MAX_RESPONSE_BYTES" in source
    assert "UPSTREAM_TIMEOUT_MS" in source
    assert "AbortController" in source
