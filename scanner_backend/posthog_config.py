from __future__ import annotations

import atexit
import os
import warnings
from functools import lru_cache

try:
    from posthog import Posthog
    _POSTHOG_AVAILABLE = True
except ImportError:
    _POSTHOG_AVAILABLE = False

_posthog_client = None


def _make_client() -> object | None:
    token = os.getenv("POSTHOG_PROJECT_TOKEN", "")
    host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
    disabled = os.getenv("POSTHOG_DISABLED", "false").lower() == "true"

    if disabled or not _POSTHOG_AVAILABLE:
        return None

    debug = os.getenv("SCANNER_ENVIRONMENT", "local").lower() != "production"

    if not token or token == "<ph_project_token>":
        if debug:
            warnings.warn(
                "POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, "
                "this causes events to be silently missed. "
                "This error stops appearing once POSTHOG_PROJECT_TOKEN is configured",
                stacklevel=2,
            )
        return None

    client = Posthog(
        project_api_key=token,
        host=host,
        debug=debug,
        enable_exception_autocapture=True,
    )
    atexit.register(client.shutdown)
    return client


def get_posthog():
    global _posthog_client
    if _posthog_client is None:
        _posthog_client = _make_client()
    return _posthog_client


def capture(distinct_id: str, event: str, properties: dict | None = None) -> None:
    client = get_posthog()
    if client is None:
        return
    client.capture(distinct_id=distinct_id, event=event, properties=properties or {})


def flush() -> None:
    client = get_posthog()
    if client is not None:
        client.flush()
