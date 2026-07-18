"""Build structured A11yway reports."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import List

from a11yway import __version__
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.report import AccessibilityReport
from a11yway.models.task import AccessibilityTask
from a11yway.core.ai_scout import build_ai_scout_markdown
from a11yway.core.announce import (
    ANNOUNCE_LIMITATIONS,
    build_announce_transcript,
    trace_has_announce_data,
)
from a11yway.core.extended_results import EXTENDED_RESULT_SCHEMA_VERSION, json_safe
from a11yway.core.finding_validation import issue_cluster_summary, validate_findings
from a11yway.core.page_analyzer import STATIC_CHECKS_RUN
from a11yway.core.rules import enrich_issue_with_rule
from a11yway.core.wcag_coverage import coverage_summary_for_report


REPORT_SCHEMA_VERSION = "1.0"


def _count_by(items: list[str]) -> dict[str, int]:
    """Count string values while keeping the report builder dependency-free."""
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    """Merge count dictionaries in place."""
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


def _format_evidence_for_json(evidence: str | dict) -> dict:
    """Return evidence as a JSON-ready object."""
    if isinstance(evidence, dict):
        return evidence
    return {"description": evidence}


BROWSER_MODE_LIMITATIONS = [
    "Browser mode approximates keyboard interaction but does not simulate a full screen reader.",
    "Accessible names are estimated and require manual review.",
]

TASK_EXECUTION_LIMITATIONS = [
    "Task steps are deterministic scripts; a human may find a workaround the script does not try.",
    "Step results show keyboard operability, not full assistive technology behavior.",
]


def _visual_proof_for_report(visual_proof: dict | None) -> dict | None:
    """Return compact visual proof metadata suitable for JSON reports."""
    if not visual_proof:
        return None
    if visual_proof.get("enabled") is False:
        return {
            "enabled": False,
            "error": visual_proof.get("error"),
        }
    return {
        "enabled": bool(visual_proof.get("enabled")),
        "screenshot_path": visual_proof.get("screenshot_path"),
        "focus_overlay_path": visual_proof.get("focus_overlay_path"),
        "focus_points_count": visual_proof.get(
            "focus_points_count", len(visual_proof.get("focus_points", []))
        ),
        "viewport": visual_proof.get("viewport", {}),
        "limitations": visual_proof.get("limitations", []),
    }


def build_json_report(
    source_file: str,
    issues: list[AccessibilityIssue],
    task: AccessibilityTask | None = None,
    task_blockers: list[dict] | None = None,
    source_metadata: dict | None = None,
    browser_result: dict | None = None,
    task_execution: dict | None = None,
    low_vision_result: dict | None = None,
    ai_scout_result: dict | None = None,
    extended_results: list[dict] | None = None,
) -> dict:
    """Build the prototype JSON report shape for CLI exports."""
    page_url = ""
    if source_metadata:
        page_url = (
            source_metadata.get("final_url")
            or source_metadata.get("source")
            or source_file
        )
    issues = validate_findings(issues, page_url=page_url or source_file)
    normalized_extended_results = sorted(
        [json_safe(result) for result in (extended_results or [])],
        key=lambda result: (
            str(result.get("module", "")),
            str(result.get("check_id", "")),
            str(result.get("status", "")),
        ),
    )
    checks_run = list(STATIC_CHECKS_RUN)
    limitations = [
        "This prototype only runs static HTML checks.",
        "It does not replace a full human accessibility audit.",
        "It does not yet perform browser-based interaction testing.",
    ]
    if browser_result is not None:
        checks_run.extend(browser_result.get("checks_run", []))
        limitations = [
            "This prototype runs static HTML checks plus a basic keyboard interaction audit.",
            "It does not replace a full human accessibility audit.",
            "Browser mode does not simulate a full screen reader, and accessible names are estimated.",
        ]
    if low_vision_result is not None:
        checks_run.extend(low_vision_result.get("checks_run", []))
        if "Low-vision browser checks are conservative heuristics and require manual review." not in limitations:
            limitations.append(
                "Low-vision browser checks are conservative heuristics and require manual review."
            )
    if normalized_extended_results:
        for result in normalized_extended_results:
            check_id = result.get("check_id")
            if check_id:
                checks_run.append(check_id)
        limitations.append(
            "Extended module evidence may include deterministic browser/file metadata and heuristic review points; it is not a certification claim."
        )

    enriched_issues = [
        enrich_issue_with_rule(
            {
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "agent_name": issue.agent_name,
                "message": issue.title,
                "evidence": _format_evidence_for_json(issue.evidence),
                "suggested_fix": issue.suggested_fix,
                **({"confidence": issue.confidence} if issue.confidence else {}),
            }
        )
        for issue in issues
    ]
    raw_occurrences = sum(
        int(issue.evidence.get("occurrence_count", 1) or 1)
        if isinstance(issue.evidence, dict)
        else 1
        for issue in issues
    )
    clusters = issue_cluster_summary(issues)

    report = {
        "tool": "A11yway",
        "version": __version__,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "extended_result_schema_version": EXTENDED_RESULT_SCHEMA_VERSION,
        "source_file": source_file,
        "summary": {
            "issues_found": len(issues),
            "raw_occurrences": raw_occurrences,
            "unique_root_issues": len(clusters),
            "counts_by_severity": _count_by([issue.severity for issue in issues]),
            "counts_by_issue_type": _count_by([issue.issue_type for issue in issues]),
            "counts_by_confidence": _count_by(
                [issue.get("confidence", "") for issue in enriched_issues]
            ),
            "counts_by_confidence_level": _count_by(
                [
                    issue.get("evidence", {}).get("confidence_level", "")
                    for issue in enriched_issues
                    if isinstance(issue.get("evidence"), dict)
                ]
            ),
            "agents_used": ["Keyboard-only student"],
            "checks_run": checks_run,
        },
        "issues": enriched_issues,
        "issue_clusters": clusters,
        "wcag_coverage": coverage_summary_for_report(),
        "limitations": limitations,
    }

    if normalized_extended_results:
        report["extended_modules"] = normalized_extended_results
        report["summary"]["extended_modules"] = [
            {
                "module": result.get("module"),
                "check_id": result.get("check_id"),
                "status": result.get("status"),
                "findings": len(result.get("findings", [])),
            }
            for result in extended_results
        ]

    if task:
        report["task"] = {
            "id": task.id,
            "name": task.name,
            "student_profile": task.student_profile,
            "required_actions": task.required_actions,
            "likely_blockers": task_blockers or [],
        }

    if source_metadata:
        report["source"] = {
            "input": source_metadata.get("source"),
            "type": source_metadata.get("source_type"),
            "final_url": source_metadata.get("final_url"),
            "status_code": source_metadata.get("status_code"),
            "content_type": source_metadata.get("content_type"),
        }

    if browser_result is not None:
        analysis_modes = ["static", "browser"]
        if low_vision_result is not None:
            analysis_modes.append("low_vision")
        report["analysis_modes"] = analysis_modes
        focus_trace = browser_result.get("focus_trace", [])
        browser_limitations = list(BROWSER_MODE_LIMITATIONS)
        report["browser"] = {
            "success": browser_result.get("success", False),
            "error": browser_result.get("error"),
            "final_url": browser_result.get("final_url"),
            "checks_run": browser_result.get("checks_run", []),
            "focus_trace": focus_trace,
            "limitations": browser_limitations,
        }
        if trace_has_announce_data(focus_trace):
            report["browser"]["announce_transcript"] = build_announce_transcript(
                focus_trace
            )
            browser_limitations.extend(ANNOUNCE_LIMITATIONS)
        if browser_result.get("axe") is not None:
            report["browser"]["axe"] = browser_result["axe"]
        visual_proof = _visual_proof_for_report(browser_result.get("visual_proof"))
        if visual_proof is not None:
            report["visual_proof"] = visual_proof

    if low_vision_result is not None:
        if "analysis_modes" not in report:
            report["analysis_modes"] = ["static", "low_vision"]
        report["low_vision"] = {
            "success": low_vision_result.get("success", False),
            "error": low_vision_result.get("error"),
            "checks_run": low_vision_result.get("checks_run", []),
            "contrast_sample_count": len(low_vision_result.get("contrast_samples", [])),
            "zoom_reflow": low_vision_result.get("zoom_reflow", {}),
            "focus_visibility": low_vision_result.get("focus_visibility", {}),
            "limitations": low_vision_result.get("limitations", []),
        }

    if task_execution is not None:
        report["task_execution"] = {
            "task_id": task_execution.get("task_id"),
            "task_name": task_execution.get("task_name"),
            "student_profile": task_execution.get("student_profile"),
            "success": task_execution.get("success", False),
            "error": task_execution.get("error"),
            "completed": task_execution.get("completed", False),
            "blocked_at_step": task_execution.get("blocked_at_step"),
            "blocked_reason": task_execution.get("blocked_reason"),
            "steps_total": task_execution.get("steps_total", 0),
            "steps_passed": task_execution.get("steps_passed", 0),
            "steps": task_execution.get("steps", []),
            "announce_available": task_execution.get("announce_available", False),
            "limitations": list(TASK_EXECUTION_LIMITATIONS),
        }
        if task_execution.get("announce_available"):
            report["task_execution"]["limitations"].extend(ANNOUNCE_LIMITATIONS)
        video = task_execution.get("video") or {}
        if video:
            if "visual_proof" not in report:
                report["visual_proof"] = {"enabled": False}
            if video.get("enabled"):
                report["visual_proof"]["video_path"] = video.get("path")
                report["visual_proof"]["video_caption"] = video.get("caption")
            else:
                report["visual_proof"]["video_error"] = video.get("error")

    if ai_scout_result is not None:
        report["ai_scout"] = ai_scout_result

    return report


def save_json_report(report: dict, output_path: str | Path) -> None:
    """Write a prototype JSON report, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True)


