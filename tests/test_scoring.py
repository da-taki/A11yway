"""Tests for cautious A11yway scoring."""

from a11yway.core.scoring import score_report


def test_scoring_classifies_weighted_issue_burden() -> None:
    report = {
        "issues": [
            {"issue_type": "missing_form_label", "severity": "high"},
            {"issue_type": "generic_link_text", "severity": "medium"},
            {"issue_type": "missing_viewport_meta", "severity": "low"},
        ]
    }

    score = score_report(report)

    assert score["total_issues"] == 3
    assert score["severity_counts"] == {
        "critical": 0,
        "high": 1,
        "medium": 1,
        "low": 1,
    }
    assert score["weighted_score"] == 15
    assert score["classification"] == "Minor review points"
    assert "accessible names/labels" in score["top_risk_areas"]


def test_scoring_marks_blocked_workflow_cautiously() -> None:
    report = {
        "issues": [{"issue_type": "task_step_blocked", "severity": "high"}],
        "task_execution": {"success": True, "completed": False},
    }

    score = score_report(report)

    assert score["classification"] == "Workflow may be blocked"
