"""Command-line entry point for the A11yway prototype."""

import argparse
import json
import sys
from pathlib import Path

from a11yway.core.batch_runner import run_batch
from a11yway.core.ai_scout import run_ai_scout, save_ai_scout_outputs
from a11yway.core.axe_runner import AXE_SETUP_MESSAGE, is_axe_available
from a11yway.core.capabilities import detect_capabilities, format_capabilities_cli
from a11yway.core.browser_runner import (
    PLAYWRIGHT_SETUP_MESSAGE,
    is_playwright_available,
    merge_browser_issues,
    run_browser_audit,
)
from a11yway.core.ci_output import (
    EXIT_TOOL_ERROR,
    compute_ci_exit_code,
    save_junit_xml,
    save_sarif_report,
)
from a11yway.core.low_vision_audit import run_low_vision_audit_for_source
from a11yway.core.cognitive_audit import analyze_cognitive
from a11yway.core.component_audit import analyze_components
from a11yway.core.document_audit import analyze_document
from a11yway.core.forms_audit import analyze_forms
from a11yway.core.language_audit import analyze_language
from a11yway.core.media_audit import MEDIA_EXTENSIONS, analyze_media, analyze_media_file
from a11yway.core.mobile_audit import run_mobile_audit
from a11yway.core.passive_security_audit import analyze_passive_security
from a11yway.core.screen_reader_audit import run_screen_reader_audit
from a11yway.core.fix_suggester import FixSuggester
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.report_diff import (
    build_diff_markdown,
    compare_reports,
    save_diff_json,
    save_diff_markdown,
)
from a11yway.core.report_builder import (
    build_json_report,
    save_html_report,
    save_json_report,
    save_markdown_report,
)
from a11yway.core.verdicts import (
    apply_verdicts_to_report,
    load_verdicts,
    save_verdict_summary_markdown,
    summarize_verdicts,
)
from a11yway.core.dedup import deduplicate_issues
from a11yway.core.rules import (
    DEFAULT_CONFIDENCE_BY_RULE,
    FALLBACK_CONFIDENCE,
    get_rule,
    list_rules,
)
from a11yway.core.source_loader import load_html_source
from a11yway.core.wcag_coverage import (
    build_coverage_markdown,
    format_coverage_cli,
    wcag_mappings_for_issue_type,
)
from a11yway.core.task_executor import run_task_execution
from a11yway.core.task_runner import build_task_blockers, find_task, load_tasks
from a11yway.core.workflow_audit import run_workflow_audit
from a11yway.core.workflow_packs import (
    list_workflow_packs,
    load_workflow_pack,
    suggest_workflows_from_pack,
)
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
        confidence = issue.confidence or DEFAULT_CONFIDENCE_BY_RULE.get(
            issue.issue_type, FALLBACK_CONFIDENCE
        )
        print()
        print(f"{index}. {issue.title}")
        print(f"   Severity: {issue.severity}")
        print(f"   Type: {issue.issue_type}")
        print(f"   Confidence: {confidence}")
        wcag = wcag_mappings_for_issue_type(issue.issue_type)
        if wcag:
            print(
                "   Related WCAG 2.2: "
                + "; ".join(
                    f"SC {item['sc']} {item['name']} ({item['coverage']})"
                    for item in wcag
                )
            )
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

    axe = browser_result.get("axe")
    if axe is not None:
        print()
        print("Axe-core scan")
        if not axe.get("success"):
            print(f"   Status: failed ({axe.get('error')})")
            return
        print("   Status: passed")
        print(f"   Rules violated: {axe.get('violation_rule_count', 0)}")
        print(f"   Axe findings: {axe.get('issue_count', 0)}")


def print_low_vision_summary(low_vision_result: dict, total_issue_count: int) -> None:
    """Print a short breakdown of low-vision browser checks."""
    print()
    print("Low-vision checks")
    if not low_vision_result.get("success"):
        print(f"   Status: failed ({low_vision_result.get('error')})")
        return
    print("   Status: passed")
    print(f"   Low-vision issues: {len(low_vision_result.get('issues', []))}")
    print(f"   Contrast samples: {len(low_vision_result.get('contrast_samples', []))}")
    print(f"   Total issues: {total_issue_count}")


