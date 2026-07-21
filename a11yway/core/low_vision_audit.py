

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from a11yway.core.browser_runner import is_playwright_available, source_to_browser_url
from a11yway.models.issue import AccessibilityIssue

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


LOW_VISION_CHECKS_RUN = [
    "rendered_color_contrast",
    "zoom_reflow_200_400",
    "focus_visibility",
    "focus_not_obscured",
    "target_size_minimum",
    "text_spacing_overrides",
]

LOW_VISION_LIMITATIONS = [
    "Low-vision checks use browser-computed styles and conservative heuristics.",
    "Rendered color contrast checks do not prove full WCAG conformance; text over images, gradients, or transparency is reported as needs_review instead of a suspected failure.",
    "Zoom checks emulate browser zoom through the equivalent CSS viewport widths (WCAG 1.4.10 uses 320 CSS px at 400%); intentional horizontal-scroll regions (data tables, code blocks, maps) are excluded when detectable.",
    "Focus indicator detection compares focused and unfocused computed styles (including pseudo-elements and parent styles) in one Chromium run; canvas-drawn or animated indicators can still be missed.",
    "Target size and focus-obscured measurements come from one run at default zoom; exceptions (equivalent controls, essential presentation) need human judgment.",
    "Text-spacing checks apply the WCAG 1.4.12 reference overrides once; JavaScript reacting to layout changes is not modeled.",
]



