"""Small HTML helpers for extended modules."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any


VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "source", "track", "area", "base", "col", "embed", "param", "wbr"}


class SimpleElementParser(HTMLParser):
    """Collect start tags and rough text content without external deps."""

    def __init__(self) -> None:
        super().__init__()
        self.elements: list[dict[str, Any]] = []
        self.stack: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        element = {
            "tag": tag.lower(),
            "attrs": {name.lower(): value or "" for name, value in attrs},
            "text": "",
            "children": [],
            "snippet": self.get_starttag_text() or "",
        }
        self.elements.append(element)
        if self.stack:
            self.stack[-1]["children"].append(element)
        if tag.lower() not in VOID_TAGS:
            self.stack.append(element)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        while self.stack:
            current = self.stack.pop()
            if current["tag"] == tag:
                break

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.stack[-1]["text"] += data


def parse_elements(html: str) -> list[dict[str, Any]]:
    parser = SimpleElementParser()
    parser.feed(html)
    return parser.elements


def text_content(html: str) -> str:
    cleaned = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", html, flags=re.I | re.S)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return re.sub(r"\s+", " ", unescape(cleaned)).strip()


def attr(element: dict[str, Any], name: str) -> str:
    return str(element.get("attrs", {}).get(name.lower(), "") or "")


def selector_for(element: dict[str, Any]) -> str:
    tag = element.get("tag", "element")
    element_id = attr(element, "id")
    name = attr(element, "name")
    role = attr(element, "role")
    if element_id:
        return f"{tag}#{element_id}"
    if name:
        return f'{tag}[name="{name}"]'
    if role:
        return f'{tag}[role="{role}"]'
    text = re.sub(r"\s+", " ", str(element.get("text", ""))).strip()
    return f"{tag} ({text[:32]})" if text else tag


def visible_text(element: dict[str, Any]) -> str:
    return re.sub(r"\s+", " ", str(element.get("text", ""))).strip()


def is_hidden(element: dict[str, Any]) -> bool:
    style = attr(element, "style").lower()
    return (
        attr(element, "hidden") != ""
        or attr(element, "aria-hidden").lower() == "true"
        or "display:none" in style.replace(" ", "")
        or "visibility:hidden" in style.replace(" ", "")
    )


def accessible_name_hint(element: dict[str, Any]) -> str:
    for key in ("aria-label", "title", "alt", "value", "placeholder"):
        value = attr(element, key).strip()
        if value:
            return value
    return visible_text(element)
