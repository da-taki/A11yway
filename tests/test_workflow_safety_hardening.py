from __future__ import annotations

import json

import pytest

from a11yway.core.workflow_audit import run_workflow_audit


def _write_workflow(tmp_path, steps, **extra):
    path = tmp_path / "workflow.json"
    data = {"name": "workflow", "start_url": "https://example.test/start", "steps": steps}
    data.update(extra)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _first_reason_code(result: dict) -> str:
    return result["artifacts"]["steps"][0]["reason_code"]


@pytest.mark.parametrize(
    ("step", "reason_code"),
    [
        ({"action": "submit", "target": "Search"}, "unsupported_safe_action"),
        ({"action": "activate link", "target": "Log in"}, "authentication"),
        ({"action": "activate link", "target": "Create account"}, "account_creation"),
        ({"action": "activate link", "target": "Pay now"}, "payment"),
        ({"action": "activate link", "target": "Upload transcript"}, "file_upload"),
        ({"action": "activate link", "target": "Send message"}, "message_sending"),
        ({"action": "activate link", "target": "Apply now"}, "application_submission"),
        ({"action": "activate link", "target": "Delete profile"}, "destructive_action"),
        ({"action": "activate link", "target": "CAPTCHA challenge"}, "captcha_or_challenge"),
    ],
)
def test_safe_public_mode_reports_structured_block_reason(tmp_path, step, reason_code) -> None:
    workflow = _write_workflow(tmp_path, [step])

    issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    assert result["status"] == "blocked"
    assert _first_reason_code(result) == reason_code
    assert issues[0].evidence["context"]["blocked_reason_code"] == reason_code


def test_safe_public_mode_blocks_external_domain_navigation(tmp_path) -> None:
    workflow = _write_workflow(
        tmp_path,
        [{"action": "navigate", "target": "https://elsewhere.test/page"}],
    )

    _issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    assert result["status"] == "blocked"
    assert _first_reason_code(result) == "external_domain"


