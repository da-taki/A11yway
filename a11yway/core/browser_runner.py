








from __future__ import annotations

from pathlib import Path
from typing import Any

from a11yway.core.announce import (
    ANNOUNCE_CHECK_NAME,
    capture_focused_announcement,
    format_announcement,
    is_unnamed_announcement,
    open_announce_session,
)
from a11yway.core.axe_runner import AXE_CHECK_NAME, run_axe_scan
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.source_loader import is_url
from a11yway.core.visual_proof import (
    build_visual_proof_metadata,
    save_focus_overlay_html,
)
from a11yway.models.issue import AccessibilityIssue

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


PLAYWRIGHT_SETUP_MESSAGE = (
    "Browser mode requires Playwright. Install it with:\n"
    "\n"
    "  pip install -r requirements-browser.txt\n"
    "  python -m playwright install chromium\n"
    "\n"
    "Static audits keep working without Playwright."
)

BROWSER_CHECKS_RUN = ["keyboard_focus_traversal", "browser_dom_snapshot"]


CONTROL_TAGS = {"a", "button", "input", "select", "textarea"}


REPEATED_FOCUS_THRESHOLD = 3


FOCUS_LOST_THRESHOLD = 3

_PAGE_STATS_SCRIPT = r"""
() => {
  const selector =
    'a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const seenRadioGroups = new Set();
  let focusableCount = 0;
  for (const el of document.querySelectorAll(selector)) {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const visible =
      (rect.width > 0 || rect.height > 0) &&
      style.visibility !== "hidden" &&
      style.display !== "none";
    if (!visible) continue;
    // A radio group is one Tab stop, so count each group once.
    const type = (el.getAttribute("type") || "").toLowerCase();
    if (el.tagName === "INPUT" && type === "radio" && el.name) {
      if (seenRadioGroups.has(el.name)) continue;
      seenRadioGroups.add(el.name);
    }
    focusableCount += 1;
  }
  return {
    focusable_count: focusableCount,
    interactive_like_count: document.querySelectorAll(
      'a, button, input:not([type="hidden"]), select, textarea, [role="button"], [role="link"]'
    ).length
  };
}
"""

