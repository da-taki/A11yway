"""Placeholder page analysis helpers.

Future versions can use this module to inspect HTML, browser state,
PDF files, and accessibility trees.
"""

from __future__ import annotations

from typing import Any


def analyze_html(html: str) -> dict[str, Any]:
    """Return placeholder analysis for an HTML page.

    TODO: Parse HTML and inspect headings, landmarks, labels, images,
    controls, focusable elements, and media.
    """
    return {
        "html_length": len(html),
        "notes": "HTML analysis is not implemented yet.",
    }


def analyze_browser_page(url: str) -> dict[str, Any]:
    """Return placeholder browser analysis for a URL.

    TODO: Integrate Playwright or Selenium to load pages, run keyboard
    navigation checks, inspect computed styles, and capture evidence.
    """
    return {
        "url": url,
        "notes": "Browser automation is not implemented yet.",
    }


def analyze_pdf(path: str) -> dict[str, Any]:
    """Return placeholder PDF analysis.

    TODO: Add PDF text extraction, reading order checks, tags checks,
    image alternative text checks, and form field checks.
    """
    return {
        "path": path,
        "notes": "PDF analysis is not implemented yet.",
    }
