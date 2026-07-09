"""Local Flask demo interface for A11yway.

The app runs one public URL per review, writes the standard batch config to
reports/web_demo_batch_config.json, and stores each run under
reports/web_demo_runs.
"""

from __future__ import annotations

import ipaddress
import json
import os
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from flask import Flask, abort, redirect, render_template, request, send_file, url_for

from a11yway.core.batch_runner import run_batch, safe_report_id
from a11yway.core.browser_runner import is_playwright_available
from a11yway.core.report_builder import save_json_report
from a11yway.core.scoring import score_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DEMO_CONFIG_PATH = PROJECT_ROOT / "reports" / "web_demo_batch_config.json"
WEB_DEMO_RUNS_DIR = PROJECT_ROOT / "reports" / "web_demo_runs"

BLOCKED_HOST_LABELS = {
    "localhost",
    "local",
    "intranet",
    "internal",
    "router",
    "gateway",
    "admin",
    "dashboard",
}
BLOCKED_HOST_SUFFIXES = (
    ".local",
    ".localhost",
    ".internal",
    ".intranet",
    ".lan",
    ".corp",
    ".home",
)


@dataclass(frozen=True)
class ReviewType:
    """Configuration for a web demo review mode."""

    key: str
    label: str
    browser: bool
    low_vision: bool
    ai_scout: bool
    max_tabs: int
    wait_ms: int
    workflow: str


REVIEW_TYPES = {
    "quick": ReviewType(
        key="quick",
        label="Quick accessibility review",
        browser=False,
        low_vision=False,
        ai_scout=False,
        max_tabs=20,
        wait_ms=800,
        workflow="Quick deterministic accessibility review",
    ),
    "full_low_vision": ReviewType(
        key="full_low_vision",
        label="Full accessibility + low-vision review",
        browser=True,
        low_vision=True,
        ai_scout=False,
        max_tabs=60,
        wait_ms=1500,
        workflow="Full accessibility and low-vision review",
    ),
    "keyboard_focus": ReviewType(
        key="keyboard_focus",
        label="Keyboard/focus review",
        browser=True,
        low_vision=False,
        ai_scout=False,
        max_tabs=60,
        wait_ms=1500,
        workflow="Keyboard and focus-path review",
    ),
    "ai_summary": ReviewType(
        key="ai_summary",
        label="AI-assisted report summary",
        browser=False,
        low_vision=False,
        ai_scout=True,
        max_tabs=20,
        wait_ms=800,
        workflow="AI-assisted suggest-only summary",
    ),
    "full_public_workflow": ReviewType(
        key="full_public_workflow",
        label="Full public workflow review",
        browser=True,
        low_vision=True,
        ai_scout=True,
        max_tabs=60,
        wait_ms=1500,
        workflow="Full public workflow accessibility review",
    ),
}


