





from __future__ import annotations

import ipaddress
import json
import os
import socket
import threading
import time
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

from a11yway.core.ai_scout import run_ai_scout, save_ai_scout_outputs
from a11yway.core.batch_runner import safe_report_id
from a11yway.core.browser_runner import is_playwright_available, merge_browser_issues, run_browser_audit
from a11yway.core.ci_output import save_junit_xml, save_sarif_report
from a11yway.core.dedup import deduplicate_issues
from a11yway.core.low_vision_audit import run_low_vision_audit_for_source
from a11yway.core.page_analyzer import analyze_html_static
from a11yway.core.passive_security_audit import analyze_passive_security
from a11yway.core.report_builder import (
    build_batch_index_report,
    build_json_report,
    save_batch_index_csv,
    save_batch_index_markdown,
    save_evaluation_summary_markdown,
    save_html_report,
    save_json_report,
    save_markdown_report,
)
from a11yway.core.scoring import score_report
from a11yway.core.source_loader import load_html_source
from a11yway.main import run_html_extended_modules


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DEMO_CONFIG_PATH = PROJECT_ROOT / "reports" / "web_demo_batch_config.json"
WEB_DEMO_RUNS_DIR = PROJECT_ROOT / "reports" / "web_demo_runs"
URL_MAX_LENGTH = 2048
MAX_REDIRECTS = 5

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


    key: str
    label: str
    browser: bool
    low_vision: bool
    ai_scout: bool
    max_tabs: int
    wait_ms: int
    workflow: str


@dataclass(frozen=True)
class AuditModule:


    key: str
    label: str
    short_label: str
    description: str
    category: str
    requires_browser: bool = False
    always_on: bool = False
    unavailable_for_url: bool = False


REVIEW_TYPES = {
    "quick": ReviewType("quick", "Quick accessibility review", False, False, False, 20, 800, "Quick deterministic accessibility review"),
    "full_low_vision": ReviewType("full_low_vision", "Full accessibility + low-vision review", True, True, False, 60, 1500, "Full accessibility and low-vision review"),
    "keyboard_focus": ReviewType("keyboard_focus", "Keyboard/focus review", True, False, False, 60, 1500, "Keyboard and focus-path review"),
    "ai_summary": ReviewType("ai_summary", "AI-assisted report summary", False, False, True, 20, 800, "AI-assisted suggest-only summary"),
    "full_public_workflow": ReviewType("full_public_workflow", "Full public workflow review", True, True, True, 60, 1500, "Full public workflow accessibility review"),
}

AUDIT_MODULES = {
    "static": AuditModule("static", "Static HTML analysis", "Static", "Parses the fetched HTML for semantic structure, labels, headings, alt text, media cues, and Indic-language markup.", "Core", always_on=True),
    "browser": AuditModule("browser", "Browser-rendered analysis", "Rendered DOM", "Loads the page in Chromium, waits for JavaScript, and re-checks the rendered DOM.", "Browser evidence", requires_browser=True),
    "keyboard": AuditModule("keyboard", "Keyboard navigation", "Keyboard", "Tabs through reachable controls and records the focus trace.", "Browser evidence", requires_browser=True),
    "focus_trap": AuditModule("focus_trap", "Keyboard trap and focus-loop detection", "Focus traps", "Uses the keyboard traversal evidence to identify focus loops, lost focus, and repeated stops.", "Browser evidence", requires_browser=True),
    "axe": AuditModule("axe", "axe-core", "axe-core", "Runs axe-core against the rendered page when the optional integration is available.", "Browser evidence", requires_browser=True),
    "screen_reader": AuditModule("screen_reader", "Chromium accessibility-tree evidence", "A11y tree", "Summarizes computed accessibility-tree announcements from browser focus evidence.", "Browser evidence", requires_browser=True),
    "low_vision": AuditModule("low_vision", "Low-vision and reflow checks", "Low vision", "Checks contrast samples, focus indicators, and 200%/400% reflow behavior.", "Visual review", requires_browser=True),
    "mobile": AuditModule("mobile", "Mobile emulation", "Mobile", "Runs Playwright device-emulation checks for mobile overflow, orientation, and touch target review.", "Visual review", requires_browser=True),
    "forms": AuditModule("forms", "Forms", "Forms", "Reviews labels, instructions, errors, grouping, and safe recovery patterns without submitting forms.", "HTML modules"),
    "components": AuditModule("components", "Components", "Components", "Reviews common custom component patterns such as dialogs, menus, disclosure controls, and tabs.", "HTML modules"),
    "media": AuditModule("media", "Media", "Media", "Checks embedded audio/video cues such as captions, controls, transcripts, and autoplay patterns.", "HTML modules"),
    "language": AuditModule("language", "Language and cognitive checks", "Language", "Reviews multilingual, bidirectional, and cognitive-load signals for human follow-up.", "HTML modules"),
    "indic": AuditModule("indic", "Indic-language checks", "Indic", "Runs the static Indic script/language checks already included in the core parser.", "HTML modules"),
    "screenshots": AuditModule("screenshots", "Screenshots", "Screenshots", "Captures a full-page screenshot when browser evidence is available.", "Evidence", requires_browser=True),
    "focus_path": AuditModule("focus_path", "Focus-path overlays", "Focus path", "Creates an HTML overlay of the keyboard focus path when browser evidence is available.", "Evidence", requires_browser=True),
    "video": AuditModule("video", "Video proof", "Video", "Video proof is supported by CLI task execution, but is unavailable for this one-page public web flow.", "Evidence", requires_browser=True, unavailable_for_url=True),
    "document": AuditModule("document", "Document auditing", "Documents", "Document auditing is available for local files in the CLI, not public page URL audits.", "Evidence", unavailable_for_url=True),
    "ai_scout": AuditModule("ai_scout", "AI Scout", "AI Scout", "Asks server-side AI Scout to summarize and prioritize deterministic findings in suggest-only mode.", "Review"),
}

