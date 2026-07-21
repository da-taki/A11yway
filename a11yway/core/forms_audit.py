

from __future__ import annotations

from a11yway.core.extended_results import HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import accessible_name_hint, attr, parse_elements, selector_for, visible_text
from a11yway.models.issue import AccessibilityIssue


FORM_LIMITATIONS = [
    "Public-site form mode inspects markup and rendered-safe evidence only; it does not submit forms.",
    "Error recovery behavior is deterministic only for local or explicitly permitted workflows.",
]


def analyze_forms(html: str, source: str, *, permit_submission: bool = False) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    elements = parse_elements(html)
    controls = [
        element
        for element in elements
        if element["tag"] in {"input", "select", "textarea"}
        and attr(element, "type").lower() not in {"hidden", "submit", "button", "reset"}
    ]
    for control in controls:
        required = "required" in control.get("attrs", {}) or attr(control, "aria-required").lower() == "true"
        if required and not attr(control, "aria-describedby"):
            issues.append(
                extended_issue(
                    module="forms",
                    check_id="required_field_instruction",
                    title="Required field may lack programmatic instructions",
                    issue_type="form_required_instruction_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(control),
                    observed="Required control has no obvious label or described-by relationship.",
                    expected="Expose required state and instructions through a visible label and programmatic description.",
                    manual="Try the form in a local fixture or permitted environment and verify the required-field announcement.",
                    evidence_type=HEURISTIC,
                    snippet=control.get("snippet", ""),
                )
            )
        if attr(control, "aria-invalid").lower() == "true" and not attr(control, "aria-describedby"):
            issues.append(
                extended_issue(
                    module="forms",
                    check_id="error_association",
                    title="Invalid field may not be associated with an error message",
                    issue_type="form_error_not_described",
                    severity="high",
                    source=source,
                    selector=selector_for(control),
                    observed="Control is marked aria-invalid without aria-describedby.",
                    expected="Associate inline error text or an error summary with aria-describedby.",
                    manual="Trigger the error in a permitted fixture and confirm focus and screen-reader announcement.",
                    evidence_type=HEURISTIC,
                    snippet=control.get("snippet", ""),
                )
            )
        autocomplete = attr(control, "autocomplete")
        input_type = attr(control, "type").lower()
        if input_type in {"email", "tel", "password", "date"} and not autocomplete:
            issues.append(
                extended_issue(
                    module="forms",
                    check_id="input_purpose_detail",
                    title="Common personal-data field lacks autocomplete hint",
                    issue_type="form_autocomplete_missing",
                    severity="low",
                    source=source,
                    selector=selector_for(control),
                    observed=f"{input_type or control['tag']} control has no autocomplete token.",
                    expected="Use an appropriate autocomplete token when the field collects common user information.",
                    manual="Confirm whether the field collects user data or fixture-only data.",
                    evidence_type=HEURISTIC,
                    snippet=control.get("snippet", ""),
                )
            )
    for button in [e for e in elements if e["tag"] in {"button", "input"}]:
        text = accessible_name_hint(button).lower()
        if "show" in text and "password" in text and attr(button, "aria-pressed") == "":
            issues.append(
                extended_issue(
                    module="forms",
                    check_id="show_password_state",
                    title="Show-password control may not expose state",
                    issue_type="show_password_state_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(button),
                    observed="Show-password style control found without aria-pressed.",
                    expected="Expose the toggle state with aria-pressed or equivalent state text.",
                    manual="Toggle the control in a safe fixture and confirm state announcement.",
                    evidence_type=HEURISTIC,
                    snippet=button.get("snippet", ""),
                )
            )
    for form in [e for e in elements if e["tag"] == "form"]:
        action = attr(form, "action")
        method = attr(form, "method").lower()
        if not permit_submission and method == "post":
            issues.append(
                extended_issue(
                    module="forms",
                    check_id="safe_public_form_boundary",
                    title="Public form submission was not attempted",
                    issue_type="form_submission_blocked_safe_mode",
                    severity="low",
                    source=source,
                    selector=selector_for(form),
                    observed=f"Form uses POST action '{action}'.",
                    expected="Do not submit public forms unless explicit permission exists.",
                    manual="Use a local fixture or explicit permission before testing invalid submission and error recovery.",
                    evidence_type=HEURISTIC,
                    confidence="informational",
                    snippet=form.get("snippet", ""),
                )
            )
    result = module_result("forms", "safe_form_error_recovery", issues, limitations=FORM_LIMITATIONS)
    return issues, result.to_json()
