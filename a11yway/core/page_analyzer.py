






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


DECORATIVE_SRC_PATTERN = re.compile(
    r"(spacer|pixel|blank|transparent|divider|shim|corner|dot|bullet)[^/]*\.(gif|png|svg|webp|jpg)",
    re.IGNORECASE,
)


INFORMATIVE_SRC_PATTERN = re.compile(
    r"(chart|diagram|graph|infographic|screenshot|map|figure)[^/]*\.(gif|png|svg|webp|jpg|jpeg)",
    re.IGNORECASE,
)




IMPLICITLY_CLOSED_TAGS = {
    "a", "button", "label", "select", "textarea", "option",
    "p", "li", "td", "th", "tr",
    "h1", "h2", "h3", "h4", "h5", "h6",
}


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
    "authentication_and_error_prevention",
    "wcag_static_evidence",
]


@dataclass
class HTMLElement:


    tag: str
    attrs: dict[str, str]
    parent_tags: list[str]
    text_parts: list[str] = field(default_factory=list)
    child_images: list[dict[str, str]] = field(default_factory=list)
    track_kinds: list[str] = field(default_factory=list)
    wrapped_by_label: bool = False
    line: int | None = None
    start_tag_snippet: str = ""



    ancestors: list["HTMLElement"] = field(default_factory=list)

    @property
    def text(self) -> str:

        return normalize_text(" ".join(self.text_parts))


class _StaticHTMLParser(HTMLParser):


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

        return normalize_text(" ".join(self.document_text_parts))


def normalize_text(value: str) -> str:

    return " ".join(value.split())


def _parse_html(html: str) -> _StaticHTMLParser:





    parser = _StaticHTMLParser(html)
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        pass
    return parser


def estimate_line_number(source_html: str, snippet: str) -> int | None:





    if not snippet:
        return None

    index = source_html.find(snippet)
    if index == -1:
        return None
    return source_html.count("\n", 0, index) + 1


def _shorten(value: str, max_length: int = 200) -> str:

    normalized = normalize_text(value)
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def build_start_tag_snippet(tag: str, attrs: dict[str, str]) -> str:

    attr_parts = []
    for name, value in attrs.items():
        if value == "":
            attr_parts.append(name)
        else:
            attr_parts.append(f'{name}="{escape(value, quote=True)}"')

    attrs_text = f" {' '.join(attr_parts)}" if attr_parts else ""
    return _shorten(f"<{tag}{attrs_text}>")


def _element_snippet(element: HTMLElement) -> str:

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

    if "hidden" in attrs:
        return True
    if attrs.get("aria-hidden", "").lower() == "true":
        return True
    style = attrs.get("style", "").lower()
    return bool(style and _HIDDEN_STYLE_PATTERN.search(style))


def _element_is_hidden(element: HTMLElement) -> bool:





    if _attrs_mark_hidden(element.attrs):
        return True
    return any(_attrs_mark_hidden(ancestor.attrs) for ancestor in element.ancestors)


def _element_is_inactive(element: HTMLElement) -> bool:

    if _element_is_hidden(element):
        return True
    if element.tag == "template" or "template" in element.parent_tags:
        return True
    if "inert" in element.attrs:
        return True
    return any("inert" in ancestor.attrs for ancestor in element.ancestors)


def _nearest_ancestor(element: HTMLElement, tags: set[str]) -> HTMLElement | None:

    for ancestor in reversed(element.ancestors):
        if ancestor.tag in tags:
            return ancestor
    return None


def _normalize_name_text(value: str) -> str:

    lowered = value.casefold()
    cleaned = re.sub(r"[^\w\s]", " ", lowered, flags=re.UNICODE)
    return " ".join(cleaned.split())


def _control_identity(control: HTMLElement) -> str:

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

    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name=agent_name,
        evidence=evidence,
        suggested_fix=suggested_fix,
    )


def analyze_html_forms(html: str) -> list[AccessibilityIssue]:

    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []

    for control in parser.elements:
        if control.tag not in {"input", "textarea", "select"}:
            continue

        input_type = control.attrs.get("type", "text").lower()
        if control.tag == "input" and input_type in IGNORED_INPUT_TYPES:
            continue



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

    if action.attrs.get("aria-label") or action.attrs.get("aria-labelledby"):
        return True
    if action.attrs.get("title"):
        return True
    if action.text:
        return True
    for child in action.child_images:


        if child is not image.attrs and child.get("alt"):
            return True
    return False


