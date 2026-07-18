"""Reviewer verdict ingestion for A11yway reports."""

from __future__ import annotations

import hashlib
import json
import csv
from pathlib import Path
from typing import Any


VERDICT_VALUES = {
    "confirmed",
    "false_positive",
    "partially_confirmed",
    "needs_review",
    "fixed",
    "missed_issue",
    "duplicate",
    "not_applicable",
    "unable_to_reproduce",
}
TRUE_POSITIVE_VERDICTS = {"confirmed", "partially_confirmed", "fixed"}
FALSE_POSITIVE_VERDICTS = {
    "false_positive",
    "duplicate",
    "not_applicable",
    "unable_to_reproduce",
}
DECIDED_VERDICTS = TRUE_POSITIVE_VERDICTS | FALSE_POSITIVE_VERDICTS


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
                "reviewer_role": verdict.get("reviewer_role")
                or verdicts.get("reviewer", {}).get("role", ""),
                "testing_environment": verdict.get("testing_environment", ""),
                "browser": verdict.get("browser", ""),
                "operating_system": verdict.get("operating_system", ""),
                "assistive_technology": verdict.get("assistive_technology", ""),
                "manual_testing_method": verdict.get("manual_testing_method", ""),
                "related_wcag": verdict.get("related_wcag", []),
                "severity_adjustment": verdict.get("severity_adjustment", ""),
                "corrected_evidence": verdict.get("corrected_evidence", {}),
                "permission_to_quote": bool(
                    verdict.get(
                        "permission_to_quote",
                        verdicts.get("reviewer", {}).get("permission_to_quote", False),
                    )
                ),
                "permission_to_name_reviewer": bool(
                    verdict.get(
                        "permission_to_name_reviewer",
                        verdicts.get("reviewer", {}).get("permission_to_name_reviewer", False),
                    )
                ),
            }
    summary = summarize_verdicts(verdicts)
    updated["review_summary"] = {
        **summary["counts"],
        "missed_issue_count": summary["missed_issue_count"],
    }
    if verdicts.get("missed_issues"):
        updated["reviewer_missed_issues"] = verdicts["missed_issues"]
    updated["reviewer"] = verdicts.get("reviewer", {})
    updated["precision_stats"] = build_precision_stats([updated])
    return updated


def _issue_detection_modes(issue: dict[str, Any]) -> list[str]:
    """Return the detection modes recorded in one issue's evidence."""
    evidence = issue.get("evidence")
    if not isinstance(evidence, dict):
        return ["static"]
    sources = evidence.get("evidence_sources")
    if isinstance(sources, list) and sources:
        return [str(source) for source in sources]
    return [str(evidence.get("detected_in") or "static")]


def _precision_bucket() -> dict[str, Any]:
    """Return an empty precision accumulator."""
    return {
        "confirmed": 0,
        "partially_confirmed": 0,
        "false_positive": 0,
        "needs_review": 0,
        "fixed": 0,
        "duplicate": 0,
        "not_applicable": 0,
        "unable_to_reproduce": 0,
        "reviewed": 0,
        "decided": 0,
        "precision": None,
        "false_positive_rate": None,
        "confirmation_rate": None,
        "unable_to_reproduce_rate": None,
    }


def _record_verdict(bucket: dict[str, Any], verdict: str) -> None:
    """Count one verdict into a precision accumulator."""
    if verdict in VERDICT_VALUES - {"missed_issue"}:
        bucket[verdict] += 1
        bucket["reviewed"] += 1
        if verdict in DECIDED_VERDICTS:
            bucket["decided"] += 1


def _finalize_precision(bucket: dict[str, Any]) -> None:
    """Compute precision as (confirmed + fixed) / decided reviews."""
    decided = bucket["decided"]
    if decided:
        bucket["precision"] = round(
            (
                bucket["confirmed"]
                + bucket["fixed"]
                + bucket["partially_confirmed"]
            )
            / decided,
            3,
        )
        bucket["false_positive_rate"] = round(
            (
                bucket["false_positive"]
                + bucket["duplicate"]
                + bucket["not_applicable"]
                + bucket["unable_to_reproduce"]
            )
            / decided,
            3,
        )
    if bucket["reviewed"]:
        bucket["confirmation_rate"] = round(
            (
                bucket["confirmed"]
                + bucket["fixed"]
                + bucket["partially_confirmed"]
            )
            / bucket["reviewed"],
            3,
        )
        bucket["unable_to_reproduce_rate"] = round(
            bucket["unable_to_reproduce"] / bucket["reviewed"], 3
        )


