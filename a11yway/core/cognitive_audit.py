

from __future__ import annotations

import re

from a11yway.core.extended_results import HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import attr, parse_elements, selector_for, text_content, visible_text
from a11yway.models.issue import AccessibilityIssue


COGNITIVE_LIMITATIONS = [
    "Cognitive accessibility findings are heuristic review points.",
    "Readability or density evidence alone is not a WCAG conformance failure.",
]


AMBIGUOUS_ACTIONS = {"click here", "read more", "learn more", "more", "submit", "go", "continue"}


def analyze_cognitive(html: str, source: str) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    elements = parse_elements(html)
    text = text_content(html)
    long_sentences = [sentence for sentence in re.split(r"[.!?]+", text) if len(sentence.split()) > 35]
    if long_sentences:
        issues.append(
            extended_issue(
                module="cognitive",
                check_id="dense_instructions",
                title="Long dense text may need clearer structure",
                issue_type="cognitive_dense_text_review",
                severity="low",
                source=source,
                observed=f"{len(long_sentences)} sentences exceed 35 words.",
                expected="Break complex instructions into headings, lists, examples, or step indicators.",
                manual="Review whether the text is instructions-critical and whether structure helps comprehension.",
                evidence_type=HEURISTIC,
                confidence="informational",
            )
        )
    for control in [e for e in elements if e["tag"] in {"a", "button"}]:
        label = visible_text(control).strip().lower()
        aria = attr(control, "aria-label").strip().lower()
        if label in AMBIGUOUS_ACTIONS and not aria:
            issues.append(
                extended_issue(
                    module="cognitive",
                    check_id="ambiguous_action_text",
                    title="Action text may be ambiguous out of context",
                    issue_type="cognitive_ambiguous_action_text",
                    severity="low",
                    source=source,
                    selector=selector_for(control),
                    observed=f"Control text is '{label}'.",
                    expected="Use specific action labels or an accessible name that explains the destination/action.",
                    manual="Check whether surrounding context makes the action clear for screen-reader link lists and cognitive load.",
                    evidence_type=HEURISTIC,
                    snippet=control.get("snippet", ""),
                )
            )
    destructive_terms = {"delete", "remove", "discard", "cancel application", "withdraw"}
    for button in [e for e in elements if e["tag"] in {"button", "a"}]:
        label = (visible_text(button) + " " + attr(button, "aria-label")).lower()
        if any(term in label for term in destructive_terms) and "confirm" not in html.lower():
            issues.append(
                extended_issue(
                    module="cognitive",
                    check_id="destructive_confirmation",
                    title="Destructive action may lack confirmation evidence",
                    issue_type="cognitive_destructive_action_review",
                    severity="medium",
                    source=source,
                    selector=selector_for(button),
                    observed="Destructive action text found without obvious confirmation wording in page.",
                    expected="Require confirmation or clear recovery for destructive actions.",
                    manual="Verify the actual activation flow in a safe local fixture or explicitly permitted environment.",
                    evidence_type=HEURISTIC,
                    snippet=button.get("snippet", ""),
                )
            )
    if re.search(r"\b(password|passphrase)\b", text, re.I) and len(re.findall(r"\b(must|require|required|at least|uppercase|symbol|special)\b", text, re.I)) >= 4:
        issues.append(
            extended_issue(
                module="cognitive",
                check_id="complex_password_rules",
                title="Password rules may be cognitively complex",
                issue_type="cognitive_complex_password_rules",
                severity="low",
                source=source,
                observed="Several password-requirement terms were found.",
                expected="Keep password requirements clear, visible before failure, and compatible with password managers.",
                manual="Review the password flow in a local fixture and verify examples/help are present.",
                evidence_type=HEURISTIC,
            )
        )
    return issues, module_result("cognitive", "cognitive_review_points", issues, limitations=COGNITIVE_LIMITATIONS).to_json()
