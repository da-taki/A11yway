"""Build structured A11yway reports."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from a11yway.models.issue import AccessibilityIssue
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask
from a11yway.core.page_analyzer import STATIC_CHECKS_RUN
from a11yway.core.rules import enrich_issue_with_rule


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


BROWSER_MODE_LIMITATIONS = [
    "Browser mode approximates keyboard interaction but does not simulate a full screen reader.",
    "Accessible names are estimated and require manual review.",
]

TASK_EXECUTION_LIMITATIONS = [
    "Task steps are deterministic scripts; a human may find a workaround the script does not try.",
    "Step results show keyboard operability, not full assistive technology behavior.",
]


def build_json_report(
    source_file: str,
    issues: list[AccessibilityIssue],
    task: AccessibilityTask | None = None,
    task_blockers: list[dict] | None = None,
    source_metadata: dict | None = None,
    browser_result: dict | None = None,
    task_execution: dict | None = None,
) -> dict:
    """Build the prototype JSON report shape for CLI exports."""
    checks_run = list(STATIC_CHECKS_RUN)
    limitations = [
        "This prototype only runs static HTML checks.",
        "It does not replace a full human accessibility audit.",
        "It does not yet perform browser-based interaction testing.",
    ]
    if browser_result is not None:
        checks_run.extend(browser_result.get("checks_run", []))
        limitations = [
            "This prototype runs static HTML checks plus a basic keyboard interaction audit.",
            "It does not replace a full human accessibility audit.",
            "Browser mode does not simulate a full screen reader, and accessible names are estimated.",
        ]

    report = {
        "tool": "A11yway",
        "version": "prototype",
        "source_file": source_file,
        "summary": {
            "issues_found": len(issues),
            "counts_by_severity": _count_by([issue.severity for issue in issues]),
            "counts_by_issue_type": _count_by([issue.issue_type for issue in issues]),
            "agents_used": ["Keyboard-only student"],
            "checks_run": checks_run,
        },
        "issues": [
            enrich_issue_with_rule(
                {
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "agent_name": issue.agent_name,
                    "message": issue.title,
                    "evidence": _format_evidence_for_json(issue.evidence),
                    "suggested_fix": issue.suggested_fix,
                }
            )
            for issue in issues
        ],
        "limitations": limitations,
    }

    if task:
        report["task"] = {
            "id": task.id,
            "name": task.name,
            "student_profile": task.student_profile,
            "required_actions": task.required_actions,
            "likely_blockers": task_blockers or [],
        }

    if source_metadata:
        report["source"] = {
            "input": source_metadata.get("source"),
            "type": source_metadata.get("source_type"),
            "final_url": source_metadata.get("final_url"),
            "status_code": source_metadata.get("status_code"),
            "content_type": source_metadata.get("content_type"),
        }

    if browser_result is not None:
        report["analysis_modes"] = ["static", "browser"]
        report["browser"] = {
            "success": browser_result.get("success", False),
            "error": browser_result.get("error"),
            "final_url": browser_result.get("final_url"),
            "checks_run": browser_result.get("checks_run", []),
            "focus_trace": browser_result.get("focus_trace", []),
            "limitations": list(BROWSER_MODE_LIMITATIONS),
        }

    if task_execution is not None:
        report["task_execution"] = {
            "task_id": task_execution.get("task_id"),
            "task_name": task_execution.get("task_name"),
            "student_profile": task_execution.get("student_profile"),
            "success": task_execution.get("success", False),
            "error": task_execution.get("error"),
            "completed": task_execution.get("completed", False),
            "blocked_at_step": task_execution.get("blocked_at_step"),
            "steps_total": task_execution.get("steps_total", 0),
            "steps_passed": task_execution.get("steps_passed", 0),
            "steps": task_execution.get("steps", []),
            "limitations": list(TASK_EXECUTION_LIMITATIONS),
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
    for key in ["tag", "id", "name", "href", "src", "text", "line", "step", "detected_in", "reason"]:
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
    source = report.get("source", {})
    source_label = source.get("input") or report.get("source_file", "")
    lines = [
        "# A11yway Accessibility Report",
        "",
        "## Summary",
        "",
        f"- Source: {source_label}",
        f"- Source type: {source.get('type', 'file')}",
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
    if source.get("final_url") or source.get("status_code"):
        lines.extend(
            [
                "### Source Metadata",
                "",
                f"- Final URL: {source.get('final_url') or ''}",
                f"- Status code: {source.get('status_code') or ''}",
                f"- Content type: {source.get('content_type') or ''}",
                "",
            ]
        )

    browser = report.get("browser")
    if browser is not None:
        trace = browser.get("focus_trace", [])
        lines.extend(
            [
                "## Browser Mode Summary",
                "",
                f"- Analysis modes: {', '.join(report.get('analysis_modes', []))}",
                f"- Browser audit success: {str(browser.get('success', False)).lower()}",
            ]
        )
        if browser.get("error"):
            lines.append(f"- Error: {browser['error']}")
        lines.extend(
            [
                f"- Checks run: {', '.join(browser.get('checks_run', []))}",
                f"- Focus trace length: {len(trace)}",
                "",
            ]
        )
        if trace:
            lines.extend(
                [
                    "## Browser Interaction Trace",
                    "",
                    "| Step | Tag | Accessible name guess | ID/Name | Text/Href |",
                    "| ---: | --- | --- | --- | --- |",
                ]
            )
            for entry in trace[:20]:
                lines.append(
                    "| {step} | {tag} | {name_guess} | {id_name} | {text_href} |".format(
                        step=entry.get("step", ""),
                        tag=entry.get("tag", ""),
                        name_guess=entry.get("accessible_name_guess", ""),
                        id_name=entry.get("id") or entry.get("name") or "",
                        text_href=entry.get("text") or entry.get("href") or "",
                    )
                )
            if len(trace) > 20:
                lines.extend(
                    ["", f"Trace truncated: showing the first 20 of {len(trace)} steps."]
                )
            lines.append("")
        if browser.get("limitations"):
            lines.extend(["### Browser Limitations", ""])
            lines.extend(f"- {limitation}" for limitation in browser["limitations"])
            lines.append("")

    execution = report.get("task_execution")
    if execution is not None:
        lines.extend(["## Task Execution", ""])
        if not execution.get("success"):
            lines.extend(
                [
                    f"- Task: {execution.get('task_name', '')}",
                    f"- Result: could not run ({execution.get('error', '')})",
                    "",
                ]
            )
        else:
            if execution.get("completed"):
                verdict = "COMPLETED with keyboard-only interaction"
            else:
                verdict = f"BLOCKED at step `{execution.get('blocked_at_step', '')}`"
            lines.extend(
                [
                    f"- Task: {execution.get('task_name', '')}",
                    f"- Student profile: {execution.get('student_profile', '')}",
                    f"- Result: {verdict}",
                    f"- Steps passed: {execution.get('steps_passed', 0)} of {execution.get('steps_total', 0)}",
                    "",
                    "| Step | Action | Status | Detail |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for step in execution.get("steps", []):
                status = step.get("status", "")
                if step.get("used_fallback"):
                    status += " (fallback)"
                lines.append(
                    "| {id} | {action} | {status} | {detail} |".format(
                        id=step.get("id", ""),
                        action=step.get("action", ""),
                        status=status,
                        detail=step.get("detail", ""),
                    )
                )
            lines.append("")
        if execution.get("limitations"):
            lines.extend(["### Task Execution Limitations", ""])
            lines.extend(f"- {limitation}" for limitation in execution["limitations"])
            lines.append("")

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
        rule = issue.get("rule", {})
        lines.extend(
            [
                f"### {index}. {issue.get('message', '')}",
                "",
                f"- Issue type: {issue.get('issue_type', '')}",
            ]
        )
        if rule.get("title"):
            lines.append(f"- Rule: {rule['title']}")
        if rule.get("category"):
            lines.append(f"- Category: {rule['category']}")
        lines.append(f"- Severity: {issue.get('severity', '')}")
        if rule.get("why_it_matters"):
            lines.append(f"- Why it matters: {rule['why_it_matters']}")
        lines.append(f"- Suggested fix: {issue.get('suggested_fix', '')}")
        if rule.get("manual_review_notes"):
            lines.append(f"- Manual review: {rule['manual_review_notes']}")
        if rule.get("static_check_limitations"):
            lines.append(f"- Static check limitation: {rule['static_check_limitations']}")
        if rule.get("browser_check_limitations"):
            lines.append(f"- Browser check limitation: {rule['browser_check_limitations']}")
        lines.extend(["", "Evidence:", ""])
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

    successful_pages = sum(1 for item in items if item.get("status") == "passed")
    analysis_modes = ["static"]
    if any("browser" in item.get("analysis_modes", []) for item in items):
        analysis_modes = ["static", "browser"]
    executed = [item for item in items if item.get("task_execution_status")]

    return {
        "tool": "A11yway",
        "version": "prototype",
        "summary": {
            "analysis_modes": analysis_modes,
            "total_pages_tested": len(items),
            "successful_pages": successful_pages,
            "failed_pages": len(items) - successful_pages,
            "total_issues": sum(item.get("issue_count", 0) for item in items),
            "total_task_blockers": sum(
                item.get("task_blocker_count", 0) for item in items
            ),
            "tasks_executed": len(executed),
            "tasks_completed": sum(
                1 for item in executed if item.get("task_execution_status") == "completed"
            ),
            "tasks_blocked": sum(
                1 for item in executed if item.get("task_execution_status") == "blocked"
            ),
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
        f"- CSV index: {index_report.get('csv_index_path', '')}",
        f"- Evaluation summary: {index_report.get('evaluation_summary_path', '')}",
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
        "| ID | Name | Source | Task | Status | Issues | Task blockers | Reports | Error |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]

    for item in index_report.get("sources", []):
        reports = item.get("reports", {})
        report_links = ", ".join(
            f"{kind}: {path}" for kind, path in reports.items() if path
        )
        lines.append(
            "| {id} | {name} | {source} | {task} | {status} | {issues} | {blockers} | {reports} | {error} |".format(
                id=item.get("id", ""),
                name=item.get("name", ""),
                source=item.get("source", ""),
                task=item.get("task", ""),
                status=item.get("status", "passed"),
                issues=item.get("issue_count", 0),
                blockers=item.get("task_blocker_count", 0),
                reports=report_links,
                error=item.get("error", ""),
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


def save_batch_index_csv(index_report: dict, output_path: str | Path) -> None:
    """Write a spreadsheet-friendly CSV index for a batch audit."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "name",
        "source",
        "source_type",
        "task",
        "status",
        "issues_found",
        "task_blockers",
        "browser_status",
        "browser_issue_count",
        "task_execution_status",
        "task_steps_passed",
        "task_steps_total",
        "high_count",
        "medium_count",
        "low_count",
        "issue_types",
        "json_report",
        "markdown_report",
        "error",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in index_report.get("sources", []):
            severity_counts = item.get("counts_by_severity", {})
            issue_type_counts = item.get("counts_by_issue_type", {})
            reports = item.get("reports", {})
            writer.writerow(
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "source": item.get("source", ""),
                    "source_type": item.get("source_type", ""),
                    "task": item.get("task", ""),
                    "status": item.get("status", ""),
                    "issues_found": item.get("issue_count", 0),
                    "task_blockers": item.get("task_blocker_count", 0),
                    "browser_status": item.get("browser_status", ""),
                    "browser_issue_count": item.get("browser_issue_count", 0),
                    "task_execution_status": item.get("task_execution_status", ""),
                    "task_steps_passed": item.get("task_steps_passed", ""),
                    "task_steps_total": item.get("task_steps_total", ""),
                    "high_count": severity_counts.get("high", 0),
                    "medium_count": severity_counts.get("medium", 0),
                    "low_count": severity_counts.get("low", 0),
                    "issue_types": ";".join(issue_type_counts.keys()),
                    "json_report": reports.get("json", ""),
                    "markdown_report": reports.get("markdown", ""),
                    "error": item.get("error", ""),
                }
            )


