from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_consent(
    customer_id: str,
    consent_type: str,
    channel: str,
    consent_text: str,
    record_file: Path | None = None,
) -> dict[str, Any]:
    record = {
        "ok": True,
        "consent_id": f"consent_{uuid.uuid4().hex[:12]}",
        "customer_id": customer_id,
        "consent_type": consent_type,
        "channel": channel,
        "consent_text": consent_text,
        "timestamp": now_iso(),
    }
    if record_file is not None:
        record_file.parent.mkdir(parents=True, exist_ok=True)
        with record_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    return record
