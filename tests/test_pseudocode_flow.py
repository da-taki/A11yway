"""Lightweight tests for the A11yway pseudocode scaffold."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import csv
import json
from pathlib import Path
import threading

from a11yway.agents.dyslexia_agent import DyslexiaAgent
from a11yway.agents.hearing_agent import HearingAgent
from a11yway.agents.keyboard_agent import KeyboardOnlyAgent
from a11yway.agents.low_vision_agent import LowVisionAgent
from a11yway.main import analyze_html_file, main
from a11yway.core.batch_runner import load_batch_config, run_batch
from a11yway.core.page_analyzer import (
    analyze_heading_structure,
    analyze_html_forms,
    analyze_html_static,
    analyze_images,
    analyze_interactive_names,
    analyze_media_accessibility,
    analyze_page_metadata,
)
from a11yway.core.report_builder import (
    ReportBuilder,
    build_json_report,
    build_markdown_report,
    save_json_report,
    save_markdown_report,
)
from a11yway.core.source_loader import is_url, load_html_source
from a11yway.core.task_runner import (
    TaskRunner,
    build_task_blockers,
    filter_issues_for_task,
    find_task,
    load_tasks,
)


def issue_types_for(issues: list) -> set[str]:
    """Return issue types from a list of accessibility issues."""
    return {issue.issue_type for issue in issues}


def evidence_text_for(issues: list) -> str:
    """Return searchable text from string or structured issue evidence."""
    parts = []
    for issue in issues:
        if isinstance(issue.evidence, dict):
            parts.extend(str(value) for value in issue.evidence.values())
        else:
            parts.append(issue.evidence)
    return " ".join(parts)


class _StaticHTMLHandler(BaseHTTPRequestHandler):
    """Small local HTTP handler for URL loading tests."""

    def do_GET(self) -> None:
        """Serve one static HTML response."""
        body = b'<!doctype html><html lang="en"><head><title>Test</title></head><body><h1>Test</h1></body></html>'
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        """Keep test output quiet."""
        return


def load_from_local_test_server() -> dict:
    """Load HTML through a local standard-library HTTP server."""
    server = HTTPServer(("127.0.0.1", 0), _StaticHTMLHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        return load_html_source(f"http://{host}:{port}/")
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_sample_agents_can_be_instantiated() -> None:
    """The initial student agents should be easy to construct."""
    agents = [
        KeyboardOnlyAgent(),
        LowVisionAgent(),
        DyslexiaAgent(),
        HearingAgent(),
    ]

    assert [agent.name for agent in agents] == [
        "Keyboard-only student",
        "Low-vision student",
        "Dyslexia/reading-difficulty student",
        "Hearing-impaired student",
    ]


def test_sample_task_can_be_loaded() -> None:
    """The sample task JSON should load into task dataclasses."""
    runner = TaskRunner(agents=[])
    tasks = runner.load_tasks(Path("examples/sample_tasks.json"))

    assert len(tasks) == 2
    assert tasks[0].id == "submit_scholarship_application"
    assert tasks[0].name == "Submit scholarship application"


def test_report_builder_returns_expected_structure() -> None:
    """ReportBuilder should return a structured report object."""
    runner = TaskRunner(agents=[KeyboardOnlyAgent()])
    task = runner.load_tasks(Path("examples/sample_tasks.json"))[0]

    report = ReportBuilder().build_report(
        task=task,
        agents_used=["Keyboard-only student"],
        issues=[],
    )

    assert report.task.title == task.title
    assert report.agents_used == ["Keyboard-only student"]
    assert report.issues == []
    assert "Found 0 placeholder issue" in report.summary


def test_unlabeled_input_is_flagged() -> None:
    """A text input without an accessible label should be reported."""
    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_form_label"
    assert issues[0].evidence["name"] == "student_name"


def test_input_with_label_for_is_not_flagged() -> None:
    """An input with an associated label should pass this basic check."""
    html = '<label for="email">Email</label><input id="email" type="email">'

    assert analyze_html_forms(html) == []


def test_hidden_and_submit_inputs_are_ignored() -> None:
    """Inputs that do not need student-entered labels should be ignored."""
    html = '<input type="hidden" name="token"><input type="submit" value="Send">'

    assert analyze_html_forms(html) == []


def test_keyboard_agent_uses_html_form_analyzer() -> None:
    """KeyboardOnlyAgent should run static checks when HTML is available."""
    runner = TaskRunner(agents=[])
    task = runner.load_tasks(Path("examples/sample_tasks.json"))[0]
    agent = KeyboardOnlyAgent()

    findings = agent.detect_barriers(
        task,
        {"html": '<form><input type="text" name="student_name"></form>'},
    )

    assert any(issue.issue_type == "missing_form_label" for issue in findings)


def test_sample_form_fixture_exists() -> None:
    """The CLI sample fixture should be present."""
    assert Path("examples/sample_form.html").exists()


def test_is_url_detects_http_and_https() -> None:
    """Only http and https sources should be treated as URLs."""
    assert is_url("https://example.com")
    assert is_url("http://example.com")
    assert not is_url("examples/sample_form.html")


def test_load_html_source_reads_local_file() -> None:
    """Source loader should read local HTML fixtures."""
    result = load_html_source("examples/sample_form.html")

    assert result["source_type"] == "file"
    assert result["error"] is None
    assert "Student Scholarship Application" in result["html"]


def test_load_html_source_reads_local_http_server() -> None:
    """URL loading should work with a local standard-library HTTP server."""
    result = load_from_local_test_server()

    assert result["source_type"] == "url"
    assert result["status_code"] == 200
    assert result["error"] is None
    assert "<h1>Test</h1>" in result["html"]


def test_sample_form_returns_expected_missing_label_count() -> None:
    """The sample form should contain the expected static audit issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert len(issues) == 7
    assert issue_types_for(issues) == {
        "missing_form_label",
        "generic_link_text",
        "missing_button_name",
        "missing_image_alt",
        "skipped_heading_level",
        "missing_video_captions",
    }


