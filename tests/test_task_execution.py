"""Tests for deterministic browser task execution.

These tests must pass whether or not Playwright is installed. Real
headless-browser integration tests skip themselves when the browser
cannot run.
"""

import csv
import json
from pathlib import Path

import pytest

from a11yway.core import task_executor
from a11yway.core.batch_runner import run_batch
from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.report_builder import build_json_report, build_markdown_report
from a11yway.core.rules import get_rule
from a11yway.core.task_executor import (
    SUPPORTED_ACTIONS,
    _matches_target,
    _normalize,
    run_task_execution,
)
from a11yway.core.task_runner import find_task, load_tasks
from a11yway.main import main
from a11yway.models.task import AccessibilityTask


TASK_EXECUTION_ISSUE_TYPES = [
    "task_step_blocked",
    "task_control_not_keyboard_reachable",
    "task_expected_content_missing",
]


def scholarship_task() -> AccessibilityTask:
    """Load the sample task that defines browser steps."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    assert task is not None
    return task


def fake_execution_result(**overrides) -> dict:
    """Build a small execution result for report tests."""
    result = {
        "mode": "browser_task_execution",
        "source": "examples/sample_task_execution_form.html",
        "task_id": "submit_scholarship_application",
        "task_name": "Submit scholarship application",
        "student_profile": "Keyboard-only student",
        "success": True,
        "error": None,
        "completed": True,
        "blocked_at_step": None,
        "steps_total": 2,
        "steps_passed": 2,
        "steps": [
            {
                "id": "read_page_purpose",
                "action": "expect_visible_text",
                "target": "Student Scholarship Application",
                "description": "Confirm the page purpose is visible.",
                "status": "passed",
                "detail": "Text is visible on the page.",
                "used_fallback": False,
            },
            {
                "id": "submit_form",
                "action": "activate_by_role_or_text",
                "target": "Submit application",
                "description": "Submit the application.",
                "status": "passed",
                "detail": "Activated with Enter (tag: button).",
                "used_fallback": False,
            },
        ],
        "issues": [],
    }
    result.update(overrides)
    return result


def test_task_model_loads_browser_steps() -> None:
    """The extended task schema should load browser steps from JSON."""
    task = scholarship_task()

    assert len(task.browser_steps) == 11
    assert task.browser_steps[0]["action"] == "expect_visible_text"
    assert task.browser_steps[-1]["action"] == "wait_for_text"


def test_tasks_without_browser_steps_stay_compatible() -> None:
    """Tasks that do not define browser_steps should default to an empty list."""
    tasks = load_tasks("examples/sample_tasks.json")
    other_task = find_task(tasks, "access_learning_resources")

    assert other_task is not None
    assert other_task.browser_steps == []


def test_sample_task_steps_use_only_supported_actions() -> None:
    """Every sample step action must be implemented by the runner."""
    task = scholarship_task()

    for step in task.browser_steps:
        assert step["action"] in SUPPORTED_ACTIONS, step["id"]


def test_normalize_handles_underscores_and_case() -> None:
    """Matching normalization should be forgiving but deterministic."""
    assert _normalize("Student_Name") == "student name"
    assert _normalize("  Submit   application ") == "submit application"
    assert _normalize(None) == ""


def test_matches_target_prefers_labels_and_accepts_name_fallback() -> None:
    """Target matching should use labels first and id/name as weak fallback."""
    labeled = {"label_text": "Student name", "tag": "input"}
    named_only = {"name": "student_name", "tag": "input"}
    unrelated = {"label_text": "School", "tag": "select"}

    assert _matches_target(labeled, "Student name")
    assert _matches_target(named_only, "Student name")
    assert not _matches_target(unrelated, "Student name")


def test_matches_target_rejects_empty_target() -> None:
    """An empty target should never match anything."""
    assert not _matches_target({"label_text": "Email"}, "")


@pytest.mark.parametrize("issue_type", TASK_EXECUTION_ISSUE_TYPES)
def test_task_execution_rules_exist(issue_type: str) -> None:
    """Task execution issue types should be documented in the registry."""
    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Task Execution"
    assert rule["default_severity"] in {"high", "medium"}
    assert rule["browser_check_limitations"]


def test_json_report_includes_task_execution_block() -> None:
    """Reports should carry the execution verdict and step evidence."""
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution=fake_execution_result(),
    )

    execution = report["task_execution"]
    assert execution["completed"] is True
    assert execution["steps_total"] == 2
    assert execution["steps"][0]["id"] == "read_page_purpose"
    assert execution["limitations"]


def test_json_report_without_execution_is_unchanged() -> None:
    """Reports built without execution data must not grow the new key."""
    report = build_json_report("examples/sample_form.html", [])

    assert "task_execution" not in report


def test_markdown_report_shows_completed_verdict() -> None:
    """Markdown should state the keyboard-only completion verdict."""
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution=fake_execution_result(),
    )

    markdown = build_markdown_report(report)

    assert "## Task Execution" in markdown
    assert "COMPLETED with keyboard-only interaction" in markdown
    assert "| read_page_purpose |" in markdown
    assert "### Task Execution Limitations" in markdown


def test_markdown_report_shows_blocked_verdict() -> None:
    """Markdown should name the blocking step when the task fails."""
    report = build_json_report(
        "examples/sample_task_execution_form_broken.html",
        [],
        task_execution=fake_execution_result(
            completed=False,
            blocked_at_step="submit_form",
            steps_passed=1,
        ),
    )

    markdown = build_markdown_report(report)

    assert "BLOCKED at step `submit_form`" in markdown


def test_run_task_execution_without_playwright(monkeypatch) -> None:
    """The executor should degrade gracefully when Playwright is missing."""
    monkeypatch.setattr(task_executor, "is_playwright_available", lambda: False)

    result = run_task_execution("examples/sample_task_execution_form.html", scholarship_task())

    assert result["success"] is False
    assert "Playwright" in result["error"]
    assert result["steps"] == []


def test_run_task_execution_requires_browser_steps() -> None:
    """A task without browser_steps should return a clear error."""
    task = AccessibilityTask(id="empty_task", name="Empty task")

    result = run_task_execution("examples/sample_form.html", task)

    assert result["success"] is False
    assert "browser_steps" in result["error"]


def test_cli_execute_task_requires_browser_flag(capsys) -> None:
    """--execute-task without --browser should fail with a clear message."""
    exit_code = main(
        ["examples/sample_task_execution_form.html", "--execute-task", "submit_scholarship_application"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "requires browser mode" in captured.out


def test_cli_execute_tasks_requires_browser_flag(capsys) -> None:
    """Batch --execute-tasks without --browser should fail the same way."""
    exit_code = main(
        ["--batch", "examples/sample_task_execution_batch.json", "--execute-tasks"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "requires browser mode" in captured.out


def test_cli_execute_task_unknown_task(monkeypatch, capsys) -> None:
    """An unknown task id should exit before any browser work."""
    import a11yway.main as main_module

    monkeypatch.setattr(main_module, "is_playwright_available", lambda: True)
    exit_code = main(
        ["examples/sample_form.html", "--browser", "--execute-task", "not_a_real_task"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Task not found" in captured.out


def test_sample_task_execution_fixtures_exist() -> None:
    """Both sample forms and the batch config should be present."""
    assert Path("examples/sample_task_execution_form.html").exists()
    assert Path("examples/sample_task_execution_form_broken.html").exists()
    assert Path("examples/sample_task_execution_batch.json").exists()


def test_static_batch_includes_task_execution_columns(tmp_path: Path) -> None:
    """CSV and index should carry execution fields even without execution."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["task_execution_status"] == ""

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
    assert index["summary"]["tasks_executed"] == 0
    assert index["summary"]["tasks_completed"] == 0
    assert index["summary"]["tasks_blocked"] == 0


