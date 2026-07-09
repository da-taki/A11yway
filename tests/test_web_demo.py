"""Tests for the A11yway Flask web demo helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import a11yway.web_app as web_app


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0",
        "http://169.254.169.254/latest/meta-data",
        "file:///etc/passwd",
        "ftp://example.org",
        "javascript:alert(1)",
        "data:text/html,hello",
        "https://user:pass@example.org",
        "http://intranet",
    ],
)
def test_url_validation_blocks_unsafe_urls(url: str) -> None:
    result = web_app.validate_public_url(url, resolver=lambda _host: ["93.184.216.34"])

    assert result["ok"] is False


def test_url_validation_allows_public_http_url() -> None:
    result = web_app.validate_public_url(
        "https://example.org/page",
        resolver=lambda _host: ["93.184.216.34"],
    )

    assert result["ok"] is True


def test_web_run_creates_batch_config(tmp_path: Path) -> None:
    config_path = tmp_path / "reports" / "web_demo_batch_config.json"

    item = web_app.create_web_batch_config(
        "https://example.org",
        "Example",
        web_app.REVIEW_TYPES["quick"],
        config_path=config_path,
    )

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data[0]["source"] == "https://example.org"
    assert data[0]["name"] == "Example"
    assert item["id"] == "Example"


def test_report_links_are_generated_inside_demo_runs(tmp_path: Path, monkeypatch) -> None:
    runs_dir = tmp_path / "reports" / "web_demo_runs"
    report_path = runs_dir / "run-one" / "example.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(web_app, "WEB_DEMO_RUNS_DIR", runs_dir)

    app = web_app.create_app()
    with app.test_request_context("/"):
        link = web_app.report_link(report_path)
        resolved = web_app.safe_report_path("run-one/example.json")

    assert link == "/reports/run-one/example.json"
    assert resolved == report_path.resolve()
    assert web_app.safe_report_path("../secret.txt") is None


def test_missing_groq_key_does_not_crash_web_summary(tmp_path: Path, monkeypatch) -> None:
    runs_dir = tmp_path / "reports" / "web_demo_runs"
    config_path = tmp_path / "reports" / "web_demo_batch_config.json"
    monkeypatch.setattr(web_app, "WEB_DEMO_RUNS_DIR", runs_dir)
    monkeypatch.setattr(web_app, "WEB_DEMO_CONFIG_PATH", config_path)
    monkeypatch.setattr(web_app, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(web_app, "is_playwright_available", lambda: False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    def fake_run_batch(config_path_arg, out_dir, **_kwargs):
        config = json.loads(Path(config_path_arg).read_text(encoding="utf-8"))
        item_id = config[0]["id"]
        out = Path(out_dir)
        report = {
            "tool": "A11yway",
            "source_file": config[0]["source"],
            "summary": {
                "issues_found": 1,
                "counts_by_severity": {"high": 1},
                "counts_by_issue_type": {"missing_form_label": 1},
            },
            "issues": [
                {
                    "issue_type": "missing_form_label",
                    "severity": "high",
                    "message": "Form control is missing an accessible label",
                    "evidence": {},
                }
            ],
            "ai_scout": {
                "enabled": True,
                "mode": "suggest_only",
                "status": "failed",
                "summary": "AI Scout did not produce suggestions: GROQ_API_KEY is not configured.",
                "limitations": [],
            },
        }
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{item_id}.json").write_text(json.dumps(report), encoding="utf-8")
        (out / f"{item_id}.md").write_text("# Report", encoding="utf-8")
        (out / f"{item_id}.html").write_text("<h1>Report</h1>", encoding="utf-8")
        (out / "index.json").write_text(json.dumps({"sources": []}), encoding="utf-8")
        (out / "index.md").write_text("# Index", encoding="utf-8")
        (out / "evaluation_summary.md").write_text("# Summary", encoding="utf-8")
        return {"index": {"summary": {"total_issues": 1}}}

    monkeypatch.setattr(web_app, "run_batch", fake_run_batch)
    app = web_app.create_app()

    with app.test_request_context("/"):
        result = web_app.run_web_review(
            "https://example.org",
            review_type_key="ai_summary",
            label="Example",
        )

    assert result["status"] == "passed"
    assert result["ai_scout"]["status"] == "failed"
    assert "GROQ_API_KEY" in result["ai_scout"]["summary"]
    assert result["reports"]["json"].endswith(".json")
