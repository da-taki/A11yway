"""Build structured A11yway reports."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask
from a11yway.core.page_analyzer import STATIC_CHECKS_RUN


def _count_by(items: list[str]) -> dict[str, int]:
    """Count string values while keeping the report builder dependency-free."""
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    """Merge count dictionaries in place."""
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


def _format_evidence_for_json(evidence: str | dict) -> dict:
    """Return evidence as a JSON-ready object."""
    if isinstance(evidence, dict):
        return evidence
    return {"description": evidence}


def build_json_report(
    source_file: str,
    issues: list[AccessibilityIssue],
    task: AccessibilityTask | None = None,
    task_blockers: list[dict] | None = None,
) -> dict:
    """Build the prototype JSON report shape for CLI exports."""
    report = {
        "tool": "A11yway",
        "version": "prototype",
        "source_file": source_file,
        "summary": {
            "issues_found": len(issues),
            "counts_by_severity": _count_by([issue.severity for issue in issues]),
            "counts_by_issue_type": _count_by([issue.issue_type for issue in issues]),
            "agents_used": ["Keyboard-only student"],
            "checks_run": STATIC_CHECKS_RUN,
        },
        "issues": [
            {
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "agent_name": issue.agent_name,
                "message": issue.title,
                "evidence": _format_evidence_for_json(issue.evidence),
                "suggested_fix": issue.suggested_fix,
            }
            for issue in issues
        ],
        "limitations": [
            "This prototype only runs static HTML checks.",
            "It does not replace a full human accessibility audit.",
            "It does not yet perform browser-based interaction testing.",
        ],
    }

    if task:
        report["task"] = {
            "id": task.id,
            "name": task.name,
            "student_profile": task.student_profile,
            "required_actions": task.required_actions,
            "likely_blockers": task_blockers or [],
        }

    return report


def save_json_report(report: dict, output_path: str | Path) -> None:
    """Write a prototype JSON report, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def _format_count_items(counts: dict) -> list[str]:
    """Format report count dictionaries for Markdown output."""
    if not counts:
        return ["- None"]
    return [f"- {key}: {value}" for key, value in counts.items()]


def _format_evidence_lines(evidence: dict) -> list[str]:
    """Format structured evidence for Markdown output."""
    lines = []
    for key in ["tag", "id", "name", "href", "src", "text", "line", "reason"]:
        value = evidence.get(key)
        if value not in [None, ""]:
            lines.append(f"- {key}: {value}")

    snippet = evidence.get("snippet")
    if snippet:
        lines.extend(["", "```html", str(snippet), "```"])

    return lines or ["- No structured evidence available."]


def build_markdown_report(report: dict) -> str:
    """Build a readable Markdown report from a JSON-style report dict."""
    summary = report.get("summary", {})
    lines = [
        "# A11yway Accessibility Report",
        "",
        "## Summary",
        "",
        f"- Source file: {report.get('source_file', '')}",
        f"- Issues found: {summary.get('issues_found', 0)}",
        f"- Agents used: {', '.join(summary.get('agents_used', []))}",
        f"- Checks run: {', '.join(summary.get('checks_run', []))}",
        "",
        "### Counts By Severity",
        "",
        *_format_count_items(summary.get("counts_by_severity", {})),
        "",
        "### Counts By Issue Type",
        "",
        *_format_count_items(summary.get("counts_by_issue_type", {})),
        "",
    ]

    task = report.get("task")
    if task:
        lines.extend(
            [
                "## Task Context",
                "",
                f"- Task name: {task.get('name', '')}",
                f"- Student profile: {task.get('student_profile', '')}",
                "",
                "### Required Actions",
                "",
            ]
        )
        lines.extend(f"- {action}" for action in task.get("required_actions", []))
        lines.extend(["", "### Likely Blockers", ""])
        blockers = task.get("likely_blockers", [])
        if blockers:
            for blocker in blockers:
                lines.extend(
                    [
                        f"- {blocker.get('message', '')}",
                        f"  - Issue type: {blocker.get('issue_type', '')}",
                        f"  - Severity: {blocker.get('severity', '')}",
                        f"  - Task impact: {blocker.get('task_impact', '')}",
                    ]
                )
        else:
            lines.append("- None found for this task.")
        lines.append("")

    lines.extend(["## Issues Found", ""])
    issues = report.get("issues", [])
    if not issues:
        lines.append("No issues found by the current static checks.")
    for index, issue in enumerate(issues, start=1):
        lines.extend(
            [
                f"### {index}. {issue.get('message', '')}",
                "",
                f"- Issue type: {issue.get('issue_type', '')}",
                f"- Severity: {issue.get('severity', '')}",
                f"- Suggested fix: {issue.get('suggested_fix', '')}",
                "",
                "Evidence:",
                "",
            ]
        )
        lines.extend(_format_evidence_lines(issue.get("evidence", {})))
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_markdown_report(report: dict, output_path: str | Path) -> None:
    """Write a Markdown report, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown_report(report), encoding="utf-8")


def build_batch_index_report(items: list[dict]) -> dict:
    """Build a JSON-ready index for a batch audit run."""
    counts_by_severity: dict[str, int] = {}
    counts_by_issue_type: dict[str, int] = {}

    for item in items:
        merge_counts(counts_by_severity, item.get("counts_by_severity", {}))
        merge_counts(counts_by_issue_type, item.get("counts_by_issue_type", {}))

    return {
        "tool": "A11yway",
        "version": "prototype",
        "summary": {
            "total_pages_tested": len(items),
            "total_issues": sum(item.get("issue_count", 0) for item in items),
            "counts_by_severity": counts_by_severity,
            "counts_by_issue_type": counts_by_issue_type,
        },
        "sources": items,
        "limitations": [
            "This prototype only runs static HTML checks.",
            "It does not replace a full human accessibility audit.",
            "It does not yet perform browser-based interaction testing.",
        ],
    }


def build_batch_index_markdown(index_report: dict) -> str:
    """Build a readable Markdown index for a batch audit run."""
    summary = index_report.get("summary", {})
    lines = [
        "# A11yway Batch Accessibility Index",
        "",
        "## Summary",
        "",
        f"- Total pages tested: {summary.get('total_pages_tested', 0)}",
        f"- Total issues: {summary.get('total_issues', 0)}",
        "",
        "### Counts By Severity",
        "",
        *_format_count_items(summary.get("counts_by_severity", {})),
        "",
        "### Counts By Issue Type",
        "",
        *_format_count_items(summary.get("counts_by_issue_type", {})),
        "",
        "## Sources Tested",
        "",
        "| ID | Name | Source | Task | Issues | Task blockers | Reports |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]

    for item in index_report.get("sources", []):
        reports = item.get("reports", {})
        report_links = ", ".join(
            f"{kind}: {path}" for kind, path in reports.items() if path
        )
        lines.append(
            "| {id} | {name} | {source} | {task} | {issues} | {blockers} | {reports} |".format(
                id=item.get("id", ""),
                name=item.get("name", ""),
                source=item.get("source", ""),
                task=item.get("task", ""),
                issues=item.get("issue_count", 0),
                blockers=item.get("task_blocker_count", 0),
                reports=report_links,
            )
        )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in index_report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_batch_index_markdown(index_report: dict, output_path: str | Path) -> None:
    """Write a Markdown batch index, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_batch_index_markdown(index_report), encoding="utf-8")


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
