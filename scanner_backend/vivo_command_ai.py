from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

try:
    from .ai_operating_system import build_ai_operating_system_brief
    from .bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from .fcra_rights_reference import build_fcra_rights_reference
    from .growth_ai import GrowthSnapshot, build_growth_brief
    from .operator_ai import OperatorEvent, build_operator_brief, demo_operator_events
except ImportError:
    from ai_operating_system import build_ai_operating_system_brief
    from bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from fcra_rights_reference import build_fcra_rights_reference
    from growth_ai import GrowthSnapshot, build_growth_brief
    from operator_ai import OperatorEvent, build_operator_brief, demo_operator_events


@dataclass(frozen=True)
class CommandMission:
    id: str
    name: str
    objective: str
    success_metric: str
    status: str
    approval_boundary: str


COMMAND_MISSIONS: List[CommandMission] = [
    CommandMission(
        id="growth",
        name="Growth AI",
        objective="Bring qualified customers into the Credit Vivo funnel.",
        success_metric="More free scans started, paid upgrades, and lower cost per paid customer.",
        status="foundation_ready",
        approval_boundary="AI can draft campaigns; founder approves spend and public messaging.",
    ),
    CommandMission(
        id="scanner",
        name="Scanner AI",
        objective="Find possible credit report problems and explain them in plain English.",
        success_metric="Reports parsed, findings created, and next steps prepared.",
        status="backend_ready",
        approval_boundary="AI can analyze; customer/compliance approval required before letters are sent.",
    ),
    CommandMission(
        id="operator",
        name="Operator AI",
        objective="Watch Credit Vivo systems and recommend fixes when something needs attention.",
        success_metric="Issues detected, prioritized, and routed before customers are harmed.",
        status="foundation_ready",
        approval_boundary="AI can create safe internal tasks; sensitive actions require approval.",
    ),
    CommandMission(
        id="retention",
        name="Retention AI",
        objective="Find customers likely to cancel or get stuck before they leave.",
        success_metric="Lower cancellation risk and faster customer progress updates.",
        status="needs_customer_data",
        approval_boundary="AI can draft messages; founder approves customer-facing sends.",
    ),
    CommandMission(
        id="compliance",
        name="Compliance Guard AI",
        objective="Flag risky actions, missing consent, and approval gaps.",
        success_metric="No dispute, legal, payment, or customer-facing action occurs without proper approval.",
        status="foundation_ready",
        approval_boundary="Compliance/attorney review required for regulated or legal actions.",
    ),
]


def mission_to_dict(mission: CommandMission) -> Dict[str, str]:
    return {
        "id": mission.id,
        "name": mission.name,
        "objective": mission.objective,
        "success_metric": mission.success_metric,
        "status": mission.status,
        "approval_boundary": mission.approval_boundary,
    }


def build_command_brief(
    growth_snapshot: GrowthSnapshot | None = None,
    operator_events: List[OperatorEvent] | None = None,
) -> Dict[str, object]:
    snapshot = growth_snapshot or GrowthSnapshot()
    events = operator_events or demo_operator_events()
    growth = build_growth_brief(snapshot)
    operator = build_operator_brief(events)
    ai_system = build_ai_operating_system_brief()
    fcra_rights = build_fcra_rights_reference()
    bureau_reference = build_bureau_debt_collection_reference()

    top_actions = []
    for action in growth["recommended_actions"][:3]:
        top_actions.append({
            "mission": "Growth AI",
            "priority": "revenue_growth",
            "issue": action["issue"],
            "recommended_action": action["action"],
            "approval_required": False,
        })

    for action in operator["actions"][:3]:
        top_actions.append({
            "mission": "Operator AI",
            "priority": action["severity"],
            "issue": f"{action['area']}: {action['event_type']}",
            "recommended_action": action["recommended_action"],
            "approval_required": action["approval_required"],
        })

    return {
        "ok": True,
        "service": "vivo-command-ai",
        "mode": "mission_oriented_watch_recommend_approve",
        "mission_statement": "Automate Credit Vivo operations toward growth, customer help, and compliance-safe execution.",
        "operating_standard": ai_system["standard"],
        "revenue_goal": {
            "monthly_target": 1000000,
            "current_mrr": snapshot.monthly_recurring_revenue,
            "paid_customer_gap": growth["million_month_target"]["paid_customer_gap"],
        },
        "missions": [mission_to_dict(mission) for mission in COMMAND_MISSIONS],
        "ai_operating_system": ai_system,
        "top_actions": top_actions,
        "automation_policy": {
            "can_do_now": [
                "monitor systems",
                "calculate growth funnel health",
                "score leads",
                "draft campaigns",
                "draft customer updates",
                "create internal tasks",
                "prepare founder briefs",
            ],
            "approval_required": [
                "send customer messages",
                "send dispute letters",
                "issue refunds",
                "change pricing",
                "change legal/compliance language",
                "submit CFPB/state complaints",
                "route FCRA federal regulator or state Attorney General complaints",
                "refer to attorney/legal provider",
            ],
        },
        "fcra_rights_reference": {
            "plain_english_note": fcra_rights["source_notes"]["plain_english_note"],
            "source": fcra_rights["source_notes"]["primary_reference"],
            "federal_consumer_rights_count": len(fcra_rights["federal_consumer_rights"]),
            "maryland_rights_summary": fcra_rights["maryland_consumer_rights"]["plain_english_summary"],
            "state_notice_count": len(fcra_rights["state_notice_links"]),
            "federal_contact_count": len(fcra_rights["federal_contacts"]),
            "ai_rules": fcra_rights["ai_rules"],
        },
        "bureau_debt_collection_reference": {
            "bureau_count": len(bureau_reference["bureau_dispute_workflow"]),
            "experian_outcomes": [item["outcome"] for item in bureau_reference["experian_dispute_outcomes"]],
            "fdcpa_rule_count": len(bureau_reference["fdcpa_collection_rules"]),
            "ai_rules": bureau_reference["ai_rules"],
        },
        "growth_brief": growth,
        "operator_brief": operator,
    }
