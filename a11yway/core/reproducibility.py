

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from a11yway.core.finding_validation import validate_findings
from a11yway.models.issue import AccessibilityIssue


DYNAMIC_REPRO_RULES = {
    "keyboard_trap",
    "browser_repeated_focus",
    "browser_focus_not_moving",
    "browser_focus_on_hidden_element",
    "unnamed_focus_stop",
    "focus_lost",
    "focus_obscured",
    "focus_indicator_missing",
    "reflow_horizontal_scroll",
    "reflow_clipped_content",
    "reflow_overlap",
    "text_spacing_content_loss",
    "low_contrast_text",
    "contrast_unresolved_background",
}


def _issue_key(issue: AccessibilityIssue) -> tuple[str, str]:
    validate_findings([issue])
    evidence = issue.evidence if isinstance(issue.evidence, dict) else {}
    return (
        issue.issue_type,
        str(
            evidence.get("deduplication_fingerprint")
            or evidence.get("fingerprint")
            or evidence.get("element_selector")
            or evidence.get("reason")
            or ""
        ),
    )


def _keys_for_run(issues: Iterable[AccessibilityIssue]) -> set[tuple[str, str]]:
    return {_issue_key(issue) for issue in issues}


def apply_reproducibility(
    primary_issues: list[AccessibilityIssue],
    repeated_issue_runs: list[list[AccessibilityIssue]],
    verify_runs: int,
) -> list[AccessibilityIssue]:






    if verify_runs <= 1:
        return primary_issues

    run_key_sets = [_keys_for_run(run) for run in repeated_issue_runs]
    for issue in primary_issues:
        if issue.issue_type not in DYNAMIC_REPRO_RULES:
            continue
        key = _issue_key(issue)
        reproduced_after_primary = sum(1 for keys in run_key_sets if key in keys)
        successful = 1 + reproduced_after_primary
        failed = max(0, verify_runs - successful)
        rate = successful / verify_runs if verify_runs else 0

        if not isinstance(issue.evidence, dict):
            issue.evidence = {"description": str(issue.evidence)}
        issue.evidence["reproducibility"] = {
            "verify_runs": verify_runs,
            "successful_reproductions": successful,
            "failed_reproductions": failed,
            "reproduction_rate": round(rate, 3),
            "rule": (
                "3/3 strong, 2/3 likely, 1/3 needs_review, "
                "0/3 suppressed or unable_to_reproduce"
            ),
        }

        if successful >= verify_runs:
            issue.confidence = "repeat_verified"
            issue.evidence["confidence_level"] = "strong"
            issue.evidence["verification_status"] = "repeat_verified"
        elif successful >= max(2, verify_runs - 1):
            issue.confidence = "likely"
            issue.evidence["confidence_level"] = "likely"
            issue.evidence["verification_status"] = "repeat_partially_verified"
        elif successful >= 1:
            issue.confidence = "needs_review"
            issue.evidence["confidence_level"] = "needs_review"
            issue.evidence["verification_status"] = "needs_manual_review"
            issue.evidence["human_review_reason"] = (
                "Finding appeared in the primary run but did not reproduce "
                "reliably across repeat verification."
            )
        else:
            issue.confidence = "informational"
            issue.evidence["confidence_level"] = "suppressed"
            issue.evidence["verification_status"] = "suppressed"
            issue.evidence["suppressed"] = True
            issue.evidence["human_review_reason"] = (
                "Finding did not reproduce across repeat verification."
            )
    return primary_issues
