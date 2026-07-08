"""Lightweight tests for the A11yway pseudocode scaffold."""

import json
from pathlib import Path

from a11yway.agents.dyslexia_agent import DyslexiaAgent
from a11yway.agents.hearing_agent import HearingAgent
from a11yway.agents.keyboard_agent import KeyboardOnlyAgent
from a11yway.agents.low_vision_agent import LowVisionAgent
from a11yway.main import analyze_html_file
from a11yway.core.page_analyzer import analyze_html_forms
from a11yway.core.report_builder import ReportBuilder, build_json_report, save_json_report
from a11yway.core.task_runner import TaskRunner


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
    assert tasks[0].title == "Submit a scholarship application form"


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
    """KeyboardOnlyAgent should run the real label check when HTML is available."""
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
    """The sample form should contain exactly two missing label issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert len(issues) == 2
    assert all(issue.issue_type == "missing_form_label" for issue in issues)


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

    assert report["summary"]["issues_found"] == 2
    assert len(report["issues"]) == 2


def test_save_json_report_writes_valid_json(tmp_path: Path) -> None:
    """JSON reports should be written to disk with parent directories created."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.json"

    save_json_report(report, output_path)

    saved_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_report["tool"] == "A11yway"
    assert saved_report["summary"]["issues_found"] == 2
