"""Merge duplicate findings discovered through different evidence sources.

Static analysis, the rendered-DOM re-check, browser interaction, the
accessibility tree, and axe-core can all report the same underlying problem
on the same element. Reports should show one primary finding that lists
every evidence source, not the same barrier several times.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import re

from a11yway.core.finding_validation import cluster_repeated_findings, validate_findings
from a11yway.models.issue import AccessibilityIssue

# Evidence keys that identify the element a finding is about, strongest
# identity first. Text-like values are normalized so a static snippet and a
# browser-rendered snippet of the same element compare equal.
_IDENTITY_KEYS = ["snippet", "id", "selector", "name", "text", "href", "src"]

_CANONICAL_ISSUE_TYPES = {
    "axe_button_name": "missing_button_name",
    "axe_image_alt": "missing_image_alt",
    "axe_label": "missing_form_label",
    "axe_link_name": "missing_link_name",
    "axe_heading_order": "skipped_heading_level",
    "axe_document_title": "missing_page_title",
    "axe_html_has_lang": "missing_html_lang",
}

_STABLE_HTML_ATTRS = [
    "id",
    "name",
    "type",
    "href",
    "src",
    "for",
    "role",
    "aria-label",
    "aria-labelledby",
]


class _FirstElementParser(HTMLParser):
    """Capture the first element tag and attributes from a snippet."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tag = ""
        self.attrs: dict[str, str] = {}
        self.text_parts: list[str] = []
        self._capturing_text = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.tag:
            return
        self.tag = tag
        self.attrs = {name.casefold(): value or "" for name, value in attrs}
        self._capturing_text = True

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self._capturing_text = False

    def handle_endtag(self, tag: str) -> None:
        if self.tag and tag.casefold() == self.tag.casefold():
            self._capturing_text = False

    def handle_data(self, data: str) -> None:
        if self._capturing_text and data.strip():
            self.text_parts.append(data)

_CONFIDENCE_RANK = {
    "confirmed": 3,
    "likely": 2,
    "needs_review": 1,
    "informational": 0,
}

DEFAULT_EVIDENCE_SOURCE = "static"


def _normalize_identity_text(value: str) -> str:
    """Normalize snippets and text for cross-source comparison."""
    lowered = str(value).casefold()
    # Attribute order and self-closing slashes can differ between the source
    # HTML and the browser-serialized DOM; strip syntax that varies.
    cleaned = re.sub(r"[<>/\"'=]", " ", lowered)
    return " ".join(sorted(cleaned.split()))


def _normalize_html_snippet(value: str) -> str:
    """Return a stable element identity from an HTML snippet when possible."""
    parser = _FirstElementParser()
    try:
        parser.feed(str(value or ""))
    except Exception:  # noqa: BLE001 - malformed snippets fall back below
        return _normalize_identity_text(value)

    if not parser.tag:
        return _normalize_identity_text(value)

    parts = [parser.tag.casefold()]
    for attr in _STABLE_HTML_ATTRS:
        if attr not in parser.attrs:
            continue
        raw_value = parser.attrs[attr]
        parts.append(f"{attr}={_normalize_identity_text(raw_value)}")

    text = " ".join(" ".join(parser.text_parts).split())
    if text:
        parts.append(f"text={_normalize_identity_text(text)[:80]}")
    return "|".join(parts)


def _canonical_issue_type(issue_type: str) -> str:
    """Map equivalent third-party rules to the native A11yway rule family."""
    return _CANONICAL_ISSUE_TYPES.get(issue_type, issue_type)


def _issue_identity(issue: AccessibilityIssue) -> str:
    """Return the strongest element identity available in the evidence."""
    if not isinstance(issue.evidence, dict):
        return _normalize_identity_text(str(issue.evidence))
    for key in _IDENTITY_KEYS:
        value = issue.evidence.get(key)
        if value not in [None, ""]:
            if key == "snippet":
                return f"{key}:{_normalize_html_snippet(value)}"
            if key in {"snippet", "text"}:
                return f"{key}:{_normalize_identity_text(value)}"
            return f"{key}:{value}"
    # Page-level findings (missing title, missing h1) identify by reason.
    return f"reason:{_normalize_identity_text(issue.evidence.get('reason', ''))}"


def finding_fingerprint(issue: AccessibilityIssue) -> str:
    """Return a stable fingerprint for one finding.

    Built from the rule and the normalized element identity, so the same
    barrier found statically and in the browser produces the same value.
    """
    raw = "|".join([_canonical_issue_type(issue.issue_type), _issue_identity(issue)])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _evidence_source(issue: AccessibilityIssue) -> str:
    """Return where a finding was detected."""
    if isinstance(issue.evidence, dict):
        return issue.evidence.get("detected_in") or DEFAULT_EVIDENCE_SOURCE
    return DEFAULT_EVIDENCE_SOURCE


def deduplicate_issues(issues: list[AccessibilityIssue]) -> list[AccessibilityIssue]:
    """Merge findings that share a fingerprint across evidence sources.

    The first occurrence (list order puts static findings first) becomes the
    primary finding. Its evidence gains:

    - ``evidence_sources``: every detection mode that saw the problem
    - ``merged_finding_count``: how many raw findings were merged
    - ``fingerprint``: the stable finding fingerprint

    Confidence is upgraded to the strongest confidence among the merged
    findings, because independent detection strengthens the evidence.
    """
    merged: dict[str, AccessibilityIssue] = {}
    order: list[str] = []
    sources: dict[str, list[str]] = {}
    counts: dict[str, int] = {}

    for issue in issues:
        fingerprint = finding_fingerprint(issue)
        source = _evidence_source(issue)
        if fingerprint not in merged:
            merged[fingerprint] = issue
            order.append(fingerprint)
            sources[fingerprint] = [source]
            counts[fingerprint] = 1
            continue
        counts[fingerprint] += 1
        if source not in sources[fingerprint]:
            sources[fingerprint].append(source)
        primary = merged[fingerprint]
        primary_rank = _CONFIDENCE_RANK.get(primary.confidence or "", -1)
        candidate_rank = _CONFIDENCE_RANK.get(issue.confidence or "", -1)
        if candidate_rank > primary_rank:
            primary.confidence = issue.confidence

    result: list[AccessibilityIssue] = []
    for fingerprint in order:
        issue = merged[fingerprint]
        if isinstance(issue.evidence, dict):
            issue.evidence["fingerprint"] = fingerprint
            issue.evidence["evidence_sources"] = sources[fingerprint]
            if counts[fingerprint] > 1:
                issue.evidence["merged_finding_count"] = counts[fingerprint]
                issue.evidence["occurrence_count"] = counts[fingerprint]
        result.append(issue)
    return cluster_repeated_findings(validate_findings(result))
