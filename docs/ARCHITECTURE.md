# Architecture

A11yway is a Python package with a CLI, a Flask web interface, and small rule modules.

## Flow

1. Load one source URL, one local file, or a batch item.
2. Run selected static, browser, workflow, low-vision, media, document, language, component, or passive-security checks.
3. Normalize findings through the rule registry.
4. Merge repeated findings into root issues where possible.
5. Write reports and evidence for human review.

## Main areas

- `a11yway/main.py`: CLI parsing and run orchestration.
- `a11yway/core/source_loader.py`: safe source loading for static audits.
- `a11yway/core/browser_runner.py`: rendered-page and keyboard evidence.
- `a11yway/core/report_builder.py`: JSON, Markdown, HTML, CSV, SARIF, and JUnit output.
- `a11yway/core/rules.py`: issue metadata used by CLI and reports.
- `a11yway/core/wcag_coverage.py`: generated WCAG coverage output.
- `a11yway/web_app.py`: Flask routes for the web interface.

Optional integrations are imported lazily. A missing optional parser or browser should produce an unavailable status, not break static mode.
