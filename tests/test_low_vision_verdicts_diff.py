"""Tests for low-vision checks, reviewer verdicts, and re-audit diffs."""

from pathlib import Path
import csv
import json

import pytest

from a11yway.core.batch_runner import run_batch
from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.low_vision_audit import (
    calculate_contrast_ratio,
    run_low_vision_audit_for_source,
)
from a11yway.core.report_builder import build_html_report, build_json_report, build_markdown_report
from a11yway.core.report_diff import compare_reports, build_diff_markdown, save_diff_json, save_diff_markdown
from a11yway.core.rules import get_rule
from a11yway.core.verdicts import (
    apply_verdicts_to_report,
    build_verdict_summary_markdown,
    issue_fingerprint,
    summarize_verdicts,
)
from a11yway.main import main
from a11yway.models.issue import AccessibilityIssue


def sample_issue(issue_type: str = "missing_form_label") -> dict:
    """Return a report-style issue dict."""
    return {
        "issue_type": issue_type,
        "severity": "high",
        "message": "Form control is missing an accessible label",
        "evidence": {
            "snippet": '<input name="student_name">',
            "tag": "input",
            "name": "student_name",
        },
    }


def test_contrast_ratio_black_white_is_about_21() -> None:
    """Black on white should have the maximum common contrast ratio."""
    assert calculate_contrast_ratio("rgb(0, 0, 0)", "rgb(255, 255, 255)") == 21


def test_contrast_ratio_low_contrast_is_below_threshold() -> None:
    """Similar grays should be below the normal text review threshold."""
    ratio = calculate_contrast_ratio("rgb(180, 180, 180)", "rgb(255, 255, 255)")
    assert ratio is not None
    assert ratio < 4.5


@pytest.mark.parametrize(
    "issue_type",
    [
        "low_contrast_text",
        "zoom_horizontal_overflow",
        "zoom_fixed_width_content",
        "focus_indicator_missing",
    ],
)
def test_low_vision_rules_exist(issue_type: str) -> None:
    """Low-vision issue types should be documented in the rule registry."""
    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Low Vision"
    assert rule["browser_check_limitations"]


def test_json_report_can_include_low_vision_block() -> None:
    """JSON reports should carry low-vision metadata when provided."""
    report = build_json_report(
        "examples/sample_low_vision_page.html",
        [],
        low_vision_result={
            "success": True,
            "checks_run": ["rendered_color_contrast"],
            "contrast_samples": [{"text": "Sample"}],
            "zoom_reflow": {"overflow_amount": 12},
            "focus_visibility": {"checked_count": 2, "flagged_count": 1},
            "limitations": ["Heuristic."],
        },
    )

    assert report["low_vision"]["success"] is True
    assert report["low_vision"]["contrast_sample_count"] == 1
    assert "low_vision" in report["analysis_modes"]


def test_markdown_and_html_include_low_vision_section() -> None:
    """Rendered reports should include low-vision summaries."""
    report = build_json_report(
        "examples/sample_low_vision_page.html",
        [],
        low_vision_result={
            "success": True,
            "checks_run": ["rendered_color_contrast"],
            "contrast_samples": [],
            "zoom_reflow": {},
            "focus_visibility": {},
            "limitations": [],
        },
    )

    assert "## Low-Vision Checks" in build_markdown_report(report)
    assert "<h2>Low-Vision Checks</h2>" in build_html_report(report)


