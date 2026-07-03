from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AdChannelSkill:
    channel: str
    role: str
    best_use: str
    required_setup: List[str]
    policy_guardrails: List[str]
    first_campaign: str


@dataclass(frozen=True)
class AdCreative:
    campaign: str
    channel: str
    audience_signal: str
    headline: str
    body: str
    cta: str
    landing_page: str
    compliance_note: str


AD_CHANNEL_SKILLS: List[AdChannelSkill] = [
    AdChannelSkill(
        channel="Google Search",
        role="Capture high-intent searches.",
        best_use="People actively searching for credit report errors, collections, apartment denial, auto loan denial, and mortgage readiness.",
        required_setup=[
            "Google Ads account",
            "conversion tracking for Join Free",
            "negative keywords for guaranteed repair language",
            "compliance-reviewed landing pages",
        ],
        policy_guardrails=[
            "Avoid credit repair promises.",
            "Avoid personalized targeting around negative financial status.",
            "Use education, report review, and no-hard-pull check-in language.",
        ],
        first_campaign="Credit report check-in search campaign",
    ),
    AdChannelSkill(
        channel="Microsoft/Bing Search",
        role="Capture searchers on Bing, Yahoo, and partner search.",
        best_use="Older, homeowner, mortgage, and desktop search audiences with intent-driven queries.",
        required_setup=[
            "Microsoft Advertising account",
            "conversion tracking",
            "import-safe keyword list",
            "policy-reviewed ad copy",
        ],
        policy_guardrails=[
            "Comply with financial services ad policies.",
            "Do not imply guaranteed approval, deletion, or score increase.",
            "Send traffic to transparent educational landing pages.",
        ],
        first_campaign="Mortgage readiness and collections review search campaign",
    ),
    AdChannelSkill(
        channel="Meta Facebook/Instagram",
        role="Build awareness and collect opt-in leads.",
        best_use="Broad educational campaigns for people interested in credit learning, buying a car, renting, or buying a home.",
        required_setup=[
            "Meta Business account",
            "Financial Products and Services category when required",
            "lead form or landing page conversion tracking",
            "creative approval checklist",
        ],
        policy_guardrails=[
            "Use required financial-services category where applicable.",
            "Target adults only.",
            "Avoid copy that says or implies the viewer personally has bad credit, debt, denial, or hardship.",
        ],
        first_campaign="Free Credit Check-In awareness campaign",
    ),
    AdChannelSkill(
        channel="TikTok",
        role="Short education videos and founder/brand trust.",
        best_use="Simple explainers: what a collection means, what a credit report error looks like, and what to check before applying.",
        required_setup=[
            "TikTok Ads account",
            "short video creative",
            "landing page pixel",
            "age and policy review",
        ],
        policy_guardrails=[
            "Do not shame or call out viewers' financial status.",
            "Avoid guaranteed outcomes.",
            "Use education-first content and opt-in calls to action.",
        ],
        first_campaign="Credit mistakes explained in plain English",
    ),
    AdChannelSkill(
        channel="Reddit",
        role="Contextual education and community-aware ads.",
        best_use="Personal finance, credit cards, car buying, mortgage, renting, and debt education contexts.",
        required_setup=[
            "Reddit Ads account",
            "community-safe creative",
            "financial services policy review",
            "landing page with clear disclosures",
        ],
        policy_guardrails=[
            "Follow Reddit financial services restrictions.",
            "Do not scrape users or target people from hardship posts.",
            "Use educational, non-invasive ads.",
        ],
        first_campaign="Credit report review education campaign",
    ),
    AdChannelSkill(
        channel="YouTube",
        role="Explain and build trust before customers join.",
        best_use="Short video ads and educational videos for report errors, collections, and credit readiness.",
        required_setup=[
            "YouTube channel",
            "Google Ads video campaign",
            "retargeting only where allowed",
            "plain-English disclosure language",
        ],
        policy_guardrails=[
            "No credit repair guarantees.",
            "No before/after score claims.",
            "Use educational positioning and clear next steps.",
        ],
        first_campaign="What to check before your next loan application",
    ),
    AdChannelSkill(
        channel="Partner/referral ads",
        role="Reach customers through trusted businesses.",
        best_use="Auto dealers, mortgage brokers, realtors, housing counselors, tax preparers, employers, and community nonprofits.",
        required_setup=[
            "partner outreach list",
            "co-branded referral link",
            "tracking source code",
            "approved partner email/social copy",
        ],
        policy_guardrails=[
            "Partner must not share private customer data without consent.",
            "Use opt-in referral links.",
            "Avoid claiming Credit Vivo is endorsed by government, bureaus, or attorneys unless contractually true.",
        ],
        first_campaign="Partner referral: free Credit Check-In",
    ),
]


