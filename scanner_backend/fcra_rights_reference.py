from __future__ import annotations

from typing import Dict, List


FCRA_RIGHTS_SOURCE_NOTES = {
    "primary_reference": "CFPB Regulation V Appendix K - Summary of Consumer Rights",
    "primary_url": "https://www.consumerfinance.gov/rules-policy/regulations/1022/K",
    "agency_contact_update_reference": "CFPB 2023 Agency Contact Information technical corrections",
    "agency_contact_update_url": "https://www.federalregister.gov/documents/2023/03/20/2023-05216/agency-contact-information",
    "plain_english_note": (
        "States may enforce the FCRA, and many states have their own consumer reporting laws. "
        "Customers may have more rights under state law and should contact their state or local "
        "consumer protection agency or state Attorney General for state-law questions."
    ),
    "compliance_note": (
        "Use this as an internal routing/reference checklist. It is not legal advice. "
        "Before production disclosure use, confirm the current CFPB model form and agency addresses."
    ),
}


FCRA_FEDERAL_CONTACTS: List[Dict[str, object]] = [
    {
        "category": "Banks, savings associations, and credit unions with total assets over $10 billion and affiliates",
        "contacts": [
            {
                "agency": "Bureau of Consumer Financial Protection",
                "address": "1700 G Street NW, Washington, DC 20552",
            },
            {
                "agency": "Federal Trade Commission Consumer Response Center",
                "address": "600 Pennsylvania Avenue NW, Washington, DC 20580",
                "use_when": "Affiliate is not a bank, savings association, or credit union; list in addition to the Bureau.",
            },
        ],
    },
    {
        "category": "National banks, federal savings associations, and federal branches/agencies of foreign banks",
        "contacts": [
            {
                "agency": "Office of the Comptroller of the Currency - Customer Assistance Group",
                "address": "P.O. Box 53570, Houston, TX 77052",
            }
        ],
    },
    {
        "category": "State member banks, foreign bank branches/agencies, and commercial lending companies owned or controlled by foreign banks",
        "contacts": [
            {
                "agency": "Federal Reserve Consumer Help Center",
                "address": "PO Box 1200, Minneapolis, MN 55480",
            }
        ],
    },
    {
        "category": "Nonmember insured banks, insured state branches of foreign banks, and insured state savings associations",
        "contacts": [
            {
                "agency": "FDIC Division of Depositor and Consumer Protection - National Center for Consumer and Depositor Assistance",
                "address": "1100 Walnut Street, Box #11, Kansas City, MO 64106",
            }
        ],
    },
    {
        "category": "Federal credit unions",
        "contacts": [
            {
                "agency": "National Credit Union Administration - Office of Consumer Financial Protection",
                "address": "1775 Duke Street, Alexandria, VA 22314",
            }
        ],
    },
    {
        "category": "Air carriers",
        "contacts": [
            {
                "agency": "Department of Transportation - Assistant General Counsel for Office of Aviation Consumer Protection",
                "address": "1200 New Jersey Avenue SE, Washington, DC 20590",
            }
        ],
    },
    {
        "category": "Creditors subject to the Surface Transportation Board",
        "contacts": [
            {
                "agency": "Surface Transportation Board - Office of Public Assistance, Governmental Affairs, and Compliance",
                "address": "395 E Street SW, Washington, DC 20423",
            }
        ],
    },
    {
        "category": "Creditors subject to Packers and Stockyards Act",
        "contacts": [
            {
                "agency": "Nearest Packers and Stockyards Division Regional Office",
                "address": "Regional office varies by location",
            }
        ],
    },
    {
        "category": "Small Business Investment Companies",
        "contacts": [
            {
                "agency": "United States Small Business Administration - Associate Administrator, Office of Capital Access",
                "address": "409 Third Street SW, Suite 8200, Washington, DC 20416",
            }
        ],
    },
    {
        "category": "Brokers and dealers",
        "contacts": [
            {
                "agency": "Securities and Exchange Commission",
                "address": "100 F Street NE, Washington, DC 20549",
            }
        ],
    },
    {
        "category": "Federal Land Banks, Federal Land Bank Associations, Federal Intermediate Credit Banks, and Production Credit Associations",
        "contacts": [
            {
                "agency": "Farm Credit Administration",
                "address": "1501 Farm Credit Drive, McLean, VA 22102-5090",
            }
        ],
    },
    {
        "category": "Retailers, finance companies, and all other creditors not listed above",
        "contacts": [
            {
                "agency": "Federal Trade Commission Consumer Response Center - FCRA",
                "address": "600 Pennsylvania Avenue NW, Washington, DC 20580",
                "phone": "(877) 382-4357",
            }
        ],
    },
]


