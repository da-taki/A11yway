"""Keyboard-only student agent pseudocode."""

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class KeyboardOnlyAgent(BaseAccessibilityAgent):
    """Simulates a student who uses only the keyboard."""

    name = "Keyboard-only student"
    description = "Checks whether an education task can be completed without a mouse."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:
        """Return placeholder keyboard accessibility findings."""
        findings = []

        # TODO: Check focus order by tabbing through all interactive elements.
        # TODO: Detect tab traps where focus cannot escape a component.
        # TODO: Check that focused links, buttons, and fields have visible focus styles.
        # TODO: Attempt keyboard-only form completion for education forms.
        if "form" in task.goal.lower():
            findings.append(
                AccessibilityIssue(
                    title="Keyboard form completion needs verification",
                    issue_type="keyboard_form_completion",
                    severity="medium",
                    agent_name=self.name,
                    evidence="Placeholder finding: form task should be tested without a mouse.",
                    suggested_fix="Ensure every field, button, and error message can be reached and used with the keyboard.",
                )
            )

        return findings