ZOOM_BASE_VIEWPORT = {"width": 1280, "height": 1024}
ZOOM_LEVELS = [200, 400]
REFLOW_MIN_OVERFLOW_PX = 24
REFLOW_MIN_OVERFLOW_RATIO = 0.05
FOCUS_OBSCURED_MIN_COVERAGE = 0.8

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
  // Walk the background stack. The background is "resolved" only when an
  // opaque background color is found with no background image, gradient, or
  // partial transparency layered on the way there.
  const backgroundFor = (el) => {
    let node = el;
    let imageInStack = false;
    let translucentInStack = false;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
      const style = window.getComputedStyle(node);
      if (style.backgroundImage && style.backgroundImage !== 'none') {
        imageInStack = true;
      }
      const bg = style.backgroundColor || '';
      const alphaMatch = bg.match(/rgba\([^)]*,\s*([0-9.]+)\)/);
      const alpha = alphaMatch ? Number(alphaMatch[1]) : (bg && bg !== 'transparent' ? 1 : 0);
      if (alpha >= 1) {
        return {
          color: bg,
          resolved: !imageInStack && !translucentInStack,
          image_in_stack: imageInStack
        };
      }
      if (alpha > 0) {
        translucentInStack = true;
      }
      node = node.parentElement;
    }
    return {
      color: 'rgb(255, 255, 255)',
      resolved: !imageInStack && !translucentInStack,
      image_in_stack: imageInStack
    };
  };
  return Array.from(document.querySelectorAll(selectors)).slice(0, 250).map((el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    let text = clean(el.innerText || el.textContent);
    if (!text && ['input', 'select', 'textarea'].includes(el.tagName.toLowerCase())) {
      text = clean(el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.getAttribute('name'));
    }
    const background = backgroundFor(el);
    return {
      tag: el.tagName.toLowerCase(),
      selector: pathFor(el),
      text: text.slice(0, 120),
      color: style.color,
      background_color: background.color,
      background_resolved: background.resolved,
      background_image_in_stack: background.image_in_stack,
      disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true'),
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

  // WCAG 1.4.10 allows two-dimensional content (data tables, code, maps,
  // media timelines) to scroll horizontally. Content inside such regions,
  // or inside any container that scrolls on its own, is reachable and is
  // not counted as clipped or overflowing.
  const ALLOWED_REGION_SELECTOR =
    'table, pre, code, figure, canvas, svg, [role="table"], [role="grid"], ' +
    '[data-a11yway-scroll-region]';
  const inAllowedScrollRegion = (el) => {
    if (el.closest && el.closest(ALLOWED_REGION_SELECTOR)) return true;
    let node = el.parentElement;
    while (node && node !== document.body) {
      const style = window.getComputedStyle(node);
      if (['auto', 'scroll'].includes(style.overflowX)) return true;
      node = node.parentElement;
    }
    return false;
  };

  const viewportWidth = document.documentElement.clientWidth;
  const scrollWidth = Math.max(
    document.documentElement.scrollWidth, document.body.scrollWidth
  );
  const reachableRight = Math.max(viewportWidth, scrollWidth);

  // Attribute document-level overflow to the widest offenders so Python can
  // tell intentional scroll regions from broken layout.
  const overflowSources = [];
  if (scrollWidth > viewportWidth + TOL) {
    const offenders = [];
    for (const el of document.body.querySelectorAll('*')) {
      if (offenders.length >= 200) break;
      const rect = el.getBoundingClientRect();
      if (rect.right > viewportWidth + TOL && isVisible(el)) {
        offenders.push({ el, right: rect.right });
      }
    }
    offenders.sort((a, b) => b.right - a.right);
    for (const item of offenders.slice(0, 5)) {
      const entry = describe(item.el);
      entry.allowed_scroll_region = inAllowedScrollRegion(item.el) ||
        !!(item.el.closest && item.el.closest(ALLOWED_REGION_SELECTOR));
      overflowSources.push(entry);
    }
  }

  // Clipped content: text or controls whose right edge sits beyond every
  // reachable area (either past the document's scrollable width, or past a
  // clipping overflow-hidden ancestor).
  const contentSelector =
    'h1,h2,h3,h4,h5,h6,p,li,a[href],button,input:not([type="hidden"]),select,textarea';
  const clipped = [];
  for (const el of document.querySelectorAll(contentSelector)) {
    if (clipped.length >= 5 || !isVisible(el)) continue;
    if (inAllowedScrollRegion(el)) continue;
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
  )).filter((el) => isVisible(el) && !inAllowedScrollRegion(el)).slice(0, 40);
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
    overflow_sources: overflowSources,
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
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();

  // Style properties that can visually mark focus. Captured on the element,
  // its parent (parent-highlight patterns), and its pseudo-elements
  // (indicator drawn with ::before/::after), both focused and unfocused.
  const INDICATOR_PROPS = [
    'outlineStyle', 'outlineWidth', 'outlineColor', 'outlineOffset',
    'boxShadow', 'borderTopColor', 'borderTopWidth', 'borderTopStyle',
    'borderBottomColor', 'borderLeftColor', 'borderRightColor',
    'backgroundColor', 'backgroundImage', 'color', 'textDecorationLine',
    'transform', 'filter'
  ];
  const snapshot = (target) => {
    if (!target) return null;
    const out = {};
    const style = window.getComputedStyle(target);
    for (const prop of INDICATOR_PROPS) out[prop] = style[prop];
    for (const pseudo of ['::before', '::after']) {
      const ps = window.getComputedStyle(target, pseudo);
      out[pseudo + '.content'] = ps.content;
      out[pseudo + '.boxShadow'] = ps.boxShadow;
      out[pseudo + '.backgroundColor'] = ps.backgroundColor;
      out[pseudo + '.borderTopColor'] = ps.borderTopColor;
      out[pseudo + '.opacity'] = ps.opacity;
    }
    return out;
  };

  const focusedSelf = snapshot(el);
  const focusedParent = snapshot(el.parentElement);
  let unfocusedSelf = null;
  let unfocusedParent = null;
  let comparison_available = false;
  try {
    el.blur();
    unfocusedSelf = snapshot(el);
    unfocusedParent = snapshot(el.parentElement);
    el.focus({ preventScroll: true });
    comparison_available = document.activeElement === el;
  } catch (error) {
    comparison_available = false;
  }

  const differences = [];
  if (comparison_available) {
    for (const [scope, focused, unfocused] of [
      ['self', focusedSelf, unfocusedSelf],
      ['parent', focusedParent, unfocusedParent]
    ]) {
      if (!focused || !unfocused) continue;
      for (const prop of Object.keys(focused)) {
        if (focused[prop] !== unfocused[prop]) {
          differences.push({
            scope,
            property: prop,
            focused: String(focused[prop]).slice(0, 120),
            unfocused: String(unfocused[prop]).slice(0, 120)
          });
        }
      }
    }
  }

  // Focus-obscured sampling: hit-test the focused element's box against
  // overlays. A covering element that is (or sits inside) position fixed or
  // sticky indicates a sticky header, floating widget, or banner.
  const rect = el.getBoundingClientRect();
  const inset = Math.min(4, rect.width / 4, rect.height / 4);
  const points = [
    [rect.left + rect.width / 2, rect.top + rect.height / 2],
    [rect.left + inset, rect.top + inset],
    [rect.right - inset, rect.top + inset],
    [rect.left + inset, rect.bottom - inset],
    [rect.right - inset, rect.bottom - inset]
  ];
  let coveredPoints = 0;
  let coveringLabel = null;
  let coveringPosition = null;
  const inViewport = rect.width > 0 && rect.height > 0 &&
    rect.bottom > 0 && rect.top < window.innerHeight &&
    rect.right > 0 && rect.left < window.innerWidth;
  if (inViewport) {
    for (const [x, y] of points) {
      if (x < 0 || y < 0 || x >= window.innerWidth || y >= window.innerHeight) continue;
      const hit = document.elementFromPoint(x, y);
      if (!hit || hit === el || el.contains(hit) || hit.contains(el)) continue;
      let node = hit;
      let overlay = null;
      while (node && node !== document.body) {
        const position = window.getComputedStyle(node).position;
        if (position === 'fixed' || position === 'sticky') {
          overlay = { node, position };
          break;
        }
        node = node.parentElement;
      }
      if (overlay) {
        coveredPoints += 1;
        if (!coveringLabel) {
          const overlayEl = overlay.node;
          coveringLabel = overlayEl.tagName.toLowerCase() +
            (overlayEl.id ? '#' + overlayEl.id : '') +
            (overlayEl.className && typeof overlayEl.className === 'string'
              ? '.' + overlayEl.className.split(/\s+/).slice(0, 2).join('.') : '');
          coveringPosition = overlay.position;
        }
      }
    }
  }

  const style = window.getComputedStyle(el);
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
    height: rect.height,
    comparison_available,
    focus_style_differences: differences,
    obscured: {
      in_viewport: inViewport,
      sampled_points: points.length,
      covered_points: coveredPoints,
      covering_element: coveringLabel,
      covering_position: coveringPosition,
      bounding_box: {
        x: Math.round(rect.x), y: Math.round(rect.y),
        width: Math.round(rect.width), height: Math.round(rect.height)
      }
    }
  };
}
"""

_TARGET_SIZE_SCRIPT = r"""
() => {
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const isVisible = (el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 &&
      style.visibility !== 'hidden' && style.display !== 'none';
  };
  const targets = [];
  const elements = Array.from(document.querySelectorAll(
    'a[href], button, input:not([type="hidden"]), select, textarea, ' +
    '[role="button"], [role="link"], [role="checkbox"], [role="radio"], ' +
    '[role="tab"], [role="menuitem"]'
  )).filter(isVisible).slice(0, 80);
  for (const el of elements) {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    // Inline links inside sentences are exempt from 2.5.8.
    let inlineTextLink = false;
    if (el.tagName.toLowerCase() === 'a' && style.display === 'inline') {
      const parent = el.parentElement;
      if (parent) {
        const parentText = clean(parent.textContent);
        const ownText = clean(el.textContent);
        inlineTextLink = parentText.length > ownText.length + 5;
      }
    }
    targets.push({
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      text: clean(el.innerText || el.textContent || el.getAttribute('aria-label')).slice(0, 60),
      inline_text_link: inlineTextLink,
      box: {
        x: rect.x, y: rect.y,
        width: rect.width, height: rect.height
      }
    });
  }
  return targets;
}
"""


_TEXT_SPACING_CSS = (
    "* { line-height: 1.5 !important; letter-spacing: 0.12em !important; "
    "word-spacing: 0.16em !important; } "
    "p { margin-bottom: 2em !important; }"
)

_APPLY_TEXT_SPACING_SCRIPT = r"""
(css) => {
  const style = document.createElement('style');
  style.id = 'a11yway-text-spacing-override';
  style.textContent = css;
  document.head.appendChild(style);
}
"""

_REMOVE_TEXT_SPACING_SCRIPT = r"""
() => {
  const style = document.getElementById('a11yway-text-spacing-override');
  if (style) style.remove();
}
"""

_TEXT_LOSS_MEASURE_SCRIPT = r"""
() => {
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const isVisible = (el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 &&
      style.visibility !== 'hidden' && style.display !== 'none';
  };
  const labelFor = (el) => {
    const tag = el.tagName.toLowerCase();
    if (el.id) return tag + '#' + el.id;
    const text = clean(el.innerText || el.textContent).slice(0, 40);
    return text ? tag + ' "' + text + '"' : tag;
  };
  const box = (el) => {
    const rect = el.getBoundingClientRect();
    return {
      x: Math.round(rect.x), y: Math.round(rect.y),
      width: Math.round(rect.width), height: Math.round(rect.height)
    };
  };

  // Text containers that clip their own overflowing content, and controls
  // that have collapsed to nothing, indicate content loss.
  const clipped = [];
  const selector = 'h1,h2,h3,h4,h5,h6,p,li,a[href],button,label,td,th,div,span';
  let inspected = 0;
  for (const el of document.querySelectorAll(selector)) {
    if (clipped.length >= 8 || inspected >= 400) break;
    inspected += 1;
    if (!isVisible(el)) continue;
    if (!clean(el.innerText || el.textContent)) continue;
    const style = window.getComputedStyle(el);
    const clipsY = ['hidden', 'clip'].includes(style.overflowY) ||
      ['hidden', 'clip'].includes(style.overflow);
    const clipsX = ['hidden', 'clip'].includes(style.overflowX) ||
      ['hidden', 'clip'].includes(style.overflow);
    const lossY = clipsY && el.scrollHeight > el.clientHeight + 4;
    const lossX = clipsX && el.scrollWidth > el.clientWidth + 4 &&
      style.textOverflow !== 'ellipsis';
    if (lossY || lossX) {
      clipped.push({
        label: labelFor(el),
        box: box(el),
        scroll_height: el.scrollHeight,
        client_height: el.clientHeight,
        scroll_width: el.scrollWidth,
        client_width: el.clientWidth,
        direction: lossY ? 'vertical' : 'horizontal'
      });
    }
  }

  // Overlapping interactive controls.
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
      overlaps.push({
        first: labelFor(a), first_box: box(a),
        second: labelFor(b), second_box: box(b)
      });
    }
  }

  return { clipped, overlaps };
}
"""


def _parse_color(value: str) -> tuple[float, float, float, float] | None:

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

    channels = []
    for channel in color[:3]:
        value = channel / 255
        if value <= 0.03928:
            channels.append(value / 12.92)
        else:
            channels.append(((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def calculate_contrast_ratio(foreground: str, background: str) -> float | None:

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


def _sample_background_unresolved(sample: dict[str, Any]) -> bool:

    if sample.get("background_resolved") is False:
        return True
    try:
        opacity = float(sample.get("opacity", 1) or 1)
    except (TypeError, ValueError):
        opacity = 1.0
    return opacity < 1.0


def _contrast_issues(samples: list[dict[str, Any]]) -> list[AccessibilityIssue]:







    issues: list[AccessibilityIssue] = []
    seen: set[tuple[str, str]] = set()
    for sample in samples:
        if sample.get("disabled"):
            continue
        ratio = calculate_contrast_ratio(
            sample.get("color", ""),
            sample.get("background_color", ""),
        )
        sample["contrast_ratio"] = ratio
        unresolved = _sample_background_unresolved(sample) or ratio is None
        if not unresolved and ratio >= 4.5:
            continue
        if unresolved and (ratio is not None and ratio >= 4.5):



            continue
        key = (sample.get("selector", ""), sample.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        base_evidence = {
            "text": sample.get("text"),
            "tag": sample.get("tag"),
            "selector": sample.get("selector"),
            "foreground_color": sample.get("color"),
            "background_color": sample.get("background_color"),
            "contrast_ratio": ratio,
            "font_size": sample.get("font_size"),
            "font_weight": sample.get("font_weight"),
        }
        if unresolved:
            issues.append(
                _low_vision_issue(
                    title="Text contrast could not be resolved reliably",
                    issue_type="contrast_unresolved_background",
                    severity="medium",
                    evidence={
                        **base_evidence,
                        "background_image_in_stack": sample.get("background_image_in_stack"),
                        "reason": (
                            "The background stack contains an image, gradient, "
                            "or transparency, so the contrast ratio cannot be "
                            "computed from CSS colors alone. Manual "
                            "confirmation required."
                        ),
                    },
                    suggested_fix=(
                        "Measure contrast against the actual rendered "
                        "background; add a solid backing color if needed."
                    ),
                )
            )
            continue
        severity = "high" if ratio < 3.0 else "medium"
        issues.append(
            _low_vision_issue(
                title="Rendered text may have low contrast",
                issue_type="low_contrast_text",
                severity=severity,
                evidence={
                    **base_evidence,
                    "reason": "Computed foreground/background contrast is below the conservative 4.5:1 review threshold.",
                },
                suggested_fix="Increase foreground/background contrast and confirm the final design with manual review.",
            )
        )
    return issues


def _apply_zoom(page, zoom_percent: int) -> None:






    factor = zoom_percent / 100
    page.set_viewport_size(
        {
            "width": int(ZOOM_BASE_VIEWPORT["width"] / factor),
            "height": int(ZOOM_BASE_VIEWPORT["height"] / factor),
        }
    )


def _element_label(element: dict[str, Any]) -> str:

    tag = element.get("tag") or "element"
    if element.get("id"):
        return f"{tag}#{element['id']}"
    text = (element.get("text") or "").strip()
    if text:
        return f'{tag} "{text[:40]}"'
    return tag


def _overflow_is_intentional(level: dict[str, Any]) -> bool:






    sources = level.get("overflow_sources") or []
    return bool(sources) and all(
        source.get("allowed_scroll_region") for source in sources
    )


def _overflow_is_meaningful(level: dict[str, Any]) -> bool:

    overflow = int(level.get("overflow_amount", 0) or 0)
    viewport = int(level.get("viewport_width", 0) or 0)
    if overflow <= REFLOW_MIN_OVERFLOW_PX:
        return False
    if viewport and (overflow / viewport) <= REFLOW_MIN_OVERFLOW_RATIO:
        return False
    return True


def _reflow_issues(levels: list[dict[str, Any]]) -> list[AccessibilityIssue]:

    issues: list[AccessibilityIssue] = []

    overflowing = [
        level
        for level in levels
        if _overflow_is_meaningful(level)
        and not _overflow_is_intentional(level)
    ]
    if overflowing:
        wcag_reference_hit = any(
            level["zoom_percent"] == 400 for level in overflowing
        )
        has_content_loss = any(
            level.get("clipped_elements") or level.get("overlapping_pairs")
            for level in overflowing
        )
        issues.append(
            _low_vision_issue(
                title="Page requires horizontal scrolling under zoom",
                issue_type="reflow_horizontal_scroll",
                severity="high" if wcag_reference_hit and has_content_loss else "medium",
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
                        "for every line. The overflow exceeds A11yway's "
                        f"{REFLOW_MIN_OVERFLOW_PX}px / {int(REFLOW_MIN_OVERFLOW_RATIO * 100)}% "
                        "noise tolerance for scrollbars and subpixel rounding "
                        "(WCAG 1.4.10 reflow reference: 320 CSS px at 400%)."
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
        if not has_content_loss:
            issues[-1].confidence = "needs_review"

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


def _meaningful_focus_differences(info: dict[str, Any]) -> list[dict[str, Any]]:







    differences = info.get("focus_style_differences") or []
    outline_style = (info.get("outline_style") or "").lower()
    outline_width = (info.get("outline_width") or "").lower()
    outline_drawn = outline_style not in {"", "none", "hidden"} and outline_width not in {"", "0px"}
    meaningful = []
    for difference in differences:
        prop = str(difference.get("property", ""))
        if prop.startswith("outline") and difference.get("scope") == "self" and not outline_drawn:
            continue
        meaningful.append(difference)
    return meaningful


def _focus_indicator_visible(info: dict[str, Any]) -> tuple[bool, str]:







    if info.get("comparison_available"):
        if _meaningful_focus_differences(info):
            return True, "style_comparison"
        return False, "style_comparison"
    return _has_visible_focus_style(info), "heuristic_fallback"


def _focus_obscured_issue(info: dict[str, Any]) -> AccessibilityIssue | None:

    obscured = info.get("obscured") or {}
    if not obscured.get("in_viewport"):
        return None
    covered = int(obscured.get("covered_points", 0) or 0)
    total = int(obscured.get("sampled_points", 0) or 0)
    if covered == 0 or total == 0:
        return None
    coverage = covered / total
    if coverage < FOCUS_OBSCURED_MIN_COVERAGE:
        return None
    fully_covered = covered >= total
    issue = _low_vision_issue(
        title="Focused control is covered by overlaying content",
        issue_type="focus_obscured",
        severity="high" if fully_covered else "medium",
        evidence={
            "step": info.get("step"),
            "tag": info.get("tag"),
            "id": info.get("id"),
            "text": info.get("text") or info.get("aria_label"),
            "covered_points": covered,
            "sampled_points": total,
            "coverage_ratio": round(coverage, 3),
            "coverage_threshold": FOCUS_OBSCURED_MIN_COVERAGE,
            "covering_element": obscured.get("covering_element"),
            "covering_position": obscured.get("covering_position"),
            "bounding_box": obscured.get("bounding_box"),
            "reason": (
                f"While focused, {covered} of {total} sampled points of this "
                "control were covered by "
                f"{obscured.get('covering_element') or 'an overlay'} "
                f"(position: {obscured.get('covering_position')}), so a "
                "keyboard user may not see where focus is. "
                f"Coverage ratio: {round(coverage, 2)}."
                + ("" if fully_covered else " The control is only partially covered; manual confirmation required.")
            ),
        },
        suggested_fix=(
            "Use scroll-padding or scroll-margin so focused elements scroll "
            "clear of fixed overlays, or make overlays dismissible."
        ),
    )
    issue.confidence = "likely" if fully_covered else "needs_review"
    return issue


def _focus_visibility_check(page, max_tabs: int = 40) -> tuple[dict[str, Any], list[AccessibilityIssue]]:

    issues: list[AccessibilityIssue] = []
    checked: list[dict[str, Any]] = []
    flagged: set[tuple[str, str, str]] = set()
    flagged_obscured: set[tuple[str, str, str]] = set()
    comparison_used = 0
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

        obscured_issue = _focus_obscured_issue(info)
        if obscured_issue is not None and key not in flagged_obscured:
            flagged_obscured.add(key)
            issues.append(obscured_issue)

        visible, method = _focus_indicator_visible(info)
        if method == "style_comparison":
            comparison_used += 1
        if key in flagged or visible:
            continue
        flagged.add(key)
        severity = "high" if info.get("tag") in {"a", "button", "input", "select", "textarea"} else "medium"
        issue = _low_vision_issue(
            title="Focused element may not show a visible focus indicator",
            issue_type="focus_indicator_missing",
            severity=severity,
            evidence={
                "step": step,
                "tag": info.get("tag"),
                "id": info.get("id"),
                "name": info.get("name"),
                "text": info.get("text") or info.get("aria_label"),
                "detection_method": method,
                "outline_style": info.get("outline_style"),
                "outline_width": info.get("outline_width"),
                "outline_color": info.get("outline_color"),
                "box_shadow": info.get("box_shadow"),
                "border": info.get("border"),
                "reason": (
                    "Focused and unfocused computed styles were identical "
                    "(element, parent, and pseudo-elements), so no visible "
                    "focus indicator was detected."
                    if method == "style_comparison"
                    else "The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS (comparison unavailable; heuristic fallback)."
                ),
            },
            suggested_fix="Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.",
        )
        issue.confidence = "likely" if method == "style_comparison" else "needs_review"
        issues.append(issue)
    return {
        "checked_count": len(checked),
        "flagged_count": sum(1 for issue in issues if issue.issue_type == "focus_indicator_missing"),
        "obscured_count": sum(1 for issue in issues if issue.issue_type == "focus_obscured"),
        "style_comparison_stops": comparison_used,
    }, issues


def _circle_intersects_rect(
    center_x: float, center_y: float, radius: float, box: dict[str, Any]
) -> bool:

    closest_x = max(box["x"], min(center_x, box["x"] + box["width"]))
    closest_y = max(box["y"], min(center_y, box["y"] + box["height"]))
    distance_sq = (center_x - closest_x) ** 2 + (center_y - closest_y) ** 2
    return distance_sq < radius * radius


def _target_size_issues(targets: list[dict[str, Any]]) -> list[AccessibilityIssue]:








    issues: list[AccessibilityIssue] = []
    for index, target in enumerate(targets):
        if len(issues) >= 5:
            break
        box = target.get("box") or {}
        width = float(box.get("width", 0) or 0)
        height = float(box.get("height", 0) or 0)
        if width >= 24 and height >= 24:
            continue
        if target.get("inline_text_link"):
            continue
        center_x = box.get("x", 0) + width / 2
        center_y = box.get("y", 0) + height / 2
        neighbor = None
        for other_index, other in enumerate(targets):
            if other_index == index:
                continue
            if _circle_intersects_rect(center_x, center_y, 12, other.get("box") or {}):
                neighbor = other
                break
        if neighbor is None:

            continue
        label = target.get("text") or target.get("id") or target.get("tag")
        neighbor_label = neighbor.get("text") or neighbor.get("id") or neighbor.get("tag")
        issues.append(
            _low_vision_issue(
                title="Interactive target is smaller than 24x24 CSS pixels",
                issue_type="small_target_size",
                severity="medium",
                evidence={
                    "tag": target.get("tag"),
                    "id": target.get("id"),
                    "text": target.get("text"),
                    "width": round(width, 1),
                    "height": round(height, 1),
                    "bounding_box": box,
                    "nearby_target": neighbor_label,
                    "nearby_target_box": neighbor.get("box"),
                    "reason": (
                        f'Target "{label}" measures {round(width)}x{round(height)} '
                        "CSS px and a 24 px circle centered on it intersects "
                        f'the nearby target "{neighbor_label}", so the WCAG '
                        "2.5.8 spacing exception does not apply. Check the "
                        "remaining exceptions (equivalent control, essential) "
                        "manually."
                    ),
                },
                suggested_fix=(
                    "Make the target at least 24x24 CSS pixels or give it "
                    "more surrounding space."
                ),
            )
        )
    return issues


def _measurement_labels(measurement: dict[str, Any]) -> tuple[set[str], set[tuple[str, str]]]:

    clipped = {item.get("label", "") for item in measurement.get("clipped", [])}
    overlaps = {
        tuple(sorted([pair.get("first", ""), pair.get("second", "")]))
        for pair in measurement.get("overlaps", [])
    }
    return clipped, overlaps


def _text_spacing_issues(
    before: dict[str, Any], after: dict[str, Any]
) -> list[AccessibilityIssue]:





    issues: list[AccessibilityIssue] = []
    before_clipped, before_overlaps = _measurement_labels(before)

    before_boxes = {
        item.get("label", ""): item.get("box") for item in before.get("clipped", [])
    }
    for item in after.get("clipped", []):
        if len(issues) >= 5:
            break
        label = item.get("label", "")
        if label in before_clipped:
            continue
        issues.append(
            _low_vision_issue(
                title="Content breaks under WCAG text-spacing overrides",
                issue_type="text_spacing_content_loss",
                severity="high",
                evidence={
                    "element": label,
                    "direction": item.get("direction"),
                    "bounding_box_after": item.get("box"),
                    "bounding_box_before": before_boxes.get(label),
                    "scroll_height": item.get("scroll_height"),
                    "client_height": item.get("client_height"),
                    "scroll_width": item.get("scroll_width"),
                    "client_width": item.get("client_width"),
                    "reason": (
                        "After applying the WCAG 1.4.12 reference overrides "
                        "(line height 1.5, paragraph spacing 2em, letter "
                        "spacing 0.12em, word spacing 0.16em), this element "
                        "clips its own text content. Without the overrides "
                        "it did not."
                    ),
                },
                suggested_fix=(
                    "Avoid fixed heights and overflow: hidden on text "
                    "containers; let them grow with their content."
                ),
            )
        )

    for pair in after.get("overlaps", []):
        if len(issues) >= 8:
            break
        key = tuple(sorted([pair.get("first", ""), pair.get("second", "")]))
        if key in before_overlaps:
            continue
        issues.append(
            _low_vision_issue(
                title="Content breaks under WCAG text-spacing overrides",
                issue_type="text_spacing_content_loss",
                severity="high",
                evidence={
                    "first_element": pair.get("first"),
                    "first_bounding_box": pair.get("first_box"),
                    "second_element": pair.get("second"),
                    "second_bounding_box": pair.get("second_box"),
                    "reason": (
                        "After applying the WCAG 1.4.12 reference text-spacing "
                        "overrides, these two controls overlap. Without the "
                        "overrides they did not."
                    ),
                },
                suggested_fix=(
                    "Let controls wrap or grow when text spacing increases "
                    "instead of using fixed positions or heights."
                ),
            )
        )
    return issues


def run_low_vision_audit(page, source: str | None = None) -> dict[str, Any]:

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
        "target_size": {},
        "text_spacing": {},
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


        targets = page.evaluate(_TARGET_SIZE_SCRIPT)
        target_issues = _target_size_issues(targets)
        result["target_size"] = {
            "targets_measured": len(targets),
            "flagged_count": len(target_issues),
        }
        issues.extend(target_issues)


        spacing_before = page.evaluate(_TEXT_LOSS_MEASURE_SCRIPT)
        page.evaluate(_APPLY_TEXT_SPACING_SCRIPT, _TEXT_SPACING_CSS)
        page.wait_for_timeout(150)
        spacing_after = page.evaluate(_TEXT_LOSS_MEASURE_SCRIPT)
        page.evaluate(_REMOVE_TEXT_SPACING_SCRIPT)
        page.wait_for_timeout(50)
        spacing_issues = _text_spacing_issues(spacing_before, spacing_after)
        result["text_spacing"] = {
            "overrides": _TEXT_SPACING_CSS,
            "clipped_before": len(spacing_before.get("clipped", [])),
            "clipped_after": len(spacing_after.get("clipped", [])),
            "overlaps_before": len(spacing_before.get("overlaps", [])),
            "overlaps_after": len(spacing_after.get("overlaps", [])),
            "flagged_count": len(spacing_issues),
        }
        issues.extend(spacing_issues)


        focus_visibility, focus_issues = _focus_visibility_check(page)
        result["focus_visibility"] = focus_visibility
        issues.extend(focus_issues)

        result["issues"] = issues
        result["success"] = True
    except Exception as error:
        result["error"] = str(error).strip().splitlines()[0][:300]
        result["success"] = False
    return result


def run_low_vision_audit_for_source(
    source: str,
    wait_ms: int = 500,
) -> dict[str, Any]:

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
            "target_size": {},
            "text_spacing": {},
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
    except Exception as error:
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
            "target_size": {},
            "text_spacing": {},
            "limitations": list(LOW_VISION_LIMITATIONS),
        }
