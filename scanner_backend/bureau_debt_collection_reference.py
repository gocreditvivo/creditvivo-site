from __future__ import annotations

from typing import Dict, List


BUREAU_HELP_SOURCE_NOTES = {
    "equifax_dispute_url": "https://www.equifax.com/personal/credit-report-services/credit-dispute/",
    "equifax_mail_dispute_url": "https://www.equifax.com/personal/help/article-list/-/h/a/mail-in-credit-report-dispute/",
    "experian_dispute_url": "https://www.experian.com/blogs/ask-experian/credit-education/faqs/how-to-dispute-credit-report-information/",
    "experian_outcome_url": "https://www.experian.com/blogs/ask-experian/what-happens-when-you-submit-a-dispute-online/",
    "experian_average_score_url": "https://www.experian.com/blogs/ask-experian/what-is-the-average-credit-score-in-the-u-s/",
    "transunion_dispute_url": "https://www.transunion.com/credit-disputes/dispute-your-credit",
    "cfpb_dispute_url": "https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-an-error-on-my-credit-report-en-314/",
    "fdcpa_source": "Local FDCPA.pdf provided by Credit Vivo owner; Consumer Compliance Handbook FDCPA summary.",
    "compliance_note": (
        "Use bureau and FDCPA references for education, scanner workflow, and draft preparation only. "
        "Do not send disputes, debt-validation requests, complaints, or legal notices without customer approval and compliance review."
    ),
}


BUREAU_DISPUTE_WORKFLOW: List[Dict[str, object]] = [
    {
        "bureau": "Equifax",
        "customer_help_rule": "If an Equifax report item appears incomplete or inaccurate, the consumer can file a dispute.",
        "channels": ["online through Equifax/myEquifax", "mail with dispute form and documents", "phone/contact support where available"],
        "scanner_action": "Prepare Equifax-specific dispute packet with ID/address proof if mailing, account details, exact field, reason, and supporting documents.",
        "proof_examples": ["copy of credit report page", "account statement", "payment confirmation", "identity theft report if fraud", "proof of identity/address when required"],
    },
    {
        "bureau": "Experian",
        "customer_help_rule": "Experian disputes can update, delete, process, remain, or verify/update information depending on investigation results.",
        "channels": ["Experian Dispute Center", "mail instructions", "phone number shown on report or Experian support"],
        "scanner_action": "Parse Experian outcome wording and translate it into next steps for the customer.",
        "proof_examples": ["documents showing inaccurate field", "furnisher records", "payment proof", "identity theft/fraud documents", "prior report comparison"],
    },
    {
        "bureau": "TransUnion",
        "customer_help_rule": "TransUnion allows free disputes through the Service Center and says customers can add supporting documents and track status.",
        "channels": ["TransUnion Service Center online", "mail", "phone"],
        "scanner_action": "Prepare TransUnion-specific dispute packet and track whether the item is verified, changed, deleted, or still unresolved.",
        "proof_examples": ["creditor letter", "billing statement", "IRS letter", "canceled check or money order", "court or public-record proof"],
    },
]


EXPERIAN_DISPUTE_OUTCOMES: List[Dict[str, str]] = [
    {
        "outcome": "Added",
        "meaning": "The item was added to the credit report.",
        "scanner_next_step": "Review why the item appeared; verify ownership, dates, balance, and whether the added item belongs to the customer.",
    },
    {
        "outcome": "Updated",
        "meaning": "The information or item disputed was updated on the credit report.",
        "scanner_next_step": "Compare before/after values field by field. Updated does not automatically mean every disputed issue was fixed.",
    },
    {
        "outcome": "Verified and updated",
        "meaning": "The disputed information was verified as accurate, but separate unrelated information was updated.",
        "scanner_next_step": "Treat as partial/unsuccessful for the disputed field; consider furnisher dispute, MOV/process review, new evidence, or statement of dispute.",
    },
    {
        "outcome": "Deleted",
        "meaning": "The item was removed from the credit report.",
        "scanner_next_step": "Mark resolved for that bureau, monitor for reinsertions, and compare other bureaus for the same item.",
    },
    {
        "outcome": "Processed",
        "meaning": "The item was either updated or deleted.",
        "scanner_next_step": "Require before/after comparison before calling it resolved.",
    },
    {
        "outcome": "Remains",
        "meaning": "The company reporting the information verified that it was accurate, so it was not changed.",
        "scanner_next_step": "If customer still has proof, route to new-evidence dispute, direct furnisher dispute, 100-word statement, CFPB/state review, or attorney-review prep.",
    },
]


