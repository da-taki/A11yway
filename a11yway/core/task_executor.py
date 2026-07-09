"""Deterministic browser task execution.

This module attempts a task's browser_steps in headless Chromium using
keyboard-only interaction wherever possible: focus moves with the Tab key,
text is typed with the keyboard, and controls are activated with Enter.
The goal is honest evidence for one question: can a keyboard-only student
complete this education workflow?

The step runner is intentionally small and deterministic — no AI, no
crawling, and conservative heuristics. Playwright is optional; everything
degrades gracefully when it is missing.
"""

from __future__ import annotations

from typing import Any

from a11yway.core.announce import (
    capture_focused_announcement,
    format_announcement,
    open_announce_session,
)
from a11yway.core.browser_runner import (
    _FOCUS_INFO_SCRIPT,
    _accessible_name_guess,
    _focus_signature,
    _loop_sequence_label,
    find_focus_cycle,
    is_playwright_available,
    source_to_browser_url,
    sync_playwright,
)
from a11yway.models.issue import AccessibilityIssue
from a11yway.models.task import AccessibilityTask


TASK_EXECUTION_CHECKS_RUN = ["keyboard_task_execution"]

SUPPORTED_ACTIONS = [
    "expect_visible_text",
    "assert_visible_text",
    "wait_for_text",
    "focus_by_label_or_name",
    "focus_by_selector",
    "type_text",
    "select_first_non_empty_option",
    "activate_by_role_or_text",
    "press_key",
    "assert_url_contains",
]

# Tags a keyboard user can activate with Enter once focused.
_ACTIVATABLE_TAGS = {"button", "a", "input"}

_BODY_TEXT_SCRIPT = "() => document.body ? document.body.innerText : ''"

_ACTIVE_VALUE_SCRIPT = (
    "() => { const el = document.activeElement;"
    " return el && ('value' in el) ? String(el.value) : null; }"
)


def _normalize(value: str | None) -> str:
    """Normalize text for conservative matching."""
    if not value:
        return ""
    return " ".join(value.replace("_", " ").replace("-", " ").lower().split())


def _matches_target(info: dict, target: str) -> bool:
    """Return whether a focused element matches a step target.

    Strong signals (labels, accessible name, text) are checked first;
    id/name attributes are a weak fallback so tasks can still find fields
    the page failed to label — the missing label is reported separately.
    """
    target_norm = _normalize(target)
    if not target_norm:
        return False

    candidates = [
        _accessible_name_guess(info),
        info.get("label_text"),
        info.get("aria_label"),
        info.get("text"),
        info.get("title"),
        info.get("id"),
        info.get("name"),
    ]
    for candidate in candidates:
        candidate_norm = _normalize(candidate)
        if not candidate_norm:
            continue
        if target_norm in candidate_norm or candidate_norm in target_norm:
            return True
    return False


def _execution_issue(
    title: str,
    issue_type: str,
    severity: str,
    step: dict,
    reason: str,
    extra: dict[str, Any] | None = None,
) -> AccessibilityIssue:
    """Create a task execution issue with step evidence."""
    evidence: dict[str, Any] = {
        "detected_in": "browser_task_execution",
        "step_id": step.get("id", ""),
        "action": step.get("action", ""),
        "reason": reason,
    }
    if step.get("target"):
        evidence["target"] = step["target"]
    if extra:
        evidence.update({key: value for key, value in extra.items() if value not in ["", None]})

    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name="Keyboard Task Runner",
        evidence=evidence,
        suggested_fix="",
    )


