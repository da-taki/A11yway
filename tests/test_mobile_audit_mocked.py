from __future__ import annotations

import pytest

from a11yway.core.mobile_audit import run_mobile_audit


class _FakeMobilePage:
    def __init__(self, data=None, error: Exception | None = None):
        self.data = data or {}
        self.error = error

    def goto(self, *_args, **_kwargs):
        if self.error:
            raise self.error

    def wait_for_timeout(self, *_args, **_kwargs):
        return None

    def evaluate(self, *_args, **_kwargs):
        return dict(self.data)


class _FakeMobileContext:
    def __init__(self, page):
        self.page = page
        self.closed = False

    def new_page(self):
        return self.page

    def close(self):
        self.closed = True


class _FakeMobileBrowser:
    def __init__(self, pages):
        self.pages = list(pages)
        self.closed = False
        self.contexts = []

    def new_context(self, **_kwargs):
        context = _FakeMobileContext(self.pages.pop(0))
        self.contexts.append(context)
        return context

    def close(self):
        self.closed = True


class _FakeMobileChromium:
    def __init__(self, browser):
        self.browser = browser

    def launch(self, headless=True):
        return self.browser


class _FakeMobilePlaywright:
    def __init__(self, browser):
        self.chromium = _FakeMobileChromium(browser)


class _FakeSyncPlaywright:
    def __init__(self, browser):
        self.browser = browser

    def __call__(self):
        return self

    def __enter__(self):
        return _FakeMobilePlaywright(self.browser)

    def __exit__(self, *_args):
        return False


def _mobile_data(**overrides):
    data = {
        "viewport": {"width": 360, "height": 640},
        "scrollWidth": 500,
        "scrollHeight": 1000,
        "focusables": [
            {
                "visible": True,
                "width": 20,
                "height": 20,
                "selector": "button#tiny",
            },
            {
                "visible": False,
                "width": 10,
                "height": 10,
                "selector": "button#hidden",
            },
        ],
        "fixed": [],
        "orientationLocked": True,
        "hoverDependentCount": 2,
        "mobileHiddenCount": 0,
    }
    data.update(overrides)
    return data


def test_mobile_audit_records_emulated_findings_and_closes_context(monkeypatch) -> None:
    browser = _FakeMobileBrowser([_FakeMobilePage(_mobile_data())])
    monkeypatch.setattr("a11yway.core.mobile_audit.is_playwright_available", lambda: True)
    monkeypatch.setattr("a11yway.core.mobile_audit.sync_playwright", _FakeSyncPlaywright(browser))

    issues, result = run_mobile_audit("fixture.html", device="android-small", orientations=["portrait"], wait_ms=1)

    assert result["status"] == "completed"
    assert browser.closed is True
    assert browser.contexts[0].closed is True
    assert {
        "mobile_viewport_overflow",
        "mobile_small_touch_target",
        "mobile_orientation_restriction",
        "mobile_hover_dependent_content",
    }.issubset({issue.issue_type for issue in issues})


def test_mobile_audit_records_orientation_failure_and_closes_context(monkeypatch) -> None:
    browser = _FakeMobileBrowser([_FakeMobilePage(error=RuntimeError("navigation failed"))])
    monkeypatch.setattr("a11yway.core.mobile_audit.is_playwright_available", lambda: True)
    monkeypatch.setattr("a11yway.core.mobile_audit.sync_playwright", _FakeSyncPlaywright(browser))

    issues, result = run_mobile_audit("fixture.html", orientations=["portrait"], wait_ms=1)

    assert result["status"] == "completed"
    assert browser.closed is True
    assert browser.contexts[0].closed is True
    assert issues[0].issue_type == "mobile_orientation_audit_failed"
    assert result["artifacts"]["observations"][0]["error"] == "navigation failed"


@pytest.mark.parametrize(
    ("device", "orientation", "expected"),
    [
        ("android-small", "portrait", {"width": 360, "height": 640}),
        ("android-small", "landscape", {"width": 640, "height": 360}),
        ("tablet", "landscape", {"width": 1024, "height": 768}),
    ],
)
def test_mobile_audit_orientation_profiles(monkeypatch, device, orientation, expected) -> None:
    browser = _FakeMobileBrowser([_FakeMobilePage(_mobile_data(scrollWidth=expected["width"], viewport=expected))])
    monkeypatch.setattr("a11yway.core.mobile_audit.is_playwright_available", lambda: True)
    monkeypatch.setattr("a11yway.core.mobile_audit.sync_playwright", _FakeSyncPlaywright(browser))

    _issues, result = run_mobile_audit("fixture.html", device=device, orientations=[orientation], wait_ms=1)

    assert result["artifacts"]["observations"][0]["viewport"] == expected

