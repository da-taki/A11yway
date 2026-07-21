

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from a11yway.core.browser_runner import is_playwright_available, source_to_browser_url
from a11yway.core.extended_results import DETERMINISTIC, HEURISTIC, extended_issue, module_result
from a11yway.models.issue import AccessibilityIssue

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


WORKFLOW_LIMITATIONS = [
    "Workflow testing executes only structured safe actions.",
    "Public-site safe mode blocks submissions, account creation, login, payment, upload, support-chat messages, destructive actions, CAPTCHA interaction, and private workflows.",
]

SAFE_ACTIONS = {
    "navigate",
    "activate link",
    "open and close menu",
    "open and close dialog",
    "select tab",
    "expand and collapse disclosure",
    "assert_text",
    "assert_focus",
    "go back",
    "reload",
}

BLOCKED_RULES = [
    ("form_submission", ("submit", "confirm", "save changes", "complete")),
    ("authentication", ("login", "log in", "sign in", "password", "two-factor")),
    ("account_creation", ("create account", "register", "sign up")),
    ("payment", ("pay", "payment", "checkout", "purchase", "donate")),
    ("file_upload", ("upload", "attach file")),
    ("message_sending", ("send", "chat", "message", "support chat")),
    ("application_submission", ("apply", "application")),
    ("destructive_action", ("delete", "remove account", "cancel subscription")),
    ("captcha_or_challenge", ("captcha", "recaptcha", "challenge")),
]


