"""Helpers for applying reviewer-backed rule calibration."""

from __future__ import annotations

import json
from pathlib import Path

from a11yway.core.rules import DEFAULT_CONFIDENCE_BY_RULE, FALLBACK_CONFIDENCE
from a11yway.core.verdicts import (
    build_rule_reliability_profiles,
    review_only_rules_from_reliability_profiles,
)
from a11yway.models.issue import AccessibilityIssue


def parse_rule_list(value: str | None) -> set[str]:
    """Parse a comma-separated rule list from the CLI."""
    if not value:
        return set()
    return {name.strip() for name in value.split(",") if name.strip()}


def load_reviewed_reports(paths: list[str] | None) -> list[dict]:
    """Load reviewed A11yway report JSON files for calibration."""
    return [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in (paths or [])
    ]


def review_only_rules_from_reports(paths: list[str] | None) -> set[str]:
    """Return historically noisy rules that should be review-only."""
    if not paths:
        return set()
    profiles = build_rule_reliability_profiles(load_reviewed_reports(paths))
    return review_only_rules_from_reliability_profiles(profiles)


def downgrade_review_only_issues(
    issues: list[AccessibilityIssue],
    review_only_rules: set[str],
    *,
    reason: str = "Rule configured as review-only for this run.",
) -> None:
    """Mark matching issues as needs_review while keeping them in reports."""
    if not review_only_rules:
        return
    for issue in issues:
        if issue.issue_type not in review_only_rules:
            continue
        effective = issue.confidence or DEFAULT_CONFIDENCE_BY_RULE.get(
            issue.issue_type, FALLBACK_CONFIDENCE
        )
        if effective in {"confirmed", "likely"}:
            issue.confidence = "needs_review"
            if isinstance(issue.evidence, dict):
                issue.evidence["downgraded_to_review_only"] = True
                issue.evidence["review_only_reason"] = reason
