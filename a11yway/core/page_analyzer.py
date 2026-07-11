"""Static HTML analysis helpers.

Future versions can use this module to inspect browser state, computed
styles, PDF files, and accessibility trees. For now, these checks use the
Python standard library and intentionally stay conservative.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from typing import Any

from a11yway.core.indic_checks import analyze_indic_language
from a11yway.models.issue import AccessibilityIssue


IGNORED_INPUT_TYPES = {"hidden", "submit", "button", "reset"}
GENERIC_LINK_TEXT = {"click here", "here", "read more", "more", "link", "learn more"}

# Filenames that almost always mean a decorative or spacer image.
DECORATIVE_SRC_PATTERN = re.compile(
    r"(spacer|pixel|blank|transparent|divider|shim|corner|dot|bullet)[^/]*\.(gif|png|svg|webp|jpg)",
    re.IGNORECASE,
)

# Filenames that suggest an image carries information a reviewer should see.
INFORMATIVE_SRC_PATTERN = re.compile(
    r"(chart|diagram|graph|infographic|screenshot|map|figure)[^/]*\.(gif|png|svg|webp|jpg|jpeg)",
    re.IGNORECASE,
)

# Tags browsers close implicitly when a new tag of the same name starts.
# Real pages often omit these end tags; without this rule one unclosed
# <label> or <a> would wrap the rest of the document and hide findings.
IMPLICITLY_CLOSED_TAGS = {
    "a", "button", "label", "select", "textarea", "option",
    "p", "li", "td", "th", "tr",
    "h1", "h2", "h3", "h4", "h5", "h6",
}

# Elements whose raw text browsers never render as page content.
NON_RENDERED_TEXT_TAGS = {"script", "style", "template"}
STATIC_CHECKS_RUN = [
    "html_form_labels",
    "interactive_names",
    "image_alt_text",
    "heading_structure",
    "page_metadata",
    "media_accessibility",
    "indic_language_checks",
    "structure_relationships",
    "sensory_instructions",
    "input_purpose",
    "bypass_blocks",
    "label_in_name",
    "wcag_static_evidence",
]


@dataclass
class HTMLElement:
    """Small parsed element record used by static checks."""

    tag: str
    attrs: dict[str, str]
    parent_tags: list[str]
    text_parts: list[str] = field(default_factory=list)
    child_images: list[dict[str, str]] = field(default_factory=list)
    track_kinds: list[str] = field(default_factory=list)
    wrapped_by_label: bool = False
    line: int | None = None
    start_tag_snippet: str = ""
    # References to the open ancestor elements at parse time. Ancestors keep
    # collecting text after this element is created, so post-parse checks can
    # read final ancestor state (attributes, text) through these references.
    ancestors: list["HTMLElement"] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Return normalized visible text collected inside this element."""
        return normalize_text(" ".join(self.text_parts))


class _StaticHTMLParser(HTMLParser):
    """Tiny parser that records enough HTML structure for static checks."""

    def __init__(self, source_html: str) -> None:
        super().__init__()
        self.source_html = source_html
        self.elements: list[HTMLElement] = []
        self.label_for_values: set[str] = set()
        self.html_attrs: dict[str, str] = {}
        self.html_element: HTMLElement | None = None
        self.title_text = ""
        self.document_text_parts: list[str] = []
        self._open_elements: list[HTMLElement] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}

        if tag_name in IMPLICITLY_CLOSED_TAGS and any(
            item.tag == tag_name for item in self._open_elements
        ):
            self.handle_endtag(tag_name)

        if tag_name == "html":
            self.html_attrs = attrs_dict

        if tag_name == "label":
            label_for = attrs_dict.get("for")
            if label_for:
                self.label_for_values.add(label_for)

        element = HTMLElement(
            tag=tag_name,
            attrs=attrs_dict,
            parent_tags=[item.tag for item in self._open_elements],
            wrapped_by_label=any(item.tag == "label" for item in self._open_elements),
            line=self.getpos()[0],
            start_tag_snippet=self.get_starttag_text()
            or build_start_tag_snippet(tag_name, attrs_dict),
            ancestors=list(self._open_elements),
        )
        self.elements.append(element)

        if tag_name == "img":
            for open_element in reversed(self._open_elements):
                if open_element.tag in {"a", "button"}:
                    open_element.child_images.append(attrs_dict)
                    break

        if tag_name == "track":
            for open_element in reversed(self._open_elements):
                if open_element.tag in {"video", "audio"}:
                    open_element.track_kinds.append(attrs_dict.get("kind", "").lower())
                    break

        if tag_name == "html":
            self.html_element = element

        if tag_name not in {"input", "img", "br", "hr", "meta", "link", "track"}:
            self._open_elements.append(element)

    def handle_endtag(self, tag: str) -> None:
        tag_name = tag.lower()

        for index in range(len(self._open_elements) - 1, -1, -1):
            if self._open_elements[index].tag == tag_name:
                # Elements above the match never got an end tag; browsers
                # close them here too, so drop them instead of letting them
                # wrap the rest of the document.
                closed = self._open_elements[index:]
                del self._open_elements[index:]
                for element in closed:
                    if element.tag == "title" and not self.title_text:
                        self.title_text = element.text
                return

    def handle_data(self, data: str) -> None:
        if any(item.tag in NON_RENDERED_TEXT_TAGS for item in self._open_elements):
            return

        normalized = normalize_text(data)
        if not normalized:
            return

        self.document_text_parts.append(normalized)

        for element in self._open_elements:
            element.text_parts.append(normalized)

    def close(self) -> None:
        super().close()
        if not self.title_text:
            for element in self._open_elements:
                if element.tag == "title":
                    self.title_text = element.text
                    break

    @property
    def document_text(self) -> str:
        """Return normalized document text."""
        return normalize_text(" ".join(self.document_text_parts))


def normalize_text(value: str) -> str:
    """Collapse whitespace for simple static comparisons."""
    return " ".join(value.split())


def _parse_html(html: str) -> _StaticHTMLParser:
    """Parse HTML into a small reusable snapshot.

    Severely malformed markup must never crash a static audit, so any
    parser error keeps whatever was parsed before the failure.
    """
    parser = _StaticHTMLParser(html)
    try:
        parser.feed(html)
        parser.close()
    except Exception:  # noqa: BLE001 - degrade to partial results, never crash
        pass
    return parser


def estimate_line_number(source_html: str, snippet: str) -> int | None:
    """Estimate the 1-based line number for a snippet in source HTML.

    This is approximate. Static parsing does not know the rendered DOM or
    browser-repaired markup, so reports should treat this as a helpful pointer.
    """
    if not snippet:
        return None

    index = source_html.find(snippet)
    if index == -1:
        return None
    return source_html.count("\n", 0, index) + 1


def _shorten(value: str, max_length: int = 200) -> str:
    """Keep evidence snippets compact."""
    normalized = normalize_text(value)
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def build_start_tag_snippet(tag: str, attrs: dict[str, str]) -> str:
    """Build a readable start-tag snippet from parsed attributes."""
    attr_parts = []
    for name, value in attrs.items():
        if value == "":
            attr_parts.append(name)
        else:
            attr_parts.append(f'{name}="{escape(value, quote=True)}"')

    attrs_text = f" {' '.join(attr_parts)}" if attr_parts else ""
    return _shorten(f"<{tag}{attrs_text}>")


def _element_snippet(element: HTMLElement) -> str:
    """Return a short element snippet for evidence."""
    start_tag = element.start_tag_snippet or build_start_tag_snippet(
        element.tag,
        element.attrs,
    )
    if element.tag in {"a", "button"} and element.text:
        return _shorten(f"{start_tag}{element.text}</{element.tag}>")
    return _shorten(start_tag)


