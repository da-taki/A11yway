"""Tests for CI mode: exit codes, SARIF output, and JUnit XML.

These tests must pass whether or not Playwright is installed. The real
browser integration tests skip themselves when the browser cannot run.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import a11yway.main as main_module
from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.ci_output import (
    EXIT_BLOCKED,
    EXIT_FINDINGS,
    EXIT_OK,
    EXIT_TOOL_ERROR,
    SEVERITY_TO_SARIF_LEVEL,
    build_junit_xml,
    build_sarif_report,
    compute_ci_exit_code,
)
from a11yway.core.report_builder import build_json_report
from a11yway.main import analyze_html_file, main
from a11yway.models.issue import AccessibilityIssue


def report_with_issue(severity: str) -> dict:
    """Build a small enriched report containing one issue."""
    issue = AccessibilityIssue(
        title="Form control is missing an accessible label",
        issue_type="missing_form_label",
        severity=severity,
        agent_name="Page Analyzer",
        evidence={"snippet": '<input type="text">', "line": 12},
        suggested_fix="Add a label.",
    )
    return build_json_report("examples/sample_form.html", [issue])


def report_with_execution(completed: bool, success: bool = True) -> dict:
    """Build a report carrying a task execution block."""
    execution = {
        "task_id": "submit_scholarship_application",
        "task_name": "Submit scholarship application",
        "student_profile": "Keyboard-only student",
        "success": success,
        "error": None if success else "Playwright is not installed.",
        "completed": completed,
        "blocked_at_step": None if completed else "submit_form",
        "blocked_reason": None,
        "steps_total": 2,
        "steps_passed": 2 if completed else 1,
        "steps": [
            {
                "id": "focus_name",
                "action": "focus_by_label_or_name",
                "target": "Student name",
                "status": "passed",
                "detail": "Reached with the keyboard (tag: input).",
                "used_fallback": False,
                "announced": 'textbox, "Student name"',
                "blocked_reason": None,
            },
            {
                "id": "submit_form",
                "action": "activate_by_role_or_text",
                "target": "Submit application",
                "status": "passed" if completed else "failed",
                "detail": (
                    "Activated with Enter (tag: button)."
                    if completed
                    else "No keyboard-activatable control matched this step."
                ),
                "used_fallback": False,
                "announced": None,
                "blocked_reason": None,
            },
        ],
    }
    return build_json_report(
        "examples/sample_task_execution_form.html", [], task_execution=execution
    )


def test_exit_codes_follow_the_documented_contract() -> None:
    """0 clean, 1 findings, 2 blocked, 3 tool error (which wins)."""
    clean = build_json_report("examples/sample_form.html", [])
    high = report_with_issue("high")
    blocked = report_with_execution(completed=False)

    assert compute_ci_exit_code([clean]) == EXIT_OK
    assert compute_ci_exit_code([high]) == EXIT_FINDINGS
    assert compute_ci_exit_code([blocked], fail_on_blocked=True) == EXIT_BLOCKED
    assert compute_ci_exit_code([high], tool_error=True) == EXIT_TOOL_ERROR
    assert (
        compute_ci_exit_code([blocked, high], fail_on_blocked=True) == EXIT_BLOCKED
    )


def test_fail_severity_threshold() -> None:
    """Findings below the threshold must not fail the run."""
    medium = report_with_issue("medium")
    low = report_with_issue("low")

    assert compute_ci_exit_code([medium], fail_severity="high") == EXIT_OK
    assert compute_ci_exit_code([medium], fail_severity="medium") == EXIT_FINDINGS
    assert compute_ci_exit_code([low], fail_severity="low") == EXIT_FINDINGS
    assert compute_ci_exit_code([low], fail_severity="medium") == EXIT_OK


def test_blocked_without_flag_does_not_use_exit_two() -> None:
    """Without fail_on_blocked, a blocked task is not exit code 2."""
    blocked = report_with_execution(completed=False)

    assert compute_ci_exit_code([blocked], fail_on_blocked=False) == EXIT_OK


def test_unrun_execution_is_not_treated_as_blocked() -> None:
    """A task that could not run is a tool problem, not a blocked task."""
    unrun = report_with_execution(completed=False, success=False)

    assert compute_ci_exit_code([unrun], fail_on_blocked=True) == EXIT_OK


def test_sarif_structure_matches_the_2_1_0_shape() -> None:
    """A lightweight structural validation of the SARIF document."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    sarif = build_sarif_report([report])

    assert sarif["version"] == "2.1.0"
    assert sarif["$schema"].endswith("sarif-2.1.0.json")
    assert isinstance(sarif["runs"], list) and len(sarif["runs"]) == 1

    run = sarif["runs"][0]
    driver = run["tool"]["driver"]
    assert driver["name"] == "A11yway"
    rule_ids = [rule["id"] for rule in driver["rules"]]
    assert len(rule_ids) == len(set(rule_ids)), "rule ids must be unique"
    for rule in driver["rules"]:
        assert rule["shortDescription"]["text"]
        assert rule["defaultConfiguration"]["level"] in {"error", "warning", "note"}

    assert run["results"], "sample_form should produce findings"
    for result in run["results"]:
        assert result["ruleId"] in rule_ids
        assert rule_ids[result["ruleIndex"]] == result["ruleId"]
        assert result["level"] in {"error", "warning", "note"}
        assert result["message"]["text"]
        location = result["locations"][0]["physicalLocation"]
        assert location["artifactLocation"]["uri"]


