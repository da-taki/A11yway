"""Central registry describing every static issue type A11yway can report.

Each rule documents what a check detects, why it matters for students, how
to fix it, and what the static prototype cannot verify. Reports use this
registry so reviewers can understand findings without reading the code.
"""

from __future__ import annotations

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
}


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
    else:
        issue_dict = dict(issue)

    rule = get_rule(issue_dict.get("issue_type", ""))
    if rule:
        issue_dict["rule"] = {
            field: rule[field] for field in REPORT_RULE_FIELDS if field in rule
        }

    return issue_dict
