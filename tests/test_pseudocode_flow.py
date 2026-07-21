

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

    return {issue.issue_type for issue in issues}


def evidence_text_for(issues: list) -> str:

    parts = []
    for issue in issues:
        if isinstance(issue.evidence, dict):
            parts.extend(str(value) for value in issue.evidence.values())
        else:
            parts.append(issue.evidence)
    return " ".join(parts)


class _StaticHTMLHandler(BaseHTTPRequestHandler):


    def do_GET(self) -> None:

        body = b'<!doctype html><html lang="en"><head><title>Test</title></head><body><h1>Test</h1></body></html>'
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:

        return


def load_from_local_test_server() -> dict:

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

    runner = TaskRunner(agents=[])
    tasks = runner.load_tasks(Path("examples/sample_tasks.json"))

    assert len(tasks) == 3
    assert tasks[0].id == "submit_scholarship_application"
    assert tasks[0].name == "Submit scholarship application"


def test_report_builder_returns_expected_structure() -> None:

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

    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_form_label"
    assert issues[0].evidence["name"] == "student_name"


def test_input_with_label_for_is_not_flagged() -> None:

    html = '<label for="email">Email</label><input id="email" type="email">'

    assert analyze_html_forms(html) == []


def test_hidden_and_submit_inputs_are_ignored() -> None:

    html = '<input type="hidden" name="token"><input type="submit" value="Send">'

    assert analyze_html_forms(html) == []


def test_keyboard_agent_uses_html_form_analyzer() -> None:

    runner = TaskRunner(agents=[])
    task = runner.load_tasks(Path("examples/sample_tasks.json"))[0]
    agent = KeyboardOnlyAgent()

    findings = agent.detect_barriers(
        task,
        {"html": '<form><input type="text" name="student_name"></form>'},
    )

    assert any(issue.issue_type == "missing_form_label" for issue in findings)


def test_sample_form_fixture_exists() -> None:

    assert Path("examples/sample_form.html").exists()


def test_is_url_detects_http_and_https() -> None:

    assert is_url("https://example.com")
    assert is_url("http://example.com")
    assert not is_url("examples/sample_form.html")


def test_load_html_source_reads_local_file() -> None:

    result = load_html_source("examples/sample_form.html")

    assert result["source_type"] == "file"
    assert result["error"] is None
    assert "Student Scholarship Application" in result["html"]


def test_load_html_source_reads_local_http_server() -> None:

    result = load_from_local_test_server()

    assert result["source_type"] == "url"
    assert result["status_code"] == 200
    assert result["error"] is None
    assert "<h1>Test</h1>" in result["html"]


def test_sample_form_returns_expected_missing_label_count() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))

    assert len(issues) == 9
    assert issue_types_for(issues) == {
        "missing_form_label",
        "generic_link_text",
        "missing_button_name",
        "missing_image_alt",
        "skipped_heading_level",
            "missing_video_captions",

            "missing_autocomplete",
            "error_prevention_missing",
        }


def test_sample_form_labeled_fields_are_not_flagged() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    label_evidence = evidence_text_for(
        [issue for issue in issues if issue.issue_type == "missing_form_label"]
    )

    assert "student_email" not in label_evidence
    assert "school_name" not in label_evidence


def test_sample_form_hidden_and_submit_fields_are_ignored() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    evidence = evidence_text_for(issues)

    assert "application_token" not in evidence
    assert "submit" not in evidence.lower()


def test_empty_button_is_flagged() -> None:

    issues = analyze_interactive_names("<button></button>")

    assert "missing_button_name" in issue_types_for(issues)


def test_button_with_aria_label_is_not_flagged() -> None:

    issues = analyze_interactive_names('<button aria-label="Save draft"></button>')

    assert "missing_button_name" not in issue_types_for(issues)


def test_generic_click_here_link_is_flagged() -> None:

    issues = analyze_interactive_names('<a href="/help">click here</a>')

    assert "generic_link_text" in issue_types_for(issues)


def test_descriptive_link_is_not_flagged() -> None:

    issues = analyze_interactive_names(
        '<a href="/guidelines">Download scholarship guidelines</a>'
    )

    assert issue_types_for(issues) == set()


def test_missing_image_alt_is_flagged() -> None:

    issues = analyze_images('<img src="award.png">')

    assert "missing_image_alt" in issue_types_for(issues)


