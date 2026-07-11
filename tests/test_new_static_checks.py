"""Tests for the WCAG 2.2 static checks added to the page analyzer.

Each rule gets at least: one true positive, one clean pass, one known
exception, and (where relevant) an ambiguity/review-only case.
"""

from pathlib import Path

from a11yway.core.page_analyzer import (
    analyze_bypass_blocks,
    analyze_html_static,
    analyze_input_purposes,
    analyze_label_in_name,
    analyze_sensory_instructions,
    analyze_structure_relationships,
    analyze_wcag_static_evidence,
)


def issue_types(issues: list) -> set[str]:
    return {issue.issue_type for issue in issues}


def wrap(body: str) -> str:
    return f'<html lang="en"><head><title>T</title></head><body>{body}</body></html>'


# --- radio_group_missing_fieldset (1.3.1) ---

RADIOS = (
    '<input type="radio" name="plan" id="a"><label for="a">A</label>'
    '<input type="radio" name="plan" id="b"><label for="b">B</label>'
)


def test_radio_group_without_fieldset_is_flagged() -> None:
    issues = analyze_structure_relationships(wrap(f"<form>{RADIOS}</form>"))
    assert "radio_group_missing_fieldset" in issue_types(issues)


def test_radio_group_with_fieldset_legend_passes() -> None:
    html = wrap(f"<form><fieldset><legend>Plan</legend>{RADIOS}</fieldset></form>")
    assert "radio_group_missing_fieldset" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_radio_group_with_named_radiogroup_role_passes() -> None:
    html = wrap(f'<form><div role="radiogroup" aria-label="Plan">{RADIOS}</div></form>')
    assert "radio_group_missing_fieldset" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_single_radio_is_not_a_group() -> None:
    html = wrap('<form><input type="radio" name="only" id="o"><label for="o">O</label></form>')
    assert "radio_group_missing_fieldset" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_fieldset_without_legend_still_flags() -> None:
    """A fieldset alone does not name the group; a legend is required."""
    html = wrap(f"<form><fieldset>{RADIOS}</fieldset></form>")
    assert "radio_group_missing_fieldset" in issue_types(
        analyze_structure_relationships(html)
    )


# --- table_missing_headers (1.3.1) ---

DATA_ROWS = (
    "<tr><td>Mon</td><td>9:00</td></tr>"
    "<tr><td>Tue</td><td>10:00</td></tr>"
)


def test_data_table_without_headers_is_flagged() -> None:
    issues = analyze_structure_relationships(wrap(f"<table>{DATA_ROWS}</table>"))
    assert "table_missing_headers" in issue_types(issues)


def test_table_with_th_passes() -> None:
    html = wrap(f"<table><tr><th>Day</th><th>Opens</th></tr>{DATA_ROWS}</table>")
    assert "table_missing_headers" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_presentation_table_is_exempt() -> None:
    html = wrap(f'<table role="presentation">{DATA_ROWS}</table>')
    assert "table_missing_headers" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_single_column_table_is_not_flagged() -> None:
    """One-column tables are usually layout or lists; too ambiguous."""
    html = wrap("<table><tr><td>a</td></tr><tr><td>b</td></tr></table>")
    assert "table_missing_headers" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_headers_attribute_association_passes() -> None:
    html = wrap(
        '<table><tr><td headers="h1">Mon</td><td headers="h2">9:00</td></tr>'
        f"{DATA_ROWS}</table>"
    )
    assert "table_missing_headers" not in issue_types(
        analyze_structure_relationships(html)
    )


# --- visual_required_not_programmatic (1.3.1 / 3.3.2) ---


def test_visual_required_marker_without_required_attr_is_flagged() -> None:
    html = wrap('<form><label for="n">Name *</label><input type="text" id="n"></form>')
    issues = analyze_structure_relationships(html)
    assert "visual_required_not_programmatic" in issue_types(issues)


def test_required_attr_satisfies_marker() -> None:
    html = wrap('<form><label for="n">Name *</label><input type="text" id="n" required></form>')
    assert "visual_required_not_programmatic" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_aria_required_satisfies_marker() -> None:
    html = wrap(
        '<form><label for="n">Name (required)</label>'
        '<input type="text" id="n" aria-required="true"></form>'
    )
    assert "visual_required_not_programmatic" not in issue_types(
        analyze_structure_relationships(html)
    )


def test_not_required_label_is_exempt() -> None:
    """Labels saying 'not required' or 'optional' must not match."""
    html = wrap('<form><label for="n">Nickname (not required)</label><input type="text" id="n"></form>')
    assert "visual_required_not_programmatic" not in issue_types(
        analyze_structure_relationships(html)
    )


# --- fake_heading (1.3.1, review-only) ---


