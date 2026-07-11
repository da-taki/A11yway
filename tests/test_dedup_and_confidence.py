"""Tests for finding deduplication, confidence, downgrades, and precision."""

import json
from pathlib import Path

from a11yway.core.dedup import deduplicate_issues, finding_fingerprint
from a11yway.core.report_builder import build_json_report, build_markdown_report
from a11yway.core.verdicts import (
    apply_verdicts_to_report,
    build_precision_stats,
    issue_fingerprint,
)
from a11yway.main import main
from a11yway.models.issue import AccessibilityIssue


def make_issue(
    issue_type: str = "missing_form_label",
    detected_in: str | None = None,
    snippet: str = '<input type="text" name="student_name">',
    confidence: str | None = None,
) -> AccessibilityIssue:
    evidence = {"tag": "input", "snippet": snippet, "reason": "no label"}
    if detected_in:
        evidence["detected_in"] = detected_in
    return AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type=issue_type,
        severity="high",
        agent_name="Test",
        evidence=evidence,
        suggested_fix="",
        confidence=confidence,
    )


def test_same_finding_from_two_sources_merges() -> None:
    merged = deduplicate_issues([make_issue(), make_issue(detected_in="browser_dom")])

    assert len(merged) == 1
    assert merged[0].evidence["evidence_sources"] == ["static", "browser_dom"]
    assert merged[0].evidence["merged_finding_count"] == 2
    assert merged[0].evidence["fingerprint"]


def test_fingerprint_survives_attribute_reordering() -> None:
    """Static source order and browser DOM serialization must match."""
    first = make_issue(snippet='<input type="text" name="student_name">')
    second = make_issue(snippet='<input name="student_name" type="text" />')

    assert finding_fingerprint(first) == finding_fingerprint(second)


def test_different_elements_do_not_merge() -> None:
    merged = deduplicate_issues(
        [
            make_issue(snippet='<input name="a">'),
            make_issue(snippet='<input name="b">'),
        ]
    )
    assert len(merged) == 2


def test_different_rules_do_not_merge() -> None:
    merged = deduplicate_issues(
        [make_issue("missing_form_label"), make_issue("missing_autocomplete")]
    )
    assert len(merged) == 2


def test_equivalent_axe_rule_merges_with_native_rule() -> None:
    axe_issue = make_issue(
        issue_type="axe_label",
        detected_in="axe_core",
        snippet='<input name="student_name" type="text">',
        confidence="needs_review",
    )
    native_issue = make_issue(
        issue_type="missing_form_label",
        snippet='<input type="text" name="student_name">',
        confidence="likely",
    )

    merged = deduplicate_issues([native_issue, axe_issue])

    assert len(merged) == 1
    assert merged[0].issue_type == "missing_form_label"
    assert merged[0].confidence == "likely"
    assert merged[0].evidence["evidence_sources"] == ["static", "axe_core"]
    assert merged[0].evidence["merged_finding_count"] == 2


def test_equivalent_axe_rule_keeps_distinct_elements_separate() -> None:
    merged = deduplicate_issues(
        [
            make_issue(
                issue_type="missing_form_label",
                snippet='<input type="text" name="first_name">',
            ),
            make_issue(
                issue_type="axe_label",
                detected_in="axe_core",
                snippet='<input type="text" name="last_name">',
            ),
        ]
    )

    assert len(merged) == 2


def test_merge_upgrades_to_strongest_confidence() -> None:
    merged = deduplicate_issues(
        [
            make_issue(confidence="needs_review"),
            make_issue(detected_in="browser_interaction", confidence="confirmed"),
        ]
    )
    assert len(merged) == 1
    assert merged[0].confidence == "confirmed"


def test_dedup_keeps_first_occurrence_order() -> None:
    issues = [
        make_issue(snippet='<input name="a">'),
        make_issue(snippet='<input name="b">'),
        make_issue(snippet='<input name="a">', detected_in="browser_dom"),
    ]
    merged = deduplicate_issues(issues)
    assert [issue.evidence["snippet"] for issue in merged] == [
        '<input name="a">',
        '<input name="b">',
    ]


