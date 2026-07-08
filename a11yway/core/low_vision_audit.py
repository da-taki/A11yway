"""Optional browser-based low-vision accessibility checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from a11yway.core.browser_runner import is_playwright_available, source_to_browser_url
from a11yway.models.issue import AccessibilityIssue

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # Browser mode is optional.
    sync_playwright = None


LOW_VISION_CHECKS_RUN = [
    "rendered_color_contrast",
    "zoom_reflow_200",
    "focus_visibility",
]

LOW_VISION_LIMITATIONS = [
    "Low-vision checks use browser-computed styles and conservative heuristics.",
    "Rendered color contrast checks do not prove full WCAG conformance.",
    "Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.",
    "Focus indicator detection may miss custom focus styles.",
]

_VISIBLE_TEXT_SCRIPT = r"""
() => {
  const selectors = 'h1,h2,h3,h4,h5,h6,p,label,a,button,input,select,textarea,li,td,th';
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const pathFor = (el) => {
    const parts = [];
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE && parts.length < 4) {
      let part = node.tagName.toLowerCase();
      if (node.id) {
        part += '#' + node.id;
        parts.unshift(part);
        break;
      }
      if (node.classList && node.classList.length) {
        part += '.' + Array.from(node.classList).slice(0, 2).join('.');
      }
      parts.unshift(part);
      node = node.parentElement;
    }
    return parts.join(' > ');
  };
  const backgroundFor = (el) => {
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
      const bg = window.getComputedStyle(node).backgroundColor;
      if (bg && !bg.includes('rgba(0, 0, 0, 0)') && bg !== 'transparent') {
        return bg;
      }
      node = node.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  return Array.from(document.querySelectorAll(selectors)).slice(0, 250).map((el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    let text = clean(el.innerText || el.textContent);
    if (!text && ['input', 'select', 'textarea'].includes(el.tagName.toLowerCase())) {
      text = clean(el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.getAttribute('name'));
    }
    return {
      tag: el.tagName.toLowerCase(),
      selector: pathFor(el),
      text: text.slice(0, 120),
      color: style.color,
      background_color: backgroundFor(el),
      font_size: style.fontSize,
      font_weight: style.fontWeight,
      opacity: style.opacity,
      display: style.display,
      visibility: style.visibility,
      width: rect.width,
      height: rect.height
    };
  }).filter((item) =>
    item.text &&
    item.width > 0 &&
    item.height > 0 &&
    item.display !== 'none' &&
    item.visibility !== 'hidden' &&
    Number(item.opacity || 1) > 0.05
  ).slice(0, 100);
}
"""

_REFLOW_SCRIPT = r"""
() => {
  const viewportWidth = document.documentElement.clientWidth;
  const scrollWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
  const wide = Array.from(document.querySelectorAll('body *')).map((el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const widthStyle = style.width || '';
    const position = style.position || '';
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      class_name: el.className ? String(el.className).slice(0, 80) : '',
      width: rect.width,
      width_style: widthStyle,
      position,
      text: (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80)
    };
  }).filter((item) =>
    item.width > viewportWidth + 24 ||
    /^\d{3,}px$/.test(item.width_style)
  ).slice(0, 5);
  return {
    viewport_width: viewportWidth,
    document_scroll_width: scrollWidth,
    overflow_amount: Math.max(0, scrollWidth - viewportWidth),
    wide_elements: wide
  };
}
"""

_FOCUS_STYLE_SCRIPT = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) {
    return null;
  }
  const style = window.getComputedStyle(el);
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const rect = el.getBoundingClientRect();
  return {
    tag: el.tagName.toLowerCase(),
    id: el.id || null,
    name: el.getAttribute('name'),
    text: clean(el.innerText || el.textContent).slice(0, 80),
    aria_label: clean(el.getAttribute('aria-label')),
    outline_style: style.outlineStyle,
    outline_width: style.outlineWidth,
    outline_color: style.outlineColor,
    box_shadow: style.boxShadow,
    border: style.border,
    width: rect.width,
    height: rect.height
  };
}
"""


def _parse_color(value: str) -> tuple[float, float, float, float] | None:
    """Parse common CSS rgb/rgba/hex colors."""
    if not value:
        return None
    text = value.strip().lower()
    if text == "transparent":
        return None
    if text.startswith("#"):
        hex_value = text[1:]
        if len(hex_value) == 3:
            hex_value = "".join(char * 2 for char in hex_value)
        if len(hex_value) == 6:
            try:
                return (
                    int(hex_value[0:2], 16),
                    int(hex_value[2:4], 16),
                    int(hex_value[4:6], 16),
                    1.0,
                )
            except ValueError:
                return None
    match = re.match(r"rgba?\(([^)]+)\)", text)
    if not match:
        return None
    parts = [part.strip() for part in match.group(1).split(",")]
    if len(parts) < 3:
        return None
    try:
        rgb = tuple(float(part.rstrip("%")) for part in parts[:3])
        alpha = float(parts[3]) if len(parts) > 3 else 1.0
    except ValueError:
        return None
    return (rgb[0], rgb[1], rgb[2], alpha)


