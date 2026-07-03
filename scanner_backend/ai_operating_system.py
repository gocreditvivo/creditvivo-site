from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

try:
    from .bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from .fcra_rights_reference import build_fcra_rights_reference
except ImportError:
    from bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from fcra_rights_reference import build_fcra_rights_reference


@dataclass(frozen=True)
class AiStandard:
    principle: str
    plain_english_rule: str
    required_behavior: str


@dataclass(frozen=True)
class AiRoleCapability:
    role_id: str
    role_name: str
    mission: str
    tools_needed: List[str]
    can_do: List[str]
    cannot_do_without_approval: List[str]
    data_needed_next: List[str]


AI_OPERATING_STANDARDS: List[AiStandard] = [
    AiStandard(
        principle="Mission first",
        plain_english_rule="Each AI must know the business goal before giving advice.",
        required_behavior="Tie every recommendation to growth, customer progress, compliance, retention, or system health.",
    ),
    AiStandard(
        principle="Facts before guesses",
        plain_english_rule="Use numbers, logs, and customer events before making claims.",
        required_behavior="Show the signal used, the confidence level, and the missing data when data is incomplete.",
    ),
    AiStandard(
        principle="Founder control",
        plain_english_rule="The AI can prepare work, but the owner approves sensitive actions.",
        required_behavior="Require approval before customer messages, legal escalation, refunds, pricing changes, paid ads, or dispute sends.",
    ),
    AiStandard(
        principle="Compliance guardrails",
        plain_english_rule="Do not overpromise, pressure, or act like a law firm.",
        required_behavior="Flag guarantee language, missing consent, unsupported claims, attorney/legal wording, and FCRA/state-rights routing that needs review.",
    ),
    AiStandard(
        principle="Private data protection",
        plain_english_rule="Customer credit data is sensitive and must be protected.",
        required_behavior="Avoid exposing raw reports, secrets, payment data, or personal details in logs, GitHub, public files, or outreach lists.",
    ),
    AiStandard(
        principle="Verify after action",
        plain_english_rule="After the AI changes something, it must check that it worked.",
        required_behavior="Run the strongest practical test, route check, API check, or deployment check before reporting success.",
    ),
    AiStandard(
        principle="Human-friendly output",
        plain_english_rule="The founder should not need technical training to understand the brief.",
        required_behavior="Write owner alerts in plain English with next action, business impact, and approval needed.",
    ),
]


AI_ROLE_CAPABILITIES: List[AiRoleCapability] = [
    AiRoleCapability(
        role_id="growth_ai",
        role_name="Growth AI",
        mission="Bring qualified, opt-in customers into Credit Vivo and improve revenue math.",
        tools_needed=["analytics", "lead capture", "campaign tracking", "referral tracking", "payment events"],
        can_do=[
            "score leads",
            "recommend campaigns",
            "draft partner outreach",
            "track funnel bottlenecks",
            "calculate path to revenue targets",
        ],
        cannot_do_without_approval=[
            "send bulk emails",
            "launch paid ads",
            "scrape private consumer contacts",
            "change public promises",
        ],
        data_needed_next=["traffic source", "join clicks", "scan starts", "paid upgrades", "cancellations"],
    ),
    AiRoleCapability(
        role_id="scanner_ai",
        role_name="Scanner AI",
        mission="Review credit report data and explain possible issues in plain English.",
        tools_needed=["credit report parser", "finding classifier", "customer consent log", "secure storage"],
        can_do=[
            "parse reports",
            "flag possible mismatches",
            "rank possible errors",
            "create customer-friendly summaries",
            "translate bureau dispute outcomes into next-step options",
        ],
        cannot_do_without_approval=[
            "send disputes",
            "delete customer data outside retention policy",
            "make legal conclusions",
            "promise score changes",
        ],
        data_needed_next=["raw report source", "bureau", "tradelines", "finding history", "customer approvals"],
    ),
    AiRoleCapability(
        role_id="dispute_ai",
        role_name="Dispute AI",
        mission="Prepare organized dispute scenarios, draft letters, evidence packets, and tracking steps.",
        tools_needed=["letter templates", "dispute history", "mail provider", "tracking log", "response parser"],
        can_do=[
            "draft letters",
            "summarize evidence",
            "track dispute rounds",
            "recommend next escalation path",
            "prepare FCRA federal regulator and state-rights routing notes",
            "prepare FDCPA debt-validation and collector-conduct review checklists",
        ],
        cannot_do_without_approval=[
            "send bureau letters",
            "send furnisher letters",
            "submit CFPB or state complaints",
            "represent Credit Vivo as a law firm",
        ],
        data_needed_next=["approved findings", "letter status", "mail tracking", "bureau responses", "furnisher responses"],
    ),
    AiRoleCapability(
        role_id="retention_ai",
        role_name="Retention AI",
        mission="Keep customers informed, moving, and less likely to cancel.",
        tools_needed=["customer activity", "support tickets", "payment events", "scan progress", "message drafts"],
        can_do=[
            "flag stuck customers",
            "draft progress updates",
            "recommend plan fit",
            "identify cancellation risk",
        ],
        cannot_do_without_approval=[
            "send customer messages",
            "offer refunds",
            "pressure upgrades",
            "make personalized financial product recommendations without policy review",
        ],
        data_needed_next=["last login", "stuck step", "support history", "payment status", "customer goal"],
    ),
    AiRoleCapability(
        role_id="operator_ai",
        role_name="Operator AI",
        mission="Watch the company systems and tell the founder what needs attention.",
        tools_needed=["website monitor", "Render health check", "Vercel deploy status", "error logs", "task tracker"],
        can_do=[
            "detect outages",
            "prioritize issues",
            "create internal tasks",
            "prepare daily owner brief",
        ],
        cannot_do_without_approval=[
            "change production settings",
            "access secrets without need",
            "disable compliance checks",
            "modify pricing or plans",
        ],
        data_needed_next=["deploy status", "health endpoint", "error logs", "support queue", "payment failures"],
    ),
    AiRoleCapability(
        role_id="compliance_guard_ai",
        role_name="Compliance Guard AI",
        mission="Protect Credit Vivo from risky claims, missing approvals, and sensitive data mistakes.",
        tools_needed=["content scanner", "approval log", "consent records", "disclosure checklist", "state launch rules"],
        can_do=[
            "flag risky wording",
            "block unsupported automation",
            "check approval requirements",
            "prepare attorney/compliance review notes",
            "check FCRA regulator/state-rights references before escalation workflows",
        ],
        cannot_do_without_approval=[
            "approve legal disclosures",
            "give legal advice",
            "override attorney review",
            "send regulated communications",
        ],
        data_needed_next=["current disclosures", "customer consents", "state availability", "letter approval records"],
    ),
]