def _element_evidence(
    element: HTMLElement,
    reason: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build structured evidence for an element-level issue."""
    evidence: dict[str, Any] = {
        "tag": element.tag,
        "line": element.line,
        "snippet": _element_snippet(element),
        "reason": reason,
    }

    for key in ["type", "id", "name", "href", "src"]:
        value = element.attrs.get(key)
        if value:
            evidence[key] = value

    if element.tag == "input" and "type" not in evidence:
        evidence["type"] = "text"

    if element.text:
        evidence["text"] = element.text

    if extra:
        evidence.update({key: value for key, value in extra.items() if value not in ["", None]})

    return evidence


def _page_evidence(
    tag: str,
    reason: str,
    line: int | None = None,
    snippet: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build structured evidence for a page-level issue."""
    evidence: dict[str, Any] = {
        "tag": tag,
        "line": line,
        "reason": reason,
    }
    if snippet:
        evidence["snippet"] = _shorten(snippet)
    if extra:
        evidence.update({key: value for key, value in extra.items() if value not in ["", None]})
    return evidence


def _has_accessible_name(element: HTMLElement) -> bool:
    """Return whether an element has a simple static accessible name."""
    if element.attrs.get("aria-label") or element.attrs.get("aria-labelledby"):
        return True
    if element.attrs.get("title"):
        return True
    if element.text:
        return True

    for image in element.child_images:
        if image.get("alt"):
            return True

    return False


_HIDDEN_STYLE_PATTERN = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden")


def _attrs_mark_hidden(attrs: dict[str, str]) -> bool:
    """Return whether one element's attributes hide it from all users."""
    if "hidden" in attrs:
        return True
    if attrs.get("aria-hidden", "").lower() == "true":
        return True
    style = attrs.get("style", "").lower()
    return bool(style and _HIDDEN_STYLE_PATTERN.search(style))


def _element_is_hidden(element: HTMLElement) -> bool:
    """Return whether an element or any ancestor is statically hidden.

    Hidden templates, inert helpers, and offscreen implementation controls
    should not produce findings: users never reach them.
    """
    if _attrs_mark_hidden(element.attrs):
        return True
    return any(_attrs_mark_hidden(ancestor.attrs) for ancestor in element.ancestors)


def _element_is_inactive(element: HTMLElement) -> bool:
    """Return whether static evidence says an element is not active content."""
    if _element_is_hidden(element):
        return True
    if element.tag == "template" or "template" in element.parent_tags:
        return True
    if "inert" in element.attrs:
        return True
    return any("inert" in ancestor.attrs for ancestor in element.ancestors)


def _nearest_ancestor(element: HTMLElement, tags: set[str]) -> HTMLElement | None:
    """Return the closest ancestor whose tag is in tags, if any."""
    for ancestor in reversed(element.ancestors):
        if ancestor.tag in tags:
            return ancestor
    return None


def _normalize_name_text(value: str) -> str:
    """Normalize label text for name comparisons (casing, punctuation, space)."""
    lowered = value.casefold()
    cleaned = re.sub(r"[^\w\s]", " ", lowered, flags=re.UNICODE)
    return " ".join(cleaned.split())


def _control_identity(control: HTMLElement) -> str:
    """Return a short control identity for evidence."""
    identity_parts = []
    control_id = control.attrs.get("id", "")
    control_name = control.attrs.get("name", "")

    if control_id:
        identity_parts.append(f'id="{control_id}"')
    if control_name:
        identity_parts.append(f'name="{control_name}"')

    return ", ".join(identity_parts) if identity_parts else "no id or name"


def _issue(
    title: str,
    issue_type: str,
    severity: str,
    evidence: str | dict[str, Any],
    suggested_fix: str,
    agent_name: str = "Page Analyzer",
) -> AccessibilityIssue:
    """Create a static analyzer issue."""
    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name=agent_name,
        evidence=evidence,
        suggested_fix=suggested_fix,
    )


def analyze_html_forms(html: str) -> list[AccessibilityIssue]:
    """Detect form controls that appear to be missing accessible labels."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for control in parser.elements:
        if control.tag not in {"input", "textarea", "select"}:
            continue

        input_type = control.attrs.get("type", "text").lower()
        if control.tag == "input" and input_type in IGNORED_INPUT_TYPES:
            continue

        # Hidden or non-user-facing controls (templates, inert helpers,
        # implementation details) never reach users, so they are not flagged.
        if _element_is_hidden(control):
            continue

        control_id = control.attrs.get("id", "")
        has_label_for = bool(control_id and control_id in parser.label_for_values)
        has_wrapping_label = control.wrapped_by_label
        has_aria_label = bool(control.attrs.get("aria-label"))
        has_aria_labelledby = bool(control.attrs.get("aria-labelledby"))
        has_title = bool(control.attrs.get("title"))

        if any(
            [
                has_label_for,
                has_wrapping_label,
                has_aria_label,
                has_aria_labelledby,
                has_title,
            ]
        ):
            continue

        has_placeholder = bool(control.attrs.get("placeholder"))
        reason = "Form control has no accessible label."
        if has_placeholder:
            reason = (
                "Form control has only a placeholder, which disappears while "
                "typing and is not a programmatic label."
            )
        issues.append(
            _issue(
                title="Form control is missing an accessible label",
                issue_type="missing_form_label",
                severity="high",
                evidence=_element_evidence(
                    control,
                    reason,
                    {
                        "type": input_type,
                        "identity": _control_identity(control),
                        "placeholder_only": has_placeholder or None,
                    },
                ),
                suggested_fix=(
                    "Add a visible <label> connected with for/id. Use aria-label only "
                    "when a visible label is not possible."
                ),
            )
        )

    return issues


def analyze_interactive_names(html: str) -> list[AccessibilityIssue]:
    """Detect links and buttons with missing or weak accessible names."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for element in parser.elements:
        if element.tag in {"button", "a"} and _element_is_hidden(element):
            continue

        if element.tag == "button" and not _has_accessible_name(element):
            issues.append(
                _issue(
                    title="Button is missing an accessible name",
                    issue_type="missing_button_name",
                    severity="high",
                    evidence=_element_evidence(
                        element,
                        "Button has no visible text, aria-label, title, or image alt text.",
                    ),
                    suggested_fix="Add clear button text or an aria-label that describes the button action.",
                )
            )

        if element.tag != "a" or "href" not in element.attrs:
            continue

        if not _has_accessible_name(element):
            issues.append(
                _issue(
                    title="Link is missing an accessible name",
                    issue_type="missing_link_name",
                    severity="high",
                    evidence=_element_evidence(
                        element,
                        "Link has no usable text, aria-label, title, or image alt text.",
                    ),
                    suggested_fix="Add descriptive link text that explains the link destination or action.",
                )
            )
            continue

        # The accessible name, not the visible phrase, is what link lists
        # announce. A generic visible phrase is acceptable when aria-label
        # or aria-labelledby gives the link a specific computed name.
        if element.attrs.get("aria-labelledby"):
            continue
        accessible_name = (element.attrs.get("aria-label") or element.text).lower().strip()
        if accessible_name in GENERIC_LINK_TEXT:
            issues.append(
                _issue(
                    title="Link text is too generic",
                    issue_type="generic_link_text",
                    severity="medium",
                    evidence=_element_evidence(
                        element,
                        "The link's accessible name is generic and does not explain the destination or action.",
                    ),
                    suggested_fix='Use descriptive link text like "Download scholarship guidelines" instead of "click here."',
                )
            )

    return issues


def _action_has_name_besides_image(action: HTMLElement, image: HTMLElement) -> bool:
    """Return whether a link/button has an accessible name beyond this image."""
    if action.attrs.get("aria-label") or action.attrs.get("aria-labelledby"):
        return True
    if action.attrs.get("title"):
        return True
    if action.text:
        return True
    for child in action.child_images:
        # child_images stores the same attrs dict object created at parse
        # time, so identity distinguishes this image from sibling images.
        if child is not image.attrs and child.get("alt"):
            return True
    return False


