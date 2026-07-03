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
class CreditDomainTopic:
    topic: str
    plain_english_meaning: str
    why_growth_ai_needs_it: str
    growth_use: List[str]
    caution: str


CREDIT_DOMAIN_TOPICS: List[CreditDomainTopic] = [
    CreditDomainTopic(
        topic="FCRA",
        plain_english_meaning="The Fair Credit Reporting Act is the main federal law about credit reporting, consumer report accuracy, disputes, and investigations.",
        why_growth_ai_needs_it="Credit Vivo's messaging and customer journey must respect consumer rights, dispute language, timing, and accuracy standards.",
        growth_use=[
            "create accurate educational content",
            "explain consumer rights in plain English",
            "route serious unresolved issues to escalation review",
            "avoid overpromising deletion or score increases",
        ],
        caution="Growth AI should not give legal advice or decide legal liability.",
    ),
    CreditDomainTopic(
        topic="FACTA",
        plain_english_meaning="The Fair and Accurate Credit Transactions Act amended the FCRA and includes rights around free reports, fraud alerts, identity theft, and accuracy.",
        why_growth_ai_needs_it="Many customers have identity, mixed-file, fraud, or wrong-person issues that need careful wording and routing.",
        growth_use=[
            "identify identity-theft and mixed-file content opportunities",
            "explain fraud alert and report review concepts",
            "support scanner triage for wrong personal information",
        ],
        caution="Identity-theft and fraud workflows need careful approval and secure handling of personal documents.",
    ),
    CreditDomainTopic(
        topic="Metro 2",
        plain_english_meaning="Metro 2 is the credit reporting data format furnishers use to report account information to the bureaus.",
        why_growth_ai_needs_it="Credit Vivo's scanner and ads can explain that AI looks for possible inconsistencies in dates, balances, statuses, and account reporting.",
        growth_use=[
            "position Credit Vivo as forensic credit report analysis",
            "create content about inconsistent reporting",
            "support scanner feature messaging",
            "explain bureau-to-bureau mismatches in simple terms",
        ],
        caution="Do not claim every Metro 2 inconsistency is illegal or removable.",
    ),
    CreditDomainTopic(
        topic="Credit bureaus",
        plain_english_meaning="Equifax, Experian, and TransUnion collect and sell credit report information from furnishers and public record sources.",
        why_growth_ai_needs_it="Customers often do not understand why the three reports differ.",
        growth_use=[
            "create three-bureau comparison content",
            "explain why one bureau may show an item differently",
            "route bureau-specific disputes",
        ],
        caution="Do not imply partnership with any bureau unless there is a signed agreement.",
    ),
    CreditDomainTopic(
        topic="Furnishers",
        plain_english_meaning="Furnishers are companies that send account information to credit bureaus, like banks, lenders, collectors, and servicers.",
        why_growth_ai_needs_it="Many disputes should consider whether the bureau, furnisher, or both are involved.",
        growth_use=[
            "explain bureau vs furnisher disputes",
            "create content around collections and charge-offs",
            "support escalation path messaging",
        ],
        caution="Do not send furnisher demands without approval and tracking.",
    ),
    CreditDomainTopic(
        topic="Credit report dispute process",
        plain_english_meaning="Consumers can dispute inaccurate or incomplete information with credit bureaus and furnishers, and the company must investigate under applicable rules.",
        why_growth_ai_needs_it="Credit Vivo needs to explain what happens after a finding and what customers can do next.",
        growth_use=[
            "build plain-English customer education",
            "write scanner next-step explanations",
            "create dispute workflow content",
            "identify upsell moments after findings",
        ],
        caution="Credit Vivo should keep customer approval before anything is sent or escalated.",
    ),
    CreditDomainTopic(
        topic="FCRA federal and state rights routing",
        plain_english_meaning="Federal agencies enforce different parts of the FCRA, and states may enforce the FCRA or provide extra consumer reporting rights.",
        why_growth_ai_needs_it="Credit Vivo content and escalation workflows should explain that customers may contact CFPB, FTC, another federal regulator, a state consumer protection agency, or a state Attorney General depending on the issue.",
        growth_use=[
            "write accurate education about federal and state dispute rights",
            "route unresolved scanner findings to the right escalation review",
            "avoid making state-law promises in ads or customer messages",
            "prepare owner/compliance review notes before state or federal complaints",
        ],
        caution="Growth AI should not decide legal rights, file complaints automatically, or claim a state-law outcome without qualified review.",
    ),
    CreditDomainTopic(
        topic="Debt collection reporting",
        plain_english_meaning="Collection accounts may appear on reports when a debt is placed or sold to a collector.",
        why_growth_ai_needs_it="Collections are a high-intent customer problem and a strong campaign wedge.",
        growth_use=[
            "create collection-not-mine campaigns",
            "explain unfamiliar collections",
            "support validation/dispute workflow content",
        ],
        caution="Do not tell customers to dispute accurate debt just to remove it.",
    ),
    CreditDomainTopic(
        topic="FDCPA debt collection conduct",
        plain_english_meaning="The FDCPA is a federal law that limits abusive, deceptive, or unfair third-party debt collection practices.",
        why_growth_ai_needs_it="Many collection customers need help separating credit-report accuracy issues from collector-contact, validation, harassment, or legal-threat issues.",
        growth_use=[
            "create education around debt validation and collector conduct",
            "route collection-account users to scanner and dispute tracking",
            "flag when attorney/compliance review is needed",
        ],
        caution="Do not accuse a collector of violating the FDCPA in ads or customer output without qualified review.",
    ),
    CreditDomainTopic(
        topic="Charge-offs and late payments",
        plain_english_meaning="Charge-offs and late payments are negative account statuses that may affect credit and may remain if accurate.",
        why_growth_ai_needs_it="These are common reasons people seek help and need clear expectations.",
        growth_use=[
            "write realistic education content",
            "explain what AI can review",
            "route users to scanner findings and next-step planning",
        ],
        caution="Do not guarantee removal of accurate negative information.",
    ),
    CreditDomainTopic(
        topic="Soft pull vs hard pull",
        plain_english_meaning="A soft pull does not affect a credit score; a hard pull can happen when applying for credit.",
        why_growth_ai_needs_it="No-hard-pull is a major trust point for the free Credit Check-In.",
        growth_use=[
            "write ads with no-hard-pull positioning",
            "reduce customer fear about starting",
            "explain the difference before scanner start",
        ],
        caution="Only use no-hard-pull language where the actual report-access flow supports it.",
    ),
    CreditDomainTopic(
        topic="Credit repair organization rules",
        plain_english_meaning="Credit repair laws regulate how companies advertise, contract, charge, and promise services related to improving credit.",
        why_growth_ai_needs_it="Growth AI must avoid risky promises, misleading claims, and payment flows that could create launch risk.",
        growth_use=[
            "screen ad copy",
            "flag risky pricing or guarantee language",
            "support content review before launch",
        ],
        caution="State-by-state rules and contracts require legal/compliance review.",
    ),
]


