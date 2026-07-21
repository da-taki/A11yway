






from pathlib import Path

import pytest

from a11yway.core.announce import (
    ANNOUNCE_LIMITATIONS,
    announcement_from_ax_node,
    build_announce_transcript,
    capture_focused_announcement,
    format_announcement,
    is_unnamed_announcement,
    trace_has_announce_data,
)
from a11yway.core.browser_runner import is_playwright_available, run_browser_audit
from a11yway.core.report_builder import (
    build_html_report,
    build_json_report,
    build_markdown_report,
)
from a11yway.core.rules import get_rule
from a11yway.core.visual_proof import build_focus_overlay_html


def named_trace_entry(**overrides) -> dict:

    entry = {
        "step": 1,
        "tag": "input",
        "id": "full_name",
        "name": "full_name",
        "type": "text",
        "href": None,
        "src": None,
        "text": "",
        "role": None,
        "accessible_name_guess": "Full name",
        "is_visible": True,
        "announce": {
            "role": "textbox",
            "name": "Full name",
            "states": ["required"],
            "ignored": False,
        },
        "announcement": 'textbox, "Full name", required',
    }
    entry.update(overrides)
    return entry


def unnamed_trace_entry(**overrides) -> dict:

    entry = named_trace_entry(
        step=2,
        tag="button",
        id=None,
        name=None,
        type="button",
        accessible_name_guess="",
        announce={"role": "button", "name": "", "states": [], "ignored": False},
        announcement="button, (no accessible name)",
    )
    entry.update(overrides)
    return entry


def announce_browser_result(**overrides) -> dict:

    result = {
        "mode": "browser",
        "source": "examples/sample_announce_transcript.html",
        "final_url": "file:///sample_announce_transcript.html",
        "success": True,
        "error": None,
        "checks_run": [
            "keyboard_focus_traversal",
            "browser_dom_snapshot",
            "accessibility_tree_announce",
        ],
        "focus_trace": [named_trace_entry(), unnamed_trace_entry()],
        "issues": [],
    }
    result.update(overrides)
    return result


def test_format_announcement_examples() -> None:

    unnamed = {"role": "button", "name": "", "states": [], "ignored": False}
    named = {"role": "edit", "name": "Full name", "states": ["required"], "ignored": False}

    assert format_announcement(unnamed) == "button, (no accessible name)"
    assert format_announcement(named) == 'edit, "Full name", required'
    assert format_announcement(None) == "(announcement unavailable)"


def test_announcement_from_ax_node_maps_states() -> None:

    node = {
        "role": {"value": "checkbox"},
        "name": {"value": "Send me the monthly reading list"},
        "ignored": False,
        "properties": [
            {"name": "checked", "value": {"value": "true"}},
            {"name": "required", "value": {"value": True}},
            {"name": "invalid", "value": {"value": "false"}},
            {"name": "focusable", "value": {"value": True}},
        ],
    }

    announce = announcement_from_ax_node(node)

    assert announce["role"] == "checkbox"
    assert announce["name"] == "Send me the monthly reading list"
    assert announce["states"] == ["required", "checked"]
    assert announce["ignored"] is False


def test_announcement_from_ax_node_handles_tristate_and_expanded() -> None:

    node = {
        "role": {"value": "button"},
        "name": {"value": "Show opening hours"},
        "properties": [
            {"name": "expanded", "value": {"value": False}},
            {"name": "checked", "value": {"value": "mixed"}},
        ],
    }

    announce = announcement_from_ax_node(node)

    assert announce["states"] == ["partially checked", "collapsed"]


def test_is_unnamed_announcement() -> None:

    assert is_unnamed_announcement({"role": "button", "name": "", "states": []})
    assert is_unnamed_announcement({"role": "button", "name": "   ", "states": []})
    assert not is_unnamed_announcement({"role": "button", "name": "Go", "states": []})
    assert not is_unnamed_announcement(None)


def test_capture_returns_none_without_session() -> None:

    assert capture_focused_announcement(None) is None


def test_build_announce_transcript_marks_unnamed_and_unavailable() -> None:

    trace = [
        named_trace_entry(),
        unnamed_trace_entry(),
        named_trace_entry(step=3, announce=None, announcement=None),
    ]

    transcript = build_announce_transcript(trace)

    assert transcript[0]["announcement"] == 'textbox, "Full name", required'
    assert transcript[0]["unnamed"] is False
    assert transcript[0]["available"] is True
    assert transcript[1]["unnamed"] is True
    assert transcript[2]["available"] is False
    assert transcript[2]["announcement"] == "(announcement unavailable)"
    assert transcript[2]["unnamed"] is False


def test_trace_has_announce_data() -> None:

    assert trace_has_announce_data([named_trace_entry()])
    assert not trace_has_announce_data([{"step": 1, "tag": "a"}])
    assert not trace_has_announce_data([])


def test_unnamed_focus_stop_rule_exists_in_registry() -> None:

    rule = get_rule("unnamed_focus_stop")

    assert rule is not None
    assert rule["category"] == "Keyboard Interaction"
    assert rule["default_severity"] == "high"
    assert rule["browser_check_limitations"]
    assert rule["how_to_fix"]


