

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class AccessibilityTask:


    id: str = ""
    name: str = ""
    description: str = ""
    student_profile: str = ""
    required_actions: List[str] = field(default_factory=list)
    relevant_issue_types: List[str] = field(default_factory=list)
    title: str = ""
    url: str = ""
    goal: str = ""
    steps: List[str] = field(default_factory=list)



    browser_steps: List[dict] = field(default_factory=list)

    def __post_init__(self) -> None:

        if not self.name:
            self.name = self.title
        if not self.title:
            self.title = self.name
        if not self.description:
            self.description = self.goal
        if not self.goal:
            self.goal = self.description
        if not self.required_actions:
            self.required_actions = list(self.steps)
        if not self.steps:
            self.steps = list(self.required_actions)
