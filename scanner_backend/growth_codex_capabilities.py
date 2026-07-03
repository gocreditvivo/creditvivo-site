from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CodexLikeCapability:
    name: str
    what_it_means: str
    growth_ai_use: str
    tools_needed: List[str]
    maturity: str


CODEX_LIKE_CAPABILITIES: List[CodexLikeCapability] = [
    CodexLikeCapability(
        name="Mission planning",
        what_it_means="Break a big goal into smaller steps, priorities, and next actions.",
        growth_ai_use="Turn the $1M/month goal into weekly campaigns, funnel targets, partner tasks, and tracking goals.",
        tools_needed=["growth metrics", "campaign list", "owner priorities"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Research synthesis",
        what_it_means="Read many sources and summarize what matters.",
        growth_ai_use="Turn CFPB, BBB, forums, search trends, bureaus, and open data into campaign ideas and market insights.",
        tools_needed=["approved public sources", "search tools", "source citations"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Problem diagnosis",
        what_it_means="Find what is wrong and why it may be happening.",
        growth_ai_use="Diagnose weak traffic, low signups, scanner drop-off, low upgrades, ad waste, and churn.",
        tools_needed=["website events", "scanner events", "payment events", "support events"],
        maturity="backend_ready",
    ),
    CodexLikeCapability(
        name="Solution design",
        what_it_means="Recommend a fix that is practical and testable.",
        growth_ai_use="Suggest landing page edits, ad tests, partner scripts, pricing tests, and retention fixes.",
        tools_needed=["campaign pages", "ad library", "problem solver"],
        maturity="backend_ready",
    ),
    CodexLikeCapability(
        name="Ad and copy generation",
        what_it_means="Write customer-facing copy with a clear goal and channel fit.",
        growth_ai_use="Draft Google, Bing, Meta, TikTok, Reddit, YouTube, and partner/referral ads.",
        tools_needed=["ad channel rules", "campaign pages", "offer library"],
        maturity="backend_ready",
    ),
    CodexLikeCapability(
        name="Tool-use routing",
        what_it_means="Know which tool or system should handle each job.",
        growth_ai_use="Route questions to ad planning, source research, problem solving, Codex advisor, outreach, or founder brief.",
        tools_needed=["internal API routes", "task queue", "owner dashboard"],
        maturity="needs_dashboard_connection",
    ),
    CodexLikeCapability(
        name="Experiment execution plan",
        what_it_means="Define a test, a success metric, and a stop/scale rule.",
        growth_ai_use="Create 7-day campaign tests and decide whether to pause, improve, or scale.",
        tools_needed=["ad spend", "lead source", "scan starts", "paid upgrades"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Verification after action",
        what_it_means="Check whether the change worked before claiming success.",
        growth_ai_use="After an ad, page, or funnel change, verify conversion, scan completion, and paid upgrade impact.",
        tools_needed=["analytics", "event logs", "weekly reports"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Memory and learning loop",
        what_it_means="Remember what was tried, what worked, and what failed.",
        growth_ai_use="Build a campaign learning history so Growth AI improves every week.",
        tools_needed=["experiment log", "campaign history", "source attribution"],
        maturity="needs_persistent_database",
    ),
    CodexLikeCapability(
        name="Founder brief",
        what_it_means="Translate complex system data into plain-English owner actions.",
        growth_ai_use="Tell the founder what needs attention today, what is working, and what decision is needed.",
        tools_needed=["Vivo Command AI", "growth metrics", "operator events"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Approval-gated execution",
        what_it_means="Prepare actions but require approval for sensitive or money-spending moves.",
        growth_ai_use="Draft ads, outreach, pricing ideas, and customer messages, then wait for owner approval before launch.",
        tools_needed=["approval queue", "audit log", "owner dashboard"],
        maturity="foundation_ready",
    ),
    CodexLikeCapability(
        name="Codex advisor handoff",
        what_it_means="Package context and ask Codex for higher-level review or implementation help.",
        growth_ai_use="Send structured questions to Codex for strategy, copy, funnel, measurement, and engineering advice.",
        tools_needed=["Codex advisor bridge", "Codex SDK or manual Codex prompt"],
        maturity="bridge_ready_sdk_next",
    ),
]


def capability_to_dict(capability: CodexLikeCapability) -> Dict[str, object]:
    return capability.__dict__


def build_codex_like_growth_brief() -> Dict[str, object]:
    maturity_counts: Dict[str, int] = {}
    for capability in CODEX_LIKE_CAPABILITIES:
        maturity_counts[capability.maturity] = maturity_counts.get(capability.maturity, 0) + 1

    return {
        "ok": True,
        "service": "credit-vivo-growth-codex-like-capabilities",
        "plain_english_summary": (
            "Growth AI can be made Codex-like for growth work: it can plan, research, diagnose, write, "
            "design experiments, verify results, remember lessons, and ask Codex for advice. It needs live data, "
            "a persistent database, a dashboard, and tool connections to become more automatic."
        ),
        "capabilities": [capability_to_dict(capability) for capability in CODEX_LIKE_CAPABILITIES],
        "maturity_counts": maturity_counts,
        "next_build_steps": [
            "Connect live analytics and scanner events.",
            "Add persistent experiment memory.",
            "Add owner approval queue.",
            "Add dashboard view of Growth AI skills and status.",
            "Connect Codex SDK from a secure backend worker when ready.",
        ],
    }
