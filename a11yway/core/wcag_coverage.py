




















from __future__ import annotations

import json
from pathlib import Path
from typing import Any


COVERAGE_LEVELS = ["direct", "partial", "supporting_evidence", "manual_only"]

_COVERAGE_RANK = {"direct": 3, "partial": 2, "supporting_evidence": 1}

DETECTION_MODES = [
    "static",
    "rendered_dom",
    "browser_interaction",
    "accessibility_tree",
    "low_vision",
    "task_execution",
    "axe_core",
]

CONFIDENCE_LEVELS = [
    "confirmed_by_multiple_engines",
    "repeat_verified",
    "strong",
    "likely",
    "needs_review",
    "weak_heuristic",
    "informational",
]



WCAG_2_2_CRITERIA: dict[str, dict[str, str]] = {
    "1.1.1": {"name": "Non-text Content", "level": "A"},
    "1.2.1": {"name": "Audio-only and Video-only (Prerecorded)", "level": "A"},
    "1.2.2": {"name": "Captions (Prerecorded)", "level": "A"},
    "1.2.3": {"name": "Audio Description or Media Alternative (Prerecorded)", "level": "A"},
    "1.2.4": {"name": "Captions (Live)", "level": "AA"},
    "1.2.5": {"name": "Audio Description (Prerecorded)", "level": "AA"},
    "1.2.6": {"name": "Sign Language (Prerecorded)", "level": "AAA"},
    "1.2.7": {"name": "Extended Audio Description (Prerecorded)", "level": "AAA"},
    "1.2.8": {"name": "Media Alternative (Prerecorded)", "level": "AAA"},
    "1.2.9": {"name": "Audio-only (Live)", "level": "AAA"},
    "1.3.1": {"name": "Info and Relationships", "level": "A"},
    "1.3.2": {"name": "Meaningful Sequence", "level": "A"},
    "1.3.3": {"name": "Sensory Characteristics", "level": "A"},
    "1.3.4": {"name": "Orientation", "level": "AA"},
    "1.3.5": {"name": "Identify Input Purpose", "level": "AA"},
    "1.3.6": {"name": "Identify Purpose", "level": "AAA"},
    "1.4.1": {"name": "Use of Color", "level": "A"},
    "1.4.2": {"name": "Audio Control", "level": "A"},
    "1.4.3": {"name": "Contrast (Minimum)", "level": "AA"},
    "1.4.4": {"name": "Resize Text", "level": "AA"},
    "1.4.5": {"name": "Images of Text", "level": "AA"},
    "1.4.6": {"name": "Contrast (Enhanced)", "level": "AAA"},
    "1.4.7": {"name": "Low or No Background Audio", "level": "AAA"},
    "1.4.8": {"name": "Visual Presentation", "level": "AAA"},
    "1.4.9": {"name": "Images of Text (No Exception)", "level": "AAA"},
    "1.4.10": {"name": "Reflow", "level": "AA"},
    "1.4.11": {"name": "Non-text Contrast", "level": "AA"},
    "1.4.12": {"name": "Text Spacing", "level": "AA"},
    "1.4.13": {"name": "Content on Hover or Focus", "level": "AA"},
    "2.1.1": {"name": "Keyboard", "level": "A"},
    "2.1.2": {"name": "No Keyboard Trap", "level": "A"},
    "2.1.3": {"name": "Keyboard (No Exception)", "level": "AAA"},
    "2.1.4": {"name": "Character Key Shortcuts", "level": "A"},
    "2.2.1": {"name": "Timing Adjustable", "level": "A"},
    "2.2.2": {"name": "Pause, Stop, Hide", "level": "A"},
    "2.2.3": {"name": "No Timing", "level": "AAA"},
    "2.2.4": {"name": "Interruptions", "level": "AAA"},
    "2.2.5": {"name": "Re-authenticating", "level": "AAA"},
    "2.2.6": {"name": "Timeouts", "level": "AAA"},
    "2.3.1": {"name": "Three Flashes or Below Threshold", "level": "A"},
    "2.3.2": {"name": "Three Flashes", "level": "AAA"},
    "2.3.3": {"name": "Animation from Interactions", "level": "AAA"},
    "2.4.1": {"name": "Bypass Blocks", "level": "A"},
    "2.4.2": {"name": "Page Titled", "level": "A"},
    "2.4.3": {"name": "Focus Order", "level": "A"},
    "2.4.4": {"name": "Link Purpose (In Context)", "level": "A"},
    "2.4.5": {"name": "Multiple Ways", "level": "AA"},
    "2.4.6": {"name": "Headings and Labels", "level": "AA"},
    "2.4.7": {"name": "Focus Visible", "level": "AA"},
    "2.4.8": {"name": "Location", "level": "AAA"},
    "2.4.9": {"name": "Link Purpose (Link Only)", "level": "AAA"},
    "2.4.10": {"name": "Section Headings", "level": "AAA"},
    "2.4.11": {"name": "Focus Not Obscured (Minimum)", "level": "AA"},
    "2.4.12": {"name": "Focus Not Obscured (Enhanced)", "level": "AAA"},
    "2.4.13": {"name": "Focus Appearance", "level": "AAA"},
    "2.5.1": {"name": "Pointer Gestures", "level": "A"},
    "2.5.2": {"name": "Pointer Cancellation", "level": "A"},
    "2.5.3": {"name": "Label in Name", "level": "A"},
    "2.5.4": {"name": "Motion Actuation", "level": "A"},
    "2.5.5": {"name": "Target Size (Enhanced)", "level": "AAA"},
    "2.5.6": {"name": "Concurrent Input Mechanisms", "level": "AAA"},
    "2.5.7": {"name": "Dragging Movements", "level": "AA"},
    "2.5.8": {"name": "Target Size (Minimum)", "level": "AA"},
    "3.1.1": {"name": "Language of Page", "level": "A"},
    "3.1.2": {"name": "Language of Parts", "level": "AA"},
    "3.1.3": {"name": "Unusual Words", "level": "AAA"},
    "3.1.4": {"name": "Abbreviations", "level": "AAA"},
    "3.1.5": {"name": "Reading Level", "level": "AAA"},
    "3.1.6": {"name": "Pronunciation", "level": "AAA"},
    "3.2.1": {"name": "On Focus", "level": "A"},
    "3.2.2": {"name": "On Input", "level": "A"},
    "3.2.3": {"name": "Consistent Navigation", "level": "AA"},
    "3.2.4": {"name": "Consistent Identification", "level": "AA"},
    "3.2.5": {"name": "Change on Request", "level": "AAA"},
    "3.2.6": {"name": "Consistent Help", "level": "A"},
    "3.3.1": {"name": "Error Identification", "level": "A"},
    "3.3.2": {"name": "Labels or Instructions", "level": "A"},
    "3.3.3": {"name": "Error Suggestion", "level": "AA"},
    "3.3.4": {"name": "Error Prevention (Legal, Financial, Data)", "level": "AA"},
    "3.3.5": {"name": "Help", "level": "AAA"},
    "3.3.6": {"name": "Error Prevention (All)", "level": "AAA"},
    "3.3.7": {"name": "Redundant Entry", "level": "A"},
    "3.3.8": {"name": "Accessible Authentication (Minimum)", "level": "AA"},
    "3.3.9": {"name": "Accessible Authentication (Enhanced)", "level": "AAA"},
    "4.1.2": {"name": "Name, Role, Value", "level": "A"},
    "4.1.3": {"name": "Status Messages", "level": "AA"},
}


