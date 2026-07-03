from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ProblemSkill:
    name: str
    purpose: str
    question_examples: List[str]
    output: List[str]


@dataclass(frozen=True)
class ProblemPattern:
    trigger_keywords: List[str]
    problem_type: str
    likely_cause: str
    solution: str
    data_needed: List[str]
    verification: str
    owner_decision: str


PROBLEM_SKILLS: List[ProblemSkill] = [
    ProblemSkill(
        name="question_triage",
        purpose="Classify founder/customer/team questions into a growth, funnel, ad, partner, retention, pricing, or operations problem.",
        question_examples=[
            "Why are people not joining?",
            "Which ad should we run?",
            "Why are scans not completing?",
        ],
        output=["problem_type", "urgency", "best_next_action"],
    ),
    ProblemSkill(
        name="root_cause_analysis",
        purpose="Find the likely reason a growth number is weak.",
        question_examples=[
            "Why are leads not starting the scanner?",
            "Why are customers canceling?",
            "Why is ad spend not converting?",
        ],
        output=["likely_cause", "missing_data", "recommended_fix"],
    ),
    ProblemSkill(
        name="solution_design",
        purpose="Turn the problem into one practical fix or experiment.",
        question_examples=[
            "How do we improve the Join Free page?",
            "How do we get more partner referrals?",
            "How do we increase paid upgrades?",
        ],
        output=["solution", "copy_or_workflow_change", "owner_decision"],
    ),
    ProblemSkill(
        name="experiment_planning",
        purpose="Create a test with a clear metric and time window.",
        question_examples=[
            "Test auto loan ads",
            "Try a new pricing message",
            "Compare mortgage vs collections pages",
        ],
        output=["experiment", "success_metric", "stop_or_scale_rule"],
    ),
    ProblemSkill(
        name="answer_builder",
        purpose="Answer owner questions in plain English with a direct recommendation.",
        question_examples=[
            "What should I do today?",
            "What is broken?",
            "What is the fastest way to get customers?",
        ],
        output=["plain_english_answer", "next_step", "verification"],
    ),
]


PROBLEM_PATTERNS: List[ProblemPattern] = [
    ProblemPattern(
        trigger_keywords=["traffic", "visitors", "nobody", "no one", "not enough people"],
        problem_type="traffic_problem",
        likely_cause="Credit Vivo does not have enough qualified visitors yet.",
        solution="Start with high-intent Google/Bing search campaigns and partner referral outreach before broad social ads.",
        data_needed=["visitors by source", "landing page", "join clicks", "campaign source"],
        verification="Within 7 days, compare visitors, Join Free clicks, and cost per lead by source.",
        owner_decision="Approve first campaign budget and partner outreach list.",
    ),
    ProblemPattern(
        trigger_keywords=["lead", "join", "signup", "sign up", "conversion"],
        problem_type="lead_conversion_problem",
        likely_cause="Visitors may not understand the free Credit Check-In fast enough or may not trust the next step.",
        solution="Make the call to action simpler and show no-hard-pull, plain-English findings, and attorney support when needed near the CTA.",
        data_needed=["page views", "Join Free clicks", "form starts", "form submissions", "drop-off field"],
        verification="A/B test the headline and CTA for 7 days; winner is higher visitor-to-lead rate.",
        owner_decision="Approve customer-facing copy test.",
    ),
    ProblemPattern(
        trigger_keywords=["scanner", "scan", "upload", "report", "parser", "finish", "complete"],
        problem_type="scanner_completion_problem",
        likely_cause="Customers may be confused, worried about upload privacy, or blocked by scanner errors.",
        solution="Add a simple scanner progress state, privacy reassurance, file guidance, and rescue message for failed scans.",
        data_needed=["scan_started", "scan_completed", "scan_failed", "file type", "time to complete"],
        verification="Scan completion rate should improve and failed scan tickets should drop.",
        owner_decision="Approve scanner copy and support fallback flow.",
    ),
    ProblemPattern(
        trigger_keywords=["upgrade", "paid", "pricing", "money", "revenue", "subscription"],
        problem_type="paid_upgrade_problem",
        likely_cause="Free users may not see the value of guided support after findings.",
        solution="After scan findings, show a plain-English next-step card explaining why AI Guided or Vivo Plus helps.",
        data_needed=["scan_completed", "pricing_viewed", "paid_upgrade", "finding_count", "customer goal"],
        verification="Free-scan-to-paid rate should increase within two weekly cohorts.",
        owner_decision="Approve plan positioning and offer copy.",
    ),
    ProblemPattern(
        trigger_keywords=["cancel", "retention", "churn", "refund", "leave"],
        problem_type="retention_problem",
        likely_cause="Customers may feel no progress or may not know what step is waiting.",
        solution="Trigger a progress update when a customer is stuck for 7 days or has no visible next action.",
        data_needed=["last login", "stuck step", "support ticket", "payment status", "days since last progress"],
        verification="Cancellation requests and stuck-customer count should decrease.",
        owner_decision="Approve retention message templates.",
    ),
    ProblemPattern(
        trigger_keywords=["ad", "ads", "google", "meta", "tiktok", "youtube", "reddit", "bing"],
        problem_type="ad_performance_problem",
        likely_cause="The ad may be attracting curiosity clicks instead of scanner-ready customers.",
        solution="Start with search ads tied to high-intent pages, then pause any ad with low scan-start rate.",
        data_needed=["impressions", "clicks", "cost", "leads", "scan_started", "scan_completed", "paid_upgrade"],
        verification="Keep campaigns that produce completed scans; pause campaigns with cheap clicks but poor scan starts.",
        owner_decision="Approve channel budget and stop/scale thresholds.",
    ),
    ProblemPattern(
        trigger_keywords=["partner", "referral", "dealer", "mortgage", "realtor", "housing", "counselor"],
        problem_type="partner_growth_problem",
        likely_cause="Partner pitch may not clearly show how Credit Vivo helps their customers without extra work.",
        solution="Offer a tracked free Credit Check-In referral link and a simple partner one-pager.",
        data_needed=["partner contacted", "reply", "referral clicks", "joins", "scans", "paid upgrades"],
        verification="Rank partners by completed scans, not just replies.",
        owner_decision="Approve partner pitch and referral tracking code.",
    ),
]


