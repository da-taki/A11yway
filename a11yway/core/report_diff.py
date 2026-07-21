

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from a11yway.core.verdicts import issue_fingerprint


def _source_for(report: dict[str, Any]) -> str:
    source = report.get("source", {}).get("input") or report.get("source_file", "")
    return Path(str(source)).name if source and not str(source).startswith("http") else str(source)


def _issue_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source = _source_for(report)
    mapped = {}
    for issue in report.get("issues", []):
        mapped[issue_fingerprint(issue, source=source)] = issue
    return mapped


def _task_status(report: dict[str, Any]) -> dict[str, Any]:
    execution = report.get("task_execution") or {}
    if not execution:
        return {"status": ""}
    if not execution.get("success"):
        status = "failed"
    elif execution.get("completed"):
        status = "completed"
    else:
        status = "blocked"
    return {
        "status": status,
        "blocked_at_step": execution.get("blocked_at_step"),
        "steps_passed": execution.get("steps_passed", 0),
        "steps_total": execution.get("steps_total", 0),
    }


def compare_reports(old_report: dict[str, Any], new_report: dict[str, Any]) -> dict[str, Any]:

    old_issues = _issue_map(old_report)
    new_issues = _issue_map(new_report)
    old_keys = set(old_issues)
    new_keys = set(new_issues)
    fixed_keys = sorted(old_keys - new_keys)
    remaining_keys = sorted(old_keys & new_keys)
    new_only_keys = sorted(new_keys - old_keys)
    changed_severity = []
    for key in remaining_keys:
        old_severity = old_issues[key].get("severity")
        new_severity = new_issues[key].get("severity")
        if old_severity != new_severity:
            changed_severity.append(
                {
                    "fingerprint": key,
                    "issue_type": old_issues[key].get("issue_type"),
                    "old_severity": old_severity,
                    "new_severity": new_severity,
                }
            )
    old_task = _task_status(old_report)
    new_task = _task_status(new_report)
    task_execution_changed = old_task != new_task
    return {
        "old_source": old_report.get("source_file", ""),
        "new_source": new_report.get("source_file", ""),
        "summary": {
            "old_issue_count": len(old_issues),
            "new_issue_count": len(new_issues),
            "fixed_count": len(fixed_keys),
            "remaining_count": len(remaining_keys),
            "new_count": len(new_only_keys),
            "changed_severity_count": len(changed_severity),
            "net_issue_change": len(new_issues) - len(old_issues),
        },
        "fixed": [_issue_summary(key, old_issues[key]) for key in fixed_keys],
        "remaining": [_issue_summary(key, old_issues[key]) for key in remaining_keys],
        "new": [_issue_summary(key, new_issues[key]) for key in new_only_keys],
        "changed_severity": changed_severity,
        "task_execution_changed": task_execution_changed,
        "task_execution": {
            "old": old_task,
            "new": new_task,
        },
    }


def _issue_summary(fingerprint: str, issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "fingerprint": fingerprint,
        "issue_type": issue.get("issue_type"),
        "severity": issue.get("severity"),
        "message": issue.get("message"),
    }


def build_diff_markdown(diff: dict[str, Any]) -> str:

    summary = diff.get("summary", {})
    lines = [
        "# A11yway Re-Audit Diff",
        "",
        "## Summary",
        "",
        f"- Old issue count: {summary.get('old_issue_count', 0)}",
        f"- New issue count: {summary.get('new_issue_count', 0)}",
        f"- Fixed: {summary.get('fixed_count', 0)}",
        f"- Remaining: {summary.get('remaining_count', 0)}",
        f"- New: {summary.get('new_count', 0)}",
        f"- Net issue change: {summary.get('net_issue_change', 0)}",
        "",
        "## Task Execution Change",
        "",
    ]
    task = diff.get("task_execution", {})
    if diff.get("task_execution_changed"):
        lines.extend(
            [
                f"- Old status: {task.get('old', {}).get('status', '')}",
                f"- New status: {task.get('new', {}).get('status', '')}",
                f"- Old blocked step: {task.get('old', {}).get('blocked_at_step', '')}",
                f"- New blocked step: {task.get('new', {}).get('blocked_at_step', '')}",
            ]
        )
    else:
        lines.append("- No task execution change detected.")
    for section in ["fixed", "remaining", "new"]:
        lines.extend(["", f"## {section.replace('_', ' ').title()} Issues", ""])
        items = diff.get(section, [])
        if not items:
            lines.append("- None")
        for item in items:
            lines.append(
                f"- {item.get('issue_type', '')} ({item.get('severity', '')}): {item.get('message', '')}"
            )
    lines.extend(
        [
            "",
            "Re-audit diffs support impact tracking, but fixes should be verified by re-audit evidence or reviewer confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def save_diff_json(diff: dict[str, Any], path: str | Path) -> None:

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(diff, indent=2), encoding="utf-8")


def save_diff_markdown(diff: dict[str, Any], path: str | Path) -> None:

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_diff_markdown(diff), encoding="utf-8")