_FOCUS_INFO_SCRIPT = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) {
    return { is_body: true, tag: el ? el.tagName.toLowerCase() : null };
  }
  const style = window.getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  const clean = (value) => (value || "").replace(/\s+/g, " ").trim();
  let labelledbyText = "";
  const labelledby = el.getAttribute("aria-labelledby");
  if (labelledby) {
    labelledbyText = labelledby
      .split(/\s+/)
      .map((id) => {
        const target = document.getElementById(id);
        return target ? target.textContent : "";
      })
      .join(" ");
  }
  let labelText = "";
  if (el.labels && el.labels.length) {
    labelText = Array.from(el.labels).map((label) => label.textContent).join(" ");
  }
  let imageAlt = "";
  if (el.querySelector) {
    const image = el.querySelector("img[alt]");
    if (image) imageAlt = image.getAttribute("alt");
  }
  const inputType = clean(el.getAttribute("type")).toLowerCase();
  return {
    is_body: false,
    tag: el.tagName.toLowerCase(),
    id: el.id || null,
    name: el.getAttribute("name"),
    type: el.getAttribute("type"),
    href: el.getAttribute("href"),
    src: el.getAttribute("src"),
    text: clean(el.innerText || el.textContent).slice(0, 80),
    value_label: ["submit", "button", "reset"].includes(inputType) ? clean(el.value) : "",
    aria_label: clean(el.getAttribute("aria-label")),
    labelledby_text: clean(labelledbyText),
    label_text: clean(labelText),
    title: clean(el.getAttribute("title")),
    role: el.getAttribute("role"),
    image_alt: clean(imageAlt),
    is_visible:
      (rect.width > 0 || rect.height > 0) &&
      style.visibility !== "hidden" &&
      style.display !== "none",
    x: rect.x,
    y: rect.y,
    width: rect.width,
    height: rect.height
  };
}
"""


def is_playwright_available() -> bool:

    return sync_playwright is not None


def source_to_browser_url(source: str) -> str:

    if is_url(source):
        return source
    return Path(source).resolve().as_uri()


def _accessible_name_guess(info: dict) -> str:





    for key in [
        "aria_label",
        "labelledby_text",
        "label_text",
        "text",
        "value_label",
        "image_alt",
        "title",
    ]:
        value = (info.get(key) or "").strip()
        if value:
            return value
    return ""


def _focus_signature(info: dict) -> tuple:

    return (
        info.get("tag"),
        info.get("id"),
        info.get("name"),
        info.get("href"),
        info.get("text"),
        _accessible_name_guess(info),
    )


def find_focus_cycle(signatures: list[tuple]) -> int | None:






    count = len(signatures)
    for period in range(1, count // 2 + 1):
        if signatures[-period:] == signatures[-2 * period : -period]:
            return period
    return None


def _short_element_label(entry: dict) -> str:

    tag = entry.get("tag") or "element"
    for key in ["id", "name"]:
        value = entry.get(key)
        if value:
            return f"{tag}#{value}"
    text = (entry.get("text") or "").strip()
    if text:
        return f'{tag} "{text[:40]}"'
    return tag


def _loop_sequence_label(entries: list[dict]) -> str:

    return " -> ".join(_short_element_label(entry) for entry in entries)


def _trace_entry(step: int, info: dict) -> dict:

    return {
        "step": step,
        "tag": info.get("tag"),
        "id": info.get("id"),
        "name": info.get("name"),
        "type": info.get("type"),
        "href": info.get("href"),
        "src": info.get("src"),
        "text": info.get("text"),
        "role": info.get("role"),
        "accessible_name_guess": _accessible_name_guess(info),
        "is_visible": bool(info.get("is_visible")),
        "x": info.get("x"),
        "y": info.get("y"),
        "width": info.get("width"),
        "height": info.get("height"),
    }


def _browser_issue(
    title: str,
    issue_type: str,
    severity: str,
    evidence: dict[str, Any],
    suggested_fix: str,
) -> AccessibilityIssue:

    evidence = dict(evidence)
    evidence["detected_in"] = "browser_interaction"
    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name="Keyboard Navigator",
        evidence=evidence,
        suggested_fix=suggested_fix,
    )


def _element_evidence_from_entry(entry: dict, reason: str) -> dict[str, Any]:

    evidence: dict[str, Any] = {"step": entry.get("step"), "reason": reason}
    for key in ["tag", "id", "name", "type", "href", "src", "text", "role"]:
        value = entry.get(key)
        if value not in [None, ""]:
            evidence[key] = value
    return evidence


def _run_keyboard_traversal(
    page,
    stats: dict,
    max_tabs: int,
    announce_session=None,
) -> tuple[list[dict], list[AccessibilityIssue]]:

    trace: list[dict] = []
    issues: list[AccessibilityIssue] = []
    focusable_count = stats.get("focusable_count", 0)
    interactive_like_count = stats.get("interactive_like_count", 0)

    if focusable_count == 0:
        if interactive_like_count > 0:
            issues.append(
                _browser_issue(
                    title="Page has interactive elements but nothing is keyboard focusable",
                    issue_type="browser_no_focusable_elements",
                    severity="high",
                    evidence={
                        "reason": (
                            "The page contains interactive-looking elements but the "
                            "keyboard cannot reach any of them."
                        ),
                        "interactive_like_count": interactive_like_count,
                    },
                    suggested_fix=(
                        "Use native links, buttons, and form controls, or add proper "
                        "tabindex and keyboard handlers to custom controls."
                    ),
                )
            )
        return trace, issues

    signatures: list[tuple] = []



    body_passed: list[bool] = []
    consecutive_repeats = 1
    worst_repeat_count = 1
    worst_repeat_entry: dict | None = None
    body_streak = 0
    pending_body_pass = False
    full_pass = False
    focus_lost = False

    for step in range(1, max_tabs + 1):
        page.keyboard.press("Tab")
        info = page.evaluate(_FOCUS_INFO_SCRIPT)

        if info.get("is_body"):
            if not trace:
                continue
            body_streak += 1
            pending_body_pass = True
            if body_streak >= FOCUS_LOST_THRESHOLD:
                focus_lost = True
                break
            continue
        body_streak = 0

        signature = _focus_signature(info)
        wrapped = bool(
            signatures
            and signature == signatures[0]
            and (pending_body_pass or signature != signatures[-1])
        )
        if wrapped and len(set(signatures)) >= focusable_count:
            full_pass = True
            break



        if signatures and signature == signatures[-1]:
            consecutive_repeats += 1
        else:
            consecutive_repeats = 1

        entry = _trace_entry(len(trace) + 1, info)
        announce = capture_focused_announcement(announce_session)
        entry["announce"] = announce
        entry["announcement"] = format_announcement(announce) if announce else None
        signatures.append(signature)
        body_passed.append(pending_body_pass)
        pending_body_pass = False
        trace.append(entry)

        if consecutive_repeats > worst_repeat_count:
            worst_repeat_count = consecutive_repeats
            worst_repeat_entry = entry

    if not trace:
        issues.append(
            _browser_issue(
                title="Keyboard focus did not move into the page",
                issue_type="browser_focus_not_moving",
                severity="high",
                evidence={
                    "reason": (
                        "Pressing Tab repeatedly never focused a page element even "
                        "though focusable elements exist."
                    ),
                    "focusable_count": focusable_count,
                    "tab_presses": max_tabs,
                },
                suggested_fix=(
                    "Check for scripts that cancel Tab key events or move focus back, "
                    "and confirm controls are reachable with the keyboard."
                ),
            )
        )
        return trace, issues

    if focus_lost:
        issues.append(
            _browser_issue(
                title="Keyboard focus left the page content",
                issue_type="focus_lost",
                severity="medium",
                evidence={
                    "reason": (
                        f"After {len(trace)} focus stop(s), pressing Tab landed on "
                        f"the document body {body_streak} times in a row and focus "
                        "never returned to page content."
                    ),
                    "body_streak": body_streak,
                    "focusable_count": focusable_count,
                },
                suggested_fix=(
                    "Check for scripts that remove, hide, or blur the focused "
                    "element, and keep every control at a stable place in the "
                    "Tab order."
                ),
            )
        )

    trap_signatures: set[tuple] = set()
    if trace and not full_pass and not focus_lost:
        period = find_focus_cycle(signatures)
        unreached = focusable_count - len(set(signatures))
        if (
            period is not None
            and unreached >= 1
            and not any(body_passed[-2 * period :])
        ):
            loop_entries = trace[-period:]
            trap_signatures = set(signatures[-period:])
            issues.append(
                _browser_issue(
                    title="Keyboard focus is trapped in a loop",
                    issue_type="keyboard_trap",
                    severity="high",
                    evidence={
                        "reason": (
                            "Tab keeps cycling through the same "
                            f"{len(trap_signatures)} element(s) without passing "
                            f"through the rest of the page; about {unreached} "
                            "focusable element(s) were never reached within "
                            f"{max_tabs} Tab presses."
                        ),
                        "loop_sequence": _loop_sequence_label(loop_entries),
                        "loop_length": len(trap_signatures),
                        "unreached_focusable_count": unreached,
                        "tab_presses": max_tabs,
                    },
                    suggested_fix=(
                        "Let Tab move past the widget, or provide a standard way "
                        "out, such as closing a modal with Escape and returning "
                        "focus. Related to WCAG 2.1.2 No Keyboard Trap."
                    ),
                )
            )

    if (
        worst_repeat_count >= REPEATED_FOCUS_THRESHOLD
        and worst_repeat_entry
        and _focus_signature(worst_repeat_entry) not in trap_signatures
    ):
        issues.append(
            _browser_issue(
                title="Keyboard focus repeats on the same element",
                issue_type="browser_repeated_focus",
                severity="medium",
                evidence=_element_evidence_from_entry(
                    worst_repeat_entry,
                    f"The same element stayed focused for {worst_repeat_count} "
                    "Tab presses in a row, which can indicate a keyboard trap.",
                ),
                suggested_fix=(
                    "Review tabindex values and focus scripts so Tab moves through "
                    "every control in a sensible order."
                ),
            )
        )

    flagged_missing_name: set[tuple] = set()
    flagged_unnamed: set[tuple] = set()
    flagged_hidden: set[tuple] = set()
    for entry, signature in zip(trace, signatures):
        announce = entry.get("announce")
        if announce is not None:


            if is_unnamed_announcement(announce) and signature not in flagged_unnamed:
                flagged_unnamed.add(signature)
                evidence = _element_evidence_from_entry(
                    entry,
                    "Chromium's accessibility tree computed an empty accessible "
                    "name for this focus stop, so a screen reader announces "
                    "nothing useful about it.",
                )
                evidence["announced_role"] = announce.get("role")
                evidence["announcement"] = entry.get("announcement")
                if announce.get("ignored"):
                    evidence["ax_ignored"] = True
                issues.append(
                    _browser_issue(
                        title="Focus stop announces no accessible name",
                        issue_type="unnamed_focus_stop",
                        severity="high",
                        evidence=evidence,
                        suggested_fix=(
                            "Add a visible label, text content, alt text, or "
                            "aria-label so the browser computes a usable "
                            "accessible name for this element."
                        ),
                    )
                )
        elif (
            entry["tag"] in CONTROL_TAGS
            and not entry["accessible_name_guess"]
            and signature not in flagged_missing_name
        ):
            flagged_missing_name.add(signature)
            issues.append(
                _browser_issue(
                    title="Focused control has no accessible name",
                    issue_type="browser_focused_control_missing_name",
                    severity="high",
                    evidence=_element_evidence_from_entry(
                        entry,
                        "A keyboard user reached this control, but it has no label, "
                        "text, aria-label, or other usable name.",
                    ),
                    suggested_fix=(
                        "Add a visible label, text content, or aria-label so students "
                        "know what the control does."
                    ),
                )
            )

        if not entry["is_visible"] and signature not in flagged_hidden:
            flagged_hidden.add(signature)
            issues.append(
                _browser_issue(
                    title="Keyboard focus landed on a hidden element",
                    issue_type="browser_focus_on_hidden_element",
                    severity="high",
                    evidence=_element_evidence_from_entry(
                        entry,
                        "This element received keyboard focus but does not appear "
                        "to be visible on the page.",
                    ),
                    suggested_fix=(
                        'Remove hidden elements from the Tab order with tabindex="-1" '
                        "or make them visible when focused."
                    ),
                )
            )

    return trace, issues


def _rendered_dom_issues(rendered_html: str) -> list[AccessibilityIssue]:

    issues = analyze_html_static(rendered_html)
    for issue in issues:
        if isinstance(issue.evidence, dict):
            issue.evidence["detected_in"] = "browser_dom"
    return issues


def _short_error(error: Exception) -> str:

    message = str(error)
    if "Executable doesn't exist" in message or "playwright install" in message:
        return (
            "Chromium browser is not installed for Playwright. "
            "Run: python -m playwright install chromium"
        )
    first_line = message.strip().splitlines()[0] if message.strip() else "Unknown browser error"
    return first_line[:300]


def _focus_points_from_trace(trace: list[dict]) -> list[dict[str, Any]]:

    points: list[dict[str, Any]] = []
    for entry in trace:
        points.append(
            {
                "step": entry.get("step"),
                "tag": entry.get("tag"),
                "accessible_name_guess": entry.get("accessible_name_guess"),
                "announcement": entry.get("announcement"),
                "id": entry.get("id"),
                "name": entry.get("name"),
                "href": entry.get("href"),
                "text": entry.get("text"),
                "x": entry.get("x"),
                "y": entry.get("y"),
                "width": entry.get("width"),
                "height": entry.get("height"),
            }
        )
    return points


def _collect_visual_proof(
    page,
    source: str,
    output_dir: str | Path,
    focus_trace: list[dict],
) -> dict[str, Any]:

    visual_dir = Path(output_dir)
    visual_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = visual_dir / "page.png"
    overlay_path = visual_dir / "focus_path.html"
    page.screenshot(path=str(screenshot_path), full_page=True)
    focus_points = _focus_points_from_trace(focus_trace)
    viewport = page.viewport_size or {}
    save_focus_overlay_html(
        screenshot_path,
        focus_points,
        overlay_path,
        source=source,
        viewport=viewport,
    )
    return build_visual_proof_metadata(
        screenshot_path,
        overlay_path,
        focus_points,
        viewport=viewport,
    )


def run_browser_audit(
    source: str,
    max_tabs: int = 40,
    wait_ms: int = 500,
    visual_proof_dir: str | Path | None = None,
    include_axe: bool = False,
) -> dict:






    result: dict[str, Any] = {
        "mode": "browser",
        "source": source,
        "final_url": None,
        "success": False,
        "error": None,
        "checks_run": list(BROWSER_CHECKS_RUN),
        "focus_trace": [],
        "issues": [],
        "visual_proof": None,
        "axe": None,
    }

    if not is_playwright_available():
        result["error"] = "Playwright is not installed."
        return result

    try:
        url = source_to_browser_url(source)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_timeout(wait_ms)
                result["final_url"] = page.url

                stats = page.evaluate(_PAGE_STATS_SCRIPT)
                announce_session = open_announce_session(page)
                if announce_session is not None:
                    result["checks_run"].append(ANNOUNCE_CHECK_NAME)
                trace, interaction_issues = _run_keyboard_traversal(
                    page, stats, max_tabs, announce_session=announce_session
                )
                result["focus_trace"] = trace
                if visual_proof_dir:
                    try:
                        result["visual_proof"] = _collect_visual_proof(
                            page,
                            source,
                            visual_proof_dir,
                            trace,
                        )
                    except Exception as error:
                        result["visual_proof"] = {
                            "enabled": False,
                            "error": _short_error(error),
                        }

                dom_issues = _rendered_dom_issues(page.content())
                result["issues"] = interaction_issues + dom_issues

                if include_axe:
                    axe_result = run_axe_scan(page)
                    axe_issues = axe_result.pop("issues")
                    result["axe"] = axe_result
                    if axe_result["success"]:
                        result["checks_run"].append(AXE_CHECK_NAME)
                        result["issues"] = result["issues"] + axe_issues

                result["success"] = True
            finally:
                browser.close()
    except Exception as error:
        result["error"] = _short_error(error)
        result["success"] = False

    return result


def _issue_snippet_key(issue: AccessibilityIssue) -> tuple[str, str]:

    snippet = ""
    if isinstance(issue.evidence, dict):
        snippet = issue.evidence.get("snippet", "") or ""
    return (issue.issue_type, snippet)


def merge_browser_issues(
    static_issues: list[AccessibilityIssue],
    browser_result: dict | None,
) -> list[AccessibilityIssue]:






    merged = list(static_issues)
    if not browser_result or not browser_result.get("success"):
        return merged

    static_keys = {_issue_snippet_key(issue) for issue in static_issues}
    for issue in browser_result.get("issues", []):
        detected_in = ""
        if isinstance(issue.evidence, dict):
            detected_in = issue.evidence.get("detected_in", "")
        if detected_in == "browser_dom" and _issue_snippet_key(issue) in static_keys:
            continue
        merged.append(issue)

    return merged