def _looks_decorative(image: HTMLElement) -> bool:
    """Return whether static evidence says the image is decorative."""
    src = image.attrs.get("src", "")
    if DECORATIVE_SRC_PATTERN.search(src):
        return True
    try:
        width = int(image.attrs.get("width", ""))
        height = int(image.attrs.get("height", ""))
    except ValueError:
        return False
    return width <= 16 and height <= 16


def analyze_images(html: str) -> list[AccessibilityIssue]:
    """Detect images that appear to be missing useful alt text.

    alt="" is the standard decorative marker, so it is respected by default.
    An empty alt is flagged only when the image appears interactive (the only
    content of an unnamed link or button) or looks informative by filename.
    """
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for image in parser.elements:
        if image.tag != "img":
            continue
        if _element_is_hidden(image):
            continue

        alt = image.attrs.get("alt")
        role = image.attrs.get("role", "").lower()
        aria_hidden = image.attrs.get("aria-hidden", "").lower()
        explicitly_decorative = (
            role in {"presentation", "none"}
            or aria_hidden == "true"
            or image.attrs.get("data-decorative") == "true"
        )
        action = _nearest_ancestor(image, {"a", "button"})
        action_needs_this_image = bool(
            action and not _action_has_name_besides_image(action, image)
        )

        if alt is None:
            if explicitly_decorative:
                continue
            if action_needs_this_image:
                severity, confidence = "high", "likely"
                reason = (
                    "This image is the only content of a link or button, and "
                    "it has no alt attribute, so the control has no name."
                )
            elif _looks_decorative(image):
                severity, confidence = "low", "needs_review"
                reason = (
                    "Image has no alt attribute. Its filename or size suggests "
                    'decoration; if so, alt="" is the right fix.'
                )
            else:
                severity, confidence = "medium", "likely"
                reason = "Image has no alt attribute."
            issues.append(
                _issue(
                    title="Image is missing useful alt text",
                    issue_type="missing_image_alt",
                    severity=severity,
                    evidence=_element_evidence(image, reason),
                    suggested_fix=(
                        "Add alt text that describes the image purpose, or mark "
                        'decorative images with alt="".'
                    ),
                ),
            )
            issues[-1].confidence = confidence
            continue

        if alt != "" or explicitly_decorative:
            continue

        # alt="" cases: respect the decorative declaration unless the image
        # is clearly load-bearing.
        if action_needs_this_image:
            issues.append(
                _issue(
                    title="Image is missing useful alt text",
                    issue_type="missing_image_alt",
                    severity="high",
                    evidence=_element_evidence(
                        image,
                        'This image has alt="" but is the only content of a '
                        "link or button, so the control has no accessible name.",
                    ),
                    suggested_fix=(
                        "Describe the control's action in the image alt text or "
                        "in an aria-label on the link or button."
                    ),
                )
            )
        elif INFORMATIVE_SRC_PATTERN.search(image.attrs.get("src", "")):
            issues.append(
                _issue(
                    title="Empty alt on an image that looks informative",
                    issue_type="image_empty_alt_suspicious",
                    severity="low",
                    evidence=_element_evidence(
                        image,
                        'Image has alt="" but its filename suggests informative '
                        "content (chart, diagram, map, screenshot).",
                    ),
                    suggested_fix=(
                        "If the image is informative, describe it in alt text; "
                        'if it is decorative, alt="" is already correct.'
                    ),
                )
            )

    return issues


