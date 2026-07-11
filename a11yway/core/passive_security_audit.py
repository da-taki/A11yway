"""Opt-in passive security observations.

This module never attacks, fuzzes, authenticates, or validates exploits. It
only inspects the provided public HTML/source metadata and optional response
headers already available from normal fetching.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from a11yway.core.extended_results import HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import attr, parse_elements, selector_for
from a11yway.models.issue import AccessibilityIssue


PASSIVE_SECURITY_NOTE = (
    "Passive security observations do not constitute a penetration test or a determination that a system is secure."
)

SECURITY_LIMITATIONS = [
    PASSIVE_SECURITY_NOTE,
    "A11yway does not inject payloads, brute force, scan ports, bypass access controls, or validate exploits.",
]


def analyze_passive_security(
    html: str,
    source: str,
    *,
    source_metadata: dict | None = None,
) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    parsed = urlparse(source)
    if parsed.scheme == "http":
        issues.append(
            extended_issue(
                module="passive_security",
                check_id="https_usage",
                title="Page uses HTTP rather than HTTPS",
                issue_type="security_http_not_https",
                severity="high",
                source=source,
                observed="The source URL uses http://.",
                expected="Use HTTPS and redirect HTTP to HTTPS.",
                manual="Confirm the canonical production URL and redirect behavior with a normal browser request.",
                evidence_type=HEURISTIC,
            )
        )
    headers = (source_metadata or {}).get("headers") or {}
    lower_headers = {str(k).lower(): str(v) for k, v in headers.items()}
    for header, issue_type, expected in [
        ("strict-transport-security", "security_hsts_missing", "Set Strict-Transport-Security on HTTPS responses."),
        ("content-security-policy", "security_csp_missing", "Set a Content-Security-Policy appropriate to the application."),
        ("referrer-policy", "security_referrer_policy_missing", "Set a Referrer-Policy."),
        ("x-content-type-options", "security_content_type_options_missing", "Set X-Content-Type-Options: nosniff."),
    ]:
        if parsed.scheme == "https" and header not in lower_headers:
            issues.append(
                extended_issue(
                    module="passive_security",
                    check_id="security_header_presence",
                    title=f"Security header may be missing: {header}",
                    issue_type=issue_type,
                    severity="low",
                    source=source,
                    observed=f"{header} was not available in supplied response metadata.",
                    expected=expected,
                    manual="Confirm headers with a standard browser or HTTP client; static local files do not provide response headers.",
                    evidence_type=HEURISTIC,
                )
            )
    for element in parse_elements(html):
        if element["tag"] == "script":
            src = attr(element, "src")
            if src.startswith("http://"):
                issues.append(
                    extended_issue(
                        module="passive_security",
                        check_id="mixed_content",
                        title="External script uses insecure HTTP",
                        issue_type="security_mixed_content_script",
                        severity="high",
                        source=source,
                        selector=selector_for(element),
                        observed=src,
                        expected="Load active subresources over HTTPS.",
                        manual="Confirm the script is requested in production and not a fixture-only URL.",
                        evidence_type=HEURISTIC,
                        snippet=element.get("snippet", ""),
                    )
                )
            if src.startswith("http") and not attr(element, "integrity"):
                issues.append(
                    extended_issue(
                        module="passive_security",
                        check_id="subresource_integrity",
                        title="External script lacks integrity metadata",
                        issue_type="security_external_script_no_sri",
                        severity="low",
                        source=source,
                        selector=selector_for(element),
                        observed=src,
                        expected="Consider integrity metadata for third-party static scripts where feasible.",
                        manual="Verify whether this is a third-party static script and whether SRI fits the deployment model.",
                        evidence_type=HEURISTIC,
                        snippet=element.get("snippet", ""),
                    )
                )
        if element["tag"] == "form":
            action = attr(element, "action")
            if action.startswith("http://"):
                issues.append(
                    extended_issue(
                        module="passive_security",
                        check_id="insecure_form_action",
                        title="Form action uses insecure HTTP",
                        issue_type="security_insecure_form_action",
                        severity="high",
                        source=source,
                        selector=selector_for(element),
                        observed=action,
                        expected="Submit forms only to HTTPS endpoints.",
                        manual="Do not submit the form; confirm action URL in markup and production rendering.",
                        evidence_type=HEURISTIC,
                        snippet=element.get("snippet", ""),
                    )
                )
        if element["tag"] == "input" and attr(element, "type").lower() == "password" and parsed.scheme == "http":
            issues.append(
                extended_issue(
                    module="passive_security",
                    check_id="password_on_http",
                    title="Password field appears on insecure page",
                    issue_type="security_password_on_http",
                    severity="high",
                    source=source,
                    selector=selector_for(element),
                    observed="Password input is present on an HTTP source.",
                    expected="Password fields should be served only over HTTPS.",
                    manual="Confirm in production without entering credentials.",
                    evidence_type=HEURISTIC,
                    snippet=element.get("snippet", ""),
                )
            )
    comments = re.findall(r"<!--(.*?)-->", html, flags=re.S)
    for comment in comments:
        if re.search(r"(api[_-]?key|secret|token|password)\s*[:=]", comment, re.I):
            issues.append(
                extended_issue(
                    module="passive_security",
                    check_id="sensitive_comment_pattern",
                    title="HTML comment contains sensitive-looking key words",
                    issue_type="security_sensitive_comment_pattern",
                    severity="medium",
                    source=source,
                    observed=comment.strip()[:160],
                    expected="Do not expose secrets or sensitive operational notes in public HTML comments.",
                    manual="Manually verify this is not a real secret; do not test or use any value.",
                    evidence_type=HEURISTIC,
                )
            )
    result = module_result(
        "passive_security",
        "passive_security_observations",
        issues,
        limitations=SECURITY_LIMITATIONS,
    ).to_json()
    result["namespace"] = "security"
    result["notice"] = PASSIVE_SECURITY_NOTE
    return issues, result
