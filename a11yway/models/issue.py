

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AccessibilityIssue:







    title: str
    issue_type: str
    severity: str
    agent_name: str
    evidence: str | dict[str, Any]
    suggested_fix: str
    confidence: str | None = None