def test_sarif_maps_severities_to_levels() -> None:
    """high=error, medium=warning, low=note."""
    assert SEVERITY_TO_SARIF_LEVEL == {
        "high": "error",
        "medium": "warning",
        "low": "note",
    }
    for severity, level in SEVERITY_TO_SARIF_LEVEL.items():
        sarif = build_sarif_report([report_with_issue(severity)])
        assert sarif["runs"][0]["results"][0]["level"] == level


def test_sarif_includes_line_regions_when_available() -> None:
    """Findings with an approximate line get a startLine region."""
    sarif = build_sarif_report([report_with_issue("high")])

    location = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
    assert location["region"]["startLine"] == 12


def test_junit_xml_has_one_test_case_per_step() -> None:
    """Blocked steps become failures with the evidence as the message."""
    blocked = report_with_execution(completed=False)

    root = ET.fromstring(build_junit_xml([blocked]))

    assert root.tag == "testsuites"
    suite = root.find("testsuite")
    assert suite.get("name") == "Submit scholarship application"
    cases = suite.findall("testcase")
    assert [case.get("name") for case in cases] == ["focus_name", "submit_form"]

    failure = cases[1].find("failure")
    assert failure is not None
    assert "No keyboard-activatable control" in failure.get("message")
    assert suite.get("failures") == "1"


def test_junit_xml_marks_unrun_execution_as_error() -> None:
    """A task that could not run becomes an error test case, not a failure."""
    unrun = report_with_execution(completed=False, success=False)

    root = ET.fromstring(build_junit_xml([unrun]))

    suite = root.find("testsuite")
    case = suite.find("testcase")
    assert case.get("name") == "task_setup"
    assert case.find("error") is not None


def test_cli_ci_mode_fails_on_findings(tmp_path: Path) -> None:
    """--ci should exit 1 on the sample form's high findings and write SARIF."""
    sarif_path = tmp_path / "findings.sarif"

    exit_code = main(
        ["examples/sample_form.html", "--ci", "--sarif", str(sarif_path)]
    )

    assert exit_code == EXIT_FINDINGS
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"]


def test_cli_ci_mode_passes_on_clean_page() -> None:
    """--ci should exit 0 when the page has no findings at the threshold."""
    exit_code = main(["examples/sample_announce_transcript.html", "--ci"])

    assert exit_code == EXIT_OK


def test_cli_sarif_without_ci_keeps_exit_zero(tmp_path: Path) -> None:
    """--sarif alone is an export, not a gate."""
    sarif_path = tmp_path / "export.sarif"

    exit_code = main(["examples/sample_form.html", "--sarif", str(sarif_path)])

    assert exit_code == 0
    assert sarif_path.exists()


def test_cli_ci_mode_reports_setup_errors_as_three(monkeypatch) -> None:
    """Missing Playwright in --ci mode must exit 3, not 1."""
    monkeypatch.setattr(main_module, "is_playwright_available", lambda: False)

    exit_code = main(["examples/sample_form.html", "--browser", "--ci"])

    assert exit_code == EXIT_TOOL_ERROR


def test_cli_ci_mode_missing_source_is_setup_error() -> None:
    """An unreadable source in --ci mode must exit 3."""
    exit_code = main(["examples/does_not_exist.html", "--ci"])

    assert exit_code == EXIT_TOOL_ERROR


def test_cli_ci_batch_mode_fails_on_findings(tmp_path: Path) -> None:
    """Batch --ci runs aggregate findings across items."""
    out_dir = tmp_path / "batch"
    sarif_path = tmp_path / "batch.sarif"
    junit_path = tmp_path / "batch-junit.xml"

    exit_code = main(
        [
            "--batch",
            "examples/sample_batch.json",
            "--out-dir",
            str(out_dir),
            "--ci",
            "--sarif",
            str(sarif_path),
            "--junit",
            str(junit_path),
        ]
    )

    assert exit_code == EXIT_FINDINGS
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif["runs"][0]["results"]
    root = ET.fromstring(junit_path.read_text(encoding="utf-8"))
    assert root.tag == "testsuites"


def test_example_workflow_file_exists_and_is_dispatch_only() -> None:
    """The GitHub Action example must not run on this repo's CI."""
    workflow = Path(".github/workflows/a11yway-example.yml").read_text(
        encoding="utf-8"
    )

    assert "workflow_dispatch" in workflow
    assert "push:" not in workflow
    assert "pull_request:" not in workflow
    assert "--ci" in workflow
    assert "--fail-on-blocked" in workflow


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_cli_ci_blocked_task_exits_two(tmp_path: Path) -> None:
    """Integration: a keyboard-blocked workflow fails the build with 2."""
    junit_path = tmp_path / "trap-junit.xml"

    exit_code = main(
        [
            "examples/sample_keyboard_trap.html",
            "--browser",
            "--execute-task",
            "fill_course_survey",
            "--ci",
            "--fail-on-blocked",
            "--junit",
            str(junit_path),
        ]
    )

    assert exit_code == EXIT_BLOCKED
    root = ET.fromstring(junit_path.read_text(encoding="utf-8"))
    failures = root.findall(".//failure")
    assert failures
    assert any("keyboard_trap" in (node.get("message") or "") for node in failures)


@pytest.mark.skipif(
    not is_playwright_available(), reason="Playwright is not installed"
)
def test_cli_ci_completed_task_exits_zero() -> None:
    """Integration: the accessible sample workflow passes CI."""
    exit_code = main(
        [
            "examples/sample_task_execution_form.html",
            "--browser",
            "--execute-task",
            "submit_scholarship_application",
            "--ci",
            "--fail-on-blocked",
        ]
    )

    assert exit_code == EXIT_OK
