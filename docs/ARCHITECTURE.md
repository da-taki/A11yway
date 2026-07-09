# A11yway Architecture

A11yway is a small Python project. Static mode uses only the standard library; browser mode optionally uses Playwright. This document explains how a page and workflow templates flow through the tool.

## Data Flow

```
source file/url
  -> source_loader
  -> static analyzer
  -> optional browser runner
  -> optional low-vision browser checks
  -> optional visual proof collector
  -> optional task executor
  -> workflow packs
  -> optional future AI scout suggestions
  -> deterministic verification
  -> optional reviewer verdicts / re-audit diff
  -> report builder
  -> JSON / Markdown / HTML / CSV outputs
```

In practice, deterministic verification is the center of the system. Static checks, browser checks, and task execution can produce confirmed findings. Workflow packs help reviewers choose what to test. A future AI scout layer may propose likely workflows or risks, but reports should clearly separate suggested risks from confirmed findings.

Batch mode wraps the same flow in a loop over a JSON config and adds index and evaluation summary reports.

## Modules

### CLI Entry Point - `a11yway/main.py`

Parses arguments, decides between single-page, batch, rule-listing, and workflow-pack modes, and prints readable console summaries. `--browser` is guarded here: if Playwright is missing, the CLI prints setup instructions and exits instead of crashing.

### Source Loading - `a11yway/core/source_loader.py`

Reads a local HTML file or fetches a public `http(s)` URL with the standard library. Returns the HTML plus metadata (source type, final URL, status code, content type) and an error field instead of raising, so batch runs can continue past one bad source.

### Static Analyzer - `a11yway/core/page_analyzer.py`

A small `html.parser`-based analyzer that runs heuristic checks on the raw HTML: form labels, link/button names, image alt text, heading structure, page title/language, and media captions/transcripts. Each finding carries structured evidence: a tag snippet, the reason, and an approximate line number.

### Indic-Language Checks - `a11yway/core/indic_checks.py`

A static rule pack that runs inside every static analysis. It walks the HTML with a lang-tracking parser, detects Indic scripts through Unicode ranges, and flags Indic text with missing or contradicting lang markup plus mixed Latin/Indic text nodes. Script detection is a heuristic and cannot see transliterated text.

### Browser Runner - `a11yway/core/browser_runner.py` (Optional)

Only used with `--browser`. Loads the page in headless Chromium via Playwright, presses Tab repeatedly to build a keyboard focus trace, then re-runs the static checks on the JavaScript-rendered DOM (`detected_in: "browser_dom"`). Each focus stop is also resolved against Chromium's computed accessibility tree (see the announce module below); when tree data is unavailable, accessible names fall back to estimates. The focus trace is analyzed for keyboard traps (a subset of elements cycling at least twice without passing through the body while other focusable elements stay unreached) and for lost focus (repeated body landings). Playwright is imported optionally so this module is always safe to import. `merge_browser_issues` combines static and browser findings without duplicating DOM re-checks that match static findings.

### Announce Transcript - `a11yway/core/announce.py` (Optional)

Used by browser mode and task execution. Opens a Chrome DevTools Protocol session and, for each focused element, resolves the specific node (activeElement to backendNodeId to partial AX tree) to read the computed role, accessible name, and states (disabled, required, invalid, checked, expanded). Reports render this as a numbered announce transcript, and focus stops with an empty computed name become `unnamed_focus_stop` findings. Every capture degrades to "announcement unavailable" on failure. This is one Chromium run's computed tree, not a screen reader simulation.

### Visual Proof - `a11yway/core/visual_proof.py` (Optional)

Only used when browser mode is active and visual proof is requested. The browser runner saves a full-page Playwright screenshot, records observed focus trace bounding boxes when available, and generates a focus-path HTML overlay with numbered Tab stops.

Visual proof is an evidence aid, not accessibility certification. The overlay shows one observed browser focus path and does not represent every assistive technology experience.

### Low-Vision Audit - `a11yway/core/low_vision_audit.py` (Optional)

Only used with `--browser --low-vision`. Samples browser-computed styles for rendered contrast, runs zoom reflow passes at 200% and 400% (laid out at the equivalent CSS widths browser zoom produces, including the WCAG 1.4.10 reference of 320 px) detecting horizontal scrolling, clipped content, and overlapping controls, and checks focused elements for obvious focus indicators. These checks are conservative and require manual review.

### Task Runner - `a11yway/core/task_runner.py`

Loads task scenarios, filters findings down to the issue types relevant to a task, and turns them into "likely blocker" notes with task impact text.

### Task Executor - `a11yway/core/task_executor.py` (Optional)

