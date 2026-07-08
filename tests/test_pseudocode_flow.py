"""Lightweight tests for the A11yway pseudocode scaffold."""

import json
from pathlib import Path

from a11yway.agents.dyslexia_agent import DyslexiaAgent
from a11yway.agents.hearing_agent import HearingAgent
from a11yway.agents.keyboard_agent import KeyboardOnlyAgent
from a11yway.agents.low_vision_agent import LowVisionAgent
from a11yway.main import analyze_html_file, main
from a11yway.core.page_analyzer import (
    analyze_heading_structure,
    analyze_html_forms,
    analyze_html_static,
    analyze_images,
    analyze_interactive_names,
    analyze_media_accessibility,
    analyze_page_metadata,
)
from a11yway.core.report_builder import ReportBuilder, build_json_report, save_json_report
from a11yway.core.task_runner import (
    TaskRunner,
    build_task_blockers,
    filter_issues_for_task,
    find_task,
    load_tasks,
)


def issue_types_for(issues: list) -> set[str]:
    """Return issue types from a list of accessibility issues."""
    return {issue.issue_type for issue in issues}


def test_sample_agents_can_be_instantiated() -> None:
    """The initial student agents should be easy to construct."""
    agents = [
        KeyboardOnlyAgent(),
        LowVisionAgent(),
        DyslexiaAgent(),
        HearingAgent(),
    ]

    assert [agent.name for agent in agents] == [
        "Keyboard-only student",
        "Low-vision student",
        "Dyslexia/reading-difficulty student",
        "Hearing-impaired student",
    ]


def test_sample_task_can_be_loaded() -> None:
    """The sample task JSON should load into task dataclasses."""
    runner = TaskRunner(agents=[])
    tasks = runner.load_tasks(Path("examples/sample_tasks.json"))

    assert len(tasks) == 2
    assert tasks[0].id == "submit_scholarship_application"
    assert tasks[0].name == "Submit scholarship application"


def test_report_builder_returns_expected_structure() -> None:
    """ReportBuilder should return a structured report object."""
    runner = TaskRunner(agents=[KeyboardOnlyAgent()])
    task = runner.load_tasks(Path("examples/sample_tasks.json"))[0]

    report = ReportBuilder().build_report(
        task=task,
        agents_used=["Keyboard-only student"],
        issues=[],
    )

    assert report.task.title == task.title
    assert report.agents_used == ["Keyboard-only student"]
    assert report.issues == []
    assert "Found 0 placeholder issue" in report.summary


def test_unlabeled_input_is_flagged() -> None:
    """A text input without an accessible label should be reported."""
    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_form_label"
    assert 'name="student_name"' in issues[0].evidence


def test_input_with_label_for_is_not_flagged() -> None:
    """An input with an associated label should pass this basic check."""
    html = '<label for="email">Email</label><input id="email" type="email">'

    assert analyze_html_forms(html) == []


def test_hidden_and_submit_inputs_are_ignored() -> None:
    """Inputs that do not need student-entered labels should be ignored."""
    html = '<input type="hidden" name="token"><input type="submit" value="Send">'

    assert analyze_html_forms(html) == []


def test_keyboard_agent_uses_html_form_analyzer() -> None:
    """KeyboardOnlyAgent should run static checks when HTML is available."""
    runner = TaskRunner(agents=[])
    task = runner.load_tasks(Path("examples/sample_tasks.json"))[0]
    agent = KeyboardOnlyAgent()

    findings = agent.detect_barriers(
        task,
        {"html": '<form><input type="text" name="student_name"></form>'},
    )

    assert any(issue.issue_type == "missing_form_label" for issue in findings)


def test_sample_form_fixture_exists() -> None:
    """The CLI sample fixture should be present."""
    assert Path("examples/sample_form.html").exists()


def test_sample_form_returns_expected_missing_label_count() -> None:
    """The sample form should contain the expected static audit issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert len(issues) == 7
    assert issue_types_for(issues) == {
        "missing_form_label",
        "generic_link_text",
        "missing_button_name",
        "missing_image_alt",
        "skipped_heading_level",
        "missing_video_captions",
    }


def test_sample_form_labeled_fields_are_not_flagged() -> None:
    """Properly labeled email and school controls should not be reported."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    evidence = " ".join(issue.evidence for issue in issues)

    assert "student_email" not in evidence
    assert "school_name" not in evidence


