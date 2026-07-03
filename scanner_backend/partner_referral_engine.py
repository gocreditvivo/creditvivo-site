from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .rules_engine import get_rule_pack
except ImportError:
    from rules_engine import get_rule_pack


def track_partner_referral(
    partner_id: str,
    lead_id: str,
    status: str,
    record_file: Path | None = None,
) -> dict[str, Any]:
    rules = get_rule_pack("partner_referral_rules")
    clean_status = (status or "new").strip().lower()
    if clean_status not in rules.get("allowed_statuses", []):
        clean_status = "new"
    record = {
        "ok": True,
        "partner_id": partner_id,
        "lead_id": lead_id,
        "status": clean_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "approval_required_before_outreach": True,
        "tracking_note": rules.get("tracking_note"),
    }
    if record_file is not None:
        record_file.parent.mkdir(parents=True, exist_ok=True)
        with record_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    return record