def analyze_heading_structure(html: str) -> list[AccessibilityIssue]:
    """Detect simple heading structure problems."""
    parser = _parse_html(html)
    headings = [
        (int(element.tag[1]), element)
        for element in parser.elements
        if element.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    issues: list[AccessibilityIssue] = []

    h1_count = sum(1 for level, _element in headings if level == 1)
    if h1_count == 0:
        issues.append(
            _issue(
                title="Page is missing an h1",
                issue_type="missing_h1",
                severity="medium",
                evidence=_page_evidence(
                    "html",
                    "Document has no h1 heading.",
                    line=parser.html_element.line if parser.html_element else None,
                    snippet=parser.html_element.start_tag_snippet if parser.html_element else "",
                ),
                suggested_fix="Add one clear h1 that matches the page purpose.",
            )
        )
    elif h1_count > 1:
        issues.append(
            _issue(
                title="Page has multiple h1 headings",
                issue_type="multiple_h1",
                severity="low",
                evidence=_page_evidence(
                    "h1",
                    "Document has multiple h1 headings. This is valid HTML and "
                    "often intentional; review evidence only.",
                    extra={"count": h1_count},
                ),
                suggested_fix="If heading navigation feels ambiguous, use one main h1 for the page purpose, then organize sections with h2 and lower headings.",
            )
        )

    previous_level: int | None = None
    previous_region: tuple | None = None
    for level, element in headings:
        region = _independent_region_signature(element)
        # Headings inside a different independent region (article, named
        # region/complementary landmark) legitimately restart their levels,
        # so consecutive headings are only compared within one region.
        if region != previous_region:
            previous_level = None
            previous_region = region
        if previous_level is not None and level > previous_level + 1:
            issues.append(
                _issue(
                    title="Heading level is skipped",
                    issue_type="skipped_heading_level",
                    severity="medium",
                    evidence=_element_evidence(
                        element,
                        f"Heading level jumps from h{previous_level} to h{level}.",
                        {"previous_level": previous_level, "level": level},
                    ),
                    suggested_fix="Do not skip heading levels; move from h1 to h2 before h3.",
                )
            )
        previous_level = level

    return issues


def _independent_region_signature(element: HTMLElement) -> tuple:
    """Return an identity for the independent region a heading belongs to.

    Articles and labeled landmark regions are treated as independent
    components whose headings restart; plain sections and divs are not,
    because they usually continue the page outline.
    """
    for ancestor in reversed(element.ancestors):
        role = ancestor.attrs.get("role", "").lower()
        if ancestor.tag == "article":
            return ("article", id(ancestor))
        if role in {"region", "complementary"} and (
            ancestor.attrs.get("aria-label") or ancestor.attrs.get("aria-labelledby")
        ):
            return (role, id(ancestor))
    return ()


def analyze_page_metadata(html: str) -> list[AccessibilityIssue]:
    """Detect missing page title and document language metadata."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    if not parser.title_text:
        issues.append(
            _issue(
                title="Page is missing a title",
                issue_type="missing_page_title",
                severity="medium",
                evidence=_page_evidence(
                    "title",
                    "No non-empty title element was found.",
                ),
                suggested_fix="Add a short, descriptive page title.",
            )
        )

    if not parser.html_attrs.get("lang"):
        issues.append(
            _issue(
                title="HTML document is missing a language",
                issue_type="missing_html_lang",
                severity="medium",
                evidence=_page_evidence(
                    "html",
                    "The html element does not include a lang attribute.",
                    line=parser.html_element.line if parser.html_element else None,
                    snippet=parser.html_element.start_tag_snippet if parser.html_element else "",
                ),
                suggested_fix='Add lang="en" or the correct document language to the <html> element.',
            )
        )

    return issues


def analyze_media_accessibility(html: str) -> list[AccessibilityIssue]:
    """Detect basic media accessibility gaps."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []
    has_transcript_text = "transcript" in parser.document_text.lower()

    for media in parser.elements:
        if media.tag == "video":
            has_captions = any(kind in {"captions", "subtitles"} for kind in media.track_kinds)
            if not has_captions:
                issues.append(
                    _issue(
                        title="Video is missing captions",
                        issue_type="missing_video_captions",
                        severity="high",
                        evidence=_element_evidence(
                            media,
                            "Video has no captions or subtitles track.",
                        ),
                        suggested_fix="Add captions or subtitles for education video content.",
                    )
                )

        if media.tag == "audio" and not has_transcript_text:
            issues.append(
                _issue(
                    title="Audio is missing a transcript",
                    issue_type="missing_audio_transcript",
                    severity="high",
                    evidence=_element_evidence(
                        media,
                        'Audio element has no visible document text containing "transcript".',
                    ),
                    suggested_fix="Add a transcript near audio lessons or instructions.",
                )
            )

    return issues


def _radio_group_is_named(radio: HTMLElement) -> bool:
    """Return whether a radio button sits inside a named group container."""
    for ancestor in reversed(radio.ancestors):
        if ancestor.tag == "fieldset":
            # A legend parsed anywhere inside this fieldset marks it named.
            return True if getattr(ancestor, "_has_legend", False) else False
        role = ancestor.attrs.get("role", "").lower()
        if role == "radiogroup":
            return bool(
                ancestor.attrs.get("aria-label") or ancestor.attrs.get("aria-labelledby")
            )
    return False


def analyze_structure_relationships(html: str) -> list[AccessibilityIssue]:
    """Detect structural relationships conveyed visually but not in markup.

    Conservative checks for WCAG 2.2 SC 1.3.1: radio groups without a named
    group container, data tables without header cells, required markers that
    are visual only, and (review-only) large bold text acting as a heading.
    """
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    # Mark fieldsets that contain a legend so radio checks can see it.
    for element in parser.elements:
        if element.tag == "legend":
            fieldset = _nearest_ancestor(element, {"fieldset"})
            if fieldset is not None:
                fieldset._has_legend = True  # noqa: SLF001 - parser-internal marker

    # Radio groups: two or more radios sharing a name need a group label.
    radios_by_name: dict[str, list[HTMLElement]] = {}
    for element in parser.elements:
        if (
            element.tag == "input"
            and element.attrs.get("type", "").lower() == "radio"
            and element.attrs.get("name")
            and not _element_is_hidden(element)
        ):
            radios_by_name.setdefault(element.attrs["name"], []).append(element)
    for group_name, radios in radios_by_name.items():
        if len(radios) < 2:
            continue
        if any(_radio_group_is_named(radio) for radio in radios):
            continue
        issues.append(
            _issue(
                title="Radio group is not grouped with fieldset/legend",
                issue_type="radio_group_missing_fieldset",
                severity="medium",
                evidence=_element_evidence(
                    radios[0],
                    f'Radio group "{group_name}" has {len(radios)} options but '
                    "no fieldset/legend or named radiogroup, so the shared "
                    "question is not announced with each option.",
                    {"group_name": group_name, "option_count": len(radios)},
                ),
                suggested_fix=(
                    "Wrap the radio buttons in a <fieldset> whose <legend> states "
                    'the group question, or use role="radiogroup" with an '
                    "accessible name."
                ),
            )
        )

    # Data tables without any header cells.
    tables = [element for element in parser.elements if element.tag == "table"]
    for table in tables:
        role = table.attrs.get("role", "").lower()
        if role in {"presentation", "none"} or _element_is_hidden(table):
            continue
        rows: list[HTMLElement] = []
        has_th = False
        has_headers_attr = False
        cells_by_row: dict[int, int] = {}
        for element in parser.elements:
            nearest_table = _nearest_ancestor(element, {"table"})
            if nearest_table is not table:
                continue
            if element.tag == "tr":
                rows.append(element)
            elif element.tag == "th":
                has_th = True
            elif element.tag == "td":
                row = _nearest_ancestor(element, {"tr"})
                if row is not None:
                    cells_by_row[id(row)] = cells_by_row.get(id(row), 0) + 1
                if element.attrs.get("headers"):
                    has_headers_attr = True
        max_columns = max(cells_by_row.values(), default=0)
        if has_th or has_headers_attr or len(rows) < 2 or max_columns < 2:
            continue
        if not table.text:
            continue
        issues.append(
            _issue(
                title="Data table has no header cells",
                issue_type="table_missing_headers",
                severity="medium",
                evidence=_element_evidence(
                    table,
                    f"Table with {len(rows)} rows and up to {max_columns} "
                    "columns has no th cells and no headers associations.",
                    {"rows": len(rows), "max_columns": max_columns},
                ),
                suggested_fix=(
                    "Mark header cells with <th> and scope, or use headers/id "
                    "associations. Purely visual layout tables should use "
                    'role="presentation" or CSS layout instead.'
                ),
            )
        )

    # Required markers shown in a label but not exposed programmatically.
    controls_by_id = {
        element.attrs.get("id"): element
        for element in parser.elements
        if element.tag in {"input", "textarea", "select"} and element.attrs.get("id")
    }
    required_marker = re.compile(r"\*|\brequired\b", re.IGNORECASE)
    optional_marker = re.compile(r"\b(optional|not required)\b", re.IGNORECASE)
    for label in parser.elements:
        if label.tag != "label" or _element_is_hidden(label):
            continue
        text = label.text
        if not text or not required_marker.search(text) or optional_marker.search(text):
            continue
        control = controls_by_id.get(label.attrs.get("for", ""))
        if control is None:
            for candidate in parser.elements:
                if candidate.tag in {"input", "textarea", "select"} and label in candidate.ancestors:
                    control = candidate
                    break
        if control is None:
            continue
        if "required" in control.attrs or control.attrs.get("aria-required", "").lower() == "true":
            continue
        issues.append(
            _issue(
                title="Required marker is visual only",
                issue_type="visual_required_not_programmatic",
                severity="medium",
                evidence=_element_evidence(
                    control,
                    f'The label "{_shorten(text, 80)}" marks this field as '
                    "required, but the control has neither required nor "
                    'aria-required="true".',
                    {"label_text": _shorten(text, 80)},
                ),
                suggested_fix=(
                    'Add required or aria-required="true" to the control the '
                    "visible marker refers to."
                ),
            )
        )

    # Review-only: large bold inline-styled div/span text acting as a heading.
    fake_heading_style = re.compile(
        r"font-size\s*:\s*(?:(2[4-9]|[3-9]\d)(?:\.\d+)?px|(1\.[5-9]\d*|[2-9](?:\.\d+)?)(?:em|rem))",
        re.IGNORECASE,
    )
    bold_style = re.compile(r"font-weight\s*:\s*(bold|[6-9]00)", re.IGNORECASE)
    for element in parser.elements:
        if element.tag not in {"div", "span"} or _element_is_hidden(element):
            continue
        if element.attrs.get("role", "").lower() == "heading":
            continue
        if _nearest_ancestor(element, {"a", "button", "label", "th", "h1", "h2", "h3", "h4", "h5", "h6"}):
            continue
        style = element.attrs.get("style", "")
        if not style or not fake_heading_style.search(style) or not bold_style.search(style):
            continue
        text = element.text
        if not text or len(text) < 3 or len(text) > 120:
            continue
        issues.append(
            _issue(
                title="Styled text may act as a heading without heading markup",
                issue_type="fake_heading",
                severity="low",
                evidence=_element_evidence(
                    element,
                    "Large bold inline-styled text may function as a section "
                    "heading without heading markup. Review evidence only.",
                ),
                suggested_fix=(
                    "If this text introduces a section, use a real heading "
                    "element (h2-h6) at the right outline level."
                ),
            )
        )

    return issues


_SENSORY_PATTERNS = [
    re.compile(
        r"\b(click|press|select|choose|tap|use|find)\b[^.!?\n]{0,40}\b"
        r"(red|green|blue|yellow|orange|purple|pink|round|circular|square|triangular)\b"
        r"[^.!?\n]{0,25}\b(button|icon|link|box|arrow|tab|menu)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(button|box|menu|icon|link|panel|column|section|form|field)\b"
        r"[^.!?\n]{0,20}\bon the (right|left)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\blisten for\b", re.IGNORECASE),
    re.compile(r"\bwhen you hear\b[^.!?\n]{0,30}\b(beep|sound|tone|chime)\b", re.IGNORECASE),
]

_SENSORY_TEXT_TAGS = {"p", "li", "td", "th", "label", "figcaption", "dd", "dt"}


def analyze_sensory_instructions(html: str) -> list[AccessibilityIssue]:
    """Flag instructions that appear to rely only on shape, color, or position.

    Review-only heuristic for WCAG 2.2 SC 1.3.3: keyword presence alone is
    never treated as a confirmed issue, because the sentence may also name
    the target.
    """
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []
    seen_texts: set[str] = set()

    for element in parser.elements:
        if len(issues) >= 5:
            break
        if element.tag not in _SENSORY_TEXT_TAGS or _element_is_hidden(element):
            continue
        text = element.text
        if not text or text in seen_texts:
            continue
        for pattern in _SENSORY_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            seen_texts.add(text)
            issues.append(
                _issue(
                    title="Instruction may rely on sensory characteristics only",
                    issue_type="sensory_instruction",
                    severity="low",
                    evidence=_element_evidence(
                        element,
                        "This instruction references shape, color, position, or "
                        "sound. If the target is not also identified by name, "
                        "users who cannot perceive that characteristic are lost. "
                        "Manual confirmation required.",
                        {"matched_phrase": _shorten(match.group(0), 100)},
                    ),
                    suggested_fix=(
                        "Also identify the target by its name or label, for "
                        "example 'click the red Submit button'."
                    ),
                )
            )
            break

    return issues


# Conservative field-purpose inference for WCAG 2.2 SC 1.3.5. Keys are
# regexes matched against a normalized bundle of name, id, and label text;
# order matters (first match wins).
_AUTOCOMPLETE_TOKEN_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(e ?mail|email address)\b"), "email"),
    (re.compile(r"\b(phone|telephone|mobile|tel)\b"), "tel"),
    (re.compile(r"\b(first name|given name|firstname|givenname|fname)\b"), "given-name"),
    (re.compile(r"\b(last name|family name|surname|lastname|familyname|lname)\b"), "family-name"),
    (re.compile(r"\b(full name|fullname)\b"), "name"),
    (re.compile(r"\b(user ?name)\b"), "username"),
    (re.compile(r"\b(postal ?code|zip ?code|zip|pincode|pin ?code)\b"), "postal-code"),
    (re.compile(r"\b(birth ?day|birth ?date|date of birth|dob)\b"), "bday"),
    (re.compile(r"\b(street address|address line ?1?)\b"), "street-address"),
]

