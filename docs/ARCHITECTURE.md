# A11yway Architecture

A11yway is a small Python project. Static mode uses only the standard
library; browser mode optionally uses Playwright. This document explains
how a page flows through the tool.

## Data Flow

```
source file/url
  -> source_loader        (read local file or fetch public URL)
  -> static analyzer      (heuristic checks on the HTML source)
  -> optional browser runner
       - keyboard focus traversal (Tab key trace)
       - rendered DOM re-check (static checks on page.content())
  -> task mapping         (which findings block a student task)
  -> report builder       (rule enrichment, summaries)
  -> JSON / Markdown / CSV outputs
```

Batch mode wraps this flow in a loop over a JSON config and adds index and
evaluation summary reports.

## Modules

### CLI entry point — `a11yway/main.py`

Parses arguments, decides between single-page, batch, and rule-listing
modes, and prints readable console summaries. `--browser` is guarded here:
if Playwright is missing, the CLI prints setup instructions and exits
instead of crashing.

### Source loading — `a11yway/core/source_loader.py`

Reads a local HTML file or fetches a public `http(s)` URL with the standard
library. Returns the HTML plus metadata (source type, final URL, status
code, content type) and an error field instead of raising, so batch runs
can continue past one bad source.

### Static analyzer — `a11yway/core/page_analyzer.py`

A small `html.parser`-based analyzer that runs heuristic checks on the raw
HTML: form labels, link/button names, image alt text, heading structure,
page title/language, and media captions/transcripts. Each finding carries
structured evidence: a tag snippet, the reason, and an approximate line
number.

### Browser runner — `a11yway/core/browser_runner.py` (optional)

Only used with `--browser`. Loads the page in headless Chromium via
Playwright, presses Tab repeatedly to build a keyboard focus trace with
estimated accessible names, then re-runs the static checks on the
JavaScript-rendered DOM (`detected_in: "browser_dom"`). Playwright is
imported optionally so this module is always safe to import.
`merge_browser_issues` combines static and browser findings without
duplicating DOM re-checks that match static findings.

### Task runner — `a11yway/core/task_runner.py`

Loads education task scenarios (for example, submitting a scholarship
application), filters findings down to the issue types relevant to a task,
and turns them into "likely blocker" notes with task impact text.

### Rule registry — `a11yway/core/rules.py`

One central dictionary documenting every issue type: title, category,
default severity, why it matters, how to fix it, manual review notes, and
what the check cannot verify. Reports and the `--list-rules` / `--rule`
CLI commands read from here. `docs/RULES.md` is the human-readable version.

### Report builder — `a11yway/core/report_builder.py`

Builds the JSON report shape, enriches each issue with rule metadata,
renders Markdown reports (including the browser interaction trace when
present), and produces the batch index in JSON, Markdown, and CSV plus the
reviewer-facing `evaluation_summary.md`.

### Batch runner — `a11yway/core/batch_runner.py`

Loads a batch config (a JSON list of sources with optional tasks), runs
the audit for each item, keeps going when one item fails, and writes all
per-page and index artifacts to the output directory.

### Agents — `a11yway/agents/`

Simulated student profiles (keyboard-only, low-vision, dyslexia, hearing).
These are early scaffolding for future task simulation; today the keyboard
profile delegates to the static analyzer.

## Report Artifacts

Single-page mode writes what you ask for:

- `--json path.json` — structured report with summary, issues, rule
  metadata, evidence, optional task context, optional browser block
- `--markdown path.md` — the same report rendered for human reviewers

Batch mode writes into the output directory:

- `<item_id>.json` / `<item_id>.md` — per-page reports
- `index.json` — machine-readable batch summary and per-source stats
- `index.md` — human-readable batch index
- `index.csv` — spreadsheet-friendly benchmark row per source
- `evaluation_summary.md` — reviewer-facing overview: top issue types,
  severity breakdown, high priority findings, recommended review process

## Limitations

- Static checks are heuristics on HTML source; they cannot judge visual
  design, alt-text quality, or anything rendered only by JavaScript.
- Browser mode estimates accessible names from labels, text, and common
  attributes; it does not compute the real accessibility tree.
- There is no full screen-reader simulation.
- There is no crawling and no authenticated portal testing; audits run on
  exactly the public page you provide (or a page you have permission to
  test).
- Results are hints for human reviewers, not WCAG conformance claims.