def print_task_execution_summary(task_execution: dict) -> None:
    """Print the outcome of a deterministic keyboard task attempt."""
    print()
    print(f"Task execution: {task_execution.get('task_name', '')}")
    if not task_execution.get("success"):
        print(f"   Result: could not run ({task_execution.get('error')})")
        return

    if task_execution.get("completed"):
        print("   Result: COMPLETED with keyboard-only interaction")
    else:
        verdict = f"   Result: BLOCKED at step {task_execution.get('blocked_at_step')}"
        if task_execution.get("blocked_reason"):
            verdict += f" (reason: {task_execution['blocked_reason']})"
        print(verdict)
    print(
        f"   Steps passed: {task_execution.get('steps_passed', 0)} "
        f"of {task_execution.get('steps_total', 0)}"
    )
    print(f"   Task execution issues: {len(task_execution.get('issues', []))}")
    for step in task_execution.get("steps", []):
        marker = {"passed": "+", "failed": "x", "skipped": "-"}.get(step.get("status"), "?")
        fallback_note = " (fallback)" if step.get("used_fallback") else ""
        print(f"   [{marker}] {step.get('id', '')}: {step.get('status', '')}{fallback_note}")


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
        "--html",
        dest="html_output",
        help="Optional path where a self-contained HTML report should be written.",
    )
    parser.add_argument(
        "--visual-proof",
        dest="visual_proof_dir",
        help="Optional directory for browser screenshot and focus overlay artifacts. Requires --browser.",
    )
    parser.add_argument(
        "--video",
        dest="video",
        action="store_true",
        help=(
            "Record the task execution browser session as a video saved "
            "alongside the visual proof assets. Requires --browser, "
            "--execute-task, and --visual-proof."
        ),
    )
    parser.add_argument(
        "--html-reports",
        dest="html_reports",
        action="store_true",
        help="In batch mode, write per-page HTML reports and browser visual proof when available.",
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
        "--low-vision",
        dest="low_vision",
        action="store_true",
        help="Run optional browser-based low-vision checks. Requires --browser.",
    )
    parser.add_argument(
        "--axe",
        dest="axe",
        action="store_true",
        help="Also run the axe-core rule scan on the rendered page. Requires --browser.",
    )
    parser.add_argument(
        "--ai-scout",
        dest="ai_scout",
        action="store_true",
        help="Run optional Groq-backed AI Scout in suggest-only mode and write sidecar reports.",
    )
    parser.add_argument(
        "--execute-task",
        dest="execute_task",
        metavar="TASK",
        help="Attempt a task's browser steps with keyboard-only interaction. Requires --browser.",
    )
    parser.add_argument(
        "--execute-tasks",
        dest="execute_tasks",
        action="store_true",
        help="In batch mode, execute browser steps for items whose task defines them. Requires --browser.",
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
        "--wcag-coverage",
        dest="wcag_coverage",
        action="store_true",
        help=(
            "Print the WCAG 2.2 coverage map (direct/partial/supporting/"
            "axe-only/manual-only counts per Success Criterion) and exit. "
            "Coverage is not a conformance claim."
        ),
    )
    parser.add_argument(
        "--wcag-coverage-markdown",
        dest="wcag_coverage_markdown",
        metavar="PATH",
        help="Write the full WCAG 2.2 coverage matrix as Markdown and exit.",
    )
    parser.add_argument(
        "--review-only-rules",
        dest="review_only_rules",
        metavar="RULES",
        help=(
            "Comma-separated issue types whose findings are downgraded to "
            "needs_review confidence in this run's reports (for rules with "
            "poor reviewer precision). The rules still run and report."
        ),
    )
    parser.add_argument(
        "--rule",
        dest="rule_issue_type",
        help="Print detailed documentation for one issue type and exit.",
    )
    parser.add_argument(
        "--list-packs",
        dest="list_packs",
        action="store_true",
        help="Print available deterministic workflow packs and exit.",
    )
    parser.add_argument(
        "--show-pack",
        dest="show_pack",
        metavar="PACK_ID",
        help="Print details for one deterministic workflow pack and exit.",
    )
    parser.add_argument(
        "--suggest-tasks",
        dest="suggest_tasks",
        metavar="PACK_ID",
        help="Print workflow templates from a pack and exit.",
    )
    parser.add_argument(
        "--apply-verdicts",
        dest="apply_verdicts",
        metavar="VERDICTS_JSON",
        help="Apply reviewer verdicts to an A11yway JSON report.",
    )
    parser.add_argument(
        "--to",
        dest="verdict_report_json",
        metavar="REPORT_JSON",
        help="Input report JSON for --apply-verdicts.",
    )
    parser.add_argument(
        "--out",
        dest="verdict_output_json",
        metavar="OUTPUT_JSON",
        help="Output report JSON for --apply-verdicts.",
    )
    parser.add_argument(
        "--summarize-verdicts",
        dest="summarize_verdicts",
        metavar="VERDICTS_JSON",
        help="Write a Markdown summary for reviewer verdicts.",
    )
    parser.add_argument(
        "--compare-reports",
        dest="compare_reports",
        nargs=2,
        metavar=("OLD_REPORT", "NEW_REPORT"),
        help="Compare two A11yway JSON reports for re-audit tracking.",
    )
    parser.add_argument(
        "--ci",
        dest="ci",
        action="store_true",
        help=(
            "CI mode: exit 0 when clean, 1 for findings at or above "
            "--fail-severity, 2 for a blocked task (with --fail-on-blocked), "
            "3 for tool or setup errors."
        ),
    )
    parser.add_argument(
        "--fail-severity",
        dest="fail_severity",
        choices=["high", "medium", "low"],
        default="high",
        help="Lowest severity that fails a --ci run. Defaults to high.",
    )
    parser.add_argument(
        "--fail-on-blocked",
        dest="fail_on_blocked",
        action="store_true",
        help=(
            "In --ci mode, exit 2 when a task execution is blocked. Without "
            "this flag a blocked task still fails through its high-severity "
            "findings, but with exit code 1."
        ),
    )
    parser.add_argument(
        "--sarif",
        dest="sarif_output",
        metavar="PATH",
        help="Write findings as SARIF 2.1.0 so they render inline on GitHub.",
    )
    parser.add_argument(
        "--junit",
        dest="junit_output",
        metavar="PATH",
        help="Write task execution steps as JUnit XML test cases.",
    )
    parser.add_argument(
        "--capabilities",
        dest="capabilities",
        action="store_true",
        help="Print optional tool and adapter capability detection, then exit.",
    )
    parser.add_argument(
        "--screen-reader",
        dest="screen_reader",
        action="store_true",
        help="Add screen-reader evidence. Chromium engine uses the browser accessibility tree.",
    )
    parser.add_argument(
        "--screen-reader-engine",
        dest="screen_reader_engine",
        default="chromium",
        choices=["chromium", "nvda", "jaws", "voiceover", "talkback"],
        help="Screen-reader evidence engine. Native engines run only when a safe adapter is available.",
    )
    parser.add_argument(
        "--announce-transcript",
        dest="announce_transcript",
        action="store_true",
        help="Include ordered accessibility-tree announcement transcript where available.",
    )
    parser.add_argument(
        "--mobile",
        dest="mobile",
        action="store_true",
        help="Run Playwright mobile device-emulation checks. This is not real mobile AT testing.",
    )
    parser.add_argument(
        "--device",
        dest="device",
        default="android-small",
        choices=["android-small", "android-large", "iphone-small", "iphone-large", "tablet"],
        help="Mobile device profile for --mobile.",
    )
    parser.add_argument(
        "--orientation",
        dest="orientations",
        action="append",
        choices=["portrait", "landscape"],
        help="Mobile orientation to test. Can be passed more than once.",
    )
    parser.add_argument(
        "--document",
        dest="document",
        action="store_true",
        help="Inspect a local PDF, DOCX, or PPTX file instead of HTML.",
    )
    parser.add_argument(
        "--media",
        dest="media",
        action="store_true",
        help="Run HTML media accessibility evidence checks.",
    )
    parser.add_argument(
        "--workflow",
        dest="workflow",
        action="store_true",
        help="Run a safe structured workflow from --workflow-config.",
    )
    parser.add_argument(
        "--workflow-config",
        dest="workflow_config",
        help="JSON workflow config for --workflow.",
    )
    parser.add_argument(
        "--safe-public-mode",
        dest="safe_public_mode",
        action="store_true",
        default=True,
        help="Block submitting or private workflow actions. Enabled by default for public-site workflows.",
    )
    parser.add_argument(
        "--forms",
        dest="forms",
        action="store_true",
        help="Run safe forms and error-recovery evidence checks.",
    )
    parser.add_argument(
        "--cognitive",
        dest="cognitive",
        action="store_true",
        help="Run cognitive-accessibility heuristic review checks.",
    )
    parser.add_argument(
        "--language-audit",
        dest="language_audit",
        action="store_true",
        help="Run multilingual and bidirectional-language checks.",
    )
    parser.add_argument(
        "--components",
        dest="components",
        action="store_true",
        help="Run complex component pattern checks.",
    )
    parser.add_argument(
        "--passive-security",
        dest="passive_security",
        action="store_true",
        help="Run opt-in passive security observations. This is not penetration testing.",
    )
    parser.add_argument(
        "--all-accessibility-modules",
        dest="all_accessibility_modules",
        action="store_true",
        help="Enable screen-reader, mobile, forms, cognitive, language, media, and components modules. Does not enable passive security.",
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
        ("Default confidence", "default_confidence"),
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
    wcag = wcag_mappings_for_issue_type(issue_type)
    if wcag:
        print("Related WCAG 2.2 Success Criteria (not a conformance claim):")
        for item in wcag:
            print(
                f"   SC {item['sc']} {item['name']} (Level {item['level']}) - "
                f"coverage: {item['coverage']}, detection: {item['detection_mode']}, "
                f"confidence: {item['confidence']}"
            )
            print(f"      Limitations: {item['limitations']}")
            print(f"      Manual check: {item['manual_check']}")
    return 0


def print_workflow_pack_list() -> None:
    """Print a compact listing of deterministic workflow packs."""
    packs = list_workflow_packs()
    print("A11yway workflow packs")
    print(f"Packs available: {len(packs)}")
    for pack in packs:
        workflows = pack.get("workflows", [])
        print()
        print(f"{pack.get('pack_id', '')}")
        print(f"   Name: {pack.get('name', '')}")
        print(f"   Workflows: {len(workflows)}")
        print(f"   Description: {pack.get('description', '')}")


def print_workflow_pack_details(pack_id: str) -> int:
    """Print responsible-use notes and workflow details for one pack."""
    pack = load_workflow_pack(pack_id)
    if pack is None:
        print(f'Unknown workflow pack: "{pack_id}".')
        print("Use --list-packs to see available workflow packs.")
        return 1

    print(f"Workflow pack: {pack.get('name', pack_id)}")
    print(f"Pack id: {pack.get('pack_id', pack_id)}")
    print(f"Description: {pack.get('description', '')}")

    responsible_use = pack.get("responsible_use", [])
    if responsible_use:
        print()
        print("Responsible use:")
        for note in responsible_use:
            print(f"   - {note}")

    print()
    print("Workflows:")
    for workflow in pack.get("workflows", []):
        print()
        print(f"{workflow.get('id', '')}: {workflow.get('name', '')}")
        print(f"   Description: {workflow.get('description', '')}")
        print("   Required actions:")
        for action in workflow.get("required_actions", []):
            print(f"      - {action}")
    return 0


def print_workflow_suggestions(pack_id: str, source: str | None = None) -> int:
    """Print workflow templates that can guide deterministic task planning."""
    pack = load_workflow_pack(pack_id)
    if pack is None:
        print(f'Unknown workflow pack: "{pack_id}".')
        print("Use --list-packs to see available workflow packs.")
        return 1

    workflows = suggest_workflows_from_pack(pack_id)
    print(f"Workflow task templates: {pack.get('name', pack_id)}")
    print("These are deterministic templates, not AI-generated tasks.")
    print("Add page-specific browser_steps before deterministic task execution.")
    if source:
        print(f"Source provided: {source}")
        print("The source can be audited separately with static, browser, or task mode.")

    for workflow in workflows:
        print()
        print(f"{workflow.get('id', '')}: {workflow.get('name', '')}")
        print(f"   Description: {workflow.get('description', '')}")
        print("   Required actions:")
        for action in workflow.get("required_actions", []):
            print(f"      - {action}")
        print("   Relevant issue types:")
        for issue_type in workflow.get("relevant_issue_types", []):
            print(f"      - {issue_type}")
        risks = workflow.get("accessibility_risks", [])
        if risks:
            print("   Accessibility risks to review:")
            for risk in risks:
                print(f"      - {risk}")
    return 0


def apply_verdicts_cli(verdicts_path: str | None, report_path: str | None, output_path: str | None) -> int:
    """Apply reviewer verdicts from the CLI."""
    if not verdicts_path or not report_path or not output_path:
        print("--apply-verdicts requires --to REPORT_JSON and --out OUTPUT_JSON.")
        return 1
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    verdicts = load_verdicts(verdicts_path)
    reviewed = apply_verdicts_to_report(report, verdicts)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reviewed, indent=2), encoding="utf-8")
    summary = reviewed.get("review_summary", {})
    print(f"Reviewed report saved: {output_path}")
    print(f"Confirmed: {summary.get('confirmed', 0)}")
    print(f"False positives: {summary.get('false_positive', 0)}")
    print(f"Missed issues: {summary.get('missed_issue_count', 0)}")
    precision = reviewed.get("precision_stats", {})
    overall = precision.get("overall", {})
    if overall.get("precision") is not None:
        print(f"Overall precision: {overall['precision']}")
    by_rule = precision.get("by_rule", {})
    if by_rule:
        print("Precision by rule:")
        for rule_name in sorted(by_rule):
            bucket = by_rule[rule_name]
            precision_text = (
                bucket["precision"] if bucket.get("precision") is not None else "n/a"
            )
            print(
                f"   {rule_name}: precision={precision_text} "
                f"(confirmed={bucket.get('confirmed', 0)}, "
                f"false_positive={bucket.get('false_positive', 0)}, "
                f"needs_review={bucket.get('needs_review', 0)}, "
                f"fixed={bucket.get('fixed', 0)})"
            )
    return 0


