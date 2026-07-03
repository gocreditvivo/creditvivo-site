from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .rules_engine import get_rule_pack
except ImportError:
    from rules_engine import get_rule_pack


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(record: dict[str, Any], record_file: Path | None) -> None:
    if record_file is None:
        return
    record_file.parent.mkdir(parents=True, exist_ok=True)
    with record_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def create_approval_item(
    item_type: str,
    content: str | dict[str, Any],
    risk_level: str,
    record_file: Path | None = None,
) -> dict[str, Any]:
    rules = get_rule_pack("approval_queue_rules")
    risk = (risk_level or "medium").strip().lower()
    if risk not in rules.get("risk_levels", []):
        risk = "compliance_review"
    requires_approval = item_type in rules.get("approval_required_item_types", [])
    status = "founder_review_pending" if requires_approval or risk in {"high", "compliance_review"} else "draft_ready"
    item = {
        "ok": True,
        "approval_id": f"approval_{uuid.uuid4().hex[:12]}",
        "item_type": item_type,
        "content": content,
        "risk_level": risk,
        "status": status,
        "approval_required": True,
        "can_send_now": False,
        "created_at": now_iso(),
        "founder_review_note": rules.get("founder_review_note"),
    }
    _append_jsonl(item, record_file)
    return item
