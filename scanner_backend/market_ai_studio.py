from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import re
import uuid


DISCLOSURE = (
    "Credit Vivo helps identify possible credit-report issues, prepare documents, and track progress. "
    "Credit Vivo does not guarantee removals, score increases, approvals, or timelines. "
    "Attorney support may be available for eligible unresolved credit-reporting issues."
)

CREDIT_VIVO_BRAND_KIT = {
    "brandName": "Credit Vivo",
    "positioning": "AI Credit Boost + Attorney Support",
    "slogan": "You take control. We clear the path.",
    "trustLine": "Find errors. Build disputes. Track progress.",
    "tone": ["short", "direct", "simple", "confident", "educational"],
    "colors": {
        "blue": "#1F58FF",
        "green": "#2ACF8F",
        "navy": "#08122B",
        "lightBlue": "#EDF8FF",
        "mint": "#E0FFF5",
        "white": "#FFFFFF",
        "gray": "#64748B",
    },
    "disclosure": DISCLOSURE,
}

BANNED_MARKETING_PHRASES = [
    "guaranteed deletion",
    "guaranteed removal",
    "guaranteed score",
    "guaranteed score increase",
    "delete anything",
    "remove all negative",
    "100% guaranteed",
    "instant credit repair",
    "approved for loan",
    "approved for mortgage",
    "approved for apartment",
    "approved for car loan",
    "lawsuit guaranteed",
    "bureaus must delete",
    "we force deletions",
]

PREFERRED_MARKETING_PHRASES = [
    "Find errors",
    "Build disputes",
    "Track progress",
    "Review negative accounts",
    "Compare all 3 bureaus",
    "Focused dispute rounds",
    "Clear next steps",
    "Credit improvement is a process",
    "Attorney support may be available for eligible unresolved credit-reporting issues",
]

LEARNING_TOPICS = [
    {
        "id": "free-weekly-reports",
        "title": "Use Your Free Weekly Reports With Credit Vivo",
        "category": "Free weekly reports",
        "duration": 180,
        "format": "learning_video",
        "hook": "Your credit report can change. Credit Vivo helps you track what changed.",
        "keyPoints": [
            "Customers can review updated reports regularly",
            "All three bureaus may report differently",
            "Upload reports to refresh the scan",
            "Credit Vivo compares changes over time",
        ],
        "cta": "Upload your latest reports and refresh your scan.",
    },
    {
        "id": "three-bureau-comparison",
        "title": "Why Your 3 Credit Reports Can Be Different",
        "category": "3-bureau comparison",
        "duration": 180,
        "format": "learning_video",
        "hook": "Equifax, Experian, and TransUnion do not always match.",
        "keyPoints": [
            "Different bureaus may show different balances",
            "Account status can vary",
            "Dates and timelines may need review",
            "Credit Vivo compares the differences",
        ],
        "cta": "Compare your reports with Credit Vivo.",
    },
    {
        "id": "negative-account-review",
        "title": "Why Negative Accounts Need Careful Review",
        "category": "Negative account review",
        "duration": 180,
        "format": "learning_video",
        "hook": "Collections and charge-offs need more than a quick glance.",
        "keyPoints": ["Review balance", "Review status", "Review Date of First Delinquency", "Review original creditor", "Review timeline"],
        "cta": "Review your negative accounts.",
    },
    {
        "id": "dispute-packet",
        "title": "What Goes Inside a Strong Dispute Packet",
        "category": "Dispute packet basics",
        "duration": 180,
        "format": "learning_video",
        "hook": "A strong dispute is more than a letter.",
        "keyPoints": ["Cover letter", "3-bureau comparison", "Relevant credit report pages", "Evidence", "ID and proof of address when needed", "Mail tracking"],
        "cta": "Review and approve your packet.",
    },
    {
        "id": "credit-improvement-process",
        "title": "Credit Improvement Is a Process",
        "category": "Credit improvement timeline",
        "duration": 180,
        "format": "learning_video",
        "hook": "Credit improvement is a process, not a one-click fix.",
        "keyPoints": ["Dispute rounds can take time", "Responses must be reviewed", "Verified does not always mean resolved", "Follow-ups may be needed", "Progress should be tracked"],
        "cta": "Follow your Credit Vivo plan.",
    },
]

VIDEO_TEMPLATES = [
    {"id": "weekly-report-refresh-3min", "title": "Weekly Report Refresh", "duration": 180, "format": "9:16", "scenes": 12, "visualStyle": "animated-dashboard", "exports": ["9:16", "16:9", "1:1"]},
    {"id": "negative-account-review-3min", "title": "Negative Account Review", "duration": 180, "format": "9:16", "scenes": 12, "visualStyle": "animated-card-sort"},
    {"id": "dispute-packet-3min", "title": "Dispute Packet Explainer", "duration": 180, "format": "9:16", "scenes": 12, "visualStyle": "packet-layer-animation"},
    {"id": "credit-process-3min", "title": "Credit Improvement Process", "duration": 180, "format": "9:16", "scenes": 12, "visualStyle": "timeline-animation"},
]