def _mapping(
    sc: str,
    coverage: str,
    detection_mode: str,
    confidence: str,
    limitations: str,
    manual_check: str,
) -> dict[str, str]:

    return {
        "sc": sc,
        "name": WCAG_2_2_CRITERIA[sc]["name"],
        "level": WCAG_2_2_CRITERIA[sc]["level"],
        "coverage": coverage,
        "detection_mode": detection_mode,
        "confidence": confidence,
        "limitations": limitations,
        "manual_check": manual_check,
    }





RULE_WCAG_MAP: dict[str, list[dict[str, str]]] = {
    "missing_form_label": [
        _mapping(
            "3.3.2", "partial", "static", "likely",
            "Static HTML only; labels added by JavaScript are seen only in browser mode.",
            "Confirm the field has no visible or programmatic label in the final rendered page.",
        ),
        _mapping(
            "1.3.1", "partial", "static", "likely",
            "Only detects missing label association, not other relationship failures.",
            "Check whether a visually implied label exists that is not programmatically connected.",
        ),
        _mapping(
            "4.1.2", "supporting_evidence", "static", "likely",
            "A missing label usually means a missing accessible name, but the browser may compute one from other sources.",
            "Inspect the computed accessible name in browser dev tools.",
        ),
    ],
    "missing_button_name": [
        _mapping(
            "4.1.2", "partial", "static", "likely",
            "Static heuristic; icon fonts and JavaScript-injected names are invisible statically.",
            "Confirm the computed accessible name is empty in the rendered page.",
        ),
    ],
    "missing_link_name": [
        _mapping(
            "2.4.4", "partial", "static", "likely",
            "Only detects empty names, not misleading ones.",
            "Confirm the link announces nothing useful in a screen reader.",
        ),
        _mapping(
            "4.1.2", "partial", "static", "likely",
            "Static heuristic on source HTML.",
            "Confirm the computed accessible name is empty in the rendered page.",
        ),
    ],
    "generic_link_text": [
        _mapping(
            "2.4.4", "supporting_evidence", "static", "needs_review",
            "Generic visible text can still be acceptable when programmatic context (aria-labelledby, list context) disambiguates it.",
            "Listen to the link in a links list; judge whether its purpose is clear in context.",
        ),
    ],
    "missing_image_alt": [
        _mapping(
            "1.1.1", "partial", "static", "likely",
            "Cannot judge whether existing alt text is useful; decorative detection is heuristic.",
            "Decide whether the image is informative and whether the alternative conveys the same information.",
        ),
    ],
    "image_empty_alt_suspicious": [
        _mapping(
            "1.1.1", "supporting_evidence", "static", "needs_review",
            "Filename-based heuristic; an image named chart.png can still be decorative.",
            "Check whether the empty-alt image actually carries information a text alternative should convey.",
        ),
    ],
    "missing_h1": [
        _mapping(
            "1.3.1", "supporting_evidence", "static", "needs_review",
            "WCAG does not require an h1; this is structural review evidence.",
            "Judge whether the page structure is understandable without a main heading.",
        ),
        _mapping(
            "2.4.6", "supporting_evidence", "static", "needs_review",
            "Absence of an h1 is not itself a 2.4.6 failure.",
            "Judge whether existing headings describe their sections.",
        ),
    ],
    "skipped_heading_level": [
        _mapping(
            "1.3.1", "supporting_evidence", "static", "needs_review",
            "Skipped levels are not automatically WCAG failures; independent regions and embedded components can legitimately restart levels.",
            "Read the heading outline and judge whether relationships are conveyed.",
        ),
    ],
    "multiple_h1": [
        _mapping(
            "1.3.1", "supporting_evidence", "static", "informational",
            "Multiple h1 elements are valid HTML and often intentional; this is review evidence only.",
            "Judge whether multiple h1 headings make the main topic unclear when navigating by headings.",
        ),
    ],
    "missing_page_title": [
        _mapping(
            "2.4.2", "partial", "static", "likely",
            "Titles set by JavaScript are only visible in browser mode.",
            "Confirm the rendered page has no usable title.",
        ),
    ],
    "missing_html_lang": [
        _mapping(
            "3.1.1", "direct", "static", "likely",
            "Direct for static HTML; a lang attribute added by JavaScript would be missed in static mode.",
            "Confirm the rendered html element still has no lang attribute.",
        ),
    ],
    "missing_video_captions": [
        _mapping(
            "1.2.2", "partial", "static", "needs_review",
            "Only sees <track> elements; player-level, platform, or burned-in captions are invisible.",
            "Play the video and check for captions from the player or platform.",
        ),
    ],
    "missing_audio_transcript": [
        _mapping(
            "1.2.1", "supporting_evidence", "static", "needs_review",
            "The transcript search is a rough text heuristic; a transcript may exist on a linked page.",
            "Check whether a transcript is available and easy to find.",
        ),
    ],
    "missing_lang_indic": [
        _mapping(
            "3.1.1", "partial", "static", "likely",
            "Unicode-range script detection; languages sharing a script cannot be told apart.",
            "Confirm the actual language and add the right lang value.",
        ),
        _mapping(
            "3.1.2", "partial", "static", "likely",
            "Same script heuristic; transliterated text is invisible.",
            "Confirm each language passage carries a matching lang attribute.",
        ),
    ],
    "lang_mismatch": [
        _mapping(
            "3.1.2", "partial", "static", "likely",
            "Fires only when the script itself contradicts the declaration.",
            "Confirm the element's language and correct the lang attribute.",
        ),
    ],
    "mixed_script_element": [
        _mapping(
            "3.1.2", "supporting_evidence", "static", "needs_review",
            "Conservative heuristic; may flag intentional bilingual lines.",
            "Listen with a real screen reader to confirm the impact.",
        ),
    ],
    "browser_no_focusable_elements": [
        _mapping(
            "2.1.1", "partial", "browser_interaction", "likely",
            "Counts common focusable selectors in one Chromium run.",
            "Try the page with a real keyboard.",
        ),
    ],
    "browser_focus_not_moving": [
        _mapping(
            "2.1.1", "partial", "browser_interaction", "likely",
            "Headless Tab behavior can differ from a desktop browser session.",
            "Press Tab in a visible browser and confirm focus never enters the page.",
        ),
    ],
    "browser_repeated_focus": [
        _mapping(
            "2.1.2", "supporting_evidence", "browser_interaction", "needs_review",
            "Repeated focus suggests but does not prove a trap.",
            "Confirm by hand whether standard keys escape the widget.",
        ),
    ],
    "browser_focused_control_missing_name": [
        _mapping(
            "4.1.2", "partial", "browser_interaction", "likely",
            "Heuristic name estimate; only used when accessibility tree data is unavailable.",
            "Inspect the computed accessible name in browser dev tools.",
        ),
    ],
    "browser_focus_on_hidden_element": [
        _mapping(
            "2.4.3", "supporting_evidence", "browser_interaction", "needs_review",
            "Visibility is estimated from size and CSS; skip links that appear on focus are a valid pattern.",
            "Check whether the element becomes visible when focused.",
        ),
        _mapping(
            "2.4.7", "supporting_evidence", "browser_interaction", "needs_review",
            "An invisible focused element usually has no visible indicator, but the pattern needs human judgment.",
            "Tab to the element and look for any visible focus location.",
        ),
    ],
    "unnamed_focus_stop": [
        _mapping(
            "4.1.2", "partial", "accessibility_tree", "likely",
            "Chromium's computed tree in one run; real screen readers apply their own rules.",
            "Confirm with NVDA, JAWS, or VoiceOver what is actually announced.",
        ),
    ],
    "keyboard_trap": [
        _mapping(
            "2.1.2", "partial", "browser_interaction", "strong",
            "Observed Tab-only behavior; a documented escape mechanism (Escape, arrow keys) would not be seen.",
            "Confirm the loop by hand and check for documented escape mechanisms.",
        ),
    ],
    "focus_lost": [
        _mapping(
            "2.4.3", "supporting_evidence", "browser_interaction", "needs_review",
            "One headless run; focus handling can differ with browser UI present.",
            "Reproduce by hand in a visible browser.",
        ),
    ],
    "task_step_blocked": [
        _mapping(
            "2.1.1", "partial", "task_execution", "strong",
            "Proves one scripted path failed under keyboard-only interaction, not that every path fails.",
            "Repeat the step manually with a keyboard.",
        ),
    ],
    "task_control_not_keyboard_reachable": [
        _mapping(
            "2.1.1", "partial", "task_execution", "strong",
            "The Tab search has a fixed press budget and may miss controls on very long pages.",
            "Tab through the page manually and confirm the control is unreachable.",
        ),
        _mapping(
            "2.4.3", "supporting_evidence", "task_execution", "likely",
            "Reachability failure often indicates focus-order problems too.",
            "Review the Tab order around the unreachable control.",
        ),
    ],
    "task_expected_content_missing": [
        _mapping(
            "4.1.3", "supporting_evidence", "task_execution", "needs_review",
            "Compares normalized visible text only; the status may exist but use different wording.",
            "Check whether the outcome of the action is communicated at all, and whether it is exposed to assistive technology.",
        ),
    ],
    "low_contrast_text": [
        _mapping(
            "1.4.3", "partial", "low_vision", "likely",
            "Computed-color sampling; gradients, images, and overlays force a needs_review confidence instead.",
            "Verify the sampled colors match what users see, then measure contrast precisely.",
        ),
    ],
    "contrast_unresolved_background": [
        _mapping(
            "1.4.3", "supporting_evidence", "low_vision", "needs_review",
            "The background stack includes an image, gradient, or transparency, so the ratio cannot be computed reliably.",
            "Measure contrast against the actual rendered background (eyedropper or contrast tool).",
        ),
    ],
    "zoom_horizontal_overflow": [
        _mapping(
            "1.4.10", "supporting_evidence", "low_vision", "needs_review",
            "Legacy check kept for old reports; replaced by reflow_horizontal_scroll.",
            "Re-audit with a current A11yway version.",
        ),
    ],
    "zoom_fixed_width_content": [
        _mapping(
            "1.4.10", "supporting_evidence", "low_vision", "needs_review",
            "Legacy check kept for old reports; replaced by the reflow_* checks.",
            "Re-audit with a current A11yway version.",
        ),
    ],
    "reflow_horizontal_scroll": [
        _mapping(
            "1.4.10", "partial", "low_vision", "likely",
            "Zoom is emulated through equivalent viewport widths in one Chromium run; intentional scroll regions (data tables, maps) are allowed by WCAG.",
            "Confirm the overflow is not an allowed two-dimensional content region.",
        ),
    ],
    "reflow_clipped_content": [
        _mapping(
            "1.4.10", "partial", "low_vision", "likely",
            "Bounding boxes from one run; animation and lazy layout can shift results.",
            "Confirm the clipped element holds real content.",
        ),
        _mapping(
            "1.4.4", "supporting_evidence", "low_vision", "needs_review",
            "Viewport-based emulation approximates but does not equal text-only scaling to 200%.",
            "Test with browser text-size settings at 200%.",
        ),
    ],
    "reflow_overlap": [
        _mapping(
            "1.4.10", "partial", "low_vision", "needs_review",
            "Bounding-box intersection cannot judge visual intent; intentional stacking can be fine.",
            "Confirm the overlap visually at high zoom.",
        ),
    ],
    "focus_indicator_missing": [
        _mapping(
            "2.4.7", "partial", "low_vision", "likely",
            "Compares focused and unfocused computed styles (outline, box-shadow, border, background, text-decoration, transform, pseudo-elements, parent styles) in one Chromium run; animated or canvas-drawn indicators can still be missed.",
            "Tab through the page and look for any visible focus indication.",
        ),
    ],
    "radio_group_missing_fieldset": [
        _mapping(
            "1.3.1", "partial", "static", "likely",
            "Only checks fieldset/legend and role=radiogroup with an accessible name; other grouping idioms need review.",
            "Confirm the group question is announced when a screen reader reaches each radio button.",
        ),
    ],
    "table_missing_headers": [
        _mapping(
            "1.3.1", "partial", "static", "likely",
            "A table can be a layout table; the check skips role=presentation and single-row/column tables but cannot always tell intent.",
            "Decide whether the table presents data; if so, header cells must be programmatically associated.",
        ),
    ],
    "visual_required_not_programmatic": [
        _mapping(
            "1.3.1", "partial", "static", "likely",
            "Detects * or 'required' in an associated label without required/aria-required on the control.",
            "Confirm the field is actually mandatory and expose that state programmatically.",
        ),
        _mapping(
            "3.3.2", "supporting_evidence", "static", "needs_review",
            "The visible instruction exists; only the programmatic exposure is missing.",
            "Check what a screen reader announces for the field's required state.",
        ),
    ],
    "fake_heading": [
        _mapping(
            "1.3.1", "supporting_evidence", "static", "needs_review",
            "Inline-style heuristic (large bold text in div/span); many false positives are possible in decorated content, so this is review evidence only.",
            "Judge whether the styled text functions as a section heading; if so, use a real heading element.",
        ),
    ],
    "sensory_instruction": [
        _mapping(
            "1.3.3", "supporting_evidence", "static", "needs_review",
            "Keyword pattern heuristic; the surrounding text may also give non-sensory identification.",
            "Read the instruction in context and check whether it also identifies the target by name or label.",
        ),
    ],
    "missing_autocomplete": [
        _mapping(
            "1.3.5", "partial", "static", "likely",
            "Conservative token map for common personal-data fields; custom or ambiguous fields are skipped, and search/one-time-code fields are excluded.",
            "Confirm the field collects information about the user and add the matching autocomplete token.",
        ),
    ],
    "invalid_autocomplete_token": [
        _mapping(
            "1.3.5", "partial", "static", "likely",
            "Validates known autocomplete detail tokens but cannot prove the field purpose.",
            "Confirm the field collects information about the user and replace the invalid token with a matching valid one.",
        ),
    ],
    "contradictory_autocomplete": [
        _mapping(
            "1.3.5", "partial", "static", "likely",
            "Compares inferred purpose with the token; ambiguous labels and localized forms can require review.",
            "Confirm the intended field purpose and use the matching autocomplete token.",
        ),
    ],
    "autocomplete_unsupported_control": [
        _mapping(
            "1.3.5", "supporting_evidence", "static", "needs_review",
            "Flags autocomplete metadata on controls that normally do not collect reusable personal data.",
            "Confirm the control is not a user-information field and remove misleading autocomplete metadata.",
        ),
    ],
    "no_bypass_mechanism": [
        _mapping(
            "2.4.1", "partial", "static", "needs_review",
            "Fires only for pages with a substantial repeated navigation block and no skip link, main landmark, or heading-based structure; other bypass mechanisms may exist.",
            "Check whether keyboard users can reach the main content without tabbing through all repeated blocks.",
        ),
    ],
    "label_in_name_mismatch": [
        _mapping(
            "2.5.3", "partial", "static", "likely",
            "Normalized substring comparison of visible text vs aria-label; icon-only and very short labels are skipped.",
            "Say the visible label to a speech-input tool and check whether the control activates.",
        ),
    ],
    "accessible_authentication_barrier": [
        _mapping(
            "3.3.8", "supporting_evidence", "static", "needs_review",
            "Public-page heuristic for paste blocking and CAPTCHA-like challenge text; authentication is never attempted.",
            "Inspect the authentication flow manually and verify accessible alternatives without logging in.",
        ),
    ],
    "redundant_entry_repeated_field": [
        _mapping(
            "3.3.7", "supporting_evidence", "static", "needs_review",
            "Single-page repeated-field inference only; full redundant-entry testing needs a controlled workflow.",
            "Confirm whether repeated fields request already-entered information or a legitimate second person's information.",
        ),
    ],
    "error_prevention_missing": [
        _mapping(
            "3.3.4", "supporting_evidence", "static", "needs_review",
            "Keyword heuristic for high-consequence public forms; it does not submit forms or inspect later workflow steps.",
            "Review the permitted workflow for confirmation, correction, reversal, or review mechanisms.",
        ),
    ],
    "status_message_not_live": [
        _mapping(
            "4.1.3", "supporting_evidence", "static", "needs_review",
            "Static status-like content only; dynamic before/after accessibility-tree behavior is not reproduced.",
            "Trigger the update and inspect whether the status message is exposed through role=status, role=alert, or aria-live.",
        ),
    ],
    "small_target_size": [
        _mapping(
            "2.5.8", "partial", "low_vision", "likely",
            "Measured in one Chromium run at default zoom; inline text links and targets with sufficient surrounding spacing are excluded, but equivalent-control and essential exceptions need human judgment.",
            "Check the 2.5.8 exceptions: equivalent target, inline, user-agent default, essential.",
        ),
        _mapping(
            "2.5.5", "supporting_evidence", "low_vision", "informational",
            "2.5.5 (AAA) uses a 44px target; measurements are evidence only.",
            "Apply the 44px AAA threshold manually if targeting AAA.",
        ),
    ],
    "focus_obscured": [
        _mapping(
            "2.4.11", "partial", "low_vision", "likely",
            "Bounding-box and hit-test sampling against sticky/fixed overlays in one run; overlays that appear only after user actions are not seen.",
            "Tab to the control and confirm whether it is visible behind sticky headers, footers, banners, or widgets.",
        ),
    ],
    "text_spacing_content_loss": [
        _mapping(
            "1.4.12", "partial", "low_vision", "likely",
            "Applies the WCAG reference text-spacing overrides and compares clipping/overlap before and after; loss caused by JavaScript reacting to resize is not modeled.",
            "Apply a text-spacing bookmarklet and confirm the content or control is genuinely lost.",
        ),
    ],
    "meaningful_sequence_reorder": [
        _mapping(
            "1.3.2", "supporting_evidence", "static", "needs_review",
            "Detects inline CSS order/grid placement that can desynchronize visual and DOM order, but cannot determine intended meaning.",
            "Compare DOM order, visual order, and keyboard/focus order in the rendered page.",
        ),
    ],
    "orientation_restriction": [
        _mapping(
            "1.3.4", "partial", "static", "needs_review",
            "Requires strong static restriction evidence such as rotate messaging, orientation-lock code, or orientation-specific hidden content.",
            "Test the page in portrait and landscape and confirm content/functionality is restricted without an essential reason.",
        ),
    ],
    "color_only_indicator": [
        _mapping(
            "1.4.1", "supporting_evidence", "static", "needs_review",
            "Looks for status/selection classes or inline color cues while excluding common non-color alternatives; final computed presentation is not measured.",
            "Confirm color is the only way the information is conveyed.",
        ),
    ],
    "autoplay_audio_no_control": [
        _mapping(
            "1.4.2", "partial", "static", "needs_review",
            "Detects native autoplay audio without controls; duration and custom controls require rendered-page review.",
            "Confirm the audio starts automatically, lasts more than about three seconds, and lacks pause/stop or volume controls.",
        ),
    ],
    "image_of_text": [
        _mapping(
            "1.4.5", "supporting_evidence", "static", "needs_review",
            "Uses SVG text or image filename evidence; it does not perform OCR or judge exceptions such as logos.",
            "Inspect whether the graphic contains text that should be real text, or whether an exception applies.",
        ),
    ],
    "hover_focus_content": [
        _mapping(
            "1.4.13", "supporting_evidence", "static", "needs_review",
            "Static event/CSS evidence cannot verify dismissible, hoverable, or persistent behavior.",
            "Interact with the component by keyboard and pointer to test dismissibility, hoverability, persistence, and obstruction.",
        ),
    ],
    "single_character_shortcut": [
        _mapping(
            "2.1.4", "supporting_evidence", "static", "needs_review",
            "Script heuristic for unmodified single-character key listeners; minified code and typing-field exceptions require manual testing.",
            "Verify whether the shortcut triggers without modifiers and whether it can be disabled, remapped, or scoped away from text entry.",
        ),
    ],
    "timing_adjustable_missing": [
        _mapping(
            "2.2.1", "supporting_evidence", "static", "needs_review",
            "Detects meta refresh, timeout scripts, and countdown language, but not all timing exceptions or custom adjustment controls.",
            "Confirm the time limit, whether users can extend/disable/adjust it, and whether an exception applies.",
        ),
    ],
    "moving_content_no_pause": [
        _mapping(
            "2.2.2", "supporting_evidence", "static", "needs_review",
            "Detects common auto-moving/update patterns and visible pause/stop/hide controls; duration and process exceptions require review.",
            "Confirm movement lasts more than five seconds and no pause, stop, hide, or update-frequency control exists.",
        ),
    ],
    "possible_flashing_content": [
        _mapping(
            "2.3.1", "supporting_evidence", "static", "needs_review",
            "CSS keyframe/duration evidence suggests rapid flashing but does not measure luminance area or precise flash thresholds.",
            "Use a specialized flashing-threshold tool or visual review to confirm risk.",
        ),
    ],
    "interaction_motion_no_reduced_motion": [
        _mapping(
            "2.3.3", "supporting_evidence", "static", "needs_review",
            "Detects interaction-triggered CSS motion without prefers-reduced-motion evidence; it cannot judge whether motion is essential.",
            "Trigger the interaction and confirm non-essential motion can be disabled or respects reduced-motion preferences.",
        ),
    ],
    "pointer_gesture_no_alternative": [
        _mapping(
            "2.5.1", "supporting_evidence", "static", "needs_review",
            "Event-name heuristic for swipe, pinch, path, or pointer-move interactions; visible alternatives are inferred from control text.",
            "Confirm the gesture is required and whether a simple pointer alternative exists.",
        ),
    ],
    "pointer_down_activation": [
        _mapping(
            "2.5.2", "supporting_evidence", "static", "needs_review",
            "Requires down-event evidence and no obvious up/cancel handler, but cannot verify final activation behavior.",
            "Test whether activation occurs on down, whether moving away cancels, and whether undo exists.",
        ),
    ],
    "dragging_no_alternative": [
        _mapping(
            "2.5.7", "supporting_evidence", "static", "needs_review",
            "Detects draggable markup or drag/drop script names and common non-drag alternatives; cannot prove dragging is required.",
            "Confirm the operation can be completed without dragging.",
        ),
    ],
    "focus_context_change": [
        _mapping(
            "3.2.1", "supporting_evidence", "static", "needs_review",
            "Inline onfocus-handler evidence only; external scripts and actual browser state changes require interaction testing.",
            "Focus the control without activating it and confirm whether navigation, submission, modal opening, or focus relocation occurs.",
        ),
    ],
    "input_context_change": [
        _mapping(
            "3.2.2", "supporting_evidence", "static", "needs_review",
            "Inline input/change-handler evidence only; external scripts and warning mechanisms may be missed.",
            "Change the control value with synthetic local data and confirm whether an unexpected context change occurs.",
        ),
    ],
    "error_not_identified": [
        _mapping(
            "3.3.1", "supporting_evidence", "static", "needs_review",
            "Static error markup is inspected for aria-invalid/aria-describedby association; runtime validation may be different.",
            "Submit local or permitted test data and confirm errors identify affected fields in text and accessibility APIs.",
        ),
    ],
    "error_suggestion_missing": [
        _mapping(
            "3.3.3", "supporting_evidence", "static", "needs_review",
            "Checks static error text for common correction guidance words; it cannot judge all useful suggestions.",
            "Confirm a practical correction suggestion is provided when the correction is known.",
        ),
    ],
}





