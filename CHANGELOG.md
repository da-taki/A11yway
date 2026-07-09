# Changelog

A11yway is a prototype. Versions below are development milestones, not
production releases.

## Unreleased - Accessibility-tree announce transcript

- Browser mode now resolves every observed focus stop against Chromium's
  computed accessibility tree (over the Chrome DevTools Protocol) and
  records the computed role, accessible name, and states (disabled,
  required, invalid, checked, expanded).
- Reports gain a numbered announce transcript, for example
  `3. button, (no accessible name)` or `7. textbox, "Full name", required`,
  in Markdown, JSON, and HTML reports, in per-step task execution tables
  (Announced column), and in the visual proof overlay legend and marker
  hover text.
- Added the `unnamed_focus_stop` rule (severity high): a focus stop whose
  computed accessible name is empty. When tree data is available it
  supersedes the heuristic `browser_focused_control_missing_name` check
  for the same element; the heuristic remains as a fallback.
- Added paired samples `examples/sample_announce_transcript.html` and
  `examples/sample_announce_transcript_broken.html`, plus a test suite
  (`tests/test_announce_transcript.py`) with real-browser integration
  tests that skip when Playwright is unavailable.
- Announce capture degrades gracefully: any CDP failure yields
  "announcement unavailable" instead of a crash or invented finding, and
  static mode is untouched. Documented that the transcript is one Chromium
  run's computed tree, not a real screen reader (NVDA, JAWS, and VoiceOver
  can differ).

## Unreleased - Malformed-HTML hardening and optional axe-core scan

- Hardened the static HTML parser against real-world tag soup: an end tag
  now also closes unclosed children (an unclosed `<label>` or `<a>` can no
  longer wrap the rest of the document and hide findings), non-nestable
  tags like `a`, `button`, `label`, `p`, and `li` implicitly close a
  previous unclosed instance the way browsers repair them, script/style
  text no longer counts as visible content or accessible names, an
  unclosed `<title>` still counts as a page title, and parser failures
  degrade to partial results instead of crashing an audit.
- Added a malformed-HTML regression test suite
  (`tests/test_malformed_html.py`).
- Added an optional axe-core rule scan to browser mode with `--axe`, in
  single audits and batch mode. Axe findings map onto A11yway severities,
  carry element snippets and Deque University help links, and reports gain
  an "Axe-core Scan" summary section.
- axe-core is bundled through the optional `axe-playwright-python` package
  in `requirements-browser.txt`; no network access is needed at audit time
  and every static or browser command keeps working without it.

## Unreleased - Low-vision checks, reviewer verdicts, and re-audit diff tracking

- Added optional browser-based low-vision checks with `--browser --low-vision`
  for rendered contrast samples, reflow approximation, and focus visibility.
- Added low-vision issue types and rule documentation:
  `low_contrast_text`, `zoom_horizontal_overflow`,
  `zoom_fixed_width_content`, and `focus_indicator_missing`.
- Added reviewer verdict ingestion with `--apply-verdicts` and
  `--summarize-verdicts`.
- Added re-audit diff tracking with `--compare-reports`.
- Added sample low-vision page/batch, sample verdicts, and generated
  low-vision/verdict/diff reports.
- Kept browser mode optional and avoided AI, OCR, PDF, crawling, security
  testing, and heavy visual dependencies.

## Unreleased - Visual proof reports

- Added self-contained HTML report export with `--html`.
- Added browser screenshot and observed focus-path overlay generation with
  `--visual-proof`.
- Added visual proof metadata to JSON and Markdown/HTML reports.
- Added batch HTML report support with `--html-reports`, including
  `html_report` paths in batch index and CSV output.
- Kept visual proof browser-optional and deterministic; no AI, OCR, PDF,
  crawling, security testing, or image-processing dependencies were added.

## Unreleased - Workflow packs and AI scout configuration

- Added `.env.example` for future optional AI scout configuration with
  Groq placeholders and responsible-use defaults.
- Added deterministic workflow pack JSON templates for education, college
  applications, NGO services, government services, AI products,
  scholarships, and public resources.
- Added workflow pack CLI commands: `--list-packs`, `--show-pack`, and
  `--suggest-tasks`.
- Expanded the public-interest accessibility stress-testing vision in the
  README, roadmap, and architecture docs.
- Added `docs/AI_SCOUT_DESIGN.md` describing optional future scout mode,
  provider options, safety boundaries, and suggested-vs-confirmed output.
- No actual AI calls, SDKs, external dependencies, crawling, or API key
  requirements were added.

## v0.3-deterministic-task-execution

- Deterministic browser task execution (`--browser --execute-task`) for
  tasks that define explicit `browser_steps`.
- Keyboard-style task steps for visible-text checks, Tab-based focus,
  text entry, select option changes, Enter activation, and confirmation
  text.
- Pass, blocked, failed, or unavailable task execution results with
  per-step evidence in JSON and Markdown reports.
- Batch task execution support (`--execute-tasks`) with status and step
  counts in batch index, CSV, and evaluation summary outputs.
- Three task execution rules: `task_step_blocked`,
  `task_control_not_keyboard_reachable`, and
  `task_expected_content_missing`.
- Added accessible and intentionally broken scholarship form samples for
  browser task execution checks.
- Added tests for task schema loading, graceful browser-unavailable paths,
  report output, rule registry coverage, and browser integration when
  Playwright is available.

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
