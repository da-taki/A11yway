"""Static HTML analysis helpers.

Future versions can use this module to inspect browser state, computed
styles, PDF files, and accessibility trees. For now, these checks use the
Python standard library and intentionally stay conservative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from typing import Any

from a11yway.core.indic_checks import analyze_indic_language
from a11yway.models.issue import AccessibilityIssue


IGNORED_INPUT_TYPES = {"hidden", "submit", "button", "reset"}
GENERIC_LINK_TEXT = {"click here", "here", "read more", "more", "link", "learn more"}

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

        issues.append(
            _issue(
                title="Form control is missing an accessible label",
                issue_type="missing_form_label",
                severity="high",
                evidence=_element_evidence(
                    control,
                    "Form control has no accessible label.",
                    {"type": input_type, "identity": _control_identity(control)},
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

        link_text = element.text.lower()
        if link_text in GENERIC_LINK_TEXT:
            issues.append(
                _issue(
                    title="Link text is too generic",
                    issue_type="generic_link_text",
                    severity="medium",
                    evidence=_element_evidence(
                        element,
                        "Link text is generic and does not explain the destination or action.",
                    ),
                    suggested_fix='Use descriptive link text like "Download scholarship guidelines" instead of "click here."',
                )
            )

    return issues


def analyze_images(html: str) -> list[AccessibilityIssue]:
    """Detect images that appear to be missing useful alt text."""
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for image in parser.elements:
        if image.tag != "img":
            continue

        alt = image.attrs.get("alt")
        role = image.attrs.get("role", "").lower()
        aria_hidden = image.attrs.get("aria-hidden", "").lower()
        inside_action = any(parent in {"a", "button"} for parent in image.parent_tags)

        if alt is None:
            severity = "high" if inside_action else "medium"
        elif alt == "" and not (
            role == "presentation" or aria_hidden == "true" or image.attrs.get("data-decorative") == "true"
        ):
            severity = "high" if inside_action else "medium"
        else:
            continue

        issues.append(
            _issue(
                title="Image is missing useful alt text",
                issue_type="missing_image_alt",
                severity=severity,
                evidence=_element_evidence(
                    image,
                    "Image is missing useful alt text.",
                ),
                suggested_fix="Add alt text that describes the image purpose, or mark decorative images as presentation.",
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
                    "Document has multiple h1 headings.",
                    extra={"count": h1_count},
                ),
                suggested_fix="Use one main h1 for the page purpose, then organize sections with h2 and lower headings.",
            )
        )

    previous_level: int | None = None
    for level, element in headings:
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