def test_sample_form_labeled_fields_are_not_flagged() -> None:
    """Properly labeled email and school controls should not be reported."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    evidence = evidence_text_for(issues)

    assert "student_email" not in evidence
    assert "school_name" not in evidence


def test_sample_form_hidden_and_submit_fields_are_ignored() -> None:
    """Hidden and submit fields in the sample should not become issues."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    evidence = evidence_text_for(issues)

    assert "application_token" not in evidence
    assert "submit" not in evidence.lower()


def test_empty_button_is_flagged() -> None:
    """A button without text or an accessible name should be reported."""
    issues = analyze_interactive_names("<button></button>")

    assert "missing_button_name" in issue_types_for(issues)


def test_button_with_aria_label_is_not_flagged() -> None:
    """A button with aria-label should pass this basic static check."""
    issues = analyze_interactive_names('<button aria-label="Save draft"></button>')

    assert "missing_button_name" not in issue_types_for(issues)


def test_generic_click_here_link_is_flagged() -> None:
    """Generic link text should be reported."""
    issues = analyze_interactive_names('<a href="/help">click here</a>')

    assert "generic_link_text" in issue_types_for(issues)


def test_descriptive_link_is_not_flagged() -> None:
    """Specific link text should not be treated as generic."""
    issues = analyze_interactive_names(
        '<a href="/guidelines">Download scholarship guidelines</a>'
    )

    assert issue_types_for(issues) == set()


def test_missing_image_alt_is_flagged() -> None:
    """An image without alt should be reported."""
    issues = analyze_images('<img src="award.png">')

    assert "missing_image_alt" in issue_types_for(issues)


def test_image_with_alt_is_not_flagged() -> None:
    """An image with useful alt text should pass this basic check."""
    issues = analyze_images('<img src="award.png" alt="Student receiving an award">')

    assert "missing_image_alt" not in issue_types_for(issues)


def test_missing_h1_is_flagged() -> None:
    """A page without h1 should be reported."""
    html = '<html lang="en"><head><title>Page</title></head><body><h2>Start</h2></body></html>'
    issues = analyze_heading_structure(html)

    assert "missing_h1" in issue_types_for(issues)


def test_skipped_heading_level_is_flagged() -> None:
    """A jump from h1 to h3 should be reported."""
    issues = analyze_heading_structure("<h1>Application</h1><h3>Details</h3>")

    assert "skipped_heading_level" in issue_types_for(issues)


def test_missing_title_is_flagged() -> None:
    """A page without title should be reported."""
    html = '<html lang="en"><body><h1>Application</h1></body></html>'
    issues = analyze_page_metadata(html)

    assert "missing_page_title" in issue_types_for(issues)


def test_missing_html_lang_is_flagged() -> None:
    """A page without html lang should be reported."""
    html = "<html><head><title>Application</title></head><body><h1>Application</h1></body></html>"
    issues = analyze_page_metadata(html)

    assert "missing_html_lang" in issue_types_for(issues)


