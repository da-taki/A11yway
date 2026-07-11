from __future__ import annotations

import pytest

from a11yway.core.passive_security_audit import PASSIVE_SECURITY_NOTE, analyze_passive_security


def _types(issues):
    return {issue.issue_type for issue in issues}


def test_passive_security_uses_only_supplied_html_and_metadata(monkeypatch) -> None:
    def blocked_network(*_args, **_kwargs):
        raise AssertionError("passive security must not make network requests")

    monkeypatch.setattr("urllib.request.urlopen", blocked_network, raising=False)

    issues, result = analyze_passive_security(
        '<script src="http://cdn.example.test/app.js"></script>',
        "https://example.test/page",
    )

    assert "security_mixed_content_script" in _types(issues)
    assert result["notice"] == PASSIVE_SECURITY_NOTE


@pytest.mark.parametrize(
    ("html", "source", "expected"),
    [
        ('<form action="http://example.test/post"></form>', "https://example.test", "security_insecure_form_action"),
        ('<input type="password">', "http://example.test/login", "security_password_on_http"),
        ("<!-- api_key=abc123 -->", "https://example.test", "security_sensitive_comment_pattern"),
        ('<script src="https://cdn.example.test/app.js"></script>', "https://example.test", "security_external_script_no_sri"),
    ],
)
def test_passive_security_flags_static_observations(html: str, source: str, expected: str) -> None:
    issues, _result = analyze_passive_security(html, source)

    assert expected in _types(issues)


def test_passive_security_respects_supplied_headers() -> None:
    _issues, result = analyze_passive_security(
        "<main>ok</main>",
        "https://example.test",
        source_metadata={
            "headers": {
                "Strict-Transport-Security": "max-age=31536000",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "X-Content-Type-Options": "nosniff",
            }
        },
    )

    assert result["module"] == "passive_security"


def test_passive_security_missing_headers_are_low_severity_review_points() -> None:
    issues, _result = analyze_passive_security("<main>ok</main>", "https://example.test")

    header_issues = [issue for issue in issues if issue.issue_type.endswith("_missing")]
    assert header_issues
    assert {issue.severity for issue in header_issues} == {"low"}
    assert {issue.confidence for issue in header_issues} == {"needs_review"}

