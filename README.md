# A11yway

A11yway is an early pseudocode scaffold for an agentic accessibility testing tool focused on education websites, forms, PDFs, and learning portals.

The idea is simple: instead of only scanning a page for technical accessibility rules, A11yway will eventually simulate how students with different accessibility needs complete real education tasks. Example tasks include finding an assignment, submitting a form, reading instructions, accessing a video, or downloading a resource.

## Why Education Accessibility Testing Matters

Education websites often contain forms, documents, videos, assignments, portals, and deadlines. If any of those are inaccessible, students can be blocked from learning or from completing required school tasks.

Accessibility testing in education should answer practical questions:

- Can a keyboard-only student complete the task?
- Can a low-vision student read and use the page after zooming?
- Are instructions clear for a student with reading difficulty?
- Are captions or transcripts available for audio and video content?

## What "Agentic Accessibility Testing" Means Here

In this project, an agent is a small simulated student profile. Each agent has a specific accessibility need and tries to complete a task from that point of view.

For this first draft, agents only contain placeholder logic and readable pseudocode. Later, they could use browser automation, PDF analysis, accessibility APIs, and human feedback to produce stronger results.

## MVP Scope

The first MVP should stay small:

- Load a task description.
- Run a few student accessibility agents.
- Collect barriers found by each agent.
- Suggest practical fixes.
- Build a simple report.

This scaffold does not include real AI integrations, browser automation, PDF parsing, or production APIs yet.

## Try the Prototype

Run the sample static HTML audit:

```bash
python -m a11yway.main examples/sample_form.html
```

Save a structured JSON report:

```bash
python -m a11yway.main examples/sample_form.html --json reports/sample_form_report.json
```

Save a readable Markdown report:

```bash
python -m a11yway.main examples/sample_form.html --task submit_scholarship_application --markdown reports/sample_form_report.md
```

Audit a public static page:

```bash
python -m a11yway.main https://example.com --markdown reports/url_report.md
```

Run the audit in the context of a task:

```bash
python -m a11yway.main examples/sample_form.html --task submit_scholarship_application
```

If no file path is provided, the command tries `examples/sample_form.html`.

The current prototype runs a static HTML audit for form labels, link and button names, image alt text, heading structure, page title/language, and basic media captions/transcripts. The JSON export is meant to grow into future NGO and school review reports.

Task mode explains which page barriers matter for a specific education workflow, such as submitting a scholarship form or accessing learning resources. This is the first step toward agentic accessibility testing, but it still uses deterministic static checks rather than real student simulation.

Markdown export is meant for sharing readable reports with schools, NGOs, and accessibility reviewers.

Reports include structured evidence such as HTML snippets, tag attributes, reasons, and approximate line numbers when available.

This is still not a full accessibility audit and does not replace testing with disabled users.

## Batch Evaluation

Run a batch audit across multiple local sample pages:

```bash
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample
```

Batch mode is meant for reviewing multiple school or NGO pages. It creates per-page JSON and Markdown reports, plus `index.json`, `index.md`, and `index.csv` summaries for tracking pages tested, issue counts, and task blockers. This is useful for future outreach and evaluation work.

You can also choose a CSV path:

```bash
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample --csv reports/batch_sample/index.csv
```

URL mode fetches the exact static HTML page you provide. It does not execute JavaScript, does not crawl websites, and should be used responsibly on public pages or pages you have permission to test.

## Evaluation Materials

Use these templates when sharing reports with schools, NGOs, or reviewers:

- [NGO report email template](docs/outreach/NGO_REPORT_EMAIL.md)
- [Feedback form questions](docs/outreach/FEEDBACK_FORM_QUESTIONS.md)
- [Evaluation protocol](docs/outreach/EVALUATION_PROTOCOL.md)
- [Reviewer guide](docs/outreach/REVIEWER_GUIDE.md)

## Example Use Case

A school wants to test whether students can submit a scholarship application form. A11yway runs several student agents against that task and reports problems such as missing form labels, confusing errors, weak focus indicators, or instructions that are only available in audio.

## Current Status

This repository is currently a lightweight pseudocode scaffold. It is meant to be readable for a student developer and easy to grow into a Python, Flask, or FastAPI project later.
