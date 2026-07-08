"""Load static HTML from local files or exact URLs.

This module intentionally fetches only the provided source. It does not crawl
sites and does not execute JavaScript.
"""

from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


USER_AGENT = "A11ywayPrototype/0.1"


def is_url(source: str) -> bool:
    """Return whether a source is an http or https URL."""
    return urlparse(source).scheme in {"http", "https"}


def _empty_result(source: str, source_type: str) -> dict:
    """Build the common source result shape."""
    return {
        "source": source,
        "source_type": source_type,
        "html": "",
        "final_url": None,
        "status_code": None,
        "content_type": None,
        "error": None,
    }


def load_html_source(source: str, timeout_seconds: int = 10) -> dict:
    """Load static HTML from a local file or a single URL.

    Errors are returned in the result dictionary instead of being raised so
    batch mode can continue when one source fails.
    """
    if is_url(source):
        return _load_url_source(source, timeout_seconds)
    return _load_file_source(source)


def _load_file_source(source: str) -> dict:
    """Load HTML from a local file path."""
    result = _empty_result(source, "file")
    result["content_type"] = "text/html"

    try:
        result["html"] = Path(source).read_text(encoding="utf-8")
    except OSError as error:
        result["error"] = str(error)

    return result


def _load_url_source(source: str, timeout_seconds: int) -> dict:
    """Load static HTML from one URL using urllib."""
    result = _empty_result(source, "url")
    request = Request(source, headers={"User-Agent": USER_AGENT})

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            content_type = response.headers.get("Content-Type")
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read()

            result["final_url"] = response.geturl()
            result["status_code"] = getattr(response, "status", None)
            result["content_type"] = content_type

            if content_type and "html" not in content_type.lower():
                result["error"] = f"Unsupported content type: {content_type}"
                return result

            result["html"] = body.decode(charset, errors="replace")
    except HTTPError as error:
        result["final_url"] = error.geturl()
        result["status_code"] = error.code
        result["content_type"] = error.headers.get("Content-Type") if error.headers else None
        result["error"] = f"HTTP error {error.code}: {error.reason}"
    except URLError as error:
        result["error"] = f"URL error: {error.reason}"
    except OSError as error:
        result["error"] = str(error)

    return result
