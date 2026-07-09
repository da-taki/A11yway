# A11yway

A11yway audits essential web workflows for accessibility barriers that block real tasks. It began with education pages and now supports a broader public-interest accessibility stress-testing direction, with static HTML checks by default, an optional headless-browser keyboard audit, and deterministic task execution that proves whether a keyboard-only user can finish a declared workflow.

**Status: prototype, open for evaluation.** Not production software, not a WCAG certification tool, and not a replacement for human accessibility review.

Instead of only scanning a page for technical rules, A11yway is built around tasks: submitting a scholarship form, finding an assignment, accessing a video lesson, locating public services, or using a public AI product interface. It reports which barriers likely block those tasks, with evidence a reviewer can verify.

## Responsible Accessibility Stress Testing

A11yway is expanding from education workflow testing into public-interest accessibility stress testing for essential digital workflows. The goal is to help reviewers test whether people can complete important public tasks, then report where access breaks with deterministic evidence.

Example workflow areas include:

- College applications
- NGO services
- Government information and service pages
- AI/LLM product interfaces
- Scholarships
- Public resources

A11yway does not do security testing, exploit testing, private data access, scraping behind login, or unauthorized testing. Use it only on public pages or pages where permission was granted.

## Quickstart: Static Mode

Static mode needs only Python 3.10+ and no external dependencies.

```bash
python -m a11yway.main examples/sample_form.html
```

Save reports, optionally in the context of a task:

```bash
python -m a11yway.main examples/sample_form.html --task submit_scholarship_application --json reports/sample_form_report.json --markdown reports/sample_form_report.md
```

Audit a public page by fetching the static HTML. URL mode does not execute JavaScript and does not crawl.

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

Real sites often build forms and buttons with JavaScript. Browser mode loads the page in headless Chromium, presses Tab repeatedly to trace where keyboard focus actually goes, and re-runs the static checks on the rendered DOM.

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

## Optional axe-core Scan

Browser mode can also run Deque's [axe-core](https://github.com/dequelabs/axe-core) rule set against the rendered page with `--axe`, in single audits and batch mode:

```bash
python -m a11yway.main examples/sample_form.html --browser --axe --markdown reports/axe_report.md
```

Axe findings appear alongside A11yway's own checks with issue types like `axe_label`, severities mapped from axe impacts (critical/serious become high, moderate becomes medium, minor becomes low), the affected element snippet, and a Deque University help link. Reports gain an "Axe-core Scan" section with a per-rule summary. A11yway's focus stays deterministic keyboard task evidence; the axe scan complements it with a mature, community-vetted rule set that covers far more technical rules than the built-in static checks.

The scan uses the axe-core copy bundled with the optional `axe-playwright-python` package (installed by `requirements-browser.txt`), so no network access is needed at audit time. If the package is missing, `--axe` prints setup instructions and exits; every static and browser command keeps working without it.

## Announce Transcript

In browser mode, A11yway asks Chromium's computed accessibility tree what a screen reader would be told at every observed Tab stop and at every task execution step: the computed role, the computed accessible name, and relevant states (disabled, required, invalid, checked, expanded). Reports render this as a numbered announce transcript, for example `3. button, (no accessible name)` or `7. textbox, "Full name", required`.

```bash
python -m a11yway.main examples/sample_announce_transcript_broken.html --browser --markdown reports/announce_transcript_broken_report.md
```

Focus stops whose computed accessible name is empty become `unnamed_focus_stop` findings with severity high, because a screen reader user hears at most a bare role at that stop. The paired samples show the difference: [examples/sample_announce_transcript.html](examples/sample_announce_transcript.html) announces a usable name at every stop, while [examples/sample_announce_transcript_broken.html](examples/sample_announce_transcript_broken.html) has three focus stops that announce nothing. The transcript appears in Markdown, JSON, and HTML reports, in the per-step task execution tables, and in the visual proof overlay (marker hover text and legend). No extra flag is needed: any `--browser` audit collects it.

Announce transcript limitations:

