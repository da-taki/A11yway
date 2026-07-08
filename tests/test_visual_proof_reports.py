"""Tests for HTML reports and visual proof overlays."""

import csv
import json
from pathlib import Path

import pytest

from a11yway.core.batch_runner import run_batch
from a11yway.core.browser_runner import is_playwright_available, run_browser_audit
from a11yway.core.report_builder import (
    build_html_report,
    build_json_report,
    save_html_report,
)
from a11yway.core.visual_proof import build_focus_overlay_html, save_focus_overlay_html
from a11yway.main import analyze_html_file, main


def sample_report() -> dict:
    """Build a small realistic report with issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    return build_json_report("examples/sample_form.html", issues)


def test_build_html_report_includes_title_summary_and_issues() -> None:
    """HTML reports should render the core static report sections."""
    html = build_html_report(sample_report())

    assert "<title>A11yway Accessibility Report</title>" in html
    assert "<h2>Summary</h2>" in html
    assert "Issues found" in html
    assert "missing_form_label" in html


def test_save_html_report_writes_file(tmp_path: Path) -> None:
    """HTML reports should be written to disk."""
    output_path = tmp_path / "report.html"

    save_html_report(sample_report(), output_path)

    assert output_path.exists()
    assert "A11yway Accessibility Report" in output_path.read_text(encoding="utf-8")


def test_html_report_includes_task_execution_section() -> None:
    """Task execution blocks should appear in HTML reports when present."""
    report = build_json_report(
        "examples/sample_task_execution_form.html",
        [],
        task_execution={
            "task_id": "submit_scholarship_application",
            "task_name": "Submit scholarship application",
            "student_profile": "Keyboard-only student",
            "success": True,
            "completed": True,
            "blocked_at_step": None,
            "steps_total": 1,
            "steps_passed": 1,
            "steps": [
                {
                    "id": "confirm_submission",
                    "action": "wait_for_text",
                    "status": "passed",
                    "detail": "Confirmation text appeared.",
                }
            ],
        },
    )

    html = build_html_report(report)

    assert "<h2>Task Execution</h2>" in html
    assert "COMPLETED with keyboard-only interaction" in html
    assert "confirm_submission" in html


def test_html_report_includes_visual_proof_section() -> None:
    """Visual proof metadata should render as links and counts."""
    report = build_json_report(
        "examples/sample_dynamic_form.html",
        [],
        browser_result={
            "success": True,
            "error": None,
            "final_url": "file:///sample_dynamic_form.html",
            "checks_run": ["keyboard_focus_traversal"],
            "focus_trace": [],
            "visual_proof": {
                "enabled": True,
                "screenshot_path": "reports/visual_dynamic/page.png",
                "focus_overlay_path": "reports/visual_dynamic/focus_path.html",
                "focus_points_count": 2,
                "limitations": ["Focus overlay shows observed Tab stops."],
            },
        },
    )

    html = build_html_report(report)

    assert "<h2>Visual Proof</h2>" in html
    assert "reports/visual_dynamic/page.png" in html
    assert "reports/visual_dynamic/focus_path.html" in html
    assert "Focus points count: 2" in html


def test_focus_overlay_html_from_fake_focus_points() -> None:
    """The overlay helper should work without Playwright."""
    html = build_focus_overlay_html(
        "page.png",
        [
            {
                "step": 1,
                "tag": "a",
                "accessible_name_guess": "Download guide",
                "x": 20,
                "y": 40,
                "width": 100,
                "height": 20,
            }
        ],
        source="examples/sample_form.html",
        viewport={"width": 1280, "height": 720},
    )

    assert "A11yway Focus Path Overlay" in html
    assert "Download guide" in html
    assert "Marker numbers show the Tab order" in html
    assert "left: 20.0px" in html


def test_save_focus_overlay_html_writes_file(tmp_path: Path) -> None:
    """The overlay writer should create parent directories."""
    output_path = tmp_path / "visual" / "focus_path.html"

    save_focus_overlay_html(
        "page.png",
        [{"step": 1, "tag": "button", "x": 10, "y": 12}],
        output_path,
    )

    assert output_path.exists()
    assert "Focus Path Overlay" in output_path.read_text(encoding="utf-8")


@pytest.mark.skipif(not is_playwright_available(), reason="Playwright is not installed")
def test_browser_visual_proof_generates_artifacts(tmp_path: Path) -> None:
    """Browser visual proof should produce a screenshot and overlay when available."""
    visual_dir = tmp_path / "visual"

    result = run_browser_audit(
        "examples/sample_task_execution_form.html",
        visual_proof_dir=visual_dir,
    )

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    visual_proof = result["visual_proof"]
    assert visual_proof["enabled"] is True
    assert (visual_dir / "page.png").exists()
    assert (visual_dir / "focus_path.html").exists()
    assert visual_proof["focus_points_count"] == len(result["focus_trace"])


def test_cli_html_writes_report(tmp_path: Path, capsys) -> None:
    """--html should write an HTML report without requiring browser mode."""
    html_path = tmp_path / "sample_form_report.html"

    exit_code = main(["examples/sample_form.html", "--html", str(html_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "HTML report saved" in captured.out
    assert html_path.exists()
    assert "A11yway Accessibility Report" in html_path.read_text(encoding="utf-8")


def test_cli_visual_proof_requires_browser(capsys) -> None:
    """Visual proof should fail clearly without --browser."""
    exit_code = main(["examples/sample_form.html", "--visual-proof", "reports/visual"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Visual proof requires browser mode" in captured.out


def test_batch_html_reports_add_index_and_csv_columns(tmp_path: Path) -> None:
    """Batch HTML report mode should add report paths to index and CSV."""
    out_dir = tmp_path / "batch"

    result = run_batch("examples/sample_batch.json", out_dir, html_reports=True)

    index = result["index"]
    assert index["summary"]["html_reports"] == 2
    for item in index["sources"]:
        assert item["reports"]["html"].endswith(".html")
        assert Path(item["reports"]["html"]).exists()

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert "html_report" in rows[0]
    assert rows[0]["html_report"].endswith(".html")


def test_batch_html_reports_are_reflected_in_index_json(tmp_path: Path) -> None:
    """Saved index JSON should include the HTML report paths."""
    out_dir = tmp_path / "batch"

    run_batch("examples/sample_batch.json", out_dir, html_reports=True)

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
    assert index["summary"]["html_reports"] == 2
    assert index["sources"][0]["reports"]["html"].endswith(".html")