def test_json_report_includes_announce_transcript() -> None:

    report = build_json_report(
        "examples/sample_announce_transcript.html",
        [],
        browser_result=announce_browser_result(),
    )

    transcript = report["browser"]["announce_transcript"]
    assert len(transcript) == 2
    assert transcript[1]["unnamed"] is True
    for limitation in ANNOUNCE_LIMITATIONS:
        assert limitation in report["browser"]["limitations"]


def test_json_report_without_announce_data_stays_unchanged() -> None:

    result = announce_browser_result(
        focus_trace=[{"step": 1, "tag": "a", "accessible_name_guess": "Home"}]
    )
    report = build_json_report("examples/sample_form.html", [], browser_result=result)

    assert "announce_transcript" not in report["browser"]


def test_markdown_report_renders_announce_transcript() -> None:

    report = build_json_report(
        "examples/sample_announce_transcript.html",
        [],
        browser_result=announce_browser_result(),
    )

    markdown = build_markdown_report(report)

    assert "## Announce Transcript" in markdown
    assert '1. textbox, "Full name", required' in markdown
    assert "2. button, (no accessible name) <- finding: unnamed focus stop" in markdown


def test_html_report_renders_announce_transcript() -> None:

    report = build_json_report(
        "examples/sample_announce_transcript.html",
        [],
        browser_result=announce_browser_result(),
    )

    html = build_html_report(report)

    assert "Announce Transcript" in html
    assert "&quot;Full name&quot;, required" in html
    assert 'class="announce-unnamed"' in html
    assert "(finding: unnamed focus stop)" in html


def test_task_execution_report_shows_announced_column() -> None:

    execution = {
        "mode": "browser_task_execution",
        "source": "examples/sample_task_execution_form.html",
        "task_id": "submit_scholarship_application",
        "task_name": "Submit scholarship application",
        "student_profile": "keyboard_only",
        "success": True,
        "error": None,
        "completed": True,
        "blocked_at_step": None,
        "steps_total": 1,
        "steps_passed": 1,
        "announce_available": True,
        "steps": [
            {
                "id": "focus_full_name",
                "action": "focus_by_label_or_name",
                "target": "Full name",
                "description": "",
                "status": "passed",
                "detail": "Reached with the keyboard (tag: input).",
                "used_fallback": False,
                "announced": 'textbox, "Full name", required',
            }
        ],
    }
    report = build_json_report(
        "examples/sample_task_execution_form.html", [], task_execution=execution
    )

    markdown = build_markdown_report(report)
    html = build_html_report(report)

    assert "| Step | Action | Status | Announced | Detail |" in markdown
    assert '| focus_full_name | focus_by_label_or_name | passed | textbox, "Full name", required |' in markdown
    assert "<th>Announced</th>" in html
    assert "&quot;Full name&quot;, required" in html
    for limitation in ANNOUNCE_LIMITATIONS:
        assert limitation in report["task_execution"]["limitations"]


def test_focus_overlay_includes_announcements() -> None:

    focus_points = [
        {
            "step": 1,
            "tag": "input",
            "accessible_name_guess": "Full name",
            "announcement": 'textbox, "Full name", required',
            "x": 10,
            "y": 20,
            "width": 100,
            "height": 30,
        },
        {
            "step": 2,
            "tag": "button",
            "accessible_name_guess": "",
            "announcement": "button, (no accessible name)",
            "x": 10,
            "y": 80,
            "width": 40,
            "height": 30,
        },
    ]

    overlay = build_focus_overlay_html("page.png", focus_points, source="sample.html")

    assert "Announce Transcript" in overlay
    assert "button, (no accessible name)" in overlay
    assert "Step 1 | textbox, &quot;Full name&quot;, required" in overlay


def test_focus_overlay_without_announcements_stays_unchanged() -> None:

    focus_points = [
        {"step": 1, "tag": "a", "accessible_name_guess": "Home", "x": 1, "y": 2}
    ]

    overlay = build_focus_overlay_html("page.png", focus_points, source="sample.html")

    assert "Announce Transcript" not in overlay


def test_announce_example_pages_exist() -> None:

    assert Path("examples/sample_announce_transcript.html").exists()
    assert Path("examples/sample_announce_transcript_broken.html").exists()


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_flags_unnamed_focus_stops() -> None:

    result = run_browser_audit("examples/sample_announce_transcript_broken.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")
    if not trace_has_announce_data(result["focus_trace"]):
        pytest.skip("Accessibility tree data was not available in this browser run.")

    unnamed = [
        issue for issue in result["issues"] if issue.issue_type == "unnamed_focus_stop"
    ]
    assert unnamed, "Expected at least one unnamed_focus_stop finding"
    for issue in unnamed:
        assert issue.severity == "high"
        assert issue.evidence.get("announcement")

    heuristic = [
        issue
        for issue in result["issues"]
        if issue.issue_type == "browser_focused_control_missing_name"
    ]
    assert not heuristic


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_browser_audit_announces_names_and_states_on_clean_page() -> None:

    result = run_browser_audit("examples/sample_announce_transcript.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")
    if not trace_has_announce_data(result["focus_trace"]):
        pytest.skip("Accessibility tree data was not available in this browser run.")

    announcements = [
        entry.get("announcement")
        for entry in result["focus_trace"]
        if entry.get("announcement")
    ]
    assert any("Full name" in text for text in announcements)
    assert any("required" in text for text in announcements)

    unnamed = [
        issue for issue in result["issues"] if issue.issue_type == "unnamed_focus_stop"
    ]
    assert not unnamed
