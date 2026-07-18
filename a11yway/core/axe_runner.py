"""Optional axe-core rule scan for browser mode.

Browser mode already loads pages in headless Chromium, so injecting Deque's
axe-core adds a mature, community-vetted rule set alongside A11yway's own
checks. This module is safe to import when the optional
axe-playwright-python dependency is not installed: everything degrades
gracefully, exactly like browser mode without Playwright. Axe findings are
rule-scan results, not deterministic task evidence, and reports mark them
with their own agent and evidence source.
"""

from __future__ import annotations

from typing import Any

from a11yway.models.issue import AccessibilityIssue

try:
    from axe_playwright_python.sync_playwright import Axe
except ImportError:  # axe-core is optional; browser mode must keep working.
    Axe = None


AXE_SETUP_MESSAGE = (
    "The axe-core scan requires the optional axe-playwright-python package.\n"
    "Install it with:\n"
    "\n"
    "  pip install -r requirements-browser.txt\n"
    "\n"
    "Static audits and browser mode keep working without it."
)

AXE_CHECK_NAME = "axe_core_scan"

AXE_AGENT_NAME = "Axe Core Scanner"

# axe-core reports critical/serious/moderate/minor impacts; A11yway reports
# high/medium/low severities. Violations with no impact stay medium so they
# are reviewed rather than buried.
AXE_IMPACT_TO_SEVERITY = {
    "critical": "high",
    "serious": "high",
    "moderate": "medium",
    "minor": "low",
}

# Cap per-rule findings so one repeated template bug cannot flood a report.
MAX_NODES_PER_VIOLATION = 10

REVIEW_ONLY_AXE_RULES = {
    "tabindex": {
        "severity": "medium",
        "confidence": "needs_review",
        "reason_suffix": (
            " A positive tabindex value is review evidence only here; "
            "A11yway does not treat it as a strong finding unless observed "
            "keyboard traversal proves a harmful focus-order mismatch."
        ),
    }
}


def is_axe_available() -> bool:
    """Return whether the optional axe-core dependency can be used."""
    return Axe is not None


def axe_impact_to_severity(impact: str | None) -> str:
    """Map an axe-core impact level onto an A11yway severity."""
    return AXE_IMPACT_TO_SEVERITY.get((impact or "").strip().lower(), "medium")


def _shorten(value: str, max_length: int = 200) -> str:
    """Keep evidence snippets compact."""
    normalized = " ".join(str(value or "").split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def axe_violations_to_issues(violations: list[dict]) -> list[AccessibilityIssue]:
    """Convert raw axe-core violations into A11yway issues.

    Each affected element becomes one issue so evidence stays reviewable,
    capped at MAX_NODES_PER_VIOLATION elements per rule.
    """
    issues: list[AccessibilityIssue] = []

    for violation in violations or []:
        rule_id = str(violation.get("id", "") or "unknown_rule")
        impact = str(violation.get("impact", "") or "")
        severity = axe_impact_to_severity(impact)
        review_only = REVIEW_ONLY_AXE_RULES.get(rule_id)
        if review_only:
            severity = review_only["severity"]
        help_text = str(violation.get("help", "") or "")
        help_url = str(violation.get("helpUrl", "") or "")
        description = str(violation.get("description", "") or "")
        nodes = violation.get("nodes") or []

        suggested_fix = help_text or description
        if help_url:
            suggested_fix = f"{suggested_fix} See {help_url}".strip()

        for node in nodes[:MAX_NODES_PER_VIOLATION]:
            evidence: dict[str, Any] = {
                "detected_in": "axe_core",
                "axe_rule": rule_id,
                "axe_impact": impact,
                "snippet": _shorten(node.get("html", "")),
                "target": ", ".join(str(item) for item in node.get("target", [])),
                "reason": _shorten(
                    node.get("failureSummary", "") or description, 400
                ),
                "nodes_total": len(nodes),
            }
            confidence = None
            if review_only:
                confidence = review_only["confidence"]
                evidence["review_only_reason"] = review_only["reason_suffix"].strip()
                evidence["reason"] = _shorten(
                    f"{evidence['reason']}{review_only['reason_suffix']}", 500
                )
            if help_url:
                evidence["help_url"] = help_url

            issues.append(
                AccessibilityIssue(
                    title=f"axe-core: {help_text or rule_id}",
                    issue_type=f"axe_{rule_id.replace('-', '_')}",
                    severity=severity,
                    agent_name=AXE_AGENT_NAME,
                    evidence=evidence,
                    suggested_fix=suggested_fix,
                    confidence=confidence,
                )
            )

    return issues


def summarize_axe_violations(violations: list[dict]) -> list[dict[str, Any]]:
    """Build a compact JSON-safe per-rule summary for reports."""
    return [
        {
            "rule": str(violation.get("id", "") or "unknown_rule"),
            "impact": str(violation.get("impact", "") or ""),
            "severity": axe_impact_to_severity(violation.get("impact")),
            "help": str(violation.get("help", "") or ""),
            "help_url": str(violation.get("helpUrl", "") or ""),
            "node_count": len(violation.get("nodes") or []),
        }
        for violation in violations or []
    ]


def run_axe_scan(page) -> dict[str, Any]:
    """Run axe-core against an already-loaded Playwright page.

    Always returns a result dict; on any failure success is False and the
    error field explains what happened, so the browser audit keeps going.
    """
    result: dict[str, Any] = {
        "success": False,
        "error": None,
        "axe_version": "",
        "violation_rule_count": 0,
        "issue_count": 0,
        "violations": [],
        "issues": [],
    }

    if not is_axe_available():
        result["error"] = "axe-playwright-python is not installed."
        return result

    try:
        response = Axe().run(page).response
    except Exception as error:  # noqa: BLE001 - a scan failure must not break the audit
        message = str(error).strip()
        result["error"] = (
            message.splitlines()[0][:300] if message else "Unknown axe-core error"
        )
        return result

    violations = response.get("violations", []) or []
    result["success"] = True
    result["axe_version"] = str(response.get("testEngine", {}).get("version", ""))
    result["violation_rule_count"] = len(violations)
    result["violations"] = summarize_axe_violations(violations)
    result["issues"] = axe_violations_to_issues(violations)
    result["issue_count"] = len(result["issues"])
    return result