def test_report_shows_confidence_counts_and_sources() -> None:
    issues = deduplicate_issues([make_issue(), make_issue(detected_in="browser_dom")])
    report = build_json_report("x.html", issues)

    assert report["summary"]["counts_by_confidence"] == {"likely": 1}
    issue = report["issues"][0]
    assert issue["confidence"] == "likely"
    assert issue["evidence"]["evidence_sources"] == ["static", "browser_dom"]

    markdown = build_markdown_report(report)
    assert "Confidence: likely" in markdown
    assert "WCAG 2.2 Coverage Snapshot" in markdown
    assert "not" in markdown and "conformance" in markdown.lower()
    assert "WCAG compliant" not in markdown


def test_review_only_rules_downgrade_confidence(tmp_path, capsys) -> None:
    page = tmp_path / "page.html"
    page.write_text(
        '<html lang="en"><head><title>T</title></head><body><h1>T</h1>'
        '<form><input type="text" name="q1"></form></body></html>',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"
    exit_code = main(
        [str(page), "--review-only-rules", "missing_form_label", "--json", str(out)]
    )
    assert exit_code == 0

    report = json.loads(out.read_text(encoding="utf-8"))
    flagged = [
        issue
        for issue in report["issues"]
        if issue["issue_type"] == "missing_form_label"
    ]
    assert flagged, "the rule must still run and report"
    assert all(issue["confidence"] == "needs_review" for issue in flagged)
    assert all(
        issue["evidence"].get("downgraded_to_review_only") for issue in flagged
    )
    assert report["summary"]["review_only_rules"] == ["missing_form_label"]


def _reviewed_report() -> dict:
    issues = [
        make_issue(snippet='<input name="a">'),
        make_issue(snippet='<input name="b">'),
        make_issue("missing_autocomplete", snippet='<input name="c">'),
    ]
    report = build_json_report("examples/sample.html", issues)
    verdicts = {
        "reviewer": {"role": "tester"},
        "verdicts": [
            {
                "issue_fingerprint": issue_fingerprint(
                    report["issues"][0], source="sample.html"
                ),
                "verdict": "confirmed",
            },
            {
                "issue_fingerprint": issue_fingerprint(
                    report["issues"][1], source="sample.html"
                ),
                "verdict": "false_positive",
            },
            {
                "issue_fingerprint": issue_fingerprint(
                    report["issues"][2], source="sample.html"
                ),
                "verdict": "needs_review",
            },
        ],
        "missed_issues": [{"description": "missed contrast problem"}],
    }
    return apply_verdicts_to_report(report, verdicts)


def test_precision_stats_per_rule_and_mode() -> None:
    reviewed = _reviewed_report()
    stats = reviewed["precision_stats"]

    label_bucket = stats["by_rule"]["missing_form_label"]
    assert label_bucket["confirmed"] == 1
    assert label_bucket["false_positive"] == 1
    assert label_bucket["precision"] == 0.5

    auto_bucket = stats["by_rule"]["missing_autocomplete"]
    assert auto_bucket["needs_review"] == 1
    assert auto_bucket["precision"] is None  # undecided reviews only

    assert stats["overall"]["reviewed"] == 3
    assert stats["overall"]["precision"] == 0.5
    assert stats["missed_issue_count"] == 1
    assert stats["by_detection_mode"]["static"]["reviewed"] == 3


def test_precision_stats_per_wcag_sc() -> None:
    reviewed = _reviewed_report()
    by_sc = reviewed["precision_stats"]["by_wcag_sc"]

    # missing_form_label maps to 3.3.2 among others; both reviewed findings count.
    assert by_sc["3.3.2"]["reviewed"] == 2
    assert by_sc["1.3.5"]["needs_review"] == 1


def test_precision_stats_empty_without_reviews() -> None:
    report = build_json_report("x.html", [make_issue()])
    stats = build_precision_stats([report])

    assert stats["overall"]["reviewed"] == 0
    assert stats["overall"]["precision"] is None
    assert stats["by_rule"] == {}
