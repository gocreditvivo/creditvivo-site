from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def attribute_revenue(
    customer_id: str,
    source: str,
    campaign: str,
    partner_id: str | None,
    amount: float,
    record_file: Path | None = None,
) -> dict[str, Any]:
    record = {
        "ok": True,
        "customer_id": customer_id,
        "source": source,
        "campaign": campaign,
        "partner_id": partner_id,
        "amount": round(float(amount), 2),
        "attributed_at": datetime.now(timezone.utc).isoformat(),
        "internal_use_only": True,
    }
    if record_file is not None:
        record_file.parent.mkdir(parents=True, exist_ok=True)
        with record_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    return record
