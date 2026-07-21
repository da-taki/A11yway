

from __future__ import annotations

from pathlib import Path
from typing import Any

from a11yway.core.browser_runner import is_playwright_available, source_to_browser_url
from a11yway.core.extended_results import DETERMINISTIC, HEURISTIC, extended_issue, module_result
from a11yway.models.issue import AccessibilityIssue

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


DEVICE_PROFILES = {
    "android-small": {"viewport": {"width": 360, "height": 640}, "user_agent": "Mozilla/5.0 (Linux; Android 12) A11yway"},
    "android-large": {"viewport": {"width": 412, "height": 915}, "user_agent": "Mozilla/5.0 (Linux; Android 12) A11yway"},
    "iphone-small": {"viewport": {"width": 375, "height": 667}, "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) A11yway"},
    "iphone-large": {"viewport": {"width": 430, "height": 932}, "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) A11yway"},
    "tablet": {"viewport": {"width": 768, "height": 1024}, "user_agent": "Mozilla/5.0 (Linux; Android 12; Tablet) A11yway"},
}

MOBILE_LIMITATIONS = [
    "Playwright device emulation is not equivalent to real TalkBack or VoiceOver testing.",
    "Virtual keyboard obstruction is only inferred when layout evidence is reproducible.",
]


_MOBILE_SCRIPT = r"""
() => {
  const focusableSelector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const focusables = Array.from(document.querySelectorAll(focusableSelector)).slice(0, 120).map((el) => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    const name = (el.getAttribute('aria-label') || el.innerText || el.value || el.title || '').replace(/\s+/g, ' ').trim();
    return {
      tag: el.tagName.toLowerCase(),
      selector: el.id ? `${el.tagName.toLowerCase()}#${el.id}` : el.tagName.toLowerCase(),
      name,
      width: rect.width,
      height: rect.height,
      x: rect.x,
      y: rect.y,
      visible: rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none',
      position: style.position,
      hoverClass: (el.className || '').toString()
    };
  });
  const fixed = Array.from(document.querySelectorAll('*')).filter((el) => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return ['fixed','sticky'].includes(style.position) && rect.width > 0 && rect.height > 0;
  }).slice(0, 20).map((el) => {
    const rect = el.getBoundingClientRect();
    return { selector: el.id ? `${el.tagName.toLowerCase()}#${el.id}` : el.tagName.toLowerCase(), x: rect.x, y: rect.y, width: rect.width, height: rect.height, position: getComputedStyle(el).position };
  });
  return {
    viewport: { width: window.innerWidth, height: window.innerHeight },
    scrollWidth: document.documentElement.scrollWidth,
    scrollHeight: document.documentElement.scrollHeight,
    focusables,
    fixed,
    orientationLocked: !!document.querySelector('meta[name="screen-orientation"], meta[name="x5-orientation"]'),
    hoverDependentCount: Array.from(document.querySelectorAll('[class*="hover"], [data-hover], [onmouseover]')).length,
    mobileHiddenCount: Array.from(document.querySelectorAll('[class*="mobile"][hidden], [class*="mobile"][aria-hidden="true"]')).length
  };
}
"""


def _oriented_viewport(profile: dict[str, Any], orientation: str) -> dict[str, int]:
    viewport = dict(profile["viewport"])
    if orientation == "landscape" and viewport["height"] > viewport["width"]:
        viewport["width"], viewport["height"] = viewport["height"], viewport["width"]
    return viewport