def test_sample_form_hidden_and_submit_fields_are_ignored() -> None:
    """Hidden and submit fields in the sample should not become issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    evidence = " ".join(issue.evidence for issue in issues)

    assert "application_token" not in evidence
    assert "submit" not in evidence.lower()


def test_empty_button_is_flagged() -> None:
    """A button without text or an accessible name should be reported."""
    issues = analyze_interactive_names("<button></button>")

    assert "missing_button_name" in issue_types_for(issues)


def test_button_with_aria_label_is_not_flagged() -> None:
    """A button with aria-label should pass this basic static check."""
    issues = analyze_interactive_names('<button aria-label="Save draft"></button>')

    assert "missing_button_name" not in issue_types_for(issues)


def test_generic_click_here_link_is_flagged() -> None:
    """Generic link text should be reported."""
    issues = analyze_interactive_names('<a href="/help">click here</a>')

    assert "generic_link_text" in issue_types_for(issues)


def test_descriptive_link_is_not_flagged() -> None:
    """Specific link text should not be treated as generic."""
    issues = analyze_interactive_names(
        '<a href="/guidelines">Download scholarship guidelines</a>'
    )

    assert issue_types_for(issues) == set()


def test_missing_image_alt_is_flagged() -> None:
    """An image without alt should be reported."""
    issues = analyze_images('<img src="award.png">')

    assert "missing_image_alt" in issue_types_for(issues)


def test_image_with_alt_is_not_flagged() -> None:
    """An image with useful alt text should pass this basic check."""
    issues = analyze_images('<img src="award.png" alt="Student receiving an award">')

    assert "missing_image_alt" not in issue_types_for(issues)


def test_missing_h1_is_flagged() -> None:
    """A page without h1 should be reported."""
    html = '<html lang="en"><head><title>Page</title></head><body><h2>Start</h2></body></html>'
    issues = analyze_heading_structure(html)

    assert "missing_h1" in issue_types_for(issues)


def test_skipped_heading_level_is_flagged() -> None:
    """A jump from h1 to h3 should be reported."""
    issues = analyze_heading_structure("<h1>Application</h1><h3>Details</h3>")

    assert "skipped_heading_level" in issue_types_for(issues)


def test_missing_title_is_flagged() -> None:
    """A page without title should be reported."""
    html = '<html lang="en"><body><h1>Application</h1></body></html>'
    issues = analyze_page_metadata(html)

    assert "missing_page_title" in issue_types_for(issues)


def test_missing_html_lang_is_flagged() -> None:
    """A page without html lang should be reported."""
    html = "<html><head><title>Application</title></head><body><h1>Application</h1></body></html>"
    issues = analyze_page_metadata(html)

    assert "missing_html_lang" in issue_types_for(issues)


def test_video_without_captions_is_flagged() -> None:
    """A video without captions or subtitles should be reported."""
    issues = analyze_media_accessibility('<video controls src="lesson.mp4"></video>')

    assert "missing_video_captions" in issue_types_for(issues)


def test_static_analyzer_combines_checks() -> None:
    """The combined analyzer should return issue types from multiple checks."""
    html = '<html><body><h1>Page</h1><button></button><img src="x.png"></body></html>'
    issues = analyze_html_static(html)

    assert {"missing_button_name", "missing_image_alt", "missing_page_title"}.issubset(
        issue_types_for(issues)
    )


def test_build_json_report_returns_expected_top_level_keys() -> None:
    """The CLI JSON report should have a stable prototype structure."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert set(report) == {
        "tool",
        "version",
        "source_file",
        "summary",
        "issues",
        "limitations",
    }


def test_build_json_report_has_correct_issue_count() -> None:
    """The report summary should match the issue list length."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert report["summary"]["issues_found"] == 7
    assert len(report["issues"]) == 7


def test_json_report_includes_issue_counts() -> None:
    """The report summary should include useful grouped counts."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert "counts_by_severity" in report["summary"]
    assert "counts_by_issue_type" in report["summary"]
    assert report["summary"]["counts_by_issue_type"]["missing_form_label"] == 2


def test_save_json_report_writes_valid_json(tmp_path: Path) -> None:
    """JSON reports should be written to disk with parent directories created."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.json"

    save_json_report(report, output_path)

    saved_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_report["tool"] == "A11yway"
    assert saved_report["summary"]["issues_found"] == 7


def test_sample_tasks_load_correctly() -> None:
    """Task scenario helpers should load the sample task file."""
    tasks = load_tasks("examples/sample_tasks.json")

    assert len(tasks) == 2
    assert tasks[0].student_profile == "Keyboard-only student"
    assert "missing_form_label" in tasks[0].relevant_issue_types


def test_find_task_by_id() -> None:
    """A task should be found by exact id."""
    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit_scholarship_application")

    assert task is not None
    assert task.name == "Submit scholarship application"


def test_find_task_by_name_case_insensitively() -> None:
    """A task should be found by case-insensitive name."""
    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit scholarship APPLICATION")

    assert task is not None
    assert task.id == "submit_scholarship_application"


def test_filter_issues_for_task_returns_relevant_issue_types() -> None:
    """Task filtering should keep only task-relevant issue types."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    filtered = filter_issues_for_task(task, issues)

    assert issue_types_for(filtered) == {
        "missing_form_label",
        "missing_button_name",
        "generic_link_text",
        "skipped_heading_level",
    }


def test_task_blockers_are_generated_from_relevant_issues() -> None:
    """Task blockers should be deterministic notes from relevant issues."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    blockers = build_task_blockers(task, issues)

    assert len(blockers) == 5
    assert {blocker["issue_type"] for blocker in blockers} == {
        "missing_form_label",
        "missing_button_name",
        "generic_link_text",
        "skipped_heading_level",
    }
    assert all("task_impact" in blocker for blocker in blockers)


def test_json_report_includes_task_data_when_task_is_provided() -> None:
    """JSON reports should include task context when requested."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    blockers = build_task_blockers(task, issues)
    report = build_json_report(
        "examples/sample_form.html",
        issues,
        task=task,
        task_blockers=blockers,
    )

    assert report["task"]["id"] == "submit_scholarship_application"
    assert report["task"]["student_profile"] == "Keyboard-only student"
    assert len(report["task"]["likely_blockers"]) == 5


def test_cli_default_sample_still_runs(capsys) -> None:
    """The no-argument CLI flow should still analyze the sample fixture."""
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Issues found: 7" in captured.out


def test_cli_task_mode_runs(capsys) -> None:
    """Task mode should print task context without breaking the audit."""
    exit_code = main(
        ["examples/sample_form.html", "--task", "submit_scholarship_application"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Task: Submit scholarship application" in captured.out
    assert "Likely blockers: 5" in captured.out
