"""Optional browser interaction audit built on Playwright.

This module is safe to import when Playwright is not installed: everything
degrades gracefully so static audits keep working without any browser
dependency. Browser mode approximates keyboard navigation with the Tab key
and re-checks the JavaScript-rendered DOM. It does not simulate a full
screen reader, does not crawl sites, and does not log into private pages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
except ImportError:  # Playwright is optional; static mode must keep working.
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

# Tags whose focused instances should always have an accessible name.
CONTROL_TAGS = {"a", "button", "input", "select", "textarea"}

# How many identical focus stops in a row look like a stuck Tab key.
REPEATED_FOCUS_THRESHOLD = 3

_PAGE_STATS_SCRIPT = r"""
() => ({
  focusable_count: document.querySelectorAll(
    'a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ).length,
  interactive_like_count: document.querySelectorAll(
    'a, button, input:not([type="hidden"]), select, textarea, [role="button"], [role="link"]'
  ).length
})
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
    """Return whether the optional Playwright dependency can be used."""
    return sync_playwright is not None


def source_to_browser_url(source: str) -> str:
    """Convert a local file path to a file:// URL; leave real URLs alone."""
    if is_url(source):
        return source
    return Path(source).resolve().as_uri()


def _accessible_name_guess(info: dict) -> str:
    """Estimate an accessible name from the strongest available signal.

    The id/name attributes are intentionally excluded: they help reviewers
    identify the element but are not real accessible names.
    """
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
    """Return a comparable identity for one focus stop."""
    return (
        info.get("tag"),
        info.get("id"),
        info.get("name"),
        info.get("href"),
        info.get("text"),
    )


def _trace_entry(step: int, info: dict) -> dict:
    """Build one focus trace entry for reports."""
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
    """Create a keyboard interaction issue with browser evidence."""
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
    """Build evidence for an issue about one focused element."""
    evidence: dict[str, Any] = {"step": entry.get("step"), "reason": reason}
    for key in ["tag", "id", "name", "type", "href", "src", "text", "role"]:
        value = entry.get(key)
        if value not in [None, ""]:
            evidence[key] = value
    return evidence


def _run_keyboard_traversal(page, stats: dict, max_tabs: int) -> tuple[list[dict], list[AccessibilityIssue]]:
    """Press Tab repeatedly and collect a focus trace plus interaction issues."""
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
    consecutive_repeats = 1
    worst_repeat_count = 1
    worst_repeat_entry: dict | None = None

    for step in range(1, max_tabs + 1):
        page.keyboard.press("Tab")
        info = page.evaluate(_FOCUS_INFO_SCRIPT)

        if info.get("is_body"):
            if trace:
                break  # Tab cycled through the page and returned to the body.
            continue

        signature = _focus_signature(info)
        if signatures and signature == signatures[-1]:
            consecutive_repeats += 1
        else:
            consecutive_repeats = 1
        if signatures and signature == signatures[0] and signature != signatures[-1]:
            break  # Focus wrapped around to the first element again.

        entry = _trace_entry(len(trace) + 1, info)
        signatures.append(signature)
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

    if worst_repeat_count >= REPEATED_FOCUS_THRESHOLD and worst_repeat_entry:
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
    flagged_hidden: set[tuple] = set()
    for entry, signature in zip(trace, signatures):
        if (
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
    """Re-run the static checks on the JavaScript-rendered DOM."""
    issues = analyze_html_static(rendered_html)
    for issue in issues:
        if isinstance(issue.evidence, dict):
            issue.evidence["detected_in"] = "browser_dom"
    return issues


def _short_error(error: Exception) -> str:
    """Return a short, friendly error message for browser failures."""
    message = str(error)
    if "Executable doesn't exist" in message or "playwright install" in message:
        return (
            "Chromium browser is not installed for Playwright. "
            "Run: python -m playwright install chromium"
        )
    first_line = message.strip().splitlines()[0] if message.strip() else "Unknown browser error"
    return first_line[:300]


def _focus_points_from_trace(trace: list[dict]) -> list[dict[str, Any]]:
    """Return overlay-ready focus points from the browser trace."""
    points: list[dict[str, Any]] = []
    for entry in trace:
        points.append(
            {
                "step": entry.get("step"),
                "tag": entry.get("tag"),
                "accessible_name_guess": entry.get("accessible_name_guess"),
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
    """Save screenshot and focus overlay files for a browser run."""
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
    """Load a page in headless Chromium and run keyboard/DOM checks.

    With include_axe, the axe-core rule set also runs against the rendered
    page. Always returns a result dict; on any failure success is False and
    the error field explains what happened, so batch mode can keep going.
    """
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
                trace, interaction_issues = _run_keyboard_traversal(page, stats, max_tabs)
                result["focus_trace"] = trace
                if visual_proof_dir:
                    try:
                        result["visual_proof"] = _collect_visual_proof(
                            page,
                            source,
                            visual_proof_dir,
                            trace,
                        )
                    except Exception as error:  # noqa: BLE001 - visual proof must not break audit
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
    except Exception as error:  # noqa: BLE001 - batch mode must survive any browser failure
        result["error"] = _short_error(error)
        result["success"] = False

    return result


def _issue_snippet_key(issue: AccessibilityIssue) -> tuple[str, str]:
    """Return a dedupe key using issue type and evidence snippet."""
    snippet = ""
    if isinstance(issue.evidence, dict):
        snippet = issue.evidence.get("snippet", "") or ""
    return (issue.issue_type, snippet)


def merge_browser_issues(
    static_issues: list[AccessibilityIssue],
    browser_result: dict | None,
) -> list[AccessibilityIssue]:
    """Combine static and browser issues without duplicating DOM re-checks.

    Issues the browser DOM re-check found that match a static finding (same
    issue type and evidence snippet) are dropped, so pages that render the
    same HTML statically and in the browser are not reported twice.
    """
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
