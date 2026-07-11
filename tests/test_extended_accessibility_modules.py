from __future__ import annotations

import json
from pathlib import Path

from a11yway.core.capabilities import detect_capabilities, format_capabilities_cli
from a11yway.core.cognitive_audit import analyze_cognitive
from a11yway.core.component_audit import analyze_components
from a11yway.core.document_audit import analyze_document
from a11yway.core.forms_audit import analyze_forms
from a11yway.core.language_audit import analyze_language
from a11yway.core.media_audit import analyze_media
from a11yway.core.mobile_audit import run_mobile_audit
from a11yway.core.passive_security_audit import PASSIVE_SECURITY_NOTE, analyze_passive_security
from a11yway.core.report_builder import build_html_report, build_json_report, build_markdown_report
from a11yway.core.screen_reader_audit import run_screen_reader_audit
from a11yway.core.workflow_audit import run_workflow_audit
from a11yway.main import _apply_all_accessibility_modules, parse_args


ROOT = Path(__file__).resolve().parents[1]


def _html(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _types(issues):
    return {issue.issue_type for issue in issues}


def test_capabilities_report_missing_optional_tools_without_crashing():
    capabilities = detect_capabilities(verify_browsers=False)
    assert "playwright" in capabilities
    assert "screen_readers" in capabilities
    rendered = format_capabilities_cli(capabilities)
    assert "A11yway capability detection" in rendered
    assert "Missing optional tools" in rendered


def test_cli_all_modules_does_not_enable_passive_security():
    args = parse_args(["examples/sample_form.html", "--all-accessibility-modules"])
    _apply_all_accessibility_modules(args)
    assert args.screen_reader
    assert args.mobile
    assert args.forms
    assert args.cognitive
    assert args.language_audit
    assert args.media
    assert args.components
    assert not args.passive_security


def test_forms_problematic_and_clean_fixtures():
    broken, result = analyze_forms(_html("examples/forms/problematic.html"), "fixture")
    assert result["module"] == "forms"
    assert {
        "form_required_instruction_missing",
        "form_error_not_described",
        "show_password_state_missing",
        "form_submission_blocked_safe_mode",
    }.issubset(_types(broken))
    clean, _ = analyze_forms(_html("examples/forms/clean.html"), "fixture")
    assert not _types(clean)


def test_media_cognitive_language_component_and_security_modules():
    media, _ = analyze_media(_html("examples/media/problematic.html"), "fixture")
    assert "media_autoplay_without_control" in _types(media)
    cognitive, _ = analyze_cognitive(_html("examples/cognitive/problematic.html"), "fixture")
    assert "cognitive_ambiguous_action_text" in _types(cognitive)
    language, _ = analyze_language(_html("examples/languages/problematic.html"), "fixture")
    assert "language_rtl_direction_missing" in _types(language)
    components, _ = analyze_components(_html("examples/components/problematic.html"), "fixture")
    assert "component_duplicate_id" in _types(components)
    security, result = analyze_passive_security(
        _html("examples/security_passive/problematic_headers_fixture.html"),
        "https://example.test/page",
    )
    assert result["namespace"] == "security"
    assert result["notice"] == PASSIVE_SECURITY_NOTE
    assert "security_mixed_content_script" in _types(security)


def test_passive_security_is_not_in_all_accessibility_fixture_expectations():
    clean_security, _ = analyze_passive_security(
        _html("examples/security_passive/clean.html"),
        "https://example.test/page",
    )
    assert "security_mixed_content_script" not in _types(clean_security)


def test_document_fixtures_are_inspected_without_claiming_conformance():
    pdf_issues, pdf_result = analyze_document(str(ROOT / "examples/documents/problematic.pdf"))
    assert pdf_result["module"] == "documents"
    assert "document_pdf_untagged" in _types(pdf_issues)
    docx_issues, _ = analyze_document(str(ROOT / "examples/documents/problematic.docx"))
    assert "document_title_missing" in _types(docx_issues)
    pptx_issues, _ = analyze_document(str(ROOT / "examples/documents/problematic.pptx"))
    assert "document_slide_title_missing" in _types(pptx_issues)


def test_mobile_module_reports_or_degrades_without_crashing():
    issues, result = run_mobile_audit(
        str(ROOT / "examples/mobile/problematic.html"),
        device="android-small",
        orientations=["portrait"],
        wait_ms=50,
    )
    assert result["module"] == "mobile"
    if result["status"] == "completed":
        assert _types(issues) & {
            "mobile_viewport_overflow",
            "mobile_small_touch_target",
            "mobile_orientation_restriction",
            "mobile_hover_dependent_content",
        }
    else:
        assert result["status"] == "unavailable"


def test_screen_reader_chromium_transcript_from_browser_result():
    browser_result = {
        "success": True,
        "focus_trace": [
            {"step": 1, "tag": "button", "selector": "button", "announce": {"role": "button", "name": "", "states": [], "ignored": False}},
            {"step": 2, "tag": "a", "selector": "a", "announce": {"role": "link", "name": "Read more", "states": [], "ignored": False}},
        ],
    }
    issues, result = run_screen_reader_audit(
        "fixture",
        browser_result,
        engine="chromium",
        include_transcript=True,
    )
    assert "screen_reader_empty_name" in _types(issues)
    assert result["artifacts"]["transcript_count"] == 2
    assert result["capability"]["engine"] == "chromium"


def test_native_screen_reader_adapter_scaffold_when_unavailable():
    issues, result = run_screen_reader_audit("fixture", None, engine="nvda")
    assert issues == []
    assert result["module"] == "screen_reader"
    assert result["status"] in {"scaffolded", "available_untested"}


def test_safe_public_workflow_blocks_submission_terms():
    issues, result = run_workflow_audit(
        ROOT / "examples/workflows/problematic_application.json",
        safe_public_mode=True,
    )
    assert result["status"] == "blocked"
    assert "workflow_safe_mode_blocked_action" in _types(issues)


def test_extended_module_report_serializes_to_json_markdown_and_html():
    issues, forms_result = analyze_forms(_html("examples/forms/problematic.html"), "fixture")
    report = build_json_report("fixture", issues, extended_results=[forms_result])
    assert report["extended_modules"][0]["module"] == "forms"
    markdown = build_markdown_report(report)
    html = build_html_report(report)
    assert "Extended Accessibility Modules" in markdown
    assert "Extended Accessibility Modules" in html
    json.dumps(report)
