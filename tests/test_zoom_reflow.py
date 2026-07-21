





from pathlib import Path

import pytest

from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.low_vision_audit import (
    ZOOM_BASE_VIEWPORT,
    ZOOM_LEVELS,
    _reflow_issues,
    run_low_vision_audit_for_source,
)
from a11yway.core.report_builder import (
    build_html_report,
    build_json_report,
    build_markdown_report,
)
from a11yway.core.rules import get_rule


def level(zoom_percent: int, **overrides) -> dict:

    data = {
        "zoom_percent": zoom_percent,
        "viewport_width": int(ZOOM_BASE_VIEWPORT["width"] / (zoom_percent / 100)),
        "document_scroll_width": int(
            ZOOM_BASE_VIEWPORT["width"] / (zoom_percent / 100)
        ),
        "overflow_amount": 0,
        "clipped_elements": [],
        "overlapping_pairs": [],
    }
    data.update(overrides)
    return data


def test_zoom_levels_match_the_wcag_reference() -> None:

    assert ZOOM_LEVELS == [200, 400]
    assert int(ZOOM_BASE_VIEWPORT["width"] / 4) == 320


@pytest.mark.parametrize(
    "issue_type",
    ["reflow_horizontal_scroll", "reflow_clipped_content", "reflow_overlap"],
)
def test_reflow_rules_exist(issue_type: str) -> None:

    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Low Vision"
    assert rule["browser_check_limitations"]
    assert "1.4.10" in rule["standard_hint"]


def test_horizontal_scroll_at_400_without_content_loss_is_review_only() -> None:

    issues = _reflow_issues(
        [
            level(200, overflow_amount=260, document_scroll_width=900),
            level(400, overflow_amount=580, document_scroll_width=900),
        ]
    )

    scroll = [i for i in issues if i.issue_type == "reflow_horizontal_scroll"]
    assert len(scroll) == 1
    assert scroll[0].severity == "medium"
    assert scroll[0].confidence == "needs_review"
    zoom_levels = scroll[0].evidence["zoom_levels"]
    assert [entry["zoom_percent"] for entry in zoom_levels] == [200, 400]


def test_horizontal_scroll_with_content_loss_is_high_severity() -> None:

    issues = _reflow_issues(
        [
            level(200, overflow_amount=260, document_scroll_width=900),
            level(
                400,
                overflow_amount=580,
                document_scroll_width=900,
                clipped_elements=[
                    {
                        "tag": "p",
                        "id": "",
                        "text": "Long label",
                        "box": {"x": 700, "y": 100, "width": 260, "height": 20},
                        "clipped_by": "document",
                    }
                ],
            ),
        ]
    )

    scroll = [i for i in issues if i.issue_type == "reflow_horizontal_scroll"]
    assert len(scroll) == 1
    assert scroll[0].severity == "high"


def test_small_horizontal_overflow_is_treated_as_noise() -> None:

    issues = _reflow_issues(
        [level(400, overflow_amount=20, document_scroll_width=340)]
    )

    assert [issue.issue_type for issue in issues] == []


def test_horizontal_scroll_only_at_200_is_medium() -> None:

    issues = _reflow_issues(
        [
            level(200, overflow_amount=60, document_scroll_width=700),
            level(400),
        ]
    )

    scroll = [i for i in issues if i.issue_type == "reflow_horizontal_scroll"]
    assert len(scroll) == 1
    assert scroll[0].severity == "medium"


def test_no_overflow_produces_no_scroll_finding() -> None:

    issues = _reflow_issues([level(200), level(400)])

    assert issues == []


