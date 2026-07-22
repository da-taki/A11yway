from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        and "reports" not in path.parts
        and "dist" not in path.parts
        and "build" not in path.parts
    ]


def test_first_party_markdown_relative_links_resolve() -> None:
    missing: list[str] = []
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith("#"):
                continue
            if "://" in target or target.startswith(("mailto:", "tel:")):
                continue
            if target.startswith("/"):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            if target.startswith("reports/") or "/reports/" in target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                continue
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")

    assert missing == []
