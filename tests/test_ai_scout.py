

from __future__ import annotations

import json
from pathlib import Path

from a11yway.core.ai_scout import (
    AIScoutConfig,
    build_ai_scout_markdown,
    build_ai_scout_payload,
    load_ai_scout_config,
    redact_secrets,
    run_ai_scout,
    save_ai_scout_outputs,
    select_ai_scout_findings,
)


def sample_report() -> dict:

    return {
        "tool": "A11yway",
        "version": "prototype",
        "source_file": "https://example.org/contact/",
        "source": {
            "input": "https://example.org/contact/",
            "final_url": "https://example.org/contact/",
            "type": "url",
        },
        "summary": {
            "issues_found": 1,
            "counts_by_severity": {"high": 1},
            "checks_run": ["missing_form_label", "keyboard_focus_traversal"],
        },
        "issues": [
            {
                "issue_type": "missing_form_label",
                "severity": "high",
                "message": "Form control is missing an accessible label",
                "evidence": {
                    "snippet": '<input id="email">',
                    "detected_in": "browser_dom",
                },
            }
        ],
        "browser": {
            "focus_trace": [
                {
                    "step": 1,
                    "tag": "a",
                    "accessible_name_guess": "Contact",
                    "text": "Contact",
                    "href": "/contact/",
                }
            ]
        },
        "visual_proof": {
            "screenshot_path": "reports/visual/example/page.png",
            "focus_overlay_path": "reports/visual/example/focus_path.html",
        },
        "limitations": ["It does not replace a full human accessibility audit."],
    }


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse(self.content)


class FakeChat:
    def __init__(self, content: str) -> None:
        self.completions = FakeCompletions(content)


class FakeClient:
    def __init__(self, content: str) -> None:
        self.chat = FakeChat(content)


def test_ai_scout_disabled_through_env() -> None:
    config = load_ai_scout_config(
        {
            "A11YWAY_AI_SCOUT_ENABLED": "false",
            "GROQ_API_KEY": "secret-key",
        },
        dotenv_path="does-not-exist.env",
    )

    result = run_ai_scout(sample_report(), config=config)

    assert result["enabled"] is False
    assert result["status"] == "unavailable"
    assert "disabled" in result["reason"]


def test_ai_scout_enabled_missing_api_key() -> None:
    config = AIScoutConfig(enabled=True, api_key="")

    result = run_ai_scout(sample_report(), config=config)

    assert result["enabled"] is True
    assert result["status"] == "failed"
    assert "GROQ_API_KEY" in result["reason"]


def test_ai_scout_enabled_with_mocked_groq_response() -> None:
    response = json.dumps(
        {
            "summary": "AI Scout suggested one possible barrier for review.",
            "ai_suggested_observations": [
                {
                    "observation": "The unlabeled email field may be hard to identify.",
                    "why_it_may_matter": "Keyboard-only or low-vision users may need a visible label.",
                    "related_deterministic_evidence": "missing_form_label on input#email",
                    "human_review_needed": True,
                    "confidence": "AI plus deterministic support",
                }
            ],
            "outreach_notes": ["Ask for expert feedback on the evidence."],
            "limitations": ["AI Scout findings are suggestions and need human review."],
        }
    )
    fake_client = FakeClient(response)
    config = AIScoutConfig(enabled=True, api_key="secret-key")

    result = run_ai_scout(
        sample_report(),
        target_name="Example",
        workflow_tested="Reach contact page",
        outreach_tone="expert feedback request",
        config=config,
        client_factory=lambda _api_key: fake_client,
    )

    assert result["status"] == "ok"
    assert result["mode"] == "suggest_only"
    assert result["ai_suggested_observations"][0]["confidence"] == (
        "AI plus deterministic support"
    )
    call = fake_client.chat.completions.calls[0]
    assert call["model"] == "llama-3.3-70b-versatile"
    assert "AI Scout for A11yway" in call["messages"][0]["content"]
    assert "secret-key" not in json.dumps(result)


