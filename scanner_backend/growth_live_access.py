from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LiveAccessTool:
    name: str
    category: str
    official_url: str
    access_needed: List[str]
    growth_ai_reads: List[str]
    growth_ai_can_do: List[str]
    execution_level: str
    setup_priority: str


LIVE_ACCESS_TOOLS: List[LiveAccessTool] = [
    LiveAccessTool(
        name="Credit Vivo first-party event tracking",
        category="owned_product_data",
        official_url="internal",
        access_needed=["website event collector", "scanner event collector", "campaign source tags"],
        growth_ai_reads=["join_clicked", "lead_created", "scan_started", "scan_completed", "pricing_viewed", "paid_upgrade"],
        growth_ai_can_do=["diagnose funnel leaks", "rank campaigns by completed scans", "find missing events"],
        execution_level="read_and_analyze",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="Google Analytics 4 Data API",
        category="website_analytics",
        official_url="https://developers.google.com/analytics/devguides/reporting/data/v1",
        access_needed=["Google Cloud project", "GA4 property access", "service account or OAuth", "property id"],
        growth_ai_reads=["traffic source", "landing page views", "campaign traffic", "conversion events", "drop-off pages"],
        growth_ai_can_do=["daily traffic brief", "source conversion analysis", "landing page recommendations"],
        execution_level="read_only_first",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="Google Search Console API",
        category="search_data",
        official_url="https://developers.google.com/webmaster-tools",
        access_needed=["verified creditvivo.com property", "Google Cloud OAuth/service account", "site permission"],
        growth_ai_reads=["queries", "impressions", "clicks", "average position", "top pages"],
        growth_ai_can_do=["find SEO topics", "recommend learning pages", "spot search demand by campaign"],
        execution_level="read_only_first",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="Stripe API and webhooks",
        category="payments",
        official_url="https://docs.stripe.com/webhooks",
        access_needed=["Stripe account", "restricted API key", "webhook endpoint", "selected events"],
        growth_ai_reads=["subscription created", "payment succeeded", "payment failed", "refund", "cancellation", "MRR"],
        growth_ai_can_do=["track revenue", "calculate churn", "flag failed payments", "measure paid upgrade rate"],
        execution_level="read_and_alert",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="Google Ads API",
        category="ad_platform",
        official_url="https://developers.google.com/google-ads/api",
        access_needed=["Google Ads account", "developer token", "OAuth credentials", "customer id"],
        growth_ai_reads=["campaign spend", "clicks", "conversions", "keywords", "cost per lead"],
        growth_ai_can_do=["recommend pause/scale", "write keyword tests", "compare cost per scan start"],
        execution_level="read_only_then_owner_approved_changes",
        setup_priority="phase_2_paid_growth",
    ),
    LiveAccessTool(
        name="Microsoft Advertising API",
        category="ad_platform",
        official_url="https://learn.microsoft.com/en-us/advertising/",
        access_needed=["Microsoft Ads account", "developer token", "OAuth credentials", "customer/account ids"],
        growth_ai_reads=["campaign reports", "keyword reports", "spend", "clicks", "conversions"],
        growth_ai_can_do=["compare Bing/Yahoo search performance", "recommend bid and keyword tests"],
        execution_level="read_only_then_owner_approved_changes",
        setup_priority="phase_2_paid_growth",
    ),
    LiveAccessTool(
        name="Meta Marketing API Insights",
        category="ad_platform",
        official_url="https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights",
        access_needed=["Meta Business account", "app", "ad account access", "access token", "approved permissions"],
        growth_ai_reads=["impressions", "clicks", "spend", "leads", "campaign performance"],
        growth_ai_can_do=["compare social creative", "recommend pause/scale", "spot cheap-click low-quality campaigns"],
        execution_level="read_only_then_owner_approved_changes",
        setup_priority="phase_3_social_scale",
    ),
    LiveAccessTool(
        name="TikTok API for Business",
        category="ad_platform",
        official_url="https://business-api.tiktok.com/portal/docs",
        access_needed=["TikTok Business account", "advertiser id", "app access", "access token"],
        growth_ai_reads=["video ad spend", "clicks", "conversions", "creative performance"],
        growth_ai_can_do=["recommend video hooks", "rank short-form topics", "pause weak creatives"],
        execution_level="read_only_then_owner_approved_changes",
        setup_priority="phase_3_social_scale",
    ),
    LiveAccessTool(
        name="Reddit Ads API",
        category="ad_platform",
        official_url="https://ads-api.reddit.com/docs/v3/",
        access_needed=["Reddit Ads account", "API access", "OAuth credentials", "ad account id"],
        growth_ai_reads=["campaign analytics", "spend", "clicks", "community/context performance"],
        growth_ai_can_do=["test education-first Reddit campaigns", "rank topics by scan starts"],
        execution_level="read_only_then_owner_approved_changes",
        setup_priority="phase_3_social_scale",
    ),
    LiveAccessTool(
        name="Supabase Postgres",
        category="database_memory",
        official_url="https://supabase.com/docs",
        access_needed=["Supabase project", "Postgres database", "service role key stored as secret", "tables"],
        growth_ai_reads=["events", "leads", "campaigns", "experiments", "recommendations", "approvals"],
        growth_ai_can_do=["remember what worked", "generate daily brief", "track 12-month goal progress"],
        execution_level="read_write_internal",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="Render Cron Jobs",
        category="worker_scheduler",
        official_url="https://render.com/docs/cronjobs",
        access_needed=["Render account", "GitHub repo connection", "cron service", "environment secrets"],
        growth_ai_reads=["scheduled job status", "daily worker result", "errors"],
        growth_ai_can_do=["run daily growth brief", "run hourly health checks", "trigger report imports"],
        execution_level="internal_automation",
        setup_priority="phase_1_must_have",
    ),
    LiveAccessTool(
        name="SendGrid Email API",
        category="alerts_outreach",
        official_url="https://www.twilio.com/docs/sendgrid/api-reference",
        access_needed=["SendGrid account", "API key", "verified sender/domain", "suppression handling"],
        growth_ai_reads=["delivery status", "opens/clicks if enabled", "bounce data"],
        growth_ai_can_do=["send founder briefs", "send owner-approved partner outreach", "send system alerts"],
        execution_level="owner_approved_sends",
        setup_priority="phase_2_operations",
    ),
    LiveAccessTool(
        name="Twilio Messaging API",
        category="alerts_messaging",
        official_url="https://www.twilio.com/docs/messaging/api",
        access_needed=["Twilio account", "phone number or messaging service", "API credentials", "opt-in rules"],
        growth_ai_reads=["delivery status", "message failures"],
        growth_ai_can_do=["send urgent owner alerts", "send approved customer SMS only with consent"],
        execution_level="owner_approved_sends",
        setup_priority="phase_3_alerts",
    ),
]


