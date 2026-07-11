"""Screen-reader evidence based on Chromium accessibility tree data."""

from __future__ import annotations

from collections import Counter

from a11yway.core.announce import ANNOUNCE_LIMITATIONS, build_announce_transcript
from a11yway.core.capabilities import detect_capabilities
from a11yway.core.extended_results import DETERMINISTIC, HEURISTIC, extended_issue, module_result
from a11yway.models.issue import AccessibilityIssue


SCREEN_READER_LIMITATIONS = [
    "Chromium engine mode uses the browser accessibility tree and does not run NVDA, JAWS, VoiceOver, or TalkBack.",
    *ANNOUNCE_LIMITATIONS,
]


def run_screen_reader_audit(
    source: str,
    browser_result: dict | None,
    *,
    engine: str = "chromium",
    include_transcript: bool = False,
) -> tuple[list[AccessibilityIssue], dict]:
    """Create screen-reader evidence from browser focus/announce data."""
    issues: list[AccessibilityIssue] = []
    capabilities = detect_capabilities(verify_browsers=False)
    if engine != "chromium":
        status = capabilities["screen_readers"].get(engine, {}).get("status", "unavailable")
        result = module_result(
            "screen_reader",
            f"{engine}_adapter",
            issues,
            status="scaffolded" if status != "available_verified" else "available_untested",
            limitations=[
                f"{engine} native adapter did not run in this environment.",
                "No proprietary assistive-technology component is automated or redistributed.",
            ],
            capability=capabilities["screen_readers"].get(engine, {"status": "unavailable"}),
        ).to_json()
        return issues, result

    if not browser_result or not browser_result.get("success"):
        return issues, module_result(
            "screen_reader",
            "chromium_accessibility_tree",
            issues,
            status="unavailable",
            limitations=["Screen-reader evidence requires a successful browser run."],
            capability={"status": "unavailable"},
        ).to_json()

    focus_trace = browser_result.get("focus_trace", [])
    transcript = build_announce_transcript(focus_trace)
    seen = Counter()
    for entry, announcement in zip(focus_trace, transcript):
        text = announcement.get("announcement", "")
        seen[text] += 1
        role = announcement.get("role") or ""
        name = announcement.get("name") or ""
        selector = entry.get("selector") or entry.get("id") or entry.get("name") or entry.get("tag") or ""
        if announcement.get("available") and not name and role in {"button", "link", "textbox", "combobox", "checkbox", "radio"}:
            issues.append(
                extended_issue(
                    module="screen_reader",
                    check_id="empty_computed_name",
                    title="Focusable control has empty computed accessibility-tree name",
                    issue_type="screen_reader_empty_name",
                    severity="high",
                    source=source,
                    selector=str(selector),
                    observed=text,
                    expected="Reachable controls should expose a meaningful computed name.",
                    manual="Verify with a real screen reader if available; Chromium tree evidence is deterministic browser evidence.",
                    evidence_type=DETERMINISTIC,
                    detection_source="chromium_accessibility_tree",
                    context={"focus_index": entry.get("step"), "role": role, "state": announcement.get("states", [])},
                )
            )
        if entry.get("aria_hidden_ancestor") or entry.get("hidden"):
            issues.append(
                extended_issue(
                    module="screen_reader",
                    check_id="focus_hidden_tree",
                    title="Focused element may be hidden from assistive technology",
                    issue_type="screen_reader_focus_hidden",
                    severity="high",
                    source=source,
                    selector=str(selector),
                    observed=text,
                    expected="Keyboard focus should not land in aria-hidden or hidden accessibility-tree content.",
                    manual="Confirm focus and computed tree exposure in browser dev tools and a real screen reader.",
                    evidence_type=HEURISTIC,
                    detection_source="chromium_accessibility_tree",
                    context={"focus_index": entry.get("step")},
                )
            )
    for announcement, count in seen.items():
        if announcement and announcement != "(announcement unavailable)" and count >= 4:
            issues.append(
                extended_issue(
                    module="screen_reader",
                    check_id="duplicate_announcement",
                    title="Repeated identical announcements may be confusing",
                    issue_type="screen_reader_duplicate_announcement",
                    severity="low",
                    source=source,
                    observed=f"Announcement repeated {count} times: {announcement}",
                    expected="Repeated controls should have distinguishable names or context.",
                    manual="Review whether repeated labels are meaningfully distinguished by surrounding context.",
                    evidence_type=HEURISTIC,
                    detection_source="chromium_accessibility_tree",
                )
            )
    artifacts = {"engine": "chromium", "transcript": transcript if include_transcript else [], "transcript_count": len(transcript)}
    return issues, module_result(
        "screen_reader",
        "chromium_accessibility_tree",
        issues,
        limitations=SCREEN_READER_LIMITATIONS,
        artifacts=artifacts,
        capability={"status": "available_verified", "engine": "chromium"},
    ).to_json()