def test_large_bold_styled_div_is_flagged_for_review() -> None:
    html = wrap('<div style="font-size: 28px; font-weight: bold;">Section title</div>')
    issues = [
        issue
        for issue in analyze_structure_relationships(html)
        if issue.issue_type == "fake_heading"
    ]
    assert len(issues) == 1
    assert issues[0].severity == "low"


def test_real_heading_is_not_flagged() -> None:
    html = wrap('<h2 style="font-size: 28px; font-weight: bold;">Section title</h2>')
    assert "fake_heading" not in issue_types(analyze_structure_relationships(html))


def test_div_with_heading_role_is_exempt() -> None:
    html = wrap(
        '<div role="heading" aria-level="2" style="font-size: 28px; '
        'font-weight: bold;">Section title</div>'
    )
    assert "fake_heading" not in issue_types(analyze_structure_relationships(html))


def test_long_bold_paragraph_text_is_ambiguous_and_skipped() -> None:
    """Long decorated text is likely a callout, not a heading."""
    long_text = "word " * 40
    html = wrap(f'<div style="font-size: 28px; font-weight: bold;">{long_text}</div>')
    assert "fake_heading" not in issue_types(analyze_structure_relationships(html))


# --- sensory_instruction (1.3.3, review-only) ---


def test_click_the_red_button_is_flagged_for_review() -> None:
    html = wrap("<p>Click the red button to continue.</p>")
    issues = [
        issue
        for issue in analyze_sensory_instructions(html)
        if issue.issue_type == "sensory_instruction"
    ]
    assert len(issues) == 1
    assert issues[0].severity == "low"
    assert "matched_phrase" in issues[0].evidence


def test_box_on_the_right_is_flagged_for_review() -> None:
    html = wrap("<p>Use the box on the right to search.</p>")
    assert "sensory_instruction" in issue_types(analyze_sensory_instructions(html))


def test_listen_for_the_beep_is_flagged_for_review() -> None:
    html = wrap("<li>Listen for the beep before speaking.</li>")
    assert "sensory_instruction" in issue_types(analyze_sensory_instructions(html))


def test_plain_instruction_passes() -> None:
    html = wrap("<p>Select Submit application to continue.</p>")
    assert analyze_sensory_instructions(html) == []


def test_color_mention_without_instruction_verb_is_not_flagged() -> None:
    """Descriptive prose about colors is not an instruction."""
    html = wrap("<p>Our logo features a red circle above a blue box of text.</p>")
    assert analyze_sensory_instructions(html) == []


# --- missing_autocomplete (1.3.5) ---


def test_email_input_without_autocomplete_is_flagged() -> None:
    html = wrap('<form><label for="e">Email</label><input type="email" id="e"></form>')
    issues = analyze_input_purposes(html)
    assert issue_types(issues) == {"missing_autocomplete"}
    assert issues[0].evidence["suggested_token"] == "email"


def test_name_field_inferred_from_label() -> None:
    html = wrap('<form><label for="f">First name</label><input type="text" id="f"></form>')
    issues = analyze_input_purposes(html)
    assert issues and issues[0].evidence["suggested_token"] == "given-name"


def test_autocomplete_present_passes() -> None:
    html = wrap('<form><label for="e">Email</label><input type="email" id="e" autocomplete="email"></form>')
    assert analyze_input_purposes(html) == []


def test_search_box_is_exempt() -> None:
    html = wrap('<form><label for="q">Search</label><input type="search" id="q" name="q"></form>')
    assert analyze_input_purposes(html) == []


def test_one_time_code_is_exempt() -> None:
    html = wrap('<form><label for="otp">One-time code</label><input type="text" id="otp" name="otp_code"></form>')
    assert analyze_input_purposes(html) == []


def test_ambiguous_text_field_is_skipped() -> None:
    """A field whose purpose cannot be inferred confidently is not flagged."""
    html = wrap('<form><label for="x">Project reference</label><input type="text" id="x"></form>')
    assert analyze_input_purposes(html) == []


def test_generic_password_field_is_skipped_but_new_password_is_flagged() -> None:
    ambiguous = wrap('<form><label for="p">Password</label><input type="password" id="p"></form>')
    assert analyze_input_purposes(ambiguous) == []

    new = wrap('<form><label for="p">Create new password</label><input type="password" id="p"></form>')
    issues = analyze_input_purposes(new)
    assert issues and issues[0].evidence["suggested_token"] == "new-password"


def test_input_outside_form_is_skipped() -> None:
    html = wrap('<label for="e">Email</label><input type="email" id="e">')
    assert analyze_input_purposes(html) == []


# --- no_bypass_mechanism (2.4.1) ---

NAV_LINKS = "".join(f'<a href="/p{i}">Page {i}</a>' for i in range(6))
BODY_LINKS = "".join(f'<a href="/d{i}">Doc {i}</a>' for i in range(6))