def _format_count_items(counts: dict) -> list[str]:
    """Format report count dictionaries for Markdown output."""
    if not counts:
        return ["- None"]
    return [f"- {key}: {value}" for key, value in counts.items()]


_EVIDENCE_KEYS = [
    "rule_id",
    "issue_category",
    "source_engine",
    "confidence_level",
    "verification_status",
    "deduplication_fingerprint",
    "human_review_reason",
    "occurrence_count",
    "affected_page_count",
    "component_signature",
    "normalized_page_url",
    "element_selector",
    "normalized_element_snippet",
    "accessible_name",
    "visible_text",
    "role",
    "tag",
    "id",
    "name",
    "href",
    "src",
    "text",
    "line",
    "step",
    "detected_in",
    "evidence_sources",
    "merged_finding_count",
    "fingerprint",
    "selector",
    "contrast_ratio",
    "foreground_color",
    "background_color",
    "background_image_in_stack",
    "group_name",
    "option_count",
    "label_text",
    "suggested_token",
    "matched_phrase",
    "visible_label",
    "aria_label",
    "nav_link_count",
    "width",
    "height",
    "bounding_box",
    "nearby_target",
    "covered_points",
    "sampled_points",
    "covering_element",
    "covering_position",
    "detection_method",
    "direction",
    "element",
    "bounding_box_before",
    "bounding_box_after",
    "downgraded_to_review_only",
    "announced_role",
    "announcement",
    "loop_sequence",
    "loop_length",
    "unreached_focusable_count",
    "tab_presses",
    "body_streak",
    "zoom_percent",
    "viewport_width",
    "document_scroll_width",
    "overflow_amount",
    "clipped_by",
    "first_element",
    "second_element",
    "reason",
    "module",
    "check_id",
    "evidence_type",
    "review_status",
    "source",
    "observed",
    "expected",
    "manual_verification",
    "detection_source",
    "deterministic",
    "limitations",
]


def _format_evidence_lines(evidence: dict) -> list[str]:
    """Format structured evidence for Markdown output."""
    lines = []
    for key in _EVIDENCE_KEYS:
        value = evidence.get(key)
        if value not in [None, ""]:
            lines.append(f"- {key}: {value}")

    snippet = evidence.get("snippet")
    if snippet:
        lines.extend(["", "```html", str(snippet), "```"])

    return lines or ["- No structured evidence available."]