def create_app() -> Flask:
    """Build the Flask app for local and Render deployments."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("A11YWAY_WEB_SECRET", "a11yway-local-demo")

    @app.get("/")
    def home():
        return render_template(
            "web_demo/home.html",
            review_types=REVIEW_TYPES,
            submitted={},
            error="",
        )

    @app.post("/run")
    def run_review():
        form = request.form
        submitted = {
            "url": form.get("url", "").strip(),
            "label": form.get("label", "").strip(),
            "review_type": form.get("review_type", "quick"),
        }
        if form.get("permission") != "on":
            return (
                render_template(
                    "web_demo/home.html",
                    review_types=REVIEW_TYPES,
                    submitted=submitted,
                    error="Please confirm this is a public page or that you have permission to review it.",
                ),
                400,
            )

        validation = validate_public_url(submitted["url"])
        if not validation["ok"]:
            return (
                render_template(
                    "web_demo/home.html",
                    review_types=REVIEW_TYPES,
                    submitted=submitted,
                    error=validation["error"],
                ),
                400,
            )

        try:
            run_result = run_web_review(
                validation["url"],
                review_type_key=submitted["review_type"],
                label=submitted["label"],
            )
        except Exception as error:  # noqa: BLE001 - web demo should show a clean failure
            return (
                render_template(
                    "web_demo/result.html",
                    run={
                        "status": "failed",
                        "target_url": validation["url"],
                        "target_name": submitted["label"] or validation["url"],
                        "error": str(error).splitlines()[0],
                        "score": {},
                        "reports": {},
                        "top_findings": [],
                        "ai_scout": {},
                        "visual_proof": {},
                        "guardrails": guardrail_notes(),
                    },
                ),
                500,
            )

        return redirect(url_for("result", run_id=run_result["run_id"]))

    @app.get("/runs/<run_id>")
    def result(run_id: str):
        run = load_run_summary(run_id)
        if not run:
            abort(404)
        return render_template("web_demo/result.html", run=run)

    @app.get("/runs")
    def past_runs():
        return render_template("web_demo/runs.html", runs=list_recent_runs())

    @app.get("/reports/<path:relative_path>")
    def report_file(relative_path: str):
        path = safe_report_path(relative_path)
        if path is None or not path.exists() or not path.is_file():
            abort(404)
        return send_file(path, as_attachment=request.args.get("download") == "1")

    return app


def _is_blocked_ip(ip_text: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_text)
    except ValueError:
        return True
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_host_ips(hostname: str) -> list[str]:
    infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    return sorted({info[4][0] for info in infos})


def validate_public_url(url: str, resolver=_resolve_host_ips) -> dict[str, Any]:
    """Validate that a URL points to an allowed public http(s) target."""
    candidate = str(url or "").strip()
    if not candidate:
        return {"ok": False, "error": "Enter a website URL.", "url": ""}

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return {"ok": False, "error": "Only http:// and https:// URLs are allowed.", "url": candidate}
    if parsed.username or parsed.password:
        return {"ok": False, "error": "URLs with embedded usernames or passwords are not allowed.", "url": candidate}
    if not parsed.hostname:
        return {"ok": False, "error": "Enter a complete public website URL.", "url": candidate}

    hostname = parsed.hostname.rstrip(".").lower()
    labels = set(hostname.split("."))
    if labels & BLOCKED_HOST_LABELS or hostname.endswith(BLOCKED_HOST_SUFFIXES):
        return {"ok": False, "error": "Internal or private hostnames are not allowed.", "url": candidate}
    if "." not in hostname and not _looks_like_ip(hostname):
        return {"ok": False, "error": "Use a public hostname, not an internal short name.", "url": candidate}

    if _looks_like_ip(hostname):
        if _is_blocked_ip(hostname):
            return {"ok": False, "error": "Private, local, metadata, and reserved IP addresses are blocked.", "url": candidate}
        return {"ok": True, "error": "", "url": candidate}

    try:
        resolved_ips = resolver(hostname)
    except OSError:
        return {"ok": False, "error": "The hostname could not be resolved as a public website.", "url": candidate}
    if not resolved_ips:
        return {"ok": False, "error": "The hostname did not resolve to a public address.", "url": candidate}
    if any(_is_blocked_ip(ip) for ip in resolved_ips):
        return {"ok": False, "error": "The hostname resolves to a private, local, metadata, or reserved address.", "url": candidate}

    return {"ok": True, "error": "", "url": candidate}


def _looks_like_ip(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def slug_for_url(url: str, label: str = "") -> str:
    """Return a readable filesystem slug for a run."""
    if label.strip():
        return safe_report_id(label)[:60]
    parsed = urlparse(url)
    base = parsed.hostname or "website"
    path_hint = parsed.path.strip("/").replace("/", "_")
    if path_hint:
        base = f"{base}_{path_hint}"
    return safe_report_id(base)[:60]


def create_web_batch_config(
    url: str,
    label: str,
    review_type: ReviewType,
    config_path: Path = WEB_DEMO_CONFIG_PATH,
) -> dict[str, Any]:
    """Write the required single-target batch config and return its item."""
    item_id = slug_for_url(url, label)
    item = {
        "id": item_id,
        "name": label.strip() or item_id,
        "source": url,
        "workflow": review_type.workflow,
        "notes": (
            "Web demo run. Public pages only; no login, form submission, "
            "auth bypass, scraping, or security scanning."
        ),
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps([item], indent=2), encoding="utf-8")
    return item


def run_web_review(url: str, review_type_key: str = "quick", label: str = "") -> dict[str, Any]:
    """Create config, run A11yway, score results, and save web metadata."""
    review_type = REVIEW_TYPES.get(review_type_key, REVIEW_TYPES["quick"])
    now = datetime.now()
    slug = slug_for_url(url, label)
    run_id = f"{now:%Y-%m-%d_%H%M%S}_{slug}"
    run_dir = WEB_DEMO_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    item = create_web_batch_config(url, label, review_type, config_path=WEB_DEMO_CONFIG_PATH)
    (run_dir / "batch_config.json").write_text(
        WEB_DEMO_CONFIG_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    browser_requested = review_type.browser
    browser_enabled = browser_requested and os.environ.get("A11YWAY_WEB_BROWSER_ENABLED", "true").lower() not in {"0", "false", "no", "off"}
    browser_available = is_playwright_available() if browser_enabled else False
    browser = bool(browser_enabled and browser_available)
    low_vision = bool(browser and review_type.low_vision)
    fallback_notice = ""
    if browser_requested and not browser:
        fallback_notice = "Browser evidence unavailable in this deployment."

    batch_result = run_batch(
        WEB_DEMO_CONFIG_PATH,
        run_dir,
        browser=browser,
        max_tabs=review_type.max_tabs,
        wait_ms=review_type.wait_ms,
        html_reports=True,
        low_vision=low_vision,
        ai_scout=review_type.ai_scout,
    )

    run_summary = build_run_summary(
        run_id=run_id,
        run_dir=run_dir,
        item_id=item["id"],
        review_type=review_type,
        batch_result=batch_result,
        target_url=url,
        target_name=item["name"],
        fallback_notice=fallback_notice,
        browser_requested=browser_requested,
        browser_used=browser,
    )
    save_json_report(run_summary, run_dir / "web_run.json")
    return run_summary


def build_run_summary(
    run_id: str,
    run_dir: Path,
    item_id: str,
    review_type: ReviewType,
    batch_result: dict[str, Any],
    target_url: str,
    target_name: str,
    fallback_notice: str = "",
    browser_requested: bool = False,
    browser_used: bool = False,
) -> dict[str, Any]:
    """Build a compact web-facing run summary from A11yway report files."""
    report_path = run_dir / f"{item_id}.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    score = score_report(report)
    if report:
        report["score"] = score
        save_json_report(report, report_path)

    index_path = run_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["score"] = score
        save_json_report(index, index_path)

    reports = {
        "json": report_link(run_dir / f"{item_id}.json"),
        "markdown": report_link(run_dir / f"{item_id}.md"),
        "html": report_link(run_dir / f"{item_id}.html"),
        "index_json": report_link(run_dir / "index.json"),
        "index_markdown": report_link(run_dir / "index.md"),
        "evaluation_summary": report_link(run_dir / "evaluation_summary.md"),
    }
    ai_json = run_dir / f"{item_id}_ai_scout.json"
    ai_md = run_dir / f"{item_id}_ai_scout.md"
    if ai_json.exists():
        reports["ai_scout_json"] = report_link(ai_json)
    if ai_md.exists():
        reports["ai_scout_markdown"] = report_link(ai_md)

    visual_proof = report.get("visual_proof") or {}
    screenshot = visual_proof.get("screenshot_path")
    focus_overlay = visual_proof.get("focus_overlay_path")
    visual_links = {
        "screenshot_path": screenshot or "",
        "screenshot_link": report_link(PROJECT_ROOT / screenshot) if screenshot else "",
        "focus_overlay_path": focus_overlay or "",
        "focus_overlay_link": report_link(PROJECT_ROOT / focus_overlay) if focus_overlay else "",
    }

    return {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "target_url": target_url,
        "target_name": target_name,
        "review_type": review_type.label,
        "status": "passed" if report else "failed",
        "error": "",
        "config_path": WEB_DEMO_CONFIG_PATH.as_posix(),
        "output_dir": run_dir.as_posix(),
        "batch_result": batch_result,
        "score": score,
        "total_issues": score.get("total_issues", 0),
        "classification": score.get("classification", ""),
        "top_findings": top_findings(report),
        "ai_scout": report.get("ai_scout", {}),
        "reports": {key: value for key, value in reports.items() if value},
        "visual_proof": visual_links,
        "fallback_notice": fallback_notice,
        "browser_requested": browser_requested,
        "browser_used": browser_used,
        "guardrails": guardrail_notes(),
    }


def top_findings(report: dict[str, Any], limit: int = 6) -> list[dict[str, str]]:
    """Return compact top findings from a report."""
    weights = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues = sorted(
        report.get("issues", []),
        key=lambda issue: (weights.get(str(issue.get("severity", "")).lower(), 9), str(issue.get("issue_type", ""))),
    )
    return [
        {
            "severity": str(issue.get("severity", "")),
            "issue_type": str(issue.get("issue_type", "")),
            "message": str(issue.get("message", "")),
        }
        for issue in issues[:limit]
    ]


def report_link(path: Path) -> str:
    """Return a Flask URL for a report file under the web demo run folder."""
    try:
        resolved = path.resolve()
        relative = resolved.relative_to(WEB_DEMO_RUNS_DIR.resolve()).as_posix()
    except (OSError, ValueError):
        return ""
    return url_for("report_file", relative_path=relative)


def safe_report_path(relative_path: str) -> Path | None:
    """Resolve a report path while keeping file access inside web demo runs."""
    try:
        root = WEB_DEMO_RUNS_DIR.resolve()
        path = (root / relative_path).resolve()
        path.relative_to(root)
    except (OSError, ValueError):
        return None
    return path


def load_run_summary(run_id: str) -> dict[str, Any] | None:
    """Load one run summary by folder name."""
    if safe_report_id(run_id) != run_id:
        return None
    path = WEB_DEMO_RUNS_DIR / run_id / "web_run.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def list_recent_runs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent local web demo runs without using a database."""
    if not WEB_DEMO_RUNS_DIR.exists():
        return []
    runs = []
    for path in WEB_DEMO_RUNS_DIR.iterdir():
        summary_path = path / "web_run.json"
        if not path.is_dir() or not summary_path.exists():
            continue
        try:
            run = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        runs.append(run)
    runs.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return runs[:limit]


def guardrail_notes() -> list[str]:
    """Return short responsible-use notes shown in the web UI."""
    return [
        "Tests one public URL per run.",
        "Blocks localhost, private IPs, metadata IPs, internal hostnames, non-http schemes, and embedded credentials.",
        "Does not log in, bypass authentication, submit forms, create accounts, send messages, or test payment flows.",
        "Does not run vulnerability scans, exploit checks, port scans, or private-data scraping.",
        "AI Scout is suggest-only and may be unavailable without a configured Groq key.",
    ]


app = create_app()


def main() -> None:
    """Run the local Flask development server."""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