def _bypass_page(prefix: str = "", main_tag: str = "div", headings: str = "") -> str:
    return (
        '<html lang="en"><head><title>T</title></head><body>'
        f"{prefix}<nav>{NAV_LINKS}</nav>{headings}"
        f"<{main_tag}><p>content</p>{BODY_LINKS}</{main_tag}></body></html>"
    )


def test_repeated_nav_without_bypass_is_flagged() -> None:
    issues = analyze_bypass_blocks(_bypass_page())
    assert issue_types(issues) == {"no_bypass_mechanism"}


def test_skip_link_satisfies_bypass() -> None:
    html = _bypass_page(prefix='<a href="#main">Skip to main content</a>')
    assert analyze_bypass_blocks(html) == []


def test_main_landmark_satisfies_bypass() -> None:
    assert analyze_bypass_blocks(_bypass_page(main_tag="main")) == []


def test_heading_structure_counts_as_bypass_mechanism() -> None:
    html = _bypass_page(headings="<h1>Title</h1><h2>Section</h2>")
    assert analyze_bypass_blocks(html) == []


def test_small_page_without_repeated_blocks_is_not_flagged() -> None:
    html = wrap('<nav><a href="/a">A</a></nav><p>tiny page</p>')
    assert analyze_bypass_blocks(html) == []


# --- label_in_name_mismatch (2.5.3) ---


def test_aria_label_missing_visible_text_is_flagged() -> None:
    html = wrap('<button aria-label="Close dialog">Save draft</button>')
    issues = analyze_label_in_name(html)
    assert issue_types(issues) == {"label_in_name_mismatch"}


def test_aria_label_containing_visible_text_passes() -> None:
    """Exact equality is not required; containment after normalization is."""
    html = wrap('<a href="/g" aria-label="Learn more about scholarships">Learn More!</a>')
    assert analyze_label_in_name(html) == []


def test_icon_only_control_is_exempt() -> None:
    html = wrap('<button aria-label="Search">&#128269;</button>')
    assert analyze_label_in_name(html) == []


def test_punctuation_and_case_are_normalized() -> None:
    html = wrap('<button aria-label="submit application now">Submit, Application</button>')
    assert analyze_label_in_name(html) == []


def test_input_button_value_is_compared() -> None:
    html = wrap('<form><input type="submit" value="Send request" aria-label="Deliver form"></form>')
    assert issue_types(analyze_label_in_name(html)) == {"label_in_name_mismatch"}


# --- fixtures ---


def test_seeded_structure_sample_reports_all_new_checks() -> None:
    html = Path("examples/sample_wcag_structure.html").read_text(encoding="utf-8")
    types = issue_types(analyze_html_static(html))
    assert {
        "radio_group_missing_fieldset",
        "table_missing_headers",
        "visual_required_not_programmatic",
        "fake_heading",
        "sensory_instruction",
        "missing_autocomplete",
        "label_in_name_mismatch",
    } <= types


def test_clean_structure_sample_passes_new_checks() -> None:
    html = Path("examples/sample_wcag_structure_clean.html").read_text(encoding="utf-8")
    types = issue_types(analyze_html_static(html))
    assert not (
        {
            "radio_group_missing_fieldset",
            "table_missing_headers",
            "visual_required_not_programmatic",
            "fake_heading",
            "sensory_instruction",
            "missing_autocomplete",
            "label_in_name_mismatch",
            "no_bypass_mechanism",
        }
        & types
    )


# --- additional WCAG static evidence checks ---


def wcag_types(html: str) -> set[str]:
    return issue_types(analyze_wcag_static_evidence(wrap(html)))


def test_meaningful_sequence_css_order_is_review_evidence() -> None:
    assert "meaningful_sequence_reorder" in wcag_types(
        '<div style="display:flex"><p style="order:2">First in DOM</p></div>'
    )
    assert "meaningful_sequence_reorder" not in wcag_types("<p>Normal order</p>")


def test_orientation_restriction_requires_restriction_evidence() -> None:
    assert "orientation_restriction" in wcag_types(
        "<p>Please rotate your device to landscape mode required.</p>"
    )
    assert "orientation_restriction" not in analyze_wcag_static_evidence(
        wrap("<p>Responsive layout</p><style>@media (orientation: portrait){body{font-size:1rem}}</style>")
    )


def test_color_only_indicator_exempts_textual_or_aria_cues() -> None:
    assert "color_only_indicator" in wcag_types('<span class="error"></span>')
    assert "color_only_indicator" not in wcag_types(
        '<span class="error" role="alert">Email is required</span>'
    )


def test_autoplay_audio_without_controls_is_flagged_but_controls_pass() -> None:
    assert "autoplay_audio_no_control" in wcag_types('<audio autoplay src="intro.mp3"></audio>')
    assert "autoplay_audio_no_control" not in wcag_types(
        '<audio autoplay controls src="intro.mp3"></audio>'
    )


