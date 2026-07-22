# Report Schema

A11yway JSON reports are reviewer evidence, not compliance certificates.

## Top-level fields

- `version`: A11yway package version.
- `report_schema_version`: JSON report shape version.
- `source`: audited source path or URL.
- `final_url`: final URL when URL loading or redirects apply.
- `issues`: normalized findings.
- `summary`: counts and run metadata.
- `wcag_coverage`: WCAG evidence snapshot when available.
- `visual_proof`: screenshot, focus overlay, or video paths when requested.
- `browser`: rendered-page and keyboard evidence when browser mode runs.
- `task_execution`: task step results when task execution runs.
- `passive_security`: separate passive-security observations when requested.

## Finding fields

Findings can include `issue_type`, `severity`, `message`, `selector`, `snippet`, `wcag`, `confidence`, `suggested_fix`, `affected_url`, and module-specific evidence.

## Outputs

JSON is the source report. Markdown and HTML are human-readable views. CSV is for triage. SARIF and JUnit are for CI integrations.

Treat `needs_review` and heuristic findings as review prompts. Confirm behavior before making legal, procurement, or compliance claims.