class _StepRunner:
    """Runs one task's browser steps on an open Playwright page."""

    def __init__(self, page, max_tabs: int, announce_session=None) -> None:
        self.page = page
        self.max_tabs = max_tabs
        self.announce_session = announce_session
        self.issues: list[AccessibilityIssue] = []
        # Set by tab_search when the last search failed inside a focus loop.
        self.last_search_trap: dict | None = None

    def focus_info(self) -> dict:
        """Return details about the currently focused element."""
        return self.page.evaluate(_FOCUS_INFO_SCRIPT)

    def body_text(self) -> str:
        """Return normalized visible page text."""
        return " ".join(str(self.page.evaluate(_BODY_TEXT_SCRIPT)).split())

    def text_visible(self, target: str) -> bool:
        """Return whether target text appears in the visible page text."""
        return _normalize(target) in _normalize(self.body_text())

    def tab_search(self, target: str) -> dict | None:
        """Tab through the page looking for an element matching target.

        Starts from the current focus position and presses Tab up to
        max_tabs times, which allows a full wrap-around of typical pages.
        When the search fails inside a confirmed focus loop that never
        passes through the body, last_search_trap records the looping
        elements so the step can report a keyboard trap.
        """
        self.last_search_trap = None
        info = self.focus_info()
        if not info.get("is_body") and _matches_target(info, target):
            return info

        signatures: list[tuple] = []
        body_passed: list[bool] = []
        entries: list[dict] = []
        pending_body_pass = False
        for _press in range(self.max_tabs):
            self.page.keyboard.press("Tab")
            info = self.focus_info()
            if info.get("is_body"):
                pending_body_pass = True
                continue
            if _matches_target(info, target):
                return info
            signatures.append(_focus_signature(info))
            body_passed.append(pending_body_pass)
            pending_body_pass = False
            entries.append(info)

        period = find_focus_cycle(signatures)
        if period is not None and not any(body_passed[-2 * period :]):
            self.last_search_trap = {
                "loop_sequence": _loop_sequence_label(entries[-period:]),
                "loop_length": len(set(signatures[-period:])),
                "tab_presses": self.max_tabs,
            }
        return None

    def focus_by_selectors(self, selectors: list[str]) -> dict | None:
        """Programmatically focus the first selector that works."""
        for selector in selectors:
            try:
                handle = self.page.query_selector(selector)
                if handle is None:
                    continue
                handle.focus()
            except Exception:  # noqa: BLE001 - a bad selector should not stop the task
                continue
            info = self.focus_info()
            if not info.get("is_body"):
                return info
        return None

    def run_step(self, step: dict) -> dict:
        """Run one step and return its result record."""
        action = step.get("action", "")
        result = {
            "id": step.get("id", ""),
            "action": action,
            "target": step.get("target", ""),
            "description": step.get("description", ""),
            "status": "failed",
            "detail": "",
            "used_fallback": False,
            "announced": None,
            "blocked_reason": None,
        }

        handler = {
            "expect_visible_text": self._do_expect_visible_text,
            "assert_visible_text": self._do_expect_visible_text,
            "wait_for_text": self._do_wait_for_text,
            "focus_by_label_or_name": self._do_focus_by_label_or_name,
            "focus_by_selector": self._do_focus_by_selector,
            "type_text": self._do_type_text,
            "select_first_non_empty_option": self._do_select_first_non_empty_option,
            "activate_by_role_or_text": self._do_activate_by_role_or_text,
            "press_key": self._do_press_key,
            "assert_url_contains": self._do_assert_url_contains,
        }.get(action)

        if handler is None:
            result["detail"] = f"Unknown action: {action}"
            return result

        handler(step, result)
        result["announced"] = self._announced_after_step()
        return result

    def _announced_after_step(self) -> str | None:
        """Return what the accessibility tree announces for the element
        focused when the step finished, or None when unavailable."""
        try:
            info = self.focus_info()
        except Exception:  # noqa: BLE001 - announce data must never fail a step
            return None
        if info.get("is_body"):
            return None
        announce = capture_focused_announcement(self.announce_session)
        return format_announcement(announce) if announce else None

    def _do_expect_visible_text(self, step: dict, result: dict) -> None:
        target = step.get("target", "")
        if self.text_visible(target):
            result["status"] = "passed"
            result["detail"] = "Text is visible on the page."
        else:
            result["detail"] = f'Expected text "{target}" is not visible.'
            self.issues.append(
                _execution_issue(
                    title="Expected task content is not visible",
                    issue_type="task_expected_content_missing",
                    severity="medium",
                    step=step,
                    reason=f'The text "{target}" was not found in the visible page text.',
                )
            )

    def _do_wait_for_text(self, step: dict, result: dict) -> None:
        target = step.get("target", "")
        for _attempt in range(6):  # up to ~3 seconds
            if self.text_visible(target):
                result["status"] = "passed"
                result["detail"] = "Text appeared on the page."
                return
            self.page.wait_for_timeout(500)
        result["detail"] = f'Text "{target}" did not appear within the wait budget.'
        self.issues.append(
            _execution_issue(
                title="Expected task content did not appear",
                issue_type="task_expected_content_missing",
                severity="medium",
                step=step,
                reason=f'The text "{target}" never appeared after the previous steps.',
            )
        )

    def _do_focus_by_label_or_name(self, step: dict, result: dict) -> None:
        target = step.get("target", "")
        info = self.tab_search(target)
        if info is not None:
            result["status"] = "passed"
            result["detail"] = f"Reached with the keyboard (tag: {info.get('tag')})."
            return

        fallback = self.focus_by_selectors(step.get("fallback_selectors", []))
        if fallback is not None:
            result["status"] = "passed"
            result["used_fallback"] = True
            result["detail"] = (
                "Not reachable by Tab; focused programmatically via fallback selector."
            )
            self._record_trap_if_seen(step)
            self.issues.append(
                _execution_issue(
                    title="Task control is not reachable with the keyboard",
                    issue_type="task_control_not_keyboard_reachable",
                    severity="high",
                    step=step,
                    reason=(
                        "Tab traversal never reached this control; the task could "
                        "only continue by focusing it programmatically."
                    ),
                    extra={"tag": fallback.get("tag"), "name": fallback.get("name")},
                )
            )
            return

        if self._record_trap_if_seen(step):
            result["detail"] = (
                "Focus loops through "
                f"{self.last_search_trap['loop_sequence']} and never reaches this control."
            )
            result["blocked_reason"] = "keyboard_trap"
            return

        result["detail"] = "No matching element could be focused."
        self._record_blocked(step, "The control for this step could not be found or focused.")

    def _do_focus_by_selector(self, step: dict, result: dict) -> None:
        selectors = list(step.get("fallback_selectors", []))
        if step.get("target"):
            selectors.insert(0, step["target"])
        info = self.focus_by_selectors(selectors)
        if info is not None:
            result["status"] = "passed"
            result["detail"] = f"Focused via selector (tag: {info.get('tag')})."
            return
        result["detail"] = "No selector matched a focusable element."
        self._record_blocked(step, "No selector matched a focusable element.")

    def _do_type_text(self, step: dict, result: dict) -> None:
        value = step.get("value", "")
        info = self.focus_info()
        if info.get("is_body") or info.get("tag") not in {"input", "textarea"}:
            result["detail"] = "No text field is focused for typing."
            self._record_blocked(step, "Typing was attempted without a focused text field.")
            return

        self.page.keyboard.type(value)
        typed = self.page.evaluate(_ACTIVE_VALUE_SCRIPT)
        if typed:
            result["status"] = "passed"
            result["detail"] = "Typed with the keyboard."
        else:
            result["detail"] = "Typed text did not appear in the field."
            self._record_blocked(step, "Keyboard input did not reach the focused field.")

    def _do_select_first_non_empty_option(self, step: dict, result: dict) -> None:
        info = self.focus_info()
        if info.get("tag") != "select":
            result["detail"] = "No select element is focused."
            self._record_blocked(step, "Option selection was attempted without a focused select.")
            return

        for _press in range(5):
            value = self.page.evaluate(_ACTIVE_VALUE_SCRIPT)
            if value:
                result["status"] = "passed"
                result["detail"] = f'Selected option with ArrowDown (value: "{value}").'
                return
            self.page.keyboard.press("ArrowDown")

        value = self.page.evaluate(_ACTIVE_VALUE_SCRIPT)
        if value:
            result["status"] = "passed"
            result["detail"] = f'Selected option with ArrowDown (value: "{value}").'
            return
        result["detail"] = "ArrowDown never produced a non-empty selection."
        self._record_blocked(step, "The select has no reachable non-empty option.")

    def _do_activate_by_role_or_text(self, step: dict, result: dict) -> None:
        target = step.get("target", "")
        info = self.tab_search(target)
        if info is not None and info.get("tag") in _ACTIVATABLE_TAGS | {"select", "textarea"}:
            self.page.keyboard.press("Enter")
            result["status"] = "passed"
            result["detail"] = f"Activated with Enter (tag: {info.get('tag')})."
            return

        fallback = self.focus_by_selectors(step.get("fallback_selectors", []))
        if fallback is not None and fallback.get("tag") in _ACTIVATABLE_TAGS:
            self.page.keyboard.press("Enter")
            result["status"] = "passed"
            result["used_fallback"] = True
            result["detail"] = (
                "Not reachable by Tab; activated after programmatic focus."
            )
            self._record_trap_if_seen(step)
            self.issues.append(
                _execution_issue(
                    title="Task control is not reachable with the keyboard",
                    issue_type="task_control_not_keyboard_reachable",
                    severity="high",
                    step=step,
                    reason=(
                        "Tab traversal never reached this control; a keyboard-only "
                        "student could not activate it."
                    ),
                    extra={"tag": fallback.get("tag")},
                )
            )
            return

        if self._record_trap_if_seen(step):
            result["detail"] = (
                "Focus loops through "
                f"{self.last_search_trap['loop_sequence']} and never reaches this control."
            )
            result["blocked_reason"] = "keyboard_trap"
            return

        result["detail"] = "No keyboard-activatable control matched this step."
        self._record_blocked(
            step,
            "No focusable button, link, or submit control matching the step "
            "target could be reached and activated with the keyboard.",
        )

    def _do_press_key(self, step: dict, result: dict) -> None:
        key = step.get("value") or step.get("target") or ""
        if not key:
            result["detail"] = "No key was specified."
            return
        self.page.keyboard.press(key)
        result["status"] = "passed"
        result["detail"] = f"Pressed {key}."

    def _do_assert_url_contains(self, step: dict, result: dict) -> None:
        target = step.get("target", "")
        if target and target.lower() in self.page.url.lower():
            result["status"] = "passed"
            result["detail"] = "URL contains the expected text."
        else:
            result["detail"] = f'URL "{self.page.url}" does not contain "{target}".'
            self._record_blocked(step, "The page URL does not show the expected task progress.")

    def _record_blocked(self, step: dict, reason: str) -> None:
        """Record the high-severity issue for a blocking step failure."""
        self.issues.append(
            _execution_issue(
                title="Task step could not be completed with the keyboard",
                issue_type="task_step_blocked",
                severity="high",
                step=step,
                reason=reason,
            )
        )

    def _record_trap_if_seen(self, step: dict) -> bool:
        """Record a keyboard_trap issue when the last Tab search looped.

        Returns whether a trap was recorded, so callers can mark the step
        as blocked with reason keyboard_trap.
        """
        if not self.last_search_trap:
            return False
        self.issues.append(
            _execution_issue(
                title="Keyboard focus is trapped in a loop",
                issue_type="keyboard_trap",
                severity="high",
                step=step,
                reason=(
                    "While searching for this step's control, Tab kept cycling "
                    "through the same elements without passing through the rest "
                    "of the page."
                ),
                extra=dict(self.last_search_trap),
            )
        )
        return True


