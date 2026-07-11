"""Tests for the new low-vision decision logic and browser checks.

Decision functions are pure and tested without a browser; a few integration
tests run headless Chromium when Playwright is available (like the existing
zoom-reflow tests).
"""

import pytest

from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.low_vision_audit import (
    _contrast_issues,
    _focus_indicator_visible,
    _focus_obscured_issue,
    _overflow_is_intentional,
    _target_size_issues,
    _text_spacing_issues,
    run_low_vision_audit_for_source,
)

requires_browser = pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)


def issue_types(issues: list) -> set[str]:
    return {issue.issue_type for issue in issues}


# --- contrast: unresolved backgrounds become needs_review ---


def _sample(**overrides) -> dict:
    sample = {
        "tag": "p",
        "selector": "p.intro",
        "text": "hello",
        "color": "rgb(120, 120, 120)",
        "background_color": "rgb(255, 255, 255)",
        "background_resolved": True,
        "background_image_in_stack": False,
        "disabled": False,
        "opacity": "1",
    }
    sample.update(overrides)
    return sample


def test_resolved_low_contrast_is_flagged_as_likely_failure() -> None:
    issues = _contrast_issues([_sample()])
    assert issue_types(issues) == {"low_contrast_text"}


def test_unresolved_background_becomes_needs_review() -> None:
    issues = _contrast_issues(
        [_sample(background_resolved=False, background_image_in_stack=True)]
    )
    assert issue_types(issues) == {"contrast_unresolved_background"}
    assert issues[0].severity == "medium"


def test_unresolved_background_with_passing_computable_part_is_skipped() -> None:
    issues = _contrast_issues(
        [
            _sample(
                color="rgb(0, 0, 0)",
                background_resolved=False,
                background_image_in_stack=True,
            )
        ]
    )
    assert issues == []


def test_disabled_control_is_exempt_from_contrast() -> None:
    assert _contrast_issues([_sample(tag="button", disabled=True)]) == []


def test_translucent_element_opacity_is_unresolved() -> None:
    issues = _contrast_issues([_sample(opacity="0.6")])
    assert issue_types(issues) == {"contrast_unresolved_background"}


# --- reflow: intentional scroll regions ---


def test_overflow_from_data_table_only_is_intentional() -> None:
    level = {
        "overflow_amount": 300,
        "overflow_sources": [
            {"tag": "table", "allowed_scroll_region": True},
            {"tag": "td", "allowed_scroll_region": True},
        ],
    }
    assert _overflow_is_intentional(level)


def test_overflow_from_broken_layout_is_not_intentional() -> None:
    level = {
        "overflow_amount": 300,
        "overflow_sources": [
            {"tag": "table", "allowed_scroll_region": True},
            {"tag": "div", "allowed_scroll_region": False},
        ],
    }
    assert not _overflow_is_intentional(level)


def test_overflow_without_source_attribution_is_not_intentional() -> None:
    """When attribution failed, stay on the reporting side."""
    assert not _overflow_is_intentional({"overflow_amount": 300, "overflow_sources": []})


# --- focus indicator: style comparison ---


def test_style_difference_counts_as_visible_focus() -> None:
    visible, method = _focus_indicator_visible(
        {
            "comparison_available": True,
            "focus_style_differences": [
                {"scope": "self", "property": "boxShadow", "focused": "x", "unfocused": "none"}
            ],
        }
    )
    assert visible and method == "style_comparison"


def test_no_style_difference_flags_missing_indicator() -> None:
    visible, method = _focus_indicator_visible(
        {"comparison_available": True, "focus_style_differences": []}
    )
    assert not visible and method == "style_comparison"


def test_fallback_heuristic_used_when_comparison_unavailable() -> None:
    visible, method = _focus_indicator_visible(
        {
            "comparison_available": False,
            "outline_style": "solid",
            "outline_width": "2px",
        }
    )
    assert visible and method == "heuristic_fallback"


# --- focus obscured ---


def _stop(covered: int, total: int = 5, in_viewport: bool = True) -> dict:
    return {
        "step": 3,
        "tag": "a",
        "id": "buy",
        "text": "Buy now",
        "obscured": {
            "in_viewport": in_viewport,
            "sampled_points": total,
            "covered_points": covered,
            "covering_element": "header.sticky",
            "covering_position": "sticky",
            "bounding_box": {"x": 0, "y": 0, "width": 100, "height": 30},
        },
    }


def test_fully_covered_focus_is_high_and_likely() -> None:
    issue = _focus_obscured_issue(_stop(covered=5))
    assert issue is not None
    assert issue.issue_type == "focus_obscured"
    assert issue.severity == "high"
    assert issue.confidence == "likely"


def test_partially_covered_focus_is_review_only() -> None:
    issue = _focus_obscured_issue(_stop(covered=2))
    assert issue is not None
    assert issue.severity == "medium"
    assert issue.confidence == "needs_review"


def test_uncovered_focus_produces_no_finding() -> None:
    assert _focus_obscured_issue(_stop(covered=0)) is None


def test_offscreen_element_is_not_judged() -> None:
    assert _focus_obscured_issue(_stop(covered=5, in_viewport=False)) is None


# --- target size (2.5.8) ---


def _target(x: float, y: float, width: float, height: float, **extra) -> dict:
    return {
        "tag": "button",
        "id": "",
        "text": "x",
        "inline_text_link": False,
        "box": {"x": x, "y": y, "width": width, "height": height},
        **extra,
    }


def test_small_crowded_target_is_flagged_with_dimensions() -> None:
    issues = _target_size_issues(
        [_target(0, 0, 16, 16), _target(18, 0, 16, 16)]
    )
    assert issue_types(issues) == {"small_target_size"}
    evidence = issues[0].evidence
    assert evidence["width"] == 16 and evidence["height"] == 16
    assert evidence["nearby_target"]