def test_video_without_captions_is_flagged() -> None:
    """A video without captions or subtitles should be reported."""
    issues = analyze_media_accessibility('<video controls src="lesson.mp4"></video>')

    assert "missing_video_captions" in issue_types_for(issues)


def test_missing_form_label_evidence_includes_snippet() -> None:
    """Missing label findings should include a useful HTML snippet."""
    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    evidence = issues[0].evidence
    assert isinstance(evidence, dict)
    assert "snippet" in evidence
    assert "<input" in evidence["snippet"]


def test_missing_form_label_evidence_includes_tag_and_name() -> None:
    """Form evidence should include tag and identifying attributes when available."""
    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    evidence = issues[0].evidence
    assert evidence["tag"] == "input"
    assert evidence["name"] == "student_name"


def test_generic_link_evidence_includes_text_and_href() -> None:
    """Generic link evidence should include link text and destination."""
    issues = analyze_interactive_names('<a href="/help">click here</a>')

    evidence = issues[0].evidence
    assert evidence["text"] == "click here"
    assert evidence["href"] == "/help"


def test_missing_image_alt_evidence_includes_src() -> None:
    """Image alt evidence should include the image source when available."""
    issues = analyze_images('<img src="award.png">')

    evidence = issues[0].evidence
    assert evidence["src"] == "award.png"


def test_issue_evidence_includes_line_key_when_possible() -> None:
    """Element evidence should include an approximate line number key."""
    html = '<form>\n<input type="text" name="student_name">\n</form>'
    issues = analyze_html_forms(html)

    evidence = issues[0].evidence
    assert "line" in evidence
    assert evidence["line"] in {2, None}


def test_static_analyzer_combines_checks() -> None:
    """The combined analyzer should return issue types from multiple checks."""
    html = '<html><body><h1>Page</h1><button></button><img src="x.png"></body></html>'
    issues = analyze_html_static(html)

    assert {"missing_button_name", "missing_image_alt", "missing_page_title"}.issubset(
        issue_types_for(issues)
    )


def test_build_json_report_returns_expected_top_level_keys() -> None:
    """The CLI JSON report should have a stable prototype structure."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert set(report) == {
        "tool",
        "version",
        "source_file",
        "summary",
        "issues",
        "limitations",
    }


def test_build_json_report_has_correct_issue_count() -> None:
    """The report summary should match the issue list length."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert report["summary"]["issues_found"] == 7
    assert len(report["issues"]) == 7


def test_json_report_includes_issue_counts() -> None:
    """The report summary should include useful grouped counts."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert "counts_by_severity" in report["summary"]
    assert "counts_by_issue_type" in report["summary"]
    assert report["summary"]["counts_by_issue_type"]["missing_form_label"] == 2


def test_json_report_preserves_structured_evidence_fields() -> None:
    """JSON report issues should include structured evidence, not only text."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    first_issue_evidence = report["issues"][0]["evidence"]

    assert "snippet" in first_issue_evidence
    assert "reason" in first_issue_evidence
    assert "line" in first_issue_evidence


def test_save_json_report_writes_valid_json(tmp_path: Path) -> None:
    """JSON reports should be written to disk with parent directories created."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.json"

    save_json_report(report, output_path)

    saved_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_report["tool"] == "A11yway"
    assert saved_report["summary"]["issues_found"] == 7


def test_sample_tasks_load_correctly() -> None:
    """Task scenario helpers should load the sample task file."""
    tasks = load_tasks("examples/sample_tasks.json")

    assert len(tasks) == 2
    assert tasks[0].student_profile == "Keyboard-only student"
    assert "missing_form_label" in tasks[0].relevant_issue_types


def test_find_task_by_id() -> None:
    """A task should be found by exact id."""
    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit_scholarship_application")

    assert task is not None
    assert task.name == "Submit scholarship application"


def test_find_task_by_name_case_insensitively() -> None:
    """A task should be found by case-insensitive name."""
    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit scholarship APPLICATION")

    assert task is not None
    assert task.id == "submit_scholarship_application"


def test_filter_issues_for_task_returns_relevant_issue_types() -> None:
    """Task filtering should keep only task-relevant issue types."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    filtered = filter_issues_for_task(task, issues)

    assert issue_types_for(filtered) == {
        "missing_form_label",
        "missing_button_name",
        "generic_link_text",
        "skipped_heading_level",
    }


