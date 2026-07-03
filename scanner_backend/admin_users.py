from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import string
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


ROLE_TEMPLATES: dict[str, dict[str, Any]] = {
    "owner_admin": {
        "label": "Owner Admin",
        "privileges": [
            "all_privileges",
            "owner_ai_dashboard",
            "create_users",
            "manage_roles",
            "view_growth_ai",
            "view_scanner_results",
            "view_dispute_workflow",
            "approve_admin_actions",
            "view_partner_setup",
            "view_billing_overview",
            "view_system_health",
        ],
    },
    "partner_reviewer": {
        "label": "Partner Reviewer",
        "privileges": [
            "view_website_preview",
            "view_partner_docs",
            "view_demo_customer_flow",
        ],
    },
    "technical_reviewer": {
        "label": "Technical Reviewer",
        "privileges": [
            "view_backend_docs",
            "test_scanner_api",
            "view_code_review_packet",
            "view_system_health",
        ],
    },
    "demo_customer": {
        "label": "Demo Customer",
        "privileges": [
            "view_customer_dashboard",
            "start_demo_scan",
            "view_findings",
            "view_dispute_tracking_preview",
        ],
    },
}


@dataclass(frozen=True)
class ProvisionedUser:
    user_id: str
    email: str
    display_name: str
    role: str
    role_label: str
    privileges: list[str]
    password_hash: str
    password_salt: str
    password_reset_required: bool
    created_by: str
    created_at: str
    status: str = "provisioned_not_connected_to_full_auth"


def role_templates() -> dict[str, dict[str, Any]]:
    return ROLE_TEMPLATES


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return digest.hex()


def generate_temporary_password(length: int = 18) -> str:
    alphabet = string.ascii_letters + string.digits + "!@$%"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(char.islower() for char in password)
            and any(char.isupper() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in "!@$%" for char in password)
        ):
            return password


def require_setup_token(provided_token: str | None, expected_token: str | None) -> None:
    if not expected_token:
        raise ValueError("ADMIN_SETUP_TOKEN is not configured on the backend.")
    if not provided_token or not hmac.compare_digest(provided_token, expected_token):
        raise PermissionError("Valid owner setup token is required.")


def build_provisioned_user(payload: dict[str, Any], *, created_by: str = "owner") -> tuple[ProvisionedUser, str]:
    email = str(payload.get("email", "")).strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("A valid email is required.")

    role = str(payload.get("role", "demo_customer")).strip()
    if role not in ROLE_TEMPLATES:
        raise ValueError(f"Unknown role: {role}")

    display_name = str(payload.get("display_name") or email.split("@")[0]).strip()
    temporary_password = str(payload.get("temporary_password") or generate_temporary_password()).strip()
    if len(temporary_password) < 12:
        raise ValueError("Temporary password must be at least 12 characters.")

    salt = secrets.token_hex(16)
    role_template = ROLE_TEMPLATES[role]
    user = ProvisionedUser(
        user_id=f"cvu_{secrets.token_hex(8)}",
        email=email,
        display_name=display_name,
        role=role,
        role_label=str(role_template["label"]),
        privileges=list(role_template["privileges"]),
        password_hash=_hash_password(temporary_password, salt),
        password_salt=salt,
        password_reset_required=True,
        created_by=created_by,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return user, temporary_password


def append_provisioned_user(user: ProvisionedUser, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(user), sort_keys=True) + "\n")


def read_provisioned_users(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    users = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            users.append(json.loads(line))
    return users