def test_small_but_spaced_target_uses_spacing_exception() -> None:
    issues = _target_size_issues(
        [_target(0, 0, 16, 16), _target(200, 200, 16, 16)]
    )
    assert issues == []


def test_inline_text_link_is_exempt() -> None:
    issues = _target_size_issues(
        [
            _target(0, 0, 16, 16, tag="a", inline_text_link=True),
            _target(20, 0, 16, 16, tag="a", inline_text_link=True),
        ]
    )
    assert issues == []


def test_adequately_sized_targets_pass() -> None:
    issues = _target_size_issues(
        [_target(0, 0, 24, 24), _target(25, 0, 24, 24)]
    )
    assert issues == []


# --- text spacing (1.4.12) ---


def test_new_clipping_after_overrides_is_flagged_with_boxes() -> None:
    before = {"clipped": [], "overlaps": []}
    after = {
        "clipped": [
            {
                "label": 'div "Terms"',
                "box": {"x": 0, "y": 0, "width": 200, "height": 40},
                "scroll_height": 90,
                "client_height": 40,
                "direction": "vertical",
            }
        ],
        "overlaps": [],
    }
    issues = _text_spacing_issues(before, after)
    assert issue_types(issues) == {"text_spacing_content_loss"}
    assert issues[0].evidence["bounding_box_after"]["height"] == 40


def test_preexisting_clipping_is_not_a_spacing_regression() -> None:
    measurement = {
        "clipped": [
            {"label": 'div "Terms"', "box": {}, "direction": "vertical"}
        ],
        "overlaps": [],
    }
    assert _text_spacing_issues(measurement, measurement) == []


def test_new_overlap_after_overrides_is_flagged() -> None:
    before = {"clipped": [], "overlaps": []}
    after = {
        "clipped": [],
        "overlaps": [
            {
                "first": "button#a",
                "first_box": {"x": 0, "y": 0, "width": 50, "height": 20},
                "second": "button#b",
                "second_box": {"x": 10, "y": 5, "width": 50, "height": 20},
            }
        ],
    }
    issues = _text_spacing_issues(before, after)
    assert len(issues) == 1
    assert issues[0].evidence["first_element"] == "button#a"


# --- browser integration (headless Chromium) ---


@requires_browser
def test_browser_flags_missing_focus_indicator_and_passes_custom_style(tmp_path) -> None:
    page = tmp_path / "focus.html"
    page.write_text(
        """
        <html lang="en"><head><title>Focus</title><style>
          a, button { outline: none; }
          #styled:focus { box-shadow: 0 0 0 3px #1a4a8a; }
        </style></head><body>
        <h1>Focus test</h1>
        <p><a id="bare" href="/a">Bare link with removed outline</a></p>
        <p><button id="styled">Styled focus button</button></p>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = run_low_vision_audit_for_source(page.as_posix())
    assert result["success"], result.get("error")
    flagged = [
        issue.evidence.get("id")
        for issue in result["issues"]
        if issue.issue_type == "focus_indicator_missing"
    ]
    assert "bare" in flagged
    assert "styled" not in flagged


@requires_browser
def test_browser_detects_focus_obscured_by_fixed_overlay(tmp_path) -> None:
    page = tmp_path / "obscured.html"
    page.write_text(
        """
        <html lang="en"><head><title>Obscured</title><style>
          #banner { position: fixed; top: 0; left: 0; right: 0; height: 120px;
                    background: #333; z-index: 10; }
          #covered { position: absolute; top: 30px; left: 10px; }
        </style></head><body>
        <h1 style="margin-top: 140px">Overlay test</h1>
        <a id="covered" href="/x">Covered link</a>
        <p><a id="clear" href="/y" style="display:block; margin-top: 200px">Clear link</a></p>
        <div id="banner">Cookie banner</div>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = run_low_vision_audit_for_source(page.as_posix())
    assert result["success"], result.get("error")
    obscured_ids = [
        issue.evidence.get("id")
        for issue in result["issues"]
        if issue.issue_type == "focus_obscured"
    ]
    assert "covered" in obscured_ids
    assert "clear" not in obscured_ids


@requires_browser
def test_browser_ignores_reflow_overflow_from_data_table(tmp_path) -> None:
    page = tmp_path / "table.html"
    page.write_text(
        """
        <html lang="en"><head><title>Wide table</title></head><body>
        <h1>Schedule</h1>
        <table><tr>"""
        + "".join(f"<th style='min-width:120px'>Col {i}</th>" for i in range(12))
        + "</tr><tr>"
        + "".join(f"<td style='min-width:120px'>v{i}</td>" for i in range(12))
        + """</tr></table>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = run_low_vision_audit_for_source(page.as_posix())
    assert result["success"], result.get("error")
    assert "reflow_horizontal_scroll" not in issue_types(result["issues"])


@requires_browser
def test_browser_detects_text_spacing_content_loss(tmp_path) -> None:
    page = tmp_path / "spacing.html"
    page.write_text(
        """
        <html lang="en"><head><title>Spacing</title><style>
          /* Three 16px lines at line-height 1.0 (48px) fit inside 52px, so
             nothing clips at normal spacing; the 1.5 line-height override
             needs 72px and clips. */
          #tight { height: 52px; overflow: hidden; line-height: 1.0;
                   width: 400px; font-size: 16px; }
        </style></head><body>
        <h1>Spacing test</h1>
        <div id="tight">Agreement line one.<br>Agreement line two.<br>Agreement line three.</div>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = run_low_vision_audit_for_source(page.as_posix())
    assert result["success"], result.get("error")
    assert "text_spacing_content_loss" in issue_types(result["issues"])
