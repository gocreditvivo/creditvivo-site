from pathlib import Path

import pytest

from admin_users import (
    append_provisioned_user,
    build_provisioned_user,
    read_provisioned_users,
    require_setup_token,
    role_templates,
)


def test_role_templates_include_owner_admin_all_privileges():
    roles = role_templates()

    assert "owner_admin" in roles
    assert "all_privileges" in roles["owner_admin"]["privileges"]


def test_require_setup_token_blocks_missing_or_wrong_token():
    with pytest.raises(ValueError, match="not configured"):
        require_setup_token("anything", None)

    with pytest.raises(PermissionError, match="Valid owner setup token"):
        require_setup_token("wrong", "right")


def test_build_provisioned_owner_admin_user_hashes_password():
    user, temporary_password = build_provisioned_user({
        "email": "Owner@CreditVivo.com",
        "display_name": "Owner",
        "role": "owner_admin",
        "temporary_password": "StrongPass123!",
    })

    assert user.email == "owner@creditvivo.com"
    assert user.role == "owner_admin"
    assert "all_privileges" in user.privileges
    assert temporary_password == "StrongPass123!"
    assert user.password_hash != temporary_password
    assert user.password_reset_required is True


def test_build_provisioned_user_rejects_bad_email_and_role():
    with pytest.raises(ValueError, match="valid email"):
        build_provisioned_user({"email": "bad", "role": "demo_customer"})

    with pytest.raises(ValueError, match="Unknown role"):
        build_provisioned_user({"email": "owner@creditvivo.com", "role": "superhero"})


def test_provisioned_user_log_round_trip(tmp_path: Path):
    log_path = tmp_path / "users.jsonl"
    user, _ = build_provisioned_user({
        "email": "partner.review@creditvivo.com",
        "role": "partner_reviewer",
    })

    append_provisioned_user(user, log_path)
    users = read_provisioned_users(log_path)

    assert len(users) == 1
    assert users[0]["email"] == "partner.review@creditvivo.com"
    assert users[0]["role"] == "partner_reviewer"
    assert "password_hash" in users[0]