AD_CREATIVES: List[AdCreative] = [
    AdCreative(
        campaign="Free Credit Check-In",
        channel="Google Search",
        audience_signal="searching for credit report errors or confusing report items",
        headline="Free Credit Check-In",
        body="See possible credit report issues in plain English. No hard pull to start.",
        cta="Start Free",
        landing_page="/join",
        compliance_note="Education/check-in language. No guarantee of deletion, approval, or score increase.",
    ),
    AdCreative(
        campaign="Auto Loan Denial",
        channel="Google Search",
        audience_signal="searching after auto loan denial or high APR concern",
        headline="Before Your Next Auto Loan",
        body="Check your credit report for possible issues before you try again. Start with a free Credit Check-In.",
        cta="Start Free",
        landing_page="/auto-loan-denial",
        compliance_note="Avoid saying the viewer was denied or has bad credit; frame as preparation.",
    ),
    AdCreative(
        campaign="Mortgage Readiness",
        channel="Microsoft/Bing Search",
        audience_signal="searching mortgage readiness, collections before mortgage, credit report before home loan",
        headline="Get Mortgage-Ready Clarity",
        body="Review possible credit report issues before your next home loan step. Plain-English AI review.",
        cta="Check Your Report",
        landing_page="/mortgage-readiness",
        compliance_note="No approval promises. Use readiness and review language.",
    ),
    AdCreative(
        campaign="Apartment Denial",
        channel="Meta Facebook/Instagram",
        audience_signal="broad renter education audience",
        headline="Understand Your Credit Report",
        body="Renting soon? Start with a no-hard-pull Credit Check-In and see possible report issues in plain English.",
        cta="Join Free",
        landing_page="/apartment-denial",
        compliance_note="Do not imply the viewer was denied housing or has a negative status.",
    ),
    AdCreative(
        campaign="Collection Not Mine",
        channel="Reddit",
        audience_signal="contextual credit education and debt collection questions",
        headline="Collection Account Look Unfamiliar?",
        body="Credit Vivo helps organize possible report issues so you can understand your next step.",
        cta="Start Check-In",
        landing_page="/collection-not-mine",
        compliance_note="Educational. Do not target users from hardship posts.",
    ),
    AdCreative(
        campaign="Credit Learning",
        channel="TikTok",
        audience_signal="credit education video viewers",
        headline="Credit Reports, Plain English",
        body="AI helps explain possible report problems and what to review next.",
        cta="Start Free",
        landing_page="/learning",
        compliance_note="No personalized negative financial claims.",
    ),
    AdCreative(
        campaign="Partner Referral",
        channel="Partner/referral ads",
        audience_signal="referred by dealer, mortgage, realtor, housing, or counseling partner",
        headline="Give Customers a Credit Check-In",
        body="A simple no-hard-pull starting point for customers who need credit report clarity.",
        cta="Create Referral Link",
        landing_page="/join",
        compliance_note="Partner must use opt-in links and cannot share customer data without consent.",
    ),
    AdCreative(
        campaign="Attorney Access Positioning",
        channel="YouTube",
        audience_signal="education viewers comparing credit help options",
        headline="AI Review. Attorney Support When Needed.",
        body="Start with AI credit report review. If the issue is serious, prepare your file for attorney review options.",
        cta="Start Free",
        landing_page="/pricing",
        compliance_note="Keep attorney services separate and do not imply legal advice from Credit Vivo.",
    ),
]


def channel_skill_to_dict(skill: AdChannelSkill) -> Dict[str, object]:
    return skill.__dict__


def ad_creative_to_dict(creative: AdCreative) -> Dict[str, str]:
    return creative.__dict__


def build_ad_plan() -> Dict[str, object]:
    channel_counts: Dict[str, int] = {}
    for creative in AD_CREATIVES:
        channel_counts[creative.channel] = channel_counts.get(creative.channel, 0) + 1

    return {
        "ok": True,
        "service": "credit-vivo-growth-ads-ai",
        "mode": "draft_review_launch_measure",
        "guardrail": "Growth AI can draft and score ads. Owner/compliance approval is required before launch or spend.",
        "ad_channel_skills": [channel_skill_to_dict(skill) for skill in AD_CHANNEL_SKILLS],
        "ad_creatives": [ad_creative_to_dict(creative) for creative in AD_CREATIVES],
        "counts": {
            "channels": len(AD_CHANNEL_SKILLS),
            "ad_creatives": len(AD_CREATIVES),
            "creative_by_channel": channel_counts,
        },
        "launch_sequence": [
            "Set up GA4, Search Console, and conversion events first.",
            "Launch search campaigns with exact and phrase-match high-intent keywords.",
            "Launch partner/referral links with tracked source codes.",
            "Test Meta/TikTok/YouTube with education-first creative.",
            "Use Reddit for contextual education and trust, not direct hardship targeting.",
            "Review cost per lead, scan completion rate, and paid conversion weekly.",
            "Pause any campaign with high spend and low scan completion.",
        ],
    }
