"""Tests for video proof recording of task executions.

These tests must pass whether or not Playwright is installed. The real
browser integration tests skip themselves when the browser cannot run.
"""

from pathlib import Path

import pytest

from a11yway.core import task_executor
from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.report_builder import (
    build_html_report,
    build_json_report,
    build_markdown_report,
)
from a11yway.core.task_executor import run_task_execution
from a11yway.core.task_runner import find_task, load_tasks
from a11yway.main import main


def scholarship_task():
    """Load the accessible sample task used across the test suite."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    assert task is not None
    return task


def execution_with_video(video: dict | None) -> dict:
    """Build a small execution result carrying video metadata."""
    return {
        "task_id": "submit_scholarship_application",
        "task_name": "Submit scholarship application",
        "student_profile": "Keyboard-only student",
        "success": True,
        "error": None,
        "completed": True,
        "blocked_at_step": None,
        "blocked_reason": None,
        "steps_total": 1,
        "steps_passed": 1,
        "announce_available": False,
        "steps": [],
        "video": video,
    }


def test_cli_video_requires_task_and_visual_proof(capsys) -> None:
    """--video without its companions should fail clearly."""
    exit_code = main(["examples/sample_form.html", "--video"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Video proof requires" in captured.out


def test_cli_video_guard_is_setup_error_in_ci_mode() -> None:
    """The same misuse in --ci mode must exit 3."""
    exit_code = main(["examples/sample_form.html", "--video", "--ci"])

    assert exit_code == 3


def test_execution_without_playwright_stays_graceful(monkeypatch, tmp_path: Path) -> None:
    """Asking for video without Playwright degrades like everything else."""
    monkeypatch.setattr(task_executor, "is_playwright_available", lambda: False)

    result = run_task_execution(
        "examples/sample_task_execution_form.html",
        scholarship_task(),
        video_dir=tmp_path,
    )

    assert result["success"] is False
    assert "Playwright" in result["error"]
    assert result["video"] is None


def test_reports_link_the_video_with_caption() -> None:
    """All report formats should carry the video path and caption."""
    video = {
        "enabled": True,
        "path": "reports/visual_task_execution/task_execution.webm",
        "caption": (
            'Keyboard-only task execution of "Submit scholarship application" '
            "on examples/sample_task_execution_form.html in one headless "
            "Chromium run. An evidence aid for human reviewers, not "
            "accessibility certification."
        ),
    }
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution=execution_with_video(video),
    )

    markdown = build_markdown_report(report)
    html = build_html_report(report)

    assert report["visual_proof"]["video_path"] == video["path"]
    assert report["visual_proof"]["video_caption"] == video["caption"]
    assert "- Task execution video: reports/visual_task_execution/task_execution.webm" in markdown
    assert "one headless Chromium run" in markdown
    assert "<h3>Task Execution Video</h3>" in html
    assert 'href="reports/visual_task_execution/task_execution.webm"' in html
    assert "evidence aid for human reviewers" in html


def test_reports_show_video_errors_honestly() -> None:
    """A failed recording must be reported, not hidden."""
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution=execution_with_video(
            {"enabled": False, "error": "Recording could not start."}
        ),
    )

    markdown = build_markdown_report(report)

    assert report["visual_proof"]["video_error"] == "Recording could not start."
    assert "Task execution video unavailable: Recording could not start." in markdown


def test_reports_without_video_stay_unchanged() -> None:
    """Executions that did not record must not grow video keys."""
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution=execution_with_video(None),
    )

    assert "visual_proof" not in report


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_video_recording_produces_a_webm_file(tmp_path: Path) -> None:
    """Integration: the recording lands in the requested directory."""
    result = run_task_execution(
        "examples/sample_task_execution_form.html",
        scholarship_task(),
        video_dir=tmp_path,
    )

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    video = result["video"]
    assert video and video["enabled"] is True
    video_path = Path(video["path"])
    assert video_path.name == "task_execution.webm"
    assert video_path.exists()
    size = video_path.stat().st_size
    assert 0 < size < 20 * 1024 * 1024, "viewport-sized video should stay small"
    assert "Submit scholarship application" in video["caption"]
    assert result["completed"] is True


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_cli_video_end_to_end(tmp_path: Path) -> None:
    """Integration: --video saves the recording and links it in HTML."""
    proof_dir = tmp_path / "visual"
    html_path = tmp_path / "report.html"

    exit_code = main(
        [
            "examples/sample_task_execution_form.html",
            "--browser",
            "--execute-task",
            "submit_scholarship_application",
            "--visual-proof",
            str(proof_dir),
            "--video",
            "--html",
            str(html_path),
        ]
    )

    assert exit_code == 0
    assert (proof_dir / "task_execution.webm").exists()
    html = html_path.read_text(encoding="utf-8")
    assert "Task Execution Video" in html
    assert "task_execution.webm" in html