# Fields whose purpose is ambiguous or explicitly out of scope for 1.3.5.
_AUTOCOMPLETE_SKIP = re.compile(
    r"\b(search|query|otp|one time|code|token|captcha|coupon|promo|voucher|company|organization|org)\b"
)


def analyze_input_purposes(html: str) -> list[AccessibilityIssue]:
    """Detect common user-information inputs missing autocomplete tokens."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    labels_by_for: dict[str, str] = {}
    for element in parser.elements:
        if element.tag == "label" and element.attrs.get("for"):
            labels_by_for[element.attrs["for"]] = element.text

    for control in parser.elements:
        if control.tag != "input" or _element_is_hidden(control):
            continue
        input_type = control.attrs.get("type", "text").lower()
        if input_type in IGNORED_INPUT_TYPES or input_type in {"search", "checkbox", "radio", "file"}:
            continue
        if control.attrs.get("autocomplete"):
            continue
        if _nearest_ancestor(control, {"form"}) is None:
            continue

        label_text = labels_by_for.get(control.attrs.get("id", ""), "")
        if not label_text and control.wrapped_by_label:
            label = _nearest_ancestor(control, {"label"})
            label_text = label.text if label else ""
        haystack = _normalize_name_text(
            " ".join(
                [
                    control.attrs.get("name", "").replace("_", " ").replace("-", " "),
                    control.attrs.get("id", "").replace("_", " ").replace("-", " "),
                    label_text,
                ]
            )
        )
        if _AUTOCOMPLETE_SKIP.search(haystack):
            continue

        token = None
        if input_type == "email":
            token = "email"
        elif input_type == "tel":
            token = "tel"
        elif input_type == "password":
            if re.search(r"\b(new|confirm|repeat|create)\b", haystack):
                token = "new-password"
            elif re.search(r"\b(current|old|existing)\b", haystack):
                token = "current-password"
        elif input_type == "text" or not control.attrs.get("type"):
            for pattern, mapped_token in _AUTOCOMPLETE_TOKEN_RULES:
                if pattern.search(haystack):
                    token = mapped_token
                    break
        if token is None:
            continue

        issues.append(
            _issue(
                title="Common personal-data field is missing an autocomplete token",
                issue_type="missing_autocomplete",
                severity="medium",
                evidence=_element_evidence(
                    control,
                    "This field appears to collect the user's own "
                    f'information but has no autocomplete token; "{token}" '
                    "looks appropriate.",
                    {"suggested_token": token, "identity": _control_identity(control)},
                ),
                suggested_fix=f'Add autocomplete="{token}" if the field collects the user\'s own information.',
            )
        )

    return issues


_SKIP_LINK_TEXT = re.compile(r"\b(skip|jump)\b.*\b(content|main|navigation)\b", re.IGNORECASE)


def analyze_bypass_blocks(html: str) -> list[AccessibilityIssue]:
    """Detect a substantial repeated navigation block with no bypass mechanism.

    Conservative: small pages, pages with a main landmark, a skip link, or a
    usable heading structure are never flagged.
    """
    parser = _parse_html(html)

    links = [
        element
        for element in parser.elements
        if element.tag == "a" and "href" in element.attrs and not _element_is_hidden(element)
    ]
    nav_links = [
        element
        for element in links
        if _nearest_ancestor(element, {"nav"}) is not None
        or any(
            ancestor.attrs.get("role", "").lower() == "navigation"
            for ancestor in element.ancestors
        )
    ]
    if len(nav_links) < 5 or len(links) < 10:
        return []

    has_main = any(
        element.tag == "main" or element.attrs.get("role", "").lower() == "main"
        for element in parser.elements
    )
    if has_main:
        return []

    heading_count = sum(
        1
        for element in parser.elements
        if element.tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and element.text
    )
    if heading_count >= 2:
        # Heading navigation is a recognized bypass mechanism for assistive
        # technology users; treat this as sufficient to stay conservative.
        return []

    for link in links[:5]:
        href = link.attrs.get("href", "")
        if href.startswith("#") and _SKIP_LINK_TEXT.search(link.text or ""):
            return []

    first_nav_link = nav_links[0]
    return [
        _issue(
            title="No apparent way to bypass repeated navigation",
            issue_type="no_bypass_mechanism",
            severity="medium",
            evidence=_element_evidence(
                first_nav_link,
                f"The page has a navigation block with {len(nav_links)} links "
                "but no skip link, no main landmark, and fewer than two "
                "headings, so keyboard users may have to move through every "
                "link on every visit.",
                {"nav_link_count": len(nav_links), "total_link_count": len(links)},
            ),
            suggested_fix=(
                'Add a "Skip to main content" link as the first focusable '
                'element, and mark the main content with <main> or role="main".'
            ),
        )
    ]


def analyze_label_in_name(html: str) -> list[AccessibilityIssue]:
    """Compare visible labels with aria-label overrides (WCAG 2.2 SC 2.5.3)."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for element in parser.elements:
        if _element_is_hidden(element):
            continue
        aria_label = element.attrs.get("aria-label", "")
        if not aria_label:
            continue
        if element.tag in {"a", "button"}:
            visible = element.text
        elif (
            element.tag == "input"
            and element.attrs.get("type", "").lower() in {"submit", "button"}
        ):
            visible = element.attrs.get("value", "")
        else:
            continue

        visible_norm = _normalize_name_text(visible)
        aria_norm = _normalize_name_text(aria_label)
        # Icon-only or near-empty visible labels have nothing for speech
        # input users to say, so there is nothing to mismatch.
        if len(visible_norm) < 3 or not re.search(r"[a-z]", visible_norm):
            continue
        if visible_norm in aria_norm:
            continue
        issues.append(
            _issue(
                title="Visible label is missing from the accessible name",
                issue_type="label_in_name_mismatch",
                severity="medium",
                evidence=_element_evidence(
                    element,
                    f'The visible label "{_shorten(visible, 60)}" does not appear '
                    f'in the accessible name "{_shorten(aria_label, 60)}", so '
                    "speech-input users saying what they see cannot activate "
                    "this control.",
                    {"visible_label": _shorten(visible, 60), "aria_label": _shorten(aria_label, 60)},
                ),
                suggested_fix=(
                    "Make the accessible name contain the visible label text, "
                    "or remove the overriding aria-label."
                ),
            )
        )

    return issues


