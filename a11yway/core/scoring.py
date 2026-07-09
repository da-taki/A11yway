"""Cautious scoring helpers for A11yway reports.

The score is an issue-burden indicator for public-interest review. It is not a
WCAG conformance score and must not be presented as legal or compliance advice.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


SEVERITY_WEIGHTS = {
    "critical": 20,
    "high": 10,
    "medium": 4,
    "low": 1,
}

CLASSIFICATION_LOOKS_CLEAR = "Looks mostly clear"
CLASSIFICATION_MINOR = "Minor review points"
CLASSIFICATION_NEEDS_REVIEW = "Needs review"
CLASSIFICATION_SERIOUS = "Serious review recommended"
CLASSIFICATION_BLOCKED = "Workflow may be blocked"

RISK_FAMILY_RULES = [
    (
        "keyboard/focus",
        [
            "browser_",
            "focus_",
            "task_control_not_keyboard_reachable",
            "task_step_blocked",
        ],
    ),
    ("low vision/contrast", ["low_contrast", "focus_indicator"]),
    ("reflow/zoom", ["zoom_", "overflow", "fixed_width"]),
    ("accessible names/labels", ["missing_form_label", "missing_button_name", "missing_link_name"]),
    ("headings/structure", ["heading", "missing_h1", "multiple_h1"]),
    ("alt text/media", ["missing_image_alt", "video", "audio", "captions", "transcript"]),
    ("forms/errors", ["form", "error"]),
    ("generic links", ["generic_link_text"]),
    ("AI-assisted observations", ["ai_scout", "ai_"]),
    ("performance/basic page quality", ["page_title", "html_lang", "meta_description", "viewport"]),
]


def severity_counts_from_issues(issues: list[dict[str, Any]]) -> dict[str, int]:
    """Return normalized severity counts for report issues."""
    counts = Counter(str(issue.get("severity", "low")).lower() for issue in issues)
    return {
        "critical": counts.get("critical", 0),
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
    }


def weighted_score_from_counts(severity_counts: dict[str, int]) -> int:
    """Return the weighted issue-burden score."""
    return sum(
        int(severity_counts.get(severity, 0)) * weight
        for severity, weight in SEVERITY_WEIGHTS.items()
    )


def has_blocked_task(report: dict[str, Any]) -> bool:
    """Return whether deterministic task data suggests a blocked workflow."""
    execution = report.get("task_execution") or {}
    if execution.get("success") and execution.get("completed") is False:
        return True
    sources = report.get("sources", [])
    return any(item.get("task_execution_status") == "blocked" for item in sources)


def classify_issue_burden(
    weighted_score: int,
    severity_counts: dict[str, int],
    task_blocked: bool = False,
) -> str:
    """Classify the review result with cautious, non-compliance language."""
    if task_blocked or severity_counts.get("critical", 0) > 0:
        return CLASSIFICATION_BLOCKED
    if weighted_score >= 80:
        return CLASSIFICATION_SERIOUS
    if weighted_score >= 35:
        return CLASSIFICATION_NEEDS_REVIEW
    if weighted_score >= 10:
        return CLASSIFICATION_MINOR
    return CLASSIFICATION_LOOKS_CLEAR


def _issue_family(issue_type: str) -> str:
    lowered = issue_type.lower()
    for family, needles in RISK_FAMILY_RULES:
        if any(needle in lowered for needle in needles):
            return family
    return "web quality review"


def top_risk_areas(issues: list[dict[str, Any]], limit: int = 4) -> list[str]:
    """Return the highest-weighted risk family labels."""
    family_scores: dict[str, int] = {}
    for issue in issues:
        family = _issue_family(str(issue.get("issue_type", "")))
        severity = str(issue.get("severity", "low")).lower()
        family_scores[family] = family_scores.get(family, 0) + SEVERITY_WEIGHTS.get(severity, 1)
    ranked = sorted(family_scores.items(), key=lambda item: (-item[1], item[0]))
    return [family for family, _score in ranked[:limit]]


def plain_language_summary(classification: str, risk_areas: list[str], total_issues: int) -> str:
    """Build a short public-facing summary without compliance claims."""
    if total_issues == 0:
        return "This page did not show review points in the current deterministic checks."
    if risk_areas:
        areas = ", ".join(risk_areas[:3])
        return (
            f"This page has {total_issues} review point(s). The main themes are "
            f"{areas}. Classification: {classification}."
        )
    return f"This page has {total_issues} review point(s). Classification: {classification}."


def score_report(report: dict[str, Any]) -> dict[str, Any]:
    """Score a single-page or batch report using existing issue summaries."""
    issues = report.get("issues")
    if issues is None:
        issues = []
        for source in report.get("sources", []):
            for issue in source.get("high_severity_issues", []):
                issues.append(
                    {
                        "issue_type": issue.get("issue_type", ""),
                        "severity": "high",
                        "message": issue.get("message", ""),
                    }
                )

    severity_counts = severity_counts_from_issues(list(issues))
    weighted_score = weighted_score_from_counts(severity_counts)
    classification = classify_issue_burden(
        weighted_score,
        severity_counts,
        task_blocked=has_blocked_task(report),
    )
    risk_areas = top_risk_areas(list(issues))
    total_issues = sum(severity_counts.values())
    return {
        "total_issues": total_issues,
        "severity_counts": severity_counts,
        "weighted_score": weighted_score,
        "classification": classification,
        "top_risk_areas": risk_areas,
        "plain_language_summary": plain_language_summary(
            classification,
            risk_areas,
            total_issues,
        ),
    }
