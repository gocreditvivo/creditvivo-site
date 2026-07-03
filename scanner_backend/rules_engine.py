from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


RULES_DIR = Path(__file__).resolve().parent / "rules"
EXPECTED_RULE_FILES = {
    "fcra_rules": "fcra_rules.yml",
    "metro2_field_map": "metro2_field_map.yml",
    "metro2_issue_rules": "metro2_issue_rules.yml",
    "negative_account_rules": "negative_account_rules.yml",
    "eoscar_workflow_rules": "eoscar_workflow_rules.yml",
    "compliance_guard_rules": "compliance_guard_rules.yml",
    "growth_ai_skills": "growth_ai_skills.yml",
    "market_ai_rules": "market_ai_rules.yml",
    "growth_compliance_rules": "growth_compliance_rules.yml",
    "partner_referral_rules": "partner_referral_rules.yml",
    "revenue_attribution_rules": "revenue_attribution_rules.yml",
    "approval_queue_rules": "approval_queue_rules.yml",
    "campaign_timing_rules": "campaign_timing_rules.yml",
}


def load_yaml_rule_file(filename: str) -> dict[str, Any]:
    path = RULES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Scanner rule file not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Scanner rule file must contain a mapping: {path}")
    return payload


def load_rule_file(name: str) -> dict[str, Any]:
    # Backward-compatible alias used by existing scanner code.
    try:
        return load_yaml_rule_file(name)
    except Exception:
        path = RULES_DIR / name
        return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_all_rules() -> dict[str, dict[str, Any]]:
    return {
        rule_name: load_yaml_rule_file(filename)
        for rule_name, filename in EXPECTED_RULE_FILES.items()
    }


def load_scanner_rules() -> dict[str, dict[str, Any]]:
    # Backward-compatible alias used by existing scanner code.
    return load_all_rules()


def get_rule_pack(rule_name: str) -> dict[str, Any]:
    rules = load_all_rules()
    if rule_name not in rules:
        raise KeyError(f"Unknown scanner rule pack: {rule_name}")
    return rules[rule_name]


def _tradeline_blob(tradeline: Any) -> str:
    parts = []
    for field in (
        "account_name",
        "account_type",
        "portfolio_type",
        "responsibility",
        "creditor_classification",
        "original_creditor",
        "collector_or_debt_buyer",
        "status",
        "pay_status",
        "remarks",
        "payment_history_summary",
        "raw_block",
    ):
        value = getattr(tradeline, field, "")
        if isinstance(tradeline, dict):
            value = tradeline.get(field, value)
        parts.append(str(value or ""))
    return " ".join(parts).lower()


def classify_negative_tradeline(tradeline: Any, rules: dict[str, dict[str, Any]] | None = None) -> list[dict[str, str]]:
    rules = rules or load_scanner_rules()
    blob = _tradeline_blob(tradeline)
    matches: list[dict[str, str]] = []
    for category in rules["negative_account_rules"].get("categories", []):
        keywords = [str(keyword).lower() for keyword in category.get("keywords", [])]
        status_codes = [str(code) for code in category.get("metro2_status_codes", [])]
        code_match = any(re.search(rf"\b{re.escape(code)}\b", blob) for code in status_codes)
        keyword_match = any(keyword in blob for keyword in keywords)
        if keyword_match or code_match:
            matches.append({
                "id": category.get("id", ""),
                "label": category.get("label", ""),
                "priority": category.get("priority", "medium"),
                "review_reason": category.get("review_reason", ""),
                "metro2_status_codes": ", ".join(status_codes),
            })
    return matches


def blocked_compliance_phrases(text: str, rules: dict[str, dict[str, Any]] | None = None) -> list[str]:
    rules = rules or load_scanner_rules()
    lowered = (text or "").lower()
    return [
        phrase
        for phrase in rules["compliance_guard_rules"].get("blocked_phrases", [])
        if phrase.lower() in lowered
    ]