def run_mobile_audit(
    source: str,
    *,
    device: str = "android-small",
    orientations: list[str] | None = None,
    wait_ms: int = 500,
) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    if not is_playwright_available() or sync_playwright is None:
        return issues, module_result(
            "mobile",
            "playwright_device_emulation",
            issues,
            status="unavailable",
            limitations=["Mobile checks require Playwright and a browser install."],
            capability={"status": "unavailable"},
        ).to_json()
    profile = DEVICE_PROFILES.get(device, DEVICE_PROFILES["android-small"])
    orientations = orientations or ["portrait"]
    observations = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for orientation in orientations:
                viewport = _oriented_viewport(profile, orientation)
                context = None
                try:
                    context = browser.new_context(
                        viewport=viewport,
                        user_agent=profile["user_agent"],
                        is_mobile=device != "tablet",
                        has_touch=True,
                    )
                    page = context.new_page()
                    page.goto(source_to_browser_url(source), wait_until="domcontentloaded")
                    page.wait_for_timeout(wait_ms)
                    data = page.evaluate(_MOBILE_SCRIPT)
                except Exception as error:
                    data = {
                        "device": device,
                        "orientation": orientation,
                        "viewport": viewport,
                        "error": str(error),
                    }
                    observations.append(data)
                    issues.append(
                        extended_issue(
                            module="mobile",
                            check_id="mobile_orientation_failed",
                            title="Mobile orientation audit could not complete",
                            issue_type="mobile_orientation_audit_failed",
                            severity="low",
                            source=source,
                            observed=str(error),
                            expected="The page should load reliably in the emulated mobile viewport.",
                            manual="Retry on a real device or in a browser emulator.",
                            evidence_type=HEURISTIC,
                            detection_source="playwright_mobile_emulation",
                            confidence="informational",
                            context={"device": device, "orientation": orientation},
                        )
                    )
                    continue
                finally:
                    if context is not None:
                        context.close()
                data["device"] = device
                data["orientation"] = orientation
                observations.append(data)
                if data["scrollWidth"] > data["viewport"]["width"] + 2:
                    issues.append(
                        extended_issue(
                            module="mobile",
                            check_id="viewport_overflow",
                            title="Mobile viewport has horizontal overflow",
                            issue_type="mobile_viewport_overflow",
                            severity="high",
                            source=source,
                            observed=f"scrollWidth {data['scrollWidth']} exceeds viewport {data['viewport']['width']}.",
                            expected="Content should fit the viewport without horizontal scrolling.",
                            manual="Verify at the emulated device size and on a real device when possible.",
                            evidence_type=DETERMINISTIC,
                            detection_source="playwright_mobile_emulation",
                            context={"device": device, "orientation": orientation, "viewport": data["viewport"]},
                        )
                    )
                for focusable in data["focusables"]:
                    if focusable["visible"] and (focusable["width"] < 24 or focusable["height"] < 24):
                        issues.append(
                            extended_issue(
                                module="mobile",
                                check_id="mobile_touch_target",
                                title="Mobile touch target may be too small",
                                issue_type="mobile_small_touch_target",
                                severity="medium",
                                source=source,
                                selector=focusable["selector"],
                                observed=f"Target size {focusable['width']}x{focusable['height']}.",
                                expected="Touch targets should be large enough and have adequate spacing.",
                                manual="Confirm actual hit target and spacing on mobile.",
                                evidence_type=HEURISTIC,
                                detection_source="playwright_mobile_emulation",
                                context={"device": device, "orientation": orientation},
                            )
                        )
                if data["orientationLocked"]:
                    issues.append(
                        extended_issue(
                            module="mobile",
                            check_id="orientation_restriction",
                            title="Page contains orientation restriction metadata",
                            issue_type="mobile_orientation_restriction",
                            severity="medium",
                            source=source,
                            observed="Orientation-locking metadata was found.",
                            expected="Content should support portrait and landscape unless essential.",
                            manual="Verify whether orientation is actually restricted on real devices.",
                            evidence_type=HEURISTIC,
                            detection_source="playwright_mobile_emulation",
                            context={"device": device, "orientation": orientation},
                        )
                    )
                if data["hoverDependentCount"] > 0:
                    issues.append(
                        extended_issue(
                            module="mobile",
                            check_id="hover_dependency",
                            title="Mobile layout contains hover-dependent hooks",
                            issue_type="mobile_hover_dependent_content",
                            severity="low",
                            source=source,
                            observed=f"{data['hoverDependentCount']} hover-like hooks found.",
                            expected="Touch users should not need hover to access content.",
                            manual="Confirm equivalent tap/focus interaction exists.",
                            evidence_type=HEURISTIC,
                            detection_source="playwright_mobile_emulation",
                            context={"device": device, "orientation": orientation},
                        )
                    )
        finally:
            browser.close()
    return issues, module_result(
        "mobile",
        "playwright_device_emulation",
        issues,
        artifacts={"device": device, "observations": observations},
        limitations=MOBILE_LIMITATIONS,
        capability={"status": "available_verified", "device": device},
    ).to_json()
