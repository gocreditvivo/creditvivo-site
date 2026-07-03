from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ForensicSearchLane:
    name: str
    purpose: str
    sources: List[str]
    search_questions: List[str]
    signals_to_extract: List[str]
    campaign_mapping: str


@dataclass(frozen=True)
class ForensicFindingPattern:
    signal: str
    what_it_means: str
    growth_action: str
    metric_to_watch: str


FORENSIC_SEARCH_LANES: List[ForensicSearchLane] = [
    ForensicSearchLane(
        name="Credit report error demand",
        purpose="Find what consumers are actively confused or angry about on reports.",
        sources=[
            "CFPB complaint database",
            "BBB complaint themes",
            "credit forums",
            "bureau public dispute pages",
            "Google/Bing search demand",
        ],
        search_questions=[
            "Which credit reporting issues are most common right now?",
            "Which phrases do people use when they describe wrong collections, mixed files, or inaccurate late payments?",
            "Which complaint themes map to Credit Vivo scanner findings?",
        ],
        signals_to_extract=[
            "issue frequency",
            "consumer wording",
            "bureau/furnisher category",
            "state trend",
            "urgency level",
        ],
        campaign_mapping="/collection-not-mine",
    ),
    ForensicSearchLane(
        name="Auto loan denial demand",
        purpose="Find people searching for why they were denied or quoted a high APR.",
        sources=[
            "Google/Bing keyword tools",
            "auto forums",
            "dealer association content",
            "CFPB auto loan complaints",
            "YouTube comments and topics",
        ],
        search_questions=[
            "What terms do consumers use after a car loan denial?",
            "What credit issues block or raise auto loan pricing?",
            "Which partners see these customers before Credit Vivo does?",
        ],
        signals_to_extract=[
            "denial phrase",
            "APR concern",
            "dealer pain point",
            "finance manager objection",
            "pre-application question",
        ],
        campaign_mapping="/auto-loan-denial",
    ),
    ForensicSearchLane(
        name="Mortgage readiness demand",
        purpose="Find homebuyer credit-readiness problems before application or underwriting.",
        sources=[
            "mortgage forums",
            "realtor/mortgage partner pages",
            "housing counseling directories",
            "NY Fed household debt data",
            "CFPB mortgage complaints",
        ],
        search_questions=[
            "What credit issues stop mortgage applicants?",
            "Which questions appear before homebuyers apply?",
            "Which partners can refer people before denial?",
        ],
        signals_to_extract=[
            "mortgage readiness phrase",
            "collection before mortgage",
            "credit score concern",
            "debt-to-income concern",
            "partner referral type",
        ],
        campaign_mapping="/mortgage-readiness",
    ),
    ForensicSearchLane(
        name="Rental and apartment denial demand",
        purpose="Find credit report and screening issues connected to renting.",
        sources=[
            "renter forums",
            "tenant help organizations",
            "housing counselor directories",
            "state/local housing data",
            "search demand",
        ],
        search_questions=[
            "What credit issues trigger apartment denial questions?",
            "Which rental-screening phrases do consumers use?",
            "Which community partners can send opt-in referrals?",
        ],
        signals_to_extract=[
            "rental denial wording",
            "screening company mention",
            "collection or eviction confusion",
            "state/city housing stress",
            "partner agency",
        ],
        campaign_mapping="/apartment-denial",
    ),
    ForensicSearchLane(
        name="Competitor weakness search",
        purpose="Find what consumers dislike about credit repair and monitoring competitors.",
        sources=[
            "BBB company complaints",
            "Trustpilot and app-store themes",
            "Reddit and forum themes",
            "public reviews",
            "competitor pricing pages",
        ],
        search_questions=[
            "What do customers complain about in credit repair companies?",
            "Which promises create distrust?",
            "What do competitors fail to explain clearly?",
        ],
        signals_to_extract=[
            "complaint theme",
            "pricing objection",
            "trust issue",
            "cancel/refund issue",
            "missing feature",
        ],
        campaign_mapping="/why",
    ),
    ForensicSearchLane(
        name="Partner source search",
        purpose="Find organizations that already encounter Credit Vivo's best-fit customers.",
        sources=[
            "dealer associations",
            "mortgage associations",
            "realtor associations",
            "housing counseling directories",
            "credit counseling directories",
            "consumer attorney directories",
        ],
        search_questions=[
            "Who sees the customer before Credit Vivo does?",
            "Which partner has repeat contact with denied or confused consumers?",
            "Which partner can send opt-in referrals with a tracked link?",
        ],
        signals_to_extract=[
            "partner category",
            "public contact route",
            "customer overlap",
            "referral fit",
            "campaign link",
        ],
        campaign_mapping="/join?source=partner",
    ),
]


