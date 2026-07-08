"""Report model for A11yway."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


@dataclass
class AccessibilityReport:
    """Structured report returned after agents run against a task."""

    task: AccessibilityTask
    agents_used: List[str]
    issues: List[AccessibilityIssue] = field(default_factory=list)
    summary: str = ""
