"""Reviewer verdict ingestion for A11yway reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


VERDICT_VALUES = {"confirmed", "false_positive", "needs_review", "fixed", "missed_issue"}


def load_verdicts(path: str | Path) -> dict[str, Any]:
    """Load a reviewer verdict JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _stable_source(report_or_issue: dict[str, Any]) -> str:
    """Return source text without depending on absolute local paths."""
    source = report_or_issue.get("source_file") or report_or_issue.get("source") or ""
    if isinstance(source, dict):
        source = source.get("input") or source.get("final_url") or ""
    return Path(str(source)).name if source and not str(source).startswith("http") else str(source)


def issue_fingerprint(issue: dict[str, Any], source: str = "") -> str:
    """Build a deterministic fingerprint from stable issue fields."""
    evidence = issue.get("evidence", {}) if isinstance(issue.get("evidence"), dict) else {}
    parts = [
        issue.get("issue_type", ""),
        source or _stable_source(issue),
        issue.get("message", ""),
    ]
    for key in ["snippet", "tag", "id", "name", "href", "src", "text"]:
        value = evidence.get(key)
        if value not in [None, ""]:
            parts.append(f"{key}={value}")
    raw = "|".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def summarize_verdicts(verdicts: dict[str, Any]) -> dict[str, Any]:
    """Count verdict outcomes and preserve reviewer context."""
    counts = {value: 0 for value in VERDICT_VALUES}
    for item in verdicts.get("verdicts", []):
        verdict = item.get("verdict", "needs_review")
        if verdict in counts:
            counts[verdict] += 1
    missed = verdicts.get("missed_issues", [])
    counts["missed_issue"] += len(missed)
    return {
        "reviewer": verdicts.get("reviewer", {}),
        "source_report": verdicts.get("source_report", ""),
        "counts": counts,
        "missed_issue_count": len(missed),
        "overall_feedback": verdicts.get("overall_feedback", {}),
    }


def apply_verdicts_to_report(report: dict[str, Any], verdicts: dict[str, Any]) -> dict[str, Any]:
    """Attach reviewer verdicts to report issues and add a review summary."""
    updated = json.loads(json.dumps(report))
    source = _stable_source(updated)
    by_fingerprint = {
        item.get("issue_fingerprint"): item for item in verdicts.get("verdicts", [])
    }
    for issue in updated.get("issues", []):
        fingerprint = issue_fingerprint(issue, source=source)
        issue["fingerprint"] = fingerprint
        verdict = by_fingerprint.get(fingerprint)
        if verdict:
            issue["review"] = {
                "verdict": verdict.get("verdict", "needs_review"),
                "severity_feedback": verdict.get("severity_feedback", ""),
                "notes": verdict.get("notes", ""),
            }
    summary = summarize_verdicts(verdicts)
    updated["review_summary"] = {
        **summary["counts"],
        "missed_issue_count": summary["missed_issue_count"],
    }
    if verdicts.get("missed_issues"):
        updated["reviewer_missed_issues"] = verdicts["missed_issues"]
    updated["reviewer"] = verdicts.get("reviewer", {})
    return updated


def build_verdict_summary_markdown(summary: dict[str, Any]) -> str:
    """Build a Markdown summary of reviewer verdicts."""
    reviewer = summary.get("reviewer", {})
    counts = summary.get("counts", {})
    feedback = summary.get("overall_feedback", {})
    lines = [
        "# A11yway Reviewer Verdict Summary",
        "",
        f"- Source report: {summary.get('source_report', '')}",
        f"- Reviewer role: {reviewer.get('role', '')}",
        f"- Permission to quote: {str(reviewer.get('permission_to_quote', False)).lower()}",
        f"- Permission to name organization: {str(reviewer.get('permission_to_name_organization', False)).lower()}",
        "",
        "## Verdict Counts",
        "",
    ]
    for key in ["confirmed", "false_positive", "needs_review", "fixed", "missed_issue"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")
    if feedback:
        lines.extend(
            [
                "",
                "## Overall Feedback",
                "",
                f"- Accuracy rating: {feedback.get('accuracy_rating', '')}",
                f"- Usefulness rating: {feedback.get('usefulness_rating', '')}",
                f"- Clarity rating: {feedback.get('clarity_rating', '')}",
                f"- Would use again: {str(feedback.get('would_use_again', '')).lower()}",
            ]
        )
    lines.extend(
        [
            "",
            "Reviewer verdicts support responsible accuracy tracking. Do not publicly name organizations unless permission was granted.",
            "",
        ]
    )
    return "\n".join(lines)


def save_verdict_summary_markdown(summary: dict[str, Any], path: str | Path) -> None:
    """Write a reviewer verdict summary."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_verdict_summary_markdown(summary), encoding="utf-8")