def _sorted_issue_type_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    """Return issue type counts sorted by count (highest first), then name."""
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))


def build_evaluation_summary_markdown(index_report: dict, config_path: str = "") -> str:
    """Build a reviewer-friendly Markdown summary for a whole batch run."""
    summary = index_report.get("summary", {})
    sources = index_report.get("sources", [])
    severity_counts = summary.get("counts_by_severity", {})

    lines = [
        "# A11yway Batch Evaluation Summary",
        "",
        "## Overview",
        "",
        f"- Batch config used: {config_path or 'not recorded'}",
        f"- Pages tested: {summary.get('total_pages_tested', 0)}",
        f"- Successful pages: {summary.get('successful_pages', 0)}",
        f"- Failed pages: {summary.get('failed_pages', 0)}",
        f"- Total issues: {summary.get('total_issues', 0)}",
        f"- Total task blockers: {summary.get('total_task_blockers', 0)}",
        "",
        "## Top Issue Types",
        "",
    ]

    issue_type_counts = _sorted_issue_type_counts(summary.get("counts_by_issue_type", {}))
    if issue_type_counts:
        lines.extend(f"- {issue_type}: {count}" for issue_type, count in issue_type_counts)
    else:
        lines.append("- None found by the current static checks.")

    lines.extend(
        [
            "",
            "## Severity Breakdown",
            "",
            f"- High: {severity_counts.get('high', 0)}",
            f"- Medium: {severity_counts.get('medium', 0)}",
            f"- Low: {severity_counts.get('low', 0)}",
            "",
            "## Sources With Most Issues",
            "",
            "| Name | Source | Task | Issues | Blockers | Report |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )

    ranked_sources = sorted(
        sources, key=lambda item: item.get("issue_count", 0), reverse=True
    )
    for item in ranked_sources:
        lines.append(
            "| {name} | {source} | {task} | {issues} | {blockers} | {report} |".format(
                name=item.get("name", ""),
                source=item.get("source", ""),
                task=item.get("task", ""),
                issues=item.get("issue_count", 0),
                blockers=item.get("task_blocker_count", 0),
                report=item.get("reports", {}).get("markdown", ""),
            )
        )

    executed_items = [item for item in sources if item.get("task_execution_status")]
    if executed_items:
        lines.extend(
            [
                "",
                "## Task Execution Results",
                "",
                "Deterministic keyboard-only task attempts per page:",
                "",
                "| Name | Task | Result | Steps passed |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in executed_items:
            lines.append(
                "| {name} | {task} | {result} | {passed} of {total} |".format(
                    name=item.get("name", ""),
                    task=item.get("task", ""),
                    result=item.get("task_execution_status", ""),
                    passed=item.get("task_steps_passed", 0),
                    total=item.get("task_steps_total", 0),
                )
            )

    lines.extend(["", "## High Priority Findings", ""])
    found_high_priority = False
    for item in sources:
        high_issues = item.get("high_severity_issues", [])
        if not high_issues:
            continue
        found_high_priority = True
        lines.extend([f"### {item.get('name', item.get('id', ''))}", ""])
        for issue in high_issues:
            lines.append(f"- {issue.get('issue_type', '')}: {issue.get('message', '')}")
            if issue.get("snippet"):
                lines.append(f"  - Evidence: `{issue['snippet']}`")
        report_path = item.get("reports", {}).get("markdown", "")
        if report_path:
            lines.append(f"- Full report: {report_path}")
        lines.append("")
    if not found_high_priority:
        lines.extend(["No high severity issues were found by the current static checks.", ""])

    lines.extend(
        [
            "## Recommended Review Process",
            "",
            "1. Review high severity issues first.",
            "2. Confirm evidence snippets against the actual page.",
            "3. Mark false positives.",
            "4. Note barriers the static checks missed.",
            "5. Decide which fixes are feasible for the organization.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {limitation}" for limitation in index_report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_evaluation_summary_markdown(
    index_report: dict,
    output_path: str | Path,
    config_path: str = "",
) -> None:
    """Write the batch evaluation summary, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_evaluation_summary_markdown(index_report, config_path=config_path),
        encoding="utf-8",
    )


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
