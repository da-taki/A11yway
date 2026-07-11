"""Central registry describing every static issue type A11yway can report.

Each rule documents what a check detects, why it matters for students, how
to fix it, and what the static prototype cannot verify. Reports use this
registry so reviewers can understand findings without reading the code.
"""

from __future__ import annotations

from a11yway.core.wcag_coverage import wcag_mappings_for_issue_type
from a11yway.models.issue import AccessibilityIssue


# Rule fields copied into per-issue report metadata. The how_to_fix text is
# intentionally excluded because issues already carry a suggested_fix.
# Static rules document static_check_limitations; browser rules document
# browser_check_limitations. Only fields present on a rule are copied.
REPORT_RULE_FIELDS = [
    "title",
    "category",
    "why_it_matters",
    "manual_review_notes",
    "static_check_limitations",
    "browser_check_limitations",
]

# Confidence a finding carries when the check did not set one explicitly.
# confirmed: deterministic observed blockage or state.
# likely: strong single-source evidence with known blind spots.
# needs_review: heuristic evidence a human must judge.
# informational: context for reviewers, not a suspected failure.
DEFAULT_CONFIDENCE_BY_RULE = {
    "missing_form_label": "likely",
    "missing_button_name": "likely",
    "missing_link_name": "likely",
    "generic_link_text": "needs_review",
    "missing_image_alt": "likely",
    "image_empty_alt_suspicious": "needs_review",
    "missing_h1": "needs_review",
    "skipped_heading_level": "needs_review",
    "multiple_h1": "informational",
    "missing_page_title": "likely",
    "missing_html_lang": "likely",
    "missing_video_captions": "needs_review",
    "missing_audio_transcript": "needs_review",
    "missing_lang_indic": "likely",
    "mixed_script_element": "needs_review",
    "lang_mismatch": "likely",
    "radio_group_missing_fieldset": "likely",
    "table_missing_headers": "likely",
    "visual_required_not_programmatic": "likely",
    "fake_heading": "needs_review",
    "sensory_instruction": "needs_review",
    "missing_autocomplete": "likely",
    "no_bypass_mechanism": "needs_review",
    "label_in_name_mismatch": "likely",
    "browser_no_focusable_elements": "likely",
    "browser_focus_not_moving": "likely",
    "browser_repeated_focus": "needs_review",
    "browser_focused_control_missing_name": "likely",
    "browser_focus_on_hidden_element": "needs_review",
    "unnamed_focus_stop": "likely",
    "keyboard_trap": "confirmed",
    "focus_lost": "needs_review",
    "task_step_blocked": "confirmed",
    "task_control_not_keyboard_reachable": "confirmed",
    "task_expected_content_missing": "needs_review",
    "low_contrast_text": "likely",
    "contrast_unresolved_background": "needs_review",
    "zoom_horizontal_overflow": "needs_review",
    "zoom_fixed_width_content": "needs_review",
    "reflow_horizontal_scroll": "likely",
    "reflow_clipped_content": "likely",
    "reflow_overlap": "needs_review",
    "focus_indicator_missing": "likely",
    "small_target_size": "likely",
    "focus_obscured": "likely",
    "text_spacing_content_loss": "likely",
    "meaningful_sequence_reorder": "needs_review",
    "orientation_restriction": "needs_review",
    "color_only_indicator": "needs_review",
    "autoplay_audio_no_control": "needs_review",
    "image_of_text": "needs_review",
    "hover_focus_content": "needs_review",
    "single_character_shortcut": "needs_review",
    "timing_adjustable_missing": "needs_review",
    "moving_content_no_pause": "needs_review",
    "possible_flashing_content": "needs_review",
    "interaction_motion_no_reduced_motion": "needs_review",
    "pointer_gesture_no_alternative": "needs_review",
    "pointer_down_activation": "needs_review",
    "dragging_no_alternative": "needs_review",
    "focus_context_change": "needs_review",
    "input_context_change": "needs_review",
    "error_not_identified": "needs_review",
    "error_suggestion_missing": "needs_review",
}

FALLBACK_CONFIDENCE = "needs_review"


