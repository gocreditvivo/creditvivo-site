from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

try:
    from .growth_ai import GrowthSnapshot
    from .operator_ai import OperatorEvent
except ImportError:
    from growth_ai import GrowthSnapshot
    from operator_ai import OperatorEvent


@dataclass(frozen=True)
class VivoEvent:
    event_type: str
    source: str
    timestamp: str
    customer_id: str | None = None
    lead_id: str | None = None
    campaign: str | None = None
    partner: str | None = None
    amount: float = 0.0
    metadata: Dict[str, object] | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_event(payload: Dict[str, object]) -> VivoEvent:
    return VivoEvent(
        event_type=str(payload.get("event_type", "unknown")),
        source=str(payload.get("source", "unknown")),
        timestamp=str(payload.get("timestamp") or now_iso()),
        customer_id=payload.get("customer_id") if payload.get("customer_id") else None,
        lead_id=payload.get("lead_id") if payload.get("lead_id") else None,
        campaign=payload.get("campaign") if payload.get("campaign") else None,
        partner=payload.get("partner") if payload.get("partner") else None,
        amount=float(payload.get("amount") or 0.0),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
    )


def append_event(event: VivoEvent, event_file: Path) -> None:
    event_file.parent.mkdir(parents=True, exist_ok=True)
    with event_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), separators=(",", ":")) + "\n")


def read_events(event_file: Path) -> List[VivoEvent]:
    if not event_file.exists():
        return []

    events: List[VivoEvent] = []
    for line in event_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        events.append(build_event(data))
    return events


def growth_snapshot_from_events(events: Iterable[VivoEvent]) -> GrowthSnapshot:
    visitors = leads = free_scans_started = free_scans_completed = paid_customers = cancellations = 0
    monthly_recurring_revenue = ad_spend = 0.0
    referral_signups = 0

    for event in events:
        event_type = event.event_type
        if event_type == "website_visit":
            visitors += 1
        elif event_type in {"join_clicked", "lead_created"}:
            leads += 1
        elif event_type == "scan_started":
            free_scans_started += 1
        elif event_type == "scan_completed":
            free_scans_completed += 1
        elif event_type == "paid_upgrade":
            paid_customers += 1
            monthly_recurring_revenue += event.amount
        elif event_type == "customer_cancelled":
            cancellations += 1
        elif event_type == "ad_spend":
            ad_spend += event.amount
        elif event_type == "referral_signup":
            referral_signups += 1
            leads += 1

    return GrowthSnapshot(
        visitors=visitors,
        leads=leads,
        free_scans_started=free_scans_started,
        free_scans_completed=free_scans_completed,
        paid_customers=paid_customers,
        monthly_recurring_revenue=round(monthly_recurring_revenue, 2),
        cancellations=cancellations,
        ad_spend=round(ad_spend, 2),
        referral_signups=referral_signups,
    )


def operator_events_from_vivo_events(events: Iterable[VivoEvent]) -> List[OperatorEvent]:
    operator_events: List[OperatorEvent] = []

    for event in events:
        if event.event_type == "scan_failed":
            operator_events.append(OperatorEvent(
                area="scanner",
                event_type="parse_failed",
                severity="high",
                detail="A customer scan failed and needs review.",
                customer_id=event.customer_id,
            ))
        elif event.event_type == "customer_stuck":
            operator_events.append(OperatorEvent(
                area="customer",
                event_type="stuck",
                severity="medium",
                detail="A customer appears stuck and may need a progress update.",
                customer_id=event.customer_id,
            ))
        elif event.event_type == "failed_payment":
            operator_events.append(OperatorEvent(
                area="payments",
                event_type="failed_payment",
                severity="medium",
                detail="A customer payment failed.",
                customer_id=event.customer_id,
            ))
        elif event.event_type == "dispute_letter_ready":
            operator_events.append(OperatorEvent(
                area="compliance",
                event_type="letter_ready",
                severity="high",
                detail="A dispute letter is ready and needs approval before sending.",
                customer_id=event.customer_id,
            ))
        elif event.event_type == "campaign_needed":
            operator_events.append(OperatorEvent(
                area="growth",
                event_type="campaign_needed",
                severity="low",
                detail="Growth AI detected a campaign opportunity.",
            ))

    return operator_events


def summarize_events(events: List[VivoEvent]) -> Dict[str, object]:
    by_type: Dict[str, int] = {}
    by_source: Dict[str, int] = {}

    for event in events:
        by_type[event.event_type] = by_type.get(event.event_type, 0) + 1
        by_source[event.source] = by_source.get(event.source, 0) + 1

    return {
        "event_count": len(events),
        "by_type": by_type,
        "by_source": by_source,
    }