FDCPA_COLLECTION_RULES: List[Dict[str, str]] = [
    {
        "rule": "Consumer-purpose debt coverage",
        "plain_english": "The FDCPA applies to collection of consumer debts for personal, family, or household purposes, not business or agricultural debts.",
        "scanner_use": "Classify collection accounts as consumer, business, unknown, or needs review before FDCPA workflows.",
    },
    {
        "rule": "Covered debt collectors",
        "plain_english": "The FDCPA generally covers third-party debt collectors collecting debts for another party or using another name.",
        "scanner_use": "Distinguish original creditor, servicer, debt buyer, collection agency, and attorney collector where possible.",
    },
    {
        "rule": "Contact time and place limits",
        "plain_english": "Collectors generally may not contact consumers before 8 a.m. or after 9 p.m., at inconvenient places, or at work if they know the employer prohibits it.",
        "scanner_use": "Add intake questions for harassment/contact-time complaints tied to collection accounts.",
    },
    {
        "rule": "Attorney representation",
        "plain_english": "If the collector knows the consumer has an attorney for the debt, contacts should generally go through the attorney unless an exception applies.",
        "scanner_use": "Flag attorney-involved accounts for attorney/compliance review before Credit Vivo drafts customer communications.",
    },
    {
        "rule": "Cease communication request",
        "plain_english": "After a written refusal to pay or cease-contact request, the collector must stop most communications except limited allowed notices.",
        "scanner_use": "Track cease-contact letter date, proof of delivery, and any later collector contact evidence.",
    },
    {
        "rule": "Third-party contact limits",
        "plain_english": "Collectors are limited in who they may contact and what they may say when seeking location information.",
        "scanner_use": "Collect evidence if customer says family, employer, or third parties were contacted about the debt.",
    },
    {
        "rule": "Validation notice",
        "plain_english": "Collectors must provide debt amount, creditor name, 30-day dispute notice, verification rights, and original-creditor request rights.",
        "scanner_use": "Generate debt-validation checklist for collection accounts and identify missing validation-notice elements.",
    },
    {
        "rule": "Written dispute within 30 days",
        "plain_english": "If the consumer disputes in writing within the 30-day period, the collector must stop collection until verification or original-creditor information is mailed, as applicable.",
        "scanner_use": "Track validation/dispute deadline and pause/escalation evidence.",
    },
    {
        "rule": "Harassment or abuse",
        "plain_english": "Collectors may not harass, oppress, abuse, threaten violence, use obscene language, or repeatedly call to annoy.",
        "scanner_use": "Add harassment flags and route strong evidence to compliance/attorney review.",
    },
    {
        "rule": "False or misleading representations",
        "plain_english": "Collectors may not misrepresent the debt, legal status, attorney involvement, government affiliation, arrest risk, or report false credit information.",
        "scanner_use": "Flag inconsistent collection reporting, disputed-debt notation failures, fake legal threats, or false amount/status claims.",
    },
    {
        "rule": "Unfair practices",
        "plain_english": "Collectors may not collect unauthorized fees, misuse postdated checks, create communication charges by concealing purpose, or threaten improper repossession.",
        "scanner_use": "Review fee/charge complaints and repossession threats as collection-conduct issues separate from bureau reporting.",
    },
    {
        "rule": "Multiple debts",
        "plain_english": "When one collector handles several debts, payments must follow the consumer's instructions and cannot be applied to disputed debt.",
        "scanner_use": "Track payment allocation complaints when a customer has several collection accounts with the same collector.",
    },
    {
        "rule": "Legal venue",
        "plain_english": "Certain debt-collection lawsuits must be brought in the proper judicial district tied to the property, consumer residence, or contract location.",
        "scanner_use": "For lawsuit/judgment collection accounts, route venue issues to attorney review.",
    },
]


def build_bureau_debt_collection_reference() -> Dict[str, object]:
    return {
        "source_notes": BUREAU_HELP_SOURCE_NOTES,
        "bureau_dispute_workflow": BUREAU_DISPUTE_WORKFLOW,
        "experian_dispute_outcomes": EXPERIAN_DISPUTE_OUTCOMES,
        "fdcpa_collection_rules": FDCPA_COLLECTION_RULES,
        "ai_rules": [
            "Translate bureau outcomes into plain-English next steps before recommending another dispute round.",
            "If a result is verified/remains, require new evidence, furnisher review, statement of dispute, CFPB/state review, or attorney-review prep before escalating.",
            "Treat FDCPA issues as debt-collection conduct issues; separate them from FCRA credit-report accuracy issues.",
            "Do not accuse a collector or furnisher of legal violations in customer-facing output without compliance/attorney review.",
            "Keep all disputes, validation requests, complaints, and legal escalation approval-gated.",
        ],
    }