def test_image_with_alt_is_not_flagged() -> None:

    issues = analyze_images('<img src="award.png" alt="Student receiving an award">')

    assert "missing_image_alt" not in issue_types_for(issues)


def test_missing_h1_is_flagged() -> None:

    html = '<html lang="en"><head><title>Page</title></head><body><h2>Start</h2></body></html>'
    issues = analyze_heading_structure(html)

    assert "missing_h1" in issue_types_for(issues)


def test_skipped_heading_level_is_flagged() -> None:

    issues = analyze_heading_structure("<h1>Application</h1><h3>Details</h3>")

    assert "skipped_heading_level" in issue_types_for(issues)


def test_missing_title_is_flagged() -> None:

    html = '<html lang="en"><body><h1>Application</h1></body></html>'
    issues = analyze_page_metadata(html)

    assert "missing_page_title" in issue_types_for(issues)


def test_missing_html_lang_is_flagged() -> None:

    html = "<html><head><title>Application</title></head><body><h1>Application</h1></body></html>"
    issues = analyze_page_metadata(html)

    assert "missing_html_lang" in issue_types_for(issues)


def test_video_without_captions_is_flagged() -> None:

    issues = analyze_media_accessibility('<video controls src="lesson.mp4"></video>')

    assert "missing_video_captions" in issue_types_for(issues)


def test_missing_form_label_evidence_includes_snippet() -> None:

    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    evidence = issues[0].evidence
    assert isinstance(evidence, dict)
    assert "snippet" in evidence
    assert "<input" in evidence["snippet"]


def test_missing_form_label_evidence_includes_tag_and_name() -> None:

    issues = analyze_html_forms('<form><input type="text" name="student_name"></form>')

    evidence = issues[0].evidence
    assert evidence["tag"] == "input"
    assert evidence["name"] == "student_name"


def test_generic_link_evidence_includes_text_and_href() -> None:

    issues = analyze_interactive_names('<a href="/help">click here</a>')

    evidence = issues[0].evidence
    assert evidence["text"] == "click here"
    assert evidence["href"] == "/help"


def test_missing_image_alt_evidence_includes_src() -> None:

    issues = analyze_images('<img src="award.png">')

    evidence = issues[0].evidence
    assert evidence["src"] == "award.png"


def test_issue_evidence_includes_line_key_when_possible() -> None:

    html = '<form>\n<input type="text" name="student_name">\n</form>'
    issues = analyze_html_forms(html)

    evidence = issues[0].evidence
    assert "line" in evidence
    assert evidence["line"] in {2, None}


def test_static_analyzer_combines_checks() -> None:

    html = '<html><body><h1>Page</h1><button></button><img src="x.png"></body></html>'
    issues = analyze_html_static(html)

    assert {"missing_button_name", "missing_image_alt", "missing_page_title"}.issubset(
        issue_types_for(issues)
    )


def test_build_json_report_returns_expected_top_level_keys() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert set(report) == {
        "tool",
        "version",
        "report_schema_version",
        "extended_result_schema_version",
        "source_file",
            "summary",
            "issues",
            "issue_clusters",
            "wcag_coverage",
            "limitations",
        }


def test_build_json_report_has_correct_issue_count() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert report["summary"]["issues_found"] == 9
    assert len(report["issues"]) == 9


def test_json_report_includes_issue_counts() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    assert "counts_by_severity" in report["summary"]
    assert "counts_by_issue_type" in report["summary"]
    assert report["summary"]["counts_by_issue_type"]["missing_form_label"] == 2


def test_json_report_preserves_structured_evidence_fields() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    first_issue_evidence = report["issues"][0]["evidence"]

    assert "snippet" in first_issue_evidence
    assert "reason" in first_issue_evidence
    assert "line" in first_issue_evidence


def test_save_json_report_writes_valid_json(tmp_path: Path) -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.json"

    save_json_report(report, output_path)

    saved_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_report["tool"] == "A11yway"
    assert saved_report["summary"]["issues_found"] == 9


def test_sample_tasks_load_correctly() -> None:

    tasks = load_tasks("examples/sample_tasks.json")

    assert len(tasks) == 3
    assert tasks[0].student_profile == "Keyboard-only student"
    assert "missing_form_label" in tasks[0].relevant_issue_types


