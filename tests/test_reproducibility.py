

from a11yway.core.reproducibility import apply_reproducibility
from a11yway.models.issue import AccessibilityIssue


def dynamic_issue(selector: str = "#cta") -> AccessibilityIssue:
    return AccessibilityIssue(
        title="Focused control is covered by overlaying content",
        issue_type="focus_obscured",
        severity="high",
        agent_name="Low Vision Auditor",
        evidence={"element_selector": selector, "detected_in": "low_vision"},
        suggested_fix="Keep focused controls clear of overlays.",
    )


def test_primary_only_dynamic_finding_becomes_needs_review() -> None:
    issues = apply_reproducibility([dynamic_issue()], [[], []], 3)

    assert issues[0].confidence == "needs_review"
    assert issues[0].evidence["confidence_level"] == "needs_review"
    repro = issues[0].evidence["reproducibility"]
    assert repro["successful_reproductions"] == 1
    assert repro["failed_reproductions"] == 2


def test_dynamic_finding_reproduced_in_every_run_is_repeat_verified() -> None:
    issue = dynamic_issue()
    repeat = dynamic_issue()

    issues = apply_reproducibility([issue], [[repeat], [repeat]], 3)

    assert issues[0].confidence == "repeat_verified"
    assert issues[0].evidence["verification_status"] == "repeat_verified"
    assert issues[0].evidence["reproducibility"]["reproduction_rate"] == 1.0
