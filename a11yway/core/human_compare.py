"""Compare A11yway findings with structured human-tester findings."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_human_review(path: str | Path) -> dict[str, Any]:
    """Load a human-review comparison file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_compare_text(value: Any) -> str:
    """Normalize free text for rough matching."""
    lowered = str(value or "").casefold()
    cleaned = re.sub(r"[^\w\s#.-]", " ", lowered, flags=re.UNICODE)
    return " ".join(cleaned.split())


def _issue_tokens(issue: dict[str, Any]) -> set[str]:
    evidence = issue.get("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}
    values = [
        issue.get("issue_type", ""),
        issue.get("message", ""),
        evidence.get("element_selector", ""),
        evidence.get("selector", ""),
        evidence.get("target", ""),
        evidence.get("snippet", ""),
        evidence.get("visible_text", ""),
        evidence.get("accessible_name", ""),
        evidence.get("reason", ""),
    ]
    for mapping in issue.get("wcag", []) or []:
        values.append(mapping.get("sc", ""))
        values.append(mapping.get("name", ""))
    return set(normalize_compare_text(" ".join(str(value) for value in values)).split())


def _human_tokens(finding: dict[str, Any]) -> set[str]:
    values = [
        finding.get("description", ""),
        finding.get("selector", ""),
        finding.get("component", ""),
        finding.get("wcag", ""),
        finding.get("notes", ""),
        finding.get("expected_behavior", ""),
        finding.get("actual_behavior", ""),
    ]
    return set(normalize_compare_text(" ".join(str(value) for value in values)).split())


def _match_score(a11yway_issue: dict[str, Any], human_finding: dict[str, Any]) -> float:
    issue_tokens = _issue_tokens(a11yway_issue)
    human_tokens = _human_tokens(human_finding)
    if not issue_tokens or not human_tokens:
        return 0.0
    overlap = len(issue_tokens & human_tokens)
    score = overlap / max(1, min(len(issue_tokens), len(human_tokens)))

    issue_sc = {
        str(mapping.get("sc", ""))
        for mapping in a11yway_issue.get("wcag", []) or []
        if mapping.get("sc")
    }
    human_sc = {
        str(item)
        for item in (
            human_finding.get("wcag_criteria")
            or human_finding.get("wcag")
            or []
        )
        if item
    }
    if isinstance(human_finding.get("wcag"), str):
        human_sc.add(str(human_finding["wcag"]))
    if issue_sc & human_sc:
        score += 0.35

    evidence = a11yway_issue.get("evidence", {})
    selector = ""
    if isinstance(evidence, dict):
        selector = str(
            evidence.get("element_selector")
            or evidence.get("selector")
            or evidence.get("target")
            or ""
        )
    human_selector = str(human_finding.get("selector") or "")
    if selector and human_selector and normalize_compare_text(selector) == normalize_compare_text(human_selector):
        score += 0.5
    return min(score, 1.0)


def compare_human_review(
    a11yway_report: dict[str, Any],
    human_review: dict[str, Any],
    *,
    match_threshold: float = 0.42,
) -> dict[str, Any]:
    """Match likely equivalent A11yway and human findings."""
    a11yway_issues = list(a11yway_report.get("issues", []))
    human_findings = list(
        human_review.get("findings")
        or human_review.get("human_findings")
        or []
    )
    used_issue_indexes: set[int] = set()
    matches: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []

    for human_index, human in enumerate(human_findings):
        best_index = None
        best_score = 0.0
        for issue_index, issue in enumerate(a11yway_issues):
            if issue_index in used_issue_indexes:
                continue
            score = _match_score(issue, human)
            if score > best_score:
                best_index = issue_index
                best_score = score
        if best_index is None or best_score < match_threshold:
            missed.append({"human_index": human_index, "human_finding": human})
            continue
        used_issue_indexes.add(best_index)
        issue = a11yway_issues[best_index]
        severity_disagreement = bool(
            human.get("severity")
            and issue.get("severity")
            and str(human.get("severity")).casefold() != str(issue.get("severity")).casefold()
        )
        match_type = "true_positive" if best_score >= 0.65 else "partial_match"
        if best_score >= 0.5 and not severity_disagreement:
            match_type = "true_positive"
        matches.append(
            {
                "human_index": human_index,
                "a11yway_index": best_index,
                "match_score": round(best_score, 3),
                "match_type": match_type,
                "human_finding": human,
                "a11yway_issue": {
                    "issue_type": issue.get("issue_type"),
                    "severity": issue.get("severity"),
                    "message": issue.get("message"),
                    "evidence": issue.get("evidence", {}),
                },
                "severity_disagreement": severity_disagreement,
                "evidence_disagreement": bool(human.get("corrected_evidence")),
            }
        )

    false_positives = [
        {"a11yway_index": index, "a11yway_issue": issue}
        for index, issue in enumerate(a11yway_issues)
        if index not in used_issue_indexes
    ]
    true_positive_count = sum(1 for item in matches if item["match_type"] == "true_positive")
    partial_count = sum(1 for item in matches if item["match_type"] == "partial_match")
    decided = true_positive_count + partial_count + len(false_positives)
    precision = (
        round((true_positive_count + partial_count) / decided, 3)
        if decided
        else None
    )
    recall_denominator = len(human_findings)
    recall = (
        round((true_positive_count + partial_count) / recall_denominator, 3)
        if recall_denominator
        else None
    )
    return {
        "schema_version": "1.0",
        "reviewer": human_review.get("reviewer", {}),
        "summary": {
            "a11yway_findings": len(a11yway_issues),
            "human_findings": len(human_findings),
            "true_positives": true_positive_count,
            "partial_matches": partial_count,
            "false_positives": len(false_positives),
            "missed_human_findings": len(missed),
            "severity_disagreements": sum(1 for item in matches if item["severity_disagreement"]),
            "evidence_disagreements": sum(1 for item in matches if item["evidence_disagreement"]),
            "precision": precision,
            "recall_against_human_findings": recall,
        },
        "matches": matches,
        "false_positives": false_positives,
        "missed_human_findings": missed,
        "limitations": [
            "Matching is heuristic and should be reviewed by a trained accessibility professional.",
            "Human findings do not need A11yway rule IDs; selectors, WCAG criteria, descriptions, and notes are used when available.",
        ],
    }


def build_human_comparison_markdown(comparison: dict[str, Any]) -> str:
    """Build a readable human-comparison report."""
    summary = comparison.get("summary", {})
    lines = [
        "# A11yway Human-Tester Comparison",
        "",
        "## Summary",
        "",
        f"- A11yway findings: {summary.get('a11yway_findings', 0)}",
        f"- Human findings: {summary.get('human_findings', 0)}",
        f"- True positives: {summary.get('true_positives', 0)}",
        f"- Partial matches: {summary.get('partial_matches', 0)}",
        f"- False positives: {summary.get('false_positives', 0)}",
        f"- Missed human findings: {summary.get('missed_human_findings', 0)}",
        f"- Severity disagreements: {summary.get('severity_disagreements', 0)}",
        f"- Evidence disagreements: {summary.get('evidence_disagreements', 0)}",
        f"- Precision: {summary.get('precision', 'n/a')}",
        f"- Recall against human findings: {summary.get('recall_against_human_findings', 'n/a')}",
        "",
        "## Matches",
        "",
    ]
    if not comparison.get("matches"):
        lines.append("- None")
    for item in comparison.get("matches", []):
        issue = item.get("a11yway_issue", {})
        human = item.get("human_finding", {})
        lines.append(
            "- {match_type}: {issue_type} matched human finding \"{description}\" (score {score})".format(
                match_type=item.get("match_type", ""),
                issue_type=issue.get("issue_type", ""),
                description=str(human.get("description", ""))[:120],
                score=item.get("match_score", ""),
            )
        )
    lines.extend(["", "## Missed Human Findings", ""])
    if not comparison.get("missed_human_findings"):
        lines.append("- None")
    for item in comparison.get("missed_human_findings", []):
        finding = item.get("human_finding", {})
        lines.append(f"- {finding.get('description', '')}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in comparison.get("limitations", []))
    lines.append("")
    return "\n".join(lines)


def save_human_comparison(
    comparison: dict[str, Any],
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> None:
    """Save human-comparison outputs."""
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(comparison, indent=2, sort_keys=True), encoding="utf-8")
    if markdown_path:
        path = Path(markdown_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_human_comparison_markdown(comparison), encoding="utf-8")
