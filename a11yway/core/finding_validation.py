"""Post-collection finding validation and clustering helpers.

The raw rule checks intentionally stay small and conservative. This module
adds a second pass after collection/deduplication so reports can explain how
strong each finding is, which engines supported it, and whether repeated
elements look like one shared root issue.
"""

from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from a11yway.core.rules import DEFAULT_CONFIDENCE_BY_RULE, FALLBACK_CONFIDENCE, get_rule
from a11yway.models.issue import AccessibilityIssue


CONFIDENCE_CONFIRMED_BY_MULTIPLE_ENGINES = "confirmed_by_multiple_engines"
CONFIDENCE_STRONG = "strong"
CONFIDENCE_LIKELY = "likely"
CONFIDENCE_NEEDS_REVIEW = "needs_review"
CONFIDENCE_WEAK_HEURISTIC = "weak_heuristic"
CONFIDENCE_SUPPRESSED = "suppressed"

AI_SOURCES = {"ai_scout", "ai"}
WEAK_HEURISTIC_RULES = {
    "axe_tabindex",
    "generic_link_text",
    "image_empty_alt_suspicious",
    "multiple_h1",
    "skipped_heading_level",
    "contrast_unresolved_background",
    "reflow_overlap",
    "focus_indicator_missing",
    "possible_flashing_content",
    "interaction_motion_no_reduced_motion",
    "hover_focus_content",
    "pointer_gesture_no_alternative",
    "dragging_no_alternative",
    "moving_content_no_pause",
}
STRONG_BROWSER_RULES = {
    "keyboard_trap",
    "task_step_blocked",
    "task_control_not_keyboard_reachable",
    "unnamed_focus_stop",
    "browser_focus_on_hidden_element",
}