def load_workflow_config(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Workflow config must be a JSON object.")
    return data


def _host(value: str) -> str:
    parsed = urlparse(value)
    return (parsed.hostname or "").lower()


def _blocked_public_step(step: dict, *, start_url: str = "", allowed_domains: set[str] | None = None) -> dict:
    action = str(step.get("action", "")).lower()
    target = str(step.get("target", step.get("text", ""))).lower()
    combined = f"{action} {target}"
    if action not in SAFE_ACTIONS:
        return {
            "code": "unsupported_safe_action",
            "term": action or "(missing action)",
            "detail": f"Unsupported safe action: {action}",
        }
    for code, terms in BLOCKED_RULES:
        for term in terms:
            if term in combined:
                return {"code": code, "term": term, "detail": f"Matched blocked public-site term: {term}"}
    if action == "navigate":
        target_host = _host(str(step.get("target", "")))
        start_host = _host(start_url)
        allowed = set(allowed_domains or set())
        if start_host:
            allowed.add(start_host)
        if target_host and target_host not in allowed:
            return {
                "code": "external_domain",
                "term": target_host,
                "detail": f"Navigation target is outside the allowed domains: {target_host}",
            }
    return {}


def run_workflow_audit(config_path: str | Path, *, safe_public_mode: bool = True, wait_ms: int = 500) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    try:
        config = load_workflow_config(config_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        issue = extended_issue(
            module="workflow",
            check_id="workflow_config_parse",
            title="Workflow config could not be parsed",
            issue_type="workflow_config_invalid",
            severity="low",
            source=str(config_path),
            observed=str(error),
            expected="Provide a JSON object with a start_url/source and a steps array.",
            manual="Validate the workflow file before running public-site workflow checks.",
            evidence_type=DETERMINISTIC,
            detection_source="workflow_config_loader",
            confidence="informational",
            context={"error_type": type(error).__name__},
        )
        return [issue], module_result(
            "workflow",
            "safe_structured_workflow",
            [issue],
            status="failed",
            limitations=WORKFLOW_LIMITATIONS,
        ).to_json()
    source = config.get("start_url") or config.get("source") or ""
    raw_steps = config.get("steps", [])
    steps = raw_steps if isinstance(raw_steps, list) else []
    allowed_domains = {str(domain).lower() for domain in config.get("allowed_domains", [])}
    step_results = []
    if safe_public_mode or config.get("safe_mode", True):
        for index, step in enumerate(steps, start=1):
            blocked = _blocked_public_step(step, start_url=source, allowed_domains=allowed_domains)
            if blocked:
                issue = extended_issue(
                    module="workflow",
                    check_id="safe_public_block",
                    title="Workflow step blocked by safe public mode",
                    issue_type="workflow_safe_mode_blocked_action",
                    severity="high",
                    source=source,
                    observed=f"Step {index} blocked: {blocked['detail']}.",
                    expected="Use only safe navigation, menu/dialog, tab/disclosure, assertion, reload, and non-submitting fixture steps on public sites.",
                    manual="Run submitting or private workflows only against local fixtures or explicitly permitted targets.",
                    evidence_type=DETERMINISTIC,
                    detection_source="workflow_safe_mode",
                    context={
                        "step": step,
                        "step_index": index,
                        "blocked_reason_code": blocked["code"],
                        "blocked_term": blocked["term"],
                    },
                )
                issues.append(issue)
                step_results.append(
                    {
                        "index": index,
                        "status": "blocked",
                        "reason": blocked["detail"],
                        "reason_code": blocked["code"],
                        "step": step,
                    }
                )
                return issues, module_result(
                    "workflow",
                    "safe_structured_workflow",
                    issues,
                    status="blocked",
                    artifacts={"name": config.get("name", ""), "steps": step_results},
                    limitations=WORKFLOW_LIMITATIONS,
                ).to_json()
    if not is_playwright_available() or sync_playwright is None:
        return issues, module_result("workflow", "safe_structured_workflow", issues, status="unavailable", limitations=["Workflow execution requires Playwright."]).to_json()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(source_to_browser_url(source), wait_until="domcontentloaded")
            page.wait_for_timeout(wait_ms)
            for index, step in enumerate(steps, start=1):
                action = step.get("action")
                target = step.get("target") or step.get("text") or ""
                result = {"index": index, "action": action, "target": target, "status": "passed", "step": step}
                try:
                    if action in {"navigate", "activate link"}:
                        link = page.get_by_text(str(target), exact=False).first
                        link.click(timeout=1500)
                        page.wait_for_timeout(wait_ms)
                    elif action in {"open and close menu", "open and close dialog", "select tab", "expand and collapse disclosure"}:
                        page.get_by_text(str(target), exact=False).first.click(timeout=1500)
                        page.keyboard.press("Escape")
                    elif action == "assert_text":
                        if str(target).lower() not in page.locator("body").inner_text(timeout=2000).lower():
                            raise AssertionError(f"Text not found: {target}")
                    elif action == "assert_focus":
                        focused = page.evaluate("document.activeElement ? document.activeElement.outerHTML : ''")
                        if str(target) and str(target).lower() not in focused.lower():
                            raise AssertionError(f"Focused element did not include: {target}")
                    elif action == "go back":
                        page.go_back()
                    elif action == "reload":
                        page.reload(wait_until="domcontentloaded")
                    else:
                        raise AssertionError(f"Unsupported safe action: {action}")
                except Exception as error:
                    result["status"] = "failed"
                    result["reason"] = str(error)
                    issues.append(
                        extended_issue(
                            module="workflow",
                            check_id="workflow_step_blocker",
                            title="Workflow step could not be completed",
                            issue_type="workflow_step_blocked",
                            severity="high",
                            source=source,
                            observed=f"Step {index} failed: {error}",
                            expected="The workflow should be completable through safe public interactions.",
                            manual="Manually verify the step with keyboard-only navigation and screen-reader evidence.",
                            evidence_type=HEURISTIC,
                            detection_source="playwright_workflow",
                            context={"step": step, "step_index": index},
                        )
                    )
                    step_results.append(result)
                    break
                step_results.append(result)
        finally:
            browser.close()
    status = "completed" if all(step.get("status") == "passed" for step in step_results) else "blocked"
    return issues, module_result(
        "workflow",
        "safe_structured_workflow",
        issues,
        status=status,
        artifacts={"name": config.get("name", ""), "steps": step_results},
        limitations=WORKFLOW_LIMITATIONS,
    ).to_json()
