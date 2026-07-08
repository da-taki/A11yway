"""Dyslexia and reading-difficulty student agent pseudocode."""

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class DyslexiaAgent(BaseAccessibilityAgent):
    """Simulates a student with dyslexia or reading difficulty."""

    name = "Dyslexia/reading-difficulty student"
    description = "Checks whether instructions and errors are clear and readable."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:
        """Return placeholder reading accessibility findings."""
        findings = []

        # TODO: Detect dense instructions with long paragraphs.
        # TODO: Check whether error messages explain how to fix the problem.
        # TODO: Flag confusing labels, jargon, or unclear next steps.
        # TODO: Check whether a plain-language version is available.
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
