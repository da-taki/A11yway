import json
from pathlib import Path

from a11yway.core.rules import RULES, enrich_issue_with_rule
from a11yway.core.wcag_coverage import (
    RULE_WCAG_MAP,
    WCAG_2_2_CRITERIA,
    build_coverage_markdown,
    build_coverage_matrix,
    coverage_summary,
    format_coverage_cli,
    load_coverage_registry,
    rule_coverage_index,
    wcag_mappings_for_issue_type,
)
from a11yway.main import main


def test_wcag22_registry_scope_and_schema() -> None:
    registry = load_coverage_registry()
    criteria = registry["criteria"]
    assert registry["allowed_coverage_statuses"] == [
        "automated",
        "partially_automated",
        "manual_only",
        "unsupported",
    ]
    assert len(criteria) == 55
    assert "4.1.1" not in {row["criterion"] for row in criteria}
    for row in criteria:
        assert row["criterion"] in WCAG_2_2_CRITERIA
        assert WCAG_2_2_CRITERIA[row["criterion"]]["level"] in {"A", "AA"}
        assert row["short_name"] == WCAG_2_2_CRITERIA[row["criterion"]]["name"]
        assert row["level"] in {"A", "AA"}
        assert row["coverage_status"] in registry["allowed_coverage_statuses"]
        assert isinstance(row["implemented_rule_ids"], list)
        assert isinstance(row["testing_engines_used"], list)
        assert isinstance(row["evidence_produced"], list)
        assert row["limitations"]
        assert isinstance(row["human_review_required"], bool)


def test_rule_registry_and_mapping_stay_synchronized() -> None:
    assert set(RULES) == set(RULE_WCAG_MAP)
    assert len(RULES) == len(set(RULES))
    for issue_type, mappings in RULE_WCAG_MAP.items():
        assert mappings, issue_type
        for mapping in mappings:
            assert mapping["sc"] in WCAG_2_2_CRITERIA
            assert mapping["sc"] != "4.1.1"
            assert mapping["coverage"] in {"direct", "partial", "supporting_evidence"}
            assert mapping["detection_mode"]
            assert mapping["limitations"]
            assert mapping["manual_check"]


def test_coverage_summary_counts_required_statuses() -> None:
    summary = coverage_summary()
    assert summary["total_criteria"] == 55
    assert summary["counts"] == {
        "automated": 1,
        "partially_automated": 45,
        "manual_only": 4,
        "unsupported": 5,
    }
    buckets = [
        set(summary["automated"]),
        set(summary["partially_automated"]),
        set(summary["manual_only"]),
        set(summary["unsupported"]),
    ]
    combined: set[str] = set()
    for bucket in buckets:
        assert not (combined & bucket)
        combined |= bucket
    assert combined == {row["criterion"] for row in load_coverage_registry()["criteria"]}


def test_coverage_matrix_and_markdown_are_generated_from_json() -> None:
    registry = load_coverage_registry()
    rows = build_coverage_matrix()
    assert rows == sorted(registry["criteria"], key=lambda row: tuple(int(part) for part in row["criterion"].split(".")))
    markdown = build_coverage_markdown()
    docs = Path("docs/WCAG22_COVERAGE.md").read_text(encoding="utf-8")
    assert markdown == docs
    assert "| Criterion | Short name | Level | Status | Rules | Engines | Evidence | Human review required | Limitations |" in markdown
    assert "This figure is not WCAG conformance" in markdown


def test_coverage_json_file_matches_loader() -> None:
    raw = json.loads(Path("a11yway/data/wcag22_coverage.json").read_text(encoding="utf-8"))
    assert raw == load_coverage_registry()


def test_cli_output_uses_honest_a_aa_labels(capsys) -> None:
    exit_code = main(["--wcag-coverage"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Total WCAG 2.2 Level A and AA Success Criteria: 55" in captured.out
    assert "Automated: 1" in captured.out
    assert "Partially automated: 45" in captured.out
    assert "Manual only: 4" in captured.out
    assert "Unsupported: 5" in captured.out
    assert "Automated or partially automated rule coverage" in captured.out
    assert "This figure is not WCAG conformance" in captured.out
    assert "Automated or partially automated rule coverage" in captured.out
    assert "Criteria covered by each A11yway rule" in captured.out


def test_wcag_coverage_markdown_flag(tmp_path) -> None:
    output = tmp_path / "coverage.md"
    assert main(["--wcag-coverage-markdown", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == build_coverage_markdown()


def test_rule_coverage_index_does_not_double_count_criteria() -> None:
    index = rule_coverage_index()
    assert index["missing_autocomplete"] == ["1.3.5"]
    assert index["invalid_autocomplete_token"] == ["1.3.5"]
    assert index["accessible_authentication_barrier"] == ["3.3.8"]
    assert len(set(index["missing_form_label"])) == len(index["missing_form_label"])


def test_enriched_issue_carries_wcag_and_confidence() -> None:
    enriched = enrich_issue_with_rule(
        {
            "issue_type": "invalid_autocomplete_token",
            "severity": "medium",
            "message": "x",
            "evidence": {},
            "suggested_fix": "",
        }
    )
    assert enriched["confidence"] == "likely"
    assert [m["sc"] for m in enriched["wcag"]] == ["1.3.5"]
    assert enriched["wcag"][0]["coverage"] == "partial"
    assert enriched["wcag"][0]["manual_check"]


def test_unknown_issue_type_gets_fallback_confidence() -> None:
    enriched = enrich_issue_with_rule(
        {"issue_type": "future_rule", "severity": "low", "evidence": {}}
    )
    assert enriched["confidence"] == "needs_review"
    assert "wcag" not in enriched


def test_wcag_mappings_are_copies() -> None:
    first = wcag_mappings_for_issue_type("keyboard_trap")
    first[0]["coverage"] = "mutated"
    second = wcag_mappings_for_issue_type("keyboard_trap")
    assert second[0]["coverage"] == "partial"