def test_safe_public_mode_allows_configured_navigation_domain_until_browser_layer(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("a11yway.core.workflow_audit.is_playwright_available", lambda: False)
    workflow = _write_workflow(
        tmp_path,
        [{"action": "navigate", "target": "https://elsewhere.test/page"}],
        allowed_domains=["elsewhere.test"],
    )

    _issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    assert result["status"] != "blocked" or _first_reason_code(result) != "external_domain"


@pytest.mark.parametrize(
    "step",
    [
        {"action": "assert_text", "target": "Welcome"},
        {"action": "assert_focus", "target": "button"},
        {"action": "go back"},
        {"action": "reload"},
        {"action": "open and close menu", "target": "Menu"},
        {"action": "open and close dialog", "target": "Details"},
        {"action": "select tab", "target": "Admissions"},
        {"action": "expand and collapse disclosure", "target": "More"},
    ],
)
def test_safe_action_vocabulary_is_not_blocked_by_static_guard(tmp_path, step, monkeypatch) -> None:
    monkeypatch.setattr("a11yway.core.workflow_audit.is_playwright_available", lambda: False)
    workflow = _write_workflow(tmp_path, [step])

    _issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    if result["status"] == "blocked":
        assert _first_reason_code(result) != "unsupported_safe_action"


def test_malformed_workflow_json_reports_failure(tmp_path) -> None:
    workflow = tmp_path / "workflow.json"
    workflow.write_text("{not json", encoding="utf-8")

    issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    assert result["status"] == "failed"
    assert issues[0].issue_type == "workflow_config_invalid"
    assert issues[0].confidence == "informational"


def test_non_object_workflow_json_reports_failure(tmp_path) -> None:
    workflow = tmp_path / "workflow.json"
    workflow.write_text("[]", encoding="utf-8")

    issues, result = run_workflow_audit(workflow, safe_public_mode=True)

    assert result["status"] == "failed"
    assert issues[0].issue_type == "workflow_config_invalid"


class _FakeLocator:
    @property
    def first(self):
        return self

    def click(self, timeout=0):
        return None

    def inner_text(self, timeout=0):
        return "Welcome target text"


class _FakeKeyboard:
    def __init__(self):
        self.pressed = []

    def press(self, key):
        self.pressed.append(key)


class _FakeWorkflowPage:
    def __init__(self, *, body_text="Welcome target text", focused="<button id='target'></button>"):
        self.keyboard = _FakeKeyboard()
        self.body_text = body_text
        self.focused = focused
        self.events = []

    def goto(self, *_args, **_kwargs):
        self.events.append("goto")

    def wait_for_timeout(self, *_args, **_kwargs):
        self.events.append("wait")

    def get_by_text(self, *_args, **_kwargs):
        return _FakeLocator()

    def locator(self, *_args, **_kwargs):
        return _FakeLocatorWithText(self.body_text)

    def evaluate(self, *_args, **_kwargs):
        return self.focused

    def go_back(self):
        self.events.append("back")

    def reload(self, **_kwargs):
        self.events.append("reload")


class _FakeLocatorWithText(_FakeLocator):
    def __init__(self, text):
        self.text = text

    def inner_text(self, timeout=0):
        return self.text


class _FakeBrowser:
    def __init__(self, page):
        self.page = page
        self.closed = False

    def new_page(self):
        return self.page

    def close(self):
        self.closed = True


class _FakeChromium:
    def __init__(self, page):
        self.page = page

    def launch(self, headless=True):
        return _FakeBrowser(self.page)


class _FakePlaywright:
    def __init__(self, page):
        self.chromium = _FakeChromium(page)


class _FakeSyncPlaywright:
    def __init__(self, page):
        self.page = page

    def __call__(self):
        return self

    def __enter__(self):
        return _FakePlaywright(self.page)

    def __exit__(self, *_args):
        return False


def test_workflow_executes_safe_actions_with_mocked_playwright(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("a11yway.core.workflow_audit.is_playwright_available", lambda: True)
    monkeypatch.setattr("a11yway.core.workflow_audit.sync_playwright", _FakeSyncPlaywright(_FakeWorkflowPage()))
    workflow = _write_workflow(
        tmp_path,
        [
            {"action": "navigate", "target": "https://example.test/next"},
            {"action": "activate link", "target": "More"},
            {"action": "open and close menu", "target": "Menu"},
            {"action": "open and close dialog", "target": "Dialog"},
            {"action": "select tab", "target": "Tab"},
            {"action": "expand and collapse disclosure", "target": "More"},
            {"action": "assert_text", "target": "target text"},
            {"action": "assert_focus", "target": "target"},
            {"action": "go back"},
            {"action": "reload"},
        ],
        allowed_domains=["example.test"],
    )

    issues, result = run_workflow_audit(workflow, safe_public_mode=True, wait_ms=1)

    assert issues == []
    assert result["status"] == "completed"
    assert len(result["artifacts"]["steps"]) == 10


@pytest.mark.parametrize(
    ("step", "page", "message"),
    [
        ({"action": "assert_text", "target": "missing"}, _FakeWorkflowPage(body_text="other"), "Text not found"),
        ({"action": "assert_focus", "target": "missing"}, _FakeWorkflowPage(focused="<button></button>"), "Focused element did not include"),
        ({"action": "custom action"}, _FakeWorkflowPage(), "Unsupported safe action"),
    ],
)
def test_workflow_records_playwright_step_failures(tmp_path, monkeypatch, step, page, message) -> None:
    monkeypatch.setattr("a11yway.core.workflow_audit.is_playwright_available", lambda: True)
    monkeypatch.setattr("a11yway.core.workflow_audit.sync_playwright", _FakeSyncPlaywright(page))
    workflow = _write_workflow(tmp_path, [step], safe_mode=False)

    issues, result = run_workflow_audit(workflow, safe_public_mode=False, wait_ms=1)

    assert result["status"] == "blocked"
    assert issues[0].issue_type == "workflow_step_blocked"
    assert message in result["artifacts"]["steps"][0]["reason"]
