from __future__ import annotations

import pytest

from a11yway.core.cognitive_audit import analyze_cognitive
from a11yway.core.component_audit import analyze_components
from a11yway.core.forms_audit import analyze_forms
from a11yway.core.language_audit import analyze_language
from a11yway.core.media_audit import analyze_media
from a11yway.core.passive_security_audit import analyze_passive_security


def _types(issues):
    return {issue.issue_type for issue in issues}


FORM_CASES = [
    ('<input required name="name">', "form_required_instruction_missing"),
    ('<input aria-required="true" name="name">', "form_required_instruction_missing"),
    ('<textarea required></textarea>', "form_required_instruction_missing"),
    ('<select required><option>A</option></select>', "form_required_instruction_missing"),
    ('<input aria-invalid="true" name="email">', "form_error_not_described"),
    ('<textarea aria-invalid="true"></textarea>', "form_error_not_described"),
    ('<input type="email" name="email">', "form_autocomplete_missing"),
    ('<input type="tel" name="phone">', "form_autocomplete_missing"),
    ('<input type="password" name="pw">', "form_autocomplete_missing"),
    ('<input type="date" name="birth">', "form_autocomplete_missing"),
    ('<button>Show password</button>', "show_password_state_missing"),
    ('<form method="post" action="/send"><input name="q"></form>', "form_submission_blocked_safe_mode"),
]


MEDIA_CASES = [
    ('<video autoplay src="a.mp4"></video>', "media_autoplay_without_control"),
    ('<audio autoplay src="a.mp3"></audio>', "media_autoplay_without_control"),
    ('<video src="a.mp4"></video>', "media_caption_track_missing"),
    ('<video><track kind="captions" src="c.vtt"></video>', "media_caption_language_missing"),
    ('<video controls src="a.mp4"></video>', "media_transcript_not_found"),
    ('<audio controls src="a.mp3"></audio>', "media_transcript_not_found"),
    ('<video autoplay loop muted src="bg.mp4"></video>', "media_decorative_background_review"),
    ('<img src="spinner.gif" alt="Loading">', "media_animated_gif_review"),
    ('<video controls><track kind="metadata" src="m.vtt"></video>', "media_caption_track_missing"),
    ('<video controls><track kind="subtitles" src="s.vtt"></video>', "media_caption_language_missing"),
]


COGNITIVE_CASES = [
    ("<a href='/x'>Click here</a>", "cognitive_ambiguous_action_text"),
    ("<a href='/x'>Read more</a>", "cognitive_ambiguous_action_text"),
    ("<button>Continue</button>", "cognitive_ambiguous_action_text"),
    ("<button>Go</button>", "cognitive_ambiguous_action_text"),
    ("<button>Delete record</button>", "cognitive_destructive_action_review"),
    ("<a href='/remove'>Remove item</a>", "cognitive_destructive_action_review"),
    ("<p>Password must require at least one uppercase symbol and special character.</p>", "cognitive_complex_password_rules"),
    ("<p>This instruction sentence contains many separate clauses and repeated conditions for students who must review eligibility, gather documentation, check identity, confirm deadlines, compare aid offers, contact offices, upload evidence, revisit forms, track changing statuses, and finish the process without missing hidden requirements.</p>", "cognitive_dense_text_review"),
]


LANGUAGE_CASES = [
    ('<html lang="bad_code"><body>Hello</body></html>', "language_invalid_code"),
    ("<html lang='en'><body>यह हिंदी सामग्री लंबी है और भाषा टैग चाहिए</body></html>", "language_passage_lang_missing"),
    ("<html lang='en'><body>ਪੰਜਾਬੀ ਸਮੱਗਰੀ ਲਈ ਭਾਸ਼ਾ ਟੈਗ ਚਾਹੀਦਾ ਹੈ</body></html>", "language_passage_lang_missing"),
    ("<html lang='en'><body>বাংলা ভাষার এই অংশে ভাষা ট্যাগ থাকা উচিত</body></html>", "language_passage_lang_missing"),
    ("<html lang='en'><body>தமிழ் உள்ளடக்கத்திற்கு மொழி குறி தேவை</body></html>", "language_passage_lang_missing"),
    ("<html lang='en'><body>తెలుగు సమాచారం కోసం భాష గుర్తు అవసరం</body></html>", "language_passage_lang_missing"),
    ("<html lang='en'><body>مرحبا هذا نص عربي يحتاج اتجاه صحيح</body></html>", "language_rtl_direction_missing"),
    ('<button aria-label="हिंदी विकल्प">X</button>', "language_accessible_name_lang_missing"),
]