def test_find_task_by_id() -> None:

    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit_scholarship_application")

    assert task is not None
    assert task.name == "Submit scholarship application"


def test_find_task_by_name_case_insensitively() -> None:

    tasks = load_tasks("examples/sample_tasks.json")

    task = find_task(tasks, "submit scholarship APPLICATION")

    assert task is not None
    assert task.id == "submit_scholarship_application"


def test_filter_issues_for_task_returns_relevant_issue_types() -> None:

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

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert isinstance(markdown, str)


def test_markdown_report_includes_summary_and_issue_types() -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert "# A11yway Accessibility Report" in markdown
    assert "## Summary" in markdown
    assert "Issues found: 9" in markdown
    assert "missing_form_label" in markdown


def test_markdown_report_includes_task_context() -> None:

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

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)

    markdown = build_markdown_report(report)

    assert "```html" in markdown
    assert '<input type="text" name="student_name">' in markdown


def test_save_markdown_report_writes_file(tmp_path: Path) -> None:

    issues = analyze_html_file(Path("examples/sample_form.html"))
    report = build_json_report("examples/sample_form.html", issues)
    output_path = tmp_path / "reports" / "sample_form_report.md"

    save_markdown_report(report, output_path)

    markdown = output_path.read_text(encoding="utf-8")
    assert "# A11yway Accessibility Report" in markdown


def test_cli_default_sample_still_runs(capsys) -> None:

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Issues found: 9" in captured.out


def test_cli_task_mode_runs(capsys) -> None:

    exit_code = main(
        ["examples/sample_form.html", "--task", "submit_scholarship_application"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Task: Submit scholarship application" in captured.out
    assert "Likely blockers: 5" in captured.out


def test_cli_markdown_mode_writes_report(tmp_path: Path, capsys) -> None:

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

    items = load_batch_config("examples/sample_batch.json")

    assert len(items) == 2
    assert items[0]["id"] == "scholarship_form"
    assert items[1]["source"] == "examples/sample_resource_page.html"


def test_batch_runner_processes_sample_pages(tmp_path: Path) -> None:

    result = run_batch("examples/sample_batch.json", tmp_path / "batch_sample")

    assert result["index"]["summary"]["total_pages_tested"] == 2
    assert len(result["index"]["sources"]) == 2


def test_batch_runner_writes_per_page_reports(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    assert (out_dir / "scholarship_form.json").exists()
    assert (out_dir / "scholarship_form.md").exists()
    assert (out_dir / "learning_resources.json").exists()
    assert (out_dir / "learning_resources.md").exists()


def test_batch_index_json_contains_total_pages(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    index = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
    assert index["summary"]["total_pages_tested"] == 2
    assert index["summary"]["total_issues"] >= 2


def test_batch_index_markdown_includes_sources_and_total(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    result = run_batch("examples/sample_batch.json", out_dir)

    markdown = (out_dir / "index.md").read_text(encoding="utf-8")
    assert "Student Scholarship Application" in markdown
    assert "Learning Resources Page" in markdown
    assert f"- Total issues: {result['index']['summary']['total_issues']}" in markdown


def test_batch_run_creates_index_csv(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    assert (out_dir / "index.csv").exists()


def test_batch_csv_has_expected_headers(tmp_path: Path) -> None:

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
            "raw_occurrences",
            "unique_root_issues",
            "task_blockers",
            "browser_status",
            "browser_issue_count",
            "low_vision_status",
            "low_vision_issue_count",
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

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2


def test_batch_csv_includes_issue_counts(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["issues_found"] == "9"
    assert int(rows[0]["high_count"]) >= 1


def test_batch_csv_includes_report_paths(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    run_batch("examples/sample_batch.json", out_dir)

    with (out_dir / "index.csv").open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["json_report"].endswith("scholarship_form.json")
    assert rows[0]["markdown_report"].endswith("scholarship_form.md")


def test_batch_csv_override_path(tmp_path: Path) -> None:

    out_dir = tmp_path / "batch_sample"
    csv_path = tmp_path / "custom" / "benchmark.csv"
    result = run_batch("examples/sample_batch.json", out_dir, csv_path=csv_path)

    assert csv_path.exists()
    assert result["csv_index_path"] == csv_path.as_posix()


def test_batch_runner_continues_if_one_source_fails(tmp_path: Path) -> None:

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
