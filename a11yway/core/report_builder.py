"""Build structured A11yway reports."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask


def build_json_report(source_file: str, issues: list[AccessibilityIssue]) -> dict:
    """Build the prototype JSON report shape for CLI exports."""
    return {
        "tool": "A11yway",
        "version": "prototype",
        "source_file": source_file,
        "summary": {
            "issues_found": len(issues),
            "agents_used": ["Keyboard-only student"],
            "checks_run": ["html_form_labels"],
        },
        "issues": [
            {
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "agent_name": issue.agent_name,
                "message": issue.title,
                "evidence": {
                    "description": issue.evidence,
                },
                "suggested_fix": issue.suggested_fix,
            }
            for issue in issues
        ],
        "limitations": [
            "This prototype only checks basic HTML form labels.",
            "It does not replace a full human accessibility audit.",
        ],
    }


def save_json_report(report: dict, output_path: str | Path) -> None:
    """Write a prototype JSON report, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


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
