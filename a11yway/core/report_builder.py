"""Build structured A11yway reports."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask


class ReportBuilder:
    """Converts agent findings into report objects and export formats."""

    def build_report(
        self,
        task: AccessibilityTask,
        agents_used: List[str],
        issues: List[AccessibilityIssue],
    ) -> AccessibilityReport:
        """Create an accessibility report object."""
        return AccessibilityReport(
            task=task,
            agents_used=agents_used,
            issues=issues,
            summary=f"Found {len(issues)} placeholder issue(s) for task: {task.title}.",
        )

    def export_json(self, report: AccessibilityReport, path: Path) -> None:
        """Export a report as JSON.

        TODO: Decide final report schema before using this in production.
        """
        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(report), file, indent=2)

    def export_markdown(self, report: AccessibilityReport, path: Path) -> None:
        """Export a simple Markdown report.

        TODO: Replace this with a better report template later.
        """
        lines = [
            f"# A11yway Report: {report.task.title}",
            "",
            f"Task goal: {report.task.goal}",
            f"URL: {report.task.url}",
            "",
            "## Summary",
            report.summary,
            "",
            "## Issues",
        ]

        for issue in report.issues:
            lines.extend(
                [
                    f"### {issue.title}",
                    f"- Severity: {issue.severity}",
                    f"- Agent: {issue.agent_name}",
                    f"- Evidence: {issue.evidence}",
                    f"- Suggested fix: {issue.suggested_fix}",
                    "",
                ]
            )

        path.write_text("\n".join(lines), encoding="utf-8")
