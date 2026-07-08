"""Task model for A11yway."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class AccessibilityTask:
    """A real education task that a student needs to complete."""

    title: str
    url: str
    goal: str
    steps: List[str] = field(default_factory=list)
