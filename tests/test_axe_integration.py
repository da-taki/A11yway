






from pathlib import Path

import pytest

import a11yway.main as main_module
from a11yway.core import axe_runner
from a11yway.core.axe_runner import (
    AXE_CHECK_NAME,
    axe_impact_to_severity,
    axe_violations_to_issues,
    is_axe_available,
    run_axe_scan,
    summarize_axe_violations,
)
from a11yway.core.browser_runner import (
    is_playwright_available,
    merge_browser_issues,
    run_browser_audit,
)
from a11yway.core.dedup import deduplicate_issues
from a11yway.core.report_builder import build_json_report, build_markdown_report
from a11yway.main import main
from a11yway.models.issue import AccessibilityIssue


def fake_violation(**overrides) -> dict:

    violation = {
        "id": "label",
        "impact": "critical",
        "help": "Form elements must have labels",
        "helpUrl": "https://dequeuniversity.com/rules/axe/4.4/label",
        "description": "Ensures every form element has a label",
        "nodes": [
            {
                "html": '<input type="text" name="student_name">',
                "target": ["#student-form > input"],
                "failureSummary": "Fix any of the following:\n  Element has no label",
            }
        ],
    }
    violation.update(overrides)
    return violation


def test_axe_runner_imports_without_axe_package() -> None:

    assert hasattr(axe_runner, "run_axe_scan")
    assert isinstance(is_axe_available(), bool)


def test_axe_impact_maps_to_project_severities() -> None:

    assert axe_impact_to_severity("critical") == "high"
    assert axe_impact_to_severity("serious") == "high"
    assert axe_impact_to_severity("moderate") == "medium"
    assert axe_impact_to_severity("minor") == "low"
    assert axe_impact_to_severity(None) == "medium"
    assert axe_impact_to_severity("something-new") == "medium"


def test_violations_become_issues_with_reviewable_evidence() -> None:

    issues = axe_violations_to_issues([fake_violation()])

    assert len(issues) == 1
    issue = issues[0]
    assert isinstance(issue, AccessibilityIssue)
    assert issue.issue_type == "axe_label"
    assert issue.severity == "high"
    assert issue.agent_name == "Axe Core Scanner"
    assert issue.evidence["detected_in"] == "axe_core"
    assert issue.evidence["snippet"] == '<input type="text" name="student_name">'
    assert issue.evidence["target"] == "#student-form > input"
    assert "label" in issue.evidence["reason"].lower()
    assert "dequeuniversity.com" in issue.suggested_fix


def test_positive_tabindex_is_review_only_axe_evidence() -> None:

    issues = axe_violations_to_issues(
        [
            fake_violation(
                id="tabindex",
                impact="serious",
                help="Elements should not have tabindex greater than zero",
                nodes=[
                    {
                        "html": '<a href="#main" tabindex="1">Skip</a>',
                        "target": ["a[href='#main']"],
                        "failureSummary": "Element has a positive tabindex",
                    }
                ],
            )
        ]
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "axe_tabindex"
    assert issues[0].severity == "medium"
    assert issues[0].confidence == "needs_review"
    assert issues[0].evidence["review_only_reason"]


def test_violation_nodes_are_capped_per_rule() -> None:

    nodes = [
        {"html": f"<input id='f{i}'>", "target": [f"#f{i}"], "failureSummary": "x"}
        for i in range(25)
    ]
    issues = axe_violations_to_issues([fake_violation(nodes=nodes)])

    assert len(issues) == axe_runner.MAX_NODES_PER_VIOLATION
    assert issues[0].evidence["nodes_total"] == 25


def test_violation_summary_is_json_safe() -> None:

    summary = summarize_axe_violations([fake_violation()])

    assert summary == [
        {
            "rule": "label",
            "impact": "critical",
            "severity": "high",
            "help": "Form elements must have labels",
            "help_url": "https://dequeuniversity.com/rules/axe/4.4/label",
            "node_count": 1,
        }
    ]


def test_run_axe_scan_reports_missing_dependency(monkeypatch) -> None:

    monkeypatch.setattr(axe_runner, "Axe", None)

    result = run_axe_scan(page=None)

    assert result["success"] is False
    assert "axe-playwright-python" in result["error"]
    assert result["issues"] == []


def test_final_dedup_merges_equivalent_axe_findings() -> None:

    static_issue = AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type="missing_form_label",
        severity="high",
        agent_name="Page Analyzer",
        evidence={"snippet": '<input type="text" name="student_name">'},
        suggested_fix="Add a label.",
    )
    axe_issue = axe_violations_to_issues([fake_violation()])[0]
    browser_result = {
        "success": True,
        "issues": [axe_issue],
    }

    merged = merge_browser_issues([static_issue], browser_result)

    assert len(merged) == 2
    assert merged[1] is axe_issue

    deduped = deduplicate_issues(merged)

    assert len(deduped) == 1
    assert deduped[0] is static_issue
    assert deduped[0].evidence["evidence_sources"] == ["static", "axe_core"]
    assert deduped[0].evidence["merged_finding_count"] == 2