def build_markdown_report(report: dict) -> str:
    """Build a readable Markdown report from a JSON-style report dict."""
    summary = report.get("summary", {})
    source = report.get("source", {})
    source_label = source.get("input") or report.get("source_file", "")
    lines = [
        "# A11yway Accessibility Report",
        "",
        "## Summary",
        "",
        f"- Source: {source_label}",
        f"- Source type: {source.get('type', 'file')}",
        f"- Issues found: {summary.get('issues_found', 0)}",
        f"- Raw occurrences: {summary.get('raw_occurrences', summary.get('issues_found', 0))}",
        f"- Unique root issues: {summary.get('unique_root_issues', summary.get('issues_found', 0))}",
        f"- Agents used: {', '.join(summary.get('agents_used', []))}",
        f"- Checks run: {', '.join(summary.get('checks_run', []))}",
        "",
        "### Counts By Severity",
        "",
        *_format_count_items(summary.get("counts_by_severity", {})),
        "",
        "### Counts By Issue Type",
        "",
        *_format_count_items(summary.get("counts_by_issue_type", {})),
        "",
        "### Counts By Confidence",
        "",
        *_format_count_items(summary.get("counts_by_confidence", {})),
        "",
        "### Counts By Confidence Level",
        "",
        *_format_count_items(summary.get("counts_by_confidence_level", {})),
        "",
    ]
    clusters = report.get("issue_clusters", [])
    if clusters:
        lines.extend(
            [
                "### Root Issue Clusters",
                "",
                "| Root issue | Rule | Component | Occurrences | Confidence |",
                "| --- | --- | --- | ---: | --- |",
            ]
        )
        for cluster in clusters[:10]:
            lines.append(
                "| {root} | {rule} | {component} | {occurrences} | {confidence} |".format(
                    root=cluster.get("root_issue_id", ""),
                    rule=cluster.get("rule_id", ""),
                    component=cluster.get("component_signature", ""),
                    occurrences=cluster.get("occurrence_count", 0),
                    confidence=cluster.get("confidence_level", ""),
                )
            )
        if len(clusters) > 10:
            lines.append(f"| ... | {len(clusters) - 10} more |  |  |  |")
        lines.append("")
    if summary.get("review_only_rules"):
        lines.extend(
            [
                "### Rules Downgraded To Review-Only",
                "",
                "These rules still ran, but their findings carry needs_review "
                "confidence in this report per configuration:",
                "",
                *[f"- {rule}" for rule in summary["review_only_rules"]],
                "",
            ]
        )
    if source.get("final_url") or source.get("status_code"):
        lines.extend(
            [
                "### Source Metadata",
                "",
                f"- Final URL: {source.get('final_url') or ''}",
                f"- Status code: {source.get('status_code') or ''}",
                f"- Content type: {source.get('content_type') or ''}",
                "",
            ]
        )

    browser = report.get("browser")
    if browser is not None:
        trace = browser.get("focus_trace", [])
        lines.extend(
            [
                "## Browser Mode Summary",
                "",
                f"- Analysis modes: {', '.join(report.get('analysis_modes', []))}",
                f"- Browser audit success: {str(browser.get('success', False)).lower()}",
            ]
        )
        if browser.get("error"):
            lines.append(f"- Error: {browser['error']}")
        lines.extend(
            [
                f"- Checks run: {', '.join(browser.get('checks_run', []))}",
                f"- Focus trace length: {len(trace)}",
                "",
            ]
        )
        if trace:
            lines.extend(
                [
                    "## Browser Interaction Trace",
                    "",
                    "| Step | Tag | Accessible name guess | ID/Name | Text/Href |",
                    "| ---: | --- | --- | --- | --- |",
                ]
            )
            for entry in trace[:20]:
                lines.append(
                    "| {step} | {tag} | {name_guess} | {id_name} | {text_href} |".format(
                        step=entry.get("step", ""),
                        tag=entry.get("tag", ""),
                        name_guess=entry.get("accessible_name_guess", ""),
                        id_name=entry.get("id") or entry.get("name") or "",
                        text_href=entry.get("text") or entry.get("href") or "",
                    )
                )
            if len(trace) > 20:
                lines.extend(
                    ["", f"Trace truncated: showing the first 20 of {len(trace)} steps."]
                )
            lines.append("")
        transcript = browser.get("announce_transcript", [])
        if transcript:
            lines.extend(
                [
                    "## Announce Transcript",
                    "",
                    "What Chromium's computed accessibility tree exposes at each "
                    "observed focus stop. This approximates what a screen reader "
                    "would announce; real screen readers can differ.",
                    "",
                ]
            )
            for entry in transcript:
                marker = " <- finding: unnamed focus stop" if entry.get("unnamed") else ""
                lines.append(f"{entry.get('step')}. {entry.get('announcement')}{marker}")
            lines.append("")
        axe = browser.get("axe")
        if axe is not None:
            lines.extend(
                [
                    "### Axe-core Scan",
                    "",
                    f"- Scan success: {str(axe.get('success', False)).lower()}",
                ]
            )
            if axe.get("error"):
                lines.append(f"- Error: {axe['error']}")
            if axe.get("axe_version"):
                lines.append(f"- axe-core version: {axe['axe_version']}")
            lines.extend(
                [
                    f"- Rules violated: {axe.get('violation_rule_count', 0)}",
                    f"- Findings reported: {axe.get('issue_count', 0)}",
                    "",
                ]
            )
            violations = axe.get("violations", [])
            if violations:
                lines.extend(
                    [
                        "| Rule | Impact | Elements | Help |",
                        "| --- | --- | ---: | --- |",
                    ]
                )
                for violation in violations:
                    lines.append(
                        "| {rule} | {impact} | {nodes} | {help} |".format(
                            rule=violation.get("rule", ""),
                            impact=violation.get("impact", ""),
                            nodes=violation.get("node_count", 0),
                            help=violation.get("help", ""),
                        )
                    )
                lines.append("")
        if browser.get("limitations"):
            lines.extend(["### Browser Limitations", ""])
            lines.extend(f"- {limitation}" for limitation in browser["limitations"])
            lines.append("")

    low_vision = report.get("low_vision")
    if low_vision is not None:
        zoom = low_vision.get("zoom_reflow", {})
        focus = low_vision.get("focus_visibility", {})
        lines.extend(
            [
                "## Low-Vision Checks",
                "",
                f"- Status: {'passed' if low_vision.get('success') else 'failed'}",
                f"- Checks run: {', '.join(low_vision.get('checks_run', []))}",
                f"- Contrast samples analyzed: {low_vision.get('contrast_sample_count', 0)}",
                f"- Viewport width for reflow check: {zoom.get('viewport_width', '')}",
                f"- Document scroll width: {zoom.get('document_scroll_width', '')}",
                f"- Horizontal overflow amount: {zoom.get('overflow_amount', '')}",
                f"- Focus stops checked: {focus.get('checked_count', 0)}",
                f"- Focus indicator concerns: {focus.get('flagged_count', 0)}",
                "",
            ]
        )
        zoom_levels = zoom.get("levels", [])
        if zoom_levels:
            lines.extend(
                [
                    "### Zoom Reflow Levels",
                    "",
                    "| Zoom | Viewport width | Scroll width | Overflow | Clipped | Overlaps |",
                    "| ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for level in zoom_levels:
                lines.append(
                    "| {zoom}% | {viewport} | {scroll} | {overflow} | {clipped} | {overlaps} |".format(
                        zoom=level.get("zoom_percent", ""),
                        viewport=level.get("viewport_width", ""),
                        scroll=level.get("document_scroll_width", ""),
                        overflow=level.get("overflow_amount", ""),
                        clipped=len(level.get("clipped_elements", [])),
                        overlaps=len(level.get("overlapping_pairs", [])),
                    )
                )
            lines.append("")
        if low_vision.get("error"):
            lines.extend([f"- Error: {low_vision['error']}", ""])
        if low_vision.get("limitations"):
            lines.extend(["### Low-Vision Limitations", ""])
            lines.extend(f"- {limitation}" for limitation in low_vision["limitations"])
            lines.append("")

    visual_proof = report.get("visual_proof")
    if visual_proof is not None:
        lines.extend(["## Visual Proof", ""])
        if visual_proof.get("enabled"):
            lines.extend(
                [
                    f"- Screenshot path: {visual_proof.get('screenshot_path', '')}",
                    f"- Focus path overlay path: {visual_proof.get('focus_overlay_path', '')}",
                    f"- Focus points count: {visual_proof.get('focus_points_count', 0)}",
                    "",
                ]
            )
            for limitation in visual_proof.get("limitations", []):
                lines.append(f"- {limitation}")
            lines.append("")
        else:
            lines.extend(
                [
                    f"- Visual proof unavailable: {visual_proof.get('error', '')}",
                    "",
                ]
            )
        if visual_proof.get("video_path"):
            lines.extend(
                [
                    f"- Task execution video: {visual_proof['video_path']}",
                    f"- Video caption: {visual_proof.get('video_caption', '')}",
                    "",
                ]
            )
        elif visual_proof.get("video_error"):
            lines.extend(
                [
                    f"- Task execution video unavailable: {visual_proof['video_error']}",
                    "",
                ]
            )

    extended_modules = report.get("extended_modules", [])
    if extended_modules:
        lines.extend(["## Extended Accessibility Modules", ""])
        for module in extended_modules:
            namespace = module.get("namespace", "")
            title = (
                "Passive Security Observations"
                if namespace == "security"
                else str(module.get("module", "")).replace("_", " ").title()
            )
            lines.extend(
                [
                    f"### {title}",
                    "",
                    f"- Check: {module.get('check_id', '')}",
                    f"- Status: {module.get('status', '')}",
                    f"- Findings: {len(module.get('findings', []))}",
                ]
            )
            if module.get("notice"):
                lines.append(f"- Notice: {module['notice']}")
            artifacts = module.get("artifacts", {})
            if artifacts:
                lines.append(
                    f"- Artifacts: {json.dumps(artifacts, ensure_ascii=False)[:500]}"
                )
            limitations = module.get("limitations", [])
            if limitations:
                lines.append("- Limitations:")
                lines.extend(f"  - {limitation}" for limitation in limitations)
            lines.append("")

    execution = report.get("task_execution")
    if execution is not None:
        lines.extend(["## Task Execution", ""])
        if not execution.get("success"):
            lines.extend(
                [
                    f"- Task: {execution.get('task_name', '')}",
                    f"- Result: could not run ({execution.get('error', '')})",
                    "",
                ]
            )
        else:
            if execution.get("completed"):
                verdict = "COMPLETED with keyboard-only interaction"
            else:
                verdict = f"BLOCKED at step `{execution.get('blocked_at_step', '')}`"
                if execution.get("blocked_reason"):
                    verdict += f" (reason: {execution['blocked_reason']})"
            lines.extend(
                [
                    f"- Task: {execution.get('task_name', '')}",
                    f"- Student profile: {execution.get('student_profile', '')}",
                    f"- Result: {verdict}",
                    f"- Steps passed: {execution.get('steps_passed', 0)} of {execution.get('steps_total', 0)}",
                    "",
                    "| Step | Action | Status | Announced | Detail |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for step in execution.get("steps", []):
                status = step.get("status", "")
                if step.get("used_fallback"):
                    status += " (fallback)"
                lines.append(
                    "| {id} | {action} | {status} | {announced} | {detail} |".format(
                        id=step.get("id", ""),
                        action=step.get("action", ""),
                        status=status,
                        announced=step.get("announced") or "",
                        detail=step.get("detail", ""),
                    )
                )
            lines.append("")
        if execution.get("limitations"):
            lines.extend(["### Task Execution Limitations", ""])
            lines.extend(f"- {limitation}" for limitation in execution["limitations"])
            lines.append("")

    task = report.get("task")
    if task:
        lines.extend(
            [
                "## Task Context",
                "",
                f"- Task name: {task.get('name', '')}",
                f"- Student profile: {task.get('student_profile', '')}",
                "",
                "### Required Actions",
                "",
            ]
        )
        lines.extend(f"- {action}" for action in task.get("required_actions", []))
        lines.extend(["", "### Likely Blockers", ""])
        blockers = task.get("likely_blockers", [])
        if blockers:
            for blocker in blockers:
                lines.extend(
                    [
                        f"- {blocker.get('message', '')}",
                        f"  - Issue type: {blocker.get('issue_type', '')}",
                        f"  - Severity: {blocker.get('severity', '')}",
                        f"  - Task impact: {blocker.get('task_impact', '')}",
                    ]
                )
        else:
            lines.append("- None found for this task.")
        lines.append("")

    ai_scout = report.get("ai_scout")
    if ai_scout is not None:
        lines.extend([build_ai_scout_markdown(ai_scout), ""])

    lines.extend(["## Issues Found", ""])
    issues = report.get("issues", [])
    if not issues:
        lines.append("No issues found by the current static checks.")
    for index, issue in enumerate(issues, start=1):
        rule = issue.get("rule", {})
        lines.extend(
            [
                f"### {index}. {issue.get('message', '')}",
                "",
                f"- Issue type: {issue.get('issue_type', '')}",
            ]
        )
        if rule.get("title"):
            lines.append(f"- Rule: {rule['title']}")
        if rule.get("category"):
            lines.append(f"- Category: {rule['category']}")
        lines.append(f"- Severity: {issue.get('severity', '')}")
        if issue.get("confidence"):
            lines.append(f"- Confidence: {issue['confidence']}")
        for mapping in issue.get("wcag", []) or []:
            lines.append(
                f"- Related to WCAG 2.2 SC {mapping.get('sc')} "
                f"{mapping.get('name')} (Level {mapping.get('level')}, "
                f"coverage: {mapping.get('coverage')})"
            )
            if mapping.get("manual_check"):
                lines.append(f"  - Manual check: {mapping['manual_check']}")
        if rule.get("why_it_matters"):
            lines.append(f"- Why it matters: {rule['why_it_matters']}")
        lines.append(f"- Suggested fix: {issue.get('suggested_fix', '')}")
        if rule.get("manual_review_notes"):
            lines.append(f"- Manual review: {rule['manual_review_notes']}")
        if rule.get("static_check_limitations"):
            lines.append(f"- Static check limitation: {rule['static_check_limitations']}")
        if rule.get("browser_check_limitations"):
            lines.append(f"- Browser check limitation: {rule['browser_check_limitations']}")
        lines.extend(["", "Evidence:", ""])
        lines.extend(_format_evidence_lines(issue.get("evidence", {})))
        lines.append("")

    coverage = report.get("wcag_coverage")
    if coverage:
        counts = coverage.get("counts", {})
        lines.extend(
            [
                "## WCAG 2.2 Coverage Snapshot",
                "",
                "How A11yway's checks relate to the "
                f"{coverage.get('total_criteria', 86)} WCAG "
                f"{coverage.get('wcag_version', '2.2')} Success Criteria. "
                "This describes tool coverage, not the conformance of the "
                "audited page.",
                "",
                f"- Direct native coverage: {counts.get('direct', 0)}",
                f"- Partial native coverage: {counts.get('partial', 0)}",
                f"- Supporting evidence only: {counts.get('supporting_evidence', 0)}",
                f"- Covered only through the optional axe-core scan: {counts.get('axe_only', 0)}",
                f"- Manual review only: {counts.get('manual_only', 0)}",
                f"- Unsupported: {counts.get('unsupported', 0)}",
                "",
                f"{coverage.get('note', '')}",
                "",
            ]
        )

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_markdown_report(report: dict, output_path: str | Path) -> None:
    """Write a Markdown report, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown_report(report), encoding="utf-8")


def _html_list(items: list[str]) -> str:
    """Render a simple HTML list."""
    if not items:
        return "<p>None.</p>"
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"


def _html_count_list(counts: dict) -> str:
    """Render count dictionaries as an HTML list."""
    if not counts:
        return "<p>None.</p>"
    return "<ul>" + "".join(
        f"<li><code>{escape(str(key))}</code>: {value}</li>"
        for key, value in counts.items()
    ) + "</ul>"


def _html_evidence(evidence: dict) -> str:
    """Render structured evidence for the HTML report."""
    rows = []
    for key in _EVIDENCE_KEYS:
        value = evidence.get(key)
        if value not in [None, ""]:
            rows.append(
                f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
            )
    table = ""
    if rows:
        table = "<table><tbody>" + "".join(rows) + "</tbody></table>"

    snippet = evidence.get("snippet")
    if snippet:
        table += f"<pre><code>{escape(str(snippet))}</code></pre>"
    return table or "<p>No structured evidence available.</p>"


def build_html_report(report: dict) -> str:
    """Build a self-contained HTML report from a JSON-style report dict."""
    summary = report.get("summary", {})
    source = report.get("source", {})
    source_label = source.get("input") or report.get("source_file", "")
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>A11yway Accessibility Report</title>",
        "<style>",
        "body { margin: 0; font-family: system-ui, sans-serif; line-height: 1.5; color: #172033; background: #f6f8fb; }",
        "header, main { max-width: 1120px; margin: 0 auto; padding: 1.25rem; }",
        "header { background: #ffffff; border-bottom: 1px solid #d8deea; }",
        "section { margin: 1rem 0; padding: 1rem; background: #ffffff; border: 1px solid #d8deea; }",
        "h1, h2, h3 { line-height: 1.2; }",
        "table { border-collapse: collapse; width: 100%; margin: 0.75rem 0; }",
        "th, td { border: 1px solid #d8deea; padding: 0.45rem 0.55rem; text-align: left; vertical-align: top; }",
        "th { background: #eef2f7; }",
        "code, pre { background: #eef2f7; }",
        "pre { overflow-x: auto; padding: 0.75rem; }",
        ".meta { color: #526071; }",
        ".issue { border-top: 4px solid #5067a3; }",
        ".high { border-top-color: #b42318; }",
        ".medium { border-top-color: #b86e00; }",
        ".low { border-top-color: #367a45; }",
        ".announce-unnamed { color: #b42318; font-weight: 600; }",
        ".security-observations { border-left: 4px solid #7a2f00; padding-left: 0.75rem; background: #fff8f0; }",
        "</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>A11yway Accessibility Report</h1>",
        f'<p class="meta">Source: {escape(str(source_label))}</p>',
        "</header>",
        "<main>",
        "<section>",
        "<h2>Summary</h2>",
        f"<p>Issues found: <strong>{summary.get('issues_found', 0)}</strong></p>",
        f"<p>Raw occurrences: <strong>{summary.get('raw_occurrences', summary.get('issues_found', 0))}</strong></p>",
        f"<p>Unique root issues: <strong>{summary.get('unique_root_issues', summary.get('issues_found', 0))}</strong></p>",
        f"<p>Agents used: {escape(', '.join(summary.get('agents_used', [])))}</p>",
        f"<p>Checks run: {escape(', '.join(summary.get('checks_run', [])))}</p>",
        "<h3>Counts By Severity</h3>",
        _html_count_list(summary.get("counts_by_severity", {})),
        "<h3>Counts By Issue Type</h3>",
        _html_count_list(summary.get("counts_by_issue_type", {})),
        "<h3>Counts By Confidence Level</h3>",
        _html_count_list(summary.get("counts_by_confidence_level", {})),
        "</section>",
    ]

    clusters = report.get("issue_clusters", [])
    if clusters:
        lines.extend(
            [
                "<section>",
                "<h2>Root Issue Clusters</h2>",
                "<table><thead><tr><th>Root issue</th><th>Rule</th><th>Component</th><th>Occurrences</th><th>Confidence</th></tr></thead><tbody>",
            ]
        )
        for cluster in clusters[:20]:
            lines.append(
                "<tr><td>{root}</td><td>{rule}</td><td>{component}</td><td>{occurrences}</td><td>{confidence}</td></tr>".format(
                    root=escape(str(cluster.get("root_issue_id", ""))),
                    rule=escape(str(cluster.get("rule_id", ""))),
                    component=escape(str(cluster.get("component_signature", ""))),
                    occurrences=escape(str(cluster.get("occurrence_count", 0))),
                    confidence=escape(str(cluster.get("confidence_level", ""))),
                )
            )
        lines.extend(["</tbody></table>", "</section>"])

    if source:
        lines.extend(
            [
                "<section>",
                "<h2>Source Metadata</h2>",
                "<table><tbody>",
                f"<tr><th>Input</th><td>{escape(str(source.get('input') or ''))}</td></tr>",
                f"<tr><th>Type</th><td>{escape(str(source.get('type') or ''))}</td></tr>",
                f"<tr><th>Final URL</th><td>{escape(str(source.get('final_url') or ''))}</td></tr>",
                f"<tr><th>Status code</th><td>{escape(str(source.get('status_code') or ''))}</td></tr>",
                f"<tr><th>Content type</th><td>{escape(str(source.get('content_type') or ''))}</td></tr>",
                "</tbody></table>",
                "</section>",
            ]
        )

    if report.get("analysis_modes"):
        lines.extend(
            [
                "<section>",
                "<h2>Analysis Modes</h2>",
                _html_list(report.get("analysis_modes", [])),
                "</section>",
            ]
        )

    task = report.get("task")
    if task:
        lines.extend(
            [
                "<section>",
                "<h2>Task Context</h2>",
                f"<p>Task name: {escape(str(task.get('name', '')))}</p>",
                f"<p>Student profile: {escape(str(task.get('student_profile', '')))}</p>",
                "<h3>Required Actions</h3>",
                _html_list(task.get("required_actions", [])),
                "<h3>Likely Blockers</h3>",
            ]
        )
        blockers = task.get("likely_blockers", [])
        if blockers:
            lines.append("<ul>")
            for blocker in blockers:
                lines.append(
                    "<li>{message} <span class=\"meta\">({issue_type}, {severity})</span><br>{impact}</li>".format(
                        message=escape(str(blocker.get("message", ""))),
                        issue_type=escape(str(blocker.get("issue_type", ""))),
                        severity=escape(str(blocker.get("severity", ""))),
                        impact=escape(str(blocker.get("task_impact", ""))),
                    )
                )
            lines.append("</ul>")
        else:
            lines.append("<p>None found for this task.</p>")
        lines.append("</section>")

    extended_modules = report.get("extended_modules", [])
    if extended_modules:
        lines.extend(["<section>", "<h2>Extended Accessibility Modules</h2>"])
        for module in extended_modules:
            namespace = module.get("namespace", "")
            css_class = ' class="security-observations"' if namespace == "security" else ""
            title = (
                "Passive Security Observations"
                if namespace == "security"
                else str(module.get("module", "")).replace("_", " ").title()
            )
            lines.extend(
                [
                    f"<article{css_class}>",
                    f"<h3>{escape(title)}</h3>",
                    f"<p><strong>Check:</strong> {escape(str(module.get('check_id', '')))}</p>",
                    f"<p><strong>Status:</strong> {escape(str(module.get('status', '')))}</p>",
                    f"<p><strong>Findings:</strong> {len(module.get('findings', []))}</p>",
                ]
            )
            if module.get("notice"):
                lines.append(f"<p><strong>Notice:</strong> {escape(str(module['notice']))}</p>")
            limitations = module.get("limitations", [])
            if limitations:
                lines.append("<h4>Limitations</h4>")
                lines.append(_html_list([str(item) for item in limitations]))
            lines.append("</article>")
        lines.append("</section>")

    execution = report.get("task_execution")
    if execution is not None:
        lines.extend(["<section>", "<h2>Task Execution</h2>"])
        if not execution.get("success"):
            lines.append(
                f"<p>Result: could not run ({escape(str(execution.get('error', '')))}).</p>"
            )
        else:
            verdict = (
                "COMPLETED with keyboard-only interaction"
                if execution.get("completed")
                else f"BLOCKED at step {execution.get('blocked_at_step', '')}"
            )
            if not execution.get("completed") and execution.get("blocked_reason"):
                verdict += f" (reason: {execution['blocked_reason']})"
            lines.extend(
                [
                    f"<p>Task: {escape(str(execution.get('task_name', '')))}</p>",
                    f"<p>Deterministic task execution result: <strong>{escape(verdict)}</strong></p>",
                    f"<p>Steps passed: {execution.get('steps_passed', 0)} of {execution.get('steps_total', 0)}</p>",
                    "<table><thead><tr><th>Step</th><th>Action</th><th>Status</th><th>Announced</th><th>Detail</th></tr></thead><tbody>",
                ]
            )
            for step in execution.get("steps", []):
                status = step.get("status", "")
                if step.get("used_fallback"):
                    status += " (fallback)"
                lines.append(
                    "<tr><td>{id}</td><td>{action}</td><td>{status}</td><td>{announced}</td><td>{detail}</td></tr>".format(
                        id=escape(str(step.get("id", ""))),
                        action=escape(str(step.get("action", ""))),
                        status=escape(str(status)),
                        announced=escape(str(step.get("announced") or "")),
                        detail=escape(str(step.get("detail", ""))),
                    )
                )
            lines.append("</tbody></table>")
        lines.append(_html_list(execution.get("limitations", [])))
        lines.append("</section>")

    browser = report.get("browser")
    if browser is not None:
        trace = browser.get("focus_trace", [])
        lines.extend(
            [
                "<section>",
                "<h2>Browser Interaction Trace</h2>",
                f"<p>Browser audit success: {escape(str(browser.get('success', False)).lower())}</p>",
            ]
        )
        if browser.get("error"):
            lines.append(f"<p>Error: {escape(str(browser['error']))}</p>")
        lines.append(f"<p>Focus trace length: {len(trace)}</p>")
        if trace:
            lines.append(
                "<table><thead><tr><th>Step</th><th>Tag</th><th>Accessible name guess</th><th>ID/Name</th><th>Text/Href</th></tr></thead><tbody>"
            )
            for entry in trace[:20]:
                lines.append(
                    "<tr><td>{step}</td><td>{tag}</td><td>{name}</td><td>{id_name}</td><td>{text_href}</td></tr>".format(
                        step=escape(str(entry.get("step", ""))),
                        tag=escape(str(entry.get("tag", ""))),
                        name=escape(str(entry.get("accessible_name_guess", ""))),
                        id_name=escape(str(entry.get("id") or entry.get("name") or "")),
                        text_href=escape(str(entry.get("text") or entry.get("href") or "")),
                    )
                )
            lines.append("</tbody></table>")
        transcript = browser.get("announce_transcript", [])
        if transcript:
            lines.extend(
                [
                    "<h3>Announce Transcript</h3>",
                    "<p>What Chromium's computed accessibility tree exposes at each "
                    "observed focus stop. This approximates what a screen reader "
                    "would announce; real screen readers can differ.</p>",
                    "<ol>",
                ]
            )
            for entry in transcript:
                announcement = escape(str(entry.get("announcement", "")))
                if entry.get("unnamed"):
                    lines.append(
                        f'<li class="announce-unnamed">{announcement} '
                        "(finding: unnamed focus stop)</li>"
                    )
                else:
                    lines.append(f"<li>{announcement}</li>")
            lines.append("</ol>")
        axe = browser.get("axe")
        if axe is not None:
            lines.extend(
                [
                    "<h3>Axe-core Scan</h3>",
                    f"<p>Scan success: {escape(str(axe.get('success', False)).lower())}</p>",
                ]
            )
            if axe.get("error"):
                lines.append(f"<p>Error: {escape(str(axe['error']))}</p>")
            lines.append(
                "<p>Rules violated: {rules}. Findings reported: {findings}.</p>".format(
                    rules=escape(str(axe.get("violation_rule_count", 0))),
                    findings=escape(str(axe.get("issue_count", 0))),
                )
            )
            violations = axe.get("violations", [])
            if violations:
                lines.append(
                    "<table><thead><tr><th>Rule</th><th>Impact</th><th>Elements</th><th>Help</th></tr></thead><tbody>"
                )
                for violation in violations:
                    lines.append(
                        "<tr><td>{rule}</td><td>{impact}</td><td>{nodes}</td><td>{help}</td></tr>".format(
                            rule=escape(str(violation.get("rule", ""))),
                            impact=escape(str(violation.get("impact", ""))),
                            nodes=escape(str(violation.get("node_count", 0))),
                            help=escape(str(violation.get("help", ""))),
                        )
                    )
                lines.append("</tbody></table>")
        lines.append(_html_list(browser.get("limitations", [])))
        lines.append("</section>")

    low_vision = report.get("low_vision")
    if low_vision is not None:
        zoom = low_vision.get("zoom_reflow", {})
        focus = low_vision.get("focus_visibility", {})
        lines.extend(
            [
                "<section>",
                "<h2>Low-Vision Checks</h2>",
                f"<p>Status: {escape('passed' if low_vision.get('success') else 'failed')}</p>",
                f"<p>Checks run: {escape(', '.join(low_vision.get('checks_run', [])))}</p>",
                f"<p>Contrast samples analyzed: {low_vision.get('contrast_sample_count', 0)}</p>",
                "<table><tbody>",
                f"<tr><th>Viewport width</th><td>{escape(str(zoom.get('viewport_width', '')))}</td></tr>",
                f"<tr><th>Document scroll width</th><td>{escape(str(zoom.get('document_scroll_width', '')))}</td></tr>",
                f"<tr><th>Horizontal overflow amount</th><td>{escape(str(zoom.get('overflow_amount', '')))}</td></tr>",
                f"<tr><th>Focus stops checked</th><td>{escape(str(focus.get('checked_count', 0)))}</td></tr>",
                f"<tr><th>Focus indicator concerns</th><td>{escape(str(focus.get('flagged_count', 0)))}</td></tr>",
                "</tbody></table>",
            ]
        )
        zoom_levels = zoom.get("levels", [])
        if zoom_levels:
            lines.extend(
                [
                    "<h3>Zoom Reflow Levels</h3>",
                    "<table><thead><tr><th>Zoom</th><th>Viewport width</th><th>Scroll width</th><th>Overflow</th><th>Clipped</th><th>Overlaps</th></tr></thead><tbody>",
                ]
            )
            for level in zoom_levels:
                lines.append(
                    "<tr><td>{zoom}%</td><td>{viewport}</td><td>{scroll}</td><td>{overflow}</td><td>{clipped}</td><td>{overlaps}</td></tr>".format(
                        zoom=escape(str(level.get("zoom_percent", ""))),
                        viewport=escape(str(level.get("viewport_width", ""))),
                        scroll=escape(str(level.get("document_scroll_width", ""))),
                        overflow=escape(str(level.get("overflow_amount", ""))),
                        clipped=len(level.get("clipped_elements", [])),
                        overlaps=len(level.get("overlapping_pairs", [])),
                    )
                )
            lines.append("</tbody></table>")
        if low_vision.get("error"):
            lines.append(f"<p>Error: {escape(str(low_vision['error']))}</p>")
        lines.append(_html_list(low_vision.get("limitations", [])))
        lines.append("</section>")

    visual_proof = report.get("visual_proof")
    if visual_proof is not None:
        lines.extend(["<section>", "<h2>Visual Proof</h2>"])
        if visual_proof.get("enabled"):
            screenshot = visual_proof.get("screenshot_path", "")
            overlay = visual_proof.get("focus_overlay_path", "")
            lines.extend(
                [
                    "<p>Visual proof is an evidence aid for manual review. It is not accessibility certification.</p>",
                    f'<p>Screenshot: <a href="{escape(str(screenshot), quote=True)}">{escape(str(screenshot))}</a></p>',
                    f'<p>Observed focus path overlay: <a href="{escape(str(overlay), quote=True)}">{escape(str(overlay))}</a></p>',
                    f"<p>Focus points count: {visual_proof.get('focus_points_count', 0)}</p>",
                    _html_list(visual_proof.get("limitations", [])),
                ]
            )
        else:
            lines.append(
                f"<p>Visual proof unavailable: {escape(str(visual_proof.get('error', '')))}</p>"
            )
        if visual_proof.get("video_path"):
            video_path = str(visual_proof["video_path"])
            lines.extend(
                [
                    "<h3>Task Execution Video</h3>",
                    f'<p><a href="{escape(video_path, quote=True)}">{escape(video_path)}</a></p>',
                    f'<p class="meta">{escape(str(visual_proof.get("video_caption", "")))}</p>',
                ]
            )
        elif visual_proof.get("video_error"):
            lines.append(
                f"<p>Task execution video unavailable: {escape(str(visual_proof['video_error']))}</p>"
            )
        lines.append("</section>")

    ai_scout = report.get("ai_scout")
    if ai_scout is not None:
        lines.extend(
            [
                "<section>",
                "<h2>What the AI Found</h2>",
                f"<p>Status: {escape(str(ai_scout.get('status', '')))}</p>",
                f"<p>Mode: {escape(str(ai_scout.get('mode', 'suggest_only')))}</p>",
                f"<p>Model: {escape(str(ai_scout.get('model', '')))}</p>",
            ]
        )
        if ai_scout.get("status") != "ok":
            reason = ai_scout.get("reason") or ai_scout.get("summary") or "unknown reason"
            lines.append(
                "<p>AI Scout was enabled, but no AI summary was produced because: "
                f"{escape(str(reason))}. No AI findings should be inferred from this run.</p>"
            )
        else:
            if ai_scout.get("summary"):
                lines.append(f"<p>{escape(str(ai_scout['summary']))}</p>")
            observations = ai_scout.get("ai_suggested_observations", [])
            if observations:
                lines.append("<ol>")
                for item in observations:
                    lines.append(
                        "<li>"
                        f"<strong>AI-suggested observation:</strong> {escape(str(item.get('observation', '')))}<br>"
                        f"<strong>Related evidence, if any:</strong> {escape(str(item.get('related_deterministic_evidence', '')))}<br>"
                        f"<strong>Human review needed:</strong> {escape(str(item.get('human_review_needed', True)).lower())}<br>"
                        f"<strong>Confidence:</strong> {escape(str(item.get('confidence', 'unclear')))}"
                        "</li>"
                    )
                lines.append("</ol>")
            else:
                lines.append("<p>AI Scout did not return specific observations.</p>")
        lines.append(_html_list(ai_scout.get("limitations", [])))
        lines.append("</section>")

    lines.extend(["<section>", "<h2>Issues Found</h2>"])
    issues = report.get("issues", [])
    if not issues:
        lines.append("<p>No issues found by the current checks.</p>")
    for index, issue in enumerate(issues, start=1):
        rule = issue.get("rule", {})
        severity = issue.get("severity", "")
        lines.extend(
            [
                f'<article class="issue {escape(str(severity))}">',
                f"<h3>{index}. {escape(str(issue.get('message', '')))}</h3>",
                f"<p>Issue type: <code>{escape(str(issue.get('issue_type', '')))}</code></p>",
                f"<p>Severity: {escape(str(severity))}</p>",
            ]
        )
        if issue.get("confidence"):
            lines.append(f"<p>Confidence: {escape(str(issue['confidence']))}</p>")
        wcag_mappings = issue.get("wcag", []) or []
        if wcag_mappings:
            lines.append("<p>Related WCAG 2.2 Success Criteria (not a conformance claim):</p><ul>")
            for mapping in wcag_mappings:
                lines.append(
                    "<li>SC {sc} {name} (Level {level}, coverage: {coverage})"
                    "<br><span class=\"meta\">Manual check: {manual}</span></li>".format(
                        sc=escape(str(mapping.get("sc", ""))),
                        name=escape(str(mapping.get("name", ""))),
                        level=escape(str(mapping.get("level", ""))),
                        coverage=escape(str(mapping.get("coverage", ""))),
                        manual=escape(str(mapping.get("manual_check", ""))),
                    )
                )
            lines.append("</ul>")
        if rule.get("title"):
            lines.append(f"<p>Rule: {escape(str(rule['title']))}</p>")
        if rule.get("why_it_matters"):
            lines.append(f"<p>Why it matters: {escape(str(rule['why_it_matters']))}</p>")
        if issue.get("suggested_fix"):
            lines.append(f"<p>Suggested fix: {escape(str(issue['suggested_fix']))}</p>")
        lines.append("<h4>Evidence</h4>")
        lines.append(_html_evidence(issue.get("evidence", {})))
        lines.append("</article>")
    lines.append("</section>")

    coverage = report.get("wcag_coverage")
    if coverage:
        counts = coverage.get("counts", {})
        lines.extend(
            [
                "<section>",
                "<h2>WCAG 2.2 Coverage Snapshot</h2>",
                "<p>How A11yway's checks relate to the "
                f"{coverage.get('total_criteria', 86)} WCAG "
                f"{escape(str(coverage.get('wcag_version', '2.2')))} Success "
                "Criteria. This describes tool coverage, not the conformance "
                "of the audited page.</p>",
                "<ul>",
                f"<li>Direct native coverage: {counts.get('direct', 0)}</li>",
                f"<li>Partial native coverage: {counts.get('partial', 0)}</li>",
                f"<li>Supporting evidence only: {counts.get('supporting_evidence', 0)}</li>",
                f"<li>Covered only through the optional axe-core scan: {counts.get('axe_only', 0)}</li>",
                f"<li>Manual review only: {counts.get('manual_only', 0)}</li>",
                f"<li>Unsupported: {counts.get('unsupported', 0)}</li>",
                "</ul>",
                f"<p class=\"meta\">{escape(str(coverage.get('note', '')))}</p>",
                "</section>",
            ]
        )

    lines.extend(
        [
            "<section>",
            "<h2>Limitations</h2>",
            _html_list(report.get("limitations", [])),
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(lines)


def save_html_report(report: dict, output_path: str | Path) -> None:
    """Write a self-contained HTML report, creating parent directories."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_html_report(report), encoding="utf-8")


def build_batch_index_report(items: list[dict]) -> dict:
    """Build a JSON-ready index for a batch audit run."""
    counts_by_severity: dict[str, int] = {}
    counts_by_issue_type: dict[str, int] = {}

    for item in items:
        merge_counts(counts_by_severity, item.get("counts_by_severity", {}))
        merge_counts(counts_by_issue_type, item.get("counts_by_issue_type", {}))

    successful_pages = sum(1 for item in items if item.get("status") == "passed")
    analysis_modes = ["static"]
    if any("browser" in item.get("analysis_modes", []) for item in items):
        analysis_modes = ["static", "browser"]
    if any("low_vision" in item.get("analysis_modes", []) for item in items):
        analysis_modes = [mode for mode in ["static", "browser", "low_vision"] if mode == "static" or any(mode in item.get("analysis_modes", []) for item in items)]
    executed = [item for item in items if item.get("task_execution_status")]
    html_reports = [item for item in items if item.get("reports", {}).get("html")]
    ai_scout_items = [item for item in items if item.get("ai_scout_status")]

    return {
        "tool": "A11yway",
        "version": __version__,
        "summary": {
            "analysis_modes": analysis_modes,
            "total_pages_tested": len(items),
            "successful_pages": successful_pages,
            "failed_pages": len(items) - successful_pages,
            "total_issues": sum(item.get("issue_count", 0) for item in items),
            "total_raw_occurrences": sum(
                item.get("raw_occurrences", item.get("issue_count", 0))
                for item in items
            ),
            "total_unique_root_issues": sum(
                item.get("unique_root_issues", item.get("issue_count", 0))
                for item in items
            ),
            "total_task_blockers": sum(
                item.get("task_blocker_count", 0) for item in items
            ),
            "tasks_executed": len(executed),
            "tasks_completed": sum(
                1 for item in executed if item.get("task_execution_status") == "completed"
            ),
            "tasks_blocked": sum(
                1 for item in executed if item.get("task_execution_status") == "blocked"
            ),
            "html_reports": len(html_reports),
            "ai_scout_runs": len(ai_scout_items),
            "ai_scout_ok": sum(
                1 for item in ai_scout_items if item.get("ai_scout_status") == "ok"
            ),
            "low_vision_issues": sum(item.get("low_vision_issue_count", 0) for item in items),
            "counts_by_severity": counts_by_severity,
            "counts_by_issue_type": counts_by_issue_type,
        },
        "sources": items,
        "limitations": [
            "This prototype only runs static HTML checks.",
            "It does not replace a full human accessibility audit.",
            "It does not yet perform browser-based interaction testing.",
        ],
    }


def build_batch_index_markdown(index_report: dict) -> str:
    """Build a readable Markdown index for a batch audit run."""
    summary = index_report.get("summary", {})
    lines = [
        "# A11yway Batch Accessibility Index",
        "",
        "## Summary",
        "",
        f"- Total pages tested: {summary.get('total_pages_tested', 0)}",
        f"- Total issues: {summary.get('total_issues', 0)}",
        f"- Raw occurrences: {summary.get('total_raw_occurrences', summary.get('total_issues', 0))}",
        f"- Unique root issues: {summary.get('total_unique_root_issues', summary.get('total_issues', 0))}",
        f"- CSV index: {index_report.get('csv_index_path', '')}",
        f"- Evaluation summary: {index_report.get('evaluation_summary_path', '')}",
        "",
        "### Counts By Severity",
        "",
        *_format_count_items(summary.get("counts_by_severity", {})),
        "",
        "### Counts By Issue Type",
        "",
        *_format_count_items(summary.get("counts_by_issue_type", {})),
        "",
        "## Sources Tested",
        "",
        "| ID | Name | Source | Task | Status | Issues | Task blockers | AI Scout | Reports | Error |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]

    for item in index_report.get("sources", []):
        reports = item.get("reports", {})
        report_links = ", ".join(
            f"{kind}: {path}" for kind, path in reports.items() if path
        )
        lines.append(
            "| {id} | {name} | {source} | {task} | {status} | {issues} | {blockers} | {ai_scout} | {reports} | {error} |".format(
                id=item.get("id", ""),
                name=item.get("name", ""),
                source=item.get("source", ""),
                task=item.get("task", ""),
                status=item.get("status", "passed"),
                issues=item.get("issue_count", 0),
                blockers=item.get("task_blocker_count", 0),
                ai_scout=item.get("ai_scout_status", ""),
                reports=report_links,
                error=item.get("error", ""),
            )
        )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in index_report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_batch_index_markdown(index_report: dict, output_path: str | Path) -> None:
    """Write a Markdown batch index, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_batch_index_markdown(index_report), encoding="utf-8")


def save_batch_index_csv(index_report: dict, output_path: str | Path) -> None:
    """Write a spreadsheet-friendly CSV index for a batch audit."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "name",
        "source",
        "source_type",
        "task",
        "status",
        "issues_found",
        "raw_occurrences",
        "unique_root_issues",
        "task_blockers",
        "browser_status",
        "browser_issue_count",
        "low_vision_status",
        "low_vision_issue_count",
        "task_execution_status",
        "task_steps_passed",
        "task_steps_total",
        "high_count",
        "medium_count",
        "low_count",
        "issue_types",
        "json_report",
        "markdown_report",
        "html_report",
        "error",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in index_report.get("sources", []):
            severity_counts = item.get("counts_by_severity", {})
            issue_type_counts = item.get("counts_by_issue_type", {})
            reports = item.get("reports", {})
            writer.writerow(
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "source": item.get("source", ""),
                    "source_type": item.get("source_type", ""),
                    "task": item.get("task", ""),
                    "status": item.get("status", ""),
                    "issues_found": item.get("issue_count", 0),
                    "raw_occurrences": item.get("raw_occurrences", item.get("issue_count", 0)),
                    "unique_root_issues": item.get("unique_root_issues", item.get("issue_count", 0)),
                    "task_blockers": item.get("task_blocker_count", 0),
                    "browser_status": item.get("browser_status", ""),
                    "browser_issue_count": item.get("browser_issue_count", 0),
                    "low_vision_status": item.get("low_vision_status", ""),
                    "low_vision_issue_count": item.get("low_vision_issue_count", 0),
                    "task_execution_status": item.get("task_execution_status", ""),
                    "task_steps_passed": item.get("task_steps_passed", ""),
                    "task_steps_total": item.get("task_steps_total", ""),
                    "high_count": severity_counts.get("high", 0),
                    "medium_count": severity_counts.get("medium", 0),
                    "low_count": severity_counts.get("low", 0),
                    "issue_types": ";".join(issue_type_counts.keys()),
                    "json_report": reports.get("json", ""),
                    "markdown_report": reports.get("markdown", ""),
                    "html_report": reports.get("html", ""),
                    "error": item.get("error", ""),
                }
            )


def _sorted_issue_type_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    """Return issue type counts sorted by count (highest first), then name."""
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))


def build_evaluation_summary_markdown(index_report: dict, config_path: str = "") -> str:
    """Build a reviewer-friendly Markdown summary for a whole batch run."""
    summary = index_report.get("summary", {})
    sources = index_report.get("sources", [])
    severity_counts = summary.get("counts_by_severity", {})

    lines = [
        "# A11yway Batch Evaluation Summary",
        "",
        "## Overview",
        "",
        f"- Batch config used: {config_path or 'not recorded'}",
        f"- Pages tested: {summary.get('total_pages_tested', 0)}",
        f"- Successful pages: {summary.get('successful_pages', 0)}",
        f"- Failed pages: {summary.get('failed_pages', 0)}",
        f"- Total issues: {summary.get('total_issues', 0)}",
        f"- Raw occurrences: {summary.get('total_raw_occurrences', summary.get('total_issues', 0))}",
        f"- Unique root issues: {summary.get('total_unique_root_issues', summary.get('total_issues', 0))}",
        f"- Total task blockers: {summary.get('total_task_blockers', 0)}",
        f"- HTML reports: {summary.get('html_reports', 0)}",
        f"- AI Scout runs: {summary.get('ai_scout_runs', 0)}",
        f"- AI Scout successful runs: {summary.get('ai_scout_ok', 0)}",
        f"- Low-vision issues: {summary.get('low_vision_issues', 0)}",
        "",
        "## Top Issue Types",
        "",
    ]

    issue_type_counts = _sorted_issue_type_counts(summary.get("counts_by_issue_type", {}))
    if issue_type_counts:
        lines.extend(f"- {issue_type}: {count}" for issue_type, count in issue_type_counts)
    else:
        lines.append("- None found by the current static checks.")

    lines.extend(
        [
            "",
            "## Severity Breakdown",
            "",
            f"- High: {severity_counts.get('high', 0)}",
            f"- Medium: {severity_counts.get('medium', 0)}",
            f"- Low: {severity_counts.get('low', 0)}",
            "",
            "## Sources With Most Issues",
            "",
            "| Name | Source | Task | Issues | Blockers | Report | HTML report |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )

    ranked_sources = sorted(
        sources, key=lambda item: item.get("issue_count", 0), reverse=True
    )
    for item in ranked_sources:
        lines.append(
            "| {name} | {source} | {task} | {issues} | {blockers} | {report} | {html_report} |".format(
                name=item.get("name", ""),
                source=item.get("source", ""),
                task=item.get("task", ""),
                issues=item.get("issue_count", 0),
                blockers=item.get("task_blocker_count", 0),
                report=item.get("reports", {}).get("markdown", ""),
                html_report=item.get("reports", {}).get("html", ""),
            )
        )

    executed_items = [item for item in sources if item.get("task_execution_status")]
    if executed_items:
        lines.extend(
            [
                "",
                "## Task Execution Results",
                "",
                "Deterministic keyboard-only task attempts per page:",
                "",
                "| Name | Task | Result | Steps passed |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in executed_items:
            lines.append(
                "| {name} | {task} | {result} | {passed} of {total} |".format(
                    name=item.get("name", ""),
                    task=item.get("task", ""),
                    result=item.get("task_execution_status", ""),
                    passed=item.get("task_steps_passed", 0),
                    total=item.get("task_steps_total", 0),
                )
            )

    ai_scout_items = [item for item in sources if item.get("ai_scout_status")]
    if ai_scout_items:
        lines.extend(
            [
                "",
                "## AI Scout Results",
                "",
                "AI Scout suggestions are suggest-only and require human review.",
                "",
                "| Name | Status | AI Scout report |",
                "| --- | --- | --- |",
            ]
        )
        for item in ai_scout_items:
            lines.append(
                "| {name} | {status} | {report} |".format(
                    name=item.get("name", ""),
                    status=item.get("ai_scout_status", ""),
                    report=item.get("reports", {}).get("ai_scout_markdown", ""),
                )
            )

    lines.extend(["", "## High Priority Findings", ""])
    found_high_priority = False
    for item in sources:
        high_issues = item.get("high_severity_issues", [])
        if not high_issues:
            continue
        found_high_priority = True
        lines.extend([f"### {item.get('name', item.get('id', ''))}", ""])
        for issue in high_issues:
            lines.append(f"- {issue.get('issue_type', '')}: {issue.get('message', '')}")
            if issue.get("snippet"):
                lines.append(f"  - Evidence: `{issue['snippet']}`")
        report_path = item.get("reports", {}).get("markdown", "")
        if report_path:
            lines.append(f"- Full report: {report_path}")
        lines.append("")
    if not found_high_priority:
        lines.extend(["No high severity issues were found by the current static checks.", ""])

    lines.extend(
        [
            "## Recommended Review Process",
            "",
            "1. Review high severity issues first.",
            "2. Confirm evidence snippets against the actual page.",
            "3. Mark false positives.",
            "4. Note barriers the static checks missed.",
            "5. Decide which fixes are feasible for the organization.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {limitation}" for limitation in index_report.get("limitations", []))
    lines.append("")

    return "\n".join(lines)


def save_evaluation_summary_markdown(
    index_report: dict,
    output_path: str | Path,
    config_path: str = "",
) -> None:
    """Write the batch evaluation summary, creating parent directories if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_evaluation_summary_markdown(index_report, config_path=config_path),
        encoding="utf-8",
    )


class ReportBuilder:
    """Converts agent findings into report objects and export formats."""

    def build_report(
        self,
        task: AccessibilityTask,
        agents_used: List[str],
        issues: List[AccessibilityIssue],
    ) -> AccessibilityReport:
        """Create an accessibility report object."""
        return AccessibilityReport(
            task=task,
            agents_used=agents_used,
            issues=issues,
            summary=f"Found {len(issues)} placeholder issue(s) for task: {task.title}.",
        )

    def export_json(self, report: AccessibilityReport, path: Path) -> None:
        """Export a report as JSON.

        TODO: Decide final report schema before using this in production.
        """
        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(report), file, indent=2)

    def export_markdown(self, report: AccessibilityReport, path: Path) -> None:
        """Export a simple Markdown report.

        TODO: Replace this with a better report template later.
        """
        lines = [
            f"# A11yway Report: {report.task.title}",
            "",
            f"Task goal: {report.task.goal}",
            f"URL: {report.task.url}",
            "",
            "## Summary",
            report.summary,
            "",
            "## Issues",
        ]

        for issue in report.issues:
            lines.extend(
                [
                    f"### {issue.title}",
                    f"- Severity: {issue.severity}",
                    f"- Agent: {issue.agent_name}",
                    f"- Evidence: {issue.evidence}",
                    f"- Suggested fix: {issue.suggested_fix}",
                    "",
                ]
            )

        path.write_text("\n".join(lines), encoding="utf-8")