class _SnippetParser(HTMLParser):
    """Capture a compact element signature from a snippet."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tag = ""
        self.attrs: dict[str, str] = {}
        self.text_parts: list[str] = []
        self._capturing = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.tag:
            return
        self.tag = tag.casefold()
        self.attrs = {name.casefold(): value or "" for name, value in attrs}
        self._capturing = True

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self._capturing = False

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == self.tag:
            self._capturing = False

    def handle_data(self, data: str) -> None:
        if self._capturing and data.strip():
            self.text_parts.append(data)


def normalize_text(value: Any) -> str:
    """Return stable lowercase text for fingerprints and summaries."""
    lowered = str(value or "").casefold()
    cleaned = re.sub(r"[^\w\s:/#.-]", " ", lowered, flags=re.UNICODE)
    return " ".join(cleaned.split())


def normalize_page_url(url: str) -> str:
    """Normalize a page URL without making network requests."""
    raw = str(url or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    if not parsed.scheme:
        return raw.replace("\\", "/")
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    netloc = parsed.netloc.casefold()
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme.casefold(), netloc, path, query, ""))


def _parse_snippet(snippet: str) -> _SnippetParser:
    parser = _SnippetParser()
    try:
        parser.feed(snippet or "")
    except Exception:  # noqa: BLE001 - snippets are best-effort evidence
        pass
    return parser


def _normalized_snippet(snippet: str) -> str:
    parser = _parse_snippet(snippet)
    if not parser.tag:
        return normalize_text(snippet)
    parts = [parser.tag]
    for attr in [
        "id",
        "name",
        "type",
        "href",
        "src",
        "role",
        "aria-label",
        "aria-labelledby",
    ]:
        if parser.attrs.get(attr):
            parts.append(f"{attr}={normalize_text(parser.attrs[attr])}")
    text = normalize_text(" ".join(parser.text_parts))
    if text:
        parts.append(f"text={text[:80]}")
    return "|".join(parts)


def _evidence_sources(issue: AccessibilityIssue) -> list[str]:
    evidence = issue.evidence if isinstance(issue.evidence, dict) else {}
    sources = evidence.get("evidence_sources")
    if isinstance(sources, list) and sources:
        return [str(source) for source in sources]
    detected = evidence.get("detected_in")
    if detected:
        return [str(detected)]
    return ["static"]


def _source_engine(issue: AccessibilityIssue) -> str:
    sources = _evidence_sources(issue)
    if len(sources) > 1:
        return "multiple"
    return sources[0]


def _selector_for(evidence: dict[str, Any]) -> str:
    for key in ["selector", "target"]:
        value = evidence.get(key)
        if value not in [None, ""]:
            return str(value)
    tag = evidence.get("tag") or "element"
    if evidence.get("id"):
        return f"{tag}#{evidence['id']}"
    if evidence.get("name"):
        return f'{tag}[name="{evidence["name"]}"]'
    if evidence.get("href"):
        return f'{tag}[href="{evidence["href"]}"]'
    return str(tag)


def _accessible_name(evidence: dict[str, Any]) -> str:
    for key in [
        "accessible_name",
        "accessible_name_guess",
        "announcement",
        "aria_label",
        "label_text",
        "visible_label",
        "text",
        "title",
    ]:
        value = evidence.get(key)
        if value not in [None, ""]:
            return str(value)
    return ""


def _visible_text(evidence: dict[str, Any]) -> str:
    for key in ["visible_text", "text", "label_text", "matched_phrase"]:
        value = evidence.get(key)
        if value not in [None, ""]:
            return str(value)
    return ""


def _role_for(evidence: dict[str, Any]) -> str:
    return str(
        evidence.get("role")
        or evidence.get("announced_role")
        or evidence.get("tag")
        or ""
    )


def _component_signature(issue: AccessibilityIssue, evidence: dict[str, Any]) -> str:
    explicit = evidence.get("component_signature")
    if explicit:
        return normalize_text(explicit)
    selector = str(evidence.get("selector") or evidence.get("target") or "")
    snippet = str(evidence.get("snippet") or "")
    haystack = " ".join([selector, snippet, str(evidence.get("id") or ""), str(evidence.get("name") or "")])
    lowered = haystack.casefold()
    for component in [
        "navigation",
        "nav",
        "header",
        "footer",
        "cookie",
        "search",
        "card",
        "carousel",
        "chat",
        "recaptcha",
        "captcha",
        "map",
        "table",
        "form",
    ]:
        if component in lowered:
            return component
    tag = evidence.get("tag")
    issue_type = issue.issue_type
    if tag:
        return f"{issue_type}:{tag}"
    return issue_type


def _dedupe_fingerprint(issue: AccessibilityIssue, evidence: dict[str, Any]) -> str:
    existing = evidence.get("fingerprint") or evidence.get("deduplication_fingerprint")
    if existing:
        return str(existing)
    raw = "|".join(
        [
            issue.issue_type,
            _selector_for(evidence),
            _normalized_snippet(str(evidence.get("snippet") or "")),
            normalize_text(_visible_text(evidence))[:80],
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _effective_confidence(issue: AccessibilityIssue) -> str:
    return issue.confidence or DEFAULT_CONFIDENCE_BY_RULE.get(
        issue.issue_type, FALLBACK_CONFIDENCE
    )


def _confidence_level(issue: AccessibilityIssue, evidence: dict[str, Any]) -> str:
    sources = [source for source in _evidence_sources(issue) if source not in AI_SOURCES]
    if evidence.get("suppressed"):
        return CONFIDENCE_SUPPRESSED
    if len(set(sources)) >= 2:
        return CONFIDENCE_CONFIRMED_BY_MULTIPLE_ENGINES
    if issue.issue_type in STRONG_BROWSER_RULES:
        return CONFIDENCE_STRONG
    effective = _effective_confidence(issue)
    if effective == "confirmed":
        return CONFIDENCE_STRONG
    if issue.issue_type in WEAK_HEURISTIC_RULES:
        return CONFIDENCE_WEAK_HEURISTIC if effective in {"needs_review", "informational"} else CONFIDENCE_NEEDS_REVIEW
    if effective == "likely":
        return CONFIDENCE_LIKELY
    if effective == "needs_review":
        return CONFIDENCE_NEEDS_REVIEW
    if effective == "informational":
        return CONFIDENCE_WEAK_HEURISTIC
    return CONFIDENCE_NEEDS_REVIEW


def _verification_status(confidence_level: str) -> str:
    if confidence_level == CONFIDENCE_CONFIRMED_BY_MULTIPLE_ENGINES:
        return "cross_checked"
    if confidence_level in {CONFIDENCE_STRONG, CONFIDENCE_LIKELY}:
        return "single_engine_supported"
    if confidence_level == CONFIDENCE_SUPPRESSED:
        return "suppressed"
    return "needs_manual_review"


def _human_review_reason(issue: AccessibilityIssue, evidence: dict[str, Any], confidence_level: str) -> str:
    reason = str(evidence.get("reason") or "").strip()
    if confidence_level == CONFIDENCE_CONFIRMED_BY_MULTIPLE_ENGINES:
        return "Multiple deterministic engines reported the same root concern."
    if confidence_level == CONFIDENCE_STRONG:
        return reason or "Strong deterministic browser or task evidence supports this finding."
    if confidence_level == CONFIDENCE_LIKELY:
        return reason or "Single-source deterministic evidence supports this finding."
    if confidence_level == CONFIDENCE_WEAK_HEURISTIC:
        return reason or "Heuristic evidence only; a trained reviewer should confirm impact."
    if confidence_level == CONFIDENCE_SUPPRESSED:
        return reason or "Finding was intentionally suppressed or downgraded."
    return reason or "Manual review is needed before treating this as a confirmed accessibility barrier."


def validate_findings(
    issues: list[AccessibilityIssue],
    page_url: str = "",
) -> list[AccessibilityIssue]:
    """Enrich findings with validation metadata while preserving compatibility."""
    normalized_url = normalize_page_url(page_url)
    for issue in issues:
        if not isinstance(issue.evidence, dict):
            issue.evidence = {"description": str(issue.evidence)}
        evidence = issue.evidence
        rule = get_rule(issue.issue_type) or {}
        fingerprint = _dedupe_fingerprint(issue, evidence)
        confidence_level = _confidence_level(issue, evidence)
        sources = _evidence_sources(issue)

        evidence.setdefault("rule_id", issue.issue_type)
        if normalized_url:
            evidence["normalized_page_url"] = normalized_url
        evidence.setdefault("issue_category", rule.get("category", "Uncategorized"))
        evidence.setdefault("source_engine", _source_engine(issue))
        evidence.setdefault("element_selector", _selector_for(evidence))
        if evidence.get("snippet"):
            evidence.setdefault(
                "normalized_element_snippet",
                _normalized_snippet(str(evidence.get("snippet") or "")),
            )
        evidence.setdefault("accessible_name", _accessible_name(evidence))
        evidence.setdefault("visible_text", _visible_text(evidence))
        evidence.setdefault("role", _role_for(evidence))
        evidence.setdefault("confidence_level", confidence_level)
        evidence.setdefault("verification_status", _verification_status(confidence_level))
        evidence.setdefault("deduplication_fingerprint", fingerprint)
        evidence.setdefault("fingerprint", fingerprint)
        evidence.setdefault("human_review_reason", _human_review_reason(issue, evidence, confidence_level))
        evidence.setdefault("related_finding_ids", [])
        evidence.setdefault("occurrence_count", int(evidence.get("merged_finding_count", 1) or 1))
        evidence.setdefault("affected_page_count", 1)
        evidence.setdefault("component_signature", _component_signature(issue, evidence))
        evidence.setdefault("evidence_sources", sources)
    return issues


def root_issue_key(issue: AccessibilityIssue) -> str:
    """Return a stable key for the unique root issue represented by a finding."""
    evidence = issue.evidence if isinstance(issue.evidence, dict) else {}
    raw = "|".join(
        [
            str(evidence.get("rule_id") or issue.issue_type),
            str(evidence.get("component_signature") or ""),
            str(evidence.get("deduplication_fingerprint") or ""),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def cluster_repeated_findings(issues: list[AccessibilityIssue]) -> list[AccessibilityIssue]:
    """Merge repeated findings from an explicitly identified shared component.

    This only collapses findings that already carry a component signature and
    share the same rule. Findings without component evidence remain separate.
    """
    validate_findings(issues)
    grouped: dict[tuple[str, str], AccessibilityIssue] = {}
    order: list[tuple[str, str]] = []
    for issue in issues:
        evidence = issue.evidence if isinstance(issue.evidence, dict) else {}
        signature = str(evidence.get("component_signature") or "")
        explicit = bool(evidence.get("component_signature_explicit"))
        should_cluster = explicit or evidence.get("cluster_repeated_component")
        if not should_cluster:
            key = (str(evidence.get("deduplication_fingerprint")), "")
        else:
            key = (issue.issue_type, signature)
        if key not in grouped:
            grouped[key] = issue
            order.append(key)
            continue
        primary = grouped[key]
        primary_evidence = primary.evidence if isinstance(primary.evidence, dict) else {}
        current_count = int(primary_evidence.get("occurrence_count", 1) or 1)
        next_count = int(evidence.get("occurrence_count", 1) or 1)
        primary_evidence["occurrence_count"] = current_count + next_count
        primary_evidence["merged_finding_count"] = primary_evidence["occurrence_count"]
        examples = list(primary_evidence.get("example_elements", []))
        if not examples:
            examples.append(
                primary_evidence.get("element_selector")
                or primary_evidence.get("snippet")
                or primary.issue_type
            )
        examples.append(evidence.get("element_selector") or evidence.get("snippet") or issue.issue_type)
        primary_evidence["example_elements"] = examples[:5]
        related = list(primary_evidence.get("related_finding_ids", []))
        related.append(str(evidence.get("deduplication_fingerprint") or ""))
        primary_evidence["related_finding_ids"] = [item for item in related if item]
        primary_evidence["human_review_reason"] = (
            "Repeated findings share a component signature; review one primary "
            "example, then sample the related occurrences."
        )
    return [grouped[key] for key in order]


def issue_cluster_summary(issues: list[AccessibilityIssue]) -> list[dict[str, Any]]:
    """Build compact component/root summaries for reports."""
    validate_findings(issues)
    clusters: dict[str, dict[str, Any]] = {}
    for issue in issues:
        evidence = issue.evidence if isinstance(issue.evidence, dict) else {}
        key = root_issue_key(issue)
        cluster = clusters.setdefault(
            key,
            {
                "root_issue_id": key,
                "rule_id": evidence.get("rule_id") or issue.issue_type,
                "issue_type": issue.issue_type,
                "issue_category": evidence.get("issue_category", ""),
                "component_signature": evidence.get("component_signature", ""),
                "confidence_level": evidence.get("confidence_level", ""),
                "occurrence_count": 0,
                "affected_page_count": 0,
                "example_elements": [],
                "affected_pages": [],
            },
        )
        cluster["occurrence_count"] += int(evidence.get("occurrence_count", 1) or 1)
        cluster["affected_page_count"] = max(
            int(cluster["affected_page_count"]),
            int(evidence.get("affected_page_count", 1) or 1),
        )
        selector = evidence.get("element_selector") or evidence.get("snippet")
        if selector and selector not in cluster["example_elements"]:
            cluster["example_elements"].append(selector)
        page = evidence.get("normalized_page_url")
        if page and page not in cluster["affected_pages"]:
            cluster["affected_pages"].append(page)
    return sorted(
        clusters.values(),
        key=lambda item: (-int(item["occurrence_count"]), str(item["rule_id"])),
    )
