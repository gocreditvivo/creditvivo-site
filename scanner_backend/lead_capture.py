from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class CapturedLead:
    email: str
    first_name: str
    goal: str
    campaign: str | None
    source: str
    consent_to_contact: bool
    timestamp: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_lead(payload: Dict[str, object]) -> CapturedLead:
    email = str(payload.get("email", "")).strip().lower()
    first_name = str(payload.get("first_name", "")).strip()
    goal = str(payload.get("goal", "")).strip()
    campaign_value = payload.get("campaign")
    source = str(payload.get("source", "join_page")).strip() or "join_page"
    consent_to_contact = bool(payload.get("consent_to_contact", False))

    if not EMAIL_RE.match(email):
        raise ValueError("A valid email is required.")
    if not first_name:
        raise ValueError("First name is required.")
    if not goal:
        raise ValueError("Goal is required.")
    if not consent_to_contact:
        raise ValueError("Consent to contact is required.")

    return CapturedLead(
        email=email,
        first_name=first_name,
        goal=goal,
        campaign=str(campaign_value).strip() if campaign_value else None,
        source=source,
        consent_to_contact=True,
        timestamp=str(payload.get("timestamp") or now_iso()),
    )


def append_lead(lead: CapturedLead, lead_file: Path) -> None:
    lead_file.parent.mkdir(parents=True, exist_ok=True)
    with lead_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(lead), separators=(",", ":")) + "\n")


def read_leads(lead_file: Path) -> List[CapturedLead]:
    if not lead_file.exists():
        return []

    leads: List[CapturedLead] = []
    for line in lead_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        leads.append(CapturedLead(**data))
    return leads


def summarize_leads(leads: List[CapturedLead]) -> Dict[str, object]:
    by_campaign: Dict[str, int] = {}
    by_goal: Dict[str, int] = {}

    for lead in leads:
        campaign = lead.campaign or "direct"
        by_campaign[campaign] = by_campaign.get(campaign, 0) + 1
        by_goal[lead.goal] = by_goal.get(lead.goal, 0) + 1

    return {
        "lead_count": len(leads),
        "by_campaign": by_campaign,
        "by_goal": by_goal,
    }