RULES: dict[str, dict] = {
    "missing_form_label": {
        "issue_type": "missing_form_label",
        "title": "Form control missing accessible label",
        "category": "Forms",
        "default_severity": "high",
        "why_it_matters": (
            "Students using keyboard navigation, assistive technology, or "
            "simplified layouts may not know what information the field expects."
        ),
        "how_to_fix": (
            "Add a visible label connected with for/id. Use aria-label only "
            "when a visible label is not possible."
        ),
        "manual_review_notes": (
            "Check whether the visual design already implies the label but "
            "fails programmatically."
        ),
        "static_check_limitations": (
            "Static HTML cannot always confirm labels created dynamically by JavaScript."
        ),
        "standard_hint": (
            "Related to label/name/role accessibility requirements for form controls."
        ),
    },
    "missing_button_name": {
        "issue_type": "missing_button_name",
        "title": "Button missing accessible name",
        "category": "Interactive Elements",
        "default_severity": "high",
        "why_it_matters": (
            "A button without a name is announced as just 'button' by screen "
            "readers, so students cannot tell what pressing it will do."
        ),
        "how_to_fix": (
            "Add clear button text or an aria-label that describes the button action."
        ),
        "manual_review_notes": (
            "Icon-only buttons may look meaningful visually but still need a "
            "programmatic name."
        ),
        "static_check_limitations": (
            "Static HTML cannot see names added later by JavaScript or icon fonts."
        ),
        "standard_hint": (
            "Related to name/role/value accessibility requirements for controls."
        ),
    },
    "missing_link_name": {
        "issue_type": "missing_link_name",
        "title": "Link missing accessible name",
        "category": "Interactive Elements",
        "default_severity": "high",
        "why_it_matters": (
            "Screen reader users hear an empty or meaningless link and cannot "
            "decide whether to follow it."
        ),
        "how_to_fix": (
            "Add descriptive link text that explains the link destination or action."
        ),
        "manual_review_notes": (
            "Links wrapping only images need useful alt text on the image."
        ),
        "static_check_limitations": (
            "Static HTML cannot detect link names injected by JavaScript."
        ),
        "standard_hint": (
            "Related to link purpose and name/role accessibility requirements."
        ),
    },
    "generic_link_text": {
        "issue_type": "generic_link_text",
        "title": "Link text is too generic",
        "category": "Interactive Elements",
        "default_severity": "medium",
        "why_it_matters": (
            "Students who navigate by a list of links hear 'click here' with no "
            "context and cannot tell links apart."
        ),
        "how_to_fix": (
            'Use descriptive link text like "Download scholarship guidelines" '
            'instead of "click here."'
        ),
        "manual_review_notes": (
            "Surrounding text may add context visually, but the link should "
            "still make sense on its own."
        ),
        "static_check_limitations": (
            "The check only matches a small list of common generic phrases."
        ),
        "standard_hint": (
            "Related to link purpose accessibility requirements."
        ),
    },
    "missing_image_alt": {
        "issue_type": "missing_image_alt",
        "title": "Image missing useful alt text",
        "category": "Images",
        "default_severity": "medium",
        "why_it_matters": (
            "Students using screen readers miss the image content entirely, "
            "which can hide instructions, diagrams, or required information."
        ),
        "how_to_fix": (
            "Add alt text that describes the image purpose, or mark decorative "
            "images as presentation."
        ),
        "manual_review_notes": (
            "Confirm whether the image is informative or decorative; only a "
            "human can judge if existing alt text is actually useful."
        ),
        "static_check_limitations": (
            "Static checks cannot judge alt text quality, only whether it exists."
        ),
        "standard_hint": (
            "Related to text alternatives for non-text content."
        ),
    },
    "missing_h1": {
        "issue_type": "missing_h1",
        "title": "Page missing an h1 heading",
        "category": "Headings & Structure",
        "default_severity": "medium",
        "why_it_matters": (
            "Students using screen readers often jump to the main heading first; "
            "without an h1 they cannot quickly confirm what the page is about."
        ),
        "how_to_fix": "Add one clear h1 that matches the page purpose.",
        "manual_review_notes": (
            "A large styled heading may exist visually without being a real h1 element."
        ),
        "static_check_limitations": (
            "Static HTML cannot detect headings rendered by JavaScript."
        ),
        "standard_hint": (
            "Related to page structure and heading accessibility requirements."
        ),
    },
    "skipped_heading_level": {
        "issue_type": "skipped_heading_level",
        "title": "Heading level is skipped",
        "category": "Headings & Structure",
        "default_severity": "medium",
        "why_it_matters": (
            "Jumping from h1 to h3 breaks the page outline that screen reader "
            "users rely on to understand and navigate content."
        ),
        "how_to_fix": "Do not skip heading levels; move from h1 to h2 before h3.",
        "manual_review_notes": (
            "Check whether the heading order still makes sense when read as an outline."
        ),
        "static_check_limitations": (
            "The check follows document order only; visual layout may differ."
        ),
        "standard_hint": (
            "Related to page structure and heading accessibility requirements."
        ),
    },
    "multiple_h1": {
        "issue_type": "multiple_h1",
        "title": "Page has multiple h1 headings",
        "category": "Headings & Structure",
        "default_severity": "low",
        "why_it_matters": (
            "Several h1 headings make it harder for students to identify the "
            "single main topic of the page."
        ),
        "how_to_fix": (
            "Use one main h1 for the page purpose, then organize sections with "
            "h2 and lower headings."
        ),
        "manual_review_notes": (
            "Some layouts intentionally use sectioned h1 elements; judge readability."
        ),
        "static_check_limitations": (
            "Static HTML cannot evaluate how the headings are presented visually."
        ),
        "standard_hint": (
            "Related to page structure and heading accessibility requirements."
        ),
    },
    "missing_page_title": {
        "issue_type": "missing_page_title",
        "title": "Page missing a title",
        "category": "Page Metadata",
        "default_severity": "medium",
        "why_it_matters": (
            "The title is the first thing screen readers announce and how "
            "students tell browser tabs apart."
        ),
        "how_to_fix": "Add a short, descriptive page title.",
        "manual_review_notes": (
            "Check that the title actually describes this page, not just the site name."
        ),
        "static_check_limitations": (
            "Titles set dynamically by JavaScript are not visible to this check."
        ),
        "standard_hint": (
            "Related to page title accessibility requirements."
        ),
    },
    "missing_html_lang": {
        "issue_type": "missing_html_lang",
        "title": "HTML document missing a language",
        "category": "Page Metadata",
        "default_severity": "medium",
        "why_it_matters": (
            "Without a lang attribute, screen readers may mispronounce the page "
            "content by guessing the wrong language."
        ),
        "how_to_fix": (
            'Add lang="en" or the correct document language to the <html> element.'
        ),
        "manual_review_notes": (
            "Confirm the declared language matches the actual page content."
        ),
        "static_check_limitations": (
            "The check only inspects the html element, not mixed-language sections."
        ),
        "standard_hint": (
            "Related to language-of-page accessibility requirements."
        ),
    },
    "missing_video_captions": {
        "issue_type": "missing_video_captions",
        "title": "Video missing captions",
        "category": "Media",
        "default_severity": "high",
        "why_it_matters": (
            "Deaf and hard-of-hearing students cannot access spoken lesson "
            "content without captions or subtitles."
        ),
        "how_to_fix": "Add captions or subtitles for education video content.",
        "manual_review_notes": (
            "Captions may be provided by an embedded player or platform instead "
            "of a track element."
        ),
        "static_check_limitations": (
            "The check only sees <track> elements; player-level or burned-in "
            "captions are invisible to static HTML."
        ),
        "standard_hint": (
            "Related to captions requirements for prerecorded media."
        ),
    },
    "missing_audio_transcript": {
        "issue_type": "missing_audio_transcript",
        "title": "Audio missing a transcript",
        "category": "Media",
        "default_severity": "high",
        "why_it_matters": (
            "Deaf and hard-of-hearing students need a text alternative to use "
            "audio lessons or instructions."
        ),
        "how_to_fix": "Add a transcript near audio lessons or instructions.",
        "manual_review_notes": (
            "A transcript may exist on a linked page; confirm it is easy to find."
        ),
        "static_check_limitations": (
            'The check only looks for the word "transcript" in visible page text, '
            "which is a rough heuristic."
        ),
        "standard_hint": (
            "Related to text alternatives for prerecorded audio."
        ),
    },
    "missing_lang_indic": {
        "issue_type": "missing_lang_indic",
        "title": "Indic-script text lacks a matching lang attribute",
        "category": "Language",
        "default_severity": "high",
        "why_it_matters": (
            "Text-to-speech picks a voice from the declared language, so "
            "Devanagari, Gurmukhi, Tamil, or other Indic-script text under a "
            "missing or non-matching lang is read as garbled English."
        ),
        "how_to_fix": (
            "Add a lang attribute matching the text's language (for example "
            'lang="hi" for Hindi in Devanagari, lang="pa" for Punjabi in '
            "Gurmukhi) on the element or a fitting ancestor."
        ),
        "manual_review_notes": (
            "Confirm the actual language: several languages share a script "
            "(Hindi and Marathi both use Devanagari), so the right lang value "
            "needs a human decision."
        ),
        "static_check_limitations": (
            "Script detection uses Unicode ranges and is a heuristic. "
            "Transliterated text (Hindi written in Latin letters) cannot be "
            "detected at all."
        ),
        "standard_hint": (
            "Related to WCAG 3.1.1 Language of Page and 3.1.2 Language of Parts."
        ),
    },
    "mixed_script_element": {
        "issue_type": "mixed_script_element",
        "title": "Latin and Indic scripts mix without a lang boundary",
        "category": "Language",
        "default_severity": "medium",
        "why_it_matters": (
            "When one text run mixes scripts without lang-tagged boundaries, "
            "speech engines cannot switch voices and commonly garble one of "
            "the languages."
        ),
        "how_to_fix": (
            "Wrap each language's text in an element with the matching lang "
            "attribute so speech engines can switch voices."
        ),
        "manual_review_notes": (
            "Short mixes are often fine; the check already ignores numbers, "
            "short acronyms, and single loanwords, but listen with a real "
            "screen reader to confirm impact."
        ),
        "static_check_limitations": (
            "A conservative heuristic: it requires several Latin words next "
            "to Indic text in one text node and may miss subtler mixes or "
            "flag intentional bilingual lines."
        ),
        "standard_hint": (
            "Related to WCAG 3.1.2 Language of Parts."
        ),
    },
    "lang_mismatch": {
        "issue_type": "lang_mismatch",
        "title": "Declared lang contradicts the text's script",
        "category": "Language",
        "default_severity": "high",
        "why_it_matters": (
            "A lang attribute promising one language over text written in a "
            "different script makes screen readers pick the wrong voice, "
            "which is worse than no declaration at all."
        ),
        "how_to_fix": (
            "Correct the lang attribute to match the language actually "
            "written in the element."
        ),
        "manual_review_notes": (
            "Languages sharing a script cannot be told apart here; the check "
            "only fires when the script itself contradicts the declaration."
        ),
        "static_check_limitations": (
            "Script detection uses Unicode ranges and cannot judge "
            "transliterated or romanized text."
        ),
        "standard_hint": (
            "Related to WCAG 3.1.2 Language of Parts."
        ),
    },
    "browser_no_focusable_elements": {
        "issue_type": "browser_no_focusable_elements",
        "title": "No keyboard focusable elements found",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "If nothing on the page can receive keyboard focus, students who "
            "cannot use a mouse are completely blocked from interacting."
        ),
        "how_to_fix": (
            "Use native links, buttons, and form controls, or add proper "
            "tabindex and keyboard handlers to custom controls."
        ),
        "manual_review_notes": (
            "Confirm with a real keyboard that Tab reaches the page controls; "
            "some pages move focus with custom scripts."
        ),
        "browser_check_limitations": (
            "The check counts common focusable selectors in headless Chromium "
            "and may miss unusual custom widgets."
        ),
        "standard_hint": (
            "Related to keyboard accessibility requirements for interactive content."
        ),
    },
    "browser_focus_not_moving": {
        "issue_type": "browser_focus_not_moving",
        "title": "Keyboard focus does not move into the page",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "If pressing Tab never focuses page content, keyboard-only students "
            "cannot start the task at all."
        ),
        "how_to_fix": (
            "Check for scripts that cancel Tab key events or reset focus, and "
            "make sure controls are reachable with the keyboard."
        ),
        "manual_review_notes": (
            "Verify manually with a keyboard; timing or focus scripts can "
            "behave differently in a headless browser."
        ),
        "browser_check_limitations": (
            "Headless browser Tab behavior can differ slightly from a real "
            "desktop browser session."
        ),
        "standard_hint": (
            "Related to keyboard accessibility and no-keyboard-trap requirements."
        ),
    },
    "browser_repeated_focus": {
        "issue_type": "browser_repeated_focus",
        "title": "Keyboard focus repeats on the same element",
        "category": "Keyboard Interaction",
        "default_severity": "medium",
        "why_it_matters": (
            "Focus that keeps returning to the same element suggests a keyboard "
            "trap, which can strand students inside one control."
        ),
        "how_to_fix": (
            "Review tabindex values and focus scripts so Tab moves through "
            "every control in a sensible order."
        ),
        "manual_review_notes": (
            "Some widgets (like editors) legitimately hold focus; confirm "
            "whether the student can escape with standard keys."
        ),
        "browser_check_limitations": (
            "The heuristic only watches repeated Tab stops and cannot prove a "
            "real trap."
        ),
        "standard_hint": (
            "Related to no-keyboard-trap accessibility requirements."
        ),
    },
    "browser_focused_control_missing_name": {
        "issue_type": "browser_focused_control_missing_name",
        "title": "Focused control has no accessible name",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "A keyboard user can reach the control, but without a name a screen "
            "reader announces nothing useful about what it does."
        ),
        "how_to_fix": (
            "Add a visible label, text content, or aria-label so students know "
            "what the control does."
        ),
        "manual_review_notes": (
            "The accessible name is estimated; confirm with browser dev tools "
            "or a screen reader what is actually announced."
        ),
        "browser_check_limitations": (
            "Accessible names are estimated from labels, text, and common "
            "attributes, not from a full accessibility tree computation."
        ),
        "standard_hint": (
            "Related to name/role/value accessibility requirements for controls."
        ),
    },
    "browser_focus_on_hidden_element": {
        "issue_type": "browser_focus_on_hidden_element",
        "title": "Keyboard focus landed on a hidden element",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "When focus moves to an invisible element, keyboard users lose "
            "track of where they are on the page."
        ),
        "how_to_fix": (
            'Remove hidden elements from the Tab order with tabindex="-1" or '
            "make them visible when focused."
        ),
        "manual_review_notes": (
            "Check whether the element becomes visible on focus (like a skip "
            "link); that pattern is fine."
        ),
        "browser_check_limitations": (
            "Visibility is estimated from element size and CSS and may not "
            "match what users actually see."
        ),
        "standard_hint": (
            "Related to visible focus and keyboard accessibility requirements."
        ),
    },
    "unnamed_focus_stop": {
        "issue_type": "unnamed_focus_stop",
        "title": "Focus stop announces no accessible name",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "Chromium's accessibility tree computed an empty accessible name "
            "for this focus stop, so a screen reader user hears at most a role "
            "and cannot tell what the element is or does."
        ),
        "how_to_fix": (
            "Add a visible label, text content, alt text, or aria-label so "
            "the browser computes a usable accessible name for the element."
        ),
        "manual_review_notes": (
            "Confirm with a real screen reader. When this finding is present, "
            "the heuristic browser_focused_control_missing_name check is "
            "skipped for the same element, since the computed tree is the "
            "stronger evidence."
        ),
        "browser_check_limitations": (
            "Based on Chromium's computed accessibility tree in one browser "
            "run. It is not a screen reader simulation; NVDA, JAWS, and "
            "VoiceOver apply their own rules and other browsers can differ."
        ),
        "standard_hint": (
            "Related to name, role, and value accessibility requirements for "
            "user interface components."
        ),
    },
    "keyboard_trap": {
        "issue_type": "keyboard_trap",
        "title": "Keyboard focus is trapped in a loop",
        "category": "Keyboard Interaction",
        "default_severity": "high",
        "why_it_matters": (
            "Tab kept cycling through the same subset of elements without "
            "ever reaching the rest of the page, so a keyboard-only user is "
            "stuck and cannot finish anything beyond the loop."
        ),
        "how_to_fix": (
            "Let Tab move past the widget, or provide a standard way out, "
            "such as closing a modal with Escape and returning focus to the "
            "trigger."
        ),
        "manual_review_notes": (
            "Confirm the loop by hand and check for documented escape "
            "mechanisms (Escape, arrow keys, custom shortcuts) that Tab-only "
            "traversal cannot see."
        ),
        "browser_check_limitations": (
            "Based on observed Tab behavior in one Chromium run. It cannot "
            "verify custom escape mechanisms, and the count of unreached "
            "elements is an estimate from visible focusable elements."
        ),
        "standard_hint": ("Related to WCAG 2.1.2 No Keyboard Trap."),
    },
    "focus_lost": {
        "issue_type": "focus_lost",
        "title": "Keyboard focus left the page content",
        "category": "Keyboard Interaction",
        "default_severity": "medium",
        "why_it_matters": (
            "Pressing Tab repeatedly landed on the document body and focus "
            "never returned to page content, so keyboard users lose their "
            "place and cannot continue."
        ),
        "how_to_fix": (
            "Check for scripts that remove, hide, or blur the focused "
            "element, and keep every control at a stable place in the Tab "
            "order."
        ),
        "manual_review_notes": (
            "A single pass through the body between the last and first "
            "element is normal; this only fires when focus stays on the body "
            "across several presses. Confirm by hand in a visible browser."
        ),
        "browser_check_limitations": (
            "Observed in one headless Chromium run; focus handling can "
            "differ in other browsers and with browser UI present."
        ),
        "standard_hint": (
            "Related to keyboard operability and focus order requirements."
        ),
    },
    "task_step_blocked": {
        "issue_type": "task_step_blocked",
        "title": "Task step could not be completed with the keyboard",
        "category": "Task Execution",
        "default_severity": "high",
        "why_it_matters": (
            "A required step of a real education workflow failed under "
            "keyboard-only interaction, so a keyboard-only student is likely "
            "blocked from finishing the task."
        ),
        "how_to_fix": (
            "Make every control in the workflow reachable and operable with "
            "the keyboard, and check the step evidence for what failed."
        ),
        "manual_review_notes": (
            "Repeat the step manually with a keyboard; timing or scripted "
            "focus can behave differently in a headless browser."
        ),
        "browser_check_limitations": (
            "Steps are deterministic scripts; a human may find a workaround "
            "the script does not try."
        ),
        "standard_hint": (
            "Related to keyboard accessibility requirements for interactive workflows."
        ),
    },
    "task_control_not_keyboard_reachable": {
        "issue_type": "task_control_not_keyboard_reachable",
        "title": "Task control is not reachable with the keyboard",
        "category": "Task Execution",
        "default_severity": "high",
        "why_it_matters": (
            "The workflow could only continue by focusing the control "
            "programmatically; a real keyboard-only student cannot do that "
            "and would be stuck."
        ),
        "how_to_fix": (
            "Ensure the control is a native focusable element or has a "
            "proper tabindex, and that scripts do not skip it in Tab order."
        ),
        "manual_review_notes": (
            "Tab through the page manually and confirm whether the control "
            "is truly unreachable."
        ),
        "browser_check_limitations": (
            "The Tab search has a fixed press budget and may miss controls "
            "on very long pages."
        ),
        "standard_hint": (
            "Related to keyboard accessibility and focus order requirements."
        ),
    },
    "task_expected_content_missing": {
        "issue_type": "task_expected_content_missing",
        "title": "Expected task content is missing",
        "category": "Task Execution",
        "default_severity": "medium",
        "why_it_matters": (
            "Text the task expects (page purpose, instructions, or a success "
            "confirmation) was not visible, so students may not know where "
            "they are or whether the task worked."
        ),
        "how_to_fix": (
            "Show clear visible text for the page purpose and for the result "
            "of submitting a form."
        ),
        "manual_review_notes": (
            "The expected text is defined by the task author; confirm the "
            "wording still matches the live page."
        ),
        "browser_check_limitations": (
            "The check compares normalized visible text only; content inside "
            "images or drawn by unusual scripts is not seen."
        ),
        "standard_hint": (
            "Related to clear labeling and status feedback accessibility requirements."
        ),
    },
    "low_contrast_text": {
        "issue_type": "low_contrast_text",
        "title": "Rendered text may have low contrast",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "Low-vision readers may not be able to read text when the computed "
            "foreground and background colors are too similar."
        ),
        "how_to_fix": (
            "Increase foreground/background contrast and verify the final design "
            "with manual review."
        ),
        "manual_review_notes": (
            "Confirm the sampled colors match what users actually see, especially "
            "over gradients, images, and layered components."
        ),
        "browser_check_limitations": (
            "The check samples browser-computed colors and does not prove full "
            "WCAG color contrast compliance."
        ),
        "standard_hint": (
            "Related to text contrast requirements; treat this as a conservative review hint."
        ),
    },
    "zoom_horizontal_overflow": {
        "issue_type": "zoom_horizontal_overflow",
        "title": "Page has horizontal overflow under zoom/reflow stress",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "Horizontal scrolling can make pages difficult or impossible to use "
            "for low-vision readers who zoom or use narrow viewports."
        ),
        "how_to_fix": (
            "Use responsive layout, avoid fixed-width containers, and test reflow "
            "at high zoom."
        ),
        "manual_review_notes": (
            "Check the page manually at 200% zoom and narrow widths; some overflow "
            "may be intentional for data tables. Current audits emit "
            "reflow_horizontal_scroll instead; this type is kept for reports "
            "generated by older versions."
        ),
        "browser_check_limitations": (
            "This approximates reflow stress with a narrow viewport and does not "
            "prove full zoom/reflow compliance."
        ),
        "standard_hint": (
            "Related to reflow and resize text accessibility requirements."
        ),
    },
    "zoom_fixed_width_content": {
        "issue_type": "zoom_fixed_width_content",
        "title": "Fixed or wide content may prevent reflow",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "Large fixed-width elements can force horizontal scrolling and hide "
            "content when users zoom or use narrow windows."
        ),
        "how_to_fix": (
            "Replace fixed pixel widths with responsive constraints such as "
            "max-width: 100% and flexible layouts."
        ),
        "manual_review_notes": (
            "Confirm whether the wide element is essential and whether all content "
            "remains reachable without two-dimensional scrolling. Current audits "
            "emit the reflow_* checks instead; this type is kept for reports "
            "generated by older versions."
        ),
        "browser_check_limitations": (
            "The check flags obvious wide rendered elements and fixed pixel widths; "
            "it may miss complex layout problems."
        ),
        "standard_hint": (
            "Related to reflow and responsive layout accessibility requirements."
        ),
    },
    "reflow_horizontal_scroll": {
        "issue_type": "reflow_horizontal_scroll",
        "title": "Page requires horizontal scrolling under zoom",
        "category": "Low Vision",
        "default_severity": "high",
        "why_it_matters": (
            "At high zoom, readers must scroll horizontally for every line "
            "when the page does not reflow into one column, which makes "
            "reading exhausting or impossible."
        ),
        "how_to_fix": (
            "Use responsive layout and max-width: 100% so content reflows "
            "at the WCAG 1.4.10 reference width of 320 CSS px (400% zoom)."
        ),
        "manual_review_notes": (
            "Data tables, maps, and similar two-dimensional content may "
            "scroll horizontally by design; WCAG allows that, so confirm "
            "the overflow is not essential content."
        ),
        "browser_check_limitations": (
            "Zoom is emulated through the equivalent CSS viewport widths "
            "(1280 base at 200% and 400%) in one Chromium run; gradients "
            "and image-heavy layouts need manual review."
        ),
        "standard_hint": ("Related to WCAG 1.4.10 Reflow."),
    },
    "reflow_clipped_content": {
        "issue_type": "reflow_clipped_content",
        "title": "Content is clipped outside the zoomed viewport",
        "category": "Low Vision",
        "default_severity": "high",
        "why_it_matters": (
            "Text or controls cut off beyond the reachable area disappear "
            "entirely for zoomed readers; they cannot scroll to them."
        ),
        "how_to_fix": (
            "Avoid fixed offsets and overflow: hidden cut-offs; let content "
            "wrap within the viewport width."
        ),
        "manual_review_notes": (
            "Confirm the clipped element holds real content; decorative "
            "elements cut by design are not a barrier."
        ),
        "browser_check_limitations": (
            "Bounding boxes come from one Chromium run at emulated zoom "
            "widths; animation and lazy layout can shift results."
        ),
        "standard_hint": (
            "Related to WCAG 1.4.10 Reflow and 1.4.4 Resize Text."
        ),
    },
    "reflow_overlap": {
        "issue_type": "reflow_overlap",
        "title": "Interactive elements overlap under zoom",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "Controls that collide at high zoom can cover each other, so "
            "zoomed readers cannot see or activate the one underneath."
        ),
        "how_to_fix": (
            "Let controls wrap or stack at narrow widths instead of using "
            "absolute positions that collide under zoom."
        ),
        "manual_review_notes": (
            "Confirm the overlap visually; intentional stacking such as a "
            "badge over a button can be fine."
        ),
        "browser_check_limitations": (
            "Overlap uses bounding-box intersection of visible controls in "
            "one Chromium run and cannot judge visual intent."
        ),
        "standard_hint": (
            "Related to WCAG 1.4.10 Reflow and general operability of controls."
        ),
    },
    "focus_indicator_missing": {
        "issue_type": "focus_indicator_missing",
        "title": "Focused element may not show a visible focus indicator",
        "category": "Low Vision",
        "default_severity": "high",
        "why_it_matters": (
            "Keyboard users with low vision need a visible indicator to know "
            "which control currently has focus."
        ),
        "how_to_fix": (
            "Provide a clear :focus or :focus-visible style with visible outline, "
            "border, or shadow."
        ),
        "manual_review_notes": (
            "Manually tab through the page; some custom focus styles may be visible "
            "but not detected by this heuristic."
        ),
        "browser_check_limitations": (
            "Focus indicator detection checks computed outline, border, and shadow "
            "heuristically and can miss custom visual treatments."
        ),
        "standard_hint": (
            "Related to visible focus accessibility requirements."
        ),
    },
    "image_empty_alt_suspicious": {
        "issue_type": "image_empty_alt_suspicious",
        "title": "Empty alt on an image that looks informative",
        "category": "Images",
        "default_severity": "low",
        "why_it_matters": (
            'alt="" hides an image from screen readers entirely. That is '
            "correct for decoration, but this image's filename suggests it "
            "may carry information (chart, diagram, map, screenshot)."
        ),
        "how_to_fix": (
            "If the image is informative, describe it in alt text. If it is "
            'decorative, alt="" is already correct and this finding can be '
            "dismissed."
        ),
        "manual_review_notes": (
            "Only a human can decide whether the image carries information; "
            "the filename heuristic is weak evidence."
        ),
        "static_check_limitations": (
            "Based on the src filename only; the image content is not analyzed."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.1.1 Non-text Content; manual "
            "confirmation required."
        ),
    },
    "radio_group_missing_fieldset": {
        "issue_type": "radio_group_missing_fieldset",
        "title": "Radio group is not grouped with fieldset/legend",
        "category": "Forms",
        "default_severity": "medium",
        "why_it_matters": (
            "Without fieldset/legend (or an equivalent named group role), a "
            "screen reader user hears each radio option without the shared "
            "question it answers."
        ),
        "how_to_fix": (
            "Wrap the radio buttons in a <fieldset> whose <legend> states "
            'the group question, or use role="radiogroup" with an '
            "accessible name."
        ),
        "manual_review_notes": (
            "Some designs convey the group through a nearby heading; judge "
            "whether the question is announced with each option."
        ),
        "static_check_limitations": (
            "Only fieldset/legend and role=radiogroup with a name are "
            "recognized as grouping; aria-labelledby group idioms on other "
            "containers may be missed."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.3.1 Info and Relationships."
        ),
    },
    "table_missing_headers": {
        "issue_type": "table_missing_headers",
        "title": "Data table has no header cells",
        "category": "Structure",
        "default_severity": "medium",
        "why_it_matters": (
            "Without th cells (or scope/headers associations), screen "
            "reader users hear data cells with no column or row context."
        ),
        "how_to_fix": (
            "Mark header cells with <th> and scope, or use headers/id "
            "associations for complex tables. Purely visual layout tables "
            'should use role="presentation" or CSS layout instead.'
        ),
        "manual_review_notes": (
            "A table can be a layout table; the check skips presentation "
            "roles and trivial tables but cannot always tell intent."
        ),
        "static_check_limitations": (
            "Static heuristic on markup: needs at least two rows and two "
            "columns of data cells with no th anywhere."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.3.1 Info and Relationships."
        ),
    },
    "visual_required_not_programmatic": {
        "issue_type": "visual_required_not_programmatic",
        "title": "Required marker is visual only",
        "category": "Forms",
        "default_severity": "medium",
        "why_it_matters": (
            "The label shows * or the word 'required', but the control does "
            "not expose required state, so screen reader users are not told "
            "the field is mandatory."
        ),
        "how_to_fix": (
            'Add required or aria-required="true" to the control that the '
            "visible marker refers to."
        ),
        "manual_review_notes": (
            "Confirm the field is actually mandatory; some designs mark "
            "optional fields instead."
        ),
        "static_check_limitations": (
            "Only labels associated via for/id or wrapping are checked; "
            "required markers placed outside labels are not seen."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.3.1 Info and Relationships and "
            "SC 3.3.2 Labels or Instructions."
        ),
    },
    "fake_heading": {
        "issue_type": "fake_heading",
        "title": "Styled text may act as a heading without heading markup",
        "category": "Headings & Structure",
        "default_severity": "low",
        "why_it_matters": (
            "Large bold text that visually introduces a section is invisible "
            "to heading navigation when it is a styled div or span, so "
            "screen reader users cannot jump to it."
        ),
        "how_to_fix": (
            "Use a real heading element (h2-h6) at the right outline level "
            "instead of styling a div or span."
        ),
        "manual_review_notes": (
            "This is a review-only heuristic: decorated text (pull quotes, "
            "prices, hero taglines) can legitimately be large and bold "
            "without being a heading."
        ),
        "static_check_limitations": (
            "Only inline style attributes are inspected; stylesheet-driven "
            "fake headings are invisible statically."
        ),
        "standard_hint": (
            "Possible review point related to WCAG 2.2 SC 1.3.1 Info and "
            "Relationships; manual confirmation required."
        ),
    },
    "sensory_instruction": {
        "issue_type": "sensory_instruction",
        "title": "Instruction may rely on sensory characteristics only",
        "category": "Content",
        "default_severity": "low",
        "why_it_matters": (
            "Instructions like 'click the red button' or 'use the box on "
            "the right' can be meaningless to blind users, colorblind "
            "users, or screen reader users who cannot perceive shape, "
            "color, or position."
        ),
        "how_to_fix": (
            "Also identify the target by its name or label, for example "
            "'click the red Submit button'."
        ),
        "manual_review_notes": (
            "Keyword presence alone is not a failure: the sentence may "
            "already include the control's name, or the reference may be "
            "supplemented elsewhere. A human must read it in context."
        ),
        "static_check_limitations": (
            "English-language keyword patterns only; instructions in other "
            "languages or unusual phrasings are missed."
        ),
        "standard_hint": (
            "Possible review point related to WCAG 2.2 SC 1.3.3 Sensory "
            "Characteristics; manual confirmation required."
        ),
    },
    "missing_autocomplete": {
        "issue_type": "missing_autocomplete",
        "title": "Common personal-data field is missing an autocomplete token",
        "category": "Forms",
        "default_severity": "medium",
        "why_it_matters": (
            "autocomplete tokens let browsers and assistive tools fill and "
            "explain fields that collect the user's own information, which "
            "helps people with memory or motor difficulties."
        ),
        "how_to_fix": (
            "Add the matching autocomplete token, for example "
            'autocomplete="email" or autocomplete="given-name".'
        ),
        "manual_review_notes": (
            "Confirm the field really collects information about the user "
            "(SC 1.3.5 only applies then); fields about other people or "
            "entities are exempt."
        ),
        "static_check_limitations": (
            "Conservative token map keyed on type, name, id, and label "
            "text; search boxes, one-time codes, and ambiguous fields are "
            "skipped, so many missing tokens are not reported."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.3.5 Identify Input Purpose."
        ),
    },
    "no_bypass_mechanism": {
        "issue_type": "no_bypass_mechanism",
        "title": "No apparent way to bypass repeated navigation",
        "category": "Structure",
        "default_severity": "medium",
        "why_it_matters": (
            "Keyboard and screen reader users must move through every "
            "repeated navigation link on every page unless a skip link, "
            "main landmark, or heading structure lets them jump past it."
        ),
        "how_to_fix": (
            'Add a "Skip to main content" link as the first focusable '
            "element, and mark the main content with <main> or "
            'role="main".'
        ),
        "manual_review_notes": (
            "Fires only when a substantial navigation block exists with no "
            "skip link, no main landmark, and no headings; confirm no other "
            "bypass mechanism exists."
        ),
        "static_check_limitations": (
            "Static heuristic; visually hidden skip links that appear on "
            "focus are recognized only if present in the markup."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 2.4.1 Bypass Blocks."
        ),
    },
    "label_in_name_mismatch": {
        "issue_type": "label_in_name_mismatch",
        "title": "Visible label is missing from the accessible name",
        "category": "Interactive Elements",
        "default_severity": "medium",
        "why_it_matters": (
            "Speech-input users say the visible label to activate a "
            "control; when an aria-label replaces rather than includes the "
            "visible text, saying what they see does nothing."
        ),
        "how_to_fix": (
            "Make the accessible name start with or contain the visible "
            "label text, or remove the overriding aria-label."
        ),
        "manual_review_notes": (
            "Comparison normalizes casing, punctuation, and whitespace and "
            "does not require exact equality; judge whether a speech-input "
            "user would realistically be blocked."
        ),
        "static_check_limitations": (
            "Static text comparison; names computed from aria-labelledby "
            "chains are only partially resolved."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 2.5.3 Label in Name."
        ),
    },
    "contrast_unresolved_background": {
        "issue_type": "contrast_unresolved_background",
        "title": "Text contrast could not be resolved reliably",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "This text sits over an image, gradient, or semi-transparent "
            "background stack, so its contrast cannot be computed from CSS "
            "colors alone and may be too low."
        ),
        "how_to_fix": (
            "Measure contrast against the actual rendered background and, "
            "if needed, add a solid backing color or text shadow."
        ),
        "manual_review_notes": (
            "This is explicitly a needs-review observation, not a suspected "
            "failure: the real contrast may be fine."
        ),
        "browser_check_limitations": (
            "Reported instead of a low-contrast finding whenever the "
            "background stack contains images, gradients, or transparency "
            "the checker cannot resolve."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.4.3 Contrast (Minimum); manual "
            "confirmation required."
        ),
    },
    "small_target_size": {
        "issue_type": "small_target_size",
        "title": "Interactive target is smaller than 24x24 CSS pixels",
        "category": "Low Vision",
        "default_severity": "medium",
        "why_it_matters": (
            "Small touch/click targets placed near other targets are hard "
            "to hit for people with tremor, limited dexterity, or large "
            "pointers."
        ),
        "how_to_fix": (
            "Make the target at least 24x24 CSS pixels, or give it enough "
            "surrounding space that a 24 px circle centered on it does not "
            "intersect another target."
        ),
        "manual_review_notes": (
            "WCAG 2.5.8 has exceptions (equivalent control elsewhere, "
            "inline text links, browser defaults, essential presentation); "
            "inline links and spaced targets are already excluded, but the "
            "equivalent-control exception needs human judgment."
        ),
        "browser_check_limitations": (
            "Measured in one Chromium run at default zoom; CSS hit areas "
            "extended through pseudo-elements are not seen."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 2.5.8 Target Size (Minimum)."
        ),
    },
    "focus_obscured": {
        "issue_type": "focus_obscured",
        "title": "Focused control is covered by overlaying content",
        "category": "Low Vision",
        "default_severity": "high",
        "why_it_matters": (
            "When a sticky header, fixed footer, cookie banner, or floating "
            "widget covers the focused control, keyboard users cannot see "
            "where they are."
        ),
        "how_to_fix": (
            "Use scroll-padding or scroll-margin so focused elements scroll "
            "clear of fixed overlays, or make overlays dismissible."
        ),
        "manual_review_notes": (
            "Partial covering is reported at lower confidence; confirm how "
            "much of the control stays visible while focused."
        ),
        "browser_check_limitations": (
            "Bounding-box and hit-test sampling in one run; overlays that "
            "appear only after user actions are not seen."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum)."
        ),
    },
    "text_spacing_content_loss": {
        "issue_type": "text_spacing_content_loss",
        "title": "Content breaks under WCAG text-spacing overrides",
        "category": "Low Vision",
        "default_severity": "high",
        "why_it_matters": (
            "People who need wider line, letter, and word spacing apply "
            "user stylesheets; content that clips, overlaps, or disappears "
            "under the WCAG reference overrides is lost to them."
        ),
        "how_to_fix": (
            "Avoid fixed-height text containers and overflow: hidden on "
            "text; let containers grow with their content."
        ),
        "manual_review_notes": (
            "Before/after bounding boxes are included; confirm the loss "
            "with a text-spacing bookmarklet in a visible browser."
        ),
        "browser_check_limitations": (
            "Applies line-height 1.5, paragraph spacing 2em, letter "
            "spacing 0.12em, and word spacing 0.16em in one Chromium run; "
            "JavaScript that reacts to layout changes is not modeled."
        ),
        "standard_hint": (
            "Related to WCAG 2.2 SC 1.4.12 Text Spacing."
        ),
    },
    "meaningful_sequence_reorder": {
        "issue_type": "meaningful_sequence_reorder",
        "title": "CSS may reorder content away from DOM order",
        "category": "Structure",
        "default_severity": "low",
        "why_it_matters": "Screen reader and keyboard users follow DOM/focus order, so visual reordering can make content hard to understand when order conveys meaning.",
        "how_to_fix": "Keep meaningful sequence in the DOM, or verify visual reordering does not change meaning.",
        "manual_review_notes": "Compare DOM, visual, and focus order. CSS order alone is not a failure.",
        "static_check_limitations": "Only inline CSS order/grid placement is inspected; final layout needs browser review.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 1.3.2 Meaningful Sequence.",
    },
    "orientation_restriction": {
        "issue_type": "orientation_restriction",
        "title": "Page may restrict use to one orientation",
        "category": "Responsive Layout",
        "default_severity": "medium",
        "why_it_matters": "People using mounted devices or fixed displays may be unable to rotate their screen.",
        "how_to_fix": "Support both portrait and landscape unless a specific orientation is essential.",
        "manual_review_notes": "Confirm content or functionality is actually restricted, not merely adapted responsively.",
        "static_check_limitations": "Requires strong static evidence such as rotate messaging, orientation-lock code, or hidden content in an orientation media query.",
        "standard_hint": "Partial evidence related to WCAG 2.2 SC 1.3.4 Orientation.",
    },
    "color_only_indicator": {
        "issue_type": "color_only_indicator",
        "title": "Color may be the only indicator",
        "category": "Low Vision",
        "default_severity": "low",
        "why_it_matters": "Users who cannot perceive color differences may miss status, selection, required, or error cues.",
        "how_to_fix": "Add text, an icon, border, underline, pattern, shape, or ARIA state in addition to color.",
        "manual_review_notes": "Needs human review; static evidence cannot prove color is the only perceivable cue.",
        "static_check_limitations": "Checks class/style/status cues and known non-color exceptions, but does not compute final styles.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 1.4.1 Use of Color.",
    },
    "autoplay_audio_no_control": {
        "issue_type": "autoplay_audio_no_control",
        "title": "Autoplaying audio may lack independent controls",
        "category": "Media",
        "default_severity": "medium",
        "why_it_matters": "Autoplaying audio can interfere with screen readers and concentration if users cannot pause or control it.",
        "how_to_fix": "Avoid autoplay or provide pause/stop and volume controls independent of system volume.",
        "manual_review_notes": "Confirm duration, custom controls, and whether audio starts automatically in the rendered page.",
        "static_check_limitations": "Only native audio autoplay without controls is detected statically.",
        "standard_hint": "Partial evidence related to WCAG 2.2 SC 1.4.2 Audio Control.",
    },
    "image_of_text": {
        "issue_type": "image_of_text",
        "title": "Graphic appears to contain text",
        "category": "Images",
        "default_severity": "low",
        "why_it_matters": "Text embedded in images does not adapt as well to user text settings and may pixelate or be unavailable to assistive tools.",
        "how_to_fix": "Use real text where possible, or confirm an image-of-text exception applies.",
        "manual_review_notes": "Review whether the graphic is essential, a logo, or can be replaced by styled text.",
        "static_check_limitations": "Uses SVG text or filename heuristics; no OCR is performed.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 1.4.5 Images of Text.",
    },
    "hover_focus_content": {
        "issue_type": "hover_focus_content",
        "title": "Hover or focus may reveal additional content",
        "category": "Interaction",
        "default_severity": "low",
        "why_it_matters": "People using magnification, keyboard, or pointer alternatives can lose hover/focus content if it cannot be dismissed, hovered, or kept visible.",
        "how_to_fix": "Make hover/focus content dismissible, hoverable, and persistent until dismissed or focus/hover moves away.",
        "manual_review_notes": "Test in a browser; native title tooltips are not fully testable here.",
        "static_check_limitations": "Static event/CSS evidence only; behavior must be confirmed interactively.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 1.4.13 Content on Hover or Focus.",
    },
    "single_character_shortcut": {
        "issue_type": "single_character_shortcut",
        "title": "Single-character keyboard shortcut may be active",
        "category": "Keyboard Interaction",
        "default_severity": "medium",
        "why_it_matters": "Speech input users and keyboard users can accidentally trigger unmodified character shortcuts.",
        "how_to_fix": "Provide a way to turn off, remap, or require modifiers for character shortcuts.",
        "manual_review_notes": "Verify shortcuts do not trigger while typing and that a disable/remap option exists.",
        "static_check_limitations": "Script heuristic; minified or delegated listeners may be ambiguous.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.1.4 Character Key Shortcuts.",
    },
    "timing_adjustable_missing": {
        "issue_type": "timing_adjustable_missing",
        "title": "Timed behavior may not be adjustable",
        "category": "Timing",
        "default_severity": "medium",
        "why_it_matters": "Users may need more time to read, type, or complete tasks.",
        "how_to_fix": "Let users extend, disable, or adjust time limits unless an exception applies.",
        "manual_review_notes": "Confirm the timeout exists, its duration, and whether it is essential or adjustable.",
        "static_check_limitations": "Detects meta refresh, timeout scripts, and visible countdown language only.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.2.1 Timing Adjustable.",
    },
    "moving_content_no_pause": {
        "issue_type": "moving_content_no_pause",
        "title": "Auto-moving content may lack pause controls",
        "category": "Motion",
        "default_severity": "medium",
        "why_it_matters": "Moving or updating content can distract users and make content hard to read.",
        "how_to_fix": "Provide pause, stop, hide, or update-frequency controls for long-running movement.",
        "manual_review_notes": "Confirm the motion lasts more than five seconds and is not a required progress indicator.",
        "static_check_limitations": "Detects common carousel/ticker/marquee/autoplay evidence and visible pause controls.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.2.2 Pause, Stop, Hide.",
    },
    "possible_flashing_content": {
        "issue_type": "possible_flashing_content",
        "title": "Animation may flash rapidly",
        "category": "Motion",
        "default_severity": "medium",
        "why_it_matters": "Rapid flashing can trigger seizures for some users.",
        "how_to_fix": "Avoid rapid flashing or verify flash thresholds with a specialized tool.",
        "manual_review_notes": "This is review evidence only; threshold testing requires visual analysis.",
        "static_check_limitations": "Looks for flash/blink keyframes and fast durations in CSS.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.3.1 Three Flashes or Below Threshold.",
    },
    "interaction_motion_no_reduced_motion": {
        "issue_type": "interaction_motion_no_reduced_motion",
        "title": "Interaction-triggered motion lacks reduced-motion evidence",
        "category": "Motion",
        "default_severity": "low",
        "why_it_matters": "Non-essential motion triggered by interaction can cause vestibular discomfort.",
        "how_to_fix": "Respect prefers-reduced-motion or provide a control to disable non-essential motion.",
        "manual_review_notes": "Confirm motion is non-essential and triggered by user interaction.",
        "static_check_limitations": "CSS-only heuristic for transform/animation on hover/focus/active.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.3.3 Animation from Interactions.",
    },
    "pointer_gesture_no_alternative": {
        "issue_type": "pointer_gesture_no_alternative",
        "title": "Function may require a path or multipoint gesture",
        "category": "Pointer Interaction",
        "default_severity": "medium",
        "why_it_matters": "Users with limited dexterity may be unable to perform swipes, pinches, or path gestures.",
        "how_to_fix": "Provide simple pointer alternatives such as buttons, menus, fields, or steppers.",
        "manual_review_notes": "Confirm the gesture is required and no single-pointer alternative exists.",
        "static_check_limitations": "Event-name heuristic; rendered behavior must be verified.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.5.1 Pointer Gestures.",
    },
    "pointer_down_activation": {
        "issue_type": "pointer_down_activation",
        "title": "Control may activate on pointer down",
        "category": "Pointer Interaction",
        "default_severity": "medium",
        "why_it_matters": "Down-event activation can prevent users from aborting an accidental pointer action.",
        "how_to_fix": "Activate on pointer-up, support cancellation by moving away, or provide undo.",
        "manual_review_notes": "Confirm down-event activation is not essential and cancellation/undo is unavailable.",
        "static_check_limitations": "Requires strong event evidence and absence of obvious pointer-up/cancel handlers.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.5.2 Pointer Cancellation.",
    },
    "dragging_no_alternative": {
        "issue_type": "dragging_no_alternative",
        "title": "Function may require dragging",
        "category": "Pointer Interaction",
        "default_severity": "medium",
        "why_it_matters": "Drag operations can be hard or impossible for users with limited pointer precision.",
        "how_to_fix": "Provide non-drag alternatives such as buttons, menus, keyboard commands, or direct input.",
        "manual_review_notes": "Confirm dragging is required for operation, not just an optional shortcut.",
        "static_check_limitations": "Detects draggable markup or drag/drop script names and visible alternatives.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 2.5.7 Dragging Movements.",
    },
    "focus_context_change": {
        "issue_type": "focus_context_change",
        "title": "Focus may trigger a context change",
        "category": "Interaction",
        "default_severity": "medium",
        "why_it_matters": "Changing context on focus can disorient keyboard and assistive technology users.",
        "how_to_fix": "Do not navigate, submit, open modals, or move focus until explicit activation.",
        "manual_review_notes": "Verify focusing alone causes the change; visual focus styling is expected and should not be flagged.",
        "static_check_limitations": "Inline onfocus handlers only; external scripts may be missed.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 3.2.1 On Focus.",
    },
    "input_context_change": {
        "issue_type": "input_context_change",
        "title": "Changing a control may trigger a context change",
        "category": "Interaction",
        "default_severity": "medium",
        "why_it_matters": "Unexpected navigation, submission, or focus movement after input can disorient users.",
        "how_to_fix": "Warn users before context changes or require an explicit submit/activate action.",
        "manual_review_notes": "Verify the context change occurs merely from changing the value.",
        "static_check_limitations": "Inline oninput/onchange handlers only; external scripts may be missed.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 3.2.2 On Input.",
    },
    "error_not_identified": {
        "issue_type": "error_not_identified",
        "title": "Error message may not identify the affected field",
        "category": "Forms",
        "default_severity": "medium",
        "why_it_matters": "Users need to know which field has an error and what state it is in.",
        "how_to_fix": "Identify the affected field in text and connect errors with aria-describedby and/or aria-invalid.",
        "manual_review_notes": "Submit only local or permitted test forms with synthetic data to confirm behavior.",
        "static_check_limitations": "Static error markup only; runtime validation may differ.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 3.3.1 Error Identification.",
    },
    "error_suggestion_missing": {
        "issue_type": "error_suggestion_missing",
        "title": "Error message may lack a correction suggestion",
        "category": "Forms",
        "default_severity": "low",
        "why_it_matters": "When a correction is known, users benefit from guidance such as the required format or missing value.",
        "how_to_fix": "Explain how to fix the error where a useful suggestion is possible.",
        "manual_review_notes": "Do not judge subjective writing quality; look for practical correction guidance.",
        "static_check_limitations": "Static text heuristic for common suggestion words.",
        "standard_hint": "Supporting evidence related to WCAG 2.2 SC 3.3.3 Error Suggestion.",
    },
}