def test_task_blockers_are_generated_from_relevant_issues() -> None:
    """Task blockers should be deterministic notes from relevant issues."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    blockers = build_task_blockers(task, issues)

    assert len(blockers) == 5
    assert {blocker["issue_type"] for blocker in blockers} == {
        "missing_form_label",
        "missing_button_name",
        "generic_link_text",
        "skipped_heading_level",
    }
    assert all("task_impact" in blocker for blocker in blockers)


def test_json_report_includes_task_data_when_task_is_provided() -> None:
    """JSON reports should include task context when requested."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    blockers = build_task_blockers(task, issues)
    report = build_json_report(
        "examples/sample_form.html",
        issues,
        task=task,
        task_blockers=blockers,
    )

    assert report["task"]["id"] == "submit_scholarship_application"
    assert report["task"]["student_profile"] == "Keyboard-only student"
    assert len(report["task"]["likely_blockers"]) == 5


def test_json_report_includes_source_metadata() -> None:
    """JSON reports should include optional source metadata."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    source_metadata = load_html_source("examples/sample_form.html")
    report = build_json_report(
        "examples/sample_form.html",
        issues,
        source_metadata=source_metadata,
    )

    assert report["source"]["input"] == "examples/sample_form.html"
    assert report["source"]["type"] == "file"


def test_build_markdown_report_returns_string() -> None:
    """Markdown report builder should return a string."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert isinstance(markdown, str)


