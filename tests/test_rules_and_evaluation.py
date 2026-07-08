"""Tests for the rule registry, enriched reports, and evaluation summaries."""

import csv
import json
from pathlib import Path

from a11yway.core.batch_runner import run_batch
from a11yway.core.rules import (
    RULES,
    enrich_issue_with_rule,
    get_rule,
    list_rules,
)
from a11yway.core.report_builder import (
    build_evaluation_summary_markdown,
    build_json_report,
    build_markdown_report,
)
from a11yway.main import analyze_html_file, main
from a11yway.models.issue import AccessibilityIssue


EXPECTED_STATIC_ISSUE_TYPES = {
    "missing_form_label",
    "missing_button_name",
    "missing_link_name",
    "generic_link_text",
    "missing_image_alt",
    "missing_h1",
    "skipped_heading_level",
    "multiple_h1",
    "missing_page_title",
    "missing_html_lang",
    "missing_video_captions",
    "missing_audio_transcript",
}

EXPECTED_BROWSER_ISSUE_TYPES = {
    "browser_no_focusable_elements",
    "browser_focus_not_moving",
    "browser_repeated_focus",
    "browser_focused_control_missing_name",
    "browser_focus_on_hidden_element",
}

EXPECTED_TASK_EXECUTION_ISSUE_TYPES = {
    "task_step_blocked",
    "task_control_not_keyboard_reachable",
    "task_expected_content_missing",
}

EXPECTED_LOW_VISION_ISSUE_TYPES = {
    "low_contrast_text",
    "zoom_horizontal_overflow",
    "zoom_fixed_width_content",
    "focus_indicator_missing",
}

EXPECTED_ISSUE_TYPES = (
    EXPECTED_STATIC_ISSUE_TYPES
    | EXPECTED_BROWSER_ISSUE_TYPES
    | EXPECTED_TASK_EXECUTION_ISSUE_TYPES
    | EXPECTED_LOW_VISION_ISSUE_TYPES
)


def test_rule_registry_covers_all_expected_issue_types() -> None:
    """The registry should document every current static issue type."""
    assert set(RULES) == EXPECTED_ISSUE_TYPES


def test_every_rule_has_required_documentation_fields() -> None:
    """Each rule should describe the check for reviewers."""
    required_fields = {
        "issue_type",
        "title",
        "category",
        "default_severity",
        "why_it_matters",
        "how_to_fix",
        "manual_review_notes",
        "standard_hint",
    }

    for issue_type, rule in RULES.items():
        assert required_fields.issubset(rule), issue_type
        assert rule["issue_type"] == issue_type
        assert rule["default_severity"] in {"high", "medium", "low"}
        # Static rules explain static limits; browser rules explain browser limits.
        assert "static_check_limitations" in rule or "browser_check_limitations" in rule


def test_get_rule_returns_known_rule() -> None:
    """get_rule should return the registry entry for a known issue type."""
    rule = get_rule("missing_form_label")

    assert rule is not None
    assert rule["category"] == "Forms"
    assert rule["default_severity"] == "high"


def test_get_rule_returns_none_for_unknown_issue_type() -> None:
    """Unknown issue types should return None, not raise."""
    assert get_rule("not_a_real_rule") is None


def test_list_rules_returns_all_rules() -> None:
    """list_rules should return one entry per registered issue type."""
    rules = list_rules()

    assert len(rules) == len(EXPECTED_ISSUE_TYPES)
    assert {rule["issue_type"] for rule in rules} == EXPECTED_ISSUE_TYPES


def test_enrich_issue_with_rule_accepts_accessibility_issue() -> None:
    """Enrichment should work directly on AccessibilityIssue objects."""
    issue = AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type="missing_form_label",
        severity="high",
        agent_name="Page Analyzer",
        evidence={"tag": "input"},
        suggested_fix="Add a label.",
    )

    enriched = enrich_issue_with_rule(issue)

    assert enriched["rule"]["title"]
    assert enriched["rule"]["category"] == "Forms"


def test_enrich_issue_with_rule_leaves_unknown_types_unchanged() -> None:
    """Unknown issue types should pass through without a rule block."""
    enriched = enrich_issue_with_rule({"issue_type": "future_check", "severity": "low"})

    assert "rule" not in enriched
    assert enriched["issue_type"] == "future_check"


def test_json_report_issues_include_rule_metadata() -> None:
    """Every JSON report issue should carry rule metadata."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    for issue in report["issues"]:
        assert "rule" in issue
        assert issue["rule"]["title"]
        assert issue["rule"]["category"]
        assert issue["rule"]["why_it_matters"]


def test_markdown_report_includes_rule_details() -> None:
    """Markdown issues should show rule title, category, and why it matters."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert "- Rule: Form control missing accessible label" in markdown
    assert "- Category: Forms" in markdown
    assert "- Why it matters:" in markdown
    assert "- Static check limitation:" in markdown