def _raw_block_text(html: str, tag: str) -> str:
    """Return raw script/style text for conservative static evidence scans."""
    pattern = re.compile(rf"<{tag}\b[^>]*>(.*?)</{tag}>", re.IGNORECASE | re.DOTALL)
    return "\n".join(match.group(1) for match in pattern.finditer(html))


def _has_nearby_text(parser: _StaticHTMLParser, words: set[str]) -> bool:
    """Return whether visible page text contains any whole-word cue."""
    text = parser.document_text.casefold()
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def _has_control_text(parser: _StaticHTMLParser, words: set[str]) -> bool:
    """Return whether visible controls provide an alternative by name."""
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        if element.tag not in {"button", "a", "input", "select"}:
            continue
        text = " ".join(
            [
                element.text,
                element.attrs.get("value", ""),
                element.attrs.get("aria-label", ""),
                element.attrs.get("title", ""),
            ]
        ).casefold()
        if any(word in text for word in words):
            return True
    return False


def _has_reduced_motion_support(html: str) -> bool:
    """Return whether CSS appears to include a reduced-motion accommodation."""
    return bool(re.search(r"prefers-reduced-motion", html, re.IGNORECASE))


def _script_has(pattern: str, scripts: str) -> bool:
    return bool(re.search(pattern, scripts, re.IGNORECASE | re.DOTALL))