def _relative_luminance(color: tuple[float, float, float, float]) -> float:
    """Return WCAG-style relative luminance for an sRGB color."""
    channels = []
    for channel in color[:3]:
        value = channel / 255
        if value <= 0.03928:
            channels.append(value / 12.92)
        else:
            channels.append(((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def calculate_contrast_ratio(foreground: str, background: str) -> float | None:
    """Calculate a contrast ratio for two CSS colors."""
    fg = _parse_color(foreground)
    bg = _parse_color(background)
    if fg is None or bg is None or fg[3] == 0 or bg[3] == 0:
        return None
    lighter = max(_relative_luminance(fg), _relative_luminance(bg))
    darker = min(_relative_luminance(fg), _relative_luminance(bg))
    return round((lighter + 0.05) / (darker + 0.05), 2)


def _low_vision_issue(
    title: str,
    issue_type: str,
    severity: str,
    evidence: dict[str, Any],
    suggested_fix: str,
) -> AccessibilityIssue:
    """Create a low-vision issue with consistent evidence."""
    evidence = dict(evidence)
    evidence["detected_in"] = "low_vision"
    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name="Low Vision Browser Audit",
        evidence=evidence,
        suggested_fix=suggested_fix,
    )


def _contrast_issues(samples: list[dict[str, Any]]) -> list[AccessibilityIssue]:
    """Return low contrast text issues from computed style samples."""
    issues: list[AccessibilityIssue] = []
    seen: set[tuple[str, str]] = set()
    for sample in samples:
        ratio = calculate_contrast_ratio(
            sample.get("color", ""),
            sample.get("background_color", ""),
        )
        sample["contrast_ratio"] = ratio
        if ratio is None or ratio >= 4.5:
            continue
        key = (sample.get("selector", ""), sample.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        severity = "high" if ratio < 3.0 else "medium"
        issues.append(
            _low_vision_issue(
                title="Rendered text may have low contrast",
                issue_type="low_contrast_text",
                severity=severity,
                evidence={
                    "text": sample.get("text"),
                    "tag": sample.get("tag"),
                    "selector": sample.get("selector"),
                    "foreground_color": sample.get("color"),
                    "background_color": sample.get("background_color"),
                    "contrast_ratio": ratio,
                    "font_size": sample.get("font_size"),
                    "font_weight": sample.get("font_weight"),
                    "reason": "Computed foreground/background contrast is below the conservative 4.5:1 review threshold.",
                },
                suggested_fix="Increase foreground/background contrast and confirm the final design with manual review.",
            )
        )
    return issues


def _zoom_issues(zoom_reflow: dict[str, Any]) -> list[AccessibilityIssue]:
    """Return zoom/reflow approximation issues."""
    issues: list[AccessibilityIssue] = []
    overflow = int(zoom_reflow.get("overflow_amount", 0) or 0)
    viewport_width = int(zoom_reflow.get("viewport_width", 0) or 0)
    scroll_width = int(zoom_reflow.get("document_scroll_width", 0) or 0)
    if overflow > 24:
        severity = "high" if overflow > 240 else "medium"
        issues.append(
            _low_vision_issue(
                title="Page has horizontal overflow in a narrow viewport",
                issue_type="zoom_horizontal_overflow",
                severity=severity,
                evidence={
                    "viewport_width": viewport_width,
                    "document_scroll_width": scroll_width,
                    "overflow_amount": overflow,
                    "reason": "At a narrow viewport used to approximate 200% zoom/reflow stress, the document is wider than the viewport.",
                },
                suggested_fix="Use responsive layout, avoid fixed-width containers, and test reflow at high zoom.",
            )
        )
    for element in zoom_reflow.get("wide_elements", [])[:3]:
        issues.append(
            _low_vision_issue(
                title="Fixed or wide content may prevent reflow",
                issue_type="zoom_fixed_width_content",
                severity="medium",
                evidence={
                    "tag": element.get("tag"),
                    "id": element.get("id"),
                    "class": element.get("class_name"),
                    "width": element.get("width"),
                    "width_style": element.get("width_style"),
                    "text": element.get("text"),
                    "viewport_width": viewport_width,
                    "reason": "A rendered element is wider than the narrow viewport or uses a large fixed pixel width.",
                },
                suggested_fix="Replace fixed-width layout with responsive sizing such as max-width: 100%.",
            )
        )
    return issues


def _has_visible_focus_style(info: dict[str, Any]) -> bool:
    """Heuristically decide whether a focused element has visible styling."""
    outline_style = (info.get("outline_style") or "").lower()
    outline_width = (info.get("outline_width") or "").lower()
    box_shadow = (info.get("box_shadow") or "").lower()
    border = (info.get("border") or "").lower()
    if outline_style not in {"", "none", "hidden"} and outline_width not in {"", "0px"}:
        return True
    if box_shadow and box_shadow != "none":
        return True
    if border and "0px" not in border and "none" not in border:
        return True
    return False


def _focus_visibility_check(page, max_tabs: int = 40) -> tuple[dict[str, Any], list[AccessibilityIssue]]:
    """Tab through the page and flag missing obvious focus indicators."""
    issues: list[AccessibilityIssue] = []
    checked: list[dict[str, Any]] = []
    flagged: set[tuple[str, str, str]] = set()
    for step in range(1, max_tabs + 1):
        page.keyboard.press("Tab")
        info = page.evaluate(_FOCUS_STYLE_SCRIPT)
        if not info:
            if checked:
                break
            continue
        info["step"] = step
        checked.append(info)
        key = (info.get("tag") or "", info.get("id") or "", info.get("text") or "")
        if key in flagged or _has_visible_focus_style(info):
            continue
        flagged.add(key)
        severity = "high" if info.get("tag") in {"a", "button", "input", "select", "textarea"} else "medium"
        issues.append(
            _low_vision_issue(
                title="Focused element may not show a visible focus indicator",
                issue_type="focus_indicator_missing",
                severity=severity,
                evidence={
                    "step": step,
                    "tag": info.get("tag"),
                    "id": info.get("id"),
                    "name": info.get("name"),
                    "text": info.get("text") or info.get("aria_label"),
                    "outline_style": info.get("outline_style"),
                    "outline_width": info.get("outline_width"),
                    "outline_color": info.get("outline_color"),
                    "box_shadow": info.get("box_shadow"),
                    "border": info.get("border"),
                    "reason": "The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.",
                },
                suggested_fix="Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.",
            )
        )
    return {"checked_count": len(checked), "flagged_count": len(issues)}, issues


def run_low_vision_audit(page, source: str | None = None) -> dict[str, Any]:
    """Run low-vision checks against an already-loaded Playwright page."""
    result: dict[str, Any] = {
        "mode": "low_vision",
        "source": source,
        "success": False,
        "error": None,
        "checks_run": list(LOW_VISION_CHECKS_RUN),
        "issues": [],
        "contrast_samples": [],
        "zoom_reflow": {},
        "focus_visibility": {},
        "limitations": list(LOW_VISION_LIMITATIONS),
    }
    try:
        samples = page.evaluate(_VISIBLE_TEXT_SCRIPT)
        result["contrast_samples"] = samples
        issues = _contrast_issues(samples)

        original_viewport = page.viewport_size or {"width": 1280, "height": 720}
        page.set_viewport_size({"width": 640, "height": original_viewport.get("height", 720)})
        page.wait_for_timeout(100)
        zoom_reflow = page.evaluate(_REFLOW_SCRIPT)
        result["zoom_reflow"] = zoom_reflow
        issues.extend(_zoom_issues(zoom_reflow))

        page.set_viewport_size(original_viewport)
        page.wait_for_timeout(100)
        focus_visibility, focus_issues = _focus_visibility_check(page)
        result["focus_visibility"] = focus_visibility
        issues.extend(focus_issues)

        result["issues"] = issues
        result["success"] = True
    except Exception as error:  # noqa: BLE001 - browser batch mode must survive failures
        result["error"] = str(error).strip().splitlines()[0][:300]
        result["success"] = False
    return result


def run_low_vision_audit_for_source(
    source: str,
    wait_ms: int = 500,
) -> dict[str, Any]:
    """Open a source in Chromium and run low-vision checks."""
    if not is_playwright_available() or sync_playwright is None:
        return {
            "mode": "low_vision",
            "source": source,
            "success": False,
            "error": "Playwright is not installed.",
            "checks_run": list(LOW_VISION_CHECKS_RUN),
            "issues": [],
            "contrast_samples": [],
            "zoom_reflow": {},
            "focus_visibility": {},
            "limitations": list(LOW_VISION_LIMITATIONS),
        }
    try:
        url = source_to_browser_url(source)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_timeout(wait_ms)
                return run_low_vision_audit(page, source=source)
            finally:
                browser.close()
    except Exception as error:  # noqa: BLE001
        return {
            "mode": "low_vision",
            "source": source,
            "success": False,
            "error": str(error).strip().splitlines()[0][:300],
            "checks_run": list(LOW_VISION_CHECKS_RUN),
            "issues": [],
            "contrast_samples": [],
            "zoom_reflow": {},
            "focus_visibility": {},
            "limitations": list(LOW_VISION_LIMITATIONS),
        }
