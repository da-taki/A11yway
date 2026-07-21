






from pathlib import Path

import pytest

from a11yway.core.browser_runner import (
    _focus_signature,
    _loop_sequence_label,
    find_focus_cycle,
    is_playwright_available,
    run_browser_audit,
)
from a11yway.core.report_builder import (
    build_html_report,
    build_json_report,
    build_markdown_report,
)
from a11yway.core.rules import get_rule
from a11yway.core.task_executor import run_task_execution
from a11yway.models.task import AccessibilityTask


def test_find_focus_cycle_confirms_repeated_tail() -> None:

    a, b, c = ("a",), ("b",), ("c",)

    assert find_focus_cycle([a, b, c, a, b, c]) == 3
    assert find_focus_cycle([c, a, b, a, b]) == 2
    assert find_focus_cycle([a, a]) == 1
    assert find_focus_cycle([a, b, c]) is None
    assert find_focus_cycle([a, b, a, c]) is None
    assert find_focus_cycle([]) is None
    assert find_focus_cycle([a]) is None


def test_find_focus_cycle_prefers_shortest_period() -> None:

    a = ("a",)

    assert find_focus_cycle([a, a, a, a]) == 1


def test_loop_sequence_label_is_readable() -> None:

    entries = [
        {"tag": "select", "id": "rating"},
        {"tag": "button", "id": None, "name": None, "text": "Send feedback"},
        {"tag": "button"},
    ]

    label = _loop_sequence_label(entries)

    assert label == 'select#rating -> button "Send feedback" -> button'


def test_focus_signature_separates_same_name_controls_by_label() -> None:

    first = _focus_signature(
        {
            "tag": "input",
            "name": "modules",
            "type": "checkbox",
            "labelledby_text": "Browser evidence",
        }
    )
    second = _focus_signature(
        {
            "tag": "input",
            "name": "modules",
            "type": "checkbox",
            "labelledby_text": "Low vision checks",
        }
    )

    assert first != second


@pytest.mark.parametrize("issue_type", ["keyboard_trap", "focus_lost"])
def test_trap_rules_exist_in_registry(issue_type: str) -> None:

    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Keyboard Interaction"
    assert rule["default_severity"] in {"high", "medium"}
    assert rule["browser_check_limitations"]


def test_keyboard_trap_rule_references_wcag_212() -> None:

    rule = get_rule("keyboard_trap")

    assert "2.1.2" in rule["standard_hint"]


def test_reports_show_blocked_reason() -> None:

    execution = {
        "mode": "browser_task_execution",
        "source": "examples/sample_keyboard_trap.html",
        "task_id": "fill_course_survey",
        "task_name": "Fill the course survey",
        "student_profile": "Keyboard-only student",
        "success": True,
        "error": None,
        "completed": False,
        "blocked_at_step": "focus_favorite_topic",
        "blocked_reason": "keyboard_trap",
        "steps_total": 1,
        "steps_passed": 0,
        "announce_available": False,
        "steps": [
            {
                "id": "focus_favorite_topic",
                "action": "focus_by_label_or_name",
                "target": "Favorite topic",
                "description": "",
                "status": "failed",
                "detail": "Focus loops through select#rating -> button#send_feedback.",
                "used_fallback": False,
                "announced": None,
                "blocked_reason": "keyboard_trap",
            }
        ],
    }
    report = build_json_report(
        "examples/sample_keyboard_trap.html", [], task_execution=execution
    )

    markdown = build_markdown_report(report)
    html = build_html_report(report)

    assert report["task_execution"]["blocked_reason"] == "keyboard_trap"
    assert "BLOCKED at step `focus_favorite_topic` (reason: keyboard_trap)" in markdown
    assert "BLOCKED at step focus_favorite_topic (reason: keyboard_trap)" in html


def test_blocked_report_without_reason_stays_unchanged() -> None:

    execution = {
        "success": True,
        "completed": False,
        "blocked_at_step": "submit_form",
        "steps_total": 1,
        "steps_passed": 0,
        "steps": [],
    }
    report = build_json_report(
        "examples/sample_task_execution_form_broken.html",
        [],
        task_execution=execution,
    )

    markdown = build_markdown_report(report)

    assert "BLOCKED at step `submit_form`" in markdown
    assert "(reason:" not in markdown


def test_trap_example_pages_exist() -> None:

    assert Path("examples/sample_keyboard_trap.html").exists()
    assert Path("examples/sample_keyboard_trap_fixed.html").exists()


def _survey_task() -> AccessibilityTask:

    return AccessibilityTask(
        id="fill_course_survey",
        name="Fill the course survey",
        student_profile="Keyboard-only student",
        browser_steps=[
            {
                "id": "focus_favorite_topic",
                "action": "focus_by_label_or_name",
                "target": "Favorite topic",
                "description": "Move to the favorite topic field.",
            },
            {
                "id": "type_favorite_topic",
                "action": "type_text",
                "value": "Accessible design",
                "description": "Type an answer.",
            },
        ],
    )


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_detects_keyboard_trap() -> None:

    result = run_browser_audit("examples/sample_keyboard_trap.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    traps = [
        issue for issue in result["issues"] if issue.issue_type == "keyboard_trap"
    ]
    assert traps, "Expected a keyboard_trap finding"
    evidence = traps[0].evidence
    assert traps[0].severity == "high"
    assert "rating" in evidence.get("loop_sequence", "")
    assert evidence.get("unreached_focusable_count", 0) >= 1


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_passes_fixed_trap_page() -> None:

    result = run_browser_audit("examples/sample_keyboard_trap_fixed.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    issue_types = {issue.issue_type for issue in result["issues"]}
    assert "keyboard_trap" not in issue_types
    assert "focus_lost" not in issue_types

    trace_ids = {entry.get("id") for entry in result["focus_trace"]}
    assert "favorite_topic" in trace_ids


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_task_execution_blocked_by_keyboard_trap() -> None:

    result = run_task_execution("examples/sample_keyboard_trap.html", _survey_task())

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    assert result["completed"] is False
    assert result["blocked_at_step"] == "focus_favorite_topic"
    assert result["blocked_reason"] == "keyboard_trap"
    assert "loops" in result["steps"][0]["detail"]

    traps = [
        issue for issue in result["issues"] if issue.issue_type == "keyboard_trap"
    ]
    assert traps
    assert traps[0].evidence.get("loop_sequence")


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_task_execution_completes_on_fixed_trap_page() -> None:

    result = run_task_execution(
        "examples/sample_keyboard_trap_fixed.html", _survey_task()
    )

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    assert result["completed"] is True
    assert result["blocked_reason"] is None


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_detects_focus_lost(tmp_path: Path) -> None:

    page = tmp_path / "focus_lost.html"
    page.write_text(
        """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Focus Lost Demo</title></head>
<body>
  <h1>Focus Lost Demo</h1>
  <button type="button">Start here</button>
  <button type="button" onfocus="this.remove()">Vanishes 1</button>
  <button type="button" onfocus="this.remove()">Vanishes 2</button>
  <button type="button" onfocus="this.remove()">Vanishes 3</button>
  <button type="button" onfocus="this.remove()">Vanishes 4</button>
</body>
</html>
""",
        encoding="utf-8",
    )

    result = run_browser_audit(str(page))

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    lost = [issue for issue in result["issues"] if issue.issue_type == "focus_lost"]
    assert lost, "Expected a focus_lost finding"
    assert lost[0].evidence.get("body_streak", 0) >= 3