def analyze_wcag_static_evidence(html: str) -> list[AccessibilityIssue]:
    """Collect conservative static evidence for additional WCAG criteria.

    These checks intentionally produce partial or supporting evidence. They
    look for concrete markup, CSS, or script patterns and include exceptions
    for common accessible alternatives rather than mapping loose keywords.
    """
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []
    scripts = _raw_block_text(html, "script")
    styles = _raw_block_text(html, "style")
    combined_code = "\n".join([styles, scripts])

    # 1.3.2 Meaningful Sequence: CSS order/grid placement can make visual
    # order differ from DOM order. This is review evidence, not a conclusion.
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        style = element.attrs.get("style", "")
        if re.search(r"(?:^|;)\s*order\s*:\s*-?\d+", style, re.IGNORECASE) or re.search(
            r"grid-(?:row|column)\s*:\s*\d+\s*/", style, re.IGNORECASE
        ):
            issues.append(
                _issue(
                    title="CSS may reorder content away from DOM order",
                    issue_type="meaningful_sequence_reorder",
                    severity="low",
                    evidence=_element_evidence(
                        element,
                        "Inline CSS changes visual order or grid placement; "
                        "compare DOM, visual, and focus order manually.",
                        {"dom_index": parser.elements.index(element), "css": _shorten(style, 160)},
                    ),
                    suggested_fix=(
                        "Keep meaningful reading order in the DOM, or ensure "
                        "the visual reordering does not change meaning."
                    ),
                )
            )
            break

    # 1.3.4 Orientation: require evidence of restriction, not responsive CSS.
    orientation_message = re.search(
        r"\b(rotate (?:your )?device|landscape mode required|portrait mode required|"
        r"please use (?:landscape|portrait))\b",
        parser.document_text,
        re.IGNORECASE,
    )
    orientation_code = _script_has(
        r"screen\.orientation|orientation\.lock|matchMedia\([^)]*orientation",
        scripts,
    )
    orientation_hidden = re.search(
        r"@media[^{]+orientation\s*:\s*(portrait|landscape)[^{]+{[^}]+display\s*:\s*none",
        styles,
        re.IGNORECASE | re.DOTALL,
    )
    if orientation_message or (_script_has(r"orientation\.lock", scripts) or (orientation_code and orientation_hidden)):
        issues.append(
            _issue(
                title="Page may restrict use to one orientation",
                issue_type="orientation_restriction",
                severity="medium",
                evidence=_page_evidence(
                    "page",
                    "Static evidence suggests functionality or content is restricted by device orientation.",
                    snippet=(orientation_message.group(0) if orientation_message else "orientation restriction code"),
                    extra={
                        "message": orientation_message.group(0) if orientation_message else None,
                        "script_orientation_check": orientation_code,
                        "orientation_hidden_content": bool(orientation_hidden),
                    },
                ),
                suggested_fix=(
                    "Let content and functionality work in both portrait and "
                    "landscape unless a specific orientation is essential."
                ),
            )
        )

    # 1.4.1 Use of Color: require color-only cue plus lack of text/icon/state.
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        classes = element.attrs.get("class", "").casefold()
        style = element.attrs.get("style", "").casefold()
        text = element.text.casefold()
        has_color_cue = any(cue in classes for cue in ["error", "invalid", "required", "active", "selected", "success"]) or (
            "color:" in style and any(word in text for word in ["required", "error", "success", "selected"])
        )
        if not has_color_cue:
            continue
        has_non_color = any(
            [
                any(word in text for word in ["required", "error", "invalid", "success", "selected"]),
                element.attrs.get("aria-current"),
                element.attrs.get("aria-selected"),
                element.attrs.get("aria-invalid"),
                element.attrs.get("role", "").lower() in {"img", "status", "alert"},
                re.search(r"text-decoration|border|font-weight\s*:\s*(bold|[6-9]00)", style, re.IGNORECASE),
            ]
        )
        if has_non_color:
            continue
        issues.append(
            _issue(
                title="Color may be the only indicator",
                issue_type="color_only_indicator",
                severity="low",
                evidence=_element_evidence(
                    element,
                    "Class/style names suggest status is communicated by color, but no text, icon, aria state, border, underline, or weight distinction is visible statically.",
                    {"class": classes, "style": _shorten(style, 120)},
                ),
                suggested_fix=(
                    "Add text, an icon with text alternative, underline, pattern, "
                    "shape, border, aria-current/selected/invalid, or another "
                    "non-color cue."
                ),
            )
        )
        break

    # 1.4.2 Audio Control.
    for audio in parser.elements:
        if audio.tag != "audio" or _element_is_inactive(audio):
            continue
        if "autoplay" not in audio.attrs:
            continue
        if "controls" in audio.attrs or audio.attrs.get("muted") == "muted":
            continue
        issues.append(
            _issue(
                title="Autoplaying audio may lack independent controls",
                issue_type="autoplay_audio_no_control",
                severity="medium",
                evidence=_element_evidence(
                    audio,
                    "Audio is marked autoplay and has no native controls; duration and custom controls need manual confirmation.",
                    {"autoplay": True},
                ),
                suggested_fix=(
                    "Avoid autoplay, or provide a pause/stop and volume control "
                    "independent of the system volume."
                ),
            )
        )
        break

    # 1.4.5 Images of Text: review evidence for SVG/image text labels.
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        if element.tag == "svg" and element.text and len(element.text) <= 120:
            issues.append(
                _issue(
                    title="Graphic appears to contain text",
                    issue_type="image_of_text",
                    severity="low",
                    evidence=_element_evidence(
                        element,
                        "SVG contains visible text; confirm whether this should be real HTML text instead of an image of text.",
                    ),
                    suggested_fix="Use real text where possible, or confirm the image-of-text exception applies.",
                )
            )
            break
        if element.tag == "img" and re.search(r"(text|banner|heading|label|logo)", element.attrs.get("src", ""), re.IGNORECASE):
            issues.append(
                _issue(
                    title="Image may contain text",
                    issue_type="image_of_text",
                    severity="low",
                    evidence=_element_evidence(
                        element,
                        "The image filename suggests text may be embedded in the image; manual confirmation required.",
                    ),
                    suggested_fix="Use real text where possible, or confirm the image-of-text exception applies.",
                )
            )
            break

    # 1.4.13 Content on Hover or Focus.
    hover_focus_css = re.search(r":(?:hover|focus(?:-within)?)[^{]+{[^}]*display\s*:\s*(?:block|flex|grid|inline)", styles, re.IGNORECASE | re.DOTALL)
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        handler = element.attrs.get("onmouseover") or element.attrs.get("onfocus") or ""
        tooltipish = element.attrs.get("role", "").lower() in {"tooltip", "menu", "dialog"} or "tooltip" in element.attrs.get("class", "").casefold()
        if not handler and not tooltipish and not hover_focus_css:
            continue
        if element.attrs.get("title") and not handler and not tooltipish:
            continue
        issues.append(
            _issue(
                title="Hover or focus may reveal additional content",
                issue_type="hover_focus_content",
                severity="low",
                evidence=_element_evidence(
                    element,
                    "Static evidence shows hover/focus-revealed content; verify it is dismissible, hoverable, and persistent.",
                    {"event_handler": _shorten(handler, 120) or None, "css_hover_focus": bool(hover_focus_css)},
                ),
                suggested_fix=(
                    "Ensure hover/focus content can be dismissed without moving "
                    "focus, remains visible when hovered, and does not obscure "
                    "essential content."
                ),
            )
        )
        break

    # 2.1.4 Character Key Shortcuts.
    if _script_has(r"(?:keydown|keyup|keypress)", scripts) and re.search(
        r"(?:event|e)\.key\s*={2,3}\s*['\"][A-Za-z0-9]['\"]", scripts
    ) and not re.search(r"(ctrlKey|altKey|metaKey)", scripts):
        issues.append(
            _issue(
                title="Single-character keyboard shortcut may be active",
                issue_type="single_character_shortcut",
                severity="medium",
                evidence=_page_evidence(
                    "script",
                    "Script listens for a single character key without an obvious Ctrl/Alt/Meta modifier check.",
                    snippet=_shorten(re.search(r"(?:event|e)\.key\s*={2,3}\s*['\"][A-Za-z0-9]['\"]", scripts).group(0), 120),
                    extra={"event_type": "keydown/keyup/keypress"},
                ),
                suggested_fix=(
                    "Provide a way to turn the shortcut off, remap it, or require "
                    "a modifier key."
                ),
            )
        )

    # 2.2.1 Timing Adjustable.
    meta_refresh = next(
        (
            element
            for element in parser.elements
            if element.tag == "meta"
            and element.attrs.get("http-equiv", "").casefold() == "refresh"
        ),
        None,
    )
    timeout_script = re.search(r"setTimeout\s*\([^)]*(location|submit|reload)", scripts, re.IGNORECASE | re.DOTALL)
    countdown_text = re.search(r"\b(session expires|time remaining|countdown|expires in)\b", parser.document_text, re.IGNORECASE)
    if meta_refresh or timeout_script or countdown_text:
        has_adjust = _has_control_text(parser, {"extend", "continue", "pause", "disable", "more time"})
        if not has_adjust:
            issues.append(
                _issue(
                    title="Timed behavior may not be adjustable",
                    issue_type="timing_adjustable_missing",
                    severity="medium",
                    evidence=(
                        _element_evidence(meta_refresh, "Meta refresh creates timed navigation with no visible adjustment control.")
                        if meta_refresh
                        else _page_evidence(
                            "page",
                            "Static evidence shows a timeout/countdown with no visible extend, pause, or disable control.",
                            snippet=_shorten(timeout_script.group(0) if timeout_script else countdown_text.group(0), 160),
                        )
                    ),
                    suggested_fix="Let users extend, disable, or adjust time limits unless an exception applies.",
                )
            )

    # 2.2.2 Pause, Stop, Hide.
    moving_css = re.search(r"animation(?:-name)?\s*:[^;}]*(carousel|ticker|marquee|blink|scroll|slide)", combined_code, re.IGNORECASE)
    moving_markup = any(
        element.tag == "marquee"
        or "autoplay" in element.attrs
        or re.search(r"\b(carousel|ticker|marquee|auto-?rotate|auto-?scroll)\b", element.attrs.get("class", ""), re.IGNORECASE)
        for element in parser.elements
        if not _element_is_inactive(element)
    )
    if moving_css or moving_markup:
        if not _has_control_text(parser, {"pause", "stop", "hide"}):
            issues.append(
                _issue(
                    title="Auto-moving content may lack pause controls",
                    issue_type="moving_content_no_pause",
                    severity="medium",
                    evidence=_page_evidence(
                        "page",
                        "Static evidence shows auto-moving or auto-updating content with no visible pause, stop, or hide control.",
                        snippet=_shorten(moving_css.group(0) if moving_css else "auto-moving markup", 160),
                    ),
                    suggested_fix="Add visible controls to pause, stop, hide, or control the update frequency.",
                )
            )

    # 2.3.1 Three flashes or below threshold.
    flash_css = re.search(r"@keyframes\s+[^{}]*(flash|blink|strobe)[^{]*{", styles, re.IGNORECASE)
    fast_animation = re.search(
        r"animation(?:-duration)?\s*:[^;}]*\b(?:0?\.[0-3]\d*s|[1-3]00ms)\b",
        styles,
        re.IGNORECASE,
    )
    if flash_css and fast_animation:
        issues.append(
            _issue(
                title="Animation may flash rapidly",
                issue_type="possible_flashing_content",
                severity="medium",
                evidence=_page_evidence(
                    "style",
                    "CSS keyframes and duration suggest rapid flashing; threshold testing requires visual confirmation.",
                    snippet=_shorten(f"{flash_css.group(0)} {fast_animation.group(0)}", 160),
                ),
                suggested_fix="Avoid rapid flashing, or verify the flash threshold with a specialized tool.",
            )
        )

    # 2.3.3 Animation from interactions.
    interaction_motion = re.search(r":(?:hover|active|focus)[^{]*{[^}]*(transform|animation)", styles, re.IGNORECASE | re.DOTALL)
    if interaction_motion and not _has_reduced_motion_support(html):
        issues.append(
            _issue(
                title="Interaction-triggered motion lacks reduced-motion evidence",
                issue_type="interaction_motion_no_reduced_motion",
                severity="low",
                evidence=_page_evidence(
                    "style",
                    "CSS applies transform/animation on interaction and no prefers-reduced-motion accommodation is present.",
                    snippet=_shorten(interaction_motion.group(0), 180),
                ),
                suggested_fix="Respect prefers-reduced-motion or provide a control to disable non-essential motion.",
            )
        )

    # 2.5.1 Pointer Gestures.
    gesture_evidence = re.search(r"\b(touchstart|touchmove|pointermove|gesturestart|pinch|swipe)\b", combined_code, re.IGNORECASE)
    if gesture_evidence and not _has_control_text(parser, {"previous", "next", "zoom", "increase", "decrease", "move"}):
        issues.append(
            _issue(
                title="Function may require a path or multipoint gesture",
                issue_type="pointer_gesture_no_alternative",
                severity="medium",
                evidence=_page_evidence(
                    "page",
                    "Static event evidence suggests swipe, pinch, drag-path, or pointer-move operation without an obvious simple alternative.",
                    snippet=_shorten(gesture_evidence.group(0), 120),
                    extra={"event_type": gesture_evidence.group(0)},
                ),
                suggested_fix="Provide single-pointer alternatives such as buttons, menus, fields, or steppers.",
            )
        )

    # 2.5.2 Pointer Cancellation.
    pointer_code = "\n".join([combined_code, html])
    down_event = re.search(r"\b(onmousedown|onpointerdown|ontouchstart|mousedown|pointerdown|touchstart)\b", pointer_code, re.IGNORECASE)
    if down_event and not re.search(r"\b(mouseup|pointerup|touchend|preventDefault|cancel)\b", pointer_code, re.IGNORECASE):
        issues.append(
            _issue(
                title="Control may activate on pointer down",
                issue_type="pointer_down_activation",
                severity="medium",
                evidence=_page_evidence(
                    "page",
                    "Static event evidence suggests activation on pointer-down without an obvious pointer-up or cancellation path.",
                    snippet=_shorten(down_event.group(0), 120),
                    extra={"event_type": down_event.group(0)},
                ),
                suggested_fix="Activate on pointer-up, support cancellation by moving away, or provide undo unless down-event activation is essential.",
            )
        )

    # 2.5.7 Dragging Movements.
    drag_elements = [
        element
        for element in parser.elements
        if not _element_is_inactive(element)
        and ("draggable" in element.attrs or any(attr in element.attrs for attr in ["ondragstart", "ondrop", "ondragover"]))
    ]
    drag_script = re.search(r"\b(dragstart|dragover|drop|sortable|draggable)\b", combined_code, re.IGNORECASE)
    if (drag_elements or drag_script) and not _has_control_text(parser, {"move up", "move down", "select", "place", "upload", "browse"}):
        target = drag_elements[0] if drag_elements else None
        issues.append(
            _issue(
                title="Function may require dragging",
                issue_type="dragging_no_alternative",
                severity="medium",
                evidence=(
                    _element_evidence(target, "Draggable UI has no obvious non-drag alternative.")
                    if target
                    else _page_evidence("script", "Script mentions drag/drop with no obvious non-drag alternative.", snippet=_shorten(drag_script.group(0), 120))
                ),
                suggested_fix="Provide non-drag alternatives such as buttons, menus, keyboard commands, or direct input.",
            )
        )

    # 3.2.1 On Focus.
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        handler = element.attrs.get("onfocus", "")
        if handler and re.search(r"(location|href|submit|open\(|dialog|modal|focus\()", handler, re.IGNORECASE):
            issues.append(
                _issue(
                    title="Focus may trigger a context change",
                    issue_type="focus_context_change",
                    severity="medium",
                    evidence=_element_evidence(
                        element,
                        "The onfocus handler appears to navigate, submit, open UI, or move focus before activation.",
                        {"event_type": "focus", "handler": _shorten(handler, 160)},
                    ),
                    suggested_fix="Do not change context on focus alone; wait for explicit user activation.",
                )
            )
            break

    # 3.2.2 On Input.
    for element in parser.elements:
        if _element_is_inactive(element):
            continue
        handler = element.attrs.get("onchange", "") or element.attrs.get("oninput", "")
        if handler and re.search(r"(location|href|submit|reload|open\(|dialog|modal|focus\()", handler, re.IGNORECASE):
            issues.append(
                _issue(
                    title="Changing a control may trigger a context change",
                    issue_type="input_context_change",
                    severity="medium",
                    evidence=_element_evidence(
                        element,
                        "The input/change handler appears to navigate, submit, open UI, reload, or move focus immediately.",
                        {"event_type": "input/change", "handler": _shorten(handler, 160)},
                    ),
                    suggested_fix="Warn users before context changes or require an explicit submit/activate action.",
                )
            )
            break

    # 3.3.1 / 3.3.3 Error identification and suggestions.
    error_elements = [
        element
        for element in parser.elements
        if not _element_is_inactive(element)
        and (
            element.attrs.get("role", "").lower() == "alert"
            or "error" in element.attrs.get("class", "").casefold()
            or "error" in element.attrs.get("id", "").casefold()
        )
    ]
    form_controls = [
        element
        for element in parser.elements
        if element.tag in {"input", "textarea", "select"} and not _element_is_inactive(element)
    ]
    if error_elements and form_controls:
        associated = any(
            control.attrs.get("aria-invalid", "").lower() == "true"
            or control.attrs.get("aria-describedby")
            for control in form_controls
        )
        if not associated:
            issues.append(
                _issue(
                    title="Error message may not identify the affected field",
                    issue_type="error_not_identified",
                    severity="medium",
                    evidence=_element_evidence(
                        error_elements[0],
                        "An error message is present, but no form control exposes aria-invalid or aria-describedby association.",
                    ),
                    suggested_fix="Identify the affected field in text and connect the error with aria-describedby and/or aria-invalid.",
                )
            )
        suggestion_words = {"required", "enter", "use", "format", "example", "must", "choose", "select"}
        if not any(any(word in error.text.casefold() for word in suggestion_words) for error in error_elements):
            issues.append(
                _issue(
                    title="Error message may lack a correction suggestion",
                    issue_type="error_suggestion_missing",
                    severity="low",
                    evidence=_element_evidence(
                        error_elements[0],
                        "An error message is present, but it does not include obvious correction guidance such as required, format, example, or must.",
                    ),
                    suggested_fix="Where a correction is known, explain how to fix the error, for example the required format or missing value.",
                )
            )

    return issues


