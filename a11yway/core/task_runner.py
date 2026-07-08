"""Task loading and agent orchestration pseudocode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.core.report_builder import ReportBuilder
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask


class TaskRunner:
    """Loads tasks, runs selected agents, and builds a report."""

    def __init__(self, agents: Iterable[BaseAccessibilityAgent]) -> None:
        self.agents = list(agents)
        self.report_builder = ReportBuilder()

    def load_tasks(self, path: Path) -> List[AccessibilityTask]:
        """Load task definitions from JSON.

        TODO: Add validation and helpful error messages once the format is stable.
        """
        with path.open("r", encoding="utf-8") as file:
            raw_tasks = json.load(file)

        return [AccessibilityTask(**item) for item in raw_tasks]

    def run_task(self, task: AccessibilityTask) -> AccessibilityReport:
        """Run every configured agent against one task."""
        all_findings = []

        for agent in self.agents:
            findings = agent.run_task(task)
            all_findings.extend(findings)

        return self.report_builder.build_report(
            task=task,
            agents_used=[agent.name for agent in self.agents],
            issues=all_findings,
        )
