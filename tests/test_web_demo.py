

from __future__ import annotations

import json
from pathlib import Path

import pytest

import a11yway.web_app as web_app


def _patch_web_runtime(monkeypatch, tmp_path: Path, html: str | None = None) -> None:
    runs_dir = tmp_path / "reports" / "web_demo_runs"
    config_path = tmp_path / "reports" / "web_demo_batch_config.json"
    monkeypatch.setattr(web_app, "WEB_DEMO_RUNS_DIR", runs_dir)
    monkeypatch.setattr(web_app, "WEB_DEMO_CONFIG_PATH", config_path)
    monkeypatch.setattr(web_app, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(web_app, "validate_redirect_chain", lambda url: {"ok": True, "error": "", "url": url})
    monkeypatch.setattr(web_app, "validate_public_url", lambda url, resolver=None: {"ok": True, "error": "", "url": url})
    monkeypatch.setattr(web_app, "is_playwright_available", lambda: False)
    monkeypatch.setattr(
        web_app,
        "load_html_source",
        lambda source: {
            "source": source,
            "source_type": "url",
            "html": html or "<html><body><h1>Example</h1><label>Name</label><input><button>Send</button></body></html>",
            "final_url": source,
            "status_code": 200,
            "content_type": "text/html",
            "error": None,
        },
    )


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


def test_landing_page_renders_accessible_form_controls() -> None:
    app = web_app.create_app()
    client = app.test_client()

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="url"' in body
    assert "Public website URL" in body
    assert "Audit preset" in body
    assert "Select A11yway modules" in body
    assert 'role="status" aria-live="polite"' in body


def test_selected_modules_from_form_forces_static_and_dedupes() -> None:
    selected = web_app.selected_modules_from_form(["forms", "forms", "ai_scout"], "custom")

    assert selected == ["forms", "ai_scout", "static"]


def test_invalid_audit_request_shows_validation_error() -> None:
    app = web_app.create_app()
    client = app.test_client()

    response = client.post("/audit", data={"url": "https://example.org", "modules": ["static"]})

    assert response.status_code == 400
    assert "Please confirm" in response.get_data(as_text=True)


def test_audit_request_status_result_and_download(tmp_path: Path, monkeypatch) -> None:
    _patch_web_runtime(monkeypatch, tmp_path)
    app = web_app.create_app()
    app.testing = True
    client = app.test_client()

    response = client.post(
        "/audit",
        data={
            "url": "https://example.org",
            "label": "Example",
            "preset": "custom",
            "modules": ["static", "forms", "indic"],
            "permission": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    run_id = response.headers["Location"].rstrip("/").split("/")[-2]
    status_response = client.get(f"/api/audits/{run_id}/status")
    assert status_response.status_code == 200
    assert status_response.get_json()["status"] == "complete"

    result_response = client.get(f"/runs/{run_id}")
    result_body = result_response.get_data(as_text=True)
    assert result_response.status_code == 200
    assert "Executive summary" in result_body
    assert "Report downloads" in result_body
    assert 'id="page-filter"' in result_body
    assert 'id="clear-filters"' in result_body
    assert "<details open>" in result_body

    summary = web_app.load_run_summary(run_id)
    download = client.get(next(iter(summary["reports"].values())) + "?download=1")
    assert download.status_code == 200


def test_run_web_review_builds_links_without_request_context(tmp_path: Path, monkeypatch) -> None:
    _patch_web_runtime(monkeypatch, tmp_path)

    result = web_app.run_web_review(
        "https://example.org",
        label="Example background",
        selected_modules=["static", "forms"],
    )

    assert result["status"] == "passed"
    assert result["reports"]["JSON"].startswith("/reports/")
    assert all(module["status"] == "complete" for module in result["module_statuses"])


def test_visual_proof_paths_are_sanitized_to_relative_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(web_app, "PROJECT_ROOT", tmp_path)
    report = {
        "visual_proof": {
            "screenshot_path": str(tmp_path / "reports" / "web_demo_runs" / "run" / "page.png"),
            "focus_overlay_path": str(tmp_path / "reports" / "web_demo_runs" / "run" / "focus_path.html"),
        }
    }

    web_app.sanitize_visual_proof_paths(report)

    assert report["visual_proof"]["screenshot_path"] == "reports/web_demo_runs/run/page.png"
    assert report["visual_proof"]["focus_overlay_path"] == "reports/web_demo_runs/run/focus_path.html"


def test_browser_mode_falls_back_when_unavailable(tmp_path: Path, monkeypatch) -> None:
    _patch_web_runtime(monkeypatch, tmp_path)
    app = web_app.create_app()
    app.testing = True
    client = app.test_client()

    response = client.post(
        "/audit",
        data={
            "url": "https://example.org",
            "preset": "custom",
            "modules": ["static", "browser", "keyboard"],
            "permission": "on",
        },
    )

    run_id = response.headers["Location"].rstrip("/").split("/")[-2]
    status = client.get(f"/api/audits/{run_id}/status").get_json()
    module_statuses = {module["key"]: module["status"] for module in status["modules"]}

    assert status["status"] == "complete"
    assert module_statuses["browser"] == "unavailable"
    assert module_statuses["keyboard"] == "unavailable"


def test_health_route_reports_ok() -> None:
    app = web_app.create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["ok"] is True


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
    assert web_app.safe_report_path("run-one/../other-run/example.json") is None

    client = app.test_client()
    assert client.get("/reports/run-one/%2e%2e/secret.txt").status_code == 404


def test_missing_groq_key_does_not_crash_web_summary(tmp_path: Path, monkeypatch) -> None:
    runs_dir = tmp_path / "reports" / "web_demo_runs"
    config_path = tmp_path / "reports" / "web_demo_batch_config.json"
    monkeypatch.setattr(web_app, "WEB_DEMO_RUNS_DIR", runs_dir)
    monkeypatch.setattr(web_app, "WEB_DEMO_CONFIG_PATH", config_path)
    monkeypatch.setattr(web_app, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(web_app, "is_playwright_available", lambda: False)
    monkeypatch.setenv("A11YWAY_AI_SCOUT_ENABLED", "true")
    monkeypatch.setenv("A11YWAY_AI_SCOUT_MODE", "suggest_only")
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setattr(
        web_app,
        "load_html_source",
        lambda source: {
            "source": source,
            "source_type": "url",
            "html": "<html><body><label>Name</label><input></body></html>",
            "final_url": source,
            "status_code": 200,
            "content_type": "text/html",
            "error": None,
        },
    )
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
    assert result["reports"]["JSON"].endswith(".json")
