"""Low-vision student agent pseudocode."""

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class LowVisionAgent(BaseAccessibilityAgent):
    """Simulates a student with low vision."""

    name = "Low-vision student"
    description = "Checks contrast, zoom behavior, small text, and layout overflow."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:
        """Return placeholder low-vision findings."""
        findings = []

        # TODO: Check text and control contrast.
        # TODO: Test browser zoom at 200 percent and 400 percent.
        # TODO: Flag small text that is difficult to read.
        # TODO: Detect horizontal scrolling or content overlap after zoom.
        findings.append(
            AccessibilityIssue(
                title="Low-vision checks are not implemented yet",
                issue_type="low_vision_review_needed",
                severity="info",
                agent_name=self.name,
                evidence="Placeholder finding: contrast and zoom behavior still need real analysis.",
                suggested_fix="Add contrast checks, zoom testing, and layout overflow detection.",
            )
        )

        return findings