- The transcript is Chromium's computed accessibility tree, not a real screen reader. NVDA, JAWS, and VoiceOver apply their own rules and can announce things differently.
- It reflects one run in one browser engine.
- When accessibility tree data cannot be captured, transcript entries say "announcement unavailable" and A11yway falls back to its older estimated-name heuristic instead of guessing.

## Deterministic Task Execution

Normal task mode maps static issues to likely blockers for a workflow. Deterministic task execution goes one step further: with `--execute-task`, A11yway attempts a task's scripted steps in the browser using **keyboard-only interaction**. Focus moves with Tab, text is typed, controls are activated with Enter, and the report states whether the task passed, failed, or was blocked.

```bash
python -m a11yway.main examples/sample_task_execution_form.html --browser --execute-task submit_scholarship_application --json reports/task_execution_report.json --markdown reports/task_execution_report.md
```

The report states either `COMPLETED with keyboard-only interaction` or `BLOCKED at step <id>`, with a per-step table of evidence. The two sample forms show why this matters: [sample_task_execution_form.html](examples/sample_task_execution_form.html) completes all 11 steps, while [sample_task_execution_form_broken.html](examples/sample_task_execution_form_broken.html) passes every static check yet gets blocked at submit because its submit control is a click-only div a keyboard user can never reach.

Batch execution works too:

```bash
python -m a11yway.main --batch examples/sample_task_execution_batch.json --out-dir reports/task_execution_batch --browser --execute-tasks
```

Steps are deterministic scripts defined per task in [examples/sample_tasks.json](examples/sample_tasks.json) (`browser_steps`); see [docs/RULES.md](docs/RULES.md) for the supported actions. This is the key difference from normal rule scanners: A11yway can report that a defined workflow did or did not complete under browser conditions.

Task execution limitations:

- It only covers steps declared in the task file.
- It is not a full screen-reader simulation.
- It does not replace disabled-user testing.
- Browser mode requires Playwright and Chromium.
- Use it only on public pages or pages you have permission to test.

## Workflow Packs

Workflow packs are deterministic task templates that help reviewers decide what to test on a page. They are not AI prompts, they do not automatically prove accessibility, and they do not replace deterministic verification.

```bash
python -m a11yway.main --list-packs
python -m a11yway.main --show-pack ngo_services
python -m a11yway.main --suggest-tasks ai_products
```

You can also provide a source while asking for suggestions:

```bash
python -m a11yway.main https://example.org --suggest-tasks ngo_services
```

This still only prints workflow templates. To confirm findings, add page-specific `browser_steps` and use deterministic static, browser, or task execution modes.

## Visual Proof Reports

Visual proof uses Playwright screenshots plus an HTML/CSS focus overlay to show the observed keyboard Tab order. This is useful for non-technical reviewers because a numbered focus path or blocked control is often easier to understand than a raw HTML snippet.

Visual proof depends on browser mode. It is an evidence aid for manual review, not a full screen-reader simulation, not WCAG certification, and not a replacement for human accessibility testing.

```bash
python -m a11yway.main examples/sample_task_execution_form.html --browser --execute-task submit_scholarship_application --visual-proof reports/visual_task_execution --html reports/task_execution_report.html

python -m a11yway.main examples/sample_task_execution_form_broken.html --browser --execute-task submit_scholarship_application --visual-proof reports/visual_task_execution_broken --html reports/task_execution_broken_report.html
```

Batch HTML reports and per-page visual proof assets:

```bash
python -m a11yway.main --batch examples/sample_task_execution_batch.json --out-dir reports/task_execution_batch --browser --execute-tasks --html-reports
```

The focus overlay shows observed Tab stops from a single browser run. It does not represent every assistive technology experience.

## Low-Vision Checks

Low-vision checks run in browser mode and use computed styles to review rendered color contrast, a narrow-viewport reflow approximation, and visible keyboard focus indicators.

```bash
python -m a11yway.main examples/sample_low_vision_page.html --browser --low-vision --json reports/low_vision_report.json --markdown reports/low_vision_report.md --html reports/low_vision_report.html

python -m a11yway.main --batch examples/sample_low_vision_batch.json --out-dir reports/low_vision_batch --browser --low-vision --html-reports
```

