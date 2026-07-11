"""Shared helpers for extended accessibility modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from a11yway.models.issue import AccessibilityIssue


EXTENDED_RESULT_SCHEMA_VERSION = "1.0"
RESULT_STATUSES = {
    "completed",
    "blocked",
    "failed",
    "unavailable",
    "unsupported",
    "scaffolded",
}
SEVERITIES = {"high", "medium", "low"}
CONFIDENCE_VALUES = {"confirmed", "likely", "needs_review", "informational"}
REVIEW_STATUSES = {"confirmed", "likely", "needs_review", "informational"}
EVIDENCE_TYPES = {"deterministic", "heuristic"}
DETERMINISTIC = "deterministic"
HEURISTIC = "heuristic"


def current_timestamp() -> str:
    """Return a report timestamp in an explicit, timezone-safe format."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_safe(value: Any) -> Any:
    """Normalize values so extended module output is JSON-stable."""
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): json_safe(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _normalized_choice(value: str | None, allowed: set[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else fallback


def validate_extended_result(data: dict[str, Any]) -> list[str]:
    """Return schema problems for an extended module result."""
    problems = []
    for key in ("schema_version", "created_at", "module", "check_id", "status"):
        if not data.get(key):
            problems.append(f"missing_{key}")
    if data.get("schema_version") != EXTENDED_RESULT_SCHEMA_VERSION:
        problems.append("unsupported_schema_version")
    if data.get("status") not in RESULT_STATUSES:
        problems.append("invalid_status")
    if not isinstance(data.get("findings", []), list):
        problems.append("invalid_findings")
    if not isinstance(data.get("artifacts", {}), dict):
        problems.append("invalid_artifacts")
    if not isinstance(data.get("limitations", []), list):
        problems.append("invalid_limitations")
    return problems


@dataclass
class ExtendedCheckResult:
    """Report-ready metadata for non-core A11yway modules."""

    module: str
    check_id: str
    status: str = "completed"
    findings: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    capability: dict[str, Any] | None = None
    schema_version: str = EXTENDED_RESULT_SCHEMA_VERSION
    created_at: str = field(default_factory=current_timestamp)

    def to_json(self) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "module": self.module,
            "check_id": self.check_id,
            "status": _normalized_choice(self.status, RESULT_STATUSES, "failed"),
            "findings": json_safe(self.findings),
            "artifacts": json_safe(self.artifacts),
            "limitations": json_safe(self.limitations),
        }
        if self.capability:
            result["capability"] = json_safe(self.capability)
        problems = validate_extended_result(result)
        if problems:
            result["schema_errors"] = problems
        return result


def extended_issue(
    *,
    module: str,
    check_id: str,
    title: str,
    issue_type: str,
    severity: str,
    source: str,
    selector: str = "",
    observed: str = "",
    expected: str = "",
    manual: str = "",
    evidence_type: str = HEURISTIC,
    detection_source: str = "",
    confidence: str | None = None,
    review_status: str | None = None,
    context: dict[str, Any] | None = None,
    snippet: str = "",
    wcag: list[dict[str, str]] | None = None,
    limitations: list[str] | None = None,
) -> AccessibilityIssue:
    """Create a consistent issue for extended module findings."""
    evidence_type = _normalized_choice(evidence_type, EVIDENCE_TYPES, HEURISTIC)
    severity = _normalized_choice(severity, SEVERITIES, "low")
    effective_confidence = confidence or (
        "needs_review" if evidence_type == HEURISTIC else "likely"
    )
    effective_confidence = _normalized_choice(
        effective_confidence,
        CONFIDENCE_VALUES,
        "needs_review",
    )
    effective_review_status = _normalized_choice(
        review_status,
        REVIEW_STATUSES,
        effective_confidence,
    )
    evidence = {
        "module": module,
        "check_id": check_id,
        "evidence_type": evidence_type,
        "deterministic": evidence_type == DETERMINISTIC,
        "review_status": effective_review_status,
        "source": source,
        "selector": selector,
        "observed": observed,
        "expected": expected,
        "manual_verification": manual,
        "detection_source": detection_source or module,
        "evidence_sources": [detection_source or module],
        "limitations": json_safe(limitations or []),
    }
    if context:
        evidence["context"] = json_safe(context)
    if snippet:
        evidence["snippet"] = snippet
    if wcag:
        evidence["wcag_relation"] = json_safe(wcag)
    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name=f"A11yway {module}",
        evidence=evidence,
        suggested_fix=expected or "Review the evidence and update the experience to expose accessible semantics.",
        confidence=effective_confidence,
    )


def module_result(
    module: str,
    check_id: str,
    issues: list[AccessibilityIssue],
    *,
    status: str = "completed",
    limitations: list[str] | None = None,
    artifacts: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
) -> ExtendedCheckResult:
    """Build report metadata from module issues."""
    return ExtendedCheckResult(
        module=module,
        check_id=check_id,
        status=status,
        findings=sorted(
            [
                {
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "confidence": issue.confidence,
                    "evidence": issue.evidence,
                }
                for issue in issues
            ],
            key=lambda item: (
                str(item.get("issue_type", "")),
                str(item.get("severity", "")),
                str(item.get("evidence", {}).get("selector", "")),
                str(item.get("evidence", {}).get("observed", "")),
            ),
        ),
        artifacts=artifacts or {},
        limitations=limitations or [],
        capability=capability,
    )