def test_image_of_text_static_evidence_is_review_only() -> None:
    assert "image_of_text" in wcag_types('<svg><text>Sale ends today</text></svg>')
    assert "image_of_text" not in wcag_types('<img src="photo.jpg" alt="Student smiling">')


def test_hover_focus_content_detects_custom_reveals_not_title_only() -> None:
    assert "hover_focus_content" in wcag_types(
        '<button onfocus="showHelp()">Help</button><div role="tooltip">Details</div>'
    )
    assert "hover_focus_content" not in wcag_types('<button title="Native tip">Help</button>')


def test_single_character_shortcut_requires_unmodified_character_listener() -> None:
    assert "single_character_shortcut" in wcag_types(
        '<script>document.addEventListener("keydown", e => { if (e.key === "k") openMenu(); });</script>'
    )
    assert "single_character_shortcut" not in wcag_types(
        '<script>document.addEventListener("keydown", e => { if (e.ctrlKey && e.key === "k") openMenu(); });</script>'
    )


def test_timing_adjustable_detects_meta_refresh_without_extend_control() -> None:
    assert "timing_adjustable_missing" in wcag_types(
        '<meta http-equiv="refresh" content="20;url=/next"><p>Session expires soon</p>'
    )
    assert "timing_adjustable_missing" not in wcag_types(
        '<p>Session expires soon</p><button>Extend time</button>'
    )


def test_moving_content_no_pause_detects_carousel_exception_control() -> None:
    assert "moving_content_no_pause" in wcag_types('<div class="carousel auto-rotate">Slide</div>')
    assert "moving_content_no_pause" not in wcag_types(
        '<div class="carousel auto-rotate">Slide</div><button>Pause carousel</button>'
    )


def test_possible_flashing_content_requires_fast_flash_animation() -> None:
    assert "possible_flashing_content" in wcag_types(
        "<style>@keyframes flashWarn {from{opacity:1}to{opacity:0}} .x{animation: flashWarn 200ms infinite}</style>"
    )
    assert "possible_flashing_content" not in wcag_types(
        "<style>@keyframes fade {from{opacity:1}to{opacity:.8}} .x{animation-duration: 2s}</style>"
    )


def test_interaction_motion_exempts_reduced_motion_support() -> None:
    assert "interaction_motion_no_reduced_motion" in wcag_types(
        "<style>.card:hover{transform: scale(1.2)}</style>"
    )
    assert "interaction_motion_no_reduced_motion" not in wcag_types(
        "<style>@media (prefers-reduced-motion: reduce){.card{transition:none}} .card:hover{transform: scale(1.2)}</style>"
    )


def test_pointer_gesture_requires_no_obvious_simple_alternative() -> None:
    assert "pointer_gesture_no_alternative" in wcag_types(
        '<script>el.addEventListener("touchmove", swipeCard)</script>'
    )
    assert "pointer_gesture_no_alternative" not in wcag_types(
        '<script>el.addEventListener("touchmove", swipeCard)</script><button>Next</button>'
    )


def test_pointer_down_activation_exempts_pointer_up_cancel_code() -> None:
    assert "pointer_down_activation" in wcag_types('<button onmousedown="buyNow()">Buy</button>')
    assert "pointer_down_activation" not in wcag_types(
        '<button onmousedown="preview()" onmouseup="activate()" onmouseleave="cancel()">Buy</button>'
    )


def test_dragging_without_alternative_is_flagged() -> None:
    assert "dragging_no_alternative" in wcag_types('<div draggable="true">Drag card</div>')
    assert "dragging_no_alternative" not in wcag_types(
        '<div draggable="true">Drag card</div><button>Move up</button>'
    )


def test_focus_context_change_and_safe_focus_style() -> None:
    assert "focus_context_change" in wcag_types('<input onfocus="location.href=\'/next\'">')
    assert "focus_context_change" not in wcag_types('<input onfocus="this.classList.add(\'focus\')">')


def test_input_context_change_and_safe_local_update() -> None:
    assert "input_context_change" in wcag_types('<select onchange="location.href=this.value"><option>Next</option></select>')
    assert "input_context_change" not in wcag_types('<input oninput="preview.textContent=this.value">')


def test_error_identification_and_suggestion_evidence() -> None:
    types = wcag_types('<form><input id="email"><p class="error">Bad</p></form>')
    assert {"error_not_identified", "error_suggestion_missing"} <= types
    clean = wcag_types(
        '<form><input id="email" aria-invalid="true" aria-describedby="e">'
        '<p id="e" class="error">Enter an email like name@example.com</p></form>'
    )
    assert "error_not_identified" not in clean
    assert "error_suggestion_missing" not in clean
