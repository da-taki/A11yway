

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

    if not value:
        return set()
    return {name.strip() for name in value.split(",") if name.strip()}


def load_reviewed_reports(paths: list[str] | None) -> list[dict]:

    return [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in (paths or [])
    ]


def review_only_rules_from_reports(paths: list[str] | None) -> set[str]:

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

    if not review_only_rules:
        return
    for issue in issues:
        if issue.issue_type not in review_only_rules:
            continue
        effective = issue.confidence or DEFAULT_CONFIDENCE_BY_RULE.get(
            issue.issue_type, FALLBACK_CONFIDENCE
        )
        if effective in {"strong", "repeat_verified", "confirmed_by_multiple_engines", "likely"}:
            issue.confidence = "needs_review"
            if isinstance(issue.evidence, dict):
                issue.evidence["downgraded_to_review_only"] = True
                issue.evidence["review_only_reason"] = reason
