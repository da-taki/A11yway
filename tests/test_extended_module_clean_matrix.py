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


@pytest.mark.parametrize(
    ("html", "unexpected"),
    [
        ('<input required aria-describedby="name-help"><p id="name-help">Required.</p>', "form_required_instruction_missing"),
        ('<input aria-invalid="true" aria-describedby="error"><p id="error">Fix it.</p>', "form_error_not_described"),
        ('<input type="email" autocomplete="email">', "form_autocomplete_missing"),
        ('<button aria-pressed="false">Show password</button>', "show_password_state_missing"),
        ('<form method="get"><input name="q"></form>', "form_submission_blocked_safe_mode"),
    ],
)
def test_form_clean_matrix(html: str, unexpected: str) -> None:
    issues, _result = analyze_forms(html, "fixture")

    assert unexpected not in _types(issues)


@pytest.mark.parametrize(
    ("html", "unexpected"),
    [
        ('<video muted autoplay loop src="bg.mp4"></video><a href="/transcript">Transcript</a>', "media_transcript_not_found"),
        ('<video muted src="bg.mp4"></video>', "media_caption_track_missing"),
        ('<track kind="captions" srclang="en" src="c.vtt">', "media_caption_language_missing"),
        ('<img src="photo.jpg" alt="Photo">', "media_animated_gif_review"),
    ],
)
def test_media_clean_matrix(html: str, unexpected: str) -> None:
    issues, _result = analyze_media(html, "fixture")

    assert unexpected not in _types(issues)


@pytest.mark.parametrize(
    ("html", "unexpected"),
    [
        ('<a href="/aid" aria-label="Read more about financial aid">Read more</a>', "cognitive_ambiguous_action_text"),
        ("<button>Delete record</button><p>Confirm before deleting.</p>", "cognitive_destructive_action_review"),
        ("<p>Password rules are short and clear.</p>", "cognitive_complex_password_rules"),
    ],
)
def test_cognitive_clean_matrix(html: str, unexpected: str) -> None:
    issues, _result = analyze_cognitive(html, "fixture")

    assert unexpected not in _types(issues)


@pytest.mark.parametrize(
    ("html", "unexpected"),
    [
        ("<html lang='hi'><body>यह हिंदी सामग्री लंबी है और भाषा टैग चाहिए</body></html>", "language_passage_lang_missing"),
        ("<html lang='en'><body><span dir='rtl'>مرحبا هذا نص عربي يحتاج اتجاه صحيح</span></body></html>", "language_rtl_direction_missing"),
        ('<button lang="hi" aria-label="हिंदी विकल्प">X</button>', "language_accessible_name_lang_missing"),
    ],
)
def test_language_clean_matrix(html: str, unexpected: str) -> None:
    issues, _result = analyze_language(html, "fixture")

    assert unexpected not in _types(issues)


@pytest.mark.parametrize(
    ("html", "unexpected"),
    [
        ('<div role="dialog" aria-modal="true" aria-label="Settings"></div>', "component_required_state_missing"),
        ('<button role="tab" aria-selected="true">One</button>', "component_required_state_missing"),
        ('<div class="carousel"><button>Pause</button></div>', "component_carousel_pause_missing"),
    ],
)
def test_component_clean_matrix(html: str, unexpected: str) -> None:
    issues, _result = analyze_components(html, "fixture")

    assert unexpected not in _types(issues)


@pytest.mark.parametrize(
    ("html", "source", "unexpected"),
    [
        ('<script src="https://cdn.example.test/app.js" integrity="sha384-test"></script>', "https://example.test", "security_external_script_no_sri"),
        ('<form action="https://example.test/post"></form>', "https://example.test", "security_insecure_form_action"),
        ('<input type="password">', "https://example.test", "security_password_on_http"),
    ],
)
def test_passive_security_clean_matrix(html: str, source: str, unexpected: str) -> None:
    issues, _result = analyze_passive_security(html, source)

    assert unexpected not in _types(issues)