def _looks_decorative(image: HTMLElement) -> bool:

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

    for ancestor in reversed(radio.ancestors):
        if ancestor.tag == "fieldset":

            return True if getattr(ancestor, "_has_legend", False) else False
        role = ancestor.attrs.get("role", "").lower()
        if role == "radiogroup":
            return bool(
                ancestor.attrs.get("aria-label") or ancestor.attrs.get("aria-labelledby")
            )
    return False


def analyze_structure_relationships(html: str) -> list[AccessibilityIssue]:






    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []


    for element in parser.elements:
        if element.tag == "legend":
            fieldset = _nearest_ancestor(element, {"fieldset"})
            if fieldset is not None:
                fieldset._has_legend = True


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


_AUTOCOMPLETE_SKIP = re.compile(
    r"\b(search|query|otp|one time|code|token|captcha|coupon|promo|voucher|company|organization|org)\b"
)

_AUTOCOMPLETE_VALID_TOKENS = {
    "name", "honorific-prefix", "given-name", "additional-name", "family-name",
    "honorific-suffix", "nickname", "username", "new-password",
    "current-password", "one-time-code", "organization-title",
    "organization", "street-address", "address-line1", "address-line2",
    "address-line3", "address-level4", "address-level3", "address-level2",
    "address-level1", "country", "country-name", "postal-code",
    "cc-name", "cc-given-name", "cc-additional-name", "cc-family-name",
    "cc-number", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-csc",
    "cc-type", "transaction-currency", "transaction-amount", "language",
    "bday", "bday-day", "bday-month", "bday-year", "sex", "url",
    "photo", "tel", "tel-country-code", "tel-national", "tel-area-code",
    "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-extension",
    "email", "impp", "webauthn",
}

_AUTOCOMPLETE_GROUP_TOKENS = {"shipping", "billing", "home", "work", "mobile", "fax", "pager"}


def _autocomplete_detail_tokens(value: str) -> list[str]:
    return [
        token
        for token in value.casefold().split()
        if token not in {"on", "off"}
        and not token.startswith("section-")
        and token not in _AUTOCOMPLETE_GROUP_TOKENS
    ]


def _autocomplete_expected_token(input_type: str, haystack: str) -> str | None:
    if input_type == "email":
        return "email"
    if input_type == "tel":
        return "tel"
    if input_type == "password":
        if re.search(r"\b(new|confirm|repeat|create)\b", haystack):
            return "new-password"
        if re.search(r"\b(current|existing|login|sign ?in|password)\b", haystack) and re.search(r"\b(user ?name|email|login|sign ?in|account)\b", haystack):
            return "current-password"
        return None
    if input_type == "text" or not input_type:
        for pattern, mapped_token in _AUTOCOMPLETE_TOKEN_RULES:
            if pattern.search(haystack):
                return mapped_token
    return None


def _autocomplete_token_compatible(expected: str, tokens: list[str]) -> bool:
    if expected in tokens:
        return True
    if expected in {"current-password", "new-password"} and any(token.endswith("password") for token in tokens):
        return True
    if expected == "name" and {"given-name", "family-name"} & set(tokens):
        return True
    return False


def analyze_input_purposes(html: str) -> list[AccessibilityIssue]:
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
        autocomplete = control.attrs.get("autocomplete", "").strip()
        if autocomplete and input_type in IGNORED_INPUT_TYPES | {"checkbox", "radio", "file"}:
            issues.append(
                _issue(
                    title="Autocomplete token is on an unsupported control",
                    issue_type="autocomplete_unsupported_control",
                    severity="low",
                    evidence=_element_evidence(
                        control,
                        "This control type does not collect reusable personal information for autocomplete.",
                        {"autocomplete": autocomplete, "type": input_type},
                    ),
                    suggested_fix="Remove autocomplete from controls that do not collect reusable personal information.",
                )
            )
            continue
        if input_type in IGNORED_INPUT_TYPES or input_type in {"search", "checkbox", "radio", "file"}:
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

        token = _autocomplete_expected_token(input_type, haystack)
        if token is None:
            continue

        if autocomplete:
            detail_tokens = _autocomplete_detail_tokens(autocomplete)
            invalid_tokens = [
                item for item in detail_tokens if item not in _AUTOCOMPLETE_VALID_TOKENS
            ]
            if invalid_tokens:
                issues.append(
                    _issue(
                        title="Autocomplete token is invalid",
                        issue_type="invalid_autocomplete_token",
                        severity="medium",
                        evidence=_element_evidence(
                            control,
                            "The autocomplete attribute contains tokens that are not recognized HTML autofill detail tokens.",
                            {
                                "autocomplete": autocomplete,
                                "invalid_tokens": invalid_tokens,
                                "suggested_token": token,
                            },
                        ),
                        suggested_fix=f'Use a valid autocomplete token such as "{token}", or remove the attribute if the field is not for the user\'s own information.',
                    )
                )
                continue
            if detail_tokens and not _autocomplete_token_compatible(token, detail_tokens):
                issues.append(
                    _issue(
                        title="Autocomplete token contradicts the field purpose",
                        issue_type="contradictory_autocomplete",
                        severity="medium",
                        evidence=_element_evidence(
                            control,
                            f'The field appears to collect "{token}", but autocomplete is set to "{autocomplete}".',
                            {
                                "autocomplete": autocomplete,
                                "expected_token": token,
                                "identity": _control_identity(control),
                            },
                        ),
                        suggested_fix=f'Use autocomplete="{token}" if the field collects the user\'s own information.',
                    )
                )
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