def test_ai_scout_json_parsing_fallback() -> None:
    config = AIScoutConfig(enabled=True, api_key="secret-key")
    fake_client = FakeClient("not json at all")

    result = run_ai_scout(
        sample_report(),
        config=config,
        client_factory=lambda _api_key: fake_client,
    )

    assert result["status"] == "failed"
    assert "JSON" in result["reason"]
    assert "secret-key" not in json.dumps(result)


def test_ai_scout_secret_redaction() -> None:
    data = {
        "message": "request failed for secret-key",
        "api_key": "secret-key",
        "items": ["secret-key"],
    }

    redacted = redact_secrets(data, ["secret-key"])

    assert redacted["message"] == "request failed for [REDACTED]"
    assert "api_key" not in redacted
    assert redacted["items"] == ["[REDACTED]"]


def test_ai_scout_report_file_creation(tmp_path: Path) -> None:
    result = {
        "enabled": True,
        "mode": "suggest_only",
        "model": "llama-3.3-70b-versatile",
        "status": "ok",
        "summary": "AI Scout suggested one possible barrier.",
        "ai_suggested_observations": [],
        "outreach_notes": [],
        "limitations": ["AI Scout findings are suggestions and need human review."],
    }

    paths = save_ai_scout_outputs(result, tmp_path / "example")

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()
    assert "### What the AI Found" in Path(paths["markdown"]).read_text(
        encoding="utf-8"
    )
    assert json.loads(Path(paths["json"]).read_text(encoding="utf-8"))["status"] == "ok"


def test_ai_scout_payload_is_concise() -> None:
    payload = build_ai_scout_payload(sample_report(), target_name="Example")

    assert payload["target_name"] == "Example"
    assert payload["deterministic_findings"][0]["evidence"]["snippet"] == '<input id="email">'
    assert "html" not in payload


def test_ai_scout_prioritizes_evidence_sources_and_severity() -> None:
    issues = [
        {
            "issue_type": "missing_alt_text",
            "severity": "high",
            "message": "Static issue",
            "evidence": {"snippet": "<img>"},
        },
        {
            "issue_type": "low_contrast_text",
            "severity": "high",
            "message": "Low vision issue",
            "evidence": {"detected_in": "low_vision"},
        },
        {
            "issue_type": "missing_form_label",
            "severity": "high",
            "message": "Rendered DOM issue",
            "evidence": {"detected_in": "browser_dom"},
        },
        {
            "issue_type": "browser_focus_on_hidden_element",
            "severity": "medium",
            "message": "Browser issue",
            "evidence": {"detected_in": "browser_interaction"},
        },
        {
            "issue_type": "axe_label",
            "severity": "low",
            "message": "Axe issue",
            "evidence": {"detected_in": "axe_core"},
        },
        {
            "issue_type": "axe_color_contrast",
            "severity": "high",
            "message": "High axe issue",
            "evidence": {"detected_in": "axe_core"},
        },
    ]

    selected = select_ai_scout_findings(issues)

    assert [issue["issue_type"] for issue in selected] == [
        "axe_color_contrast",
        "axe_label",
        "browser_focus_on_hidden_element",
        "missing_form_label",
        "low_contrast_text",
        "missing_alt_text",
    ]


def test_ai_scout_payload_caps_findings_at_25() -> None:
    report = sample_report()
    report["issues"] = [
        {
            "issue_type": f"static_{index}",
            "severity": "low",
            "message": f"Static issue {index}",
            "evidence": {"snippet": f"<span>{index}</span>"},
        }
        for index in range(30)
    ]

    payload = build_ai_scout_payload(report, target_name="Example")

    assert len(payload["deterministic_findings"]) == 25


def test_ai_scout_markdown_for_failed_run_uses_required_text() -> None:
    markdown = build_ai_scout_markdown(
        {
            "enabled": True,
            "mode": "suggest_only",
            "model": "llama-3.3-70b-versatile",
            "status": "failed",
            "reason": "model unavailable",
            "limitations": [],
        }
    )

    assert "### What the AI Found" in markdown
    assert "No AI findings should be inferred from this run." in markdown