PRESETS = {
    "quick": {
        "label": "Quick Check",
        "description": "Fast static review with the always-on parser and Indic checks.",
        "modules": ["static", "indic"],
    },
    "standard": {
        "label": "Standard Audit",
        "description": "Static, rendered DOM, keyboard, screenshots, forms, components, media, and language review.",
        "modules": ["static", "browser", "keyboard", "focus_trap", "forms", "components", "media", "language", "indic", "screenshots", "focus_path"],
    },
    "full": {
        "label": "Full Accessibility Review",
        "description": "All applicable accessibility modules, including axe-core, low-vision, mobile, accessibility-tree evidence, and AI Scout.",
        "modules": ["static", "browser", "keyboard", "focus_trap", "axe", "screen_reader", "low_vision", "mobile", "forms", "components", "media", "language", "indic", "screenshots", "focus_path", "ai_scout"],
    },
    "keyboard_screen_reader": {
        "label": "Keyboard and Screen Reader Evidence",
        "description": "Focus traversal, focus-loop detection, accessibility-tree evidence, screenshots, and focus overlays.",
        "modules": ["static", "browser", "keyboard", "focus_trap", "screen_reader", "screenshots", "focus_path"],
    },
    "low_vision": {
        "label": "Low-Vision Review",
        "description": "Rendered page, low-vision/reflow checks, mobile emulation, screenshots, and focus overlays.",
        "modules": ["static", "browser", "keyboard", "low_vision", "mobile", "screenshots", "focus_path"],
    },
    "custom": {
        "label": "Custom",
        "description": "Choose the exact existing modules to run.",
        "modules": ["static", "indic"],
    },
}

REVIEW_TYPE_TO_MODULES = {
    "quick": PRESETS["quick"]["modules"],
    "full_low_vision": [module for module in PRESETS["full"]["modules"] if module != "ai_scout"],
    "keyboard_focus": PRESETS["keyboard_screen_reader"]["modules"],
    "ai_summary": ["static", "indic", "ai_scout"],
    "full_public_workflow": PRESETS["full"]["modules"],
}

ACTIVE_JOBS: dict[str, threading.Thread] = {}


def create_app() -> Flask:

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("A11YWAY_WEB_SECRET", "a11yway-local-demo")

    @app.get("/")
    def home():
        return render_template(
            "web_demo/home.html",
            modules=AUDIT_MODULES,
            presets=PRESETS,
            default_modules=set(PRESETS["standard"]["modules"]),
            recent_runs=list_recent_runs(limit=4),
            browser_available=is_playwright_available(),
            submitted={},
            error="",
        )

    @app.post("/run")
    @app.post("/audit")
    def run_review():
        form = request.form
        submitted = {
            "url": form.get("url", "").strip(),
            "label": form.get("label", "").strip(),
            "preset": form.get("preset", "standard"),
            "modules": form.getlist("modules"),
            "passive_security": form.get("passive_security") == "on",
        }
        if form.get("permission") != "on":
            return render_home_error("Please confirm this is a public page or that you have permission to review it.", submitted, 400)

        validation = validate_public_url(submitted["url"])
        if not validation["ok"]:
            return render_home_error(validation["error"], submitted, 400)

        redirect_validation = validate_redirect_chain(validation["url"])
        if not redirect_validation["ok"]:
            return render_home_error(redirect_validation["error"], submitted, 400)

        selected_modules = selected_modules_from_form(submitted["modules"], submitted["preset"])
        run_id = make_run_id(validation["url"], submitted["label"])
        run_dir = WEB_DEMO_RUNS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        status = initial_status(run_id, validation["url"], submitted["label"], selected_modules, submitted["passive_security"])
        save_status(run_dir, status)

        if app.testing or os.environ.get("A11YWAY_WEB_SYNC_JOBS", "").lower() in {"1", "true", "yes", "on"}:
            _run_job(run_id, validation["url"], submitted["label"], selected_modules, submitted["passive_security"])
        else:
            thread = threading.Thread(
                target=_run_job,
                args=(run_id, validation["url"], submitted["label"], selected_modules, submitted["passive_security"]),
                daemon=True,
            )
            ACTIVE_JOBS[run_id] = thread
            thread.start()

        return redirect(url_for("audit_progress", run_id=run_id), code=303)

    @app.get("/audits/<run_id>/progress")
    def audit_progress(run_id: str):
        run = load_status(run_id)
        if not run:
            abort(404)
        return render_template("web_demo/progress.html", run=run)

    @app.get("/api/audits/<run_id>/status")
    def audit_status(run_id: str):
        run = load_status(run_id)
        if not run:
            abort(404)
        return jsonify(run)

    @app.get("/runs/<run_id>")
    def result(run_id: str):
        run = load_run_summary(run_id)
        if not run:
            status = load_status(run_id)
            if status and status.get("status") not in {"complete", "failed"}:
                return redirect(url_for("audit_progress", run_id=run_id))
            abort(404)
        return render_template("web_demo/result.html", run=run)

    @app.get("/runs")
    def past_runs():
        return render_template("web_demo/runs.html", runs=list_recent_runs())

    @app.get("/reports/<path:relative_path>")
    def report_file(relative_path: str):
        if request_path_has_traversal():
            abort(404)
        path = safe_report_path(relative_path)
        if path is None or not path.exists() or not path.is_file():
            abort(404)
        return send_file(path, as_attachment=request.args.get("download") == "1")

    @app.get("/evidence/<path:relative_path>")
    def evidence_file(relative_path: str):
        if request_path_has_traversal():
            abort(404)
        path = safe_report_path(relative_path)
        if path is None or not path.exists() or not path.is_file():
            abort(404)
        return send_file(path, as_attachment=False)

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "a11yway-web", "browser_available": is_playwright_available()})

    return app


