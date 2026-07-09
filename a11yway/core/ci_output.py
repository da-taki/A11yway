"""CI-friendly outputs: exit codes, SARIF 2.1.0, and JUnit XML.

This module turns A11yway JSON reports into artifacts a pipeline can act
on: a meaningful exit code, a SARIF file so findings render inline on
GitHub, and a JUnit XML file where each task execution step is a test
case. Everything here uses only the standard library and works the same
for single audits and batch runs (a batch is just a list of reports).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


# Exit codes for --ci mode.
EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_BLOCKED = 2
EXIT_TOOL_ERROR = 3

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}

SEVERITY_TO_SARIF_LEVEL = {
    "high": "error",
    "medium": "warning",
    "low": "note",
}

SARIF_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"


def count_findings_at_or_above(reports: list[dict], fail_severity: str) -> int:
    """Count issues across reports whose severity meets the threshold."""
    threshold = SEVERITY_RANK.get(fail_severity, SEVERITY_RANK["high"])
    count = 0
    for report in reports:
        for issue in report.get("issues", []):
            if SEVERITY_RANK.get(issue.get("severity", ""), 0) >= threshold:
                count += 1
    return count


def find_blocked_tasks(reports: list[dict]) -> list[dict]:
    """Return task execution blocks that ran but did not complete."""
    blocked = []
    for report in reports:
        execution = report.get("task_execution")
        if execution and execution.get("success") and not execution.get("completed"):
            blocked.append(execution)
    return blocked


def compute_ci_exit_code(
    reports: list[dict],
    fail_severity: str = "high",
    fail_on_blocked: bool = True,
    tool_error: bool = False,
) -> int:
    """Map audit outcomes onto CI exit codes.

    3 = tool or setup error (results are incomplete, so it wins),
    2 = a task execution was blocked, 1 = findings at or above the
    severity threshold, 0 = neither.
    """
    if tool_error:
        return EXIT_TOOL_ERROR
    if fail_on_blocked and find_blocked_tasks(reports):
        return EXIT_BLOCKED
    if count_findings_at_or_above(reports, fail_severity) > 0:
        return EXIT_FINDINGS
    return EXIT_OK


def _source_uri(report: dict) -> str:
    """Return a SARIF artifact URI for the report's source."""
    source = ""
    if isinstance(report.get("source"), dict):
        source = report["source"].get("input") or ""
    source = source or report.get("source_file", "") or "unknown-source"
    if source.startswith("http://") or source.startswith("https://"):
        return source
    return Path(source).as_posix()


def _result_message(issue: dict) -> str:
    """Build a readable SARIF result message from one issue."""
    parts = [issue.get("message") or issue.get("issue_type", "Accessibility finding")]
    evidence = issue.get("evidence")
    if isinstance(evidence, dict):
        reason = evidence.get("reason")
        if reason:
            parts.append(str(reason))
        snippet = evidence.get("snippet")
        if snippet:
            parts.append(f"Evidence: {snippet}")
    return " ".join(str(part) for part in parts)