def summarize_verdicts_cli(verdicts_path: str | None, markdown_path: str | None) -> int:
    """Summarize reviewer verdicts from the CLI."""
    if not verdicts_path or not markdown_path:
        print("--summarize-verdicts requires --markdown OUTPUT_MD.")
        return 1
    verdicts = load_verdicts(verdicts_path)
    summary = summarize_verdicts(verdicts)
    save_verdict_summary_markdown(summary, markdown_path)
    counts = summary.get("counts", {})
    print(f"Verdict summary saved: {markdown_path}")
    print(f"Confirmed: {counts.get('confirmed', 0)}")
    print(f"False positives: {counts.get('false_positive', 0)}")
    print(f"Missed issues: {counts.get('missed_issue', 0)}")
    return 0


def compare_reports_cli(report_paths: list[str] | None, markdown_path: str | None, json_path: str | None) -> int:
    """Compare reports from the CLI."""
    if not report_paths:
        print("--compare-reports requires OLD_REPORT and NEW_REPORT.")
        return 1
    old_report = json.loads(Path(report_paths[0]).read_text(encoding="utf-8"))
    new_report = json.loads(Path(report_paths[1]).read_text(encoding="utf-8"))
    diff = compare_reports(old_report, new_report)
    if json_path:
        save_diff_json(diff, json_path)
        print(f"Diff JSON saved: {json_path}")
    if markdown_path:
        save_diff_markdown(diff, markdown_path)
        print(f"Diff Markdown saved: {markdown_path}")
    if not json_path and not markdown_path:
        print(build_diff_markdown(diff))
    summary = diff.get("summary", {})
    print(f"Fixed: {summary.get('fixed_count', 0)}")
    print(f"Remaining: {summary.get('remaining_count', 0)}")
    print(f"New: {summary.get('new_count', 0)}")
    return 0


