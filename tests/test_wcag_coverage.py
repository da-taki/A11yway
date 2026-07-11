"""Tests for the WCAG 2.2 coverage registry and CLI command."""

from a11yway.core.rules import RULES, enrich_issue_with_rule
from a11yway.core.wcag_coverage import (
    AXE_COVERED_CRITERIA,
    CONFIDENCE_LEVELS,
    COVERAGE_LEVELS,
    DETECTION_MODES,
    RULE_WCAG_MAP,
    WCAG_2_2_CRITERIA,
    best_native_coverage,
    build_coverage_markdown,
    build_coverage_matrix,
    coverage_summary,
    format_coverage_cli,
    wcag_mappings_for_issue_type,
)
from a11yway.main import main


def test_wcag_2_2_has_86_criteria() -> None:
    """WCAG 2.2 defines 86 Success Criteria (4.1.1 was removed)."""
    assert len(WCAG_2_2_CRITERIA) == 86
    assert "4.1.1" not in WCAG_2_2_CRITERIA
    assert WCAG_2_2_CRITERIA["2.5.8"]["name"] == "Target Size (Minimum)"
    assert all(
        info["level"] in {"A", "AA", "AAA"} for info in WCAG_2_2_CRITERIA.values()
    )


def test_every_rule_has_a_wcag_mapping_and_vice_versa() -> None:
    """The rule registry and the coverage map must stay in sync."""
    assert set(RULES) == set(RULE_WCAG_MAP)


def test_mappings_reference_valid_criteria_and_vocabulary() -> None:
    """Every mapping must use known criteria, levels, and modes."""
    for issue_type, mappings in RULE_WCAG_MAP.items():
        assert mappings, issue_type
        for mapping in mappings:
            assert mapping["sc"] in WCAG_2_2_CRITERIA, issue_type
            assert mapping["coverage"] in COVERAGE_LEVELS[:3], issue_type
            assert mapping["detection_mode"] in DETECTION_MODES, issue_type
            assert mapping["confidence"] in CONFIDENCE_LEVELS, issue_type
            assert mapping["limitations"], issue_type
            assert mapping["manual_check"], issue_type


def test_axe_covered_criteria_are_valid() -> None:
    """Axe coverage hints must reference real WCAG 2.2 criteria."""
    assert AXE_COVERED_CRITERIA <= set(WCAG_2_2_CRITERIA)


def test_summary_counts_each_criterion_once() -> None:
    """A criterion mapped by several rules must not be double counted."""
    summary = coverage_summary()
    counts = summary["counts"]
    buckets = [
        set(summary["direct"]),
        set(summary["partial"]),
        set(summary["supporting_evidence"]),
        set(summary["axe_only"]),
        set(summary["manual_only"]),
        set(summary["unsupported"]),
    ]
    # Buckets are disjoint and cover all 86 criteria exactly once.
    combined: set[str] = set()
    for bucket in buckets:
        assert not (combined & bucket)
        combined |= bucket
    assert combined == set(WCAG_2_2_CRITERIA)
    assert sum(counts.values()) == 86
    # 4.1.2 is mapped by several rules but appears in exactly one bucket.
    appearances = sum(1 for bucket in buckets if "4.1.2" in bucket)
    assert appearances == 1


def test_best_native_coverage_prefers_strongest_level() -> None:
    """2.1.1 has partial task-execution coverage, which beats supporting."""
    best = best_native_coverage()
    assert best["2.1.1"]["coverage"] == "partial"
    # 1.3.3 only has a review-only heuristic.
    assert best["1.3.3"]["coverage"] == "supporting_evidence"


def test_coverage_matrix_has_one_row_per_criterion() -> None:
    """The matrix must cover every criterion, sorted numerically."""
    rows = build_coverage_matrix()
    assert len(rows) == 86
    scs = [row["sc"] for row in rows]
    assert scs.index("1.4.9") < scs.index("1.4.10")
    manual = [row for row in rows if row["coverage_type"] == "manual_only"]
    assert all(not row["native_rules"] for row in manual)
    assert all(row["native_coverage"] != "none" for row in rows if row["native_rules"])


def test_cli_output_avoids_conformance_claims() -> None:
    """Coverage text must never read as a conformance claim."""
    for text in [format_coverage_cli(), build_coverage_markdown()]:
        lowered = text.lower()
        assert "not a" in lowered and "conformance" in lowered
        assert "wcag compliant" not in lowered
        assert "certified" not in lowered


def test_wcag_coverage_cli_flag(capsys) -> None:
    """--wcag-coverage prints the summary and exits cleanly."""
    exit_code = main(["--wcag-coverage"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Total WCAG 2.2 Success Criteria: 86" in captured.out
    assert "Direct native coverage" in captured.out
    assert "Manual review only" in captured.out
    assert "Unsupported" in captured.out


def test_wcag_coverage_markdown_flag(tmp_path, capsys) -> None:
    """--wcag-coverage-markdown writes the full matrix."""
    output = tmp_path / "coverage.md"
    exit_code = main(["--wcag-coverage-markdown", str(output)])

    assert exit_code == 0
    text = output.read_text(encoding="utf-8")
    assert "| WCAG Success Criterion | Name | Level | Native coverage | Axe-only coverage | Coverage type | A11yway rules | Evidence mode | Limitations | Manual testing needed |" in text
    assert "| 2.5.8 | Target Size (Minimum) | AA | partial | no | partial |" in text
    assert "manual_only" in text


def test_enriched_issue_carries_wcag_and_confidence() -> None:
    """Report issues expose WCAG mappings and a confidence level."""
    enriched = enrich_issue_with_rule(
        {
            "issue_type": "missing_autocomplete",
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
    """Unknown checks never break enrichment."""
    enriched = enrich_issue_with_rule(
        {"issue_type": "future_rule", "severity": "low", "evidence": {}}
    )

    assert enriched["confidence"] == "needs_review"
    assert "wcag" not in enriched


def test_wcag_mappings_are_copies() -> None:
    """Callers must not be able to mutate the registry."""
    first = wcag_mappings_for_issue_type("keyboard_trap")
    first[0]["coverage"] = "mutated"
    second = wcag_mappings_for_issue_type("keyboard_trap")

    assert second[0]["coverage"] == "partial"