def build_sarif_report(reports: list[dict]) -> dict:
    """Build a SARIF 2.1.0 document from one or more A11yway reports."""
    rules: list[dict] = []
    rule_indexes: dict[str, int] = {}
    results: list[dict] = []

    for report in reports:
        uri = _source_uri(report)
        for issue in report.get("issues", []):
            issue_type = issue.get("issue_type", "unknown_issue")
            rule_meta = issue.get("rule") or {}
            if issue_type not in rule_indexes:
                rule_indexes[issue_type] = len(rules)
                sarif_rule: dict[str, Any] = {
                    "id": issue_type,
                    "shortDescription": {
                        "text": rule_meta.get("title")
                        or issue.get("message")
                        or issue_type
                    },
                    "defaultConfiguration": {
                        "level": SEVERITY_TO_SARIF_LEVEL.get(
                            rule_meta.get("default_severity")
                            or issue.get("severity", "medium"),
                            "warning",
                        )
                    },
                }
                if rule_meta.get("why_it_matters"):
                    sarif_rule["fullDescription"] = {
                        "text": rule_meta["why_it_matters"]
                    }
                if rule_meta.get("how_to_fix"):
                    sarif_rule["help"] = {"text": rule_meta["how_to_fix"]}
                rules.append(sarif_rule)

            location: dict[str, Any] = {
                "physicalLocation": {"artifactLocation": {"uri": uri}}
            }
            evidence = issue.get("evidence")
            if isinstance(evidence, dict):
                line = evidence.get("line")
                if isinstance(line, int) and line > 0:
                    location["physicalLocation"]["region"] = {"startLine": line}

            results.append(
                {
                    "ruleId": issue_type,
                    "ruleIndex": rule_indexes[issue_type],
                    "level": SEVERITY_TO_SARIF_LEVEL.get(
                        issue.get("severity", "medium"), "warning"
                    ),
                    "message": {"text": _result_message(issue)},
                    "locations": [location],
                }
            )

    return {
        "$schema": SARIF_SCHEMA_URI,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "A11yway",
                        "version": "prototype",
                        "informationUri": "https://github.com/da-taki/A11yway",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def save_sarif_report(reports: list[dict], output_path: str | Path) -> None:
    """Write a SARIF file, creating parent directories if needed."""
    import json

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_sarif_report(reports), indent=2), encoding="utf-8"
    )


def _junit_step_message(step: dict) -> str:
    """Build the failure message for one blocked or failed step."""
    parts = [step.get("detail") or "Step failed."]
    target = step.get("target")
    if target:
        parts.append(f'Target: "{target}".')
    if step.get("blocked_reason"):
        parts.append(f"Reason: {step['blocked_reason']}.")
    return " ".join(parts)


def build_junit_xml(reports: list[dict]) -> str:
    """Build JUnit XML where each task execution step is a test case."""
    testsuites = ET.Element("testsuites", name="A11yway task execution")
    total_tests = 0
    total_failures = 0
    total_skipped = 0

    for report in reports:
        execution = report.get("task_execution")
        if not execution:
            continue
        suite_name = execution.get("task_name") or execution.get("task_id") or "task"
        source = _source_uri(report)
        testsuite = ET.SubElement(testsuites, "testsuite", name=suite_name)

        if not execution.get("success"):
            case = ET.SubElement(
                testsuite, "testcase", classname=source, name="task_setup"
            )
            error = ET.SubElement(
                case,
                "error",
                message=str(execution.get("error") or "Task execution could not run."),
            )
            error.text = (
                "The task could not be attempted; this is a tool or setup "
                "problem, not a verdict about the page."
            )
            testsuite.set("tests", "1")
            testsuite.set("errors", "1")
            total_tests += 1
            continue

        suite_tests = 0
        suite_failures = 0
        suite_skipped = 0
        for step in execution.get("steps", []):
            case = ET.SubElement(
                testsuite,
                "testcase",
                classname=source,
                name=str(step.get("id") or step.get("action") or "step"),
            )
            status = step.get("status")
            suite_tests += 1
            if status == "failed":
                suite_failures += 1
                failure = ET.SubElement(
                    case, "failure", message=_junit_step_message(step)
                )
                failure.text = (
                    f"Action: {step.get('action', '')}. "
                    f"Detail: {step.get('detail', '')}"
                )
            elif status == "skipped":
                suite_skipped += 1
                skipped = ET.SubElement(case, "skipped")
                skipped.set("message", str(step.get("detail") or "Skipped."))

        testsuite.set("tests", str(suite_tests))
        testsuite.set("failures", str(suite_failures))
        testsuite.set("skipped", str(suite_skipped))
        total_tests += suite_tests
        total_failures += suite_failures
        total_skipped += suite_skipped

    testsuites.set("tests", str(total_tests))
    testsuites.set("failures", str(total_failures))
    testsuites.set("skipped", str(total_skipped))
    return ET.tostring(testsuites, encoding="unicode", xml_declaration=True)


def save_junit_xml(reports: list[dict], output_path: str | Path) -> None:
    """Write a JUnit XML file, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_junit_xml(reports), encoding="utf-8")