def test_cli_list_rules_prints_issue_types(capsys) -> None:
    """--list-rules should print every issue type without running an audit."""
    exit_code = main(["--list-rules"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Issues found" not in captured.out
    for issue_type in EXPECTED_ISSUE_TYPES:
        assert issue_type in captured.out


def test_cli_rule_details_for_known_rule(capsys) -> None:
    """--rule should print full documentation for one rule."""
    exit_code = main(["--rule", "missing_form_label"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "missing_form_label" in captured.out
    assert "Why it matters:" in captured.out
    assert "How to fix:" in captured.out


def test_cli_rule_details_for_unknown_rule(capsys) -> None:
    """--rule with an unknown type should fail gracefully with a message."""
    exit_code = main(["--rule", "not_a_real_rule"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Unknown rule" in captured.out


def test_batch_run_creates_evaluation_summary(tmp_path: Path) -> None:
    """Batch mode should write evaluation_summary.md in the output directory."""
    out_dir = tmp_path / "batch_sample"
    result = run_batch("examples/sample_batch.json", out_dir)

    summary_path = out_dir / "evaluation_summary.md"
    assert summary_path.exists()
    assert result["evaluation_summary_path"] == summary_path.as_posix()


def test_evaluation_summary_includes_totals_and_top_issue_types(tmp_path: Path) -> None:
    """The evaluation summary should report totals and ranked issue types."""
    out_dir = tmp_path / "batch_sample"
    result = run_batch("examples/sample_batch.json", out_dir)

    markdown = (out_dir / "evaluation_summary.md").read_text(encoding="utf-8")
    total_issues = result["index"]["summary"]["total_issues"]

    assert "# A11yway Batch Evaluation Summary" in markdown
    assert f"- Total issues: {total_issues}" in markdown
    assert "## Top Issue Types" in markdown
    assert "## Severity Breakdown" in markdown
    assert "## High Priority Findings" in markdown
    assert "## Recommended Review Process" in markdown
    assert "missing_form_label" in markdown


def test_evaluation_summary_lists_high_priority_findings(tmp_path: Path) -> None:
    """High severity issues should appear with page names and evidence."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    markdown = (out_dir / "evaluation_summary.md").read_text(encoding="utf-8")

    assert "### Student Scholarship Application" in markdown
    assert "- Evidence: `" in markdown


def test_index_json_includes_new_summary_fields(tmp_path: Path) -> None:
    """index.json should include evaluation summary path and page counts."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))

    assert index["evaluation_summary_path"].endswith("evaluation_summary.md")
    assert index["summary"]["successful_pages"] == 2
    assert index["summary"]["failed_pages"] == 0
    assert index["summary"]["total_task_blockers"] >= 1
    # Existing fields must stay for backwards compatibility.
    assert index["summary"]["total_pages_tested"] == 2
    assert "counts_by_severity" in index["summary"]


def test_index_counts_failed_pages(tmp_path: Path) -> None:
    """Failed sources should be counted separately in the summary."""
    config_path = tmp_path / "batch_with_failure.json"
    config_path.write_text(
        json.dumps(
            [
                {
                    "id": "valid_page",
                    "name": "Valid Page",
                    "source": "examples/sample_form.html",
                },
                {
                    "id": "missing_page",
                    "name": "Missing Page",
                    "source": str(tmp_path / "missing.html"),
                },
            ]
        ),
        encoding="utf-8",
    )

    result = run_batch(config_path, tmp_path / "batch_output")
    summary = result["index"]["summary"]

    assert summary["successful_pages"] == 1
    assert summary["failed_pages"] == 1


def test_batch_still_creates_csv_alongside_summary(tmp_path: Path) -> None:
    """The CSV benchmark index should still be generated with its old headers."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    assert (out_dir / "index.csv").exists()
    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2


def test_build_evaluation_summary_handles_empty_batch() -> None:
    """The summary builder should not break on an empty index report."""
    markdown = build_evaluation_summary_markdown(
        {"summary": {}, "sources": [], "limitations": []}
    )

    assert "# A11yway Batch Evaluation Summary" in markdown
    assert "No high severity issues" in markdown


def test_cli_batch_mode_prints_evaluation_summary_path(tmp_path: Path, capsys) -> None:
    """CLI batch output should point reviewers at the evaluation summary."""
    out_dir = tmp_path / "batch_sample"

    exit_code = main(
        ["--batch", "examples/sample_batch.json", "--out-dir", str(out_dir)]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Evaluation summary:" in captured.out
    assert (out_dir / "evaluation_summary.md").exists()


def test_evaluation_batch_template_is_valid_config() -> None:
    """The evaluation template should be a loadable batch config."""
    items = json.loads(
        Path("examples/evaluation_batch_template.json").read_text(encoding="utf-8")
    )

    assert isinstance(items, list)
    for item in items:
        assert item["id"]
        assert item["source"]
        assert "notes" in item
