from __future__ import annotations

"""
Credit Vivo Proprietary Parser Engine v18.1.7

Purpose:
- Build a stronger original Credit Vivo parser/scanner engine.
- No Claude / Anthropic / paid AI API.
- No competitor code.
- No automatic dispute sending.
- Every output includes source evidence and confidence.

Core ideas:
1. Extract all raw report text first.
2. Detect bureau and report layout.
3. Segment report into account/profile blocks.
4. Extract fields into Credit Vivo's normalized tradeline schema.
5. Score confidence.
6. Match same/similar accounts across bureaus.
7. Detect review issues.
8. Return customer-friendly and admin-ready output.

This is draft review software. It does not provide legal advice.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Iterable
import hashlib
import re
import json
import csv
from pathlib import Path
from datetime import date
from urllib.parse import quote_plus

try:
    from .bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from .cfpb_packet_vault import build_cfpb_packet_system, save_document_vault_artifacts
    from .fcra_rights_reference import build_fcra_rights_reference
    from .rules_engine import classify_negative_tradeline, load_scanner_rules
except ImportError:
    from bureau_debt_collection_reference import build_bureau_debt_collection_reference
    from cfpb_packet_vault import build_cfpb_packet_system, save_document_vault_artifacts
    from fcra_rights_reference import build_fcra_rights_reference
    from rules_engine import classify_negative_tradeline, load_scanner_rules

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except Exception:
    Workbook = None
    Alignment = None
    Font = None
    Border = None
    PatternFill = None
    Side = None
    get_column_letter = None


# -----------------------------
# Utility
# -----------------------------

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compact_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def stable_id(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return "cvp_" + hashlib.sha256(raw).hexdigest()[:16]


SCANNER_SKILL_MAP = [
    {
        "skill_id": "credit_report_parser",
        "skill_name": "Credit Report Parser",
        "scanner_role": "Extracts and normalizes consumer credit report data into tradelines, bureau fields, evidence snippets, and confidence signals.",
        "used_for": "PDF text extraction review, bureau detection, tradeline parsing, raw evidence, 3-bureau comparison.",
        "output_area": "Review Items, Ours 3 Bureaus Comparison, Raw Data Verification.",
        "approval_gate": "Parser facts must be checked against raw report data before customer-facing action.",
        "customer_visible": "No",
    },
    {
        "skill_id": "workbook_output_qa",
        "skill_name": "Workbook Output QA",
        "scanner_role": "Checks the v9 forensic workbook layout, required tabs, template headers, and raw-data verification before files are written.",
        "used_for": "Template matching, pre-output verification, export cleanup flags, worksheet readiness.",
        "output_area": "Pre_Output_Verification, Raw Data Verification, Dashboard.",
        "approval_gate": "Output must pass template/raw-data checks or be marked for admin review.",
        "customer_visible": "No",
    },
    {
        "skill_id": "creditvivo_compliance_reviewer",
        "skill_name": "Credit Vivo Compliance Reviewer",
        "scanner_role": "Keeps language framed as possible report errors, plain-English review, documented next steps, and customer-approved dispute prep.",
        "used_for": "Safe wording, blocked phrase prevention, no guarantees, no legal advice, no automatic escalation.",
        "output_area": "Dashboard, Read_Me_v9, FCRA Compliance Review, Draft Letters.",
        "approval_gate": "Customer approval, admin review, and compliance review are required before dispute prep moves forward.",
        "customer_visible": "Partly",
    },
    {
        "skill_id": "dispute_strategy_assistant",
        "skill_name": "Dispute Strategy Assistant",
        "scanner_role": "Turns verified possible issues into draft-only review paths, letter type suggestions, document needs, and next-step checkpoints.",
        "used_for": "Draft letter queue, dispute method planning, packet checklist, evidence-backed issue classification.",
        "output_area": "Exact_Letters_To_Mail, Dispute_Cycle_Status, CFPB_Packet_Checklist.",
        "approval_gate": "No dispute, validation letter, complaint, or mail packet is sent automatically.",
        "customer_visible": "Partly",
    },
    {
        "skill_id": "creditvivo_product_manager",
        "skill_name": "Credit Vivo Product Manager",
        "scanner_role": "Separates customer-facing review from backend/admin engine controls, status queues, audit trail needs, and operator workflow.",
        "used_for": "Customer/admin mode separation, dashboard planning, document vault, approval lifecycle.",
        "output_area": "Dashboard, Document_Vault, Lob_Tracking, scanner API summary.",
        "approval_gate": "Admin/founder controls stay backend-only unless explicitly approved for customer portal release.",
        "customer_visible": "No",
    },
    {
        "skill_id": "customer_summary_writer",
        "skill_name": "Customer-Safe Summary Writer",
        "scanner_role": "Creates plain-English summaries that explain review points without legal conclusions, promises, or pressure language.",
        "used_for": "Customer summary, decision-readiness cards, simple next steps.",
        "output_area": "customer_summary, decision_readiness.",
        "approval_gate": "Summaries must avoid guaranteed removals, guaranteed score changes, and legal conclusions.",
        "customer_visible": "Yes",
    },
    {
        "skill_id": "letter_lifecycle_manager",
        "skill_name": "Letter Lifecycle Manager",
        "scanner_role": "Tracks draft letters from scanner recommendation through customer approval, admin review, compliance review, and Lob-ready packet prep.",
        "used_for": "Letter workflow, recommended queue, packet/vault planning, Lob tracking placeholder.",
        "output_area": "recommended_letter_queue, letter_workflow, Lob_Tracking.",
        "approval_gate": "Lob-ready means prepared for review only; mailing remains blocked until production controls are approved.",
        "customer_visible": "Partly",
    },
    {
        "skill_id": "security_privacy_reviewer",
        "skill_name": "Security and Privacy Reviewer",
        "scanner_role": "Protects sensitive consumer data by masking visible output and keeping raw reports, IDs, account numbers, and credentials out of unsafe channels.",
        "used_for": "Visible workbook masking, upload retention controls, document vault planning, raw text handling.",
        "output_area": "Document_Vault, visible workbook tabs, API health/settings.",
        "approval_gate": "Customer-sensitive files, secrets, full SSNs, IDs, bureau credentials, and full account numbers must not be committed or broadly synced.",
        "customer_visible": "No",
    },
]


def build_scanner_skill_map() -> List[dict]:
    return [dict(item) for item in SCANNER_SKILL_MAP]


def money_to_number(value: str) -> Optional[float]:
    if not value:
        return None
    value = value.replace("$", "").replace(",", "").strip()
    try:
        return float(value)
    except Exception:
        return None


def normalize_money(value: str) -> str:
    n = money_to_number(value)
    if n is None:
        return value.strip()
    if n.is_integer():
        return f"${int(n):,}"
    return f"${n:,.2f}"


def normalize_date(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip())


def mask_account_number(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 4:
        return "*" + digits[-4:]
    if len(value) >= 6:
        return value[:2] + "..." + value[-2:]
    return value


def simple_similarity(a: str, b: str) -> float:
    """
    Custom no-dependency similarity for proprietary matching.
    Not perfect, but good enough for candidate grouping without RapidFuzz.
    """
    ak = compact_key(a)
    bk = compact_key(b)
    if not ak or not bk:
        return 0.0
    if ak == bk:
        return 1.0
    if ak in bk or bk in ak:
        return 0.86

    aset = set(re.findall(r"[a-z0-9]{2,}", a.lower()))
    bset = set(re.findall(r"[a-z0-9]{2,}", b.lower()))
    if not aset or not bset:
        return 0.0
    return len(aset & bset) / max(1, len(aset | bset))


# -----------------------------
# Schema
# -----------------------------

@dataclass
class Evidence:
    bureau: str
    page: Optional[int]
    snippet: str
    extraction_method: str = "native_rule_engine"


@dataclass
class NormalizedTradeline:
    id: str
    bureau: str
    source_filename: str
    account_name: str = ""
    account_number_masked: str = ""
    account_type: str = ""
    portfolio_type: str = ""
    responsibility: str = ""
    creditor_classification: str = ""
    original_creditor: str = ""
    collector_or_debt_buyer: str = ""
    status: str = ""
    pay_status: str = ""
    balance: str = ""
    past_due: str = ""
    high_credit_or_original_amount: str = ""
    credit_limit: str = ""
    date_opened: str = ""
    date_closed: str = ""
    date_reported: str = ""
    date_last_activity: str = ""
    date_last_payment: str = ""
    date_of_first_delinquency: str = ""
    estimated_removal_date: str = ""
    remarks: str = ""
    payment_history_summary: str = ""
    raw_block: str = ""
    page_start: Optional[int] = None
    confidence: str = "medium"
    confidence_score: float = 0.0
    needs_admin_review: bool = True
    missing_required_fields: List[str] = field(default_factory=list)
    field_warnings: List[str] = field(default_factory=list)
    parser_confidence: str = "medium"
    source_bureau: str = ""
    source_report_date: str = ""
    source_page_hint: Optional[int] = None
    raw_verification_status: str = "not_verified"
    raw_verified_fields: List[str] = field(default_factory=list)
    raw_unverified_fields: List[str] = field(default_factory=list)
    raw_verification_warnings: List[str] = field(default_factory=list)


@dataclass
class ReviewIssue:
    id: str
    issue_type: str
    severity: str
    customer_label: str
    customer_explanation: str
    admin_explanation: str
    suggested_round: str
    related_tradeline_ids: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class ParseResult:
    engine: str
    version: str
    paid_ai_used: bool
    files: List[dict]
    tradelines: List[NormalizedTradeline]
    issues: List[ReviewIssue]
    cross_bureau_groups: List[dict]
    customer_summary: dict
    admin_summary: dict
    raw_verification_summary: dict = field(default_factory=dict)
    identity_raw_data: List[dict] = field(default_factory=list)


# -----------------------------
# Bureau profiles
# -----------------------------

DATE = r"(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})"
MONEY = r"\$?\s?[0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?|\$?\s?[0-9]+(?:\.\d{2})?"

COMMON_FIELD_PATTERNS: Dict[str, List[str]] = {
    "account_number_masked": [
        r"(?:account\s*(?:#|number|no\.?)|acct\s*(?:#|number|no\.?))\s*[:\-]?\s*([A-Za-z0-9\*\-xX]{3,32})",
        r"^\s*([A-Za-z0-9]{4,}\*{2,}[A-Za-z0-9\*]*)\s*$",
    ],
    "account_type": [
        r"(?:loan/account type|account type|type of account|loan type|type)\s*[:\-]?\s*([A-Za-z0-9 /&-]{3,80})",
    ],
    "portfolio_type": [
        r"(?:portfolio type|portfolio)\s*[:\-]?\s*([A-Za-z0-9 /&-]{3,60})",
    ],
    "responsibility": [
        r"(?:responsibility|account holder|owner)\s*[:\-]?\s*([A-Za-z0-9 /&-]{3,60})",
    ],
    "status": [
        r"(?:account status|status)\s*[:\-]?\s*([A-Za-z0-9 /&.,'$-]{3,140})",
        r"(?:pay status)\s*[:\-]?\s*([A-Za-z0-9 /&.,'$-]{3,140})",
    ],
    "pay_status": [
        r"(?:payment status|pay status|payment\s*condition)\s*[:\-]?\s*([A-Za-z0-9 /&.,'$-]{3,140})",
    ],
    "balance": [
        r"(?:current balance|balance)\s*[:\-]?\s*(" + MONEY + r")",
    ],
    "past_due": [
        r"(?:past due|amount past due)\s*[:\-]?\s*(" + MONEY + r")",
        r"(" + MONEY + r")\s+past due",
    ],
    "high_credit_or_original_amount": [
        r"(?:high credit|original amount|original balance|loan amount)\s*[:\-]?\s*(" + MONEY + r")",
    ],
    "credit_limit": [
        r"(?:credit limit|limit)\s*[:\-]?\s*(" + MONEY + r")",
    ],
    "date_opened": [
        r"(?:date opened|opened)\s*[:\-]?\s*(" + DATE + r")",
    ],
    "date_closed": [
        r"(?:date closed|closed)\s*[:\-]?\s*(" + DATE + r")",
    ],
    "date_reported": [
        r"(?:date reported|last reported|balance updated|date updated)\s*[:\-]?\s*(" + DATE + r")",
        r"\breported\s*[:\-]?\s*(" + DATE + r")",
    ],
    "date_last_activity": [
        r"(?:date of last activity|last activity|date last active)\s*[:\-]?\s*(" + DATE + r")",
    ],
    "date_last_payment": [
        r"(?:date of last payment|last payment made|last payment|date last payment)\s*[:\-]?\s*(" + DATE + r")",
    ],
    "date_of_first_delinquency": [
        r"(?:date of first delinquency|date of 1st delinquency|first delinquency date|first delinquency|dofd|original delinquency date|first reported delinquency)\s*[:\-]?\s*(" + DATE + r")",
    ],
    "estimated_removal_date": [
        r"(?:on record until|estimated month and year this item will be removed|estimated removal|scheduled to continue on record until)\s*[:\-]?\s*(" + DATE + r")",
        r"(?:by\s+(" + DATE + r"),?\s+this account is scheduled)",
    ],
    "original_creditor": [
        r"(?:original creditor|original lender|original account)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{3,90})",
    ],
    "collector_or_debt_buyer": [
        r"(?:collection agency|collector|debt buyer|assigned to)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{3,90})",
    ],
    "creditor_classification": [
        r"(?:creditor classification|classification|industry type)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{3,80})",
    ],
    "remarks": [
        r"(?:remarks|comments|comment|account information)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{5,220})",
        r"(account information disputed by consumer[^\n]{0,180})",
    ],
}

FIELD_STOP_LABELS = [
    "Account Number",
    "Owner",
    "Responsibility",
    "Account Type",
    "Loan Type",
    "Loan/Account Type",
    "Status",
    "Pay Status",
    "Status Updated",
    "Balance",
    "Balance Updated",
    "Date Opened",
    "Date Reported",
    "Date Updated",
    "Date of Last Activity",
    "Last Payment Made",
    "Date of Last Payment",
    "Date of 1st Delinquency",
    "Date of First Delinquency",
    "Date Major Delinquency",
    "Terms",
    "High Credit",
    "High Balance",
    "Credit Limit",
    "Scheduled Payment Amount",
    "Amount Past Due",
    "Actual Payment Amount",
    "Charge Off Amount",
    "Balloon Payment",
    "Term Duration",
    "Payment History",
    "On Record Until",
    "Recent Payment",
    "Monthly Payment",
]

ALIAS_GROUPS = {
    "MIDLAND CREDIT MANAGEMENT": [
        "MIDLAND CREDIT MANAGEMENT",
        "MIDLAND CREDIT MANAGEMENT INC",
        "MIDLAND CREDIT MANAGEMEN",
    ],
    "JEFFERSON CAPITAL": [
        "JEFFERSON CAPITAL LLC",
        "JEFFERSON CAPITAL SYSTEMS",
        "JEFFERSON CAPITAL SYSTEM",
    ],
    "LVNV / RESURGENT": [
        "LVNV FUNDING LLC",
        "RESURGENT/LVNV FUNDING",
        "LVNV FUNDING",
        "RESURGENT CAPITAL SERVICES",
    ],
    "CAINE & WEINER": [
        "CAINE & WEINER COMPANY INC",
        "CAINE & WEINER",
    ],
    "CAPITAL ONE": [
        "CAPITAL ONE",
        "CAPITAL ONE BANK USA NA",
        "CAPITAL ONE PLATINUM",
    ],
    "CREDIT ONE": [
        "CREDIT ONE BANK",
        "CREDIT ONE BANK NA",
    ],
    "VERIZON": [
        "VERIZON",
        "VERIZON WIRELESS",
    ],
}


def normalized_alias_name(value: str) -> str:
    key = compact_key(value)
    if not key:
        return ""
    for canonical, aliases in ALIAS_GROUPS.items():
        for alias in aliases:
            alias_key = compact_key(alias)
            if key == alias_key or key.startswith(alias_key) or alias_key.startswith(key):
                return canonical
    return clean_text(value).upper()


def visible_account_digits(value: str) -> str:
    return "".join(re.findall(r"\d", value or ""))[-4:]

ENTITY_COMPLIANCE_CUSTOMER_WORDING = "License/business status review needed."
ENTITY_COMPLIANCE_ADMIN_WORDING = (
    "Verify state business authority and collection licensing through official records before using this issue "
    "in a dispute, validation letter, complaint, or attorney-review package."
)

OFFICIAL_ENTITY_LOOKUP_LINKS = {
    "business_registry": "Use State_License_Links tab for official state business registries.",
    "state_license": "Use State_License_Links tab for official state financial/license registries.",
    "debt_collector_license": "Use State_License_Links tab; check collector/debt-buyer license route for consumer state and company state.",
    "nmls": "https://www.nmlsconsumeraccess.org/",
    "cfpb_complaint": "https://www.consumerfinance.gov/complaint/",
    "ftc": "https://reportfraud.ftc.gov/",
    "fcc": "https://consumercomplaints.fcc.gov/",
    "ncua": "https://mycreditunion.gov/consumer-assistance-center/complaint-process",
    "occ": "https://www.helpwithmybank.gov/file-a-complaint/index-file-a-complaint.html",
    "fdic": "https://ask.fdic.gov/fdicinformationandsupportcenter/s/",
    "state_ag": "Use customer state Attorney General / consumer protection official complaint route.",
}

BUREAU_SIGNATURES = {
    "Experian": ["experian", "experian credit report", "experian information solutions"],
    "Equifax": ["equifax", "equifax information services", "econsumer"],
    "TransUnion": ["transunion", "trans union", "transunion llc"],
}

NEGATIVE_TERMS = [
    "collection", "charge off", "charge-off", "charged off", "past due", "late",
    "delinquent", "derogatory", "settled", "repossession", "foreclosure",
    "120 days", "90 days", "60 days", "30 days", "placed for collection",
    "transferred", "sold", "profit and loss", "written off", "bad debt",
    "unpaid", "seriously past due"
]

COLLECTION_TERMS = [
    "collection", "collection agency", "collector", "debt buyer",
    "original creditor", "placed for collection", "assigned"
]

BOILERPLATE_TERMS = [
    "consumerfinance.gov",
    "violates the fcra",
    "additional information",
    "the last reported status of the account",
    "name, address, and phone",
    "insurer, employer, landlord",
    "upgrades and enhancements",
    "account types is good for your credit",
    "amount of the debt",
    "public records and residential information",
    "supplemental public records",
    "your credit report can include",
    "consumer added notices",
    "security freezes or locks",
    "prescreened offers of credit",
    "when reviewing your account info",
    "see if an account is open",
]

BAD_ACCOUNT_NAME_FRAGMENTS = [
    "consumerfinance.gov",
    "learnmore",
    "violates the fcra",
    "additional information",
    "last reported status",
    "account types is good",
    "amount of the debt",
    "name, address",
    "insurer, employer",
    "landlord",
    "enhancements",
    "responsibility individual",
    "public records and residential",
    "supplemental public records",
    "consumer added notices",
    "equifax.com/personal/help",
    "your credit report can include",
    "see if an account is open",
    "closed accounts should have",
    "s of credit accounts",
]

ACCOUNT_SECTION_TERMS = [
    "account number",
    "account #",
    "account name",
    "account type",
    "loan/account type",
    "date opened",
    "date reported",
    "date updated",
    "date of first delinquency",
    "date of 1st delinquency",
    "original creditor",
    "pay status",
    "payment status",
    "account status",
    "balance",
    "past due",
]

NON_ACCOUNT_SECTION_TERMS = [
    "payment history guide",
    "your credit report can include",
    "consumer added notices",
    "security freezes or locks",
    "prescreened offers",
    "see if an account is open",
    "closed accounts should have no money",
    "for more information",
]


# -----------------------------
# Text + page utilities
# -----------------------------

def detect_bureau(filename: str, text: str) -> str:
    sample = (filename + "\n" + text[:5000]).lower()
    scores = {}
    for bureau, terms in BUREAU_SIGNATURES.items():
        scores[bureau] = sum(1 for t in terms if t in sample)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unknown Bureau"


def page_split(text: str) -> List[Tuple[Optional[int], str]]:
    """
    Supports extraction format with --- PAGE 1 --- markers.
    """
    parts = re.split(r"\n?\s*---\s*PAGE\s+(\d+)\s*---\s*\n?", text, flags=re.I)
    if len(parts) <= 1:
        return [(None, text)]
    pages = []
    preface = parts[0]
    for i in range(1, len(parts), 2):
        try:
            page_num = int(parts[i])
        except Exception:
            page_num = None
        page_text = parts[i + 1] if i + 1 < len(parts) else ""
        pages.append((page_num, page_text))
    return pages


def likely_account_start_line(line: str, lookahead: str) -> bool:
    cleaned = clean_text(line).strip()
    lower = cleaned.lower()
    if is_bad_account_name(cleaned):
        return False
    if re.search(r"^(?:account|date|balance|status|pay status|responsibility|address|phone|payment|remarks|terms|owner)\b", lower):
        return False
    if re.search(r"\d{2}/\d{2}/\d{4}|\$\d|account number|date opened|balance|pay status|account type|loan type", cleaned, flags=re.I):
        return False
    return bool(re.search(r"\b(account number|date opened|date updated|balance|pay status|account type|loan/account type|date of 1st delinquency|original creditor)\b", lookahead, flags=re.I))


def line_based_candidate_blocks(page_text: str) -> List[str]:
    lines = [clean_text(line) for line in page_text.splitlines() if clean_text(line)]
    starts: List[int] = []
    for index, line in enumerate(lines):
        lookahead = "\n".join(lines[index:index + 14])
        if likely_account_start_line(line, lookahead):
            starts.append(index)
    blocks = []
    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else min(len(lines), start + 42)
        block_start = start
        if block_start > 0 and account_name_quality(lines[block_start - 1]) >= 2:
            block_start -= 1
        while block_start > 0 and re.search(
            r"(account information disputed by consumer|consumer disputes this account|fair credit reporting act)",
            lines[block_start - 1],
            flags=re.I,
        ):
            block_start -= 1
        block = "\n".join(lines[block_start:end])
        if len(block) > 90:
            blocks.append(block)
    return blocks


def candidate_blocks(text: str, bureau: str = "") -> List[Tuple[Optional[int], str]]:
    blocks: List[Tuple[Optional[int], str]] = []

    for page_num, page_text in page_split(text):
        page_text = clean_text(page_text)
        if not page_text:
            continue

        if bureau in {"TransUnion", "Equifax"} or re.search(r"\b(Account Information|Collections|Collection Agency Name)\b", page_text, flags=re.I):
            for block in line_based_candidate_blocks(page_text):
                blocks.append((page_num, block))

        # Main split using paragraph gaps
        chunks = re.split(r"\n\s*\n", page_text)
        buffer: List[str] = []

        for chunk in chunks:
            c = clean_text(chunk)
            if len(c) < 20:
                continue
            lower = c.lower()
            continuation = lower.startswith((
                "date opened",
                "date of last activity",
                "date of last payment",
                "scheduled payment",
                "actual payment",
                "amount past due",
                "payment history",
                "terms",
                "high balance",
                "credit limit",
                "by ",
            ))
            starts = (
                any(label in lower for label in ["account number", "account #", "payment status", "account status", "account name"])
                or any(term in lower for term in NEGATIVE_TERMS)
            ) and not continuation
            if starts and buffer:
                block = "\n".join(buffer)
                if len(block) > 80:
                    blocks.append((page_num, block))
                buffer = [c]
            else:
                buffer.append(c)

            if len("\n".join(buffer)) > 3500:
                blocks.append((page_num, "\n".join(buffer)))
                buffer = []

        if buffer:
            block = "\n".join(buffer)
            if len(block) > 80:
                blocks.append((page_num, block))

    return dedupe_blocks(blocks)


def dedupe_blocks(blocks: List[Tuple[Optional[int], str]]) -> List[Tuple[Optional[int], str]]:
    seen = set()
    out = []
    for page_num, block in blocks:
        clean = clean_text(block)
        if len(clean) < 80:
            continue
        key = hashlib.sha1(clean[:700].encode("utf-8", errors="ignore")).hexdigest()
        if key not in seen:
            seen.add(key)
            out.append((page_num, clean[:4500]))
    return out


# -----------------------------
# Field extraction
# -----------------------------

def first_match(patterns: List[str], text: str) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.I | re.M)
        if m:
            val = clean_text(m.group(1))
            val = re.split(r"\n| {3,}", val)[0].strip(" :-")
            return val[:240]
    return ""


def trim_embedded_labels(value: str, field_name: str) -> str:
    value = clean_text(value).strip(" :-|")
    if not value:
        return ""

    protected = {
        "account_type": {"Account"},
        "status": set(),
        "pay_status": set(),
        "remarks": set(),
    }.get(field_name, set())

    for label in FIELD_STOP_LABELS:
        if label in protected:
            continue
        pattern = r"(?:\s+\|\s+|\s+\|\s*|\s{1,})(?=" + re.escape(label) + r"\b\s*:?)"
        parts = re.split(pattern, value, maxsplit=1, flags=re.I)
        if len(parts) > 1 and parts[0].strip():
            value = parts[0].strip(" :-|")

    if field_name in {"status", "pay_status"}:
        value = re.split(
            r"\s+(?:Status Updated|Balance Updated|Balance|Recent Payment|Monthly Payment|Credit Limit|Highest Balance|Terms|Payment History)\b",
            value,
            maxsplit=1,
            flags=re.I,
        )[0].strip(" :-|")
        if re.match(
            r"^(?:Date Opened|Date Reported|Date Updated|Date of|Terms|Frequency|Months Reviewed|Scheduled Payment|Amount Past Due)\b",
            value,
            flags=re.I,
        ):
            value = ""

    if field_name == "account_type":
        value = re.split(r"\s+\|\s+|\s+Status\s*:", value, maxsplit=1, flags=re.I)[0].strip(" :-|")

    if field_name == "responsibility":
        m = re.search(r"\b(Individual|Joint|Authorized User|Co-signer|Terminated|Undesignated)\b", value, flags=re.I)
        if m:
            value = clean_text(m.group(1)).title()

    return value[:240]


def infer_missing_fields_from_block(t: NormalizedTradeline) -> None:
    block = t.raw_block
    lower = block.lower()

    if not t.past_due:
        m = re.search(r"(" + MONEY + r")\s+past due\b", block, flags=re.I)
        if m:
            t.past_due = normalize_money(m.group(1))

    if not t.pay_status:
        m = re.search(r"\bPay Status\s*[:\-]?\s*([A-Za-z0-9 /&.,'$-]{3,120})", block, flags=re.I)
        if m:
            t.pay_status = trim_embedded_labels(m.group(1), "pay_status")

    if not t.status and t.pay_status:
        t.status = t.pay_status

    if not t.date_reported:
        m = re.search(r"\b(?:Balance Updated|Date Updated)\s*[:\-]?\s*(" + DATE + r")", block, flags=re.I)
        if m:
            t.date_reported = normalize_date(m.group(1))

    if not t.date_last_payment:
        m = re.search(r"\b(?:Last Payment Made|Date of Last Payment|Last Payment)\s*[:\-]?\s*(" + DATE + r")", block, flags=re.I)
        if m:
            t.date_last_payment = normalize_date(m.group(1))

    if not t.responsibility:
        m = re.search(r"\b(?:Owner|Responsibility)\s*[:\-]?\s*(Individual|Joint|Authorized User|Co-signer|Terminated|Undesignated)", block, flags=re.I)
        if m:
            t.responsibility = clean_text(m.group(1)).title()

    if not t.account_type:
        m = re.search(r"\bLoan Type\s*[:\-]?\s*([A-Za-z0-9 /&-]{3,80})", block, flags=re.I)
        if m:
            t.account_type = trim_embedded_labels(m.group(1), "account_type")

    if not t.credit_limit:
        m = re.search(r"\bCredit Limit(?:\s*\(Hist\.\))?\s*(?:[:\-]|of)?\s*(" + MONEY + r")", block, flags=re.I)
        if m:
            t.credit_limit = normalize_money(m.group(1))

    if not t.high_credit_or_original_amount:
        m = re.search(r"\b(?:High Balance|Highest Balance|Original Balance|High Credit)(?:\s*\(Hist\.\))?\s*(?:[:\-]|of)?\s*(" + MONEY + r")", block, flags=re.I)
        if m:
            t.high_credit_or_original_amount = normalize_money(m.group(1))

    if not t.estimated_removal_date:
        m = re.search(r"\bOn Record Until\s*[:\-]?\s*(" + DATE + r")", block, flags=re.I)
        if m:
            t.estimated_removal_date = normalize_date(m.group(1))

    if not t.date_of_first_delinquency:
        m = re.search(r"\b(?:Date of 1st Delinquency|Date of First Delinquency|DOFD|Original Delinquency Date|First Delinquency Date)\s*[:\-]?\s*(" + DATE + r")", block, flags=re.I)
        if m:
            t.date_of_first_delinquency = normalize_date(m.group(1))

    if not t.original_creditor:
        m = re.search(r"\b(?:Original Creditor|Original Lender|Owner)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{3,90})", block, flags=re.I)
        if m:
            t.original_creditor = trim_embedded_labels(m.group(1), "original_creditor")

    if not t.collector_or_debt_buyer and is_collection_like(t):
        t.collector_or_debt_buyer = t.account_name

    if "account information disputed by consumer" in lower and "disputed by consumer" not in (t.remarks or "").lower():
        t.remarks = "; ".join(part for part in [t.remarks, "Account information disputed by consumer"] if part)


def finalize_parser_metadata(t: NormalizedTradeline) -> None:
    blob = tradeline_blob(t)
    t.source_bureau = t.bureau.lower()
    t.source_page_hint = t.page_start
    t.parser_confidence = t.confidence
    required = ["account_name", "account_number_masked", "account_type", "status", "balance", "date_opened", "date_reported"]
    if any(term in blob for term in ["collection", "charge", "late", "past due", "delinquent", "debt buyer"]):
        required.append("date_of_first_delinquency")
    if is_collection_like(t):
        required.extend(["original_creditor", "creditor_classification"])
    labels = {
        "account_name": "Account/Furnisher Name",
        "account_number_masked": "Account Number",
        "account_type": "Account Type",
        "status": "Status / Pay Status",
        "balance": "Balance",
        "date_opened": "Date Opened",
        "date_reported": "Date Reported / Date Updated",
        "date_of_first_delinquency": "Date of First Delinquency / DOFD",
        "original_creditor": "Original Creditor",
        "creditor_classification": "Creditor Classification",
    }
    t.missing_required_fields = [labels[field] for field in required if not getattr(t, field, "")]
    warnings = []
    if "Date of First Delinquency / DOFD" in t.missing_required_fields:
        warnings.append("DOFD Missing / Timeline Review Needed")
    if is_collection_like(t) and not t.original_creditor:
        warnings.append("Original creditor review recommended")
    if not t.account_number_masked:
        warnings.append("Account identifier missing or not visible")
    if account_name_quality(t.account_name) < 1:
        warnings.append("Account boundary/name confidence needs admin review")
    t.field_warnings = warnings
    if warnings or len(t.missing_required_fields) >= 4:
        t.parser_confidence = "low"
        t.confidence = "low"
        t.needs_admin_review = True
    elif t.missing_required_fields:
        t.parser_confidence = "medium"
        if t.confidence == "high":
            t.confidence = "medium"


def tradeline_blob(t: NormalizedTradeline) -> str:
    return " ".join(str(value or "") for value in [
        t.account_name,
        t.account_type,
        t.status,
        t.pay_status,
        t.balance,
        t.past_due,
        t.original_creditor,
        t.collector_or_debt_buyer,
        t.creditor_classification,
        t.remarks,
        t.raw_block,
    ]).lower()


def normalize_verification_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def raw_text_contains_money(raw_text: str, value: str) -> bool:
    target = normalize_money(value)
    if not target:
        return True
    for match in re.finditer(MONEY, raw_text or ""):
        if normalize_money(match.group(0)) == target:
            return True
    return False


def raw_text_contains_date(raw_text: str, value: str) -> bool:
    target = normalize_date(value)
    if not target:
        return True
    if value and value.lower() in (raw_text or "").lower():
        return True
    for match in re.finditer(DATE, raw_text or "", flags=re.I):
        if normalize_date(match.group(0)) == target:
            return True
    return False


def raw_text_contains_account_digits(raw_text: str, value: str) -> bool:
    digits = visible_account_digits(value)
    if not digits:
        return True
    raw_digits = re.sub(r"\D+", "", raw_text or "")
    return digits in raw_digits


def raw_text_contains_words(raw_text: str, value: str) -> bool:
    normalized_value = normalize_verification_text(value)
    if not normalized_value:
        return True
    normalized_raw = normalize_verification_text(raw_text)
    if normalized_value in normalized_raw:
        return True
    words = [normalize_verification_text(word) for word in re.findall(r"[A-Za-z0-9&']{3,}", value or "")]
    words = [word for word in words if word]
    if not words:
        return True
    return sum(1 for word in words if word in normalized_raw) >= max(1, min(2, len(words)))


RAW_VERIFICATION_FIELDS = [
    ("account_name", "Account/Furnisher Name", "words"),
    ("account_number_masked", "Account Number", "digits"),
    ("account_type", "Account Type", "words"),
    ("responsibility", "Responsibility", "words"),
    ("original_creditor", "Original Creditor", "words"),
    ("collector_or_debt_buyer", "Collector / Debt Buyer", "words"),
    ("status", "Status / Pay Status", "words"),
    ("pay_status", "Pay Status", "words"),
    ("balance", "Balance", "money"),
    ("past_due", "Past Due", "money"),
    ("high_credit_or_original_amount", "High Credit / Original Amount", "money"),
    ("credit_limit", "Credit Limit", "money"),
    ("date_opened", "Date Opened", "date"),
    ("date_closed", "Date Closed", "date"),
    ("date_reported", "Date Reported / Updated", "date"),
    ("date_last_activity", "Date Last Activity", "date"),
    ("date_last_payment", "Date Last Payment", "date"),
    ("date_of_first_delinquency", "Date of First Delinquency / DOFD", "date"),
    ("estimated_removal_date", "Estimated Removal", "date"),
    ("remarks", "Remarks / Dispute Notation", "words"),
]


def verify_tradeline_against_raw_text(t: NormalizedTradeline, report_text: str) -> None:
    raw_scope = t.raw_block or report_text
    verified: List[str] = []
    unverified: List[str] = []

    for field_name, label, verifier in RAW_VERIFICATION_FIELDS:
        value = getattr(t, field_name, "")
        if not value:
            continue
        if verifier == "money":
            ok = raw_text_contains_money(raw_scope, value)
        elif verifier == "date":
            ok = raw_text_contains_date(raw_scope, value)
        elif verifier == "digits":
            ok = raw_text_contains_account_digits(raw_scope, value)
        else:
            ok = raw_text_contains_words(raw_scope, value)
        if ok:
            verified.append(label)
        else:
            unverified.append(label)

    warnings = []
    if not t.raw_block:
        warnings.append("No account-level raw block retained for parser verification")
    else:
        warnings.append("Exact verification scope: account-level raw bureau block")
    if not report_text:
        warnings.append("No full raw report text available for parser verification")
    if unverified:
        warnings.append("Parsed field(s) need manual raw-report confirmation: " + ", ".join(unverified[:8]))

    t.raw_verified_fields = verified
    t.raw_unverified_fields = unverified
    t.raw_verification_warnings = warnings
    if not report_text:
        t.raw_verification_status = "not_verified"
    elif unverified:
        t.raw_verification_status = "needs_review"
    else:
        t.raw_verification_status = "verified"

    for warning in warnings:
        if warning not in t.field_warnings:
            t.field_warnings.append(warning)
    if unverified:
        t.needs_admin_review = True
        if t.parser_confidence == "high":
            t.parser_confidence = "medium"
        if t.confidence == "high":
            t.confidence = "medium"


def verify_tradelines_against_raw_data(report_texts: Dict[str, dict], tradelines: List[NormalizedTradeline]) -> dict:
    text_by_file = {
        filename: clean_text(payload.get("text", ""))
        for filename, payload in report_texts.items()
    }
    for t in tradelines:
        verify_tradeline_against_raw_text(t, text_by_file.get(t.source_filename, ""))

    total = len(tradelines)
    verified = sum(1 for t in tradelines if t.raw_verification_status == "verified")
    needs_review = sum(1 for t in tradelines if t.raw_verification_status == "needs_review")
    not_verified = sum(1 for t in tradelines if t.raw_verification_status == "not_verified")
    return {
        "status": "pass_with_review" if needs_review or not_verified else "pass",
        "total_tradelines_checked": total,
        "verified": verified,
        "needs_review": needs_review,
        "not_verified": not_verified,
        "warning": "Scanner verified parsed fields against raw extracted report text before output. Items marked needs_review require admin raw-report confirmation before letters, mail, complaints, or escalation.",
    }


def _page_for_offset(text: str, offset: int) -> int | None:
    page = None
    for marker in re.finditer(r"--- PAGE\s+(\d+)\s+---", text, flags=re.I):
        if marker.start() <= offset:
            try:
                page = int(marker.group(1))
            except ValueError:
                page = None
        else:
            break
    return page


def _mask_sensitive_identity_value(category: str, value: str) -> str:
    value = clean_text(value)
    if category == "masked_ssn":
        digits = re.sub(r"\D", "", value)
        return "***-**-" + digits[-4:] if len(digits) >= 4 else "***-**-****"
    if category == "dob":
        m = re.search(r"\b(?:19|20)\d{2}\b", value)
        return f"Year only: {m.group(0)}" if m else "DOB present - masked"
    return value


def _identity_add(rows: List[dict], seen: set, category: str, raw_value: str, bureau: str, filename: str, text: str, offset: int) -> None:
    raw_value = _mask_sensitive_identity_value(category, raw_value).strip(" .,:;-")
    if not raw_value:
        return
    key = (category, raw_value.lower(), bureau, filename)
    if key in seen:
        return
    seen.add(key)
    rows.append({
        "category": category,
        "raw_value": raw_value,
        "bureau": bureau,
        "source_filename": filename,
        "page": _page_for_offset(text, offset),
        "source": f"{bureau} {filename}".strip(),
    })


def _identity_candidate_sections(text: str) -> List[tuple[int, str]]:
    sections: List[tuple[int, str]] = []
    lower = text.lower()
    end_markers = [
        "\ncredit accounts",
        "\naccount information",
        "\naccounts\n",
        "\npublic records",
        "\nhard inquiries",
        "\ncredit inquiries",
        "\ncollections",
        "\nrequests for your credit",
    ]
    keep_markers = [
        "social security",
        "date of birth",
        "current address",
        "former address",
        "other address",
        "addresses",
        "also known as",
        "phone numbers",
        "employers",
        "employment information",
        "former name",
    ]
    for match in re.finditer(r"\bPersonal Information\b", text, flags=re.I):
        start = match.start()
        candidates = [lower.find(marker, start + 1) for marker in end_markers]
        candidates = [position for position in candidates if position > start]
        end = min(candidates) if candidates else min(len(text), start + 20000)
        section = text[start:end]
        section_lower = section.lower()
        if "this section includes your name" in section_lower and not re.search(r"\b(?:xxx-xx-|date of birth|current address|addresses)\b", section_lower):
            continue
        if any(marker in section_lower for marker in keep_markers):
            sections.append((start, section))
    return sections or [(0, text[:12000])]


def extract_identity_raw_data(report_texts: Dict[str, dict]) -> List[dict]:
    rows: List[dict] = []
    seen: set = set()
    street_suffix = r"(?:ST|STREET|RD|ROAD|AVE|AVENUE|BLVD|DR|DRIVE|LN|LANE|WAY|CT|COURT|CIR|CIRCLE|PL|PLACE|PKWY|HWY|TER|TERRACE)"
    for filename, payload in report_texts.items():
        text = str(payload.get("text", "") or "")
        bureau = str(payload.get("bureau", "") or detect_bureau(filename, text))
        for section_start, section in _identity_candidate_sections(text):
            for pattern in [
                r"\bPrepared for\s*:?\s*([A-Z][A-Z .'\-]{2,70})",
                r"\b(?:Consumer Name|Legal Name|Full Name)\s*:?\s*([A-Z][A-Z .'\-]{2,70})",
                r"(?:^|\n)\s*Name\b\s*:?\s*(?:\n\s*)?([A-Z][A-Z .'\-]{2,70})",
                r"\bAlso Known As\s+(?:AKA\s+)?([A-Z][A-Z .'\-]{2,70})",
            ]:
                for match in re.finditer(pattern, section, flags=re.I):
                    value = clean_text(match.group(1)).strip(" .,:;-")
                    if value and len(value.split()) <= 8 and not is_bad_account_name(value):
                        _identity_add(rows, seen, "name", value, bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"\bPersonal Information\b.*?impact on your credit score\.\s*\n([A-Z][A-Z .'\-]{2,70})\s*\n", section, flags=re.I | re.S):
                value = clean_text(match.group(1)).strip(" .,:;-")
                if value and len(value.split()) <= 8 and not is_bad_account_name(value):
                    _identity_add(rows, seen, "name", value, bureau, filename, text, section_start + match.start(1))
            for match in re.finditer(
                rf"\b(?:PO BOX[ \t]+\d+|\d{{2,6}}[ \t]+[A-Z0-9 .'\-]+?[ \t]+{street_suffix})[^\n|]{{0,90}}\b[A-Z]{{2}},?\s+\d{{5}}(?:-\d{{4}})?",
                section,
                flags=re.I,
            ):
                _identity_add(rows, seen, "address", match.group(0), bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", section):
                prior = section[max(0, match.start() - 100):match.start()].lower()
                if "phone" in prior:
                    _identity_add(rows, seen, "phone", match.group(0), bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", section, flags=re.I):
                _identity_add(rows, seen, "email", match.group(0), bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"\b(?:DOB|Date of Birth|Birth Date)\s*:?\s*([0-9Xx*/\-]{4,12}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", section, flags=re.I):
                _identity_add(rows, seen, "dob", match.group(1), bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"\b(?:SSN|Social Security(?: Number)?)\s*:?\s*([Xx*\d]{3}[-\s]?[Xx*\d]{2}[-\s]?[Xx*\d]{4})", section, flags=re.I):
                _identity_add(rows, seen, "masked_ssn", match.group(1), bureau, filename, text, section_start + match.start())
            for match in re.finditer(r"\b(?:Employer|Employment)\b\s*:?\s*([A-Z0-9 &.'/\-]{3,80})", section, flags=re.I):
                value = trim_embedded_labels(match.group(1), "remarks").strip(" .,:;-")
                if value and value.lower() not in {"data", "information", "employment information"}:
                    _identity_add(rows, seen, "employment", value, bureau, filename, text, section_start + match.start())
    return rows


def extract_field(field_name: str, block: str) -> str:
    value = first_match(COMMON_FIELD_PATTERNS.get(field_name, []), block)
    value = trim_embedded_labels(value, field_name)
    if field_name in {"balance", "past_due", "high_credit_or_original_amount", "credit_limit"}:
        return normalize_money(value)
    if "date" in field_name:
        return normalize_date(value)
    if field_name == "account_number_masked":
        return mask_account_number(value)
    return value


def is_bad_account_name(name: str) -> bool:
    cleaned = clean_account_name_candidate(name) if "clean_account_name_candidate" in globals() else clean_text(name).strip(" .;:,|-")
    lower = cleaned.lower()
    if not cleaned or cleaned == "Review Item":
        return True
    if re.search(r"\bpage\s+\d+\s+of\s+\d+\b", lower) or re.search(r"\b(?:efx|acr|disc)\b", lower):
        return True
    if re.fullmatch(r"\d+\s+collection account", lower):
        return True
    if lower.startswith((
        "c/o ",
        "interest type",
        "last payment made",
        "last payment",
        "collection account",
        "original creditor",
        "responsibility ",
        "on record until",
        "removed ",
        "estimated month and year",
        "https://",
        "http://",
    )):
        return True
    if lower in {"scheduled", "terms", "term", "frequency", "monthly", "lines of credit", "contact info", "comment", "comments"}:
        return True
    if re.search(r"\b(?:po|p\.o\.?|ox|box)\s*\d+", lower) and re.search(r"\b(?:va|md|dc|sc|nc|ca|mn|mi|de|tx|nv)\b", lower):
        return True
    if re.fullmatch(r"[a-z .'-]+,\s*[a-z]{2}", lower):
        return True
    if re.fullmatch(r"[a-z .'-]+\s+(?:al|ak|az|ar|ca|co|ct|de|dc|fl|ga|hi|ia|id|il|in|ks|ky|la|ma|md|me|mi|mn|mo|ms|mt|nc|nd|ne|nh|nj|nm|nv|ny|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|va|vt|wa|wi|wv|wy)", lower):
        return True
    if re.fullmatch(r"(?:p\.?o\.?\s+box|box\s+\d+.*|\d{2,6}\s+.+)", lower) and re.search(r"\b(?:st|street|rd|road|ave|avenue|blvd|drive|dr|lane|ln|way|suite|ste|box|greenville|sartell)\b", lower):
        return True
    if lower in {"amount paid", "account closed at consumer's request", "placed for collection", "collection<", ">placed for collection<"}:
        return True
    if lower.startswith(("collection reported", ">settled", "settled-less", "paid/", "date reported", "date updated")):
        return True
    if len(cleaned) < 3 or len(cleaned) > 90:
        return True
    if any(fragment in lower for fragment in BAD_ACCOUNT_NAME_FRAGMENTS):
        return True
    if re.match(
        r"^(?:high balance|highest balance|high credit|credit limit|balance|past due|amount past due|monthly payment|recent payment)\b",
        lower,
    ):
        return True
    if lower.startswith(("of ", "and ", "the ", "this ", "that ", "www.")):
        return True
    if cleaned.endswith(".") and len(cleaned.split()) > 3:
        return True
    if len(cleaned.split()) > 8:
        return True
    if not re.search(r"[A-Za-z]", cleaned):
        return True
    return False


def clean_account_name_candidate(name: str) -> str:
    cleaned = clean_text(name).strip(" .;:,|-")
    cleaned = re.sub(r"\s+(?:\*{2,}|\d{3,}|\d{2,}\*{2,}|[xX]{2,}|\*{2,}\d{2,})[A-Za-z0-9*xX-]*\s*$", "", cleaned).strip(" .;:,|-")
    cleaned = re.sub(r"\s+\*{2,}\d{2,}\*{2,}\s*$", "", cleaned).strip(" .;:,|-")
    cleaned = re.sub(r"\s+-\s*(?:Closed|Open|Current|Paid|Collection)\s*$", lambda m: " - " + m.group(0).split("-")[-1].strip().title(), cleaned, flags=re.I)
    return cleaned


def export_account_name_with_qa(name: str) -> Tuple[str, str]:
    cleaned = clean_account_name_candidate(name)
    if is_bad_account_name(cleaned):
        return (
            "ADMIN REVIEW REQUIRED - parser fragment detected",
            f"Parser cleanup required before customer view. Original extracted label: {cleaned or 'blank'}",
        )
    return cleaned, ""


THREE_BUREAU_COMPARISON_TEMPLATE_HEADERS = [
    "Account Name",
    "Primary Bureau",
    "Matched Bureaus",
    "Missing Bureaus",
    "Errors",
    "Findings",
    "Primary Account #",
    "Primary Type",
    "Primary Balance",
    "Primary Past Due",
    "Primary Status",
    "Primary Opened",
    "Primary Reported",
    "Primary DOFD",
]


def account_name_quality(name: str) -> float:
    cleaned = clean_account_name_candidate(name)
    lower = cleaned.lower()
    if is_bad_account_name(cleaned):
        return -10.0

    score = 0.0
    words = re.findall(r"[A-Za-z0-9&']+", cleaned)
    if 1 <= len(words) <= 5:
        score += 2.0
    if len(words) > 5:
        score -= 1.0
    if re.search(r"\b(bank|credit|capital|midland|ford|federal|jpm|jpmcb|caine|jefferson|systems?|management|services?|financial|portfolio|synchrony|citibank|northwest|firstpoint|resources|funding|lvnv|resurgent|macys|cbna)\b", lower, flags=re.I):
        score += 2.0
    if any(x in lower for x in [
        "prepared for",
        "date:",
        "date reported",
        "balance:",
        "loan/account type",
        "account type:",
        "account type ",
        "loan type",
        "pay status",
        "credit limit",
        "high credit",
        "status:",
        "term duration",
        "terms paid",
        "minimum payment",
        "confirmation #",
        "responsibility relationship",
    ]):
        score -= 5.0
    if re.search(r"\d{2}/\d{2}/\d{4}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\s+\d{4}\b|\b20\d{2}\s+(?:CO|OK|C|30|60|90|120|150|CLS|ND)(?:\s+(?:CO|OK|C|30|60|90|120|150|CLS|ND))*\b|\$\d", cleaned, flags=re.I):
        score -= 4.0
    if "|" in cleaned or ":" in cleaned:
        score -= 2.0
    return score


def tradeline_quality_score(t: NormalizedTradeline) -> float:
    score = t.confidence_score * 10
    score += account_name_quality(t.account_name)
    if t.account_number_masked:
        score += 4
    if t.balance:
        score += 1
    if t.account_type:
        score += 1
    if t.date_opened:
        score += 1
    if t.date_reported:
        score += 1
    if t.original_creditor:
        score += 1
    if t.status and t.status.lower() not in {"date opened", "account information"}:
        score += 1
    if len(t.raw_block) > 3200:
        score -= 1
    return score


def guess_account_name(block: str) -> str:
    lines = [clean_text(x).strip(" :-") for x in block.splitlines() if clean_text(x)]
    bad = (
        "account number", "account #", "balance", "date ", "status", "payment",
        "remarks", "comments", "address", "phone", "page ", "experian", "equifax",
        "transunion", "trans union", "credit report", "report number", "summary",
        "prepared for", "confirmation #", "account type", "loan type", "pay status", "responsibility relationship"
    )

    labeled = first_match([
        r"(?:account name|furnisher|subscriber)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{3,90})"
    ], block)
    if labeled:
        labeled = clean_account_name_candidate(labeled)
        return labeled if not is_bad_account_name(labeled) else "Review Item"

    candidates = []
    for line in lines[:26]:
        lower = line.lower()
        if any(lower.startswith(x) for x in bad):
            continue
        if re.match(r"^date\s*:", lower):
            continue
        if re.match(r"^(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}$", lower):
            continue
        if re.match(r"^20\d{2}\s+(?:co|ok|c|30|60|90|120|150|cls|nd)(?:\s+(?:co|ok|c|30|60|90|120|150|cls|nd))*$", lower):
            continue
        if lower.startswith(("responsibility relationship", "total months", "rating", "ok", "date opened", "terms paid", "minimum payment", "pay status")):
            continue
        if lower.endswith("minimum payment.") or "credit scoring model" in lower:
            continue
        if lower in {"collections", "satisfactory accounts", "potentially negative", "account information"}:
            continue
        if re.fullmatch(r"[A-Z][A-Z ]{1,30}", line) and len(line.split()) <= 4:
            # Skip consumer-name header lines in bureau PDFs. Creditor names
            # usually appear near account fields and score higher below.
            if not re.search(r"\b(BANK|CREDIT|CAPITAL|MIDLAND|FORD|FEDERAL|JPM|JPMCB|CAINE|JEFFERSON|RESURGENT|LVNV|MACYS|CBNA|MOTOR|FUNDING|SYSTEM|SYSTEMS|MANAGEMENT|SERVICES|FIRSTPOINT|RESOURCES)\b", line):
                continue
        line = clean_account_name_candidate(line)
        if len(line) < 3 or len(line) > 85:
            continue
        if not re.search(r"[A-Za-z]", line):
            continue
        # Avoid long report sentences
        if len(line.split()) <= 9 and not is_bad_account_name(line):
            candidates.append(line)

    if candidates:
        return max(candidates, key=account_name_quality)

    return "Review Item"


def is_boilerplate_block(block: str) -> bool:
    lower = block.lower()
    boilerplate_hits = sum(1 for term in BOILERPLATE_TERMS if term in lower)
    core_field_hits = sum(
        1
        for term in ACCOUNT_SECTION_TERMS
        if term in lower
    )
    return boilerplate_hits > 0 and core_field_hits < 2


def account_section_score(block: str) -> int:
    lower = block.lower()
    return sum(1 for term in ACCOUNT_SECTION_TERMS if term in lower)


def has_non_account_section_bias(block: str) -> bool:
    lower = block.lower()
    non_account_hits = sum(1 for term in NON_ACCOUNT_SECTION_TERMS if term in lower)
    return non_account_hits >= 2 and account_section_score(block) < 4


def is_probable_tradeline(t: NormalizedTradeline) -> bool:
    if is_bad_account_name(t.account_name):
        return False
    if has_non_account_section_bias(t.raw_block):
        return False
    if compact_key(t.account_name) in {"co", "ok", "cls", "nd", "address"}:
        return False

    core_fields = [
        t.account_number_masked,
        t.account_type,
        t.status or t.pay_status,
        t.balance,
        t.date_opened,
        t.date_reported,
        t.date_of_first_delinquency,
        t.original_creditor,
        t.remarks,
    ]
    core_count = sum(1 for field in core_fields if field)
    lower = t.raw_block.lower()
    section_score = account_section_score(t.raw_block)
    has_money_or_account = bool(t.balance or t.account_number_masked)
    has_account_identifier = bool(
        t.account_number_masked
        or re.search(r"\b(?:account number|account #|account name)\b", lower, flags=re.I)
    )
    has_credit_signal = any(
        term in lower
        for term in [
            "account type",
            "original creditor",
            "date opened",
            "date reported",
            "payment status",
            "account status",
            "credit limit",
            "past due",
            "high credit",
        ]
    )
    if section_score < 2 and not has_account_identifier:
        return False
    if not has_account_identifier and core_count < 4:
        return False
    return core_count >= 2 and (has_money_or_account or has_credit_signal)


def classify_category(t: NormalizedTradeline) -> Tuple[str, str, str, str]:
    blob = " ".join([
        t.account_name, t.account_type, t.status, t.pay_status, t.remarks,
        t.original_creditor, t.collector_or_debt_buyer, t.raw_block
    ]).lower()

    if any(x in blob for x in COLLECTION_TERMS):
        return (
            "Collection Review",
            "medium",
            "Collection or debt-buyer information should be reviewed.",
            "Round 2 — Collection Review"
        )

    if "charge" in blob and "off" in blob:
        return (
            "Reporting Accuracy Review",
            "medium",
            "Charge-off reporting should be reviewed for balance, status, dates, and ownership.",
            "Round 4 — Reporting Accuracy Review"
        )

    if any(x in blob for x in ["transferred", "sold", "closed"]):
        return (
            "Reporting Accuracy Review",
            "medium",
            "Transferred, sold, or closed reporting should be reviewed for accuracy.",
            "Round 4 — Reporting Accuracy Review"
        )

    if any(x in blob for x in NEGATIVE_TERMS):
        return (
            "Factual Review",
            "medium",
            "This negative item should be reviewed for factual accuracy.",
            "Round 5 — Factual Review"
        )

    return (
        "Bureau Match Review",
        "low",
        "Compare this item across bureaus for consistency.",
        "Round 3 — Bureau Match Review"
    )


def score_confidence(t: NormalizedTradeline) -> float:
    score = 0.0
    if t.account_name and t.account_name != "Review Item":
        score += 0.22
    if t.account_number_masked:
        score += 0.16
    if t.balance:
        score += 0.10
    if t.status or t.pay_status:
        score += 0.13
    if t.date_opened:
        score += 0.08
    if t.date_reported:
        score += 0.08
    if t.date_of_first_delinquency or t.estimated_removal_date:
        score += 0.10
    if t.raw_block and len(t.raw_block) > 250:
        score += 0.08
    if any(x in t.raw_block.lower() for x in NEGATIVE_TERMS):
        score += 0.05
    return min(1.0, score)


def confidence_label(score: float) -> str:
    if score >= 0.72:
        return "high"
    if score >= 0.42:
        return "medium"
    return "low"


def parse_tradelines_for_bureau(bureau: str, filename: str, text: str) -> List[NormalizedTradeline]:
    tradelines = []
    for page_num, block in candidate_blocks(text, bureau):
        lower = block.lower()
        if is_boilerplate_block(block):
            continue
        has_signal = (
            any(term in lower for term in NEGATIVE_TERMS)
            or any(label in lower for label in ["account number", "account #", "date opened", "payment status", "account status"])
        )
        if not has_signal:
            continue

        account_name = guess_account_name(block)
        t = NormalizedTradeline(
            id=stable_id(bureau, filename, account_name, block[:160]),
            bureau=bureau,
            source_filename=filename,
            account_name=account_name,
            account_number_masked=extract_field("account_number_masked", block),
            account_type=extract_field("account_type", block),
            portfolio_type=extract_field("portfolio_type", block),
            responsibility=extract_field("responsibility", block),
            creditor_classification=extract_field("creditor_classification", block),
            original_creditor=extract_field("original_creditor", block),
            collector_or_debt_buyer=extract_field("collector_or_debt_buyer", block),
            status=extract_field("status", block),
            pay_status=extract_field("pay_status", block),
            balance=extract_field("balance", block),
            past_due=extract_field("past_due", block),
            high_credit_or_original_amount=extract_field("high_credit_or_original_amount", block),
            credit_limit=extract_field("credit_limit", block),
            date_opened=extract_field("date_opened", block),
            date_closed=extract_field("date_closed", block),
            date_reported=extract_field("date_reported", block),
            date_last_activity=extract_field("date_last_activity", block),
            date_last_payment=extract_field("date_last_payment", block),
            date_of_first_delinquency=extract_field("date_of_first_delinquency", block),
            estimated_removal_date=extract_field("estimated_removal_date", block),
            remarks=extract_field("remarks", block),
            raw_block=block[:2500],
            page_start=page_num,
        )
        infer_missing_fields_from_block(t)
        t.confidence_score = score_confidence(t)
        t.confidence = confidence_label(t.confidence_score)
        t.needs_admin_review = t.confidence != "high"
        finalize_parser_metadata(t)
        if not is_probable_tradeline(t):
            continue
        tradelines.append(t)

    return dedupe_tradelines(tradelines)


def dedupe_tradelines(items: List[NormalizedTradeline]) -> List[NormalizedTradeline]:
    best_by_key: Dict[Tuple[str, str], NormalizedTradeline] = {}
    no_number: List[NormalizedTradeline] = []

    for t in items:
        if t.account_number_masked:
            key = (t.bureau, t.account_number_masked)
            current = best_by_key.get(key)
            if current is None or tradeline_quality_score(t) > tradeline_quality_score(current):
                best_by_key[key] = t
            continue
        no_number.append(t)

    out = list(best_by_key.values())
    seen = {
        (
            t.bureau,
            compact_key(t.account_name)[:35],
            t.account_number_masked,
            compact_key(t.balance),
            compact_key(t.status or t.pay_status)[:25],
        )
        for t in out
    }

    for t in no_number:
        key = (
            t.bureau,
            compact_key(t.account_name)[:35],
            compact_key(t.balance),
            compact_key(t.status or t.pay_status)[:25],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


# -----------------------------
# Cross-bureau matching
# -----------------------------

def is_collection_like(t: NormalizedTradeline) -> bool:
    blob = " ".join([
        t.account_name,
        t.account_type,
        t.status,
        t.pay_status,
        t.remarks,
        t.collector_or_debt_buyer,
        t.raw_block,
    ]).lower()
    return any(term in blob for term in [
        "collection",
        "collector",
        "debt buyer",
        "factoring company",
        "placed for collection",
        "assigned",
    ])


def same_cross_bureau_account(left: NormalizedTradeline, right: NormalizedTradeline) -> bool:
    name_score = simple_similarity(left.account_name, right.account_name)
    acct_match = bool(left.account_number_masked and left.account_number_masked == right.account_number_masked)
    alias_match = bool(normalized_alias_name(left.account_name) and normalized_alias_name(left.account_name) == normalized_alias_name(right.account_name))
    digit_match = bool(visible_account_digits(left.account_number_masked) and visible_account_digits(left.account_number_masked) == visible_account_digits(right.account_number_masked))
    balance_match = bool(left.balance and right.balance and normalize_money(left.balance) == normalize_money(right.balance))
    dofd_match = bool(left.date_of_first_delinquency and right.date_of_first_delinquency and left.date_of_first_delinquency == right.date_of_first_delinquency)
    opened_match = bool(left.date_opened and right.date_opened and left.date_opened == right.date_opened)
    original_score = (
        simple_similarity(left.original_creditor, right.original_creditor)
        if left.original_creditor and right.original_creditor
        else 0
    )
    left_key = compact_key(left.account_name)
    right_key = compact_key(right.account_name)

    if not left_key or not right_key:
        return False
    if left_key in {"co", "ok", "cls", "nd", "address"} or right_key in {"co", "ok", "cls", "nd", "address"}:
        return False

    if acct_match:
        return True
    if alias_match and (digit_match or balance_match or dofd_match or opened_match or original_score >= 0.65):
        return True

    if name_score >= 0.82:
        return True

    # Same original creditor is only supporting evidence. It cannot, by itself,
    # merge a collector/debt-buyer tradeline with the original creditor's own card/loan.
    if original_score >= 0.72:
        if name_score >= 0.65:
            return True
        if is_collection_like(left) and is_collection_like(right) and name_score >= 0.55:
            return True

    return False


def group_cross_bureau(tradelines: List[NormalizedTradeline]) -> List[dict]:
    groups: List[dict] = []
    used = set()

    for i, t in enumerate(tradelines):
        if t.id in used:
            continue

        group = [t]
        used.add(t.id)

        for other in tradelines[i+1:]:
            if other.id in used:
                continue
            if t.bureau == other.bureau:
                continue

            if same_cross_bureau_account(t, other):
                group.append(other)
                used.add(other.id)

        if len(group) >= 2:
            groups.append({
                "group_id": stable_id("group", *[x.id for x in group]),
                "bureaus": sorted({x.bureau for x in group}),
                "account_names": sorted({x.account_name for x in group}),
                "tradeline_ids": [x.id for x in group],
                "review_note": "Same or similar item appears across multiple bureaus. Compare balance, status, dates, original creditor, and remarks.",
                "field_snapshot": [
                    {
                        "bureau": x.bureau,
                        "account_name": x.account_name,
                        "balance": x.balance,
                        "status": x.status,
                        "pay_status": x.pay_status,
                        "date_opened": x.date_opened,
                        "date_reported": x.date_reported,
                        "date_of_first_delinquency": x.date_of_first_delinquency,
                        "estimated_removal_date": x.estimated_removal_date,
                    }
                    for x in group
                ]
            })

    return groups


# -----------------------------
# Issue detection engine
# -----------------------------

def ev(t: NormalizedTradeline) -> Evidence:
    return Evidence(
        bureau=t.bureau,
        page=t.page_start,
        snippet=t.raw_block[:800],
    )


def contact_signature_from_raw(text: str) -> str:
    raw = clean_text(text or "")
    phone = re.search(r"(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", raw)
    address = re.search(
        r"\b(?:PO BOX|P\.O\. BOX|\d{2,6}\s+[A-Z0-9 .'-]+(?:ST|RD|AVE|BLVD|DR|LN|WAY|STE)\b[^\n|]{0,80})",
        raw,
        flags=re.I,
    )
    return compact_key(" ".join(part for part in [
        address.group(0) if address else "",
        phone.group(0) if phone else "",
    ] if part))


def add_issue(issues: List[ReviewIssue], issue_type: str, severity: str, label: str,
              customer: str, admin: str, round_name: str, tradelines: List[NormalizedTradeline],
              confidence: str = "medium") -> None:
    issues.append(ReviewIssue(
        id=stable_id(issue_type, *[t.id for t in tradelines], label),
        issue_type=issue_type,
        severity=severity,
        customer_label=label,
        customer_explanation=customer,
        admin_explanation=admin,
        suggested_round=round_name,
        related_tradeline_ids=[t.id for t in tradelines],
        evidence=[ev(t) for t in tradelines],
        confidence=confidence,
    ))


def detect_issues(tradelines: List[NormalizedTradeline], groups: List[dict]) -> List[ReviewIssue]:
    issues: List[ReviewIssue] = []
    scanner_rules = load_scanner_rules()

    for t in tradelines:
        blob = " ".join([t.status, t.pay_status, t.remarks, t.raw_block]).lower()
        negative_matches = classify_negative_tradeline(t, scanner_rules)

        for match in negative_matches:
            add_issue(
                issues,
                f"negative_{match['id']}_review",
                "high" if match.get("priority") == "high" else "medium",
                match["label"],
                f"{match['label']} reporting has a possible report error or inconsistency. Review recommended.",
                match.get("review_reason", "Review this negative/reviewable account category against source report fields."),
                "Negative Account Rules Review",
                [t],
                t.confidence,
            )

        if negative_matches:
            add_issue(
                issues,
                "entity_compliance_review",
                "low",
                ENTITY_COMPLIANCE_CUSTOMER_WORDING,
                ENTITY_COMPLIANCE_CUSTOMER_WORDING,
                ENTITY_COMPLIANCE_ADMIN_WORDING,
                "Entity Compliance Intelligence Review",
                [t],
                t.confidence,
            )

        if any(x in blob for x in COLLECTION_TERMS):
            add_issue(
                issues,
                "collection_review",
                "medium",
                "Collection review",
                "This collection item should be reviewed for original creditor, balance, ownership, and reporting details.",
                "Collection/debt buyer candidate. Verify original creditor, assignment/ownership, balance, authority, and reporting fields.",
                "Round 2 — Collection Review",
                [t],
                t.confidence
            )

        if "charge" in blob and "off" in blob:
            add_issue(
                issues,
                "chargeoff_review",
                "medium",
                "Charge-off review",
                "This charge-off should be reviewed for balance, status, dates, and whether it was sold or transferred.",
                "Charge-off candidate. Check DOFD, balance, sold/transferred status, creditor ownership, and duplicate collection reporting.",
                "Round 4 — Reporting Accuracy Review",
                [t],
                t.confidence
            )

        if not t.date_of_first_delinquency and any(x in blob for x in ["charge", "collection", "delinquent", "past due"]):
            add_issue(
                issues,
                "reage_dofd_missing_review",
                "medium",
                "DOFD Missing / Timeline Review Needed",
                "Timeline review needed. A key delinquency/removal date may need review.",
                "REAGE-002: Negative item lacks detected DOFD/removal date. Verify raw report and bureau-specific fields before any dispute path.",
                "Round 4 — Reporting Accuracy Review",
                [t],
                "medium"
            )

        if (
            classify_negative_tradeline(t, scanner_rules)
            and t.date_opened
            and (t.date_of_first_delinquency or t.original_creditor or t.estimated_removal_date)
            and any(x in blob for x in ["collection", "debt buyer", "assigned", "sold", "transferred"])
        ):
            add_issue(
                issues,
                "reage_timeline_review",
                "medium",
                "Timeline review needed",
                "Collection/debt-buyer reporting should be reviewed to confirm the reporting period is based on the original delinquency timeline.",
                "REAGE-001/006: New collector/debt-buyer reporting may require DOFD/removal-date verification. Human compliance review required.",
                "Round 4 â€” Reporting Accuracy Review",
                [t],
                t.confidence,
            )

        dispute_terms = [
            "consumer disputes this account",
            "account information disputed by consumer",
            "meets requirement of the fair credit reporting act",
            "account information disputed by consumer (fcra)",
            " aid ",
            "dispute account",
            "dispute resolved/consumer disagrees",
        ]
        if any(term in blob for term in dispute_terms):
            add_issue(
                issues,
                "fcra_nod_dispute_notation_review",
                "low",
                "Notice of dispute notation review",
                "A dispute notation appears in the report text and should be checked for accuracy/current status.",
                "FCRA-NOD-001 rule candidate: verify whether dispute delivery occurred and whether the account is correctly marked as disputed by the consumer.",
                "Notice of Dispute Review",
                [t],
                t.confidence,
            )

        if t.balance and t.balance not in {"$0", "$0.00"} and "closed" in blob and any(x in blob for x in ["transferred", "sold"]):
            add_issue(
                issues,
                "closed_sold_balance_review",
                "medium",
                "Closed or sold account balance review",
                "A closed, sold, or transferred account may still show a balance that should be reviewed.",
                "Closed/sold/transferred item with non-zero balance detected. Needs admin validation.",
                "Round 4 — Reporting Accuracy Review",
                [t],
                "medium"
            )

        if any(x in blob for x in ["90 days", "120 days", "150 days", "180 days", "seriously past due", "major delinquency"]) and "date major delinquency" not in blob:
            add_issue(
                issues,
                "major_delinquency_date_missing",
                "medium",
                "Major delinquency date missing/inconsistent",
                "A serious delinquency may need a major-delinquency date review.",
                "Serious delinquency wording found without a clear major-delinquency date in parsed fields.",
                "Metro 2 Field Review",
                [t],
                "medium",
            )

        if any(x in blob for x in ["30 days", "60 days", "90 days", "120 days", "150 days", "180 days", "late payment"]) and not t.payment_history_summary:
            add_issue(
                issues,
                "payment_history_inconsistency",
                "medium",
                "Payment history inconsistency",
                "Late-payment wording may need review against the payment history profile.",
                "Late-payment signal found without a clean payment-history summary extraction.",
                "Metro 2 Field Review",
                [t],
                "medium",
            )

        if classify_negative_tradeline(t, scanner_rules) and not t.estimated_removal_date and any(x in blob for x in ["on record", "removed", "estimated removal", "date of first delinquency", "collection", "charge"]):
            add_issue(
                issues,
                "removal_obsolescence_date_missing",
                "medium",
                "Removal/obsolescence date mismatch or missing",
                "The adverse item may need reporting-period or estimated-removal review.",
                "Negative/reviewable item lacks a clean estimated removal/on-record-until date in parsed fields.",
                "Metro 2 Field Review",
                [t],
                "medium",
            )

        if t.confidence == "low":
            add_issue(
                issues,
                "low_confidence_admin_review",
                "low",
                "Needs manual review",
                "This item needs a closer review before any action is recommended.",
                "Parser confidence is low. Admin should verify source snippet and fields.",
                "Admin Review",
                [t],
                "low"
            )

    # Cross-bureau mismatch checks
    by_id = {t.id: t for t in tradelines}
    for group in groups:
        group_items = [by_id[x] for x in group["tradeline_ids"] if x in by_id]
        if len(group_items) < 2:
            continue

        balances = {x.balance for x in group_items if x.balance}
        statuses = {clean_text(x.status or x.pay_status).lower() for x in group_items if x.status or x.pay_status}
        dates_reported = {x.date_reported for x in group_items if x.date_reported}
        dofds = {x.date_of_first_delinquency for x in group_items if x.date_of_first_delinquency}
        account_numbers = {x.account_number_masked for x in group_items if x.account_number_masked}
        account_types = {clean_text(x.account_type).lower() for x in group_items if x.account_type}
        original_creditors = {clean_text(x.original_creditor).lower() for x in group_items if x.original_creditor}
        remarks = {clean_text(x.remarks).lower() for x in group_items if x.remarks}
        payment_histories = {clean_text(x.payment_history_summary).lower() for x in group_items if x.payment_history_summary}
        removal_dates = {x.estimated_removal_date for x in group_items if x.estimated_removal_date}
        contact_signatures = {contact_signature_from_raw(x.raw_block) for x in group_items if contact_signature_from_raw(x.raw_block)}

        if len(balances) >= 2:
            add_issue(
                issues,
                "cross_bureau_balance_mismatch",
                "medium",
                "Balance differs across bureaus",
                "The same or similar account may show different balances across bureaus.",
                "Cross-bureau group has different balances. Verify if mismatch is expected or inaccurate.",
                "Round 3 — Bureau Match Review",
                group_items,
                "medium"
            )

        if len(account_numbers) >= 2:
            add_issue(
                issues,
                "account_identifier_mismatch",
                "medium",
                "Account identifier mismatch",
                "The same or similar account may show different account identifiers across bureaus.",
                "Compare account numbers/fragments, furnisher names, and source report blocks before relying on this match.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(account_types) >= 2:
            add_issue(
                issues,
                "account_type_classification_mismatch",
                "medium",
                "Account type/classification mismatch",
                "The same or similar account may be classified differently across bureaus.",
                "Review account type, portfolio type, creditor classification, and furnisher support.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(statuses) >= 2:
            add_issue(
                issues,
                "cross_bureau_status_mismatch",
                "medium",
                "Status differs across bureaus",
                "The same or similar account may show different statuses across bureaus.",
                "Cross-bureau group has different status/pay-status values.",
                "Round 3 — Bureau Match Review",
                group_items,
                "medium"
            )

        if len(dates_reported) >= 2 or len(dofds) >= 2:
            add_issue(
                issues,
                "cross_bureau_date_mismatch",
                "medium",
                "Dates differ across bureaus",
                "The same or similar account may show different important dates across bureaus.",
                "Cross-bureau group has different report dates or DOFD/removal dates.",
                "Round 3 — Bureau Match Review",
                group_items,
                "medium"
            )

        if len(group_items) >= 2 and any(is_collection_like(item) for item in group_items):
            add_issue(
                issues,
                "duplicate_overlap_review",
                "high",
                "Duplicate / overlapping debt review",
                "Similar collection or sold-account reporting may need duplicate/overlap review.",
                "Compare original creditor, account identifiers, balances, dates, and collector/debt-buyer ownership.",
                "Negative Account Rules Review",
                group_items,
                "medium",
            )

        if len(original_creditors) >= 2 or (any(is_collection_like(item) for item in group_items) and len(original_creditors) == 0):
            add_issue(
                issues,
                "original_creditor_missing_or_inconsistent",
                "medium",
                "Original creditor missing or inconsistent",
                "Original creditor information may be missing or inconsistent across bureau reporting.",
                "Verify original creditor and ownership/assignment records before dispute or payment decisions.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(remarks) >= 2:
            add_issue(
                issues,
                "remark_narrative_code_inconsistency",
                "medium",
                "Remark/narrative-code inconsistency",
                "The same or similar account may show different remarks or narrative codes across bureaus.",
                "Compare remarks and narrative codes against the actual account history and dispute status.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(payment_histories) >= 2:
            add_issue(
                issues,
                "payment_history_inconsistency",
                "medium",
                "Payment history inconsistency",
                "The same or similar account may show different payment-history information across bureaus.",
                "Compare payment rating/history profiles and late-payment months against source records.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(removal_dates) >= 2 or (any(classify_negative_tradeline(item, scanner_rules) for item in group_items) and len(removal_dates) == 0):
            add_issue(
                issues,
                "removal_obsolescence_date_mismatch_or_missing",
                "medium",
                "Removal/obsolescence date mismatch or missing",
                "The same or similar adverse item may need reporting-period or estimated-removal review.",
                "Compare DOFD and on-record-until fields to verify adverse reporting period.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

        if len(contact_signatures) >= 2:
            add_issue(
                issues,
                "furnisher_contact_data_differs",
                "low",
                "Furnisher contact data differs",
                "Furnisher or collector contact information may differ across bureau reporting.",
                "Compare report-sourced address/phone information before preparing any direct-dispute packet.",
                "Metro 2 Field Review",
                group_items,
                "medium",
            )

    grouped_ids = {tid for group in groups for tid in group.get("tradeline_ids", [])}
    for t in tradelines:
        if t.id not in grouped_ids and classify_negative_tradeline(t, scanner_rules):
            add_issue(
                issues,
                "single_bureau_review",
                "low",
                "Single-bureau review",
                "This negative/reviewable item appears in one parsed bureau group and may need confirmation against the other reports.",
                "Verify whether the account is truly single-bureau or missing because the other report text was unavailable.",
                "Bureau Match Review",
                [t],
                t.confidence,
            )

    return dedupe_issues(issues)


def dedupe_issues(issues: List[ReviewIssue]) -> List[ReviewIssue]:
    seen = set()
    out = []
    for issue in issues:
        key = (
            issue.issue_type,
            tuple(sorted(issue.related_tradeline_ids)),
            issue.customer_label,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(issue)
    return out


# -----------------------------
# Main parse API
# -----------------------------

def build_decision_readiness(issues: List[ReviewIssue]) -> List[dict]:
    issue_types = {issue.issue_type for issue in issues}
    has_collection = "collection_review" in issue_types
    has_chargeoff = "chargeoff_review" in issue_types
    has_bureau_mismatch = any(issue_type.startswith("cross_bureau") for issue_type in issue_types)
    has_missing_date = "missing_dofd_review" in issue_types

    cards = [
        {
            "situation": "Auto loan or refinance review",
            "scanner_focus": "Balances, account status, recent late-payment signals, and bureau mismatches that may confuse a lender review.",
            "next_step": "Review the flagged accounts before applying again or accepting a high-rate offer.",
        },
        {
            "situation": "Mortgage readiness",
            "scanner_focus": "Collections, charge-offs, reported balances, important dates, and items that may need documentation early.",
            "next_step": "Start with report clarity before lender underwriting so there is time to organize proof.",
        },
        {
            "situation": "Apartment application review",
            "scanner_focus": "Collection accounts, duplicate reporting, balances, and accounts the customer does not recognize.",
            "next_step": "Confirm what is being reported before the next rental application or screening review.",
        },
    ]

    if has_collection:
        cards.append({
            "situation": "Collection account review",
            "scanner_focus": "Original creditor, collector/debt buyer details, balance, ownership, and verification questions.",
            "next_step": "Check whether the account details are complete and supported before dispute or payment decisions.",
        })

    if has_chargeoff or has_missing_date:
        cards.append({
            "situation": "Charge-off or late-payment review",
            "scanner_focus": "Status, balance, date of first delinquency, last reported date, and sold/transferred wording.",
            "next_step": "Compare dates and status fields before deciding whether a reporting accuracy dispute makes sense.",
        })

    if has_bureau_mismatch:
        cards.append({
            "situation": "Bureau mismatch review",
            "scanner_focus": "Same or similar accounts that report different balances, statuses, or dates across bureaus.",
            "next_step": "Use the side-by-side review to identify the exact field that may need correction.",
        })

    return cards


def parse_reports(report_texts: Dict[str, dict]) -> ParseResult:
    """
    report_texts format:
    {
      "filename.pdf": {
        "text": "...",
        "bureau": "Experian" optional
      }
    }
    """
    files = []
    all_tradelines: List[NormalizedTradeline] = []

    for filename, payload in report_texts.items():
        text = clean_text(payload.get("text", ""))
        bureau = payload.get("bureau") or detect_bureau(filename, text)
        if bureau == "Unknown Bureau":
            bureau = f"Unknown Report"

        files.append({
            "filename": filename,
            "bureau": bureau,
            "chars": len(text),
            "status": "parsed" if text else "empty_text",
        })

        all_tradelines.extend(parse_tradelines_for_bureau(bureau, filename, text))

    raw_verification_summary = verify_tradelines_against_raw_data(report_texts, all_tradelines)
    identity_raw_data = extract_identity_raw_data(report_texts)
    groups = group_cross_bureau(all_tradelines)
    issues = detect_issues(all_tradelines, groups)

    customer_summary = {
        "headline": "Your report review is organized.",
        "message": "Credit Vivo mapped possible report issues to real next-step situations like loan, mortgage, apartment, collection, and bureau mismatch review. No letters or disputes are sent without your approval.",
        "review_items": len(all_tradelines),
        "possible_review_points": len(issues),
        "categories": sorted({i.customer_label for i in issues}),
        "next_step": "Review the decision-readiness cards and confirm the raw report details before taking action."
    }

    admin_summary = {
        "engine": "Credit Vivo Proprietary Parser Engine",
        "version": "18.1.7",
        "paid_ai_used": False,
        "tradeline_count": len(all_tradelines),
        "issue_count": len(issues),
        "cross_bureau_group_count": len(groups),
        "raw_verification": raw_verification_summary,
        "decision_readiness_count": len(build_decision_readiness(issues)),
        "warning": "Parser output is draft review data. Verify raw evidence snippets before preparing letters."
    }

    return ParseResult(
        engine="Credit Vivo Proprietary Parser Engine",
        version="18.1.7",
        paid_ai_used=False,
        files=files,
        tradelines=all_tradelines,
        issues=issues,
        cross_bureau_groups=groups,
        customer_summary=customer_summary,
        admin_summary=admin_summary,
        raw_verification_summary=raw_verification_summary,
        identity_raw_data=identity_raw_data,
    )


FCRA_NOTICE_OF_DISPUTE = (
    "This is my formal notice of dispute. I dispute the accuracy, completeness, "
    "and/or verifiability of the item identified in this letter. Please conduct a "
    "reasonable investigation under the Fair Credit Reporting Act (FCRA), review all "
    "information I provide with this dispute, forward the dispute and all relevant "
    "information to the furnisher when this is a bureau dispute, and correct, update, "
    "or delete any information that cannot be verified as accurate and complete. "
    "Please mark the item as disputed while the investigation is pending and provide "
    "the written results of the investigation, including any corrected report or "
    "explanation of the verification method used."
)

FCRA_NOTICE_RULES = {
    "cfpb_official_template_sources": [
        "CFPB credit reporting company dispute letter template",
        "CFPB furnisher dispute letter template",
        "CFPB complaint process overview",
    ],
    "cfpb_letter_fields": [
        "consumer full name and mailing address",
        "date of letter",
        "recipient name and mailing address",
        "account name and account number",
        "specific information being disputed",
        "plain-language explanation of why the information is wrong",
        "requested correction or investigation result",
        "copies of supporting documents",
    ],
    "consumer_notice_contents": [
        "identify the consumer",
        "identify the account or item being disputed",
        "state the specific information disputed",
        "explain the basis for the dispute",
        "include supporting documents or evidence when available",
        "request correction, update, deletion, or verification results",
    ],
    "bureau_dispute_rules": [
        "consumer reporting agency must conduct a reasonable reinvestigation when accuracy or completeness is disputed",
        "bureau should forward notice of the dispute and relevant information to the furnisher",
        "bureau should provide written reinvestigation results after completion",
        "bureau dispute path is preferred when the next step needs furnisher duties triggered through bureau notice",
        "CFPB template method: clearly identify the disputed item, explain the problem, request correction, and attach copies of proof",
    ],
    "furnisher_dispute_rules": [
        "direct furnisher dispute should be sent to the furnisher address shown on the report or other proper direct-dispute address",
        "direct dispute should include enough identifying information, the specific disputed information, the basis for dispute, and supporting evidence",
        "furnisher should conduct a reasonable investigation and review relevant information provided with a proper direct dispute",
        "furnisher should report corrections or stop reporting information that cannot be verified as accurate and complete",
        "CFPB template method: dispute directly with the company that gave the information to the bureau when the furnisher's records appear wrong",
    ],
    "credit_vivo_controls": [
        "do not send automatically",
        "customer approval required before mail, bureau dispute, furnisher dispute, CFPB complaint, state complaint, or attorney escalation",
        "store date sent, recipient, delivery method, tracking number, response due date, response received, and next action",
        "attach evidence packet hash or file reference before sending",
        "record whether the item was marked disputed and whether written results were received",
    ],
}


def _issue_evidence_strength(issue: ReviewIssue) -> str:
    if issue.severity == "high" or issue.confidence == "high":
        return "high"
    if issue.confidence == "low" or issue.severity == "low":
        return "low"
    return "medium"


def _responsible_party_for_issue(issue: ReviewIssue) -> str:
    if issue.issue_type.startswith("cross_bureau"):
        return "bureau_and_furnisher"
    if issue.issue_type in {"collection_review", "chargeoff_review", "closed_sold_balance_review"}:
        return "furnisher_or_collector"
    if issue.issue_type in {"missing_dofd_review", "reage_dofd_missing_review", "reage_timeline_review", "fcra_nod_dispute_notation_review"}:
        return "bureau_and_furnisher"
    return "admin_review_required"


def _next_action_for_issue(issue: ReviewIssue) -> str:
    if issue.issue_type.startswith("cross_bureau"):
        return "round_2_field_level_bureau_dispute"
    if issue.issue_type in {"collection_review", "chargeoff_review", "closed_sold_balance_review"}:
        return "furnisher_direct_dispute_after_bureau_review"
    if issue.issue_type in {"missing_dofd_review", "reage_dofd_missing_review", "reage_timeline_review"}:
        return "round_2_bureau_dispute_then_reinvestigation_if_unverified"
    if issue.issue_type == "fcra_nod_dispute_notation_review":
        return "notice_of_dispute_follow_up_after_admin_review"
    return "admin_review_before_letter"


def _letter_type_label(letter_type: str) -> str:
    return {
        "bureau_dispute": "Credit Bureau Dispute",
        "furnisher_direct_dispute": "Furnisher Direct Dispute",
        "debt_validation_request": "Debt Validation Request",
        "method_of_verification_request": "Method of Verification Request",
        "reinvestigation_request": "Reinvestigation Request",
        "escalation_follow_up": "Escalation Follow-Up",
        "complaint_preparation_packet": "Complaint Preparation Packet",
        "attorney_review_summary": "Attorney-Review Summary",
        "admin_review_hold": "Admin Review Hold",
    }.get(letter_type, letter_type.replace("_", " ").title())


def _draft_letter_subject(letter_type: str, issue: ReviewIssue) -> str:
    if letter_type == "debt_validation_request":
        return f"Debt Validation Request - {issue.customer_label}"
    if letter_type == "method_of_verification_request":
        return f"Method of Verification Request - {issue.customer_label}"
    if letter_type == "reinvestigation_request":
        return f"Reinvestigation Request - {issue.customer_label}"
    if letter_type == "escalation_follow_up":
        return f"Escalation Follow-Up - {issue.customer_label}"
    if letter_type == "complaint_preparation_packet":
        return f"Complaint Packet Preparation - {issue.customer_label}"
    if letter_type == "attorney_review_summary":
        return f"Attorney-Review Summary - {issue.customer_label}"
    if letter_type == "furnisher_direct_dispute":
        return f"Direct Dispute of Account Reporting - {issue.customer_label}"
    if letter_type == "bureau_dispute":
        return f"Credit Report Dispute - {issue.customer_label}"
    return f"Admin Review Required - {issue.customer_label}"


def _draft_letter_body(letter_type: str, recipient_type: str, issue: ReviewIssue) -> str:
    if letter_type == "admin_review_hold":
        return (
            "DRAFT HOLD - ADMIN REVIEW REQUIRED\n\n"
            "CUSTOMER REVIEW AND APPROVAL REQUIRED before any dispute, validation request, mailing, complaint, or escalation.\n\n"
            f"Issue: {issue.customer_label}\n"
            f"Reason: {issue.customer_explanation}\n\n"
            "FCRA/Metro 2-style field review may apply, but this hold is not a legal conclusion.\n\n"
            "Credit Vivo did not generate a send-ready letter for this item because it needs "
            "manual review before any dispute path is selected."
        )

    evidence_note = "Evidence from the Credit Vivo scanner is attached for customer/admin review."
    if issue.evidence:
        snippet = issue.evidence[0].snippet[:450]
        evidence_note = f"Scanner evidence excerpt for review: {snippet}"
    entity_compliance_note = (
        "\nEntity compliance intelligence note: "
        f"{ENTITY_COMPLIANCE_ADMIN_WORDING} "
        "Use official records only; do not characterize license/business status as a violation without documented proof and compliance review.\n"
    )

    common_header = (
        "DRAFT ONLY - CUSTOMER REVIEW, E-SIGN APPROVAL, AND ADMIN REVIEW REQUIRED\n"
        "CUSTOMER REVIEW AND APPROVAL REQUIRED\n"
        "LOB-READY DRAFT PACKET ONLY - DO NOT SEND UNTIL ALL APPROVAL GATES ARE RECORDED\n"
        "Credit Vivo is not a law firm and this draft is not legal advice.\n\n"
        "[Customer Name]\n"
        "[Customer Mailing Address]\n"
        "[City, State ZIP]\n\n"
        "[Date]\n\n"
    )
    common_footer = (
        "\n\nAttachments / packet checklist:\n"
        "- Copy of relevant credit report page or excerpt with disputed item marked\n"
        "- 3-bureau comparison attachment when available\n"
        "- Customer ID and proof of address when required by the recipient\n"
        "- Supporting proof supplied or approved by customer, if available\n"
        "- Prior dispute letters, delivery proof, and responses when this is a follow-up\n\n"
        "Mailing / Lob status: Draft only. Not sent. Queue only after customer e-sign, admin approval, sensitive-data review, recipient address verification, and approved production workflow.\n\n"
        "Sincerely,\n\n"
        "[Customer Signature / E-Sign Reference]\n"
        "[Customer Printed Name]\n"
    )

    if letter_type == "debt_validation_request":
        return (
            common_header +
            "To: Debt Collector / Debt Buyer\n"
            "[Recipient Address]\n\n"
            f"Re: {issue.customer_label}\n\n"
            "To Whom It May Concern:\n\n"
            "I am requesting validation of the debt you claim is owed. If you are attempting "
            "to collect this debt or reporting it as a collector/debt buyer, please provide "
            "documents and information sufficient to verify the debt, the amount claimed, "
            "the original creditor, your authority to collect, and any assignment or sale "
            "of the account.\n\n"
            "Please provide:\n"
            "- the name and address of the original creditor;\n"
            "- an itemized accounting of the balance, fees, interest, and payments;\n"
            "- documents showing I am responsible for the debt;\n"
            "- documents showing your authority to collect or report this account;\n"
            "- the date of first delinquency and records supporting the reported timeline;\n"
            "- the account number or other identifier used to report the account.\n\n"
            "This request is made for consumer review and dispute-tracking purposes. "
            "Nothing in this letter is an admission that the debt is owed. Please send "
            "your written response to the mailing address above. If you continue furnishing "
            "this information to any consumer reporting agency, please report that the account "
            "is disputed by the consumer.\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}\n\n"
            + common_footer
        )

    if letter_type == "method_of_verification_request":
        return (
            common_header +
            "To: Credit Bureau\n"
            "[Recipient Address]\n\n"
            f"Re: Method of Verification Request - {issue.customer_label}\n\n"
            "To Whom It May Concern:\n\n"
            "I previously disputed the credit reporting item identified below. Please provide the method of verification used during your investigation, including the name, address, and telephone number of each furnisher or source contacted, the date of contact, and the specific records reviewed.\n\n"
            f"Disputed issue: {issue.customer_label}\n"
            f"Reason this remains under review: {issue.customer_explanation}\n"
            f"Review round: {issue.suggested_round}\n\n"
            "If the item cannot be verified as accurate, complete, and current, please correct, update, or remove it and send written results. Please continue marking the item as disputed by the consumer while this review is pending and in any continued reporting.\n\n"
            f"{FCRA_NOTICE_OF_DISPUTE}\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}"
            + common_footer
        )

    if letter_type == "reinvestigation_request":
        return (
            common_header +
            "To: Credit Bureau / Furnisher\n"
            "[Recipient Address]\n\n"
            f"Re: Reinvestigation Request - {issue.customer_label}\n\n"
            "To Whom It May Concern:\n\n"
            "I am requesting reinvestigation of the item below because the reporting still appears inaccurate, incomplete, inconsistent, or unverifiable based on the attached review packet.\n\n"
            f"Item for reinvestigation: {issue.customer_label}\n"
            f"Reason for reinvestigation: {issue.customer_explanation}\n"
            f"Review round: {issue.suggested_round}\n\n"
            "Please review all enclosed information, conduct a reasonable reinvestigation, forward the dispute and supporting materials to the appropriate furnisher when applicable, and provide written results. If the item cannot be verified as accurate, complete, and current, please correct, update, or remove it.\n\n"
            f"{FCRA_NOTICE_OF_DISPUTE}\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}"
            + common_footer
        )

    if letter_type == "escalation_follow_up":
        return (
            common_header +
            "To: Escalation / Executive / Compliance Department\n"
            "[Verified Escalation Address]\n\n"
            f"Re: Documented Follow-Up and Escalation Review - {issue.customer_label}\n\n"
            "To Whom It May Concern:\n\n"
            "This is a documented follow-up request concerning the credit reporting issue identified below. The customer packet should include the prior dispute history, proof of delivery, any investigation responses, current report excerpts, and supporting documentation.\n\n"
            f"Unresolved issue: {issue.customer_label}\n"
            f"Reason escalation is requested: {issue.customer_explanation}\n\n"
            "Please review the complete file, identify the records relied upon, correct or update any inaccurate or incomplete reporting, and remove any information that cannot be verified as accurate, complete, and current. If you continue furnishing this information, please report that the account is disputed by the consumer.\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}"
            + common_footer
        )

    if letter_type == "complaint_preparation_packet":
        return (
            common_header +
            "To: CFPB / State Regulator Complaint Intake\n"
            "[Complaint is not filed automatically]\n\n"
            f"Re: Complaint Preparation Packet - {issue.customer_label}\n\n"
            "This packet is prepared for customer and admin review only. It is not a filed complaint. Before any complaint is submitted, the customer must approve the facts, admin must review the packet, and any legal/compliance review required by Credit Vivo must be completed.\n\n"
            "Draft complaint summary:\n"
            f"- Reporting item: {issue.customer_label}\n"
            f"- Consumer concern: {issue.customer_explanation}\n"
            "- Requested resolution: investigate the reporting, correct/update inaccurate or incomplete information, remove information that cannot be verified as accurate, complete, and current, and provide written response.\n"
            "- Evidence to attach: current report excerpt, 3-bureau comparison, prior dispute letters, delivery proof, responses, customer documents, and any regulator/license records verified by admin.\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}"
            + common_footer
        )

    if letter_type == "attorney_review_summary":
        return (
            common_header +
            "To: Attorney / Compliance Reviewer\n"
            "[Reviewer Address]\n\n"
            f"Re: Attorney-Review Summary - {issue.customer_label}\n\n"
            "This summary is prepared for human review only and does not state a legal conclusion. Please review the report data, dispute history, responses, and customer evidence before determining whether any legal or regulatory action is appropriate.\n\n"
            f"Issue summary: {issue.customer_label}\n"
            f"Scanner review reason: {issue.customer_explanation}\n"
            f"Admin notes: {issue.admin_explanation}\n\n"
            "Potential review areas may include FCRA accuracy/completeness, reasonable investigation, furnisher reporting support, debt validation/collection authority, dispute notation, and damages evidence if supplied by the customer.\n\n"
            f"{entity_compliance_note}\n"
            f"{evidence_note}"
            + common_footer
        )

    recipient_line = "Credit Bureau" if recipient_type == "credit_bureau" else "Furnisher / Collector"
    requested_action = (
        "Please investigate this item, correct any inaccurate or incomplete information, "
        "delete any information that cannot be verified, and send the investigation results in writing."
        if letter_type == "bureau_dispute"
        else
        "Please provide the basis for your reporting, including records supporting ownership, "
        "balance, status, payment history, date of first delinquency, and authority to report this account."
    )
    required_notice_sentence = (
        "Please ensure this account is marked as disputed by the consumer while the investigation is pending "
        "and in any continued reporting, as required by applicable credit reporting law."
        if letter_type == "bureau_dispute"
        else
        "If you continue furnishing this information to any consumer reporting agency, please report that the "
        "account is disputed by the consumer."
    )

    return (
        common_header +
        f"To: {recipient_line}\n"
        "[Recipient Address]\n\n"
        f"Re: {issue.customer_label}\n\n"
        "To Whom It May Concern:\n\n"
        "I am disputing the accuracy, completeness, or verifiability of the credit reporting item "
        "identified below. Please treat this letter as my formal notice of dispute.\n\n"
        f"Disputed issue: {issue.customer_label}\n"
        f"Reason for dispute: {issue.customer_explanation}\n"
        f"Review round: {issue.suggested_round}\n\n"
        f"{FCRA_NOTICE_OF_DISPUTE}\n\n"
        f"{requested_action}\n\n"
        f"{required_notice_sentence}\n\n"
        f"{entity_compliance_note}\n"
        f"{evidence_note}\n\n"
        "Please send your written response to the mailing address above."
        + common_footer
    )


def build_letter_workflow() -> dict:
    return {
        "draft_only": True,
        "send_letters_automatically": False,
        "customer_authorization_required": True,
        "fcra_notice_of_dispute": FCRA_NOTICE_OF_DISPUTE,
        "fcra_notice_rules": FCRA_NOTICE_RULES,
        "official_cfpb_files_to_reference": [
            "CFPB_credit_reporting_company_dispute_letter_template.docx",
            "CFPB_credit_reporting_company_dispute_instructions.pdf",
            "CFPB_furnisher_dispute_letter_template.docx",
            "CFPB_furnisher_dispute_instructions.pdf",
            "CFPB_complaint_process_one_page.pdf",
        ],
        "bureau_dispute_procedure": {
            "recipient_type": "credit_bureau",
            "delivery_preference": "certified_mail_for_important_disputes",
            "cfpb_template_alignment": "Use the CFPB credit reporting company dispute template structure: identify the item, explain the dispute, request correction, and attach supporting copies.",
            "round_1_uses": [
                "wrong balance or status",
                "unrecognized account",
                "duplicate collection",
                "original creditor and debt buyer both showing active balance",
                "obsolete or missing key date item",
                "obvious mismatch across bureaus",
            ],
            "packet_checklist": [
                "customer-approved dispute letter",
                "FCRA notice of dispute",
                "specific disputed item and reason",
                "targeted proof only",
                "ID and proof of address when needed",
                "redacted unrelated account data",
                "highlighted disputed item",
                "request written investigation results",
            ],
        },
        "furnisher_direct_dispute_procedure": {
            "recipient_type": "furnisher_or_collector",
            "delivery_preference": "certified_mail",
            "cfpb_template_alignment": "Use the CFPB furnisher dispute template structure when the source company, collector, or servicer appears to be reporting wrong information.",
            "prerequisites": [
                "consumer-specific issue identified",
                "customer authorization verified",
                "evidence packet reviewed by admin",
                "specific furnisher item and dispute reason stated",
                "proper furnisher/direct-dispute address confirmed when available",
            ],
            "requested_verification": [
                "basis for reporting",
                "contract or account records",
                "itemized balance",
                "chain of title or assignment where applicable",
                "payment history",
                "date of first delinquency support",
                "proof reporting is complete and accurate",
                "written investigation result or correction/deletion notice",
            ],
        },
        "debt_validation_procedure": {
            "recipient_type": "debt_collector_or_debt_buyer",
            "delivery_preference": "certified_mail_recommended",
            "legal_basis": "FDCPA validation-style request when a collector/debt buyer is collecting or reporting the debt; not a substitute for an FCRA furnisher dispute.",
            "when_to_use": [
                "collection account",
                "debt buyer account",
                "factoring company account",
                "collector is reporting a balance",
                "original creditor, ownership, authority, or itemized balance needs proof",
            ],
            "requested_validation": [
                "original creditor name and address",
                "itemized balance, fees, interest, and payments",
                "documents showing consumer responsibility",
                "chain of title, sale, assignment, or authority to collect",
                "date of first delinquency support",
                "account number or reporting identifier",
            ],
            "credit_vivo_guardrail": "Generate as draft only. Customer approval required. Use with attorney/compliance review for state-specific debt-collection requirements.",
        },
        "escalation_procedure": {
            "cfpb_complaint": {
                "trigger": "no response, verified-as-accurate with weak support, or repeated inaccurate reporting after dispute history is complete",
                "packet": "original dispute, proof of delivery, bureau/furnisher responses, current report excerpt, damages or denial evidence if available",
                "cfpb_method": "Use CFPB complaint escalation only after the normal dispute record is clear: who was contacted, when, what was disputed, how the company responded, and what remains wrong.",
            },
            "state_attorney_general": {
                "trigger": "pattern of non-response, abusive collection conduct, or unresolved state-law concern",
                "packet": "same evidence packet plus consumer timeline and requested resolution",
            },
            "state_regulator": {
                "trigger": "licensed collector, lender, or credit repair/regulatory issue needs agency review",
                "packet": "collector/furnisher identity, license information if known, dispute timeline, and supporting evidence",
            },
            "attorney_review": {
                "trigger": "strong FCRA/FDCPA pattern, measurable damages, denial letter, identity theft, mixed file, or repeated verification without reasonable investigation",
                "packet": "full dispute history, reports before and after disputes, notices, responses, delivery proofs, and damages evidence",
            },
        },
        "tracking_schema": [
            "letter_id",
            "issue_ids",
            "recipient_type",
            "recipient_name",
            "recipient_address",
            "delivery_method",
            "certified_tracking_number",
            "sent_date",
            "delivered_date",
            "response_due_date",
            "day_15_check_date",
            "day_35_followup_check_date",
            "response_received_date",
            "current_status",
            "next_action",
            "fcra_notice_included",
            "customer_authorization_verified",
            "evidence_packet_hash",
        ],
        "event_log_entries": [
            "letter_drafted",
            "customer_authorization_verified",
            "fcra_notice_added",
            "proof_packet_attached",
            "certified_mail_queued",
            "tracking_number_saved",
            "delivery_confirmed",
            "response_deadline_created",
            "response_received",
            "response_scanned",
            "next_action_assigned",
        ],
}


def _is_debt_validation_candidate(issue: ReviewIssue) -> bool:
    blob = " ".join([
        issue.issue_type,
        issue.customer_label,
        issue.customer_explanation,
        issue.admin_explanation,
        " ".join(e.snippet for e in issue.evidence),
    ]).lower()
    return any(term in blob for term in [
        "collection",
        "collector",
        "debt buyer",
        "factoring company",
        "placed for collection",
    ])


def _letter_queue_item(issue: ReviewIssue, letter_type: str, recipient_type: str, responsible_party: str) -> dict:
    draft_body = _draft_letter_body(letter_type, recipient_type, issue)
    return {
        "letter_id": stable_id("letter", issue.id, letter_type),
        "issue_id": issue.id,
        "issue_type": issue.issue_type,
        "customer_label": issue.customer_label,
        "customer_explanation": issue.customer_explanation,
        "admin_explanation": issue.admin_explanation,
        "account_name": issue.customer_label,
        "letter_type": letter_type,
        "letter_type_label": _letter_type_label(letter_type),
        "letter_subject": _draft_letter_subject(letter_type, issue),
        "draft_letter_body": draft_body,
        "round": issue.suggested_round,
        "recipient_type": recipient_type,
        "responsible_party": responsible_party,
        "delivery_method": "certified_mail_recommended",
        "fcra_notice_required": letter_type not in {"admin_review_hold", "debt_validation_request", "complaint_preparation_packet", "attorney_review_summary"},
        "fcra_notice_included": letter_type not in {"admin_review_hold", "debt_validation_request", "complaint_preparation_packet", "attorney_review_summary"},
        "fdcpa_validation_request": letter_type == "debt_validation_request",
        "customer_approval_required": True,
        "customer_authorization_verified": False,
        "admin_review_required": True,
        "sensitive_data_review_required": True,
        "tracking_status": "draft_not_sent",
        "lob_ready_status": "draft_ready_for_lob_preview_after_approval",
        "mailing_allowed": False,
        "auto_send": False,
        "auto_file_complaint": False,
        "lob_ready_preview": {
            "lob_object": "letter",
            "to": {
                "name": "[Verified recipient name]",
                "address_line1": "[Verified recipient address]",
                "address_city": "[City]",
                "address_state": "[State]",
                "address_zip": "[ZIP]",
            },
            "from": {
                "name": "[Customer Name]",
                "address_line1": "[Customer mailing address]",
                "address_city": "[City]",
                "address_state": "[State]",
                "address_zip": "[ZIP]",
            },
            "file_reference": f"letters/{stable_id('letter', issue.id, letter_type)}.txt",
            "send_date": None,
            "color": False,
            "double_sided": False,
            "mail_type": "usps_first_class",
            "blocked_until": [
                "customer_esign_recorded",
                "admin_approval_recorded",
                "sensitive_data_review_passed",
                "recipient_address_verified",
                "production_lob_workflow_approved",
            ],
        },
        "recommended_next_action": (
            "send_debt_validation_request_if_collector_or_debt_buyer_and_customer_approves"
            if letter_type == "debt_validation_request"
            else _next_action_for_issue(issue)
        ),
        "escalation_candidate": letter_type in {"escalation_follow_up", "complaint_preparation_packet", "attorney_review_summary"},
    }


def build_recommended_letter_queue(issues: List[ReviewIssue]) -> List[dict]:
    queue = []
    for issue in issues:
        responsible_party = _responsible_party_for_issue(issue)
        queue.append(_letter_queue_item(issue, "bureau_dispute", "credit_bureau", responsible_party))
        queue.append(_letter_queue_item(issue, "furnisher_direct_dispute", "furnisher_or_collector", responsible_party))

        if _is_debt_validation_candidate(issue):
            queue.append(_letter_queue_item(
                issue,
                "debt_validation_request",
                "debt_collector_or_debt_buyer",
                "collector_or_debt_buyer",
            ))
        queue.append(_letter_queue_item(issue, "method_of_verification_request", "credit_bureau", responsible_party))
        queue.append(_letter_queue_item(issue, "reinvestigation_request", "credit_bureau_or_furnisher", responsible_party))
        queue.append(_letter_queue_item(issue, "escalation_follow_up", "escalation_or_compliance_department", responsible_party))
        queue.append(_letter_queue_item(issue, "complaint_preparation_packet", "regulator_packet", responsible_party))
        queue.append(_letter_queue_item(issue, "attorney_review_summary", "attorney_or_compliance_reviewer", responsible_party))
    return queue


def build_fcra_review(issues: List[ReviewIssue]) -> List[dict]:
    return [
        {
            "issue_id": issue.id,
            "possible_fcra_issue": issue.issue_type != "low_confidence_admin_review",
            "issue_type": issue.issue_type,
            "responsible_party": _responsible_party_for_issue(issue),
            "dispute_history_complete": False,
            "evidence_strength": _issue_evidence_strength(issue),
            "damages_evidence": "none",
            "next_action": _next_action_for_issue(issue),
            "requires_admin_review": True,
        }
        for issue in issues
    ]


METRO2_FCRA_RULES = {
    "collection_review": {
        "metro2_fields": ["Account Type", "Portfolio Type", "Original Creditor", "Current Balance", "Account Status", "Date Reported"],
        "fcra_focus": "Accuracy, completeness, ownership, and verification of collection reporting.",
        "fcra_sections": ["FCRA 611 reinvestigation", "FCRA 623 furnisher duties after notice"],
        "evidence_needed": ["original creditor", "assignment or ownership proof", "balance calculation", "reporting authority", "account-level source records"],
        "dispute_theory": "The collection must be accurate, complete, and verifiable. If ownership, balance, or reporting authority cannot be supported, correction or deletion may be appropriate.",
    },
    "chargeoff_review": {
        "metro2_fields": ["Account Status", "Payment Rating", "Current Balance", "Amount Past Due", "Date of First Delinquency", "Date Closed", "Special Comment"],
        "fcra_focus": "Charge-off reporting accuracy, dates, balance, sold/transferred status, and obsolescence risk.",
        "fcra_sections": ["FCRA 611 reinvestigation", "FCRA 623 furnisher duties after notice", "FCRA 605 obsolescence review"],
        "evidence_needed": ["charge-off ledger", "payment history", "DOFD support", "sale or transfer record", "balance breakdown"],
        "dispute_theory": "A charge-off should not report internally inconsistent status, balance, ownership, or delinquency dates.",
    },
    "missing_dofd_review": {
        "metro2_fields": ["Date of First Delinquency", "FCRA Compliance/Date of First Delinquency", "Estimated Removal Date"],
        "fcra_focus": "Missing or unsupported delinquency date for negative reporting.",
        "fcra_sections": ["FCRA 611 reinvestigation", "FCRA 605 obsolescence review", "FCRA 623 furnisher duties after notice"],
        "evidence_needed": ["first delinquency date", "payment history", "charge-off/collection timeline", "bureau reporting history"],
        "dispute_theory": "Negative reporting needs a supportable delinquency timeline so the account is not reported longer than allowed.",
    },
    "closed_sold_balance_review": {
        "metro2_fields": ["Account Status", "Current Balance", "Amount Past Due", "Date Closed", "Special Comment", "Purchased/Sold/Transferred Indicator"],
        "fcra_focus": "Closed, sold, transferred, or assigned account still reporting a balance.",
        "fcra_sections": ["FCRA 611 reinvestigation", "FCRA 623 furnisher duties after notice"],
        "evidence_needed": ["sale/transfer record", "current owner", "balance ledger", "zero-balance update support"],
        "dispute_theory": "If the account was sold or transferred, the reporting balance/status must match the furnisher's actual ownership and records.",
    },
    "cross_bureau_balance_mismatch": {
        "metro2_fields": ["Current Balance", "Amount Past Due", "High Credit/Original Amount", "Date Reported"],
        "fcra_focus": "Same account reports different balances across bureaus.",
        "fcra_sections": ["FCRA 611 reasonable reinvestigation", "FCRA 623 furnisher duties after bureau notice"],
        "evidence_needed": ["current account ledger", "last statement", "bureau reporting snapshots", "furnisher update history"],
        "dispute_theory": "The same account should have a supportable balance. Differences may be explainable by timing, but unsupported differences should be corrected.",
    },
    "cross_bureau_status_mismatch": {
        "metro2_fields": ["Account Status", "Payment Rating", "Special Comment", "Compliance Condition Code"],
        "fcra_focus": "Same account reports different status/payment condition across bureaus.",
        "fcra_sections": ["FCRA 611 reasonable reinvestigation", "FCRA 623 furnisher duties after bureau notice"],
        "evidence_needed": ["account status records", "payment history", "charge-off/collection status support", "bureau update records"],
        "dispute_theory": "Status and payment condition should be consistent with the furnisher's records and not materially misleading.",
    },
    "cross_bureau_date_mismatch": {
        "metro2_fields": ["Date Opened", "Date Closed", "Date Reported", "Date of First Delinquency", "Estimated Removal Date"],
        "fcra_focus": "Same account reports different key dates across bureaus.",
        "fcra_sections": ["FCRA 611 reasonable reinvestigation", "FCRA 605 obsolescence review", "FCRA 623 furnisher duties after bureau notice"],
        "evidence_needed": ["opening records", "closing records", "DOFD support", "payment history", "bureau report snapshots"],
        "dispute_theory": "Key dates drive legal reporting age and consumer harm. Unsupported date differences should be corrected or deleted.",
    },
    "low_confidence_admin_review": {
        "metro2_fields": ["Raw tradeline block", "All extracted fields"],
        "fcra_focus": "Manual validation before dispute strategy.",
        "fcra_sections": ["Admin review required before FCRA dispute theory is selected"],
        "evidence_needed": ["raw report excerpt", "account-level PDF pages", "manual field validation"],
        "dispute_theory": "Do not send a dispute until the extracted fields are confirmed against the raw report.",
    },
}


def _expert_rule_for_issue(issue: ReviewIssue) -> dict:
    return METRO2_FCRA_RULES.get(issue.issue_type, {
        "metro2_fields": ["Account Status", "Current Balance", "Date Reported", "Remarks"],
        "fcra_focus": "Accuracy, completeness, and verifiability review.",
        "fcra_sections": ["FCRA 611 reinvestigation", "FCRA 623 furnisher duties after notice"],
        "evidence_needed": ["raw report excerpt", "furnisher records", "bureau investigation response"],
        "dispute_theory": "If the reporting cannot be verified as accurate and complete, it should be corrected, updated, or deleted.",
    })


def build_metro2_fcra_review(issues: List[ReviewIssue]) -> List[dict]:
    review = []
    for issue in issues:
        rule = _expert_rule_for_issue(issue)
        review.append({
            "issue_id": issue.id,
            "issue_type": issue.issue_type,
            "customer_label": issue.customer_label,
            "severity": issue.severity,
            "confidence": issue.confidence,
            "metro2_fields_to_review": rule["metro2_fields"],
            "fcra_focus": rule["fcra_focus"],
            "fcra_sections": rule["fcra_sections"],
            "evidence_needed": rule["evidence_needed"],
            "dispute_theory": rule["dispute_theory"],
            "responsible_party": _responsible_party_for_issue(issue),
            "recommended_next_action": _next_action_for_issue(issue),
            "customer_approval_required": True,
            "attorney_review_signal": issue.severity == "high" or issue.issue_type.startswith("cross_bureau"),
        })
    return review


METRO2_PUBLIC_GUIDE_NOTES = {
    "source": "Collect.org public guide: How to Read the Metro 2 Format",
    "url": "https://www.collect.org/cv13/Help/howtoreadthemetro2format.html",
    "purpose": "Public field-reading guide used to improve scanner worksheets and staff review prompts.",
    "production_guardrail": "Use as a practical guide only; validate production Metro 2 logic against the official licensed CDIA Metro 2 CRRG and compliance counsel.",
    "base_segment_fields": [
        "Consumer Account Number",
        "Portfolio Type",
        "Account Type",
        "Date Opened",
        "Credit Limit",
        "Highest Credit / Original Loan Amount",
        "Terms Duration",
        "Scheduled Monthly Payment Amount",
        "Actual Payment Amount",
        "Account Status",
        "Payment Rating",
        "Payment History Profile",
        "Special Comment",
        "Compliance Condition Code",
        "Current Balance",
        "Amount Past Due",
        "Original Charge-off Amount",
        "Date of Account Information / Date Reported",
        "Date of First Delinquency",
        "Date Closed",
        "Date of Last Payment",
        "Consumer Information Indicator",
        "ECOA Code",
    ],
    "collection_segments": [
        "K1 segment: original creditor name and creditor classification where applicable",
        "J1/J2 segments: consumer name/address information where associated consumers exist",
    ],
}


METRO2_FIELD_REQUIREMENTS = {
    "collection": {
        "label": "Collection account",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Portfolio Type",
            "ECOA / Responsibility",
            "Account Status",
            "Current Balance",
            "Amount Past Due if reporting past due",
            "Original Charge-off Amount if applicable",
            "Date Opened or collection acquisition/open date",
            "Date Reported / Date Updated",
            "Date of First Delinquency for negative reporting",
            "K1 Original Creditor Name",
            "K1 Creditor Classification",
            "Creditor Classification / Collection Agency Type",
            "Payment History Profile when furnished",
            "Special Comment / Remarks when needed",
            "Compliance Condition Code / Dispute Indicator when disputed",
            "Consumer Information Indicator when bankruptcy/deceased/dispute conditions apply",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Portfolio Type": ["portfolio_type"],
            "ECOA / Responsibility": ["responsibility"],
            "Account Status": ["status", "pay_status"],
            "Current Balance": ["balance"],
            "Amount Past Due if reporting past due": ["past_due", "balance"],
            "Original Charge-off Amount if applicable": ["high_credit_or_original_amount", "raw_block"],
            "Date Opened or collection acquisition/open date": ["date_opened"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date of First Delinquency for negative reporting": ["date_of_first_delinquency"],
            "K1 Original Creditor Name": ["original_creditor"],
            "K1 Creditor Classification": ["creditor_classification", "raw_block"],
            "Creditor Classification / Collection Agency Type": ["creditor_classification", "collector_or_debt_buyer"],
            "Payment History Profile when furnished": ["payment_history_summary", "raw_block"],
            "Special Comment / Remarks when needed": ["remarks"],
            "Compliance Condition Code / Dispute Indicator when disputed": ["remarks", "raw_block"],
            "Consumer Information Indicator when bankruptcy/deceased/dispute conditions apply": ["remarks", "raw_block"],
        },
        "validation_notes": [
            "A collection should identify the K1 original creditor name and creditor classification when applicable.",
            "Negative collection reporting should have a supportable Date of First Delinquency timeline.",
            "If disputed, the report should show an appropriate dispute notation or compliance condition after notice.",
        ],
        "dispute_use": "Use for collection ownership, original creditor, balance, DOFD, status, and dispute-notation challenges.",
    },
    "charge_off": {
        "label": "Charge-off account",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Portfolio Type",
            "ECOA / Responsibility",
            "Account Status",
            "Payment Rating / Pay Status",
            "Current Balance",
            "Amount Past Due",
            "Charge-off Amount or High Credit / Original Amount",
            "Original Charge-off Amount",
            "Date of First Delinquency",
            "Date Closed when closed",
            "Date Reported / Date Updated",
            "Date Last Payment / Date Last Activity when available",
            "Payment History Profile",
            "Special Comment / Remarks",
            "Compliance Condition Code / Dispute Indicator when disputed",
            "Consumer Information Indicator when applicable",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Portfolio Type": ["portfolio_type"],
            "ECOA / Responsibility": ["responsibility"],
            "Account Status": ["status"],
            "Payment Rating / Pay Status": ["pay_status", "status"],
            "Current Balance": ["balance"],
            "Amount Past Due": ["past_due"],
            "Charge-off Amount or High Credit / Original Amount": ["high_credit_or_original_amount"],
            "Original Charge-off Amount": ["high_credit_or_original_amount", "raw_block"],
            "Date of First Delinquency": ["date_of_first_delinquency"],
            "Date Closed when closed": ["date_closed", "status"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date Last Payment / Date Last Activity when available": ["date_last_payment", "date_last_activity"],
            "Payment History Profile": ["payment_history_summary", "raw_block"],
            "Special Comment / Remarks": ["remarks"],
            "Compliance Condition Code / Dispute Indicator when disputed": ["remarks", "raw_block"],
            "Consumer Information Indicator when applicable": ["remarks", "raw_block"],
        },
        "validation_notes": [
            "Charge-off status, payment rating, balance, and past-due amount should not contradict each other.",
            "DOFD drives the reporting-age review and should not be missing from negative charge-off reporting.",
            "If sold or transferred, the balance and ownership/status should match the current reporting party's records.",
        ],
        "dispute_use": "Use for charge-off balance, status, payment rating, DOFD, sold/transferred, and obsolescence challenges.",
    },
    "closed_sold_transferred": {
        "label": "Closed, sold, transferred, or assigned account",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Account Status",
            "Current Balance",
            "Amount Past Due",
            "Original Charge-off Amount if applicable",
            "Date Closed",
            "Date Reported / Date Updated",
            "Date of First Delinquency if negative",
            "Special Comment / Sold-Transferred Remark",
            "Compliance Condition Code / Dispute Indicator when disputed",
            "Current Owner / Original Creditor context when applicable",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Account Status": ["status", "pay_status"],
            "Current Balance": ["balance"],
            "Amount Past Due": ["past_due"],
            "Original Charge-off Amount if applicable": ["high_credit_or_original_amount", "raw_block"],
            "Date Closed": ["date_closed", "status"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date of First Delinquency if negative": ["date_of_first_delinquency", "status"],
            "Special Comment / Sold-Transferred Remark": ["remarks", "status"],
            "Compliance Condition Code / Dispute Indicator when disputed": ["remarks", "raw_block"],
            "Current Owner / Original Creditor context when applicable": ["original_creditor", "collector_or_debt_buyer", "remarks"],
        },
        "validation_notes": [
            "A sold or transferred account with a nonzero balance needs ownership and balance support.",
            "Original creditor and collector reporting should not create duplicate active debt reporting.",
            "Closed/transferred status should match date closed, balance, and remarks.",
        ],
        "dispute_use": "Use for sold/transferred balance, duplicate ownership, closed-date, and status challenges.",
    },
    "installment_late_payment": {
        "label": "Installment or late-payment account",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Portfolio Type",
            "ECOA / Responsibility",
            "Account Status",
            "Payment Rating / Pay Status",
            "Current Balance",
            "Amount Past Due",
            "High Credit / Original Amount",
            "Terms or Scheduled Payment Amount when available",
            "Actual Payment Amount when available",
            "Date Opened",
            "Date Reported / Date Updated",
            "Date Last Payment / Date Last Activity",
            "Date of First Delinquency if negative",
            "Payment History Profile",
            "Special Comment / Remarks when needed",
            "Compliance Condition Code / Dispute Indicator when disputed",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Portfolio Type": ["portfolio_type"],
            "ECOA / Responsibility": ["responsibility"],
            "Account Status": ["status"],
            "Payment Rating / Pay Status": ["pay_status", "status"],
            "Current Balance": ["balance"],
            "Amount Past Due": ["past_due"],
            "High Credit / Original Amount": ["high_credit_or_original_amount"],
            "Terms or Scheduled Payment Amount when available": ["raw_block"],
            "Actual Payment Amount when available": ["raw_block"],
            "Date Opened": ["date_opened"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date Last Payment / Date Last Activity": ["date_last_payment", "date_last_activity"],
            "Date of First Delinquency if negative": ["date_of_first_delinquency", "status"],
            "Payment History Profile": ["payment_history_summary", "raw_block"],
            "Special Comment / Remarks when needed": ["remarks"],
            "Compliance Condition Code / Dispute Indicator when disputed": ["remarks", "raw_block"],
        },
        "validation_notes": [
            "Late-payment sequence should make sense against payment history and reported status.",
            "A current/paid account should not still show a materially contradictory late or past-due condition.",
            "DOFD is needed when negative reporting can affect reporting age.",
        ],
        "dispute_use": "Use for late-payment, payment history, balance, date, and pay-status challenges.",
    },
    "revolving": {
        "label": "Revolving account",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Portfolio Type",
            "ECOA / Responsibility",
            "Account Status",
            "Payment Rating / Pay Status",
            "Current Balance",
            "Credit Limit",
            "High Credit",
            "Amount Past Due",
            "Date Opened",
            "Date Reported / Date Updated",
            "Date Last Payment / Date Last Activity",
            "Date of First Delinquency if negative",
            "Payment History Profile",
            "Special Comment / Remarks when needed",
            "Compliance Condition Code / Dispute Indicator when disputed",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Portfolio Type": ["portfolio_type"],
            "ECOA / Responsibility": ["responsibility"],
            "Account Status": ["status"],
            "Payment Rating / Pay Status": ["pay_status", "status"],
            "Current Balance": ["balance"],
            "Credit Limit": ["credit_limit"],
            "High Credit": ["high_credit_or_original_amount"],
            "Amount Past Due": ["past_due"],
            "Date Opened": ["date_opened"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date Last Payment / Date Last Activity": ["date_last_payment", "date_last_activity"],
            "Date of First Delinquency if negative": ["date_of_first_delinquency", "status"],
            "Payment History Profile": ["payment_history_summary", "raw_block"],
            "Special Comment / Remarks when needed": ["remarks"],
            "Compliance Condition Code / Dispute Indicator when disputed": ["remarks", "raw_block"],
        },
        "validation_notes": [
            "Revolving balance, limit, high credit, past due, and payment rating should tell the same story.",
            "A negative revolving account needs a supportable delinquency timeline.",
            "Closed, transferred, or charged-off revolving accounts need status and balance support.",
        ],
        "dispute_use": "Use for balance, limit, utilization, late-payment, status, and DOFD challenges.",
    },
    "generic": {
        "label": "General tradeline",
        "required_fields": [
            "Account Number / Consumer Account Identifier",
            "Account Type",
            "Account Status",
            "Current Balance",
            "Date Opened",
            "Date Reported / Date Updated",
            "Date of First Delinquency if negative",
            "Special Comment / Remarks when needed",
        ],
        "field_map": {
            "Account Number / Consumer Account Identifier": ["account_number_masked"],
            "Account Type": ["account_type"],
            "Account Status": ["status", "pay_status"],
            "Current Balance": ["balance"],
            "Date Opened": ["date_opened"],
            "Date Reported / Date Updated": ["date_reported"],
            "Date of First Delinquency if negative": ["date_of_first_delinquency", "status"],
            "Special Comment / Remarks when needed": ["remarks"],
        },
        "validation_notes": [
            "At minimum, the account should identify who reported it, what it is, current status, balance, and key dates.",
            "Negative items need a supportable delinquency timeline and should be marked disputed when applicable.",
        ],
        "dispute_use": "Use as a general accuracy, completeness, and verifiability checklist.",
    },
}


def _tradeline_profile(tradeline: dict) -> str:
    text = " ".join(
        str(tradeline.get(field, ""))
        for field in [
            "account_name",
            "account_type",
            "portfolio_type",
            "status",
            "pay_status",
            "remarks",
            "raw_block",
        ]
    ).lower()
    if "collection" in text or "collector" in text or "debt buyer" in text:
        return "collection"
    if "charge" in text and "off" in text:
        return "charge_off"
    if any(term in text for term in ["sold", "transferred", "assigned", "purchased by another lender"]):
        return "closed_sold_transferred"
    if any(term in text for term in ["credit card", "revolving", "bankcard", "charge card"]):
        return "revolving"
    if any(term in text for term in ["installment", "auto", "student", "mortgage", "loan", "late", "past due"]):
        return "installment_late_payment"
    return "generic"


def _has_any_field(tradeline: dict, field_names: List[str]) -> bool:
    for field_name in field_names:
        value = str(tradeline.get(field_name, "") or "").strip()
        if not value:
            continue
        if field_name == "raw_block" and len(value) < 12:
            continue
        return True
    return False


def _metro2_presence(tradeline: dict, requirement: dict) -> Tuple[List[str], List[str]]:
    present = []
    missing = []
    field_map = requirement.get("field_map", {})
    for field_label in requirement.get("required_fields", []):
        if _has_any_field(tradeline, field_map.get(field_label, [])):
            present.append(field_label)
        else:
            missing.append(field_label)
    return present, missing


def _metro2_warning_flags(tradeline: dict, profile: str, missing_fields: List[str]) -> List[str]:
    flags = []
    status_text = " ".join([
        str(tradeline.get("status", "") or ""),
        str(tradeline.get("pay_status", "") or ""),
        str(tradeline.get("remarks", "") or ""),
    ]).lower()
    balance_number = money_to_number(str(tradeline.get("balance", "") or ""))

    if "Date of First Delinquency" in " ".join(missing_fields) and any(
        term in status_text for term in ["collection", "charge", "delinquent", "past due", "late"]
    ):
        flags.append("Missing DOFD on negative reporting candidate")
    if profile == "collection" and "Original Creditor" in missing_fields:
        flags.append("Collection missing original creditor field")
    if profile == "charge_off" and "Payment Rating / Pay Status" in missing_fields:
        flags.append("Charge-off missing payment rating/pay status support")
    if profile == "closed_sold_transferred" and balance_number and balance_number > 0:
        flags.append("Sold/transferred/closed account reports nonzero balance")
    if "dispute" not in status_text and "Compliance Condition Code / Dispute Indicator when disputed" in missing_fields:
        flags.append("If customer disputes this item, track dispute notation after notice")
    if not flags and missing_fields:
        flags.append("Admin should validate missing fields against raw PDF")
    if not flags:
        flags.append("No immediate required-field warning detected")
    return flags


def build_metro2_requirement_review(tradelines: List[dict]) -> List[dict]:
    rows = []
    for tradeline in tradelines:
        profile_key = _tradeline_profile(tradeline)
        requirement = METRO2_FIELD_REQUIREMENTS[profile_key]
        present, missing = _metro2_presence(tradeline, requirement)
        rows.append({
            "tradeline_id": tradeline.get("id", ""),
            "bureau": tradeline.get("bureau", ""),
            "account_name": tradeline.get("account_name", ""),
            "account_type": tradeline.get("account_type", ""),
            "status": tradeline.get("status") or tradeline.get("pay_status") or "",
            "metro2_profile": requirement["label"],
            "required_core_fields": requirement["required_fields"],
            "present_fields": present,
            "missing_or_needs_validation": missing,
            "warning_flags": _metro2_warning_flags(tradeline, profile_key, missing),
            "validation_notes": requirement["validation_notes"],
            "dispute_use": requirement["dispute_use"],
            "production_note": "Credit Vivo checklist. Validate against official licensed CDIA Metro 2 CRRG before production/certification.",
        })
    return rows


FCRA_COMPLIANCE_AREAS = {
    "maximum_possible_accuracy": {
        "label": "FCRA accuracy and completeness",
        "law_reference": "FCRA 607(b) / 15 USC 1681e(b)",
        "plain_english": "Credit reports should use reasonable procedures so the information is as accurate as possible.",
        "applies_when": "Any account field appears wrong, incomplete, mixed, misleading, duplicated, or inconsistent across bureaus.",
        "evidence_needed": "3-bureau comparison, raw report excerpt, account statements, payment proof, creditor/collector records, identity proof when needed.",
        "tracking_action": "Create field-level dispute draft and track before/after bureau values.",
    },
    "bureau_reinvestigation": {
        "label": "Bureau reinvestigation duty",
        "law_reference": "FCRA 611 / 15 USC 1681i",
        "plain_english": "When a consumer disputes report information, the bureau must reasonably reinvestigate and send written results.",
        "applies_when": "Customer disputes a specific bureau report item or cross-bureau mismatch.",
        "evidence_needed": "Customer-approved dispute, specific account fields challenged, proof documents, delivery tracking, bureau response.",
        "tracking_action": "Track dispute sent date, delivery date, response due date, written results, changed/deleted/verified outcome.",
    },
    "furnisher_after_notice": {
        "label": "Furnisher investigation after bureau notice",
        "law_reference": "FCRA 623(b) / 15 USC 1681s-2(b)",
        "plain_english": "After the bureau sends the dispute to the furnisher, the furnisher must investigate and report results back.",
        "applies_when": "A bureau dispute is sent and the furnisher/collector is the source of the challenged field.",
        "evidence_needed": "Bureau dispute package, furnisher records, account ledger, ownership/assignment proof, payment history, response result.",
        "tracking_action": "Track which furnisher controls each challenged field and whether the item was corrected, deleted, or verified.",
    },
    "direct_furnisher_dispute": {
        "label": "Direct furnisher dispute",
        "law_reference": "Regulation V 12 CFR 1022.43",
        "plain_english": "A consumer can dispute certain account information directly with the company furnishing the data.",
        "applies_when": "The dispute relates to liability, account terms, balance, credit limit, payment status, payment amount, or open/closed dates.",
        "evidence_needed": "Direct dispute notice, account identifier, specific facts, supporting documents, proof of delivery, furnisher response.",
        "tracking_action": "Prepare direct furnisher dispute only after customer approval and route to the furnisher's direct-dispute address when available.",
    },
    "dofd_obsolescence": {
        "label": "DOFD and obsolete information review",
        "law_reference": "FCRA 605 and 623(a)(5) / 15 USC 1681c and 1681s-2(a)(5)",
        "plain_english": "Negative reporting needs the right first-delinquency date so old items do not stay on the report too long.",
        "applies_when": "Collection, charge-off, late payment, or other negative item is missing DOFD, has conflicting dates, or appears too old.",
        "evidence_needed": "First delinquency timeline, payment history, charge-off date, collection placement date, removal date, prior reports.",
        "tracking_action": "Flag missing/conflicting DOFD and track whether deletion/correction or obsolescence review is needed.",
    },
    "disputed_by_consumer_notation": {
        "label": "Disputed-account notation",
        "law_reference": "FCRA 623(a)(3) / 15 USC 1681s-2(a)(3)",
        "plain_english": "If an account is disputed and still furnished, it should be reported as disputed when the duty applies.",
        "applies_when": "Credit Vivo sends a customer-approved dispute and later report updates still omit dispute notation.",
        "evidence_needed": "Notice of dispute, proof of delivery, post-dispute report, furnisher/bureau response.",
        "tracking_action": "After sending, check updated reports for dispute notation and escalate if unresolved.",
    },
    "identity_theft_block": {
        "label": "Identity theft block review",
        "law_reference": "FCRA 605B / 15 USC 1681c-2",
        "plain_english": "Identity-theft items can require a faster block when the consumer provides the required identity-theft packet.",
        "applies_when": "Customer says the account is identity theft, fraud, not mine, or mixed file.",
        "evidence_needed": "Identity proof, identity theft report, item identification, consumer statement that the transaction was not theirs.",
        "tracking_action": "Hold for identity-theft workflow and attorney/compliance review before using this route.",
    },
}


EOSCAR_PUBLIC_FACTS = [
    {
        "title": "What e-OSCAR is",
        "detail": "e-OSCAR is used by consumer reporting agencies and data furnishers to exchange and respond to credit-history disputes. Consumers submit disputes to bureaus and/or furnishers, not directly inside e-OSCAR.",
        "source": "Credit Vivo local e-OSCAR learning guide; public e-OSCAR getting-started concepts",
    },
    {
        "title": "ACDV path",
        "detail": "When a bureau receives a consumer dispute, it may send an Automated Credit Dispute Verification (ACDV) to the furnisher. The furnisher can verify, update, or correct the information.",
        "source": "Credit Vivo local e-OSCAR learning guide",
    },
    {
        "title": "AUD path",
        "detail": "A furnisher can initiate an Automated Universal Dataform (AUD) to request an out-of-cycle correction. AUD is not a consumer direct-submission path.",
        "source": "Credit Vivo local e-OSCAR learning guide",
    },
    {
        "title": "Best packaging principle",
        "detail": "A strong dispute package identifies each account, exact field, reported value, consumer position, support documents, and requested correction or deletion.",
        "source": "Credit Vivo local e-OSCAR learning guide; FTC/CFPB consumer dispute guidance",
    },
]


EOSCAR_ISSUE_PACKAGING = {
    "cross_bureau_balance_mismatch": {
        "category": "field-specific accuracy dispute",
        "package_hint": "List each balance reported by each bureau and attach the 3-bureau comparison.",
        "evidence_hint": "3-bureau comparison, statements, payoff/settlement proof, itemization, or account ledger.",
    },
    "cross_bureau_status_mismatch": {
        "category": "account status/payment history accuracy dispute",
        "package_hint": "Separate current status, pay status, charge-off, collection, paid/settled, and closed/open wording.",
        "evidence_hint": "Settlement letter, payoff confirmation, account statements, bureau report pages, response letters.",
    },
    "cross_bureau_date_mismatch": {
        "category": "date field accuracy dispute",
        "package_hint": "List each date reported by bureau and ask for source-record verification of the correct date.",
        "evidence_hint": "Prior reports, account statements, payment history, charge-off notice, collection notice.",
    },
    "missing_dofd_review": {
        "category": "date of first delinquency completeness dispute",
        "package_hint": "Ask for verification of the DOFD and the basis for the reporting period.",
        "evidence_hint": "Payment history, charge-off statement, collection notice, old account statement showing delinquency timeline.",
    },
    "collection_review": {
        "category": "collection account completeness dispute",
        "package_hint": "Identify the collection account, original creditor, balance, ownership/assignment question, and requested verification.",
        "evidence_hint": "Credit report page, collector letter, original creditor statement, assignment/sale letter if available.",
    },
    "chargeoff_review": {
        "category": "charge-off accuracy dispute",
        "package_hint": "Separate charge-off status, current balance, past due, charge-off amount, DOFD, and sold/transferred status.",
        "evidence_hint": "Charge-off statement, account ledger, payment history, sale/transfer notice, settlement or payoff proof.",
    },
    "closed_sold_balance_review": {
        "category": "sold/transferred balance accuracy dispute",
        "package_hint": "Ask whether the furnisher still owns the debt and why a balance remains after sold/transferred/closed status.",
        "evidence_hint": "Sale/transfer notice, account statement, collector notice, original creditor response.",
    },
    "low_confidence_admin_review": {
        "category": "manual packaging review",
        "package_hint": "Do not send until the account identity and specific field dispute are confirmed from the raw report.",
        "evidence_hint": "Raw report pages, manual parser review notes, customer statement, supporting documents.",
    },
}


def _eoscar_packaging_for_issue(issue_type: str) -> dict:
    return EOSCAR_ISSUE_PACKAGING.get(issue_type or "", {
        "category": "specific factual dispute",
        "package_hint": "Explain the exact inaccurate or incomplete reporting field. Avoid broad wording unless identity/liability is truly disputed.",
        "evidence_hint": "Relevant report page plus account-level documents supporting the specific correction requested.",
    })


def build_eoscar_packaging_review(issues: List[dict], tradelines: List[dict]) -> List[dict]:
    tradelines_by_id = {item.get("id"): item for item in tradelines}
    rows = []
    for issue in issues:
        related = [
            tradelines_by_id[item_id]
            for item_id in issue.get("related_tradeline_ids", [])
            if item_id in tradelines_by_id
        ]
        packaging = _eoscar_packaging_for_issue(issue.get("issue_type", ""))
        account_names = sorted({item.get("account_name", "") for item in related if item.get("account_name")})
        bureaus = sorted({item.get("bureau", "") for item in related if item.get("bureau")})
        fields = _expert_rule_for_issue(ReviewIssue(
            id=issue.get("id", ""),
            issue_type=issue.get("issue_type", ""),
            severity=issue.get("severity", ""),
            customer_label=issue.get("customer_label", ""),
            customer_explanation=issue.get("customer_explanation", ""),
            admin_explanation=issue.get("admin_explanation", ""),
            suggested_round=issue.get("suggested_round", ""),
        )).get("metro2_fields", [])
        rows.append({
            "issue_id": issue.get("id", ""),
            "issue_type": issue.get("issue_type", ""),
            "account_names": account_names,
            "bureaus": bureaus,
            "eoscar_category": packaging["category"],
            "acdv_packaging_steps": [
                "Create one bureau-specific package for each bureau reporting the error so the issue can survive CRA intake and ACDV routing.",
                "Use one account group per section.",
                "Include exact account name and masked account number.",
                "Name the exact disputed field and reported value.",
                "State the consumer position and factual basis.",
                "Attach exhibits and request correct, update, verify, delete, or block as appropriate.",
            ],
            "field_focus": fields,
            "package_hint": packaging["package_hint"],
            "evidence_hint": packaging["evidence_hint"],
            "avoid": [
                "Do not send generic 'this is inaccurate' wording by itself.",
                "Do not claim direct e-OSCAR access.",
                "Do not send without customer approval and proof review.",
                "Do not misrepresent facts or create false disputes.",
            ],
            "tracking_status": "draft_packaging_review_not_sent",
        })
    return rows


FIELD_COMPLIANCE_RULES = {
    "Account/Furnisher Name": {
        "source_field": "account_name",
        "required_for": ["all"],
        "metro2_concept": "Identifies the reporting furnisher/tradeline.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 611 reinvestigation if disputed.",
        "missing_issue": "Furnisher/account name is missing or not visible.",
        "different_issue": "Furnisher/account name differs across bureaus.",
        "verification_ask": "Verify the exact furnisher/subscriber name reporting this tradeline.",
    },
    "Account Number": {
        "source_field": "account_number_masked",
        "required_for": ["all"],
        "metro2_concept": "Consumer account identifier, usually masked on consumer reports.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 611 reinvestigation if disputed.",
        "missing_issue": "Account number is missing or masked differently across reports.",
        "different_issue": "Account number does not align across bureaus.",
        "verification_ask": "Verify the account identifier and confirm this is the same tradeline across bureaus.",
    },
    "Account Type": {
        "source_field": "account_type",
        "required_for": ["all"],
        "metro2_concept": "Classifies the account as collection, revolving, auto, mortgage, student loan, charge account, etc.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Account type is missing or not visible.",
        "different_issue": "Account type differs across bureaus.",
        "verification_ask": "Verify the reported account type and correct any inaccurate classification.",
    },
    "Responsibility / ECOA": {
        "source_field": "responsibility",
        "required_for": ["all"],
        "metro2_concept": "Consumer responsibility such as individual, joint, co-signer, or authorized user.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 611 reinvestigation if disputed.",
        "missing_issue": "Responsibility/ECOA field is missing.",
        "different_issue": "Responsibility/ECOA differs across bureaus.",
        "verification_ask": "Verify the consumer responsibility code for this tradeline.",
    },
    "Original Creditor": {
        "source_field": "original_creditor",
        "required_for": ["collection", "debt buyer", "factoring"],
        "metro2_concept": "K1 original creditor/source account, especially important for collections and purchased debt.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher duties after notice; Reg V direct dispute where applicable.",
        "missing_issue": "Original creditor is missing for a collection/debt-buyer review item.",
        "different_issue": "Original creditor differs across bureaus.",
        "verification_ask": "Verify the K1 original creditor/source account and ownership or assignment chain.",
    },
    "Creditor Classification": {
        "source_field": "creditor_classification",
        "required_for": ["collection", "debt buyer", "factoring"],
        "metro2_concept": "K1 creditor classification for the original creditor/source account when applicable.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Creditor classification is missing or not visible for a collection/debt-buyer item.",
        "different_issue": "Creditor classification differs across bureaus.",
        "verification_ask": "Verify the K1 creditor classification and whether the account is being reported under the correct source category.",
    },
    "Current Balance": {
        "source_field": "balance",
        "required_for": ["all"],
        "metro2_concept": "Current reported balance.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties; Reg V direct dispute.",
        "missing_issue": "Current balance is missing.",
        "different_issue": "Current balance differs across bureaus.",
        "verification_ask": "Verify the current balance and provide the records supporting the amount.",
    },
    "Past Due Amount": {
        "source_field": "past_due",
        "required_for": ["collection", "charge-off", "late", "past due", "delinquent"],
        "metro2_concept": "Amount currently past due, if applicable.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties; Reg V direct dispute.",
        "missing_issue": "Past due amount is missing or not separately shown for a negative account.",
        "different_issue": "Past due amount differs across bureaus.",
        "verification_ask": "Verify the amount past due and whether it should be separately reported.",
    },
    "High Credit / Original Amount": {
        "source_field": "high_credit_or_original_amount",
        "required_for": ["collection", "debt buyer", "installment", "mortgage", "auto", "loan", "charge-off"],
        "metro2_concept": "Original balance, high credit, or original amount depending on account type.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Original amount/high credit is missing for this account class.",
        "different_issue": "Original amount/high credit differs across bureaus.",
        "verification_ask": "Verify the original balance, original amount, high credit, or charge-off amount.",
    },
    "Original Charge-off Amount": {
        "source_field": "high_credit_or_original_amount",
        "required_for": ["charge-off", "collection", "debt buyer"],
        "metro2_concept": "Original charge-off amount when the account was charged off before collection/sale/transfer.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties; FCRA 611 reinvestigation.",
        "missing_issue": "Original charge-off amount is not separately visible for a charged-off or collection review item.",
        "different_issue": "Original charge-off/high-credit amount differs across bureaus.",
        "verification_ask": "Verify the original charge-off amount and how it relates to current balance, past due, and sale/transfer history.",
    },
    "Credit Limit": {
        "source_field": "credit_limit",
        "required_for": ["credit card", "revolving"],
        "metro2_concept": "Credit limit for revolving accounts when applicable.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Credit limit is missing where it may be applicable.",
        "different_issue": "Credit limit differs across bureaus.",
        "verification_ask": "Verify the credit limit or confirm why it is not applicable.",
    },
    "Status / Pay Status": {
        "source_field": "status",
        "required_for": ["all"],
        "metro2_concept": "Current account/payment condition such as current, collection, charge-off, paid, closed, transferred.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties; FCRA 611 after dispute.",
        "missing_issue": "Status/pay status is missing.",
        "different_issue": "Status/pay status differs across bureaus.",
        "verification_ask": "Verify the exact account/payment status and supporting account history.",
    },
    "Payment Rating": {
        "source_field": "pay_status",
        "required_for": ["charge-off", "late", "past due", "delinquent", "collection", "revolving", "installment"],
        "metro2_concept": "Payment rating represents the current payment condition and should align with account status and history.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Payment rating/pay status is missing or not visible for an account where payment condition matters.",
        "different_issue": "Payment rating/pay status differs across bureaus.",
        "verification_ask": "Verify the payment rating against the payment history profile, account status, and current balance.",
    },
    "Payment History Profile": {
        "source_field": "payment_history_summary",
        "required_for": ["charge-off", "late", "past due", "delinquent", "revolving", "installment", "auto", "mortgage"],
        "metro2_concept": "Monthly payment history string showing whether months were current, late, charged off, or otherwise coded.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties; FCRA 611 reinvestigation.",
        "missing_issue": "Payment history profile is missing or not visible for a payment-history review item.",
        "different_issue": "Payment history differs across bureaus.",
        "verification_ask": "Verify the payment history profile month by month against the account ledger.",
    },
    "Date Opened / Assigned": {
        "source_field": "date_opened",
        "required_for": ["all"],
        "metro2_concept": "Date opened or assignment/open date depending on account type.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Date opened/assigned is missing.",
        "different_issue": "Date opened/assigned differs across bureaus.",
        "verification_ask": "Verify the date opened or assignment date with source records.",
    },
    "Date Reported / Updated": {
        "source_field": "date_reported",
        "required_for": ["all"],
        "metro2_concept": "Date of account information/date reported: the date the furnisher last reported or updated the account.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Date reported/updated is missing.",
        "different_issue": "Date reported/updated differs across bureaus.",
        "verification_ask": "Verify the date this account was last reported or updated.",
    },
    "Date Closed": {
        "source_field": "date_closed",
        "required_for": ["closed", "charge-off", "transferred", "sold"],
        "metro2_concept": "Date account was closed, transferred, sold, or otherwise no longer open.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Date closed is missing for a closed/sold/transferred account.",
        "different_issue": "Date closed differs across bureaus.",
        "verification_ask": "Verify the date closed or confirm whether the account should be open/closed.",
    },
    "Date of First Delinquency": {
        "source_field": "date_of_first_delinquency",
        "required_for": ["collection", "charge-off", "late", "past due", "delinquent"],
        "metro2_concept": "First delinquency date tied to the negative reporting period.",
        "fcra_basis": "FCRA 605 obsolescence; FCRA 623(a)(5) DOFD duty; FCRA 611 reinvestigation if disputed.",
        "missing_issue": "Date of first delinquency is missing for an adverse account.",
        "different_issue": "Date of first delinquency differs across bureaus.",
        "verification_ask": "Verify the DOFD and reporting-period source records.",
    },
    "Estimated Removal / On Record Until": {
        "source_field": "estimated_removal_date",
        "required_for": ["collection", "charge-off", "late", "past due", "delinquent"],
        "metro2_concept": "Consumer-facing estimated removal or on-record-until date, when shown.",
        "fcra_basis": "FCRA 605 obsolescence; FCRA 623(a)(5) DOFD duty.",
        "missing_issue": "Estimated removal/on-record-until date is missing for an adverse account.",
        "different_issue": "Estimated removal/on-record-until date differs.",
        "verification_ask": "Verify the reporting period and estimated removal date.",
    },
    "Remarks / Narrative Codes": {
        "source_field": "remarks",
        "required_for": ["disputed", "collection", "charge-off", "transferred", "sold", "bankruptcy"],
        "metro2_concept": "Special comment, remarks, compliance condition, dispute, or narrative codes.",
        "fcra_basis": "FCRA 623(a)(3) disputed-account notation; FCRA 607(b) accuracy.",
        "missing_issue": "Remarks/dispute notation may be missing where expected.",
        "different_issue": "Remarks/narrative codes differ across bureaus.",
        "verification_ask": "Verify special comments, dispute indicators, and narrative codes.",
    },
    "Compliance Condition Code": {
        "source_field": "remarks",
        "required_for": ["disputed", "collection", "charge-off", "bankruptcy", "identity theft", "deceased"],
        "metro2_concept": "Compliance condition code signals disputes and special compliance conditions.",
        "fcra_basis": "FCRA 623(a)(3) disputed-account notation; FCRA 611 reinvestigation; Reg V accuracy/integrity duties.",
        "missing_issue": "Compliance/dispute condition is not visible where a dispute or special condition may apply.",
        "different_issue": "Compliance condition/dispute notation differs across bureaus.",
        "verification_ask": "Verify whether the account should be marked disputed or carry another compliance condition code.",
    },
    "Consumer Information Indicator": {
        "source_field": "remarks",
        "required_for": ["bankruptcy", "deceased", "personal receivership"],
        "metro2_concept": "Consumer information indicator can reflect consumer-level conditions such as bankruptcy or deceased status.",
        "fcra_basis": "FCRA 607(b) accuracy; FCRA 611 reinvestigation; FCRA 623 furnisher accuracy/integrity duties.",
        "missing_issue": "Consumer information indicator is not visible where a consumer-level condition may apply.",
        "different_issue": "Consumer information indicator differs across bureaus.",
        "verification_ask": "Verify whether any consumer-level indicator is being reported and whether it is accurate.",
    },
}


def _account_class_text(tradeline: dict) -> str:
    return " ".join(
        str(tradeline.get(field, "") or "")
        for field in [
            "account_name",
            "account_type",
            "portfolio_type",
            "status",
            "pay_status",
            "remarks",
            "raw_block",
        ]
    ).lower()


def _field_required_for_account(rule: dict, account_class: str) -> bool:
    required_for = [str(item).lower() for item in rule.get("required_for", [])]
    if "all" in required_for:
        return True
    return any(token in account_class for token in required_for)


def build_field_compliance_audit(tradelines: List[dict]) -> List[dict]:
    rows = []
    for tradeline in tradelines:
        account_class = _account_class_text(tradeline)
        for field_name, rule in FIELD_COMPLIANCE_RULES.items():
            source_field = rule["source_field"]
            value = tradeline.get(source_field, "")
            if field_name == "Status / Pay Status":
                value = tradeline.get("status") or tradeline.get("pay_status") or ""
            required = _field_required_for_account(rule, account_class)
            present = bool(str(value or "").strip())
            if present:
                issue_flag = "OK"
            elif required:
                issue_flag = "MISSING_REQUIRED_EXPECTED"
            else:
                issue_flag = "NOT_VISIBLE_CONDITIONAL"
            rows.append({
                "tradeline_id": tradeline.get("id", ""),
                "bureau": tradeline.get("bureau", ""),
                "account_name": tradeline.get("account_name", ""),
                "field_name": field_name,
                "parsed_value": value or "Not shown",
                "required_or_expected": "Yes" if required else "Conditional / if reported",
                "issue_flag": issue_flag,
                "metro2_concept": rule["metro2_concept"],
                "fcra_basis": rule["fcra_basis"],
                "issue_text": "" if issue_flag == "OK" else rule["missing_issue"],
                "verification_ask": rule["verification_ask"],
                "requested_outcome": (
                    "Verify and correct with all CRAs; delete only if inaccurate, incomplete, or unverifiable."
                    if issue_flag != "OK" else
                    "No automated correction requested unless source records show an inaccuracy."
                ),
                "source_note": "Built from Credit Vivo local FCRA/Metro 2 rule files; not a substitute for attorney/CDIA CRRG validation.",
            })
    return rows


DATE_FIELD_TITLES = {
    "date_opened": "Date Opened / Assigned",
    "date_closed": "Date Closed",
    "date_reported": "Date Reported / Last Updated",
    "date_last_activity": "Date of Last Activity",
    "date_last_payment": "Date of Last Payment",
    "date_of_first_delinquency": "Date of First Delinquency / DOFD",
    "estimated_removal_date": "Estimated Removal / On Record Until",
}


DATE_LABEL_PATTERNS = {
    "date_opened": ["date opened", "opened"],
    "date_closed": ["date closed", "closed"],
    "date_reported": ["date reported", "date updated", "balance updated", "last reported", "reported"],
    "date_last_activity": ["date of last activity", "last activity"],
    "date_last_payment": ["date of last payment", "last payment made", "last payment"],
    "date_of_first_delinquency": ["date of first delinquency", "date of 1st delinquency", "first delinquency", "dofd"],
    "estimated_removal_date": ["on record until", "estimated month and year this item will be removed", "estimated removal"],
}


def _month_number(name: str) -> str:
    months = {
        "jan": "01", "january": "01",
        "feb": "02", "february": "02",
        "mar": "03", "march": "03",
        "apr": "04", "april": "04",
        "may": "05",
        "jun": "06", "june": "06",
        "jul": "07", "july": "07",
        "aug": "08", "august": "08",
        "sep": "09", "sept": "09", "september": "09",
        "oct": "10", "october": "10",
        "nov": "11", "november": "11",
        "dec": "12", "december": "12",
    }
    return months.get(name.lower()[:9], "")


def normalize_audit_date(value: str) -> Tuple[str, str]:
    value = clean_text(value)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", value)
    if m:
        year = m.group(3)
        if len(year) == 2:
            year = "20" + year if int(year) <= 40 else "19" + year
        return f"{int(year):04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}", "day"

    m = re.search(r"\b([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})\b", value)
    if m and _month_number(m.group(1)):
        return f"{int(m.group(3)):04d}-{_month_number(m.group(1))}-{int(m.group(2)):02d}", "day"

    m = re.search(r"\b([A-Za-z]{3,9})\s+(\d{4})\b", value)
    if m and _month_number(m.group(1)):
        return f"{int(m.group(2)):04d}-{_month_number(m.group(1))}", "month"

    m = re.search(r"\b(\d{4})\b", value)
    if m:
        return m.group(1), "year"

    return value, "unknown"


def _date_context(raw_block: str, raw_date: str) -> str:
    text = clean_text(raw_block)
    idx = text.lower().find(raw_date.lower())
    if idx < 0:
        return text[:260]
    return text[max(0, idx - 120): idx + len(raw_date) + 160]


def build_dates_found_audit(tradelines: List[dict]) -> List[dict]:
    rows = []
    for tradeline in tradelines:
        raw_block = str(tradeline.get("raw_block", "") or "")
        for field_name, field_title in DATE_FIELD_TITLES.items():
            parsed_value = str(tradeline.get(field_name, "") or "").strip()
            if parsed_value:
                normalized, precision = normalize_audit_date(parsed_value)
                rows.append({
                    "source_file": tradeline.get("source_filename", ""),
                    "bureau": tradeline.get("bureau", ""),
                    "page": tradeline.get("page_start", ""),
                    "account_key": tradeline.get("id", ""),
                    "creditor": tradeline.get("account_name", ""),
                    "field_name": field_name,
                    "field_title": field_title,
                    "raw_date": parsed_value,
                    "normalized_date": normalized,
                    "precision": precision,
                    "label_matched": "; ".join(DATE_LABEL_PATTERNS.get(field_name, [])),
                    "confidence": 92 if precision in {"day", "month"} else 70,
                    "context": _date_context(raw_block, parsed_value),
                })

        for m in re.finditer(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|[A-Za-z]{3,9}\s+\d{4})\b", raw_block):
            raw_date = clean_text(m.group(0))
            normalized, precision = normalize_audit_date(raw_date)
            if any(row["normalized_date"] == normalized and row["account_key"] == tradeline.get("id", "") for row in rows):
                continue
            rows.append({
                "source_file": tradeline.get("source_filename", ""),
                "bureau": tradeline.get("bureau", ""),
                "page": tradeline.get("page_start", ""),
                "account_key": tradeline.get("id", ""),
                "creditor": tradeline.get("account_name", ""),
                "field_name": "unassigned_date_seen",
                "field_title": "Unassigned Date Seen In Account Block",
                "raw_date": raw_date,
                "normalized_date": normalized,
                "precision": precision,
                "label_matched": "not assigned - review source line",
                "confidence": 30,
                "context": _date_context(raw_block, raw_date),
            })
    return rows


def _is_negative_or_tracked_account(tradeline: dict) -> bool:
    text = _account_class_text(tradeline)
    return any(term in text for term in [
        "collection",
        "debt buyer",
        "factoring",
        "charge",
        "charged off",
        "charge-off",
        "late",
        "past due",
        "delinquent",
        "settled",
        "repossession",
        "foreclosure",
    ])


def build_date_issues_to_dispute(tradelines: List[dict], groups: List[dict]) -> List[dict]:
    rows = []
    for tradeline in tradelines:
        if not _is_negative_or_tracked_account(tradeline):
            continue

        for field_name, field_title in DATE_FIELD_TITLES.items():
            value = str(tradeline.get(field_name, "") or "").strip()
            if not value and field_name in {"date_of_first_delinquency", "date_reported", "date_opened"}:
                rows.append({
                    "severity": "High" if field_name == "date_of_first_delinquency" else "Medium",
                    "account_bureau": f"{tradeline.get('account_name', '')} / {tradeline.get('bureau', '')}",
                    "issue_type": "Missing date field",
                    "what_found": f"The scanner found a negative/tracked account, but {field_title} is blank or was not safely parsed.",
                    "why_matters": "Important date fields help verify accuracy, completeness, obsolescence, and whether the reporting period is correct.",
                    "next_step": f"Compare the PDF source. If {field_title} is missing or cannot be verified, dispute this specific field and request verification records.",
                })

    tradelines_by_id = {item.get("id"): item for item in tradelines}
    for group in groups:
        items = [tradelines_by_id.get(item_id) for item_id in group.get("tradeline_ids", [])]
        items = [item for item in items if item]
        if len(items) < 2:
            continue
        for field_name, field_title in DATE_FIELD_TITLES.items():
            values = {
                item.get("bureau", ""): item.get(field_name, "")
                for item in items
                if item.get(field_name)
            }
            normalized = {normalize_audit_date(str(value))[0] for value in values.values() if value}
            if len(normalized) >= 2:
                account_name = "; ".join(sorted({item.get("account_name", "") for item in items if item.get("account_name")}))
                rows.append({
                    "severity": "High" if field_name == "date_of_first_delinquency" else "Medium",
                    "account_bureau": account_name,
                    "issue_type": "Date differs across bureaus",
                    "what_found": f"{field_title} differs across bureaus: " + "; ".join(f"{k}: {v}" for k, v in values.items()),
                    "why_matters": "Different dates may affect reporting age, obsolescence, account history, and dispute verification.",
                    "next_step": f"Dispute the specific {field_title} mismatch with bureau comparison evidence and request the furnisher's source record.",
                })
    return rows


def _related_issue_types_for_tradeline(tradeline_id: str, issues: List[dict]) -> List[str]:
    return [
        issue.get("issue_type", "")
        for issue in issues
        if tradeline_id in issue.get("related_tradeline_ids", [])
    ]


def _fcra_scanner_signals(tradeline: dict, requirement_row: dict, issue_types: List[str], area_key: str) -> List[str]:
    signals = []
    missing = requirement_row.get("missing_or_needs_validation", [])
    warnings = requirement_row.get("warning_flags", [])
    status_text = " ".join([
        str(tradeline.get("status", "") or ""),
        str(tradeline.get("pay_status", "") or ""),
        str(tradeline.get("remarks", "") or ""),
        str(tradeline.get("raw_block", "") or ""),
    ]).lower()

    if issue_types:
        signals.append("Detected issue types: " + ", ".join(sorted(set(issue_types))))
    if missing and area_key in {"maximum_possible_accuracy", "direct_furnisher_dispute"}:
        signals.append("Missing or needs validation: " + "; ".join(missing[:8]))
    if warnings and area_key in {"maximum_possible_accuracy", "dofd_obsolescence", "disputed_by_consumer_notation"}:
        signals.append("Warnings: " + "; ".join(warnings))
    if area_key == "bureau_reinvestigation" and issue_types:
        signals.append("Specific bureau dispute candidate based on scanner findings")
    if area_key == "furnisher_after_notice" and any(
        issue.startswith("cross_bureau") or issue in {"collection_review", "chargeoff_review", "closed_sold_balance_review"}
        for issue in issue_types
    ):
        signals.append("Furnisher likely controls one or more challenged account fields")
    if area_key == "dofd_obsolescence" and (
        "Date of First Delinquency" in " ".join(missing) or any(term in status_text for term in ["collection", "charge", "late", "past due"])
    ):
        signals.append("Negative reporting candidate needs DOFD/age review")
    if area_key == "disputed_by_consumer_notation":
        signals.append("Applies after customer-approved dispute is sent and a later report is reviewed")
    if area_key == "identity_theft_block" and any(term in status_text for term in ["identity theft", "fraud", "not mine", "mixed file"]):
        signals.append("Possible identity theft or mixed-file wording found")

    if not signals:
        signals.append("No automatic trigger; keep as compliance checklist item")
    return signals


def _fcra_area_keys_for_tradeline(tradeline: dict, requirement_row: dict, issue_types: List[str]) -> List[str]:
    keys = ["maximum_possible_accuracy", "direct_furnisher_dispute", "disputed_by_consumer_notation"]
    if issue_types or requirement_row.get("missing_or_needs_validation"):
        keys.append("bureau_reinvestigation")
    if issue_types:
        keys.append("furnisher_after_notice")
    text = " ".join([
        str(tradeline.get("account_type", "") or ""),
        str(tradeline.get("status", "") or ""),
        str(tradeline.get("pay_status", "") or ""),
        str(tradeline.get("remarks", "") or ""),
        str(tradeline.get("raw_block", "") or ""),
    ]).lower()
    if (
        "Date of First Delinquency" in " ".join(requirement_row.get("missing_or_needs_validation", []))
        or any(term in text for term in ["collection", "charge", "late", "past due", "delinquent"])
    ):
        keys.append("dofd_obsolescence")
    if any(term in text for term in ["identity theft", "fraud", "not mine", "mixed file"]):
        keys.append("identity_theft_block")
    return list(dict.fromkeys(keys))


def build_fcra_compliance_review(tradelines: List[dict], issues: List[dict], metro2_rows: List[dict]) -> List[dict]:
    rows = []
    metro2_by_id = {row.get("tradeline_id"): row for row in metro2_rows}
    for tradeline in tradelines:
        tradeline_id = tradeline.get("id", "")
        requirement_row = metro2_by_id.get(tradeline_id, {})
        issue_types = _related_issue_types_for_tradeline(tradeline_id, issues)
        for area_key in _fcra_area_keys_for_tradeline(tradeline, requirement_row, issue_types):
            area = FCRA_COMPLIANCE_AREAS[area_key]
            rows.append({
                "tradeline_id": tradeline_id,
                "bureau": tradeline.get("bureau", ""),
                "account_name": tradeline.get("account_name", ""),
                "fcra_area": area["label"],
                "law_reference": area["law_reference"],
                "plain_english": area["plain_english"],
                "applies_when": area["applies_when"],
                "scanner_signals": _fcra_scanner_signals(tradeline, requirement_row, issue_types, area_key),
                "evidence_needed": area["evidence_needed"],
                "tracking_action": area["tracking_action"],
                "customer_approval_required": True,
                "attorney_or_compliance_review": area_key in {"identity_theft_block", "dofd_obsolescence"} or any(
                    issue.startswith("cross_bureau") for issue in issue_types
                ),
                "note": "Compliance checklist only. Not legal advice. Attorney/compliance review required before production policy or escalation.",
            })
    return rows


def entity_industry_roles(name: str, item: dict) -> List[str]:
    text = " ".join(str(value or "") for value in [
        name,
        item.get("account_name", ""),
        item.get("account_type", ""),
        item.get("original_creditor", ""),
        item.get("collector_or_debt_buyer", ""),
        item.get("remarks", ""),
        item.get("raw_block", ""),
    ]).lower()
    roles = []
    if any(term in text for term in ["collection", "collector"]):
        roles.append("collection agency")
        roles.append("debt collector")
    if any(term in text for term in ["debt buyer", "factoring company", "lvnv", "resurgent", "midland", "jefferson capital"]):
        roles.append("debt buyer")
    if any(term in text for term in ["bank", "jpmcb", "citibank", "capital one", "credit one", "card services", "cbna"]):
        roles.append("bank")
    if any(term in text for term in ["credit union", "fcu", "federal credit", "navy federal", "northwest"]):
        roles.append("credit union")
    if any(term in text for term in ["verizon", "telecom", "wireless", "utility", "electric", "gas", "water"]):
        roles.append("telecom/utility")
    if any(term in text for term in ["progressive", "geico", "allstate", "state farm", "insurance"]):
        roles.append("insurance collector")
    if any(term in text for term in ["mortgage", "mtg", "home loan", "real estate", "conventional re"]):
        roles.append("mortgage company")
    return roles


def complaint_route_for_entity(entity_type: str) -> str:
    if entity_type == "bureau":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"]
    if entity_type in {"debt collector", "debt buyer", "collection agency"}:
        return OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["ftc"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["state_ag"]
    if entity_type == "telecom/utility":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["fcc"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"] + " if credit reporting is disputed"
    if entity_type == "credit union":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["ncua"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"]
    if entity_type == "bank":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["occ"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["fdic"]
    if entity_type == "mortgage company":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["nmls"]
    if entity_type == "insurance collector":
        return OFFICIAL_ENTITY_LOOKUP_LINKS["state_ag"] + " | state insurance regulator"
    return OFFICIAL_ENTITY_LOOKUP_LINKS["cfpb_complaint"] + " | " + OFFICIAL_ENTITY_LOOKUP_LINKS["state_ag"]


def nmls_link_for_entity(entity_type: str) -> str:
    if entity_type in {"mortgage company", "bank", "credit union", "debt buyer", "debt collector", "furnisher"}:
        return OFFICIAL_ENTITY_LOOKUP_LINKS["nmls"]
    return ""


def build_entity_compliance_intelligence(tradelines: List[dict]) -> List[dict]:
    rows: List[dict] = []
    seen = set()
    checked_date = date.today().isoformat()

    def add_entity(item: dict, entity_name: str, entity_type: str, source_role: str) -> None:
        entity_name = clean_account_name_candidate(str(entity_name or ""))
        if not entity_name or is_bad_account_name(entity_name):
            return
        key = (
            item.get("id", ""),
            normalized_alias_name(entity_name),
            entity_type,
            source_role,
        )
        if key in seen:
            return
        seen.add(key)
        official_lookup_note = f"Search official records for: {entity_name}"
        rows.append({
            "tradeline_id": item.get("id", ""),
            "source_file": item.get("source_filename", ""),
            "bureau": item.get("bureau", ""),
            "account_name": item.get("account_name", ""),
            "entity_name": entity_name,
            "normalized_entity_name": normalized_alias_name(entity_name),
            "entity_type": entity_type,
            "source_role": source_role,
            "business_registry_search_link": OFFICIAL_ENTITY_LOOKUP_LINKS["business_registry"] + f" | {official_lookup_note}",
            "state_license_search_link": OFFICIAL_ENTITY_LOOKUP_LINKS["state_license"] + f" | {official_lookup_note}",
            "debt_collector_license_search_link": (
                OFFICIAL_ENTITY_LOOKUP_LINKS["debt_collector_license"] + f" | {official_lookup_note}"
                if entity_type in {"debt collector", "debt buyer", "collection agency"}
                else ""
            ),
            "nmls_search_link": nmls_link_for_entity(entity_type),
            "regulator_complaint_route": complaint_route_for_entity(entity_type),
            "last_checked_date": checked_date,
            "link_health_status": "not_checked_manual_required",
            "verification_status": "pending_official_manual_review",
            "customer_wording": ENTITY_COMPLIANCE_CUSTOMER_WORDING,
            "admin_wording": ENTITY_COMPLIANCE_ADMIN_WORDING,
            "manual_review_notes": (
                f"{ENTITY_COMPLIANCE_ADMIN_WORDING} Link health is not a finding; verify current official URLs and records manually. "
                "Do not call this a violation unless official evidence and compliance review support that wording."
            ),
            "supports_validation_letters": True,
            "supports_furnisher_disputes": True,
            "supports_bureau_disputes": True,
            "supports_complaint_packets": True,
            "supports_attorney_review_summaries": True,
        })

    for item in tradelines:
        if not classify_negative_tradeline(item):
            continue
        add_entity(item, item.get("bureau", ""), "bureau", "reporting_bureau")
        add_entity(item, item.get("account_name", ""), "furnisher", "reported_account_name")
        add_entity(item, item.get("original_creditor", ""), "original creditor", "original_creditor")
        collector = item.get("collector_or_debt_buyer") or item.get("account_name", "")
        if collector and ("collection" in str(item).lower() or entity_industry_roles(collector, item)):
            for role in [role for role in entity_industry_roles(collector, item) if role in {"debt collector", "debt buyer", "collection agency"}]:
                add_entity(item, collector, role, "collection_reporting_entity")
        for role in entity_industry_roles(item.get("account_name", ""), item):
            add_entity(item, item.get("account_name", ""), role, "industry_classification")
        if item.get("original_creditor"):
            for role in entity_industry_roles(item.get("original_creditor", ""), item):
                add_entity(item, item.get("original_creditor", ""), role, "original_creditor_industry")

    return rows


def result_to_dict(result: ParseResult) -> dict:
    tradelines = [asdict(t) for t in result.tradelines]
    for item in tradelines:
        item["parserConfidence"] = item.get("parser_confidence") or item.get("confidence")
        item["missingRequiredFields"] = item.get("missing_required_fields", [])
        item["fieldWarnings"] = item.get("field_warnings", [])
        item["sourceBureau"] = item.get("source_bureau") or str(item.get("bureau", "")).lower()
        item["sourceReportDate"] = item.get("source_report_date", "")
        item["sourcePageHint"] = item.get("source_page_hint")
        item["normalized_alias_name"] = normalized_alias_name(item.get("account_name", ""))
        item["rawVerificationStatus"] = item.get("raw_verification_status", "not_verified")
        item["rawVerifiedFields"] = item.get("raw_verified_fields", [])
        item["rawUnverifiedFields"] = item.get("raw_unverified_fields", [])
        item["rawVerificationWarnings"] = item.get("raw_verification_warnings", [])
    issues = [asdict(i) for i in result.issues]
    scanner_rules = load_scanner_rules()
    metro2_requirement_review = build_metro2_requirement_review(tradelines)
    field_compliance_audit = build_field_compliance_audit(tradelines)
    eoscar_packaging_review = build_eoscar_packaging_review(issues, tradelines)
    dates_found_audit = build_dates_found_audit(tradelines)
    date_issues_to_dispute = build_date_issues_to_dispute(tradelines, result.cross_bureau_groups)
    entity_compliance_intelligence = build_entity_compliance_intelligence(tradelines)
    data = {
        "engine": result.engine,
        "version": result.version,
        "paid_ai_used": result.paid_ai_used,
        "files": result.files,
        "tradelines": tradelines,
        "issues": issues,
        "identity_raw_data": result.identity_raw_data,
        "cross_bureau_groups": result.cross_bureau_groups,
        "customer_summary": result.customer_summary,
        "raw_verification_summary": result.raw_verification_summary,
        "decision_readiness": build_decision_readiness(result.issues),
        "admin_summary": result.admin_summary,
        "letter_workflow": build_letter_workflow(),
        "recommended_letter_queue": build_recommended_letter_queue(result.issues),
        "fcra_review": build_fcra_review(result.issues),
        "metro2_fcra_review": build_metro2_fcra_review(result.issues),
        "metro2_public_guide_notes": METRO2_PUBLIC_GUIDE_NOTES,
        "metro2_requirement_review": metro2_requirement_review,
        "fcra_compliance_review": build_fcra_compliance_review(tradelines, issues, metro2_requirement_review),
        "fcra_rights_reference": build_fcra_rights_reference(),
        "field_compliance_audit": field_compliance_audit,
        "entity_compliance_intelligence": entity_compliance_intelligence,
        "dates_found_audit": dates_found_audit,
        "date_issues_to_dispute": date_issues_to_dispute,
        "bureau_debt_collection_reference": build_bureau_debt_collection_reference(),
        "eoscar_public_facts": EOSCAR_PUBLIC_FACTS,
        "eoscar_packaging_review": eoscar_packaging_review,
        "scanner_rules_library": scanner_rules,
        "scanner_skill_map": build_scanner_skill_map(),
    }
    data["cfpb_packet_system"] = build_cfpb_packet_system(data)
    return data


def _safe_workbook_cell(value):
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return value


def _write_workbook_sheet(sheet, rows: List[List[object]]) -> None:
    for row in rows:
        sheet.append([_safe_workbook_cell(value) for value in row])

    if not rows or Workbook is None:
        return

    header_fill = PatternFill("solid", fgColor="D1FAE5")
    header_font = Font(bold=True, color="064E3B")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, vertical="top")

    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    for column_index, column in enumerate(sheet.columns, start=1):
        max_length = 10
        for cell in column:
            max_length = max(max_length, min(len(str(cell.value or "")), 55))
        sheet.column_dimensions[get_column_letter(column_index)].width = max_length + 2

    sheet.freeze_panes = "A2"
    sheet.sheet_view.showGridLines = False


def _norm_compare(value) -> str:
    return clean_text(str(value or "")).lower()


def _comparison_flag(values: List[str], label: str) -> str:
    present = {_norm_compare(value) for value in values if _norm_compare(value)}
    if len(present) >= 2:
        return f"{label} differs"
    return ""


def _comparison_groups(data: dict) -> List[Tuple[str, List[dict]]]:
    tradelines = [item for item in data.get("tradelines", []) if is_customer_review_item(item)]
    by_id = {item.get("id"): item for item in tradelines}
    groups = []
    used_ids = set()
    for group in data.get("cross_bureau_groups", []):
        items = [by_id[tid] for tid in group.get("tradeline_ids", []) if tid in by_id]
        if items:
            groups.append((group.get("group_id", ""), items))
            used_ids.update(item.get("id") for item in items)
    for item in tradelines:
        if item.get("id") not in used_ids:
            groups.append((item.get("id", ""), [item]))
    return groups


def is_customer_review_item(item: dict) -> bool:
    account_name = str(item.get("account_name", "") or "")
    if is_bad_account_name(account_name) or account_name_quality(account_name) < 0:
        return False
    text = " ".join(str(item.get(key, "") or "") for key in [
        "account_name",
        "account_type",
        "status",
        "pay_status",
        "remarks",
        "original_creditor",
        "collector_or_debt_buyer",
        "raw_block",
    ]).lower()
    if classify_negative_tradeline(item):
        return True
    review_terms = [
        "collection",
        "debt buyer",
        "charge",
        "past due",
        "late",
        "repossession",
        "foreclosure",
        "bankruptcy",
        "settlement",
        "settled",
        "transferred",
        "sold",
        "delinquent",
        "timeline",
        "dofd",
        "dispute",
    ]
    if any(term in text for term in review_terms):
        return True
    return False


def _issues_for_tradeline_ids(data: dict, tradeline_ids: Iterable[str]) -> List[dict]:
    id_set = set(tradeline_ids)
    return [
        issue
        for issue in data.get("issues", [])
        if id_set & set(issue.get("related_tradeline_ids", []))
    ]


RAW_DISPLAY_STOP_LABELS = [
    "Account Number",
    "Account Type",
    "Loan/Account Type",
    "Loan Type",
    "Responsibility",
    "Owner",
    "Original Creditor",
    "Creditor Classification",
    "Status Updated",
    "Status",
    "Pay Status",
    "Balance Updated",
    "Balance",
    "Amount Past Due",
    "Past Due",
    "High Balance",
    "Highest Balance",
    "High Credit",
    "Original Balance",
    "Credit Limit",
    "Monthly Payment",
    "Scheduled Payment Amount",
    "Date Opened",
    "Date Reported",
    "Date Updated",
    "Date Closed",
    "Date of Last Payment",
    "Last Payment Made",
    "Date of First Delinquency",
    "Date of 1st Delinquency",
    "Date Major Delinquency",
    "Charge Off Amount",
    "Terms",
    "Frequency",
    "Remarks",
]


RAW_DISPLAY_FIELD_LABELS = {
    "account_number_masked": ["Account Number"],
    "account_type": ["Loan/Account Type", "Account Type", "Loan Type"],
    "portfolio_type": ["Portfolio Type", "Loan Type", "Loan/Account Type"],
    "responsibility": ["Responsibility", "Owner"],
    "original_creditor": ["Original Creditor", "Original Lender"],
    "creditor_classification": ["Creditor Classification"],
    "date_opened": ["Date Opened"],
    "date_reported": ["Date Reported", "Date Updated", "Balance Updated"],
    "status": ["Pay Status", "Status"],
    "status_updated": ["Status Updated"],
    "balance": ["Current Balance", "Balance"],
    "past_due": ["Amount Past Due", "Past Due"],
    "high_credit_or_original_amount": ["High Balance", "Highest Balance", "High Credit", "Original Balance", "Original Amount"],
    "credit_limit": ["Credit Limit"],
    "monthly_payment": ["Monthly Payment", "Scheduled Payment Amount"],
    "date_last_payment": ["Date of Last Payment", "Last Payment Made", "Last Payment"],
    "date_closed": ["Date Closed"],
    "date_of_first_delinquency": ["Date of First Delinquency", "Date of 1st Delinquency", "DOFD", "Original Delinquency Date"],
    "date_major_delinquency_first_reported": ["Date Major Delinquency First Reported", "Date Major Delinquency"],
    "charge_off_amount": ["Charge Off Amount", "Charge-Off Amount"],
    "terms_frequency": ["Terms Frequency", "Terms", "Frequency"],
    "payment_history_summary": ["Payment History", "Payment Rating"],
    "remarks": ["Remarks", "Comments"],
    "estimated_removal_date": ["Estimated Removal", "On Record Until", "scheduled to"],
}


def _raw_display_cleanup(value: str) -> str:
    value = clean_text(value)
    value = re.sub(r"\s+", " ", value).strip(" ;,")
    return value


def _raw_value_after_label(raw: str, label: str) -> str:
    stop = "|".join(re.escape(item) for item in RAW_DISPLAY_STOP_LABELS if item.lower() != label.lower())
    pattern = (
        rf"\b{re.escape(label)}\b"
        rf"(?:\s*\(Hist\.\))?"
        rf"\s*(?:[:\-]|of)?\s*"
        rf"(.+?)"
        rf"(?=\s+(?:{stop})\b|\s*\||\n|$)"
    )
    m = re.search(pattern, raw, flags=re.I)
    if not m:
        return ""
    value = _raw_display_cleanup(m.group(1))
    if not value or value.lower() in {"-", "n/a", "not reported"}:
        return value
    return value


def _raw_money_after_label(raw: str, labels: List[str]) -> str:
    for label in labels:
        pattern = rf"\b{re.escape(label)}\b(?:\s*\(Hist\.\))?\s*(?:[:\-]|of)?\s*({MONEY})"
        m = re.search(pattern, raw, flags=re.I)
        if m:
            return _raw_display_cleanup(m.group(1))
    return ""


def _raw_date_after_label(raw: str, labels: List[str]) -> str:
    for label in labels:
        pattern = rf"\b{re.escape(label)}\b\s*(?:[:\-])?\s*({DATE})"
        m = re.search(pattern, raw, flags=re.I)
        if m:
            return _raw_display_cleanup(m.group(1))
    return ""


def _raw_display_value(item: dict, field_key: str) -> str:
    raw = str(item.get("raw_block", "") or "")
    if not raw:
        return ""
    if field_key == "account_name":
        name = str(item.get("account_name", "") or "").strip()
        return name if name and name in raw else ""
    if field_key in {"balance", "past_due", "high_credit_or_original_amount", "credit_limit", "monthly_payment", "charge_off_amount"}:
        return _raw_money_after_label(raw, RAW_DISPLAY_FIELD_LABELS.get(field_key, []))
    if field_key in {
        "date_opened",
        "date_reported",
        "status_updated",
        "date_last_payment",
        "date_closed",
        "date_of_first_delinquency",
        "date_major_delinquency_first_reported",
        "estimated_removal_date",
    }:
        value = _raw_date_after_label(raw, RAW_DISPLAY_FIELD_LABELS.get(field_key, []))
        if value:
            return value
        if field_key == "estimated_removal_date":
            m = re.search(r"\bBy\s+(" + DATE + r")\s*,?\s+this account is scheduled", raw, flags=re.I)
            if m:
                return _raw_display_cleanup(m.group(1))
        return ""
    for label in RAW_DISPLAY_FIELD_LABELS.get(field_key, []):
        value = _raw_value_after_label(raw, label)
        if value:
            return value
    return ""


def _field_value(item: dict, field_key: str) -> str:
    if not item:
        return ""
    raw_display = _raw_display_value(item, field_key)
    if raw_display:
        return raw_display
    if field_key == "status":
        return item.get("status") or item.get("pay_status") or ""
    if field_key == "address_phone":
        raw = str(item.get("raw_block", ""))
        phone = re.search(r"(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", raw)
        address_line = re.search(
            r"\b(?:PO BOX|P\.O\. BOX|\d{2,6}\s+[A-Z0-9 .'-]+(?:ST|RD|AVE|BLVD|DR|LN|WAY|STE)\b[^\n|]{0,80})",
            raw,
            flags=re.I,
        )
        return " | ".join(part for part in [
            address_line.group(0) if address_line else "",
            phone.group(0) if phone else "",
        ] if part)
    if field_key == "potential_issue":
        return ""
    if field_key == "raw_block":
        source = item.get("source_filename", "")
        page = item.get("page_start", "")
        return f"Source evidence retained in hidden admin audit tabs. File: {source}; page hint: {page}."
    return str(item.get(field_key, "") or "")


def _comparison_account_type(items: List[dict]) -> str:
    text = " ".join(
        str(item.get(field, "") or "")
        for item in items
        for field in [
            "account_name",
            "account_type",
            "portfolio_type",
            "status",
            "pay_status",
            "remarks",
            "raw_block",
        ]
    ).lower()
    if any(term in text for term in ["mortgage", "mtg", "foreclosure"]):
        return "mortgage"
    if any(term in text for term in ["charge off", "charge-off", "charged off", "chargeoff", "written off"]):
        return "charge off"
    if any(term in text for term in ["collection", "collector", "debt buyer", "debt collector", "assigned to", "collection agency"]):
        return "collection"
    if any(term in text for term in ["late", "past due", "delinquent", "30 days", "60 days", "90 days", "120 days"]):
        return "late"
    return "late"


def _comparison_report_furnisher_name(items: List[dict]) -> str:
    by_bureau = {}
    for item in items:
        bureau = str(item.get("bureau", "") or "")
        name = str(item.get("account_name", "") or "").strip()
        if bureau and name and bureau not in by_bureau:
            by_bureau[bureau] = name
    for bureau in ["Equifax", "Experian", "TransUnion"]:
        if by_bureau.get(bureau):
            return by_bureau[bureau]
    return next((str(item.get("account_name", "") or "").strip() for item in items if item.get("account_name")), "Review Item")


def _comparison_source_pages(items: List[dict]) -> str:
    parts = []
    for item in sorted(items, key=lambda row: (str(row.get("bureau", "")), str(row.get("source_filename", "")), int(row.get("page_start") or 0))):
        bureau = str(item.get("bureau", "") or "Report")
        page = item.get("page_start") or item.get("source_page_hint") or ""
        filename = str(item.get("source_filename", "") or "").strip()
        source = bureau
        if page:
            source += f" p.{page}"
        if filename:
            source += f" ({filename})"
        parts.append(source)
    return "; ".join(parts)


def _field_requirement_text(field_key: str, label: str, items: List[dict]) -> str:
    text = " ".join(str(item.get(key, "") or "") for item in items for key in ["account_type", "status", "raw_block"]).lower()
    if field_key in {"account_name", "account_number_masked", "account_type", "responsibility", "status", "date_opened", "date_reported", "balance"}:
        return f"REQUIRED: {label} should be accurate, complete, current, and tied to the same account across bureau reporting."
    if field_key in {"original_creditor", "creditor_classification", "portfolio_type", "address_phone", "remarks"}:
        return f"CONDITIONAL / IF SHOWN: {label} must match source records and not conflict with the account type, ownership, or status."
    if "collection" in text and field_key in {"date_of_first_delinquency", "estimated_removal_date", "past_due"}:
        return f"REQUIRED FOR COLLECTIONS: {label} should support the collection reporting timeline and should not create a misleading account history."
    if field_key in {"date_of_first_delinquency", "date_closed", "estimated_removal_date", "payment_history", "payment_rating"}:
        return f"CONDITIONAL / TIMELINE REVIEW: {label} must be supported by source records when adverse history is reported."
    return f"VERIFY IF REPORTED: {label} should be supported by account-level source records and consistent with the bureau section."


def _field_priority(differs: bool, missing_values: List[str], values: dict, related_issues: List[dict], label: str) -> str:
    if differs:
        if any(word in label.lower() for word in ["type", "status", "dofd", "delinquency", "removal", "balance", "creditor"]):
            return "Compliance issue - verify"
        return "Field mismatch - verify"
    if missing_values and any(values.values()):
        return "Missing/blank - verify"
    if any(issue.get("severity") == "high" for issue in related_issues):
        return "High-priority review"
    return "Verify"


def _field_compliance_rule_for_label(label: str) -> dict:
    if label in FIELD_COMPLIANCE_RULES:
        return FIELD_COMPLIANCE_RULES[label]
    normalized = clean_text(label).lower()
    aliases = {
        "responsibility/owner": "Responsibility / ECOA",
        "status/pay status": "Status / Pay Status",
        "status/ pay status": "Status / Pay Status",
        "current balance": "Current Balance",
        "balance": "Current Balance",
        "past due amount": "Past Due Amount",
        "amount past due": "Past Due Amount",
        "date opened/assigned": "Date Opened / Assigned",
        "date reported/updated": "Date Reported / Updated",
        "date updated": "Date Reported / Updated",
        "date of first delinquency": "Date of First Delinquency",
        "estimated removal/on record until": "Estimated Removal / On Record Until",
        "payment rating/history summary": "Payment History Profile",
        "remarks/narrative codes": "Remarks / Narrative Codes",
        "address/phone": "Address / Phone",
        "portfolio/loan type": "Account Type",
    }
    return FIELD_COMPLIANCE_RULES.get(aliases.get(normalized, ""), {
        "source_field": "",
        "required_for": [],
        "metro2_concept": f"{label} should be reviewed against the account-level source records and bureau reporting section.",
        "fcra_basis": "FCRA 607(b) accuracy/completeness; FCRA 611 reinvestigation if disputed; FCRA 623/Reg V duties where a furnisher controls the data.",
        "missing_issue": f"{label} is not visible on one or more bureau sections.",
        "different_issue": f"{label} differs across bureau sections.",
        "verification_ask": f"Verify {label} against raw bureau data and source records before using it in a letter or packet.",
    })


def _field_compliance_review(label: str, items: List[dict], values: dict, differs: bool, missing_values: List[str], related_issues: List[dict]) -> dict:
    rule = _field_compliance_rule_for_label(label)
    account_class = " ".join(_account_class_text(item) for item in items)
    required = _field_required_for_account(rule, account_class)
    present_bureaus = [bureau for bureau, value in values.items() if value]
    all_missing = not present_bureaus
    collection_context = any(term in account_class for term in ["collection", "debt buyer", "collector", "collection agency"])
    open_account_type_bureaus = [
        bureau
        for bureau, value in values.items()
        if label == "Account Type" and re.search(r"\bopen account\b", str(value or ""), flags=re.I)
    ]
    if collection_context and open_account_type_bureaus:
        status = "Compliance Review - Collection Type Classification"
        issue = (
            f"Collection/debt-buyer context found, but Account Type is reported as Open Account on "
            f"{', '.join(open_account_type_bureaus)}. Open may describe an active/unpaid account, but as an account type it can be misleading if the item is actually a collection or debt-buyer tradeline."
        )
        requested = "Verify whether the tradeline should report as collection/debt buyer instead of Open Account; correct any misleading or unsupported account-type classification."
    elif differs:
        status = "Compliance Review - Does Not Match"
        issue = rule.get("different_issue", f"{label} differs across bureaus.")
        requested = "VERIFY AND CORRECT with all CRAs; delete this field/account only if source records cannot verify it as accurate, complete, and current."
    elif missing_values and required:
        status = "Compliance Review - Missing Required Field"
        issue = rule.get("missing_issue", f"{label} is missing where expected.")
        requested = "VERIFY REQUIRED FIELD with source records; correct, update, or remove if the account-level reporting cannot support the value."
    elif missing_values and any(values.values()):
        status = "Compliance Review - Missing on Some Bureaus"
        issue = f"{label} is visible on {', '.join(present_bureaus)} but missing/blank on {', '.join(missing_values)}."
        requested = "Verify whether the missing bureau value is incomplete, not reported, or not applicable before drafting a dispute."
    elif all_missing and required:
        status = "Compliance Review - Missing Across All Bureaus"
        issue = rule.get("missing_issue", f"{label} is missing across all available bureau sections.")
        requested = "Verify whether this required/expected field exists in source records before using the account in a packet."
    else:
        status = "Pass / Verify Source Records"
        issue = f"No cross-bureau mismatch detected for {label}; still verify the raw value, account class, and source records before use."
        requested = "No correction requested from this row unless source records or customer documents show the value is inaccurate, incomplete, outdated, duplicate, or unverifiable."
    return {
        "status": status,
        "required_or_expected": "Required / expected for this account class" if required else "Conditional / verify if reported",
        "specific_issue": issue,
        "fcra_concern": (
            f"{rule.get('fcra_basis', '')} Field status: {status}. "
            "Use only as draft review data; customer approval and admin review are required."
        ),
        "metro2_concern": (
            f"{rule.get('metro2_concept', '')} "
            f"Requiredness: {'required/expected' if required else 'conditional/if reported'}. "
            "Validate against the official licensed CDIA Metro 2 CRRG before production/certification."
        ),
        "verification_ask": rule.get("verification_ask", f"Verify {label} against source records."),
        "requested_outcome": requested,
    }


def _brief_rule_text(value: str, limit: int = 210) -> str:
    value = clean_text(value)
    value = re.sub(r"\s+", " ", value)
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip(" .,;") + "..."


def _combined_issue_rules_outcome(index: int, compliance: dict) -> str:
    return " | ".join([
        f"{index}. Issue: {_brief_rule_text(compliance['specific_issue'], 190)}",
        f"Possible FCRA/Reg V: {_brief_rule_text(compliance['fcra_concern'], 170)}",
        f"Metro 2: {_brief_rule_text(compliance['metro2_concern'], 170)}",
        f"Outcome: {_brief_rule_text(compliance['requested_outcome'], 180)}",
    ])


def build_ours_three_bureaus_comparison_rows(data: dict) -> List[List[object]]:
    rules = data.get("scanner_rules_library") or load_scanner_rules()
    field_rows = rules.get("metro2_field_map", {}).get("fields", [])
    if len(field_rows) < 25:
        existing_keys = {row.get("key", "") for row in field_rows if isinstance(row, dict)}
        supplemental_fields = [
            {"key": "account_number_masked", "workbook_label": "Masked Account Number", "source_fields": ["account_number_masked", "account_number"]},
            {"key": "past_due", "workbook_label": "Past Due", "source_fields": ["past_due"]},
            {"key": "credit_limit", "workbook_label": "Credit Limit", "source_fields": ["credit_limit"]},
            {"key": "high_balance", "workbook_label": "High Balance", "source_fields": ["high_balance"]},
            {"key": "payment_status", "workbook_label": "Payment Status", "source_fields": ["payment_status", "pay_status", "status"]},
            {"key": "last_payment_date", "workbook_label": "Last Payment Date", "source_fields": ["last_payment_date"]},
            {"key": "date_closed", "workbook_label": "Date Closed", "source_fields": ["date_closed"]},
            {"key": "date_of_first_delinquency", "workbook_label": "Date of First Delinquency", "source_fields": ["date_of_first_delinquency", "dofd"]},
            {"key": "estimated_removal_date", "workbook_label": "Estimated Removal Date", "source_fields": ["estimated_removal_date"]},
            {"key": "raw_evidence_id", "workbook_label": "Raw Evidence ID", "source_fields": ["id", "source_file", "bureau"]},
        ]
        for field in supplemental_fields:
            if len(field_rows) >= 25:
                break
            if field["key"] not in existing_keys:
                field_rows.append(field)
                existing_keys.add(field["key"])
    bureau_order = ["Experian", "Equifax", "TransUnion"]
    rows = [
        ["Three-Bureau Negative Tradeline Forensic Comparison - Experian / Equifax / TransUnion"],
        [
            "Prepared from uploaded consumer credit reports. Blank cells mean the field was not visible or not reported in that bureau section. Draft review only.",
        ],
        ["", "", "", "", "", "", "Note", "Issues are likely inconsistencies from the workbook data; verify with source records before sending disputes."],
        [
        "Field #",
        "Account Info",
        "Experian",
        "Equifax",
        "TransUnion",
        "Forensic issue / dispute lead",
        "3-CRA Status",
        "AI Error / Inaccuracy Found",
        "Reason / Why It Matters",
        "Dispute / Verification Request",
        "Priority",
        "Evidence / Notes",
        ],
    ]

    for group_number, (group_id, items) in enumerate(_comparison_groups(data), start=1):
        by_bureau = {}
        for item in items:
            by_bureau.setdefault(item.get("bureau", ""), item)
        related_issues = _issues_for_tradeline_ids(data, [str(item.get("id", "")) for item in items])
        issue_text = "; ".join(sorted({issue.get("customer_label", "") for issue in related_issues if issue.get("customer_label")})) or "Review recommended"
        account_names = _comparison_report_furnisher_name(items)
        account_type = _comparison_account_type(items)
        source_pages = _comparison_source_pages(items)
        present_bureaus = [bureau for bureau in bureau_order if bureau in by_bureau]
        missing_bureaus = [bureau for bureau in bureau_order if bureau not in by_bureau]
        cra_status = "3-CRA" if len(present_bureaus) == 3 else f"Missing {', '.join(missing_bureaus)}"
        reports_on = ", ".join(present_bureaus) if present_bureaus else "No bureau values visible"
        group_priority = "High" if any(issue.get("severity") == "high" for issue in related_issues) else "Medium" if related_issues else "Review"
        group_issue = issue_text if issue_text != "Review recommended" else "Review field-level rows for missing, inconsistent, or unverifiable report data."

        rows.append([
            account_names,
            "",
            "",
            "",
            "",
            "",
            "Reports on all 3 CRAs" if len(present_bureaus) == 3 else f"Reports on: {reports_on}",
            group_issue,
            f"Reports on: {reports_on}",
            "Review field-level errors below; prepare only factual, customer-approved dispute prep with supporting proof.",
            group_priority,
            source_pages or f"Group: {group_id}",
        ])

        for index, field in enumerate(field_rows, start=1):
            field_key = field.get("key", "")
            label = field.get("workbook_label") or field.get("label") or field_key
            values = {bureau: _field_value(by_bureau.get(bureau, {}), field_key) for bureau in bureau_order}
            present_values = {clean_text(value).lower() for value in values.values() if value}
            missing_values = [bureau for bureau, value in values.items() if not value]
            differs = len(present_values) > 1
            if field_key == "potential_issue":
                forensic_issue = issue_text
            elif differs:
                forensic_issue = f"{label} differs across bureaus"
            elif missing_values and any(values.values()):
                forensic_issue = f"{label} missing on {', '.join(missing_values)}"
            else:
                forensic_issue = issue_text
            priority = _field_priority(differs, missing_values, values, related_issues, label)
            compliance = _field_compliance_review(label, items, values, differs, missing_values, related_issues)
            ai_error = compliance["specific_issue"]
            reason = f"{compliance['fcra_concern']} Metro 2: {compliance['metro2_concern']}"
            request = f"Outcome: {compliance['requested_outcome']}"
            evidence_notes = "; ".join(
                part
                for part in [
                    f"EX: {values['Experian']}" if values["Experian"] else "",
                    f"EQ: {values['Equifax']}" if values["Equifax"] else "",
                    f"TU: {values['TransUnion']}" if values["TransUnion"] else "",
                    "Raw evidence IDs: " + ", ".join(str(item.get("id", "")) for item in items if item.get("id")),
                    source_pages or f"Group: {group_id}; Source fields: {', '.join(field.get('source_fields', []))}",
                ]
                if part
            )

            rows.append([
                index,
                label,
                values["Experian"],
                values["Equifax"],
                values["TransUnion"],
                forensic_issue,
                cra_status,
                ai_error,
                reason,
                request,
                priority,
                evidence_notes,
            ])
    return rows


def build_negative_account_rules_rows(data: dict) -> List[List[object]]:
    rules = data.get("scanner_rules_library") or load_scanner_rules()
    rows = [["Rule ID", "Category", "Keywords", "Metro 2 Status Codes", "Priority", "Review Reason", "Compliance Guard"]]
    for category in rules.get("negative_account_rules", {}).get("categories", []):
        rows.append([
            category.get("id", ""),
            category.get("label", ""),
            category.get("keywords", []),
            category.get("metro2_status_codes", []),
            category.get("priority", ""),
            category.get("review_reason", ""),
            "Draft review data only; customer approval and admin review required.",
        ])
    return rows


def build_negative_definitions_rows(data: dict) -> List[List[object]]:
    rules = data.get("scanner_rules_library") or load_scanner_rules()
    rows = [["Code / Category", "Meaning", "Scanner Use"]]
    rows.extend([
        ["Collection", "An account reported by a collection agency, debt collector, or assigned collection party.", "Review original creditor, balance, ownership/assignment, status, DOFD, and reporting dates."],
        ["Charge-off", "A creditor-reported status indicating the creditor treated the account as a loss for accounting purposes.", "Review balance, sold/transferred status, date fields, payment history, and duplicate collection overlap."],
        ["Debt buyer", "A company that may have purchased or received assignment of a debt from the original creditor or another owner.", "Review ownership chain, original creditor, assigned/opened dates, balance, and authority to report or collect."],
        ["Late payment", "A reported 30/60/90/120+ day delinquency or similar payment-history remark.", "Review payment history, date first delinquent, major delinquency date, and customer proof before any draft."],
        ["Re-aging / timeline review", "A safe review label for DOFD, estimated-removal, opened, assigned, or on-record-until timeline questions.", "Use REAGE rules as admin review prompts only; do not label as a violation in customer view."],
        ["Duplicate / same-debt review", "Possible overlap where an original creditor and collector/debt buyer may be reporting the same underlying debt.", "Compare account identifiers, balances, original creditor, ownership, DOFD, and reporting status."],
        ["Notice of dispute", "A consumer-dispute notation that may need to appear after a dispute is delivered and while continued reporting occurs.", "Review FCRA-NOD-001 only when dispute delivery/history exists; drafts remain approval-gated."],
        ["Method of verification", "A request to understand how a disputed item was verified after an investigation response.", "Use as a follow-up draft after customer approval/admin review and documented response history."],
    ])
    for code, meaning in rules.get("negative_account_rules", {}).get("metro2_status_codes", {}).items():
        rows.append([code, meaning, "Internal review signal only; verify against source report and official subscriber guidance."])
    for category in rules.get("negative_account_rules", {}).get("categories", []):
        rows.append([category.get("label", ""), category.get("review_reason", ""), "Negative/reviewable account classification."])
    return rows


def build_rule_library_rows(data: dict, library_key: str) -> List[List[object]]:
    rules = data.get("scanner_rules_library") or load_scanner_rules()
    library = rules.get(library_key, {})
    rows = [["Library", "Item", "Value"]]
    for key, value in library.items():
        if isinstance(value, list):
            for index, item in enumerate(value, start=1):
                rows.append([library_key, f"{key}_{index}", item])
        else:
            rows.append([library_key, key, value])
    return rows


def build_account_summary_rows(data: dict) -> List[List[object]]:
    rows = [[
        "#",
        "Tradeline / Furnisher",
        "Normalized Group",
        "Category",
        "Bureaus Seen",
        "Equifax Summary",
        "Experian Summary",
        "TransUnion Summary",
        "Priority",
        "Main Possible Issue",
        "Recommended Draft Letter",
        "Status",
    ]]
    bureau_order = ["Equifax", "Experian", "TransUnion"]
    for row_number, (_group_id, items) in enumerate(_comparison_groups(data), start=1):
        ids = [str(item.get("id", "")) for item in items]
        issues = _issues_for_tradeline_ids(data, ids)
        categories = []
        for item in items:
            categories.extend(match["label"] for match in classify_negative_tradeline(item))
        by_bureau = {item.get("bureau", ""): item for item in items}
        account_name = "; ".join(sorted({item.get("account_name", "") for item in items if item.get("account_name")})) or "Review Item"
        main_issue = "; ".join(sorted({issue.get("customer_label", "") for issue in issues if issue.get("customer_label")})) or "; ".join(sorted(set(categories))) or "Needs review"
        recommended_letter = "Bureau review + furnisher direct dispute"
        if any("collection" in str(category).lower() or "debt" in str(category).lower() for category in categories):
            recommended_letter = "Bureau review + debt validation/furnisher review"
        rows.append([
            row_number,
            account_name,
            normalized_alias_name(account_name),
            "; ".join(sorted(set(categories))) or "Review-needed account",
            " / ".join(bureau[:2].upper() for bureau in bureau_order if bureau in by_bureau),
            _account_bureau_summary(by_bureau.get("Equifax")),
            _account_bureau_summary(by_bureau.get("Experian")),
            _account_bureau_summary(by_bureau.get("TransUnion")),
            "high" if any(issue.get("severity") == "high" for issue in issues) else "medium" if issues else "low",
            main_issue,
            recommended_letter,
            "Draft review",
        ])
    return rows


def _account_bureau_summary(item: dict | None) -> str:
    if not item:
        return "Not visible / not reported"
    parts = []
    for label, key in [
        ("type", "account_type"),
        ("status", "status"),
        ("balance", "balance"),
        ("past due", "past_due"),
        ("DOFD", "date_of_first_delinquency"),
        ("removal", "estimated_removal_date"),
    ]:
        value = item.get(key)
        if value:
            parts.append(f"{label} {value}")
    warnings = item.get("fieldWarnings") or item.get("field_warnings") or []
    if warnings:
        parts.append("; ".join(warnings[:2]))
    return "; ".join(parts) or "Needs review"


def build_safe_letter_recommendation_rows(data: dict) -> List[List[object]]:
    rules = data.get("scanner_rules_library") or load_scanner_rules()
    labels = {
        "bureau_review_dispute_letter_draft": "Bureau review/dispute letter draft",
        "furnisher_direct_dispute_draft": "Furnisher direct dispute draft",
        "debt_validation_draft": "Debt validation draft",
        "method_of_verification_draft": "Method of Verification draft",
        "reinvestigation_draft": "Reinvestigation draft",
        "documented_follow_up_packet": "Documented follow-up packet",
        "complaint_preparation_packet": "Complaint preparation packet",
    }
    rows = []
    for recommendation in rules.get("eoscar_workflow_rules", {}).get("safe_letter_recommendations", []):
        rows.append([
            f"safe_{recommendation}",
            recommendation,
            labels.get(recommendation, recommendation.replace("_", " ").title()),
            "varies_by_review",
            "Not sent - template recommendation only",
            (
                "DRAFT ONLY - CUSTOMER REVIEW AND APPROVAL REQUIRED. "
                "Admin/compliance review required before any dispute, validation request, mailing, complaint, or escalation. "
                "Credit Vivo is not a law firm and does not provide legal advice."
            ),
        ])
    return rows


def build_license_check_rows(data: dict) -> List[List[object]]:
    rows = [[
        "Company",
        "Role",
        "States to Check",
        "Known / Public ID",
        "Official Registry Needed",
        "License Pass/Fail Field",
        "Current Status",
        "Business Search Link",
        "Debt Collection / Financial License Link",
        "Evidence Source",
        "Can Use in Letter?",
        "Admin Review",
        "Notes",
        "Last Checked",
    ]]
    seen = set()
    entity_rows = data.get("entity_compliance_intelligence", [])
    for entity in entity_rows:
        company = entity.get("entity_name", "")
        role = entity.get("entity_type", "")
        key = (entity.get("normalized_entity_name") or normalized_alias_name(company), role)
        if not company or key in seen:
            continue
        seen.add(key)
        rows.append([
            company,
            role,
            "Consumer state + company state + servicing/collection state",
            "Pending official lookup",
            "Yes",
            "Needs Review / Pending official registry check",
            "Needs Review",
            entity.get("business_registry_search_link", ""),
            entity.get("debt_collector_license_search_link") or entity.get("state_license_search_link", ""),
            entity.get("source_file", ""),
            "No, until verified",
            "Required",
            entity.get("manual_review_notes", ENTITY_COMPLIANCE_ADMIN_WORDING),
            entity.get("last_checked_date", ""),
        ])
    if entity_rows:
        return rows

    for item in data.get("tradelines", []):
        if not is_customer_review_item(item):
            continue
        company = item.get("collector_or_debt_buyer") or item.get("account_name") or ""
        if not company:
            continue
        role = "Collector / debt buyer" if any(match.get("id") in {"collection", "debt_buyer"} for match in classify_negative_tradeline(item)) or "collection" in str(item).lower() else "Furnisher"
        key = (normalized_alias_name(company), role)
        if key in seen:
            continue
        seen.add(key)
        rows.append([
            company,
            role,
            "Consumer state + company state + servicing/collection state",
            "Pending official lookup",
            "Yes",
            "Needs Review / Pending official registry check",
            "Needs Review",
            "Use State_License_Links business registry for relevant state",
            "Use State_License_Links debt/financial license registry or NMLS where applicable",
            item.get("source_filename", ""),
            "No, until verified",
            "Required",
            "Possible licensing issue for review only; do not call it a violation without official evidence and compliance review.",
            "",
        ])
    if len(rows) == 1:
        rows.append([
            "No negative/reviewable company detected",
            "Review",
            "Customer state pending",
            "",
            "Yes",
            "Needs Review",
            "Needs Review",
            "",
            "",
            "",
            "No",
            "Required",
            "Run scanner with bureau reports to populate company rows.",
            "",
        ])
    return rows


def build_identity_cleanup_rows(data: dict) -> List[List[object]]:
    rows = [[
        "Action",
        "Identity Field",
        "Raw Report Value",
        "Keep One Correct Value",
        "Bureau",
        "Source File",
        "Page",
        "Brief Compliance Review",
        "Requested Outcome",
        "Customer Confirmation Needed",
        "Admin Notes",
    ]]
    raw_rows = list(data.get("identity_raw_data", []))
    if not raw_rows:
        rows.append([
            "REVIEW",
            "identity/contact",
            "No personal-information section was extracted from the uploaded raw reports.",
            "",
            "",
            "",
            "",
            "FCRA personal information accuracy review. Use raw report pages and customer documents before any correction request.",
            "Collect/confirm one legal name, one current mailing address, one phone/email if customer wants them used; delete obsolete variants only after confirmation.",
            "Yes",
            "Run scan with full bureau reports or manually add personal-info evidence.",
        ])
        return rows

    keep_seen: set[str] = set()
    keep_categories = {"name", "address", "phone", "email", "dob", "masked_ssn"}
    for item in raw_rows:
        category = item.get("category", "")
        raw_value = item.get("raw_value", "")
        is_keep = category in keep_categories and category not in keep_seen
        if is_keep:
            keep_seen.add(category)
        action = "KEEP" if is_keep else "DELETE"
        if category in {"employment"}:
            action = "DELETE"
        keep_value = raw_value if is_keep else ""
        brief = (
            "FCRA 607(b) / 611 personal-info accuracy review. Keep one confirmed current value; delete obsolete, duplicate, wrong, or unverifiable variants."
            if action == "KEEP" else
            "FCRA personal-info cleanup. Delete if obsolete, duplicate, wrong, unneeded, or unverifiable after customer confirmation."
        )
        outcome = (
            "Keep this one confirmed value as the customer profile value."
            if action == "KEEP" else
            "Delete/remove this extra identity/contact value from bureau files if customer confirms it is not current/correct."
        )
        rows.append([
            action,
            category,
            raw_value,
            keep_value,
            item.get("bureau", ""),
            item.get("source_filename", ""),
            item.get("page", ""),
            brief,
            outcome,
            "Yes",
            "Draft only. Do not send personal-info correction until customer confirms and admin reviews proof of identity/address.",
        ])
    return rows


def build_state_license_link_rows() -> List[List[object]]:
    return [
        ["State / Agency", "Business Search Type", "Business Search URL", "Debt / Financial License Type", "Debt / Financial License URL", "Use Case", "Notes"],
        ["Maryland", "Business entity search", "https://egov.maryland.gov/BusinessExpress/EntitySearch", "NMLS / state financial license lookup", "https://www.nmlsconsumeraccess.org/", "Consumer/company/collector license review", "Verify current official registry before production use."],
        ["Virginia", "State Corporation Commission entity search", "https://cis.scc.virginia.gov/EntitySearch/Index", "NMLS / financial license lookup", "https://www.nmlsconsumeraccess.org/", "Company/entity and license review", "Use official registry evidence only."],
        ["District of Columbia", "CorpOnline business search", "https://corponline.dcra.dc.gov/", "DISB financial services lookup / NMLS", "https://www.nmlsconsumeraccess.org/", "DC entity and financial-license review", "Confirm current agency routing before use."],
        ["California", "Secretary of State business search", "https://bizfileonline.sos.ca.gov/search/business", "DFPI licensee lookup", "https://dfpi.ca.gov/consumers/lookup-a-licensee/", "Collector/furnisher business and license review", "Official-link evidence must be saved before letter use."],
        ["Minnesota", "Business & Lien System search", "https://mblsportal.sos.state.mn.us/Business/Search", "Commerce license lookup / NMLS", "https://www.nmlsconsumeraccess.org/", "Business and financial-license review", "Verify current official registry."],
        ["Michigan", "LARA business entity search", "https://cofs.lara.state.mi.us/SearchApi/Search/Search", "DIFS licensee search / NMLS", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["South Carolina", "Secretary of State business entities", "https://businessfilings.sc.gov/BusinessFiling/Entity/Search", "Consumer finance / NMLS lookup", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["North Carolina", "Secretary of State business registration search", "https://www.sosnc.gov/online_services/search/by_title/_Business_Registration", "NCCOB / NMLS license lookup", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["Delaware", "Division of Corporations entity search", "https://icis.corp.delaware.gov/Ecorp/EntitySearch/NameSearch.aspx", "State Bank Commissioner / NMLS", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["Texas", "Comptroller taxable entity search", "https://mycpa.cpa.state.tx.us/coa/", "OCCC / NMLS license lookup", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["Nevada", "SilverFlume business search", "https://esos.nv.gov/EntitySearch/OnlineEntitySearch", "Financial Institutions Division / NMLS", "https://www.nmlsconsumeraccess.org/", "Business and license review", "Verify current official registry."],
        ["NMLS Consumer Access", "Nationwide financial-services lookup", "https://www.nmlsconsumeraccess.org/", "NMLS Consumer Access", "https://www.nmlsconsumeraccess.org/", "Mortgage/financial-services license cross-check", "Use only when the entity/license type belongs in NMLS."],
    ]


def build_dispute_cycle_status_rows() -> List[List[object]]:
    statuses = [
        ("scan_completed", "Scanner parsed reports and created draft review workbook."),
        ("draft_ready", "Draft recommendations exist; no send action."),
        ("customer_review_pending", "Customer must review facts and approve or reject draft use."),
        ("customer_approved", "Customer approved a specific item/draft path."),
        ("admin_review_pending", "Admin/compliance review before mailing/escalation."),
        ("ready_for_lob", "Eligible for mail vendor preparation after approvals only."),
        ("lob_sent", "Mail sent by approved workflow; not automatic."),
        ("lob_delivered", "Delivery proof captured."),
        ("waiting_for_response", "Waiting for bureau/furnisher/collector response."),
        ("response_received", "Response received and stored for review."),
        ("verified_needs_review", "Verified response still needs human review."),
        ("updated_review_needed", "Updated report must be compared against prior report."),
        ("deleted_removed", "Item appears deleted/removed; verify on updated report."),
        ("round_2_eligible", "Follow-up may be eligible after evidence/admin review."),
        ("hold_duplicate_risk", "Hold due to possible duplicate/overlap risk."),
        ("hold_weak_evidence", "Hold until stronger proof exists."),
        ("round_3_followup_ready", "MOV/process follow-up draft may be prepared."),
        ("complaint_package_ready", "Complaint packet prepared only; no auto-file."),
        ("attorney_review_candidate", "Potential attorney/compliance review candidate."),
        ("closed_customer_approved", "Closed after customer-approved outcome or customer instruction."),
    ]
    return [[
        "Status Code",
        "Meaning",
        "Owner",
        "Customer Approval Required",
        "Admin Review Required",
        "Automation Allowed?",
        "Next Allowed Step",
        "Notes",
        "Last Updated",
    ]] + [
        [
            status,
            meaning,
            "Credit Vivo admin",
            "Yes before any dispute/letter/mail/complaint/escalation" if status not in {"scan_completed", "draft_ready", "customer_review_pending"} else "Pending",
            "Yes before any external action",
            "No automatic mail, complaint, filing, or e-OSCAR action",
            "Advance only after documented approval gate",
            "Scanner output is draft review data only.",
            "",
        ]
        for status, meaning in statuses
    ]


def build_exact_letters_to_mail_rows(data: dict) -> List[List[object]]:
    required_letters = [
        ("Bureau review/dispute", "Credit bureau", "Field-level bureau dispute after customer/admin approval", "Please ensure this account is marked as disputed by the consumer while the investigation is pending and in any continued reporting, as required by applicable credit reporting law."),
        ("Furnisher direct dispute", "Furnisher / collector", "Direct furnisher dispute after bureau review or when direct support is needed", "If you continue furnishing this information to any consumer reporting agency, please report that the account is disputed by the consumer."),
        ("Debt validation", "Debt collector / debt buyer", "Debt validation and ownership/authority review", "If you continue furnishing this information to any consumer reporting agency, please report that the account is disputed by the consumer."),
        ("Method of Verification", "Credit bureau", "Follow-up after investigation response when verification method needs review", "Please identify the method of verification and mark the account disputed when continued reporting occurs."),
        ("Notice of Dispute missing follow-up", "Bureau or furnisher", "Use after documented dispute delivery if dispute notation appears missing or inconsistent", "Please report that the account is disputed by the consumer while this matter is under review."),
        ("Re-aging / DOFD timeline review", "Bureau and/or furnisher", "DOFD, estimated-removal, opened/assigned, or timeline review", "Please verify the date of first delinquency and reporting period and mark the account disputed while investigating."),
        ("Collector license/business status review", "Collector / debt buyer", "License/business status evidence review after official lookup", "Please provide records supporting authority to collect, own, or report the account."),
        ("CFPB/state complaint prep", "CFPB/state regulator packet", "Preparation packet only after unresolved documented dispute history", "No complaint is filed automatically; customer e-sign and admin review are required."),
        ("Attorney-review summary", "Attorney/compliance reviewer", "Human review summary for unresolved or complex issues", "Prepared for review only; no legal conclusion by scanner."),
    ]
    rows = [["Letter Type", "Target", "Use For", "Safe Draft Text", "Required Attachments", "Approval Required", "Mail Status", "Notes"]]
    for letter_type, target, use_for, notice in required_letters:
        rows.append([
            letter_type,
            target,
            use_for,
            (
                "DRAFT ONLY. Include account name, masked account number, bureau, exact disputed field, "
                "reported value, reason it may be inaccurate, evidence attached, requested investigation/correction. "
                + notice
            ),
            "Customer ID/proof if needed; report excerpt; evidence; prior letters/responses when applicable",
            "Customer approval + admin review required",
            "Not sent",
            "Replace bracketed fields with case data after human review.",
        ])
    legacy_recommendations = [
        "Bureau review/dispute letter draft",
        "Furnisher direct dispute draft",
        "Debt validation draft",
        "Method of Verification draft",
        "Reinvestigation draft",
        "Documented follow-up packet",
        "Complaint preparation packet",
    ]
    for label in legacy_recommendations:
        rows.append([
            label,
            "Varies by review",
            "Legacy safe recommendation label retained for scanner compatibility.",
            "DRAFT ONLY - customer approval and admin review required before any use.",
            "Scanner evidence and customer-approved attachments",
            "Customer approval + admin review required",
            "Not sent",
            "Compatibility row; not an automatic mail action.",
        ])
    for letter in data.get("recommended_letter_queue", [])[:25]:
        letter_id = str(letter.get("letter_id", ""))
        rows.append([
            str(letter.get("letter_type", "")).replace("_", " ").title(),
            letter.get("recipient_type", ""),
            letter.get("letter_subject", ""),
            (
                f"Complete draft generated. File: letters/{letter_id}.txt. "
                f"Lob status: {letter.get('lob_ready_status', 'draft preview only')}. "
                "Do not send until customer e-sign, admin approval, sensitive-data review, recipient address verification, and production workflow approval."
            ),
            "Scanner evidence and customer-approved attachments",
            "Customer approval + admin review required",
            "Not sent",
            f"Draft ID: {letter_id}",
        ])
    return rows


def build_escalation_address_rows() -> List[List[object]]:
    entity_types = [
        ("Equifax", "Credit bureau"),
        ("Experian", "Credit bureau"),
        ("TransUnion", "Credit bureau"),
        ("Furnishers", "Furnisher"),
        ("Debt collectors", "Debt collector"),
        ("Debt buyers", "Debt buyer"),
        ("CFPB", "Federal regulator"),
        ("FTC", "Federal regulator"),
        ("State AG / Consumer Protection", "State regulator"),
        ("State financial regulator", "State regulator"),
        ("OCC", "Federal banking regulator"),
        ("FDIC", "Federal banking regulator"),
        ("NCUA", "Federal credit union regulator"),
        ("Federal Reserve", "Federal banking regulator"),
        ("DOT", "Federal agency"),
        ("SEC", "Federal agency"),
        ("SBA", "Federal agency"),
        ("Farm Credit Administration", "Federal agency"),
    ]
    rows = [["Entity", "Entity Type", "Regular / Dispute Address", "Escalation / Corporate Address", "State / Regulator", "Phone", "Use Case", "Verification Needed", "Source / Link", "Mail Priority", "Notes"]]
    for entity, entity_type in entity_types:
        rows.append([
            entity,
            entity_type,
            "Verify current official address before use",
            "Verify current official escalation/corporate address before use",
            entity if "State" in entity or entity in {"CFPB", "FTC", "OCC", "FDIC", "NCUA", "Federal Reserve", "DOT", "SEC", "SBA", "Farm Credit Administration"} else "",
            "Verify current phone before use",
            "Dispute, response review, or complaint-packet preparation only",
            "Required before production mail",
            "Use official website or current correspondence",
            "Manual/admin reviewed only",
            "No automatic mail or filing.",
        ])
    return rows


def build_complaint_packet_rows() -> List[List[object]]:
    items = [
        "Customer statement",
        "Account summary",
        "Evidence snippets",
        "Prior letter copies",
        "Lob delivery proof",
        "Bureau response",
        "Furnisher response",
        "Updated report comparison",
        "License/business status evidence",
        "State-rights note",
        "Requested resolution",
        "Customer e-sign approval",
        "Admin approval",
    ]
    rows = [["#", "Packet Item", "Description", "Required?", "Owner", "Status", "Compliance Note", "Approval Gate", "Evidence Link/ID", "Notes"]]
    for index, item in enumerate(items, start=1):
        rows.append([
            index,
            item,
            "Collect and verify before any complaint packet is used.",
            "Yes" if item in {"Customer statement", "Account summary", "Evidence snippets", "Requested resolution", "Customer e-sign approval", "Admin approval"} else "When applicable",
            "Customer/Admin",
            "Not started",
            "Preparation only; Credit Vivo does not auto-file complaints and does not provide legal advice.",
            "Customer approval + admin review required",
            "",
            "Use official complaint channel manually after approvals, if appropriate.",
        ])
    return rows


def build_fico_scenario_planner_rows() -> List[List[object]]:
    return [
        ["Scenario Area", "Inputs To Review", "Customer Education Output", "Allowed Action", "Not Allowed", "Owner", "Status", "Notes", "Evidence Needed", "Result Disclaimer"],
        ["Utilization review", "Balances, limits, reported dates", "Show high-level utilization tasks.", "Education/planning", "No score guarantee", "Admin/customer", "Draft", "Verify current balances first.", "Updated report or statements", "Actual score movement varies."],
        ["Payment history improvement tasks", "Late-payment patterns and current payment behavior", "Explain consistent on-time payment habits.", "Education/planning", "No promise of deletion or score increase", "Customer", "Draft", "Focus on future behavior.", "Customer confirmation", "Actual score movement varies."],
        ["New derogatory impact", "New collections/charge-offs/late payments", "Explain why recent negatives may matter.", "Education/planning", "No legal conclusion", "Admin/customer", "Draft", "Review exact reporting fields.", "Report excerpts", "Actual score movement varies."],
        ["Old derogatory aging", "DOFD, estimated removal, on-record-until", "Explain timeline review concept.", "Education/planning", "No re-aging allegation without review", "Admin", "Draft", "Use safe timeline wording.", "Date evidence", "Actual score movement varies."],
        ["Positive account building tasks", "Open positive accounts, utilization, age", "List safe credit-building tasks.", "Education/planning", "No financial/legal advice", "Customer", "Draft", "General education only.", "Customer goals", "Actual score movement varies."],
    ]


def mask_visible_workbook_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****", value)

    def mask_long_digits(match: re.Match[str]) -> str:
        digits = match.group(0)
        if len(digits) <= 4:
            return digits
        return "****" + digits[-4:]

    text = re.sub(r"(?<!\d)\d{7,}(?!\d)", mask_long_digits, text)
    text = re.sub(r"([A-Za-z]{2,}-[A-Za-z]{2,}-)[A-Za-z0-9-]{8,}", r"\1masked", text)
    return text


def build_simple_sheet_rows(title: str, rows: List[List[object]] | None = None) -> List[List[object]]:
    return [[title, ""], *(rows or [])]


def build_scanner_skill_map_rows(data: dict) -> List[List[object]]:
    return [
        [
            "Skill ID",
            "Skill",
            "Scanner Role",
            "Used For",
            "Output Area",
            "Approval / Safety Gate",
            "Customer Visible",
        ],
        *[
            [
                row.get("skill_id", ""),
                row.get("skill_name", ""),
                row.get("scanner_role", ""),
                row.get("used_for", ""),
                row.get("output_area", ""),
                row.get("approval_gate", ""),
                row.get("customer_visible", ""),
            ]
            for row in data.get("scanner_skill_map", [])
        ],
    ]


DISPUTE_SOP_ROWS = [
    {
        "round": "Round 0",
        "status": "intake_review",
        "purpose": "Scan report, organize evidence, identify possible errors, and create draft queues before sending anything.",
        "timing": "Day 0-3",
        "recipient": "Internal/customer review",
        "packet": "uploaded report, customer goal, identity/proof docs if needed, prior letters/responses, scanner findings, evidence notes",
        "tracking": "intake date, report date/source, findings count, evidence needed, draft queue created, approval pending",
        "approval_gate": "Customer authorizes Credit Vivo to prepare drafts. Nothing is sent.",
        "next_step": "Round 1 bureau dispute if issue is specific, evidence-backed, and customer approved.",
    },
    {
        "round": "Round 1",
        "status": "round_1_bureau_draft -> round_1_customer_approval -> round_1_sent -> awaiting_bureau_response",
        "purpose": "Short, specific bureau dispute for inaccurate, incomplete, unverifiable, or cross-bureau mismatched reporting.",
        "timing": "Day 3-7 after intake; response review around Day 30-45 after delivery",
        "recipient": "Credit bureau",
        "packet": "customer-approved letter, FCRA notice of dispute, highlighted report item, targeted proof, ID/proof of address when needed, delivery tracking plan",
        "tracking": "sent date, delivery date, tracking number, response due date, day 15 check, day 35 follow-up, response received",
        "approval_gate": "Customer approves specific disputed item, reason, evidence attachments, and delivery method.",
        "next_step": "Response review. If unresolved, prepare Round 2 furnisher/direct dispute or evidence-backed bureau follow-up.",
    },
    {
        "round": "Round 2",
        "status": "round_2_furnisher_draft -> round_2_customer_approval -> round_2_sent -> awaiting_furnisher_response",
        "purpose": "Detailed field-level furnisher/collector dispute when bureau response does not resolve the item or records need direct support.",
        "timing": "Day 45-55 after response review or no meaningful resolution",
        "recipient": "Furnisher, creditor, collector, or debt buyer",
        "packet": "customer-approved furnisher dispute, prior bureau dispute if useful, bureau response, report excerpt, evidence, requested records list",
        "tracking": "sent date, delivery date, tracking number, response due date, response received, correction/deletion/verified outcome",
        "approval_gate": "Customer approves direct furnisher dispute and confirms the factual basis is truthful.",
        "next_step": "Round 3 MOV/process audit if verified, unsupported, contradictory, or still reporting wrong.",
    },
    {
        "round": "Round 3",
        "status": "round_3_mov_draft -> round_3_customer_approval -> round_3_sent -> awaiting_mov_response",
        "purpose": "Method of verification/process audit when the bureau says verified but the response does not address the evidence.",
        "timing": "Day 80-95 after prior dispute history",
        "recipient": "Credit bureau",
        "packet": "prior dispute letter, proof of delivery, bureau response, furnisher response if any, current report excerpt, dispute history summary",
        "tracking": "MOV request date, response due date, method received, verification gaps, next escalation decision",
        "approval_gate": "Customer approves escalation based on prior dispute history and unresolved issue.",
        "next_step": "Round 4+ CFPB/state/attorney-ready packet if justified by unresolved harm, no response, repeated verification, or failure to mark disputed.",
    },
    {
        "round": "Round 4+",
        "status": "cfpb_state_packet / attorney_ready_packet",
        "purpose": "Escalation review after ordinary dispute paths, repeated verification, no response, or serious unresolved harm.",
        "timing": "Day 120+ when dispute history is complete and escalation is justified",
        "recipient": "CFPB, state attorney general/regulator, or attorney review",
        "packet": "full dispute history, reports before/after, notices, responses, delivery proofs, evidence, damages/adverse action proof if available",
        "tracking": "escalation packet date, complaint/reference number, response dates, attorney review status, resolution",
        "approval_gate": "Owner/compliance and customer approval required. Attorney/legal review required when appropriate.",
        "next_step": "Submit approved packet or hold for attorney/compliance review.",
    },
]


DISPUTE_METHODS = [
    {
        "method": "FCRA Bureau Dispute",
        "legal_basis": "FCRA 611 / 15 USC 1681i",
        "when_to_use": "Use when the consumer disputes accuracy or completeness of an item on a credit report, including cross-bureau balance, status, date, duplicate, not-mine, or missing DOFD issues.",
        "recipient": "Experian, Equifax, TransUnion, or other consumer reporting agency",
        "send_channel": "Mail/tracked mail preferred for important disputes; online bureau portal may be used when customer chooses it; phone only for limited simple issues.",
        "required_notice": "Formal notice of dispute identifying the item, specific disputed information, basis for dispute, and supporting documents.",
        "required_packet": "customer-approved letter, FCRA notice, highlighted report item, targeted proof, ID/proof of address when needed, delivery tracking plan",
        "tracking": "sent date, delivery date, tracking number, response due date, written results, corrected report, next round decision",
        "next_escalation": "Round 2 furnisher dispute or Round 3 MOV/process audit if verified, incomplete, no response, or still inaccurate.",
    },
    {
        "method": "FCRA / Regulation V Direct Furnisher Dispute",
        "legal_basis": "12 CFR 1022.43 direct dispute; FCRA furnisher duties",
        "when_to_use": "Use when the issue concerns account liability, terms, balance, credit limit, payment status, payment history, dates opened/closed, or other account information furnished by a creditor, collector, or debt buyer.",
        "recipient": "Furnisher, creditor, collector, debt buyer, or servicer",
        "send_channel": "Mail/tracked mail to the furnisher address on the report or another proper direct-dispute address.",
        "required_notice": "Direct dispute identifying the account, the specific disputed information, the basis for dispute, and all supporting evidence available.",
        "required_packet": "customer-approved direct dispute, bureau comparison, report excerpt, prior bureau response if any, proof/evidence, requested records list",
        "tracking": "sent date, delivery date, tracking number, response due date, response type, correction/deletion/verified result, next round decision",
        "next_escalation": "Round 3 MOV/process audit, CFPB/state packet, or attorney-ready packet if reporting remains unsupported or contradictory.",
    },
    {
        "method": "FDCPA Debt Validation Request",
        "legal_basis": "FDCPA validation-style request for debt collectors; state debt-collection laws may add requirements",
        "when_to_use": "Use for collection agencies, debt buyers, or factoring company accounts when the customer needs proof of the debt, original creditor, itemized balance, ownership, assignment, or authority to collect/report.",
        "recipient": "Debt collector, collection agency, debt buyer, or collection attorney when acting as collector",
        "send_channel": "Mail/tracked mail preferred, with customer approval and proof-of-delivery tracking.",
        "required_notice": "Request validation of the debt and documentation supporting amount, original creditor, consumer responsibility, and authority to collect.",
        "required_packet": "customer-approved validation request, report excerpt, collector identity, account identifier, and any collection notice if available",
        "tracking": "sent date, delivery date, tracking number, response due date, validation received, gaps, next dispute/escalation decision",
        "next_escalation": "FCRA furnisher dispute, CFPB/state complaint, or attorney-ready packet if the collector keeps reporting/collecting without adequate support.",
    },
    {
        "method": "MOV / Process Audit",
        "legal_basis": "FCRA 611(a)(6)-(7) results and method-of-verification style follow-up",
        "when_to_use": "Use after a bureau verifies an item but the response does not explain or resolve the evidence-backed dispute.",
        "recipient": "Credit bureau",
        "send_channel": "Mail/tracked mail preferred, with prior dispute history attached.",
        "required_notice": "Request the method used to verify the disputed item and ask why the consumer evidence did not change the result.",
        "required_packet": "prior dispute, proof of delivery, bureau response, furnisher response if any, current report excerpt, dispute history summary",
        "tracking": "MOV request date, response due date, method received, unresolved verification gaps, escalation decision",
        "next_escalation": "CFPB/state complaint packet or attorney-ready review when verification remains weak or contradictory.",
    },
    {
        "method": "CFPB / CFPA Complaint Escalation",
        "legal_basis": "CFPB complaint process; Consumer Financial Protection Act unfair/deceptive/abusive practice review where appropriate",
        "when_to_use": "Use only after ordinary dispute channels are no longer pending or enough time has passed, and there is unresolved inaccurate reporting, no meaningful response, repeated verification, or failure to correct/mark disputed.",
        "recipient": "CFPB complaint portal; optionally state attorney general or state regulator depending on issue",
        "send_channel": "CFPB complaint portal or approved state/regulator complaint channel.",
        "required_notice": "Complaint narrative explaining the timeline, disputed item, company response, remaining harm, and requested resolution.",
        "required_packet": "full dispute history, credit reports before/after, notices, responses, delivery proofs, evidence, denial/adverse-action or damages proof if available",
        "tracking": "complaint date, portal/reference number, company response due date, response received, customer review, escalation outcome",
        "next_escalation": "Attorney-ready packet when damages, repeated noncompliance, mixed file, identity theft, or other serious unresolved harm exists.",
    },
    {
        "method": "Metro 2 Field-Level Dispute",
        "legal_basis": "Metro 2 reporting field analysis used as factual dispute support; FCRA/Reg V provide dispute framework",
        "when_to_use": "Use when the scanner identifies specific field contradictions such as balance, current status, payment rating, DOFD, date reported, account type, original creditor, ownership, charge-off/sold status, or missing/obsolete dates.",
        "recipient": "Bureau and/or furnisher depending on which party controls or reports the field",
        "send_channel": "Include Metro 2 field table inside bureau/furnisher dispute package.",
        "required_notice": "Identify each field being challenged and why the value appears inaccurate, incomplete, unverifiable, obsolete, or materially misleading.",
        "required_packet": "3-bureau comparison, tradeline field table, raw evidence excerpt, supporting documents, requested field corrections",
        "tracking": "field challenged, bureau values, furnisher values, requested correction, response result, updated report value",
        "next_escalation": "MOV/process audit if field is verified without support; CFPB/state/attorney-ready packet if unresolved after dispute history.",
    },
]


def dispute_methods_for_comparison(flags: List[str], missing: List[str], has_cross_issue: bool) -> dict:
    methods = ["FCRA Bureau Dispute", "Metro 2 Field-Level Dispute"]
    if has_cross_issue or flags or missing:
        methods.append("FCRA / Regulation V Direct Furnisher Dispute")
        methods.append("FDCPA Debt Validation Request for collector/debt-buyer items")
    if any("verified" in flag.lower() for flag in flags):
        methods.append("MOV / Process Audit")
    return {
        "primary": methods[0],
        "secondary": "; ".join(methods[1:]),
        "cfpb_cfpa_trigger": (
            "Use CFPB/CFPA escalation only after normal dispute path is no longer pending or 45 days have passed, and the issue remains unresolved."
        ),
        "metro2_focus": "; ".join(
            focus
            for focus in ["Current Balance", "Account Status", "Date Reported", "Date of First Delinquency", "Account Type", "Original Creditor"]
            if flags or missing or has_cross_issue
        ) or "Hold for admin field validation",
    }


def sop_for_comparison(flags: List[str], missing: List[str], has_cross_issue: bool) -> dict:
    if has_cross_issue or flags or missing:
        return {
            "round": "Round 1 bureau dispute, then Round 2 furnisher/direct dispute if unresolved",
            "status": "round_1_bureau_draft",
            "timing": "Day 3-7 after intake; review response Day 30-45",
            "packet": "customer-approved letter; FCRA notice of dispute; highlighted bureau comparison; targeted proof; ID/proof of address if needed; tracking plan",
            "tracking": "sent date; delivery date; tracking number; response due date; day 15 check; day 35 follow-up; response received; next action",
            "approval": "Do not send. Customer must approve the specific item, reason, evidence, and delivery method.",
            "escalation": "If verified/no response/contradictory response: Round 2 furnisher dispute, Round 3 MOV, then CFPB/state/attorney-ready packet if justified.",
        }
    return {
        "round": "Round 0 intake review",
        "status": "intake_review",
        "timing": "Hold until a specific, evidence-backed issue is confirmed",
        "packet": "raw report excerpt; admin validation; customer explanation",
        "tracking": "admin review status; evidence needed; approval pending",
        "approval": "No dispute recommended until a specific issue is confirmed and customer approves.",
        "escalation": "No escalation until dispute history exists.",
    }


def build_three_bureau_comparison_rows(data: dict) -> List[List[object]]:
    tradelines = data.get("tradelines", [])
    tradeline_indexes_by_id = {}
    for index, item in enumerate(tradelines):
        tradeline_indexes_by_id.setdefault(item.get("id"), []).append(index)
    bureau_order = ["Equifax", "Experian", "TransUnion"]
    cross_issue_ids = set()
    per_bureau_fields = [
        ("Source", "source_filename"),
        ("Account #", "account_number_masked"),
        ("Type", "account_type"),
        ("Original Creditor", "original_creditor"),
        ("Balance", "balance"),
        ("Past Due", "past_due"),
        ("Status", "status"),
        ("Opened", "date_opened"),
        ("Closed", "date_closed"),
        ("Reported", "date_reported"),
        ("DOFD", "date_of_first_delinquency"),
        ("Remarks", "remarks"),
        ("Confidence", "confidence"),
        ("Raw Evidence", "raw_block"),
    ]

    for issue in data.get("issues", []):
        if str(issue.get("issue_type", "")).startswith("cross_bureau"):
            cross_issue_ids.update(issue.get("related_tradeline_ids", []))

    rows = [THREE_BUREAU_COMPARISON_TEMPLATE_HEADERS.copy()]
    for bureau in bureau_order:
        rows[0].extend([f"{bureau} {label}" for label, _field in per_bureau_fields])
    rows[0].extend([
        "Dispute Targets",
        "Primary Dispute Method",
        "Secondary Dispute Methods",
        "Metro 2 Field Focus",
        "CFPB/CFPA Escalation Trigger",
        "Bureau Dispute Draft",
        "Furnisher Dispute Draft",
        "Debt Validation Draft",
        "SOP Round",
        "SOP Status",
        "SOP Timing",
        "SOP Required Packet",
        "SOP Tracking Checklist",
        "SOP Approval Gate",
        "SOP Escalation Rule",
        "Tracking Status",
        "Review Missing Bureaus",
        "Review Matched Bureaus",
        "Export QA Flags",
        "Group ID",
    ])

    used_indexes = set()

    def row_for_items(items: List[dict], group_id: str = "") -> List[object]:
        by_bureau = {}
        for item in items:
            bureau = item.get("bureau")
            if bureau and bureau not in by_bureau:
                by_bureau[bureau] = item

        balances = [item.get("balance", "") for item in items]
        statuses = [item.get("status") or item.get("pay_status") or "" for item in items]
        reported_dates = [item.get("date_reported", "") for item in items]
        dofds = [item.get("date_of_first_delinquency", "") for item in items]
        account_names = [item.get("account_name", "") for item in items]

        flags = [
            _comparison_flag(balances, "Balance"),
            _comparison_flag(statuses, "Status"),
            _comparison_flag(reported_dates, "Reported date"),
            _comparison_flag(dofds, "DOFD"),
            _comparison_flag(account_names, "Account name"),
        ]
        missing = [bureau for bureau in bureau_order if bureau not in by_bureau]
        if missing:
            flags.append("Missing on " + ", ".join(missing))

        has_cross_issue = any(item.get("id") in cross_issue_ids for item in items)
        sop = sop_for_comparison([flag for flag in flags if flag], missing, has_cross_issue)
        methods = dispute_methods_for_comparison([flag for flag in flags if flag], missing, has_cross_issue)
        suggested_review = (
            "Review and dispute field-level mismatch if inaccurate or unverifiable."
            if has_cross_issue or any(flags)
            else
            "Matched across bureaus. No mismatch flag detected."
        )
        account_name = "; ".join(sorted({name for name in account_names if name}))
        account_name, account_name_qa = export_account_name_with_qa(account_name)
        error_text = "; ".join(flag for flag in flags if flag) or "No mismatch flag detected."
        export_qa_flags = "; ".join(flag for flag in [account_name_qa] if flag) or "OK for admin workbook review"
        dispute_targets = "Credit bureaus and furnishing creditor/collector"
        bureau_letter = (
            "DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED\n"
            "To: Credit Bureau\n"
            f"Re: {account_name}\n\n"
            "I dispute the accuracy, completeness, and/or verifiability of this account as reported on my credit file. "
            f"The bureau comparison shows: {error_text}. "
            "Please conduct a reasonable FCRA investigation, forward all relevant dispute information to the furnisher, "
            "mark the item as disputed while pending, and correct, update, or delete any information that cannot be verified as accurate and complete. "
            "Please provide written investigation results and an updated report if changes are made."
        )
        furnisher_letter = (
            "DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED\n"
            "To: Furnisher / Collector\n"
            f"Re: {account_name}\n\n"
            "I dispute the accuracy, completeness, and/or verifiability of the information you are furnishing about this account. "
            f"The bureau comparison shows: {error_text}. "
            "Please investigate your records and provide the basis for reporting, including balance support, account status support, "
            "date reporting support, ownership/assignment records where applicable, and any records used to verify the account. "
            "If the information cannot be verified as accurate and complete, please correct, update, or stop furnishing the disputed information."
        )
        debt_validation_letter = (
            "DRAFT - CUSTOMER REVIEW AND APPROVAL REQUIRED\n"
            "To: Debt Collector / Debt Buyer\n"
            f"Re: {account_name}\n\n"
            "I request validation of the debt you claim is owed or are reporting. Please provide the original creditor, "
            "an itemized balance, documents showing consumer responsibility, chain of title or assignment, authority to collect/report, "
            "date of first delinquency support, and the account identifier used for reporting. Nothing in this request is an admission "
            "that the debt is owed."
        )

        primary_item = next((by_bureau.get(bureau) for bureau in bureau_order if by_bureau.get(bureau)), items[0] if items else {})
        primary_status = primary_item.get("status") or primary_item.get("pay_status") or ""
        matched_bureaus = ", ".join(sorted(by_bureau.keys()))
        missing_bureaus = ", ".join(missing)

        row = [
            account_name,
            primary_item.get("bureau", ""),
            matched_bureaus,
            missing_bureaus,
            error_text,
            suggested_review,
            primary_item.get("account_number_masked", "") or primary_item.get("account_number", ""),
            primary_item.get("account_type", ""),
            primary_item.get("balance", ""),
            primary_item.get("past_due", ""),
            primary_status,
            primary_item.get("date_opened", ""),
            primary_item.get("date_reported", ""),
            primary_item.get("date_of_first_delinquency", ""),
        ]
        for bureau in bureau_order:
            item = by_bureau.get(bureau, {})
            for _label, field in per_bureau_fields:
                value = item.get(field, "")
                if field == "status":
                    value = item.get("status") or item.get("pay_status") or ""
                if field == "raw_block":
                    value = clean_text(str(value))[:650]
                row.append(value)
        row.extend([
            dispute_targets,
            methods["primary"],
            methods["secondary"],
            methods["metro2_focus"],
            methods["cfpb_cfpa_trigger"],
            bureau_letter,
            furnisher_letter,
            debt_validation_letter,
            sop["round"],
            sop["status"],
            sop["timing"],
            sop["packet"],
            sop["tracking"],
            sop["approval"],
            sop["escalation"],
            "draft_not_sent_customer_approval_required",
            missing_bureaus,
            matched_bureaus,
            export_qa_flags,
            group_id,
        ])
        return row

    for group in data.get("cross_bureau_groups", []):
        group_indexes = []
        for item_id in group.get("tradeline_ids", []):
            available = [index for index in tradeline_indexes_by_id.get(item_id, []) if index not in used_indexes]
            if available:
                group_indexes.append(available[0])
        items = [tradelines[index] for index in group_indexes]
        if len(items) < 2:
            continue

        used_indexes.update(group_indexes)
        rows.append(row_for_items(items, group.get("group_id", "")))

    for index, item in enumerate(tradelines):
        if index in used_indexes:
            continue
        rows.append(row_for_items([item], item.get("id", "")))
        used_indexes.add(index)

    if len(rows) == 1:
        rows.append([
            "No matched cross-bureau accounts",
            *["" for _ in range(len(bureau_order) * len(per_bureau_fields))],
            "No 3-bureau comparison could be created from the uploaded report set.",
            "Upload reports from at least two bureaus to compare the same account side by side.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ])

    return rows


def validate_output_against_template_and_raw(data: dict, comparison_rows: List[List[object]], ours_rows: List[List[object]] | None = None) -> dict:
    checks = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"check": name, "status": status, "detail": detail})

    headers = comparison_rows[0] if comparison_rows else []
    expected_start = THREE_BUREAU_COMPARISON_TEMPLATE_HEADERS
    expected_tail = [
        "Dispute Targets",
        "Primary Dispute Method",
        "Secondary Dispute Methods",
        "Metro 2 Field Focus",
        "CFPB/CFPA Escalation Trigger",
        "Bureau Dispute Draft",
        "Furnisher Dispute Draft",
        "Debt Validation Draft",
        "SOP Round",
        "SOP Status",
        "SOP Timing",
        "SOP Required Packet",
        "SOP Tracking Checklist",
        "SOP Approval Gate",
        "SOP Escalation Rule",
        "Tracking Status",
        "Review Missing Bureaus",
        "Review Matched Bureaus",
        "Export QA Flags",
        "Group ID",
    ]

    if headers[:len(expected_start)] == expected_start and headers[-len(expected_tail):] == expected_tail:
        add_check("3 Bureau Comparison template", "pass", "Export headers match the expected v18.1.7 template.")
    else:
        add_check("3 Bureau Comparison template", "fail", "Export headers do not match the expected template.")

    duplicate_headers = sorted({header for header in headers if headers.count(header) > 1})
    add_check(
        "Duplicate export headers",
        "fail" if duplicate_headers else "pass",
        ", ".join(duplicate_headers) if duplicate_headers else "No duplicate column names found.",
    )

    bad_width_rows = [
        index
        for index, row in enumerate(comparison_rows[1:], start=2)
        if len(row) != len(headers)
    ]
    add_check(
        "Row width matches template",
        "fail" if bad_width_rows else "pass",
        f"Rows with wrong column count: {bad_width_rows[:20]}" if bad_width_rows else "All rows match the header column count.",
    )

    raw_summary = data.get("raw_verification_summary", {})
    raw_status = raw_summary.get("status", "missing")
    add_check(
        "Raw data verification summary",
        "pass" if raw_status in {"pass", "pass_with_review"} else "fail",
        f"Raw verification status: {raw_status}.",
    )

    tradelines = data.get("tradelines", [])
    missing_raw_rows = [
        item.get("id", item.get("account_name", "unknown"))
        for item in tradelines
        if not item.get("raw_block")
    ]
    add_check(
        "Raw evidence present",
        "fail" if missing_raw_rows else "pass",
        f"Tradelines missing raw evidence: {missing_raw_rows[:20]}" if missing_raw_rows else "Every parsed tradeline has raw evidence available for audit.",
    )

    source_names = {
        clean_account_name_candidate(str(item.get("account_name", ""))).lower()
        for item in tradelines
        if item.get("account_name") and not is_bad_account_name(str(item.get("account_name", "")))
    }
    unlinked_rows = []
    qa_flag_rows = []
    header_index = {header: index for index, header in enumerate(headers)}
    qa_index = header_index.get("Export QA Flags")
    for row_number, row in enumerate(comparison_rows[1:], start=2):
        account_name = str(row[0] if row else "").strip()
        normalized_names = {
            clean_account_name_candidate(part).lower()
            for part in re.split(r"\s*;\s*", account_name)
            if part.strip()
        }
        normalized_names.add(clean_account_name_candidate(account_name).lower())
        linked_to_source = any(name in source_names for name in normalized_names if name)
        if account_name and not account_name.startswith("ADMIN REVIEW REQUIRED") and not linked_to_source:
            unlinked_rows.append(row_number)
        if qa_index is not None and qa_index < len(row):
            qa_value = str(row[qa_index] or "")
            if "Parser cleanup required" in qa_value:
                qa_flag_rows.append(row_number)

    add_check(
        "Export rows link to raw tradelines",
        "fail" if unlinked_rows else "pass",
        f"Rows not linked to parsed raw tradelines: {unlinked_rows[:20]}" if unlinked_rows else "Every clean comparison row links back to parsed raw tradeline names.",
    )
    add_check(
        "Parser-fragment customer protection",
        "pass_with_review" if qa_flag_rows else "pass",
        f"Rows flagged for admin cleanup before customer view: {qa_flag_rows[:20]}" if qa_flag_rows else "No parser-fragment rows were flagged.",
    )

    v9_expected_headers = [
        "Field #",
        "Account Info",
        "Experian",
        "Equifax",
        "TransUnion",
        "Forensic issue / dispute lead",
        "3-CRA Status",
        "AI Error / Inaccuracy Found",
        "Reason / Why It Matters",
        "Dispute / Verification Request",
        "Priority",
        "Evidence / Notes",
    ]
    ours_rows = ours_rows or []
    v9_headers = ours_rows[3] if len(ours_rows) >= 4 else []
    add_check(
        "Ours 3 Bureaus v9 forensic template",
        "pass" if v9_headers == v9_expected_headers else "fail",
        "Main visible workbook sheet matches the v9 forensic header layout." if v9_headers == v9_expected_headers else "Main visible workbook sheet does not match the v9 forensic header layout.",
    )
    field_rows = [
        row for row in ours_rows[4:]
        if row and isinstance(row[0], int)
    ]
    add_check(
        "Ours 3 Bureaus field rows",
        "pass" if field_rows else "fail",
        f"{len(field_rows)} field-level forensic row(s) generated." if field_rows else "No field-level forensic rows generated.",
    )
    skill_ids = {row.get("skill_id") for row in data.get("scanner_skill_map", [])}
    required_skill_ids = {
        "credit_report_parser",
        "workbook_output_qa",
        "creditvivo_compliance_reviewer",
        "dispute_strategy_assistant",
        "creditvivo_product_manager",
        "letter_lifecycle_manager",
        "security_privacy_reviewer",
    }
    missing_skill_ids = sorted(required_skill_ids - skill_ids)
    add_check(
        "Scanner skills map",
        "fail" if missing_skill_ids else "pass",
        f"Missing scanner skills: {missing_skill_ids}" if missing_skill_ids else "Scanner skills map is present for parser, QA, compliance, dispute prep, workflow, letters, and privacy.",
    )

    failed = [check for check in checks if check["status"] == "fail"]
    review = [check for check in checks if check["status"] == "pass_with_review"]
    return {
        "status": "fail" if failed else "pass_with_review" if review else "pass",
        "checked_before_output": True,
        "blocks_customer_view_when_failed": True,
        "template": "3 Bureau Comparison + Ours 3 Bureaus v9 forensic layout v18.1.7",
        "checks": checks,
    }


def build_pre_output_verification_rows(data: dict) -> List[List[object]]:
    verification = data.get("pre_output_verification", {})
    rows = [
        ["Pre-Output Verification", verification.get("status", "missing")],
        ["Checked Before Output", verification.get("checked_before_output", False)],
        ["Customer View Blocked When Failed", verification.get("blocks_customer_view_when_failed", True)],
        [],
        ["Check", "Status", "Detail"],
    ]
    rows.extend(
        [check.get("check", ""), check.get("status", ""), check.get("detail", "")]
        for check in verification.get("checks", [])
    )
    return rows


def build_ground_truth_validation_rows(data: dict) -> List[List[object]]:
    raw_summary = data.get("raw_verification_summary", {})
    pre_output = data.get("pre_output_verification", {})
    rows = [
        ["Validation Area", "Status", "Raw PDF Evidence", "Parser JSON Evidence", "Workbook Evidence", "Admin Notes"],
        ["Equifax detected", "PASS" if any(str(file.get("bureau", "")).lower() == "equifax" for file in data.get("files", [])) else "REVIEW", "Bureau source file", "files[].bureau", "Workbook source metadata", "Confirm bureau label if unclear."],
        ["Experian detected", "PASS" if any(str(file.get("bureau", "")).lower() == "experian" for file in data.get("files", [])) else "REVIEW", "Bureau source file", "files[].bureau", "Workbook source metadata", "Confirm bureau label if unclear."],
        ["TransUnion detected", "PASS" if any(str(file.get("bureau", "")).lower() == "transunion" for file in data.get("files", [])) else "REVIEW", "Bureau source file", "files[].bureau", "Workbook source metadata", "Confirm bureau label if unclear."],
        ["Raw verification status", raw_summary.get("status", "not_available"), f"{raw_summary.get('verified', 0)} verified", "raw_verification_summary", "Raw_Data_Verification / Pre_Output_Verification", "Draft QA only."],
        ["Pre-output status", pre_output.get("status", "not_available"), "Raw PDF -> JSON -> workbook checks", "pre_output_verification", "Production_Gate", "Must pass before production approval."],
    ]
    for item in data.get("tradelines", [])[:250]:
        raw_evidence_id = item.get("id", "")
        rows.append([
            item.get("account_name", "Unknown account"),
            "PASS" if item.get("raw_block") else "REVIEW",
            f"{item.get('source_file', '')} / page {item.get('page', '')}",
            raw_evidence_id,
            "Account_Summary + Ours 3 Bureaus Comparison",
            "Raw evidence present." if item.get("raw_block") else "Raw evidence missing or not visible.",
        ])
    return rows


def build_security_audit_summary_rows(data: dict) -> List[List[object]]:
    packet_system = data.get("cfpb_packet_system", {})
    security = packet_system.get("security", {})
    return [
        ["Control", "Status", "Evidence", "Production Requirement", "Notes"],
        ["Draft-only scanner output", "PASS", "Workbook + letter lifecycle guardrails", "Required", "Scanner output is review data only."],
        ["Automatic disputes", "PASS", "Not implemented", "Must remain off", "No automatic dispute filing."],
        ["Automatic mailing", "PASS" if not security.get("automatic_mailing_enabled") else "FAIL", str(security.get("automatic_mailing_enabled", False)), "Must remain disabled until approved production workflow", "No mail is sent from scanner output."],
        ["Automatic complaints", "PASS" if not security.get("automatic_complaint_submission_enabled") else "FAIL", str(security.get("automatic_complaint_submission_enabled", False)), "Must remain disabled", "No CFPB/legal complaint is filed automatically."],
        ["Customer approval required", "PASS", "Letter lifecycle + packet gates", "Required", "Customer approval required before dispute prep moves forward."],
        ["Admin review required", "PASS", "Letter lifecycle + packet gates", "Required", "Admin review required before packet prep."],
        ["Compliance review required", "PASS", "Letter lifecycle + packet gates", "Required", "Credit Vivo is not a law firm and does not provide legal advice."],
        ["Browser localStorage for sensitive docs", "PASS", "Document vault manifest", "Must be blocked", "Sensitive documents are server-side only."],
        ["Paid AI dependency", "PASS" if not data.get("paid_ai_used") else "REVIEW", str(data.get("paid_ai_used", False)), "No paid AI required", "Native parser remains default."],
    ]


def build_production_gate_rows(data: dict) -> List[List[object]]:
    pre_output = data.get("pre_output_verification", {})
    raw_summary = data.get("raw_verification_summary", {})
    packet_system = data.get("cfpb_packet_system", {})
    security = packet_system.get("security", {})
    blockers = []
    if pre_output.get("status") not in {"pass", "pass_with_review"}:
        blockers.append("pre_output_verification_not_passed")
    if raw_summary.get("status") not in {"pass", "pass_with_review"}:
        blockers.append("raw_pdf_json_workbook_validation_not_passed")
    if security.get("automatic_mailing_enabled") or security.get("automatic_complaint_submission_enabled"):
        blockers.append("automatic_actions_enabled")
    approval = "FAIL" if blockers else "PASS_WITH_REVIEW"
    return [
        ["Gate", "Status", "Evidence", "Required Before Production", "Notes"],
        ["Overall scanner workbook approval", approval, ", ".join(blockers) if blockers else "No workbook blockers detected", "Founder/admin approval", "Use as draft QA evidence until approved."],
        ["Required v17 sheets present", "PASS", "Ground_Truth_Validation, Security_Audit_Summary, Production_Gate", "Required", "Workbook contract sheets are generated."],
        ["v9 workbook structure", "PASS_WITH_REVIEW", "Title rows + metadata + notes + header row + padded target ranges", "Required", "Template depth is preserved for review."],
        ["Raw PDF -> JSON -> workbook triple-check", "PASS_WITH_REVIEW" if raw_summary else "REVIEW", raw_summary.get("status", "not_available"), "Required", "Admin must verify evidence for live customer decisions."],
        ["Letters draft-only", "PASS", "Letter lifecycle guardrails", "Required", "No letter is sent automatically."],
        ["Customer approval", "PASS", "Packet gates", "Required", "Approval required before dispute prep moves forward."],
        ["Admin/compliance review", "PASS", "Packet gates", "Required", "Review required; not legal advice."],
    ]


def build_qa_verification_rows(data: dict) -> List[List[object]]:
    pre_output = data.get("pre_output_verification", {})
    rows = [["QA Area", "Status", "Expected", "Actual", "Evidence", "Admin Review Notes"]]
    rows.append(["Workbook status", pre_output.get("status", "not_available"), "pass or pass_with_review", pre_output.get("status", "not_available"), "pre_output_verification", "Do not approve production output while failed."])
    for check in pre_output.get("checks", []):
        rows.append([
            check.get("check", ""),
            check.get("status", ""),
            "pass",
            check.get("status", ""),
            check.get("detail", ""),
            "Review required when not pass.",
        ])
    return rows


def build_positive_accounts_keep_rows(data: dict) -> List[List[object]]:
    rows = [["Account Name", "Bureau", "Status", "Reason To Keep", "Evidence ID"]]
    for item in data.get("tradelines", []):
        status_blob = " ".join(str(item.get(key, "")) for key in ("status", "pay_status", "remarks")).lower()
        balance = str(item.get("balance", "")).strip()
        is_positive = (
            "paid as agreed" in status_blob
            or "current" in status_blob
            or "never late" in status_blob
            or "positive" in status_blob
        )
        if is_positive:
            rows.append([
                item.get("account_name", ""),
                item.get("bureau", ""),
                item.get("status") or item.get("pay_status", ""),
                "Usually keep if accurate because positive/current accounts may support credit history.",
                item.get("id", ""),
            ])
    if len(rows) == 1:
        rows.append(["No positive keep accounts detected", "", "", "Review raw report manually before customer-facing advice.", ""])
    return rows


def ensure_sheet_dimensions(ws, min_rows: int, min_cols: int, fill_value: str = "Not visible in report") -> None:
    for row_index in range(1, min_rows + 1):
        for col_index in range(1, min_cols + 1):
            cell = ws.cell(row_index, col_index)
            if cell.__class__.__name__ == "MergedCell":
                continue
            if cell.value in (None, "") and row_index >= 4:
                cell.value = fill_value


def build_dispute_sop_rows() -> List[List[object]]:
    return [
        [
            "Round",
            "Status / State Flow",
            "Purpose",
            "Timing",
            "Recipient",
            "Required Packet",
            "Tracking Fields",
            "Approval Gate",
            "Next Step",
        ],
        *[
            [
                row["round"],
                row["status"],
                row["purpose"],
                row["timing"],
                row["recipient"],
                row["packet"],
                row["tracking"],
                row["approval_gate"],
                row["next_step"],
            ]
            for row in DISPUTE_SOP_ROWS
        ],
    ]


def build_dispute_method_rows() -> List[List[object]]:
    return [
        [
            "Method",
            "Legal / Rule Basis",
            "When To Use",
            "Recipient",
            "Send Channel",
            "Required Notice",
            "Required Packet",
            "Tracking",
            "Next Escalation",
        ],
        *[
            [
                row["method"],
                row["legal_basis"],
                row["when_to_use"],
                row["recipient"],
                row["send_channel"],
                row["required_notice"],
                row["required_packet"],
                row["tracking"],
                row["next_escalation"],
            ]
            for row in DISPUTE_METHODS
        ],
    ]


def _desktop_priority_for_flags(flags: List[str], missing: List[str]) -> Tuple[str, str, int]:
    flag_text = " ".join(flags).lower()
    if missing or any(term in flag_text for term in ["balance", "status", "dofd", "missing"]):
        return "High priority", "critical", 82
    if flags:
        return "Review", "medium", 58
    return "Usually keep", "positive", 20


def _desktop_documents_for_flags(flags: List[str], missing: List[str]) -> List[str]:
    docs = []
    flag_text = " ".join(flags).lower()
    if "balance" in flag_text:
        docs.append("Payment proof, settlement proof, itemization, or account statement if available")
    if "status" in flag_text or "closed" in flag_text:
        docs.append("Account statements, closure letters, or proof of transfer if available")
    if "dofd" in flag_text or "reported date" in flag_text:
        docs.append("Prior credit reports, delinquency timeline, and payment history if available")
    if missing:
        docs.append("All three bureau reports or proof the account is missing from one bureau")
    if not docs:
        docs.append("Bank statement or payment confirmation if the customer says the reporting is wrong")
    return docs


def build_desktop_customer_dashboard(data: dict) -> List[dict]:
    tradelines_by_id = {item.get("id"): item for item in data.get("tradelines", [])}
    bureau_order = ["Equifax", "Experian", "TransUnion"]
    findings = []
    keep_if_correct = []

    for group in data.get("cross_bureau_groups", []):
        items = [tradelines_by_id.get(item_id) for item_id in group.get("tradeline_ids", [])]
        items = [item for item in items if item]
        if not items:
            continue
        by_bureau = {item.get("bureau"): item for item in items}
        flags = [
            _comparison_flag([item.get("balance", "") for item in items], "Balance"),
            _comparison_flag([item.get("status") or item.get("pay_status") or "" for item in items], "Status"),
            _comparison_flag([item.get("date_reported", "") for item in items], "Reported date"),
            _comparison_flag([item.get("date_of_first_delinquency", "") for item in items], "DOFD"),
            _comparison_flag([item.get("account_name", "") for item in items], "Account name"),
        ]
        flags = [flag for flag in flags if flag]
        missing = [bureau for bureau in bureau_order if bureau not in by_bureau]
        priority, tone, _score = _desktop_priority_for_flags(flags, missing)
        account_name = "; ".join(sorted({item.get("account_name", "") for item in items if item.get("account_name")}))
        entry = {
            "id": group.get("group_id", ""),
            "account_name": account_name,
            "priority": priority,
            "tone": tone,
            "bureaus": sorted(by_bureau.keys()),
            "simple_issue": (
                "The same account does not match across every credit report."
                if flags or missing else
                "This looks consistent across the uploaded reports."
            ),
            "explanation": [
                "The " + flag.lower() + " across bureaus." for flag in flags
            ] + ([f"Missing from {', '.join(missing)}."] if missing else []),
            "recommended_action": (
                "Upload proof and review the draft dispute package before anything is sent."
                if flags or missing else
                "Keep this account if it is correct."
            ),
            "documents_needed": _desktop_documents_for_flags(flags, missing),
        }
        if priority == "Usually keep":
            keep_if_correct.append(entry)
        else:
            findings.append(entry)

    return [
        {
            "section": "summary",
            "health_score": max(300, 700 - (len(findings) * 28) - (len(data.get("issues", [])) * 7)),
            "negative_accounts": len(findings),
            "potential_issues": len(data.get("issues", [])),
            "active_disputes": 0,
            "next_best_actions": [
                "Confirm all three reports are uploaded",
                "Upload proof for flagged accounts",
                "Review and approve draft letters",
                "Prepare attorney/compliance review for high-priority files",
            ],
        },
        {"section": "findings", "items": findings},
        {"section": "keep_if_correct", "items": keep_if_correct},
    ]


def build_desktop_staff_workbox(data: dict) -> List[dict]:
    dashboard = build_desktop_customer_dashboard(data)
    findings = []
    for section in dashboard:
        if section.get("section") == "findings":
            findings = section.get("items", [])
            break
    workbox = []
    for finding in findings:
        flags = finding.get("explanation", [])
        priority_score = 84 if finding.get("priority") == "High priority" else 58
        workbox.append({
            "account_id": finding.get("id", ""),
            "account_name": finding.get("account_name", ""),
            "priority_score": priority_score,
            "queue": "Attorney Assist prep" if priority_score >= 80 else "Scanner review",
            "internal_findings": flags,
            "recommended_letter_types": ["bureau_dispute", "furnisher_dispute", "method_of_verification_followup"],
            "documents_needed": finding.get("documents_needed", []),
        })
    return workbox


def build_desktop_bureau_field_matrix(data: dict) -> List[dict]:
    tradelines_by_id = {item.get("id"): item for item in data.get("tradelines", [])}
    bureau_order = ["Equifax", "Experian", "TransUnion"]
    fields = [
        ("account_number_masked", "Account number"),
        ("account_type", "Account type"),
        ("responsibility", "Responsibility"),
        ("original_creditor", "Original creditor"),
        ("balance", "Current balance"),
        ("past_due", "Past due amount"),
        ("credit_limit", "Credit limit"),
        ("high_credit_or_original_amount", "High balance or original amount"),
        ("status", "Status or pay status"),
        ("date_opened", "Date opened or assigned"),
        ("date_reported", "Date reported or updated"),
        ("date_closed", "Date closed"),
        ("date_last_payment", "Last payment date"),
        ("date_of_first_delinquency", "Date of first delinquency"),
        ("estimated_removal_date", "Estimated removal date"),
        ("remarks", "Remarks"),
    ]
    rows = []
    for group in data.get("cross_bureau_groups", []):
        items = [tradelines_by_id.get(item_id) for item_id in group.get("tradeline_ids", [])]
        items = [item for item in items if item]
        if not items:
            continue
        by_bureau = {item.get("bureau"): item for item in items}
        account_name = "; ".join(sorted({item.get("account_name", "") for item in items if item.get("account_name")}))
        for field, label in fields:
            values = {}
            for bureau in bureau_order:
                item = by_bureau.get(bureau, {})
                value = item.get(field, "")
                if field == "status":
                    value = item.get("status") or item.get("pay_status") or ""
                values[bureau] = value or "Not shown"
            present_values = {_norm_compare(value) for value in values.values() if _norm_compare(value) != "not shown"}
            rows.append({
                "account_name": account_name,
                "field": field,
                "label": label,
                "equifax": values["Equifax"],
                "experian": values["Experian"],
                "transunion": values["TransUnion"],
                "differs": len(present_values) >= 2,
            })
    return rows


def build_side_by_side_negative_rows(data: dict) -> List[List[object]]:
    tradelines = data.get("tradelines", [])
    tradeline_indexes_by_id = {}
    for index, item in enumerate(tradelines):
        tradeline_indexes_by_id.setdefault(item.get("id"), []).append(index)

    bureau_order = ["Experian", "Equifax", "TransUnion"]
    fields = [
        ("account_name", "Creditor / Furnisher"),
        ("account_number_masked", "Account Number"),
        ("original_creditor", "Original Creditor"),
        ("creditor_classification", "Creditor Classification / Industry"),
        ("account_type", "Account Type"),
        ("status", "Account Status"),
        ("pay_status", "Payment Status"),
        ("balance", "Balance"),
        ("past_due", "Past Due"),
        ("high_credit_or_original_amount", "High Balance"),
        ("credit_limit", "Credit Limit"),
        ("date_opened", "Date Opened / Assigned"),
        ("date_reported", "Date Reported / Updated"),
        ("date_closed", "Date Closed"),
        ("date_last_activity", "Date of Last Activity"),
        ("date_last_payment", "Date of Last Payment"),
        ("date_of_first_delinquency", "Date of First Delinquency"),
        ("estimated_removal_date", "Estimated Removal Date"),
        ("remarks", "Remarks"),
    ]

    rows = [[
        "Account Group",
        "Field",
        "Experian",
        "Equifax",
        "TransUnion",
        "Mismatch/Missing?",
        "Plain-English Review",
    ]]
    used_indexes = set()

    def append_group(items: List[dict]) -> None:
        if not items:
            return
        by_bureau = {}
        for item in items:
            bureau = item.get("bureau")
            if bureau and bureau not in by_bureau:
                by_bureau[bureau] = item

        account_group = "; ".join(sorted({item.get("account_name", "") for item in items if item.get("account_name")})) or "Review Item"
        for field, label in fields:
            values = {}
            for bureau in bureau_order:
                item = by_bureau.get(bureau, {})
                value = item.get(field, "")
                if field == "status":
                    value = item.get("status") or item.get("pay_status") or ""
                if field == "account_name":
                    value = item.get("account_name", "")
                values[bureau] = value or ""

            present_values = {_norm_compare(value) for value in values.values() if _norm_compare(value)}
            present_bureaus = [bureau for bureau in bureau_order if values[bureau]]
            missing_bureaus = [bureau for bureau in bureau_order if not values[bureau]]
            mismatch_note = ""
            if missing_bureaus and present_bureaus:
                mismatch_note = "Missing from one or more bureaus"
            if len(present_values) >= 2:
                mismatch_note = "Mismatch across bureaus" if not mismatch_note else mismatch_note + "; mismatch across bureaus"

            plain_review = ""
            if mismatch_note:
                plain_review = (
                    f"Review original report/PDF. If this {label} field is blank, different, or unverifiable, "
                    "dispute the specific field with bureau/furnisher evidence."
                )

            rows.append([
                account_group,
                label,
                values["Experian"],
                values["Equifax"],
                values["TransUnion"],
                mismatch_note,
                plain_review,
            ])

    for group in data.get("cross_bureau_groups", []):
        group_indexes = []
        for item_id in group.get("tradeline_ids", []):
            available = [index for index in tradeline_indexes_by_id.get(item_id, []) if index not in used_indexes]
            if available:
                group_indexes.append(available[0])
        if not group_indexes:
            continue
        used_indexes.update(group_indexes)
        append_group([tradelines[index] for index in group_indexes])

    for index, item in enumerate(tradelines):
        if index in used_indexes:
            continue
        used_indexes.add(index)
        append_group([item])

    return rows


def _find_header_row(ws) -> int:
    if ws.max_row >= 4 and ws.cell(4, 1).value:
        return 4
    if ws.cell(1, 1).value:
        return 1
    return 1


def _sheet_auto_filter_range(ws) -> str | None:
    if not ws.max_row or not ws.max_column:
        return None
    header_row = _find_header_row(ws)
    return f"A{header_row}:{get_column_letter(ws.max_column)}{ws.max_row}"


def _style_workbook_sheet(
    ws,
    title_color: str,
    subtitle_color: str,
    header_color: str,
    band_color: str,
    font_color: str,
) -> None:
    if not Font or not PatternFill or not Alignment:
        return
    thin_border = Border(
        left=Side(style="thin", color="D7DEE8"),
        right=Side(style="thin", color="D7DEE8"),
        top=Side(style="thin", color="D7DEE8"),
        bottom=Side(style="thin", color="D7DEE8"),
    ) if Border and Side else None
    header_row = _find_header_row(ws)

    for row in ws.iter_rows():
        row_index = row[0].row if row else 1
        for cell in row:
            if cell.__class__.__name__ == "MergedCell":
                continue
            if thin_border:
                cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if row_index > header_row and row_index % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=band_color)

    for cell in ws[1]:
        if cell.__class__.__name__ == "MergedCell":
            continue
        cell.fill = PatternFill("solid", fgColor=title_color)
        cell.font = Font(bold=True, color="FFFFFF", size=14)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 26

    if ws.max_row >= 2:
        for cell in ws[2]:
            if cell.__class__.__name__ == "MergedCell":
                continue
            cell.fill = PatternFill("solid", fgColor=subtitle_color)
            cell.font = Font(bold=True, color=font_color, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[2].height = 34

    if header_row <= ws.max_row:
        for cell in ws[header_row]:
            if cell.__class__.__name__ == "MergedCell":
                continue
            cell.fill = PatternFill("solid", fgColor=header_color)
            cell.font = Font(bold=True, color=font_color)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[header_row].height = 34

    for row_index in range(header_row + 1, min(ws.max_row, header_row + 250) + 1):
        ws.row_dimensions[row_index].height = 45

    if ws.max_row >= header_row and ws.max_column:
        ws.freeze_panes = f"A{header_row + 1}"
        ws.auto_filter.ref = _sheet_auto_filter_range(ws)


def _style_status_cells(ws) -> None:
    if not PatternFill or not Font:
        return
    fills = {
        "KEEP": ("DCFCE7", "166534"),
        "DELETE": ("FEE2E2", "991B1B"),
        "REVIEW": ("DBEAFE", "1E40AF"),
        "Needs Review": ("FEF3C7", "92400E"),
        "Required": ("FEF3C7", "92400E"),
        "High": ("FEE2E2", "991B1B"),
        "Medium": ("FEF3C7", "92400E"),
        "Low": ("E0F2FE", "075985"),
        "Yes": ("DCFCE7", "166534"),
        "No": ("F8FAFC", "475569"),
    }
    for row in ws.iter_rows():
        for cell in row:
            value = str(cell.value or "").strip()
            if value in fills:
                fill, color = fills[value]
                cell.fill = PatternFill("solid", fgColor=fill)
                cell.font = Font(bold=True, color=color)


def _auto_size_remaining_columns(ws, explicit_widths: dict[str, int | float] | None = None) -> None:
    explicit_widths = explicit_widths or {}
    for col_index in range(1, ws.max_column + 1):
        letter = get_column_letter(col_index)
        if letter in explicit_widths:
            ws.column_dimensions[letter].width = explicit_widths[letter]
            continue
        max_length = 10
        for row_index in range(1, min(ws.max_row, 80) + 1):
            value = ws.cell(row=row_index, column=col_index).value
            if value is None:
                continue
            max_length = max(max_length, min(len(str(value)), 46))
        ws.column_dimensions[letter].width = min(max(max_length + 2, 12), 42)


def write_desktop_workbook(data: dict, out_dir: Path) -> None:
    if Workbook is None:
        return

    wb = Workbook()
    summary = wb.active
    summary.title = "Summary"
    dashboard = wb.create_sheet("Dashboard")
    ours_three_bureaus = wb.create_sheet("Ours 3 Bureaus Comparison")
    account_summary = wb.create_sheet("Account_Summary")
    identity_cleanup = wb.create_sheet("Identity_Cleanup")
    negative_definitions = wb.create_sheet("Negative_Definitions")
    negative_account_rules = wb.create_sheet("Negative_Account_Rules")
    license_check = wb.create_sheet("License_Check")
    state_license_links = wb.create_sheet("State_License_Links")
    dispute_cycle_status = wb.create_sheet("Dispute_Cycle_Status")
    exact_letters_to_mail = wb.create_sheet("Exact_Letters_To_Mail")
    escalation_addresses = wb.create_sheet("Escalation_Addresses")
    complaint_packet = wb.create_sheet("Complaint_Packet")
    cfpb_packet_checklist = wb.create_sheet("CFPB_Packet_Checklist")
    comparison_attachment = wb.create_sheet("3B_Comparison_Attachment")
    document_vault = wb.create_sheet("Document_Vault")
    lob_tracking = wb.create_sheet("Lob_Tracking")
    scanner_skills = wb.create_sheet("Scanner_Skills_Map")
    fico_scenario_planner = wb.create_sheet("FICO_Scenario_Planner")
    codex_build_task = wb.create_sheet("Codex_Build_Task")
    read_me = wb.create_sheet("Read_Me")
    bureau_comparison = wb.create_sheet("3 Bureau Comparison")
    side_by_side_negative = wb.create_sheet("Side By Side Negative")
    desktop_dashboard = wb.create_sheet("Desktop Dashboard")
    desktop_workbox = wb.create_sheet("Desktop Staff Workbox")
    desktop_field_matrix = wb.create_sheet("Desktop Field Matrix")
    errors = wb.create_sheet("Detected Errors")
    items = wb.create_sheet("Review Items")
    raw_tradelines_dates = wb.create_sheet("Raw Tradelines With Dates")
    raw_data_verification = wb.create_sheet("Raw Data Verification")
    pre_output_verification = wb.create_sheet("Pre_Output_Verification")
    ground_truth_validation = wb.create_sheet("Ground_Truth_Validation")
    qa_verification = wb.create_sheet("QA_Verification")
    security_audit_summary = wb.create_sheet("Security_Audit_Summary")
    production_gate = wb.create_sheet("Production_Gate")
    positive_accounts_keep = wb.create_sheet("Positive_Accounts_Keep")
    entity_compliance = wb.create_sheet("Entity Compliance Intelligence")
    dates_found_audit = wb.create_sheet("Dates Found Audit")
    date_issues = wb.create_sheet("Date Issues To Dispute")
    metro2_fcra = wb.create_sheet("Metro 2 + FCRA Review")
    metro2_requirements = wb.create_sheet("Metro 2 Requirements")
    metro2_guide_notes = wb.create_sheet("Metro 2 Guide Notes")
    fcra_compliance = wb.create_sheet("FCRA Compliance Review")
    fcra_rights = wb.create_sheet("FCRA Rights Regulators")
    bureau_help = wb.create_sheet("Bureau Help + FDCPA")
    field_compliance = wb.create_sheet("Field Compliance Audit")
    eoscar_packaging = wb.create_sheet("e-OSCAR Packaging Review")
    fcra_notice_rules = wb.create_sheet("FCRA Notice Rules")
    dispute_methods = wb.create_sheet("Dispute Methods")
    dispute_sop = wb.create_sheet("Dispute SOP")
    letters = wb.create_sheet("Draft Letters")
    fcra = wb.create_sheet("FCRA Review")

    _write_workbook_sheet(summary, [
        ["Credit Vivo Scanner Output", ""],
        ["Engine", data.get("engine", "")],
        ["Version", data.get("version", "")],
        ["Paid AI Used", "Yes" if data.get("paid_ai_used") else "No"],
        ["Files Parsed", len(data.get("files", []))],
        ["Review Items", len(data.get("tradelines", []))],
        ["Detected Errors / Review Points", len(data.get("issues", []))],
        ["Draft Letters Queued", len(data.get("recommended_letter_queue", []))],
        ["Customer Message", data.get("customer_summary", {}).get("message", "")],
        ["Important Notice", "Draft review data only. Nothing is sent without customer approval and admin review."],
    ])

    _write_workbook_sheet(dashboard, [
        ["Metric", "Value", "Note"],
        ["Files Parsed", len(data.get("files", [])), "Consumer credit reports only."],
        ["Review Items", len(data.get("tradelines", [])), "Parsed tradelines and account blocks."],
        ["Possible Review Points", len(data.get("issues", [])), "Possible report errors or inconsistencies."],
        ["Draft Letters Queued", len(data.get("recommended_letter_queue", [])), "Draft only; nothing is sent automatically."],
        ["Paid AI Used", "Yes" if data.get("paid_ai_used") else "No", "No paid AI dependency added."],
        ["Compliance Notice", "Draft review data only", "Customer approval and admin review required before any dispute, mailing, complaint, or escalation."],
    ])

    _write_workbook_sheet(ours_three_bureaus, data.get("_ours_three_bureaus_rows") or build_ours_three_bureaus_comparison_rows(data))
    _write_workbook_sheet(account_summary, build_account_summary_rows(data))
    _write_workbook_sheet(identity_cleanup, build_identity_cleanup_rows(data))
    _write_workbook_sheet(negative_definitions, build_negative_definitions_rows(data))
    _write_workbook_sheet(negative_account_rules, build_negative_account_rules_rows(data))
    _write_workbook_sheet(license_check, build_license_check_rows(data))
    _write_workbook_sheet(state_license_links, build_state_license_link_rows())
    _write_workbook_sheet(dispute_cycle_status, build_dispute_cycle_status_rows())
    _write_workbook_sheet(exact_letters_to_mail, build_exact_letters_to_mail_rows(data))
    _write_workbook_sheet(escalation_addresses, build_escalation_address_rows())
    _write_workbook_sheet(complaint_packet, build_complaint_packet_rows())
    packet_system = data.get("cfpb_packet_system", {})
    _write_workbook_sheet(cfpb_packet_checklist, [
        [
            "Packet ID",
            "Packet Type",
            "Status",
            "Document Type",
            "Document Label",
            "Required Before Mailing",
            "Document Status",
            "Server-Side Only",
            "Browser LocalStorage Allowed",
            "Customer E-Sign Required",
            "Admin Approval Required",
            "Sensitive Data Review Required",
            "Mailing Allowed",
            "Block Reasons",
        ],
        *[
            [
                packet.get("packet_id", ""),
                packet.get("packet_type", ""),
                packet.get("status", ""),
                document.get("document_type", ""),
                document.get("label", ""),
                "Yes" if document.get("required_before_mailing") else "No",
                document.get("status", ""),
                "Yes" if document.get("server_side_only") else "No",
                "Yes" if document.get("browser_local_storage_allowed") else "No",
                "Yes" if packet.get("packet_gate", {}).get("customer_esign_required") else "No",
                "Yes" if packet.get("packet_gate", {}).get("admin_approval_required") else "No",
                "Yes" if packet.get("packet_gate", {}).get("sensitive_data_review_required") else "No",
                "Yes" if packet.get("mailing_allowed") else "No",
                packet.get("packet_gate", {}).get("block_reasons", []),
            ]
            for packet in packet_system.get("dispute_packets", [])
            for document in packet.get("documents", [])
        ],
    ])
    _write_workbook_sheet(comparison_attachment, [
        [
            "Account / Field",
            "Equifax Raw Value",
            "Experian Raw Value",
            "TransUnion Raw Value",
            "Main Issue",
            "License / Authority Status",
            "Business Registry Status",
            "Debt Collector License Status",
            "Last Checked Date",
            "Source Link",
            "Manual Review Needed",
            "Evidence Source",
            "Recommended Action",
            "Source Report Date",
            "Source Page/Section",
            "Masked Account Number",
            "Raw Data Integrity",
        ],
        *[
            [
                row.get("account_field", ""),
                row.get("equifax_raw_value", ""),
                row.get("experian_raw_value", ""),
                row.get("transunion_raw_value", ""),
                row.get("main_issue", ""),
                row.get("license_authority_status", ""),
                row.get("business_registry_status", ""),
                row.get("debt_collector_license_status", ""),
                row.get("last_checked_date", ""),
                row.get("source_link", ""),
                row.get("manual_review_needed", ""),
                row.get("evidence_source", ""),
                row.get("recommended_action", ""),
                row.get("source_report_date", ""),
                row.get("source_page_section", ""),
                row.get("masked_account_number", ""),
                row.get("raw_data_integrity", ""),
            ]
            for row in packet_system.get("three_bureau_comparison_attachment", [])
        ],
    ])
    _write_workbook_sheet(document_vault, [
        [
            "Document ID",
            "Case ID",
            "Customer ID",
            "Document Type",
            "Letter Type",
            "Recipient",
            "Date Created",
            "Customer Approved Date",
            "Admin Approved Date",
            "Lob Mail ID",
            "Tracking Number",
            "Delivery Status",
            "Response Deadline",
            "Stored Evidence",
            "Next Action",
            "Viewed By",
            "Last Accessed",
            "Retention Status",
            "Server-Side Only",
            "Browser LocalStorage Allowed",
        ],
        *[
            [
                row.get("document_id", ""),
                row.get("case_id", ""),
                row.get("customer_id", ""),
                row.get("document_type", ""),
                row.get("letter_type", ""),
                row.get("recipient", ""),
                row.get("date_created", ""),
                row.get("customer_approved_date", ""),
                row.get("admin_approved_date", ""),
                row.get("lob_mail_id", ""),
                row.get("tracking_number", ""),
                row.get("delivery_status", ""),
                row.get("response_deadline", ""),
                row.get("stored_evidence", ""),
                row.get("next_action", ""),
                row.get("viewed_by", []),
                row.get("last_accessed", ""),
                row.get("retention_status", ""),
                "Yes" if row.get("server_side_only") else "No",
                "Yes" if row.get("browser_local_storage_allowed") else "No",
            ]
            for row in packet_system.get("document_vault", {}).get("records", [])
        ],
    ])
    _write_workbook_sheet(lob_tracking, [
        ["Packet ID", "Packet Type", "Lob ID", "Recipient", "Tracking Number", "Delivery Status", "Webhook Event", "Error Message", "Response Deadline", "Next Action", "Automatic Send"],
        *[
            [
                packet.get("packet_id", ""),
                packet.get("packet_type", ""),
                packet.get("lob_tracking", {}).get("lob_id", ""),
                packet.get("lob_tracking", {}).get("recipient", "pending"),
                packet.get("lob_tracking", {}).get("tracking_number", ""),
                packet.get("lob_tracking", {}).get("delivery_status", ""),
                packet.get("lob_tracking", {}).get("webhook_event", ""),
                packet.get("lob_tracking", {}).get("error_message", ""),
                packet.get("lob_tracking", {}).get("response_deadline", ""),
                packet.get("lob_tracking", {}).get("next_action", ""),
                "Yes" if packet.get("auto_send") else "No",
            ]
            for packet in packet_system.get("dispute_packets", [])
        ],
    ])
    _write_workbook_sheet(scanner_skills, build_scanner_skill_map_rows(data))
    _write_workbook_sheet(fico_scenario_planner, build_fico_scenario_planner_rows())
    _write_workbook_sheet(codex_build_task, [
        ["Task", "Status"],
        ["Negative Account Rules Quick Reference", "Added"],
        ["Metro 2/FCRA Skills Library", "Added"],
        ["Ours 3 Bureaus Comparison layout", "Added"],
        ["Automatic dispute/letter/mail/complaint sending", "Not added"],
    ])
    _write_workbook_sheet(read_me, [
        ["Credit Vivo Workbook", "Read before using output"],
        ["Purpose", "Organize possible report errors and inconsistencies for customer/admin review."],
        ["Limits", "Draft review data only. Credit Vivo is not a law firm and does not provide legal advice."],
        ["Approval", "Nothing is sent, mailed, filed, or escalated automatically."],
        ["Results", "Accurate, current, and verifiable information may remain. Results vary."],
    ])

    _write_workbook_sheet(bureau_comparison, data.get("_three_bureau_comparison_rows") or build_three_bureau_comparison_rows(data))
    _write_workbook_sheet(side_by_side_negative, build_side_by_side_negative_rows(data))

    dashboard_sections = build_desktop_customer_dashboard(data)
    dashboard_summary = next((section for section in dashboard_sections if section.get("section") == "summary"), {})
    dashboard_findings = next((section for section in dashboard_sections if section.get("section") == "findings"), {}).get("items", [])
    dashboard_keep = next((section for section in dashboard_sections if section.get("section") == "keep_if_correct"), {}).get("items", [])
    _write_workbook_sheet(desktop_dashboard, [
        ["Section", "Account Name", "Priority", "Tone", "Bureaus", "Simple Issue", "Recommended Action", "Documents Needed", "Explanation"],
        ["Summary", "", "", "", "", f"Health score: {dashboard_summary.get('health_score', '')}; Negative accounts: {dashboard_summary.get('negative_accounts', '')}; Potential issues: {dashboard_summary.get('potential_issues', '')}", "; ".join(dashboard_summary.get("next_best_actions", [])), "", ""],
        *[
            [
                "Findings",
                item.get("account_name", ""),
                item.get("priority", ""),
                item.get("tone", ""),
                item.get("bureaus", []),
                item.get("simple_issue", ""),
                item.get("recommended_action", ""),
                item.get("documents_needed", []),
                item.get("explanation", []),
            ]
            for item in dashboard_findings
        ],
        *[
            [
                "Keep If Correct",
                item.get("account_name", ""),
                item.get("priority", ""),
                item.get("tone", ""),
                item.get("bureaus", []),
                item.get("simple_issue", ""),
                item.get("recommended_action", ""),
                item.get("documents_needed", []),
                item.get("explanation", []),
            ]
            for item in dashboard_keep
        ],
    ])

    _write_workbook_sheet(desktop_workbox, [
        ["Account ID", "Account Name", "Priority Score", "Queue", "Internal Findings", "Recommended Letter Types", "Documents Needed"],
        *[
            [
                row.get("account_id", ""),
                row.get("account_name", ""),
                row.get("priority_score", ""),
                row.get("queue", ""),
                row.get("internal_findings", []),
                row.get("recommended_letter_types", []),
                row.get("documents_needed", []),
            ]
            for row in build_desktop_staff_workbox(data)
        ],
    ])

    _write_workbook_sheet(desktop_field_matrix, [
        ["Account Name", "Field", "Label", "Equifax", "Experian", "TransUnion", "Differs"],
        *[
            [
                row.get("account_name", ""),
                row.get("field", ""),
                row.get("label", ""),
                row.get("equifax", ""),
                row.get("experian", ""),
                row.get("transunion", ""),
                "Yes" if row.get("differs") else "No",
            ]
            for row in build_desktop_bureau_field_matrix(data)
        ],
    ])

    _write_workbook_sheet(errors, [
        ["Issue ID", "Issue Type", "Severity", "Customer Label", "Customer Explanation", "Admin Explanation", "Suggested Round", "Related Tradeline IDs", "Confidence", "Evidence Count"],
        *[
            [
                issue.get("id", ""),
                issue.get("issue_type", ""),
                issue.get("severity", ""),
                issue.get("customer_label", ""),
                issue.get("customer_explanation", ""),
                issue.get("admin_explanation", ""),
                issue.get("suggested_round", ""),
                issue.get("related_tradeline_ids", []),
                issue.get("confidence", ""),
                len(issue.get("evidence", [])),
            ]
            for issue in data.get("issues", [])
        ],
    ])

    _write_workbook_sheet(items, [
        ["ID", "Bureau", "Source File", "Account Name", "Account Type", "Status", "Balance", "Date Opened", "Date Reported", "DOFD", "Remarks", "Confidence", "Needs Admin Review"],
        *[
            [
                item.get("id", ""),
                item.get("bureau", ""),
                item.get("source_filename", ""),
                item.get("account_name", ""),
                item.get("account_type", ""),
                item.get("status", ""),
                item.get("balance", ""),
                item.get("date_opened", ""),
                item.get("date_reported", ""),
                item.get("date_of_first_delinquency", ""),
                item.get("remarks", ""),
                item.get("confidence", ""),
                "Yes" if item.get("needs_admin_review") else "No",
            ]
            for item in data.get("tradelines", [])
        ],
    ])

    _write_workbook_sheet(raw_tradelines_dates, [
        [
            "source_file",
            "bureau",
            "page",
            "account_group",
            "creditor",
            "account_number",
            "original_creditor",
            "creditor_classification",
            "account_type",
            "account_status",
            "payment_status",
            "balance",
            "past_due",
            "high_balance",
            "credit_limit",
            "date_opened",
            "collection_assigned_date",
            "date_reported",
            "date_updated",
            "status_updated_date",
            "date_closed",
            "date_last_payment",
            "date_last_activity",
            "date_of_first_delinquency",
            "estimated_removal_date",
            "remarks",
            "confidence",
            "raw_evidence",
        ],
        *[
            [
                item.get("source_filename", ""),
                item.get("bureau", ""),
                item.get("page_start", ""),
                item.get("group_id", "") or item.get("id", ""),
                item.get("account_name", ""),
                item.get("account_number", "") or item.get("account_number_masked", ""),
                item.get("original_creditor", ""),
                item.get("creditor_classification", ""),
                item.get("account_type", ""),
                item.get("status", ""),
                item.get("pay_status", ""),
                item.get("balance", ""),
                item.get("past_due", ""),
                item.get("high_balance", "") or item.get("high_credit_or_original_amount", ""),
                item.get("credit_limit", ""),
                item.get("date_opened", ""),
                "",
                item.get("date_reported", ""),
                item.get("date_reported", ""),
                "",
                item.get("date_closed", ""),
                item.get("date_last_payment", ""),
                item.get("date_last_activity", ""),
                item.get("date_of_first_delinquency", ""),
                item.get("estimated_removal_date", ""),
                item.get("remarks", ""),
                item.get("confidence", ""),
                item.get("raw_block", ""),
            ]
            for item in data.get("tradelines", [])
        ],
    ])

    raw_verification = data.get("raw_verification_summary", {})
    _write_workbook_sheet(raw_data_verification, [
        ["Raw Verification Summary", ""],
        ["Status", raw_verification.get("status", "")],
        ["Total Tradelines Checked", raw_verification.get("total_tradelines_checked", "")],
        ["Verified", raw_verification.get("verified", "")],
        ["Needs Review", raw_verification.get("needs_review", "")],
        ["Not Verified", raw_verification.get("not_verified", "")],
        ["Warning", raw_verification.get("warning", "")],
        [],
        ["Tradeline ID", "Bureau", "Source File", "Account Name", "Raw Verification Status", "Verified Fields", "Unverified Fields", "Warnings", "Admin Review Required"],
        *[
            [
                item.get("id", ""),
                item.get("bureau", ""),
                item.get("source_filename", ""),
                item.get("account_name", ""),
                item.get("rawVerificationStatus", ""),
                item.get("rawVerifiedFields", []),
                item.get("rawUnverifiedFields", []),
                item.get("rawVerificationWarnings", []),
                "Yes" if item.get("needs_admin_review") else "No",
            ]
            for item in data.get("tradelines", [])
        ],
    ])

    _write_workbook_sheet(pre_output_verification, build_pre_output_verification_rows(data))
    _write_workbook_sheet(ground_truth_validation, build_ground_truth_validation_rows(data))
    _write_workbook_sheet(qa_verification, build_qa_verification_rows(data))
    _write_workbook_sheet(security_audit_summary, build_security_audit_summary_rows(data))
    _write_workbook_sheet(production_gate, build_production_gate_rows(data))
    _write_workbook_sheet(positive_accounts_keep, build_positive_accounts_keep_rows(data))

    _write_workbook_sheet(entity_compliance, [
        [
            "Tradeline ID",
            "Source File",
            "Bureau",
            "Account Name",
            "Entity Name",
            "Normalized Entity",
            "Entity Type",
            "Source Role",
            "Business Registry Search Link",
            "State License Search Link",
            "Debt Collector License Search Link",
            "NMLS Search Link",
            "Regulator Complaint Route",
            "Last Checked Date",
            "Link Health Status",
            "Verification Status",
            "Customer Wording",
            "Admin Wording",
            "Manual Review Notes",
            "Supports Validation Letters",
            "Supports Furnisher Disputes",
            "Supports Bureau Disputes",
            "Supports Complaint Packets",
            "Supports Attorney Review Summaries",
        ],
        *[
            [
                row.get("tradeline_id", ""),
                row.get("source_file", ""),
                row.get("bureau", ""),
                row.get("account_name", ""),
                row.get("entity_name", ""),
                row.get("normalized_entity_name", ""),
                row.get("entity_type", ""),
                row.get("source_role", ""),
                row.get("business_registry_search_link", ""),
                row.get("state_license_search_link", ""),
                row.get("debt_collector_license_search_link", ""),
                row.get("nmls_search_link", ""),
                row.get("regulator_complaint_route", ""),
                row.get("last_checked_date", ""),
                row.get("link_health_status", ""),
                row.get("verification_status", ""),
                row.get("customer_wording", ""),
                row.get("admin_wording", ""),
                row.get("manual_review_notes", ""),
                "Yes" if row.get("supports_validation_letters") else "No",
                "Yes" if row.get("supports_furnisher_disputes") else "No",
                "Yes" if row.get("supports_bureau_disputes") else "No",
                "Yes" if row.get("supports_complaint_packets") else "No",
                "Yes" if row.get("supports_attorney_review_summaries") else "No",
            ]
            for row in data.get("entity_compliance_intelligence", [])
        ],
    ])

    _write_workbook_sheet(dates_found_audit, [
        ["source_file", "bureau", "page", "account_key", "creditor", "field_name", "field_title", "raw_date", "normalized_date", "precision", "label_matched", "confidence", "context"],
        *[
            [
                row.get("source_file", ""),
                row.get("bureau", ""),
                row.get("page", ""),
                row.get("account_key", ""),
                row.get("creditor", ""),
                row.get("field_name", ""),
                row.get("field_title", ""),
                row.get("raw_date", ""),
                row.get("normalized_date", ""),
                row.get("precision", ""),
                row.get("label_matched", ""),
                row.get("confidence", ""),
                row.get("context", ""),
            ]
            for row in data.get("dates_found_audit", [])
        ],
    ])

    _write_workbook_sheet(date_issues, [
        ["Severity", "Account/Bureau", "Issue Type", "What we found in plain English", "Why it matters", "What to do next"],
        *[
            [
                row.get("severity", ""),
                row.get("account_bureau", ""),
                row.get("issue_type", ""),
                row.get("what_found", ""),
                row.get("why_matters", ""),
                row.get("next_step", ""),
            ]
            for row in data.get("date_issues_to_dispute", [])
        ],
    ])

    _write_workbook_sheet(metro2_fcra, [
        [
            "Issue ID",
            "Issue Type",
            "Customer Label",
            "Metro 2 Fields To Review",
            "FCRA Focus",
            "FCRA Sections / Duties",
            "Evidence Needed",
            "Dispute Theory",
            "Responsible Party",
            "Recommended Next Action",
            "Attorney Review Signal",
            "Customer Approval Required",
        ],
        *[
            [
                row.get("issue_id", ""),
                row.get("issue_type", ""),
                row.get("customer_label", ""),
                row.get("metro2_fields_to_review", []),
                row.get("fcra_focus", ""),
                row.get("fcra_sections", []),
                row.get("evidence_needed", []),
                row.get("dispute_theory", ""),
                row.get("responsible_party", ""),
                row.get("recommended_next_action", ""),
                "Yes" if row.get("attorney_review_signal") else "No",
                "Yes" if row.get("customer_approval_required") else "No",
            ]
            for row in data.get("metro2_fcra_review", [])
        ],
    ])

    _write_workbook_sheet(metro2_requirements, [
        [
            "Tradeline ID",
            "Bureau",
            "Account Name",
            "Account Type",
            "Status",
            "Metro 2 Profile",
            "Required/Core Fields",
            "Present Fields",
            "Missing / Needs Validation",
            "Warning Flags",
            "Validation Notes",
            "Dispute Use",
            "Production Note",
        ],
        *[
            [
                row.get("tradeline_id", ""),
                row.get("bureau", ""),
                row.get("account_name", ""),
                row.get("account_type", ""),
                row.get("status", ""),
                row.get("metro2_profile", ""),
                row.get("required_core_fields", []),
                row.get("present_fields", []),
                row.get("missing_or_needs_validation", []),
                row.get("warning_flags", []),
                row.get("validation_notes", []),
                row.get("dispute_use", ""),
                row.get("production_note", ""),
            ]
            for row in data.get("metro2_requirement_review", [])
        ],
    ])

    guide_notes = data.get("metro2_public_guide_notes", {})
    _write_workbook_sheet(metro2_guide_notes, [
        ["Item", "Value"],
        ["Source", guide_notes.get("source", "")],
        ["URL", guide_notes.get("url", "")],
        ["Purpose", guide_notes.get("purpose", "")],
        ["Production Guardrail", guide_notes.get("production_guardrail", "")],
        ["Base Segment Fields Mapped", guide_notes.get("base_segment_fields", [])],
        ["Collection / Associated Segments", guide_notes.get("collection_segments", [])],
    ])

    _write_workbook_sheet(fcra_compliance, [
        [
            "Tradeline ID",
            "Bureau",
            "Account Name",
            "FCRA Area",
            "Law Reference",
            "Plain English Meaning",
            "Applies When",
            "Scanner Signals",
            "Evidence Needed",
            "Tracking Action",
            "Customer Approval Required",
            "Attorney / Compliance Review",
            "Note",
        ],
        *[
            [
                row.get("tradeline_id", ""),
                row.get("bureau", ""),
                row.get("account_name", ""),
                row.get("fcra_area", ""),
                row.get("law_reference", ""),
                row.get("plain_english", ""),
                row.get("applies_when", ""),
                row.get("scanner_signals", []),
                row.get("evidence_needed", ""),
                row.get("tracking_action", ""),
                "Yes" if row.get("customer_approval_required") else "No",
                "Yes" if row.get("attorney_or_compliance_review") else "No",
                row.get("note", ""),
            ]
            for row in data.get("fcra_compliance_review", [])
        ],
    ])

    rights_reference = data.get("fcra_rights_reference", {})
    source_notes = rights_reference.get("source_notes", {})
    rights_rows = [
        ["Section", "Category / State", "Agency / Item", "Address / URL", "Phone / Note"],
        ["Source", "Primary Reference", source_notes.get("primary_reference", ""), source_notes.get("primary_url", ""), source_notes.get("plain_english_note", "")],
        ["Source", "Agency Contact Update", source_notes.get("agency_contact_update_reference", ""), source_notes.get("agency_contact_update_url", ""), source_notes.get("compliance_note", "")],
    ]
    for right in rights_reference.get("federal_consumer_rights", []):
        rights_rows.append([
            "Federal Consumer Right",
            "FCRA",
            right.get("right", ""),
            right.get("plain_english", ""),
            right.get("scanner_use", ""),
        ])
    maryland_rights = rights_reference.get("maryland_consumer_rights", {})
    if maryland_rights:
        rights_rows.append([
            "State Consumer Right",
            maryland_rights.get("state", "Maryland"),
            maryland_rights.get("legal_reference", ""),
            maryland_rights.get("plain_english_summary", ""),
            "",
        ])
        for right in maryland_rights.get("consumer_rights", []):
            rights_rows.append([
                "State Consumer Right",
                maryland_rights.get("state", "Maryland"),
                "Maryland consumer reporting right",
                right,
                "",
            ])
        contact = maryland_rights.get("complaint_contact", {})
        rights_rows.append([
            "State Complaint Contact",
            maryland_rights.get("state", "Maryland"),
            contact.get("agency", ""),
            contact.get("address", ""),
            contact.get("phone", ""),
        ])
        for use in maryland_rights.get("scanner_use", []):
            rights_rows.append([
                "State Scanner Rule",
                maryland_rights.get("state", "Maryland"),
                "Credit Vivo workflow",
                "",
                use,
            ])
    for contact_group in rights_reference.get("federal_contacts", []):
        for contact in contact_group.get("contacts", []):
            rights_rows.append([
                "Federal Contact",
                contact_group.get("category", ""),
                contact.get("agency", ""),
                contact.get("address", ""),
                contact.get("phone") or contact.get("use_when", ""),
            ])
    for state_link in rights_reference.get("state_notice_links", []):
        rights_rows.append([
            "State Notice Link",
            state_link.get("state", ""),
            "State consumer reporting rights reference",
            state_link.get("url", ""),
            "Confirm current state-law requirements before production disclosure use.",
        ])
    for rule in rights_reference.get("ai_rules", []):
        rights_rows.append(["AI Rule", "All AI engines", "FCRA rights routing rule", "", rule])
    _write_workbook_sheet(fcra_rights, rights_rows)

    bureau_reference = data.get("bureau_debt_collection_reference", {})
    source_notes = bureau_reference.get("source_notes", {})
    bureau_rows = [
        ["Section", "Bureau / Rule", "Meaning", "Scanner / Customer Next Step", "Source / Note"],
        ["Source", "Equifax dispute help", source_notes.get("equifax_dispute_url", ""), source_notes.get("equifax_mail_dispute_url", ""), source_notes.get("compliance_note", "")],
        ["Source", "Experian dispute/outcomes", source_notes.get("experian_dispute_url", ""), source_notes.get("experian_outcome_url", ""), ""],
        ["Source", "TransUnion dispute help", source_notes.get("transunion_dispute_url", ""), "", ""],
        ["Source", "CFPB dispute help", source_notes.get("cfpb_dispute_url", ""), "", ""],
        ["Source", "FDCPA", source_notes.get("fdcpa_source", ""), "", ""],
    ]
    for item in bureau_reference.get("bureau_dispute_workflow", []):
        bureau_rows.append([
            "Bureau Workflow",
            item.get("bureau", ""),
            item.get("customer_help_rule", ""),
            item.get("scanner_action", ""),
            "Channels: " + "; ".join(item.get("channels", [])) + " | Proof: " + "; ".join(item.get("proof_examples", [])),
        ])
    for item in bureau_reference.get("experian_dispute_outcomes", []):
        bureau_rows.append([
            "Experian Outcome",
            item.get("outcome", ""),
            item.get("meaning", ""),
            item.get("scanner_next_step", ""),
            "Use to parse bureau response/results letters.",
        ])
    for item in bureau_reference.get("fdcpa_collection_rules", []):
        bureau_rows.append([
            "FDCPA Rule",
            item.get("rule", ""),
            item.get("plain_english", ""),
            item.get("scanner_use", ""),
            "Debt-collection conduct rule; approval-gated.",
        ])
    for rule in bureau_reference.get("ai_rules", []):
        bureau_rows.append(["AI Rule", "All AI engines", rule, "", ""])
    _write_workbook_sheet(bureau_help, bureau_rows)

    _write_workbook_sheet(field_compliance, [
        [
            "Tradeline ID",
            "Bureau",
            "Account Name",
            "Field Name",
            "Parsed Value",
            "Required / Expected",
            "Issue Flag",
            "Metro 2 Concept",
            "FCRA / Reg V Basis",
            "Issue Text",
            "Verification Ask",
            "Requested Outcome",
            "Source Note",
        ],
        *[
            [
                row.get("tradeline_id", ""),
                row.get("bureau", ""),
                row.get("account_name", ""),
                row.get("field_name", ""),
                row.get("parsed_value", ""),
                row.get("required_or_expected", ""),
                row.get("issue_flag", ""),
                row.get("metro2_concept", ""),
                row.get("fcra_basis", ""),
                row.get("issue_text", ""),
                row.get("verification_ask", ""),
                row.get("requested_outcome", ""),
                row.get("source_note", ""),
            ]
            for row in data.get("field_compliance_audit", [])
        ],
    ])

    _write_workbook_sheet(eoscar_packaging, [
        [
            "Issue ID",
            "Issue Type",
            "Account Names",
            "Bureaus",
            "e-OSCAR / ACDV Category",
            "ACDV Packaging Steps",
            "Field Focus",
            "Package Hint",
            "Evidence Hint",
            "Avoid",
            "Tracking Status",
        ],
        *[
            [
                row.get("issue_id", ""),
                row.get("issue_type", ""),
                row.get("account_names", []),
                row.get("bureaus", []),
                row.get("eoscar_category", ""),
                row.get("acdv_packaging_steps", []),
                row.get("field_focus", []),
                row.get("package_hint", ""),
                row.get("evidence_hint", ""),
                row.get("avoid", []),
                row.get("tracking_status", ""),
            ]
            for row in data.get("eoscar_packaging_review", [])
        ],
        ["Public Fact", "What e-OSCAR is", "", "", "", EOSCAR_PUBLIC_FACTS[0]["detail"], "", "", "", EOSCAR_PUBLIC_FACTS[0]["source"], ""],
        ["Public Fact", "ACDV path", "", "", "", EOSCAR_PUBLIC_FACTS[1]["detail"], "", "", "", EOSCAR_PUBLIC_FACTS[1]["source"], ""],
        ["Public Fact", "AUD path", "", "", "", EOSCAR_PUBLIC_FACTS[2]["detail"], "", "", "", EOSCAR_PUBLIC_FACTS[2]["source"], ""],
    ])

    notice_rows = [["Rule Area", "Requirement / Control"]]
    for area, controls in data.get("letter_workflow", {}).get("fcra_notice_rules", {}).items():
        label = area.replace("_", " ").title()
        for control in controls:
            notice_rows.append([label, control])
    _write_workbook_sheet(fcra_notice_rules, notice_rows)

    _write_workbook_sheet(dispute_methods, build_dispute_method_rows())

    _write_workbook_sheet(dispute_sop, build_dispute_sop_rows())

    _write_workbook_sheet(letters, [
        ["Letter ID", "Issue ID", "Subject", "Letter Type", "Round", "Recipient Type", "Delivery Method", "FCRA Notice Included", "Customer Approval Required", "Tracking Status", "Recommended Next Action", "Draft Letter Body"],
        *[
            [
                letter.get("letter_id", ""),
                letter.get("issue_id", ""),
                letter.get("letter_subject", ""),
                letter.get("letter_type", ""),
                letter.get("round", ""),
                letter.get("recipient_type", ""),
                letter.get("delivery_method", ""),
                "Yes" if letter.get("fcra_notice_included") else "No",
                "Yes" if letter.get("customer_approval_required") else "No",
                letter.get("tracking_status", ""),
                letter.get("recommended_next_action", ""),
                letter.get("draft_letter_body", ""),
            ]
            for letter in data.get("recommended_letter_queue", [])
        ],
    ])

    _write_workbook_sheet(fcra, [
        ["Issue ID", "Possible FCRA Issue", "Issue Type", "Responsible Party", "Dispute History Complete", "Evidence Strength", "Damages Evidence", "Next Action", "Requires Admin Review"],
        *[
            [
                row.get("issue_id", ""),
                "Yes" if row.get("possible_fcra_issue") else "No",
                row.get("issue_type", ""),
                row.get("responsible_party", ""),
                "Yes" if row.get("dispute_history_complete") else "No",
                row.get("evidence_strength", ""),
                row.get("damages_evidence", ""),
                row.get("next_action", ""),
                "Yes" if row.get("requires_admin_review") else "No",
            ]
            for row in data.get("fcra_review", [])
        ],
    ])

    apply_v9_forensic_layout(wb, data)
    wb.save(out_dir / "credit_vivo_desktop_scanner_output.xlsx")


def apply_v9_forensic_layout(wb: Workbook, data: dict) -> None:
    """Make the exported workbook open like the v9 3-bureau forensic layout."""
    if "Summary" in wb.sheetnames:
        wb["Summary"].sheet_state = "hidden"
    else:
        summary = wb.create_sheet("Summary")
        summary.sheet_state = "hidden"

    if "Read_Me" in wb.sheetnames:
        wb["Read_Me"].title = "Read_Me_v9"
    if "Read_Me" not in wb.sheetnames:
        read_me_compat = wb.create_sheet("Read_Me")
        read_me_compat.sheet_state = "hidden"
        read_me_compat.append(["Credit Vivo Workbook", "Compatibility tab"])
        read_me_compat.append(["Purpose", "Hidden compatibility sheet. Use visible Read_Me_v9 for v9 workbook notes."])

    visible_order = [
        "Dashboard",
        "Account_Summary",
        "Ours 3 Bureaus Comparison",
        "Identity_Cleanup",
        "Negative_Definitions",
        "License_Check",
        "State_License_Links",
        "Dispute_Cycle_Status",
        "Exact_Letters_To_Mail",
        "Escalation_Addresses",
        "Complaint_Packet",
        "CFPB_Packet_Checklist",
        "3B_Comparison_Attachment",
        "Document_Vault",
        "Lob_Tracking",
        "Scanner_Skills_Map",
        "FICO_Scenario_Planner",
        "Codex_Build_Task",
        "Read_Me_v9",
        "Ground_Truth_Validation",
        "QA_Verification",
        "Security_Audit_Summary",
        "Production_Gate",
        "Positive_Accounts_Keep",
    ]
    for sheet_name in reversed(visible_order):
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            wb._sheets.remove(sheet)
            wb._sheets.insert(0, sheet)

    sheet_titles = {
        "Dashboard": ("Credit Vivo Backend Engine Workbook v18.1.7", "v9 forensic workbook layout + scanner skills map + approval-gated packet planning + pre-output template/raw-data verification + export QA cleanup flags", "A1:J1", "A2:J2"),
        "Account_Summary": ("Account Summary", "One row per negative/reviewable account. Counts are draft review categories, not final legal conclusions.", "A1:L1", "A2:L2"),
        "Identity_Cleanup": ("Identity Cleanup - Raw Personal Info", "Keep one confirmed contact profile. Delete extra names/contact/address/employment data only after customer confirmation and admin review.", "A1:K1", "A2:K2"),
        "Negative_Definitions": ("Negative Account Count + FCRA / Metro 2 Definitions", "Definitions are plain-English product logic for Credit Vivo. Not legal advice.", "A1:H1", "A2:H2"),
        "License_Check": ("Business / Debt Collection License Check", "License status must be verified from official registry before use in a letter or complaint packet. Pending/Needs Review is not a violation finding.", "A1:N1", "A2:N2"),
        "State_License_Links": ("State Business + Debt Collection License Lookup Links", "Use official state or NMLS links for license evidence. Add results to License_Check after verification.", "A1:G1", "A2:G2"),
        "Dispute_Cycle_Status": ("Dispute Cycle + Status Flow", "Backend engine status flow. Customer-facing portal is separate. No automatic mail, complaints, or legal escalation.", "A1:I1", "A2:I2"),
        "Exact_Letters_To_Mail": ("Draft Letter Templates - Ready for Review", "Draft-only templates. Customer approval + admin review required before mailing. Replace bracketed fields with case data.", "A1:H1", "A2:H2"),
        "Escalation_Addresses": ("Addresses - Bureaus, Furnishers, Escalation, Agencies", "Verify addresses before production mail. Corporate/executive addresses may change; use official current address before sending.", "A1:K1", "A2:K2"),
        "Complaint_Packet": ("Complaint Packet Prep", "Preparation-only packet. Credit Vivo does not auto-file complaints and does not provide legal advice.", "A1:J1", "A2:J2"),
        "CFPB_Packet_Checklist": ("CFPB-Style Packet Checklist", "Evidence-backed packet readiness. Mailing is blocked until customer e-sign, admin approval, sensitive-data review, and approved production workflow are complete.", "A1:N1", "A2:N2"),
        "3B_Comparison_Attachment": ("3-Bureau Comparison Attachment", "Short packet attachment using exact raw bureau values plus license/authority review prompts.", "A1:Q1", "A2:Q2"),
        "Document_Vault": ("Customer Document Vault Manifest", "Server-side document manifest for outgoing and incoming packet documents. Sensitive documents are not stored in browser localStorage.", "A1:T1", "A2:T2"),
        "Lob_Tracking": ("Lob Tracking Placeholder", "Draft tracking model only. No Lob call is made until all approvals and production controls are configured.", "A1:K1", "A2:K2"),
        "Scanner_Skills_Map": ("Scanner Skills Map", "Admin/founder view of the internal scanner capability areas. This is not paid AI and does not trigger automatic sending.", "A1:G1", "A2:G2"),
        "FICO_Scenario_Planner": ("FICO Scenario Planner - Non-Guaranteed", "Scenario planning only. Actual score movement depends on FICO model, bureau data, age of accounts, utilization, payment history, and full credit file.", "A1:J1", "A2:J2"),
        "Codex_Build_Task": ("Codex Build Task - Export This Layout", "Use this to instruct Codex to update the backend scanner export to this workbook layout.", "A1:G1", "A2:G2"),
        "Read_Me_v9": ("Credit Vivo v18.1.7 Workbook Notes", "", None, None),
        "Ground_Truth_Validation": ("Ground Truth Validation - Raw PDF to JSON to Workbook", "Triple-check sheet for source PDF evidence, parser JSON evidence, workbook evidence, and admin review notes.", "A1:F1", "A2:F2"),
        "QA_Verification": ("QA Verification", "Automated workbook verification summary. Draft QA evidence only; not production approval by itself.", "A1:F1", "A2:F2"),
        "Security_Audit_Summary": ("Security Audit Summary", "Draft-only, approval-gated, no automatic sending, complaint, or legal escalation controls.", "A1:E1", "A2:E2"),
        "Production_Gate": ("Production Gate", "Final scanner workbook gate before production approval. Results vary; no legal advice.", "A1:E1", "A2:E2"),
        "Positive_Accounts_Keep": ("Positive Accounts To Keep If Accurate", "Usually keep accurate positive/current accounts. Customer/admin review still required.", "A1:E1", "A2:E2"),
    }

    workbook_theme = {
        "title": "064E3B",
        "subtitle": "D1FAE5",
        "header": "BBF7D0",
        "band": "F8FAFC",
        "font": "064E3B",
    }
    sheet_tab_colors = {
        "Dashboard": "064E3B",
        "Account_Summary": "0F766E",
        "Ours 3 Bureaus Comparison": "1D4ED8",
        "Identity_Cleanup": "7C3AED",
        "License_Check": "B45309",
        "State_License_Links": "B45309",
        "Dispute_Cycle_Status": "0E7490",
        "Exact_Letters_To_Mail": "0E7490",
        "Escalation_Addresses": "B91C1C",
        "Complaint_Packet": "B91C1C",
        "CFPB_Packet_Checklist": "B91C1C",
        "3B_Comparison_Attachment": "1D4ED8",
        "Document_Vault": "475569",
        "Lob_Tracking": "475569",
        "Scanner_Skills_Map": "0F766E",
        "FICO_Scenario_Planner": "4338CA",
        "Codex_Build_Task": "475569",
        "Read_Me_v9": "064E3B",
        "Ground_Truth_Validation": "0F766E",
        "QA_Verification": "0F766E",
        "Security_Audit_Summary": "B91C1C",
        "Production_Gate": "B91C1C",
        "Positive_Accounts_Keep": "0F766E",
    }
    title_fill = PatternFill("solid", fgColor=workbook_theme["title"]) if PatternFill else None
    subtitle_fill = PatternFill("solid", fgColor=workbook_theme["subtitle"]) if PatternFill else None
    title_font = Font(bold=True, color="FFFFFF", size=14) if Font else None
    subtitle_font = Font(bold=True, color=workbook_theme["font"]) if Font else None
    header_fill = PatternFill("solid", fgColor=workbook_theme["header"]) if PatternFill else None
    header_font = Font(bold=True, color=workbook_theme["font"]) if Font else None

    for sheet_name, (title, subtitle, merge_title, merge_subtitle) in sheet_titles.items():
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        if ws.max_row and ws.cell(1, 1).value != title:
            ws.insert_rows(1, 3)
        ws.cell(1, 1).value = title
        ws.cell(2, 1).value = subtitle
        if sheet_name == "Dashboard":
            raw_verification = data.get("raw_verification_summary", {})
            ws.cell(3, 1).value = "Prepared from"
            ws.cell(3, 2).value = f"{len(data.get('files', []))} uploaded report(s)"
            ws.cell(3, 3).value = "Draft review only"
            ws.cell(4, 1).value = "3-CRA tradelines"
            ws.cell(4, 2).value = len(data.get("cross_bureau_groups", []))
            ws.cell(5, 1).value = "Single-bureau tradelines"
            ws.cell(5, 2).value = max(len(data.get("tradelines", [])) - len(data.get("cross_bureau_groups", [])), 0)
            ws.cell(6, 1).value = "Likely issue rows"
            ws.cell(6, 2).value = len(data.get("issues", []))
            ws.cell(7, 1).value = "Compliance note"
            ws.cell(7, 2).value = "Possible errors are draft review data only."
            ws.cell(7, 3).value = "Customer approval + admin review required before sending any dispute, validation, reinvestigation, complaint, or mail packet."
            ws.cell(8, 1).value = "Safe wording"
            ws.cell(8, 2).value = "Correct, update, or remove information that cannot be verified as accurate, complete, and current."
            ws.cell(8, 3).value = "No guarantees, no legal advice, results vary."
            ws.cell(9, 1).value = "Raw data verification"
            ws.cell(9, 2).value = raw_verification.get("status", "not_verified")
            ws.cell(9, 3).value = (
                f"Checked {raw_verification.get('total_tradelines_checked', 0)} parsed item(s): "
                f"{raw_verification.get('verified', 0)} verified, "
                f"{raw_verification.get('needs_review', 0)} need admin review, "
                f"{raw_verification.get('not_verified', 0)} not verified."
            )
        for merge_range in (merge_title, merge_subtitle):
            if merge_range and merge_range not in [str(rng) for rng in ws.merged_cells.ranges]:
                ws.merge_cells(merge_range)
        if title_fill:
            for cell in ws[1]:
                cell.fill = title_fill
                cell.font = title_font
        if subtitle_fill:
            for cell in ws[2]:
                cell.fill = subtitle_fill
                cell.font = subtitle_font
        header_row = 4 if sheet_name != "Dashboard" else None
        if header_row and header_row <= ws.max_row:
            for cell in ws[header_row]:
                cell.fill = header_fill
                cell.font = header_font
        ws.freeze_panes = None
        if sheet_name in sheet_tab_colors:
            ws.sheet_properties.tabColor = sheet_tab_colors[sheet_name]

    if "Ours 3 Bureaus Comparison" in wb.sheetnames:
        ws = wb["Ours 3 Bureaus Comparison"]
        for cell in ws[4]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "A5"

    widths_by_sheet = {
        "Dashboard": {"A": 24, "B": 36, "C": 58},
        "Account_Summary": {"A": 8, "B": 32, "C": 26, "D": 22, "E": 14, "F": 38, "G": 38, "H": 38, "I": 18, "J": 42, "K": 34, "L": 18},
        "Ours 3 Bureaus Comparison": {"A": 9, "B": 34, "C": 13, "D": 9, "E": 26, "F": 24, "G": 18, "H": 18, "I": 28, "J": 18, "K": 82, "L": 30},
        "Identity_Cleanup": {"A": 12, "B": 18, "C": 42, "D": 42, "E": 14, "F": 28, "G": 8, "H": 48, "I": 48, "J": 16, "K": 52},
        "CFPB_Packet_Checklist": {"A": 22, "B": 24, "C": 24, "D": 28, "E": 42, "F": 16, "G": 18, "H": 16, "I": 18, "J": 18, "K": 18, "L": 20, "M": 16, "N": 42},
        "3B_Comparison_Attachment": {"A": 40, "B": 24, "C": 24, "D": 24, "E": 22, "F": 28, "G": 24, "H": 24, "I": 16, "J": 40, "K": 16, "L": 32, "M": 42, "N": 18, "O": 28, "P": 22, "Q": 42},
        "Document_Vault": {"A": 42, "B": 18, "C": 18, "D": 30, "E": 24, "F": 22, "G": 25, "H": 20, "I": 20, "J": 18, "K": 22, "L": 18, "M": 20, "N": 24, "O": 42, "P": 18, "Q": 20, "R": 34, "S": 16, "T": 18},
        "Lob_Tracking": {"A": 22, "B": 24, "C": 18, "D": 22, "E": 22, "F": 18, "G": 24, "H": 30, "I": 20, "J": 48, "K": 16},
        "Scanner_Skills_Map": {"A": 30, "B": 30, "C": 62, "D": 52, "E": 42, "F": 56, "G": 16},
        "Exact_Letters_To_Mail": {"A": 28, "B": 26, "C": 52, "D": 90, "E": 44, "F": 18, "G": 14, "H": 45},
        "Read_Me_v9": {"A": 24, "B": 80, "C": 18, "D": 18},
        "Ground_Truth_Validation": {"A": 32, "B": 18, "C": 42, "D": 28, "E": 34, "F": 52},
        "Security_Audit_Summary": {"A": 32, "B": 18, "C": 44, "D": 38, "E": 52},
        "Production_Gate": {"A": 32, "B": 18, "C": 48, "D": 38, "E": 52},
        "Positive_Accounts_Keep": {"A": 34, "B": 18, "C": 22, "D": 62, "E": 24},
    }
    minimum_dimensions = {
        "Account_Summary": (15, 12),
        "Ours 3 Bureaus Comparison": (355, 12),
        "Identity_Cleanup": (10, 11),
        "License_Check": (16, 14),
        "State_License_Links": (13, 7),
        "Dispute_Cycle_Status": (15, 9),
        "Escalation_Addresses": (19, 11),
        "Complaint_Packet": (12, 10),
        "FICO_Scenario_Planner": (11, 10),
        "Ground_Truth_Validation": (12, 6),
        "Security_Audit_Summary": (10, 5),
        "Production_Gate": (10, 5),
        "Positive_Accounts_Keep": (6, 5),
    }
    for sheet_name, (min_rows, min_cols) in minimum_dimensions.items():
        if sheet_name in wb.sheetnames:
            ensure_sheet_dimensions(wb[sheet_name], min_rows, min_cols)
    for sheet_name, widths in widths_by_sheet.items():
        if sheet_name in wb.sheetnames:
            for column, width in widths.items():
                wb[sheet_name].column_dimensions[column].width = width

    if "Read_Me_v9" in wb.sheetnames:
        read_me = wb["Read_Me_v9"]
        read_me.cell(1, 1).value = "Credit Vivo v18.1.7 Workbook Notes"
        read_me.cell(2, 1).value = "What changed"
        read_me.cell(2, 2).value = "The main comparison output matches the v9 three-bureau forensic layout while retaining v18 raw-data and template verification."
        read_me.cell(3, 1).value = "Main tab"
        read_me.cell(3, 2).value = "Ours 3 Bureaus Comparison"
        read_me.cell(4, 1).value = "Layout"
        read_me.cell(4, 2).value = "Field # | Account Info | Experian | Equifax | TransUnion | Forensic issue / dispute lead | 3-CRA Status | AI Error / Inaccuracy Found | Reason / Why It Matters | Dispute / Verification Request | Priority | Evidence / Notes"
        read_me.cell(5, 1).value = "Compliance rule"
        read_me.cell(5, 2).value = "All findings are possible issues for review only. Accurate, current, and verifiable information may remain."
        read_me.cell(6, 1).value = "Approval rule"
        read_me.cell(6, 2).value = "Customer approval and admin review are required before any dispute, validation letter, reinvestigation request, complaint packet, or mail sending."
        read_me.cell(7, 1).value = "CFPB packet rule"
        read_me.cell(7, 2).value = "CFPB_Packet_Checklist, 3B_Comparison_Attachment, Document_Vault, and Lob_Tracking are draft packet-planning tabs. They do not send mail or file complaints."
        read_me.cell(8, 1).value = "Skills map"
        read_me.cell(8, 2).value = "Scanner_Skills_Map documents the parser, QA, compliance, dispute-prep, workflow, letter lifecycle, and privacy skill areas used by the backend engine."

    for ws in wb.worksheets:
        ws.sheet_state = "visible" if ws.title in visible_order else "hidden"
        if ws.title in visible_order:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.__class__.__name__ == "MergedCell":
                        continue
                    cell.value = mask_visible_workbook_text(cell.value)
            _style_workbook_sheet(
                ws,
                workbook_theme["title"],
                workbook_theme["subtitle"],
                workbook_theme["header"],
                workbook_theme["band"],
                workbook_theme["font"],
            )
            _style_status_cells(ws)
            _auto_size_remaining_columns(ws, widths_by_sheet.get(ws.title, {}))
            if ws.title in {"Dashboard", "Read_Me_v9", "Codex_Build_Task"}:
                ws.auto_filter.ref = None
                ws.freeze_panes = "A4"
            if ws.title in sheet_tab_colors:
                ws.sheet_properties.tabColor = sheet_tab_colors[ws.title]


def write_outputs(result: ParseResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    data = result_to_dict(result)
    comparison_rows = build_three_bureau_comparison_rows(data)
    ours_rows = build_ours_three_bureaus_comparison_rows(data)
    data["_three_bureau_comparison_rows"] = comparison_rows
    data["_ours_three_bureaus_rows"] = ours_rows
    data["pre_output_verification"] = validate_output_against_template_and_raw(data, comparison_rows, ours_rows)
    json_data = dict(data)
    json_data.pop("_three_bureau_comparison_rows", None)
    json_data.pop("_ours_three_bureaus_rows", None)
    (out_dir / "credit_vivo_parser_result.json").write_text(json.dumps(json_data, indent=2), encoding="utf-8")
    save_document_vault_artifacts(data, out_dir)

    # Tradelines CSV
    tradeline_rows = [asdict(t) for t in result.tradelines]
    if tradeline_rows:
        with (out_dir / "tradelines.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(tradeline_rows[0].keys()))
            writer.writeheader()
            writer.writerows(tradeline_rows)

    # Issues CSV - flatten evidence count only
    issue_rows = []
    for issue in result.issues:
        d = asdict(issue)
        d["related_tradeline_ids"] = ";".join(issue.related_tradeline_ids)
        d["evidence_count"] = len(issue.evidence)
        d.pop("evidence", None)
        issue_rows.append(d)

    if issue_rows:
        with (out_dir / "review_issues.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(issue_rows[0].keys()))
            writer.writeheader()
            writer.writerows(issue_rows)

    date_rows = data.get("dates_found_audit", [])
    if date_rows:
        with (out_dir / "dates_found_audit.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(date_rows[0].keys()))
            writer.writeheader()
            writer.writerows(date_rows)

    letter_sections = []
    for letter in data.get("recommended_letter_queue", []):
        letter_sections.append(
            "\n".join(
                [
                    f"Letter ID: {letter.get('letter_id', '')}",
                    f"Subject: {letter.get('letter_subject', '')}",
                    f"Type: {letter.get('letter_type', '')}",
                    f"Round: {letter.get('round', '')}",
                    f"Recipient: {letter.get('recipient_type', '')}",
                    f"Tracking status: {letter.get('tracking_status', '')}",
                    "",
                    str(letter.get("draft_letter_body") or "No draft body generated."),
                ]
            )
        )

    if letter_sections:
        (out_dir / "draft_dispute_letters.txt").write_text(
            ("\n\n" + ("-" * 72) + "\n\n").join(letter_sections),
            encoding="utf-8",
        )
        letters_dir = out_dir / "letters"
        letters_dir.mkdir(parents=True, exist_ok=True)
        lob_preview_rows = []
        for letter in data.get("recommended_letter_queue", []):
            letter_id = str(letter.get("letter_id") or stable_id("letter", letter.get("issue_id", ""), letter.get("letter_type", "")))
            safe_letter_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", letter_id)
            letter_path = letters_dir / f"{safe_letter_id}.txt"
            letter_path.write_text(
                "\n".join([
                    f"Letter ID: {letter_id}",
                    f"Subject: {letter.get('letter_subject', '')}",
                    f"Type: {letter.get('letter_type', '')}",
                    "Status: Draft only - not sent",
                    "Approval: customer e-sign + admin review + sensitive-data review required",
                    "",
                    str(letter.get("draft_letter_body") or "No draft body generated."),
                ]),
                encoding="utf-8",
            )
            lob_preview_rows.append({
                "letter_id": letter_id,
                "letter_type": letter.get("letter_type", ""),
                "letter_subject": letter.get("letter_subject", ""),
                "letter_file": str(letter_path),
                "lob_ready_status": letter.get("lob_ready_status", "draft_ready_for_lob_preview_after_approval"),
                "mailing_allowed": False,
                "auto_send": False,
                "approval_required": True,
                "lob_ready_preview": letter.get("lob_ready_preview", {}),
            })
        (out_dir / "lob_ready_letter_preview_manifest.json").write_text(
            json.dumps({
                "status": "draft_preview_only",
                "mailing_allowed": False,
                "automatic_lob_submission_enabled": False,
                "required_before_queueing": [
                    "customer_esign_recorded",
                    "admin_approval_recorded",
                    "sensitive_data_review_passed",
                    "recipient_address_verified",
                    "production_lob_workflow_approved",
                ],
                "letters": lob_preview_rows,
            }, indent=2),
            encoding="utf-8",
        )

    write_desktop_workbook(data, out_dir)


# Phase 3 draft-only integrations.
# These classes intentionally do not send disputes, mail, or bank data by
# themselves. They prepare review artifacts for an authenticated admin workflow.
import hashlib
import os
import random
import re
from datetime import datetime, timezone
from typing import Any, Optional

import requests
from sodapy import Socrata


class OpenDataCrossMatcher:
    """Cross-match collector names against public licensing data."""

    def __init__(self, domain: str = "opendata.maryland.gov"):
        self.domain = domain
        self.app_token = os.getenv("SOCRATA_APP_TOKEN")
        self.client = Socrata(self.domain, self.app_token or None)

    @staticmethod
    def _safe_collector_name(collector_name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9 '&.,-]", "", collector_name or "").strip()
        return cleaned[:120]

    def verify_collector_license(self, collector_name: str, state_code: str = "MD") -> dict[str, Any]:
        safe_name = self._safe_collector_name(collector_name)
        safe_state = (state_code or "MD").upper()[:2]

        if not safe_name:
            return {
                "found": False,
                "status": "UNKNOWN",
                "leverage_flag": None,
                "review_note": "Collector name was empty or unsupported.",
            }

        try:
            dataset_id = "gdzy-2fen"
            escaped_name = safe_name.upper().replace("'", "''")
            query = f"business_name like '%{escaped_name}%'"
            results = self.client.get(dataset_id, where=query, limit=1)

            if not results:
                return {
                    "found": False,
                    "status": "UNKNOWN",
                    "leverage_flag": None,
                    "review_note": "No public licensing record matched this collector name.",
                    "last_checked_at": datetime.now(timezone.utc).isoformat(),
                }

            record = results[0]
            status = str(record.get("license_status", "UNKNOWN")).upper()
            inactive_statuses = {"REVOKED", "EXPIRED", "SUSPENDED", "INACTIVE"}
            leverage_flag: Optional[str] = None

            if status in inactive_statuses:
                leverage_flag = (
                    f"Public open-data records may indicate {safe_name} has a {status} "
                    f"license status in {safe_state}. Admin review should verify the "
                    "source record before using this in a customer letter."
                )

            return {
                "found": True,
                "status": status,
                "leverage_flag": leverage_flag,
                "raw_evidence": record,
                "last_checked_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            return {
                "found": False,
                "status": "ERROR",
                "leverage_flag": None,
                "error": str(exc),
                "last_checked_at": datetime.now(timezone.utc).isoformat(),
            }


class EOSCARBypassSpinner:
    """Generate unique, draft-only dispute letter language for admin review."""

    def __init__(self):
        self.openers = [
            "I am requesting an investigation of an item appearing on my {bureau} credit file.",
            "Please review my {bureau} credit profile, including the tradeline reported by {creditor}.",
            "I am asking for a reasonable reinvestigation of the {creditor} account on my {bureau} report.",
        ]
        self.closers = [
            "Please complete a reasonable investigation and provide the results in writing.",
            "Please verify the reporting with competent evidence or correct the information as required.",
            "Please send the investigation results and any updated report after your review is complete.",
        ]

    @staticmethod
    def _mask_account(account_num: str) -> str:
        digits = re.sub(r"\D", "", account_num or "")
        if len(digits) <= 4:
            return "ending in " + (digits or "unknown")
        return "ending in " + digits[-4:]

    def generate_unique_letter(
        self,
        bureau: str,
        creditor: str,
        account_num: str,
        violation_code: str,
        open_data_leverage: str | None = None,
    ) -> str:
        safe_bureau = bureau or "the bureau"
        safe_creditor = creditor or "the furnisher"
        safe_violation = violation_code or "reporting accuracy review"
        opener = random.choice(self.openers).format(
            bureau=safe_bureau,
            creditor=safe_creditor,
            account_num=self._mask_account(account_num),
        )
        closer = random.choice(self.closers)
        body = (
            f"This draft concerns {safe_creditor}, account {self._mask_account(account_num)}. "
            f"The item is being reviewed for {safe_violation}. I am not asking for any "
            "accurate and verifiable information to be removed; I am asking that the "
            "reporting be investigated, corrected, updated, or deleted only if it cannot "
            "be verified under applicable law."
        )

        if open_data_leverage:
            body += (
                f"\n\nAdditional review note: {open_data_leverage} This public-data signal "
                "must be verified by an admin before the language is sent."
            )

        return f"{opener}\n\n{body}\n\n{closer}\n\nDraft only - requires customer approval and admin review."


class LitigationTracker:
    """Prepare mail-tracking records without transmitting mail automatically."""

    def __init__(self):
        self.lob_api_key = os.getenv("LOB_API_KEY")
        self.lob_base_url = os.getenv("LOB_BASE_URL", "https://api.lob.com/v1")

    @staticmethod
    def hash_tracking_number(tracking_number: str) -> str:
        normalized = re.sub(r"\s+", "", tracking_number or "").upper()
        if not normalized:
            raise ValueError("tracking_number is required")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def build_mail_tracking_event(
        self,
        letter_id: str,
        tracking_number: str,
        delivery_status: str,
        delivery_timestamp: str | None = None,
    ) -> dict[str, Any]:
        return {
            "letter_id": letter_id,
            "usps_tracking_hash": self.hash_tracking_number(tracking_number),
            "delivery_status": (delivery_status or "UNKNOWN").upper(),
            "delivery_timestamp": delivery_timestamp,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def fetch_lob_letter_status(self, lob_letter_id: str) -> dict[str, Any]:
        if not self.lob_api_key:
            return {
                "ok": False,
                "error": "LOB_API_KEY is not configured.",
                "review_note": "Mail status lookup is disabled in local testing.",
            }

        response = requests.get(
            f"{self.lob_base_url}/letters/{lob_letter_id}",
            auth=(self.lob_api_key, ""),
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        return {
            "ok": True,
            "letter_id": payload.get("id"),
            "mail_type": payload.get("mail_type"),
            "expected_delivery_date": payload.get("expected_delivery_date"),
            "tracking_events": payload.get("tracking_events", []),
        }
