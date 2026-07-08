"""Command-line entry point for the A11yway prototype."""

import argparse
import sys
from pathlib import Path

from a11yway.core.batch_runner import run_batch
from a11yway.core.browser_runner import (
    PLAYWRIGHT_SETUP_MESSAGE,
    is_playwright_available,
    merge_browser_issues,
    run_browser_audit,
)
from a11yway.core.fix_suggester import FixSuggester
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.report_builder import (
    build_json_report,
    save_json_report,
    save_markdown_report,
)
from a11yway.core.rules import get_rule, list_rules
from a11yway.core.source_loader import load_html_source
from a11yway.core.task_runner import build_task_blockers, find_task, load_tasks
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


DEFAULT_HTML_PATH = Path("examples/sample_form.html")
DEFAULT_TASKS_PATH = Path("examples/sample_tasks.json")


def analyze_html_source(source: str) -> tuple[list[AccessibilityIssue], dict]:
    """Load a file or URL source and return static accessibility issues."""
    source_result = load_html_source(source)
    if source_result["error"]:
        return [], source_result

    html = source_result["html"]
    issues = analyze_html_static(html)
    fix_suggester = FixSuggester()

    for issue in issues:
        if not issue.suggested_fix:
            issue.suggested_fix = fix_suggester.suggest_fix(issue.issue_type)

    return issues, source_result


def analyze_html_file(path: Path) -> list[AccessibilityIssue]:
    """Read a local HTML file and return static accessibility issues."""
    issues, _source_result = analyze_html_source(path.as_posix())
    return issues


def print_summary(source: str | Path, issues: list[AccessibilityIssue]) -> None:
    """Print a readable command-line summary."""
    print("A11yway static HTML accessibility audit")
    print(f"Source analyzed: {source}")
    print(f"Issues found: {len(issues)}")

    for index, issue in enumerate(issues, start=1):
        print()
        print(f"{index}. {issue.title}")
        print(f"   Severity: {issue.severity}")
        print(f"   Type: {issue.issue_type}")
        print(f"   Message: {issue.title}")
        print(f"   Evidence: {format_evidence_for_cli(issue.evidence)}")
        if issue.suggested_fix:
            print(f"   Suggested fix: {issue.suggested_fix}")


def format_evidence_for_cli(evidence: str | dict) -> str:
    """Format string or structured evidence for a compact CLI line."""
    if isinstance(evidence, str):
        return evidence

    parts = []
    snippet = evidence.get("snippet")
    line = evidence.get("line")
    reason = evidence.get("reason")

    if snippet:
        parts.append(str(snippet))
    if line:
        parts.append(f"line {line}")
    if reason:
        parts.append(str(reason))

    return " | ".join(parts) if parts else str(evidence)


def print_browser_summary(
    browser_result: dict,
    static_issue_count: int,
    total_issue_count: int,
) -> None:
    """Print a short breakdown of the optional browser audit."""
    print()
    print("Browser interaction audit")
    if not browser_result.get("success"):
        print(f"   Status: failed ({browser_result.get('error')})")
        print("   Static results above are still valid.")
        return

    print("   Status: passed")
    print(f"   Static issues: {static_issue_count}")
    print(f"   Browser issues: {total_issue_count - static_issue_count}")
    print(f"   Total issues: {total_issue_count}")
    print(f"   Focus trace length: {len(browser_result.get('focus_trace', []))}")