FCRA_FEDERAL_CONSUMER_RIGHTS: List[Dict[str, str]] = [
    {
        "right": "Adverse action notice",
        "plain_english": "A consumer must be told when information in a consumer report is used against them, such as a denial or worse terms.",
        "scanner_use": "Ask for or track adverse-action notices after auto, mortgage, apartment, insurance, employment, or credit denials.",
    },
    {
        "right": "File disclosure",
        "plain_english": "A consumer has the right to know what is in their consumer reporting file after proper identification.",
        "scanner_use": "Route the customer to obtain the full report or specialty report when scanner data is incomplete.",
    },
    {
        "right": "Free report situations",
        "plain_english": "A consumer may qualify for a free file disclosure after adverse action, fraud alert/identity theft, fraud-related inaccuracy, public assistance, or unemployment with expected job search.",
        "scanner_use": "Use in intake questions and customer education before asking the customer to pay for duplicate data.",
    },
    {
        "right": "Credit score disclosure",
        "plain_english": "A consumer may ask for a credit score from reporting agencies that create or distribute scores, and may receive score information in certain mortgage transactions.",
        "scanner_use": "Explain that score data and report data are related but not the same thing.",
    },
    {
        "right": "Dispute incomplete or inaccurate information",
        "plain_english": "A consumer can dispute information that appears incomplete or inaccurate, and the consumer reporting agency must investigate unless the dispute is frivolous.",
        "scanner_use": "Convert findings into specific dispute reasons, fields, evidence, and requested corrections.",
    },
    {
        "right": "Correction or deletion",
        "plain_english": "Inaccurate, incomplete, or unverifiable information must be corrected or deleted, usually within 30 days, though verified accurate information may remain.",
        "scanner_use": "Set customer expectations: correction/deletion is not guaranteed if the information is verified as accurate.",
    },
    {
        "right": "Outdated negative information",
        "plain_english": "Most negative information cannot be reported after seven years, and bankruptcies generally cannot be reported after ten years.",
        "scanner_use": "Flag possible obsolete reporting and DOFD/removal-date issues.",
    },
    {
        "right": "Limited access",
        "plain_english": "Consumer reports may only be provided to parties with a permissible purpose.",
        "scanner_use": "Flag suspicious inquiry/access questions for customer review.",
    },
    {
        "right": "Employment consent",
        "plain_english": "A report generally cannot be provided to an employer or potential employer without written consent.",
        "scanner_use": "Route employment-screening issues separately from ordinary credit disputes.",
    },
    {
        "right": "Prescreened offer opt-out",
        "plain_english": "Consumers may limit prescreened credit and insurance offers by opting out through the nationwide bureaus.",
        "scanner_use": "Offer as education, not as a dispute or repair action.",
    },
    {
        "right": "Security freeze",
        "plain_english": "A consumer can place a security freeze to restrict release of their credit report without express authorization.",
        "scanner_use": "Recommend as an education topic for identity theft, fraud, or unauthorized-account concerns.",
    },
    {
        "right": "Fraud alert",
        "plain_english": "A consumer can place an initial fraud alert, and identity-theft victims may qualify for an extended fraud alert.",
        "scanner_use": "Route identity theft and not-mine accounts to fraud-alert and identity-theft workflows.",
    },
    {
        "right": "Potential damages",
        "plain_english": "If a consumer reporting agency, user, or furnisher violates the FCRA, a consumer may be able to seek damages in state or federal court.",
        "scanner_use": "Escalate serious repeated failures, damages, denials, mixed files, or identity theft to attorney-review prep.",
    },
    {
        "right": "Identity theft and active duty rights",
        "plain_english": "Identity theft victims and active duty military personnel have additional rights.",
        "scanner_use": "Ask intake questions that identify these special workflows and protect sensitive documents.",
    },
]


