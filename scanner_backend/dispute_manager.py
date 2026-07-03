from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from jinja2 import Template
from sqlalchemy import JSON, Column, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class DisputeStatus(str, Enum):
    DRAFTING = "drafting"
    DATA_HYGIENE = "data_hygiene"
    FORENSIC_AUDIT = "forensic_audit"
    PROCESS_AUDIT = "process_audit"
    ESCALATED_MOV = "escalated_mov"
    LEGAL_ENDGAME = "legal_endgame"
    CLOSED = "closed"


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True)
    status = Column(SqlEnum(DisputeStatus), default=DisputeStatus.DRAFTING, nullable=False)
    history_log = Column(JSON, default=list)
    forensic_data = Column(JSON, default=dict)
    lob_tracking_number = Column(String)


@dataclass
class ManagedDispute:
    id: int
    status: DisputeStatus = DisputeStatus.DRAFTING
    history_log: list[dict[str, Any]] = field(default_factory=list)
    forensic_data: dict[str, Any] = field(default_factory=dict)
    lob_tracking_number: str | None = None


HISTORY_TEMPLATE = Template(
    """TO: {{ bureau_name }}
RE: DISPUTE HISTORY SUMMARY - ACCOUNT #{{ account_number }}

HISTORY OF DISPUTE:
{% for entry in history_log -%}
- {{ entry.timestamp }}: Strategy {{ entry.strategy }} (Outcome: {{ entry.outcome }})
{% endfor %}
STATEMENT:
I have disputed this item {{ history_count }} times. You have failed to perform a reasonable investigation under FCRA 611(a)(7). This letter serves as formal notice of non-compliance. My evidence is attached. Please verify or delete immediately.
"""
)


class DisputeManager:
    def audit_tradeline(self, raw_json: dict[str, Any]) -> dict[str, Any]:
        bureau_rows = raw_json.get("bureaus", [])
        flags: list[dict[str, Any]] = []

        self._flag_contradiction(flags, bureau_rows, "balance", "balance_mismatch")
        self._flag_contradiction(flags, bureau_rows, "date_of_first_delinquency", "dofd_mismatch")
        self._flag_contradiction(flags, bureau_rows, "status", "status_mismatch")

        for row in bureau_rows:
            if row.get("closed") and self._money(row.get("balance")) > 0 and row.get("sold_or_transferred"):
                flags.append({
                    "type": "closed_sold_balance",
                    "bureau": row.get("bureau"),
                    "message": "Closed/sold/transferred account reports a non-zero balance.",
                })

        return {
            "account_number": raw_json.get("account_number"),
            "has_contradictions": bool(flags),
            "flags": flags,
            "flag_count": len(flags),
        }

    def transition_state(self, dispute: ManagedDispute, response_type: str) -> ManagedDispute:
        normalized = (response_type or "").strip().lower()
        if normalized == "verified":
            dispute.status = DisputeStatus.ESCALATED_MOV
            outcome = "Verified - Strategy B MOV escalation triggered"
        elif normalized in {"deleted", "corrected", "updated"}:
            dispute.status = DisputeStatus.CLOSED
            outcome = normalized.title()
        elif normalized in {"no_response", "stall"}:
            dispute.status = DisputeStatus.PROCESS_AUDIT
            outcome = "No response - process audit"
        else:
            dispute.status = DisputeStatus.FORENSIC_AUDIT
            outcome = "Further forensic review"

        dispute.history_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strategy": self.strategy_for_round(len(dispute.history_log) + 1),
            "response_type": response_type,
            "outcome": outcome,
            "customer_message": (
                "The bureau is standing their ground, but our engine found a flaw. "
                "Escalating to Strategy B. No action required."
                if normalized == "verified"
                else outcome
            ),
        })
        return dispute

    def generate_history_summary_header(
        self,
        dispute: ManagedDispute,
        bureau_name: str,
        account_number: str,
    ) -> str:
        return HISTORY_TEMPLATE.render(
            bureau_name=bureau_name,
            account_number=account_number,
            history_log=dispute.history_log,
            history_count=len(dispute.history_log),
        )

    @staticmethod
    def strategy_for_round(round_number: int) -> str:
        if round_number <= 3:
            return "Data Hygiene"
        if round_number <= 6:
            return "Forensic Audit"
        if round_number <= 9:
            return "Process Audit"
        return "Legal Endgame"

    @staticmethod
    def _flag_contradiction(
        flags: list[dict[str, Any]],
        rows: list[dict[str, Any]],
        field_name: str,
        flag_type: str,
    ) -> None:
        values = {
            str(row.get(field_name)).strip().lower()
            for row in rows
            if row.get(field_name) not in {None, ""}
        }
        if len(values) > 1:
            flags.append({
                "type": flag_type,
                "field": field_name,
                "values": sorted(values),
                "message": f"{field_name} differs across bureaus.",
            })

    @staticmethod
    def _money(value: Any) -> float:
        if value in {None, ""}:
            return 0.0
        try:
            return float(str(value).replace("$", "").replace(",", ""))
        except ValueError:
            return 0.0


def make_mock_bureau_json(index: int) -> dict[str, Any]:
    base_balance = 1000 + index
    return {
        "account_number": f"MOCK-{index:04d}",
        "bureaus": [
            {
                "bureau": "Experian",
                "balance": f"${base_balance}",
                "date_of_first_delinquency": "01/2021",
                "status": "Collection",
                "closed": True,
                "sold_or_transferred": True,
            },
            {
                "bureau": "Equifax",
                "balance": f"${base_balance + 75}",
                "date_of_first_delinquency": "02/2021",
                "status": "Charge-off",
                "closed": True,
                "sold_or_transferred": True,
            },
            {
                "bureau": "TransUnion",
                "balance": f"${base_balance}",
                "date_of_first_delinquency": "01/2021",
                "status": "Collection",
                "closed": True,
                "sold_or_transferred": True,
            },
        ],
    }