def analyze_html_static(html: str) -> list[AccessibilityIssue]:
    """Run all current static HTML accessibility checks."""
    issues: list[AccessibilityIssue] = []

    for check in [
        analyze_html_forms,
        analyze_interactive_names,
        analyze_images,
        analyze_heading_structure,
        analyze_page_metadata,
        analyze_media_accessibility,
        analyze_indic_language,
        analyze_structure_relationships,
        analyze_sensory_instructions,
        analyze_input_purposes,
        analyze_bypass_blocks,
        analyze_label_in_name,
        analyze_wcag_static_evidence,
    ]:
        issues.extend(check(html))

    return issues


def analyze_html(html: str) -> dict[str, Any]:
    """Return a small summary for an HTML page."""
    issues = analyze_html_static(html)

    return {
        "html_length": len(html),
        "issue_count": len(issues),
        "checks_run": STATIC_CHECKS_RUN,
        "notes": "Static HTML analysis is limited and does not replace a full audit.",
    }


def analyze_browser_page(url: str) -> dict[str, Any]:
    """Return placeholder browser analysis for a URL.

    TODO: Integrate Playwright or Selenium to load pages, run keyboard
    navigation checks, inspect computed styles, and capture evidence.
    """
    return {
        "url": url,
        "notes": "Browser automation is not implemented yet.",
    }


def analyze_pdf(path: str) -> dict[str, Any]:
    """Return placeholder PDF analysis.

    TODO: Add PDF text extraction, reading order checks, tags checks,
    image alternative text checks, and form field checks.
    """
    return {
        "path": path,
        "notes": "PDF analysis is not implemented yet.",
    }