def standard_to_dict(standard: AiStandard) -> Dict[str, str]:
    return {
        "principle": standard.principle,
        "plain_english_rule": standard.plain_english_rule,
        "required_behavior": standard.required_behavior,
    }


def role_capability_to_dict(role: AiRoleCapability) -> Dict[str, object]:
    return {
        "role_id": role.role_id,
        "role_name": role.role_name,
        "mission": role.mission,
        "tools_needed": role.tools_needed,
        "can_do": role.can_do,
        "cannot_do_without_approval": role.cannot_do_without_approval,
        "data_needed_next": role.data_needed_next,
    }


def build_ai_operating_system_brief() -> Dict[str, object]:
    fcra_rights = build_fcra_rights_reference()
    bureau_reference = build_bureau_debt_collection_reference()
    return {
        "ok": True,
        "service": "credit-vivo-ai-operating-system",
        "standard": "mission_oriented_verify_after_action_approval_gated",
        "plain_english_summary": (
            "Credit Vivo AIs should act like specialized departments: they monitor, analyze, draft, "
            "recommend, and prepare work. Sensitive customer, legal, payment, dispute, and public actions "
            "stay approval-gated."
        ),
        "standards": [standard_to_dict(standard) for standard in AI_OPERATING_STANDARDS],
        "roles": [role_capability_to_dict(role) for role in AI_ROLE_CAPABILITIES],
        "fcra_rights_reference": {
            "source_notes": fcra_rights["source_notes"],
            "ai_rules": fcra_rights["ai_rules"],
            "federal_consumer_rights_count": len(fcra_rights["federal_consumer_rights"]),
            "maryland_rights_summary": fcra_rights["maryland_consumer_rights"]["plain_english_summary"],
            "federal_contact_categories": [item["category"] for item in fcra_rights["federal_contacts"]],
            "federal_agencies": [
                contact["agency"]
                for item in fcra_rights["federal_contacts"]
                for contact in item["contacts"]
            ],
            "state_notice_states": [item["state"] for item in fcra_rights["state_notice_links"]],
        },
        "bureau_debt_collection_reference": {
            "bureau_count": len(bureau_reference["bureau_dispute_workflow"]),
            "experian_outcomes": [item["outcome"] for item in bureau_reference["experian_dispute_outcomes"]],
            "fdcpa_rule_count": len(bureau_reference["fdcpa_collection_rules"]),
            "ai_rules": bureau_reference["ai_rules"],
        },
        "highest_priority_next_connections": [
            "real analytics events",
            "secure customer profile database",
            "scanner completion events",
            "payment and cancellation events",
            "support ticket events",
            "mail/dispute tracking events",
            "Render and Vercel health/deploy status",
        ],
    }
