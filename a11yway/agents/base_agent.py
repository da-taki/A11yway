"""Base classes for simulated student accessibility agents."""

from __future__ import annotations

from typing import Any, List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class BaseAccessibilityAgent:
    """Base class for a simulated student accessibility agent.

    Each subclass represents a student profile and checks whether that
    student might be blocked while completing an education task.
    """

    name = "Base accessibility agent"
    description = "Generic placeholder agent."

    def run_task(self, task: AccessibilityTask) -> List[AccessibilityIssue]:
        """Run the agent against a task and return findings.

        TODO: Later this method can drive a browser, inspect PDFs, track
        task steps, and collect stronger evidence.
        """
        page_context = self.observe_page(task)
        findings = self.detect_barriers(task, page_context)
        return findings

    def observe_page(self, task: AccessibilityTask) -> dict[str, Any]:
        """Observe the task target and return placeholder page context.

        TODO: Replace this with real page inspection using Playwright,
        Selenium, accessibility trees, PDF parsers, or portal APIs.
        """
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
        """Detect barriers for this agent.

        Subclasses should override this method with profile-specific
        checks. The base class returns no issues.
        """
        return []
