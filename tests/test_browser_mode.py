"""Tests for the optional browser interaction mode.

These tests must pass whether or not Playwright is installed. The real
headless-browser integration test skips itself when the browser cannot run.
"""

import csv
import json
from pathlib import Path

import pytest

import a11yway.main as main_module
from a11yway.core import browser_runner
from a11yway.core.batch_runner import run_batch
from a11yway.core.browser_runner import (
    is_playwright_available,
    merge_browser_issues,
    run_browser_audit,
    source_to_browser_url,
)
from a11yway.core.report_builder import build_json_report, build_markdown_report
from a11yway.core.rules import get_rule
from a11yway.main import analyze_html_file, main
from a11yway.models.issue import AccessibilityIssue


BROWSER_ISSUE_TYPES = [
    "browser_no_focusable_elements",
    "browser_focus_not_moving",
    "browser_repeated_focus",
    "browser_focused_control_missing_name",
    "browser_focus_on_hidden_element",
]


def fake_browser_result(**overrides) -> dict:
    """Build a small successful browser result for report tests."""
    result = {
        "mode": "browser",
        "source": "examples/sample_form.html",
        "final_url": "file:///sample_form.html",
        "success": True,
        "error": None,
        "checks_run": ["keyboard_focus_traversal", "browser_dom_snapshot"],
        "focus_trace": [
            {
                "step": 1,
                "tag": "a",
                "id": None,
                "name": None,
                "type": None,
                "href": "/guidelines",
                "src": None,
                "text": "Download scholarship guidelines",
                "role": None,
                "accessible_name_guess": "Download scholarship guidelines",
                "is_visible": True,
            }
        ],
        "issues": [],
    }
    result.update(overrides)
    return result


def test_browser_runner_imports_without_playwright() -> None:
    """Importing the module must never require Playwright."""
    assert hasattr(browser_runner, "run_browser_audit")


def test_is_playwright_available_returns_bool() -> None:
    """Availability should be a plain boolean either way."""
    assert isinstance(is_playwright_available(), bool)


def test_source_to_browser_url_keeps_urls() -> None:
    """http/https sources should pass through unchanged."""
    assert source_to_browser_url("https://example.org/page") == "https://example.org/page"
    assert source_to_browser_url("http://example.org") == "http://example.org"


def test_source_to_browser_url_converts_local_files() -> None:
    """Local paths should become absolute file:// URLs."""
    url = source_to_browser_url("examples/sample_form.html")

    assert url.startswith("file:///")
    assert url.endswith("sample_form.html")


@pytest.mark.parametrize("issue_type", BROWSER_ISSUE_TYPES)
def test_browser_issue_rules_exist_in_registry(issue_type: str) -> None:
    """Every browser issue type should be documented in the rule registry."""
    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Keyboard Interaction"
    assert rule["default_severity"] in {"high", "medium"}
    assert rule["browser_check_limitations"]


def test_json_report_includes_analysis_modes_with_browser_data() -> None:
    """Reports built with browser data should record both analysis modes."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report(
        "examples/sample_form.html", issues, browser_result=fake_browser_result()
    )

    assert report["analysis_modes"] == ["static", "browser"]
    assert report["browser"]["success"] is True
    assert report["browser"]["focus_trace"]
    assert report["browser"]["limitations"]
    assert "keyboard_focus_traversal" in report["summary"]["checks_run"]


def test_json_report_without_browser_data_is_unchanged() -> None:
    """Static reports must not grow browser keys."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert "analysis_modes" not in report
    assert "browser" not in report