FORENSIC_FINDING_PATTERNS: List[ForensicFindingPattern] = [
    ForensicFindingPattern(
        signal="Many searches use denial language",
        what_it_means="The customer is urgent and may act now.",
        growth_action="Send traffic to a problem-specific page, not the generic homepage.",
        metric_to_watch="landing page join rate",
    ),
    ForensicFindingPattern(
        signal="Many complaints mention confusing verification or unresolved disputes",
        what_it_means="Customers need plain-English explanation and tracking.",
        growth_action="Promote scanner findings, dispute tracking, and attorney-ready escalation preparation.",
        metric_to_watch="scan completion and pricing view rate",
    ),
    ForensicFindingPattern(
        signal="Partners already handle the problem manually",
        what_it_means="Referral channel may convert better than broad ads.",
        growth_action="Create a tracked partner referral link and partner one-pager.",
        metric_to_watch="partner referral scan completion rate",
    ),
    ForensicFindingPattern(
        signal="Forums repeat the same question in plain language",
        what_it_means="This is a content and search-ad opportunity.",
        growth_action="Write a learning page and matching search ad using the same plain-language phrase.",
        metric_to_watch="organic clicks and Join Free clicks",
    ),
    ForensicFindingPattern(
        signal="Competitor complaints mention hidden fees, slow progress, or unclear work",
        what_it_means="Credit Vivo should differentiate on clarity, tracking, and customer control.",
        growth_action="Use comparison messaging: AI check-in, plain-English findings, progress tracking.",
        metric_to_watch="pricing page conversion rate",
    ),
]


def lane_to_dict(lane: ForensicSearchLane) -> Dict[str, object]:
    return lane.__dict__


def pattern_to_dict(pattern: ForensicFindingPattern) -> Dict[str, str]:
    return pattern.__dict__


def run_forensic_search(query: str = "Find the strongest growth opportunity for Credit Vivo") -> Dict[str, object]:
    normalized = query.lower()
    query_words = [word for word in normalized.split() if len(word) > 3]
    scored_lanes = []

    for lane in FORENSIC_SEARCH_LANES:
        haystack = f"{lane.name} {lane.purpose} {' '.join(lane.search_questions)}".lower()
        score = sum(1 for word in query_words if word in haystack)
        if lane.name.lower() in normalized:
            score += 10
        if "auto loan" in normalized and "auto loan" in haystack:
            score += 8
        if "mortgage" in normalized and "mortgage" in haystack:
            score += 8
        if "competitor" in normalized and "competitor" in haystack:
            score += 8
        if "apartment" in normalized and "apartment" in haystack:
            score += 8
        if "collection" in normalized and "collection" in haystack:
            score += 8
        if score > 0:
            scored_lanes.append((score, lane))

    selected_lanes = [lane for _, lane in sorted(scored_lanes, key=lambda item: item[0], reverse=True)]

    if not selected_lanes:
        selected_lanes = FORENSIC_SEARCH_LANES[:3]

    return {
        "ok": True,
        "service": "credit-vivo-growth-forensic-search",
        "query": query,
        "mode": "search_sources_extract_signals_map_campaign_verify",
        "selected_lanes": [lane_to_dict(lane) for lane in selected_lanes],
        "finding_patterns": [pattern_to_dict(pattern) for pattern in FORENSIC_FINDING_PATTERNS],
        "owner_brief": {
            "best_first_search": selected_lanes[0].name,
            "why": selected_lanes[0].purpose,
            "campaign_to_use": selected_lanes[0].campaign_mapping,
            "next_action": "Collect source evidence, extract repeated consumer wording, map it to a campaign page, then test traffic against Join Free and scanner-start rates.",
            "verification": "A finding is useful only if it improves Join Free clicks, scan starts, scan completions, or paid upgrades.",
        },
        "output_fields": [
            "source",
            "search_query",
            "signal",
            "customer_words",
            "pain_point",
            "campaign_page",
            "ad_angle",
            "partner_type",
            "metric_to_watch",
        ],
    }


def build_forensic_search_brief() -> Dict[str, object]:
    return {
        "ok": True,
        "service": "credit-vivo-growth-forensic-search",
        "plain_english_summary": "Growth AI can search demand sources, extract repeated pain signals, map them to campaigns, and tell the owner what to test next.",
        "lanes": [lane_to_dict(lane) for lane in FORENSIC_SEARCH_LANES],
        "finding_patterns": [pattern_to_dict(pattern) for pattern in FORENSIC_FINDING_PATTERNS],
        "example_queries": [
            "Find auto loan denial demand",
            "Find collection not mine wording",
            "Find mortgage readiness partner opportunities",
            "Find competitor complaint weaknesses",
            "Find renter denial credit issues",
        ],
    }
