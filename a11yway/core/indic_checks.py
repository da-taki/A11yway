













from __future__ import annotations

import re
from html.parser import HTMLParser

from a11yway.models.issue import AccessibilityIssue


INDIC_CHECK_NAME = "indic_language_checks"


INDIC_SCRIPT_RANGES = {
    "Devanagari": (0x0900, 0x097F),
    "Bengali": (0x0980, 0x09FF),
    "Gurmukhi": (0x0A00, 0x0A7F),
    "Gujarati": (0x0A80, 0x0AFF),
    "Oriya": (0x0B00, 0x0B7F),
    "Tamil": (0x0B80, 0x0BFF),
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
}


LANG_TO_SCRIPT = {
    "hi": "Devanagari",
    "mr": "Devanagari",
    "ne": "Devanagari",
    "sa": "Devanagari",
    "kok": "Devanagari",
    "mai": "Devanagari",
    "bn": "Bengali",
    "as": "Bengali",
    "pa": "Gurmukhi",
    "gu": "Gujarati",
    "or": "Oriya",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
}


_MIN_INDIC_CHARS = 3
_MIN_LATIN_WORDS_FOR_MIX = 2

_NON_RENDERED_TAGS = {"script", "style", "template"}


_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def script_of_char(char: str) -> str | None:





    if not char.isalpha():
        return None
    code = ord(char)
    for name, (low, high) in INDIC_SCRIPT_RANGES.items():
        if low <= code <= high:
            return name
    if code < 0x0250:
        return "Latin"
    return None


def script_counts(text: str) -> dict[str, int]:

    counts: dict[str, int] = {}
    for char in text:
        script = script_of_char(char)
        if script:
            counts[script] = counts.get(script, 0) + 1
    return counts


def dominant_indic_script(counts: dict[str, int]) -> str | None:

    best_name = None
    best_count = 0
    for name in INDIC_SCRIPT_RANGES:
        count = counts.get(name, 0)
        if count > best_count:
            best_name = name
            best_count = count
    return best_name


def expected_script_for_lang(lang: str | None) -> str | None:

    if not lang:
        return None
    primary = lang.split("-")[0].strip().lower()
    return LANG_TO_SCRIPT.get(primary)


def substantial_latin_words(text: str) -> list[str]:






    words = []
    for token in re.findall(r"[A-Za-z][A-Za-z'\-]*", text):
        if len(token) <= 1:
            continue
        if token.isupper() and len(token) <= 5:
            continue
        words.append(token)
    return words


class _LangTextParser(HTMLParser):


    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.skip_depth = 0
        self.text_nodes: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _VOID_TAGS:
            return
        lang = None
        for name, value in attrs:
            if name == "lang" and value and value.strip():
                lang = value.strip()
                break
        self.stack.append((tag, lang))
        if tag in _NON_RENDERED_TAGS:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                removed = self.stack[index:]
                del self.stack[index:]
                self.skip_depth -= sum(
                    1 for removed_tag, _ in removed
                    if removed_tag in _NON_RENDERED_TAGS
                )
                break

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text or self.skip_depth > 0:
            return
        effective_lang = None
        for _tag, lang in reversed(self.stack):
            if lang:
                effective_lang = lang
                break
        owner_tag, owner_lang = self.stack[-1] if self.stack else ("", None)
        self.text_nodes.append(
            {
                "text": text,
                "tag": owner_tag,
                "own_lang": owner_lang,
                "effective_lang": effective_lang,
                "line": self.getpos()[0],
            }
        )


def _indic_issue(
    title: str,
    issue_type: str,
    severity: str,
    node: dict,
    reason: str,
    extra: dict | None = None,
) -> AccessibilityIssue:

    evidence = {
        "snippet": node["text"][:120],
        "tag": node["tag"],
        "line": node["line"],
        "reason": reason,
    }
    if extra:
        evidence.update(extra)
    return AccessibilityIssue(
        title=title,
        issue_type=issue_type,
        severity=severity,
        agent_name="Indic Language Checker",
        evidence=evidence,
        suggested_fix="",
    )


def analyze_indic_language(html: str) -> list[AccessibilityIssue]:

    parser = _LangTextParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        pass

    issues: list[AccessibilityIssue] = []
    flagged: set[tuple[str, str]] = set()

    for node in parser.text_nodes:
        counts = script_counts(node["text"])
        indic_total = sum(counts.get(name, 0) for name in INDIC_SCRIPT_RANGES)
        if indic_total < _MIN_INDIC_CHARS:
            continue
        script = dominant_indic_script(counts)

        latin_words = substantial_latin_words(node["text"])
        if len(latin_words) >= _MIN_LATIN_WORDS_FOR_MIX:
            key = ("mixed_script_element", node["text"][:120])
            if key not in flagged:
                flagged.add(key)
                issues.append(
                    _indic_issue(
                        title="Latin and Indic scripts mix without a lang boundary",
                        issue_type="mixed_script_element",
                        severity="medium",
                        node=node,
                        reason=(
                            f"One text node mixes {script} text with "
                            f"{len(latin_words)} Latin words and no lang-tagged "
                            "boundary, which commonly garbles text-to-speech."
                        ),
                        extra={
                            "detected_script": script,
                            "latin_word_count": len(latin_words),
                        },
                    )
                )

        if node["own_lang"]:
            expected = expected_script_for_lang(node["own_lang"])
            if expected != script:
                key = ("lang_mismatch", node["text"][:120])
                if key not in flagged:
                    flagged.add(key)
                    issues.append(
                        _indic_issue(
                            title="Declared lang contradicts the text's script",
                            issue_type="lang_mismatch",
                            severity="high",
                            node=node,
                            reason=(
                                f'The element declares lang="{node["own_lang"]}" '
                                f"but its text is dominantly {script} script, so "
                                "a screen reader picks the wrong voice."
                            ),
                            extra={
                                "declared_lang": node["own_lang"],
                                "detected_script": script,
                            },
                        )
                    )
            continue

        effective = node["effective_lang"]
        expected = expected_script_for_lang(effective)
        if effective is None or expected != script:
            key = ("missing_lang_indic", node["text"][:120])
            if key in flagged:
                continue
            flagged.add(key)
            if effective is None:
                reason = (
                    f"{script} text appears with no lang declared anywhere up "
                    "the tree, so text-to-speech falls back to a default voice."
                )
            else:
                reason = (
                    f"{script} text inherits lang=\"{effective}\", which does "
                    f"not match the script, so text-to-speech reads it with "
                    "the wrong voice."
                )
            issues.append(
                _indic_issue(
                    title="Indic-script text lacks a matching lang attribute",
                    issue_type="missing_lang_indic",
                    severity="high",
                    node=node,
                    reason=reason,
                    extra={
                        "effective_lang": effective or "",
                        "detected_script": script,
                    },
                )
            )

    for issue in issues:
        if issue.issue_type == "mixed_script_element":
            issue.suggested_fix = (
                "Wrap each language's text in an element with the matching "
                "lang attribute so speech engines can switch voices."
            )
        elif issue.issue_type == "lang_mismatch":
            issue.suggested_fix = (
                "Correct the lang attribute to match the language actually "
                "written in the element."
            )
        else:
            issue.suggested_fix = (
                "Add a lang attribute matching the text's language (for "
                'example lang="pa" for Gurmukhi) on the element or a fitting '
                "ancestor."
            )
    return issues
