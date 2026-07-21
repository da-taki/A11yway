from __future__ import annotations

import json
import os
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import a11yway.web_app as web_app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_report_downloads(summary: dict, client) -> None:
    reports = summary.get("reports", {})
    _assert("JSON" in reports, "JSON report link missing")
    _assert("HTML" in reports, "HTML report link missing")

    for label, href in reports.items():
        response = client.get(f"{href}?download=1")
        _assert(response.status_code == 200, f"{label} download failed: {response.status_code}")
        _assert(response.data, f"{label} download was empty")

    json_response = client.get(f"{reports['JSON']}?download=1")
    payload = json.loads(json_response.data.decode("utf-8"))
    _assert("/app/" not in json.dumps(payload), "report exposed an absolute container path")


def _run_review(label: str, modules: list[str], client) -> dict:
    summary = web_app.run_web_review(
        "https://example.org",
        label=label,
        selected_modules=modules,
        run_id=label.replace(" ", "_").lower(),
    )
    _assert(summary["status"] == "passed", f"{label} did not pass")
    _assert_report_downloads(summary, client)
    return summary


def _module_status(summary: dict, key: str) -> str:
    for module in summary.get("module_statuses", []):
        if module.get("key") == key:
            return str(module.get("status", ""))
    return ""


def main() -> int:
    print(f"python_version={sys.version.split()[0]}")
    _assert(sys.version_info >= (3, 12), "Render image must use Python 3.12+")

    import flask
    import playwright

    print(f"flask={version('Flask')}")
    print(f"playwright={version('playwright')}")

    with sync_playwright() as manager:
        browser = manager.chromium.launch(headless=True)
        print(f"chromium={browser.version}")
        browser.close()

    os.environ["A11YWAY_WEB_BROWSER_ENABLED"] = "true"
    os.environ["A11YWAY_AI_SCOUT_ENABLED"] = "true"
    os.environ["GROQ_API_KEY"] = ""

    with tempfile.TemporaryDirectory(prefix="a11yway-render-smoke-") as tmp:
        root = Path(tmp)
        web_app.WEB_DEMO_RUNS_DIR = root / "runs"
        web_app.WEB_DEMO_CONFIG_PATH = root / "web_demo_batch_config.json"
        web_app.PROJECT_ROOT = Path.cwd()

        app = web_app.create_app()
        client = app.test_client()

        health = client.get("/health")
        _assert(health.status_code == 200, f"/health returned {health.status_code}")
        _assert(health.json["ok"] is True, "/health did not report ok")
        _assert(health.json["browser_available"] is True, "Playwright was not available")

        landing = client.get("/")
        _assert(landing.status_code == 200, f"landing returned {landing.status_code}")
        _assert(b"Run accessibility audit" in landing.data, "landing form did not render")

        quick = _run_review("render quick smoke", ["static", "indic"], client)
        browser_summary = _run_review(
            "render browser smoke",
            ["static", "browser", "keyboard"],
            client,
        )
        axe_summary = _run_review(
            "render axe smoke",
            ["static", "browser", "axe"],
            client,
        )
        ai_summary = _run_review(
            "render ai fallback smoke",
            ["static", "ai_scout"],
            client,
        )

        _assert(browser_summary["browser_used"] is True, "browser audit did not use Chromium")
        _assert(_module_status(axe_summary, "axe") == "complete", "axe did not complete")
        ai_status = ai_summary["ai_scout"]["status"]
        ai_summary_text = ai_summary["ai_scout"]["summary"]
        _assert(ai_status in {"failed", "unavailable"}, "AI Scout missing-key fallback failed")
        _assert("GROQ_API_KEY" in ai_summary_text or "disabled" in ai_summary_text.lower(), "AI fallback reason not reported")
        _assert("/app/" not in json.dumps([quick, browser_summary, axe_summary, ai_summary]), "summary exposed an absolute container path")

    print("render_docker_smoke=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
