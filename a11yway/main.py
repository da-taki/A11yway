"""Command-line entry point for the A11yway prototype."""

import sys
from pathlib import Path

from a11yway.core.fix_suggester import FixSuggester
from a11yway.core.page_analyzer import analyze_html_forms
from a11yway.models.issue import AccessibilityIssue


DEFAULT_HTML_PATH = Path("examples/sample_form.html")


def analyze_html_file(path: Path) -> list[AccessibilityIssue]:
    """Read an HTML file and return basic form label issues."""
    html = path.read_text(encoding="utf-8")
    issues = analyze_html_forms(html)
    fix_suggester = FixSuggester()

    for issue in issues:
        if not issue.suggested_fix:
            issue.suggested_fix = fix_suggester.suggest_fix(issue.issue_type)

    return issues


def print_summary(path: Path, issues: list[AccessibilityIssue]) -> None:
    """Print a readable command-line summary."""
    print("A11yway HTML form label analysis")
    print(f"File analyzed: {path}")
    print(f"Issues found: {len(issues)}")

    for index, issue in enumerate(issues, start=1):
        print()
        print(f"{index}. {issue.title}")
        print(f"   Severity: {issue.severity}")
        print(f"   Type: {issue.issue_type}")
        print(f"   Message: {issue.title}")
        print(f"   Evidence: {issue.evidence}")
        if issue.suggested_fix:
            print(f"   Suggested fix: {issue.suggested_fix}")


def main(argv: list[str] | None = None) -> int:
    """Analyze a sample or provided HTML file from the command line."""
    args = argv if argv is not None else sys.argv[1:]
    html_path = Path(args[0]) if args else DEFAULT_HTML_PATH

    if not html_path.exists():
        print(f"HTML file not found: {html_path}", file=sys.stderr)
        return 1

    issues = analyze_html_file(html_path)
    print_summary(html_path, issues)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
