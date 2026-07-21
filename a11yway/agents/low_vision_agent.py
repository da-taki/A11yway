

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class LowVisionAgent(BaseAccessibilityAgent):


    name = "Low-vision student"
    description = "Checks contrast, zoom behavior, small text, and layout overflow."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:

        findings = []





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
