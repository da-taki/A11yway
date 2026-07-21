

import json

from a11yway.core.dedup import deduplicate_issues
from a11yway.core.human_compare import compare_human_review
from a11yway.core.report_builder import build_json_report, build_markdown_report
from a11yway.core.verdicts import (
    apply_verdicts_to_report,
    build_precision_stats,
    issue_fingerprint,
)
from a11yway.models.issue import AccessibilityIssue


def _issue(
    issue_type: str = "missing_form_label",
    snippet: str = '<input type="text" name="search">',
    detected_in: str | None = None,
    confidence: str | None = None,
    extra: dict | None = None,
) -> AccessibilityIssue:
    evidence = {
        "tag": "input",
        "snippet": snippet,
        "reason": "no accessible label",
    }
    if detected_in:
        evidence["detected_in"] = detected_in
    if extra:
        evidence.update(extra)
    return AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type=issue_type,
        severity="high",
        agent_name="Test",
        evidence=evidence,
        suggested_fix="Add a label.",
        confidence=confidence,
    )


def test_validation_marks_cross_engine_findings() -> None:
    issues = deduplicate_issues(
        [
            _issue(confidence="likely"),
            _issue(detected_in="axe_core", issue_type="axe_label", confidence="needs_review"),
        ]
    )
    report = build_json_report(
        "https://Example.test/page?b=2&a=1#frag",
        issues,
        source_metadata={
            "source": "https://Example.test/page?b=2&a=1#frag",
            "source_type": "url",
            "final_url": "https://Example.test/page?b=2&a=1#frag",
            "status_code": 200,
            "content_type": "text/html",
        },
    )

    issue = report["issues"][0]
    evidence = issue["evidence"]
    assert report["summary"]["raw_occurrences"] == 2
    assert report["summary"]["unique_root_issues"] == 1
    assert evidence["confidence_level"] == "confirmed_by_multiple_engines"
    assert evidence["verification_status"] == "cross_checked"
    assert evidence["normalized_page_url"] == "https://example.test/page?a=1&b=2"
    assert evidence["rule_id"] == "missing_form_label"
    assert evidence["occurrence_count"] == 2


def test_component_level_clustering_collapses_repeated_component_findings() -> None:
    issues = deduplicate_issues(
        [
            _issue(
                issue_type="missing_link_name",
                snippet='<a href="/one"></a>',
                extra={
                    "tag": "a",
                    "href": "/one",
                    "component_signature": "primary navigation",
                    "component_signature_explicit": True,
                    "cluster_repeated_component": True,
                },
            ),
            _issue(
                issue_type="missing_link_name",
                snippet='<a href="/two"></a>',
                extra={
                    "tag": "a",
                    "href": "/two",
                    "component_signature": "primary navigation",
                    "component_signature_explicit": True,
                    "cluster_repeated_component": True,
                },
            ),
        ]
    )

    assert len(issues) == 1
    evidence = issues[0].evidence
    assert evidence["occurrence_count"] == 2
    assert len(evidence["example_elements"]) == 2

    report = build_json_report("nav.html", issues)
    assert report["summary"]["raw_occurrences"] == 2
    assert report["summary"]["unique_root_issues"] == 1
    assert report["issue_clusters"][0]["occurrence_count"] == 2
    assert "Root Issue Clusters" in build_markdown_report(report)


def test_expanded_verdict_metrics_include_unable_to_reproduce_and_raw_precision() -> None:
    report = build_json_report(
        "sample.html",
        deduplicate_issues(
            [
                _issue(snippet='<input name="a">'),
                _issue(snippet='<input name="b">'),
            ]
        ),
    )
    verdicts = {
        "reviewer": {"role": "certified accessibility specialist"},
        "verdicts": [
            {
                "issue_fingerprint": issue_fingerprint(report["issues"][0], source="sample.html"),
                "verdict": "partially_confirmed",
                "browser": "Chrome",
                "operating_system": "Windows",
                "manual_testing_method": "Axe DevTools plus keyboard review",
            },
            {
                "issue_fingerprint": issue_fingerprint(report["issues"][1], source="sample.html"),
                "verdict": "unable_to_reproduce",
            },
        ],
    }
    reviewed = apply_verdicts_to_report(report, verdicts)
    stats = reviewed["precision_stats"]

    assert reviewed["issues"][0]["review"]["browser"] == "Chrome"
    assert stats["overall"]["precision"] == 0.5
    assert stats["overall"]["unable_to_reproduce_rate"] == 0.5
    assert stats["unique_root_issue_precision"]["reviewed"] == 2
    assert stats["raw_occurrence_precision"]["reviewed"] == 2
    assert "Forms" in stats["by_category"]
    assert "high" in stats["by_severity"]


def test_precision_stats_counts_raw_occurrences() -> None:
    report = build_json_report(
        "sample.html",
        deduplicate_issues(
            [
                _issue(
                    snippet='<a href="/one"></a>',
                    issue_type="missing_link_name",
                    extra={
                        "tag": "a",
                        "component_signature": "footer",
                        "component_signature_explicit": True,
                        "cluster_repeated_component": True,
                    },
                ),
                _issue(
                    snippet='<a href="/two"></a>',
                    issue_type="missing_link_name",
                    extra={
                        "tag": "a",
                        "component_signature": "footer",
                        "component_signature_explicit": True,
                        "cluster_repeated_component": True,
                    },
                ),
            ]
        ),
    )
    verdicts = {
        "verdicts": [
            {
                "issue_fingerprint": issue_fingerprint(report["issues"][0], source="sample.html"),
                "verdict": "confirmed",
            }
        ]
    }
    reviewed = apply_verdicts_to_report(report, verdicts)
    stats = build_precision_stats([reviewed])

    assert stats["unique_root_issue_precision"]["reviewed"] == 1
    assert stats["raw_occurrence_precision"]["reviewed"] == 2


def test_human_review_comparison_matches_without_internal_rule_ids() -> None:
    report = build_json_report(
        "sample.html",
        deduplicate_issues([_issue(snippet='<input id="search" name="q">')]),
    )
    human_review = {
        "reviewer": {"role": "trained tester"},
        "findings": [
            {
                "description": "Search field has no programmatic label",
                "selector": "input#search",
                "wcag_criteria": ["3.3.2"],
                "severity": "high",
                "notes": "Confirmed in Chrome on Windows.",
            },
            {
                "description": "Footer contrast is too low",
                "selector": "footer a",
                "severity": "medium",
            },
        ],
    }
    comparison = compare_human_review(report, human_review)

    assert comparison["summary"]["true_positives"] == 1
    assert comparison["summary"]["missed_human_findings"] == 1
    assert comparison["summary"]["false_positives"] == 0


def test_precision_report_cli_outputs_json(tmp_path) -> None:
    from a11yway.main import main

    report = build_json_report("sample.html", deduplicate_issues([_issue()]))
    verdicts = {
        "verdicts": [
            {
                "issue_fingerprint": issue_fingerprint(report["issues"][0], source="sample.html"),
                "verdict": "confirmed",
            }
        ]
    }
    reviewed = apply_verdicts_to_report(report, verdicts)
    reviewed_path = tmp_path / "reviewed.json"
    out_path = tmp_path / "precision.json"
    reviewed_path.write_text(json.dumps(reviewed), encoding="utf-8")

    exit_code = main(["--precision-report", str(reviewed_path), "--json", str(out_path)])

    assert exit_code == 0
    stats = json.loads(out_path.read_text(encoding="utf-8"))
    assert stats["overall"]["precision"] == 1.0