Only used with `--browser --execute-task` or batch `--execute-tasks`. Attempts explicit `browser_steps` from a task definition using keyboard-style browser actions: Tab traversal, typed text, option selection, Enter activation, and visible-text assertions. It returns a pass, blocked, failed, or unavailable result with per-step evidence; a step whose control sits beyond a confirmed focus loop blocks with reason `keyboard_trap` and the looping elements identified. It is deterministic browser automation, not AI, and it only tests the scripted workflow path.

### Workflow Packs - `a11yway/core/workflow_packs.py` and `a11yway/workflow_packs/`

Loads deterministic JSON workflow templates for education, college applications, NGO services, government services, AI products, scholarships, and public resources. These packs help reviewers choose task scenarios and relevant issue types. They do not execute anything by themselves and they are not prompts.

### Future AI Scout Layer (Optional)

Future AI scout mode may propose likely workflows and accessibility risks. It should never mark a finding as confirmed by itself. Deterministic static, browser, or task checks must verify a finding before reports call it confirmed.

### Reviewer Verdicts - `a11yway/core/verdicts.py`

Applies human reviewer verdicts to existing JSON reports and summarizes feedback. Verdicts can mark findings as confirmed, false positive, needs review, fixed, or missed issue. Organization names and quotes should only be used when permission fields allow it.

### Re-Audit Diff - `a11yway/core/report_diff.py`

Compares two JSON reports by deterministic issue fingerprints and task execution status. The diff reports fixed, remaining, new, and changed-severity issues, plus blocked-to-completed task execution changes for impact tracking.

### Rule Registry - `a11yway/core/rules.py`

One central dictionary documenting every issue type: title, category, default severity, why it matters, how to fix it, manual review notes, and what the check cannot verify. Reports and the `--list-rules` / `--rule` CLI commands read from here. `docs/RULES.md` is the human-readable version.

### Report Builder - `a11yway/core/report_builder.py`

Builds the JSON report shape, enriches each issue with rule metadata, renders Markdown reports (including the browser interaction trace when present), and produces the batch index in JSON, Markdown, and CSV plus the reviewer-facing `evaluation_summary.md`.

Reports should distinguish:

- Suggested risks from workflow packs or future AI scout mode
- Deterministic findings from static/browser/task execution
- Reviewer-confirmed findings from human review

### CI Output - `a11yway/core/ci_output.py`

Used with `--ci`, `--sarif`, and `--junit`. Maps audit outcomes onto exit codes (0 clean, 1 findings at or above the `--fail-severity` threshold, 2 blocked task with `--fail-on-blocked`, 3 tool or setup error), renders findings as SARIF 2.1.0 for inline GitHub annotations, and renders task execution steps as JUnit XML test cases. Standard library only; a batch run is handled as a list of reports.

### Batch Runner - `a11yway/core/batch_runner.py`

Loads a batch config (a JSON list of sources with optional tasks), runs the audit for each item, keeps going when one item fails, and writes all per-page and index artifacts to the output directory.

### Agents - `a11yway/agents/`

Simulated user profiles (keyboard-only, low-vision, dyslexia, hearing). These are early scaffolding for future task simulation; today the keyboard profile delegates to the static analyzer.

## Report Artifacts

Single-page mode writes what you ask for:

- `--json path.json` - structured report with summary, issues, rule metadata, evidence, optional task context, optional browser block
- `--markdown path.md` - the same report rendered for human reviewers
- `--html path.html` - a self-contained reviewer-friendly HTML report

Batch mode writes into the output directory:

- `<item_id>.json` / `<item_id>.md` - per-page reports
- `<item_id>.html` - optional per-page HTML report when `--html-reports` is used
- `index.json` - machine-readable batch summary and per-source stats
- `index.md` - human-readable batch index
- `index.csv` - spreadsheet-friendly benchmark row per source
- `evaluation_summary.md` - reviewer-facing overview: top issue types, severity breakdown, high priority findings, recommended review process

When task execution is enabled, per-page reports include a `task_execution` block. Batch index reports, the CSV index, and the evaluation summary include task execution status and step counts.

When visual proof is enabled, reports include `visual_proof` metadata with screenshot and focus overlay paths. Image bytes are not embedded in JSON.

When low-vision checks are enabled, reports include a `low_vision` block with contrast sample counts, zoom/reflow data, focus visibility summary, and limitations.

Verdict and re-audit outputs are separate JSON/Markdown artifacts so original audit reports are preserved unless the reviewer explicitly applies verdicts.

## Limitations

- Static checks are heuristics on HTML source; they cannot judge visual design, alt-text quality, or anything rendered only by JavaScript.
- Browser mode reads roles, names, and states from Chromium's computed accessibility tree when available and falls back to estimates otherwise; either way it reflects one browser engine, not a real screen reader.
- There is no full screen-reader simulation.
- There is no crawling and no authenticated portal testing; audits run on exactly the public page you provide, or a page you have permission to test.
- Results are hints for human reviewers, not WCAG conformance claims.
