

from __future__ import annotations

import re

from a11yway.core.extended_results import HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import attr, parse_elements, selector_for, text_content
from a11yway.models.issue import AccessibilityIssue


LANGUAGE_LIMITATIONS = [
    "Language detection is conservative and script-based; proper names and short phrases are ignored.",
    "Findings are evidence for manual review, not automatic language-conformance claims.",
]

SCRIPT_RANGES = {
    "hi": ("Devanagari", r"[\u0900-\u097F]"),
    "pa": ("Gurmukhi", r"[\u0A00-\u0A7F]"),
    "bn": ("Bengali", r"[\u0980-\u09FF]"),
    "ta": ("Tamil", r"[\u0B80-\u0BFF]"),
    "te": ("Telugu", r"[\u0C00-\u0C7F]"),
    "ur": ("Arabic/Urdu", r"[\u0600-\u06FF]"),
    "ar": ("Arabic", r"[\u0600-\u06FF]"),
    "he": ("Hebrew", r"[\u0590-\u05FF]"),
}


def analyze_language(html: str, source: str) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    elements = parse_elements(html)
    html_el = next((e for e in elements if e["tag"] == "html"), None)
    page_lang = attr(html_el, "lang") if html_el else ""
    if page_lang and not re.match(r"^[a-zA-Z]{2,3}(-[a-zA-Z0-9]{2,8})*$", page_lang):
        issues.append(
            extended_issue(
                module="language",
                check_id="valid_lang_code",
                title="Page language code appears invalid",
                issue_type="language_invalid_code",
                severity="medium",
                source=source,
                selector="html",
                observed=f"lang='{page_lang}'",
                expected="Use a valid BCP 47 language tag.",
                manual="Confirm the declared language matches page content.",
                evidence_type=HEURISTIC,
            )
        )
    body_text = text_content(html)
    for lang, (label, pattern) in SCRIPT_RANGES.items():
        matches = re.findall(pattern, body_text)
        if len(matches) < 8:
            continue
        tagged = any(attr(e, "lang").lower().startswith(lang) for e in elements)
        if not tagged and not page_lang.lower().startswith(lang):
            issues.append(
                extended_issue(
                    module="language",
                    check_id="mixed_script_lang",
                    title=f"{label} content may lack a language tag",
                    issue_type="language_passage_lang_missing",
                    severity="medium",
                    source=source,
                    observed=f"Detected {len(matches)} {label} script characters without matching lang='{lang}' evidence.",
                    expected="Mark sustained language changes with lang attributes.",
                    manual="Ignore names, isolated words, or examples; verify sustained passages and accessible names.",
                    evidence_type=HEURISTIC,
                )
            )
    rtl_chars = len(re.findall(r"[\u0590-\u08FF]", body_text))
    if rtl_chars >= 8:
        has_dir = any(attr(e, "dir").lower() in {"rtl", "auto"} for e in elements)
        if not has_dir:
            issues.append(
                extended_issue(
                    module="language",
                    check_id="rtl_direction",
                    title="RTL content may lack direction metadata",
                    issue_type="language_rtl_direction_missing",
                    severity="medium",
                    source=source,
                    observed="Sustained RTL-script text was detected without dir='rtl' or dir='auto'.",
                    expected="Use appropriate direction metadata for right-to-left passages and mixed LTR/RTL content.",
                    manual="Verify punctuation and number ordering in the rendered page.",
                    evidence_type=HEURISTIC,
                )
            )
    for element in elements:
        name = attr(element, "aria-label")
        if name and re.search(r"[\u0590-\u0C7F]", name) and not attr(element, "lang"):
            issues.append(
                extended_issue(
                    module="language",
                    check_id="accessible_name_language",
                    title="Non-English accessible name may lack language metadata",
                    issue_type="language_accessible_name_lang_missing",
                    severity="low",
                    source=source,
                    selector=selector_for(element),
                    observed="aria-label contains non-Latin script with no local lang attribute.",
                    expected="Mark accessible names or their owning region with the correct language when pronunciation matters.",
                    manual="Confirm whether the label is a proper name or sustained localized text.",
                    evidence_type=HEURISTIC,
                    snippet=element.get("snippet", ""),
                )
            )
    return issues, module_result("language", "multilingual_bidi_review", issues, limitations=LANGUAGE_LIMITATIONS).to_json()