def skill_to_dict(skill: ProblemSkill) -> Dict[str, object]:
    return skill.__dict__


def pattern_to_dict(pattern: ProblemPattern) -> Dict[str, object]:
    return pattern.__dict__


def solve_growth_problem(question: str) -> Dict[str, object]:
    normalized = question.lower()
    matched = [
        pattern
        for pattern in PROBLEM_PATTERNS
        if any(keyword in normalized for keyword in pattern.trigger_keywords)
    ]

    selected = matched[0] if matched else ProblemPattern(
        trigger_keywords=[],
        problem_type="general_growth_question",
        likely_cause="The question needs more context before Growth AI can diagnose it.",
        solution="Start by collecting the relevant funnel metric and then ask Growth AI again with the number.",
        data_needed=["traffic source", "lead count", "scan starts", "scan completions", "paid upgrades"],
        verification="Growth AI should return a more specific diagnosis once data is available.",
        owner_decision="Decide which metric or campaign should be investigated first.",
    )

    return {
        "ok": True,
        "service": "credit-vivo-growth-problem-solver",
        "question": question,
        "problem_type": selected.problem_type,
        "likely_cause": selected.likely_cause,
        "recommended_solution": selected.solution,
        "data_needed": selected.data_needed,
        "verification": selected.verification,
        "owner_decision": selected.owner_decision,
        "matched_patterns": [pattern_to_dict(pattern) for pattern in matched],
        "plain_english_answer": (
            f"Growth AI thinks this is a {selected.problem_type}. "
            f"The likely issue is: {selected.likely_cause} "
            f"Best next move: {selected.solution}"
        ),
    }


def build_problem_solver_brief() -> Dict[str, object]:
    return {
        "ok": True,
        "service": "credit-vivo-growth-problem-solver",
        "mode": "question_diagnose_solution_verify",
        "plain_english_summary": "Growth AI can answer owner questions by classifying the problem, finding the likely cause, recommending a fix, listing needed data, and defining how to verify the result.",
        "skills": [skill_to_dict(skill) for skill in PROBLEM_SKILLS],
        "problem_patterns": [pattern_to_dict(pattern) for pattern in PROBLEM_PATTERNS],
        "example_questions": [
            "Why are leads not starting the scanner?",
            "Which ad should we run first?",
            "Why are free users not upgrading?",
            "How do we get more partner referrals?",
            "What should I do today to get customers?",
        ],
    }