These checks are conservative browser observations. They do not prove full WCAG compliance, and manual review is still required, especially for custom focus styles, image backgrounds, gradients, and complex responsive layouts.

## Reviewer Verdicts

Reviewer verdicts let humans mark findings as `confirmed`, `false_positive`, `needs_review`, `fixed`, or `missed_issue`. This helps measure precision and usefulness before outreach claims are made.

```bash
python -m a11yway.main --apply-verdicts reports/sample_verdicts.json --to reports/task_execution_report.json --out reports/task_execution_report_reviewed.json

python -m a11yway.main --summarize-verdicts reports/sample_verdicts.json --markdown reports/verdict_summary.md
```

Do not publicly name reviewers or organizations unless permission was granted in the verdict file.

## Re-Audit Diff Tracking

Re-audit diffs compare two A11yway JSON reports and show fixed, remaining, and new findings, plus task execution changes such as blocked-to-completed workflows.

```bash
python -m a11yway.main --compare-reports reports/task_execution_broken_report.json reports/task_execution_report.json --markdown reports/re_audit_diff.md --json reports/re_audit_diff.json
```

Use re-audits for honest impact metrics: fixed issues, remaining issues, new issues, and verified task improvements over time.

## Optional AI Scout Configuration

A11yway does not require AI keys. Deterministic audits work without any `.env` file.

A future optional AI scout mode may use Groq or other providers to propose likely workflows and accessibility risks. The Groq key would live in a local `.env` copied from `.env.example`. AI scout suggestions should remain suggestions: deterministic checks and task execution are the source of confirmed findings in reports.

## Batch Evaluation

Audit multiple pages in one run:

```bash
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample
python -m a11yway.main --batch examples/sample_browser_batch.json --out-dir reports/browser_batch_sample --browser
```

Each batch writes per-page JSON/Markdown reports plus:

- `index.json` / `index.md` - batch summary and per-source stats
- `index.csv` - spreadsheet-friendly benchmark row per page
- optional per-page `.html` reports with `--html-reports`
- `evaluation_summary.md` - reviewer-facing overview: top issue types, severity breakdown, high priority findings with evidence

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
- Browser mode approximates keyboard interaction; announced roles and names come from Chromium's computed accessibility tree when available (estimated otherwise) and need manual review.
- No full screen-reader simulation.
- No crawling, no logins, no private or unauthorized testing. Public pages or explicit permission only.
- Findings are hints for human reviewers. A11yway does not certify WCAG compliance and does not replace testing with disabled users.

## Ethical Metrics

Use honest, evidence-backed project metrics:

- Audited X websites
- Sent reports to Y organizations
- Received feedback from Z organizations
- Confirmed fixes on N websites
- Re-audits showed A fixed, B remaining, and C new issues

Do not claim "I helped change X websites" unless fixes are verified by re-audit or reviewer confirmation.

## Documentation

- [docs/RULES.md](docs/RULES.md) - every check: what it detects, why it matters, what it cannot verify
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - how a page flows through the tool
- [docs/ROADMAP.md](docs/ROADMAP.md) - what is planned, and what is deliberately not
- [docs/AI_SCOUT_DESIGN.md](docs/AI_SCOUT_DESIGN.md) - design notes for optional future AI scout mode
- [docs/RUN_FIRST_EVALUATION_BATCH.md](docs/RUN_FIRST_EVALUATION_BATCH.md) - running a responsible NGO/school review batch
- [docs/outreach/EVALUATION_PROTOCOL.md](docs/outreach/EVALUATION_PROTOCOL.md) - evaluation protocol for reviewers
- [docs/outreach/REVIEWER_GUIDE.md](docs/outreach/REVIEWER_GUIDE.md) - guide for accessibility reviewers
- [CONTRIBUTING.md](CONTRIBUTING.md) - setup, tests, adding rules and sample pages
- [CHANGELOG.md](CHANGELOG.md) - milestone history

## Project Direction

In this project, an "agent" is a small simulated user profile with a specific accessibility need. Today the checks are deterministic heuristics plus browser task execution; future AI scout mode is design/config only and would propose workflows for deterministic verification, not confirm findings by itself. The code is intentionally small and readable for student developers.