# Attach default confidence to every rule so --rule output and reports can
# state it without repeating the table above.
for _issue_type, _rule in RULES.items():
    _rule["default_confidence"] = DEFAULT_CONFIDENCE_BY_RULE.get(
        _issue_type, FALLBACK_CONFIDENCE
    )


def get_rule(issue_type: str) -> dict | None:
    """Return the registry entry for an issue type, or None if unknown."""
    return RULES.get(issue_type)


def list_rules() -> list[dict]:
    """Return all registered rules in a stable order."""
    return list(RULES.values())


def enrich_issue_with_rule(issue: AccessibilityIssue | dict) -> dict:
    """Attach report-ready rule metadata to an issue.

    Accepts either an AccessibilityIssue or an already-built issue dict and
    returns a dict. Unknown issue types are returned unchanged so reports
    never break on new checks.
    """
    if isinstance(issue, AccessibilityIssue):
        issue_dict = {
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "agent_name": issue.agent_name,
            "message": issue.title,
            "evidence": issue.evidence,
            "suggested_fix": issue.suggested_fix,
        }
        if issue.confidence:
            issue_dict["confidence"] = issue.confidence
    else:
        issue_dict = dict(issue)

    issue_type = issue_dict.get("issue_type", "")
    rule = get_rule(issue_type)
    if rule:
        issue_dict["rule"] = {
            field: rule[field] for field in REPORT_RULE_FIELDS if field in rule
        }

    if not issue_dict.get("confidence"):
        issue_dict["confidence"] = DEFAULT_CONFIDENCE_BY_RULE.get(
            issue_type, FALLBACK_CONFIDENCE
        )

    wcag = wcag_mappings_for_issue_type(issue_type)
    if wcag:
        issue_dict["wcag"] = [
            {
                "sc": item["sc"],
                "name": item["name"],
                "level": item["level"],
                "coverage": item["coverage"],
                "manual_check": item["manual_check"],
            }
            for item in wcag
        ]

    return issue_dict
