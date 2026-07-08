"""Batch audit runner for local static HTML files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.report_builder import (
    build_batch_index_report,
    build_json_report,
    save_batch_index_markdown,
    save_json_report,
    save_markdown_report,
)
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
) -> dict:
    """Run a static HTML batch audit and write per-page plus index reports."""
    batch_items = load_batch_config(config_path)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks(tasks_path)
    source_summaries = []

    for item in batch_items:
        item_id = safe_report_id(str(item.get("id", item.get("name", "report"))))
        source_path = Path(str(item["source"]))
        html = source_path.read_text(encoding="utf-8")
        issues = analyze_html_static(html)

        selected_task = None
        task_blockers: list[dict] = []
        task_id_or_name = item.get("task")
        if task_id_or_name:
            selected_task = find_task(tasks, str(task_id_or_name))
            if selected_task:
                task_blockers = build_task_blockers(selected_task, issues)

        report = build_json_report(
            source_path.as_posix(),
            issues,
            task=selected_task,
            task_blockers=task_blockers,
        )
        json_path = output_dir / f"{item_id}.json"
        markdown_path = output_dir / f"{item_id}.md"
        save_json_report(report, json_path)
        save_markdown_report(report, markdown_path)

        source_summaries.append(
            {
                "id": item_id,
                "name": item.get("name", item_id),
                "source": source_path.as_posix(),
                "task": task_id_or_name or "",
                "issue_count": report["summary"]["issues_found"],
                "task_blocker_count": len(task_blockers),
                "counts_by_severity": report["summary"]["counts_by_severity"],
                "counts_by_issue_type": report["summary"]["counts_by_issue_type"],
                "reports": {
                    "json": json_path.as_posix(),
                    "markdown": markdown_path.as_posix(),
                },
            }
        )

    index_report = build_batch_index_report(source_summaries)
    index_json_path = output_dir / "index.json"
    index_markdown_path = output_dir / "index.md"
    save_json_report(index_report, index_json_path)
    save_batch_index_markdown(index_report, index_markdown_path)

    return {
        "config_path": Path(config_path).as_posix(),
        "out_dir": output_dir.as_posix(),
        "index_json_path": index_json_path.as_posix(),
        "index_markdown_path": index_markdown_path.as_posix(),
        "index": index_report,
    }