def test_markdown_report_includes_browser_trace() -> None:
    """Markdown should show the browser summary and interaction trace."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report(
        "examples/sample_form.html", issues, browser_result=fake_browser_result()
    )

    markdown = build_markdown_report(report)

    assert "## Browser Mode Summary" in markdown
    assert "## Browser Interaction Trace" in markdown
    assert "Download scholarship guidelines" in markdown
    assert "### Browser Limitations" in markdown


def test_markdown_report_truncates_long_traces() -> None:
    """Only the first 20 trace steps should be rendered."""
    trace = [
        {
            "step": step,
            "tag": "a",
            "accessible_name_guess": f"Link {step}",
            "id": None,
            "name": None,
            "href": f"/page-{step}",
            "text": f"Link {step}",
            "is_visible": True,
        }
        for step in range(1, 31)
    ]
    report = build_json_report(
        "examples/sample_form.html",
        [],
        browser_result=fake_browser_result(focus_trace=trace),
    )

    markdown = build_markdown_report(report)

    assert "Link 20" in markdown
    assert "Link 21" not in markdown
    assert "Trace truncated" in markdown


def test_cli_browser_without_playwright_exits_gracefully(monkeypatch, capsys) -> None:
    """--browser without Playwright should print setup help, not crash."""
    monkeypatch.setattr(main_module, "is_playwright_available", lambda: False)

    exit_code = main(["examples/sample_form.html", "--browser"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Browser mode requires Playwright" in captured.out
    assert "playwright install chromium" in captured.out


def test_run_browser_audit_reports_missing_playwright(monkeypatch) -> None:
    """The runner itself should degrade instead of raising."""
    monkeypatch.setattr(browser_runner, "sync_playwright", None)

    result = browser_runner.run_browser_audit("examples/sample_form.html")

    assert result["success"] is False
    assert "Playwright" in result["error"]
    assert result["issues"] == []


def test_merge_browser_issues_keeps_static_when_browser_failed() -> None:
    """A failed browser audit must not change the static issue list."""
    issues = analyze_html_file(Path("examples/sample_form.html"))

    merged = merge_browser_issues(
        issues, fake_browser_result(success=False, error="launch failed")
    )

    assert merged == issues


def test_merge_browser_issues_dedupes_dom_recheck() -> None:
    """DOM re-check findings that match static findings should not repeat."""
    static_issue = AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type="missing_form_label",
        severity="high",
        agent_name="Page Analyzer",
        evidence={"snippet": '<input type="text" name="student_name">'},
        suggested_fix="Add a label.",
    )
    duplicate_dom_issue = AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type="missing_form_label",
        severity="high",
        agent_name="Page Analyzer",
        evidence={
            "snippet": '<input type="text" name="student_name">',
            "detected_in": "browser_dom",
        },
        suggested_fix="Add a label.",
    )
    new_interaction_issue = AccessibilityIssue(
        title="Focused control has no accessible name",
        issue_type="browser_focused_control_missing_name",
        severity="high",
        agent_name="Keyboard Navigator",
        evidence={"step": 3, "detected_in": "browser_interaction"},
        suggested_fix="Add a name.",
    )

    merged = merge_browser_issues(
        [static_issue],
        fake_browser_result(issues=[duplicate_dom_issue, new_interaction_issue]),
    )

    assert len(merged) == 2
    assert merged[0] is static_issue
    assert merged[1] is new_interaction_issue


def test_sample_dynamic_form_fixture_exists() -> None:
    """The dynamic sample page and browser batch config should be present."""
    assert Path("examples/sample_dynamic_form.html").exists()
    assert Path("examples/sample_browser_batch.json").exists()


def test_static_batch_csv_includes_browser_columns(tmp_path: Path) -> None:
    """Browser columns should exist in the CSV even for static-only runs."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert "browser_status" in rows[0]
    assert "browser_issue_count" in rows[0]
    assert rows[0]["browser_status"] == ""


def test_static_batch_index_includes_browser_fields(tmp_path: Path) -> None:
    """Index items should carry analysis modes and browser fields."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))

    assert index["summary"]["analysis_modes"] == ["static"]
    for item in index["sources"]:
        assert item["analysis_modes"] == ["static"]
        assert item["browser_status"] == ""
        assert item["browser_issue_count"] == 0


def test_cli_rule_details_for_browser_rule(capsys) -> None:
    """--rule should document browser issue types too."""
    exit_code = main(["--rule", "browser_focus_not_moving"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Keyboard Interaction" in captured.out
    assert "Browser check limitations:" in captured.out


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_finds_dynamic_issues() -> None:
    """Integration: browser mode should catch JS-added unlabeled controls."""
    result = run_browser_audit("examples/sample_dynamic_form.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    issue_types = {issue.issue_type for issue in result["issues"]}
    detected_in = {
        issue.evidence.get("detected_in")
        for issue in result["issues"]
        if isinstance(issue.evidence, dict)
    }

    assert result["focus_trace"], "Tab traversal should visit page controls"
    assert "missing_form_label" in issue_types  # JS-added unlabeled input
    assert "missing_button_name" in issue_types  # JS-added unnamed button
    assert "browser_dom" in detected_in
    # The static source of the dynamic page has none of these issues.
    static_issues = analyze_html_file(Path("examples/sample_dynamic_form.html"))
    static_types = {issue.issue_type for issue in static_issues}
    assert "missing_form_label" not in static_types
