"""Placeholder page analysis helpers.

Future versions can use this module to inspect HTML, browser state,
PDF files, and accessibility trees.
"""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Any

from a11yway.models.issue import AccessibilityIssue


IGNORED_INPUT_TYPES = {"hidden", "submit", "button", "reset"}


class _FormLabelParser(HTMLParser):
    """Small HTML parser for form label checks.

    This is intentionally limited. It catches common label patterns without
    trying to become a full browser or accessibility-tree implementation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.label_for_values: set[str] = set()
        self.controls: list[dict[str, str | bool]] = []
        self._label_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        tag_name = tag.lower()

        if tag_name == "label":
            self._label_depth += 1
            label_for = attrs_dict.get("for")
            if label_for:
                self.label_for_values.add(label_for)
            return

        if tag_name not in {"input", "textarea", "select"}:
            return

        input_type = attrs_dict.get("type", "text").lower()
        if tag_name == "input" and input_type in IGNORED_INPUT_TYPES:
            return

        self.controls.append(
            {
                "tag": tag_name,
                "type": input_type,
                "id": attrs_dict.get("id", ""),
                "name": attrs_dict.get("name", ""),
                "aria_label": attrs_dict.get("aria-label", ""),
                "aria_labelledby": attrs_dict.get("aria-labelledby", ""),
                "title": attrs_dict.get("title", ""),
                "wrapped_by_label": self._label_depth > 0,
            }
        )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "label" and self._label_depth > 0:
            self._label_depth -= 1


def analyze_html_forms(html: str) -> list[AccessibilityIssue]:
    """Detect form controls that appear to be missing accessible labels."""
    parser = _FormLabelParser()
    parser.feed(html)

    issues: list[AccessibilityIssue] = []
    for control in parser.controls:
        control_id = str(control["id"])
        has_label_for = bool(control_id and control_id in parser.label_for_values)
        has_wrapping_label = bool(control["wrapped_by_label"])
        has_aria_label = bool(control["aria_label"])
        has_aria_labelledby = bool(control["aria_labelledby"])
        has_title = bool(control["title"])

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

        tag = str(control["tag"])
        input_type = str(control["type"])
        control_name = str(control["name"])
        identity_parts = []
        if control_id:
            identity_parts.append(f'id="{control_id}"')
        if control_name:
            identity_parts.append(f'name="{control_name}"')
        identity = ", ".join(identity_parts) if identity_parts else "no id or name"

        issues.append(
            AccessibilityIssue(
                title="Form control is missing an accessible label",
                issue_type="missing_form_label",
                severity="high",
                agent_name="Page Analyzer",
                evidence=f"Found unlabeled <{tag}> control with type=\"{input_type}\" and {identity}.",
                suggested_fix=(
                    "Add a visible <label> connected with for/id. Use aria-label only "
                    "when a visible label is not possible."
                ),
            )
        )

    return issues


def analyze_html(html: str) -> dict[str, Any]:
    """Return placeholder analysis for an HTML page.

    TODO: Parse HTML and inspect headings, landmarks, labels, images,
    controls, focusable elements, and media.
    """
    form_issues = analyze_html_forms(html)

    return {
        "html_length": len(html),
        "form_label_issue_count": len(form_issues),
        "notes": "Only basic form label analysis is implemented so far.",
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
