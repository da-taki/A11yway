"""Batch audit runner for local static HTML files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from a11yway.core.browser_runner import (
    is_playwright_available,
    merge_browser_issues,
    run_browser_audit,
)
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.report_builder import (
    build_batch_index_report,
    build_json_report,
    save_batch_index_markdown,
    save_batch_index_csv,
    save_evaluation_summary_markdown,
    save_json_report,
    save_markdown_report,
)
from a11yway.core.source_loader import load_html_source
from a11yway.core.task_executor import run_task_execution
from a11yway.core.task_runner import build_task_blockers, find_task, load_tasks


DEFAULT_TASKS_PATH = Path("examples/sample_tasks.json")


def load_batch_config(path: str | Path) -> list[dict]:
    """Load a batch audit config file."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Batch config must be a list of audit items.")
    return data


def safe_report_id(value: str) -> str:
    """Return a filesystem-safe report id."""
    safe_value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    return safe_value.strip("_") or "report"


def run_batch(
    config_path: str | Path,
    out_dir: str | Path = "reports/batch",
    tasks_path: str | Path = DEFAULT_TASKS_PATH,
    csv_path: str | Path | None = None,
    browser: bool = False,
    max_tabs: int = 40,
    wait_ms: int = 500,
    execute_tasks: bool = False,
) -> dict:
    """Run a static HTML batch audit and write per-page plus index reports.

    When browser is True and Playwright is installed, each page also gets a
    keyboard interaction audit; with execute_tasks, items whose task defines
    browser_steps also get a deterministic keyboard task attempt. A browser
    failure on one page never stops the rest of the batch.
    """
    batch_items = load_batch_config(config_path)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks(tasks_path)
    source_summaries = []

    for item in batch_items:
        item_id = safe_report_id(str(item.get("id", item.get("name", "report"))))
        source = str(item["source"])
        source_result = load_html_source(source)

        if source_result["error"]:
            source_summaries.append(
                {
                    "id": item_id,
                    "name": item.get("name", item_id),
                    "source": source,
                    "source_type": source_result["source_type"],
                    "task": item.get("task", ""),
                    "status": "failed",
                    "error": source_result["error"],
                    "issue_count": 0,
                    "task_blocker_count": 0,
                    "counts_by_severity": {},
                    "counts_by_issue_type": {},
                    "high_severity_issues": [],
                    "analysis_modes": ["static", "browser"] if browser else ["static"],
                    "browser_status": "",
                    "browser_issue_count": 0,
                    "task_execution_status": "",
                    "task_steps_passed": "",
                    "task_steps_total": "",
                    "reports": {},
                }
            )
            continue

        issues = analyze_html_static(source_result["html"])

        browser_result = None
        browser_status = ""
        browser_issue_count = 0
        if browser:
            if not is_playwright_available():
                browser_status = "unavailable"
            else:
                browser_result = run_browser_audit(
                    source, max_tabs=max_tabs, wait_ms=wait_ms
                )
                static_issue_count = len(issues)
                issues = merge_browser_issues(issues, browser_result)
                browser_issue_count = len(issues) - static_issue_count
                browser_status = "passed" if browser_result["success"] else "failed"

        selected_task = None
        task_blockers: list[dict] = []
        task_id_or_name = item.get("task")
        if task_id_or_name:
            selected_task = find_task(tasks, str(task_id_or_name))
            if selected_task:
                task_blockers = build_task_blockers(selected_task, issues)

        task_execution = None
        task_execution_status = ""
        if execute_tasks and browser and selected_task and selected_task.browser_steps:
            if not is_playwright_available():
                task_execution_status = "unavailable"
            else:
                task_execution = run_task_execution(
                    source, selected_task, max_tabs=max_tabs, wait_ms=wait_ms
                )
                if not task_execution["success"]:
                    task_execution_status = "failed"
                elif task_execution["completed"]:
                    task_execution_status = "completed"
                else:
                    task_execution_status = "blocked"
                issues = issues + list(task_execution["issues"])

        report = build_json_report(
            source,
            issues,
            task=selected_task,
            task_blockers=task_blockers,
            source_metadata=source_result,
            browser_result=browser_result,
            task_execution=task_execution,
        )
        json_path = output_dir / f"{item_id}.json"
        markdown_path = output_dir / f"{item_id}.md"
        save_json_report(report, json_path)
        save_markdown_report(report, markdown_path)

        high_severity_issues = [
            {
                "issue_type": issue["issue_type"],
                "message": issue["message"],
                "snippet": issue["evidence"].get("snippet", ""),
            }
            for issue in report["issues"]
            if issue["severity"] == "high"
        ]

        source_summaries.append(
            {
                "id": item_id,
                "name": item.get("name", item_id),
                "source": source,
                "source_type": source_result["source_type"],
                "task": task_id_or_name or "",
                "status": "passed",
                "error": "",
                "issue_count": report["summary"]["issues_found"],
                "task_blocker_count": len(task_blockers),
                "counts_by_severity": report["summary"]["counts_by_severity"],
                "counts_by_issue_type": report["summary"]["counts_by_issue_type"],
                "high_severity_issues": high_severity_issues,
                "analysis_modes": ["static", "browser"] if browser else ["static"],
                "browser_status": browser_status,
                "browser_issue_count": browser_issue_count,
                "task_execution_status": task_execution_status,
                "task_steps_passed": task_execution["steps_passed"] if task_execution else "",
                "task_steps_total": task_execution["steps_total"] if task_execution else "",
                "reports": {
                    "json": json_path.as_posix(),
                    "markdown": markdown_path.as_posix(),
                },
            }
        )

    index_report = build_batch_index_report(source_summaries)
    index_json_path = output_dir / "index.json"
    index_markdown_path = output_dir / "index.md"
    index_csv_path = Path(csv_path) if csv_path else output_dir / "index.csv"
    evaluation_summary_path = output_dir / "evaluation_summary.md"
    index_report["csv_index_path"] = index_csv_path.as_posix()
    index_report["evaluation_summary_path"] = evaluation_summary_path.as_posix()
    save_json_report(index_report, index_json_path)
    save_batch_index_markdown(index_report, index_markdown_path)
    save_batch_index_csv(index_report, index_csv_path)
    save_evaluation_summary_markdown(
        index_report,
        evaluation_summary_path,
        config_path=Path(config_path).as_posix(),
    )

    return {
        "config_path": Path(config_path).as_posix(),
        "out_dir": output_dir.as_posix(),
        "index_json_path": index_json_path.as_posix(),
        "index_markdown_path": index_markdown_path.as_posix(),
        "csv_index_path": index_csv_path.as_posix(),
        "evaluation_summary_path": evaluation_summary_path.as_posix(),
        "index": index_report,
    }