def print_task_summary(task: AccessibilityTask, blockers: list[dict]) -> None:
    """Print task context and likely blockers for the static findings."""
    print()
    print(f"Task: {task.name}")
    print(f"Student profile: {task.student_profile}")
    print("Required actions:")
    for action in task.required_actions:
        print(f"   - {action}")

    print(f"Likely blockers: {len(blockers)}")
    for index, blocker in enumerate(blockers, start=1):
        print()
        print(f"{index}. {blocker['message']}")
        print(f"   Severity: {blocker['severity']}")
        print(f"   Type: {blocker['issue_type']}")
        print(f"   Task impact: {blocker['task_impact']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments for the current prototype."""
    parser = argparse.ArgumentParser(
        description="Run A11yway's static HTML accessibility audit.",
    )
    parser.add_argument(
        "html_path",
        nargs="?",
        default=str(DEFAULT_HTML_PATH),
        help="HTML file to analyze. Defaults to examples/sample_form.html.",
    )
    parser.add_argument(
        "--batch",
        dest="batch_config",
        help="Optional batch config JSON file. When provided, single-file analysis is skipped.",
    )
    parser.add_argument(
        "--out-dir",
        dest="out_dir",
        default="reports/batch",
        help="Output directory for batch reports. Defaults to reports/batch.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_output",
        help="Optional CSV index path for batch mode. Defaults to out-dir/index.csv.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        help="Optional path where a structured JSON report should be written.",
    )
    parser.add_argument(
        "--markdown",
        dest="markdown_output",
        help="Optional path where a readable Markdown report should be written.",
    )
    parser.add_argument(
        "--task",
        dest="task_id_or_name",
        help="Optional task id or name from examples/sample_tasks.json.",
    )
    parser.add_argument(
        "--browser",
        dest="browser",
        action="store_true",
        help="Also run the optional keyboard interaction audit (requires Playwright).",
    )
    parser.add_argument(
        "--max-tabs",
        dest="max_tabs",
        type=int,
        default=40,
        help="Maximum Tab presses for the browser focus traversal. Defaults to 40.",
    )
    parser.add_argument(
        "--wait-ms",
        dest="wait_ms",
        type=int,
        default=500,
        help="Milliseconds to wait for JavaScript after page load. Defaults to 500.",
    )
    parser.add_argument(
        "--list-rules",
        dest="list_rules",
        action="store_true",
        help="Print all available static issue types and exit without auditing.",
    )
    parser.add_argument(
        "--rule",
        dest="rule_issue_type",
        help="Print detailed documentation for one issue type and exit.",
    )
    return parser.parse_args(argv)


def print_rule_list() -> None:
    """Print a short listing of every registered static check."""
    rules = list_rules()
    print("A11yway static checks")
    print(f"Rules registered: {len(rules)}")
    for rule in rules:
        print()
        print(f"{rule['issue_type']}")
        print(f"   Title: {rule['title']}")
        print(f"   Category: {rule['category']}")
        print(f"   Default severity: {rule['default_severity']}")


def print_rule_details(issue_type: str) -> int:
    """Print full documentation for one rule; return a CLI exit code."""
    rule = get_rule(issue_type)
    if rule is None:
        print(f'Unknown rule: "{issue_type}".')
        print("Use --list-rules to see all available issue types.")
        return 1

    print(f"Rule: {rule['issue_type']}")
    detail_fields = [
        ("Title", "title"),
        ("Category", "category"),
        ("Default severity", "default_severity"),
        ("Why it matters", "why_it_matters"),
        ("How to fix", "how_to_fix"),
        ("Manual review notes", "manual_review_notes"),
        ("Static check limitations", "static_check_limitations"),
        ("Browser check limitations", "browser_check_limitations"),
        ("Standard hint", "standard_hint"),
    ]
    for label, key in detail_fields:
        if key in rule:
            print(f"{label}: {rule[key]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Analyze a sample or provided HTML file from the command line."""
    args = argv if argv is not None else sys.argv[1:]
    parsed_args = parse_args(args)

    if parsed_args.list_rules:
        print_rule_list()
        return 0

    if parsed_args.rule_issue_type:
        return print_rule_details(parsed_args.rule_issue_type)

    if parsed_args.browser and not is_playwright_available():
        print(PLAYWRIGHT_SETUP_MESSAGE)
        return 1

    if parsed_args.batch_config:
        batch_result = run_batch(
            parsed_args.batch_config,
            parsed_args.out_dir,
            csv_path=parsed_args.csv_output,
            browser=parsed_args.browser,
            max_tabs=parsed_args.max_tabs,
            wait_ms=parsed_args.wait_ms,
        )
        summary = batch_result["index"]["summary"]
        print("A11yway batch static HTML accessibility audit")
        if parsed_args.browser:
            print("Browser mode: enabled")
        print(f"Batch file: {batch_result['config_path']}")
        print(f"Pages tested: {summary['total_pages_tested']}")
        print(f"Total issues: {summary['total_issues']}")
        print(f"Output directory: {batch_result['out_dir']}")
        print(f"Index JSON: {batch_result['index_json_path']}")
        print(f"Index Markdown: {batch_result['index_markdown_path']}")
        print(f"Index CSV: {batch_result['csv_index_path']}")
        print(f"Evaluation summary: {batch_result['evaluation_summary_path']}")
        return 0

    if parsed_args.csv_output:
        print("CSV export is currently only available in batch mode.")

    source = parsed_args.html_path
    issues, source_result = analyze_html_source(source)

    if source_result["error"]:
        print(f"Could not load HTML source: {source_result['error']}", file=sys.stderr)
        return 1

    browser_result = None
    static_issue_count = len(issues)
    if parsed_args.browser:
        browser_result = run_browser_audit(
            source,
            max_tabs=parsed_args.max_tabs,
            wait_ms=parsed_args.wait_ms,
        )
        issues = merge_browser_issues(issues, browser_result)

    print_summary(source, issues)

    if browser_result is not None:
        print_browser_summary(browser_result, static_issue_count, len(issues))

    selected_task = None
    task_blockers: list[dict] = []
    if parsed_args.task_id_or_name:
        tasks = load_tasks(DEFAULT_TASKS_PATH)
        selected_task = find_task(tasks, parsed_args.task_id_or_name)
        if selected_task:
            task_blockers = build_task_blockers(selected_task, issues)
            print_task_summary(selected_task, task_blockers)
        else:
            print()
            print(f'Task not found: "{parsed_args.task_id_or_name}". Normal audit still completed.')

    if parsed_args.json_output or parsed_args.markdown_output:
        report = build_json_report(
            source,
            issues,
            task=selected_task,
            task_blockers=task_blockers,
            source_metadata=source_result,
            browser_result=browser_result,
        )

    if parsed_args.json_output:
        save_json_report(report, parsed_args.json_output)
        print()
        print(f"JSON report saved: {parsed_args.json_output}")

    if parsed_args.markdown_output:
        save_markdown_report(report, parsed_args.markdown_output)
        print()
        print(f"Markdown report saved: {parsed_args.markdown_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
