

from __future__ import annotations

from typing import Any, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


class HearingAgent(BaseAccessibilityAgent):


    name = "Hearing-impaired student"
    description = "Checks captions, transcripts, and audio-only instructions."

    def detect_barriers(
        self,
        task: AccessibilityTask,
        page_context: dict[str, Any],
    ) -> List[AccessibilityIssue]:

        findings = []




        if "video" in task.goal.lower() or "lesson" in task.goal.lower():
            findings.append(
                AccessibilityIssue(
                    title="Caption and transcript check needed",
                    issue_type="captions_transcripts",
                    severity="high",
                    agent_name=self.name,
                    evidence="Placeholder finding: media content should be checked for captions and transcripts.",
                    suggested_fix="Provide synchronized captions and a nearby transcript for all instructional media.",
                )
            )

        return findings
