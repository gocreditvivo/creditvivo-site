from __future__ import annotations

"""
Credit Vivo Native Parser Engine

This is Credit Vivo's own rule-based parsing layer.

No Anthropic.
No Claude.
No paid AI API.
No PyMuPDF.

Design:
- Extract text with pypdf in the API adapter.
- Run Credit Vivo's native bureau/account parser.
- Return structured review items with raw snippets and confidence.
- Treat output as draft review data, not final legal conclusions.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import re
import hashlib


BUREAU_NAMES = ("Experian", "Equifax", "TransUnion")


@dataclass
class ReviewItem:
    id: str
    bureau: str
    category: str
    account_name: str
    account_number_masked: str = ""
    account_type: str = ""
    status: str = ""
    pay_status: str = ""
    balance: str = ""
    past_due: str = ""
    date_opened: str = ""
    date_closed: str = ""
    date_reported: str = ""
    date_last_payment: str = ""
    date_of_first_delinquency: str = ""
    original_creditor: str = ""
    collector_or_debt_buyer: str = ""
    remarks: str = ""
    possible_issue: str = ""
    customer_friendly_reason: str = ""
    suggested_round: str = ""
    confidence: str = "medium"
    needs_admin_review: bool = True
    raw_snippet: str = ""


def normalize_space(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def mask_account_number(value: str) -> str:
    value = value.strip()
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 4:
        return "*" + digits[-4:]
    if len(value) > 8:
        return value[:2] + "..." + value[-4:]
    return value


def make_id(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return "cv_" + hashlib.sha1(raw).hexdigest()[:12]


def detect_bureau_from_text(filename: str, text: str) -> str:
    lower = (filename + "\n" + text[:3000]).lower()
    if "experian" in lower:
        return "Experian"
    if "equifax" in lower:
        return "Equifax"
    if "transunion" in lower or "trans union" in lower:
        return "TransUnion"
    return "Unknown Bureau"


NEGATIVE_TERMS = [
    "collection", "charge off", "charge-off", "charged off", "late", "past due",
    "delinquent", "derogatory", "settled", "repossession", "foreclosure",
    "120 days", "90 days", "60 days", "30 days", "placed for collection",
    "transferred", "sold", "profit and loss", "written off"
]

COLLECTION_TERMS = [
    "collection", "collector", "debt buyer", "assigned", "placed for collection",
    "original creditor", "collection agency"
]

PROFILE_TERMS = [
    "personal information", "addresses", "address", "employer", "phone", "aliases",
    "name identification", "personal statements"
]

ACCOUNT_START_HINTS = [
    "account name", "account #", "account number", "date opened", "balance",
    "account type", "payment status", "status", "creditor", "remarks"
]

DATE_PATTERNS = [
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2},? \d{4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

FIELD_PATTERNS = {
    "balance": [
        r"(?:balance|current balance)\s*[:\-]?\s*(\$?\s?[0-9,]+(?:\.\d{2})?)",
    ],
    "past_due": [
        r"(?:past due|amount past due)\s*[:\-]?\s*(\$?\s?[0-9,]+(?:\.\d{2})?)",
    ],
    "date_opened": [
        r"(?:date opened|opened)\s*[:\-]?\s*(" + "|".join(DATE_PATTERNS) + r")",
    ],
    "date_closed": [
        r"(?:date closed|closed)\s*[:\-]?\s*(" + "|".join(DATE_PATTERNS) + r")",
    ],
    "date_reported": [
        r"(?:date reported|reported|updated|last reported)\s*[:\-]?\s*(" + "|".join(DATE_PATTERNS) + r")",
    ],
    "date_last_payment": [
        r"(?:last payment|date of last payment|date last payment)\s*[:\-]?\s*(" + "|".join(DATE_PATTERNS) + r")",
    ],
    "date_of_first_delinquency": [
        r"(?:date of first delinquency|first delinquency|dofd)\s*[:\-]?\s*(" + "|".join(DATE_PATTERNS) + r")",
    ],
    "account_number_masked": [
        r"(?:account #|account number|acct #|acct number)\s*[:\-]?\s*([A-Za-z0-9\*\-xX]{3,25})",
    ],
    "account_type": [
        r"(?:account type|type)\s*[:\-]?\s*([A-Za-z /-]{3,40})",
    ],
    "status": [
        r"(?:status|account status)\s*[:\-]?\s*([A-Za-z0-9 /-]{3,60})",
    ],
    "pay_status": [
        r"(?:payment status|pay status)\s*[:\-]?\s*([A-Za-z0-9 /-]{3,80})",
    ],
    "original_creditor": [
        r"(?:original creditor|original lender)\s*[:\-]?\s*([A-Za-z0-9 &.,'/-]{3,70})",
    ],
    "remarks": [
        r"(?:remarks|comments|comment)\s*[:\-]?\s*([A-Za-z0-9 &.,'()/\-]{5,160})",
    ],
}


def first_match(patterns: List[str], text: str) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.I)
        if m:
            return normalize_space(m.group(1))[:160]
    return ""


def split_candidate_blocks(text: str) -> List[str]:
    """
    Split report text into candidate blocks. Credit reports have many formats, so this
    uses conservative signals and keeps raw evidence snippets.
    """
    text = normalize_space(text)

    # Split on multiple newlines first.
    chunks = re.split(r"\n\s*\n", text)
    blocks: List[str] = []

    buffer: List[str] = []
    for chunk in chunks:
        c = chunk.strip()
        if not c:
            continue

        lower = c.lower()
        has_account_hint = any(h in lower for h in ACCOUNT_START_HINTS)
        has_negative = any(t in lower for t in NEGATIVE_TERMS)
        long_enough = len(c) > 80

        if has_account_hint or has_negative:
            if buffer:
                blocks.append("\n".join(buffer))
                buffer = []
            buffer.append(c)
        elif buffer and len("\n".join(buffer)) < 2500:
            buffer.append(c)
        elif long_enough and has_negative:
            blocks.append(c)

    if buffer:
        blocks.append("\n".join(buffer))

    # Fallback: sliding windows around negative terms.
    if not blocks:
        for term in NEGATIVE_TERMS:
            for m in re.finditer(re.escape(term), text, flags=re.I):
                start = max(0, m.start() - 700)
                end = min(len(text), m.end() + 1100)
                blocks.append(text[start:end])
                if len(blocks) >= 30:
                    return dedupe_blocks(blocks)

    return dedupe_blocks(blocks)


def dedupe_blocks(blocks: List[str]) -> List[str]:
    seen = set()
    out = []
    for b in blocks:
        clean = normalize_space(b)
        if len(clean) < 60:
            continue
        key = hashlib.sha1(clean[:500].encode("utf-8", errors="ignore")).hexdigest()
        if key not in seen:
            seen.add(key)
            out.append(clean[:4000])
    return out


def guess_account_name(block: str) -> str:
    lines = [normalize_space(x) for x in block.splitlines() if normalize_space(x)]
    bad_prefixes = (
        "account number", "account #", "balance", "date", "status", "payment",
        "remarks", "comment", "address", "phone", "page", "experian", "equifax",
        "transunion", "credit report"
    )

    # Prefer first short uppercase-ish line that is not a field label.
    for line in lines[:10]:
        l = line.lower().strip(": ")
        if any(l.startswith(b) for b in bad_prefixes):
            continue
        if 3 <= len(line) <= 70 and re.search(r"[A-Za-z]", line):
            # Avoid sentences.
            if len(line.split()) <= 8:
                return line.strip(" :-")

    # Try field label.
    m = re.search(r"(?:creditor|account name|furnisher)\s*[:\-]?\s*([A-Za-z0-9 &.,'/-]{3,70})", block, flags=re.I)
    if m:
        return normalize_space(m.group(1))

    return "Review Item"


def categorize(block: str) -> Tuple[str, str, str]:
    lower = block.lower()

    if any(t in lower for t in COLLECTION_TERMS):
        return (
            "Collection Review",
            "Collection or debt-buyer information may need review.",
            "Round 2 — Collection Review"
        )

    if any(t in lower for t in PROFILE_TERMS) and not any(t in lower for t in ["balance", "account number", "date opened"]):
        return (
            "Profile Cleanup",
            "Personal information may need review or cleanup.",
            "Round 1 — Profile Cleanup"
        )

    if any(t in lower for t in ["transferred", "sold", "closed", "charge off", "charge-off", "charged off"]):
        return (
            "Reporting Accuracy Review",
            "Status, dates, balance, or transfer/sold reporting may need review.",
            "Round 4 — Reporting Accuracy Review"
        )

    if any(t in lower for t in NEGATIVE_TERMS):
        return (
            "Factual Review",
            "This item contains negative reporting terms and should be reviewed for accuracy.",
            "Round 5 — Factual Review"
        )

    return (
        "Bureau Match Review",
        "This item should be compared across bureaus for consistency.",
        "Round 3 — Bureau Match Review"
    )


def confidence_for(item: ReviewItem) -> str:
    score = 0
    if item.account_name and item.account_name != "Review Item":
        score += 2
    if item.account_number_masked:
        score += 2
    if item.balance:
        score += 1
    if item.status or item.pay_status:
        score += 1
    if item.date_opened or item.date_reported or item.date_of_first_delinquency:
        score += 1
    if len(item.raw_snippet) > 200:
        score += 1

    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def parse_bureau_text(bureau: str, text: str) -> List[ReviewItem]:
    blocks = split_candidate_blocks(text)
    items: List[ReviewItem] = []

    for block in blocks:
        lower = block.lower()
        if not any(t in lower for t in NEGATIVE_TERMS + ACCOUNT_START_HINTS):
            continue

        account_name = guess_account_name(block)
        category, reason, round_name = categorize(block)

        account_number = first_match(FIELD_PATTERNS["account_number_masked"], block)
        if account_number:
            account_number = mask_account_number(account_number)

        item = ReviewItem(
            id=make_id(bureau, account_name, account_number, block[:80]),
            bureau=bureau,
            category=category,
            account_name=account_name,
            account_number_masked=account_number,
            account_type=first_match(FIELD_PATTERNS["account_type"], block),
            status=first_match(FIELD_PATTERNS["status"], block),
            pay_status=first_match(FIELD_PATTERNS["pay_status"], block),
            balance=first_match(FIELD_PATTERNS["balance"], block),
            past_due=first_match(FIELD_PATTERNS["past_due"], block),
            date_opened=first_match(FIELD_PATTERNS["date_opened"], block),
            date_closed=first_match(FIELD_PATTERNS["date_closed"], block),
            date_reported=first_match(FIELD_PATTERNS["date_reported"], block),
            date_last_payment=first_match(FIELD_PATTERNS["date_last_payment"], block),
            date_of_first_delinquency=first_match(FIELD_PATTERNS["date_of_first_delinquency"], block),
            original_creditor=first_match(FIELD_PATTERNS["original_creditor"], block),
            remarks=first_match(FIELD_PATTERNS["remarks"], block),
            possible_issue=reason,
            customer_friendly_reason=reason,
            suggested_round=round_name,
            raw_snippet=block[:1500],
        )
        item.confidence = confidence_for(item)
        item.needs_admin_review = item.confidence != "high"
        items.append(item)

    return dedupe_items(items)


def dedupe_items(items: List[ReviewItem]) -> List[ReviewItem]:
    seen = set()
    out = []
    for item in items:
        key = (
            item.bureau.lower(),
            item.account_name.lower()[:40],
            item.account_number_masked,
            item.category,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def parse_credit_reports(text_by_bureau: Dict[str, str]) -> Dict:
    all_items: List[ReviewItem] = []

    for bureau, text in text_by_bureau.items():
        all_items.extend(parse_bureau_text(bureau, text))

    # Add simple cross-bureau grouping hints.
    groups = {}
    for item in all_items:
        normalized = re.sub(r"[^a-z0-9]+", "", item.account_name.lower())[:28] or item.id
        groups.setdefault(normalized, []).append(item)

    bureau_match_notes = []
    for group_key, group_items in groups.items():
        bureaus = sorted({i.bureau for i in group_items})
        if len(bureaus) >= 2:
            bureau_match_notes.append({
                "group": group_key,
                "bureaus": bureaus,
                "account_names": sorted({i.account_name for i in group_items}),
                "review_note": "Same or similar item appears across multiple bureaus. Compare balances, dates, status, and remarks."
            })

    return {
        "engine": "Credit Vivo Native Parser",
        "version": "15.3-no-paid-ai",
        "paid_ai_used": False,
        "items": [asdict(x) for x in all_items],
        "item_count": len(all_items),
        "bureau_match_notes": bureau_match_notes,
        "customer_message": "Your Credit Check-In was reviewed. Items are organized for review before any action is sent.",
        "admin_message": "Native parser output is draft review data. Verify raw snippets before preparing letters."
    }
