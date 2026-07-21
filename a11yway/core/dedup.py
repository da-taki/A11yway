







from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import re

from a11yway.core.finding_validation import cluster_repeated_findings, validate_findings
from a11yway.models.issue import AccessibilityIssue




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
    "confirmed_by_multiple_engines": 5,
    "repeat_verified": 4,
    "strong": 3,
    "likely": 2,
    "needs_review": 1,
    "weak_heuristic": 0,
    "informational": 0,
}

DEFAULT_EVIDENCE_SOURCE = "static"


def _normalize_identity_text(value: str) -> str:

    lowered = str(value).casefold()


    cleaned = re.sub(r"[<>/\"'=]", " ", lowered)
    return " ".join(sorted(cleaned.split()))


def _normalize_html_snippet(value: str) -> str:

    parser = _FirstElementParser()
    try:
        parser.feed(str(value or ""))
    except Exception:
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

    return _CANONICAL_ISSUE_TYPES.get(issue_type, issue_type)


def _issue_identity(issue: AccessibilityIssue) -> str:

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

    return f"reason:{_normalize_identity_text(issue.evidence.get('reason', ''))}"


def finding_fingerprint(issue: AccessibilityIssue) -> str:





    raw = "|".join([_canonical_issue_type(issue.issue_type), _issue_identity(issue)])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _evidence_source(issue: AccessibilityIssue) -> str:

    if isinstance(issue.evidence, dict):
        return issue.evidence.get("detected_in") or DEFAULT_EVIDENCE_SOURCE
    return DEFAULT_EVIDENCE_SOURCE


def deduplicate_issues(issues: list[AccessibilityIssue]) -> list[AccessibilityIssue]:












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
