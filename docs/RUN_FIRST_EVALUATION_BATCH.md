# Running Your First Evaluation Batch

This guide walks through a responsible first NGO or school evaluation
batch with A11yway. The goal is useful, honest feedback for the
organization, not a public scorecard.

## Ground rules

- Only test public pages, or pages where the organization gave you
  permission. No logins, no guessing at private URLs.
- A11yway output is a set of hints for human review, not a compliance
  verdict. Never present it as a WCAG certification.
- Do not publicly shame organizations. Share findings privately and give
  them time to respond and fix issues.

## Step 1: Pick a small page set

Choose 5–10 pages for the first batch. Good candidates: the homepage, a
registration or application form, a learning resources page, a page with
video or audio content. Small batches keep the review honest and the
follow-up conversation manageable.

## Step 2: Create your batch config

Copy the template and replace the placeholders:

```bash
cp examples/evaluation_batch_template.json examples/my_first_batch.json
```

Edit `my_first_batch.json`: set real page URLs (or local HTML files), give
each entry a clear name, and pick a matching task id from
`examples/sample_tasks.json` where one fits.

## Step 3: Run the static batch

```bash
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample
```

(Substitute your own config and output directory, for example
`--batch examples/my_first_batch.json --out-dir reports/my_first_batch`.)

This writes per-page JSON/Markdown reports plus `index.json`, `index.md`,
`index.csv`, and `evaluation_summary.md`.

## Step 4: Optionally run the browser batch

If Playwright is set up (see the README), a browser pass adds keyboard
traversal findings and catches JavaScript-added controls:

```bash
python -m a11yway.main --batch examples/sample_browser_batch.json --out-dir reports/browser_batch_sample --browser
```

## Step 5: Inspect reports before sending anything

Read `evaluation_summary.md` first, then the per-page Markdown reports.
For each high severity finding, open the actual page and confirm the
evidence snippet. Remove or annotate anything that looks like a false
positive. You are the reviewer; the tool only drafts.

## Step 6: Send the report

Send the Markdown report (or a cleaned-up version) together with the
feedback form. Templates:

- [NGO report email template](outreach/NGO_REPORT_EMAIL.md)
- [Feedback form questions](outreach/FEEDBACK_FORM_QUESTIONS.md)
- [Evaluation protocol](outreach/EVALUATION_PROTOCOL.md)

## Step 7: Track responses

Use `index.csv` as the starting point for a tracking sheet: add columns
for date sent, response received, confirmed findings, false positives,
and missed barriers the reviewer reported. This record is what turns the
prototype into an evaluated tool.

You can also store structured reviewer verdicts and summarize them:

```bash
python -m a11yway.main --summarize-verdicts reports/sample_verdicts.json --markdown reports/verdict_summary.md
```

## Step 8 - Re-audit after fixes

When an organization makes changes, run A11yway again and compare the old
and new JSON reports:

```bash
python -m a11yway.main --compare-reports reports/old_report.json reports/new_report.json --markdown reports/re_audit_diff.md --json reports/re_audit_diff.json
```

Use careful impact metrics:

- Audited X websites
- Sent reports to Y organizations
- Received feedback from Z organizations
- Confirmed fixes on N websites
- Re-audits showed A fixed, B remaining, and C new issues

Do not claim "helped change X websites" unless fixes are verified by
re-audit or reviewer confirmation.