def build_precision_stats(reviewed_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute reviewer precision per rule, WCAG criterion, and detection mode.

    Precision counts confirmed and fixed verdicts as true positives and
    false_positive verdicts as false positives; needs_review verdicts are
    tracked but excluded from the ratio because they are undecided. Missed
    issues affect recall, not precision, and are reported separately.
    """
    by_rule: dict[str, dict[str, Any]] = {}
    by_category: dict[str, dict[str, Any]] = {}
    by_sc: dict[str, dict[str, Any]] = {}
    by_mode: dict[str, dict[str, Any]] = {}
    by_severity: dict[str, dict[str, Any]] = {}
    by_site: dict[str, dict[str, Any]] = {}
    unique_root = _precision_bucket()
    raw_occurrence = _precision_bucket()
    total = _precision_bucket()
    missed_issue_count = 0

    for report in reviewed_reports:
        missed_issue_count += len(report.get("reviewer_missed_issues", []))
        site = _stable_source(report) or report.get("source_file", "") or "unknown"
        for issue in report.get("issues", []):
            review = issue.get("review")
            if not review:
                continue
            verdict = review.get("verdict", "needs_review")
            _record_verdict(total, verdict)
            _record_verdict(unique_root, verdict)
            occurrence_count = 1
            evidence = issue.get("evidence", {})
            if isinstance(evidence, dict):
                occurrence_count = int(evidence.get("occurrence_count", 1) or 1)
            for _index in range(max(1, occurrence_count)):
                _record_verdict(raw_occurrence, verdict)
            rule_bucket = by_rule.setdefault(
                issue.get("issue_type", "unknown"), _precision_bucket()
            )
            _record_verdict(rule_bucket, verdict)
            category = "Uncategorized"
            if isinstance(issue.get("evidence"), dict):
                category = issue["evidence"].get("issue_category") or category
            elif isinstance(issue.get("rule"), dict):
                category = issue["rule"].get("category") or category
            _record_verdict(by_category.setdefault(category, _precision_bucket()), verdict)
            severity = issue.get("severity", "unknown")
            _record_verdict(by_severity.setdefault(severity, _precision_bucket()), verdict)
            _record_verdict(by_site.setdefault(site, _precision_bucket()), verdict)
            for mapping in issue.get("wcag", []) or []:
                sc_bucket = by_sc.setdefault(mapping.get("sc", "?"), _precision_bucket())
                _record_verdict(sc_bucket, verdict)
            for mode in _issue_detection_modes(issue):
                mode_bucket = by_mode.setdefault(mode, _precision_bucket())
                _record_verdict(mode_bucket, verdict)

    for bucket in [
        total,
        unique_root,
        raw_occurrence,
        *by_rule.values(),
        *by_category.values(),
        *by_sc.values(),
        *by_mode.values(),
        *by_severity.values(),
        *by_site.values(),
    ]:
        _finalize_precision(bucket)

    return {
        "overall": total,
        "missed_issue_count": missed_issue_count,
        "by_rule": by_rule,
        "by_category": by_category,
        "by_wcag_sc": by_sc,
        "by_detection_mode": by_mode,
        "by_engine": by_mode,
        "by_severity": by_severity,
        "by_site": by_site,
        "unique_root_issue_precision": unique_root,
        "raw_occurrence_precision": raw_occurrence,
        "note": (
            "Precision = (confirmed + partially_confirmed + fixed) / decided "
            "reviews. False positives include false_positive, duplicate, "
            "not_applicable, and unable_to_reproduce. needs_review verdicts "
            "are undecided and excluded from the precision ratio; missed "
            "issues affect recall, not precision."
        ),
    }


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
    for key in [
        "confirmed",
        "partially_confirmed",
        "false_positive",
        "needs_review",
        "fixed",
        "duplicate",
        "not_applicable",
        "unable_to_reproduce",
        "missed_issue",
    ]:
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


def build_precision_report_markdown(stats: dict[str, Any]) -> str:
    """Build a Markdown precision report from reviewed A11yway reports."""
    overall = stats.get("overall", {})
    lines = [
        "# A11yway Precision Report",
        "",
        "## Overall",
        "",
        f"- Reviewed findings: {overall.get('reviewed', 0)}",
        f"- Decided findings: {overall.get('decided', 0)}",
        f"- Precision: {overall.get('precision', 'n/a')}",
        f"- False-positive rate: {overall.get('false_positive_rate', 'n/a')}",
        f"- Confirmation rate: {overall.get('confirmation_rate', 'n/a')}",
        f"- Unable-to-reproduce rate: {overall.get('unable_to_reproduce_rate', 'n/a')}",
        f"- Missed human issues recorded: {stats.get('missed_issue_count', 0)}",
        "",
        "## Unique Root Issues Vs Raw Occurrences",
        "",
        f"- Unique-root precision: {stats.get('unique_root_issue_precision', {}).get('precision', 'n/a')}",
        f"- Raw-occurrence precision: {stats.get('raw_occurrence_precision', {}).get('precision', 'n/a')}",
        "",
    ]
    for title, key in [
        ("Rule Precision", "by_rule"),
        ("Category Precision", "by_category"),
        ("Engine Precision", "by_detection_mode"),
        ("Severity Precision", "by_severity"),
        ("Site Precision", "by_site"),
    ]:
        lines.extend([f"## {title}", "", "| Bucket | Reviewed | Precision | False-positive rate | Unable to reproduce |", "| --- | ---: | --- | --- | ---: |"])
        buckets = stats.get(key, {})
        if not buckets:
            lines.append("| None | 0 | n/a | n/a | 0 |")
        for name, bucket in sorted(buckets.items()):
            lines.append(
                "| {name} | {reviewed} | {precision} | {fp_rate} | {utr} |".format(
                    name=name,
                    reviewed=bucket.get("reviewed", 0),
                    precision=bucket.get("precision", "n/a"),
                    fp_rate=bucket.get("false_positive_rate", "n/a"),
                    utr=bucket.get("unable_to_reproduce", 0),
                )
            )
        lines.append("")
    if stats.get("note"):
        lines.extend(["## Notes", "", str(stats["note"]), ""])
    return "\n".join(lines)


def save_precision_report_markdown(stats: dict[str, Any], path: str | Path) -> None:
    """Write a Markdown precision report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_precision_report_markdown(stats), encoding="utf-8")