AXE_COVERED_CRITERIA: set[str] = {
    "1.1.1", "1.2.2", "1.3.1", "1.3.4", "1.3.5", "1.4.1", "1.4.2", "1.4.3",
    "1.4.4", "1.4.12", "2.1.1", "2.2.1", "2.2.2", "2.4.1", "2.4.2", "2.4.4",
    "3.1.1", "3.1.2", "4.1.2", "4.1.3",
}


def wcag_mappings_for_issue_type(issue_type: str) -> list[dict[str, str]]:

    return [dict(item) for item in RULE_WCAG_MAP.get(issue_type, [])]


def best_native_coverage() -> dict[str, dict[str, Any]]:





    best: dict[str, dict[str, Any]] = {}
    for issue_type, mappings in RULE_WCAG_MAP.items():
        for mapping in mappings:
            sc = mapping["sc"]
            rank = _COVERAGE_RANK.get(mapping["coverage"], 0)
            current = best.get(sc)
            if current is None or rank > current["rank"]:
                best[sc] = {
                    "rank": rank,
                    "coverage": mapping["coverage"],
                    "rules": [issue_type],
                }
            elif rank == current["rank"] and issue_type not in current["rules"]:
                current["rules"].append(issue_type)
    return best



def _coverage_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "wcag22_coverage.json"


