"""Issue model for A11yway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AccessibilityIssue:
    """A barrier found by one simulated student agent."""

    title: str
    issue_type: str
    severity: str
    agent_name: str
    evidence: str | dict[str, Any]
    suggested_fix: str
