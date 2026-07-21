

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class DyslexiaAgent(BaseAccessibilityAgent):


    name = "Dyslexia/reading-difficulty student"
    description = "Checks whether instructions and errors are clear and readable."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:

        findings = []





        findings.append(
            AccessibilityIssue(
                title="Plain-language review needed",
                issue_type="plain_language_review",
                severity="medium",
                agent_name=self.name,
                evidence="Placeholder finding: instructions should be checked for clarity and reading load.",
                suggested_fix="Use short sentences, clear headings, bullet points, and direct error messages.",
            )
        )

        return findings