def analyze_authentication_and_error_prevention(html: str) -> list[AccessibilityIssue]:
    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []
    document_text = parser.document_text.casefold()
    forms = [element for element in parser.elements if element.tag == "form" and not _element_is_hidden(element)]
    controls = [element for element in parser.elements if element.tag in {"input", "select", "textarea"} and not _element_is_hidden(element)]

    password_controls = [
        control for control in controls if control.attrs.get("type", "").casefold() == "password"
    ]
    if password_controls:
        blocked_paste = any(
            re.search(r"paste|copy", control.attrs.get("onpaste", "") + control.attrs.get("oncopy", ""), re.IGNORECASE)
            or control.attrs.get("onpaste", "").strip().casefold() == "return false"
            for control in password_controls
        )
        captcha_text = re.search(r"\b(captcha|recaptcha|type the characters|security code)\b", document_text)
        has_accessible_alternative = re.search(r"\b(audio challenge|email link|magic link|passkey|webauthn|one-time code|otp|alternative)\b", document_text)
        if blocked_paste or (captcha_text and not has_accessible_alternative):
            issues.append(
                _issue(
                    title="Authentication flow may require a cognitive function test without an accessible alternative",
                    issue_type="accessible_authentication_barrier",
                    severity="medium",
                    evidence=_page_evidence(
                        "form",
                        "The public authentication interface shows evidence such as blocked paste or CAPTCHA text without an obvious accessible alternative.",
                        snippet=_element_snippet(password_controls[0]),
                        extra={
                            "blocked_paste": blocked_paste,
                            "captcha_text": captcha_text.group(0) if captcha_text else "",
                        },
                    ),
                    suggested_fix="Support password managers and paste, and provide an accessible authentication alternative such as passkeys, one-time links, or accessible challenge options.",
                )
            )

    seen_fields: dict[str, HTMLElement] = {}
    repeat_candidates = {"email", "tel", "name", "given-name", "family-name", "postal-code", "street-address"}
    for control in controls:
        input_type = control.attrs.get("type", "text").casefold()
        haystack = _normalize_name_text(
            " ".join(
                [
                    control.attrs.get("name", "").replace("_", " ").replace("-", " "),
                    control.attrs.get("id", "").replace("_", " ").replace("-", " "),
                    control.attrs.get("aria-label", ""),
                    control.attrs.get("placeholder", ""),
                ]
            )
        )
        token = _autocomplete_expected_token(input_type, haystack)
        if token not in repeat_candidates:
            continue
        previous = seen_fields.get(token)
        if previous is not None:
            issues.append(
                _issue(
                    title="Workflow may ask for the same information more than once",
                    issue_type="redundant_entry_repeated_field",
                    severity="low",
                    evidence=_element_evidence(
                        control,
                        f'This form contains another field that appears to request "{token}" again.',
                        {
                            "repeated_purpose": token,
                            "first_field": _control_identity(previous),
                            "current_field": _control_identity(control),
                        },
                    ),
                    suggested_fix="Avoid asking users to re-enter information already provided in the same workflow unless an exception applies.",
                )
            )
            break
        seen_fields[token] = control

    consequence_text = re.search(r"\b(payment|pay|purchase|order|application|exam|submit final|delete|remove account|legal|financial|data)\b", document_text)
    if forms and consequence_text:
        has_review = re.search(r"\b(review|confirm|summary|edit|back|undo|cancel|verify)\b", document_text)
        if not has_review:
            issues.append(
                _issue(
                    title="High-consequence form may lack visible review or reversal steps",
                    issue_type="error_prevention_missing",
                    severity="medium",
                    evidence=_page_evidence(
                        "form",
                        "The public form appears to involve legal, financial, test, or data-modifying consequences without visible review, confirmation, edit, undo, or cancellation language.",
                        snippet=_element_snippet(forms[0]),
                        extra={"consequence_keyword": consequence_text.group(0)},
                    ),
                    suggested_fix="Provide review, confirmation, correction, or reversal mechanisms before final high-consequence submission.",
                )
            )

    broad_status_containers = {"html", "body", "main", "form", "section", "article", "nav", "header", "footer", "aside", "h1", "h2", "h3", "h4", "h5", "h6"}
    statusish = [
        element
        for element in parser.elements
        if not _element_is_hidden(element)
        and element.tag not in broad_status_containers
        and (
            re.search(r"\b(status|message|toast|notification|alert|success|error|updated|saved)\b", element.attrs.get("class", "") + " " + element.attrs.get("id", ""), re.IGNORECASE)
            or re.search(r"\b(saved|updated|loading|complete|error|success)\b", element.text, re.IGNORECASE)
        )
    ]
    for element in statusish[:1]:
        role = element.attrs.get("role", "").casefold()
        live = element.attrs.get("aria-live", "").casefold()
        ancestor_live = any(
            ancestor.attrs.get("role", "").casefold() in {"status", "alert"}
            or ancestor.attrs.get("aria-live", "").casefold() in {"polite", "assertive"}
            for ancestor in element.ancestors
        )
        if role in {"status", "alert"} or live in {"polite", "assertive"} or ancestor_live:
            continue
        issues.append(
            _issue(
                title="Status message may not be exposed programmatically",
                issue_type="status_message_not_live",
                severity="medium",
                evidence=_element_evidence(
                    element,
                    "Status-like content appears in the page without role=status, role=alert, or aria-live.",
                    {"role": role, "aria_live": live},
                ),
                suggested_fix="Expose dynamic status text through role=\"status\", role=\"alert\", or an appropriate aria-live region when it appears without moving focus.",
            )
        )
        break

    return issues


