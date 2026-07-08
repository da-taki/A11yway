# A11yway

A11yway audits education web pages for accessibility barriers that block real student tasks — static HTML checks by default, with an optional headless-browser keyboard audit.

**Status: v0.2 prototype — open for evaluation.** Not production software, not a WCAG certification tool, and not a replacement for human accessibility review. Tests: 108 passing.

Instead of only scanning a page for technical rules, A11yway is built around student tasks: submitting a scholarship form, finding an assignment, accessing a video lesson. It reports which barriers likely block those tasks, with evidence a reviewer can verify.

## Quickstart: Static Mode

Static mode needs only Python 3.10+ — no external dependencies.

```bash
python -m a11yway.main examples/sample_form.html
```

Save reports, optionally in the context of a student task:

```bash
python -m a11yway.main examples/sample_form.html --task submit_scholarship_application --json reports/sample_form_report.json --markdown reports/sample_form_report.md
```

Audit a public page (fetches the static HTML; no JavaScript, no crawling):

```bash
python -m a11yway.main https://example.com --markdown reports/url_report.md
```

Explore the checks:

```bash
python -m a11yway.main --list-rules
python -m a11yway.main --rule missing_form_label
```

Static checks cover form labels, link/button names, image alt text, heading structure, page title/language, and basic media captions/transcripts. Every finding includes an evidence snippet, the reason, and an approximate line number.

## Quickstart: Browser Mode

Real education portals build forms and buttons with JavaScript. Browser mode loads the page in headless Chromium, presses Tab repeatedly to trace where keyboard focus actually goes, and re-runs the static checks on the rendered DOM. It begins to answer: can a keyboard-only student actually move through this page?

Install the optional dependency:

```bash
pip install -r requirements-browser.txt
python -m playwright install chromium
```

Then add `--browser` to any audit:

```bash
python -m a11yway.main examples/sample_dynamic_form.html --browser --markdown reports/dynamic_form_report.md
```

Tune with `--max-tabs N` (default 40) and `--wait-ms N` (default 500). [examples/sample_dynamic_form.html](examples/sample_dynamic_form.html) shows the difference: its JavaScript-added unlabeled field and unnamed button produce zero static findings but four browser findings. If Playwright is missing, `--browser` prints setup instructions and exits; every static command keeps working without it.

## Batch Evaluation

Audit multiple pages in one run:

```bash
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample
python -m a11yway.main --batch examples/sample_browser_batch.json --out-dir reports/browser_batch_sample --browser
```

Each batch writes per-page JSON/Markdown reports plus:

- `index.json` / `index.md` — batch summary and per-source stats
- `index.csv` — spreadsheet-friendly benchmark row per page
- `evaluation_summary.md` — reviewer-facing overview: top issue types, severity breakdown, high priority findings with evidence

Example generated output: [reports/batch_sample/evaluation_summary.md](reports/batch_sample/evaluation_summary.md) and [reports/dynamic_form_report.md](reports/dynamic_form_report.md) (from a real headless Chromium run).

To start your own review batch, copy [examples/evaluation_batch_template.json](examples/evaluation_batch_template.json), replace the placeholders with pages you have permission to review, and follow [docs/RUN_FIRST_EVALUATION_BATCH.md](docs/RUN_FIRST_EVALUATION_BATCH.md).

## Why Education Accessibility Testing Matters

Education sites carry forms, documents, videos, assignments, and deadlines. If any of those are inaccessible, students are blocked from learning or from completing required school tasks. Practical questions this project works toward answering:

- Can a keyboard-only student complete the task?
- Can a low-vision student read and use the page after zooming?
- Are instructions clear for a student with reading difficulty?
- Are captions or transcripts available for audio and video content?

## Limitations

- Static checks are heuristics on HTML source; URL mode does not execute JavaScript.
- Browser mode approximates keyboard interaction; accessible names are estimated and need manual review.
- No full screen-reader simulation.
- No crawling, no logins, no private or unauthorized testing — public pages or explicit permission only.
- Findings are hints for human reviewers. A11yway does not certify WCAG compliance and does not replace testing with disabled users.

## Documentation

- [docs/RULES.md](docs/RULES.md) — every check: what it detects, why it matters, what it cannot verify
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how a page flows through the tool
- [docs/ROADMAP.md](docs/ROADMAP.md) — what is planned, and what is deliberately not
- [docs/RUN_FIRST_EVALUATION_BATCH.md](docs/RUN_FIRST_EVALUATION_BATCH.md) — running a responsible NGO/school review batch
- [docs/outreach/EVALUATION_PROTOCOL.md](docs/outreach/EVALUATION_PROTOCOL.md) — evaluation protocol for reviewers
- [docs/outreach/REVIEWER_GUIDE.md](docs/outreach/REVIEWER_GUIDE.md) — guide for accessibility reviewers
- [CONTRIBUTING.md](CONTRIBUTING.md) — setup, tests, adding rules and sample pages
- [CHANGELOG.md](CHANGELOG.md) — milestone history

## Project Direction

In this project, an "agent" is a small simulated student profile with a specific accessibility need. Today the checks are deterministic heuristics plus a basic keyboard traversal; the direction is richer task simulation (see the roadmap). The code is intentionally small and readable for student developers.