def test_clipped_and_overlap_findings_carry_boxes_and_zoom() -> None:

    clipped = {
        "tag": "p",
        "id": "",
        "text": "Bring your student card",
        "box": {"x": 700, "y": 100, "width": 260, "height": 20},
        "clipped_by": "document",
    }
    pair = {
        "first": {
            "tag": "button",
            "id": "",
            "text": "Print timetable",
            "box": {"x": 0, "y": 200, "width": 200, "height": 30},
        },
        "second": {
            "tag": "button",
            "id": "",
            "text": "Download timetable",
            "box": {"x": 120, "y": 200, "width": 200, "height": 30},
        },
    }
    issues = _reflow_issues(
        [
            level(200),
            level(400, clipped_elements=[clipped], overlapping_pairs=[pair]),
        ]
    )

    types = {issue.issue_type for issue in issues}
    assert types == {"reflow_clipped_content", "reflow_overlap"}
    clipped_issue = next(
        i for i in issues if i.issue_type == "reflow_clipped_content"
    )
    assert clipped_issue.severity == "high"
    assert clipped_issue.evidence["zoom_percent"] == 400
    assert clipped_issue.evidence["bounding_box"]["width"] == 260
    overlap_issue = next(i for i in issues if i.issue_type == "reflow_overlap")
    assert overlap_issue.evidence["first_bounding_box"]
    assert overlap_issue.evidence["second_bounding_box"]


def test_clipped_elements_are_deduped_across_levels() -> None:

    clipped = {
        "tag": "p",
        "id": "note",
        "text": "Bring your student card",
        "box": {"x": 700, "y": 100, "width": 260, "height": 20},
        "clipped_by": "container",
    }
    issues = _reflow_issues(
        [
            level(200, clipped_elements=[dict(clipped)]),
            level(400, clipped_elements=[dict(clipped)]),
        ]
    )

    assert len([i for i in issues if i.issue_type == "reflow_clipped_content"]) == 1


def test_reports_render_zoom_level_table() -> None:

    low_vision_result = {
        "success": True,
        "error": None,
        "checks_run": ["zoom_reflow_200_400"],
        "contrast_samples": [],
        "zoom_reflow": {
            "method": "browser_zoom_equivalent_viewports",
            "base_viewport": dict(ZOOM_BASE_VIEWPORT),
            "levels": [
                level(200, overflow_amount=260, document_scroll_width=900),
                level(400, overflow_amount=580, document_scroll_width=900),
            ],
            "viewport_width": 320,
            "document_scroll_width": 900,
            "overflow_amount": 580,
        },
        "focus_visibility": {"checked_count": 3, "flagged_count": 0},
        "limitations": [],
    }
    report = build_json_report(
        "examples/sample_zoom_reflow.html", [], low_vision_result=low_vision_result
    )

    markdown = build_markdown_report(report)
    html = build_html_report(report)

    assert "### Zoom Reflow Levels" in markdown
    assert "| 200% | 640 | 900 | 260 | 0 | 0 |" in markdown
    assert "| 400% | 320 | 900 | 580 | 0 | 0 |" in markdown
    assert "<h3>Zoom Reflow Levels</h3>" in html
    assert "<td>400%</td>" in html


def test_zoom_reflow_example_pages_exist() -> None:

    assert Path("examples/sample_zoom_reflow.html").exists()
    assert Path("examples/sample_zoom_reflow_fixed.html").exists()


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_zoom_checks_flag_the_broken_sample() -> None:

    result = run_low_vision_audit_for_source("examples/sample_zoom_reflow.html")

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    issue_types = {issue.issue_type for issue in result["issues"]}
    assert "reflow_horizontal_scroll" in issue_types
    assert "reflow_clipped_content" in issue_types
    assert "reflow_overlap" in issue_types

    levels = result["zoom_reflow"]["levels"]
    assert [entry["zoom_percent"] for entry in levels] == [200, 400]
    assert levels[1]["viewport_width"] == 320


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_zoom_checks_pass_the_fixed_sample() -> None:

    result = run_low_vision_audit_for_source(
        "examples/sample_zoom_reflow_fixed.html"
    )

    if not result["success"]:
        pytest.skip(f"Browser could not run: {result['error']}")

    issue_types = {issue.issue_type for issue in result["issues"]}
    assert not issue_types & {
        "reflow_horizontal_scroll",
        "reflow_clipped_content",
        "reflow_overlap",
    }