def tool_to_dict(tool: LiveAccessTool) -> Dict[str, object]:
    return tool.__dict__


def build_live_access_brief() -> Dict[str, object]:
    by_priority: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    for tool in LIVE_ACCESS_TOOLS:
        by_priority[tool.setup_priority] = by_priority.get(tool.setup_priority, 0) + 1
        by_category[tool.category] = by_category.get(tool.category, 0) + 1

    return {
        "ok": True,
        "service": "credit-vivo-growth-live-access-map",
        "plain_english_summary": "Growth AI needs live access through APIs, webhooks, scheduled workers, and a database. Start read-only, store results in Supabase, run scheduled jobs on Render, and require owner approval for spend, sends, or public changes.",
        "tools": [tool_to_dict(tool) for tool in LIVE_ACCESS_TOOLS],
        "counts": {
            "tools": len(LIVE_ACCESS_TOOLS),
            "by_priority": by_priority,
            "by_category": by_category,
        },
        "first_30_day_setup_order": [
            "Credit Vivo first-party event tracking",
            "Supabase Postgres",
            "Render Cron Jobs",
            "Google Analytics 4 Data API",
            "Google Search Console API",
            "Stripe API and webhooks",
            "Google Ads API read-only reporting",
            "SendGrid founder daily brief",
        ],
        "approval_rules": [
            "Read-only reporting can be automated.",
            "Internal database writes can be automated.",
            "Founder briefs can be sent automatically to the owner.",
            "Ad launches, ad spend changes, outreach sends, SMS, pricing changes, and customer messages require owner approval.",
        ],
    }
