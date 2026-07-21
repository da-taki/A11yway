from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path


PYTHON_SUFFIXES = {".py"}
HTML_SUFFIXES = {".html", ".htm"}
CSS_SUFFIXES = {".css"}
JS_SUFFIXES = {".js", ".mjs", ".cjs"}
SKIPPED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "reports",
    "build",
    "dist",
    "a11yway.egg-info",
}


def first_party_files(root: Path) -> list[Path]:
    bases = [root / "a11yway", root / "tests", root / "scripts"]
    files: list[Path] = []
    for base in bases:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIPPED_PARTS for part in path.parts):
                continue
            if path.suffix.lower() in PYTHON_SUFFIXES | HTML_SUFFIXES | CSS_SUFFIXES | JS_SUFFIXES:
                files.append(path)
    return sorted(files)


def _docstring_lines(tree: ast.AST) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            start = getattr(first, "lineno", 0)
            end = getattr(first, "end_lineno", start)
            lines.update(range(start, end + 1))
    return lines


def scan_python(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    try:
        tree = ast.parse(text)
        for line in sorted(_docstring_lines(tree)):
            findings.append({"file": str(path), "line": line, "kind": "python_docstring"})
    except SyntaxError:
        findings.append({"file": str(path), "line": 1, "kind": "python_parse_error"})
        return findings
    stream = io.StringIO(text)
    for token in tokenize.generate_tokens(stream.readline):
        if token.type == tokenize.COMMENT:
            findings.append({"file": str(path), "line": token.start[0], "kind": "python_comment"})
    return findings


def _line_for(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_markup(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    for marker, kind in [("<!--", "html_comment"), ("{#", "jinja_comment")]:
        start = 0
        while True:
            index = text.find(marker, start)
            if index == -1:
                break
            findings.append({"file": str(path), "line": _line_for(text, index), "kind": kind})
            start = index + len(marker)
    return findings


def scan_css(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    start = 0
    while True:
        index = text.find("/*", start)
        if index == -1:
            break
        findings.append({"file": str(path), "line": _line_for(text, index), "kind": "css_comment"})
        start = index + 2
    return findings


def scan_javascript(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    state = "code"
    quote = ""
    index = 0
    line = 1
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if char == "\n":
            line += 1
        if state == "code":
            if char in {"'", '"', "`"}:
                state = "string"
                quote = char
            elif char == "/" and nxt == "/":
                findings.append({"file": str(path), "line": line, "kind": "javascript_line_comment"})
                while index < len(text) and text[index] != "\n":
                    index += 1
                continue
            elif char == "/" and nxt == "*":
                findings.append({"file": str(path), "line": line, "kind": "javascript_block_comment"})
                index += 2
                while index + 1 < len(text) and text[index:index + 2] != "*/":
                    if text[index] == "\n":
                        line += 1
                    index += 1
                index += 2
                continue
        elif state == "string":
            if char == "\\":
                index += 2
                continue
            if char == quote:
                state = "code"
        index += 1
    return findings


def scan_first_party_comments(root: Path) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    by_language = {"python": 0, "html_jinja": 0, "css": 0, "javascript": 0}
    for path in first_party_files(root):
        suffix = path.suffix.lower()
        if suffix in PYTHON_SUFFIXES:
            result = scan_python(path)
            by_language["python"] += len(result)
        elif suffix in HTML_SUFFIXES:
            result = scan_markup(path)
            by_language["html_jinja"] += len(result)
        elif suffix in CSS_SUFFIXES:
            result = scan_css(path)
            by_language["css"] += len(result)
        elif suffix in JS_SUFFIXES:
            result = scan_javascript(path)
            by_language["javascript"] += len(result)
        else:
            result = []
        findings.extend(result)
    return {"total": len(findings), "by_language": by_language, "findings": findings}


def format_comment_scan(root: Path) -> str:
    result = scan_first_party_comments(root)
    lines = [f"First-party explanatory comments found: {result['total']}"]
    for language, count in result["by_language"].items():
        lines.append(f"{language}: {count}")
    for finding in result["findings"][:50]:
        lines.append(f"{finding['file']}:{finding['line']} {finding['kind']}")
    return "\n".join(lines)
