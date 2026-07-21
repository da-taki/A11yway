

from __future__ import annotations

from typing import Any, List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class BaseAccessibilityAgent:






    name = "Base accessibility agent"
    description = "Generic placeholder agent."

    def run_task(self, task: AccessibilityTask) -> List[AccessibilityIssue]:





        page_context = self.observe_page(task)
        findings = self.detect_barriers(task, page_context)
        return findings

    def observe_page(self, task: AccessibilityTask) -> dict[str, Any]:





        return {
            "task_url": task.url,
            "task_goal": task.goal,
            "notes": "Placeholder page observation only.",
        }

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:





        return []
