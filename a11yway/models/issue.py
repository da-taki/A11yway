"""Issue model for A11yway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AccessibilityIssue:
    """A barrier found by one simulated student agent.

    confidence is one of "confirmed", "likely", "needs_review", or
    "informational". When None, reports fall back to the rule's
    default_confidence from the rule registry.
    """

    title: str
    issue_type: str
    severity: str
    agent_name: str
    evidence: str | dict[str, Any]
    suggested_fix: str
    confidence: str | None = None