MARYLAND_CONSUMER_REPORTING_RIGHTS: Dict[str, object] = {
    "state": "Maryland",
    "legal_reference": "Annotated Code of Maryland, Commercial Law Article, Title 14, Subtitle 12",
    "plain_english_summary": (
        "Maryland consumers have state consumer reporting rights in addition to federal FCRA rights, "
        "including file access, dispute, correction, statement, and complaint rights."
    ),
    "consumer_rights": [
        "Request in writing that a consumer reporting agency restrict sale or transfer of file information to mail-service, marketing, or similar organizations.",
        "Receive an exact copy of the credit file with an explanation of codes or trade language after request and proper identification.",
        "Receive file disclosure in person, by telephone after written request, or in writing after proper identification.",
        "Be accompanied by one chosen person during disclosure if proper permission and identification are provided.",
        "Dispute completeness or accuracy of credit-file information.",
        "Receive reinvestigation within 30 days for a written dispute unless the dispute is frivolous or irrelevant.",
        "Have inaccurate or unverifiable information deleted and receive written notice of correction.",
        "Receive written notice if disputed information is verified as accurate.",
        "Pay no charge for handling disputed information or corrected reports from that handling.",
        "Within 60 days after notice of correction or findings, request names, addresses, and telephone numbers of creditors contacted during reinvestigation.",
        "File a brief statement of dispute of not more than 100 words if reinvestigation does not resolve the dispute.",
        "Request notice of deleted information or dispute statement to prior recipients: past two years for employment purposes or past one year for other purposes.",
        "Request one free copy of the file within a 12-month period, with later copies subject to stated fee limits.",
    ],
    "complaint_contact": {
        "agency": "Maryland Office of Financial Regulation - Complaint Unit",
        "address": "500 N. Calvert Street, Suite 402, Baltimore, MD 21202",
        "phone": "(410) 230-6077",
    },
    "scanner_use": [
        "For Maryland residents, show Maryland rights alongside federal FCRA rights.",
        "Track written dispute date, 30-day reinvestigation deadline, response, correction/deletion notice, and creditor-contact request window.",
        "Offer a 100-word statement-of-dispute workflow when reinvestigation does not resolve the item.",
        "Route unresolved Maryland issues to state complaint/attorney-review prep only after customer approval.",
    ],
}


FCRA_STATE_NOTICE_LINKS: List[Dict[str, str]] = [
    {"state": "California Fraud State Notice", "url": "https://www.experian.com/blogs/ask-experian/california-fraud-state-notice-of-rights/"},
    {"state": "California", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/california/"},
    {"state": "Connecticut", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/connecticut/"},
    {"state": "Delaware", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/delaware/"},
    {"state": "District of Columbia", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/district-of-columbia/"},
    {"state": "Georgia", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/georgia/"},
    {"state": "Massachusetts", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/massachusetts/"},
    {"state": "Missouri", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/missouri/"},
    {"state": "Montana", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/montana/"},
    {"state": "New Hampshire", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/new-hampshire/"},
    {"state": "New Jersey", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/new-jersey/"},
    {"state": "North Carolina", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/north-carolina/"},
    {"state": "North Dakota", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/north-dakota/"},
    {"state": "Rhode Island", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/rhode-island/"},
    {"state": "Tennessee", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/tennessee/"},
    {"state": "Texas", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/texas/"},
    {"state": "Vermont", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/vermont/"},
    {"state": "Virginia", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/virginia/"},
    {"state": "Washington", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/washington/"},
    {"state": "West Virginia", "url": "https://www.experian.com/blogs/ask-experian/credit-education/report-basics/fair-credit-reporting-act-fcra/west-virginia/"},
]


def build_fcra_rights_reference() -> Dict[str, object]:
    return {
        "source_notes": FCRA_RIGHTS_SOURCE_NOTES,
        "federal_consumer_rights": FCRA_FEDERAL_CONSUMER_RIGHTS,
        "maryland_consumer_rights": MARYLAND_CONSUMER_REPORTING_RIGHTS,
        "federal_contacts": FCRA_FEDERAL_CONTACTS,
        "state_notice_links": FCRA_STATE_NOTICE_LINKS,
        "ai_rules": [
            "Always tell customers state rights may exist in addition to federal FCRA rights.",
            "Route unresolved serious issues to CFPB/state/attorney-review workflows only after customer approval.",
            "Use federal regulator contacts as a routing guide, not as legal advice.",
            "State notice links are references; confirm current state-law requirements before production disclosure use.",
            "For Maryland consumers, track state dispute rights, the 30-day reinvestigation expectation, and state complaint routing.",
        ],
    }
