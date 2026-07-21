from __future__ import annotations

import json
from pathlib import Path

import pytest

from a11yway.core.extended_results import (
    DETERMINISTIC,
    EXTENDED_RESULT_SCHEMA_VERSION,
    ExtendedCheckResult,
    extended_issue,
    json_safe,
    module_result,
    validate_extended_result,
)
from a11yway.core.report_builder import REPORT_SCHEMA_VERSION, build_json_report


ROOT = Path(__file__).resolve().parents[1]


def test_extended_results_uses_python_310_compatible_utc() -> None:
    source = (ROOT / "a11yway/core/extended_results.py").read_text(encoding="utf-8")

    assert "from datetime import UTC" not in source
    assert "datetime.now(UTC)" not in source
    assert "timezone.utc" in source


def test_extended_result_contains_schema_version_and_timestamp() -> None:
    result = ExtendedCheckResult(module="forms", check_id="x").to_json()

    assert result["schema_version"] == EXTENDED_RESULT_SCHEMA_VERSION
    assert result["created_at"].endswith("Z")
    assert not validate_extended_result(result)


@pytest.mark.parametrize(
    ("bad_value", "expected"),
    [
        ("critical", "low"),
        ("", "low"),
        ("HIGH", "high"),
    ],
)
def test_extended_issue_normalizes_severity(bad_value: str, expected: str) -> None:
    issue = extended_issue(
        module="forms",
        check_id="x",
        title="T",
        issue_type="t",
        severity=bad_value,
        source="fixture",
    )

    assert issue.severity == expected


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [
        (None, "needs_review"),
        ("confirmed", "strong"),
        ("LIKELY", "likely"),
        ("unknown", "needs_review"),
    ],
)
def test_extended_issue_normalizes_confidence(confidence: str | None, expected: str) -> None:
    issue = extended_issue(
        module="forms",
        check_id="x",
        title="T",
        issue_type="t",
        severity="medium",
        source="fixture",
        confidence=confidence,
    )

    assert issue.confidence == expected
    assert issue.evidence["review_status"] == expected


def test_deterministic_issue_defaults_to_likely_confidence() -> None:
    issue = extended_issue(
        module="documents",
        check_id="pdf_tagged",
        title="T",
        issue_type="t",
        severity="high",
        source="fixture.pdf",
        evidence_type=DETERMINISTIC,
    )

    assert issue.confidence == "likely"
    assert issue.evidence["deterministic"] is True


def test_json_safe_normalizes_paths_sets_and_unknown_objects() -> None:
    class Thing:
        def __str__(self) -> str:
            return "thing"

    normalized = json_safe(
        {
            "path": Path("a") / "b.txt",
            "set": {"z", "a"},
            "object": Thing(),
        }
    )

    assert normalized["path"] == "a/b.txt"
    assert sorted(normalized["set"]) == ["a", "z"]
    assert normalized["object"] == "thing"


def test_module_result_sorts_findings_for_stable_output() -> None:
    later = extended_issue(module="m", check_id="c", title="B", issue_type="z_type", severity="low", source="s")
    earlier = extended_issue(module="m", check_id="c", title="A", issue_type="a_type", severity="low", source="s")

    result = module_result("m", "c", [later, earlier]).to_json()

    assert [item["issue_type"] for item in result["findings"]] == ["a_type", "z_type"]


def test_validate_extended_result_reports_schema_problems() -> None:
    problems = validate_extended_result(
        {
            "schema_version": "0",
            "status": "odd",
            "findings": {},
            "artifacts": [],
            "limitations": {},
        }
    )

    assert "unsupported_schema_version" in problems
    assert "invalid_status" in problems
    assert "missing_module" in problems
    assert "invalid_findings" in problems
    assert "invalid_artifacts" in problems
    assert "invalid_limitations" in problems


def test_extended_result_records_schema_errors_for_invalid_instance() -> None:
    result = ExtendedCheckResult(
        module="forms",
        check_id="x",
        status="not-a-status",
        schema_version="0",
    ).to_json()

    assert result["status"] == "failed"
    assert "schema_errors" in result


def test_extended_issue_keeps_wcag_relation_when_supplied() -> None:
    issue = extended_issue(
        module="forms",
        check_id="x",
        title="T",
        issue_type="t",
        severity="medium",
        source="fixture",
        wcag=[{"sc": "3.3.2", "name": "Labels or Instructions"}],
    )

    assert issue.evidence["wcag_relation"][0]["sc"] == "3.3.2"


def test_build_json_report_adds_report_schema_metadata() -> None:
    report = build_json_report("fixture.html", [])

    assert report["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert report["extended_result_schema_version"] == EXTENDED_RESULT_SCHEMA_VERSION
    json.dumps(report)


def test_build_json_report_sorts_extended_modules() -> None:
    report = build_json_report(
        "fixture.html",
        [],
        extended_results=[
            ExtendedCheckResult(module="workflow", check_id="b").to_json(),
            ExtendedCheckResult(module="forms", check_id="a").to_json(),
        ],
    )

    assert [item["module"] for item in report["extended_modules"]] == ["forms", "workflow"]