def test_cli_low_vision_requires_browser(capsys) -> None:
    """--low-vision without --browser should fail clearly."""
    exit_code = main(["examples/sample_low_vision_page.html", "--low-vision"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Low-vision checks require browser mode" in captured.out


def test_batch_csv_and_index_include_low_vision_columns(tmp_path: Path) -> None:
    """Batch output should include low-vision columns even in static-only runs."""
    out_dir = tmp_path / "batch"

    result = run_batch("examples/sample_batch.json", out_dir)

    assert result["index"]["sources"][0]["low_vision_status"] == ""
    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        row = next(csv.DictReader(file))
    assert "low_vision_status" in row
    assert "low_vision_issue_count" in row


@pytest.mark.skipif(not is_playwright_available(), reason="Playwright is not installed")
def test_sample_low_vision_page_reports_expected_issue_types() -> None:
    """Integration: the sample page should trigger low-vision issues."""
    result = run_low_vision_audit_for_source("examples/sample_low_vision_page.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    issue_types = {issue.issue_type for issue in result["issues"]}
    assert "low_contrast_text" in issue_types
    assert {"zoom_horizontal_overflow", "zoom_fixed_width_content", "focus_indicator_missing"} & issue_types


def test_issue_fingerprint_is_stable() -> None:
    """Fingerprints should be stable for the same issue content."""
    issue = sample_issue()

    assert issue_fingerprint(issue, source="sample.html") == issue_fingerprint(issue, source="sample.html")


def test_apply_verdicts_to_report_attaches_review_data() -> None:
    """Applying verdicts should attach review metadata to matching issues."""
    report = {"source_file": "sample.html", "issues": [sample_issue()]}
    fingerprint = issue_fingerprint(report["issues"][0], source="sample.html")
    verdicts = {
        "verdicts": [
            {
                "issue_fingerprint": fingerprint,
                "verdict": "confirmed",
                "severity_feedback": "accurate",
                "notes": "Real issue.",
            }
        ],
        "missed_issues": [],
    }

    reviewed = apply_verdicts_to_report(report, verdicts)

    assert reviewed["issues"][0]["review"]["verdict"] == "confirmed"
    assert reviewed["review_summary"]["confirmed"] == 1


def test_summarize_verdicts_counts_outcomes() -> None:
    """Verdict summaries should count outcomes and missed issues."""
    summary = summarize_verdicts(
        {
            "verdicts": [
                {"verdict": "confirmed"},
                {"verdict": "false_positive"},
            ],
            "missed_issues": [{"issue_type": "unclear_error_message"}],
        }
    )

    assert summary["counts"]["confirmed"] == 1
    assert summary["counts"]["false_positive"] == 1
    assert summary["counts"]["missed_issue"] == 1
    assert "missed_issue" in build_verdict_summary_markdown(summary)


def test_compare_reports_detects_fixed_remaining_and_new() -> None:
    """Report diffs should categorize issue changes."""
    old_report = {
        "source_file": "sample.html",
        "issues": [sample_issue("missing_form_label"), sample_issue("missing_button_name")],
    }
    new_report = {
        "source_file": "sample.html",
        "issues": [sample_issue("missing_form_label"), sample_issue("low_contrast_text")],
    }

    diff = compare_reports(old_report, new_report)

    assert diff["summary"]["fixed_count"] == 1
    assert diff["summary"]["remaining_count"] == 1
    assert diff["summary"]["new_count"] == 1


def test_compare_reports_detects_task_execution_status_change() -> None:
    """Report diffs should capture blocked-to-completed task changes."""
    old_report = {
        "issues": [],
        "task_execution": {
            "success": True,
            "completed": False,
            "blocked_at_step": "submit_form",
            "steps_passed": 9,
            "steps_total": 11,
        },
    }
    new_report = {
        "issues": [],
        "task_execution": {
            "success": True,
            "completed": True,
            "blocked_at_step": None,
            "steps_passed": 11,
            "steps_total": 11,
        },
    }

    diff = compare_reports(old_report, new_report)

    assert diff["task_execution_changed"] is True
    assert diff["task_execution"]["old"]["status"] == "blocked"
    assert diff["task_execution"]["new"]["status"] == "completed"


def test_diff_markdown_and_writers(tmp_path: Path) -> None:
    """Diff helpers should render and write JSON/Markdown outputs."""
    diff = compare_reports({"issues": [sample_issue()]}, {"issues": []})
    json_path = tmp_path / "diff.json"
    markdown_path = tmp_path / "diff.md"

    save_diff_json(diff, json_path)
    save_diff_markdown(diff, markdown_path)

    assert json.loads(json_path.read_text(encoding="utf-8"))["summary"]["fixed_count"] == 1
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Fixed Issues" in markdown
    assert "Remaining Issues" in build_diff_markdown(diff)
