

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class KeyboardOnlyAgent(BaseAccessibilityAgent):


    name = "Keyboard-only student"
    description = "Checks whether an education task can be completed without a mouse."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:





        findings = []

        html = page_context.get("html")
        if isinstance(html, str):
            findings.extend(analyze_html_static(html))





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