COMPONENT_CASES = [
    ('<div id="x"></div><button id="x">X</button>', "component_duplicate_id"),
    ('<div role="dialog"></div>', "component_name_missing"),
    ('<div role="dialog">Settings</div>', "component_required_state_missing"),
    ('<div role="alertdialog">Confirm</div>', "component_required_state_missing"),
    ('<button role="tab">One</button>', "component_required_state_missing"),
    ('<input role="combobox" aria-label="City">', "component_required_state_missing"),
    ('<div role="menuitem">Open</div>', "component_required_state_missing"),
    ('<div role="slider" aria-label="Volume"></div>', "component_required_state_missing"),
    ('<div role="spinbutton" aria-label="Count"></div>', "component_required_state_missing"),
    ('<div role="treeitem">Section</div>', "component_required_state_missing"),
    ('<div class="carousel"><img alt="Slide"></div>', "component_carousel_pause_missing"),
    ('<div role="grid" aria-label=""></div>', "component_name_missing"),
]


SECURITY_CASES = [
    ("<main>OK</main>", "http://example.test", "security_http_not_https"),
    ('<script src="http://cdn.example.test/app.js"></script>', "https://example.test", "security_mixed_content_script"),
    ('<script src="https://cdn.example.test/app.js"></script>', "https://example.test", "security_external_script_no_sri"),
    ('<form action="http://example.test/post"></form>', "https://example.test", "security_insecure_form_action"),
    ('<input type="password">', "http://example.test", "security_password_on_http"),
    ("<!-- token: abc -->", "https://example.test", "security_sensitive_comment_pattern"),
    ("<!-- secret=value -->", "https://example.test", "security_sensitive_comment_pattern"),
    ("<!-- password=123 -->", "https://example.test", "security_sensitive_comment_pattern"),
    ("<main>OK</main>", "https://example.test", "security_hsts_missing"),
    ("<main>OK</main>", "https://example.test", "security_csp_missing"),
]


@pytest.mark.parametrize(("html", "expected"), FORM_CASES)
def test_forms_detection_matrix(html: str, expected: str) -> None:
    issues, _result = analyze_forms(html, "fixture")

    assert expected in _types(issues)


@pytest.mark.parametrize(("html", "expected"), MEDIA_CASES)
def test_media_detection_matrix(html: str, expected: str) -> None:
    issues, _result = analyze_media(html, "fixture")

    assert expected in _types(issues)


@pytest.mark.parametrize(("html", "expected"), COGNITIVE_CASES)
def test_cognitive_detection_matrix(html: str, expected: str) -> None:
    issues, _result = analyze_cognitive(html, "fixture")

    assert expected in _types(issues)


@pytest.mark.parametrize(("html", "expected"), LANGUAGE_CASES)
def test_language_detection_matrix(html: str, expected: str) -> None:
    issues, _result = analyze_language(html, "fixture")

    assert expected in _types(issues)


@pytest.mark.parametrize(("html", "expected"), COMPONENT_CASES)
def test_component_detection_matrix(html: str, expected: str) -> None:
    issues, _result = analyze_components(html, "fixture")

    assert expected in _types(issues)


@pytest.mark.parametrize(("html", "source", "expected"), SECURITY_CASES)
def test_passive_security_detection_matrix(html: str, source: str, expected: str) -> None:
    issues, _result = analyze_passive_security(html, source)

    assert expected in _types(issues)