ANIMATION_TEMPLATES = [
    {"id": "bureau-cards-slide", "title": "Bureau Cards Slide", "elements": ["Equifax card", "Experian card", "TransUnion card"], "motion": "slide-in-staggered"},
    {"id": "comparison-table-reveal", "title": "3-Bureau Comparison Table Reveal", "elements": ["field row", "bureau columns", "issue highlight"], "motion": "row-highlight"},
    {"id": "negative-account-sort", "title": "Negative Account Sort", "elements": ["collection card", "charge-off card", "late-payment card"], "motion": "sort-by-issue"},
    {"id": "dispute-packet-layers", "title": "Dispute Packet Layers", "elements": ["letter", "comparison", "report page", "ID proof", "evidence", "tracking"], "motion": "stack-layers"},
    {"id": "mail-tracking-timeline", "title": "Mail Tracking Timeline", "elements": ["draft", "approved", "mailed", "delivered", "response due"], "motion": "progress-line"},
]

IMAGE_TEMPLATES = [
    {"id": "hero-square", "title": "Hero Square Ad", "size": "1080x1080", "headline": "Find errors. Build disputes. Track progress.", "visual": "dashboard mockup"},
    {"id": "weekly-refresh-story", "title": "Weekly Refresh Story", "size": "1080x1920", "headline": "Upload your latest reports.", "visual": "three bureau cards"},
    {"id": "three-bureau-comparison", "title": "3-Bureau Comparison Ad", "size": "1080x1350", "headline": "Your 3 reports may not match.", "visual": "comparison table"},
    {"id": "negative-account-review", "title": "Negative Account Review Ad", "size": "1200x628", "headline": "Collections and charge-offs need detail.", "visual": "negative account cards"},
]


def check_marketing_compliance(text: str = "") -> dict[str, Any]:
    lower = text.lower()
    flags = [
        {
            "type": "banned_phrase",
            "phrase": phrase,
            "severity": "high",
            "message": f"Remove or rewrite banned phrase: {phrase}",
        }
        for phrase in BANNED_MARKETING_PHRASES
        if phrase.lower() in lower
    ]
    return {
        "ok": not flags,
        "flags": flags,
        "approval_required": True,
        "auto_publish_allowed": False,
        "preferred_phrases": PREFERRED_MARKETING_PHRASES,
        "disclosure": DISCLOSURE,
    }


def generate_learning_storyboard(topic: dict[str, Any]) -> dict[str, Any]:
    scenes = [
        (1, "0:00-0:15", topic["hook"], "Animated Credit Vivo dashboard opening", "Soft zoom, bureau cards slide in", topic["hook"]),
        (2, "0:15-0:30", "Start with your reports", "Three bureau cards: Equifax, Experian, TransUnion", "Cards stack into scanner", "Credit reports can show different details across the three bureaus."),
        (3, "0:30-0:45", "Credit Vivo scans for review", "AI scan animation over report cards", "Scanner beam highlights negative accounts", "Credit Vivo helps organize possible issues for review."),
        (4, "0:45-1:00", "Compare the bureaus", "3-bureau comparison table", "Rows highlight balance, status, date", "The scanner compares balances, statuses, dates, and account details."),
        (5, "1:00-1:15", "Focus on negative accounts", "Negative account cards sort by issue type", "Cards move into categories", "Collections and charge-offs need careful field-level review."),
        (6, "1:15-1:30", "Build focused rounds", "Round 1, Round 2, Follow-up timeline", "Timeline animates left to right", "Focused dispute rounds help keep the process organized."),
        (7, "1:30-1:45", "Attach the proof", "Packet layers: letter, comparison, report pages, evidence", "Layers stack into a packet", "A strong packet includes the letter, comparison, report pages, and evidence."),
        (8, "1:45-2:00", "Customer approval", "Review and approve button", "Tap animation", "Customers review and approve before anything is mailed."),
        (9, "2:00-2:15", "Track every step", "Mail tracking timeline", "Mailed, delivered, response due", "Credit Vivo tracks delivery, deadlines, responses, and follow-ups."),
        (10, "2:15-2:30", "Refresh your scan", "Upload new report cards", "New upload compares to old scan", "Refresh your reports to see what changed."),
        (11, "2:30-2:45", "Know the next step", "Dashboard next-step card", "Next step slides into view", "The dashboard shows the next step clearly."),
        (12, "2:45-3:00", CREDIT_VIVO_BRAND_KIT["trustLine"], "Credit Vivo logo and final dashboard", "Clean brand end card", f"{CREDIT_VIVO_BRAND_KIT['trustLine']}. {CREDIT_VIVO_BRAND_KIT['slogan']}."),
    ]
    scene_dicts = [
        {"scene": scene, "time": time, "headline": headline, "visual": visual, "motion": motion, "narration": narration}
        for scene, time, headline, visual, motion, narration in scenes
    ]
    compliance = check_marketing_compliance(str(scene_dicts))
    return {
        "topic_id": topic["id"],
        "title": topic["title"],
        "duration": topic["duration"],
        "brand": CREDIT_VIVO_BRAND_KIT["brandName"],
        "scenes": scene_dicts,
        "compliance": compliance,
        "source": "Credit Vivo generated",
        "uses_stock_assets": False,
        "auto_publish_allowed": False,
    }