def render_home_error(error: str, submitted: dict[str, Any], status_code: int):
    return (
        render_template(
            "web_demo/home.html",
            modules=AUDIT_MODULES,
            presets=PRESETS,
            default_modules=set(selected_modules_from_form(submitted.get("modules", []), submitted.get("preset", "standard"))),
            recent_runs=list_recent_runs(limit=4),
            browser_available=is_playwright_available(),
            submitted=submitted,
            error=error,
        ),
        status_code,
    )


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

    candidate = str(url or "").strip()
    if not candidate:
        return {"ok": False, "error": "Enter a website URL.", "url": ""}
    if len(candidate) > URL_MAX_LENGTH:
        return {"ok": False, "error": "The URL is too long for the public demo.", "url": candidate}

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return {"ok": False, "error": "Only http:// and https:// URLs are allowed.", "url": candidate}
    if parsed.username or parsed.password:
        return {"ok": False, "error": "URLs with embedded usernames or passwords are not allowed.", "url": candidate}
    if not parsed.hostname:
        return {"ok": False, "error": "Enter a complete public website URL.", "url": candidate}
    if parsed.port is not None and parsed.port not in {80, 443, 8080, 8443}:
        return {"ok": False, "error": "Only standard public web ports are allowed.", "url": candidate}

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


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_redirect_chain(url: str) -> dict[str, Any]:

    current = url
    opener = build_opener(_NoRedirect)
    for _index in range(MAX_REDIRECTS + 1):
        validation = validate_public_url(current)
        if not validation["ok"]:
            return {"ok": False, "error": f"Redirect target is not allowed: {validation['error']}", "url": current}
        request_obj = Request(current, method="HEAD", headers={"User-Agent": "A11ywayWebDemo/1.0"})
        try:
            response = opener.open(request_obj, timeout=8)
        except Exception as error:
            code = getattr(error, "code", None)
            headers = getattr(error, "headers", None)
            if code in {301, 302, 303, 307, 308} and headers:
                location = headers.get("Location")
                if not location:
                    return {"ok": False, "error": "Redirect response did not include a usable target.", "url": current}
                current = urljoin(current, location)
                continue
            if code in {405, 403}:
                return {"ok": True, "error": "", "url": current}
            return {"ok": True, "error": "", "url": current}
        else:
            final_url = response.geturl()
            response.close()
            if final_url and final_url != current:
                current = final_url
                continue
            return {"ok": True, "error": "", "url": current}
    return {"ok": False, "error": "The URL redirects too many times for the public demo.", "url": current}


