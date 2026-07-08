# Changelog

A11yway is a prototype. Versions below are development milestones, not
production releases.

## v0.2-browser-audit

- Optional browser interaction mode (`--browser`) using Playwright and
  headless Chromium; static mode still needs no external dependencies.
- Keyboard focus traversal: repeated Tab presses build a focus trace with
  estimated accessible names for each stop.
- Rendered DOM re-checks: the static checks run again on the
  JavaScript-rendered page, catching controls that scripts add after load.
- Five new keyboard interaction rules: `browser_no_focusable_elements`,
  `browser_focus_not_moving`, `browser_repeated_focus`,
  `browser_focused_control_missing_name`, `browser_focus_on_hidden_element`.
- Browser data integrated into JSON and Markdown reports (analysis modes,
  browser summary, interaction trace) and into batch index/CSV columns.
- Graceful degradation: `--browser` without Playwright prints setup
  instructions instead of a traceback; a browser failure on one batch item
  does not stop the batch.
- New sample dynamic form (`examples/sample_dynamic_form.html`) whose
  JavaScript-added unlabeled controls are invisible to static source
  analysis but caught in browser mode, plus browser sample reports
  generated from real headless Chromium runs.

## v0.1-static-evaluation

- Static HTML accessibility checks for local files and public URLs:
  form labels, link/button names, image alt text, heading structure,
  page title and language, and basic media captions/transcripts.
- Task-based education scenarios that map findings to likely blockers
  for workflows like submitting a scholarship application.
- JSON and Markdown report export with evidence snippets, reasons, and
  approximate line numbers.
- Batch evaluation mode with per-page reports plus JSON, Markdown, and
  CSV index files and a reviewer-friendly `evaluation_summary.md`.
- Rule registry documenting every check (`--list-rules`, `--rule <type>`,
  `docs/RULES.md`).
- Evaluation templates and outreach documents for NGO/school reviews.

## Initial scaffold

- Project skeleton with simulated student agent profiles, task loading,
  and placeholder report building, written to be readable for a student
  developer.