@pytest.mark.skipif(not is_playwright_available(), reason="Playwright is not installed")
def test_accessible_form_task_completes() -> None:
    """Integration: the accessible sample form should complete every step."""
    result = run_task_execution("examples/sample_task_execution_form.html", scholarship_task())

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    assert result["completed"] is True
    assert result["blocked_at_step"] is None
    assert result["steps_passed"] == result["steps_total"] == 11
    assert result["issues"] == []


@pytest.mark.skipif(not is_playwright_available(), reason="Playwright is not installed")
def test_broken_form_task_is_blocked_at_submit() -> None:
    """Integration: the click-only submit div should block the task."""
    result = run_task_execution(
        "examples/sample_task_execution_form_broken.html", scholarship_task()
    )

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    assert result["completed"] is False
    assert result["blocked_at_step"] == "submit_form"
    issue_types = {issue.issue_type for issue in result["issues"]}
    assert "task_step_blocked" in issue_types
    statuses = {step["id"]: step["status"] for step in result["steps"]}
    assert statuses["submit_form"] == "failed"
    assert statuses["confirm_submission"] == "skipped"


@pytest.mark.skipif(not is_playwright_available(), reason="Playwright is not installed")
def test_batch_task_execution_records_statuses(tmp_path: Path) -> None:
    """Integration: batch execution should record per-item verdicts."""
    out_dir = tmp_path / "task_execution_batch"
    result = run_batch(
        "examples/sample_task_execution_batch.json",
        out_dir,
        browser=True,
        execute_tasks=True,
    )

    statuses = {
        item["id"]: item["task_execution_status"]
        for item in result["index"]["sources"]
    }
    if "failed" in statuses.values():
        pytest.skip("Browser could not run in this environment.")

    assert statuses["accessible_application_form"] == "completed"
    assert statuses["broken_application_form"] == "blocked"
    assert result["index"]["summary"]["tasks_executed"] == 2
    assert result["index"]["summary"]["tasks_completed"] == 1
    assert result["index"]["summary"]["tasks_blocked"] == 1

    summary_md = (out_dir / "evaluation_summary.md").read_text(encoding="utf-8")
    assert "## Task Execution Results" in summary_md