def save_precision_report_csv(stats: dict[str, Any], path: str | Path) -> None:
    """Write rule-level precision metrics as CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "bucket_type",
                "bucket",
                "reviewed",
                "decided",
                "precision",
                "false_positive_rate",
                "confirmation_rate",
                "unable_to_reproduce_rate",
            ],
        )
        writer.writeheader()
        for bucket_type, key in [
            ("rule", "by_rule"),
            ("category", "by_category"),
            ("engine", "by_detection_mode"),
            ("severity", "by_severity"),
            ("site", "by_site"),
        ]:
            for name, bucket in sorted((stats.get(key) or {}).items()):
                writer.writerow(
                    {
                        "bucket_type": bucket_type,
                        "bucket": name,
                        "reviewed": bucket.get("reviewed", 0),
                        "decided": bucket.get("decided", 0),
                        "precision": bucket.get("precision"),
                        "false_positive_rate": bucket.get("false_positive_rate"),
                        "confirmation_rate": bucket.get("confirmation_rate"),
                        "unable_to_reproduce_rate": bucket.get("unable_to_reproduce_rate"),
                    }
                )


def save_verdict_summary_markdown(summary: dict[str, Any], path: str | Path) -> None:
    """Write a reviewer verdict summary."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_verdict_summary_markdown(summary), encoding="utf-8")