def load_batch_item_reports(items: list[dict]) -> list[dict]:
    """Load the per-item JSON reports a batch run wrote to disk."""
    reports = []
    for item in items:
        json_path = (item.get("reports") or {}).get("json")
        if json_path and Path(json_path).exists():
            reports.append(json.loads(Path(json_path).read_text(encoding="utf-8")))
    return reports


def _apply_all_accessibility_modules(parsed_args: argparse.Namespace) -> None:
    """Expand --all-accessibility-modules without enabling passive security."""
    if not parsed_args.all_accessibility_modules:
        return
    parsed_args.screen_reader = True
    parsed_args.mobile = True
    parsed_args.forms = True
    parsed_args.cognitive = True
    parsed_args.language_audit = True
    parsed_args.media = True
    parsed_args.components = True


def _extended_module_flags(parsed_args: argparse.Namespace) -> bool:
    return any(
        [
            parsed_args.screen_reader,
            parsed_args.mobile,
            parsed_args.document,
            parsed_args.media,
            parsed_args.workflow,
            parsed_args.forms,
            parsed_args.cognitive,
            parsed_args.language_audit,
            parsed_args.components,
            parsed_args.passive_security,
        ]
    )


def run_html_extended_modules(
    source: str,
    html: str,
    parsed_args: argparse.Namespace,
    *,
    browser_result: dict | None = None,
    source_result: dict | None = None,
) -> tuple[list[AccessibilityIssue], list[dict]]:
    """Run selected extended modules for one HTML source."""
    issues: list[AccessibilityIssue] = []
    results: list[dict] = []
    if parsed_args.screen_reader:
        module_issues, result = run_screen_reader_audit(
            source,
            browser_result,
            engine=parsed_args.screen_reader_engine,
            include_transcript=parsed_args.announce_transcript,
        )
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.mobile:
        module_issues, result = run_mobile_audit(
            source,
            device=parsed_args.device,
            orientations=parsed_args.orientations or ["portrait"],
            wait_ms=parsed_args.wait_ms,
        )
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.forms:
        module_issues, result = analyze_forms(html, source, permit_submission=False)
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.media:
        module_issues, result = analyze_media(html, source)
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.cognitive:
        module_issues, result = analyze_cognitive(html, source)
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.language_audit:
        module_issues, result = analyze_language(html, source)
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.components:
        module_issues, result = analyze_components(html, source)
        issues.extend(module_issues)
        results.append(result)
    if parsed_args.passive_security:
        module_issues, result = analyze_passive_security(
            html,
            source,
            source_metadata=source_result,
        )
        issues.extend(module_issues)
        results.append(result)
    return issues, results


