from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

try:
    from .growth_ads_ai import build_ad_plan
    from .growth_ai import GrowthSnapshot, build_growth_brief
    from .growth_ai_sources import build_growth_source_brief
except ImportError:
    from growth_ads_ai import build_ad_plan
    from growth_ai import GrowthSnapshot, build_growth_brief
    from growth_ai_sources import build_growth_source_brief


@dataclass(frozen=True)
class CodexAdvisorSkill:
    name: str
    purpose: str
    when_to_use: str
    expected_output: str


CODEX_ADVISOR_SKILLS: List[CodexAdvisorSkill] = [
    CodexAdvisorSkill(
        name="growth_strategy_review",
        purpose="Review Growth AI's plan and improve the next best growth moves.",
        when_to_use="Before launching a campaign, changing funnel strategy, or spending ad money.",
        expected_output="Prioritized growth plan, assumptions, risks, metrics to watch, and next experiment.",
    ),
    CodexAdvisorSkill(
        name="ad_copy_review",
        purpose="Review ads for clarity, conversion, channel fit, and platform policy risk.",
        when_to_use="Before publishing ads on Google, Bing, Meta, TikTok, Reddit, YouTube, or partner channels.",
        expected_output="Improved ad copy, rejected weak claims, landing page match, and approval checklist.",
    ),
    CodexAdvisorSkill(
        name="funnel_diagnostics",
        purpose="Diagnose where visitors, leads, scans, or paid upgrades are dropping off.",
        when_to_use="When Growth AI sees weak conversion, high ad spend, poor scan completion, or low paid upgrade rate.",
        expected_output="Likely bottleneck, needed data, suggested fix, and verification step.",
    ),
    CodexAdvisorSkill(
        name="partner_outreach_review",
        purpose="Improve partner/referral outreach to dealers, mortgage pros, realtors, housing counselors, and nonprofits.",
        when_to_use="Before sending partner outreach or creating co-branded referral materials.",
        expected_output="Partner pitch, follow-up sequence, referral offer, and tracking fields.",
    ),
    CodexAdvisorSkill(
        name="landing_page_review",
        purpose="Review landing pages for plain-English value, trust, conversion, and consistency with campaign intent.",
        when_to_use="Before sending paid or partner traffic to a campaign page.",
        expected_output="Copy edits, missing proof, CTA improvements, and route-specific test plan.",
    ),
    CodexAdvisorSkill(
        name="measurement_plan",
        purpose="Define the events and dashboards Growth AI needs to learn.",
        when_to_use="Before scaling any channel or when Growth AI says data is missing.",
        expected_output="Event list, naming standard, source tracking, and weekly founder report format.",
    ),
]


def advisor_skill_to_dict(skill: CodexAdvisorSkill) -> Dict[str, str]:
    return skill.__dict__


def build_codex_advisor_prompt(
    question: str,
    snapshot: GrowthSnapshot | None = None,
    focus: str = "growth_strategy_review",
) -> str:
    growth_snapshot = snapshot or GrowthSnapshot()
    growth_brief = build_growth_brief(growth_snapshot)
    sources = build_growth_source_brief()
    ads = build_ad_plan()

    return f"""You are advising Credit Vivo Growth AI.

Founder goal:
Grow Credit Vivo into a national AI credit check-in and attorney-support brand.

Advice focus:
{focus}

Founder question:
{question}

Current Growth AI facts:
- Current MRR: ${growth_brief['snapshot']['monthly_recurring_revenue']}
- Paid customers: {growth_brief['snapshot']['paid_customers']}
- Paid customer gap to $1M/mo target: {growth_brief['million_month_target']['paid_customer_gap']}
- Data sources available: {sources['counts']['data_sources']}
- Market signal sources available: {sources['counts']['market_signal_sources']}
- Public partner leads available: {sources['counts']['public_partner_leads']}
- Ad channels available: {ads['counts']['channels']}
- Starter ad creatives available: {ads['counts']['ad_creatives']}

Current Growth AI recommendation:
{growth_brief['recommended_actions'][0]['action']}

Required output:
1. Best next action.
2. Why it matters.
3. Exact campaign/ad/funnel move to make.
4. What data Growth AI needs next.
5. How to verify whether it worked.
6. What needs owner approval before launch.

Write in plain English for a non-technical founder.
"""


def build_codex_advisor_brief(
    question: str = "What should Growth AI do next to bring Credit Vivo customers?",
    snapshot: GrowthSnapshot | None = None,
    focus: str = "growth_strategy_review",
) -> Dict[str, object]:
    return {
        "ok": True,
        "service": "credit-vivo-codex-advisor-bridge",
        "mode": "package_context_request_advice_record_recommendation",
        "plain_english_summary": (
            "Growth AI can package its current facts into a Codex-ready prompt for strategy, ad, funnel, "
            "partner, landing page, and measurement advice. A direct automated Codex call requires Codex SDK/API setup."
        ),
        "codex_capability_path": {
            "today": "Generate a Codex-ready advisor prompt and paste/run it in Codex.",
            "next": "Use Codex SDK from a secure backend worker when credentials and runtime are approved.",
            "future": "Give Growth AI a task queue that asks Codex for reviews, stores answers, and creates approved work items.",
        },
        "advisor_skills": [advisor_skill_to_dict(skill) for skill in CODEX_ADVISOR_SKILLS],
        "codex_prompt": build_codex_advisor_prompt(question=question, snapshot=snapshot, focus=focus),
        "approval_rule": "Growth AI can ask Codex for advice. Owner approval is required before launching ads, sending outreach, changing prices, or changing public legal/compliance language.",
    }