_SKIP_LINK_TEXT = re.compile(r"\b(skip|jump)\b.*\b(content|main|navigation)\b", re.IGNORECASE)


def analyze_bypass_blocks(html: str) -> list[AccessibilityIssue]:





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


        if len(visible_norm) < 3 or not re.search(r"[a-z]", visible_norm):
            continue
        if visible_norm in aria_norm:
            continue
        functional_menu_names = {
            "up one menu level",
            "close menu",
            "open menu",
            "toggle menu",
            "expand menu",
            "collapse menu",
            "previous menu",
            "back",
        }




        if aria_norm in functional_menu_names:
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

    pattern = re.compile(rf"<{tag}\b[^>]*>(.*?)</{tag}>", re.IGNORECASE | re.DOTALL)
    return "\n".join(match.group(1) for match in pattern.finditer(html))


def _has_nearby_text(parser: _StaticHTMLParser, words: set[str]) -> bool:

    text = parser.document_text.casefold()
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def _has_control_text(parser: _StaticHTMLParser, words: set[str]) -> bool:

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

    return bool(re.search(r"prefers-reduced-motion", html, re.IGNORECASE))


def _script_has(pattern: str, scripts: str) -> bool:
    return bool(re.search(pattern, scripts, re.IGNORECASE | re.DOTALL))


def analyze_wcag_static_evidence(html: str) -> list[AccessibilityIssue]:






    parser = _parse_html(html)
    issues: list[AccessibilityIssue] = []
    scripts = _raw_block_text(html, "script")
    styles = _raw_block_text(html, "style")
    combined_code = "\n".join([styles, scripts])



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
        analyze_authentication_and_error_prevention,
        analyze_wcag_static_evidence,
    ]:
        issues.extend(check(html))

    return issues


def analyze_html(html: str) -> dict[str, Any]:

    issues = analyze_html_static(html)

    return {
        "html_length": len(html),
        "issue_count": len(issues),
        "checks_run": STATIC_CHECKS_RUN,
        "notes": "Static HTML analysis is limited and does not replace a full audit.",
    }


def analyze_browser_page(url: str) -> dict[str, Any]:





    return {
        "url": url,
        "notes": "Browser automation is not implemented yet.",
    }


def analyze_pdf(path: str) -> dict[str, Any]:





    return {
        "path": path,
        "notes": "PDF analysis is not implemented yet.",
    }