def _make_console_safe() -> None:
    """Keep console output from crashing on limited encodings.

    Windows consoles often use legacy code pages that cannot show Indic
    or other non-Latin scripts. Report files are always written as UTF-8;
    this only makes the console summary replace unprintable characters
    instead of raising UnicodeEncodeError.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    """Analyze a sample or provided HTML file from the command line."""
    _make_console_safe()
    args = argv if argv is not None else sys.argv[1:]
    parsed_args = parse_args(args)
    _apply_all_accessibility_modules(parsed_args)
    if parsed_args.announce_transcript:
        parsed_args.screen_reader = True
    if parsed_args.screen_reader and parsed_args.screen_reader_engine == "chromium":
        parsed_args.browser = True

    # In CI mode, setup problems must be distinguishable from findings.
    setup_exit = EXIT_TOOL_ERROR if parsed_args.ci else 1

    if parsed_args.capabilities:
        capabilities = detect_capabilities(verify_browsers=True)
        print(format_capabilities_cli(capabilities))
        if parsed_args.json_output:
            output = Path(parsed_args.json_output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(capabilities, indent=2), encoding="utf-8")
            print(f"Capabilities JSON saved: {parsed_args.json_output}")
        return 0

    if parsed_args.list_rules:
        print_rule_list()
        return 0

    if parsed_args.wcag_coverage:
        print(format_coverage_cli())
        return 0

    if parsed_args.wcag_coverage_markdown:
        output = Path(parsed_args.wcag_coverage_markdown)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_coverage_markdown(), encoding="utf-8")
        print(f"WCAG 2.2 coverage matrix saved: {output}")
        return 0

    if parsed_args.rule_issue_type:
        return print_rule_details(parsed_args.rule_issue_type)

    if parsed_args.apply_verdicts:
        return apply_verdicts_cli(
            parsed_args.apply_verdicts,
            parsed_args.verdict_report_json,
            parsed_args.verdict_output_json,
        )

    if parsed_args.summarize_verdicts:
        return summarize_verdicts_cli(
            parsed_args.summarize_verdicts,
            parsed_args.markdown_output,
        )

    if parsed_args.compare_reports:
        return compare_reports_cli(
            parsed_args.compare_reports,
            parsed_args.markdown_output,
            parsed_args.json_output,
        )

    if parsed_args.list_packs:
        print_workflow_pack_list()
        return 0

    if parsed_args.show_pack:
        return print_workflow_pack_details(parsed_args.show_pack)

    if parsed_args.suggest_tasks:
        source = parsed_args.html_path if parsed_args.html_path != str(DEFAULT_HTML_PATH) else None
        return print_workflow_suggestions(parsed_args.suggest_tasks, source=source)

    if parsed_args.visual_proof_dir and not parsed_args.browser:
        print("Visual proof requires browser mode. Add --browser to the command.")
        return setup_exit

    if parsed_args.low_vision and not parsed_args.browser:
        print("Low-vision checks require browser mode. Add --browser to the command.")
        return setup_exit

    if (parsed_args.execute_task or parsed_args.execute_tasks) and not parsed_args.browser:
        print("Task execution requires browser mode. Add --browser to the command.")
        return setup_exit

    if parsed_args.axe and not parsed_args.browser:
        print("The axe-core scan requires browser mode. Add --browser to the command.")
        return setup_exit

    if parsed_args.video and not (
        parsed_args.browser and parsed_args.execute_task and parsed_args.visual_proof_dir
    ):
        print(
            "Video proof requires --browser, --execute-task, and --visual-proof "
            "together."
        )
        return setup_exit

    if parsed_args.browser and not is_playwright_available():
        print(PLAYWRIGHT_SETUP_MESSAGE)
        return setup_exit

    if parsed_args.axe and not is_axe_available():
        print(AXE_SETUP_MESSAGE)
        return setup_exit

    if parsed_args.workflow and not parsed_args.workflow_config:
        print("--workflow requires --workflow-config.")
        return setup_exit

    if parsed_args.document:
        issues, document_result = analyze_document(parsed_args.html_path)
        print_summary(parsed_args.html_path, issues)
        print()
        print(f"Document module status: {document_result.get('status')}")
        print(f"Document findings: {len(issues)}")
        report = build_json_report(
            parsed_args.html_path,
            deduplicate_issues(issues),
            source_metadata={
                "source": parsed_args.html_path,
                "source_type": "document",
                "final_url": None,
                "status_code": None,
                "content_type": Path(parsed_args.html_path).suffix.lower(),
            },
            extended_results=[document_result],
        )
        if parsed_args.json_output:
            save_json_report(report, parsed_args.json_output)
            print(f"JSON report saved: {parsed_args.json_output}")
        if parsed_args.markdown_output:
            save_markdown_report(report, parsed_args.markdown_output)
            print(f"Markdown report saved: {parsed_args.markdown_output}")
        if parsed_args.html_output or parsed_args.html_reports:
            output = parsed_args.html_output or "reports/document_audit.html"
            save_html_report(report, output)
            print(f"HTML report saved: {output}")
        if parsed_args.sarif_output:
            save_sarif_report([report], parsed_args.sarif_output)
            print(f"SARIF report saved: {parsed_args.sarif_output}")
        if parsed_args.junit_output:
            save_junit_xml([report], parsed_args.junit_output)
            print(f"JUnit XML saved: {parsed_args.junit_output}")
        return 0

    if parsed_args.workflow:
        issues, workflow_result = run_workflow_audit(
            parsed_args.workflow_config,
            safe_public_mode=parsed_args.safe_public_mode,
            wait_ms=parsed_args.wait_ms,
        )
        print_summary(parsed_args.workflow_config, issues)
        print()
        print(f"Workflow status: {workflow_result.get('status')}")
        print(f"Workflow findings: {len(issues)}")
        workflow_source = workflow_result.get("artifacts", {}).get("name", "") or parsed_args.workflow_config
        report = build_json_report(
            workflow_source,
            deduplicate_issues(issues),
            source_metadata={
                "source": parsed_args.workflow_config,
                "source_type": "workflow",
                "final_url": None,
                "status_code": None,
                "content_type": "application/json",
            },
            extended_results=[workflow_result],
        )
        if parsed_args.json_output:
            save_json_report(report, parsed_args.json_output)
            print(f"JSON report saved: {parsed_args.json_output}")
        if parsed_args.markdown_output:
            save_markdown_report(report, parsed_args.markdown_output)
            print(f"Markdown report saved: {parsed_args.markdown_output}")
        if parsed_args.html_output or parsed_args.html_reports:
            output = parsed_args.html_output or "reports/workflow_audit.html"
            save_html_report(report, output)
            print(f"HTML report saved: {output}")
        if parsed_args.sarif_output:
            save_sarif_report([report], parsed_args.sarif_output)
            print(f"SARIF report saved: {parsed_args.sarif_output}")
        if parsed_args.junit_output:
            save_junit_xml([report], parsed_args.junit_output)
            print(f"JUnit XML saved: {parsed_args.junit_output}")
        return 0

    if parsed_args.batch_config:
        batch_result = run_batch(
            parsed_args.batch_config,
            parsed_args.out_dir,
            csv_path=parsed_args.csv_output,
            browser=parsed_args.browser,
            max_tabs=parsed_args.max_tabs,
            wait_ms=parsed_args.wait_ms,
            execute_tasks=parsed_args.execute_tasks,
            html_reports=parsed_args.html_reports,
            low_vision=parsed_args.low_vision,
            ai_scout=parsed_args.ai_scout,
            axe=parsed_args.axe,
        )
        summary = batch_result["index"]["summary"]
        print("A11yway batch static HTML accessibility audit")
        if parsed_args.browser:
            print("Browser mode: enabled")
        if parsed_args.low_vision:
            print("Low-vision checks: enabled")
        if parsed_args.axe:
            print("Axe-core scan: enabled")
        print(f"Batch file: {batch_result['config_path']}")
        print(f"Pages tested: {summary['total_pages_tested']}")
        print(f"Total issues: {summary['total_issues']}")
        print(f"Output directory: {batch_result['out_dir']}")
        print(f"Index JSON: {batch_result['index_json_path']}")
        print(f"Index Markdown: {batch_result['index_markdown_path']}")
        print(f"Index CSV: {batch_result['csv_index_path']}")
        print(f"Evaluation summary: {batch_result['evaluation_summary_path']}")
        if parsed_args.html_reports:
            print("HTML reports: enabled")
        if parsed_args.execute_tasks:
            print(f"Tasks executed: {summary.get('tasks_executed', 0)}")
            print(f"Tasks completed: {summary.get('tasks_completed', 0)}")
            print(f"Tasks blocked: {summary.get('tasks_blocked', 0)}")
        if parsed_args.ai_scout:
            print(f"AI Scout runs: {summary.get('ai_scout_runs', 0)}")
            print(f"AI Scout successful runs: {summary.get('ai_scout_ok', 0)}")

        if parsed_args.sarif_output or parsed_args.junit_output or parsed_args.ci:
            items = batch_result["index"]["sources"]
            item_reports = load_batch_item_reports(items)
            if parsed_args.sarif_output:
                save_sarif_report(item_reports, parsed_args.sarif_output)
                print(f"SARIF report saved: {parsed_args.sarif_output}")
            if parsed_args.junit_output:
                save_junit_xml(item_reports, parsed_args.junit_output)
                print(f"JUnit XML saved: {parsed_args.junit_output}")
            if parsed_args.ci:
                tool_error = any(
                    item.get("status") == "failed"
                    or item.get("browser_status") in {"failed", "unavailable"}
                    or item.get("task_execution_status") in {"failed", "unavailable"}
                    for item in items
                )
                exit_code = compute_ci_exit_code(
                    item_reports,
                    fail_severity=parsed_args.fail_severity,
                    fail_on_blocked=parsed_args.fail_on_blocked,
                    tool_error=tool_error,
                )
                print(f"CI mode exit code: {exit_code}")
                return exit_code
        return 0

    if parsed_args.csv_output:
        print("CSV export is currently only available in batch mode.")

    execute_task_obj = None
    if parsed_args.execute_task:
        tasks = load_tasks(DEFAULT_TASKS_PATH)
        execute_task_obj = find_task(tasks, parsed_args.execute_task)
        if execute_task_obj is None:
            print(f'Task not found: "{parsed_args.execute_task}". Use a task id or name from {DEFAULT_TASKS_PATH}.')
            return setup_exit
        if not execute_task_obj.browser_steps:
            print(f'Task "{execute_task_obj.id}" has no browser_steps defined, so it cannot be executed.')
            return setup_exit

    source = parsed_args.html_path
    if parsed_args.media and Path(source).suffix.lower() in MEDIA_EXTENSIONS:
        issues, media_result = analyze_media_file(source)
        report = build_json_report(
            source,
            deduplicate_issues(issues),
            source_metadata={
                "source": source,
                "source_type": "media",
                "final_url": None,
                "status_code": None,
                "content_type": Path(source).suffix.lower(),
            },
            extended_results=[media_result],
        )
        print_summary(source, issues)
        print()
        print(f"Media module status: {media_result.get('status')}")
        if parsed_args.json_output:
            save_json_report(report, parsed_args.json_output)
            print(f"JSON report saved: {parsed_args.json_output}")
        if parsed_args.markdown_output:
            save_markdown_report(report, parsed_args.markdown_output)
            print(f"Markdown report saved: {parsed_args.markdown_output}")
        if parsed_args.html_output or parsed_args.html_reports:
            output = parsed_args.html_output or "reports/media_audit.html"
            save_html_report(report, output)
            print(f"HTML report saved: {output}")
        if parsed_args.sarif_output:
            save_sarif_report([report], parsed_args.sarif_output)
            print(f"SARIF report saved: {parsed_args.sarif_output}")
        if parsed_args.junit_output:
            save_junit_xml([report], parsed_args.junit_output)
            print(f"JUnit XML saved: {parsed_args.junit_output}")
        return 0

    issues, source_result = analyze_html_source(source)

    if source_result["error"]:
        print(f"Could not load HTML source: {source_result['error']}", file=sys.stderr)
        return setup_exit

    browser_result = None
    low_vision_result = None
    static_issue_count = len(issues)
    if parsed_args.browser:
        browser_result = run_browser_audit(
            source,
            max_tabs=parsed_args.max_tabs,
            wait_ms=parsed_args.wait_ms,
            visual_proof_dir=parsed_args.visual_proof_dir,
            include_axe=parsed_args.axe,
        )
        issues = merge_browser_issues(issues, browser_result)
    browser_issue_total = len(issues)
    if parsed_args.low_vision:
        low_vision_result = run_low_vision_audit_for_source(
            source,
            wait_ms=parsed_args.wait_ms,
        )
        issues = issues + list(low_vision_result.get("issues", []))

    task_execution = None
    if execute_task_obj is not None:
        task_execution = run_task_execution(
            source,
            execute_task_obj,
            max_tabs=parsed_args.max_tabs,
            wait_ms=parsed_args.wait_ms,
            video_dir=parsed_args.visual_proof_dir if parsed_args.video else None,
        )
        issues = issues + list(task_execution["issues"])
        video = task_execution.get("video") or {}
        if video.get("enabled"):
            print()
            print(f"Task execution video saved: {video['path']}")
        elif video.get("error"):
            print()
            print(f"Task execution video unavailable: {video['error']}")

    extended_results: list[dict] = []
    if _extended_module_flags(parsed_args):
        module_issues, extended_results = run_html_extended_modules(
            source,
            source_result["html"],
            parsed_args,
            browser_result=browser_result,
            source_result=source_result,
        )
        issues = issues + module_issues

    # One barrier seen by several detection modes becomes one finding that
    # lists every evidence source.
    issues = deduplicate_issues(issues)

    review_only_rules: set[str] = set()
    if parsed_args.review_only_rules:
        review_only_rules = {
            name.strip()
            for name in parsed_args.review_only_rules.split(",")
            if name.strip()
        }
        for issue in issues:
            if issue.issue_type not in review_only_rules:
                continue
            effective = issue.confidence or DEFAULT_CONFIDENCE_BY_RULE.get(
                issue.issue_type, FALLBACK_CONFIDENCE
            )
            if effective in {"confirmed", "likely"}:
                issue.confidence = "needs_review"
                if isinstance(issue.evidence, dict):
                    issue.evidence["downgraded_to_review_only"] = True

    print_summary(source, issues)

    if browser_result is not None:
        print_browser_summary(browser_result, static_issue_count, browser_issue_total)

    if low_vision_result is not None:
        print_low_vision_summary(low_vision_result, len(issues))

    if task_execution is not None:
        print_task_execution_summary(task_execution)

    if extended_results:
        print()
        print("Extended modules")
        for result in extended_results:
            print(
                f"   {result.get('module')}: {result.get('status')} "
                f"({len(result.get('findings', []))} findings)"
            )

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

    if selected_task is None and execute_task_obj is not None:
        selected_task = execute_task_obj
        task_blockers = build_task_blockers(selected_task, issues)

    report = None
    if (
        parsed_args.json_output
        or parsed_args.markdown_output
        or parsed_args.html_output
        or parsed_args.ai_scout
        or parsed_args.sarif_output
        or parsed_args.junit_output
        or parsed_args.ci
    ):
        report = build_json_report(
            source,
            issues,
            task=selected_task,
            task_blockers=task_blockers,
            source_metadata=source_result,
            browser_result=browser_result,
            task_execution=task_execution,
            low_vision_result=low_vision_result,
            extended_results=extended_results,
        )
        if review_only_rules:
            report["summary"]["review_only_rules"] = sorted(review_only_rules)
        if parsed_args.ai_scout:
            workflow_tested = selected_task.name if selected_task else ""
            ai_result = run_ai_scout(
                report,
                target_name=source,
                workflow_tested=workflow_tested,
            )
            report["ai_scout"] = ai_result
            base_output = (
                parsed_args.json_output
                or parsed_args.markdown_output
                or parsed_args.html_output
                or "reports/ai_scout"
            )
            base_path = Path(base_output)
            if base_path.suffix:
                base_path = base_path.with_suffix("")
            ai_paths = save_ai_scout_outputs(ai_result, base_path)
            print()
            print(f"AI Scout JSON saved: {ai_paths['json']}")
            print(f"AI Scout Markdown saved: {ai_paths['markdown']}")

    if parsed_args.json_output:
        save_json_report(report, parsed_args.json_output)
        print()
        print(f"JSON report saved: {parsed_args.json_output}")

    if parsed_args.markdown_output:
        save_markdown_report(report, parsed_args.markdown_output)
        print()
        print(f"Markdown report saved: {parsed_args.markdown_output}")

    if parsed_args.html_output:
        save_html_report(report, parsed_args.html_output)
        print()
        print(f"HTML report saved: {parsed_args.html_output}")

    if parsed_args.sarif_output:
        save_sarif_report([report], parsed_args.sarif_output)
        print()
        print(f"SARIF report saved: {parsed_args.sarif_output}")

    if parsed_args.junit_output:
        save_junit_xml([report], parsed_args.junit_output)
        print()
        print(f"JUnit XML saved: {parsed_args.junit_output}")

    if parsed_args.ci:
        tool_error = bool(
            (browser_result is not None and not browser_result.get("success"))
            or (task_execution is not None and not task_execution.get("success"))
        )
        exit_code = compute_ci_exit_code(
            [report],
            fail_severity=parsed_args.fail_severity,
            fail_on_blocked=parsed_args.fail_on_blocked,
            tool_error=tool_error,
        )
        print()
        print(f"CI mode exit code: {exit_code}")
        return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