def run_task_execution(
    source: str,
    task: AccessibilityTask,
    max_tabs: int = 40,
    wait_ms: int = 500,
) -> dict:
    """Attempt a task's browser steps and return step-by-step evidence.

    Always returns a result dict; on any environment failure success is
    False with an error message so batch mode can keep going.
    """
    result: dict[str, Any] = {
        "mode": "browser_task_execution",
        "source": source,
        "task_id": task.id,
        "task_name": task.name,
        "student_profile": task.student_profile,
        "success": False,
        "error": None,
        "completed": False,
        "blocked_at_step": None,
        "blocked_reason": None,
        "steps_total": len(task.browser_steps),
        "steps_passed": 0,
        "steps": [],
        "issues": [],
        "announce_available": False,
    }

    if not task.browser_steps:
        result["error"] = "This task has no browser_steps defined."
        return result

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

                announce_session = open_announce_session(page)
                result["announce_available"] = announce_session is not None
                runner = _StepRunner(
                    page, max_tabs=max_tabs, announce_session=announce_session
                )
                blocked = False
                for step in task.browser_steps:
                    if blocked:
                        result["steps"].append(
                            {
                                "id": step.get("id", ""),
                                "action": step.get("action", ""),
                                "target": step.get("target", ""),
                                "description": step.get("description", ""),
                                "status": "skipped",
                                "detail": "Skipped because an earlier step was blocked.",
                                "used_fallback": False,
                                "announced": None,
                                "blocked_reason": None,
                            }
                        )
                        continue

                    step_result = runner.run_step(step)
                    result["steps"].append(step_result)
                    if step_result["status"] == "failed":
                        blocked = True
                        result["blocked_at_step"] = step_result["id"]
                        result["blocked_reason"] = step_result.get("blocked_reason")

                result["issues"] = runner.issues
                result["steps_passed"] = sum(
                    1 for step in result["steps"] if step["status"] == "passed"
                )
                result["completed"] = not blocked
                result["success"] = True
            finally:
                browser.close()
    except Exception as error:  # noqa: BLE001 - batch mode must survive any browser failure
        message = str(error).strip().splitlines()
        result["error"] = message[0][:300] if message else "Unknown browser error"

    return result
