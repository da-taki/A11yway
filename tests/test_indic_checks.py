





from pathlib import Path

import pytest

from a11yway.core.indic_checks import (
    analyze_indic_language,
    expected_script_for_lang,
    script_counts,
    script_of_char,
    substantial_latin_words,
)
from a11yway.core.page_analyzer import STATIC_CHECKS_RUN, analyze_html_static
from a11yway.core.rules import get_rule
from a11yway.main import analyze_html_file


HINDI = "छात्रवृत्ति के लिए आवेदन करें"
GURMUKHI = "ਵਜ਼ੀਫ਼ੇ ਲਈ ਅਰਜ਼ੀ ਦਿਓ"
TAMIL = "உதவித்தொகைக்கு விண்ணப்பிக்கவும்"


def page(body: str, html_lang: str | None = "en") -> str:

    lang_attr = f' lang="{html_lang}"' if html_lang else ""
    return (
        f"<!doctype html><html{lang_attr}><head><meta charset='utf-8'>"
        f"<title>T</title></head><body><h1>T</h1>{body}</body></html>"
    )


def issue_types(html: str) -> set[str]:

    return {issue.issue_type for issue in analyze_indic_language(html)}


def test_script_detection_basics() -> None:

    assert script_of_char("क") == "Devanagari"
    assert script_of_char("ਸ") == "Gurmukhi"
    assert script_of_char("த") == "Tamil"
    assert script_of_char("a") == "Latin"
    assert script_of_char("5") is None
    assert script_of_char("।") is None

    counts = script_counts("Hello क्षेत्र")
    assert counts["Latin"] == 5
    assert counts["Devanagari"] >= 4


def test_expected_script_handles_subtags() -> None:

    assert expected_script_for_lang("hi") == "Devanagari"
    assert expected_script_for_lang("pa-IN") == "Gurmukhi"
    assert expected_script_for_lang("TA") == "Tamil"
    assert expected_script_for_lang("en") is None
    assert expected_script_for_lang(None) is None


def test_substantial_latin_words_filters_noise() -> None:

    words = substantial_latin_words("PDF 2026 a Please bring certificate")
    assert words == ["Please", "bring", "certificate"]


def test_indic_text_under_english_lang_is_flagged() -> None:

    issues = analyze_indic_language(page(f"<p>{GURMUKHI}</p>"))

    assert [issue.issue_type for issue in issues] == ["missing_lang_indic"]
    evidence = issues[0].evidence
    assert evidence["detected_script"] == "Gurmukhi"
    assert evidence["effective_lang"] == "en"
    assert issues[0].severity == "high"
    assert evidence["line"] > 0


def test_indic_text_with_no_lang_anywhere_is_flagged() -> None:

    types = issue_types(page(f"<p>{HINDI}</p>", html_lang=None))

    assert types == {"missing_lang_indic"}


def test_properly_tagged_indic_text_is_clean() -> None:

    body = f'<p lang="hi">{HINDI}</p><p lang="pa">{GURMUKHI}</p>'
    assert issue_types(page(body)) == set()


def test_inherited_matching_lang_is_clean() -> None:

    assert issue_types(page(f"<p>{HINDI}</p>", html_lang="hi")) == set()


def test_declared_lang_contradicting_script_is_mismatch() -> None:

    issues = analyze_indic_language(page(f'<p lang="ta">{HINDI}</p>'))

    assert [issue.issue_type for issue in issues] == ["lang_mismatch"]
    assert issues[0].evidence["declared_lang"] == "ta"
    assert issues[0].evidence["detected_script"] == "Devanagari"


def test_transliterated_text_cannot_be_detected() -> None:

    body = '<p lang="hi">Chhatravritti ke liye aavedan karein</p>'
    assert issue_types(page(body)) == set()


def test_mixed_script_text_node_is_flagged() -> None:

    body = f'<p lang="hi">Please bring your certificate {HINDI}</p>'
    issues = analyze_indic_language(page(body))

    assert [issue.issue_type for issue in issues] == ["mixed_script_element"]
    assert issues[0].severity == "medium"


def test_single_loanword_and_numbers_are_not_a_mix() -> None:

    assert issue_types(page(f'<p lang="hi">{HINDI} PDF 2026</p>')) == set()
    assert issue_types(page(f'<p lang="hi">{HINDI} Whatsapp</p>')) == set()


def test_lang_boundary_prevents_the_mix_flag() -> None:

    body = f'<p>Please bring your income certificate <span lang="hi">{HINDI}</span></p>'
    assert issue_types(page(body)) == set()


def test_script_and_style_text_is_ignored() -> None:

    body = f"<script>var s = '{HINDI}';</script>"
    assert issue_types(page(body)) == set()


def test_indic_checks_run_in_static_mode() -> None:

    assert "indic_language_checks" in STATIC_CHECKS_RUN
    types = {
        issue.issue_type
        for issue in analyze_html_static(page(f"<p>{GURMUKHI}</p>"))
    }
    assert "missing_lang_indic" in types


@pytest.mark.parametrize(
    "issue_type", ["missing_lang_indic", "mixed_script_element", "lang_mismatch"]
)
def test_indic_rules_exist_in_registry(issue_type: str) -> None:

    rule = get_rule(issue_type)

    assert rule is not None
    assert rule["category"] == "Language"
    assert rule["static_check_limitations"]
    assert rule["how_to_fix"]


def test_sample_indic_page_seeds_all_three_types() -> None:

    issues = analyze_html_file(Path("examples/sample_indic_page.html"))

    types = {issue.issue_type for issue in issues}
    assert {"missing_lang_indic", "mixed_script_element", "lang_mismatch"} <= types
    missing = [i for i in issues if i.issue_type == "missing_lang_indic"]
    scripts = {i.evidence["detected_script"] for i in missing}
    assert {"Devanagari", "Gurmukhi"} <= scripts


def test_cli_survives_indic_output_on_limited_consoles(tmp_path: Path) -> None:

    from a11yway.main import main

    markdown_path = tmp_path / "indic_report.md"
    exit_code = main(
        ["examples/sample_indic_page.html", "--markdown", str(markdown_path)]
    )

    assert exit_code == 0
    assert markdown_path.exists()


def test_sample_indic_clean_page_has_no_language_findings() -> None:

    issues = analyze_html_file(Path("examples/sample_indic_page_clean.html"))

    types = {issue.issue_type for issue in issues}
    assert not types & {"missing_lang_indic", "mixed_script_element", "lang_mismatch"}
