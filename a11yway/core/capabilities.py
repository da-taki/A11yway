"""Capability detection for optional A11yway modules."""

from __future__ import annotations

import importlib.util
import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _which(*names: str) -> str | None:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def _status(available: bool, *, verified: bool = False, unsupported: bool = False) -> str:
    if unsupported:
        return "unsupported_on_current_platform"
    if verified:
        return "available_verified"
    if available:
        return "available_untested"
    return "unavailable"


def _playwright_browser_status(browser_name: str) -> dict[str, Any]:
    if not _module_available("playwright"):
        return {"status": "unavailable", "detail": "Playwright Python package is not importable."}
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser_type = getattr(playwright, browser_name)
            browser = browser_type.launch(headless=True)
            browser.close()
        return {"status": "available_verified", "detail": f"{browser_name} launched successfully."}
    except Exception as error:  # noqa: BLE001 - capability detection must degrade
        return {"status": "unavailable", "detail": str(error)}


def _adb_devices(adb_path: str | None) -> list[str]:
    if not adb_path:
        return []
    try:
        completed = subprocess.run(
            [adb_path, "devices"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:  # noqa: BLE001 - optional tool
        return []
    devices = []
    for line in completed.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def detect_capabilities(verify_browsers: bool = False) -> dict[str, Any]:
    """Return optional-tool capability status without requiring any dependency."""
    system = platform.system()
    is_windows = system.lower() == "windows"
    adb_path = _which("adb", "adb.exe")
    nvda_path = _which("nvda", "nvda.exe")
    jaws_path = _which("jfw", "jfw.exe")
    ffmpeg_path = _which("ffmpeg", "ffmpeg.exe")
    pdf_libs = {
        "pypdf": _module_available("pypdf"),
        "pdfplumber": _module_available("pdfplumber"),
    }
    office_libs = {
        "python-docx": _module_available("docx"),
        "python-pptx": _module_available("pptx"),
    }
    media_libs = {
        "mutagen": _module_available("mutagen"),
    }
    playwright_available = _module_available("playwright")
    browsers = {}
    for browser_name in ("chromium", "firefox", "webkit"):
        browsers[browser_name] = (
            _playwright_browser_status(browser_name)
            if verify_browsers
            else {
                "status": _status(playwright_available, verified=False),
                "detail": "Playwright package importable; launch not tested in this capability pass."
                if playwright_available
                else "Playwright Python package is not importable.",
            }
        )

    devices = _adb_devices(adb_path)
    return {
        "platform": {
            "system": system,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "windows": {
                "status": _status(is_windows, verified=is_windows, unsupported=not is_windows),
                "detail": "Windows-specific native adapters can be considered." if is_windows else "Native Windows screen-reader adapters are unsupported on this platform.",
            },
        },
        "playwright": {
            "status": _status(playwright_available, verified=False),
            "detail": "Python package importable." if playwright_available else "Playwright is not installed.",
        },
        "browsers": browsers,
        "screen_readers": {
            "nvda": {
                "status": _status(bool(nvda_path), verified=False, unsupported=not is_windows),
                "path": nvda_path,
                "detail": "Adapter scaffold only; native NVDA automation is not run unless a safe interface is configured.",
            },
            "jaws": {
                "status": _status(bool(jaws_path), verified=False, unsupported=not is_windows),
                "path": jaws_path,
                "detail": "Detected only; proprietary JAWS components are not automated or redistributed.",
            },
            "voiceover": {
                "status": "unsupported_on_current_platform" if not platform.system().lower() == "darwin" else "available_untested",
                "detail": "VoiceOver adapter scaffold only.",
            },
            "talkback": {
                "status": "available_untested" if devices else "unavailable",
                "detail": "Requires ADB and a supported Android device; Playwright emulation is not TalkBack.",
            },
        },
        "android": {
            "adb": {"status": _status(bool(adb_path)), "path": adb_path},
            "devices": devices,
        },
        "documents": {
            "pdf": {"status": _status(any(pdf_libs.values()), verified=any(pdf_libs.values())), "libraries": pdf_libs},
            "office": {"status": _status(any(office_libs.values()), verified=any(office_libs.values())), "libraries": office_libs},
        },
        "media": {
            "ffmpeg": {"status": _status(bool(ffmpeg_path)), "path": ffmpeg_path},
            "libraries": media_libs,
        },
        "optional_dependencies": {
            "reportlab": {"status": _status(_module_available("reportlab"), verified=_module_available("reportlab"))},
            "pillow": {"status": _status(_module_available("PIL"), verified=_module_available("PIL"))},
        },
    }


def format_capabilities_cli(capabilities: dict[str, Any]) -> str:
    """Render capability detection as readable CLI text."""
    lines = ["A11yway capability detection", ""]
    lines.append(f"Platform: {capabilities['platform']['platform']}")
    lines.append(f"Python: {capabilities['platform']['python']}")
    lines.append("")
    lines.append(f"Playwright: {capabilities['playwright']['status']}")
    for name, status in capabilities["browsers"].items():
        lines.append(f"{name.title()}: {status['status']} - {status.get('detail', '')}")
    lines.append("")
    for name, status in capabilities["screen_readers"].items():
        path = f" ({status['path']})" if status.get("path") else ""
        lines.append(f"{name.upper() if name in {'nvda', 'jaws'} else name.title()}: {status['status']}{path}")
    lines.append("")
    lines.append(f"ADB: {capabilities['android']['adb']['status']}")
    lines.append(f"Android devices/emulators: {len(capabilities['android']['devices'])}")
    lines.append(f"PDF libraries: {capabilities['documents']['pdf']['status']}")
    lines.append(f"Office document libraries: {capabilities['documents']['office']['status']}")
    lines.append(f"FFmpeg: {capabilities['media']['ffmpeg']['status']}")
    lines.append("")
    lines.append("Missing optional tools disable only their native adapters; static and browser-supported checks continue.")
    return "\n".join(lines)


def save_capabilities_json(capabilities: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(capabilities, indent=2), encoding="utf-8")
