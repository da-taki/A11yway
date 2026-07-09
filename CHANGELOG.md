# Changelog

A11yway is a prototype. Versions below are development milestones, not
production releases.

## Unreleased - Video proof

- Added `--video` (off by default): when `--visual-proof` and
  `--execute-task` run together, the browser session is also recorded
  with Playwright's video recording and saved as `task_execution.webm`
  alongside the visual proof assets.
- The HTML report links the video with a caption stating what run it
  shows; JSON and Markdown reports carry the path and caption too, and a
  failed recording is reported honestly instead of hidden.
- Recording is viewport-sized (1280x720) to keep files small, never
  breaks the task run, and degrades with setup instructions when
  Playwright is missing.
- Added `tests/test_video_proof.py` with real-browser integration tests
  for the recording and the HTML link.
- Documented that the video shows one Chromium run and is an evidence
  aid for human reviewers.

## Unreleased - Indic-language checks

- Added a static rule pack (standard library only, no browser) for
  Indian-language content, detecting Indic scripts via Unicode ranges:
  Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu,
  Kannada, and Malayalam.
- New finding types: `missing_lang_indic` (Indic text under a missing or
  non-matching effective lang), `lang_mismatch` (an element's own lang
  attribute contradicts its dominant script), and `mixed_script_element`
  (one text node mixing several Latin words with Indic text and no lang
  boundary; numbers, short acronyms, and single loanwords are ignored to
  limit false positives).
- The checks run as part of every static analysis, so browser DOM
  re-checks get them too.
- Added paired samples `examples/sample_indic_page.html` (seeded errors
  in Devanagari, Gurmukhi, and mixed text) and
  `examples/sample_indic_page_clean.html`, plus
  `tests/test_indic_checks.py`.
- Documented that script detection is a heuristic and that
  transliterated text (Hindi written in Latin script) cannot be
  detected.

## Unreleased - Real zoom reflow checks

- Replaced the narrow-viewport reflow approximation in `--low-vision`
  with zoom passes at 200% and 400%, laid out at the equivalent CSS
  widths browser zoom produces (1280 base: 640 px and the WCAG 1.4.10
  reference of 320 px).
- Added three reflow finding types with computed evidence (element,
  bounding boxes, zoom level): `reflow_horizontal_scroll` (high when the
  400% reference overflows), `reflow_clipped_content` (text or controls
  beyond every reachable area), and `reflow_overlap` (interactive
  elements colliding under zoom).
- Reports gain a per-level "Zoom Reflow Levels" table; the legacy
  zoom_reflow keys now mirror the 400% pass so older consumers keep
  working. The `zoom_horizontal_overflow` and `zoom_fixed_width_content`
  rules stay registered for reports from older versions but are no
  longer emitted.
- Added paired samples `examples/sample_zoom_reflow.html` (seeded
  horizontal scroll, clipped note, colliding buttons) and
  `examples/sample_zoom_reflow_fixed.html`, plus
  `tests/test_zoom_reflow.py` with real-browser integration tests.
- Documented that gradients, images, and intentional horizontal-scroll
  regions (allowed by WCAG 1.4.10) need manual review.

## Unreleased - CI mode

- Added `--ci` for pipeline use with meaningful exit codes: 0 clean,
  1 findings at or above the threshold, 2 task blocked (with
  `--fail-on-blocked`), 3 tool or setup error. Works in static, browser,
  task execution, and batch modes.
- Added `--fail-severity {high,medium,low}` (default high) to control the
  failure threshold and `--fail-on-blocked` to give blocked tasks their
  own exit code.
- Added SARIF 2.1.0 export with `--sarif PATH`: severities map to SARIF
  levels (high=error, medium=warning, low=note), rules carry descriptions
  and fix help, and results carry file/line locations where available.
- Added JUnit XML export with `--junit PATH`: each task execution step is
  a test case, a blocked step is a failure with the evidence as its
  message, and an execution that could not run is an error case.
- Added a copy-me GitHub Actions workflow
  (`.github/workflows/a11yway-example.yml`, workflow_dispatch only)
  demonstrating a keyboard task regression gate.
- Added `tests/test_ci_mode.py` with a structural SARIF validation and
  integration tests for blocked (exit 2) and completed (exit 0) runs.
- All CI outputs use only the standard library; no new dependencies.

## Unreleased - Keyboard trap and focus-loop detection

- Browser mode now detects keyboard traps from the observed focus trace:
  a `keyboard_trap` finding (severity high) fires when Tab cycles through
  the same subset of elements at least twice without passing through the
  document body while other focusable elements are never reached, with
  the looping element sequence and unreached-element count as evidence.
- Added a `focus_lost` finding for focus that lands on the document body
  repeatedly and never returns to page content.
- Task execution now reports `BLOCKED at step <id> (reason: keyboard_trap)`
  and identifies the looping elements when a step's control sits beyond a
  focus loop; the blocked reason appears in JSON, Markdown, and HTML
  reports.
- The focusable-element estimate now counts only visible elements and
  counts each radio group once, reducing false trap positives.
- Added paired samples `examples/sample_keyboard_trap.html` (a feedback
  dialog that swallows Tab) and `examples/sample_keyboard_trap_fixed.html`,
  plus `tests/test_keyboard_trap.py` with real-browser integration tests.
- Documented both rules as related to WCAG 2.1.2 No Keyboard Trap, with
  the caveat that detection observes Tab behavior in one Chromium run and
  cannot verify custom escape mechanisms.

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