def load_coverage_registry() -> dict[str, Any]:
    return json.loads(_coverage_registry_path().read_text(encoding="utf-8"))


def aa_criteria() -> dict[str, dict[str, str]]:
    return {
        sc: info
        for sc, info in WCAG_2_2_CRITERIA.items()
        if info["level"] in {"A", "AA"}
    }


def coverage_summary() -> dict[str, Any]:
    registry = load_coverage_registry()
    rows = registry["criteria"]
    buckets = {status: [] for status in registry["allowed_coverage_statuses"]}
    for row in rows:
        buckets[row["coverage_status"]].append(row["criterion"])
    for values in buckets.values():
        values.sort(key=_sc_sort_key)
    counts = {key: len(value) for key, value in buckets.items()}
    legacy = best_native_coverage()
    return {
        "wcag_version": registry["wcag_version"],
        "total_criteria": len(rows),
        "automated": buckets["automated"],
        "partially_automated": buckets["partially_automated"],
        "manual_only": buckets["manual_only"],
        "unsupported": buckets["unsupported"],
        "counts": counts,
        "registry_scope": registry["scope"],
        "direct": sorted([sc for sc, item in legacy.items() if item["coverage"] == "direct" and sc in aa_criteria()], key=_sc_sort_key),
        "partial": sorted([sc for sc, item in legacy.items() if item["coverage"] == "partial" and sc in aa_criteria()], key=_sc_sort_key),
        "supporting_evidence": sorted([sc for sc, item in legacy.items() if item["coverage"] == "supporting_evidence" and sc in aa_criteria()], key=_sc_sort_key),
        "axe_only": [],
    }


