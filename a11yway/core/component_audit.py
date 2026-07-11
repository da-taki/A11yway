"""Complex component pattern checks."""

from __future__ import annotations

from a11yway.core.extended_results import HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import attr, parse_elements, selector_for, visible_text
from a11yway.models.issue import AccessibilityIssue


COMPONENT_LIMITATIONS = [
    "Component checks use WAI-ARIA pattern guidance as review evidence, not certification.",
    "Keyboard behavior is only verified when a browser/workflow module exercises the component.",
]


ROLE_REQUIREMENTS = {
    "dialog": ("aria-modal", "true", "Dialog should identify modal state when it behaves modally."),
    "alertdialog": ("aria-modal", "true", "Alert dialog should identify modal state when it behaves modally."),
    "tab": ("aria-selected", "", "Tabs should expose selected state."),
    "combobox": ("aria-expanded", "", "Combobox should expose expanded/collapsed state."),
    "menuitem": ("role", "menu", "Menuitems should be inside a menu/menubar pattern."),
    "slider": ("aria-valuenow", "", "Slider should expose current value."),
    "spinbutton": ("aria-valuenow", "", "Spinbutton should expose current value."),
    "treeitem": ("aria-expanded", "", "Expandable tree items should expose expanded state."),
}


def analyze_components(html: str, source: str) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    elements = parse_elements(html)
    ids = {}
    for element in elements:
        element_id = attr(element, "id")
        if element_id:
            ids.setdefault(element_id, []).append(element)
    for element_id, matches in ids.items():
        if len(matches) > 1:
            issues.append(
                extended_issue(
                    module="components",
                    check_id="duplicate_component_id",
                    title="Duplicate ID may break component relationships",
                    issue_type="component_duplicate_id",
                    severity="high",
                    source=source,
                    selector=f"#{element_id}",
                    observed=f"{len(matches)} elements share the same id.",
                    expected="Component relationships require unique IDs for aria-controls, aria-labelledby, and active descendants.",
                    manual="Inspect the component relationships and computed accessibility tree.",
                    evidence_type=HEURISTIC,
                    snippet=matches[0].get("snippet", ""),
                )
            )
    roles = [e for e in elements if attr(e, "role")]
    for element in roles:
        role = attr(element, "role").lower()
        if not (visible_text(element) or attr(element, "aria-label") or attr(element, "aria-labelledby")) and role in {"dialog", "tablist", "combobox", "menu", "menubar", "listbox", "tree", "grid"}:
            issues.append(
                extended_issue(
                    module="components",
                    check_id="component_accessible_name",
                    title=f"{role} component may lack an accessible name",
                    issue_type="component_name_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(element),
                    observed=f"role='{role}' component has no visible text, aria-label, or aria-labelledby.",
                    expected="Name complex widgets so users understand the control or region.",
                    manual="Check computed accessible name and screen-reader announcement.",
                    evidence_type=HEURISTIC,
                    snippet=element.get("snippet", ""),
                )
            )
        requirement = ROLE_REQUIREMENTS.get(role)
        if requirement:
            req_attr, req_value, expected = requirement
            has_value = attr(element, req_attr)
            if req_attr == "role":
                has_value = any(attr(other, "role").lower() == req_value for other in elements)
            if not has_value or (req_value and req_attr != "role" and has_value.lower() != req_value):
                issues.append(
                    extended_issue(
                        module="components",
                        check_id="component_required_state",
                        title=f"{role} component may lack required state",
                        issue_type="component_required_state_missing",
                        severity="medium",
                        source=source,
                        selector=selector_for(element),
                        observed=f"role='{role}' lacks expected {req_attr}.",
                        expected=expected,
                        manual="Verify the WAI-ARIA pattern, keyboard behavior, and announcement changes.",
                        evidence_type=HEURISTIC,
                        snippet=element.get("snippet", ""),
                    )
                )
    for carousel in [e for e in elements if "carousel" in (attr(e, "class") + attr(e, "id")).lower()]:
        controls = any("pause" in visible_text(e).lower() or "pause" in attr(e, "aria-label").lower() for e in elements)
        if not controls:
            issues.append(
                extended_issue(
                    module="components",
                    check_id="carousel_pause",
                    title="Carousel may lack pause/stop control",
                    issue_type="component_carousel_pause_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(carousel),
                    observed="Carousel-like component found without obvious pause control text.",
                    expected="Auto-advancing carousels should provide pause/stop controls and keyboard operation.",
                    manual="Verify whether it auto-advances and whether controls are reachable and announced.",
                    evidence_type=HEURISTIC,
                    snippet=carousel.get("snippet", ""),
                )
            )
    return issues, module_result("components", "complex_component_patterns", issues, limitations=COMPONENT_LIMITATIONS).to_json()
