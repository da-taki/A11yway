from __future__ import annotations

import json

import pytest

from a11yway.core.capabilities import detect_capabilities, format_capabilities_cli
from a11yway.core.extended_results import ExtendedCheckResult
from a11yway.core.report_builder import build_json_report, save_json_report
from a11yway.main import main, parse_args


def test_verbose_flag_parses_without_enabling_modes() -> None:
    args = parse_args(["examples/sample_form.html", "--verbose"])

    assert args.verbose is True
    assert not args.browser
    assert not args.passive_security


def test_verbose_static_run_prints_mode_details(tmp_path, capsys) -> None:
    page = tmp_path / "page.html"
    page.write_text('<html lang="en"><head><title>T</title></head><body><h1>T</h1></body></html>', encoding="utf-8")

    exit_code = main([str(page), "--verbose"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Verbose: modes=static" in captured.out


def test_invalid_device_choice_exits_from_argparse() -> None:
    with pytest.raises(SystemExit):
        parse_args(["examples/sample_form.html", "--mobile", "--device", "watch"])


def test_capabilities_status_values_are_known(monkeypatch) -> None:
    monkeypatch.setattr("a11yway.core.capabilities._module_available", lambda name: name == "playwright")
    monkeypatch.setattr("a11yway.core.capabilities._which", lambda *_names: None)
    monkeypatch.setattr("a11yway.core.capabilities._adb_devices", lambda _path: [])

    capabilities = detect_capabilities(verify_browsers=False)
    rendered = format_capabilities_cli(capabilities)

    assert capabilities["playwright"]["status"] == "available_untested"
    assert capabilities["browsers"]["chromium"]["status"] == "available_untested"
    assert "Chromium: available_untested" in rendered


def test_capabilities_json_output_is_written(tmp_path) -> None:
    out = tmp_path / "capabilities.json"

    exit_code = main(["--capabilities", "--json", str(out)])
    data = json.loads(out.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert data["platform"]["python"]


def test_report_json_file_is_sorted_and_schema_tagged(tmp_path) -> None:
    report = build_json_report(
        "fixture.html",
        [],
        extended_results=[ExtendedCheckResult(module="forms", check_id="forms").to_json()],
    )
    out = tmp_path / "report.json"

    save_json_report(report, out)
    text = out.read_text(encoding="utf-8")
    data = json.loads(text)

    assert '"extended_result_schema_version"' in text
    assert data["report_schema_version"] == "1.0"