def _looks_like_ip(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def slug_for_url(url: str, label: str = "") -> str:

    if label.strip():
        return safe_report_id(label)[:60]
    parsed = urlparse(url)
    base = parsed.hostname or "website"
    path_hint = parsed.path.strip("/").replace("/", "_")
    if path_hint:
        base = f"{base}_{path_hint}"
    return safe_report_id(base)[:60]


def make_run_id(url: str, label: str = "") -> str:
    return f"{datetime.now():%Y-%m-%d_%H%M%S}_{uuid.uuid4().hex[:6]}_{slug_for_url(url, label)}"


def selected_modules_from_form(module_keys: list[str], preset: str = "standard") -> list[str]:

    selected = list(module_keys or PRESETS.get(preset, PRESETS["standard"])["modules"])
    selected.append("static")
    sanitized = []
    for key in selected:
        if key in AUDIT_MODULES and key not in sanitized:
            sanitized.append(key)
    return sanitized


def create_web_batch_config(
    url: str,
    label: str,
    review_type: ReviewType,
    config_path: Path = WEB_DEMO_CONFIG_PATH,
) -> dict[str, Any]:

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


def run_web_review(
    url: str,
    review_type_key: str = "quick",
    label: str = "",
    selected_modules: list[str] | None = None,
    passive_security: bool = False,
    run_id: str | None = None,
) -> dict[str, Any]:

    modules = selected_modules or list(REVIEW_TYPE_TO_MODULES.get(review_type_key, PRESETS["quick"]["modules"]))
    run_id = run_id or make_run_id(url, label)
    status = initial_status(run_id, url, label, modules, passive_security)
    run_dir = WEB_DEMO_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    save_status(run_dir, status)
    return execute_review(run_id, url, label, modules, passive_security, status)


def initial_status(run_id: str, url: str, label: str, modules: list[str], passive_security: bool) -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    statuses = []
    for key in modules:
        module = AUDIT_MODULES[key]
        statuses.append({"key": key, "label": module.label, "status": "pending", "message": ""})
    if passive_security:
        statuses.append({"key": "passive_security", "label": "Passive security observations", "status": "pending", "message": "Separate from the accessibility score."})
    return {
        "run_id": run_id,
        "status": "queued",
        "target_url": url,
        "target_name": label.strip() or slug_for_url(url),
        "created_at": now,
        "started_at": "",
        "finished_at": "",
        "elapsed_seconds": 0,
        "current_module": "Queued",
        "progress_percent": 0,
        "messages": ["Queued audit run."],
        "warnings": [],
        "error": "",
        "error_id": "",
        "modules": statuses,
        "result_url": "",
    }


def _run_job(run_id: str, url: str, label: str, modules: list[str], passive_security: bool) -> None:
    run_dir = WEB_DEMO_RUNS_DIR / run_id
    status = load_status(run_id) or initial_status(run_id, url, label, modules, passive_security)
    try:
        execute_review(run_id, url, label, modules, passive_security, status)
    except Exception as error:
        error_id = uuid.uuid4().hex[:10]
        (run_dir / f"error_{error_id}.log").write_text(traceback.format_exc(), encoding="utf-8")
        update_status(
            run_dir,
            status,
            state="failed",
            current="Audit failed",
            message="The audit could not finish. No raw traceback is shown in the public interface.",
            error=str(error).strip().splitlines()[0][:240],
            error_id=error_id,
            progress=100,
        )
    finally:
        ACTIVE_JOBS.pop(run_id, None)


def execute_review(run_id: str, url: str, label: str, modules: list[str], passive_security: bool, status: dict[str, Any]) -> dict[str, Any]:

    start_time = time.monotonic()
    run_dir = WEB_DEMO_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    selected = set(selected_modules_from_form(modules, "custom"))
    review_type = ReviewType("custom", "Custom module audit", wants_browser(selected), "low_vision" in selected, "ai_scout" in selected, max_tabs_for(selected), wait_ms_for(selected), "Selected public-page accessibility modules")
    item = create_web_batch_config(url, label, review_type, config_path=WEB_DEMO_CONFIG_PATH)
    (run_dir / "batch_config.json").write_text(WEB_DEMO_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    update_status(run_dir, status, state="running", current="Validating public URL", message="Validated public URL and safety scope.", progress=5)
    source_result = load_html_source(url)
    if source_result.get("error"):
        mark_module(status, "static", "failed", source_result["error"])
        raise RuntimeError(source_result["error"])
    final_url = source_result.get("final_url") or url
    final_validation = validate_public_url(final_url)
    if not final_validation["ok"]:
        mark_module(status, "static", "failed", "The final fetched URL is not an allowed public target.")
        raise RuntimeError("The final fetched URL is not an allowed public target.")

    update_status(run_dir, status, current="Running static HTML analysis", message="Fetched page and started deterministic static checks.", progress=12)
    mark_module(status, "static", "running", "Parsing fetched HTML.")
    issues = analyze_html_static(source_result["html"])
    mark_module(status, "static", "complete", f"{len(issues)} static finding(s).")
    if "indic" in selected:
        mark_module(status, "indic", "complete", "Indic-language checks run inside static analysis.")

    browser_requested = wants_browser(selected)
    browser_enabled = browser_requested and os.environ.get("A11YWAY_WEB_BROWSER_ENABLED", "true").lower() not in {"0", "false", "no", "off"}
    browser_available = is_playwright_available() if browser_enabled else False
    browser = None
    browser_used = False
    low_vision = None
    fallback_notice = ""
    if browser_requested:
        for key in ["browser", "keyboard", "focus_trap", "screenshots", "focus_path", "axe", "screen_reader", "low_vision", "mobile"]:
            if key in selected:
                mark_module(status, key, "running", "Waiting for browser capability.")
        if not browser_enabled or not browser_available:
            fallback_notice = "Browser evidence unavailable in this deployment. Static and HTML-only modules still ran."
            status["warnings"].append(fallback_notice)
            for key in ["browser", "keyboard", "focus_trap", "screenshots", "focus_path", "axe", "screen_reader", "low_vision", "mobile"]:
                if key in selected:
                    mark_module(status, key, "unavailable", "Browser evidence unavailable.")
            update_status(run_dir, status, current="Browser fallback", message=fallback_notice, progress=24)
        else:
            update_status(run_dir, status, current="Running browser evidence", message="Loading rendered DOM and running keyboard traversal.", progress=24)
            visual_dir = run_dir / "visual" / item["id"] if {"screenshots", "focus_path"} & selected else None
            browser = run_browser_audit(
                url,
                max_tabs=review_type.max_tabs,
                wait_ms=review_type.wait_ms,
                visual_proof_dir=visual_dir,
                include_axe="axe" in selected,
            )
            browser_used = bool(browser.get("success"))
            before = len(issues)
            issues = merge_browser_issues(issues, browser)
            browser_added = len(issues) - before
            browser_message = f"{browser_added} browser finding(s)." if browser_used else str(browser.get("error") or "Browser audit failed.")
            for key in ["browser", "keyboard", "focus_trap"]:
                if key in selected:
                    mark_module(status, key, "complete" if browser_used else "failed", browser_message)
            if "axe" in selected:
                axe_status = (browser.get("axe") or {}).get("success")
                mark_module(status, "axe", "complete" if axe_status else "failed", "axe-core scan completed." if axe_status else (browser.get("axe") or {}).get("error", "axe-core unavailable."))
            visual = browser.get("visual_proof") or {}
            for key in ["screenshots", "focus_path"]:
                if key in selected:
                    mark_module(status, key, "complete" if visual.get("enabled") else "failed", "Evidence asset generated." if visual.get("enabled") else visual.get("error", "Visual proof unavailable."))

    if "low_vision" in selected and browser_used:
        update_status(run_dir, status, current="Checking low vision and reflow", message="Checking zoom reflow, contrast samples, and focus indicators.", progress=42)
        low_vision = run_low_vision_audit_for_source(url, wait_ms=review_type.wait_ms)
        issues.extend(low_vision.get("issues", []))
        mark_module(status, "low_vision", "complete" if low_vision.get("success") else "failed", f"{len(low_vision.get('issues', []))} low-vision finding(s).")

    update_status(run_dir, status, current="Running HTML modules", message="Running selected HTML-only and extended modules.", progress=52)
    extended_args = SimpleNamespace(
        screen_reader="screen_reader" in selected,
        screen_reader_engine="chromium",
        announce_transcript="screen_reader" in selected,
        mobile="mobile" in selected and browser_used,
        device="android-small",
        orientations=["portrait", "landscape"],
        wait_ms=review_type.wait_ms,
        forms="forms" in selected,
        media="media" in selected,
        cognitive="language" in selected,
        language_audit="language" in selected,
        components="components" in selected,
        document=False,
        workflow=False,
        passive_security=False,
    )
    extended_issues, extended_results = run_html_extended_modules(url, source_result["html"], extended_args, browser_result=browser, source_result=source_result)
    issues.extend(extended_issues)
    complete_extended_module_statuses(status, selected, extended_results, browser_used)
    for key in ["video", "document"]:
        if key in selected:
            mark_module(status, key, "unavailable", AUDIT_MODULES[key].description)

    passive_summary = {}
    if passive_security:
        update_status(run_dir, status, current="Running separate passive security observations", message="Passive security is separate from the accessibility score.", progress=64)
        passive_issues, passive_result = analyze_passive_security(source_result["html"], url, source_metadata=source_result)
        passive_summary = {
            "status": passive_result.get("status", "complete"),
            "finding_count": len(passive_issues),
            "result": passive_result,
        }
        save_json_report(passive_summary, run_dir / f"{item['id']}_passive_security.json")
        mark_module(status, "passive_security", "complete", f"{len(passive_issues)} passive observation(s). Not included in accessibility score.")

    issues = deduplicate_issues(issues)
    update_status(run_dir, status, current="Building deterministic report", message="Merging evidence and writing report files.", progress=74)
    report = build_json_report(
        url,
        issues,
        source_metadata=source_result,
        browser_result=browser,
        low_vision_result=low_vision,
        extended_results=extended_results,
    )
    sanitize_visual_proof_paths(report)
    if passive_summary:
        report["passive_security_separate"] = {
            "status": passive_summary["status"],
            "finding_count": passive_summary["finding_count"],
            "note": "Passive security observations are stored separately and are not included in the accessibility score.",
        }

    ai_scout_paths = {}
    if "ai_scout" in selected:
        update_status(run_dir, status, current="Asking AI Scout", message="AI Scout is reviewing deterministic findings in suggest-only mode.", progress=82)
        ai_result = run_ai_scout(report, target_name=item["name"], workflow_tested=review_type.workflow)
        report["ai_scout"] = ai_result
        ai_scout_paths = save_ai_scout_outputs(ai_result, run_dir / item["id"])
        mark_module(status, "ai_scout", "complete" if ai_result.get("status") == "ok" else "unavailable", ai_result.get("summary", "AI Scout completed."))

    score = score_report(report)
    report["score"] = score
    report_path = run_dir / f"{item['id']}.json"
    markdown_path = run_dir / f"{item['id']}.md"
    html_path = run_dir / f"{item['id']}.html"
    save_json_report(report, report_path)
    save_markdown_report(report, markdown_path)
    save_html_report(report, html_path)
    sarif_path = run_dir / f"{item['id']}.sarif"
    junit_path = run_dir / f"{item['id']}.junit.xml"
    save_sarif_report([report], sarif_path)
    save_junit_xml([report], junit_path)

    source_summary = source_summary_for_index(item, source_result, report, browser, low_vision, ai_scout_paths, html_path, markdown_path, report_path)
    index = build_batch_index_report([source_summary])
    index["score"] = score
    index["csv_index_path"] = (run_dir / "index.csv").as_posix()
    index["evaluation_summary_path"] = (run_dir / "evaluation_summary.md").as_posix()
    save_json_report(index, run_dir / "index.json")
    save_batch_index_markdown(index, run_dir / "index.md")
    save_batch_index_csv(index, run_dir / "index.csv")
    save_evaluation_summary_markdown(index, run_dir / "evaluation_summary.md", config_path=(run_dir / "batch_config.json").as_posix())

    duration = time.monotonic() - start_time
    summary = build_run_summary(
        run_id=run_id,
        run_dir=run_dir,
        item_id=item["id"],
        review_type=review_type,
        target_url=url,
        target_name=item["name"],
        fallback_notice=fallback_notice,
        browser_requested=browser_requested,
        browser_used=browser_used,
        selected_modules=selected,
        module_statuses=status["modules"],
        duration_seconds=duration,
        passive_security=passive_summary,
    )
    save_json_report(summary, run_dir / "web_run.json")
    update_status(run_dir, status, state="complete", current="Audit complete", message="Reports are ready.", progress=100, result_url=url_for_safe_result(run_id), finished=True)
    return summary


def wants_browser(selected: set[str]) -> bool:
    return any(AUDIT_MODULES[key].requires_browser for key in selected if key in AUDIT_MODULES)


def max_tabs_for(selected: set[str]) -> int:
    return 60 if {"keyboard", "focus_trap", "screen_reader", "low_vision"} & selected else 24


def wait_ms_for(selected: set[str]) -> int:
    return 1500 if {"browser", "low_vision", "mobile", "axe"} & selected else 800


def mark_module(status: dict[str, Any], key: str, state: str, message: str = "") -> None:
    for module in status.get("modules", []):
        if module.get("key") == key:
            module["status"] = state
            module["message"] = message
            return


def complete_extended_module_statuses(status: dict[str, Any], selected: set[str], results: list[dict], browser_used: bool) -> None:
    by_module = {result.get("module"): result for result in results}
    for key, module_name in [("screen_reader", "screen_reader"), ("mobile", "mobile"), ("forms", "forms"), ("components", "components"), ("media", "media"), ("language", "language")]:
        if key not in selected:
            continue
        result = by_module.get(module_name)
        if key in {"screen_reader", "mobile"} and not browser_used:
            mark_module(status, key, "unavailable", "Requires browser evidence.")
        elif result:
            status_value = result.get("status", "complete")
            mark_module(status, key, "complete" if status_value in {"complete", "completed", "passed"} else status_value, f"{len(result.get('findings', []))} finding(s).")
        else:
            mark_module(status, key, "complete", "No review points reported.")


def source_summary_for_index(item: dict[str, Any], source_result: dict[str, Any], report: dict[str, Any], browser: dict[str, Any] | None, low_vision: dict[str, Any] | None, ai_paths: dict[str, str], html_path: Path, markdown_path: Path, report_path: Path) -> dict[str, Any]:
    summary = report.get("summary", {})
    reports = {"json": report_path.as_posix(), "markdown": markdown_path.as_posix(), "html": html_path.as_posix()}
    if ai_paths:
        reports["ai_scout_json"] = ai_paths["json"]
        reports["ai_scout_markdown"] = ai_paths["markdown"]
    high = [
        {"issue_type": issue.get("issue_type", ""), "message": issue.get("message", ""), "snippet": (issue.get("evidence") or {}).get("snippet", "")}
        for issue in report.get("issues", [])
        if issue.get("severity") in {"critical", "high"}
    ]
    return {
        "id": item["id"],
        "name": item["name"],
        "source": item["source"],
        "source_type": source_result.get("source_type", "url"),
        "task": "",
        "status": "passed",
        "error": "",
        "issue_count": summary.get("issues_found", 0),
        "task_blocker_count": 0,
        "counts_by_severity": summary.get("counts_by_severity", {}),
        "counts_by_issue_type": summary.get("counts_by_issue_type", {}),
        "high_severity_issues": high,
        "analysis_modes": report.get("analysis_modes", ["static"]),
        "browser_status": "passed" if browser and browser.get("success") else "unavailable" if browser is None else "failed",
        "browser_issue_count": len(browser.get("issues", [])) if browser else 0,
        "low_vision_status": "passed" if low_vision and low_vision.get("success") else "unavailable" if low_vision is None else "failed",
        "low_vision_issue_count": len(low_vision.get("issues", [])) if low_vision else 0,
        "task_execution_status": "",
        "task_steps_passed": "",
        "task_steps_total": "",
        "ai_scout_status": (report.get("ai_scout") or {}).get("status", ""),
        "reports": reports,
    }


def build_run_summary(
    run_id: str,
    run_dir: Path,
    item_id: str,
    review_type: ReviewType,
    target_url: str,
    target_name: str,
    fallback_notice: str = "",
    browser_requested: bool = False,
    browser_used: bool = False,
    selected_modules: set[str] | None = None,
    module_statuses: list[dict[str, Any]] | None = None,
    duration_seconds: float = 0,
    passive_security: dict[str, Any] | None = None,
) -> dict[str, Any]:

    report_path = run_dir / f"{item_id}.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    score = report.get("score") or score_report(report)
    severity = severity_overview(report)
    findings = findings_for_web(report)
    reports = {
        "JSON": report_link(run_dir / f"{item_id}.json"),
        "Markdown": report_link(run_dir / f"{item_id}.md"),
        "HTML": report_link(run_dir / f"{item_id}.html"),
        "CSV": report_link(run_dir / "index.csv"),
        "SARIF": report_link(run_dir / f"{item_id}.sarif"),
        "JUnit": report_link(run_dir / f"{item_id}.junit.xml"),
    }
    ai_json = run_dir / f"{item_id}_ai_scout.json"
    ai_md = run_dir / f"{item_id}_ai_scout.md"
    if ai_json.exists():
        reports["AI Scout JSON"] = report_link(ai_json)
    if ai_md.exists():
        reports["AI Scout Markdown"] = report_link(ai_md)
    passive_path = run_dir / f"{item_id}_passive_security.json"
    if passive_path.exists():
        reports["Passive Security JSON"] = report_link(passive_path)

    visual = visual_links_for_report(report)
    wcag_criteria = sorted(
        {
            str(mapping.get("sc"))
            for issue in report.get("issues", [])
            for mapping in issue.get("wcag", []) or []
            if mapping.get("sc")
        }
    )

    return {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "target_url": target_url,
        "target_name": target_name,
        "review_type": review_type.label,
        "selected_modules": [AUDIT_MODULES[key].label for key in sorted(selected_modules or []) if key in AUDIT_MODULES],
        "module_statuses": module_statuses or [],
        "status": "passed" if report else "failed",
        "error": "",
        "config_path": WEB_DEMO_CONFIG_PATH.as_posix(),
        "output_dir": run_dir.as_posix(),
        "score": score,
        "total_issues": score.get("total_issues", 0),
        "classification": score.get("classification", ""),
        "severity_overview": severity,
        "wcag_criteria": wcag_criteria,
        "wcag_criteria_count": len(wcag_criteria),
        "findings": findings,
        "top_findings": findings[:8],
        "ai_scout": report.get("ai_scout", {}),
        "reports": {key: value for key, value in reports.items() if value},
        "visual_proof": visual,
        "fallback_notice": fallback_notice,
        "browser_requested": browser_requested,
        "browser_used": browser_used,
        "duration_seconds": round(duration_seconds, 1),
        "passive_security": passive_security or {},
        "guardrails": guardrail_notes(),
    }


def severity_overview(report: dict[str, Any]) -> dict[str, int]:
    counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0, "review_required": 0}
    for issue in report.get("issues", []):
        severity = str(issue.get("severity", "")).lower()
        confidence = str(issue.get("confidence", "")).lower()
        if severity == "critical":
            counts["critical"] += 1
        elif severity == "high":
            counts["serious"] += 1
        elif severity == "medium":
            counts["moderate"] += 1
        else:
            counts["minor"] += 1
        if "review" in confidence:
            counts["review_required"] += 1
    return counts


def findings_for_web(report: dict[str, Any]) -> list[dict[str, Any]]:
    weights = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings = []
    for issue in report.get("issues", []):
        evidence = issue.get("evidence") if isinstance(issue.get("evidence"), dict) else {"description": issue.get("evidence", "")}
        wcag = issue.get("wcag", []) or []
        first_wcag = wcag[0] if wcag else {}
        findings.append(
            {
                "title": issue.get("message") or issue.get("issue_type", "Accessibility finding"),
                "severity": issue.get("severity", ""),
                "display_severity": display_severity(issue.get("severity", ""), issue.get("confidence", "")),
                "affected_url": report.get("source", {}).get("input") or report.get("source_file", ""),
                "wcag": wcag,
                "wcag_label": f"SC {first_wcag.get('sc')} {first_wcag.get('name')} (Level {first_wcag.get('level')})" if first_wcag else "No direct WCAG mapping",
                "category": issue.get("rule", {}).get("category") or issue.get("issue_type", ""),
                "issue_type": issue.get("issue_type", ""),
                "selector": evidence.get("selector") or evidence.get("element") or evidence.get("tag") or "",
                "snippet": evidence.get("snippet", ""),
                "evidence": evidence,
                "browser_observation": evidence.get("observed") or evidence.get("announcement") or evidence.get("reason") or "",
                "suggested_fix": issue.get("suggested_fix", ""),
                "source_module": evidence.get("module") or evidence.get("detected_in") or issue.get("agent_name", "static"),
                "confidence": issue.get("confidence", ""),
            }
        )
    findings.sort(key=lambda item: (weights.get(str(item["severity"]).lower(), 9), item["issue_type"]))
    return findings


def display_severity(severity: str, confidence: str = "") -> str:
    if "review" in str(confidence).lower():
        return "Review required"
    return {"critical": "Critical", "high": "Serious", "medium": "Moderate", "low": "Minor"}.get(str(severity).lower(), str(severity).title() or "Review")


def visual_links_for_report(report: dict[str, Any]) -> dict[str, str]:
    visual_proof = report.get("visual_proof") or {}
    links = {}
    for key, label in [("screenshot_path", "screenshot"), ("focus_overlay_path", "focus_overlay"), ("video_path", "video")]:
        path_text = visual_proof.get(key)
        if path_text:
            links[f"{label}_path"] = path_text
            links[f"{label}_link"] = report_link(PROJECT_ROOT / path_text)
    return links


def sanitize_visual_proof_paths(report: dict[str, Any]) -> None:

    visual = report.get("visual_proof")
    if not isinstance(visual, dict):
        return
    for key in ["screenshot_path", "focus_overlay_path", "video_path"]:
        path_text = visual.get(key)
        if not path_text:
            continue
        try:
            path = Path(path_text)
            if path.is_absolute():
                visual[key] = path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
        except (OSError, ValueError):
            continue


def update_status(run_dir: Path, status: dict[str, Any], *, state: str | None = None, current: str | None = None, message: str | None = None, progress: int | None = None, error: str = "", error_id: str = "", result_url: str = "", finished: bool = False) -> None:
    if state:
        status["status"] = state
    if current:
        status["current_module"] = current
    if progress is not None:
        status["progress_percent"] = max(0, min(100, int(progress)))
    if message:
        status.setdefault("messages", []).append(message)
    if error:
        status["error"] = error
    if error_id:
        status["error_id"] = error_id
    if result_url:
        status["result_url"] = result_url
    if not status.get("started_at") and status.get("status") == "running":
        status["started_at"] = datetime.now().isoformat(timespec="seconds")
    if finished:
        status["finished_at"] = datetime.now().isoformat(timespec="seconds")
    save_status(run_dir, status)


def save_status(run_dir: Path, status: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    if status.get("started_at"):
        try:
            started = datetime.fromisoformat(status["started_at"])
            status["elapsed_seconds"] = max(0, round((datetime.now() - started).total_seconds(), 1))
        except ValueError:
            pass
    (run_dir / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def load_status(run_id: str) -> dict[str, Any] | None:
    if safe_report_id(run_id) != run_id:
        return None
    path = WEB_DEMO_RUNS_DIR / run_id / "status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def url_for_safe_result(run_id: str) -> str:
    try:
        return url_for("result", run_id=run_id)
    except RuntimeError:
        return f"/runs/{run_id}"


def report_link(path: Path) -> str:

    try:
        resolved = path.resolve()
        relative = resolved.relative_to(WEB_DEMO_RUNS_DIR.resolve()).as_posix()
    except (OSError, ValueError):
        return ""
    try:
        return url_for("report_file", relative_path=relative)
    except RuntimeError:
        return f"/reports/{relative}"


def safe_report_path(relative_path: str) -> Path | None:

    if any(part in {"..", ""} for part in Path(relative_path).parts):
        return None
    try:
        root = WEB_DEMO_RUNS_DIR.resolve()
        path = (root / relative_path).resolve()
        path.relative_to(root)
    except (OSError, ValueError):
        return None
    return path


def request_path_has_traversal() -> bool:

    raw_values = [
        request.environ.get("RAW_URI", ""),
        request.environ.get("REQUEST_URI", ""),
        request.full_path,
        request.path,
    ]
    for raw in raw_values:
        decoded = unquote(str(raw))
        normalized = decoded.replace("\\", "/")
        if any(part == ".." for part in normalized.split("/")):
            return True
    return False


def load_run_summary(run_id: str) -> dict[str, Any] | None:

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

    return [
        "Tests one public URL per run.",
        "Blocks localhost, private IPs, metadata IPs, internal hostnames, non-http schemes, embedded credentials, unsafe ports, and unsafe redirect targets.",
        "Does not log in, bypass authentication, submit forms, create accounts, send messages, or test payment flows.",
        "Does not run vulnerability scans, exploit checks, port scans, or private-data scraping.",
        "Passive security observations are opt-in and separate from accessibility scoring.",
        "AI Scout is suggest-only, summarizes deterministic findings, and may be unavailable without a configured Groq key.",
        "A11yway reports require human review and are not legal compliance certification.",
    ]


app = create_app()


def main() -> None:

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