def topic_to_dict(topic: CreditDomainTopic) -> Dict[str, object]:
    return topic.__dict__


def build_credit_domain_expertise_brief() -> Dict[str, object]:
    fcra_rights = build_fcra_rights_reference()
    bureau_reference = build_bureau_debt_collection_reference()
    return {
        "ok": True,
        "service": "credit-vivo-growth-credit-domain-expertise",
        "plain_english_summary": "Growth AI understands the credit repair domain enough to create better education, campaigns, scanner positioning, dispute routing, and customer explanations. Legal decisions still need qualified review.",
        "topics": [topic_to_dict(topic) for topic in CREDIT_DOMAIN_TOPICS],
        "fcra_rights_reference": {
            "plain_english_note": fcra_rights["source_notes"]["plain_english_note"],
            "federal_consumer_rights_count": len(fcra_rights["federal_consumer_rights"]),
            "maryland_rights_summary": fcra_rights["maryland_consumer_rights"]["plain_english_summary"],
            "state_notice_states": [item["state"] for item in fcra_rights["state_notice_links"]],
            "federal_contact_categories": [item["category"] for item in fcra_rights["federal_contacts"]],
        },
        "bureau_debt_collection_reference": {
            "experian_outcomes": [item["outcome"] for item in bureau_reference["experian_dispute_outcomes"]],
            "fdcpa_rule_count": len(bureau_reference["fdcpa_collection_rules"]),
        },
        "how_growth_ai_uses_this": [
            "turn technical credit terms into simple customer-facing language",
            "write more accurate ads and landing pages",
            "map scanner findings to next-step options",
            "identify high-intent customer segments",
            "flag copy that overpromises or confuses customers",
            "route bureau, furnisher, CFPB/state, and attorney-review scenarios",
        ],
        "example_customer_angles": [
            "Collection account look unfamiliar?",
            "Before your next auto loan, check possible report issues.",
            "Mortgage-ready starts with report clarity.",
            "Why do my three credit reports look different?",
            "What happens after a bureau says verified?",
        ],
    }