def coverage_summary_for_report() -> dict[str, Any]:
    summary = coverage_summary()
    return {
        "wcag_version": "2.2",
        "scope": "Level A and AA Success Criteria; 4.1.1 Parsing is obsolete and excluded.",
        "total_criteria": summary["total_criteria"],
        "counts": summary["counts"],
        "note": "WCAG evidence coverage is not WCAG conformance, certification, scoring, or a legal claim. Automated and partially automated rule coverage still requires manual review.",
    }


def _sc_sort_key(sc: str) -> tuple[int, ...]:
    return tuple(int(part) for part in sc.split("."))


def build_coverage_matrix() -> list[dict[str, Any]]:
    registry = load_coverage_registry()
    return sorted(registry["criteria"], key=lambda row: _sc_sort_key(row["criterion"]))


def rule_coverage_index() -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in build_coverage_matrix():
        for rule in row["implemented_rule_ids"]:
            index.setdefault(rule, []).append(row["criterion"])
    return {rule: sorted(criteria, key=_sc_sort_key) for rule, criteria in sorted(index.items())}


def _criterion_label(sc: str) -> str:
    info = aa_criteria()[sc]
    return f"{sc} {info['name']} (Level {info['level']})"


def format_coverage_cli() -> str:
    summary = coverage_summary()
    counts = summary["counts"]
    total = summary["total_criteria"]
    covered = counts["automated"] + counts["partially_automated"]
    percent = covered / total * 100 if total else 0
    lines = [
        "A11yway WCAG 2.2 A/AA coverage inventory",
        "",
        f"Total WCAG 2.2 Level A and AA Success Criteria: {total}",
        f"Automated: {counts['automated']}",
        f"Partially automated: {counts['partially_automated']}",
        f"Manual only: {counts['manual_only']}",
        f"Unsupported: {counts['unsupported']}",
        f"Automated or partially automated rule coverage: {percent:.1f}%",
        "",
        "This figure is not WCAG conformance, certification, scoring, or a legal claim.",
        "",
        "Criteria covered by each A11yway rule:",
    ]
    for rule, criteria in rule_coverage_index().items():
        lines.append(f"   {rule}: {', '.join(criteria)}")
    lines.extend(["", "Criteria that still need implementation:"])
    for sc in summary["unsupported"]:
        lines.append(f"   {_criterion_label(sc)}")
    lines.extend(["", "Criteria that fundamentally require human judgment or permitted workflow testing:"])
    for sc in summary["manual_only"]:
        lines.append(f"   {_criterion_label(sc)}")
    for label, key in [
        ("Automated", "automated"),
        ("Partially automated", "partially_automated"),
        ("Manual only", "manual_only"),
        ("Unsupported", "unsupported"),
    ]:
        lines.append("")
        lines.append(f"{label} criteria ({len(summary[key])}):")
        if summary[key]:
            for sc in summary[key]:
                lines.append(f"   {_criterion_label(sc)}")
        else:
            lines.append("   none")
    lines.extend([
        "",
        "Coverage describes A11yway rule evidence only. Axe-core evidence is treated as partial and is never counted as full criterion coverage.",
        "Docs: docs/WCAG22_COVERAGE.md",
    ])
    return "\n".join(lines)


