"""Task loading and agent orchestration pseudocode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from a11yway.agents.base_agent import BaseAccessibilityAgent
from a11yway.core.report_builder import ReportBuilder
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask


TASK_BLOCKER_EXPLANATIONS = {
    "missing_form_label": "Form control may be hard to understand or complete because it has no accessible label.",
    "missing_button_name": "Student may not be able to identify what an unlabeled button does.",
    "missing_link_name": "Student may not be able to identify the purpose or destination of a link.",
    "generic_link_text": "Link text may not clearly explain the destination or action.",
    "missing_image_alt": "Image content may be unavailable to students who need text alternatives.",
    "missing_h1": "Student may not quickly understand the page purpose.",
    "skipped_heading_level": "Student may struggle to understand the page structure and task sections.",
    "multiple_h1": "Multiple main headings may make the page purpose less clear.",
    "missing_page_title": "Student may have trouble identifying the page in a browser tab or assistive technology.",
    "missing_html_lang": "Assistive technology may use the wrong pronunciation rules for the page.",
    "missing_video_captions": "Video content may be inaccessible to students who need captions.",
    "missing_audio_transcript": "Audio content may be inaccessible to students who need a transcript.",
}


def load_tasks(path: str | Path) -> list[AccessibilityTask]:
    """Load task scenario definitions from JSON."""
    task_path = Path(path)
    with task_path.open("r", encoding="utf-8") as file:
        raw_tasks = json.load(file)

    return [AccessibilityTask(**item) for item in raw_tasks]


def find_task(
    tasks: list[AccessibilityTask],
    task_id_or_name: str,
) -> AccessibilityTask | None:
    """Find a task by id or case-insensitive name."""
    requested = task_id_or_name.casefold()
    for task in tasks:
        if task.id.casefold() == requested or task.name.casefold() == requested:
            return task
    return None


def filter_issues_for_task(
    task: AccessibilityTask,
    issues: list,
) -> list:
    """Return issues whose issue types are relevant for a task."""
    relevant_types = set(task.relevant_issue_types)
    return [issue for issue in issues if issue.issue_type in relevant_types]


def build_task_blockers(task: AccessibilityTask, issues: list) -> list[dict]:
    """Build deterministic task blocker notes from relevant static issues.

    TODO: Replace this with real step-by-step browser interaction evidence once
    A11yway grows beyond static HTML analysis.
    """
    blockers = []
    for issue in filter_issues_for_task(task, issues):
        blockers.append(
            {
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "message": issue.title,
                "task_impact": TASK_BLOCKER_EXPLANATIONS.get(
                    issue.issue_type,
                    "This issue may make the task harder to complete.",
                ),
            }
        )
    return blockers


class TaskRunner:
    """Loads tasks, runs selected agents, and builds a report."""

    def __init__(self, agents: Iterable[BaseAccessibilityAgent]) -> None:
        self.agents = list(agents)
        self.report_builder = ReportBuilder()

    def load_tasks(self, path: Path) -> List[AccessibilityTask]:
        """Load task definitions from JSON.

        TODO: Add validation and helpful error messages once the format is stable.
        """
        return load_tasks(path)

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
