from __future__ import annotations

import pytest

from a11yway.core.extended_results import extended_issue


@pytest.mark.parametrize(
    ("severity", "expected"),
    [
        ("high", "high"),
        ("medium", "medium"),
        ("low", "low"),
        ("HIGH", "high"),
        ("Medium", "medium"),
        ("LOW", "low"),
        ("critical", "low"),
        ("", "low"),
        ("  high  ", "high"),
        ("warning", "low"),
        ("info", "low"),
        ("blocker", "low"),
    ],
)
def test_extended_issue_severity_normalization_matrix(severity: str, expected: str) -> None:
    issue = extended_issue(
        module="matrix",
        check_id="severity",
        title="Title",
        issue_type="matrix_issue",
        severity=severity,
        source="fixture",
    )

    assert issue.severity == expected


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [
        ("confirmed", "strong"),
        ("likely", "likely"),
        ("needs_review", "needs_review"),
        ("informational", "informational"),
        ("CONFIRMED", "strong"),
        ("Likely", "likely"),
        ("NEEDS_REVIEW", "needs_review"),
        ("INFORMATIONAL", "informational"),
        ("probable", "needs_review"),
        ("", "needs_review"),
        ("review", "needs_review"),
        ("manual", "needs_review"),
    ],
)
def test_extended_issue_confidence_normalization_matrix(confidence: str, expected: str) -> None:
    issue = extended_issue(
        module="matrix",
        check_id="confidence",
        title="Title",
        issue_type="matrix_issue",
        severity="medium",
        source="fixture",
        confidence=confidence,
    )

    assert issue.confidence == expected
    assert issue.evidence["review_status"] == expected