def build_coverage_markdown() -> str:
    summary = coverage_summary()
    counts = summary["counts"]
    total = summary["total_criteria"]
    covered = counts["automated"] + counts["partially_automated"]
    percent = covered / total * 100 if total else 0
    lines = [
        "# A11yway WCAG 2.2 A/AA Coverage Inventory",
        "",
        "This document is generated from `a11yway/data/wcag22_coverage.json`.",
        "",
        "This figure is not WCAG conformance, certification, scoring, or a legal claim.",
        "",
        "## Summary",
        "",
        f"- Total WCAG 2.2 Level A and AA Success Criteria: {total}",
        f"- Automated: {counts['automated']}",
        f"- Partially automated: {counts['partially_automated']}",
        f"- Manual only: {counts['manual_only']}",
        f"- Unsupported: {counts['unsupported']}",
        f"- Automated or partially automated rule coverage: {percent:.1f}%",
        "",
        "## Coverage Statuses",
        "",
        "- `automated`: deterministic A11yway rule evidence for a narrow criterion slice with fixtures and actionable output.",
        "- `partially_automated`: A11yway or axe-core evidence helps evaluate the criterion but does not fully decide it.",
        "- `manual_only`: the criterion fundamentally needs human judgment or a permitted workflow.",
        "- `unsupported`: A11yway does not currently implement criterion-specific evidence.",
        "",
        "## Matrix",
        "",
        "| Criterion | Short name | Level | Status | Rules | Engines | Evidence | Human review required | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    def cell(value: object) -> str:
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value) or "none"
        return str(value).replace("|", "\\|")
    for row in build_coverage_matrix():
        lines.append(
            "| {criterion} | {name} | {level} | {status} | {rules} | {engines} | {evidence} | {human} | {limitations} |".format(
                criterion=cell(row["criterion"]),
                name=cell(row["short_name"]),
                level=cell(row["level"]),
                status=cell(row["coverage_status"]),
                rules=cell([f"`{rule}`" for rule in row["implemented_rule_ids"]]),
                engines=cell(row["testing_engines_used"]),
                evidence=cell(row["evidence_produced"]),
                human="yes" if row["human_review_required"] else "no",
                limitations=cell(row["limitations"]),
            )
        )
    lines.extend([
        "",
        "## Rules by Criterion",
        "",
    ])
    for row in build_coverage_matrix():
        rules = ", ".join(f"`{rule}`" for rule in row["implemented_rule_ids"]) or "none"
        lines.append(f"- {row['criterion']} {row['short_name']}: {rules}")
    return "\n".join(lines) + "\n"