def generate_video_script(topic: dict[str, Any]) -> dict[str, Any]:
    storyboard = generate_learning_storyboard(topic)
    script = "\n".join(f"{scene['time']} - {scene['narration']}" for scene in storyboard["scenes"])
    return {
        "title": topic["title"],
        "duration": topic["duration"],
        "script": script,
        "captions": [scene["narration"] for scene in storyboard["scenes"]],
        "compliance": check_marketing_compliance(script),
        "approval_required": True,
        "auto_publish_allowed": False,
    }


@dataclass
class MarketAsset:
    asset_id: str
    type: str
    title: str
    campaign: str
    topic: str
    format: str
    status: str = "Needs Review"
    created_by: str = "Market AI"
    approved_by: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: list[str] = field(default_factory=list)
    compliance_flags: list[dict[str, Any]] = field(default_factory=list)
    disclosure_included: bool = True
    source: str = "Credit Vivo generated"
    version: int = 1
    file_path: str | None = None
    thumbnail_path: str | None = None
    transcript_path: str | None = None
    captions_path: str | None = None
    storyboard_path: str | None = None
    storyboard: dict[str, Any] | None = None
    approval_required: bool = True
    auto_publish_allowed: bool = False
    uses_stock_assets: bool = False


def sample_market_assets() -> list[dict[str, Any]]:
    assets = []
    for index, topic in enumerate(LEARNING_TOPICS, start=1):
        storyboard = generate_learning_storyboard(topic)
        assets.append(asdict(MarketAsset(
            asset_id=f"market-demo-{index}",
            type="storyboard",
            title=topic["title"],
            campaign="Credit Vivo Learning",
            topic=topic["category"],
            format="9:16",
            tags=["learning", re.sub(r"[^a-z0-9]+", "-", topic["category"].lower()).strip("-"), "credit-vivo"],
            compliance_flags=storyboard["compliance"]["flags"],
            storyboard=storyboard,
        )))
    return assets


def build_market_ai_dashboard() -> dict[str, Any]:
    assets = sample_market_assets()
    return {
        "ok": True,
        "service": "credit-vivo-market-ai-studio",
        "mode": "in_house_creative_studio",
        "brand": CREDIT_VIVO_BRAND_KIT,
        "assets": assets,
        "stats": {
            "assets": len(assets),
            "needs_review": sum(1 for asset in assets if asset["status"] == "Needs Review"),
            "approved": sum(1 for asset in assets if asset["status"] == "Approved"),
            "learning_topics": len(LEARNING_TOPICS),
            "stock_dependencies": 0,
        },
        "sections": [
            "Learning Videos",
            "Ad Images",
            "Animations",
            "Ad Videos",
            "Asset Library",
            "Approval Queue",
            "Compliance Review",
            "Campaign Calendar",
            "Render Queue",
            "Brand Kit",
        ],
        "approval_gate": {
            "auto_publish_allowed": False,
            "approval_required_before_public_use": True,
            "compliance_review_required": True,
        },
        "asset_policy": {
            "source": "Credit Vivo generated",
            "outside_stock_footage_dependencies": False,
            "competitor_visuals_allowed": False,
            "raw_credit_report_access_allowed": False,
        },
    }


def get_topic(topic_id: str | None) -> dict[str, Any]:
    return next((topic for topic in LEARNING_TOPICS if topic["id"] == topic_id), LEARNING_TOPICS[0])


def create_render_job(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": str(uuid.uuid4()),
        "asset_id": payload.get("asset_id", "market-demo-1"),
        "template_id": payload.get("template_id", "weekly-report-refresh-3min"),
        "status": "Queued For Review",
        "format": payload.get("format", "9:16"),
        "duration_seconds": int(payload.get("duration_seconds", 180)),
        "output_path": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "render_engine": "preview_placeholder",
        "auto_publish_allowed": False,
        "approval_required_before_export": True,
    }


def build_market_templates() -> dict[str, Any]:
    return {
        "video_templates": VIDEO_TEMPLATES,
        "animation_templates": ANIMATION_TEMPLATES,
        "image_templates": IMAGE_TEMPLATES,
        "export_profiles": {
            "verticalReel": {"label": "Vertical Reel", "width": 1080, "height": 1920, "aspect": "9:16", "fps": 30},
            "youtube": {"label": "YouTube / Website", "width": 1920, "height": 1080, "aspect": "16:9", "fps": 30},
            "square": {"label": "Square Social", "width": 1080, "height": 1080, "aspect": "1:1", "fps": 30},
            "portraitAd": {"label": "Portrait Feed Ad", "width": 1080, "height": 1350, "aspect": "4:5", "fps": 30},
            "webAd": {"label": "Web Ad", "width": 1200, "height": 628, "aspect": "1.91:1", "fps": 30},
        },
    }