def test_cli_axe_without_browser_exits_with_guidance(capsys) -> None:

    exit_code = main(["examples/sample_form.html", "--axe"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "requires browser mode" in captured.out
    assert "--browser" in captured.out


def test_cli_axe_without_package_prints_setup_help(monkeypatch, capsys) -> None:

    monkeypatch.setattr(main_module, "is_playwright_available", lambda: True)
    monkeypatch.setattr(main_module, "is_axe_available", lambda: False)

    exit_code = main(["examples/sample_form.html", "--browser", "--axe"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "axe-playwright-python" in captured.out
    assert "requirements-browser.txt" in captured.out


def test_browser_audit_without_playwright_keeps_axe_field(monkeypatch) -> None:

    from a11yway.core import browser_runner

    monkeypatch.setattr(browser_runner, "sync_playwright", None)

    result = run_browser_audit("examples/sample_form.html", include_axe=True)

    assert result["success"] is False
    assert result["axe"] is None


def test_reports_include_axe_section() -> None:

    browser_result = {
        "success": True,
        "error": None,
        "final_url": "file:///sample_form.html",
        "checks_run": ["keyboard_focus_traversal", "browser_dom_snapshot", AXE_CHECK_NAME],
        "focus_trace": [],
        "issues": [],
        "axe": {
            "success": True,
            "error": None,
            "axe_version": "4.4.3",
            "violation_rule_count": 1,
            "issue_count": 1,
            "violations": summarize_axe_violations([fake_violation()]),
        },
    }
    report = build_json_report(
        "examples/sample_form.html", [], browser_result=browser_result
    )

    assert report["browser"]["axe"]["violation_rule_count"] == 1
    assert AXE_CHECK_NAME in report["summary"]["checks_run"]

    markdown = build_markdown_report(report)
    assert "### Axe-core Scan" in markdown
    assert "Form elements must have labels" in markdown


def test_report_without_axe_scan_has_no_axe_key() -> None:

    browser_result = {
        "success": True,
        "error": None,
        "final_url": "file:///sample_form.html",
        "checks_run": ["keyboard_focus_traversal", "browser_dom_snapshot"],
        "focus_trace": [],
        "issues": [],
        "axe": None,
    }
    report = build_json_report(
        "examples/sample_form.html", [], browser_result=browser_result
    )

    assert "axe" not in report["browser"]


@pytest.mark.skipif(
    not is_playwright_available() or not is_axe_available(),
    reason="Playwright or axe-playwright-python is not installed",
)
def test_axe_scan_finds_violations_on_sample_form() -> None:

    result = run_browser_audit("examples/sample_form.html", include_axe=True)

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    axe = result["axe"]
    assert axe["success"] is True
    assert axe["violation_rule_count"] > 0
    assert AXE_CHECK_NAME in result["checks_run"]

    axe_issues = [
        issue
        for issue in result["issues"]
        if isinstance(issue.evidence, dict)
        and issue.evidence.get("detected_in") == "axe_core"
    ]
    assert axe_issues
    assert all(issue.issue_type.startswith("axe_") for issue in axe_issues)

    assert any(issue.issue_type == "axe_label" for issue in axe_issues)
