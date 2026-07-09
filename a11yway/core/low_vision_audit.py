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
    "zoom_reflow_200_400",
    "focus_visibility",
]

LOW_VISION_LIMITATIONS = [
    "Low-vision checks use browser-computed styles and conservative heuristics.",
    "Rendered color contrast checks do not prove full WCAG conformance.",
    "Zoom checks emulate browser zoom through the equivalent CSS viewport widths (WCAG 1.4.10 uses 320 CSS px at 400%); gradients, images, and intentional horizontal-scroll regions need manual review.",
    "Focus indicator detection may miss custom focus styles.",
]

# Zoom passes: browser zoom at N% lays a page out at base_width / N CSS px,
# which is how WCAG 1.4.10 defines its 320 px reflow reference (1280 / 4).
ZOOM_BASE_VIEWPORT = {"width": 1280, "height": 1024}
ZOOM_LEVELS = [200, 400]

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

_ZOOM_CHECKS_SCRIPT = r"""
() => {
  const TOL = 8;
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const describe = (el) => {
    const rect = el.getBoundingClientRect();
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      text: clean(el.innerText || el.textContent).slice(0, 60),
      box: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height)
      }
    };
  };
  const isVisible = (el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return (
      rect.width > 0 && rect.height > 0 &&
      style.visibility !== 'hidden' && style.display !== 'none'
    );
  };

  const viewportWidth = document.documentElement.clientWidth;
  const scrollWidth = Math.max(
    document.documentElement.scrollWidth, document.body.scrollWidth
  );
  const reachableRight = Math.max(viewportWidth, scrollWidth);

  // Clipped content: text or controls whose right edge sits beyond every
  // reachable area (either past the document's scrollable width, or past a
  // clipping overflow-hidden ancestor).
  const contentSelector =
    'h1,h2,h3,h4,h5,h6,p,li,a[href],button,input:not([type="hidden"]),select,textarea';
  const clipped = [];
  for (const el of document.querySelectorAll(contentSelector)) {
    if (clipped.length >= 5 || !isVisible(el)) continue;
    const rect = el.getBoundingClientRect();
    let clippedBy = null;
    if (rect.right > reachableRight + TOL) {
      clippedBy = 'document';
    } else {
      let node = el.parentElement;
      while (node && node !== document.body) {
        const style = window.getComputedStyle(node);
        if (['hidden', 'clip'].includes(style.overflowX)) {
          const nodeRect = node.getBoundingClientRect();
          if (rect.right > nodeRect.right + TOL) {
            clippedBy = 'container';
          }
          break;
        }
        node = node.parentElement;
      }
    }
    if (clippedBy) {
      const item = describe(el);
      item.clipped_by = clippedBy;
      clipped.push(item);
    }
  }

  // Overlapping interactive elements: unrelated controls whose boxes
  // intersect by more than a quarter of the smaller control.
  const interactive = Array.from(document.querySelectorAll(
    'a[href], button, input:not([type="hidden"]), select, textarea'
  )).filter(isVisible).slice(0, 40);
  const overlaps = [];
  for (let i = 0; i < interactive.length && overlaps.length < 5; i += 1) {
    for (let j = i + 1; j < interactive.length && overlaps.length < 5; j += 1) {
      const a = interactive[i];
      const b = interactive[j];
      if (a.contains(b) || b.contains(a)) continue;
      const ra = a.getBoundingClientRect();
      const rb = b.getBoundingClientRect();
      const xOverlap = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      const yOverlap = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (xOverlap <= 4 || yOverlap <= 4) continue;
      const overlapArea = xOverlap * yOverlap;
      const smallerArea = Math.min(ra.width * ra.height, rb.width * rb.height);
      if (smallerArea <= 0 || overlapArea < smallerArea * 0.25) continue;
      overlaps.push({ first: describe(a), second: describe(b) });
    }
  }

  return {
    viewport_width: viewportWidth,
    document_scroll_width: scrollWidth,
    overflow_amount: Math.max(0, scrollWidth - viewportWidth),
    clipped_elements: clipped,
    overlapping_pairs: overlaps
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


def _apply_zoom(page, zoom_percent: int) -> None:
    """Lay the page out as browser zoom at zoom_percent would.

    Browser zoom at N% renders the layout at base_width * 100 / N CSS
    pixels, which is exactly how WCAG 1.4.10 defines its 320 px reflow
    reference (1280 at 400%).
    """
    factor = zoom_percent / 100
    page.set_viewport_size(
        {
            "width": int(ZOOM_BASE_VIEWPORT["width"] / factor),
            "height": int(ZOOM_BASE_VIEWPORT["height"] / factor),
        }
    )


def _element_label(element: dict[str, Any]) -> str:
    """Describe one measured element compactly for evidence."""
    tag = element.get("tag") or "element"
    if element.get("id"):
        return f"{tag}#{element['id']}"
    text = (element.get("text") or "").strip()
    if text:
        return f'{tag} "{text[:40]}"'
    return tag


def _reflow_issues(levels: list[dict[str, Any]]) -> list[AccessibilityIssue]:
    """Build reflow findings from the per-zoom-level measurements."""
    issues: list[AccessibilityIssue] = []

    overflowing = [
        level for level in levels if int(level.get("overflow_amount", 0) or 0) > 8
    ]
    if overflowing:
        wcag_reference_hit = any(
            level["zoom_percent"] == 400 for level in overflowing
        )
        issues.append(
            _low_vision_issue(
                title="Page requires horizontal scrolling under zoom",
                issue_type="reflow_horizontal_scroll",
                severity="high" if wcag_reference_hit else "medium",
                evidence={
                    "zoom_levels": [
                        {
                            "zoom_percent": level["zoom_percent"],
                            "viewport_width": level.get("viewport_width"),
                            "document_scroll_width": level.get(
                                "document_scroll_width"
                            ),
                            "overflow_amount": level.get("overflow_amount"),
                        }
                        for level in overflowing
                    ],
                    "reason": (
                        "The document is wider than the viewport at "
                        + ", ".join(f"{level['zoom_percent']}%" for level in overflowing)
                        + " zoom, so zoomed readers must scroll horizontally "
                        "for every line (WCAG 1.4.10 reflow reference: 320 CSS "
                        "px at 400%)."
                    ),
                },
                suggested_fix=(
                    "Use responsive layout and max-width: 100% so content "
                    "reflows into one column at high zoom. Intentional "
                    "horizontal-scroll regions (data tables, maps) are "
                    "allowed by WCAG and need manual review."
                ),
            )
        )

    seen_clipped: set[str] = set()
    seen_overlaps: set[tuple[str, str]] = set()
    for level in levels:
        zoom = level["zoom_percent"]
        for element in level.get("clipped_elements", []):
            label = _element_label(element)
            if label in seen_clipped:
                continue
            seen_clipped.add(label)
            issues.append(
                _low_vision_issue(
                    title="Content is clipped outside the zoomed viewport",
                    issue_type="reflow_clipped_content",
                    severity="high",
                    evidence={
                        "tag": element.get("tag"),
                        "id": element.get("id"),
                        "text": element.get("text"),
                        "bounding_box": element.get("box"),
                        "clipped_by": element.get("clipped_by"),
                        "zoom_percent": zoom,
                        "viewport_width": level.get("viewport_width"),
                        "reason": (
                            f"At {zoom}% zoom this element extends beyond the "
                            "reachable area, so zoomed readers cannot see or "
                            "use it."
                        ),
                    },
                    suggested_fix=(
                        "Avoid fixed offsets and overflow: hidden cut-offs; "
                        "let content wrap within the viewport width."
                    ),
                )
            )
        for pair in level.get("overlapping_pairs", []):
            first_label = _element_label(pair.get("first", {}))
            second_label = _element_label(pair.get("second", {}))
            key = tuple(sorted([first_label, second_label]))
            if key in seen_overlaps:
                continue
            seen_overlaps.add(key)
            issues.append(
                _low_vision_issue(
                    title="Interactive elements overlap under zoom",
                    issue_type="reflow_overlap",
                    severity="medium",
                    evidence={
                        "first_element": first_label,
                        "first_bounding_box": pair.get("first", {}).get("box"),
                        "second_element": second_label,
                        "second_bounding_box": pair.get("second", {}).get("box"),
                        "zoom_percent": zoom,
                        "viewport_width": level.get("viewport_width"),
                        "reason": (
                            f"At {zoom}% zoom these two controls overlap, "
                            "which can hide one of them or make both hard "
                            "to activate."
                        ),
                    },
                    suggested_fix=(
                        "Let controls wrap or stack at narrow widths instead "
                        "of using absolute positions that collide under zoom."
                    ),
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

        original_viewport = page.viewport_size or dict(ZOOM_BASE_VIEWPORT)
        levels: list[dict[str, Any]] = []
        for zoom_percent in ZOOM_LEVELS:
            _apply_zoom(page, zoom_percent)
            page.wait_for_timeout(100)
            measurements = page.evaluate(_ZOOM_CHECKS_SCRIPT)
            measurements["zoom_percent"] = zoom_percent
            levels.append(measurements)

        # Legacy top-level keys mirror the 400% pass, the WCAG 1.4.10
        # reference (320 CSS px), so older report consumers keep working.
        reference = levels[-1]
        result["zoom_reflow"] = {
            "method": "browser_zoom_equivalent_viewports",
            "base_viewport": dict(ZOOM_BASE_VIEWPORT),
            "levels": levels,
            "viewport_width": reference.get("viewport_width"),
            "document_scroll_width": reference.get("document_scroll_width"),
            "overflow_amount": reference.get("overflow_amount"),
        }
        issues.extend(_reflow_issues(levels))

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