def test_markdown_report_includes_summary_and_issue_types() -> None:
    """Markdown should include the core report sections and issue type details."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert "# A11yway Accessibility Report" in markdown
    assert "## Summary" in markdown
    assert "Issues found: 7" in markdown
    assert "missing_form_label" in markdown


def test_markdown_report_includes_task_context() -> None:
    """Markdown should include task context when task data exists."""
    tasks = load_tasks("examples/sample_tasks.json")
    task = find_task(tasks, "submit_scholarship_application")
    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert task is not None
    report = build_json_report(
        "examples/sample_form.html",
        issues,
        task=task,
        task_blockers=build_task_blockers(task, issues),
    )
    markdown = build_markdown_report(report)

    assert "## Task Context" in markdown
    assert "Submit scholarship application" in markdown
    assert "Likely Blockers" in markdown


def test_markdown_report_includes_evidence_snippets() -> None:
    """Markdown should show HTML evidence snippets in fenced code blocks."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert "```html" in markdown
    assert '<input type="text" name="student_name">' in markdown


def test_save_markdown_report_writes_file(tmp_path: Path) -> None:
    """Markdown reports should be written to disk with parent directories created."""
    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.md"

    save_markdown_report(report, output_path)

    markdown = output_path.read_text(encoding="utf-8")
    assert "# A11yway Accessibility Report" in markdown


def test_cli_default_sample_still_runs(capsys) -> None:
    """The no-argument CLI flow should still analyze the sample fixture."""
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Issues found: 7" in captured.out


def test_cli_task_mode_runs(capsys) -> None:
    """Task mode should print task context without breaking the audit."""
    exit_code = main(
        ["examples/sample_form.html", "--task", "submit_scholarship_application"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Task: Submit scholarship application" in captured.out
    assert "Likely blockers: 5" in captured.out


def test_cli_markdown_mode_writes_report(tmp_path: Path, capsys) -> None:
    """CLI should save Markdown reports without breaking task mode."""
    output_path = tmp_path / "reports" / "sample_form_report.md"

    exit_code = main(
        [
            "examples/sample_form.html",
            "--task",
            "submit_scholarship_application",
            "--markdown",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Markdown report saved" in captured.out
    assert "# A11yway Accessibility Report" in output_path.read_text(encoding="utf-8")


def test_sample_batch_config_loads_correctly() -> None:
    """The sample batch config should load two audit items."""
    items = load_batch_config("examples/sample_batch.json")

    assert len(items) == 2
    assert items[0]["id"] == "scholarship_form"
    assert items[1]["source"] == "examples/sample_resource_page.html"


def test_batch_runner_processes_sample_pages(tmp_path: Path) -> None:
    """Batch runner should process both sample pages."""
    result = run_batch("examples/sample_batch.json", tmp_path / "batch_sample")

    assert result["index"]["summary"]["total_pages_tested"] == 2
    assert len(result["index"]["sources"]) == 2


def test_batch_runner_writes_per_page_reports(tmp_path: Path) -> None:
    """Batch runner should create JSON and Markdown reports for each item."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    assert (out_dir / "scholarship_form.json").exists()
    assert (out_dir / "scholarship_form.md").exists()
    assert (out_dir / "learning_resources.json").exists()
    assert (out_dir / "learning_resources.md").exists()


def test_batch_index_json_contains_total_pages(tmp_path: Path) -> None:
    """Batch index JSON should summarize the number of pages tested."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
    assert index["summary"]["total_pages_tested"] == 2
    assert index["summary"]["total_issues"] >= 2


def test_batch_index_markdown_includes_sources_and_total(tmp_path: Path) -> None:
    """Batch index Markdown should include source names and total issue count."""
    out_dir = tmp_path / "batch_sample"
    result = run_batch("examples/sample_batch.json", out_dir)

    markdown = (out_dir / "index.md").read_text(encoding="utf-8")
    assert "Student Scholarship Application" in markdown
    assert "Learning Resources Page" in markdown
    assert f"- Total issues: {result['index']['summary']['total_issues']}" in markdown


def test_batch_run_creates_index_csv(tmp_path: Path) -> None:
    """Batch runner should create a CSV index by default."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    assert (out_dir / "index.csv").exists()


def test_batch_csv_has_expected_headers(tmp_path: Path) -> None:
    """CSV index should include spreadsheet-friendly headers."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == [
            "id",
            "name",
            "source",
            "source_type",
            "task",
            "status",
            "issues_found",
            "task_blockers",
            "browser_status",
            "browser_issue_count",
            "task_execution_status",
            "task_steps_passed",
            "task_steps_total",
            "high_count",
            "medium_count",
            "low_count",
            "issue_types",
            "json_report",
            "markdown_report",
            "html_report",
            "error",
        ]


def test_batch_csv_has_one_row_per_batch_item(tmp_path: Path) -> None:
    """CSV index should have one data row for each batch item."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2


def test_batch_csv_includes_issue_counts(tmp_path: Path) -> None:
    """CSV rows should include issue counts and severity counts."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["issues_found"] == "7"
    assert int(rows[0]["high_count"]) >= 1


def test_batch_csv_includes_report_paths(tmp_path: Path) -> None:
    """CSV rows should include JSON and Markdown report paths."""
    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["json_report"].endswith("scholarship_form.json")
    assert rows[0]["markdown_report"].endswith("scholarship_form.md")


def test_batch_csv_override_path(tmp_path: Path) -> None:
    """Batch runner should allow a custom CSV output path."""
    out_dir = tmp_path / "batch_sample"
    csv_path = tmp_path / "custom" / "benchmark.csv"
    result = run_batch("examples/sample_batch.json", out_dir, csv_path=csv_path)

    assert csv_path.exists()
    assert result["csv_index_path"] == csv_path.as_posix()


def test_batch_runner_continues_if_one_source_fails(tmp_path: Path) -> None:
    """Batch mode should include failed sources in the index and continue."""
    config_path = tmp_path / "batch_with_failure.json"
    config_path.write_text(
        json.dumps(
            [
                {
                    "id": "valid_page",
                    "name": "Valid Page",
                    "source": "examples/sample_form.html",
                    "task": "submit_scholarship_application",
                },
                {
                    "id": "missing_page",
                    "name": "Missing Page",
                    "source": str(tmp_path / "missing.html"),
                    "task": "access_learning_resources",
                },
            ]
        ),
        encoding="utf-8",
    )

    result = run_batch(config_path, tmp_path / "batch_output")
    sources = result["index"]["sources"]

    assert result["index"]["summary"]["total_pages_tested"] == 2
    assert sources[0]["status"] == "passed"
    assert sources[1]["status"] == "failed"
    assert sources[1]["issue_count"] == 0
    assert sources[1]["error"]


def test_cli_batch_mode_writes_index(tmp_path: Path, capsys) -> None:
    """CLI batch mode should write index reports."""
    out_dir = tmp_path / "batch_sample"

    exit_code = main(
        [
            "--batch",
            "examples/sample_batch.json",
            "--out-dir",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Pages tested: 2" in captured.out
    assert (out_dir / "index.json").exists()
    assert (out_dir / "index.md").exists()
    assert (out_dir / "index.csv").exists()


def test_cli_batch_mode_accepts_csv_override(tmp_path: Path, capsys) -> None:
    """CLI batch mode should accept --csv for a custom benchmark path."""
    out_dir = tmp_path / "batch_sample"
    csv_path = tmp_path / "custom" / "index.csv"

    exit_code = main(
        [
            "--batch",
            "examples/sample_batch.json",
            "--out-dir",
            str(out_dir),
            "--csv",
            str(csv_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Index CSV:" in captured.out
    assert csv_path.exists()
